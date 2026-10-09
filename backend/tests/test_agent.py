import sys
import os
import json
import pytest
import httpx
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agent.graph import run_agent_investigation_graph, investigation_graph
from app.agent.nodes import llm_reasoning_node, validate_output_node, fallback_node
from app.agent.state import IncidentState

TEST_INCIDENT = {
    "id": "INC-TEST-001",
    "date": "2023-10-25T10:30:00Z",
    "status": "Investigating",
    "wasteStream": "Dry Waste",
    "summary": "Contamination reported at MRF",
    "facility": "Green Earth MRF",
    "agentStatus": "Pending",
    "agentActionRequired": True,
    "proposedAction": None,
    "timeline": [
        {
            "id": "T1",
            "title": "Segregation Logged",
            "timestamp": "2023-10-25T08:00:00Z",
            "type": "log",
            "icon": "clipboard",
            "description": "Initial segregation logged.",
            "evidence": None
        },
        {
            "id": "T2",
            "title": "Load Rejected",
            "timestamp": "2023-10-25T10:30:00Z",
            "type": "flagged",
            "icon": "alert-triangle",
            "description": "Load flagged for contamination.",
            "evidence": None
        }
    ]
}

def test_mocked_ollama_successful_llm_json():
    mock_llm_payload = {
        "response": json.dumps({
            "hypotheses": [
                "Contamination introduced during collection",
                "Scalehouse intake sensor miscalibration"
            ],
            "missingEvidence": [
                "High resolution intake photograph"
            ],
            "recommendation": "Request high-res scalehouse photo from vendor"
        })
    }

    mock_response = httpx.Response(200, json=mock_llm_payload)

    with patch("app.agent.nodes.httpx.post", return_value=mock_response):
        result = run_agent_investigation_graph(dict(TEST_INCIDENT))
        assert result["used_llm"] is True
        assert len(result["investigation"]["hypotheses"]) == 2
        assert len(result["investigation"]["missingEvidence"]) == 1
        assert "Request high-res" in result["investigation"]["recommendation"]
        assert "Ollama" in result["agentStatus"]

def test_ollama_timeout_triggers_deterministic_fallback():
    with patch("app.agent.nodes.httpx.post", side_effect=Exception("Connection timeout")):
        result = run_agent_investigation_graph(dict(TEST_INCIDENT))
        assert result["used_llm"] is False
        assert len(result["investigation"]["verifiedFacts"]) > 0
        assert len(result["investigation"]["hypotheses"]) > 0
        assert "Deterministic Rules Engine" in result["agentStatus"]

def test_invalid_llm_json_triggers_fallback():
    mock_response = httpx.Response(200, json={"response": "This is plain text, not JSON"})

    with patch("app.agent.nodes.httpx.post", return_value=mock_response):
        result = run_agent_investigation_graph(dict(TEST_INCIDENT))
        assert result["used_llm"] is False
        assert len(result["investigation"]["verifiedFacts"]) > 0

def test_no_duplicate_facts_on_reinvestigation():
    incident = dict(TEST_INCIDENT)
    incident["timeline"].append({
        "id": "T3",
        "title": "Human Approval Received",
        "timestamp": "2023-10-25T11:00:00Z",
        "type": "success",
        "icon": "check-circle",
        "description": "Operator approved evidence request.",
        "evidence": None
    })

    with patch("app.agent.nodes.httpx.post", side_effect=Exception("Timeout")):
        res1 = run_agent_investigation_graph(dict(incident))
        res2 = run_agent_investigation_graph(dict(incident))
        assert len(res1["investigation"]["verifiedFacts"]) == len(res2["investigation"]["verifiedFacts"])

def test_preserves_existing_approved_action():
    incident = dict(TEST_INCIDENT)
    incident["proposedAction"] = {
        "actionId": "ACT-101",
        "title": "Request Scalehouse Evidence",
        "description": "Request photo from vendor",
        "targetParty": "Logistics",
        "status": "approved"
    }

    with patch("app.agent.nodes.httpx.post", side_effect=Exception("Timeout")):
        res = run_agent_investigation_graph(incident)
        assert res["proposedAction"]["status"] == "approved"
        assert res["agentActionRequired"] is False
