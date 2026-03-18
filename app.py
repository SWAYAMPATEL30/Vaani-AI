"""
Smart Voice Calling Agent - Main Application
Handles incoming calls, processes speech, generates AI responses, and converts to speech
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import json
from datetime import datetime
import uuid
import threading
from pathlib import Path

from config import Config
from services.assemblyai_service import AssemblyAIService
from services.openai_service import OpenAIService
from services.gemini_service import GeminiService
from services.groq_service import GroqService
from services.huggingface_asr_service import HuggingFaceASRService
from services.huggingface_llm_service import HuggingFaceLLMService
from services.tts_service import TTSService
from services.call_manager import CallManager

# Import models (db is initialized in models.py)
from models import db, Call, CallTranscript

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

# Initialize database
db.init_app(app)

# Initialize services (they will read from Config if keys not provided)
assemblyai_service = AssemblyAIService()
huggingface_asr_service = HuggingFaceASRService()

# Initialize AI service based on provider
if Config.AI_PROVIDER == 'groq':
    ai_service = GroqService()
elif Config.AI_PROVIDER == 'gemini':
    ai_service = GeminiService()
elif Config.AI_PROVIDER in ('huggingface', 'hf'):
    ai_service = HuggingFaceLLMService()
else:
    ai_service = OpenAIService()

tts_service = TTSService()
call_manager = CallManager()

# In-memory async job state for Twilio (prevents webhook timeouts)
# call_sid -> {"status": "processing"|"ready"|"error", "audio_url": str|None, "error": str|None, "updated_at": datetime}
CALL_JOBS = {}
CALL_JOBS_LOCK = threading.Lock()

# Pre-generate static Hindi prompts so Twilio can speak immediately without blocking webhooks
def _ensure_static_audio():
    try:
        audio_dir = Path("audio_output")
        audio_dir.mkdir(exist_ok=True)

        # Generate only if missing (we create files with prefix; filename includes hash)
        has_greeting = any(audio_dir.glob("greeting_hi_*.wav"))
        has_waiting = any(audio_dir.glob("waiting_hi_*.wav"))

        if not has_greeting:
            greeting_text = "नमस्ते! मैं आपकी AI सहायक हूं। कृपया अपना संदेश बोलें।"
            url = tts_service.text_to_speech(greeting_text, call_sid="greeting_hi", language_code="hi")
            logger.info(f"Generated static greeting audio: {url}")

        if not has_waiting:
            waiting_text = "धन्यवाद। कृपया कुछ सेकंड प्रतीक्षा करें, मैं जवाब तैयार कर रही हूँ।"
            url = tts_service.text_to_speech(waiting_text, call_sid="waiting_hi", language_code="hi")
            logger.info(f"Generated static waiting audio: {url}")
    except Exception as e:
        logger.warning(f"Failed to pre-generate static Hindi audio: {e}")

# Run in background so Flask can start immediately (Twilio webhooks must be fast).
threading.Thread(target=_ensure_static_audio, daemon=True).start()

# Create database tables
with app.app_context():
    db.create_all()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'assemblyai': bool(Config.ASSEMBLYAI_API_KEY),
            'ai_provider': Config.AI_PROVIDER,
            'groq': bool(Config.GROQ_API_KEY),
            'gemini': bool(Config.GEMINI_API_KEY),
            'openai': bool(Config.OPENAI_API_KEY),
            'huggingface': bool(Config.HUGGINGFACE_TOKEN),
            'stt_provider': Config.STT_PROVIDER,
            'tts_provider': Config.TTS_PROVIDER,
            'tts': bool(Config.ELEVENLABS_API_KEY or Config.GOOGLE_APPLICATION_CREDENTIALS or Config.HUGGINGFACE_TOKEN)
        }
    })


@app.route('/webhook/incoming', methods=['POST'])
def handle_incoming_call():
    """
    Handle incoming call webhook from telephony provider (Exotel/Twilio)
    """
    try:
        # Twilio sends application/x-www-form-urlencoded by default.
        # Prefer form data, then fall back to JSON if present.
        data = request.form.to_dict() or (request.get_json(silent=True) or {})
        logger.info(f"Incoming call webhook: {json.dumps(data, indent=2)}")
        
        # Extract call information
        call_sid = data.get('CallSid') or data.get('call_sid') or str(uuid.uuid4())
        from_number = data.get('From') or data.get('from_number', '')
        to_number = data.get('To') or data.get('to_number', '')
        
        # Get or create call record (handle duplicate call_sid gracefully)
        try:
            call = Call.query.filter_by(call_sid=call_sid).first()
            if not call:
        call = Call(
            call_sid=call_sid,
            from_number=from_number,
            to_number=to_number,
            status='ringing',
            provider=data.get('provider', 'unknown')
        )
        db.session.add(call)
                try:
                    db.session.commit()
                except Exception as db_error:
                    # If commit fails (e.g., duplicate), rollback and use existing call
                    db.session.rollback()
                    call = Call.query.filter_by(call_sid=call_sid).first()
                    if call:
                        logger.info(f"Using existing call record after rollback: {call_sid}")
                    else:
                        logger.warning(f"Could not create or find call record: {db_error}")
            else:
                # Update existing call status
                call.status = 'ringing'
                if from_number:
                    call.from_number = from_number
                if to_number:
                    call.to_number = to_number
                try:
        db.session.commit()
                except Exception as db_error:
                    db.session.rollback()
                    logger.warning(f"Could not update call record: {db_error}")
        except Exception as db_error:
            logger.warning(f"Database error while handling incoming call: {db_error}")
        
        # Generate TwiML/Exotel response for call handling
        # IMPORTANT: Always return TwiML even if database operations fail.
        #
        # We construct the TwiML inline here (instead of relying on any
        # previously-imported CallManager state) to guarantee that we always
        # use relative URLs (`/audio/...`, `/webhook/...`) which are safe with
        # changing ngrok tunnels and different hosts.
        from pathlib import Path

        audio_dir = Path("audio_output")
        greeting_files = sorted(
            audio_dir.glob("greeting_hi_*.wav"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        greeting_path = greeting_files[0] if greeting_files else None

        if greeting_path and greeting_path.exists():
            greeting_url = f"/audio/{greeting_path.name}"
            response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{greeting_url}</Play>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""
        else:
            logger.info("Greeting audio not found - starting recording immediately (inline TwiML)")
            response_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""
        
        return Response(response_xml, mimetype='application/xml')
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}", exc_info=True)
        # Return minimal TwiML (no Twilio Say - open-source only)
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record action="/webhook/recording" method="POST" maxLength="10" timeout="5" />
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='application/xml')


@app.route('/webhook/status', methods=['POST'])
def handle_call_status():
    """
    Handle call status updates (answered, ended, etc.)
    """
    try:
        data = request.form.to_dict() or (request.get_json(silent=True) or {})
        logger.info(f"Call status update: {json.dumps(data, indent=2)}")
        
        call_sid = data.get('CallSid') or data.get('call_sid')
        call_status = data.get('CallStatus') or data.get('call_status', 'unknown')
        
        if call_sid:
            call = Call.query.filter_by(call_sid=call_sid).first()
            if call:
                call.status = call_status
                if call_status == 'completed':
                    call.end_time = datetime.utcnow()
                db.session.commit()
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Error handling call status: {str(e)}", exc_info=True)
        # Return OK status even on error to prevent Twilio issues
        return jsonify({'status': 'ok'}), 200


@app.route('/webhook/poll', methods=['GET', 'POST'])
def handle_poll():
    """
    Twilio polling endpoint to avoid webhook timeouts.
    Twilio redirects here until an async job produces an audio URL to play.
    """
    try:
        call_sid = request.values.get("CallSid") or request.args.get("call_sid") or request.form.get("call_sid")
        if not call_sid:
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Hangup/>
</Response>"""
            return Response(twiml, mimetype="application/xml")

        with CALL_JOBS_LOCK:
            job = CALL_JOBS.get(call_sid)

        logger.info(f"Poll request for call {call_sid}: job={job}")
        
        if job and job.get("status") == "ready" and job.get("audio_url"):
            audio_url = job["audio_url"]
            logger.info(f"Job ready for {call_sid}, playing audio: {audio_url}")
            # Clear job after consumption to avoid replaying the same audio forever
            with CALL_JOBS_LOCK:
                CALL_JOBS.pop(call_sid, None)

            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Hangup/>
