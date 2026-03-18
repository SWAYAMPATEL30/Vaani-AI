"""
Hugging Face Whisper (ASR) Service - Uses Local Whisper Model
Based on OpenAI Whisper: https://github.com/openai/whisper
Hugging Face Inference API endpoints are deprecated/not available for Whisper
"""

import logging

logger = logging.getLogger(__name__)


class HuggingFaceASRService:
    """
    Speech-to-text service using OpenAI Whisper locally.
    Based on: https://github.com/openai/whisper
    Since HF endpoints return 410/404, this uses a **local Whisper installation only**
    and does **not** call any external STT APIs.
    """

    def __init__(self, token=None, model=None):
        from config import Config

        self.token = token or Config.HUGGINGFACE_TOKEN
        self.model = model or Config.HF_ASR_MODEL or "openai/whisper-large"
        
        # PRIMARY: Use local Whisper (most reliable, no API needed)
        # Based on: https://github.com/openai/whisper
        try:
            from services.whisper_local_service import WhisperLocalService
            # Use 'base' model for good balance (can be changed to 'small', 'medium', 'large', 'turbo')
            self.whisper_local = WhisperLocalService(model_size='base')
            logger.info("Local Whisper service initialized (PRIMARY) - Based on OpenAI Whisper")
        except Exception as e:
            logger.warning(f"Local Whisper not available: {e}. Install: pip install -U openai-whisper")
            logger.warning("Also ensure ffmpeg is installed on your system")
            self.whisper_local = None
        
        # NOTE: User requirement is to run **locally only**, without external STT APIs.
        # So we DO NOT initialize AssemblyAI or OpenAI Whisper API here.
        self.assemblyai_service = None
        self.openai_whisper_service = None
        
        logger.info("HuggingFace ASR service initialized (LOCAL ONLY: OpenAI Whisper)")

    def transcribe_audio(self, audio_file, language_code='hi'):
        """
        Transcribe an audio file using local Whisper.
        Based on OpenAI Whisper: https://github.com/openai/whisper
        """
        # PRIMARY: Local Whisper (no API needed)
        if self.whisper_local:
            try:
                result = self.whisper_local.transcribe_audio(audio_file, language_code)
                if result:
                    logger.info("Successfully transcribed using Local Whisper")
                    return result
            except Exception as e:
                logger.error(f"Local Whisper failed: {e}")
                # Local-only mode: do NOT call external APIs, just fail gracefully.
                return None
        
        # If we get here, local Whisper is not available or failed
        logger.error("Whisper local transcription failed and no external STT APIs are enabled (local-only mode)")
        return None

