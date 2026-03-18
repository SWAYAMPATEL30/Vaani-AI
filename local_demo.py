"""
Local demo script (NO Twilio) to test:
- Whisper STT (local)
- Groq LLM (Hindi)
- Veena / MMS TTS (local)

Flow:
1. You provide a Hindi WAV file path (16k–24k mono recommended).
2. Script transcribes it with local Whisper.
3. Sends transcript to Groq LLM for Hindi response.
4. Generates Hindi speech locally with Veena/MMS and saves output WAV.

Run:
    python local_demo.py --input path/to/input.wav --output output.wav
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import argparse
import logging
from pathlib import Path

from config import Config
from services.whisper_local_service import WhisperLocalService
from services.groq_service import GroqService
from services.tts_service import TTSService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("local_demo")


def run_demo(input_path: Path, output_path: Path):
    # STT: local Whisper (Hindi)
    whisper_service = WhisperLocalService(model_size="base")
    if not whisper_service.model:
        logger.error("Whisper model not loaded. Install 'openai-whisper' and ffmpeg.")
        return

    # LLM: Groq (configured to speak Hindi in system prompt)
    ai_service = GroqService()

    # TTS: local Veena/MMS via HuggingFace TTS provider
    tts_service = TTSService(provider="huggingface")

    logger.info(f"Loading audio from: {input_path}")
    with open(input_path, "rb") as f:
        audio_bytes = f.read()

    logger.info("Transcribing with local Whisper (Hindi)...")
    transcript = whisper_service.transcribe_audio(audio_bytes, language_code="hi")
    if not transcript:
        logger.error("Whisper transcription failed.")
        return

    print(f"\n🗣  Transcript (Whisper, Hindi): {transcript}\n")

    logger.info("Generating Hindi response from Groq LLM...")
    response_text = ai_service.generate_response(
        transcript,
        call_id="local_demo",
        conversation_history=[],
    )
    if not response_text:
        response_text = "मैं आपकी मदद करने के लिए यहां हूं।"

    print(f"🤖 LLM Response (Hindi): {response_text}\n")

    logger.info("Generating local TTS audio (Veena/MMS)...")
    language_code = Config.LANGUAGE_CODE.split("-")[0] if "-" in Config.LANGUAGE_CODE else "hi"
    audio_url = tts_service.text_to_speech(
        response_text,
        call_sid="local_demo",
        language_code=language_code,
    )
    if not audio_url:
        logger.error("Local TTS failed.")
        return

    # audio_url is something like WEBHOOK_BASE_URL/audio/filename.wav
    filename = audio_url.rsplit("/", 1)[-1]
    src_path = Path("audio_output") / filename

    if not src_path.exists():
        logger.error(f"TTS file not found at expected path: {src_path}")
        return

    # Copy/rename to requested output path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.replace(output_path)

    print(f"🔊 TTS audio saved to: {output_path}")
    print("You can play this file locally to hear Hindi Veena/MMS voice.\n")


def main():
    parser = argparse.ArgumentParser(description="Local STT → LLM → TTS Hindi demo (no Twilio).")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input Hindi WAV file to transcribe.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="local_demo_output.wav",
        help="Path where output TTS WAV will be saved.",
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Input file does not exist: {input_path}")
        sys.exit(1)

    run_demo(input_path, output_path)


if __name__ == "__main__":
    main()

