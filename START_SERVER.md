# 🚀 Start Server Instructions

## ⚠️ IMPORTANT: Flask Server Must Be Running!

The agent won't talk if the Flask server is not running.

## ✅ Quick Start

### Step 1: Start Flask Server
```bash
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

**Keep this terminal open!** The server must stay running.

### Step 2: Verify ngrok is Running
In another terminal:
```bash
ngrok http 5000
```

You should see:
```
Forwarding  https://xxxxx.ngrok-free.app -> http://localhost:5000
```

### Step 3: Verify Connection
```bash
python test_webhook.py
```

Should return: `✅ Webhook is working!`

## 🔄 Complete Setup

**Terminal 1** (Flask Server):
```bash
cd voice
python app.py
```

**Terminal 2** (ngrok):
```bash
ngrok http 5000
```

**Terminal 3** (Make Test Call):
```bash
cd voice
python make_test_call.py
```

## ✅ Success Indicators

- Flask server shows: "Running on http://0.0.0.0:5000"
- ngrok shows: Active tunnel
- Test webhook returns: 200 OK
- Call connects and AI speaks

## 🐛 If Still Not Working

1. **Check Flask is running**: `curl http://localhost:5000/health`
2. **Check ngrok tunnel**: Open http://localhost:4040
3. **Check logs**: Watch Flask terminal for errors
4. **Restart both**: Stop and restart Flask + ngrok

---

**The Flask server is now starting in the background. Wait a few seconds, then make a test call!**




