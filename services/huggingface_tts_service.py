"""
Local Hugging Face TTS orchestration service.

This service **does not** call any external Hugging Face Inference APIs.
Instead it coordinates fully local, open‑source TTS models:

- Primary: Facebook MMS TTS Hindi (`facebook/mms-tts-hin`) via `MMSTTSLocalService`
- Fallback: Veena TTS (`maya-research/veena-tts`) via `VeenaTTSService`
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HuggingFaceTTSService:
    """Text‑to‑speech using local MMS + Veena TTS models (no external APIs)."""

    def __init__(self, token=None, model=None):
        # token/model are kept for backwards compatibility but are not used,
        # because we run everything locally.
        self.token = token
        self.model = model

        self.audio_storage_path = Path("audio_output")
        self.audio_storage_path.mkdir(exist_ok=True)

        # PRIMARY: Use local Facebook MMS TTS Hindi model (FAST - loads in seconds)
        try:
            from services.mms_tts_local_service import MMSTTSLocalService
            self.mms_tts_local = MMSTTSLocalService()
            logger.info("Local Facebook MMS TTS Hindi service initialized (PRIMARY - FAST)")
        except Exception as e:
            logger.warning(f"Local MMS TTS not available: {e}")
            self.mms_tts_local = None
        
        # FALLBACK: Use Veena TTS (SLOW on CPU - loads in minutes/hours, use only if MMS fails)
        # Lazy load Veena only when needed (not during initialization)
        self.veena_tts = None
        self._veena_tts_class = None
        try:
            from services.veena_tts_service import VeenaTTSService
            self._veena_tts_class = VeenaTTSService
            logger.info("Veena TTS class available (will be loaded on-demand if MMS fails)")
        except Exception as e:
            logger.warning(f"Veena TTS not available: {e}")
            logger.warning("Install: pip install transformers torch torchaudio snac bitsandbytes")
            self._veena_tts_class = None

        logger.info("HuggingFace TTS initialized (PRIMARY: Local MMS TTS, FALLBACK: Veena TTS)")

    def text_to_speech(self, text, call_sid=None, language_code='hi'):
        """
        Convert text to speech using Facebook MMS TTS Hindi
        Model: https://huggingface.co/facebook/mms-tts-hin
        PRIMARY: MMS TTS (FAST - loads in seconds)
        FALLBACK: Veena TTS (SLOW - loads on-demand only if MMS fails)
        Args:
            text: Text to convert (Hindi text)
            call_sid: Call SID for filename
            language_code: Language code (default: 'hi' for Hindi)
        Returns: URL to audio file or None
        """
        if not text:
            return None

        # PRIMARY: Use local Facebook MMS TTS Hindi model (FAST - loads in seconds)
        if self.mms_tts_local:
            try:
                result = self.mms_tts_local.text_to_speech(text, call_sid, language_code)
                if result:
                    logger.info("Successfully generated audio using Local MMS TTS (PRIMARY)")
                    return result
            except Exception as e:
                logger.warning(f"Local MMS TTS failed: {e}, trying Veena TTS fallback...")
        
        # FALLBACK: Use Veena TTS (SLOW - lazy load only when needed)
        if self._veena_tts_class and not self.veena_tts:
            # Lazy load Veena TTS only if MMS fails (to avoid slow startup)
            try:
                logger.info("Lazy loading Veena TTS (this may take several minutes on CPU)...")
                self.veena_tts = self._veena_tts_class()
                logger.info("Veena TTS loaded successfully")
            except Exception as e:
                logger.error(f"Failed to lazy load Veena TTS: {e}")
                self.veena_tts = None
        
        if self.veena_tts:
            try:
                result = self.veena_tts.text_to_speech(text, call_sid, language_code)
                if result:
                    logger.info("Successfully generated audio using Veena TTS (FALLBACK)")
                    return result
            except Exception as e:
                logger.warning(f"Veena TTS failed: {e}")

        # All TTS methods failed
        logger.error("All local TTS methods (MMS/Veena) failed")
        return None

