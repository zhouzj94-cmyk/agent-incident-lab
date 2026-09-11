from datetime import datetime
from tools.registry import BaseTool, ToolResult
from environment.log_store import LogStore


class GetErrorStatsTool(BaseTool):
    name = "get_error_stats"
    description = "Get error statistics for a time window including total events, error count, and top error patterns"
    input_schema = {
        "type": "object",
        "properties": {
            "start_time": {"type": "string", "description": "Start time in ISO format"},
            "end_time": {"type": "string", "description": "End time in ISO format"},
        },
        "required": ["start_time", "end_time"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "total_events": {"type": "integer"},
            "error_events": {"type": "integer"},
            "top_patterns": {"type": "array"},
        },
    }

    def __init__(self, log_store: LogStore):
        self.log_store = log_store

    async def execute(self, **kwargs) -> ToolResult:
        start_time = datetime.fromisoformat(kwargs["start_time"])
        end_time = datetime.fromisoformat(kwargs["end_time"])

        stats = self.log_store.get_error_stats(start_time, end_time)

        return ToolResult(
            tool=self.name,
            status="success",
            query=kwargs,
            result=stats,
            evidence_ids=[],
        )
