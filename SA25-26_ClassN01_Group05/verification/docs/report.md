# BÀI TẬP LỚN AN TOÀN PHẦN MỀM
## Mô hình hóa và kiểm chứng hình thức với mô hình Kripke trên hệ thống quản lý nhân sự

**Hệ thống mục tiêu:** HRM microservice của nhóm 05  
**Chức năng phân tích:** Xác thực đăng nhập, chấm công thông minh, quản lý nghỉ phép, tính lương  
**Kỹ thuật:** Kripke Structure + CTL-style Safety/Liveness + Bounded Model Checking (BMC)

---

## 1. Mục tiêu và phạm vi

Đề tài áp dụng mô hình Kripke và kiểm chứng có giới hạn lên bốn luồng nghiệp vụ quan trọng của hệ thống HRM. Phạm vi được giới hạn ở **logic trạng thái** của bốn chức năng thay vì mô hình hóa toàn bộ frontend, database, Redis, gateway, monitoring và container infrastructure.

Cách giới hạn này phù hợp với yêu cầu của đề tài: một chương trình/module có phạm vi vừa phải cần được phân tích sâu, có mô hình, thuộc tính, kết quả chạy và bằng chứng cụ thể.

### Hai phần của môn được áp dụng

- **Chương 1:** Kripke Structure.
- **Chương 3:** SAT/SMT/BMC; phần BMC của dự án được xây dựng theo cùng ý tưởng bounded transition relation trong `ch3_verify/03_bmc_manual.py`.

---

## 2. Hệ thống HRM thực tế được ánh xạ vào mô hình

### 2.1 Login

Mã nguồn thực tế nằm tại:

`auth_service/routes/auth.js`

Luồng chính trong mã gồm kiểm tra username/password, kiểm tra trạng thái `ACTIVE`, tạo JWT và lưu session Redis. Vì vậy mô hình tập trung vào chuỗi:

`UNAUTHENTICATED → AUTHENTICATING → AUTHENTICATED`

và các nhánh lỗi đăng nhập/tài khoản chưa hoạt động.

### 2.2 Attendance

Mã nguồn:

`attendance_service/routes/attendance.js`

Endpoint chấm công `POST /verify-code` sử dụng middleware xác thực token và lấy `user_id` từ token. Mô hình hóa thành:

`READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN → CHECKED_OUT`

với nhánh xác thực thất bại quay về `READY`.

### 2.3 Leave

Mã nguồn:

`leave_service/routes/leaves.js`

Yêu cầu nghỉ phép được tạo ở trạng thái `PENDING`, sau đó có thể `APPROVED` hoặc `REJECTED`. Vì vậy Kripke structure là:

`NO_REQUEST → PENDING → APPROVED/REJECTED → NO_REQUEST`

### 2.4 Payroll

Mã nguồn:

`salary_service/routes/payroll.js`

Hàm `syncPayrollRealtime()` tính dữ liệu lương và lưu bảng lương ở trạng thái `DRAFT`; endpoint trạng thái có thể chuyển bảng lương sang `PAID`. Mô hình hóa:

`NOT_CALCULATED → CALCULATING → DRAFT → PAID`

và `PAID → PAID` là self-loop biểu diễn trạng thái đã thanh toán.

---

## 3. Kripke Structure

Một Kripke structure được biểu diễn bởi:

`M = (S, S0, R, L)`

trong đó:

- `S`: tập trạng thái.
- `S0`: trạng thái khởi tạo.
- `R`: quan hệ chuyển tiếp.
- `L`: các proposition đúng tại từng trạng thái.

### 3.1 Login

| State | Labels | Vai trò |
|---|---|---|
| UNAUTHENTICATED | unauthenticated | chưa đăng nhập |
| AUTHENTICATING_VALID | valid_credentials | thông tin xác thực hợp lệ |
| AUTHENTICATING_INVALID | invalid_credentials | thông tin xác thực không hợp lệ |
| LOGIN_FAILED | login_failed | đăng nhập thất bại |
| INACTIVE_USER | inactive_user | tài khoản chưa ACTIVE |
| AUTHENTICATED | authenticated, credentials_verified | đăng nhập thành công |
| LOGGED_OUT | logged_out | đã đăng xuất |

