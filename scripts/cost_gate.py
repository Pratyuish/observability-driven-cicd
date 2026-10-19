#!/usr/bin/env python3
"""Estimate Kubernetes manifest cost and enforce a pre-deployment budget policy.

This is intentionally vendor-neutral and API-key-free. The pricing file is an
input, so teams can substitute public list prices, negotiated rates, or internal
showback rates without changing the estimator.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ResourceCost:
    resource: str
    kind: str
    compute: float = 0.0
    storage: float = 0.0
    network: float = 0.0

    @property
    def total(self) -> float:
        return self.compute + self.storage + self.network


def cpu_cores(value: str | int | float | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if text.endswith("m"):
        return float(text[:-1]) / 1000.0
    return float(text)


def memory_gib(value: str | int | float | None) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    suffixes = {
        "Ki": 1 / (1024 * 1024),
        "Mi": 1 / 1024,
        "Gi": 1.0,
        "Ti": 1024.0,
        "K": 1000 / (1024**3),
        "M": 1000**2 / (1024**3),
        "G": 1000**3 / (1024**3),
        "T": 1000**4 / (1024**3),
    }
    for suffix, multiplier in suffixes.items():
        if text.endswith(suffix):
            return float(text[: -len(suffix)]) * multiplier
    return float(text) / (1024**3)


def storage_gib(value: str | int | float | None) -> float:
    return memory_gib(value)


def load_documents(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    paths = sorted(path.rglob("*.y*ml")) if path.is_dir() else [path]
    for item in paths:
        with item.open("r", encoding="utf-8") as handle:
            for doc in yaml.safe_load_all(handle):
                if isinstance(doc, dict) and doc.get("kind"):
                    docs.append(doc)
    return docs


def pod_spec_and_replicas(doc: dict[str, Any], assumed_daemonset_nodes: int) -> tuple[dict[str, Any] | None, int]:
    kind = doc.get("kind", "")
    spec = doc.get("spec", {}) or {}

    if kind in {"Deployment", "StatefulSet", "ReplicaSet"}:
        return (spec.get("template", {}) or {}).get("spec", {}), int(spec.get("replicas", 1) or 1)
    if kind == "DaemonSet":
        return (spec.get("template", {}) or {}).get("spec", {}), assumed_daemonset_nodes
    if kind == "Pod":
        return spec, 1
    if kind == "Job":
        parallelism = int(spec.get("parallelism", 1) or 1)
        return (spec.get("template", {}) or {}).get("spec", {}), parallelism

    return None, 0


def estimate(path: Path, pricing: dict[str, Any], require_requests: bool) -> dict[str, Any]:
    hours = float(pricing["hours_per_month"])
    cpu_rate = float(pricing["compute"]["cpu_core_hour"])
    memory_rate = float(pricing["compute"]["memory_gib_hour"])
    pv_rate = float(pricing["storage"]["persistent_volume_gib_month"])
    lb_rate = float(pricing["network"]["load_balancer_month"])
    daemon_nodes = int(pricing.get("kubernetes", {}).get("assumed_daemonset_nodes", 3))

    costs: list[ResourceCost] = []
    warnings: list[str] = []
    missing_requests: list[str] = []

    for doc in load_documents(path):
        kind = str(doc.get("kind"))
        metadata = doc.get("metadata", {}) or {}
        name = metadata.get("name", "unnamed")
        namespace = metadata.get("namespace", "default")
        resource_id = f"{namespace}/{name}"

        pod_spec, replicas = pod_spec_and_replicas(doc, daemon_nodes)
        if pod_spec is not None:
            cpu = 0.0
            memory = 0.0
            containers = list(pod_spec.get("containers", []) or []) + list(pod_spec.get("initContainers", []) or [])
            for container in containers:
                requests = ((container.get("resources", {}) or {}).get("requests", {}) or {})
                cname = container.get("name", "unnamed")
                if "cpu" not in requests or "memory" not in requests:
                    missing_requests.append(f"{resource_id}/{cname}")
                cpu += cpu_cores(requests.get("cpu"))
                memory += memory_gib(requests.get("memory"))

            compute = replicas * hours * ((cpu * cpu_rate) + (memory * memory_rate))
            costs.append(ResourceCost(resource_id, kind, compute=compute))

        elif kind == "PersistentVolumeClaim":
            requested = (((doc.get("spec", {}) or {}).get("resources", {}) or {}).get("requests", {}) or {}).get("storage")
            gib = storage_gib(requested)
            costs.append(ResourceCost(resource_id, kind, storage=gib * pv_rate))

        elif kind == "Service" and (doc.get("spec", {}) or {}).get("type") == "LoadBalancer":
            costs.append(ResourceCost(resource_id, kind, network=lb_rate))

    if missing_requests:
        warnings.append(
            "Missing CPU or memory requests for: " + ", ".join(sorted(missing_requests))
        )

    total = sum(item.total for item in costs)
    return {
        "source": str(path),
        "monthly_cost": round(total, 2),
        "resources": [
            {
                **asdict(item),
                "total": round(item.total, 2),
                "compute": round(item.compute, 2),
                "storage": round(item.storage, 2),
                "network": round(item.network, 2),
            }
            for item in costs
        ],
        "warnings": warnings,
        "missing_requests": missing_requests,
        "valid": not (require_requests and missing_requests),
    }


def evaluate_policy(baseline: dict[str, Any], candidate: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    rules = policy["policy"]
    base = float(baseline["monthly_cost"])
    cand = float(candidate["monthly_cost"])
    absolute = cand - base
    percent = 0.0 if base == 0 and cand == 0 else math.inf if base == 0 else (absolute / base) * 100.0

    checks = {
        "candidate_manifest_valid": {
            "passed": bool(candidate["valid"]),
            "observed": "valid" if candidate["valid"] else "missing resource requests",
            "threshold": "all workload containers have cpu+memory requests",
        },
        "max_monthly_cost": {
            "passed": cand <= float(rules["max_monthly_cost"]),
            "observed": round(cand, 2),
            "threshold": float(rules["max_monthly_cost"]),
        },
        "max_absolute_increase": {
            "passed": absolute <= float(rules["max_absolute_increase"]),
            "observed": round(absolute, 2),
            "threshold": float(rules["max_absolute_increase"]),
        },
        "max_increase_percent": {
            "passed": percent <= float(rules["max_increase_percent"]),
            "observed": "inf" if math.isinf(percent) else round(percent, 2),
            "threshold": float(rules["max_increase_percent"]),
        },
    }

    passed = all(item["passed"] for item in checks.values())
    return {
        "decision": "PASS" if passed else "BLOCK",
        "currency": policy.get("currency"),
        "baseline_monthly_cost": round(base, 2),
        "candidate_monthly_cost": round(cand, 2),
        "absolute_change": round(absolute, 2),
        "percent_change": "inf" if math.isinf(percent) else round(percent, 2),
        "checks": checks,
        "approval_required": cand >= float(rules.get("approval_required_above_monthly_cost", math.inf)),
        "owner": rules.get("owner", "unknown"),
    }


def markdown_report(result: dict[str, Any], baseline: dict[str, Any], candidate: dict[str, Any], currency: str) -> str:
    lines = [
        "# Pre-deployment FinOps Gate",
        "",
        f"**Decision:** {result['decision']}",
        "",
        "| Metric | Baseline | Candidate | Change |",
        "| --- | ---: | ---: | ---: |",
        f"| Monthly run rate | {currency} {result['baseline_monthly_cost']:.2f} | {currency} {result['candidate_monthly_cost']:.2f} | {currency} {result['absolute_change']:.2f} ({result['percent_change']}%) |",
        "",
        "## Policy checks",
        "",
        "| Check | Result | Observed | Threshold |",
        "| --- | --- | --- | --- |",
    ]
    for name, check in result["checks"].items():
        lines.append(
            f"| {name} | {'PASS' if check['passed'] else 'FAIL'} | {check['observed']} | {check['threshold']} |"
        )

    lines += ["", "## Candidate cost by resource", "", "| Resource | Kind | Compute | Storage | Network | Total |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for item in sorted(candidate["resources"], key=lambda x: x["total"], reverse=True):
        lines.append(
            f"| {item['resource']} | {item['kind']} | {currency} {item['compute']:.2f} | {currency} {item['storage']:.2f} | {currency} {item['network']:.2f} | {currency} {item['total']:.2f} |"
        )

    warnings = baseline.get("warnings", []) + candidate.get("warnings", [])
    if warnings:
        lines += ["", "## Warnings", ""]
        lines += [f"- {warning}" for warning in warnings]

    lines += [
        "",
        "> Pricing is configurable and illustrative by default. Replace finops/pricing.yaml with your negotiated or internal showback rates.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--pricing", type=Path, default=Path("finops/pricing.yaml"))
    parser.add_argument("--policy", type=Path, default=Path("finops/budget-policy.yaml"))
    parser.add_argument("--output", type=Path, default=Path("reports/cost-gate.json"))
    parser.add_argument("--summary", type=Path, default=Path("reports/cost-gate.md"))
    args = parser.parse_args()

    pricing = yaml.safe_load(args.pricing.read_text(encoding="utf-8"))
    policy = yaml.safe_load(args.policy.read_text(encoding="utf-8"))
    policy["currency"] = pricing.get("currency", "USD")

    require_requests = bool(policy["policy"].get("require_resource_requests", True))
    baseline = estimate(args.baseline, pricing, require_requests)
    candidate = estimate(args.candidate, pricing, require_requests)
    result = evaluate_policy(baseline, candidate, policy)

    payload = {
        "result": result,
        "baseline": baseline,
        "candidate": candidate,
        "pricing_file": str(args.pricing),
        "policy_file": str(args.policy),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    args.summary.write_text(
        markdown_report(result, baseline, candidate, pricing.get("currency", "USD")),
        encoding="utf-8",
    )

    print(args.summary.read_text(encoding="utf-8"))
    return 0 if result["decision"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
