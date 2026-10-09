from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.models.incident import Incident, ActionPayload
from app.models.evidence import TimelineEvent
from app.core import database
from app.agent.graph import run_agent_investigation_graph

router = APIRouter(prefix="/api")

@router.get("/health", tags=["Health"])
def get_health():
    db_status = database.get_db_status()
    return {
        "status": "online",
        "service": "LoopBack API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status
    }

@router.get("/incidents", response_model=List[Incident], tags=["Incidents"])
def list_incidents():
    records = database.get_all_incidents()
    return records

@router.get("/incidents/{incident_id}", response_model=Incident, tags=["Incidents"])
def get_incident(incident_id: str):
    record = database.get_incident_by_id(incident_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )
    return record

@router.post("/incidents/{incident_id}/investigate", response_model=Incident, tags=["Agent"])
def investigate_incident(incident_id: str):
    record = database.get_incident_by_id(incident_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )
    
    updated_record = run_agent_investigation_graph(record)
    database.save_incident(updated_record)
    return updated_record

@router.post("/incidents/{incident_id}/action", response_model=Incident, tags=["Human Control"])
def perform_action(incident_id: str, payload: ActionPayload):
    record = database.get_incident_by_id(incident_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    proposed_action = record.get("proposedAction")
    if not proposed_action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No proposed action exists for this incident."
        )

    if proposed_action.get("status") in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Action '{proposed_action.get('title')}' is already {proposed_action.get('status')}."
        )

    current_time = datetime.now(timezone.utc).isoformat()
    action_type = payload.action.lower()

    proposed_action["decidedAt"] = current_time
    proposed_action["decidedBy"] = "Human Operator"
    proposed_action["notes"] = payload.notes

    if action_type == "approve":
        proposed_action["status"] = "approved"
        record["agentActionRequired"] = False
        record["agentStatus"] = f"Action '{proposed_action['title']}' approved by operator. Proceeding with execution."

        new_event = {
            "id": f"T{len(record.get('timeline', [])) + 1}",
            "title": "Human Approval Received",
            "timestamp": current_time,
            "type": "success",
            "icon": "check-circle",
            "description": f"Operator approved: {proposed_action['title']}." + (f" Notes: {payload.notes}" if payload.notes else ""),
            "evidence": None
        }
        record.setdefault("timeline", []).append(new_event)

    elif action_type == "reject":
        proposed_action["status"] = "rejected"
        record["agentActionRequired"] = False
        record["agentStatus"] = f"Action '{proposed_action['title']}' overridden/rejected by operator."

        new_event = {
            "id": f"T{len(record.get('timeline', [])) + 1}",
            "title": "Action Overridden",
            "timestamp": current_time,
            "type": "failed",
            "icon": "x-circle",
            "description": f"Operator rejected action: {proposed_action['title']}." + (f" Notes: {payload.notes}" if payload.notes else ""),
            "evidence": None
        }
        record.setdefault("timeline", []).append(new_event)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be either 'approve' or 'reject'."
        )

    record["proposedAction"] = proposed_action
    database.save_incident(record)
    return record
