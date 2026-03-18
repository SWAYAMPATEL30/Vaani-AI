"""Check active call jobs"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from app import CALL_JOBS, CALL_JOBS_LOCK
import json
from datetime import datetime

with CALL_JOBS_LOCK:
    jobs = dict(CALL_JOBS)

if jobs:
    print(f"Active jobs ({len(jobs)}):")
    for call_sid, job in jobs.items():
        print(f"  {call_sid}:")
        print(f"    Status: {job.get('status')}")
        print(f"    Audio URL: {job.get('audio_url')}")
        print(f"    Error: {job.get('error')}")
        print(f"    Updated: {job.get('updated_at')}")
else:
    print("No active jobs")
