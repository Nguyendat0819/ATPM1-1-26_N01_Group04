# Ca kiểm thử tĩnh được sinh từ mô hình Kripke

Các ca dưới đây kiểm tra đường đi trạng thái, chuyển tiếp và thuộc tính trên mô hình Kripke. Đây là kiểm thử tĩnh ở mức mô hình; chương trình không gửi yêu cầu HTTP đến API HRM.

Tên state, ID kiểm thử và đường dẫn mã nguồn được giữ nguyên để có thể đối chiếu trực tiếp với đặc tả JSON và repository.

| ID | Chức năng | Mã nguồn triển khai | Loại kiểm thử / độ phủ | Đường trạng thái | Kết quả mong đợi |
|---|---|---|---|---|---|
| GEN-ATTENDANCE-01 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED` | Đi đến trạng thái AUTHENTICATED theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-02 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED → VERIFY_FAILED` | Đi đến trạng thái VERIFY_FAILED theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-03 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED → CHECKIN_VALID` | Đi đến trạng thái CHECKIN_VALID theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-04 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN` | Đi đến trạng thái CHECKED_IN theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-05 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED → VERIFY_FAILED → READY` | Đi đến trạng thái READY theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-06 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN → CHECKED_OUT` | Đi đến trạng thái CHECKED_OUT theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-07 | Chấm công | `attendance_service/routes/attendance.js` | Phủ chuyển tiếp | `READY → AUTHENTICATED → CHECKIN_VALID → CHECKED_IN → CHECKED_OUT → READY` | Đi đến trạng thái READY theo chuyển tiếp đã khai báo. |
| GEN-ATTENDANCE-SAFETY-01 | Chấm công | `attendance_service/routes/attendance.js` | Kiểm tra ràng buộc an toàn (Safety) | `READY → AUTHENTICATED → CHECKED_OUT` | Từ chối chuyển tiếp AUTHENTICATED → CHECKED_OUT vì vi phạm ràng buộc A1. |
| GEN-ATTENDANCE-LIVENESS-01 | Chấm công | `attendance_service/routes/attendance.js` | Đường chứng kiến tính sống (Liveness) | `CHECKIN_VALID → CHECKED_IN` | Đạt trạng thái mang một trong các nhãn mục tiêu: checked_in. |
| GEN-LEAVE-01 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Phủ chuyển tiếp | `NO_REQUEST → PENDING` | Đi đến trạng thái PENDING theo chuyển tiếp đã khai báo. |
| GEN-LEAVE-02 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Phủ chuyển tiếp | `NO_REQUEST → PENDING → APPROVED` | Đi đến trạng thái APPROVED theo chuyển tiếp đã khai báo. |
| GEN-LEAVE-03 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Phủ chuyển tiếp | `NO_REQUEST → PENDING → REJECTED` | Đi đến trạng thái REJECTED theo chuyển tiếp đã khai báo. |
| GEN-LEAVE-04 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Phủ chuyển tiếp | `NO_REQUEST → PENDING → APPROVED → NO_REQUEST` | Đi đến trạng thái NO_REQUEST theo chuyển tiếp đã khai báo. |
| GEN-LEAVE-05 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Phủ chuyển tiếp | `NO_REQUEST → PENDING → REJECTED → NO_REQUEST` | Đi đến trạng thái NO_REQUEST theo chuyển tiếp đã khai báo. |
| GEN-LEAVE-SAFETY-01 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Kiểm tra ràng buộc an toàn (Safety) | `NO_REQUEST → APPROVED` | Từ chối chuyển tiếp NO_REQUEST → APPROVED vì vi phạm ràng buộc LV1. |
| GEN-LEAVE-LIVENESS-01 | Duyệt đơn nghỉ phép | `leave_service/routes/leaves.js` | Đường chứng kiến tính sống (Liveness) | `PENDING → APPROVED` | Đạt trạng thái mang một trong các nhãn mục tiêu: approved, rejected. |
| GEN-LOGIN-01 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE` | Đi đến trạng thái AUTHENTICATING_ACTIVE theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-02 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_INVALID` | Đi đến trạng thái AUTHENTICATING_INVALID theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-03 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_INACTIVE` | Đi đến trạng thái AUTHENTICATING_INACTIVE theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-04 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE → AUTHENTICATED` | Đi đến trạng thái AUTHENTICATED theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-05 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_INVALID → LOGIN_FAILED` | Đi đến trạng thái LOGIN_FAILED theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-06 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_INACTIVE → INACTIVE_USER` | Đi đến trạng thái INACTIVE_USER theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-07 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_INVALID → LOGIN_FAILED → UNAUTHENTICATED` | Đi đến trạng thái UNAUTHENTICATED theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-08 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_INACTIVE → INACTIVE_USER → UNAUTHENTICATED` | Đi đến trạng thái UNAUTHENTICATED theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-09 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE → AUTHENTICATED → LOGGED_OUT` | Đi đến trạng thái LOGGED_OUT theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-10 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Phủ chuyển tiếp | `UNAUTHENTICATED → AUTHENTICATING_ACTIVE → AUTHENTICATED → LOGGED_OUT → UNAUTHENTICATED` | Đi đến trạng thái UNAUTHENTICATED theo chuyển tiếp đã khai báo. |
| GEN-LOGIN-SAFETY-01 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Kiểm tra ràng buộc an toàn (Safety) | `UNAUTHENTICATED → AUTHENTICATED` | Từ chối chuyển tiếp UNAUTHENTICATED → AUTHENTICATED vì vi phạm ràng buộc L1. |
| GEN-LOGIN-LIVENESS-01 | Xác thực đăng nhập | `auth_service/routes/auth.js` | Đường chứng kiến tính sống (Liveness) | `AUTHENTICATING_ACTIVE → AUTHENTICATED` | Đạt trạng thái mang một trong các nhãn mục tiêu: authenticated. |
| GEN-PAYROLL-01 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | Phủ chuyển tiếp | `NOT_CALCULATED → CALCULATING` | Đi đến trạng thái CALCULATING theo chuyển tiếp đã khai báo. |
| GEN-PAYROLL-02 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | Phủ chuyển tiếp | `NOT_CALCULATED → CALCULATING → DRAFT` | Đi đến trạng thái DRAFT theo chuyển tiếp đã khai báo. |
| GEN-PAYROLL-03 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | Phủ chuyển tiếp | `NOT_CALCULATED → CALCULATING → DRAFT → PAID` | Đi đến trạng thái PAID theo chuyển tiếp đã khai báo. |
| GEN-PAYROLL-04 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | Phủ chuyển tiếp | `NOT_CALCULATED → CALCULATING → DRAFT → PAID → PAID` | Đi đến trạng thái PAID theo chuyển tiếp đã khai báo. |
| GEN-PAYROLL-SAFETY-01 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | Kiểm tra ràng buộc an toàn (Safety) | `NOT_CALCULATED → CALCULATING → DRAFT → PAID → DRAFT` | Từ chối chuyển tiếp PAID → DRAFT vì vi phạm ràng buộc P1. |
| GEN-PAYROLL-LIVENESS-01 | Tính và thanh toán lương | `salary_service/routes/payroll.js` | Đường chứng kiến tính sống (Liveness) | `NOT_CALCULATED → CALCULATING → DRAFT` | Đạt trạng thái mang một trong các nhãn mục tiêu: draft. |
