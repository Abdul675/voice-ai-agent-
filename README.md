# MedCall AI - Voice Appointment Reminder Agent

MedCall AI is a local-first voice automation project for outbound medical appointment reminders. It combines a FastAPI backend, a lightweight browser UI, SQLite persistence, and Vapi-powered phone calls so a clinic can call patients, confirm appointments, collect reschedule/cancel requests, and track call history.

The project is designed for local development with ngrok, which lets Vapi communicate with your machine while you build and test.

## Features

- Outbound appointment reminder calls through Vapi
- Simple web UI for triggering calls and viewing history
- Appointment seed data for quick testing
- SQLite database with appointments, calls, and transcripts
- Vapi webhook endpoint for call lifecycle events
- Tool endpoints for confirm, reschedule, and cancel actions
- Local reset script to clear the database and reseed demo records
- ngrok-ready setup for testing webhooks from Vapi

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Vapi API
- ngrok
- HTML, CSS, and vanilla JavaScript
- uv for dependency management

## Project Structure

```text
.
+-- backend/
|   +-- main.py              # FastAPI app, routes, static UI serving
|   +-- config.py            # Environment-based settings
|   +-- database.py          # SQLAlchemy engine/session setup
|   +-- models.py            # Appointment, Call, Transcript models
|   +-- schemas.py           # Pydantic request/response schemas
|   +-- seed.py              # Demo appointment seed data
|   +-- reset_db.py          # Clear database and reseed
|   +-- routers/
|   |   +-- calls.py         # Create/list/detail calls
|   |   +-- webhook.py       # Vapi webhook events
|   |   +-- tools.py         # Vapi tool callback endpoints
|   +-- services/
|       +-- appointment.py   # Appointment lookup/create logic
|       +-- vapi.py          # Vapi outbound call API client
+-- frontend/
|   +-- index.html           # Browser UI
+-- pyproject.toml
+-- uv.lock
+-- README.md
```

## Environment Variables

Create a `.env` file in the project root:

```env
VAPI_API_KEY=your_vapi_api_key
VAPI_ASSISTANT_ID=your_vapi_assistant_id
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id
DATABASE_URL=sqlite:///./voice_agent.db
```

Do not commit `.env` to GitHub. It contains secrets.

## Install

From the project root:

```powershell
cd F:\vapi
uv sync
```

If you are not using `uv`, create a virtual environment and install the dependencies from `pyproject.toml`.

## Run Locally

Start the FastAPI app:

```powershell
cd F:\vapi
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the local UI:

```text
http://localhost:8000/app
```

Health check:

```text
http://localhost:8000/
```

Appointments API:

```text
http://localhost:8000/api/appointments
```

## Run With ngrok

Start the app first:

```powershell
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

In another terminal:

```powershell
ngrok http 8000
```

ngrok will provide a public HTTPS URL, for example:

```text
https://napping-quality-marbling.ngrok-free.dev
```

Open the UI through ngrok:

```text
https://napping-quality-marbling.ngrok-free.dev/app
```

## Vapi Configuration

Use your current ngrok domain as the base URL.

Vapi webhook/server URL:

```text
https://your-ngrok-domain.ngrok-free.dev/api/webhooks/vapi
```

Tool callback URLs:

```text
confirmAppointment:
https://your-ngrok-domain.ngrok-free.dev/api/tools/confirm

rescheduleAppointment:
https://your-ngrok-domain.ngrok-free.dev/api/tools/reschedule

cancelAppointment:
https://your-ngrok-domain.ngrok-free.dev/api/tools/cancel
```

If you use a free ngrok URL, it may change when you restart ngrok. Update the Vapi URLs whenever the domain changes.

## Trigger a Call

From the UI, enter a phone number and start the call.

You can also test directly with PowerShell:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/api/calls" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"phone_number":"+923157332105"}'
```

Through ngrok:

```powershell
Invoke-RestMethod `
  -Uri "https://your-ngrok-domain.ngrok-free.dev/api/calls" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"phone_number":"+923157332105"}'
```

## Reset and Reseed the Database

To clear all database records and reload the seed appointments:

```powershell
cd F:\vapi
uv run python -m backend.reset_db
```

This deletes records in this order:

```text
transcripts -> calls -> appointments
```

Then it runs `backend/seed.py` again.

To change the starting records, edit:

```text
backend/seed.py
```

Then run the reset command again.

## API Endpoints

```text
GET  /                         Health check
GET  /app                      Browser UI
GET  /api/appointments         List appointments
POST /api/calls                Trigger outbound Vapi call
GET  /api/calls                List calls
GET  /api/calls/{call_id}      Get call detail and transcripts
POST /api/webhooks/vapi        Vapi lifecycle webhook
POST /api/tools/confirm        Confirm appointment tool endpoint
POST /api/tools/reschedule     Reschedule appointment tool endpoint
POST /api/tools/cancel         Cancel appointment tool endpoint
```

## How It Works

1. The user starts a call from the UI.
2. The frontend sends `POST /api/calls` with a phone number.
3. The backend finds or creates an appointment.
4. The backend creates a local call record.
5. The backend calls `https://api.vapi.ai/call`.
6. Vapi places the outbound phone call.
7. Vapi sends call events back to `/api/webhooks/vapi`.
8. If the assistant uses tools, Vapi calls the configured tool URLs.
9. The UI displays call status, history, and appointment data.

## Notes

- The outbound call request is implemented in `backend/services/vapi.py`.
- The browser UI is served from `frontend/index.html` at `/app`.
- The SQLite database is local and ignored by Git.
- Tool callback format may need adjustment depending on your current Vapi tool configuration.

## GitHub Upload Checklist

Before pushing:

```powershell
git status
```

Make sure these are not committed:

```text
.env
voice_agent.db
.venv/
__pycache__/
```

Initialize and push:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

## Future Improvements

- Update tool callback handling to support Vapi's latest `tool-calls` payload format
- Add authentication for dashboard access
- Add webhook signature verification
- Add tests for routers and Vapi service calls
- Add Docker support for easier deployment
- Replace SQLite with PostgreSQL for production

## License

This project is available for portfolio and educational use. Add a license file before using it in production or distributing it publicly.
