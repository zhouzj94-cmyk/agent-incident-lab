import pandas as pd
from datetime import datetime
from typing import Optional
from agent.state import Event, LogEntry


class LogStore:
    def __init__(self):
        self._events: list[Event] = []
        self._df: pd.DataFrame | None = None

    def load_from_entries(self, entries: list[LogEntry]) -> None:
        records = []
        for idx, entry in enumerate(entries):
            event = Event(
                event_id=f"ev-{idx:05d}",
                timestamp=entry.timestamp,
                node_id=entry.node_id,
                template=entry.message[:100],
                parameters={},
                severity=self._infer_severity(entry.label, entry.message),
            )
            self._events.append(event)
            records.append({
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "node_id": event.node_id,
                "template": event.template,
                "severity": event.severity,
                "label": entry.label,
                "message": entry.message,
            })

        self._df = pd.DataFrame(records)
        self._df = self._df.sort_values("timestamp").reset_index(drop=True)

    def _infer_severity(self, label: str, message: str) -> str:
        if label != "-":
            return "ERROR"
        msg_lower = message.lower()
        if "error" in msg_lower or "fail" in msg_lower:
            return "ERROR"
        if "warn" in msg_lower:
            return "WARNING"
        return "INFO"

    def query(
        self,
        start_time: datetime,
        end_time: datetime,
        severity: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[Event]:
        if self._df is None:
            return []

        mask = (self._df["timestamp"] >= start_time) & (self._df["timestamp"] <= end_time)

        if severity:
            mask &= self._df["severity"] == severity
        if node_id:
            mask &= self._df["node_id"] == node_id

        filtered = self._df[mask].head(limit)

        return [
            Event(
                event_id=row["event_id"],
                timestamp=row["timestamp"],
                node_id=row["node_id"],
                template=row["template"],
                severity=row["severity"],
            )
            for _, row in filtered.iterrows()
        ]

    def get_error_stats(
        self, start_time: datetime, end_time: datetime
    ) -> dict:
        if self._df is None:
            return {"total_events": 0, "error_events": 0, "top_patterns": []}

        mask = (self._df["timestamp"] >= start_time) & (self._df["timestamp"] <= end_time)
        window_df = self._df[mask]

        total = len(window_df)
        errors = len(window_df[window_df["severity"] == "ERROR"])

        top_patterns = (
            window_df[window_df["severity"] == "ERROR"]
            .groupby("template")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(10)
            .to_dict("records")
        )

        return {
            "total_events": total,
            "error_events": errors,
            "top_patterns": top_patterns,
        }

    def get_events_by_pattern(
        self,
        pattern: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[Event]:
        if self._df is None:
            return []

        mask = (
            (self._df["timestamp"] >= start_time)
            & (self._df["timestamp"] <= end_time)
            & (self._df["template"].str.contains(pattern, case=False, na=False))
        )

        filtered = self._df[mask]
        return [
            Event(
                event_id=row["event_id"],
                timestamp=row["timestamp"],
                node_id=row["node_id"],
                template=row["template"],
                severity=row["severity"],
            )
            for _, row in filtered.iterrows()
        ]

    def get_node_summary(self, start_time: datetime, end_time: datetime) -> list[dict]:
        if self._df is None:
            return []

        mask = (self._df["timestamp"] >= start_time) & (self._df["timestamp"] <= end_time)
        window_df = self._df[mask]

        summary = []
        for node_id, group in window_df.groupby("node_id"):
            total = len(group)
            errors = len(group[group["severity"] == "ERROR"])
            error_rate = errors / total if total > 0 else 0.0

            summary.append({
                "node_id": node_id,
                "total_events": total,
                "error_events": errors,
                "error_rate": error_rate,
            })

        return sorted(summary, key=lambda x: x["error_rate"], reverse=True)
