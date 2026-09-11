import argparse
import json
from pathlib import Path

from evaluation.evaluator import Evaluator, EvaluationResult
from evaluation.report import ReportGenerator


def main():
    parser = argparse.ArgumentParser(description="Run evaluation on investigation results")
    parser.add_argument("--results", required=True, help="Path to investigation results JSON")
    parser.add_argument("--ground-truth", default="data/incidents/bgl_incidents.json", help="Path to ground truth")
    parser.add_argument("--output", default="reports", help="Output directory for reports")

    args = parser.parse_args()

    with open(args.results, "r", encoding="utf-8") as f:
        results = json.load(f)

    if not isinstance(results, list):
        results = [results]

    with open(args.ground_truth, "r", encoding="utf-8") as f:
        ground_truth_list = json.load(f)

    ground_truth_map = {gt["incident_id"]: gt for gt in ground_truth_list}

    evaluator_results = []
    for result in results:
        incident_id = result["incident_id"]
        ground_truth = ground_truth_map.get(incident_id, {})

        evaluator = Evaluator(ground_truth)
        eval_result = evaluator.evaluate(result)
        evaluator_results.append(eval_result)

    report_gen = ReportGenerator(args.output)
    report_gen.generate(evaluator_results)


if __name__ == "__main__":
    main()
