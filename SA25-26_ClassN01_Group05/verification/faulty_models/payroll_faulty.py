"""Generated faulty model for payroll; used to check counterexample detection."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from payroll_kripke import build_model as build_safe_model

def build_model():
    model = build_safe_model()
    model.add_transition('PAID', 'DRAFT')
    return model
