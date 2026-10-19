PROPERTIES = [
    ("A1", "Safety", "forall s: R(s, CHECKED_IN) -> s == CHECKIN_VALID and R(s, CHECKED_OUT) -> s == CHECKED_IN", "Check-in chỉ sau xác thực dữ liệu; check-out chỉ sau CHECKED_IN."),
    ("A2", "Liveness", "AF(checked_in)", "Từ CHECKIN_VALID, mọi nhánh cuối cùng đạt CHECKED_IN."),
]
