# 🔐 Environment Setup

## Quick Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API keys:**

## Required API Keys

### ✅ AssemblyAI (Already Provided)
```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
```

### 🔑 OpenAI (Required for AI responses)
Get your key from: https://platform.openai.com/api-keys
```
OPENAI_API_KEY=sk-your-key-here
```

### 🎤 Text-to-Speech (Choose one)

#### Option 1: ElevenLabs (Recommended - Best quality)
Get your key from: https://elevenlabs.io/app/settings/api-keys
```
ELEVENLABS_API_KEY=your-key-here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Optional, uses default if not set
TTS_PROVIDER=elevenlabs
```

#### Option 2: Google Cloud TTS
1. Create a project at: https://console.cloud.google.com/
2. Enable Text-to-Speech API
3. Create service account and download JSON credentials
4. Set in .env:
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your-credentials.json
GOOGLE_TTS_VOICE_NAME=en-US-Wavenet-D
TTS_PROVIDER=google
```

## Optional: Telephony Setup

### Exotel
```
EXOTEL_API_KEY=your-key
EXOTEL_API_TOKEN=your-token
EXOTEL_SUBDOMAIN=your-subdomain
```

### Twilio
```
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=+1234567890
```

## Database (Optional - defaults to SQLite)

### SQLite (Default - for development)
```
DATABASE_URL=sqlite:///voice_agent.db
```

### PostgreSQL (Recommended for production)
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Server Configuration

```
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
HOST=0.0.0.0
WEBHOOK_BASE_URL=http://localhost:5000  # Update after deployment
```

## Minimum Setup for Testing

For basic testing, you only need:
1. ✅ AssemblyAI (already provided)
2. 🔑 OpenAI API key
3. 🎤 Either ElevenLabs OR Google TTS

Everything else is optional and can be added later!




