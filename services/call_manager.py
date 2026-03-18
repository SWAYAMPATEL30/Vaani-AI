"""
Call Manager for handling telephony webhooks and call flow
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CallManager:
    """Manages call flow and telephony integration"""
    
    def __init__(self):
        """Initialize call manager"""
        from config import Config
        self.webhook_base_url = Config.WEBHOOK_BASE_URL
        logger.info("Call manager initialized")
    
    def generate_call_response(self, call_sid, provider='twilio'):
        """
        Generate XML response for incoming call (TwiML for Twilio, Exotel format)
        
        Args:
            call_sid: Call session ID
            provider: 'twilio' or 'exotel'
        
        Returns:
            str: XML response for telephony provider
        """
        if provider == 'twilio':
            return self._generate_twiml(call_sid)
        elif provider == 'exotel':
            return self._generate_exotel_response(call_sid)
        else:
            # Default to Twilio format
            return self._generate_twiml(call_sid)
    
    def _generate_twiml(self, call_sid):
        """Generate TwiML response for Twilio with interactive conversation."""
        # IMPORTANT: Use relative URLs so Twilio always talks to the same host
        # that delivered this TwiML (current ngrok / production URL). Hard‑coding
        # Config.WEBHOOK_BASE_URL here can point Twilio at a stale ngrok tunnel
        # and cause the 'Application Error' message.
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
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{greeting_url}</Play>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""
        else:
            logger.info("Greeting audio not found - starting recording immediately")
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""

        return twiml
    
    def _generate_exotel_response(self, call_sid):
        """
        Generate response for Exotel using the same open‑source TTS flow.

        We avoid Twilio/Exotel `<Say>` completely and always rely on our locally
        generated audio files (Whisper for STT, MMS/Veena for TTS). Exotel can
        consume TwiML‑like XML, so we keep the structure similar to Twilio.
        """
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
        response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{greeting_url}</Play>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""
        else:
            logger.info("Greeting audio not found for Exotel - starting recording immediately")
            response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="/webhook/transcription" method="POST" speechTimeout="auto" timeout="60" language="hi-IN" />
    <Record action="/webhook/recording" method="POST" maxLength="60" timeout="30" />
    <Hangup/>
</Response>"""

        return response
    
    def handle_call_answer(self, call_sid, from_number, to_number):
        """
        Handle when a call is answered
        
        Args:
            call_sid: Call session ID
            from_number: Caller's number
            to_number: Called number
        """
        logger.info(f"Call answered: {call_sid} from {from_number} to {to_number}")
        # Additional logic can be added here
        return True
    
    def handle_call_end(self, call_sid, duration=None):
        """
        Handle when a call ends
        
        Args:
            call_sid: Call session ID
            duration: Call duration in seconds
        """
        logger.info(f"Call ended: {call_sid}, duration: {duration} seconds")
        # Additional cleanup logic can be added here
        return True

