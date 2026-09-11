from typing import TypedDict, Optional
from agent.state import Incident, Hypothesis, Evidence


class InvestigationState(TypedDict):
    incident_id: str
    user_goal: str

    current_time_window: dict

    observations: list
    hypotheses: list[Hypothesis]
    evidence: list[Evidence]

    available_tools: list[str]

    plan: list[str]
    completed_steps: list[dict]

    confidence: float

    retry_count: int
    replan_count: int

    verification_result: dict

    final_answer: dict
