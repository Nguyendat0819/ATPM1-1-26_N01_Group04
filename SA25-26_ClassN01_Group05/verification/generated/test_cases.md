# Test case tĩnh được sinh từ mô hình Kripke

Các ca dưới đây kiểm tra trạng thái và transition trong mô hình; chúng không gửi request tới các API HRM.

| ID | Chức năng | Mã nguồn nghiệp vụ | Loại phủ | Đường trạng thái | Kết quả mong đợi |
|---|---|---|---|---|---|
| GEN-ATTENDANCE-01 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED` | Reach AUTHENTICATED through the declared transition. |
| GEN-ATTENDANCE-02 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED → VERIFY_FAILED` | Reach VERIFY_FAILED through the declared transition. |
| GEN-ATTENDANCE-03 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED → CHECKIN_VALID` | Reach CHECKIN_VALID through the declared transition. |
| GEN-ATTENDANCE-04 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN` | Reach CHECKED_IN through the declared transition. |
| GEN-ATTENDANCE-05 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED → VERIFY_FAILED → READY` | Reach READY through the declared transition. |
| GEN-ATTENDANCE-06 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN → CHECKED_OUT` | Reach CHECKED_OUT through the declared transition. |
| GEN-ATTENDANCE-07 | Chấm công | `attendance_service/routes/attendance.js` | transition | `READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN → CHECKED_OUT → READY` | Reach READY through the declared transition. |
| GEN-ATTENDANCE-SAFETY-01 | Chấm công | `attendance_service/routes/attendance.js` | safety_constraint | `READY → AUTHENTICATED → CHECKED_OUT` | Reject AUTHENTICATED -> CHECKED_OUT; it violates A1. |
| GEN-ATTENDANCE-LIVENESS-01 | Chấm công | `attendance_service/routes/attendance.js` | liveness_witness | `CHECKIN_VALID → CHECKED_IN` | Reach a state labelled with checked_in. |
| GEN-LEAVE-01 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | transition | `NO_REQUEST → PENDING` | Reach PENDING through the declared transition. |
| GEN-LEAVE-02 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | transition | `NO_REQUEST → PENDING → APPROVED` | Reach APPROVED through the declared transition. |
| GEN-LEAVE-03 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | transition | `NO_REQUEST → PENDING → REJECTED` | Reach REJECTED through the declared transition. |
| GEN-LEAVE-04 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | transition | `NO_REQUEST → PENDING → APPROVED → NO_REQUEST` | Reach NO_REQUEST through the declared transition. |
| GEN-LEAVE-05 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | transition | `NO_REQUEST → PENDING → REJECTED → NO_REQUEST` | Reach NO_REQUEST through the declared transition. |
| GEN-LEAVE-SAFETY-01 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | safety_constraint | `NO_REQUEST → APPROVED` | Reject NO_REQUEST -> APPROVED; it violates LV1. |
| GEN-LEAVE-LIVENESS-01 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | liveness_witness | `PENDING → APPROVED` | Reach a state labelled with approved, rejected. |
| GEN-LOGIN-01 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE` | Reach AUTHENTICATING_ACTIVE through the declared transition. |
| GEN-LOGIN-02 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_INVALID` | Reach AUTHENTICATING_INVALID through the declared transition. |
| GEN-LOGIN-03 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_INACTIVE` | Reach AUTHENTICATING_INACTIVE through the declared transition. |
| GEN-LOGIN-04 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE → AUTHENTICATED` | Reach AUTHENTICATED through the declared transition. |
| GEN-LOGIN-05 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_INVALID → LOGIN_FAILED` | Reach LOGIN_FAILED through the declared transition. |
| GEN-LOGIN-06 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_INACTIVE → INACTIVE_USER` | Reach INACTIVE_USER through the declared transition. |
| GEN-LOGIN-07 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_INVALID → LOGIN_FAILED → UNAUTHENTICATED` | Reach UNAUTHENTICATED through the declared transition. |
| GEN-LOGIN-08 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_INACTIVE → INACTIVE_USER → UNAUTHENTICATED` | Reach UNAUTHENTICATED through the declared transition. |
| GEN-LOGIN-09 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE → AUTHENTICATED → LOGGED_OUT` | Reach LOGGED_OUT through the declared transition. |
| GEN-LOGIN-10 | Xác thực đăng nhập | `auth_service/routes/auth.js` | transition | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE → AUTHENTICATED → LOGGED_OUT → UNAUTHENTICATED` | Reach UNAUTHENTICATED through the declared transition. |
| GEN-LOGIN-SAFETY-01 | Xác thực đăng nhập | `auth_service/routes/auth.js` | safety_constraint | `UNAUTHENTICATED → AUTHENTICATED` | Reject UNAUTHENTICATED -> AUTHENTICATED; it violates L1. |
| GEN-LOGIN-LIVENESS-01 | Xác thực đăng nhập | `auth_service/routes/auth.js` | liveness_witness | `AUTHENTICATING_ACTIVE → AUTHENTICATED` | Reach a state labelled with authenticated. |
| GEN-PAYROLL-01 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | transition | `NOT_CALCULATED → CALCULATING` | Reach CALCULATING through the declared transition. |
| GEN-PAYROLL-02 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | transition | `NOT_CALCULATED → CALCULATING → DRAFT` | Reach DRAFT through the declared transition. |
| GEN-PAYROLL-03 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | transition | `NOT_CALCULATED → CALCULATING → DRAFT → PAID` | Reach PAID through the declared transition. |
| GEN-PAYROLL-04 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | transition | `NOT_CALCULATED → CALCULATING → DRAFT → PAID → PAID` | Reach PAID through the declared transition. |
| GEN-PAYROLL-SAFETY-01 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | safety_constraint | `NOT_CALCULATED → CALCULATING → DRAFT → PAID → DRAFT` | Reject PAID -> DRAFT; it violates P1. |
| GEN-PAYROLL-LIVENESS-01 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | liveness_witness | `NOT_CALCULATED → CALCULATING → DRAFT` | Reach a state labelled with draft. |
