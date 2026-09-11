from typing import Any
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    incident_id: str
    root_cause_accuracy: float
    evidence_precision: float
    tool_selection_accuracy: float
    investigation_success: bool
    steps: int
    redundant_calls: int
    recovery_count: int


class Evaluator:
    def __init__(self, ground_truth: dict):
        self.ground_truth = ground_truth

    def evaluate(self, result: dict) -> EvaluationResult:
        root_cause_acc = self._evaluate_root_cause(result)
        evidence_prec = self._evaluate_evidence(result)
        tool_acc = self._evaluate_tool_selection(result)
        success = self._evaluate_success(result)
        redundant = self._count_redundant_calls(result)

        return EvaluationResult(
            incident_id=result["incident_id"],
            root_cause_accuracy=root_cause_acc,
            evidence_precision=evidence_prec,
            tool_selection_accuracy=tool_acc,
            investigation_success=success,
            steps=result["steps"],
            redundant_calls=redundant,
            recovery_count=0,
        )

    def _evaluate_root_cause(self, result: dict) -> float:
        final_answer = result.get("final_answer", {})
        predicted_cause = final_answer.get("root_cause", "")
        actual_cause = self.ground_truth.get("root_cause", "")

        if not predicted_cause or not actual_cause:
            return 0.0

        predicted_lower = predicted_cause.lower()
        actual_lower = actual_cause.lower()

        if actual_lower in predicted_lower or predicted_lower in actual_lower:
            return 1.0

        return 0.0

    def _evaluate_evidence(self, result: dict) -> float:
        final_answer = result.get("final_answer", {})
        evidence_ids = final_answer.get("evidence_ids", [])
        actual_evidence = set(self.ground_truth.get("evidence", []))

        if not actual_evidence:
            return 1.0 if evidence_ids else 0.0

        predicted_evidence = set(evidence_ids)
        if not predicted_evidence:
            return 0.0

        intersection = len(predicted_evidence & actual_evidence)
        precision = intersection / len(predicted_evidence) if predicted_evidence else 0.0

        return precision

    def _evaluate_tool_selection(self, result: dict) -> float:
        trajectory = result.get("trajectory", [])
        if not trajectory:
            return 0.0

        tool_calls = [
            step["action"]
            for step in trajectory
            if step["action"].get("type") == "tool_call"
        ]

        if not tool_calls:
            return 0.0

        valid_tools = {"search_logs", "get_error_stats", "compare_window", "get_related_events", "get_service_summary"}
        valid_calls = sum(1 for call in tool_calls if call.get("tool_name") in valid_tools)

        return valid_calls / len(tool_calls)

    def _evaluate_success(self, result: dict) -> bool:
        final_answer = result.get("final_answer", {})
        confidence = final_answer.get("confidence", 0.0)
        evidence_ids = final_answer.get("evidence_ids", [])

        return confidence >= 0.75 and len(evidence_ids) > 0

    def _count_redundant_calls(self, result: dict) -> int:
        trajectory = result.get("trajectory", [])
        tool_signatures = []

        for step in trajectory:
            action = step.get("action", {})
            if action.get("type") == "tool_call":
                sig = f"{action.get('tool_name')}:{str(action.get('tool_args'))}"
                tool_signatures.append(sig)

        redundant = 0
        for i in range(1, len(tool_signatures)):
            if tool_signatures[i] == tool_signatures[i - 1]:
                redundant += 1

        return redundant
