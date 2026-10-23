# Báo cáo kiểm chứng mô hình HRM

Ngày chạy: 2026-10-19.

## Phạm vi

Đặc tả và sinh mô hình cho bốn luồng: đăng nhập, chấm công, nghỉ phép và tính lương. `specs/*.json` là nguồn dữ liệu để sinh mô hình Kripke Python và test case phủ chuyển tiếp. Safety hiện khai báo bằng `allowed_predecessors`: mỗi trạng thái quan trọng chỉ được đi vào từ nguồn hợp lệ. Checker suy ra tập cạnh cấm đầy đủ từ quy tắc này.

Pipeline sinh Python model và test case tĩnh từ `specs/*.json`. Checker đồ thị kiểm tra Safety và Liveness cho cả bốn mô hình; BMC-Z3 unroll transition relation và kiểm tra Safety/Liveness cho cả bốn chức năng. Test case kiểm tra mô hình, chưa tự gọi API.

Hai sơ đồ luồng, sơ đồ bộ nhớ và cách xem từng giá trị biến Z3 khi demo nằm tại [`DESIGN_FLOWS_MEMORY.md`](DESIGN_FLOWS_MEMORY.md). Sơ đồ nghiệp vụ là bản tổng quan; bốn mô hình được kiểm tra độc lập.

## Kết quả bốn mô hình

| Chức năng | State reachable | Transition | Test case | Safety | Liveness |
|---|---:|---:|---:|---|---|
| Đăng nhập | 8 | 10 | 12 | PASS; faulty DETECTED | PASS |
| Chấm công | 6 | 7 | 9 | PASS; faulty DETECTED | PASS |
| Nghỉ phép | 4 | 5 | 7 | PASS; faulty DETECTED | PASS |
| Tính lương | 4 | 4 | 6 | PASS; faulty DETECTED | PASS |
| **Tổng** | **22** | **26** | **34** | **4/4** | **4/4** |

Mỗi chức năng có test case phủ mọi transition reachable, một ca âm cho ràng buộc Safety và một witness path cho Liveness. Tổng cộng 26 ca transition, 4 ca Safety âm và 4 ca Liveness.

Safety chính:

- Đăng nhập: chỉ `AUTHENTICATING_ACTIVE → AUTHENTICATED` mới hợp lệ; thông tin sai và tài khoản chưa kích hoạt có nhánh riêng.
- Chấm công: `CHECKED_IN` chỉ đến từ `CHECKIN_VALID`; `CHECKED_OUT` chỉ đến từ `CHECKED_IN`.
- Nghỉ phép: `APPROVED` hoặc `REJECTED` chỉ đến từ `PENDING`.
- Lương: `NOT_CALCULATED → CALCULATING → DRAFT → PAID`; `PAID` được giữ nguyên.

## BMC bằng Z3 cho cả bốn chức năng

Z3 ánh xạ mỗi state trong JSON thành một mã nguyên và tạo biến `s0..sd` cho từng truy vấn độ sâu `d`. Mỗi biến được giới hạn trong miền state; `s0` bằng state đầu; từng cặp `(si,si+1)` phải thỏa một trong các cạnh của `R`. Ở cạnh cuối, truy vấn yêu cầu cặp state thuộc tập cạnh cấm. `SAT` trả các giá trị state thành trace phản ví dụ; `UNSAT` nghĩa là không có phản ví dụ ở độ sâu đó. Runner tăng dần từ 1 đến bound nên trace SAT đầu tiên là ngắn nhất.

Bound được suy ra bằng `k = |Reach(s0)|`, kết quả của DFS trong `reachable_states()`; không phải một số tùy ý. Safety: đường ngắn nhất từ state đầu đến nguồn cạnh cấm không lặp state, nên dài tối đa `k−1` cạnh; thêm cạnh lỗi là tối đa `k` cạnh. Do đó truy vấn độ sâu `1..k` đủ để phát hiện cạnh vi phạm. Một truy vấn độ sâu `d` có `d+1` lần xuất hiện state (`s0..sd`). Các bound hiện tại là Login 8, Attendance 6, Leave 4, Payroll 4.

Liveness `AF(target)` được kiểm bằng cách tìm đường dài `k` cạnh mà mọi state trong `s0..sk` tránh target. Các mô hình là Kripke total; trong `k+1` lần xuất hiện trên graph có `k` state phải có lặp state, sinh chu trình tránh target và một phản ví dụ vô hạn. `UNSAT` loại trừ chu trình đó. Nếu Z3 trả `UNKNOWN` do timeout thì chưa thể kết luận PASS.

Ví dụ truy vết cấu trúc property: Login `L1` khai báo tiền nhiệm duy nhất của `AUTHENTICATED` là `AUTHENTICATING_ACTIVE`; cạnh `UNAUTHENTICATED → AUTHENTICATED` bị đánh dấu cấm. Attendance `A1` yêu cầu `CHECKED_OUT` chỉ đến từ `CHECKED_IN`; cạnh faulty `AUTHENTICATED → CHECKED_OUT` tạo trace `READY → AUTHENTICATED → CHECKED_OUT`. Runner chèn cạnh faulty có chủ ý để kiểm tra Z3 có phát hiện được vi phạm hay không. `formula` trong JSON là mô tả, không phải CTL/LTL parser; encoding trực tiếp dùng `transitions`, `allowed_predecessors`/`forbidden_edges`, `starts` và `target_labels`.

