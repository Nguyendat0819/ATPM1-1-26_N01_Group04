# Báo cáo kiểm chứng hiện hành

Báo cáo kết quả tái lập được nằm tại [`FORMAL_VERIFICATION_REPORT.md`](FORMAL_VERIFICATION_REPORT.md). Sơ đồ hai luồng và mô hình bộ nhớ nằm tại [`DESIGN_FLOWS_MEMORY.md`](DESIGN_FLOWS_MEMORY.md). Chạy `python verification/run_all.py` từ thư mục dự án để sinh lại mô hình, 34 test case, phản ví dụ và kết quả JSON/log. Chạy `python verification/run_z3_demo.py --repeat 20` rồi `python verification/show_bmc_memory.py --feature all` để xem kết quả Z3 và RAM.

Tài liệu DOCX cùng tên báo cáo cũ được giữ làm tài liệu lưu trữ; các số liệu hiện hành lấy từ lần chạy mã nguồn và `results/verification_results.json`.
