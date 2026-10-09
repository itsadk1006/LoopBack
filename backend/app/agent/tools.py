from typing import List, Dict, Any

FACILITY_STANDARDS = {
    "Green Earth MRF": {
        "max_contamination_percent": 10.0,
        "required_documentation": ["intake_scalehouse_photo", "weight_receipt"],
        "accepted_streams": ["Dry Waste", "E-Waste"]
    },
    "TechRecycle Inc.": {
        "max_contamination_percent": 2.0,
        "required_documentation": ["serial_manifest", "recycling_certificate"],
        "accepted_streams": ["E-Waste"]
    },
    "Compost Hub": {
        "max_contamination_percent": 5.0,
        "required_documentation": ["pickup_time_log", "temperature_log"],
        "accepted_streams": ["Organic Waste"]
    }
}

WASTE_STREAM_SPECS = {
    "Dry Waste": "Paper, cardboard, dry plastics, clean metals. Must be free of wet organic food waste.",
    "E-Waste": "Computers, circuit boards, batteries, monitors. Requires strict chain of custody and serial manifests.",
    "Organic Waste": "Food waste, compostable organics. Pickups must occur within 4 hours to prevent decay."
}

def get_facility_standards(facility_name: str) -> Dict[str, Any]:
    """Returns official operational standards and intake criteria for a facility."""
    return FACILITY_STANDARDS.get(facility_name, {
        "max_contamination_percent": 5.0,
        "required_documentation": ["intake_photo", "receipt"],
        "accepted_streams": ["General Waste"]
    })

def get_waste_stream_info(waste_stream: str) -> str:
    """Returns official segregation rules for a waste stream."""
    return WASTE_STREAM_SPECS.get(waste_stream, "Standard waste segregation criteria apply.")

def format_timeline_for_prompt(timeline: List[Dict[str, Any]]) -> str:
    """Formats timeline events into clear, clean plain text for the LLM context."""
    formatted_lines = []
    for idx, event in enumerate(timeline, start=1):
        title = event.get("title", "Event")
        if title in ["Human Approval Received", "Action Overridden"]:
            continue
        ts = event.get("timestamp", "Unknown time")
        desc = event.get("description", "")
        evidence_str = ""
        if event.get("evidence"):
            evidence_type = event["evidence"].get("type", "attachment")
            evidence_str = f" [Evidence: {evidence_type}]"
        formatted_lines.append(f"{idx}. [{ts}] {title}: {desc}{evidence_str}")
    return "\n".join(formatted_lines)
