"""Adapter that reuses softsec-toolkit/ch1_models/kripke.py."""
from pathlib import Path
import importlib.util
import os


def load_kripke_class():
    candidates = []
    env = os.environ.get("SOFTSEC_TOOLKIT")
    if env:
        candidates.append(Path(env) / "ch1_models" / "kripke.py")
    here = Path(__file__).resolve()
    candidates += [
        here.parents[3] / "softsec-toolkit" / "ch1_models" / "kripke.py",
        here.parents[4] / "softsec-toolkit" / "ch1_models" / "kripke.py",
    ]
    for p in candidates:
        if p.exists():
            spec = importlib.util.spec_from_file_location("softsec_toolkit_kripke", p)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            return mod.KripkeStructure
    raise FileNotFoundError(
        "Khong tim thay softsec-toolkit/ch1_models/kripke.py. "
        "Hay dat bien moi truong SOFTSEC_TOOLKIT tro toi thu muc softsec-toolkit."
    )


KripkeStructure = load_kripke_class()
