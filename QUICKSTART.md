# 🚀 Quick Start Guide

Get your Smart Voice Calling Agent running in 5 minutes!

## Step 1: Install Dependencies

```bash
cd voice
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure API Keys

Create `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env and add your keys:
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
```

## Step 3: Initialize Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Step 4: Run Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

## Step 5: Test It!

### Health Check
```bash
curl http://localhost:5000/health
```

### Test Audio Processing
```bash
curl -X POST http://localhost:5000/api/process-audio \
  -F "audio=@your_audio_file.mp3"
```

## 🎯 Next Steps

1. **Get API Keys** (if you don't have them):
   - OpenAI:
   
   - ElevenLabs: https://elevenlabs.io/app/settings/api-keys

2. **Set up Telephony**:
   - Exotel: https://exotel.com/
   - Twilio: https://www.twilio.com/

3. **Deploy**:
   - Render: Connect GitHub repo
   - Railway: Push to Railway
   - See README.md for details

## ✅ You're Ready!

Your voice agent is now running locally. Configure webhooks in your telephony provider to start receiving calls!