### 3.2 Attendance

| State | Labels | Vai trò |
|---|---|---|
| READY | ready | sẵn sàng chấm công |
| AUTHENTICATED | authenticated | đã xác thực |
| CHECKIN_VALID | valid_checkin | dữ liệu check-in hợp lệ |
| CHECKED_IN | checked_in | đã check-in |
| CHECKED_OUT | checked_out | đã check-out |
| VERIFY_FAILED | verify_failed | xác minh thất bại |

### 3.3 Leave

| State | Labels | Vai trò |
|---|---|---|
| NO_REQUEST | no_request | chưa có yêu cầu |
| PENDING | pending, valid_leave_request | yêu cầu đang chờ duyệt |
| APPROVED | approved | được duyệt |
| REJECTED | rejected | bị từ chối |

### 3.4 Payroll

| State | Labels | Vai trò |
|---|---|---|
| NOT_CALCULATED | valid_payroll_input | chưa tính lương |
| CALCULATING | calculating | đang tính |
| DRAFT | draft, payroll_ready | bảng lương nháp |
| PAID | paid | đã thanh toán |

---

## 4. Thuộc tính kiểm chứng

Dự án dùng 8 thuộc tính, vượt yêu cầu tối thiểu 3 thuộc tính và có cả Safety + Liveness.

### Login

**L1 — Safety**

`AG(!bypass_authentication)`

Không tồn tại đường đi từ trạng thái ban đầu tới một trạng thái bỏ qua xác thực.

**L2 — Liveness**

`AG(valid_credentials → AF(authenticated))`

Khi tiền đề là thông tin xác thực hợp lệ, cuối cùng hệ thống phải đạt trạng thái authenticated.

### Attendance

**A1 — Safety**

`AG(!checkout_without_checkin)`

Không được chuyển trực tiếp tới CHECKED_OUT trước khi CHECKED_IN.

**A2 — Liveness**

`AG(valid_checkin → AF(checked_in))`

Khi yêu cầu check-in hợp lệ, cuối cùng phải đạt CHECKED_IN.

### Leave

**LV1 — Safety**

`AG(!approved_without_pending)`

Không được APPROVED trực tiếp khi chưa đi qua PENDING.

**LV2 — Liveness**

`AG(valid_leave_request → AF(approved OR rejected))`

Yêu cầu nghỉ phép hợp lệ cuối cùng phải được giải quyết theo một trong hai hướng APPROVED hoặc REJECTED.

### Payroll

**P1 — Safety**

`AG(!paid_to_draft)`

Một bảng lương đã PAID không được quay trở lại DRAFT.

**P2 — Liveness**

`AG(valid_payroll_input → AF(draft))`

Dữ liệu tính lương hợp lệ cuối cùng phải tạo được trạng thái DRAFT.

---

## 5. Mô hình lỗi và counterexample

Để chứng minh công cụ thực sự có khả năng phát hiện vi phạm, mỗi chức năng có một mô hình cố ý thêm một transition sai.

| Chức năng | Lỗi cố ý | Counterexample ngắn nhất |
|---|---|---|
| Login | `UNAUTHENTICATED → AUTHENTICATED` | UNAUTHENTICATED → AUTHENTICATED |
| Attendance | `AUTHENTICATED → CHECKED_OUT` | READY → AUTHENTICATED → CHECKED_OUT |
| Leave | `NO_REQUEST → APPROVED` | NO_REQUEST → APPROVED |
| Payroll | `PAID → DRAFT` | NOT_CALCULATED → CALCULATING → DRAFT → PAID → DRAFT |

Sau khi kiểm chứng mô hình đúng, cả bốn transition lỗi không còn tồn tại và thuộc tính Safety chuyển sang PASS.

---

## 6. Bounded Model Checking

BMC kiểm tra các đường đi hữu hạn có độ dài `k` từ trạng thái khởi tạo. Với Safety, công cụ tìm một đường đi chứa transition vi phạm. Nếu không có counterexample tới completeness threshold của đồ thị trạng thái hữu hạn, thuộc tính Safety được xác nhận trong mô hình.

Toolkit của môn cung cấp ví dụ BMC/Z3 trong:

`softsec-toolkit/ch3_verify/03_bmc_manual.py`