</Response>"""
            return Response(twiml, mimetype="application/xml")
        
        if job and job.get("status") == "error":
            error_msg = job.get("error", "Unknown error")
            logger.error(f"Job error for {call_sid}: {error_msg}")
            # Still try to continue with recording
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""
            return Response(twiml, mimetype="application/xml")

        # Not ready yet: play waiting prompt if available, then keep polling
        logger.info(f"Job not ready for {call_sid}, status={job.get('status') if job else 'None'}, continuing to poll...")
        if not job:
            job = {"status": "processing"}

        audio_dir = Path("audio_output")
        waiting_files = sorted(audio_dir.glob("waiting_hi_*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
        waiting_path = waiting_files[0] if waiting_files else None

        if waiting_path and waiting_path.exists():
            # Use relative URL so it always works with current host (ngrok/Twilio)
            waiting_url = f"/audio/{waiting_path.name}"
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{waiting_url}</Play>
    <Pause length="5"/>
    <Redirect method="POST">/webhook/poll?CallSid={call_sid}</Redirect>
</Response>"""
        else:
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="5"/>
    <Redirect method="POST">/webhook/poll?CallSid={call_sid}</Redirect>
</Response>"""
        return Response(twiml, mimetype="application/xml")
    except Exception as e:
        logger.error(f"Error in poll handler: {e}", exc_info=True)
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype="application/xml")


def _process_transcription_async(call_sid_in, transcript_text_in, from_number_in, to_number_in):
    """
    Background worker for /webhook/transcription to avoid Twilio timeouts.
    Handles:
      - Ensuring Call record exists
      - Saving user transcript
      - Generating LLM response
      - Saving agent transcript
      - Generating TTS audio
      - Updating CALL_JOBS with final audio_url or error
    """
    try:
        from config import Config  # Local import to avoid circular issues in some environments
        with app.app_context():
            logger.info(f"Async transcription processing started for call {call_sid_in}")

            # Get or create call record
            call = Call.query.filter_by(call_sid=call_sid_in).first()
            if not call:
                call = Call(
                    call_sid=call_sid_in,
                    from_number=from_number_in or '',
                    to_number=to_number_in or '',
                    status='in-progress',
                    provider='twilio'
                )
                db.session.add(call)
                try:
                db.session.commit()
                except Exception:
                    db.session.rollback()

            
            # Save user transcript
            user_transcript = CallTranscript(
                call_id=call.id,
                text=transcript_text_in,
                is_final='true',
                timestamp=datetime.utcnow(),
                speaker='user'
            )
            db.session.add(user_transcript)
            db.session.commit()
            
            # Build conversation history
            previous_transcripts = CallTranscript.query.filter_by(
                call_id=call.id
            ).order_by(CallTranscript.timestamp).all()
            
            conversation_history = []
            for t in previous_transcripts:
                conversation_history.append({
                    "role": "user" if t.speaker == 'user' else "assistant",
                    "content": t.text
                })
            
            # LLM response
            try:
                response_text_local = ai_service.generate_response(
                    transcript_text_in,
                call.id,
                conversation_history=conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                ) or "मैं आपकी मदद करने के लिए यहां हूं। कृपया अपना प्रश्न दोहराएं।"
            except Exception as llm_err:
                logger.error(f"Async LLM failed for call {call_sid_in}: {llm_err}", exc_info=True)
                response_text_local = "मैं आपकी मदद करने के लिए यहां हूं। कृपया अपना प्रश्न दोहराएं।"
            
            # Save agent response
            ai_transcript = CallTranscript(
                call_id=call.id,
                text=response_text_local,
                is_final='true',
                timestamp=datetime.utcnow(),
                speaker='agent'
            )
            db.session.add(ai_transcript)
            db.session.commit()
            
            # TTS (open-source)
            language_code_local = Config.LANGUAGE_CODE.split('-')[0] if '-' in Config.LANGUAGE_CODE else 'hi'
            logger.info(f"Starting async TTS for call {call_sid_in}...")
            audio_url_local = tts_service.text_to_speech(
                response_text_local,
                call_sid=call_sid_in,
                language_code=language_code_local
            )
            if not audio_url_local:
                raise RuntimeError("TTS failed (no audio_url)")

            logger.info(f"Async TTS completed for call {call_sid_in}: audio_url={audio_url_local}")
            with CALL_JOBS_LOCK:
                CALL_JOBS[call_sid_in] = {
                    "status": "ready",
                    "audio_url": audio_url_local,
                    "error": None,
                    "updated_at": datetime.utcnow()
                }
    except Exception as err:
        logger.error(f"Async transcription processing failed for {call_sid_in}: {err}", exc_info=True)
        with CALL_JOBS_LOCK:
            CALL_JOBS[call_sid_in] = {
                "status": "error",
                "audio_url": None,
                "error": str(err),
                "updated_at": datetime.utcnow()
            }


@app.route('/webhook/transcription', methods=['POST'])
def handle_transcription():
    """
    Handle real-time transcription from Twilio and generate AI response
    """
    try:
        # Twilio sends form-encoded data; fall back to JSON only if present
        data = request.form.to_dict() or (request.get_json(silent=True) or {})
        logger.info(f"Transcription webhook: {json.dumps(data, indent=2)}")
        
        call_sid = data.get('CallSid') or data.get('call_sid')
        transcript_text = data.get('SpeechResult', '') or data.get('text', '')
        
        if call_sid and transcript_text:
            from_number = data.get('From', '') or data.get('from_number', '')
            to_number = data.get('To', '') or data.get('to_number', '')
            
            # Mark async job as processing
            with CALL_JOBS_LOCK:
                CALL_JOBS[call_sid] = {
                    "status": "processing",
                    "audio_url": None,
                    "error": None,
                    "updated_at": datetime.utcnow()
                }

            # Kick off full async pipeline: DB save + LLM + TTS
            threading.Thread(
                target=_process_transcription_async,
                args=(call_sid, transcript_text, from_number, to_number),
                daemon=True
            ).start()

            # Immediately return TwiML that polls for the generated audio
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Redirect method="POST">/webhook/poll?CallSid={call_sid}</Redirect>
</Response>"""
            return Response(twiml, mimetype='application/xml')
        
        # Default response if no transcript - no Twilio Say
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='application/xml')
        
    except Exception as e:
        logger.error(f"Error handling transcription: {str(e)}", exc_info=True)
        # No Twilio Say - just gather for STT testing
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='application/xml')


