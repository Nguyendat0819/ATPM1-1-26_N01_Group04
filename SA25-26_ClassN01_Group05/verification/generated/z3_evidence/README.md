# Minh chứng mã hóa Z3 từ đặc tả Kripke HRM

Lần xuất: 2026-10-23T17:28:33.118973+00:00; Z3 5.3.1.

Nguồn state và transition là `verification/specs/*.json`, được nhóm trừu tượng hóa từ các route HRM ghi ở từng đặc tả. Bộ sinh không tự phân tích mã Express. `formula` trong JSON là mô tả; checker dùng trực tiếp `transitions`, `allowed_predecessors`, `starts` và `target_labels`.

Mỗi state được đổi thành mã nguyên theo thứ tự trong JSON. Ở bước i, một cạnh `u -> v` thành `And(state_i == code(u), state_(i+1) == code(v))`; quan hệ R là `Or` của tất cả các cạnh. Safety còn yêu cầu cạnh cuối thuộc tập cấm. Bound là số state reachable từ state đầu, tính lại khi chạy.

File SMT-LIB là truy vấn Z3 thực tế do cùng hàm tạo ràng buộc của checker xuất ra. File Safety chuẩn ở độ sâu k chỉ minh họa một truy vấn; kết quả Safety tổng thể được runner kiểm lần lượt mọi độ sâu 1..k.

## attendance

- Đặc tả: `verification/specs/attendance.json`; SHA-256: `e1fdeed5fbf17af1239ab05a123ce1cf606515a9507302cad09245a382acae2d`.
- Route tham chiếu: `attendance_service/routes/attendance.js`.
- State đầu: `READY`; bound = |Reach(state đầu)| = 6 cạnh; truy vấn lớn nhất có 7 biến state.
- Safety A1: tiền nhiệm cho phép `{"CHECKED_IN": ["CHECKIN_VALID"], "CHECKED_OUT": ["CHECKED_IN"]}`; suy ra 10 cặp nguồn-đích bị cấm.
- Cạnh lỗi đối chứng: `AUTHENTICATED -> CHECKED_OUT`.
- Liveness A2: starts `CHECKIN_VALID`; nhãn đích `checked_in`; state đích `CHECKED_IN`.

| State | Mã Z3 |
|---|---:|
| `READY` | 0 |
| `AUTHENTICATED` | 1 |
| `CHECKIN_VALID` | 2 |
| `CHECKED_IN` | 3 |
| `CHECKED_OUT` | 4 |
| `VERIFY_FAILED` | 5 |

| Transition trong R | Mệnh đề Z3 ở bước i |
|---|---|
| `READY -> AUTHENTICATED` | `And(state_i == 0, state_(i+1) == 1)` |
| `AUTHENTICATED -> VERIFY_FAILED` | `And(state_i == 1, state_(i+1) == 5)` |
| `AUTHENTICATED -> CHECKIN_VALID` | `And(state_i == 1, state_(i+1) == 2)` |
| `CHECKIN_VALID -> CHECKED_IN` | `And(state_i == 2, state_(i+1) == 3)` |
| `VERIFY_FAILED -> READY` | `And(state_i == 5, state_(i+1) == 0)` |
| `CHECKED_IN -> CHECKED_OUT` | `And(state_i == 3, state_(i+1) == 4)` |
| `CHECKED_OUT -> READY` | `And(state_i == 4, state_(i+1) == 0)` |

Kết quả: Safety chuẩn **UNSAT** qua độ sâu 1..6; Safety lỗi **SAT** ở độ sâu 2 với trace `READY -> AUTHENTICATED -> CHECKED_OUT`; phản ví dụ Liveness **UNSAT**.

[Liveness từ CHECKIN_VALID](attendance_liveness_start0_k6.smt2).

## leave

- Đặc tả: `verification/specs/leave.json`; SHA-256: `cb4c0e4ea48e9495a939f1ae2ed7e52818c4f3a4e3bddd17e49e28bcf20facb5`.
- Route tham chiếu: `leave_service/routes/leaves.js`.
- State đầu: `NO_REQUEST`; bound = |Reach(state đầu)| = 4 cạnh; truy vấn lớn nhất có 5 biến state.
- Safety LV1: tiền nhiệm cho phép `{"APPROVED": ["PENDING"], "REJECTED": ["PENDING"]}`; suy ra 6 cặp nguồn-đích bị cấm.
- Cạnh lỗi đối chứng: `NO_REQUEST -> APPROVED`.
- Liveness LV2: starts `PENDING`; nhãn đích `approved, rejected`; state đích `APPROVED, REJECTED`.

| State | Mã Z3 |
|---|---:|
| `NO_REQUEST` | 0 |
| `PENDING` | 1 |
| `APPROVED` | 2 |
| `REJECTED` | 3 |

| Transition trong R | Mệnh đề Z3 ở bước i |
|---|---|
| `NO_REQUEST -> PENDING` | `And(state_i == 0, state_(i+1) == 1)` |
| `PENDING -> APPROVED` | `And(state_i == 1, state_(i+1) == 2)` |
| `PENDING -> REJECTED` | `And(state_i == 1, state_(i+1) == 3)` |
| `APPROVED -> NO_REQUEST` | `And(state_i == 2, state_(i+1) == 0)` |
| `REJECTED -> NO_REQUEST` | `And(state_i == 3, state_(i+1) == 0)` |

