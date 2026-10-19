from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "bmc")]
from bounded_checker import (
    check_af_labels_from,
    graph_diameter,
    reachable_state_count,
    shortest_forbidden_edge_counterexample,
)
from generate_artifacts import forbidden_edges_for_spec


def run_suite(spec, model):
    safety = spec["properties"]["safety"]
    liveness = spec["properties"]["liveness"]
    bound = reachable_state_count(model)
    counterexample = shortest_forbidden_edge_counterexample(
        model, forbidden_edges_for_spec(spec), bound
    )
    result = {
        "model": spec["name"],
        "reachable": sorted(model.reachable_states()),
        "completeness_bound": bound,
        "graph_diameter": graph_diameter(model),
        "safety_property": safety["id"],
        "safety": counterexample is None,
        "safety_counterexample": counterexample,
        "liveness_property": liveness["id"],
        "liveness": check_af_labels_from(model, liveness["target_labels"], liveness["starts"]),
        "liveness_targets": liveness["target_labels"],
    }
    return result
