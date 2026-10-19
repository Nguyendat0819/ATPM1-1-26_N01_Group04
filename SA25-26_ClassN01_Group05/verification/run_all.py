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
    shortest_forbidden_edge_counterexample,
)
from generate_artifacts import forbidden_edges_for_spec, generate_artifacts


def load_builder(module_name):
    module = importlib.import_module(module_name)
    return module.build_model


def run_one(spec, case_counts):
    name = spec["name"]
    safe = load_builder(f"{name}_kripke")()
    faulty = load_builder(f"{name}_faulty")()
    safety = spec["properties"]["safety"]
    forbidden_edges = forbidden_edges_for_spec(spec)
    state_count = reachable_state_count(safe)
    safety_bound = state_count
    safe_counterexample = shortest_forbidden_edge_counterexample(safe, forbidden_edges, safety_bound)
    faulty_counterexample = shortest_forbidden_edge_counterexample(faulty, forbidden_edges, safety_bound)
    liveness = spec["properties"]["liveness"]
    liveness_result = check_af_labels_from(safe, liveness["target_labels"], liveness["starts"])
    transitions = sum(
        len(targets) for state, targets in safe.transitions.items()
        if state in safe.reachable_states()
    )
    transition_cases = case_counts["transition"]
    covered_transitions = {
        tuple(case["transition"])
        for case in case_counts["cases"]
        if case["coverage"] == "transition"
    }
    return {
        "function": name,
        "title": spec["title"],
        "states": sorted(safe.reachable_states()),
        "reachable_state_count": state_count,
        "transition_count": transitions,
        "graph_diameter": graph_diameter(safe),
        "safety": {
            "id": safety["id"],
            "formula": safety["formula"],
            "forbidden_edges_checked": forbidden_edges,
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
        "generated_test_cases": len(case_counts["cases"]),
        "generated_transition_test_cases": len(transition_cases),
        "generated_safety_test_cases": sum(case["coverage"] == "safety_constraint" for case in case_counts["cases"]),
        "generated_liveness_test_cases": sum(case["coverage"] == "liveness_witness" for case in case_counts["cases"]),
        "transition_coverage_percent": round(100 * len(covered_transitions) / transitions, 2) if transitions else 0.0,
    }


def main():
    specs, cases = generate_artifacts()
    case_counts = {
        spec["name"]: {
            "cases": [case for case in cases if case["feature"] == spec["title"]],
            "transition": [
                case for case in cases
                if case["feature"] == spec["title"] and case["coverage"] == "transition"
            ],
        }
        for spec in specs
    }
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
        f"Functions: {len(results)} | generated static cases: {len(cases)}",
    ]
    for row in results:
        safety = row["safety"]
        liveness = row["liveness"]
        faulty_result = safety["faulty_model_counterexample"]
        faulty_path = " -> ".join(faulty_result["path"] if faulty_result else [])
        faulty_edge = " -> ".join(faulty_result["edge"] if faulty_result else [])
        lines.append(
            f"{row['function']}: states={row['reachable_state_count']}, "
            f"transitions={row['transition_count']}, cases={row['generated_test_cases']} "
            f"(transition={row['generated_transition_test_cases']}, safety={row['generated_safety_test_cases']}, "
            f"liveness={row['generated_liveness_test_cases']}), "
            f"safe={'PASS' if safety['safe_model_pass'] else 'FAIL'}, "
            f"faulty={'DETECTED' if safety['faulty_model_detected'] else 'MISSED'}, "
            f"liveness={'PASS' if liveness['pass'] else 'FAIL'}"
        )
        lines.append(f"  faulty counterexample: {faulty_path} (violating edge: {faulty_edge})")
    lines.extend([f"Overall: {output['status']}", f"Results: {result_path}"])
    run_log = "\n".join(lines) + "\n"
    (ROOT / "results" / "run.log").write_text(run_log, encoding="utf-8")
    print(run_log, end="")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
