import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path

import yaml


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "cost_gate.py"
SPEC = importlib.util.spec_from_file_location("cost_gate", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


PRICING = {
    "currency": "USD",
    "hours_per_month": 730,
    "compute": {"cpu_core_hour": 0.04, "memory_gib_hour": 0.005},
    "storage": {"persistent_volume_gib_month": 0.08},
    "network": {"load_balancer_month": 18.0},
    "kubernetes": {"assumed_daemonset_nodes": 3},
}


def deployment(replicas=1, cpu="250m", memory="256Mi"):
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "api"},
        "spec": {
            "replicas": replicas,
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": "api",
                            "resources": {"requests": {"cpu": cpu, "memory": memory}},
                        }
                    ]
                }
            },
        },
    }


class CostGateTests(unittest.TestCase):
    def write_docs(self, docs):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        yaml.safe_dump_all(docs, tmp)
        tmp.close()
        return Path(tmp.name)

    def test_candidate_cost_increases_with_replicas(self):
        baseline_path = self.write_docs([deployment(replicas=1)])
        candidate_path = self.write_docs([deployment(replicas=3)])
        baseline = MODULE.estimate(baseline_path, PRICING, True)
        candidate = MODULE.estimate(candidate_path, PRICING, True)
        self.assertGreater(candidate["monthly_cost"], baseline["monthly_cost"])

    def test_load_balancer_and_pvc_are_costed(self):
        path = self.write_docs(
            [
                deployment(),
                {"apiVersion": "v1", "kind": "Service", "metadata": {"name": "api"}, "spec": {"type": "LoadBalancer"}},
                {
                    "apiVersion": "v1",
                    "kind": "PersistentVolumeClaim",
                    "metadata": {"name": "data"},
                    "spec": {"resources": {"requests": {"storage": "100Gi"}}},
                },
            ]
        )
        report = MODULE.estimate(path, PRICING, True)
        by_kind = {item["kind"]: item for item in report["resources"]}
        self.assertEqual(by_kind["Service"]["network"], 18.0)
        self.assertEqual(by_kind["PersistentVolumeClaim"]["storage"], 8.0)

    def test_missing_requests_can_block(self):
        doc = deployment()
        del doc["spec"]["template"]["spec"]["containers"][0]["resources"]
        path = self.write_docs([doc])
        report = MODULE.estimate(path, PRICING, True)
        self.assertFalse(report["valid"])
        self.assertTrue(report["missing_requests"])

    def test_policy_blocks_large_increase(self):
        baseline = {"monthly_cost": 100.0, "valid": True}
        candidate = {"monthly_cost": 150.0, "valid": True}
        policy = {
            "policy": {
                "max_monthly_cost": 200.0,
                "max_increase_percent": 20.0,
                "max_absolute_increase": 100.0,
                "approval_required_above_monthly_cost": 180.0,
            }
        }
        result = MODULE.evaluate_policy(baseline, candidate, policy)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertFalse(result["checks"]["max_increase_percent"]["passed"])


if __name__ == "__main__":
    unittest.main()
