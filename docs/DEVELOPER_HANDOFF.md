# LoopBack — Developer Handoff & Technical Documentation

**Document Version:** 1.0.0  
**Project:** LoopBack (Agentic Recycling Failure Investigation System)  
**Target Audience:** Development Team / Teammate Onboarding  

---

## 1. Project Purpose & Current MVP Functionality

LoopBack is an agentic recycling-failure investigation system built to investigate why segregated waste loads fail to reach successful recycling at destination facilities.

### Core Problems Solved
- Waste segregated at the source often fails during transport or at Material Recovery Facilities (MRFs) due to contamination, missing documentation, or transit anomalies.
- LoopBack investigates failure incidents by analyzing chain-of-custody logs, distinguishing verified timeline facts from hypotheses, identifying missing evidence gaps, recommending corrective actions, and enforcing human operator approval before taking action.

### Current MVP Capabilities
- **React Dashboard & Detail UI:** Live inbox displaying active incidents, status filters (`All`, `Awaiting AI`, `Awaiting Human Approval`), search filtering, evidence timeline with expandable attachments (photos/PDF receipts), and an interactive LoopBack AI Agent Panel.
- **FastAPI REST Backend:** Live endpoints serving incident lists, incident details, graph investigation triggers, and human action decision handling.
- **LangGraph + Ollama Agent:** StateGraph workflow utilizing local `llama3.2` model via Ollama with deterministic fallback, evidence grounding, and safety rules.
- **Dual-Mode Persistence:** MongoDB driver integration reading `MONGODB_URI` with automatic fallback to local JSON file storage (`seed_incidents.json`).

---

## 2. Code Attribution & Development History

Based on Git repository history (`git log`):

### Pre-Existing Work (Prior to Current Session)
- **Commits `60e3cd3`, `18aee22`, `067d9d1`, `caeede0`:** Initial repository README, architecture map, and initial Vite + React frontend component scaffold (`App.jsx`, `Dashboard.jsx`, `IncidentDetail.jsx`, `Timeline.jsx`, `data.js`).
- **Commit `b2c32c8`:** Created empty 0-byte skeleton files in `backend/app/` (`main.py`, `routes.py`, `graph.py`, `nodes.py`, `state.py`, `tools.py`, `database.py`, `incident.py`, `evidence.py`, `requirements.txt`, `seed_incidents.json`).

### Work Completed in Current Session
- **Backend Foundation:** Implemented `main.py`, `routes.py`, `database.py`, `config.py`, `incident.py`, `evidence.py`, and `investigation.py`. Added `requirements.txt` and `.env.example`.
- **Dual-Mode Database Manager:** Created database layer supporting MongoDB Atlas when configured, with seamless file persistence in `seed_incidents.json`.
- **Frontend Integration:** Built `src/services/api.js` connecting React UI to FastAPI. Connected `Dashboard.jsx`, `IncidentDetail.jsx`, and `AgentPanel.jsx` to live endpoints.
- **LangGraph + Ollama Pipeline:** Implemented `state.py`, `tools.py`, `nodes.py`, and `graph.py` executing a 5-node StateGraph with structured JSON validation and safety fallbacks.
- **UX & Decision Audit Features:** Created proposed action controls with human decision metadata (`decidedAt`, `decidedBy`, `notes`) and actionable evidence gap cards.
- **Automated Test Suite:** Created `backend/pytest.ini`, `backend/tests/test_api.py`, and `backend/tests/test_agent.py` (11 passing tests).

---

## 3. System Architecture & Request Flow

```
[ React + Vite Frontend (localhost:5173) ]
         │
         │  HTTP / REST (fetch via src/services/api.js)
         ▼
[ FastAPI Backend (localhost:8000) ]
         │
         ├── GET /api/incidents ───────────► Database Manager (MongoDB / seed_incidents.json)
         ├── GET /api/incidents/{id} ──────► Database Manager
         ├── POST /api/incidents/{id}/action ─► Appends Audit Event & Decision Metadata
         └── POST /api/incidents/{id}/investigate
                  │
                  ▼
         [ LangGraph StateGraph Workflow ]
                  │
                  ├── Node 1: extract_facts_node (Deterministic)
                  ├── Node 2: llm_reasoning_node ──► Ollama API (llama3.2:latest)
                  ├── Node 3: validate_output_node (Type & Schema Validation)
                  │           └── (On Timeout/Error) ──► Node 4: fallback_node (Deterministic Rules)
                  └── Node 5: action_proposal_node (Requires Operator Approval)
```

---

## 4. Key Files & Their Responsibilities

