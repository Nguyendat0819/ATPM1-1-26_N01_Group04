"""Kiểm thử phần trình bày trace Z3 và phát hiện snapshot kết quả không còn khớp."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_artifacts import forbidden_edges_for_spec, load_specs, spec_fingerprint
from show_bmc_memory import render_trace


class MemoryViewTests(unittest.TestCase):
    """Các test cho việc giải mã state code và kiểm tra tính mới của snapshot BMC."""

    @classmethod
    def setUpClass(cls):
        """Dùng đặc tả login làm fixture vì nó có trace faulty ngắn, dễ đối chiếu."""
        cls.login = next(spec for spec in load_specs() if spec["name"] == "login")

    def make_row(self):
        """Tạo một dòng kết quả giả lập đúng cấu trúc JSON mà runner Z3 lưu."""
        return {
            "function": "login",
            "spec_sha256": spec_fingerprint(self.login),
            "transition_count": len(self.login["transitions"]),
            "forbidden_edges": forbidden_edges_for_spec(self.login),
            "bound": len(self.login["states"]),
            "safe_model": {"status": "unsat"},
            "faulty_model": {
                "status": "sat",
                "depth": 1,
                "path": ["UNAUTHENTICATED", "AUTHENTICATED"],
            },
            "liveness_counterexample": {"status": "unsat"},
        }

    def test_snapshot_decodes_z3_codes_and_marks_violation(self):
        """Đảm bảo state code được giải mã và cạnh UNAUTHENTICATED→AUTHENTICATED bị gắn lỗi."""
        table = render_trace(self.login, self.make_row())
        self.assertIn("state_1_0 = 0", table)
        self.assertIn("state_1_1 = 6", table)
        self.assertIn("UNAUTHENTICATED → AUTHENTICATED | VI PHẠM", table)
        self.assertIn("mô hình đúng: UNSAT", table)

    def test_snapshot_rejects_stale_transition_count(self):
        """Không cho render trace nếu số transition trong log khác đặc tả hiện tại."""
        row = self.make_row()
        row["transition_count"] -= 1
        with self.assertRaisesRegex(ValueError, "chạy lại run_z3_demo.py"):
            render_trace(self.login, row)

    def test_snapshot_rejects_stale_spec_with_same_transition_count(self):
        """Hash đặc tả phải phát hiện thay đổi nội dung dù số cạnh không đổi."""
        row = self.make_row()
        row["spec_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "chạy lại run_z3_demo.py"):
            render_trace(self.login, row)


if __name__ == "__main__":
    unittest.main()
