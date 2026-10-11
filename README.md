# LoopBack ♻️

**An agentic system that investigates why recycling fails and helps prevent the same failure from happening again.**

*Built for WeMakeDevs Environmental Hacks (Waste and Energy Track).*

## The Problem
Recording that waste was segregated at the source does not guarantee it was successfully recovered at the facility. When a load is rejected for contamination, waste generators rarely know *where* the process failed or *who* needs to fix it. Throwing up more "Please Segregate" posters doesn't work if the waste is being mixed during transport.

## Our Solution
LoopBack is a local, open-source agentic workflow built with LangGraph and FastAPI. When a recycling failure is reported, the LoopBack agent automatically:
1. **Investigates** the evidence across different handoffs (campus logs, transport logs, facility receipts).
2. **Diagnoses** the failure with acknowledged uncertainty (distinguishing facts from missing evidence).
3. **Coordinates** corrective action by requesting human approval for the responsible party.
4. **Verifies** the outcome by checking subsequent collections for repeat failures.

## Features
- **Agentic Investigation Workflow:** An AI agent automatically parses timelines, hypothesizes causes, and identifies missing chain-of-custody evidence.
- **Evidence Uploads & Persistence:** Users can upload supporting evidence files (JPG, PNG, WEBP, and PDF; up to 5 MB). Files are persisted to disk and served via static routes, remaining available across investigations and page refreshes.
- **Human Approval Workflow:** The agent cannot take action unilaterally. Deterministic rules formulate proposed actions which require a human operator's explicit approval or rejection.
- **Dual-Mode Persistence:** Stores incident state and metadata using MongoDB Atlas (when configured) or seamlessly falls back to local JSON files (`seed_incidents.json`).

## Technical Architecture
- **Orchestration:** LangGraph (StateGraph architecture for deterministic agent routing and fallback).
- **Backend:** Python + FastAPI.
- **Frontend:** React + Vite + Tailwind CSS.
- **LLM / Reasoning Providers:** 
  - **Local Ollama (Llama 3.2):** Default local inference provider (`LLM_PROVIDER=ollama`).
  - **AWS Strands Agents SDK (`strands-agents`):** AWS open-source agentic SDK running locally via `OllamaModel` (`LLM_PROVIDER=strands`). Verified with `gemma:2b` via a prompt-based reasoning path without tool calling (since `gemma:2b` does not support Ollama's tool-calling API). Users must explicitly set `LLM_PROVIDER=strands` in their environment to select this provider.
  - **Amazon Bedrock:** Integration built via `boto3` for cloud inference. *(Note: While backend logic and unit tests are implemented, live Bedrock connectivity and cloud deployment have not been verified with real AWS credentials. The project runs locally under the AWS Open Source "Build It" route).*

## Setup & Local Development

### Prerequisites
- Node.js (v22+)
- Python 3.10+
- Ollama running locally (`http://localhost:11434`)
  - For default provider (`LLM_PROVIDER=ollama`): `llama3.2:latest`
  - For AWS Strands provider (`LLM_PROVIDER=strands`): `gemma:2b`

### Configuration
Copy the environment template and customize as needed:
```bash
cp backend/.env.example backend/.env
```
- **To use AWS Strands Agents SDK:** Set `LLM_PROVIDER=strands` and `STRANDS_MODEL_ID=gemma:2b` in `backend/.env`.
- **To use default Ollama:** Leave `LLM_PROVIDER=ollama` (default).
- **To configure Amazon Bedrock:** Refer to the [AWS Setup & Handoff Guide](docs/AWS_SETUP_AND_HANDOFF.md).

### 1. Start the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Start the Frontend
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```

## Attribution & Hackathon Integrity
To ensure full transparency for hackathon judging, please note the repository history:
- **Pre-Existing Scaffold:** Initial Vite/React UI scaffold, architecture diagram, and empty zero-byte backend skeleton files (`main.py`, `routes.py`, `graph.py`, etc.) were committed prior to the active hackathon session (Commits `60e3cd3` through `b2c32c8`).
- **Hackathon Implementation:** The core application logic—including the FastAPI endpoints, LangGraph orchestrator, Bedrock/Ollama integration, evidence upload feature, robust JSON parser, and the React API bindings—was actively developed and completed during the hackathon session.