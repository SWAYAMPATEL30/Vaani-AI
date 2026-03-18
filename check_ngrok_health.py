import sys
sys.stdout.reconfigure(encoding='utf-8')

"""
Check if the ngrok public URL configured in WEBHOOK_BASE_URL is actually
reachable and correctly forwarding to the local Flask server.
"""

import requests
from config import Config


def main():
    url = f"{Config.WEBHOOK_BASE_URL}/health"
    print("Requesting:", url)
    try:
        resp = requests.get(url, timeout=10)
        print("status:", resp.status_code)
        print(resp.text[:500])
    except Exception as e:
        print("ERROR while requesting ngrok URL:", e)


if __name__ == "__main__":
    main()

