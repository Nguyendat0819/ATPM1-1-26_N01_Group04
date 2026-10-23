"""Các mệnh đề Safety/Liveness nghiệp vụ đăng nhập, dùng làm tài liệu đặc tả."""
PROPERTIES = [
    ("L1", "Safety", "forall s: R(s, AUTHENTICATED) -> s == AUTHENTICATING_ACTIVE", "Chỉ thông tin hợp lệ của tài khoản đang hoạt động mới dẫn tới đăng nhập thành công."),
    ("L2", "Liveness", "AF(authenticated)", "Từ AUTHENTICATING_ACTIVE, mọi nhánh cuối cùng đạt AUTHENTICATED."),
]
