"""
Text-to-Speech Service
Supports ElevenLabs and Google Cloud TTS
"""
import os
import logging
import requests
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSService:
    """Service for converting text to speech"""
    
    def __init__(self, provider=None):
        """
        Initialize TTS service
        
        Args:
            provider: 'elevenlabs' or 'google' (auto-detected if None)
        """
        from config import Config
        
        self.provider = (provider or Config.TTS_PROVIDER or 'elevenlabs').lower()
        self.audio_storage_path = Path('audio_output')
        self.audio_storage_path.mkdir(exist_ok=True)
        
        if self.provider == 'elevenlabs':
            self._init_elevenlabs()
        elif self.provider == 'google':
            self._init_google()
        elif self.provider == 'vibevoice':
            self._init_vibevoice()
        elif self.provider in ('huggingface', 'hf'):
            self._init_huggingface()
        else:
            logger.warning(f"Unknown TTS provider: {self.provider}, defaulting to elevenlabs")
            self.provider = 'elevenlabs'
            self._init_elevenlabs()
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS"""
        from config import Config
        
        self.elevenlabs_api_key = Config.ELEVENLABS_API_KEY
        self.elevenlabs_voice_id = Config.ELEVENLABS_VOICE_ID or '21m00Tcm4TlvDq8ikWAM'  # Default voice
        self.elevenlabs_url = f"{Config.ELEVENLABS_BASE_URL}/text-to-speech/{self.elevenlabs_voice_id}"
        
        if not self.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not found, TTS may not work")
    
    def _init_google(self):
        """Initialize Google Cloud TTS"""
        from config import Config
        
        try:
            from google.cloud import texttospeech
            
            if Config.GOOGLE_APPLICATION_CREDENTIALS:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS
            
            self.google_client = texttospeech.TextToSpeechClient()
            self.google_voice_name = Config.GOOGLE_TTS_VOICE_NAME
            logger.info("Google Cloud TTS initialized")
        except Exception as e:
            logger.error(f"Error initializing Google TTS: {str(e)}")
            self.google_client = None
    
    def _init_vibevoice(self):
        """Initialize VibeVoice via Hugging Face Inference API."""
        try:
            from services.vibevoice_tts_service import VibeVoiceTTSService
            self.vibevoice = VibeVoiceTTSService()
            logger.info("VibeVoice TTS initialized")
        except Exception as e:
            logger.error(f"Error initializing VibeVoice TTS: {str(e)}", exc_info=True)
            self.vibevoice = None

    def _init_huggingface(self):
        """Initialize generic Hugging Face TTS model via Inference Router."""
        try:
            from services.huggingface_tts_service import HuggingFaceTTSService
            self.hf_tts = HuggingFaceTTSService()
            logger.info("HuggingFace TTS initialized")
        except Exception as e:
            logger.error(f"Error initializing HuggingFace TTS: {str(e)}", exc_info=True)
            self.hf_tts = None
    
    def text_to_speech(self, text, call_sid=None, voice_id=None, language_code='hi'):
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert to speech
            call_sid: Optional call ID for file naming
            voice_id: Optional voice ID override
            language_code: Language code (default: 'hi' for Hindi)
        
        Returns:
            str: URL or path to audio file
        """
        if self.provider == 'elevenlabs':
            return self._elevenlabs_tts(text, call_sid, voice_id)
        elif self.provider == 'google':
            return self._google_tts(text, call_sid, language_code)
        elif self.provider == 'vibevoice':
            if not self.vibevoice:
                logger.error("VibeVoice TTS not initialized")
                return None
            return self.vibevoice.text_to_speech(text, call_sid)
        elif self.provider in ('huggingface', 'hf'):
            if not getattr(self, "hf_tts", None):
                logger.error("HuggingFace TTS not initialized")
                return None
            return self.hf_tts.text_to_speech(text, call_sid, language_code)
        else:
            logger.error(f"Unknown TTS provider: {self.provider}")
            return None
    
    def _elevenlabs_tts(self, text, call_sid=None, voice_id=None):
        """Convert text to speech using ElevenLabs"""
        try:
            if not self.elevenlabs_api_key:
                logger.error("ElevenLabs API key not configured")
                return None
            
            url = self.elevenlabs_url
            if voice_id:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Save audio file
            filename = f"{call_sid or 'audio'}_{hash(text)}.mp3"
            filepath = self.audio_storage_path / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Generated audio file: {filepath}")
            
            # Return relative URL (Twilio/ngrok will resolve against current host)
            return f"/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error in ElevenLabs TTS: {str(e)}", exc_info=True)
            return None
    
    def _google_tts(self, text, call_sid=None):
        """Convert text to speech using Google Cloud TTS"""
        try:
            if not self.google_client:
                logger.error("Google TTS client not initialized")
                return None
            
            from google.cloud import texttospeech
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=self.google_voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = self.google_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save audio file
            filename = f"{call_sid or 'audio'}_{hash(text)}.mp3"
            filepath = self.audio_storage_path / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.audio_content)
            
            logger.info(f"Generated audio file: {filepath}")
            
            # Return relative URL (Twilio/ngrok will resolve against current host)
            return f"/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error in Google TTS: {str(e)}", exc_info=True)
            return None

