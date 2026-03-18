"""
Quick test to verify TTS is working fast (MMS TTS should load in seconds, not hours)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("QUICK TTS SPEED TEST")
print("="*60)

# Test 1: Initialize TTS service (should be fast with MMS TTS as primary)
print("\n[1/3] Initializing TTS Service...")
start_time = time.time()

try:
    from services.tts_service import TTSService
    tts = TTSService()
    init_time = time.time() - start_time
    print(f"✅ TTS Service initialized in {init_time:.2f} seconds")
    
    if init_time > 60:
        print(f"⚠️  WARNING: Initialization took {init_time:.2f} seconds (> 1 minute)")
        print("   This suggests Veena TTS is being loaded (slow). MMS TTS should load in < 10 seconds.")
    else:
        print(f"✅ GOOD: Initialization took {init_time:.2f} seconds (MMS TTS is primary)")
        
except Exception as e:
    print(f"❌ ERROR: Failed to initialize TTS service: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Generate TTS audio (should be fast)
print("\n[2/3] Generating TTS audio...")
test_text = "नमस्ते! कॉल करने के लिए धन्यवाद।"
start_time = time.time()

try:
    audio_url = tts.text_to_speech(test_text, call_sid="test_speed", language_code='hi')
    gen_time = time.time() - start_time
    
    if audio_url:
        print(f"✅ TTS audio generated in {gen_time:.2f} seconds")
        print(f"   Audio URL: {audio_url}")
        
        if gen_time > 30:
            print(f"⚠️  WARNING: Generation took {gen_time:.2f} seconds (> 30 seconds)")
            print("   This is slow - MMS TTS should generate in < 5 seconds")
        else:
            print(f"✅ GOOD: Generation took {gen_time:.2f} seconds")
    else:
        print(f"❌ ERROR: TTS returned None")
        
except Exception as e:
    print(f"❌ ERROR: Failed to generate TTS: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check which TTS is being used
print("\n[3/3] Checking TTS provider...")
try:
    if hasattr(tts, 'hf_tts'):
        if hasattr(tts.hf_tts, 'mms_tts_local') and tts.hf_tts.mms_tts_local:
            print("✅ Using: Facebook MMS TTS Hindi (PRIMARY - FAST)")
        elif hasattr(tts.hf_tts, 'veena_tts') and tts.hf_tts.veena_tts:
            print("⚠️  Using: Veena TTS (SLOW - should only be fallback)")
        else:
            print("⚠️  TTS service structure unclear")
    else:
        print(f"Using provider: {tts.provider}")
except Exception as e:
    print(f"Could not determine TTS provider: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("\nIf initialization took > 1 minute, Veena TTS is being loaded.")
print("MMS TTS should initialize in < 10 seconds and generate audio in < 5 seconds.")
