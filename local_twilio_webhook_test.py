import sys
sys.stdout.reconfigure(encoding='utf-8')

"""
Quick local test of the Flask Twilio webhooks without using Twilio.
This helps debug 'application error' issues by printing the exact TwiML.
"""

import requests


def main():
    base = "http://127.0.0.1:5000"

    print("--- Testing /webhook/incoming ---")
    resp = requests.post(
        f"{base}/webhook/incoming",
        data={"CallSid": "TESTCALL123", "From": "+111", "To": "+222"},
    )
    print("status:", resp.status_code)
    print(resp.text)

    print("\n--- Testing /webhook/transcription ---")
    resp2 = requests.post(
        f"{base}/webhook/transcription",
        data={
            "CallSid": "TESTCALL123",
            "SpeechResult": "नमस्ते",
            "From": "+111",
            "To": "+222",
        },
    )
    print("status:", resp2.status_code)
    print(resp2.text)

    print("\n--- Testing /webhook/poll ---")
    resp3 = requests.post(
        f"{base}/webhook/poll",
        data={"CallSid": "TESTCALL123"},
    )
    print("status:", resp3.status_code)
    print(resp3.text)


if __name__ == "__main__":
    main()

