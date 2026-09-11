import pytest
from datetime import datetime, timedelta
from agent.state import LogEntry, Event, Incident, Difficulty
from environment.log_store import LogStore


def test_log_store_query():
    store = LogStore()

    entries = [
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            node_id="node-1",
            label="-",
            message="Normal operation",
            raw="2024-01-01 10:00:00 node-1 Normal operation",
        ),
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 5, 0),
            node_id="node-1",
            label="ERROR",
            message="Disk failure detected",
            raw="2024-01-01 10:05:00 node-1 ERROR Disk failure detected",
        ),
    ]

    store.load_from_entries(entries)

    events = store.query(
        start_time=datetime(2024, 1, 1, 10, 0, 0),
        end_time=datetime(2024, 1, 1, 10, 10, 0),
    )

    assert len(events) == 2
    assert events[0].severity == "INFO"
    assert events[1].severity == "ERROR"


def test_log_store_error_stats():
    store = LogStore()

    entries = [
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
            node_id="node-1",
            label="-",
            message="Normal",
            raw="raw1",
        ),
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 1, 0),
            node_id="node-1",
            label="ERROR",
            message="Error A",
            raw="raw2",
        ),
        LogEntry(
            timestamp=datetime(2024, 1, 1, 10, 2, 0),
            node_id="node-1",
            label="ERROR",
            message="Error A",
            raw="raw3",
        ),
    ]

    store.load_from_entries(entries)

    stats = store.get_error_stats(
        start_time=datetime(2024, 1, 1, 10, 0, 0),
        end_time=datetime(2024, 1, 1, 10, 5, 0),
    )

    assert stats["total_events"] == 3
    assert stats["error_events"] == 2
    assert len(stats["top_patterns"]) > 0


def test_incident_model():
    incident = Incident(
        incident_id="TEST-001",
        dataset="BGL",
        start_time=datetime(2024, 1, 1, 10, 0, 0),
        end_time=datetime(2024, 1, 1, 10, 5, 0),
        label="FAILURE",
        root_cause="Test root cause",
        evidence=["ev-001", "ev-002"],
        difficulty=Difficulty.MEDIUM,
    )

    assert incident.incident_id == "TEST-001"
    assert incident.difficulty == Difficulty.MEDIUM
    assert len(incident.evidence) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
