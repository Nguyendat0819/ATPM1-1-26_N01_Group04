# Đặc tả và ràng buộc: duyệt đơn nghỉ phép

## Phạm vi

Endpoint `PUT /api/leave_ser/:id/status` chuyển một đơn nghỉ phép đang chờ xử lý sang `APPROVED` hoặc `REJECTED`. Đặc tả này chỉ áp dụng cho thao tác duyệt; tạo đơn, tính số ngày nghỉ và khấu trừ lương nằm ngoài phạm vi thay đổi.

## Mô hình trạng thái

```text
PENDING ──duyệt──> APPROVED
   └─────từ chối──> REJECTED
```

`APPROVED` và `REJECTED` là trạng thái kết thúc của một đơn. Mọi yêu cầu chuyển tiếp khác bị từ chối bằng HTTP 409 hoặc 400 tùy trường hợp.

## Tiền điều kiện và ràng buộc

| Mã | Ràng buộc | Kết quả khi vi phạm |
|---|---|---|
| R1 | Có JWT hợp lệ trong `Authorization: Bearer <token>`. | 401 |
| R2 | `id` là số nguyên dương an toàn; `status` chỉ là `APPROVED` hoặc `REJECTED`. | 400 |
| R3 | Chỉ `MANAGER`, `ADMIN`, `SUPERADMIN` được gọi thao tác duyệt. | 403 |
| R4 | Không ai được duyệt đơn của chính mình. | 403 |
| R5 | `MANAGER` chỉ duyệt đơn của `STAFF` trong cùng phòng ban; phòng ban được đọc từ cơ sở dữ liệu. | 403 |
| R6 | `ADMIN` hoặc `SUPERADMIN` chỉ duyệt đơn của `MANAGER`. | 403 |
| R7 | Đơn phải tồn tại và có trạng thái `PENDING`. | 404 nếu không tồn tại; 409 nếu đã xử lý |
| R8 | Cập nhật phải có điều kiện `WHERE status = 'PENDING'` để chỉ một yêu cầu đồng thời thành công. | 409 cho yêu cầu thua cuộc |

## Hậu điều kiện

- Sau cập nhật thành công, `status` bằng giá trị yêu cầu và `approver_id` bằng ID trong JWT.
- `approved_at` chỉ được ghi khi duyệt. `rejection_reason` chỉ được lưu khi từ chối.
- Chỉ yêu cầu cập nhật thành công mới tạo log, thông báo lưu trữ và tín hiệu Socket.IO.
- Log MongoDB và thông báo là thao tác phụ sau cập nhật PostgreSQL. Nếu hệ thống phụ gặp lỗi, API vẫn trả kết quả của cập nhật trạng thái; lỗi được ghi vào log vận hành.

## Liên hệ mã nguồn

- Quy tắc quyền và chuyển trạng thái: `leave_service/routes/leaves.js`.
- Test thực thi: `leave_service/test/leaves.status.test.js`.
- Lệnh chạy: `cd leave_service && npm test`.

## Giới hạn kiểm chứng

Bộ test dùng mock cho JWT, PostgreSQL và MongoDB để kiểm tra nhánh xử lý của route. Nó không chứng minh kết nối cơ sở dữ liệu, tính nguyên tử giữa PostgreSQL và MongoDB, hoặc toàn bộ nghiệp vụ nghỉ phép.
