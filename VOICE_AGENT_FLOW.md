# Voice Agent Flow Documentation
## Complete System Architecture & Call Flow

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S PHONE                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Voice Call (PSTN/VoIP)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TWILIO CLOUD                             │
│  - Receives incoming/outgoing calls                              │
│  - Records audio / Captures speech                               │
│  - Sends webhooks to Flask server                                │
│  - Plays audio responses                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS Webhooks (TwiML)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK SERVER (app.py)                        │
│  - Receives webhooks from Twilio                                 │
│  - Orchestrates STT → LLM → TTS pipeline                        │
│  - Manages call state and database                               │
│  - Serves audio files                                            │
└─────┬──────────────┬──────────────┬──────────────┬──────────────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   STT    │  │   LLM    │  │   TTS    │  │ DATABASE  │
│ (Whisper)│  │  (Groq)  │  │  (MMS)   │  │ (SQLite)  │
│  Local   │  │   API    │  │  Local   │  │   Local   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 2. Complete Call Flow (Step-by-Step)

### Phase 1: Call Initiation

```
1. User dials Twilio phone number
   └─> Twilio receives call
       └─> Twilio sends POST to /webhook/incoming
           └─> Flask app receives call data
               └─> Creates Call record in database
                   └─> Returns TwiML with greeting
                       └─> Twilio plays greeting audio
```

**TwiML Response**:
```xml
<Response>
    <Play>/audio/greeting_hi_*.wav</Play>
    <Gather input="speech" action="/webhook/transcription" ... />
    <Record action="/webhook/recording" ... />
</Response>
```

---

### Phase 2: User Speaks (Two Paths)

#### Path A: Twilio Speech Recognition (Real-time)
```
2a. User speaks into phone
    └─> Twilio captures speech (Gather)
        └─> Twilio transcribes speech
            └─> Twilio sends POST to /webhook/transcription
                └─> Flask app receives transcript
                    └─> Starts async processing thread
                        └─> Returns TwiML redirect to /webhook/poll
                            └─> Twilio polls /webhook/poll
```

#### Path B: Audio Recording (Whisper STT)
```
2b. User speaks into phone
    └─> Twilio records audio (Record)
        └─> Twilio sends POST to /webhook/recording
            └─> Flask app receives recording URL
                └─> Starts async processing thread
                    └─> Downloads audio from Twilio
                        └─> Returns TwiML redirect to /webhook/poll
                            └─> Twilio polls /webhook/poll
```

---

### Phase 3: Async Processing Pipeline

```
3. Background Thread (async processing)
   │
   ├─> STEP 1: Speech-to-Text (STT)
   │   └─> Local Whisper model transcribes audio
   │       └─> Output: "नमस्ते, मैं मदद चाहता हूं"
   │
   ├─> STEP 2: Save User Transcript
   │   └─> Store in database (CallTranscript table)
   │
   ├─> STEP 3: Build Conversation History
   │   └─> Retrieve previous messages from database
   │
   ├─> STEP 4: Generate AI Response (LLM)
   │   └─> Send to Groq API (llama-3.3-70b-versatile)
   │       └─> Input: User transcript + conversation history
   │       └─> Output: "नमस्ते! मैं आपकी कैसे मदद कर सकती हूं?"
   │
   ├─> STEP 5: Save AI Transcript
   │   └─> Store in database (CallTranscript table)
   │
   └─> STEP 6: Text-to-Speech (TTS)
       └─> Local MMS TTS Hindi model generates audio
           └─> Output: /audio/CA123_*.wav
           └─> Update CALL_JOBS[call_sid] = {"status": "ready", "audio_url": "..."}
```

---

### Phase 4: Response Delivery

```
4. Twilio Polling (/webhook/poll)
   │
   ├─> Twilio sends GET/POST to /webhook/poll?CallSid=CA123
   │
   ├─> Flask checks CALL_JOBS[call_sid]
   │
   ├─> If status == "processing":
   │   └─> Return TwiML with waiting message + redirect
   │       └─> Twilio plays waiting audio
   │           └─> Twilio redirects to /webhook/poll again (loop)
   │
   └─> If status == "ready":
       └─> Return TwiML with <Play> audio_url
           └─> Twilio plays AI response audio
               └─> Twilio redirects to <Gather> for next user input
                   └─> Loop back to Phase 2
```

**TwiML Response (Ready)**:
```xml
<Response>
    <Play>/audio/CA123_response.wav</Play>
    <Gather input="speech" action="/webhook/transcription" ... />
    <Hangup/>
</Response>
```

---

### Phase 5: Call Continuation or Termination

```
5. User responds again
   └─> Loop back to Phase 2 (user speaks)
       └─> Process → Respond → Continue
           └─> Repeat until:
               - User hangs up
               - Max call duration reached (300 seconds)
               - Error occurs
```

