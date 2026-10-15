# Đặc tả trạng thái và ràng buộc HRM

## Ký hiệu

Với Kripke structure `M = (S, S0, R, L)`, `S` là tập trạng thái, `S0` là trạng thái khởi đầu, `R` là quan hệ chuyển tiếp, `L` gắn nhãn proposition vào trạng thái. Safety dùng CTL `AG`: trên mọi đường đi, ở mọi trạng thái, chuyển tiếp cấm không xảy ra. Liveness dùng `AF`: trên mọi đường đi từ các trạng thái tiền đề, cuối cùng phải đạt một nhãn mục tiêu.

## Đặc tả theo chức năng

| Chức năng | Trạng thái | Chuyển tiếp đúng | Safety | Liveness |
|---|---|---|---|---|
| Đăng nhập | `UNAUTHENTICATED`, `AUTHENTICATING_VALID`, `AUTHENTICATING_INVALID`, `LOGIN_FAILED`, `INACTIVE_USER`, `AUTHENTICATED`, `LOGGED_OUT` | Đăng nhập hợp lệ → `AUTHENTICATED`; sai hoặc tài khoản chưa kích hoạt → lỗi; logout → chưa xác thực | Không có `UNAUTHENTICATED → AUTHENTICATED` | `AUTHENTICATING_VALID → AF(authenticated)` |
| Chấm công | `READY`, `AUTHENTICATED`, `CHECKIN_VALID`, `CHECKED_IN`, `CHECKED_OUT`, `VERIFY_FAILED` | Xác thực → xác nhận check-in → check-in → check-out; lỗi xác minh quay về sẵn sàng | Không có `AUTHENTICATED → CHECKED_OUT` | `CHECKIN_VALID → AF(checked_in)` |
| Nghỉ phép | `NO_REQUEST`, `PENDING`, `APPROVED`, `REJECTED` | Tạo đơn → `PENDING` → duyệt hoặc từ chối → kết thúc vòng đời | Không có `NO_REQUEST → APPROVED` | `PENDING → AF(approved OR rejected)` |
| Tính lương | `NOT_CALCULATED`, `CALCULATING`, `DRAFT`, `PAID` | Tính → `DRAFT` → `PAID`; đã trả lương giữ nguyên `PAID` | Không có `PAID → DRAFT` | `NOT_CALCULATED → AF(draft)` |

## Ràng buộc chung

1. Mỗi spec có đúng một trạng thái ban đầu.
2. Mọi transition phải trỏ tới các state đã khai báo; ID state và transition không trùng.
3. Mô hình đúng không chứa transition safety bị cấm.
4. Mỗi mô hình lỗi được sinh bằng cách thêm đúng transition bị cấm để xác nhận checker phát hiện được.
5. Các điểm bắt đầu của liveness phải đạt được từ trạng thái ban đầu và cuối cùng phải chạm một nhãn mục tiêu trên mọi đường đi.
6. Test case sinh theo transition coverage: mỗi transition reachable có ít nhất một đường đi bắt đầu từ `S0` đi qua transition đó.

Các state, label, transition và property đầy đủ nằm trong `specs/*.json`; file JSON là nguồn sự thật để sinh model Python, model lỗi và test case.
