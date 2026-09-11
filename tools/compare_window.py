from datetime import datetime
from tools.registry import BaseTool, ToolResult
from environment.log_store import LogStore


class CompareWindowTool(BaseTool):
    name = "compare_window"
    description = "Compare event patterns between a baseline (normal) window and an incident window to identify anomalies"
    input_schema = {
        "type": "object",
        "properties": {
            "baseline_start": {"type": "string", "description": "Baseline window start time"},
            "baseline_end": {"type": "string", "description": "Baseline window end time"},
            "incident_start": {"type": "string", "description": "Incident window start time"},
            "incident_end": {"type": "string", "description": "Incident window end time"},
        },
        "required": ["baseline_start", "baseline_end", "incident_start", "incident_end"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "baseline_stats": {"type": "object"},
            "incident_stats": {"type": "object"},
            "changes": {"type": "array"},
        },
    }

    def __init__(self, log_store: LogStore):
        self.log_store = log_store

    async def execute(self, **kwargs) -> ToolResult:
        baseline_start = datetime.fromisoformat(kwargs["baseline_start"])
        baseline_end = datetime.fromisoformat(kwargs["baseline_end"])
        incident_start = datetime.fromisoformat(kwargs["incident_start"])
        incident_end = datetime.fromisoformat(kwargs["incident_end"])

        baseline_stats = self.log_store.get_error_stats(baseline_start, baseline_end)
        incident_stats = self.log_store.get_error_stats(incident_start, incident_end)

        baseline_patterns = {p["template"]: p["count"] for p in baseline_stats["top_patterns"]}
        incident_patterns = {p["template"]: p["count"] for p in incident_stats["top_patterns"]}

        changes = []
        all_patterns = set(baseline_patterns.keys()) | set(incident_patterns.keys())

        for pattern in all_patterns:
            baseline_count = baseline_patterns.get(pattern, 0)
            incident_count = incident_patterns.get(pattern, 0)
            change = incident_count - baseline_count

            if abs(change) > 0:
                changes.append({
                    "template": pattern,
                    "baseline_count": baseline_count,
                    "incident_count": incident_count,
                    "change": change,
                })

        changes.sort(key=lambda x: abs(x["change"]), reverse=True)

        return ToolResult(
            tool=self.name,
            status="success",
            query=kwargs,
            result={
                "baseline_stats": baseline_stats,
                "incident_stats": incident_stats,
                "changes": changes[:10],
            },
            evidence_ids=[],
        )
