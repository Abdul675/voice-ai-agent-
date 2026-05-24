# backend/routers/calls.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Call, Appointment, Transcript
from backend.schemas import CallRequest, CallResponse, CallListItem, CallDetail
from backend.services.appointment import get_or_create_appointment
from backend.services.vapi import trigger_outbound_call

router = APIRouter(prefix="/api/calls", tags=["calls"])


# ─────────────────────────────────────────
# POST /api/calls
# UI sends phone number → lookup DB → trigger Vapi call
# ─────────────────────────────────────────
@router.post("", response_model=CallResponse)
async def create_call(
    request: CallRequest,
    db: Session = Depends(get_db),
):
    # 1. Get or create appointment for this phone number
    appointment, is_demo = get_or_create_appointment(request.phone_number, db)

    # 2. Create a call record in DB with status "initiated"
    call = Call(
        appointment_id=appointment.id,
        phone_number=request.phone_number,
        status="initiated",
    )
    db.add(call)
    db.commit()
    db.refresh(call)

    # 3. Build variables to inject into Vapi system prompt
    variables = {
        "patient_name":      appointment.patient_name,
        "appointment_date":  appointment.appointment_date,
        "appointment_time":  appointment.appointment_time,
        "doctor_name":       appointment.doctor_name,
        "location":          appointment.location,
        "appointment_id":    str(appointment.id),
        "call_id":           str(call.id),
    }

    # 4. Trigger Vapi outbound call
    try:
        vapi_response = await trigger_outbound_call(
            phone_number=request.phone_number,
            variables=variables,
        )
    except Exception as e:
        # Update call status to failed if Vapi errors
        call.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=str(e))

    # 5. Update call record with Vapi call ID
    call.vapi_call_id = vapi_response.get("id")
    call.status = "ringing"
    db.commit()
    db.refresh(call)

    return CallResponse(
        call_id=call.id,
        appointment_id=appointment.id,
        vapi_call_id=call.vapi_call_id,
        status=call.status,
        is_demo=is_demo,
        patient_name=appointment.patient_name,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        doctor_name=appointment.doctor_name,
    )


# ─────────────────────────────────────────
# GET /api/calls
# Returns all calls — for UI history table
# ─────────────────────────────────────────
@router.get("", response_model=list[CallListItem])
def list_calls(db: Session = Depends(get_db)):
    calls = (
        db.query(Call, Appointment)
        .join(Appointment, Call.appointment_id == Appointment.id)
        .order_by(Call.id.desc())
        .all()
    )

    result = []
    for call, appt in calls:
        result.append(
            CallListItem(
                call_id=call.id,
                phone_number=call.phone_number,
                patient_name=appt.patient_name,
                status=call.status,
                outcome=call.outcome,
                duration_seconds=call.duration_seconds,
                started_at=str(call.started_at) if call.started_at else None,
                ended_at=str(call.ended_at) if call.ended_at else None,
            )
        )
    return result


# ─────────────────────────────────────────
# GET /api/calls/{call_id}
# Returns single call with transcript
# ─────────────────────────────────────────
@router.get("/{call_id}", response_model=CallDetail)
def get_call(call_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(Call, Appointment)
        .join(Appointment, Call.appointment_id == Appointment.id)
        .filter(Call.id == call_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Call not found")

    call, appt = result

    # Fetch transcripts for this call
    transcripts = (
        db.query(Transcript)
        .filter(Transcript.call_id == call_id)
        .order_by(Transcript.id.asc())
        .all()
    )

    transcript_list = [
        {
            "role": t.role,
            "message": t.message,
            "timestamp": str(t.timestamp) if t.timestamp else None,
        }
        for t in transcripts
    ]

    return CallDetail(
        call_id=call.id,
        appointment_id=appt.id,
        phone_number=call.phone_number,
        patient_name=appt.patient_name,
        appointment_date=appt.appointment_date,
        appointment_time=appt.appointment_time,
        doctor_name=appt.doctor_name,
        location=appt.location,
        status=call.status,
        outcome=call.outcome,
        duration_seconds=call.duration_seconds,
        vapi_call_id=call.vapi_call_id,
        started_at=str(call.started_at) if call.started_at else None,
        ended_at=str(call.ended_at) if call.ended_at else None,
        transcripts=transcript_list,
    )