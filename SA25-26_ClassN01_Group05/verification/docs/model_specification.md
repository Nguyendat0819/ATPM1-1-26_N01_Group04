# Đặc tả trạng thái và ràng buộc HRM

## Mô hình Kripke

Với `M = (S, S0, R, L)`, `S` là tập trạng thái, `S0` là trạng thái đầu, `R` là quan hệ chuyển tiếp, `L` là nhãn mệnh đề trên mỗi trạng thái. JSON trong `specs/` là nguồn sự thật để sinh mô hình Python và test case phủ chuyển tiếp.

Trong JSON, `allowed_predecessors` quy định ràng buộc trên quan hệ chuyển tiếp: mỗi trạng thái đích chỉ được đi vào từ các trạng thái nguồn liệt kê; mọi nguồn khác sinh thành cạnh cấm. `R(s,t)` nghĩa là mô hình có cạnh `s → t`; `formula` ghi mệnh đề trên các cạnh vào. Checker kiểm tra bằng cách liệt kê cạnh cấm, không phân tích cú pháp công thức CTL tổng quát. Mệnh đề Liveness dùng `AF` và được kiểm riêng.

## Bốn luồng

| Chức năng | Trạng thái chính | Luồng hợp lệ | Ràng buộc Safety | Liveness |
|---|---|---|---|---|
| Đăng nhập | `UNAUTHENTICATED`, `AUTHENTICATING_ACTIVE`, `AUTHENTICATING_INVALID`, `AUTHENTICATING_INACTIVE`, `LOGIN_FAILED`, `INACTIVE_USER`, `AUTHENTICATED`, `LOGGED_OUT` | Thông tin hợp lệ + tài khoản hoạt động → `AUTHENTICATED`; sai mật khẩu → `LOGIN_FAILED`; tài khoản chưa hoạt động → `INACTIVE_USER`; logout → `UNAUTHENTICATED` | `AUTHENTICATED` chỉ được tới từ `AUTHENTICATING_ACTIVE` | Từ `AUTHENTICATING_ACTIVE`, cuối cùng đạt `AUTHENTICATED` |
| Chấm công | `READY`, `AUTHENTICATED`, `CHECKIN_VALID`, `CHECKED_IN`, `CHECKED_OUT`, `VERIFY_FAILED` | Xác thực → xác minh dữ liệu check-in → `CHECKED_IN` → `CHECKED_OUT` | `CHECKED_IN` chỉ tới từ `CHECKIN_VALID`; `CHECKED_OUT` chỉ tới từ `CHECKED_IN` | Từ `CHECKIN_VALID`, cuối cùng đạt `CHECKED_IN` |
| Nghỉ phép | `NO_REQUEST`, `PENDING`, `APPROVED`, `REJECTED` | Tạo đơn → `PENDING` → `APPROVED` hoặc `REJECTED` | `APPROVED` và `REJECTED` chỉ được tới từ `PENDING` | Từ `PENDING`, cuối cùng đạt một trong hai trạng thái kết quả |
| Tính lương | `NOT_CALCULATED`, `CALCULATING`, `DRAFT`, `PAID` | `NOT_CALCULATED` → `CALCULATING` → `DRAFT` → `PAID`; `PAID` có thể giữ nguyên | Các trạng thái chỉ được tới theo thứ tự hợp lệ; `PAID` không quay lại `DRAFT` | Từ `NOT_CALCULATED`, cuối cùng đạt `DRAFT` |

Các cạnh quay về `NO_REQUEST` sau trạng thái kết thúc của nghỉ phép mô tả chu kỳ của các đơn tiếp theo. Chúng không có nghĩa một đơn đã xử lý đổi ngược trạng thái.

## Ánh xạ mô hình với mã HRM

| Chức năng | Mã nguồn được trừu tượng hóa |
|---|---|
| Đăng nhập | `auth_service/routes/auth.js` |
| Chấm công | `attendance_service/routes/attendance.js` |
| Nghỉ phép | `leave_service/routes/leaves.js` |
| Tính lương | `salary_service/routes/payroll.js` |

Đường dẫn mã nguồn được lưu trong từng JSON đặc tả và được đưa vào test case sinh ra để truy vết từ kịch bản về route nghiệp vụ.

## BMC-Z3 cho bốn chức năng

Với bound `k`, Z3 tạo các biến `state_0 ... state_k`, ràng buộc `state_0` là trạng thái đầu, mỗi cặp kế tiếp thuộc quan hệ chuyển tiếp, rồi hỏi có trace nào đi qua cạnh cấm không.

- Login, Attendance, Leave và Payroll đều được unroll bằng Z3.
- Mô hình đúng trả `UNSAT` tới bound bằng số trạng thái reachable; mô hình lỗi thêm cạnh vi phạm và trả `SAT` kèm trace.
- Safety trên graph hữu hạn có bound hoàn chỉnh cho cạnh cấm: một đường tới nguồn cạnh có thể rút gọn thành đường không lặp, sau đó đi cạnh vi phạm.
- Liveness được kiểm bằng truy vấn Z3 tìm đường dài `|S_reachable|` tránh mọi target. Các đặc tả bảo đảm transition relation total; do đó đường tránh target dài hơn số state phải lặp state và tạo chu trình vô hạn. Checker đồ thị fixed point `AF` trong Python cũng được chạy như phép đối chiếu.

## Test case tĩnh và giới hạn

Generator sinh test case phủ từng transition reachable, một ca âm cho ràng buộc Safety và các witness path cho Liveness của từng chức năng. Bộ test xác nhận ca dương chỉ dùng cạnh đã khai báo, ca âm đi qua cạnh bị cấm, và witness kết thúc ở nhãn mục tiêu. Đây là kiểm thử tĩnh trên mô hình, chưa gọi HTTP API. Z3 chạy trên JSON model và không tự chứng minh implementation Express hoặc database tương đương với mô hình.

Chi tiết trạng thái, labels, transition, allowed predecessors và properties đầy đủ nằm trong `specs/login.json`, `specs/attendance.json`, `specs/leave.json`, `specs/payroll.json`.
