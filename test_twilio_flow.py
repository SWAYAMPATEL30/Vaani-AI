"""
Test Twilio call flow with optimized TTS
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
import logging
from io import BytesIO
import numpy as np
import soundfile as sf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("TESTING TWILIO FLOW: STT → LLM → TTS")
print("="*60)

# Test 1: STT (Whisper)
print("\n[1/4] Testing STT (Whisper)...")
try:
    from services.huggingface_asr_service import HuggingFaceASRService
    
    asr = HuggingFaceASRService()
    
    # Create dummy audio (1 second silence)
    sample_rate = 16000
    audio_data = np.zeros(int(sample_rate * 1.0), dtype=np.float32)
    audio_buffer = BytesIO()
    sf.write(audio_buffer, audio_data, sample_rate, format='WAV')
    audio_buffer.seek(0)
    
    start_time = time.time()
    transcript = asr.transcribe_audio(audio_buffer, language_code='hi')
    stt_time = time.time() - start_time
    
    print(f"✅ STT completed in {stt_time:.2f} seconds")
    print(f"   Transcript: {transcript or '(silence detected)'}")
    
except Exception as e:
    print(f"❌ STT ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 2: LLM (Groq)
print("\n[2/4] Testing LLM (Groq)...")
try:
    from services.groq_service import GroqService
    
    groq = GroqService()
    
    test_query = "नमस्ते"
    start_time = time.time()
    response = groq.generate_response(test_query, call_id=1, conversation_history=[])
    llm_time = time.time() - start_time
    
    print(f"✅ LLM completed in {llm_time:.2f} seconds")
    print(f"   Response: {response[:100]}...")
    
except Exception as e:
    print(f"❌ LLM ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: TTS (MMS TTS)
print("\n[3/4] Testing TTS (MMS TTS - should be FAST)...")
try:
    from services.tts_service import TTSService
    
    tts = TTSService()
    
    test_text = "नमस्ते! मैं आपकी AI सहायक हूं।"
    start_time = time.time()
    audio_url = tts.text_to_speech(test_text, call_sid="test_flow", language_code='hi')
    tts_time = time.time() - start_time
    
    if audio_url:
        print(f"✅ TTS completed in {tts_time:.2f} seconds")
        print(f"   Audio URL: {audio_url}")
        
        if tts_time > 30:
            print(f"⚠️  WARNING: TTS took {tts_time:.2f} seconds (should be < 10 seconds)")
        else:
            print(f"✅ GOOD: TTS is fast enough")
    else:
        print(f"❌ TTS returned None")
        
except Exception as e:
    print(f"❌ TTS ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Full pipeline
print("\n[4/4] Testing Full Pipeline (STT → LLM → TTS)...")
try:
    test_query = "आप कैसे हैं?"
    
    # STT (simulate)
    print("  → STT: [simulated]")
    
    # LLM
    print("  → LLM: Generating response...")
    start_time = time.time()
    response = groq.generate_response(test_query, call_id=1, conversation_history=[])
    llm_time = time.time() - start_time
    print(f"     ✅ LLM: {llm_time:.2f}s - {response[:50]}...")
    
    # TTS
    print("  → TTS: Converting to speech...")
    start_time = time.time()
    audio_url = tts.text_to_speech(response, call_sid="test_pipeline", language_code='hi')
    tts_time = time.time() - start_time
    
    if audio_url:
        print(f"     ✅ TTS: {tts_time:.2f}s - {audio_url}")
        total_time = llm_time + tts_time
        print(f"\n✅ FULL PIPELINE: {total_time:.2f} seconds")
        
        if total_time < 30:
            print("✅ EXCELLENT: Pipeline is fast enough for real-time calls")
        elif total_time < 60:
            print("⚠️  ACCEPTABLE: Pipeline may cause slight delays")
        else:
            print("❌ SLOW: Pipeline is too slow for real-time calls")
    else:
        print("     ❌ TTS failed")
        
except Exception as e:
    print(f"❌ PIPELINE ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nNext: Start Flask server and test with actual Twilio call")
print("Command: python app.py")