@app.route('/webhook/continue', methods=['GET', 'POST'])
def handle_continue():
    """Handle call continuation after gather"""
    try:
        call_sid = request.args.get('CallSid') or request.form.get('CallSid')
        
        # No Twilio Say - open-source only
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='application/xml')
    except Exception as e:
        logger.error(f"Error in continue handler: {str(e)}")
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='application/xml')


@app.route('/webhook/recording', methods=['POST'])
def handle_recording():
    """
    Handle Twilio recording webhook when using Record instead of Gather
    This allows us to use Whisper for transcription instead of Twilio's built-in STT
    """
    try:
        data = request.form.to_dict() or (request.get_json(silent=True) or {})
        logger.info(f"Recording webhook: {json.dumps(data, indent=2)}")
        
        call_sid = data.get('CallSid') or data.get('call_sid')
        recording_url = data.get('RecordingUrl') or data.get('recording_url')
        recording_status = data.get('RecordingStatus') or data.get('recording_status')
        
        if not call_sid:
            logger.error("No CallSid in recording webhook")
            # No Twilio Say - just record for testing
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""
            return Response(twiml, mimetype='application/xml')
        
        # Process recording if URL exists and duration > 0 (Twilio may not send RecordingStatus)
        recording_duration = data.get('RecordingDuration') or data.get('recording_duration') or '0'
        if not recording_url or int(float(recording_duration)) == 0:
            logger.info(f"Recording not ready yet: url={bool(recording_url)}, duration={recording_duration}, status={recording_status}")
            # Wait and try to gather speech as fallback
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Pause length="2"/>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Hangup/>
</Response>"""
            return Response(twiml, mimetype='application/xml')
        
        # Append .wav extension to Twilio recording URL for audio download
        if not recording_url.endswith('.wav'):
            recording_url = recording_url + '.wav'
        
        # Start async processing to avoid Twilio webhook timeout (critical!)
        with CALL_JOBS_LOCK:
            CALL_JOBS[call_sid] = {"status": "processing", "audio_url": None, "error": None, "updated_at": datetime.utcnow()}

        from_number = data.get('From', '') or data.get('from_number', '')
        to_number = data.get('To', '') or data.get('to_number', '')

        def _process_recording_async(call_sid_in, recording_url_in, from_number_in, to_number_in):
            try:
                import requests
                from io import BytesIO
                # Need Flask app context for DB access in background thread
                with app.app_context():

                    # Download recording from Twilio
                    logger.info(f"Downloading recording from Twilio: {recording_url_in}")
                    rec_resp = requests.get(
                        recording_url_in,
                        auth=(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN),
                        timeout=30
                    )
                    rec_resp.raise_for_status()
                    audio_data_local = rec_resp.content
                    logger.info(f"Downloaded {len(audio_data_local)} bytes of audio")
                    audio_file_local = BytesIO(audio_data_local)

                    language_code_local = Config.LANGUAGE_CODE.split('-')[0] if '-' in Config.LANGUAGE_CODE else 'hi'

                    # STT: prefer local Whisper (open-source). If AssemblyAI key exists and STT_PROVIDER says so, use it.
                    transcript_text_local = None
                    try:
                        logger.info(f"Starting STT transcription for call {call_sid_in}...")
                        if Config.STT_PROVIDER in ('huggingface', 'hf') or not Config.ASSEMBLYAI_API_KEY:
                            transcript_text_local = huggingface_asr_service.transcribe_audio(audio_file_local, language_code=language_code_local)
                        else:
                            transcript_text_local = assemblyai_service.transcribe_audio(audio_file_local, language_code=language_code_local)
                        logger.info(f"STT completed: transcript='{transcript_text_local[:100] if transcript_text_local else 'None'}'")
                    except Exception as stt_err:
                        logger.error(f"Async STT failed: {stt_err}", exc_info=True)

                    if not transcript_text_local or not transcript_text_local.strip():
                        logger.error(f"STT returned empty transcript for call {call_sid_in}")
                        raise RuntimeError("STT failed (no transcript)")

                    # Get or create call record
                    call = Call.query.filter_by(call_sid=call_sid_in).first()
                    if not call:
                        call = Call(
                            call_sid=call_sid_in,
                            from_number=from_number_in,
                            to_number=to_number_in,
                            status='in-progress',
                            provider='twilio'
                        )
                        db.session.add(call)
                        db.session.commit()

                    # Save user transcript
                    transcript = CallTranscript(
                        call_id=call.id,
                        text=transcript_text_local,
                        is_final='true',
                        timestamp=datetime.utcnow(),
                        speaker='user'
                    )
                    db.session.add(transcript)
                    db.session.commit()

                    # Conversation history
                    previous_transcripts = CallTranscript.query.filter_by(
                        call_id=call.id
                    ).order_by(CallTranscript.timestamp).all()

                    conversation_history = []
                    for t in previous_transcripts:
                        conversation_history.append({"role": "user" if t.speaker == 'user' else "assistant", "content": t.text})

                    # LLM
                    try:
                        response_text_local = ai_service.generate_response(
                            transcript_text_local,
                            call.id,
                            conversation_history=conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                        ) or "मैं आपकी मदद करने के लिए यहां हूं। कृपया अपना प्रश्न दोहराएं।"
                    except Exception as llm_err:
                        logger.error(f"Async LLM failed: {llm_err}", exc_info=True)
                        response_text_local = "मैं आपकी मदद करने के लिए यहां हूं। कृपया अपना प्रश्न दोहराएं।"

                    # Save agent response
                    ai_transcript = CallTranscript(
                        call_id=call.id,
                        text=response_text_local,
                        is_final='true',
                        timestamp=datetime.utcnow(),
                        speaker='agent'
                    )
                    db.session.add(ai_transcript)
                    db.session.commit()

                    # TTS (open-source)
                    logger.info(f"Starting TTS generation for call {call_sid_in}...")
                    audio_url_local = tts_service.text_to_speech(response_text_local, call_sid=call_sid_in, language_code=language_code_local)
                    if not audio_url_local:
                        logger.error(f"TTS returned None for call {call_sid_in}")
                        raise RuntimeError("TTS failed (no audio_url)")

                    logger.info(f"TTS completed: audio_url={audio_url_local}")
                    with CALL_JOBS_LOCK:
                        CALL_JOBS[call_sid_in] = {"status": "ready", "audio_url": audio_url_local, "error": None, "updated_at": datetime.utcnow()}
                    logger.info(f"Call job marked as ready for {call_sid_in}")

            except Exception as err:
                logger.error(f"Async processing failed for {call_sid_in}: {err}", exc_info=True)
                with CALL_JOBS_LOCK:
                    CALL_JOBS[call_sid_in] = {"status": "error", "audio_url": None, "error": str(err), "updated_at": datetime.utcnow()}

        # Kick off background worker
        threading.Thread(target=_process_recording_async, args=(call_sid, recording_url, from_number, to_number), daemon=True).start()

        # Immediately return TwiML that polls for the response audio
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Redirect method="POST">/webhook/poll?CallSid={call_sid}</Redirect>
</Response>"""
        return Response(twiml, mimetype='application/xml')
        
        # (Old synchronous flow removed: it caused Twilio timeouts.)
        
    except Exception as e:
        logger.error(f"Error handling recording: {str(e)}", exc_info=True)
        # No Twilio Say - just record again for testing
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Record action="/webhook/recording" method="POST" maxLength="10" timeout="5" />
    <Hangup/>
