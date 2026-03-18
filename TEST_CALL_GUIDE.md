# 📞 Test Call Guide - Get a Call on Your Phone

## 🎯 Goal
Receive a call on your phone (++91XXXXXXXXXX) from the AI voice agent.

## 📋 Step-by-Step Instructions

### Step 1: Start Flask Server
```bash
python app.py
```
Keep this running in Terminal 1.

### Step 2: Install & Start ngrok

**If ngrok is not installed:**
1. Download from: https://ngrok.com/download
2. Extract and add to PATH
3. Configure authtoken (already done):
   ```bash
   ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
   ```

**Start ngrok:**
```bash
ngrok http 5000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Step 3: Update .env with ngrok URL

Update `.env`:
```
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

**Restart Flask server** after updating.

### Step 4: Make Test Call

**Option A: Use Python Script**
```bash
python make_test_call.py
```

**Option B: Use curl**
```bash
curl.exe -X POST https://api.twilio.com/2010-04-01/Accounts/YOUR_TWILIO_ACCOUNT_SID/Calls.json ^
  --data-urlencode "Url=https://your-ngrok-url.ngrok.io/webhook/incoming" ^
  --data-urlencode "To=++91XXXXXXXXXX" ^
  --data-urlencode "From=+1XXXXXXXXXX" ^
  -u "YOUR_TWILIO_ACCOUNT_SID:YOUR_TWILIO_AUTH_TOKEN"
```

**Option C: Use Twilio Console**
1. Go to: https://console.twilio.com
2. Phone Numbers → Your Number → Configure
3. Set webhook: `https://your-ngrok-url.ngrok.io/webhook/incoming`
4. Call your number from another phone

## 🎤 What Happens During the Call

1. **Call connects** → Twilio sends webhook to your server
2. **Server responds** → Returns TwiML with greeting
3. **You speak** → Twilio captures audio
4. **Audio transcribed** → AssemblyAI converts to text
5. **AI responds** → Gemini generates response
6. **Response spoken** → ElevenLabs TTS converts to speech
7. **You hear** → AI response played back

## 🔍 Troubleshooting

### "Cannot connect to server"
- Make sure Flask is running: `python app.py`
- Check port 5000 is not blocked

### "Twilio webhook failed"
- Make sure ngrok is running
- Verify WEBHOOK_BASE_URL in .env matches ngrok URL
- Check ngrok URL is HTTPS (not HTTP)

### "No response from AI"
- Check Gemini API key in .env
- Check server logs for errors
- Verify all services are configured

### "Call connects but no audio"
- Check ElevenLabs API key
- Check AssemblyAI API key
- View server logs for errors

## ✅ Quick Test Checklist

- [ ] Flask server running (`python app.py`)
- [ ] ngrok running (`ngrok http 5000`)
- [ ] WEBHOOK_BASE_URL updated in .env
- [ ] Flask server restarted after .env update
- [ ] All API keys configured
- [ ] Test call made

## 🎉 Success!

When everything works:
- 📱 You'll receive a call on ++91XXXXXXXXXX
- 🤖 AI agent will greet you
- 💬 You can have a conversation
- 📝 Call will be logged in database

---

**Ready to test? Run `python make_test_call.py` after setting up ngrok!**




