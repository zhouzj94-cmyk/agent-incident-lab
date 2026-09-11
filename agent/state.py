from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class LogEntry(BaseModel):
    timestamp: datetime
    node_id: str
    label: str
    message: str
    raw: str


class Event(BaseModel):
    event_id: str
    timestamp: datetime
    node_id: str
    template: str
    parameters: dict = Field(default_factory=dict)
    severity: str = "INFO"


class Incident(BaseModel):
    incident_id: str
    dataset: str
    start_time: datetime
    end_time: datetime
    label: str
    root_cause: str
    evidence: list[str] = Field(default_factory=list)
    difficulty: Difficulty = Difficulty.MEDIUM
    metadata: dict = Field(default_factory=dict)


class Evidence(BaseModel):
    evidence_id: str
    source: str
    timestamp: Optional[datetime] = None
    content: str
    relevance: float = 0.0


class Hypothesis(BaseModel):
    hypothesis_id: str
    statement: str
    confidence: float = 0.5
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    status: str = "active"
