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

## Technical Architecture
We opted for a 100% open-source, zero-cost stack, running inference locally to ensure privacy and eliminate token costs.

- **Orchestration:** LangGraph (StateGraph architecture for deterministic agent routing)
- **Backend:** Python + FastAPI 
- **LLM / Reasoning:** Local Llama 3 (via Ollama)
- **Frontend:** React + Vite + Tailwind CSS
- **Database:** MongoDB (for persisting incident states and audit logs)

## Setup & Local Development

### Prerequisites
- Node.js & npm
- Python 3.10+
- Ollama installed locally with Llama 3 (`ollama run llama3`)
- MongoDB running locally

### 1. Start the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload