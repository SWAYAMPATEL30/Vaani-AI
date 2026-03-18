# Complete Technology Stack - Voice Calling Agent

## 🎯 Overview
This is a **fully open-source, local-first** voice calling agent that uses Hindi language for conversations. All STT and TTS models run locally on your machine.

---

## 📦 Core Technologies

### **Web Framework**
- **Flask 3.0.0** - Python web framework for handling webhooks
- **Flask-CORS 4.0.0** - Cross-origin resource sharing
- **Werkzeug 3.0.1** - WSGI utilities
- **Gunicorn 21.2.0** - Production WSGI server

### **Database**
- **SQLAlchemy 2.0.23** - ORM for database operations
- **Flask-SQLAlchemy 3.1.1** - Flask integration
- **SQLite** - Local database (default: `instance/voice_agent.db`)
- **PostgreSQL** - Optional (via `psycopg2-binary`)

### **Telephony Platform**
- **Twilio 9.0.0** - Phone call management, webhooks, audio playback
- **ngrok** - Public URL tunneling for local development

---

## 🧠 AI/ML Models & Services

### **1. Speech-to-Text (STT) - What You Say → Text**

#### **PRIMARY: Local Whisper (Open-Source) ✅**
- **Model**: OpenAI Whisper `base` (139MB)
- **Package**: `openai-whisper>=20250625`
- **Location**: `services/whisper_local_service.py`
- **Status**: ✅ **ACTIVE** - Runs completely offline
- **Language Support**: Hindi, English, and 99+ languages
- **Speed**: ~2-5 seconds per audio clip (CPU)

#### **FALLBACK 1: OpenAI Whisper API**
- **Service**: OpenAI API
- **Status**: Available but not used (local-first)

#### **FALLBACK 2: AssemblyAI**
- **Service**: AssemblyAI API
- **Status**: Available but not used (local-first)

---

### **2. Large Language Model (LLM) - Text → Response**

#### **PRIMARY: Groq LLM ✅**
- **Model**: `llama-3.3-70b-versatile` (via Groq API)
- **Service**: Groq Cloud API
- **Package**: `groq==0.4.1`
- **Location**: `services/groq_service.py`
- **Status**: ✅ **ACTIVE**
- **Language**: Generates Hindi responses
- **Speed**: ~1-3 seconds per response

#### **ALTERNATIVES (Available but not active):**
- **Google Gemini**: `gemini-pro` (via `google-generativeai`)
- **OpenAI GPT**: `gpt-4o-mini` (via `openai`)
- **Hugging Face LLM**: `mistralai/Mistral-7B-Instruct-v0.3` (local)

---

### **3. Text-to-Speech (TTS) - Response Text → Hindi Audio**

#### **PRIMARY: Facebook MMS TTS Hindi (Local) ✅**
- **Model**: `facebook/mms-tts-hin`
- **Package**: `transformers>=4.30.0`, `torchaudio>=2.0.0`
- **Location**: `services/mms_tts_local_service.py`
- **Status**: ✅ **ACTIVE** - Runs completely offline
- **Language**: Hindi only
- **Speed**: ~5-10 seconds per sentence (CPU)
- **Audio Format**: WAV, 16kHz

#### **FALLBACK 1: Veena TTS (Local)**
- **Model**: `maya-research/veena-tts`
- **Package**: `snac>=0.1.0`, `bitsandbytes>=0.41.0`
- **Location**: `services/veena_tts_service.py`
- **Status**: Available (lazy-loaded if MMS fails)
- **Language**: Hindi + English
- **Voices**: kavya, agastya, maitri, vinaya
- **Audio Format**: WAV, 24kHz
- **Speed**: Very slow on CPU (minutes), fast on GPU

#### **FALLBACK 2: Hugging Face Inference API**
- **Status**: Disabled (local-only mode)

#### **ALTERNATIVES (Available but not active):**
- **ElevenLabs**: Premium TTS API (`elevenlabs==0.2.27`)
- **Google Cloud TTS**: (`google-cloud-texttospeech==2.14.2`)
- **VibeVoice**: Via Hugging Face

---

## 🛠️ Audio Processing Libraries

- **pydub 0.25.1** - Audio manipulation
- **wave 0.0.2** - WAV file handling
- **scipy>=1.10.0** - Scientific computing (audio processing)
- **soundfile>=0.12.0** - Audio file I/O
- **torchaudio>=2.0.0** - PyTorch audio processing
- **transformers>=4.30.0** - Hugging Face transformers

---

## 🔧 Utilities & Dependencies

- **python-dotenv 1.0.0** - Environment variable management
- **requests 2.31.0** - HTTP requests
- **python-dateutil 2.8.2** - Date/time utilities
- **uuid 1.30** - Unique ID generation
- **python-json-logger 2.0.7** - Structured logging
- **alembic 1.12.1** - Database migrations

---

## 📁 Project Structure

