"""
VibeVoice TTS Service via Hugging Face Inference API.

Model reference: microsoft/VibeVoice-1.5B
See: https://huggingface.co/microsoft/VibeVoice-1.5B
Repo: https://github.com/microsoft/VibeVoice
"""

import logging
from pathlib import Path

from services.huggingface_client import HuggingFaceInferenceClient

logger = logging.getLogger(__name__)


class VibeVoiceTTSService:
    """Text-to-speech via Hugging Face Inference API (audio bytes response)."""

    def __init__(self, token=None, model=None):
        from config import Config

        self.token = token or Config.HUGGINGFACE_TOKEN
        self.model = model or Config.HF_TTS_MODEL or "microsoft/VibeVoice-1.5B"
        self.client = HuggingFaceInferenceClient(self.token, timeout_s=120)

        self.audio_storage_path = Path("audio_output")
        self.audio_storage_path.mkdir(exist_ok=True)

        if not self.token:
            logger.warning("HUGGINGFACE_TOKEN not found. VibeVoice TTS may be rate-limited or unavailable.")

        logger.info(f"VibeVoice TTS initialized with model: {self.model}")

    def text_to_speech(self, text, call_sid=None):
        """
        Convert text to audio (WAV/MP3 depending on endpoint). Returns URL to saved audio file.
        """
        if not text:
            return None

        try:
            payload = {"inputs": text}
            resp = self.client.post_json(self.model, payload)

            # Some HF TTS endpoints return audio bytes directly; others return JSON.
            content_type = resp.headers.get("content-type", "")
            if "application/json" in content_type.lower():
                data = resp.json()
                logger.error(f"Unexpected TTS JSON response: {data}")
                return None

            audio_bytes = resp.content
            if not audio_bytes:
                logger.error("Empty TTS audio response")
                return None

            # Prefer wav extension as HF often returns audio/wav.
            filename = f"{call_sid or 'audio'}_{hash(text)}.wav"
            filepath = self.audio_storage_path / filename
            with open(filepath, "wb") as f:
                f.write(audio_bytes)

            from config import Config
            return f"{Config.WEBHOOK_BASE_URL}/audio/{filename}"

        except Exception as e:
            logger.error(f"Error in VibeVoice TTS: {str(e)}", exc_info=True)
            return None

