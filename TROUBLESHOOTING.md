# 🔧 Troubleshooting: Agent Not Talking

## Common Issues & Solutions

### 1. Flask Server Not Running
**Symptom**: No response from webhook

**Solution**:
```bash
# Start Flask server
python app.py

# Should see: "Running on http://0.0.0.0:5000"
```

### 2. ngrok Not Running
**Symptom**: Twilio can't reach your server

**Solution**:
```bash
# Start ngrok
ngrok http 5000

# Verify URL matches .env:
# WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

### 3. Webhook URL Mismatch
**Symptom**: Calls connect but no response

**Check**:
```bash
# Verify .env has correct ngrok URL
python -c "from config import Config; print(Config.WEBHOOK_BASE_URL)"

# Should show: https://2011337d3f31.ngrok-free.app
```

### 4. TwiML Response Issues
**Symptom**: Call connects but silent

**Check Flask logs** for:
- Webhook received
- TwiML generated
- Any errors

### 5. Database Connection Issues
**Symptom**: Errors in logs

**Solution**:
```bash
# Test database
python -c "from app import app, db; app.app_context().push(); from models import Call; print(f'Calls: {Call.query.count()}')"
```

## 🔍 Debugging Steps

### Step 1: Check Server Status
```bash
curl http://localhost:5000/health
```

### Step 2: Test Webhook Locally
```bash
python test_webhook.py
```

### Step 3: Check Flask Logs
Watch your Flask server terminal for:
- Incoming webhook requests
- TwiML generation
- Errors

### Step 4: Check Twilio Logs
1. Go to: https://console.twilio.com/monitor/logs
2. Find your call
3. Check webhook requests/responses

### Step 5: Verify ngrok Tunnel
```bash
# Check ngrok dashboard
# Open: http://localhost:4040
# See incoming requests
```

## 🎯 Quick Fixes

### Restart Everything
```bash
# 1. Stop Flask (Ctrl+C)
# 2. Stop ngrok (Ctrl+C)
# 3. Restart ngrok
ngrok http 5000

# 4. Update .env with new ngrok URL (if changed)
# 5. Restart Flask
python app.py
```

### Test Webhook Directly
```bash
python test_webhook.py
```

### Check Configuration
```bash
python -c "from config import Config; print(f'AI Provider: {Config.AI_PROVIDER}'); print(f'Groq Key: {bool(Config.GROQ_API_KEY)}'); print(f'Webhook URL: {Config.WEBHOOK_BASE_URL}')"
```

## 📞 Expected Flow

1. **Call initiated** → Twilio sends webhook to `/webhook/incoming`
2. **Server responds** → Returns TwiML with greeting
3. **AI speaks** → "Hello! Thank you for calling..."
4. **User speaks** → Twilio captures speech
5. **Webhook called** → `/webhook/transcription` with speech
6. **AI responds** → Groq generates response
7. **AI speaks** → TwiML with AI response
8. **Loop continues**

## ⚠️ Common Errors

### "No module named 'groq'"
```bash
pip install groq
```

### "Database connection failed"
Check Supabase connection string in .env

### "Groq API error"
Verify API key in .env

### "TwiML parse error"
Check for special characters in AI responses (now fixed with HTML escaping)

---

**If still not working, check Flask server logs for detailed error messages!**




