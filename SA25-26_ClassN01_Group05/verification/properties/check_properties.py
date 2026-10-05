from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bmc"))
from bounded_checker import check_ag_not_label, check_af_label, check_ef_label, graph_diameter, shortest_bad_path


def run_suite(name, model, safety_label, liveness_label):
    result = {
        "model": name,
        "reachable": sorted(model.reachable_states()),
        "diameter": graph_diameter(model),
        "safety": check_ag_not_label(model, safety_label),
        "safety_counterexample": shortest_bad_path(model, lambda s: safety_label in model.labels.get(s, set())),
        "liveness": check_af_label(model, liveness_label),
        "liveness_target": liveness_label,
        "existential_target": check_ef_label(model, liveness_label),
    }
    return result
