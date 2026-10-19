import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "bmc"), str(ROOT)]

from run_z3_demo import run_case, run_liveness_case
from generate_artifacts import forbidden_edges_for_spec, load_specs
from z3_bounded_checker import (
    find_counterexample,
    find_liveness_counterexample,
    reachable_states,
)


class Z3BoundedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = {spec["name"]: spec for spec in load_specs()}

    def test_all_models_safe_and_faulty(self):
        for name in self.specs:
            with self.subTest(function=name):
                spec = self.specs[name]
                self.assertEqual(run_case(spec, faulty=False)["status"], "unsat")
                self.assertEqual(run_case(spec, faulty=True)["status"], "sat")

    def test_all_models_satisfy_bounded_liveness(self):
        for name, spec in self.specs.items():
            with self.subTest(function=name):
                self.assertEqual(run_liveness_case(spec)["status"], "unsat")

    def test_liveness_counterexample_detects_an_avoiding_cycle(self):
        result = find_liveness_counterexample(
            ["WAITING", "DONE"],
            [("WAITING", "WAITING"), ("DONE", "DONE")],
            ["WAITING"],
            ["DONE"],
            2,
        )
        self.assertEqual(result["status"], "sat")
        self.assertEqual(result["path"], ["WAITING", "WAITING", "WAITING"])

    def test_each_declared_forbidden_edge_has_a_z3_counterexample(self):
        for name in self.specs:
            spec = self.specs[name]
            states = [state["id"] for state in spec["states"]]
            transitions = [tuple(edge) for edge in spec["transitions"]]
            initial = next(state["id"] for state in spec["states"] if state.get("initial"))
            forbidden = forbidden_edges_for_spec(spec)
            bound = len(reachable_states(initial, transitions))
            for edge in forbidden:
                with self.subTest(function=name, edge=edge):
                    injected = transitions + [tuple(edge)]
                    result = find_counterexample(states, injected, initial, [edge], bound + 1)
                    self.assertEqual(result["status"], "sat")
                    self.assertEqual(result["path"][-2:], list(edge))


if __name__ == "__main__":
    unittest.main()
