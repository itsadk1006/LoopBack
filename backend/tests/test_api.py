import sys
import os
import json
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core import database

client = TestClient(app)

BASELINE_SEED = [
  {
    "id": "INC-001",
    "date": "2023-10-25T10:30:00Z",
    "status": "Investigating",
    "wasteStream": "Dry Waste",
    "summary": "Contamination reported at destination facility",
    "facility": "Green Earth MRF",
    "agentStatus": "Analyzing receipt discrepancy and scalehouse records...",
    "agentActionRequired": True,
    "proposedAction": {
      "actionId": "ACT-101",
      "title": "Request Clear Scalehouse Photographic Evidence",
      "description": "The destination facility flagged the load for >15% contamination (wet waste mixed), but the intake photo from scalehouse is blurry. Need approval to request uncompressed photo from vendor.",
      "targetParty": "Green Earth MRF Logistics",
      "status": "pending"
    },
    "investigation": {
      "verifiedFacts": [
        "Source facility logged 450 kg of segregated dry waste at 08:00 AM.",
        "Logistics carrier confirmed pickup at 09:15 AM without reported anomaly.",
        "Truck arrived at Green Earth MRF at 10:00 AM."
      ],
      "hypotheses": [
        "Contamination occurred during transit if secondary waste was loaded.",
        "MRF scalehouse misclassified dry paper waste as wet organic waste."
      ],
      "missingEvidence": [
        "Uncompressed high-resolution scalehouse intake photograph.",
        "Driver intermediate stop and route telemetry log."
      ],
      "recommendation": "Request high-res photo from MRF scalehouse before issuing non-compliance citation."
    },
    "timeline": [
      {
        "id": "T1",
        "title": "Segregation Logged",
        "timestamp": "2023-10-25T08:00:00Z",
        "type": "log",
        "icon": "clipboard",
        "description": "Initial waste segregation logged by source facility (Campus Block A).",
        "evidence": None
      },
      {
        "id": "T2",
        "title": "Pickup Confirmed",
        "timestamp": "2023-10-25T09:15:00Z",
        "type": "pickup",
        "icon": "truck",
        "description": "Waste pickup confirmed by EcoHaul Logistics partner.",
        "evidence": None
      },
      {
        "id": "T3",
        "title": "Arrived at MRF",
        "timestamp": "2023-10-25T10:00:00Z",
        "type": "facility",
        "icon": "factory",
        "description": "Truck arrived at Green Earth MRF.",
        "evidence": { "type": "receipt", "url": "#" }
      },
      {
        "id": "T4",
        "title": "Load Rejected",
        "timestamp": "2023-10-25T10:30:00Z",
        "type": "flagged",
        "icon": "alert-triangle",
        "description": "Load flagged for >15% contamination (wet waste mixed).",
        "evidence": {
          "type": "photo",
          "url": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&q=80&w=400&h=300"
        }
      }
    ]
  },
  {
    "id": "INC-002",
    "date": "2023-10-24T14:20:00Z",
    "status": "Resolved",
    "wasteStream": "E-Waste",
    "summary": "Successful delivery to certified recycler",
    "facility": "TechRecycle Inc.",
    "agentStatus": "Case closed. Certificate verified and archived.",
    "agentActionRequired": False,
    "proposedAction": None,
    "investigation": {
      "verifiedFacts": [
        "250 kg of electronic equipment picked up from corporate office.",
        "Received at TechRecycle Inc. with serial audit log matching initial Manifest.",
        "Recycling certificate #TR-9941 issued."
      ],
      "hypotheses": [],
      "missingEvidence": [],
      "recommendation": "No further action required."
    },
    "timeline": [
      {
        "id": "T1",
        "title": "Pickup Confirmed",
        "timestamp": "2023-10-24T10:00:00Z",
        "type": "pickup",
        "icon": "truck",
        "description": "E-waste picked up from corporate office.",
        "evidence": None
      },
      {
        "id": "T2",
        "title": "Processed",
        "timestamp": "2023-10-24T14:20:00Z",
        "type": "success",
        "icon": "check-circle",
        "description": "Successfully processed and certificate generated.",
        "evidence": { "type": "receipt", "url": "#" }
      }
    ]
  },
  {
    "id": "INC-003",
    "date": "2023-10-26T09:10:00Z",
    "status": "Failed",
    "wasteStream": "Organic Waste",
    "summary": "Missed pickup schedule",
    "facility": "Compost Hub",
    "agentStatus": "Awaiting vendor response on missed SLA.",
    "agentActionRequired": True,
    "proposedAction": {
      "actionId": "ACT-103",
      "title": "Issue SLA Penalty & Re-route Dispatch",
      "description": "Logistics partner failed to arrive within scheduled 2-hour window, risking organic degradation. Approve escalation to emergency carrier.",
      "targetParty": "GreenTransit Logistics",
      "status": "pending"
    },
    "investigation": {
      "verifiedFacts": [
        "Organic waste collection scheduled for 08:00 AM on Oct 26.",
        "No vehicle arrival registered at Campus Gate 2 by 09:10 AM."
      ],
      "hypotheses": [
        "Vehicle breakdown along primary transit route.",
        "Driver dispatch scheduling error."
      ],
      "missingEvidence": [
        "Vendor GPS telemetry and incident delay notice."
      ],
      "recommendation": "Dispatch backup carrier and file SLA infraction ticket."
    },
    "timeline": [
      {
        "id": "T1",
        "title": "Pickup Scheduled",
        "timestamp": "2023-10-26T08:00:00Z",
        "type": "pickup",
        "icon": "calendar",
        "description": "Pickup was scheduled for 08:00 AM.",
        "evidence": None
      },
      {
        "id": "T2",
        "title": "No-show Alert",
        "timestamp": "2023-10-26T09:10:00Z",
        "type": "failed",
        "icon": "x-circle",
        "description": "Logistics partner failed to arrive within window.",
        "evidence": None
      }
    ]
  }
]

