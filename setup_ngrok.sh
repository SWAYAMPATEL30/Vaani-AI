#!/bin/bash
echo "Setting up ngrok..."
echo ""
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
echo ""
echo "✅ ngrok authtoken configured!"
echo ""
echo "To start ngrok tunnel, run:"
echo "  ngrok http 5000"