Chạy 20 vòng lặp với Z3 5.3.1:

| Luồng | Bound | Safe Safety | Faulty Safety | Liveness CE | Counterexample faulty |
|---|---:|---|---|---|---|
| Login | 8 | UNSAT | SAT | UNSAT | `UNAUTHENTICATED → AUTHENTICATED` |
| Attendance | 6 | UNSAT | SAT | UNSAT | `READY → AUTHENTICATED → CHECKED_OUT` |
| Leave | 4 | UNSAT | SAT | UNSAT | `NO_REQUEST → APPROVED` |
| Payroll | 4 | UNSAT | SAT | UNSAT | `NOT_CALCULATED → CALCULATING → DRAFT → PAID → DRAFT` |

Với Safety, `UNSAT` nghĩa là không có trace đi qua cạnh cấm trong completeness bound; `SAT` trả trace của mô hình đã chèn lỗi. Với Liveness, Z3 tìm đường dài bằng số state reachable tránh target; `UNSAT` nghĩa là không có đường tránh dài như vậy. Các đặc tả có transition relation total, nên một đường tránh target dài hơn số state phải lặp lại state và tạo chu trình vô hạn. Checker đồ thị fixed point `AF` cũng trả PASS cho cả bốn chức năng.

## Sinh test case và kiểm thử bộ nhớ

Đã sinh 34 test case tĩnh từ cả bốn mô hình: phủ 26/26 transition, 4 ca kiểm tra cạnh Safety bị từ chối và 4 witness path cho Liveness. Danh sách nằm tại `generated/test_cases.json` và được lưu cùng lần chạy Z3 tại `generated/z3_demo_test_cases.json`.

Memory smoke test lặp 20 lần, số đo ghi tại `results/z3_bmc_memory.log` và `.json`. Lần đo của báo cáo này: 2026-10-19 15:53:52 UTC:

- Thời gian: 8.03 giây; CPU user/system: 7.94/0.08 giây.
- RSS tiến trình: 28,652 KiB lúc đầu, đỉnh 78,424 KiB, 70,108 KiB lúc cuối.
- Python heap `tracemalloc`: đỉnh 55,153 byte. RSS lớn hơn do tính cả bộ nhớ native của Z3.
- RAM hệ thống khả dụng: 6,969,464 KiB lúc đầu và 6,893,580 KiB lúc cuối; giá trị thay đổi theo hoạt động hệ thống.

Đây là phép đo smoke/stress lặp, ghi nhận RAM và thời gian trên máy chạy test. Nó không đặt ngưỡng phần cứng cố định và không chứng minh không rò rỉ bộ nhớ.

## Lệnh tái chạy

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r verification/requirements-z3.txt
python verification/run_all.py
python verification/run_z3_demo.py --repeat 20
python verification/show_bmc_memory.py --feature all
python -m unittest discover -s verification/tests -v
```

Kết quả tại thời điểm báo cáo này: `run_all.py` đã PASS cho 4 mô hình và 34 test case; sau khi bổ sung kiểm tra bound 8/6/4/4, toàn bộ 11/11 unit tests PASS. Z3 BMC được kiểm tra cho cả bốn mô hình ở Safety/Liveness và cả các cạnh cấm được chèn lỗi.

## Phiên kiểm thử bổ sung ngày 24/10/2026

Đã xuất bảng ánh xạ 26 transition sang mệnh đề Z3 và 12 truy vấn SMT-LIB từ cùng hàm tạo ràng buộc của checker. Nạp lại 12/12 file trên đĩa cho đúng SAT/UNSAT và 4/4 fingerprint đặc tả khớp; bộ unit test hiện có 12/12 PASS. Lần chạy BMC-Z3 riêng 20 vòng đạt PASS; RSS tiến trình trước/sau/đỉnh 27.980/68.420/68.420 KiB, thời gian 7,611546 giây trên máy kiểm thử. Xem [`biên bản test`](BIEN_BAN_KIEM_THU_2026-10-24.md), [`bản Word`](Bien_ban_kiem_thu_Kripke_BMC_HRM_2026-10-24.docx), [`minh chứng Z3`](../generated/z3_evidence/README.md) và [`log mới`](../results/teacher_demo_2026-10-24/z3_bmc_memory.log). Số đo cũ phía trên vẫn là ảnh chụp của ngày 19/10, không bị ghi đè.

## Giới hạn

- Kết quả áp dụng cho mô hình hữu hạn và các ràng buộc đã đặc tả; chưa chứng minh code ứng dụng hoặc các dịch vụ database chạy đúng.
- Chuỗi `formula` trong JSON giúp ghi tài liệu; chương trình kiểm tra trực tiếp `allowed_predecessors`, edges, starts và target labels, không parse CTL tổng quát.
- Chưa mô hình hóa toàn bộ phân quyền, ngày nghỉ, timeout/retry, lỗi database và dữ liệu lương bất thường.
- Attendance model yêu cầu check-out sau check-in; route ứng dụng hiện cần được kiểm tra/điều chỉnh để thực thi điều kiện đó.