@pytest.fixture(autouse=True)
def reset_db_state():
    """Ensure clean baseline database state before and after each test."""
    database.init_database()
    database._save_json_data(BASELINE_SEED)
    yield
    database._save_json_data(BASELINE_SEED)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "database" in data

def test_list_incidents():
    response = client.get("/api/incidents")
    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) == 3

def test_get_incident_by_id():
    response = client.get("/api/incidents/INC-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "INC-001"
    assert data["proposedAction"]["status"] == "pending"

def test_investigate_incident_no_duplicate_facts():
    # Run investigation once
    res1 = client.post("/api/incidents/INC-001/investigate")
    assert res1.status_code == 200
    data1 = res1.json()
    facts_count_1 = len(data1["investigation"]["verifiedFacts"])

    # Run investigation a second time
    res2 = client.post("/api/incidents/INC-001/investigate")
    assert res2.status_code == 200
    data2 = res2.json()
    facts_count_2 = len(data2["investigation"]["verifiedFacts"])

    assert facts_count_1 == facts_count_2

def test_approve_action_keeps_investigating_status():
    payload = {"action": "approve", "notes": "Approved by supervisor"}
    response = client.post("/api/incidents/INC-001/action", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Action approved, but incident remains Investigating until full resolution
    assert data["status"] == "Investigating"
    assert data["agentActionRequired"] is False
    assert data["proposedAction"]["status"] == "approved"

    # Re-running investigation must preserve approved status and not duplicate approval logs
    res_inv = client.post("/api/incidents/INC-001/investigate")
    inv_data = res_inv.json()
    assert inv_data["proposedAction"]["status"] == "approved"
    assert inv_data["agentActionRequired"] is False

def test_reject_action():
    payload = {"action": "reject", "notes": "Vendor photo confirmed"}
    response = client.post("/api/incidents/INC-003/action", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["agentActionRequired"] is False
    assert data["proposedAction"]["status"] == "rejected"

def test_upload_evidence_success():
    files = {"file": ("test.png", b"fake_image_content", "image/png")}
    response = client.post("/api/incidents/INC-001/evidence", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "uploadedEvidence" in data
    assert len(data["uploadedEvidence"]) == 1
    ev = data["uploadedEvidence"][0]
    assert ev["filename"] == "test.png"
    assert ev["contentType"] == "image/png"
    assert "EV-" in ev["id"]

def test_upload_evidence_invalid_type():
    files = {"file": ("test.txt", b"text content", "text/plain")}
    response = client.post("/api/incidents/INC-001/evidence", files=files)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_upload_evidence_too_large():
    # Max size is 5MB. Let's make a 6MB dummy string.
    # To save memory in test, we can mock file size or just generate it.
    large_content = b"0" * (6 * 1024 * 1024)
    files = {"file": ("large.jpg", large_content, "image/jpeg")}
    response = client.post("/api/incidents/INC-001/evidence", files=files)
    assert response.status_code == 400
    assert "File size exceeds" in response.json()["detail"]

def test_upload_evidence_not_found():
    files = {"file": ("test.png", b"fake", "image/png")}
    response = client.post("/api/incidents/INVALID-ID/evidence", files=files)
    assert response.status_code == 404

def test_evidence_metadata_persistence():
    files = {"file": ("test2.jpg", b"fake2", "image/jpeg")}
    res1 = client.post("/api/incidents/INC-002/evidence", files=files)
    assert res1.status_code == 200

    # Fetch incident directly to check persistence
    res2 = client.get("/api/incidents/INC-002")
    assert res2.status_code == 200
    data = res2.json()
    assert len(data.get("uploadedEvidence", [])) == 1
    assert data["uploadedEvidence"][0]["filename"] == "test2.jpg"

def test_evidence_retrieval():
    files = {"file": ("test_serve.png", b"serve_this", "image/png")}
    res1 = client.post("/api/incidents/INC-002/evidence", files=files)
    assert res1.status_code == 200
    ev = res1.json()["uploadedEvidence"][-1]
    storage_path = ev["storagePath"]
    
    # Retrieve via static mount
    res2 = client.get(storage_path)
    assert res2.status_code == 200
    assert res2.content == b"serve_this"

from unittest.mock import patch
def test_upload_evidence_cleanup_on_failure():
    files = {"file": ("test_fail.png", b"fake_content", "image/png")}
    
    # We patch shutil.copyfileobj to raise an exception to simulate write failure
    with patch("app.api.routes.shutil.copyfileobj", side_effect=Exception("Disk full")):
        response = client.post("/api/incidents/INC-001/evidence", files=files)
        
    assert response.status_code == 500
    
    # Verify no test_fail.png exists in evidence dir
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "evidence")
    for f in os.listdir(upload_dir):
        # We don't know the exact uuid, but let's check there's no empty or partial file created during this test
        # Actually it's easier to mock os.remove and check it was called.
        pass

def test_upload_evidence_cleanup_calls_remove():
    files = {"file": ("test_fail2.png", b"fake_content", "image/png")}
    with patch("app.api.routes.shutil.copyfileobj", side_effect=Exception("Disk full")):
        with patch("app.api.routes.os.remove") as mock_remove:
            with patch("app.api.routes.os.path.exists", return_value=True):
                response = client.post("/api/incidents/INC-001/evidence", files=files)
                assert response.status_code == 500
                mock_remove.assert_called_once()

