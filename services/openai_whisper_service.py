"""
OpenAI Whisper Service - Direct API Integration
Uses OpenAI's official Whisper API for speech-to-text
"""
import logging
import requests
from io import BytesIO

logger = logging.getLogger(__name__)


class OpenAIWhisperService:
    """Speech-to-text via OpenAI's official Whisper API"""

    def __init__(self, api_key=None):
        from config import Config
        
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/audio/transcriptions"
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Whisper transcription will not work.")
        
        logger.info("OpenAI Whisper service initialized")

    def transcribe_audio(self, audio_file, language_code='hi'):
        """
        Transcribe an audio file using OpenAI Whisper API
        Args:
            audio_file: File object or bytes
            language_code: Language code (default: 'hi' for Hindi)
        Returns: str | None
        """
        if not self.api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        try:
            # Read audio data
            if isinstance(audio_file, (bytes, bytearray)):
                audio_bytes = bytes(audio_file)
            else:
                audio_bytes = audio_file.read()
                try:
                    audio_file.seek(0)
                except Exception:
                    pass
            
            # Prepare multipart form data
            files = {
                'file': ('audio.wav', BytesIO(audio_bytes), 'audio/wav')
            }
            
            data = {
                'model': 'whisper-1',
                'language': language_code
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            # Make API call
            response = requests.post(
                self.base_url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            text = result.get('text', '').strip()
            if not text:
                logger.error(f"Empty transcription result: {result}")
                return None
            
            logger.info(f"Whisper transcription successful: {text[:50]}...")
            return text
            
        except Exception as e:
            logger.error(f"Error in OpenAI Whisper transcription: {str(e)}", exc_info=True)
            return None
