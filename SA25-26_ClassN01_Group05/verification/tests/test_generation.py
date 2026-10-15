import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "bmc"), str(ROOT / "models"), str(ROOT / "faulty_models")]

from bmc.bounded_checker import check_af_labels_from, reachable_state_count, shortest_edge_counterexample
from generate_artifacts import generate_artifacts


class GeneratedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs, cls.cases = generate_artifacts()

    def test_four_features_generate_transition_coverage(self):
        self.assertEqual(len(self.specs), 4)
        self.assertEqual(len(self.cases), sum(len(spec["transitions"]) for spec in self.specs))
        self.assertEqual({case["feature"] for case in self.cases}, {spec["title"] for spec in self.specs})

    def test_safe_and_faulty_models_match_each_property(self):
        for spec in self.specs:
            with self.subTest(feature=spec["name"]):
                safe = importlib.import_module(f"{spec['name']}_kripke").build_model()
                faulty = importlib.import_module(f"{spec['name']}_faulty").build_model()
                bound = reachable_state_count(safe)
                forbidden = spec["properties"]["safety"]["forbidden_edge"]
                self.assertIsNone(shortest_edge_counterexample(safe, forbidden, bound))
                self.assertIsNotNone(shortest_edge_counterexample(faulty, forbidden, bound))
                liveness = spec["properties"]["liveness"]
                self.assertTrue(check_af_labels_from(safe, liveness["target_labels"], liveness["starts"]))


if __name__ == "__main__":
    unittest.main()
