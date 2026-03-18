# 🌐 ngrok Setup Guide

## ✅ Your ngrok Authtoken (Configured)

**Authtoken**: `YOUR_NGROK_AUTHTOKEN`

## 🚀 Quick Setup

### Step 1: Configure Authtoken

**Windows:**
```bash
setup_ngrok.bat
```

**Linux/Mac:**
```bash
chmod +x setup_ngrok.sh
./setup_ngrok.sh
```

**Or manually:**
```bash
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

### Step 2: Start ngrok Tunnel

```bash
# Make sure your Flask server is running first
python app.py

# In another terminal, start ngrok
ngrok http 5000
```

### Step 3: Copy the HTTPS URL

ngrok will show something like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Step 4: Update .env

```env
WEBHOOK_BASE_URL=https://abc123.ngrok.io
```

### Step 5: Restart Flask Server

Restart your Flask server so it picks up the new webhook URL.

## 📋 Complete Workflow

```bash
# Terminal 1: Start Flask
python app.py

# Terminal 2: Start ngrok
ngrok http 5000

# Terminal 3: Update .env with ngrok URL
# Then restart Flask server
```

## 🔧 Configure Telephony Webhooks

### For Twilio:
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your number
3. Set webhook: `https://your-ngrok-url.ngrok.io/webhook/incoming`

### For Exotel:
1. Go to Exotel Dashboard → Settings → Webhooks
2. Set webhook: `https://your-ngrok-url.ngrok.io/webhook/incoming`

## 🎯 Testing

Once ngrok is running, test your webhook:

```bash
curl -X POST https://your-ngrok-url.ngrok.io/webhook/incoming \
  -d "CallSid=test123&From=++91XXXXXXXXXX&To=+1XXXXXXXXXX"
```

## ⚠️ Important Notes

1. **ngrok URL changes** each time you restart (unless you have a paid plan)
2. **Update webhooks** in Twilio/Exotel when URL changes
3. **Free tier** has session limits (8 hours)
4. **For production**, deploy to Render/Railway instead of using ngrok

## 🚀 Production Alternative

Instead of ngrok for production:
- Deploy to Render.com (free tier)
- Deploy to Railway.app
- Use your own domain with SSL

ngrok is only needed for **local testing**!

---

**Your ngrok authtoken is configured! Run `setup_ngrok.bat` (Windows) or `setup_ngrok.sh` (Linux/Mac) to set it up.** ✅




