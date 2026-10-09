# LoopBack Backend API

FastAPI backend and agent investigation service for the LoopBack waste failure investigation platform.

## Features
- **API Endpoints:**
  - `GET /api/health` — Healthcheck and database status reporting (`mongodb` vs `json_fallback`).
  - `GET /api/incidents` — List all incident records.
  - `GET /api/incidents/{incident_id}` — Retrieve detailed incident records & timeline events.
  - `POST /api/incidents/{incident_id}/investigate` — Run structured AI incident investigation (distinguishing verified facts, hypotheses, missing evidence).
  - `POST /api/incidents/{incident_id}/action` — Human approval control node for proposed actions (`approve` / `reject`).
- **Dual Database Architecture:**
  - Connects to MongoDB when `MONGODB_URI` is provided in `.env`.
  - Automatically falls back to local JSON file storage (`backend/data/seed_incidents.json`) if MongoDB is unavailable.

## Quick Start (Windows PowerShell)

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend server
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API Base:** `http://localhost:8000`
- **Interactive OpenAPI Docs:** `http://localhost:8000/docs`

## Running Tests

```powershell
# Run backend test suite
backend\venv\Scripts\pytest backend/tests/test_api.py -v
```
