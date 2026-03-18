"""
Database models for Voice Calling Agent
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# Initialize db here - will be configured in app.py
db = SQLAlchemy()


class Call(db.Model):
    """Call record model"""
    __tablename__ = 'calls'
    
    id = Column(Integer, primary_key=True)
    call_sid = Column(String(255), unique=True, nullable=False, index=True)
    from_number = Column(String(50))
    to_number = Column(String(50))
    status = Column(String(50), default='ringing')  # ringing, answered, completed, failed
    provider = Column(String(50))  # exotel, twilio, etc.
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration = Column(Float)  # in seconds
    
    # Relationships
    transcripts = relationship('CallTranscript', back_populates='call', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Call {self.call_sid}>'
    
    def calculate_duration(self):
        """Calculate call duration"""
        if self.start_time and self.end_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
            return self.duration
        return None


class CallTranscript(db.Model):
    """Call transcript model"""
    __tablename__ = 'call_transcripts'
    
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, ForeignKey('calls.id'), nullable=False)
    text = Column(Text, nullable=False)
    is_final = Column(String(10), default='false')  # true/false
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    speaker = Column(String(50))  # user or agent
    
    # Relationships
    call = relationship('Call', back_populates='transcripts')
    
    def __repr__(self):
        return f'<CallTranscript {self.id} for Call {self.call_id}>'

