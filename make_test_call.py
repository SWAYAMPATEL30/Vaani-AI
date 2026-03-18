"""
Make a test call to your phone.

You can control the destination number via the TEST_CALL_TO environment
variable without editing this file, for example:

    $env:TEST_CALL_TO="+918451088818"; python make_test_call.py
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from twilio.rest import Client
from config import Config
from get_ngrok_url import get_ngrok_public_url


def make_test_call():
    """Make a test call using Twilio"""
    try:
        # Prefer the live ngrok URL if available, fall back to Config.WEBHOOK_BASE_URL
        webhook_base = get_ngrok_public_url() or Config.WEBHOOK_BASE_URL

        # Allow overriding the target phone number via environment variable
        to_number = os.getenv("TEST_CALL_TO", "++91XXXXXXXXXX")

        print("📞 Making test call...")
        print(f"From: {Config.TWILIO_PHONE_NUMBER}")
        print(f"To: {to_number}")
        print(f"Webhook URL: {webhook_base}/webhook/incoming")
        print()
        
        # Initialize Twilio client
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        # Make the call
        call = client.calls.create(
            url=f"{webhook_base}/webhook/incoming",
            to=to_number,
            from_=Config.TWILIO_PHONE_NUMBER
        )
        
        print("✅ Call initiated successfully!")
        print(f"Call SID: {call.sid}")
        print(f"Status: {call.status}")
        print()
        print(f"📱 You should receive a call on {to_number}")
        print("   The AI agent will answer and you can have a conversation!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error making call: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Make sure Flask server is running: python app.py")
        print("2. Make sure ngrok is running: ngrok http 5000")
        print("3. Update WEBHOOK_BASE_URL in .env with ngrok URL")
        print("4. Check Twilio credentials in .env")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("  Voice Calling Agent - Test Call")
    print("=" * 60)
    print()
    
    # Check if webhook URL is localhost (needs ngrok)
    if Config.WEBHOOK_BASE_URL.startswith('http://localhost'):
        print("⚠️  WARNING: WEBHOOK_BASE_URL is set to localhost")
        print("   Twilio cannot reach localhost. You need ngrok!")
        print()
        print("Steps:")
        print("1. Download ngrok: https://ngrok.com/download")
        print("2. Run: ngrok http 5000")
        print("3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)")
        print("4. Update .env: WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io")
        print("5. Restart Flask server")
        print("6. Run this script again")
        print()
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    make_test_call()