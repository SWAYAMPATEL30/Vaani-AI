# 🤗 Hugging Face Integration Setup

This guide explains how to use **Whisper Large** (STT), **Mistral-7B-Instruct** (LLM), and **VibeVoice-1.5B** (TTS) via Hugging Face Inference API.

## 📋 Prerequisites

1. **Hugging Face Account**: Sign up at https://huggingface.co/
2. **Access Token**: Get your token from https://huggingface.co/settings/tokens
   - Token provided: `hf_YOUR_HUGGINGFACE_TOKEN`

## 🔧 Configuration

Add these environment variables to your `.env` file:

```env
# Hugging Face Token (REQUIRED for all HF services)
HUGGINGFACE_TOKEN=hf_YOUR_HUGGINGFACE_TOKEN

# Speech-to-Text Provider: 'assemblyai' or 'huggingface'/'hf'
STT_PROVIDER=huggingface
HF_ASR_MODEL=openai/whisper-large

# AI Provider: 'groq', 'gemini', 'openai', or 'huggingface'/'hf'
AI_PROVIDER=huggingface
HF_LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.3
HF_LLM_MAX_TOKENS=200
HF_LLM_TEMPERATURE=0.7

# Text-to-Speech Provider: 'elevenlabs', 'google', or 'vibevoice'/'huggingface'/'hf'
TTS_PROVIDER=vibevoice
HF_TTS_MODEL=microsoft/VibeVoice-1.5B
```

## 🎯 Quick Start

### Option 1: Use All Hugging Face Services

```env
HUGGINGFACE_TOKEN=hf_YOUR_HUGGINGFACE_TOKEN
STT_PROVIDER=huggingface
AI_PROVIDER=huggingface
TTS_PROVIDER=vibevoice
```

### Option 2: Mix and Match

You can use Hugging Face for one service and others for the rest:

```env
# Use Whisper for STT, but keep Groq for LLM and ElevenLabs for TTS
HUGGINGFACE_TOKEN=hf_YOUR_HUGGINGFACE_TOKEN
STT_PROVIDER=huggingface
AI_PROVIDER=groq
TTS_PROVIDER=elevenlabs
```

## 📞 Twilio Call Flow

When `STT_PROVIDER=huggingface`, the system automatically:

1. Uses `<Record>` instead of `<Gather>` to capture raw audio
2. Downloads the recording from Twilio
3. Sends audio to Whisper Large via Hugging Face Inference API
4. Processes the transcription with your configured LLM (Mistral if `AI_PROVIDER=huggingface`)
5. Generates TTS response (VibeVoice if `TTS_PROVIDER=vibevoice`)

## 🧪 Testing

### Test Audio Processing Endpoint

```bash
curl -X POST http://localhost:5000/api/process-audio \
  -F "audio=@test_audio.wav" \
  -F "call_sid=test123"
```

This will:
- Transcribe with Whisper (if `STT_PROVIDER=huggingface`)
- Generate response with Mistral (if `AI_PROVIDER=huggingface`)
- Generate audio with VibeVoice (if `TTS_PROVIDER=vibevoice`)

### Check Health

```bash
curl http://localhost:5000/health
```

Response will show:
```json
{
  "services": {
    "stt_provider": "huggingface",
    "ai_provider": "huggingface",
    "tts_provider": "vibevoice",
    "huggingface": true
  }
}
```

## 🔍 Models Used

### Speech-to-Text
- **Model**: `openai/whisper-large`
- **Hugging Face**: https://huggingface.co/openai/whisper-large
- **Features**: High accuracy, multilingual support

### LLM (Answering)
- **Model**: `mistralai/Mistral-7B-Instruct-v0.3`
- **Hugging Face**: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
- **Features**: Instruction-tuned, conversational

### Text-to-Speech
- **Model**: `microsoft/VibeVoice-1.5B`
- **Hugging Face**: https://huggingface.co/microsoft/VibeVoice-1.5B
- **GitHub**: https://github.com/microsoft/VibeVoice
- **Features**: Long-form generation, multi-speaker support

## ⚠️ Important Notes

1. **Rate Limits**: Hugging Face Inference API has rate limits for free tier
   - Consider upgrading if you need higher throughput
   - See: https://huggingface.co/pricing

2. **Model Loading**: First request to each model may take longer (cold start)
   - Subsequent requests are faster

3. **Audio Format**: Whisper accepts various formats (WAV, MP3, M4A, etc.)
   - Twilio recordings are typically WAV format

4. **Token Security**: Never commit your Hugging Face token to git
   - Always use `.env` file (which should be in `.gitignore`)

## 🐛 Troubleshooting

### "HuggingFace ASR may be rate-limited"
- Check your token is valid
- Verify token has access to the models
- Check rate limits at https://huggingface.co/settings/billing

### "Unexpected ASR response format"
- Model may be loading (wait a few seconds and retry)
- Check model name is correct: `openai/whisper-large`

### "Empty TTS audio response"
- VibeVoice model may need time to load
- Check model name: `microsoft/VibeVoice-1.5B`

### Recording webhook not working
- Ensure Twilio credentials are configured
- Check `WEBHOOK_BASE_URL` is accessible from internet (use ngrok for local testing)
- Verify `/webhook/recording` endpoint is reachable

## 📚 Additional Resources

- Hugging Face Inference API Docs: https://huggingface.co/docs/api-inference
- Whisper Model Card: https://huggingface.co/openai/whisper-large
- Mistral Model Card: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3
- VibeVoice GitHub: https://github.com/microsoft/VibeVoice

---

**Ready to use!** Set your `.env` variables and restart the server. 🚀
