from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure


def build_model():
    k = KripkeStructure()
    k.add_state("READY", ["ready"], True)
    k.add_state("AUTHENTICATED", ["authenticated"])
    k.add_state("CHECKIN_VALID", ["valid_checkin"])
    k.add_state("CHECKED_IN", ["checked_in"])
    k.add_state("CHECKED_OUT", ["checked_out"])
    k.add_state("VERIFY_FAILED", ["verify_failed"])
    k.add_transition("READY", "AUTHENTICATED")
    k.add_transition("AUTHENTICATED", "VERIFY_FAILED")
    k.add_transition("AUTHENTICATED", "CHECKIN_VALID")
    k.add_transition("CHECKIN_VALID", "CHECKED_IN")
    k.add_transition("VERIFY_FAILED", "READY")
    k.add_transition("CHECKED_IN", "CHECKED_OUT")
    k.add_transition("CHECKED_OUT", "READY")
    return k
