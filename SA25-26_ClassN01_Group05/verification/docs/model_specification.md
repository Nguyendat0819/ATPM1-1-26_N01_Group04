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

### Suy ra bound (completeness threshold)

Bound không được chọn theo cảm tính. Chương trình bắt đầu ở state đầu `s0`, duyệt quan hệ chuyển tiếp `R`, rồi lấy `k = |Reach(s0)|` bằng `reachable_states()` trong `bmc/z3_bounded_checker.py`. Bộ kiểm tra đặc tả cũng yêu cầu mọi state đã khai báo đều reachable từ state đầu; vì vậy bốn mô hình hiện tại có `k` như sau:

| Chức năng | Số state reachable `k` | Ý nghĩa khi unroll |
|---|---:|---|
| Login | 8 | Tối đa 8 cạnh để chạm cạnh vi phạm; mỗi truy vấn có tối đa 9 lần xuất hiện state |
| Attendance | 6 | Tối đa 6 cạnh; tối đa 7 lần xuất hiện state |
| Leave | 4 | Tối đa 4 cạnh; tối đa 5 lần xuất hiện state |
| Payroll | 4 | Tối đa 4 cạnh; tối đa 5 lần xuất hiện state |

Với Safety, nếu một cạnh cấm có thể tới được, lấy đường ngắn nhất từ state đầu tới nguồn cạnh đó. Đường ngắn nhất không lặp state, nên có nhiều nhất `k−1` cạnh; thêm cạnh vi phạm thì tổng độ dài nhiều nhất `k`. Vì vậy, Z3 thử lần lượt độ sâu `1..k`. Đây là completeness bound cho mô hình hữu hạn đang xét. Lưu ý `k` đếm số **cạnh chuyển** tối đa trong trace Safety; các biến `s0..sk` là `k+1` lần xuất hiện state.

### Cách chuyển đặc tả thành ràng buộc Z3

Thứ tự state trong JSON được ánh xạ thành mã nguyên `code(s)`. Ở độ sâu `d`, checker tạo `s0..sd` và thêm các ràng buộc sau:

```text
Domain(si) := si thuộc tập mã của các state đã khai báo
Init(s0)   := s0 = code(state đầu)
Step(si,si+1) := OR trên mọi (u,v) thuộc R của
                 (si = code(u) AND si+1 = code(v))
Bad(si,si+1)  := OR trên các cạnh bị cấm của
                 (si = code(u) AND si+1 = code(v))
```

Truy vấn Safety ở một độ sâu `d` là `Init(s0) AND AND_i Domain(si) AND AND_i Step(si,si+1) AND Bad(s(d−1),sd)`. Các bước trước cạnh cuối phải tuân theo transition relation của mô hình; cạnh cuối phải là cạnh vi phạm. Z3 trả `SAT` kèm giá trị các biến state khi tìm thấy trace; `UNSAT` ở mọi độ sâu từ 1 đến `k` nghĩa là không có phản ví dụ trong mô hình và bound đó. `UNKNOWN` (ví dụ hết timeout) là kết quả chưa kết luận, không được diễn giải thành PASS.

`allowed_predecessors` được `forbidden_edges_for_spec()` đổi thành các cặp nguồn–đích không được phép. Ví dụ, Login khai báo `AUTHENTICATED` chỉ có tiền nhiệm `AUTHENTICATING_ACTIVE`; do đó `UNAUTHENTICATED → AUTHENTICATED` là cạnh cấm. Khi thử nghiệm faulty, runner chủ động thêm cạnh này vào `R`; Z3 tìm được phản ví dụ `UNAUTHENTICATED → AUTHENTICATED` (SAT). Với Attendance, `CHECKED_OUT` chỉ được đến từ `CHECKED_IN`; thêm cạnh faulty `AUTHENTICATED → CHECKED_OUT` làm Z3 trả trace `READY → AUTHENTICATED → CHECKED_OUT` (SAT). Mô hình bình thường không chứa các cạnh lỗi nên truy vấn không tìm được phản ví dụ (UNSAT).

Với Liveness `AF(target)`, phản ví dụ là một đường vô hạn bắt đầu tại `starts` nhưng không bao giờ chạm state mang nhãn target. Checker hỏi Z3 liệu có đường dài `k` cạnh mà **mọi** state `s0..sk` đều không thuộc target hay không. Do quan hệ chuyển tiếp của Kripke phải total, một đường như vậy có `k+1` lần xuất hiện state trên đồ thị có `k` state reachable; theo nguyên lý Dirichlet, có state lặp và tạo chu trình tránh target, tức phản ví dụ vô hạn cho `AF`. `UNSAT` ở bound này loại trừ chu trình tránh target trong mô hình. Kiểm tra totality và phép đối chiếu fixed-point `AF` được thực hiện riêng.

### Phạm vi encoding

`formula` trong JSON là công thức mô tả cho người đọc, không được parser CTL/LTL tổng quát. Mã hiện tại thực thi cấu trúc cụ thể từ `transitions`, `allowed_predecessors`/`forbidden_edges`, `starts` và `target_labels`. Xem `bmc/z3_bounded_checker.py` (unroll/constraint), `run_z3_demo.py` (chọn bound và ánh xạ nhãn), và `generate_artifacts.py` (`forbidden_edges_for_spec`) để lần theo từng bước. Kết quả chứng minh trên mô hình đã mã hóa, không tự chứng minh implementation Express hoặc database tương đương mô hình.

## Test case tĩnh và giới hạn

Generator sinh test case phủ từng transition reachable, một ca âm cho ràng buộc Safety và các witness path cho Liveness của từng chức năng. Bộ test xác nhận ca dương chỉ dùng cạnh đã khai báo, ca âm đi qua cạnh bị cấm, và witness kết thúc ở nhãn mục tiêu. Đây là kiểm thử tĩnh trên mô hình, chưa gọi HTTP API. Z3 chạy trên JSON model và không tự chứng minh implementation Express hoặc database tương đương với mô hình.

Chi tiết trạng thái, labels, transition, allowed predecessors và properties đầy đủ nằm trong `specs/login.json`, `specs/attendance.json`, `specs/leave.json`, `specs/payroll.json`.
