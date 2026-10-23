"""Generated from verification/specs/leave.json; edit the spec instead."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure

def build_model():
    model = KripkeStructure()
    model.add_state('NO_REQUEST', ['no_request'], True)
    model.add_state('PENDING', ['pending', 'valid_leave_request'], False)
    model.add_state('APPROVED', ['approved'], False)
    model.add_state('REJECTED', ['rejected'], False)
    model.add_transition('NO_REQUEST', 'PENDING')
    model.add_transition('PENDING', 'APPROVED')
    model.add_transition('PENDING', 'REJECTED')
    model.add_transition('APPROVED', 'NO_REQUEST')
    model.add_transition('REJECTED', 'NO_REQUEST')
    return model
