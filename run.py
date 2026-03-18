"""
Production runner for Voice Calling Agent
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)




