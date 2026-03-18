"""
OpenAI Whisper Local Service
Uses the official openai-whisper Python package for local transcription
Based on: https://github.com/openai/whisper
"""
import logging
import whisper
from io import BytesIO
import tempfile
import os

logger = logging.getLogger(__name__)


class WhisperLocalService:
    """Speech-to-text using OpenAI Whisper locally (no API needed)"""

    def __init__(self, model_size='base'):
        """
        Initialize Whisper local service
        Args:
            model_size: Model size ('tiny', 'base', 'small', 'medium', 'large', 'turbo')
                       Default: 'base' (good balance of speed and accuracy)
        """
        self.model_size = model_size
        self.model = None
        
        try:
            logger.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
            logger.info(f"Whisper model '{model_size}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            logger.error("Make sure 'openai-whisper' is installed: pip install -U openai-whisper")
            logger.error("Also ensure ffmpeg is installed on your system")
            self.model = None

    def transcribe_audio(self, audio_file, language_code='hi'):
        """
        Transcribe an audio file using Whisper
        Args:
            audio_file: File object, bytes, or file path
            language_code: Language code (default: 'hi' for Hindi)
        Returns: str | None
        """
        if not self.model:
            logger.error("Whisper model not loaded. Cannot transcribe.")
            return None
        
        try:
            # Handle different input types
            if isinstance(audio_file, (bytes, bytearray)):
                # Save bytes to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_file)
                    audio_path = tmp_file.name
            elif isinstance(audio_file, str):
                # File path
                audio_path = audio_file
            else:
                # File-like object
                audio_data = audio_file.read()
                try:
                    audio_file.seek(0)
                except Exception:
                    pass
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(audio_data)
                    audio_path = tmp_file.name
            
            # Transcribe with Whisper
            # Set language if specified (Whisper supports language codes like 'hi', 'en', etc.)
            result = self.model.transcribe(
                audio_path,
                language=language_code if language_code != 'en' else None,  # 'en' is default
                task="transcribe"
            )
            
            text = result.get('text', '').strip()
            
            # Clean up temporary file if we created one
            if isinstance(audio_file, (bytes, bytearray)) or (hasattr(audio_file, 'read') and not isinstance(audio_file, str)):
                try:
                    os.unlink(audio_path)
                except Exception:
                    pass
            
            if not text:
                logger.warning("Whisper returned empty transcription")
                return None
            
            logger.info(f"Whisper transcription successful: {text[:50]}...")
            return text
            
        except Exception as e:
            logger.error(f"Error in Whisper local transcription: {str(e)}", exc_info=True)
            # Clean up temp file on error
            if 'audio_path' in locals() and os.path.exists(audio_path):
                try:
                    os.unlink(audio_path)
                except Exception:
                    pass
            return None
