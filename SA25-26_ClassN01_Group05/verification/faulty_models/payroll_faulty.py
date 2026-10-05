from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from payroll_kripke import build_model as safe

def build_model():
    k = safe()
    k.add_transition("PAID", "DRAFT")
    return k
