# HRM — Kripke + BMC Verification

## Mục tiêu

Thư mục này là phần kiểm chứng hình thức cho hệ thống HRM của nhóm. Nó **không thay thế** mã nguồn HRM; nó tạo một mô hình trạng thái hữu hạn trừu tượng hóa 4 chức năng:

1. Xác thực đăng nhập
2. Chấm công thông minh
3. Quản lý nghỉ phép
4. Tính lương

Phần kiểm chứng tái sử dụng `softsec-toolkit/ch1_models/kripke.py`. BMC được mở rộng từ ý tưởng trong `softsec-toolkit/ch3_verify/03_bmc_manual.py` bằng một bounded checker cho đồ thị trạng thái hữu hạn.

## Cấu trúc

```text
verification/
├── models/              # Kripke structures an toàn
├── faulty_models/       # Mô hình cố ý cài lỗi
├── properties/          # 8 thuộc tính Safety/Liveness
├── bmc/                 # bounded_checker.py
├── results/             # kết quả chạy
├── counterexamples/     # nơi lưu phản ví dụ nếu cần
├── docs/                # tài liệu báo cáo
├── lib/                 # adapter gọi KripkeStructure của toolkit
└── run_all.py           # chạy toàn bộ kiểm chứng
```

## Yêu cầu môi trường

- Python 3.9+
- `softsec-toolkit` của môn học
- Không bắt buộc cài Z3 để chạy phần kiểm chứng này. File `ch3_verify/03_bmc_manual.py` của toolkit vẫn là ví dụ BMC/Z3 gốc để đối chiếu.

## Chạy

Nếu `softsec-toolkit` nằm ở thư mục song song với project:

```bash
set SOFTSEC_TOOLKIT=..\softsec-toolkit
python verification\run_all.py
```

Linux/macOS:

```bash
export SOFTSEC_TOOLKIT=../softsec-toolkit
python verification/run_all.py
```

Hoặc đặt `SOFTSEC_TOOLKIT` tới thư mục chứa `ch1_models/kripke.py`.

## Kết quả mong đợi

| Chức năng | Safety mô hình đúng | Safety mô hình lỗi | Liveness | Completeness threshold |
|---|---|---|---|---:|
| Login | PASS | FAIL + bypass | PASS | 3 |
| Attendance | PASS | FAIL + checkout sớm | PASS | 4 |
| Leave | PASS | FAIL + approve trực tiếp | PASS | 2 |
| Payroll | PASS | FAIL + PAID → DRAFT | PASS | 3 |

`results/verification_results.json` được sinh lại sau mỗi lần chạy.

## Lưu ý học thuật

Mô hình Kripke là **mô hình trừu tượng** của logic nghiệp vụ, không phải toàn bộ hệ thống React/Node/PostgreSQL/Redis. Các thuộc tính chứng minh tính đúng của mô hình trong phạm vi các trạng thái và chuyển tiếp đã định nghĩa; không được diễn giải thành chứng minh toàn bộ triển khai production.
