"""Chạy BMC-Z3 cho bốn mô hình HRM và ghi kết quả cùng số đo bộ nhớ tiến trình."""
import argparse
import gc
import json
import platform
import resource
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

from z3 import get_version_string

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "bmc"))
from z3_bounded_checker import (
    find_counterexample,
    find_liveness_counterexample,
    reachable_states,
)

sys.path.insert(0, str(ROOT))
from generate_artifacts import forbidden_edges_for_spec, generate_artifacts, spec_fingerprint


def read_meminfo_kib(field):
    """Đọc một trường từ /proc/meminfo theo KiB; trả None nếu hệ điều hành không hỗ trợ."""
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith(field + ":"):
                return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return None


def read_rss_kib():
    """Đọc RSS hiện tại của chính tiến trình Python để quan sát RAM resident."""
    try:
        for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return None


def max_rss_kib():
    """Lấy RSS đỉnh từ resource, quy đổi đơn vị phù hợp theo hệ điều hành."""
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value / 1024) if platform.system() == "Darwin" else int(value)


def run_case(spec, faulty=False, timeout_ms=5000):
    """Tạo dữ liệu transition và gọi Z3 tìm cạnh Safety cấm; tùy chọn chèn lỗi có chủ ý."""
    states = [state["id"] for state in spec["states"]]
    transitions = [tuple(edge) for edge in spec["transitions"]]
    if faulty:
        transitions.append(tuple(spec["faulty_transition"]))
    initial = next(state["id"] for state in spec["states"] if state.get("initial"))
    safety = spec["properties"]["safety"]
    forbidden_edges = forbidden_edges_for_spec(spec)
    bound = len(reachable_states(initial, transitions))
    return find_counterexample(states, transitions, initial, forbidden_edges, bound, timeout_ms)


def run_liveness_case(spec, timeout_ms=5000):
    """Chuyển nhãn target thành state ID rồi tìm đường tránh target bằng Z3."""
    states = [state["id"] for state in spec["states"]]
    transitions = [tuple(edge) for edge in spec["transitions"]]
    initial = next(state["id"] for state in spec["states"] if state.get("initial"))
    reachable = reachable_states(initial, transitions)
    liveness = spec["properties"]["liveness"]
    target_labels = set(liveness["target_labels"])
    target_states = [
        state["id"] for state in spec["states"]
        if target_labels.intersection(state.get("labels", []))
    ]
    return find_liveness_counterexample(
        states,
        transitions,
        liveness["starts"],
        target_states,
        len(reachable),
        timeout_ms,
    )