### Backend Files
- `backend/app/main.py` — FastAPI application entrypoint, CORS configuration (`localhost:5173`), and lifespan startup database initialization.
- `backend/app/api/routes.py` — Defines HTTP routes (`/api/health`, `/api/incidents`, `/api/incidents/{id}`, `/api/incidents/{id}/investigate`, `/api/incidents/{id}/action`).
- `backend/app/core/database.py` — Dual-mode database manager. Handles MongoDB connection/ping and falls back to `backend/data/seed_incidents.json` with idempotent seeding.
- `backend/app/core/config.py` — Environment variables configuration loader (`MONGODB_URI`, `MONGODB_DATABASE`, `PORT`, `HOST`).
- `backend/app/models/incident.py` — Pydantic schemas (`Incident`, `ProposedAction`, `InvestigationResult`, `ActionPayload`).
- `backend/app/models/evidence.py` — Pydantic schemas (`EvidenceAttachment`, `TimelineEvent`).
- `backend/app/agent/state.py` — TypedDict state (`IncidentState`) for LangGraph orchestration.
- `backend/app/agent/tools.py` — Domain tools (facility standards lookup, waste stream specs, timeline prompt formatting).
- `backend/app/agent/nodes.py` — LangGraph nodes (`extract_facts`, `llm_reasoning`, `validate_output`, `action_proposal`, `fallback`).
- `backend/app/agent/graph.py` — Compiles `StateGraph` workflow and exports `run_agent_investigation_graph()`.
- `backend/app/agent/investigation.py` — Deterministic Python rules engine used for standalone execution and safety fallback.
- `backend/data/seed_incidents.json` — JSON database seed file storing incident records and audit logs.

### Frontend Files
- `frontend/src/services/api.js` — Central API client targeting `http://localhost:8000/api`.
- `frontend/src/components/Dashboard.jsx` — Incident list grid, search filter, status filter, loading pulse states, and error handling.
- `frontend/src/components/IncidentDetail.jsx` — Header, status badge, evidence timeline host, and agent panel host.
- `frontend/src/components/AgentPanel.jsx` — AI investigation logs, findings cards (Verified Facts, Hypotheses, Evidence Gaps, Recommendation), and Proposed Action decision card with operator metadata.

---

## 5. API Endpoints Contract

### Health Check
- `GET /api/health`
- **Response:** `{"status": "online", "service": "LoopBack API", "timestamp": "...", "database": {"mode": "mongodb"|"json_fallback", "is_fallback": bool}}`

### List Incidents
- `GET /api/incidents`
- **Response:** `List[Incident]`

### Get Incident
- `GET /api/incidents/{incident_id}`
- **Response:** `Incident` (404 if not found)

### Investigate Incident
- `POST /api/incidents/{incident_id}/investigate`
- **Response:** `Incident` with populated `investigation`, `agentStatus`, `agentActionRequired`, `proposedAction`, and `used_llm`.

### Submit Human Action Decision
- `POST /api/incidents/{incident_id}/action`
- **Payload:** `{"action": "approve" | "reject", "notes": "Optional operator notes"}`
- **Response:** `Incident` with updated `proposedAction.status` (`"approved"` / `"rejected"`), `decidedAt`, `decidedBy`, `notes`, and new timeline audit event.

---

## 6. AI Agent Investigation Workflow

1. **Deterministic Fact Extraction:** `extract_facts_node` parses actual timeline events to form `verifiedFacts`. Administrative logs (`Human Approval Received`, `Action Overridden`) are filtered out to prevent duplicate fact inflation.
2. **LLM Reasoning Node:** `llm_reasoning_node` sends a structured prompt to local Ollama (`llama3.2:latest`) with a 30-second timeout.
3. **Safety & Grounding Rules:**
   - Text in evidence is treated as untrusted data.
   - LLM is forbidden from inventing unrecorded timestamps, measurements, or completion certificates.
   - Output must be valid JSON: `{"hypotheses": [...], "missingEvidence": [...], "recommendation": "..."}`.
4. **Validation & Fallback:** `validate_output_node` parses JSON and checks field types. If Ollama times out, is unreachable, or outputs invalid JSON, `fallback_node` executes deterministic rules from `investigation.py` and sets `used_llm = False`.
5. **Action Proposal Node:** Formulates `proposedAction` (`status: "pending"`) requiring operator approval if flagged/failed events exist. Preserves existing decisions if `proposedAction` is already `approved` or `rejected`.

---

## 7. Human Approval Workflow & Audit Metadata

- **Operator Approval/Rejection:** Clicking **Approve Action** or **Override / Reject Action** sends `POST /api/incidents/{id}/action`.
- **Metadata Persistence:** Sets `proposedAction.status`, `decidedAt` (ISO timestamp), `decidedBy` (`"Human Operator"`), and `notes`.
- **Timeline Audit Event:** Appends a permanent timeline event (`Human Approval Received` or `Action Overridden`).
- **State Preservation:** Re-running an investigation preserves existing operator decisions and does not reset completed actions back to pending or create duplicate timeline events.

