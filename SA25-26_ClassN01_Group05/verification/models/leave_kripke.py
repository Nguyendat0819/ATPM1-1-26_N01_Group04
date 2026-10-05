from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure


def build_model():
    k = KripkeStructure()
    k.add_state("NO_REQUEST", ["no_request"], True)
    k.add_state("PENDING", ["pending", "valid_leave_request"])
    k.add_state("APPROVED", ["approved"])
    k.add_state("REJECTED", ["rejected"])
    k.add_transition("NO_REQUEST", "PENDING")
    k.add_transition("PENDING", "APPROVED")
    k.add_transition("PENDING", "REJECTED")
    k.add_transition("APPROVED", "NO_REQUEST")
    k.add_transition("REJECTED", "NO_REQUEST")
    return k
