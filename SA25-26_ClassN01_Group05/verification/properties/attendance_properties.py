PROPERTIES = [
    ("A1", "Safety", "AG(!checkout_without_checkin)", "An employee cannot reach CHECKED_OUT before CHECKED_IN."),
    ("A2", "Liveness", "AF(checked_in)", "From each reachable pre-check-in state, every path eventually reaches CHECKED_IN."),
]
