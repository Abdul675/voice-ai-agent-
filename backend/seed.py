# backend/seed.py

from backend.models import Appointment
from sqlalchemy.orm import Session


def seed_appointments(db: Session):
    # Only seed if table is empty
    existing = db.query(Appointment).first()
    if existing:
        return

    demo_appointments = [
        Appointment(
            phone_number="+923157332105",
            patient_name="Abdul Hameed",
            appointment_date="2026-05-26",
            appointment_time="10:30 AM",
            doctor_name="Dr. Ahmed",
            location="Block B, Room 204",
            status="scheduled",
            is_demo=False,
        ),
        Appointment(
            phone_number="+923166343922",
            patient_name="Sara Khan",
            appointment_date="2026-05-27",
            appointment_time="2:00 PM",
            doctor_name="Dr. Fatima",
            location="Block A, Room 101",
            status="scheduled",
            is_demo=False,
        ),
        Appointment(
            phone_number="",
            patient_name="Usman Ali",
            appointment_date="2026-05-28",
            appointment_time="11:00 AM",
            doctor_name="Dr. Raza",
            location="Block C, Room 305",
            status="scheduled",
            is_demo=False,
        ),
    ]

    db.add_all(demo_appointments)
    db.commit()
    print("Seeded 3 demo appointments")
