# backend/schemas.py

from pydantic import BaseModel, validator
from typing import Optional


class CallRequest(BaseModel):
    phone_number: str

    @validator("phone_number")
    def validate_phone(cls, v):
        # strip spaces, must start with + or digit
        v = v.strip().replace(" ", "")
        if not v:
            raise ValueError("Phone number is required")
        return v


class CallResponse(BaseModel):
    call_id: int
    appointment_id: int
    vapi_call_id: Optional[str]
    status: str
    is_demo: bool
    patient_name: str
    appointment_date: str
    appointment_time: str
    doctor_name: str

    class Config:
        from_attributes = True


class CallListItem(BaseModel):
    call_id: int
    phone_number: str
    patient_name: str
    status: str
    outcome: Optional[str]
    duration_seconds: Optional[int]
    started_at: Optional[str]
    ended_at: Optional[str]

    class Config:
        from_attributes = True


class CallDetail(BaseModel):
    call_id: int
    appointment_id: int
    phone_number: str
    patient_name: str
    appointment_date: str
    appointment_time: str
    doctor_name: str
    location: str
    status: str
    outcome: Optional[str]
    duration_seconds: Optional[int]
    vapi_call_id: Optional[str]
    started_at: Optional[str]
    ended_at: Optional[str]
    transcripts: list

    class Config:
        from_attributes = True


class ConfirmAppointmentRequest(BaseModel):
    appointment_id: int
    call_id: int


class CancelAppointmentRequest(BaseModel):
    appointment_id: int
    call_id: int
    reason: Optional[str] = None


class RescheduleAppointmentRequest(BaseModel):
    appointment_id: int
    call_id: int
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    reason: Optional[str] = None