def main():
    """Lặp truy vấn, đo thời gian/RAM/CPU, ghi JSON-log và trả mã thoát theo kết quả."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeat", type=int, default=20, help="repetitions for the RAM smoke test")
    parser.add_argument("--timeout-ms", type=int, default=5000, help="timeout per Z3 query")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results", help="directory for JSON and log output")
    args = parser.parse_args()
    if args.repeat < 1 or args.timeout_ms < 1:
        parser.error("--repeat and --timeout-ms must be positive")

    specs, all_cases = generate_artifacts()
    selected = specs
    demo_cases = all_cases
    generated_cases_path = ROOT / "generated" / "z3_demo_test_cases.json"
    generated_cases_path.write_text(json.dumps(demo_cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ram_before = read_meminfo_kib("MemAvailable")
    rss_before = read_rss_kib()
    cpu_before = resource.getrusage(resource.RUSAGE_SELF)
    # tracemalloc chỉ theo dõi heap Python; RSS bên dưới còn bao gồm phần native của Z3.
    tracemalloc.start()
    started = time.perf_counter()
    final_rows = []
    memory_samples = []
    all_pass = True

    # Lặp đủ số vòng để quan sát biến động RSS; mỗi vòng vẫn kiểm tra lại cả bốn mô hình.
    for _ in range(args.repeat):
        final_rows = []
        for spec in selected:
            safe_result = run_case(spec, faulty=False, timeout_ms=args.timeout_ms)
            faulty_result = run_case(spec, faulty=True, timeout_ms=args.timeout_ms)
            liveness_result = run_liveness_case(spec, timeout_ms=args.timeout_ms)
            # Không có phản ví dụ ở model đúng phải UNSAT; cạnh chèn lỗi phải SAT.
            safe_pass = safe_result["status"] == "unsat"
            faulty_detected = faulty_result["status"] == "sat"
            liveness_pass = liveness_result["status"] == "unsat"
            all_pass = all_pass and safe_pass and faulty_detected and liveness_pass
            final_rows.append({
                "function": spec["name"],
                "title": spec["title"],
                "spec_sha256": spec_fingerprint(spec),
                "reachable_states": len(reachable_states(
                    next(state["id"] for state in spec["states"] if state.get("initial")),
                    [tuple(edge) for edge in spec["transitions"]],
                )),
                "transition_count": len(spec["transitions"]),
                "forbidden_edges": forbidden_edges_for_spec(spec),
                "bound": safe_result.get("bound", safe_result.get("depth")),
                "safe_model": safe_result,
                "faulty_model": faulty_result,
                "liveness_counterexample": liveness_result,
                "pass": safe_pass and faulty_detected and liveness_pass,
            })
        gc.collect()
        heap_current_sample, heap_peak_sample = tracemalloc.get_traced_memory()
        memory_samples.append({
            "iteration": len(memory_samples) + 1,
            "process_rss_kib": read_rss_kib(),
            "python_heap_current_bytes": heap_current_sample,
            "python_heap_peak_bytes": heap_peak_sample,
        })

    elapsed = time.perf_counter() - started
    heap_current, heap_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cpu_after = resource.getrusage(resource.RUSAGE_SELF)
    ram_after = read_meminfo_kib("MemAvailable")
    rss_after = read_rss_kib()
    sampled_rss = [sample["process_rss_kib"] for sample in memory_samples if sample["process_rss_kib"] is not None]

    memory = {
        "repeat_count": args.repeat,
        "process_rss_before_kib": rss_before,
        "process_rss_after_kib": rss_after,
        "process_peak_rss_kib": max([max_rss_kib(), *sampled_rss]),
        "python_heap_current_bytes": heap_current,
        "python_heap_peak_bytes": heap_peak,
        "system_mem_available_before_kib": ram_before,
        "system_mem_available_after_kib": ram_after,
        "elapsed_seconds": round(elapsed, 6),
        "cpu_user_seconds": round(cpu_after.ru_utime - cpu_before.ru_utime, 6),
        "cpu_system_seconds": round(cpu_after.ru_stime - cpu_before.ru_stime, 6),
    }
    output = {
        "status": "PASS" if all_pass else "FAIL",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "z3_version": get_version_string(),
        "bmc_method": "bounded transition unrolling; query whether any forbidden edge is traversed",
        "functions": final_rows,
        "generated_static_model_test_cases": len(demo_cases),
        "memory_measurement": memory,
        "memory_samples": memory_samples,
    }
    results_path = args.results_dir / "z3_bmc_memory.json"
    log_path = args.results_dir / "z3_bmc_memory.log"
    args.results_dir.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "=== HRM Z3 BMC + MEMORY SMOKE TEST ===",
        f"Z3: {output['z3_version']} | functions: {len(selected)} | repetitions: {args.repeat} | generated test cases: {len(demo_cases)}",
    ]
    for row in final_rows:
        safe = row["safe_model"]
        faulty = row["faulty_model"]
        faulty_path = " -> ".join(faulty.get("path") or [])
        lines.append(
            f"{row['function']}: states={row['reachable_states']}, transitions={row['transition_count']}, "
            f"bound={row['bound']}, safe={safe['status'].upper()}, faulty={faulty['status'].upper()}, "
            f"liveness-counterexample={row['liveness_counterexample']['status'].upper()}, "
            f"result={'PASS' if row['pass'] else 'FAIL'}"
        )
        lines.append(f"  faulty counterexample: {faulty_path or 'none'}")
    lines.extend([
        f"RAM: RSS before/after/peak={rss_before}/{rss_after}/{memory['process_peak_rss_kib']} KiB; "
        f"Python heap current/peak={heap_current}/{heap_peak} bytes",
        f"System MemAvailable before/after={ram_before}/{ram_after} KiB",
        f"RSS samples per repeat: {[sample['process_rss_kib'] for sample in memory_samples]} KiB",
        f"Time: {elapsed:.6f}s | CPU user/system={memory['cpu_user_seconds']}/{memory['cpu_system_seconds']}s",
        f"Overall: {output['status']}",
        f"Results: {results_path}",
        f"Generated cases: {generated_cases_path}",
    ])
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(log_path.read_text(encoding="utf-8"), end="")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
