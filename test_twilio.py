"""
Test Twilio integration - Make a test call
"""
from twilio.rest import Client
from config import Config

def test_twilio_call():
    """Test making a call through Twilio"""
    try:
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        # Your webhook URL (update this after deployment)
        webhook_url = f"{Config.WEBHOOK_BASE_URL}/webhook/incoming"
        
        print(f"📞 Testing Twilio call...")
        print(f"From: {Config.TWILIO_PHONE_NUMBER}")
        print(f"Webhook URL: {webhook_url}")
        
        # Uncomment to make actual call (replace with your test number)
        # call = client.calls.create(
        #     url=webhook_url,
        #     to="++91XXXXXXXXXX",  # Your test number
        #     from_=Config.TWILIO_PHONE_NUMBER
        # )
        # 
        # print(f"✅ Call initiated! Call SID: {call.sid}")
        # print(f"Status: {call.status}")
        
        print("\n✅ Twilio credentials are valid!")
        print("\nTo make a test call, uncomment the code in test_twilio.py")
        print(f"Update WEBHOOK_BASE_URL in .env to your deployed URL")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_twilio_call()




