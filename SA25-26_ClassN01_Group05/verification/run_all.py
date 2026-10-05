"""Run the complete Kripke + BMC study for the HRM project."""
from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "bmc"))
from bounded_checker import (
    graph_diameter, check_ag_not_edge, check_af_label_from,
    shortest_edge_counterexample, bmc_af_from,
)

MODELS = {
    "login": ("models.login_kripke", "faulty_models.login_faulty", ("UNAUTHENTICATED", "AUTHENTICATED"), "authenticated", ["AUTHENTICATING_VALID"]),
    "attendance": ("models.attendance_kripke", "faulty_models.attendance_faulty", ("AUTHENTICATED", "CHECKED_OUT"), "checked_in", ["CHECKIN_VALID"]),
    "leave": ("models.leave_kripke", "faulty_models.leave_faulty", ("NO_REQUEST", "APPROVED"), None, ["PENDING"]),
    "payroll": ("models.payroll_kripke", "faulty_models.payroll_faulty", ("PAID", "DRAFT"), "draft", ["NOT_CALCULATED"]),
}


def load_builder(module_name):
    return __import__(module_name, fromlist=["build_model"]).build_model


def run_one(name, safe_mod, faulty_mod, forbidden, live_label, live_starts):
    safe = load_builder(safe_mod)()
    faulty = load_builder(faulty_mod)()
    diameter = graph_diameter(safe)
    safety_safe = check_ag_not_edge(safe, forbidden)
    safety_faulty = check_ag_not_edge(faulty, forbidden)
    faulty_cex = shortest_edge_counterexample(faulty, forbidden)
    safe_bmc_cex = None
    from bounded_checker import find_edge_counterexample
    for k in range(diameter + 1):
        safe_bmc_cex = find_edge_counterexample(safe, forbidden, k)
        if safe_bmc_cex is not None:
            break
    if name == "leave":
        # AF(approved OR rejected) from PENDING.
        states = set(safe.reachable_states())
        good = {s for s in states if {"approved", "rejected"} & safe.labels.get(s, set())}
        changed = True
        while changed:
            changed = False
            for s in list(states - good):
                succ = safe.transitions.get(s, set())
                if succ and all(x in good for x in succ):
                    good.add(s)
                    changed = True
        live_ok = set(live_starts).issubset(good)
        live_bmc = None
        from bounded_checker import all_paths
        for p in all_paths(safe, diameter, live_starts):
            if not any({"approved", "rejected"} & safe.labels.get(s, set()) for s in p):
                live_bmc = p
                break
    else:
        live_ok = check_af_label_from(safe, live_label, live_starts)
        live_bmc = bmc_af_from(safe, live_label, live_starts, diameter)
    return {
        "function": name,
        "reachable_states": sorted(safe.reachable_states()),
        "completeness_threshold": diameter,
        "safety_property": "AG(!forbidden_transition)",
        "safe_safety_result": safety_safe,
        "safe_bmc_counterexample_at_threshold": safe_bmc_cex,
        "faulty_safety_result": safety_faulty,
        "faulty_counterexample": faulty_cex,
        "liveness_result": live_ok,
        "liveness_bmc_counterexample": live_bmc,
    }


def main():
    out = []
    for name, args in MODELS.items():
        out.append(run_one(name, *args))
    result_dir = ROOT / "results"
    result_dir.mkdir(exist_ok=True)
    (result_dir / "verification_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== HRM KRIPKE + BMC VERIFICATION ===")
    for r in out:
        print(f"\n[{r['function'].upper()}]")
        print("reachable:", ", ".join(r["reachable_states"]))
        print("completeness threshold:", r["completeness_threshold"])
        print("safety safe-model:", "PASS" if r["safe_safety_result"] else "FAIL")
        print("BMC safe-model at threshold:", "NO COUNTEREXAMPLE" if r["safe_bmc_counterexample_at_threshold"] is None else "COUNTEREXAMPLE FOUND")
        print("safety faulty-model:", "PASS" if r["faulty_safety_result"] else "FAIL")
        print("faulty counterexample:", " -> ".join(r["faulty_counterexample"]) if r["faulty_counterexample"] else "none")
        print("liveness:", "PASS" if r["liveness_result"] else "FAIL")
    print(f"\nSaved: {result_dir / 'verification_results.json'}")


if __name__ == "__main__":
    main()
