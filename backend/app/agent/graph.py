import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from app.agent.state import IncidentState
from app.agent.nodes import (
    extract_facts_node,
    llm_reasoning_node,
    validate_output_node,
    action_proposal_node,
    fallback_node
)

logger = logging.getLogger("loopback.graph")

def check_llm_status(state: IncidentState) -> str:
    """Routing logic: proceed to validation if LLM succeeded, else route to fallback."""
    if state.get("used_llm"):
        return "validate_output"
    return "fallback"

def check_validation_status(state: IncidentState) -> str:
    """Routing logic: proceed to action proposal if validation passed, else route to fallback."""
    if state.get("used_llm"):
        return "action_proposal"
    return "fallback"

def build_investigation_graph():
    """Builds and compiles the LoopBack LangGraph investigation StateGraph."""
    builder = StateGraph(IncidentState)

    # Register nodes
    builder.add_node("extract_facts", extract_facts_node)
    builder.add_node("llm_reasoning", llm_reasoning_node)
    builder.add_node("validate_output", validate_output_node)
    builder.add_node("action_proposal", action_proposal_node)
    builder.add_node("fallback", fallback_node)

    # Connect workflow edges
    builder.add_edge(START, "extract_facts")
    builder.add_edge("extract_facts", "llm_reasoning")

    # Conditional branching for LLM invocation & validation
    builder.add_conditional_edges(
        "llm_reasoning",
        check_llm_status,
        {
            "validate_output": "validate_output",
            "fallback": "fallback"
        }
    )

    builder.add_conditional_edges(
        "validate_output",
        check_validation_status,
        {
            "action_proposal": "action_proposal",
            "fallback": "fallback"
        }
    )

    builder.add_edge("action_proposal", END)
    builder.add_edge("fallback", END)

    return builder.compile()

# Compile graph singleton
investigation_graph = build_investigation_graph()

def run_agent_investigation_graph(incident: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the LangGraph investigation workflow on an incident record.
    Returns the updated incident dictionary matching the frontend response schema.
    """
    initial_state: IncidentState = {
        "incident_id": incident.get("id", ""),
        "incident": incident,
        "verified_facts": [],
        "hypotheses": [],
        "missing_evidence": [],
        "recommendation": "",
        "proposed_action": None,
        "agent_action_required": False,
        "used_llm": False,
        "fallback_reason": None,
        "error": None
    }

    try:
        final_state = investigation_graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"LangGraph execution exception ({e}). Falling back to deterministic rules.")
        from app.agent.investigation import run_incident_investigation
        return run_incident_investigation(incident)

    # Construct investigation result
    investigation_result = {
        "verifiedFacts": final_state.get("verified_facts", []),
        "hypotheses": final_state.get("hypotheses", []),
        "missingEvidence": final_state.get("missing_evidence", []),
        "recommendation": final_state.get("recommendation", "")
    }

    used_llm = final_state.get("used_llm", False)
    facts_count = len(investigation_result["verifiedFacts"])
    gaps_count = len(investigation_result["missingEvidence"])
    engine_name = "Ollama (llama3.2)" if used_llm else "Deterministic Rules Engine"

    proposed_action = final_state.get("proposed_action")
    action_status_str = f" Action status: {proposed_action['status']}." if proposed_action else ""
    agent_status = f"Investigation complete [{engine_name}]. {facts_count} facts verified, {gaps_count} evidence gaps flagged.{action_status_str}"

    incident["investigation"] = investigation_result
    incident["agentStatus"] = agent_status
    incident["agentActionRequired"] = final_state.get("agent_action_required", False)
    if proposed_action:
        incident["proposedAction"] = proposed_action
    incident["used_llm"] = used_llm

    return incident