</Response>"""
        return Response(twiml, mimetype='application/xml')


@app.route('/api/calls', methods=['GET'])
def get_calls():
    """Get list of all calls"""
    try:
        calls = Call.query.order_by(Call.start_time.desc()).limit(50).all()
        return jsonify({
            'calls': [{
                'id': call.id,
                'call_sid': call.call_sid,
                'from_number': call.from_number,
                'to_number': call.to_number,
                'status': call.status,
                'start_time': call.start_time.isoformat() if call.start_time else None,
                'end_time': call.end_time.isoformat() if call.end_time else None,
                'duration': call.duration
            } for call in calls]
        })
    except Exception as e:
        logger.error(f"Error getting calls: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calls/<call_sid>/transcripts', methods=['GET'])
def get_call_transcripts(call_sid):
    """Get transcripts for a specific call"""
    try:
        call = Call.query.filter_by(call_sid=call_sid).first()
        if not call:
            return jsonify({'error': 'Call not found'}), 404
        
        transcripts = CallTranscript.query.filter_by(call_id=call.id).order_by(CallTranscript.timestamp).all()
        return jsonify({
            'call_sid': call_sid,
            'transcripts': [{
                'text': t.text,
                'is_final': t.is_final,
                'timestamp': t.timestamp.isoformat()
            } for t in transcripts]
        })
    except Exception as e:
        logger.error(f"Error getting transcripts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process-audio', methods=['POST'])
def process_audio():
    """
    Process audio file for transcription and response
    Useful for testing or direct audio upload
    """
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        call_sid = request.form.get('call_sid', str(uuid.uuid4()))
        
        # Transcribe audio (provider-selectable)
        if Config.STT_PROVIDER in ('huggingface', 'hf'):
            transcript = huggingface_asr_service.transcribe_audio(audio_file)
        else:
        transcript = assemblyai_service.transcribe_audio(audio_file)
        
        if transcript:
            # Generate AI response
            response_text = ai_service.generate_response(transcript, call_sid)
            
            # Convert response to speech using Facebook MMS TTS Hindi
            language_code = Config.LANGUAGE_CODE.split('-')[0] if '-' in Config.LANGUAGE_CODE else 'hi'
            audio_url = tts_service.text_to_speech(response_text, call_sid, language_code=language_code)
            
            return jsonify({
                'transcript': transcript,
                'response': response_text,
                'audio_url': audio_url
            })
        
        return jsonify({'error': 'Transcription failed'}), 500
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    """Serve generated audio files"""
    try:
        from flask import send_from_directory
        from pathlib import Path
        
        audio_dir = Path('audio_output')
        if not audio_dir.exists():
            return jsonify({'error': 'Audio directory not found'}), 404
        
        return send_from_directory(str(audio_dir), filename)
    except Exception as e:
        logger.error(f"Error serving audio: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # NOTE:
    # - We keep debug configurable via Config.FLASK_DEBUG so you can see
    #   detailed errors in the terminal when something goes wrong.
    # - We explicitly disable the Flask reloader (use_reloader=False) because
    #   on Windows it can spawn multiple processes and break Twilio webhooks.
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.FLASK_DEBUG,
        use_reloader=False,
    )

