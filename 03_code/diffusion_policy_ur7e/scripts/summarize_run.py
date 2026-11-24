"""Summarize recorded events; ACK, completed motion and task success remain distinct."""

from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np


def summarize(directory):
    directory = Path(directory)
    events = [
        json.loads(line)
        for line in (directory / "events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    counts = Counter(row.get("event", "unknown") for row in events)
    motions = [
        row for row in events if row.get("event") == "motion" and row.get("completed") is True
    ]

    def distance(a, b):
        return float(np.linalg.norm(np.asarray(a)[:3] - np.asarray(b)[:3]))

    return {
        "run_id": directory.name,
        "event_counts": dict(counts),
        "acknowledged_motions": counts["motion_command_acknowledged"],
        "completed_motions": len(motions),
        "feedback_samples": counts["motion_feedback"],
        "command_displacements_m": [
            distance(row["target"], row["actual_before"]) for row in motions
        ],
        "measured_displacements_m": [
            distance(row["actual_after"], row["actual_before"]) for row in motions
        ],
        "endpoint_errors_m": [distance(row["target"], row["actual_after"]) for row in motions],
        "run_completed": counts["completed"] > 0 and counts["failed"] == 0,
        "task_success_evaluated": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = summarize(args.directory)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
