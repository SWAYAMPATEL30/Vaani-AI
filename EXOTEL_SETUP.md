# 📞 Exotel Setup Guide

## ✅ Your Exotel Credentials (Configured)

- **API Key**: `YOUR_EXOTEL_API_KEY`
- **API Token**: `YOUR_EXOTEL_API_TOKEN`

## 🔧 Setup Steps

### 1. Get Your Exotel Subdomain

1. Log in to Exotel: https://exotel.com
2. Go to your dashboard
3. Find your subdomain (e.g., `yourcompany.exotel.com`)
4. Update `.env`:
   ```
   EXOTEL_SUBDOMAIN=yourcompany
   ```

### 2. Configure Webhook in Exotel

1. Go to Exotel Dashboard → Settings → Webhooks
2. Set **Incoming Call Webhook**:
   ```
   https://your-ngrok-url.ngrok.io/webhook/incoming
   ```
   Or after deployment:
   ```
   https://your-deployed-url.com/webhook/incoming
   ```
3. Set **Call Status Webhook**:
   ```
   https://your-ngrok-url.ngrok.io/webhook/status
   ```

### 3. Buy/Configure Phone Number

1. In Exotel dashboard, go to Numbers
2. Buy a phone number or use existing
3. Configure the number to use your webhook

### 4. Test Exotel Integration

```python
# Test script (create test_exotel.py)
from twilio.rest import Client
import requests
from config import Config

# Exotel uses similar API to Twilio
# Test webhook
response = requests.post(
    f"{Config.WEBHOOK_BASE_URL}/webhook/incoming",
    data={
        'CallSid': 'test123',
        'From': '++91XXXXXXXXXX',
        'To': Config.EXOTEL_SUBDOMAIN,
        'provider': 'exotel'
    }
)
print(response.text)
```

## 📋 Exotel vs Twilio

Both are configured! You can use either:

- **Exotel**: Better for India, local support
- **Twilio**: Global, more features

Your app supports both - just configure the webhook for the one you want to use.

## 🔍 Exotel API Endpoints

Your app handles Exotel webhooks at:
- `POST /webhook/incoming` - Incoming calls
- `POST /webhook/status` - Call status updates

## 📚 Resources

- Exotel Dashboard: https://my.exotel.com
- Exotel Docs: https://developer.exotel.com
- API Reference: https://developer.exotel.com/api

---

**Your Exotel credentials are configured in `.env`!** ✅




