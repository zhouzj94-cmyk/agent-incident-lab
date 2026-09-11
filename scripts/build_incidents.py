import argparse
from pathlib import Path

from environment.incident_env import IncidentEnvironment


def main():
    parser = argparse.ArgumentParser(description="Build incident dataset from BGL logs")
    parser.add_argument("--data", default="data", help="Data directory path")
    parser.add_argument("--output", default="data/incidents/bgl_incidents.json", help="Output path")

    args = parser.parse_args()

    print("Loading BGL dataset...")
    env = IncidentEnvironment(args.data)
    env.initialize()

    incidents = env.get_incidents()
    print(f"Extracted {len(incidents)} incidents")

    env.save_incidents(args.output)
    print(f"Saved incidents to {args.output}")

    from collections import Counter
    difficulty_counts = Counter(inc.difficulty.value for inc in incidents)
    print(f"\nDifficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"  {diff}: {count}")


if __name__ == "__main__":
    main()