---

## 3. Detailed Component Flow

### 3.1 Incoming Call Handler (`/webhook/incoming`)

```python
POST /webhook/incoming
├─> Extract CallSid, From, To from request
├─> Create/Update Call record in database
├─> Check for pre-generated greeting audio
├─> Return TwiML:
    ├─> <Play> greeting_hi_*.wav (if available)
    ├─> <Gather> for speech input
    └─> <Record> as fallback
```

**Key Features**:
- Uses relative URLs (`/audio/...`) for ngrok compatibility
- Handles duplicate CallSid gracefully
- Always returns valid TwiML (even on errors)

---

### 3.2 Transcription Handler (`/webhook/transcription`)

```python
POST /webhook/transcription
├─> Extract CallSid, SpeechResult (transcript)
├─> Mark CALL_JOBS[call_sid] = {"status": "processing"}
├─> Start background thread: _process_transcription_async()
│   ├─> Save user transcript to database
│   ├─> Build conversation history
│   ├─> Call Groq LLM API
│   ├─> Save AI response to database
│   ├─> Generate TTS audio (MMS TTS)
│   └─> Update CALL_JOBS[call_sid] = {"status": "ready", "audio_url": "..."}
└─> Return TwiML: <Redirect> to /webhook/poll
```

**Why Async?**
- LLM + TTS takes 6-12 seconds (exceeds Twilio's 10s webhook timeout)
- Async prevents Twilio "Application Error"
- Polling allows Twilio to wait for response

---

### 3.3 Recording Handler (`/webhook/recording`)

```python
POST /webhook/recording
├─> Extract CallSid, RecordingUrl, RecordingDuration
├─> Validate recording (duration > 0, URL exists)
├─> Mark CALL_JOBS[call_sid] = {"status": "processing"}
├─> Start background thread: _process_recording_async()
│   ├─> Download audio from Twilio (with auth)
│   ├─> Transcribe with local Whisper STT
│   ├─> Save user transcript to database
│   ├─> Build conversation history
│   ├─> Call Groq LLM API
│   ├─> Save AI response to database
│   ├─> Generate TTS audio (MMS TTS)
│   └─> Update CALL_JOBS[call_sid] = {"status": "ready", "audio_url": "..."}
└─> Return TwiML: <Redirect> to /webhook/poll
```

**Key Features**:
- Downloads audio from Twilio (requires auth)
- Uses local Whisper for transcription (no API cost)
- Handles recording failures gracefully

---

### 3.4 Polling Handler (`/webhook/poll`)

```python
GET/POST /webhook/poll?CallSid=CA123
├─> Extract CallSid from request
├─> Check CALL_JOBS[call_sid]
│
├─> If status == "ready" and audio_url exists:
│   ├─> Clear job from CALL_JOBS
│   └─> Return TwiML:
│       ├─> <Play> audio_url
│       └─> <Gather> for next user input
│
├─> If status == "error":
│   └─> Return TwiML:
│       ├─> <Record> (try again)
│       └─> <Hangup>
│
└─> If status == "processing" or None:
    ├─> Play waiting message (if available)
    └─> Return TwiML:
        ├─> <Pause length="5"/>
        └─> <Redirect> to /webhook/poll (loop)
```

**Polling Logic**:
- Twilio redirects every 5 seconds until ready
- Prevents webhook timeout
- Shows waiting message to user

---

## 4. Data Flow Diagram

```
┌─────────────┐
│   User      │
│  Speaks     │
└──────┬──────┘
       │ Audio
       ▼
┌─────────────┐
│   Twilio    │
│  Records    │
└──────┬──────┘
       │ Webhook (RecordingUrl)
       ▼
┌─────────────┐
│   Flask     │
│  Server     │
└──────┬──────┘
       │
       ├─> Download Audio
       │
       ▼
┌─────────────┐      ┌─────────────┐
│   Whisper   │─────>│   Text      │
│    (STT)    │      │ "नमस्ते..." │
└─────────────┘      └──────┬──────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  Database   │
                    │  (Save)     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Groq      │
                    │    LLM      │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Text     │
                    │ "नमस्ते!..."│
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Database   │
                    │  (Save)     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐      ┌─────────────┐
                    │   MMS TTS   │─────>│   Audio     │
                    │   (Hindi)   │      │  file.wav   │
                    └─────────────┘      └──────┬──────┘
                                                 │
                                                 ▼
                                         ┌─────────────┐
                                         │   Twilio    │
                                         │    Play     │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │    User     │
                                         │   Hears     │
                                         └─────────────┘
```

---

## 5. State Management

### In-Memory State (`CALL_JOBS`)

```python
CALL_JOBS = {
    "CA123...": {
        "status": "processing" | "ready" | "error",
        "audio_url": "/audio/CA123_response.wav" | None,
        "error": "Error message" | None,
        "updated_at": datetime.utcnow()
    }
}
```

**Lifecycle**:
1. **Created**: When transcription/recording webhook received
2. **Processing**: Background thread working
3. **Ready**: Audio generated, ready to play
4. **Cleared**: After Twilio plays audio (or error)

---

### Database State

**Call Table**:
```sql
Call
├─> id (primary key)
├─> call_sid (unique, from Twilio)
├─> from_number
├─> to_number
├─> status (ringing, in-progress, completed)
├─> start_time
├─> end_time
└─> duration
```

**CallTranscript Table**:
```sql
CallTranscript
├─> id (primary key)
├─> call_id (foreign key → Call.id)
├─> text (transcript text)
├─> speaker (user | agent)
├─> is_final (true | false)
└─> timestamp
```

---

## 6. Error Handling Flow

```
Error Occurs
│
├─> Try/Except Block Catches Error
│   └─> Log error with details
│
├─> Update CALL_JOBS[call_sid] = {"status": "error", "error": "..."}
│
└─> Return Graceful TwiML:
    ├─> <Record> (try again)
    └─> <Hangup> (if critical)
```

**Error Types**:
- **STT Failure**: Return error message, try again
- **LLM Failure**: Return fallback message ("कृपया दोहराएं")
- **TTS Failure**: Return error, try again
- **Database Error**: Log, continue (non-critical)

---

## 7. Audio File Management

### File Naming Convention
```
greeting_hi_{hash}.wav      # Pre-generated greeting
waiting_hi_{hash}.wav       # Pre-generated waiting message
{call_sid}_{hash}.wav       # Per-call AI responses
```

### File Lifecycle
1. **Generated**: TTS creates WAV file in `audio_output/`
2. **Served**: Flask serves via `/audio/<filename>`
3. **Played**: Twilio downloads and plays
4. **Retention**: Files kept for debugging (optional cleanup)

---

## 8. Webhook Security (Optional)

```
Twilio Webhook
│
├─> Validate Twilio Signature (optional)
│   └─> Prevents spoofed webhooks
│
└─> Process Request
    └─> Always return valid TwiML (even on error)
```

---

## 9. Performance Optimization

### Async Processing
- **STT**: 2-5 seconds (CPU), <1 second (GPU)
- **LLM**: 1-3 seconds (Groq API)
- **TTS**: 1-3 seconds (CPU), <1 second (GPU)
- **Total**: 6-12 seconds (CPU), 3-5 seconds (GPU)

### Caching
- **Greeting Audio**: Pre-generated at startup
- **Waiting Audio**: Pre-generated at startup
- **Model Loading**: Lazy-loaded (MMS TTS on init, Veena on-demand)

---

## 10. Testing Flow

### Local Testing (No Twilio)
```
python local_demo.py
├─> Test STT (Whisper)
├─> Test LLM (Groq)
└─> Test TTS (MMS)
```

### Webhook Testing (No Real Call)
```
python local_twilio_webhook_test.py
├─> Simulate /webhook/incoming
├─> Simulate /webhook/transcription
└─> Verify TwiML responses
```

### End-to-End Testing
```
python make_test_call.py
├─> Start Flask server
├─> Start ngrok tunnel
├─> Initiate Twilio call
└─> Verify complete flow
```

---

## 11. Deployment Flow

### Development
```
1. Run Flask locally (python app.py)
2. Start ngrok tunnel (ngrok http 5000)
3. Update Twilio webhook URL to ngrok URL
4. Test with real calls
```

### Production
```
1. Deploy Flask to cloud server (AWS, GCP, Azure)
2. Set up domain name + SSL
3. Configure Twilio webhook to production URL
4. Set up monitoring and logging
5. Scale as needed (load balancer, multiple servers)
```

---

## 12. Summary

### Key Components
1. **Twilio**: Telephony and audio playback
2. **Flask**: Webhook handler and orchestration
3. **Whisper**: Local STT (free, offline)
4. **Groq**: Cloud LLM (fast, cheap)
5. **MMS TTS**: Local TTS (free, offline)
6. **SQLite**: Local database (call history)

### Key Features
- ✅ **Async Processing**: Prevents webhook timeouts
- ✅ **Polling Mechanism**: Twilio waits for responses
- ✅ **Relative URLs**: Works with dynamic ngrok URLs
- ✅ **Error Handling**: Graceful degradation
- ✅ **Local Models**: Zero API cost for STT/TTS

---

**Last Updated**: 2024
**Version**: 1.0
