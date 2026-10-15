# HRM: sinh mô hình Kripke và kiểm chứng BMC

Thư mục này mô hình hóa bốn luồng HRM: đăng nhập, chấm công, nghỉ phép và tính lương. Đây là mô hình trạng thái nghiệp vụ, không thay thế hoặc chứng minh toàn bộ ứng dụng React, Express, PostgreSQL, MongoDB, Redis và gateway.

## Quy trình sinh

`specs/*.json` là nguồn khai báo trạng thái, nhãn, trạng thái khởi đầu, chuyển tiếp và thuộc tính. Lệnh sinh tạo:

- `models/*_kripke.py`: mô hình Python cho luồng đúng.
- `faulty_models/*_faulty.py`: mô hình có thêm một chuyển tiếp vi phạm để kiểm tra khả năng tìm phản ví dụ.
- `generated/test_cases.json`: đường đi ngắn nhất từ trạng thái đầu để phủ từng chuyển tiếp trong mô hình đúng.
- `results/verification_results.json`: kết quả kiểm chứng và phản ví dụ.

## Chạy

Yêu cầu Python 3.9 trở lên. Không cần Z3, `softsec-toolkit`, package bên ngoài hoặc dịch vụ Docker.

```bash
python verification/generate_artifacts.py
python verification/run_all.py
python -m unittest discover -s verification/tests -v
```

`run_all.py` tự sinh lại model và test case trước khi chạy safety, liveness và BMC. BMC dùng giới hạn số bước bằng số trạng thái reachable: phản ví dụ cho một transition có thể rút gọn thành đường đi không lặp lại tới nguồn transition, rồi thêm chính transition vi phạm.

## Đọc kết quả

- `PASS`: mô hình đúng không có counterexample cho thuộc tính safety; thuộc tính liveness đạt trên các trạng thái bắt đầu nêu trong spec.
- `DETECTED`: mô hình lỗi có counterexample, cho thấy checker bắt được lỗi đã cài.
- Test case sinh là kịch bản ở mức mô hình, chưa tự gọi HTTP API.
- Báo cáo mới: `docs/FORMAL_VERIFICATION_REPORT.md`.
