"""Xuất mã hóa SMT-LIB và kết quả kiểm chứng từ bốn đặc tả Kripke HRM."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from z3 import get_version_string

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "bmc"))

from z3_bounded_checker import build_liveness_query, build_safety_query, reachable_states
from generate_artifacts import forbidden_edges_for_spec, load_specs, spec_fingerprint
from run_z3_demo import run_case, run_liveness_case

OUTPUT_DIR = ROOT / "generated" / "z3_evidence"


def write_smt2(filename, solver):
    path = OUTPUT_DIR / filename
    path.write_text(solver.to_smt2(), encoding="utf-8")
    return str(path.relative_to(ROOT))


def inspect_spec(spec):
    name = spec["name"]
    states = [state["id"] for state in spec["states"]]
    initial = next(state["id"] for state in spec["states"] if state.get("initial"))
    transitions = [tuple(edge) for edge in spec["transitions"]]
    forbidden = forbidden_edges_for_spec(spec)
    faulty_edge = tuple(spec["faulty_transition"])
    bound = len(reachable_states(initial, transitions))
    safety_result = run_case(spec, faulty=False)
    faulty_result = run_case(spec, faulty=True)
    liveness_result = run_liveness_case(spec)

    safe_solver, _, codes = build_safety_query(states, transitions, initial, forbidden, bound)
    safe_query_status = str(safe_solver.check())
    safe_smt2 = write_smt2(f"{name}_safety_safe_k{bound}.smt2", safe_solver)

    faulty_depth = faulty_result.get("depth", bound)
    faulty_solver, _, _ = build_safety_query(
        states, [*transitions, faulty_edge], initial, forbidden, faulty_depth
    )
    faulty_query_status = str(faulty_solver.check())
    faulty_smt2 = write_smt2(f"{name}_safety_faulty_k{faulty_depth}.smt2", faulty_solver)

    liveness = spec["properties"]["liveness"]
    target_labels = set(liveness["target_labels"])
    target_states = [
        state["id"] for state in spec["states"]
        if target_labels.intersection(state.get("labels", []))
    ]
    liveness_queries = []
    for index, start in enumerate(liveness["starts"]):
        solver, _, _ = build_liveness_query(
            states, transitions, start, target_states, bound, start_index=index
        )
        query_status = str(solver.check())
        liveness_queries.append({
            "start": start,
            "status": query_status,
            "smt2": write_smt2(f"{name}_liveness_start{index}_k{bound}.smt2", solver),
        })

    return {
        "feature": name,
        "implementation_source": spec["implementation_source"],
        "spec_path": f"specs/{name}.json",
        "spec_sha256": spec_fingerprint(spec),
        "initial": initial,
        "state_codes": codes,
        "transitions": [list(edge) for edge in transitions],
        "reachable_states": sorted(reachable_states(initial, transitions)),
        "bound": bound,
        "safety_property_id": spec["properties"]["safety"]["id"],
        "allowed_predecessors": spec["properties"]["safety"].get("allowed_predecessors", {}),
        "forbidden_edges": [list(edge) for edge in forbidden],
        "faulty_edge": list(faulty_edge),
        "safe_result": safety_result,
        "faulty_result": faulty_result,
        "liveness_property_id": liveness["id"],
        "liveness_starts": liveness["starts"],
        "liveness_target_labels": liveness["target_labels"],
        "liveness_target_states": target_states,
        "liveness_result": liveness_result,
        "safe_smt2": {"path": safe_smt2, "depth": bound, "status": safe_query_status},
        "faulty_smt2": {"path": faulty_smt2, "depth": faulty_depth, "status": faulty_query_status},
        "liveness_smt2": liveness_queries,
    }


def render_markdown(rows, timestamp, z3_version):
    lines = [
        "# Minh chứng mã hóa Z3 từ đặc tả Kripke HRM",
        "",
        f"Lần xuất: {timestamp}; Z3 {z3_version}.",
        "",
        "Nguồn state và transition là `verification/specs/*.json`, được nhóm trừu tượng hóa từ các route HRM ghi ở từng đặc tả. Bộ sinh không tự phân tích mã Express. `formula` trong JSON là mô tả; checker dùng trực tiếp `transitions`, `allowed_predecessors`, `starts` và `target_labels`.",
        "",
        "Mỗi state được đổi thành mã nguyên theo thứ tự trong JSON. Ở bước i, một cạnh `u -> v` thành `And(state_i == code(u), state_(i+1) == code(v))`; quan hệ R là `Or` của tất cả các cạnh. Safety còn yêu cầu cạnh cuối thuộc tập cấm. Bound là số state reachable từ state đầu, tính lại khi chạy.",
        "",
        "File SMT-LIB là truy vấn Z3 thực tế do cùng hàm tạo ràng buộc của checker xuất ra. File Safety chuẩn ở độ sâu k chỉ minh họa một truy vấn; kết quả Safety tổng thể được runner kiểm lần lượt mọi độ sâu 1..k.",
        "",
    ]
    for row in rows:
        codes = row["state_codes"]
        lines.extend([
            f"## {row['feature']}",
            "",
            f"- Đặc tả: `verification/{row['spec_path']}`; SHA-256: `{row['spec_sha256']}`.",
            f"- Route tham chiếu: `{row['implementation_source']}`.",
            f"- State đầu: `{row['initial']}`; bound = |Reach(state đầu)| = {row['bound']} cạnh; truy vấn lớn nhất có {row['bound'] + 1} biến state.",
            f"- Safety {row['safety_property_id']}: tiền nhiệm cho phép `{json.dumps(row['allowed_predecessors'], ensure_ascii=False)}`; suy ra {len(row['forbidden_edges'])} cặp nguồn-đích bị cấm.",
            f"- Cạnh lỗi đối chứng: `{' -> '.join(row['faulty_edge'])}`.",
            f"- Liveness {row['liveness_property_id']}: starts `{', '.join(row['liveness_starts'])}`; nhãn đích `{', '.join(row['liveness_target_labels'])}`; state đích `{', '.join(row['liveness_target_states'])}`.",
            "",
            "| State | Mã Z3 |",
            "|---|---:|",
        ])
        for state, code in codes.items():
            lines.append(f"| `{state}` | {code} |")
        lines.extend(["", "| Transition trong R | Mệnh đề Z3 ở bước i |", "|---|---|"])
        for source, target in row["transitions"]:
            lines.append(
                f"| `{source} -> {target}` | `And(state_i == {codes[source]}, state_(i+1) == {codes[target]})` |"
            )
        faulty_path = row["faulty_result"].get("path") or []
        lines.extend([
            "",
            f"Kết quả: Safety chuẩn **{row['safe_result']['status'].upper()}** qua độ sâu 1..{row['bound']}; "
            f"Safety lỗi **{row['faulty_result']['status'].upper()}** ở độ sâu {row['faulty_smt2']['depth']} "
            f"với trace `{' -> '.join(faulty_path)}`; phản ví dụ Liveness **{row['liveness_result']['status'].upper()}**.",
            "",
            f"SMT-LIB: [Safety chuẩn]({Path(row['safe_smt2']['path']).name}), "
            f"[Safety lỗi]({Path(row['faulty_smt2']['path']).name}), "
            ", ".join(
                f"[Liveness từ {item['start']}]({Path(item['smt2']).name})"
                for item in row["liveness_smt2"]
            ) + ".",
            "",
        ])
    return "\n".join(lines) + "\n"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    z3_version = get_version_string()
    rows = [inspect_spec(spec) for spec in load_specs()]
    passed = all(
        row["safe_result"]["status"] == "unsat"
        and row["faulty_result"]["status"] == "sat"
        and row["liveness_result"]["status"] == "unsat"
        and row["safe_smt2"]["status"] == "unsat"
        and row["faulty_smt2"]["status"] == "sat"
        and all(item["status"] == "unsat" for item in row["liveness_smt2"])
        for row in rows
    )
    summary = {
        "timestamp_utc": timestamp,
        "z3_version": z3_version,
        "status": "PASS" if passed else "FAIL",
        "features": rows,
    }
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "README.md").write_text(
        render_markdown(rows, timestamp, z3_version), encoding="utf-8"
    )
    for row in rows:
        print(
            f"{row['feature']}: bound={row['bound']}, "
            f"safe={row['safe_result']['status'].upper()}, "
            f"faulty={row['faulty_result']['status'].upper()}, "
            f"liveness-counterexample={row['liveness_result']['status'].upper()}"
        )
    print(f"Overall: {summary['status']}")
    print(f"Evidence: {OUTPUT_DIR}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
