@echo off
echo Starting ngrok tunnel for Voice Calling Agent...
echo.
echo Make sure your Flask server is running on port 5000 first!
echo.
ngrok http 5000
pause




