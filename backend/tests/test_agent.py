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

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
        with patch("app.agent.nodes.httpx.post", return_value=mock_response):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is True
            assert len(result["investigation"]["hypotheses"]) == 2
            assert len(result["investigation"]["missingEvidence"]) == 1
            assert "Request high-res" in result["investigation"]["recommendation"]
            assert "Ollama" in result["agentStatus"]

def test_mocked_bedrock_successful_llm_json():
    mock_llm_payload = {
        "generation": json.dumps({
            "hypotheses": ["AWS Bedrock cause"],
            "missingEvidence": ["AWS missing evidence"],
            "recommendation": "AWS Bedrock recommendation"
        })
    }

    mock_response_body = MagicMock()
    mock_response_body.read.return_value = json.dumps(mock_llm_payload).encode("utf-8")
    
    mock_invoke_response = {
        "body": mock_response_body
    }

    mock_boto_client = MagicMock()
    mock_boto_client.invoke_model.return_value = mock_invoke_response

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "bedrock"):
        with patch("app.agent.nodes.boto3.client", return_value=mock_boto_client):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is True
            assert result["used_llm_provider"] == "bedrock"
            assert len(result["investigation"]["hypotheses"]) == 1
            assert "Amazon Bedrock" in result["agentStatus"]

def test_ollama_timeout_triggers_deterministic_fallback():
    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
        with patch("app.agent.nodes.httpx.post", side_effect=Exception("Connection timeout")):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is False
            assert len(result["investigation"]["verifiedFacts"]) > 0
            assert len(result["investigation"]["hypotheses"]) > 0
            assert "Deterministic Rules Engine" in result["agentStatus"]

def test_invalid_llm_json_triggers_fallback():
    mock_response = httpx.Response(200, json={"response": "This is plain text, not JSON"})

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
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

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
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

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
        with patch("app.agent.nodes.httpx.post", side_effect=Exception("Timeout")):
            res = run_agent_investigation_graph(incident)
            assert res["proposedAction"]["status"] == "approved"
            assert res["agentActionRequired"] is False

def test_mocked_ollama_fenced_json():
    json_payload = json.dumps({
        "hypotheses": ["Fenced hypothesis"],
        "missingEvidence": ["Fenced missing"],
        "recommendation": "Fenced recommendation"
    })
    mock_llm_payload = {
        "response": f"Here is the investigation:\n```json\n{json_payload}\n```\nHope this helps."
    }

    mock_response = httpx.Response(200, json=mock_llm_payload)

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
        with patch("app.agent.nodes.httpx.post", return_value=mock_response):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is True
            assert result["investigation"]["hypotheses"] == ["Fenced hypothesis"]

def test_mocked_ollama_explanatory_json():
    json_payload = json.dumps({
        "hypotheses": ["Explanatory hypothesis"],
        "missingEvidence": ["Explanatory missing"],
        "recommendation": "Explanatory recommendation"
    })
    mock_llm_payload = {
        "response": f"Sure, I can help with that.\n\n{json_payload}\n\nLet me know if you need anything else!"
    }

    mock_response = httpx.Response(200, json=mock_llm_payload)

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
        with patch("app.agent.nodes.httpx.post", return_value=mock_response):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is True
            assert result["investigation"]["hypotheses"] == ["Explanatory hypothesis"]

def test_mocked_ollama_schema_invalid_json_triggers_fallback():
    # Valid JSON but missing required fields
    json_payload = json.dumps({
        "incorrectKey": ["Hypothesis"]
    })
    mock_llm_payload = {
        "response": json_payload
    }

    mock_response = httpx.Response(200, json=mock_llm_payload)

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "ollama"):
        with patch("app.agent.nodes.httpx.post", return_value=mock_response):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is False
            assert "Deterministic Rules Engine" in result["agentStatus"]

def test_mocked_strands_successful_llm_json():
    mock_json = json.dumps({
        "hypotheses": ["Contamination from collection truck"],
        "missingEvidence": ["Scalehouse weight receipt"],
        "recommendation": "Request scalehouse documentation"
    })

    mock_agent_instance = MagicMock()
    mock_agent_instance.return_value = mock_json

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "strands"):
        with patch("strands.Agent", return_value=mock_agent_instance):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is True
            assert result["used_llm_provider"] == "strands"
            assert result["investigation"]["hypotheses"] == ["Contamination from collection truck"]
            assert result["investigation"]["missingEvidence"] == ["Scalehouse weight receipt"]
            assert "AWS Strands Agent" in result["agentStatus"]

def test_strands_error_triggers_fallback():
    mock_agent_instance = MagicMock()
    mock_agent_instance.side_effect = Exception("Ollama connection refused")

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "strands"):
        with patch("strands.Agent", return_value=mock_agent_instance):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is False
            assert len(result["investigation"]["verifiedFacts"]) > 0
            assert "Deterministic Rules Engine" in result["agentStatus"]

def test_strands_invalid_json_triggers_fallback():
    mock_agent_instance = MagicMock()
    mock_agent_instance.return_value = "Sorry, I cannot investigate this."

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "strands"):
        with patch("strands.Agent", return_value=mock_agent_instance):
            result = run_agent_investigation_graph(dict(TEST_INCIDENT))
            assert result["used_llm"] is False
            assert "Deterministic Rules Engine" in result["agentStatus"]

def test_strands_no_tools_path_for_gemma():
    mock_json = json.dumps({
        "hypotheses": ["Gemma reasoning hypothesis"],
        "missingEvidence": ["Scalehouse log"],
        "recommendation": "Review logs"
    })

    agent_calls = []
    def mock_agent_factory(*args, **kwargs):
        agent_calls.append(kwargs)
        mock_instance = MagicMock()
        mock_instance.return_value = mock_json
        return mock_instance

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "strands"):
        with patch("app.agent.nodes.settings.STRANDS_MODEL_ID", "gemma:2b"):
            with patch("strands.Agent", side_effect=mock_agent_factory):
                result = run_agent_investigation_graph(dict(TEST_INCIDENT))
                assert result["used_llm"] is True
                assert result["used_llm_provider"] == "strands"
                assert result["investigation"]["hypotheses"] == ["Gemma reasoning hypothesis"]
                assert "tools" not in agent_calls[0]

def test_strands_tool_unsupported_error_recovers_via_no_tools():
    mock_json = json.dumps({
        "hypotheses": ["Recovered hypothesis"],
        "missingEvidence": ["Camera footage"],
        "recommendation": "Inspect camera"
    })

    call_count = 0
    def mock_agent_factory(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_instance = MagicMock()
        if "tools" in kwargs and kwargs["tools"]:
            mock_instance.side_effect = Exception("registry.ollama.ai/library/custom:7b does not support tools (status code: 400)")
        else:
            mock_instance.return_value = mock_json
        return mock_instance

    with patch("app.agent.nodes.settings.LLM_PROVIDER", "strands"):
        with patch("app.agent.nodes.settings.STRANDS_MODEL_ID", "custom:7b"):
            with patch("strands.Agent", side_effect=mock_agent_factory):
                result = run_agent_investigation_graph(dict(TEST_INCIDENT))
                assert result["used_llm"] is True
                assert result["used_llm_provider"] == "strands"
                assert result["investigation"]["hypotheses"] == ["Recovered hypothesis"]
                assert call_count == 2


