# 🚀 Quick Start: Hugging Face Integration

## ⚡ 3 Steps to Use Whisper + Mistral + VibeVoice

### 1. Add Token to `.env`

```env
HUGGINGFACE_TOKEN=hf_YOUR_HUGGINGFACE_TOKEN
```

### 2. Configure Providers

Add to `.env`:

```env
# Use Whisper for speech-to-text
STT_PROVIDER=huggingface

# Use Mistral for answering
AI_PROVIDER=huggingface

# Use VibeVoice for text-to-speech
TTS_PROVIDER=vibevoice
```

### 3. Restart Server

```bash
python app.py
```

## ✅ That's It!

- **Phone calls** will automatically use Whisper when `STT_PROVIDER=huggingface`
- **AI responses** will use Mistral when `AI_PROVIDER=huggingface`
- **Voice output** will use VibeVoice when `TTS_PROVIDER=vibevoice`

## 🧪 Test It

```bash
# Check health
curl http://localhost:5000/health

# Test audio processing
curl -X POST http://localhost:5000/api/process-audio \
  -F "audio=@test.wav" \
  -F "call_sid=test123"
```

## 📚 Full Documentation

See `HUGGINGFACE_SETUP.md` for detailed configuration and troubleshooting.
