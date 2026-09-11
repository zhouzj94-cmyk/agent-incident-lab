from datetime import datetime
from tools.registry import BaseTool, ToolResult
from environment.log_store import LogStore


class SearchLogsTool(BaseTool):
    name = "search_logs"
    description = "Search logs within a time window, optionally filtered by severity level"
    input_schema = {
        "type": "object",
        "properties": {
            "start_time": {"type": "string", "description": "Start time in ISO format"},
            "end_time": {"type": "string", "description": "End time in ISO format"},
            "severity": {"type": "string", "description": "Filter by severity (INFO, WARNING, ERROR)"},
            "node_id": {"type": "string", "description": "Filter by node ID"},
            "limit": {"type": "integer", "description": "Maximum results to return", "default": 50},
        },
        "required": ["start_time", "end_time"],
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
        start_time = datetime.fromisoformat(kwargs["start_time"])
        end_time = datetime.fromisoformat(kwargs["end_time"])
        severity = kwargs.get("severity")
        node_id = kwargs.get("node_id")
        limit = kwargs.get("limit", 50)

        events = self.log_store.query(
            start_time=start_time,
            end_time=end_time,
            severity=severity,
            node_id=node_id,
            limit=limit,
        )

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
