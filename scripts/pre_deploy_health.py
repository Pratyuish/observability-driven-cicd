#!/usr/bin/env python3
"""Simple pre-deployment health gate.

The first version is dependency-light so contributors can run it anywhere.
Cluster-specific checks will be added incrementally.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def run(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(command, check=True, text=True, capture_output=True)
        return True, completed.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/pre-deploy.json")
    args = parser.parse_args()

    checks: list[Check] = []

    ok, detail = run(["kubectl", "cluster-info"])
    checks.append(Check("kubernetes_api", ok, detail))

    ok, detail = run([
        "kubectl", "get", "nodes",
        "-o", "jsonpath={range .items[*]}{.metadata.name}:{.status.conditions[?(@.type=='Ready')].status}{'\n'}{end}"
    ])
    checks.append(Check("nodes_query", ok, detail))

    passed = all(check.passed for check in checks)
    result = {
        "phase": "pre-deploy",
        "passed": passed,
        "checks": [asdict(check) for check in checks],
    }

    from pathlib import Path
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