Dự án mở rộng ý tưởng này bằng `verification/bmc/bounded_checker.py` để chạy trực tiếp trên Kripke structure.

### Completeness threshold

Đối với Safety của các mô hình hữu hạn ở đây, threshold được lấy là **maximum shortest-path distance từ S0 tới các trạng thái reachable** (đường kính reachable graph).

| Chức năng | Reachable states | Completeness threshold |
|---|---:|---:|
| Login | 7 | 3 |
| Attendance | 6 | 4 |
| Leave | 4 | 2 |
| Payroll | 4 | 3 |

Các giá trị này được tính từ chính đồ thị model, không đoán trước.

---

## 7. Kết quả thực nghiệm

Kết quả chạy `verification/run_all.py`:

| Chức năng | Safety model đúng | Faulty model | Counterexample | Liveness |
|---|---|---|---|---|
| Login | PASS | FAIL | UNAUTHENTICATED → AUTHENTICATED | PASS |
| Attendance | PASS | FAIL | READY → AUTHENTICATED → CHECKED_OUT | PASS |
| Leave | PASS | FAIL | NO_REQUEST → APPROVED | PASS |
| Payroll | PASS | FAIL | ... → PAID → DRAFT | PASS |

Điều quan trọng là kết quả `FAIL` ở faulty model là **có chủ đích**, dùng để chứng minh BMC có thể tìm ra đường vi phạm. Mô hình đúng sau đó cho Safety `PASS`.

File kết quả máy sinh:

`verification/results/verification_results.json`

---

## 8. Liên hệ với mã nguồn HRM

Mô hình không tự động chứng minh từng dòng JavaScript. Nó trừu tượng hóa các điều kiện trạng thái được thể hiện trong mã nguồn:

- Login: password comparison → ACTIVE check → JWT/session.
- Attendance: JWT middleware → xác minh/chấm công → check-in/check-out.
- Leave: tạo request → PENDING → approval/rejection.
- Payroll: calculate/sync → DRAFT → PAID.

Do đó kết quả kiểm chứng phải được hiểu là kiểm chứng **mô hình nghiệp vụ đã trừu tượng hóa**. Muốn chứng minh implementation hoàn toàn khớp model, cần thêm bước traceability hoặc kiểm chứng implementation-level.

---

## 9. Cách chạy lại

Đặt biến `SOFTSEC_TOOLKIT` tới thư mục toolkit:

Windows CMD:

```bat
set SOFTSEC_TOOLKIT=..\softsec-toolkit
python verification\run_all.py
```

PowerShell:

```powershell
$env:SOFTSEC_TOOLKIT="..\softsec-toolkit"
python verification\run_all.py
```

Linux/macOS:

```bash
export SOFTSEC_TOOLKIT=../softsec-toolkit
python verification/run_all.py
```

---

## 10. Kết luận

Dự án đã xây dựng bốn Kripke structures cho bốn chức năng HRM, tám thuộc tính Safety/Liveness, bốn faulty models, cơ chế BMC bounded checking, counterexample và completeness threshold.

Kết quả thực nghiệm cho thấy:

1. Mô hình an toàn của cả bốn chức năng thỏa các thuộc tính Safety đã chọn.
2. Bốn mô hình lỗi đều tạo được counterexample ngắn nhất.
3. Các thuộc tính Liveness được thỏa trong các tiền đề hợp lệ đã định nghĩa.
4. Completeness threshold của Safety được tính từ reachable-state graph.
5. Quy trình minh họa đầy đủ vòng đời: **mã HRM → abstraction → Kripke → property → faulty model → BMC/counterexample → model sửa → re-verification**.

---

## 11. Giới hạn cần trình bày khi bảo vệ

- Không nói rằng toàn bộ HRM production đã được chứng minh hình thức.
- Không nói rằng BMC đã kiểm tra React, PostgreSQL, Redis, Kong/Nginx, Docker và toàn bộ microservices.
- Nêu rõ đây là **state abstraction** của bốn nghiệp vụ được chọn.
- Nêu rõ completeness threshold ở đây là threshold của finite-state safety model.
- Nếu giảng viên yêu cầu chứng minh implementation-level, bước tiếp theo là xây traceability giữa transition của model và branch/route tương ứng trong mã nguồn.
