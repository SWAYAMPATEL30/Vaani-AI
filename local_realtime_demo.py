"""
Local REAL-TIME Hindi voice chat demo (NO Twilio).

Pipeline (all local where possible):
  Microphone -> Whisper STT (Hindi) -> Groq LLM (Hindi) -> Veena/MMS TTS -> Speaker

Requirements (already mostly in requirements.txt):
  pip install sounddevice soundfile

Run from project root:
  python local_realtime_demo.py

Usage:
  - You will see a prompt: "Press ENTER to start recording, or 'q' + ENTER to quit."
  - Speak in Hindi while it records (default ~5 seconds), then wait.
  - It will:
      1) Transcribe your speech (Whisper, Hindi)
      2) Generate a Hindi reply (Groq)
      3) Speak reply aloud (Veena/MMS TTS) and print text in terminal.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import logging
import queue
import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from config import Config
from services.whisper_local_service import WhisperLocalService
from services.groq_service import GroqService
from services.tts_service import TTSService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("local_realtime_demo")


SAMPLE_RATE = 16000  # 16kHz works well with Whisper and MMS TTS
CHANNELS = 1
RECORD_SECONDS = 5


def record_once(duration_sec: int = RECORD_SECONDS) -> np.ndarray:
    """Record audio from default microphone for a fixed duration."""
    print(f"\n🎙  Recording for {duration_sec} seconds... बोलिए...\n")
    audio = sd.rec(
        int(duration_sec * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )
    sd.wait()
    return audio.squeeze()


def play_audio_file(path: Path):
    """Play a WAV file to the default output device."""
    if not path.exists():
        logger.error(f"Audio file not found for playback: {path}")
        return
    data, sr = sf.read(str(path), dtype="float32")
    print("🔊 बोल रहा हूँ...\n")
    sd.play(data, sr)
    sd.wait()


def main():
    print("\n==== Local Real-Time Hindi Voice Chat (NO Twilio) ====\n")
    print("यह डेमो आपके सिस्टम पर लोकली चलता है।")
    print("Whisper STT (Hindi) + Groq LLM (Hindi) + Veena/MMS TTS (Hindi voice)\n")
    print("Controls:")
    print("  ENTER  → एक बार रिकॉर्ड करें और जवाब सुने")
    print("  q + ENTER → बाहर निकलें\n")

    # Initialize services
    whisper_service = WhisperLocalService(model_size="base")
    if not whisper_service.model:
        print("Whisper मॉडल लोड नहीं हो पाया। कृपया 'openai-whisper' और ffmpeg इंस्टॉल करें।")
        return

    ai_service = GroqService()
    tts_service = TTSService(provider="huggingface")

    conversation_history = []

    while True:
        cmd = input("रिकॉर्ड करने के लिए ENTER दबाएँ (या q + ENTER से बाहर निकलें): ").strip().lower()
        if cmd == "q":
            print("बाहर निकल रहे हैं...")
            break

        # 1) Record from mic
        audio = record_once(RECORD_SECONDS)

        # Convert to WAV bytes in memory
        tmp_path = Path("audio_output") / "local_realtime_input.wav"
        tmp_path.parent.mkdir(exist_ok=True)
        sf.write(str(tmp_path), audio, SAMPLE_RATE)
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()

        # 2) Whisper STT (Hindi)
        print("🧠 Whisper से ट्रांसक्राइब कर रहा हूँ (Hindi)...")
        transcript = whisper_service.transcribe_audio(audio_bytes, language_code="hi")
        if not transcript:
            print("ट्रांसक्रिप्शन फेल हो गया, दोबारा कोशिश करें।\n")
            continue

        print(f"🗣  आप: {transcript}\n")

        # 3) Groq LLM reply in Hindi
        print("🤖 AI जवाब सोच रहा है (Hindi)...")
        response_text = ai_service.generate_response(
            transcript,
            call_id="local_realtime",
            conversation_history=conversation_history[-10:] if len(conversation_history) > 10 else conversation_history,
        )
        if not response_text:
            response_text = "मैं आपकी मदद करने के लिए यहां हूं। कृपया अपना प्रश्न दोहराएं।"

        print(f"🤖 AI: {response_text}\n")

        # Update conversation history
        conversation_history.append({"role": "user", "content": transcript})
        conversation_history.append({"role": "assistant", "content": response_text})

        # 4) Local TTS (Veena/MMS) and playback
        print("🔊 Hindi TTS जेनरेट कर रहा हूँ (Veena/MMS)...")
        language_code = Config.LANGUAGE_CODE.split("-")[0] if "-" in Config.LANGUAGE_CODE else "hi"
        audio_url = tts_service.text_to_speech(
            response_text,
            call_sid="local_realtime",
            language_code=language_code,
        )
        if not audio_url:
            print("TTS फेल हो गया, टेक्स्ट ऊपर दिखाया गया है।\n")
            continue

        filename = audio_url.rsplit("/", 1)[-1]
        tts_path = Path("audio_output") / filename
        play_audio_file(tts_path)

        print("✅ अगला मैसेज बोलने के लिए फिर से ENTER दबाएँ।\n")


if __name__ == "__main__":
    main()

