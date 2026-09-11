from tools.registry import BaseTool, ToolResult
from agent.state import Incident


class FinishInvestigationTool(BaseTool):
    name = "finish_investigation"
    description = "Conclude the investigation with a root cause analysis and confidence level"
    input_schema = {
        "type": "object",
        "properties": {
            "root_cause": {"type": "string", "description": "Identified root cause"},
            "confidence": {"type": "number", "description": "Confidence level (0.0 to 1.0)"},
            "evidence_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of evidence IDs supporting the conclusion",
            },
        },
        "required": ["root_cause", "confidence", "evidence_ids"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "accepted": {"type": "boolean"},
        },
    }

    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold

    async def execute(self, **kwargs) -> ToolResult:
        root_cause = kwargs["root_cause"]
        confidence = kwargs["confidence"]
        evidence_ids = kwargs["evidence_ids"]

        accepted = confidence >= self.confidence_threshold and len(evidence_ids) > 0

        return ToolResult(
            tool=self.name,
            status="success",
            query=kwargs,
            result={
                "status": "accepted" if accepted else "rejected",
                "accepted": accepted,
                "root_cause": root_cause,
                "confidence": confidence,
                "evidence_count": len(evidence_ids),
            },
            evidence_ids=evidence_ids,
        )
