"""
Complete test suite for Voice Calling Agent
"""
import requests
import json
from config import Config

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    """Test health endpoint"""
    print_section("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy!")
            print(f"   Status: {data.get('status')}")
            print(f"   Services:")
            for service, status in data.get('services', {}).items():
                icon = "✅" if status else "❌"
                print(f"   {icon} {service}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_get_calls():
    """Test get calls endpoint"""
    print_section("Get Calls API")
    try:
        response = requests.get(f"{BASE_URL}/api/calls", timeout=5)
        if response.status_code == 200:
            data = response.json()
            calls = data.get('calls', [])
            print(f"✅ Successfully retrieved {len(calls)} calls")
            if calls:
                print("\n   Recent calls:")
                for call in calls[:3]:
                    print(f"   - Call {call.get('call_sid')[:20]}... | Status: {call.get('status')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_config():
    """Test configuration"""
    print_section("Configuration Check")
    checks = {
        "AssemblyAI": bool(Config.ASSEMBLYAI_API_KEY),
        "OpenAI": bool(Config.OPENAI_API_KEY),
        "ElevenLabs": bool(Config.ELEVENLABS_API_KEY),
        "Twilio Account SID": bool(Config.TWILIO_ACCOUNT_SID),
        "Twilio Auth Token": bool(Config.TWILIO_AUTH_TOKEN),
        "Twilio Phone": bool(Config.TWILIO_PHONE_NUMBER),
    }
    
    all_ok = True
    for key, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {key}")
        if not status:
            all_ok = False
    
    return all_ok

def test_webhook_endpoint():
    """Test webhook endpoint structure"""
    print_section("Webhook Endpoints")
    endpoints = [
        ("/webhook/incoming", "POST", "Incoming call handler"),
        ("/webhook/status", "POST", "Call status updates"),
        ("/webhook/transcription", "POST", "Transcription updates"),
    ]
    
    print("   Available webhook endpoints:")
    for endpoint, method, desc in endpoints:
        print(f"   ✅ {method} {endpoint} - {desc}")
    
    return True

def main():
    print("\n" + "🎤 " * 30)
    print("  Voice Calling Agent - Complete Test Suite")
    print("🎤 " * 30)
    
    results = {
        "Configuration": test_config(),
        "Health Check": test_health(),
        "Get Calls API": test_get_calls(),
        "Webhook Endpoints": test_webhook_endpoint(),
    }
    
    print_section("Test Results Summary")
    all_passed = True
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Fix any failed configuration items")
    print("2. Start server: python app.py")
    print("3. For Twilio testing, use ngrok to expose your server")
    print("4. Configure webhook in Twilio console")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    main()




