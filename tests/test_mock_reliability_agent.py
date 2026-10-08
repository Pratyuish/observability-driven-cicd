import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "agents" / "mock_reliability_agent.py"
SPEC = importlib.util.spec_from_file_location("mock_reliability_agent", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReliabilityAgentTests(unittest.TestCase):
    def test_promotes_when_all_gates_pass(self):
        report = {
            "gates": {
                "availability": {"passed": True},
                "latency": {"passed": True},
            }
        }
        result = MODULE.evaluate(report)
        self.assertEqual(result["decision"], "PROMOTE")
        self.assertEqual(result["failed_gates"], [])

    def test_blocks_when_a_gate_fails(self):
        report = {
            "gates": {
                "availability": {"passed": True},
                "latency": {
                    "passed": False,
                    "observed": 800,
                    "threshold": "<= 500 ms",
                },
            }
        }
        result = MODULE.evaluate(report)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["failed_gates"], ["latency"])


if __name__ == "__main__":
    unittest.main()
