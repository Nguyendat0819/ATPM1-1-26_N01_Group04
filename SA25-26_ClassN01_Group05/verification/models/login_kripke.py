from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure


def build_model():
    k = KripkeStructure()
    k.add_state("UNAUTHENTICATED", ["unauthenticated", "credentials_not_verified"], True)
    k.add_state("AUTHENTICATING_VALID", ["authenticating", "valid_credentials"])
    k.add_state("AUTHENTICATING_INVALID", ["authenticating", "invalid_credentials"])
    k.add_state("LOGIN_FAILED", ["login_failed"])
    k.add_state("INACTIVE_USER", ["inactive_user"])
    k.add_state("AUTHENTICATED", ["authenticated", "credentials_verified"])
    k.add_state("LOGGED_OUT", ["logged_out", "credentials_not_verified"])
    k.add_transition("UNAUTHENTICATED", "AUTHENTICATING_VALID")
    k.add_transition("UNAUTHENTICATED", "AUTHENTICATING_INVALID")
    k.add_transition("AUTHENTICATING_VALID", "AUTHENTICATED")
    k.add_transition("AUTHENTICATING_INVALID", "LOGIN_FAILED")
    k.add_transition("AUTHENTICATING_INVALID", "INACTIVE_USER")
    k.add_transition("LOGIN_FAILED", "UNAUTHENTICATED")
    k.add_transition("INACTIVE_USER", "UNAUTHENTICATED")
    k.add_transition("AUTHENTICATED", "LOGGED_OUT")
    k.add_transition("LOGGED_OUT", "UNAUTHENTICATED")
    return k
