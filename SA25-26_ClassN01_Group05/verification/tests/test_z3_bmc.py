"""Kiểm tra truy vấn BMC-Z3 cho Safety/Liveness và khả năng trả phản ví dụ."""
import sys
import unittest
from pathlib import Path
from z3 import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "bmc"), str(ROOT)]

from run_z3_demo import run_case, run_liveness_case
from generate_artifacts import forbidden_edges_for_spec, load_specs
from z3_bounded_checker import (
    build_liveness_query,
    build_safety_query,
    find_counterexample,
    find_liveness_counterexample,
    reachable_states,
)


class Z3BoundedModelTests(unittest.TestCase):
    """Bộ test cho encoding Z3 trên bốn mô hình HRM và một tình huống chu trình lỗi."""

    @classmethod
    def setUpClass(cls):
        """Nạp các đặc tả một lần để mọi test chạy trên cùng nguồn dữ liệu JSON."""
        cls.specs = {spec["name"]: spec for spec in load_specs()}

    def test_all_models_safe_and_faulty(self):
        """Mô hình bình thường phải UNSAT khi tìm lỗi; mô hình chèn lỗi phải SAT."""
        for name in self.specs:
            with self.subTest(function=name):
                spec = self.specs[name]
                self.assertEqual(run_case(spec, faulty=False)["status"], "unsat")
                self.assertEqual(run_case(spec, faulty=True)["status"], "sat")

    def test_all_models_satisfy_bounded_liveness(self):
        """Không mô hình nào được có đường tránh target đủ dài tạo chu trình vô hạn."""
        for name, spec in self.specs.items():
            with self.subTest(function=name):
                self.assertEqual(run_liveness_case(spec)["status"], "unsat")

    def test_safety_bound_equals_reachable_state_count(self):
        """Xác nhận bound lấy từ graph reachable, không phải một hằng số tùy ý."""
        expected_bounds = {"login": 8, "attendance": 6, "leave": 4, "payroll": 4}
        for name, spec in self.specs.items():
            with self.subTest(function=name):
                initial = next(state["id"] for state in spec["states"] if state.get("initial"))
                transitions = [tuple(edge) for edge in spec["transitions"]]
                bound = len(reachable_states(initial, transitions))
                self.assertEqual(bound, expected_bounds[name])
                result = run_case(spec, faulty=False)
                self.assertEqual(result["bound"], bound)
                self.assertEqual(result["status"], "unsat")

    def test_smt2_queries_replay_with_the_same_solver_status(self):
        for name, spec in self.specs.items():
            states = [state["id"] for state in spec["states"]]
            initial = next(state["id"] for state in spec["states"] if state.get("initial"))
            transitions = [tuple(edge) for edge in spec["transitions"]]
            forbidden = forbidden_edges_for_spec(spec)
            bound = len(reachable_states(initial, transitions))
            faulty_depth = run_case(spec, faulty=True)["depth"]
            target_labels = set(spec["properties"]["liveness"]["target_labels"])
            target_states = [
                state["id"] for state in spec["states"]
                if target_labels.intersection(state.get("labels", []))
            ]
            queries = [
                ("safe", build_safety_query(states, transitions, initial, forbidden, bound)[0], "unsat"),
                (
                    "faulty",
                    build_safety_query(
                        states,
                        [*transitions, tuple(spec["faulty_transition"])],
                        initial,
                        forbidden,
                        faulty_depth,
                    )[0],
                    "sat",
                ),
            ]
            for index, start in enumerate(spec["properties"]["liveness"]["starts"]):
                queries.append((
                    f"liveness_start_{index}",
                    build_liveness_query(states, transitions, start, target_states, bound)[0],
                    "unsat",
                ))
            for kind, solver, expected in queries:
                with self.subTest(function=name, query=kind):
                    replay = Solver()
                    replay.from_string(solver.to_smt2())
                    self.assertEqual(str(replay.check()), expected)

    def test_liveness_counterexample_detects_an_avoiding_cycle(self):
        """Kiểm tra đối chứng: self-loop WAITING phải là phản ví dụ cho AF(DONE)."""
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
        """Chèn lần lượt từng cạnh cấm và xác nhận Z3 trả trace kết thúc đúng cạnh đó."""
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
