"""
Configuration settings for Voice Calling Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # AssemblyAI
    ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY', '')
    ASSEMBLYAI_BASE_URL = 'https://api.assemblyai.com/v2'
    
    # Google Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    # Groq LLM
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
    
    # OpenAI (backup/optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    OPENAI_MAX_TOKENS = int(os.getenv('MAX_TOKENS', '500'))
    OPENAI_TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # AI Provider (groq, gemini, or openai)
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'groq')
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
    ELEVENLABS_BASE_URL = 'https://api.elevenlabs.io/v1'
    ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '')
    
    # Google TTS
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    GOOGLE_TTS_VOICE_NAME = os.getenv('GOOGLE_TTS_VOICE_NAME', 'en-US-Wavenet-D')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///voice_agent.db')
    
    # Telephony - Exotel
    EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY', '')
    EXOTEL_API_TOKEN = os.getenv('EXOTEL_API_TOKEN', '')
    EXOTEL_SUBDOMAIN = os.getenv('EXOTEL_SUBDOMAIN', '')
    
    # Telephony - Twilio
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # Server
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    # IMPORTANT: Disable debug reloader by default on Windows to avoid socket errors (WinError 10038)
    # that can break Twilio webhook connectivity. Enable explicitly if needed.
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', '5000'))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Webhook
    WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'http://localhost:5000')
    
    # Call Settings
    MAX_CALL_DURATION = int(os.getenv('MAX_CALL_DURATION', '300'))
    LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'hi-IN')  # Default to Hindi
    
    # TTS Provider (elevenlabs, google, vibevoice, huggingface)
    # DEFAULT: use huggingface, which in our setup means fully local TTS (Veena / MMS TTS)
    TTS_PROVIDER = os.getenv('TTS_PROVIDER', 'huggingface')

    # Hugging Face (STT/LLM/TTS via Inference API)
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')

    # STT Provider (assemblyai or huggingface)
    # Default to local Whisper (open-source) to avoid external STT API calls.
    STT_PROVIDER = os.getenv('STT_PROVIDER', 'huggingface')
    HF_ASR_MODEL = os.getenv('HF_ASR_MODEL', 'openai/whisper-large')    # AI Provider (groq, gemini, openai, or huggingface)
    HF_LLM_MODEL = os.getenv('HF_LLM_MODEL', 'mistralai/Mistral-7B-Instruct-v0.3')
    HF_LLM_MAX_TOKENS = int(os.getenv('HF_LLM_MAX_TOKENS', '200'))
    HF_LLM_TEMPERATURE = float(os.getenv('HF_LLM_TEMPERATURE', '0.7'))

    # Hugging Face TTS model name (used only if we ever call HF Inference API)
    # We keep it for completeness, but our primary TTS is local Veena/MMS, not the API.
    HF_TTS_MODEL = os.getenv('HF_TTS_MODEL', 'maya-research/veena-tts')
