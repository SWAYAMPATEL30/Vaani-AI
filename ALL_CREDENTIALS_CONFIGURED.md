# ✅ Credentials Configuration Guide

## Setting Up Your Credentials

All credentials should be placed in your `.env` file (copy from `.env.example`).
**Never commit real credentials to version control.**

### Required Services

1. **Twilio** (Telephony)
   - Get from: https://console.twilio.com/
   - Variables: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`

2. **Groq** (LLM - Recommended)
   - Get from: https://console.groq.com/
   - Variable: `GROQ_API_KEY`

3. **AssemblyAI** (Cloud STT - Optional, local Whisper is default)
   - Get from: https://www.assemblyai.com/
   - Variable: `ASSEMBLYAI_API_KEY`

### Optional Services

4. **OpenAI** (Alternative LLM)
   - Get from: https://platform.openai.com/api-keys
   - Variable: `OPENAI_API_KEY`

5. **ElevenLabs** (Cloud TTS - Optional, local MMS TTS is default)
   - Get from: https://elevenlabs.io/app/settings/api-keys
   - Variables: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`

6. **Exotel** (Alternative telephony)
   - Get from: https://my.exotel.com/
   - Variables: `EXOTEL_API_KEY`, `EXOTEL_API_TOKEN`, `EXOTEL_SUBDOMAIN`

7. **ngrok** (Local tunnel for development)
   - Get from: https://dashboard.ngrok.com/
   - Configure: `ngrok config add-authtoken YOUR_TOKEN`

8. **PostgreSQL** (Production database)
   - Variable: `DATABASE_URL=postgresql://user:password@host:5432/dbname`
   - Providers: Supabase, Neon, Render Postgres, Railway

## 📊 Service Status Tracking

| Service | Required | Default |
|---------|----------|---------|
| Twilio | ✅ Yes | — |
| Groq | ✅ Yes (LLM) | llama-3.3-70b-versatile |
| Whisper STT | ✅ Yes (local) | openai/whisper-large |
| MMS TTS | ✅ Yes (local) | facebook/mms-tts-hin |
| AssemblyAI | ❌ Optional | — |
| OpenAI | ❌ Optional | — |
| ElevenLabs | ❌ Optional | — |
| Exotel | ❌ Optional | — |
| ngrok | Dev only | — |
| PostgreSQL | Prod only | SQLite (dev) |

## 🚀 Quick Setup Checklist

- [ ] Copied `.env.example` to `.env`
- [ ] Added `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- [ ] Added `GROQ_API_KEY`
- [ ] (Optional) Added `DATABASE_URL` for PostgreSQL
- [ ] Started server: `python app.py`
- [ ] Started ngrok: `ngrok http 5000`
- [ ] Updated Twilio webhook URL to ngrok URL