```
voice/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── models.py                       # Database models (Call, CallTranscript)
├── requirements.txt                # Python dependencies
│
├── services/
│   ├── whisper_local_service.py    # Local Whisper STT
│   ├── huggingface_asr_service.py  # STT orchestrator
│   ├── groq_service.py             # Groq LLM
│   ├── mms_tts_local_service.py    # Facebook MMS TTS (PRIMARY)
│   ├── veena_tts_service.py       # Veena TTS (FALLBACK)
│   ├── huggingface_tts_service.py # TTS orchestrator
│   ├── tts_service.py             # Main TTS service
│   └── call_manager.py            # Twilio call flow management
│
├── audio_output/                   # Generated audio files
├── instance/
│   └── voice_agent.db             # SQLite database
│
└── [various setup/test scripts]
```

---

## 🔄 Complete Call Flow

```
1. User receives call from Twilio
   ↓
2. Flask webhook: /webhook/incoming
   ↓
3. Play greeting (pre-generated Hindi TTS)
   ↓
4. Gather speech input (Twilio)
   ↓
5. Webhook: /webhook/transcription
   ↓
6. STT: Local Whisper → Transcribe Hindi speech to text
   ↓
7. LLM: Groq → Generate Hindi response
   ↓
8. TTS: Facebook MMS TTS → Convert response to Hindi audio
   ↓
9. Twilio <Play> → Play audio to user
   ↓
10. Loop back to step 4 (continue conversation)
```

---

## 🌐 Current Active Configuration

### **STT (Speech-to-Text)**
- ✅ **Provider**: `huggingface` (local Whisper)
- ✅ **Model**: OpenAI Whisper `base` (local)
- ✅ **Language**: Hindi (`hi-IN`)

### **LLM (Language Model)**
- ✅ **Provider**: `groq`
- ✅ **Model**: `llama-3.3-70b-versatile`
- ✅ **Language**: Hindi responses

### **TTS (Text-to-Speech)**
- ✅ **Provider**: `huggingface` (local models)
- ✅ **Primary Model**: Facebook MMS TTS Hindi (local)
- ✅ **Fallback Model**: Veena TTS (local, lazy-loaded)
- ✅ **Language**: Hindi

### **Telephony**
- ✅ **Provider**: Twilio
- ✅ **Webhook URL**: ngrok tunnel (public HTTPS)
- ✅ **Audio Format**: WAV, mulaw 8kHz (Twilio requirement)

---

## 💾 Model Storage

- **Whisper Base**: `~/.cache/whisper/` (~139MB)
- **MMS TTS Hindi**: `~/.cache/huggingface/hub/` (~500MB)
- **Veena TTS**: `~/.cache/huggingface/hub/` (~2-4GB)
- **Audio Output**: `audio_output/` (WAV files)

---

## 🔐 Required API Keys (Environment Variables)

### **Required:**
- `TWILIO_ACCOUNT_SID` - Twilio account
- `TWILIO_AUTH_TOKEN` - Twilio authentication
- `TWILIO_PHONE_NUMBER` - Your Twilio phone number
- `GROQ_API_KEY` - Groq LLM API
- `WEBHOOK_BASE_URL` - Public URL (ngrok for local dev)

### **Optional (for fallbacks):**
- `ASSEMBLYAI_API_KEY` - AssemblyAI STT (not used)
- `OPENAI_API_KEY` - OpenAI API (not used)
- `GEMINI_API_KEY` - Google Gemini (not used)
- `HUGGINGFACE_TOKEN` - HF Inference API (not used)

---

## 🎯 Key Features

✅ **100% Open-Source STT/TTS** - All models run locally  
✅ **Hindi Language Support** - Full conversation in Hindi  
✅ **No Twilio Say** - Uses only open-source TTS models  
✅ **Async Processing** - Prevents Twilio webhook timeouts  
✅ **Database Logging** - All calls and transcripts stored  
✅ **Error Handling** - Graceful fallbacks at every step  
✅ **Production Ready** - Gunicorn, PostgreSQL support  

---

## 📊 Performance Metrics

- **STT (Whisper)**: ~2-5 seconds per audio clip
- **LLM (Groq)**: ~1-3 seconds per response
- **TTS (MMS)**: ~5-10 seconds per sentence
- **Total Response Time**: ~8-18 seconds (acceptable for voice calls)

---

## 🚀 Deployment Options

- **Local Development**: Flask dev server + ngrok
- **Production**: Gunicorn + PostgreSQL + public domain
- **Cloud**: Render, Heroku, AWS, GCP, Azure

---

## 📝 Summary

This voice calling agent uses:
- **Local Whisper** for STT (open-source, offline)
- **Groq LLM** for AI responses (cloud API, fast)
- **Local MMS/Veena TTS** for Hindi speech (open-source, offline)
- **Twilio** for call management (cloud, reliable)
- **Flask** for webhooks (Python, lightweight)
- **SQLite/PostgreSQL** for data storage

**Total Cost**: Only Groq API costs (~$0.10 per 1M tokens) + Twilio call costs. STT and TTS are completely free (local).
