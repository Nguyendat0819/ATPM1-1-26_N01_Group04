# Test case sinh theo ràng buộc duyệt đơn

Các trường hợp LV-01 đến LV-12 được sinh từ bảng dữ liệu `rejectionCases` trong `leave_service/test/leaves.status.test.js`. LV-13 đến LV-15 xác nhận chuyển trạng thái hợp lệ và lỗi ở hệ thống phụ. Mỗi test gọi chính handler của route bằng JWT, DB và MongoDB giả lập; các trường hợp thất bại kiểm tra rằng không tạo log.

| ID | Ràng buộc | Dữ liệu hoặc tình huống | HTTP mong đợi | Kết quả |
|---|---|---|---:|---|
| LV-01 | R1 | Không gửi JWT | 401 | Không cập nhật |
| LV-02 | R1 | JWT không hợp lệ | 401 | Không cập nhật |
| LV-03 | R2 | `id=abc` | 400 | Không cập nhật |
| LV-04 | R2 | `status=CANCELLED` | 400 | Không cập nhật |
| LV-05 | R3 | Vai trò `STAFF` gọi duyệt | 403 | Không cập nhật |
| LV-06 | R7 | Không tìm thấy đơn | 404 | Không cập nhật |
| LV-07 | R5 | Manager khác phòng | 403 | Không cập nhật |
| LV-08 | R5 | Manager duyệt Manager | 403 | Không cập nhật |
| LV-09 | R6 | Admin duyệt Staff | 403 | Không cập nhật |
| LV-10 | R4 | Người duyệt trùng người tạo | 403 | Không cập nhật |
| LV-11 | R7 | Đơn đã `APPROVED` | 409 | Không cập nhật lần hai |
| LV-12 | R8 | `UPDATE ... WHERE status='PENDING'` không trả dòng | 409 | Không ghi log/thông báo |
| LV-13 | R1–R8 | Manager duyệt Staff cùng phòng, đơn `PENDING` | 200 | Lưu `APPROVED`, người duyệt và log |
| LV-14 | R1–R8 | Superadmin từ chối Manager, đơn `PENDING` | 200 | Lưu `REJECTED`, lý do và người duyệt |
| LV-15 | Hậu điều kiện | MongoDB và Socket.IO lỗi sau khi cập nhật | 200 | Trạng thái PostgreSQL vẫn được ghi thành công |

## Cách chạy

```bash
cd leave_service
npm test
```

Kết quả chạy mới nhất nằm trong `LEAVE_APPROVAL_REPORT.md`. Không dùng trạng thái `PASS` của `TEST_CASES.md` cũ làm bằng chứng cho các test này.
