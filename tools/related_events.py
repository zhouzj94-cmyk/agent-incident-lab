from datetime import datetime
from tools.registry import BaseTool, ToolResult
from environment.log_store import LogStore


class GetRelatedEventsTool(BaseTool):
    name = "get_related_events"
    description = "Find events matching a pattern within a time window to trace related activity"
    input_schema = {
        "type": "object",
        "properties": {
            "event_pattern": {"type": "string", "description": "Pattern to search for in event templates"},
            "start_time": {"type": "string", "description": "Start time in ISO format"},
            "end_time": {"type": "string", "description": "End time in ISO format"},
        },
        "required": ["event_pattern", "start_time", "end_time"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "events": {"type": "array"},
            "count": {"type": "integer"},
        },
    }

    def __init__(self, log_store: LogStore):
        self.log_store = log_store

    async def execute(self, **kwargs) -> ToolResult:
        pattern = kwargs["event_pattern"]
        start_time = datetime.fromisoformat(kwargs["start_time"])
        end_time = datetime.fromisoformat(kwargs["end_time"])

        events = self.log_store.get_events_by_pattern(pattern, start_time, end_time)

        event_data = [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "node_id": e.node_id,
                "template": e.template,
                "severity": e.severity,
            }
            for e in events
        ]

        evidence_ids = [e.event_id for e in events[:5]]

        return ToolResult(
            tool=self.name,
            status="success",
            query=kwargs,
            result={"events": event_data, "count": len(event_data)},
            evidence_ids=evidence_ids,
        )
