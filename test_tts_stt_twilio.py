"""
Test TTS and STT for Twilio integration
This script tests if TTS generates audio files correctly and if they're accessible
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import logging
from pathlib import Path
from io import BytesIO
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tts():
    """Test TTS generation"""
    print("\n" + "="*60)
    print("TESTING TTS (Text-to-Speech)")
    print("="*60)
    
    from services.tts_service import TTSService
    
    tts = TTSService()
    
    # Test Hindi greeting
    test_texts = [
        "नमस्ते! कॉल करने के लिए धन्यवाद। मैं आपकी AI सहायक हूं। मैं आपकी कैसे मदद कर सकती हूं?",
        "कृपया अपना संदेश बोलें।",
        "मैं आपकी मदद करने के लिए यहां हूं।"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n[{i}/{len(test_texts)}] Testing TTS for: {text[:50]}...")
        try:
            audio_url = tts.text_to_speech(text, call_sid="test", language_code='hi')
            if audio_url:
                print(f"✅ TTS SUCCESS: {audio_url}")
                
                # Check if file exists locally
                filename = audio_url.split('/')[-1]
                filepath = Path("audio_output") / filename
                if filepath.exists():
                    file_size = filepath.stat().st_size
                    print(f"   File exists: {filepath} ({file_size} bytes)")
                else:
                    print(f"   ⚠️  File NOT found: {filepath}")
            else:
                print(f"❌ TTS FAILED: No audio URL returned")
        except Exception as e:
            print(f"❌ TTS ERROR: {e}")
            import traceback
            traceback.print_exc()

def test_audio_serving():
    """Test if audio files can be served via HTTP"""
    print("\n" + "="*60)
    print("TESTING AUDIO FILE SERVING")
    print("="*60)
    
    from config import Config
    
    audio_dir = Path("audio_output")
    if not audio_dir.exists():
        print("❌ Audio directory not found")
        return
    
    # Find a WAV file
    wav_files = list(audio_dir.glob("*.wav"))
    if not wav_files:
        print("❌ No WAV files found in audio_output directory")
        return
    
    test_file = wav_files[0]
    print(f"\nTesting with file: {test_file.name}")
    
    # Test local URL
    local_url = f"{Config.WEBHOOK_BASE_URL}/audio/{test_file.name}"
    print(f"Local URL: {local_url}")
    
    # Try to access it (if server is running)
    try:
        response = requests.get(local_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Audio file accessible via HTTP: {response.headers.get('content-type')}")
            print(f"   File size: {len(response.content)} bytes")
        else:
            print(f"⚠️  HTTP {response.status_code}: {response.text[:100]}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to server (server may not be running)")
        print("   This is OK - audio files will be served when Twilio calls")
    except Exception as e:
        print(f"⚠️  Error accessing audio: {e}")

def test_stt():
    """Test STT with a dummy audio file"""
    print("\n" + "="*60)
    print("TESTING STT (Speech-to-Text)")
    print("="*60)
    
    from services.huggingface_asr_service import HuggingFaceASRService
    
    asr = HuggingFaceASRService()
    
    # Create a dummy audio file (silence)
    import numpy as np
    import soundfile as sf
    
    # Generate 1 second of silence at 16kHz
    sample_rate = 16000
    duration = 1.0
    audio_data = np.zeros(int(sample_rate * duration), dtype=np.float32)
    
    # Save to BytesIO
    audio_buffer = BytesIO()
    sf.write(audio_buffer, audio_data, sample_rate, format='WAV')
    audio_buffer.seek(0)
    
    print("\nTesting STT with dummy audio (silence)...")
    try:
        transcript = asr.transcribe_audio(audio_buffer, language_code='hi')
        if transcript:
            print(f"✅ STT SUCCESS: {transcript}")
        else:
            print("⚠️  STT returned None (may be expected for silence)")
    except Exception as e:
        print(f"❌ STT ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TWILIO TTS/STT INTEGRATION TEST")
    print("="*60)
    
    test_tts()
    test_audio_serving()
    test_stt()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Ensure WEBHOOK_BASE_URL in config points to your ngrok/public URL")
    print("2. Start Flask server: python app.py")
    print("3. Audio files should be accessible at: {WEBHOOK_BASE_URL}/audio/<filename>")
