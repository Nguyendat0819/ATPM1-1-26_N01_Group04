import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "bmc"), str(ROOT / "models"), str(ROOT / "faulty_models")]

from bmc.bounded_checker import check_af_labels_from, reachable_state_count, shortest_forbidden_edge_counterexample
from generate_artifacts import forbidden_edges_for_spec, generate_artifacts
from properties.check_properties import run_suite


class GeneratedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs, cls.cases = generate_artifacts()

    def test_four_features_generate_transition_coverage(self):
        self.assertEqual(len(self.specs), 4)
        expected = sum(
            len(spec["transitions"]) + 1 + len(spec["properties"]["liveness"]["starts"])
            for spec in self.specs
        )
        self.assertEqual(len(self.cases), expected)
        self.assertEqual({case["feature"] for case in self.cases}, {spec["title"] for spec in self.specs})
        markdown = ROOT / "generated" / "test_cases.md"
        self.assertTrue(markdown.exists())
        self.assertIn("GEN-LOGIN-SAFETY-01", markdown.read_text(encoding="utf-8"))

    def test_generated_cases_cover_transitions_safety_and_liveness(self):
        self.assertEqual(sum(case["coverage"] == "transition" for case in self.cases), 26)
        self.assertEqual(sum(case["coverage"] == "safety_constraint" for case in self.cases), 4)
        self.assertEqual(sum(case["coverage"] == "liveness_witness" for case in self.cases), 4)
        for spec in self.specs:
            model = importlib.import_module(f"{spec['name']}_kripke").build_model()
            cases = [case for case in self.cases if case["feature"] == spec["title"]]
            for case in cases:
                with self.subTest(case=case["id"]):
                    path = case["state_path"]
                    if case["coverage"] == "transition":
                        self.assertEqual(path[-2:], case["transition"])
                        self.assertTrue(all(
                            right in model.transitions[left]
                            for left, right in zip(path, path[1:])
                        ))
                    elif case["coverage"] == "safety_constraint":
                        self.assertEqual(path[-2:], spec["faulty_transition"])
                        self.assertTrue(all(
                            right in model.transitions[left]
                            for left, right in zip(path[:-2], path[1:-1])
                        ))
                        self.assertEqual(case["expected_result"], "rejected")
                    else:
                        self.assertEqual(path[0], case["start_state"])
                        self.assertTrue(all(
                            right in model.transitions[left]
                            for left, right in zip(path, path[1:])
                        ))
                        self.assertTrue(set(case["target_labels"]).intersection(model.labels[path[-1]]))

    def test_safe_and_faulty_models_match_each_property(self):
        for spec in self.specs:
            with self.subTest(feature=spec["name"]):
                safe = importlib.import_module(f"{spec['name']}_kripke").build_model()
                faulty = importlib.import_module(f"{spec['name']}_faulty").build_model()
                bound = reachable_state_count(safe)
                safety = spec["properties"]["safety"]
                forbidden = forbidden_edges_for_spec(spec)
                self.assertIsNone(shortest_forbidden_edge_counterexample(safe, forbidden, bound))
                self.assertIsNotNone(shortest_forbidden_edge_counterexample(faulty, forbidden, bound))
                liveness = spec["properties"]["liveness"]
                self.assertTrue(check_af_labels_from(safe, liveness["target_labels"], liveness["starts"]))
                summary = run_suite(spec, safe)
                self.assertTrue(summary["safety"])
                self.assertTrue(summary["liveness"])


if __name__ == "__main__":
    unittest.main()
