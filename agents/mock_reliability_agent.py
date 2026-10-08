#!/usr/bin/env python3
"""Deterministic reliability agent used for local demos and CI tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def evaluate(report: dict[str, Any]) -> dict[str, Any]:
    failures = [name for name, gate in report.get("gates", {}).items() if not gate.get("passed", False)]
    decision = "PROMOTE" if not failures else "BLOCK"

    reasons = []
    for name in failures:
        gate = report["gates"][name]
        reasons.append(
            f"{name} failed: observed={gate.get('observed')} threshold={gate.get('threshold')}"
        )

    return {
        "agent": "mock-reliability-agent",
        "mode": "deterministic",
        "decision": decision,
        "failed_gates": failures,
        "summary": "All gates passed." if not failures else "; ".join(reasons),
        "recommended_action": "continue rollout" if not failures else "pause rollout and investigate",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path, help="JSON health-gate report")
    args = parser.parse_args()

    report = json.loads(args.report.read_text())
    result = evaluate(report)
    print(json.dumps(result, indent=2))
    return 0 if result["decision"] == "PROMOTE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
