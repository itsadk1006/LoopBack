from typing import Optional, Literal
from pydantic import BaseModel, Field

class EvidenceAttachment(BaseModel):
    type: Literal["photo", "receipt", "document"]
    url: str

class TimelineEvent(BaseModel):
    id: str
    title: str
    timestamp: str
    type: Literal["log", "pickup", "facility", "flagged", "success", "failed"]
    icon: str
    description: str
    evidence: Optional[EvidenceAttachment] = None
