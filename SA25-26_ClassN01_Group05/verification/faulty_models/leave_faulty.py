from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from leave_kripke import build_model as safe

def build_model():
    k = safe()
    k.add_transition("NO_REQUEST", "APPROVED")
    return k
