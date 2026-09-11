from datetime import datetime
from tools.registry import BaseTool, ToolResult
from agent.state import Hypothesis, Evidence


class VerifyHypothesisTool(BaseTool):
    name = "verify_hypothesis"
    description = "Verify if a hypothesis is supported by the collected evidence"
    input_schema = {
        "type": "object",
        "properties": {
            "hypothesis": {"type": "string", "description": "The hypothesis to verify"},
            "evidence_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of evidence IDs supporting this hypothesis",
            },
        },
        "required": ["hypothesis", "evidence_ids"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "verified": {"type": "boolean"},
            "confidence": {"type": "number"},
            "reasoning": {"type": "string"},
        },
    }

    def __init__(self, evidence_store: list[Evidence]):
        self.evidence_store = evidence_store

    async def execute(self, **kwargs) -> ToolResult:
        hypothesis = kwargs["hypothesis"]
        evidence_ids = kwargs["evidence_ids"]

        supporting_evidence = [
            e for e in self.evidence_store if e.evidence_id in evidence_ids
        ]

        if not supporting_evidence:
            return ToolResult(
                tool=self.name,
                status="success",
                query=kwargs,
                result={
                    "verified": False,
                    "confidence": 0.0,
                    "reasoning": "No supporting evidence found",
                },
                evidence_ids=[],
            )

        confidence = min(len(supporting_evidence) / 3.0, 1.0)

        return ToolResult(
            tool=self.name,
            status="success",
            query=kwargs,
            result={
                "verified": confidence > 0.5,
                "confidence": confidence,
                "reasoning": f"Found {len(supporting_evidence)} supporting evidence items",
            },
            evidence_ids=evidence_ids,
        )
