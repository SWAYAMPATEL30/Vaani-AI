"""
Veena TTS Service - Text-to-Speech for Hindi and English
Model: https://huggingface.co/maya-research/Veena
Supports Hindi, English, and code-mixed text
"""
import logging
import torch
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class VeenaTTSService:
    """Text-to-speech using Veena TTS model locally (supports Hindi and English)"""

    def __init__(self):
        """Initialize Veena TTS model locally"""
        self.model = None
        self.tokenizer = None
        self.snac_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Control token IDs (fixed for Veena)
        self.START_OF_SPEECH_TOKEN = 128257
        self.END_OF_SPEECH_TOKEN = 128258
        self.START_OF_HUMAN_TOKEN = 128259
        self.END_OF_HUMAN_TOKEN = 128260
        self.START_OF_AI_TOKEN = 128261
        self.END_OF_AI_TOKEN = 128262
        self.AUDIO_CODE_BASE_OFFSET = 128266
        
        # Available speakers
        self.speakers = ["kavya", "agastya", "maitri", "vinaya"]
        self.default_speaker = "kavya"  # Female Hindi voice
        
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            logger.info(f"Loading Veena TTS model locally (device: {self.device})...")
            # Use correct model ID from official example
            model_id = "maya-research/veena-tts"
            
            # Try 4-bit quantization if CUDA is available (as per official example)
            if torch.cuda.is_available():
                try:
                    from transformers import BitsAndBytesConfig
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16,
                        bnb_4bit_use_double_quant=True,
                    )
                    logger.info("Using 4-bit quantization (CUDA available)")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        quantization_config=quantization_config,
                        device_map="auto",
                        trust_remote_code=True,
                    )
                except Exception as e:
                    logger.warning(f"4-bit quantization failed: {e}, loading without quantization")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        device_map="auto",
                        trust_remote_code=True,
                        torch_dtype=torch.float16,
                    )
            else:
                # CPU mode - load without quantization (model is large, may be slow)
                logger.warning("CUDA not available. Loading model on CPU (this may be slow and require significant RAM)")
                logger.warning("Consider using a GPU for better performance")
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float32,
                )
                self.model = self.model.to("cpu")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            
            # Initialize SNAC decoder for audio (as per official example)
            try:
                from snac import SNAC
                self.snac_model = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()
                if torch.cuda.is_available():
                    self.snac_model = self.snac_model.cuda()
                else:
                    self.snac_model = self.snac_model.to("cpu")
                logger.info(f"SNAC decoder loaded successfully on {next(self.snac_model.parameters()).device}")
            except Exception as e:
                logger.error(f"Failed to load SNAC decoder: {e}")
                logger.error("Install: pip install snac")
                self.snac_model = None
            
            logger.info(f"Veena TTS model loaded successfully on {self.device}")
            logger.info(f"Available speakers: {', '.join(self.speakers)}")
            
        except ImportError as e:
            logger.error(f"Required library not found: {e}")
            logger.error("Install: pip install transformers torch torchaudio snac bitsandbytes")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load Veena TTS model: {str(e)}", exc_info=True)
            self.model = None

    def _decode_snac_tokens(self, snac_tokens):
        """De-interleave and decode SNAC tokens to audio (as per official example)"""
        if not snac_tokens or len(snac_tokens) % 7 != 0:
            return None
        
        if not self.snac_model:
            logger.error("SNAC model not loaded")
            return None
        
        # Get the device of the SNAC model (as per official example)
        device = next(self.snac_model.parameters()).device
        
        # De-interleave tokens into 3 hierarchical levels
        codes_lvl = [[] for _ in range(3)]
        llm_codebook_offsets = [self.AUDIO_CODE_BASE_OFFSET + i * 4096 for i in range(7)]
        
        for i in range(0, len(snac_tokens), 7):
            # Level 0: Coarse (1 token)
            codes_lvl[0].append(snac_tokens[i] - llm_codebook_offsets[0])
            # Level 1: Medium (2 tokens)
            codes_lvl[1].append(snac_tokens[i+1] - llm_codebook_offsets[1])
            codes_lvl[1].append(snac_tokens[i+4] - llm_codebook_offsets[4])
            # Level 2: Fine (4 tokens)
            codes_lvl[2].append(snac_tokens[i+2] - llm_codebook_offsets[2])
            codes_lvl[2].append(snac_tokens[i+3] - llm_codebook_offsets[3])
            codes_lvl[2].append(snac_tokens[i+5] - llm_codebook_offsets[5])
            codes_lvl[2].append(snac_tokens[i+6] - llm_codebook_offsets[6])
        
        # Convert to tensors for SNAC decoder
        hierarchical_codes = []
        for lvl_codes in codes_lvl:
            tensor = torch.tensor(lvl_codes, dtype=torch.int32, device=device).unsqueeze(0)
            if torch.any((tensor < 0) | (tensor > 4095)):
                raise ValueError("Invalid SNAC token values")
            hierarchical_codes.append(tensor)
        
        # Decode with SNAC
        with torch.no_grad():
            audio_hat = self.snac_model.decode(hierarchical_codes)
        
        return audio_hat.squeeze().clamp(-1, 1).cpu().numpy()

    def text_to_speech(self, text, call_sid=None, language_code='hi', speaker=None):
        """
        Convert text to speech using Veena TTS
        Args:
            text: Text to convert (Hindi or English)
            call_sid: Call SID for filename
            language_code: Language code (default: 'hi' for Hindi)
            speaker: Speaker voice (kavya, agastya, maitri, vinaya)
        Returns: URL to audio file or None
        """
        if not self.model or not text:
            logger.error("Veena TTS model not loaded or text is empty")
            return None
        
        if not self.snac_model:
            logger.error("SNAC decoder not loaded")
            return None
        
        try:
            from config import Config
            import soundfile as sf
            
            # Use specified speaker or default (as per official example)
            speaker = speaker or self.default_speaker
            
            # Prepare input with speaker token (as per official example)
            prompt = f"<spk_{speaker}> {text}"
            prompt_tokens = self.tokenizer.encode(prompt, add_special_tokens=False)
            
            # Construct full sequence: [HUMAN] <spk_speaker> text [/HUMAN] [AI] [SPEECH]
            input_tokens = [
                self.START_OF_HUMAN_TOKEN,
                *prompt_tokens,
                self.END_OF_HUMAN_TOKEN,
                self.START_OF_AI_TOKEN,
                self.START_OF_SPEECH_TOKEN
            ]
            
            # Get device from model
            model_device = next(self.model.parameters()).device
            input_ids = torch.tensor([input_tokens], device=model_device)
            
            # Calculate max tokens based on text length (as per official example)
            max_tokens = min(int(len(text) * 1.3) * 7 + 21, 700)
            
            # Generate audio tokens (as per official example)
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=0.4,
                    top_p=0.9,
                    repetition_penalty=1.05,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=[self.END_OF_SPEECH_TOKEN, self.END_OF_AI_TOKEN]
                )
            
            # Extract SNAC tokens (as per official example)
            generated_ids = output[0][len(input_tokens):].tolist()
            snac_tokens = [
                token_id for token_id in generated_ids
                if self.AUDIO_CODE_BASE_OFFSET <= token_id < (self.AUDIO_CODE_BASE_OFFSET + 7 * 4096)
            ]
            
            if not snac_tokens:
                raise ValueError("No audio tokens generated")
            
            # Decode audio
            audio = self._decode_snac_tokens(snac_tokens)
            if audio is None:
                logger.error("Failed to decode audio tokens")
                return None
            
            # Save as WAV file
            audio_storage_path = Path("audio_output")
            audio_storage_path.mkdir(exist_ok=True)
            
            filename = f"{call_sid or 'audio'}_{hash(text)}.wav"
            filepath = audio_storage_path / filename
            
            # Save audio at 24kHz (Veena's native sample rate)
            sample_rate = 24000
            sf.write(str(filepath), audio, sample_rate)
            
            logger.info(f"Veena TTS audio generated successfully: {filename} (speaker: {speaker})")
            
            # Return relative URL so it always works with the current host (ngrok/Twilio)
            return f"/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error in Veena TTS generation: {str(e)}", exc_info=True)
            return None
