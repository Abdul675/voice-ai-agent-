# backend/routers/webhooks.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend.models import Call, Transcript

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/vapi")
async def vapi_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Single endpoint that receives ALL events from Vapi.
    Vapi sends different event types — we handle each one separately.
    """

    body = await request.json()
    event_type = body.get("message", {}).get("type")

    print(f"📨 Vapi webhook received: {event_type}")

    # ── 1. CALL STARTED ──────────────────────────────────────
    if event_type == "call-started":
        await handle_call_started(body, db)

    # ── 2. TRANSCRIPT (live, fires on every sentence) ────────
    elif event_type == "transcript":
        await handle_transcript(body, db)

    # ── 3. END OF CALL REPORT (fires after call ends) ────────
    elif event_type == "end-of-call-report":
        await handle_end_of_call(body, db)

    # ── 4. HANG (call hung up) ────────────────────────────────
    elif event_type == "hang":
        await handle_hang(body, db)

    # Always return 200 to Vapi — if you return anything else
    # Vapi will retry the webhook repeatedly
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────────────────────

async def handle_call_started(body: dict, db: Session):
    """
    Fired the moment the call connects.
    Updates call status from 'ringing' to 'in_progress'.
    """
    vapi_call_id = body.get("message", {}).get("call", {}).get("id")
    if not vapi_call_id:
        return

    call = db.query(Call).filter(Call.vapi_call_id == vapi_call_id).first()
    if call:
        call.status = "in_progress"
        call.started_at = datetime.utcnow()
        db.commit()
        print(f"✅ Call {call.id} started")


async def handle_transcript(body: dict, db: Session):
    """
    Fired on every sentence spoken during the call.
    role is either 'assistant' (agent) or 'user' (patient).
    Saves each sentence as a row in transcripts table.
    """
    message = body.get("message", {})
    vapi_call_id = message.get("call", {}).get("id")
    role = message.get("role")           # "assistant" or "user"
    transcript_text = message.get("transcript")
    transcript_type = message.get("transcriptType")  # "partial" or "final"

    # Only save final transcripts — not partial (partial fires every word)
    if transcript_type != "final":
        return

    if not vapi_call_id or not transcript_text:
        return

    call = db.query(Call).filter(Call.vapi_call_id == vapi_call_id).first()
    if not call:
        return

    transcript = Transcript(
        call_id=call.id,
        role="agent" if role == "assistant" else "user",
        message=transcript_text.strip(),
        timestamp=datetime.utcnow(),
    )
    db.add(transcript)
    db.commit()
    print(f"💬 Transcript saved [{role}]: {transcript_text[:60]}...")


async def handle_end_of_call(body: dict, db: Session):
    """
    Fired after the call fully ends.
    Contains duration, ended reason, full transcript, and summary.
    This is where we finalize the call record.
    """
    message = body.get("message", {})
    vapi_call_id = message.get("call", {}).get("id")
    ended_reason = message.get("endedReason", "unknown")
    duration = message.get("durationSeconds") or 0

    if not vapi_call_id:
        return

    call = db.query(Call).filter(Call.vapi_call_id == vapi_call_id).first()
    if not call:
        return

    # Map Vapi ended reason to our status
    if ended_reason in ("assistant-ended-call", "customer-ended-call"):
        call.status = "completed"
    elif ended_reason in ("no-answer", "voicemail"):
        call.status = "failed"
        call.outcome = "no_answer"
    else:
        call.status = "completed"

    call.duration_seconds = int(duration)
    call.ended_at = datetime.utcnow()

    # If outcome was not already set by a tool call mid-call,
    # try to infer it from the ended reason
    if not call.outcome:
        if ended_reason == "no-answer":
            call.outcome = "no_answer"
        elif ended_reason == "voicemail":
            call.outcome = "voicemail"
        else:
            call.outcome = "unknown"

    db.commit()
    print(f"📞 Call {call.id} ended — reason: {ended_reason}, outcome: {call.outcome}")


async def handle_hang(body: dict, db: Session):
    """
    Fired if the call hangs unexpectedly.
    """
    vapi_call_id = body.get("message", {}).get("call", {}).get("id")
    if not vapi_call_id:
        return

    call = db.query(Call).filter(Call.vapi_call_id == vapi_call_id).first()
    if call and call.status not in ("completed", "failed"):
        call.status = "failed"
        call.ended_at = datetime.utcnow()
        db.commit()
        print(f"⚠️ Call {call.id} hung unexpectedly")