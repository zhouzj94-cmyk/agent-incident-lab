import json
import csv
from pathlib import Path
from typing import Any
from evaluation.evaluator import EvaluationResult


class ReportGenerator:
    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, results: list[EvaluationResult]) -> None:
        self._save_json(results)
        self._save_csv(results)
        self._print_summary(results)

    def _save_json(self, results: list[EvaluationResult]) -> None:
        data = [
            {
                "incident_id": r.incident_id,
                "root_cause_accuracy": r.root_cause_accuracy,
                "evidence_precision": r.evidence_precision,
                "tool_selection_accuracy": r.tool_selection_accuracy,
                "investigation_success": r.investigation_success,
                "steps": r.steps,
                "redundant_calls": r.redundant_calls,
            }
            for r in results
        ]

        output_path = self.output_dir / "evaluation_results.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Saved JSON results to {output_path}")

    def _save_csv(self, results: list[EvaluationResult]) -> None:
        output_path = self.output_dir / "evaluation_results.csv"

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "incident_id",
                "root_cause_accuracy",
                "evidence_precision",
                "tool_selection_accuracy",
                "investigation_success",
                "steps",
                "redundant_calls",
            ])

            for r in results:
                writer.writerow([
                    r.incident_id,
                    r.root_cause_accuracy,
                    r.evidence_precision,
                    r.tool_selection_accuracy,
                    r.investigation_success,
                    r.steps,
                    r.redundant_calls,
                ])

        print(f"Saved CSV results to {output_path}")

    def _print_summary(self, results: list[EvaluationResult]) -> None:
        if not results:
            print("No results to summarize")
            return

        avg_rc_acc = sum(r.root_cause_accuracy for r in results) / len(results)
        avg_ev_prec = sum(r.evidence_precision for r in results) / len(results)
        avg_tool_acc = sum(r.tool_selection_accuracy for r in results) / len(results)
        success_rate = sum(1 for r in results if r.investigation_success) / len(results)
        avg_steps = sum(r.steps for r in results) / len(results)
        avg_redundant = sum(r.redundant_calls for r in results) / len(results)

        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total incidents: {len(results)}")
        print(f"Root Cause Accuracy: {avg_rc_acc:.2%}")
        print(f"Evidence Precision: {avg_ev_prec:.2%}")
        print(f"Tool Selection Accuracy: {avg_tool_acc:.2%}")
        print(f"Investigation Success Rate: {success_rate:.2%}")
        print(f"Average Steps: {avg_steps:.1f}")
        print(f"Average Redundant Calls: {avg_redundant:.1f}")
        print("=" * 60)
