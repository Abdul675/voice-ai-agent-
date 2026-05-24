from backend.database import Base, SessionLocal, engine
from backend.models import Appointment, Call, Transcript
from backend.seed import seed_appointments


def clear_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        db.query(Transcript).delete(synchronize_session=False)
        db.query(Call).delete(synchronize_session=False)
        db.query(Appointment).delete(synchronize_session=False)
        db.commit()
        print("Deleted all database records")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def reset_database():
    clear_database()

    db = SessionLocal()
    try:
        seed_appointments(db)
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
    print("Database reset complete")
