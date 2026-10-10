from typing import List, Dict, Any, Optional, TypedDict

class IncidentState(TypedDict, total=False):
    incident_id: str
    incident: Dict[str, Any]
    verified_facts: List[str]
    hypotheses: List[str]
    missing_evidence: List[str]
    recommendation: str
    proposed_action: Optional[Dict[str, Any]]
    agent_action_required: bool
    used_llm: bool
    used_llm_provider: Optional[str]
    fallback_reason: Optional[str]
    error: Optional[str]
    _raw_llm_output: Optional[str]
