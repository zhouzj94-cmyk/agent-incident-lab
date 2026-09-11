from datetime import datetime
from tools.registry import BaseTool, ToolResult
from environment.log_store import LogStore


class GetServiceSummaryTool(BaseTool):
    name = "get_service_summary"
    description = "Get summary statistics for nodes/services within a time window"
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
            "nodes": {"type": "array"},
        },
    }

    def __init__(self, log_store: LogStore):
        self.log_store = log_store

    async def execute(self, **kwargs) -> ToolResult:
        start_time = datetime.fromisoformat(kwargs["start_time"])
        end_time = datetime.fromisoformat(kwargs["end_time"])

        summary = self.log_store.get_node_summary(start_time, end_time)

        return ToolResult(
            tool=self.name,
            status="success",
            query=kwargs,
            result={"nodes": summary},
            evidence_ids=[],
        )
