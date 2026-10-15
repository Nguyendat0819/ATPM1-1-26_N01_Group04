# Báo cáo kiểm chứng mô hình HRM

Ngày chạy: 2026-10-15.

## Phạm vi và phương pháp

Đã đặc tả, sinh mô hình và kiểm chứng bốn luồng: đăng nhập, chấm công, nghỉ phép, tính lương. Spec JSON sinh Python Kripke model, faulty model và test case phủ transition. Checker kiểm tra safety bằng tìm phản ví dụ có giới hạn và liveness bằng tính điểm cố định universal `AF` trên đồ thị reachable.

Giới hạn BMC safety là `N` transition, với `N` bằng số trạng thái reachable của mô hình đúng. Với thuộc tính transition này, đường phản ví dụ ngắn nhất có thể rút gọn thành một đường không lặp từ trạng thái đầu đến nguồn transition rồi đi qua transition lỗi; do đó không cần quá `N` bước.

## Đặc tả và kết quả

| Chức năng | State reachable | Transition | Safety đúng | Faulty model | Liveness | Test case sinh |
|---|---:|---:|---|---|---|---:|
| Đăng nhập | 7 | 9 | PASS | DETECTED | PASS | 9 |
| Chấm công | 6 | 7 | PASS | DETECTED | PASS | 7 |
| Nghỉ phép | 4 | 5 | PASS | DETECTED | PASS | 5 |
| Tính lương | 4 | 4 | PASS | DETECTED | PASS | 4 |
| **Tổng** | **21** | **25** | **4/4** | **4/4** | **4/4** | **25** |

Safety properties cấm lần lượt: đăng nhập bỏ qua xác thực, check-out trước check-in, duyệt nghỉ phép khi chưa có đơn chờ, và chuyển bảng lương `PAID → DRAFT`. Liveness properties yêu cầu đăng nhập hợp lệ hoàn tất, check-in hợp lệ được ghi nhận, đơn nghỉ phép được giải quyết, và dữ liệu lương hợp lệ tạo được bản nháp.

## Phản ví dụ của mô hình lỗi

- Login: `UNAUTHENTICATED → AUTHENTICATED`
- Attendance: `READY → AUTHENTICATED → CHECKED_OUT`
- Leave: `NO_REQUEST → APPROVED`
- Payroll: `NOT_CALCULATED → CALCULATING → DRAFT → PAID → DRAFT`

Checker tìm thấy đủ bốn phản ví dụ và xác nhận không có phản ví dụ tương ứng trong các model đúng. Toàn bộ kết quả máy sinh nằm trong `results/verification_results.json`; 25 test case nằm trong `generated/test_cases.json`.

## Cách chạy và bằng chứng

```bash
python verification/run_all.py
python -m unittest discover -s verification/tests -v
```

Lần chạy `run_all.py` ở trên đạt `Overall: PASS` cho 4/4 chức năng, sinh 25 test case và phát hiện đủ 4 mô hình lỗi. Bộ unittest hồi quy xác nhận model generation, transition coverage, safety, liveness và faulty-model detection.

Unittest: 2/2 PASS. Kiểm thử handler nghỉ phép ở `leave_service`: 15/15 PASS.

## Giới hạn

- Kết quả chứng minh các thuộc tính trên mô hình hữu hạn đã đặc tả, không chứng minh implementation Node.js, React hoặc hạ tầng chạy đúng.
- Test case sinh là đường đi trừu tượng trong mô hình; chưa sinh request HTTP hay fixture dữ liệu cho từng API.
- Mô hình không chứa timeout, retry, fairness, phân quyền đầy đủ, ngày lễ hoặc quy tắc số ngày nghỉ.
- Báo cáo kiểm thử API nghỉ phép riêng trước đó kiểm tra handler bằng dependency giả lập; chưa thay thế integration test với PostgreSQL/MongoDB/Redis.
