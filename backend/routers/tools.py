# backend/routers/tools.py

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Appointment, Call
from backend.schemas import (
    CancelAppointmentRequest,
    ConfirmAppointmentRequest,
    RescheduleAppointmentRequest,
)

router = APIRouter(prefix="/api/tools", tags=["tools"])


def get_tool_parameters(body: dict) -> dict:
    return body.get("message", {}).get("functionCall", {}).get("parameters", {})


def validate_tool_parameters(schema, params: dict):
    try:
        return schema.model_validate(params)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc


@router.post("/confirm")
async def confirm_appointment(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Called by Vapi agent when patient confirms their appointment.
    Updates appointment status to 'confirmed'.
    """
    body = await request.json()
    params = get_tool_parameters(body)
    data = validate_tool_parameters(ConfirmAppointmentRequest, params)

    print(f"Tool: confirmAppointment - appt_id={data.appointment_id}")

    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id
    ).first()

    if appointment:
        appointment.status = "confirmed"
        db.commit()

    call = db.query(Call).filter(Call.id == data.call_id).first()
    if call:
        call.outcome = "confirmed"
        db.commit()

    return {
        "result": (
            "Perfect! Your appointment has been confirmed. "
            "We look forward to seeing you. "
            "If you need to make any changes, please call us. "
            "Have a great day, goodbye!"
        )
    }


@router.post("/reschedule")
async def reschedule_appointment(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Called by Vapi agent when patient wants to reschedule.
    Updates appointment status to 'reschedule_requested'.
    """
    body = await request.json()
    params = get_tool_parameters(body)
    data = validate_tool_parameters(RescheduleAppointmentRequest, params)

    preferred_time = data.preferred_time or "not specified"
    print(
        "Tool: rescheduleAppointment - "
        f"appt_id={data.appointment_id}, pref={preferred_time}"
    )

    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id
    ).first()

    if appointment:
        appointment.status = "reschedule_requested"
        db.commit()

    call = db.query(Call).filter(Call.id == data.call_id).first()
    if call:
        call.outcome = "reschedule_requested"
        db.commit()

    return {
        "result": (
            "No problem at all. I have noted your request to reschedule. "
            "Someone from our team will call you back shortly to arrange "
            "a new appointment time that works for you. "
            "Thank you and have a good day, goodbye!"
        )
    }


@router.post("/cancel")
async def cancel_appointment(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Called by Vapi agent when patient wants to cancel.
    Updates appointment status to 'cancelled'.
    """
    body = await request.json()
    params = get_tool_parameters(body)
    data = validate_tool_parameters(CancelAppointmentRequest, params)

    reason = data.reason or "not provided"
    print(
        "Tool: cancelAppointment - "
        f"appt_id={data.appointment_id}, reason={reason}"
    )

    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id
    ).first()

    if appointment:
        appointment.status = "cancelled"
        db.commit()

    call = db.query(Call).filter(Call.id == data.call_id).first()
    if call:
        call.outcome = "cancelled"
        db.commit()

    return {
        "result": (
            "I understand. Your appointment has been cancelled. "
            "We are sorry to hear that and hope everything is okay. "
            "Please do not hesitate to call us if you would like to "
            "book a new appointment in the future. Take care, goodbye!"
        )
    }
