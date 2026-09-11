import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Iterator
from agent.state import LogEntry


class BGLDatasetLoader:
    """
    BGL 数据集加载器。
    
    BGL 日志格式（空格分隔）：
    label timestamp node day time node_id severity event_id message...
    
    标签说明：
    - "-" 表示正常日志
    - 其他值表示异常类型（如 "IF", "NF" 等）
    """
    
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self._df: pd.DataFrame | None = None  # 懒加载缓存

    def load(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df

        file_path = self.data_path / "raw" / "BGL" / "BGL.log"
        if not file_path.exists():
            raise FileNotFoundError(f"BGL dataset not found at {file_path}")

        columns = [
            "label", "time", "node", "day", "time_of_day", "node_id",
            "message", "severity", "event_id", "raw"
        ]

        records = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 9:
                    continue

                label = parts[0]
                time_val = int(parts[1])
                node = parts[2]
                day = parts[3]
                time_of_day = parts[4]
                node_id = parts[5]
                severity = parts[6]
                event_id = parts[7]
                message = " ".join(parts[8:])
                raw = line.strip()

                timestamp = datetime.fromtimestamp(time_val)

                records.append({
                    "label": label,
                    "timestamp": timestamp,
                    "node": node,
                    "day": day,
                    "time_of_day": time_of_day,
                    "node_id": node_id,
                    "severity": severity,
                    "event_id": event_id,
                    "message": message,
                    "raw": raw,
                })

        self._df = pd.DataFrame(records)
        self._df = self._df.sort_values("timestamp").reset_index(drop=True)
        return self._df

    def iter_entries(self) -> Iterator[LogEntry]:
        df = self.load()
        for _, row in df.iterrows():
            yield LogEntry(
                timestamp=row["timestamp"],
                node_id=row["node_id"],
                label=row["label"],
                message=row["message"],
                raw=row["raw"],
            )

    def get_time_range(self) -> tuple[datetime, datetime]:
        df = self.load()
        return df["timestamp"].min(), df["timestamp"].max()

    def get_node_ids(self) -> list[str]:
        df = self.load()
        return df["node_id"].unique().tolist()

    def get_anomaly_ratio(self) -> float:
        df = self.load()
        return (df["label"] != "-").sum() / len(df)
