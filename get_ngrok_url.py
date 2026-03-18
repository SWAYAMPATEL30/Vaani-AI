"""
Get ngrok public URL
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests



def get_ngrok_public_url():
    """Return the first ngrok public_url if ngrok is running, else None."""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        data = response.json()

        tunnels = data.get("tunnels") or []
        if not tunnels:
            print("No tunnels found. Make sure ngrok is running.")
            return None

        public_url = tunnels[0].get("public_url")
        if public_url:
            print(f"Found ngrok URL: {public_url}")
            print()
            print("Update .env with:")
            print(f"WEBHOOK_BASE_URL={public_url}")
            return public_url

        print("ngrok tunnel has no public_url field.")
        return None
    except requests.exceptions.ConnectionError:
        print("Cannot connect to ngrok API. Is ngrok running?")
        print("Run: ngrok http 5000  (or: ngrok start voice-agent --config ngrok.yml)")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    get_ngrok_public_url()




