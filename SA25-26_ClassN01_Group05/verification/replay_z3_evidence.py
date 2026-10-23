"""Nạp lại các truy vấn SMT-LIB đã xuất để đối chiếu kết quả Z3 và đặc tả hiện tại."""

import json
from pathlib import Path

from z3 import Solver

from generate_artifacts import load_specs, spec_fingerprint


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "generated" / "z3_evidence"


def main():
    summary = json.loads((EVIDENCE / "summary.json").read_text(encoding="utf-8"))
    current_specs = {spec["name"]: spec_fingerprint(spec) for spec in load_specs()}
    checks = 0

    for feature in summary["features"]:
        name = feature["feature"]
        if current_specs.get(name) != feature["spec_sha256"]:
            raise SystemExit(f"FAIL: đặc tả {name} đã đổi; hãy xuất minh chứng lại")

        queries = [feature["safe_smt2"], feature["faulty_smt2"], *feature["liveness_smt2"]]
        for query in queries:
            path = ROOT / query.get("path", query.get("smt2"))
            solver = Solver()
            solver.from_file(str(path))
            actual = str(solver.check())
            expected = query["status"]
            print(f"{path.name}: expected={expected}, actual={actual}")
            if actual != expected:
                raise SystemExit(f"FAIL: truy vấn {path.name} không khớp")
            checks += 1

    if len(summary["features"]) != 4 or checks != 12:
        raise SystemExit(f"FAIL: kỳ vọng 4 mô hình/12 truy vấn, nhận {len(summary['features'])}/{checks}")
    print(f"PASS: {checks}/{checks} truy vấn SMT-LIB, 4/4 fingerprint đặc tả khớp")


if __name__ == "__main__":
    main()