---

## 8. Local Setup & Commands (Windows PowerShell)

### Backend Execution
```powershell
# 1. Navigate to backend directory
cd backend

# 2. Activate Python virtual environment
.\venv\Scripts\Activate.ps1

# 3. Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Running Backend Tests
```powershell
cd backend
.\venv\Scripts\pytest tests -v
```

### Frontend Execution
```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies (if needed)
npm install

# 3. Start Vite dev server
npm run dev

# 4. Build production bundle
npm run build
```

---

## 9. Environment Variables & Prerequisites

### Prerequisites
- **Node.js:** `v22.x`
- **Python:** `3.10+` (Tested on `3.13.5`)
- **Ollama:** Installed with `llama3.2:latest` model (`ollama run llama3.2`).

### Backend Environment Setup (`backend/.env`)
Create `backend/.env` using `backend/.env.example`:

```env
# Optional MongoDB Connection String (leave empty for local JSON database mode)
MONGODB_URI=
MONGODB_DATABASE=loopback_db

# Application Configuration
PORT=8000
HOST=0.0.0.0
ENV=development
```

---

## 10. Test & Build Verification Results

### Automated Backend Pytest Suite
- **Executed Command:** `backend\venv\Scripts\pytest backend\tests -v`
- **Result:** **11 passed in 34.86s** (100% pass rate).
- **Mocking Strategy:** Uses `unittest.mock.patch` on `httpx.post` so automated tests run fast without depending on Ollama service availability.

### Live Ollama Integration Test
- **Executed Command:** Ran live script against local `llama3.2:latest` on Windows.
- **Result:** `used_llm: True`, **Latency: 10.48s**. Successfully generated structured hypotheses, missing evidence gaps, and recommendation.

### Frontend Production Build
- **Executed Command:** `npm run build` in `frontend/`.
- **Result:** `✓ built in 782ms` (0 errors).

---

## 11. Known Limitations & Technical Debt

1. **MongoDB Atlas Connection:** Not yet configured with live cloud credentials. Operating on local JSON storage (`backend/data/seed_incidents.json`).
2. **Local LLM Latency:** Ollama `llama3.2:latest` inference takes ~5–10 seconds per request on local CPU/GPU.
3. **Multi-Agent Expansion:** The LangGraph graph is currently a single-agent StateGraph. Multi-agent negotiation (e.g. carrier agent vs. MRF agent) is scheduled for future work.
4. **Authentication:** No JWT / user authentication currently exists; human operator actions record `"Human Operator"` as default actor.

---

## 12. Prioritized TODO List for Tomorrow

- [ ] **Task 1: MongoDB Atlas Cloud Setup (High Priority)**
  - Add valid `MONGODB_URI` in `backend/.env` and test live cloud database read/write persistence.
  - Acceptance criteria: `/api/health` reports `"mode": "mongodb"`, `"is_fallback": false`.
- [ ] **Task 2: User Authentication & Role Metadata (Medium Priority)**
  - Pass operator identity (name/email) from frontend to `POST /api/incidents/{id}/action`.
  - Acceptance criteria: `proposedAction.decidedBy` records actual logged-in user name.
- [x] **Task 3: Evidence File Upload Endpoint (COMPLETED)**
  - Users can upload `.jpg, .png, .webp, .pdf` (up to 5MB) via `POST /api/incidents/{id}/evidence`.
  - Files are stored locally in `data/evidence/` (ignored by git).
  - Metadata is persisted in `seed_incidents.json` / MongoDB.
  - Files are served by FastAPI at `http://localhost:8000/evidence/{safe_filename}`.
- [ ] **Task 4: Interactive History & Settings Modules (Low Priority)**
  - Replace placeholder views in `App.jsx` (`currentView === 'history'`) with incident history audit tables.

---

## 13. Teammate Onboarding & File Reading Order

Welcome to LoopBack! To get up to speed quickly without overwriting existing work:

1. **Read Documentations First:**
   - Read this document (`docs/DEVELOPER_HANDOFF.md`).
   - Read `backend/README.md`.
2. **Review Core Data Models:**
   - Read `backend/app/models/incident.py` & `backend/app/models/evidence.py`.
3. **Inspect Agent Orchestration:**
   - Read `backend/app/agent/state.py` $\rightarrow$ `nodes.py` $\rightarrow$ `graph.py`.
4. **Inspect API & Data Flow:**
   - Read `backend/app/api/routes.py` $\rightarrow$ `backend/app/core/database.py`.
5. **Inspect React Frontend Components:**
   - Read `frontend/src/services/api.js` $\rightarrow$ `Dashboard.jsx` $\rightarrow$ `AgentPanel.jsx`.
