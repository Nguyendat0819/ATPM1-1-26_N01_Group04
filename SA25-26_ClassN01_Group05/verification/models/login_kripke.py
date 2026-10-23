"""Generated from verification/specs/login.json; edit the spec instead."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kripke_adapter import KripkeStructure

def build_model():
    model = KripkeStructure()
    model.add_state('UNAUTHENTICATED', ['unauthenticated', 'credentials_not_verified'], True)
    model.add_state('AUTHENTICATING_ACTIVE', ['authenticating', 'valid_credentials', 'active_user'], False)
    model.add_state('AUTHENTICATING_INVALID', ['authenticating', 'invalid_credentials'], False)
    model.add_state('AUTHENTICATING_INACTIVE', ['authenticating', 'valid_credentials', 'inactive_user'], False)
    model.add_state('LOGIN_FAILED', ['login_failed'], False)
    model.add_state('INACTIVE_USER', ['inactive_user'], False)
    model.add_state('AUTHENTICATED', ['authenticated', 'credentials_verified'], False)
    model.add_state('LOGGED_OUT', ['logged_out', 'credentials_not_verified'], False)
    model.add_transition('UNAUTHENTICATED', 'AUTHENTICATING_ACTIVE')
    model.add_transition('UNAUTHENTICATED', 'AUTHENTICATING_INVALID')
    model.add_transition('UNAUTHENTICATED', 'AUTHENTICATING_INACTIVE')
    model.add_transition('AUTHENTICATING_ACTIVE', 'AUTHENTICATED')
    model.add_transition('AUTHENTICATING_INVALID', 'LOGIN_FAILED')
    model.add_transition('AUTHENTICATING_INACTIVE', 'INACTIVE_USER')
    model.add_transition('LOGIN_FAILED', 'UNAUTHENTICATED')
    model.add_transition('INACTIVE_USER', 'UNAUTHENTICATED')
    model.add_transition('AUTHENTICATED', 'LOGGED_OUT')
    model.add_transition('LOGGED_OUT', 'UNAUTHENTICATED')
    return model
