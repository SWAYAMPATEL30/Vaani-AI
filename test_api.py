"""
Simple test script for API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_calls():
    """Test get calls endpoint"""
    print("Testing /api/calls endpoint...")
    response = requests.get(f"{BASE_URL}/api/calls")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_process_audio(audio_file_path):
    """Test audio processing endpoint"""
    print(f"Testing /api/process-audio with {audio_file_path}...")
    with open(audio_file_path, 'rb') as f:
        files = {'audio': f}
        data = {'call_sid': 'test123'}
        response = requests.post(f"{BASE_URL}/api/process-audio", files=files, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == '__main__':
    print("=" * 50)
    print("Voice Calling Agent API Tests")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_get_calls()
        
        # Uncomment to test audio processing
        # test_process_audio('test_audio.mp3')
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {str(e)}")




