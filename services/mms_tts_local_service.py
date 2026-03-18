"""
Facebook MMS TTS Hindi Local Service
Uses transformers library to run facebook/mms-tts-hin locally
Model: https://huggingface.co/facebook/mms-tts-hin
"""
import logging
import torch
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)


class MMSTTSLocalService:
    """Text-to-speech using Facebook MMS TTS Hindi locally (no API needed)"""

    def __init__(self):
        """Initialize Facebook MMS TTS Hindi model locally"""
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            from transformers import VitsModel, AutoTokenizer
            
            logger.info(f"Loading Facebook MMS TTS Hindi model locally (device: {self.device})...")
            model_id = "facebook/mms-tts-hin"
            
            # Load model and tokenizer
            self.model = VitsModel.from_pretrained(model_id)
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Facebook MMS TTS Hindi model loaded successfully on {self.device}")
        except ImportError:
            logger.error("transformers library not found. Install: pip install transformers")
            logger.error("Also install: pip install torch torchaudio")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load Facebook MMS TTS Hindi model: {str(e)}")
            logger.error("Make sure transformers and torch are installed")
            self.model = None

    def text_to_speech(self, text, call_sid=None, language_code='hi'):
        """
        Convert text to speech using Facebook MMS TTS Hindi locally
        Args:
            text: Text to convert (Hindi text)
            call_sid: Call SID for filename
            language_code: Language code (default: 'hi' for Hindi)
        Returns: URL to audio file or None
        """
        if not self.model or not text:
            logger.error("MMS TTS model not loaded or text is empty")
            return None
        
        try:
            import torchaudio
            from config import Config
            
            # Tokenize input text
            inputs = self.tokenizer(text, return_tensors="pt")
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate speech
            with torch.no_grad():
                output = self.model(**inputs).waveform
            
            # Convert to numpy and ensure it's in the right format
            audio_numpy = output.cpu().numpy()
            
            # Handle different output shapes
            if len(audio_numpy.shape) > 1:
                audio_numpy = audio_numpy.squeeze()
            
            # Normalize audio to 16-bit PCM range
            import numpy as np
            audio_numpy = np.clip(audio_numpy, -1.0, 1.0)
            audio_int16 = (audio_numpy * 32767).astype(np.int16)
            
            # Save as WAV file
            audio_storage_path = Path("audio_output")
            audio_storage_path.mkdir(exist_ok=True)
            
            filename = f"{call_sid or 'audio'}_{hash(text)}.wav"
            filepath = audio_storage_path / filename
            
            # Save as WAV using scipy (more reliable than torchaudio)
            # Twilio accepts WAV files at various sample rates
            sample_rate = 16000
            try:
                from scipy.io import wavfile
                # scipy.io.wavfile.write expects (sample_rate, data) where data is int16
                wavfile.write(str(filepath), sample_rate, audio_int16)
            except ImportError:
                # Fallback to soundfile if scipy not available
                try:
                    import soundfile as sf
                    sf.write(str(filepath), audio_int16, sample_rate)
                except ImportError:
                    # Last resort: use wave module (built-in)
                    import wave
                    with wave.open(str(filepath), 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(audio_int16.tobytes())
            
            logger.info(f"MMS TTS audio generated successfully: {filename}")
            
            # Return relative URL so it always works with the current host (ngrok/Twilio)
            return f"/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error in MMS TTS local generation: {str(e)}", exc_info=True)
            return None
