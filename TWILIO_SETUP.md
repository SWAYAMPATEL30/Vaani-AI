# 📞 Twilio Setup Guide

## ✅ Your Twilio Credentials (Already Configured)

- **Account SID**: `YOUR_TWILIO_ACCOUNT_SID`
- **Auth Token**: `YOUR_TWILIO_AUTH_TOKEN`
- **Phone Number**: `+1XXXXXXXXXX`

## 🔧 Setup Steps

### 1. Configure Webhook in Twilio Console

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number: `+1XXXXXXXXXX`
3. Scroll to "Voice & Fax" section
4. Set **A CALL COMES IN** webhook:
   ```
   http://your-deployed-url.com/webhook/incoming
   ```
   Or for local testing with ngrok:
   ```
   https://your-ngrok-url.ngrok.io/webhook/incoming
   ```
5. Set **HTTP Method**: `POST`
6. Save

### 2. Test Locally with ngrok

```bash
# Install ngrok
# Download from: https://ngrok.com/download

# Start your Flask server
python app.py

# In another terminal, start ngrok
ngrok http 5000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Update .env: WEBHOOK_BASE_URL=https://abc123.ngrok.io
# Update Twilio webhook to: https://abc123.ngrok.io/webhook/incoming
```

### 3. Make a Test Call

```bash
# Test Twilio connection
python test_twilio.py

# Or use curl (from your provided example)
curl.exe -X POST https://api.twilio.com/2010-04-01/Accounts/YOUR_TWILIO_ACCOUNT_SID/Calls.json ^
  --data-urlencode "Url=http://your-webhook-url/webhook/incoming" ^
  --data-urlencode "To=++91XXXXXXXXXX" ^
  --data-urlencode "From=+1XXXXXXXXXX" ^
  -u "YOUR_TWILIO_ACCOUNT_SID:YOUR_TWILIO_AUTH_TOKEN"
```

### 4. Deploy and Update Webhook

After deploying to Render/Railway/Vercel:
1. Get your deployment URL
2. Update `.env`: `WEBHOOK_BASE_URL=https://your-app.onrender.com`
3. Update Twilio webhook in console

## 🎯 What Happens When a Call Comes In

1. **Call arrives** → Twilio sends webhook to `/webhook/incoming`
2. **Your server responds** with TwiML (XML) to handle the call
3. **User speaks** → Twilio captures audio
4. **Audio sent** → To AssemblyAI for transcription
5. **Text processed** → OpenAI generates response
6. **Response converted** → ElevenLabs TTS creates audio
7. **Audio played** → Back to caller via Twilio

## 🔍 Testing Checklist

- [ ] Twilio credentials in `.env`
- [ ] Flask server running (`python app.py`)
- [ ] Webhook URL configured in Twilio console
- [ ] Test call made successfully
- [ ] Call logs visible in `/api/calls`
- [ ] Transcripts saved in database

## 🐛 Troubleshooting

### Webhook not receiving calls
- Check ngrok is running (for local testing)
- Verify webhook URL in Twilio console
- Check Flask server logs for errors
- Test webhook with: `curl -X POST http://localhost:5000/webhook/incoming`

### Call connects but no response
- Check AssemblyAI API key
- Check OpenAI API key
- Check ElevenLabs API key
- View server logs for errors

### Audio not playing
- Verify ElevenLabs API key is valid
- Check TTS service logs
- Test TTS separately: `python demo.py`

## 📚 Resources

- Twilio Docs: https://www.twilio.com/docs/voice
- TwiML Reference: https://www.twilio.com/docs/voice/twiml
- Your Twilio Console: https://console.twilio.com/




