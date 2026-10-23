"""Generated from verification/specs/attendance.json; edit the spec instead."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure

def build_model():
    model = KripkeStructure()
    model.add_state('READY', ['ready'], True)
    model.add_state('AUTHENTICATED', ['authenticated'], False)
    model.add_state('CHECKIN_VALID', ['valid_checkin'], False)
    model.add_state('CHECKED_IN', ['checked_in'], False)
    model.add_state('CHECKED_OUT', ['checked_out'], False)
    model.add_state('VERIFY_FAILED', ['verify_failed'], False)
    model.add_transition('READY', 'AUTHENTICATED')
    model.add_transition('AUTHENTICATED', 'VERIFY_FAILED')
    model.add_transition('AUTHENTICATED', 'CHECKIN_VALID')
    model.add_transition('CHECKIN_VALID', 'CHECKED_IN')
    model.add_transition('VERIFY_FAILED', 'READY')
    model.add_transition('CHECKED_IN', 'CHECKED_OUT')
    model.add_transition('CHECKED_OUT', 'READY')
    return model
