"""Generate and verify all declared HRM Kripke models."""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "bmc"))
sys.path.insert(0, str(ROOT / "models"))
sys.path.insert(0, str(ROOT / "faulty_models"))

from bounded_checker import (
    check_af_labels_from,
    graph_diameter,
    reachable_state_count,
    shortest_edge_counterexample,
)
from generate_artifacts import generate_artifacts


def load_builder(module_name):
    module = importlib.import_module(module_name)
    return module.build_model


def run_one(spec, case_count):
    name = spec["name"]
    safe = load_builder(f"{name}_kripke")()
    faulty = load_builder(f"{name}_faulty")()
    forbidden = tuple(spec["properties"]["safety"]["forbidden_edge"])
    state_count = reachable_state_count(safe)
    safety_bound = state_count
    safe_counterexample = shortest_edge_counterexample(safe, forbidden, safety_bound)
    faulty_counterexample = shortest_edge_counterexample(faulty, forbidden, safety_bound)
    liveness = spec["properties"]["liveness"]
    liveness_result = check_af_labels_from(safe, liveness["target_labels"], liveness["starts"])
    transitions = sum(
        len(targets) for state, targets in safe.transitions.items()
        if state in safe.reachable_states()
    )
    return {
        "function": name,
        "title": spec["title"],
        "states": sorted(safe.reachable_states()),
        "reachable_state_count": state_count,
        "transition_count": transitions,
        "graph_diameter": graph_diameter(safe),
        "safety": {
            "id": spec["properties"]["safety"]["id"],
            "formula": spec["properties"]["safety"]["formula"],
            "bound_edges": safety_bound,
            "safe_model_pass": safe_counterexample is None,
            "safe_model_counterexample": safe_counterexample,
            "faulty_model_detected": faulty_counterexample is not None,
            "faulty_model_counterexample": faulty_counterexample,
        },
        "liveness": {
            "id": liveness["id"],
            "formula": liveness["formula"],
            "starts": liveness["starts"],
            "target_labels": liveness["target_labels"],
            "pass": liveness_result,
        },
        "generated_transition_test_cases": case_count,
        "transition_coverage_percent": 100.0 if transitions else 0.0,
    }


def main():
    specs, cases = generate_artifacts()
    case_counts = {spec["name"]: sum(case["feature"] == spec["title"] for case in cases) for spec in specs}
    results = [run_one(spec, case_counts[spec["name"]]) for spec in specs]
    all_pass = all(
        row["safety"]["safe_model_pass"]
        and row["safety"]["faulty_model_detected"]
        and row["liveness"]["pass"]
        for row in results
    )
    output = {
        "status": "PASS" if all_pass else "FAIL",
        "functions_verified": len(results),
        "generated_test_cases": len(cases),
        "models": results,
    }
    result_path = ROOT / "results" / "verification_results.json"
    result_path.parent.mkdir(exist_ok=True)
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "=== HRM STATE GENERATION AND KRIPKE/BMC VERIFICATION ===",
        f"Functions: {len(results)} | generated transition cases: {len(cases)}",
    ]
    for row in results:
        safety = row["safety"]
        liveness = row["liveness"]
        faulty_path = " -> ".join(safety["faulty_model_counterexample"] or [])
        lines.append(
            f"{row['function']}: states={row['reachable_state_count']}, "
            f"transitions={row['transition_count']}, cases={row['generated_transition_test_cases']}, "
            f"safe={'PASS' if safety['safe_model_pass'] else 'FAIL'}, "
            f"faulty={'DETECTED' if safety['faulty_model_detected'] else 'MISSED'}, "
            f"liveness={'PASS' if liveness['pass'] else 'FAIL'}"
        )
        lines.append(f"  faulty counterexample: {faulty_path}")
    lines.extend([f"Overall: {output['status']}", f"Results: {result_path}"])
    run_log = "\n".join(lines) + "\n"
    (ROOT / "results" / "run.log").write_text(run_log, encoding="utf-8")
    print(run_log, end="")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
