# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


from backend.database import engine, Base
from backend.routers import calls, webhook, tools
from backend.seed import seed_appointments
from backend.database import SessionLocal

# Creates all tables from models.py automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Voice AI Agent — Appointment Reminder",
    version="1.0.0"
)

# Allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)

@app.get("/app")
def serve_ui():
    return FileResponse("frontend/index.html")
# Mount routers
app.include_router(calls.router)
app.include_router(webhook.router)
app.include_router(tools.router)


@app.on_event("startup")
def on_startup():
    # Seed demo appointments on first run
    db = SessionLocal()
    try:
        seed_appointments(db)
    finally:
        db.close()


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Voice AI Agent"}


@app.get("/api/appointments")
def list_appointments(db=None):
    from backend.database import SessionLocal
    from backend.models import Appointment
    db = SessionLocal()
    appointments = db.query(Appointment).all()
    return [
        {
            "id": a.id,
            "phone_number": a.phone_number,
            "patient_name": a.patient_name,
            "appointment_date": a.appointment_date,
            "appointment_time": a.appointment_time,
            "doctor_name": a.doctor_name,
            "status": a.status,
            "is_demo": a.is_demo,
        }
        for a in appointments
    ]