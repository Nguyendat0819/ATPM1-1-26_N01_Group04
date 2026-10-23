"""Các mệnh đề Safety/Liveness nghiệp vụ duyệt nghỉ phép, dùng làm tài liệu đặc tả."""
PROPERTIES = [
    ("LV1", "Safety", "forall s: R(s, APPROVED) or R(s, REJECTED) -> s == PENDING", "Đơn chỉ được kết thúc bằng APPROVED hoặc REJECTED sau PENDING."),
    ("LV2", "Liveness", "AF(approved or rejected)", "Từ PENDING, mọi nhánh cuối cùng được duyệt hoặc từ chối."),
]
