from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from app.models.evidence import TimelineEvent

class ProposedAction(BaseModel):
    actionId: str
    title: str
    description: str
    targetParty: str
    status: Literal["pending", "approved", "rejected"] = "pending"
    decidedAt: Optional[str] = None
    decidedBy: Optional[str] = None
    notes: Optional[str] = None

class InvestigationResult(BaseModel):
    verifiedFacts: List[str] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    missingEvidence: List[str] = Field(default_factory=list)
    recommendation: str = ""

class UploadedEvidence(BaseModel):
    id: str
    filename: str
    contentType: str
    timestamp: str
    storagePath: str
    sizeBytes: int

class Incident(BaseModel):
    id: str
    date: str
    status: Literal["Investigating", "Resolved", "Failed"]
    wasteStream: str
    summary: str
    facility: str
    agentStatus: str
    agentActionRequired: bool = False
    proposedAction: Optional[ProposedAction] = None
    investigation: Optional[InvestigationResult] = None
    timeline: List[TimelineEvent] = Field(default_factory=list)
    uploadedEvidence: List[UploadedEvidence] = Field(default_factory=list)
    used_llm: Optional[bool] = False
    used_llm_provider: Optional[str] = None

class IncidentCreate(BaseModel):
    wasteStream: str
    summary: str
    facility: str

class ActionPayload(BaseModel):
    action: Literal["approve", "reject"]
    notes: Optional[str] = None