Kết quả: Safety chuẩn **UNSAT** qua độ sâu 1..4; Safety lỗi **SAT** ở độ sâu 1 với trace `NO_REQUEST -> APPROVED`; phản ví dụ Liveness **UNSAT**.

[Liveness từ PENDING](leave_liveness_start0_k4.smt2).

## login

- Đặc tả: `verification/specs/login.json`; SHA-256: `aa5375a51533e904812b66bd00c238d880101ef0e141d70a07095dafda988d95`.
- Route tham chiếu: `auth_service/routes/auth.js`.
- State đầu: `UNAUTHENTICATED`; bound = |Reach(state đầu)| = 8 cạnh; truy vấn lớn nhất có 9 biến state.
- Safety L1: tiền nhiệm cho phép `{"AUTHENTICATED": ["AUTHENTICATING_ACTIVE"]}`; suy ra 7 cặp nguồn-đích bị cấm.
- Cạnh lỗi đối chứng: `UNAUTHENTICATED -> AUTHENTICATED`.
- Liveness L2: starts `AUTHENTICATING_ACTIVE`; nhãn đích `authenticated`; state đích `AUTHENTICATED`.

| State | Mã Z3 |
|---|---:|
| `UNAUTHENTICATED` | 0 |
| `AUTHENTICATING_ACTIVE` | 1 |
| `AUTHENTICATING_INVALID` | 2 |
| `AUTHENTICATING_INACTIVE` | 3 |
| `LOGIN_FAILED` | 4 |
| `INACTIVE_USER` | 5 |
| `AUTHENTICATED` | 6 |
| `LOGGED_OUT` | 7 |

| Transition trong R | Mệnh đề Z3 ở bước i |
|---|---|
| `UNAUTHENTICATED -> AUTHENTICATING_ACTIVE` | `And(state_i == 0, state_(i+1) == 1)` |
| `UNAUTHENTICATED -> AUTHENTICATING_INVALID` | `And(state_i == 0, state_(i+1) == 2)` |
| `UNAUTHENTICATED -> AUTHENTICATING_INACTIVE` | `And(state_i == 0, state_(i+1) == 3)` |
| `AUTHENTICATING_ACTIVE -> AUTHENTICATED` | `And(state_i == 1, state_(i+1) == 6)` |
| `AUTHENTICATING_INVALID -> LOGIN_FAILED` | `And(state_i == 2, state_(i+1) == 4)` |
| `AUTHENTICATING_INACTIVE -> INACTIVE_USER` | `And(state_i == 3, state_(i+1) == 5)` |
| `LOGIN_FAILED -> UNAUTHENTICATED` | `And(state_i == 4, state_(i+1) == 0)` |
| `INACTIVE_USER -> UNAUTHENTICATED` | `And(state_i == 5, state_(i+1) == 0)` |
| `AUTHENTICATED -> LOGGED_OUT` | `And(state_i == 6, state_(i+1) == 7)` |
| `LOGGED_OUT -> UNAUTHENTICATED` | `And(state_i == 7, state_(i+1) == 0)` |

Kết quả: Safety chuẩn **UNSAT** qua độ sâu 1..8; Safety lỗi **SAT** ở độ sâu 1 với trace `UNAUTHENTICATED -> AUTHENTICATED`; phản ví dụ Liveness **UNSAT**.

[Liveness từ AUTHENTICATING_ACTIVE](login_liveness_start0_k8.smt2).

## payroll

- Đặc tả: `verification/specs/payroll.json`; SHA-256: `7ea81c9aedf4f0b3da4a3b089ab4087168aa02c63fc0c258293df1b3d82ea584`.
- Route tham chiếu: `salary_service/routes/payroll.js`.
- State đầu: `NOT_CALCULATED`; bound = |Reach(state đầu)| = 4 cạnh; truy vấn lớn nhất có 5 biến state.
- Safety P1: tiền nhiệm cho phép `{"CALCULATING": ["NOT_CALCULATED"], "DRAFT": ["CALCULATING"], "PAID": ["DRAFT", "PAID"]}`; suy ra 8 cặp nguồn-đích bị cấm.
- Cạnh lỗi đối chứng: `PAID -> DRAFT`.
- Liveness P2: starts `NOT_CALCULATED`; nhãn đích `draft`; state đích `DRAFT`.

| State | Mã Z3 |
|---|---:|
| `NOT_CALCULATED` | 0 |
| `CALCULATING` | 1 |
| `DRAFT` | 2 |
| `PAID` | 3 |

| Transition trong R | Mệnh đề Z3 ở bước i |
|---|---|
| `NOT_CALCULATED -> CALCULATING` | `And(state_i == 0, state_(i+1) == 1)` |
| `CALCULATING -> DRAFT` | `And(state_i == 1, state_(i+1) == 2)` |
| `DRAFT -> PAID` | `And(state_i == 2, state_(i+1) == 3)` |
| `PAID -> PAID` | `And(state_i == 3, state_(i+1) == 3)` |

Kết quả: Safety chuẩn **UNSAT** qua độ sâu 1..4; Safety lỗi **SAT** ở độ sâu 4 với trace `NOT_CALCULATED -> CALCULATING -> DRAFT -> PAID -> DRAFT`; phản ví dụ Liveness **UNSAT**.

[Liveness từ NOT_CALCULATED](payroll_liveness_start0_k4.smt2).

