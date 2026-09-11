from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import json

from agent.state import Incident, Difficulty
from environment.parser import BGLDatasetLoader
from environment.log_store import LogStore


class IncidentEnvironment:
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self.loader = BGLDatasetLoader(data_path)
        self.log_store = LogStore()
        self._incidents: list[Incident] = []
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return

        entries = list(self.loader.iter_entries())
        self.log_store.load_from_entries(entries)
        self._incidents = self._extract_incidents()
        self._initialized = True

    def _extract_incidents(self) -> list[Incident]:
        df = self.loader.load()

        anomaly_df = df[df["label"] != "-"].copy()
        if anomaly_df.empty:
            return []

        incidents = []
        incident_groups = []

        current_group = [anomaly_df.iloc[0]]
        for idx in range(1, len(anomaly_df)):
            row = anomaly_df.iloc[idx]
            prev_row = anomaly_df.iloc[idx - 1]

            time_diff = (row["timestamp"] - prev_row["timestamp"]).total_seconds()

            if time_diff <= 300:
                current_group.append(row)
            else:
                incident_groups.append(current_group)
                current_group = [row]

        incident_groups.append(current_group)

        for idx, group in enumerate(incident_groups):
            group_df = pd.DataFrame(group)

            start_time = group_df["timestamp"].min()
            end_time = group_df["timestamp"].max()

            if (end_time - start_time).total_seconds() < 60:
                end_time = start_time + timedelta(minutes=5)

            start_time = start_time - timedelta(minutes=2)
            end_time = end_time + timedelta(minutes=2)

            label = group_df["label"].mode()[0] if not group_df["label"].mode().empty else "UNKNOWN"
            node_ids = group_df["node_id"].unique().tolist()

            difficulty = self._assess_difficulty(group_df)

            incident = Incident(
                incident_id=f"BGL-{idx + 1:05d}",
                dataset="BGL",
                start_time=start_time,
                end_time=end_time,
                label=label,
                root_cause=f"Anomalous behavior detected on nodes: {', '.join(node_ids)}",
                evidence=[],
                difficulty=difficulty,
                metadata={
                    "node_ids": node_ids,
                    "anomaly_count": len(group_df),
                    "label": label,
                },
            )
            incidents.append(incident)

        return incidents

    def _assess_difficulty(self, group_df) -> Difficulty:
        anomaly_count = len(group_df)
        node_count = group_df["node_id"].nunique()

        if anomaly_count <= 3 and node_count == 1:
            return Difficulty.EASY
        elif anomaly_count <= 10 and node_count <= 3:
            return Difficulty.MEDIUM
        else:
            return Difficulty.HARD

    def get_incidents(self) -> list[Incident]:
        if not self._initialized:
            self.initialize()
        return self._incidents

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        if not self._initialized:
            self.initialize()

        for incident in self._incidents:
            if incident.incident_id == incident_id:
                return incident
        return None

    def get_incidents_by_difficulty(self, difficulty: Difficulty) -> list[Incident]:
        if not self._initialized:
            self.initialize()

        return [inc for inc in self._incidents if inc.difficulty == difficulty]

    def save_incidents(self, output_path: str | Path) -> None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        incidents_data = [inc.model_dump(mode="json") for inc in self._incidents]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(incidents_data, f, indent=2, default=str)

    def load_incidents(self, input_path: str | Path) -> None:
        input_path = Path(input_path)

        with open(input_path, "r", encoding="utf-8") as f:
            incidents_data = json.load(f)

        self._incidents = [Incident(**data) for data in incidents_data]


import pandas as pd
