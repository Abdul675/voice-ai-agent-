# backend/models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id                  = Column(Integer, primary_key=True, index=True)
    phone_number        = Column(String, nullable=False, index=True)
    patient_name        = Column(String, nullable=False)
    appointment_date    = Column(String, nullable=False)   # "2026-05-26"
    appointment_time    = Column(String, nullable=False)   # "10:30 AM"
    doctor_name         = Column(String, nullable=False)
    location            = Column(String, default="Main Clinic")
    status              = Column(String, default="scheduled")
    # scheduled | confirmed | cancelled | reschedule_requested
    is_demo             = Column(Boolean, default=False)
    created_at          = Column(DateTime, server_default=func.now())

    # one appointment can have many calls
    calls = relationship("Call", back_populates="appointment")


class Call(Base):
    __tablename__ = "calls"

    id                  = Column(Integer, primary_key=True, index=True)
    appointment_id      = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    phone_number        = Column(String, nullable=False)
    vapi_call_id        = Column(String, nullable=True)    # filled after Vapi responds
    status              = Column(String, default="initiated")
    # initiated | ringing | in_progress | completed | failed
    outcome             = Column(String, nullable=True)
    # confirmed | cancelled | reschedule_requested | no_answer | null
    duration_seconds    = Column(Integer, nullable=True)
    started_at          = Column(DateTime, nullable=True)
    ended_at            = Column(DateTime, nullable=True)
    created_at          = Column(DateTime, server_default=func.now())

    # relationships
    appointment  = relationship("Appointment", back_populates="calls")
    transcripts  = relationship("Transcript", back_populates="call")


class Transcript(Base):
    __tablename__ = "transcripts"

    id          = Column(Integer, primary_key=True, index=True)
    call_id     = Column(Integer, ForeignKey("calls.id"), nullable=False)
    role        = Column(String, nullable=False)   # "agent" or "user"
    message     = Column(Text, nullable=False)
    timestamp   = Column(DateTime, nullable=True)
    confidence  = Column(String, nullable=True)    # Deepgram confidence score
    created_at  = Column(DateTime, server_default=func.now())

    call = relationship("Call", back_populates="transcripts")