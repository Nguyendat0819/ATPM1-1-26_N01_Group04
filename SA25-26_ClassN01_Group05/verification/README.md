# HRM: mô hình Kripke, test sinh và BMC-Z3

Thư mục này đặc tả bốn luồng HRM: đăng nhập, chấm công, nghỉ phép và tính lương. Mô hình kiểm chứng hành vi trạng thái, không thay thế kiểm thử tích hợp cho các dịch vụ Express, database hoặc frontend.

Sơ đồ hai luồng, ánh xạ đặc tả → test case → BMC, cấu trúc dữ liệu trong bộ nhớ và hướng dẫn xem từng biến Z3 nằm ở [`docs/DESIGN_FLOWS_MEMORY.md`](docs/DESIGN_FLOWS_MEMORY.md).

## Chuỗi sinh

`specs/*.json` là nguồn trạng thái, nhãn, trạng thái đầu, chuyển tiếp và thuộc tính. Bộ sinh tạo `models/*_kripke.py`, `faulty_models/*_faulty.py`, JSON test case và bảng Markdown tại `generated/test_cases.md`. Bộ test tĩnh có ca phủ từng transition hợp lệ, ca âm cho mỗi ràng buộc Safety và witness path cho từng thuộc tính Liveness. Các ca này kiểm tra mô hình trạng thái, chưa gọi HTTP API.

`allowed_predecessors` trong safety chỉ định trạng thái nào được phép đi vào một trạng thái quan trọng. Bộ sinh suy ra các cạnh cấm từ quy tắc đó. Các công thức dạng `AG(...)`/`AF(...)` là biểu diễn tài liệu; checker hiện dùng các cấu trúc state, edge, predecessor, start và target trong JSON, không phân tích cú pháp CTL tổng quát.

## Chạy kiểm chứng bốn mô hình

Yêu cầu Python 3.9 trở lên; chỉ lệnh `run_all.py` không cần package ngoài:

```bash
python3 verification/run_all.py
```

Để chạy full unittest (bao gồm Z3 tests), tạo môi trường ảo trên Ubuntu rồi cài solver:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r verification/requirements-z3.txt
python -m unittest discover -s verification/tests -v
```

Safety tìm đường phản ví dụ tới bất kỳ cạnh cấm trong giới hạn số trạng thái reachable. Với transition system hữu hạn, nếu có cạnh cấm reachable thì có đường đơn không quá số trạng thái trước khi đi qua cạnh đó. Liveness được kiểm bằng fixed point `AF` trên đồ thị reachable và có phép đối chiếu bounded trong Z3.

## Chạy BMC bằng Z3 cho cả bốn chức năng

Chạy Z3 BMC cho đăng nhập, chấm công, nghỉ phép và tính lương; mặc định lặp phép đo RAM 20 lần:

```bash
python verification/run_z3_demo.py --repeat 20
python verification/show_bmc_memory.py --feature all
```

Thêm `--feature login`, `attendance`, `leave` hoặc `payroll` để chỉ xem snapshot biến trạng thái của một chức năng. Lệnh xem đọc lần chạy Z3 gần nhất trong `results/z3_bmc_memory.json`; nếu mô hình đã đổi, chạy lại demo trước. Không cài `z3-solver` bằng `pip` vào Python hệ thống Ubuntu khi gặp lỗi `externally-managed-environment`.

Mỗi time-step được biểu diễn bằng một biến trạng thái số nguyên. Z3 nhận state đầu, miền state và quan hệ chuyển tiếp. Với Safety, solver hỏi có trace nào đi qua cạnh cấm không: mô hình đúng phải `UNSAT`, mô hình lỗi phải `SAT` và trả counterexample. Với Liveness, solver hỏi có đường dài bằng số state reachable mà tránh toàn bộ target không. Do Kripke relation ở đây total và hữu hạn, một đường dài như vậy lặp lại state và chứng minh tồn tại vòng lặp vô hạn tránh target; `UNSAT` xác nhận không có phản ví dụ Liveness trong mô hình.

## Log và số đo RAM

Lệnh demo ghi:

- `results/z3_bmc_memory.log`: kết quả ngắn, counterexample, thời gian và số đo RAM.
- `results/z3_bmc_memory.json`: kết quả đầy đủ và mẫu RSS/heap qua từng vòng lặp.
- `generated/test_cases.json`: test case tĩnh được sinh từ cả bốn đặc tả.
- `generated/z3_demo_test_cases.json`: bản test case được lưu cùng kết quả lần chạy Z3 gần nhất.

Log đo RSS tiến trình (bao gồm phần native của Z3), heap Python bằng `tracemalloc`, RAM hệ thống còn khả dụng từ `/proc/meminfo`, thời gian và CPU. Đây là memory smoke test lặp 20 lần để ghi nhận mức sử dụng; nó không chứng minh không rò rỉ bộ nhớ và không áp ngưỡng pass/fail phần cứng cố định.

## Đọc kết quả

- `PASS`: cả bốn mô hình đúng không có phản ví dụ Safety/Liveness trong bound đầy đủ, cả bốn mô hình lỗi đều sinh phản ví dụ.
- `DETECTED`/`SAT`: tìm được phản ví dụ trong mô hình cố ý có lỗi.
- `UNSAT`: không có trace vi phạm trong bound đã kiểm.
- Test case JSON là test tĩnh mức mô hình; unit test của service duyệt nghỉ phép là bộ riêng và dùng mock.
