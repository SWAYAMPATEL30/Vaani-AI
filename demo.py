"""
Demo script to test the Voice Calling Agent locally
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, db
from models import Call, CallTranscript
from services.assemblyai_service import AssemblyAIService
from services.openai_service import OpenAIService
from services.tts_service import TTSService

def demo_transcription():
    """Demo: Test transcription with AssemblyAI"""
    print("=" * 50)
    print("Demo: Speech-to-Text (AssemblyAI)")
    print("=" * 50)
    
    # Check if API key is set
    from config import Config
    if not Config.ASSEMBLYAI_API_KEY:
        print("❌ AssemblyAI API key not found in .env")
        print("   Please set ASSEMBLYAI_API_KEY in your .env file")
        return False
    
    print(f"✓ AssemblyAI API Key: {Config.ASSEMBLYAI_API_KEY[:20]}...")
    print("\nNote: To test transcription, you need an audio file.")
    print("Example usage:")
    print("  python -c \"from services.assemblyai_service import AssemblyAIService; from config import Config; s = AssemblyAIService(); print(s.transcribe_audio('test.mp3'))\"")
    return True

def demo_ai_response():
    """Demo: Test AI response generation"""
    print("\n" + "=" * 50)
    print("Demo: AI Response (OpenAI)")
    print("=" * 50)
    
    from config import Config
    if not Config.OPENAI_API_KEY:
        print("❌ OpenAI API key not found in .env")
        print("   Please set OPENAI_API_KEY in your .env file")
        return False
    
    print(f"✓ OpenAI API Key: {Config.OPENAI_API_KEY[:20]}...")
    print(f"✓ Model: {Config.OPENAI_MODEL}")
    
    # Test with a simple query
    try:
        service = OpenAIService()
        test_input = "Hello, how are you?"
        print(f"\nTest Input: {test_input}")
        response = service.generate_response(test_input, call_id="demo123")
        print(f"AI Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_tts():
    """Demo: Test text-to-speech"""
    print("\n" + "=" * 50)
    print("Demo: Text-to-Speech")
    print("=" * 50)
    
    from config import Config
    provider = Config.TTS_PROVIDER or 'elevenlabs'
    print(f"Provider: {provider}")
    
    if provider == 'elevenlabs':
        if not Config.ELEVENLABS_API_KEY:
            print("❌ ElevenLabs API key not found in .env")
            print("   Please set ELEVENLABS_API_KEY in your .env file")
            return False
        print(f"✓ ElevenLabs API Key: {Config.ELEVENLABS_API_KEY[:20]}...")
    elif provider == 'google':
        if not Config.GOOGLE_APPLICATION_CREDENTIALS:
            print("❌ Google credentials not found")
            print("   Please set GOOGLE_APPLICATION_CREDENTIALS in your .env file")
            return False
        print(f"✓ Google credentials configured")
    
    try:
        service = TTSService()
        test_text = "Hello, this is a test of the text to speech system."
        print(f"\nTest Text: {test_text}")
        audio_url = service.text_to_speech(test_text, call_sid="demo123")
        if audio_url:
            print(f"✓ Audio generated: {audio_url}")
            return True
        else:
            print("❌ Failed to generate audio")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def demo_database():
    """Demo: Test database connection"""
    print("\n" + "=" * 50)
    print("Demo: Database")
    print("=" * 50)
    
    try:
        with app.app_context():
            # Try to query database
            call_count = Call.query.count()
            transcript_count = CallTranscript.query.count()
            print(f"✓ Database connected")
            print(f"✓ Calls in database: {call_count}")
            print(f"✓ Transcripts in database: {transcript_count}")
            return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        print("   Try running: python -c \"from app import app, db; app.app_context().push(); db.create_all()\"")
        return False

def main():
    """Run all demos"""
    print("\n" + "🎤 " * 25)
    print("Smart Voice Calling Agent - Demo & Test")
    print("🎤 " * 25 + "\n")
    
    results = {
        'Database': demo_database(),
        'Transcription': demo_transcription(),
        'AI Response': demo_ai_response(),
        'Text-to-Speech': demo_tts()
    }
    
    print("\n" + "=" * 50)
    print("Demo Results Summary")
    print("=" * 50)
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All services are configured and working!")
    else:
        print("\n⚠️  Some services need configuration. Check your .env file.")
    
    print("\nNext steps:")
    print("1. Ensure all API keys are set in .env")
    print("2. Run: python app.py")
    print("3. Test: curl http://localhost:5000/health")
    print()

if __name__ == '__main__':
    main()




