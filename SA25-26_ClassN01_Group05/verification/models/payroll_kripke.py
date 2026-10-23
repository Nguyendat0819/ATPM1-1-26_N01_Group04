"""Generated from verification/specs/payroll.json; edit the spec instead."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure

def build_model():
    model = KripkeStructure()
    model.add_state('NOT_CALCULATED', ['not_calculated', 'valid_payroll_input'], True)
    model.add_state('CALCULATING', ['calculating'], False)
    model.add_state('DRAFT', ['draft', 'payroll_ready'], False)
    model.add_state('PAID', ['paid'], False)
    model.add_transition('NOT_CALCULATED', 'CALCULATING')
    model.add_transition('CALCULATING', 'DRAFT')
    model.add_transition('DRAFT', 'PAID')
    model.add_transition('PAID', 'PAID')
    return model
