"""
AssemblyAI Service for Speech-to-Text
"""
import assemblyai as aai
import logging
from io import BytesIO

logger = logging.getLogger(__name__)


class AssemblyAIService:
    """Service for handling AssemblyAI transcription"""
    
    def __init__(self, api_key=None):
        """
        Initialize AssemblyAI service
        
        Args:
            api_key: AssemblyAI API key (from config if None)
        """
        from config import Config
        
        api_key = api_key or Config.ASSEMBLYAI_API_KEY
        if not api_key:
            logger.warning("AssemblyAI API key not found. Transcription will not work.")
            self.transcriber = None
        else:
            aai.settings.api_key = api_key
            self.transcriber = aai.Transcriber()
            logger.info("AssemblyAI service initialized")
    
    def transcribe_audio(self, audio_file, language_code='hi'):  # Default to Hindi
        """
        Transcribe audio file to text
        
        Args:
            audio_file: File object or file path
            language_code: Language code (default: 'en')
        
        Returns:
            str: Transcribed text
        """
        if not self.transcriber:
            logger.error("AssemblyAI transcriber not initialized. Please check API key.")
            return None
        
        try:
            # Configure transcription
            config = aai.TranscriptionConfig(
                language_code=language_code,
                speaker_labels=True,  # Identify different speakers
                punctuate=True,
                format_text=True
            )
            
            # Transcribe
            if isinstance(audio_file, str):
                # File path
                transcript = self.transcriber.transcribe(audio_file, config=config)
            else:
                # File object
                # Read file content
                audio_data = audio_file.read()
                audio_file.seek(0)  # Reset file pointer
                
                # Create temporary file-like object
                transcript = self.transcriber.transcribe(
                    BytesIO(audio_data),
                    config=config
                )
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"Transcription error: {transcript.error}")
                return None
            
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
            return None
    
    def transcribe_stream(self, stream_url):
        """
        Transcribe real-time audio stream
        
        Args:
            stream_url: URL of the audio stream
        
        Returns:
            Generator: Yields transcription results
        """
        try:
            config = aai.TranscriptionConfig(
                language_code='en',
                speaker_labels=True,
                punctuate=True
            )
            
            transcript_stream = self.transcriber.stream(
                stream_url,
                config=config
            )
            
            for transcript in transcript_stream:
                if transcript.text:
                    yield {
                        'text': transcript.text,
                        'is_final': transcript.is_final,
                        'confidence': transcript.confidence
                    }
                    
        except Exception as e:
            logger.error(f"Error in stream transcription: {str(e)}", exc_info=True)
            return None
    
    def create_realtime_session(self, sample_rate=16000):
        """
        Create a real-time transcription session
        
        Args:
            sample_rate: Audio sample rate (default: 16000)
        
        Returns:
            RealtimeTranscriber: Real-time transcriber instance
        """
        try:
            config = aai.RealtimeTranscriptionConfig(
                sample_rate=sample_rate,
                language_code='en'
            )
            
            transcriber = aai.RealtimeTranscriber(config=config)
            return transcriber
            
        except Exception as e:
            logger.error(f"Error creating realtime session: {str(e)}", exc_info=True)
            return None

