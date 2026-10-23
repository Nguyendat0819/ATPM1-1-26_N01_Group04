"""Các mệnh đề Safety/Liveness nghiệp vụ tính và thanh toán lương."""
PROPERTIES = [
    ("P1", "Safety", "forall s: R(s, CALCULATING) -> s == NOT_CALCULATED and R(s, DRAFT) -> s == CALCULATING and R(s, PAID) -> s in {DRAFT, PAID}", "Các trạng thái tính lương chỉ được đi theo thứ tự hợp lệ; PAID không quay về DRAFT."),
    ("P2", "Liveness", "AF(draft)", "Từ NOT_CALCULATED, mọi nhánh cuối cùng đạt DRAFT."),
]
