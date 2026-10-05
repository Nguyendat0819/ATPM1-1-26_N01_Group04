PROPERTIES = [
    ("L1", "Safety", "AG(!bypass_authentication)", "No reachable state may represent authentication bypass."),
    ("L2", "Liveness", "AF(authenticated)", "From every reachable state, successful authentication remains eventually reachable on every path."),
]
