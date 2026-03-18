"""Check recent call status and transcripts"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from models import Call, CallTranscript, db
from app import app

with app.app_context():
    calls = Call.query.order_by(Call.start_time.desc()).limit(3).all()
    print('Recent calls:')
    for c in calls:
        print(f"  {c.call_sid} - {c.status} - {c.start_time}")
    
    latest = Call.query.order_by(Call.start_time.desc()).first()
    if latest:
        transcripts = CallTranscript.query.filter_by(call_id=latest.id).order_by(CallTranscript.timestamp).all()
        print(f'\nCall {latest.call_sid} transcripts ({len(transcripts)}):')
        for t in transcripts:
            print(f"  [{t.speaker}] {t.text[:100]}")
