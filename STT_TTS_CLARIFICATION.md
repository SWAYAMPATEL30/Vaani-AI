# STT vs TTS - Current System Architecture

## Speech-to-Text (STT) - What YOU Say → Text

**Service Used: Whisper (OpenAI Whisper)**

### Flow:
1. **PRIMARY**: Local Whisper (`openai-whisper` package)
   - Model: `base` (can be upgraded to `small`, `medium`, `large`)
   - Runs locally, no API needed
   - Supports Hindi transcription

2. **FALLBACK 1**: OpenAI Whisper API
   - If local Whisper fails

3. **FALLBACK 2**: AssemblyAI
   - Uses Whisper internally
   - If OpenAI API fails

### Code Location:
- `services/whisper_local_service.py` - Local Whisper implementation
- `services/huggingface_asr_service.py` - Orchestrates STT with fallbacks
- `app.py` → `handle_recording()` - Processes user's speech

---

## Text-to-Speech (TTS) - AI Text → Speech Audio

**Service Used: Veena TTS (or MMS TTS as fallback)**

### Flow:
1. **PRIMARY**: Veena TTS (`maya-research/veena-tts`)
   - Supports Hindi and English
   - 4 voices: kavya, agastya, maitri, vinaya
   - 24kHz audio output

2. **FALLBACK 1**: Facebook MMS TTS Hindi
   - If Veena fails

3. **FALLBACK 2**: Hugging Face Inference API
   - If local models fail

4. **FALLBACK 3**: Twilio Say (English)
   - Guaranteed to work, but English only

### Code Location:
- `services/veena_tts_service.py` - Veena TTS implementation
- `services/mms_tts_local_service.py` - MMS TTS implementation
- `services/huggingface_tts_service.py` - Orchestrates TTS with fallbacks
- `app.py` → `handle_recording()` - Converts AI response to speech

---

## Complete Call Flow:

```
1. User speaks in Hindi
   ↓
2. STT (Whisper) → Transcribes to text: "नमस्ते, मैं मदद चाहता हूं"
   ↓
3. LLM (Groq) → Generates Hindi response: "नमस्ते! मैं आपकी कैसे मदद कर सकती हूं?"
   ↓
4. TTS (Veena) → Converts to Hindi speech audio
   ↓
5. Twilio Play → Plays audio to user
```

---

## Summary:

- **STT = Whisper** (converts YOUR speech → text)
- **TTS = Veena/MMS TTS** (converts AI text → speech)

Both are separate services working together!
