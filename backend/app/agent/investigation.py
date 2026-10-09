from typing import Dict, Any

def run_incident_investigation(incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a structured investigation on an incident.
    Enforces LoopBack safety rules:
    - Distinguishes verified facts, hypotheses, and missing evidence.
    - Excludes administrative approval/rejection logs from raw facts to prevent duplicate inflation.
    - Preserves existing proposed actions without resetting completed decisions.
    """
    timeline = incident.get("timeline", [])
    waste_stream = incident.get("wasteStream", "Waste Stream")
    facility = incident.get("facility", "Destination Facility")

    # Filter verified facts from domain timeline events only (skip operator approval/rejection logs)
    verified_facts = []
    for event in timeline:
        title = event.get("title", "")
        if title in ["Human Approval Received", "Action Overridden"]:
            continue
        if title and event.get("timestamp"):
            desc = event.get("description", "")
            verified_facts.append(f"Recorded '{title}' at {event['timestamp']}: {desc}")

    if not verified_facts:
        verified_facts.append(f"Incident reported for {waste_stream} at {facility}.")

    has_flagged = any(e.get("type") == "flagged" for e in timeline)
    has_failed = any(e.get("type") == "failed" for e in timeline)

    hypotheses = []
    missing_evidence = []
    proposed_action = incident.get("proposedAction")
    agent_action_required = incident.get("agentActionRequired", False)

    if has_flagged:
        hypotheses = [
            f"Contamination may have occurred during transit between source and {facility}.",
            f"Facility scalehouse intake assessment at {facility} may have misclassified acceptable dry recyclables."
        ]
        missing_evidence = [
            "High-resolution scalehouse intake photograph from destination facility.",
            "Carrier intermediate stop log and vehicle telemetry."
        ]
        recommendation = "Request uncompressed photographic evidence from facility scalehouse before taking punitive measures."

        if not proposed_action:
            proposed_action = {
                "actionId": f"ACT-{incident['id']}-01",
                "title": f"Request Scalehouse Evidence from {facility}",
                "description": f"The load was flagged for contamination. Human approval is required to automatically send an official evidence request to {facility}.",
                "targetParty": f"{facility} Logistics",
                "status": "pending"
            }
            agent_action_required = True
        else:
            # Respect existing decision status
            agent_action_required = (proposed_action.get("status") == "pending")

    elif has_failed:
        hypotheses = [
            "Logistics carrier experienced unannounced vehicle breakdown or route obstruction.",
            "Dispatch scheduling failure at logistics vendor."
        ]
        missing_evidence = [
            "Vendor GPS route telemetry log.",
            "Official driver delay notice."
        ]
        recommendation = "Escalate missed SLA to carrier management and dispatch backup collection vehicle."

        if not proposed_action:
            proposed_action = {
                "actionId": f"ACT-{incident['id']}-02",
                "title": "Escalate Missed SLA & Dispatch Backup",
                "description": "Logistics partner failed to arrive within scheduled window. Approval required to issue SLA infraction ticket.",
                "targetParty": "Logistics Partner",
                "status": "pending"
            }
            agent_action_required = True
        else:
            agent_action_required = (proposed_action.get("status") == "pending")
    else:
        hypotheses = ["Standard chain of custody maintained without documented anomaly."]
        missing_evidence = []
        recommendation = "All chain of custody verification checks passed."
        agent_action_required = False

    action_status_str = f" Action status: {proposed_action['status']}." if proposed_action else ""
    agent_status = f"Investigation complete. {len(verified_facts)} facts verified, {len(missing_evidence)} evidence gaps flagged.{action_status_str}"

    investigation_result = {
        "verifiedFacts": verified_facts,
        "hypotheses": hypotheses,
        "missingEvidence": missing_evidence,
        "recommendation": recommendation
    }

    # Update incident dict
    incident["investigation"] = investigation_result
    incident["agentStatus"] = agent_status
    incident["agentActionRequired"] = agent_action_required
    if proposed_action:
        incident["proposedAction"] = proposed_action

    return incident
