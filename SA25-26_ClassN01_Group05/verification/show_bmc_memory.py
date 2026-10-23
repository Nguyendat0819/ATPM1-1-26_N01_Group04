"""Hiển thị trace phản ví dụ đã lưu cạnh số đo RAM của lần chạy BMC gần nhất."""
import argparse
import json
import sys
from pathlib import Path

from generate_artifacts import forbidden_edges_for_spec, load_specs, spec_fingerprint

ROOT = Path(__file__).resolve().parent
DEFAULT_RESULTS = ROOT / "results" / "z3_bmc_memory.json"


def render_memory(result):
    """Định dạng RSS, heap Python, RAM hệ thống và thông tin phiên bản thành Markdown."""
    memory = result["memory_measurement"]
    samples = result["memory_samples"]
    rss_samples = [item["process_rss_kib"] for item in samples]
    return "\n".join([
        "## RAM của lần chạy Z3 đã lưu",
        f"Thời điểm UTC: {result['timestamp_utc']} | Z3: {result['z3_version']} | lặp: {memory['repeat_count']}",
        f"RSS tiến trình trước/sau/đỉnh: {memory['process_rss_before_kib']} / "
        f"{memory['process_rss_after_kib']} / {memory['process_peak_rss_kib']} KiB",
        f"Python heap hiện tại/đỉnh: {memory['python_heap_current_bytes']} / "
        f"{memory['python_heap_peak_bytes']} byte",
        f"MemAvailable hệ thống trước/sau: {memory['system_mem_available_before_kib']} / "
        f"{memory['system_mem_available_after_kib']} KiB",
        f"RSS theo từng lần lặp (KiB): {rss_samples}",
        "RSS gồm Python và thư viện native của Z3; tracemalloc chỉ theo dõi heap Python. "
        "MemAvailable là RAM toàn hệ thống tại thời điểm đo.",
    ])


def render_trace(spec, row):
    """Giải mã state trong trace Z3, đánh dấu cạnh vi phạm và từ chối dữ liệu đã cũ."""
    name = spec["name"]
    # Hash spec cùng số transition giúp tránh trình bày trace sinh từ phiên bản đặc tả khác.
    if (
        row["function"] != name
        or row["transition_count"] != len(spec["transitions"])
        or row.get("spec_sha256") != spec_fingerprint(spec)
    ):
        raise ValueError(f"{name}: kết quả không khớp đặc tả; hãy chạy lại run_z3_demo.py")

    declared_forbidden = {tuple(edge) for edge in forbidden_edges_for_spec(spec)}
    saved_forbidden = {tuple(edge) for edge in row["forbidden_edges"]}
    if declared_forbidden != saved_forbidden:
        raise ValueError(f"{name}: ràng buộc đã thay đổi; hãy chạy lại run_z3_demo.py")

    safe = row["safe_model"]
    faulty = row["faulty_model"]
    liveness = row["liveness_counterexample"]
    lines = [
        f"## {spec['title']} ({name})",
        f"Bound: {row['bound']} | mô hình đúng: {safe['status'].upper()} | "
        f"mô hình lỗi: {faulty['status'].upper()} | phản ví dụ liveness: {liveness['status'].upper()}",
    ]
    path = faulty.get("path")
    if faulty["status"] != "sat" or not path:
        lines.append("Không có phản ví dụ Safety để hiển thị.")
        return "\n".join(lines)

    states = {state["id"]: state for state in spec["states"]}
    codes = {state["id"]: index for index, state in enumerate(spec["states"])}
    valid_edges = {tuple(edge) for edge in spec["transitions"]}
    faulty_edge = tuple(spec["faulty_transition"])
    initial = next(state["id"] for state in spec["states"] if state.get("initial"))
    depth = faulty["depth"]
    if path[0] != initial or len(path) != depth + 1 or path[-2:] != list(faulty_edge):
        raise ValueError(f"{name}: trace đã lưu không khớp mô hình; hãy chạy lại run_z3_demo.py")

    lines.extend([
        "| Bước | Biến Z3 = mã | State | Nhãn đúng L(s) | Cạnh đi vào | Safety |",
        "|---:|---|---|---|---|---|",
    ])
    for index, state in enumerate(path):
        if state not in states:
            raise ValueError(f"{name}: trace chứa state lạ {state!r}")
        edge_text = "—"
        safety_text = "—"
        if index:
            edge = (path[index - 1], state)
            if edge not in valid_edges and edge != faulty_edge:
                raise ValueError(f"{name}: trace chứa cạnh không được khai báo {edge!r}")
            edge_text = f"{edge[0]} → {edge[1]}"
            safety_text = "VI PHẠM" if edge in declared_forbidden else "Hợp lệ"
        labels = ", ".join(states[state].get("labels", [])) or "—"
        lines.append(
            f"| {index} | `state_{depth}_{index} = {codes[state]}` | `{state}` | "
            f"{labels} | {edge_text} | {safety_text} |"
        )
    lines.append(
        f"Cạnh cuối `{faulty_edge[0]} → {faulty_edge[1]}` là cạnh lỗi được chèn vào mô hình; "
        f"mô hình đúng trả {safe['status'].upper()} nên không có trace vi phạm trong bound."
    )
    return "\n".join(lines)


def main(argv=None):
    """Đọc JSON kết quả, chọn một hoặc mọi chức năng, rồi in bảng trace/RAM."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--feature", default="all", choices=["all", "login", "attendance", "leave", "payroll"])
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args(argv)
    try:
        result = json.loads(args.results.read_text(encoding="utf-8"))
        specs = {spec["name"]: spec for spec in load_specs()}
        rows = {row["function"]: row for row in result["functions"]}
        names = sorted(specs) if args.feature == "all" else [args.feature]
        sections = ["# BMC: trạng thái trong bộ nhớ và RAM", render_memory(result)]
        for name in names:
            sections.append(render_trace(specs[name], rows[name]))
        print("\n\n".join(sections))
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as error:
        parser.exit(1, f"Không thể hiển thị kết quả: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
