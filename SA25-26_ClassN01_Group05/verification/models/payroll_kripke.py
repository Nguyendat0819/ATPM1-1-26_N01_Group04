from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure


def build_model():
    k = KripkeStructure()
    k.add_state("NOT_CALCULATED", ["not_calculated", "valid_payroll_input"], True)
    k.add_state("CALCULATING", ["calculating"])
    k.add_state("DRAFT", ["draft", "payroll_ready"])
    k.add_state("PAID", ["paid"])
    k.add_transition("NOT_CALCULATED", "CALCULATING")
    k.add_transition("CALCULATING", "DRAFT")
    k.add_transition("DRAFT", "PAID")
    k.add_transition("PAID", "PAID")
    return k
