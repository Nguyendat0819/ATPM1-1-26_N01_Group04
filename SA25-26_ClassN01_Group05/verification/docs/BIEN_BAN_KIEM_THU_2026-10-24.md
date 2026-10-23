# BIÊN BẢN KIỂM THỬ — MÔ HÌNH KRIPKE VÀ BMC-Z3 CHO HRM

**Nhóm:** SA25-26_ClassN01_Group05  
**Ngày kiểm thử:** 24/10/2026, giờ địa phương UTC+07; log Z3 ghi 23/10/2026 17:16:01 UTC.  
**Môi trường:** Linux 7.0.0-38-generic x86_64; Python 3.12.3 trong `.venv`; Z3 5.3.1.  
**Phạm vi:** bốn mô hình đăng nhập, chấm công, nghỉ phép, tính lương; sinh test tĩnh; kiểm tra đồ thị; BMC-Z3; phép đo RAM 20 vòng. Không kiểm thử HTTP API, database hay giao diện.

## 1. Căn cứ, dữ liệu đầu vào và tiêu chí đạt

Nguồn đầu vào là bốn file [`specs/*.json`](../specs/), do nhóm **trừu tượng hóa thủ công** từ các route HRM được ghi trong từng đặc tả. Mỗi file khai báo `states`, state đầu, `transitions`, `labels`, điều kiện Safety (`allowed_predecessors`), Liveness (`starts`, `target_labels`) và một `faulty_transition` cố ý. Bộ sinh **không đọc mã Express để suy luận state tự động**. Chuỗi `formula` trong JSON dùng để trình bày, không phải công thức CTL được parser tổng quát thực thi.

Tiêu chí đạt: cả 4 đặc tả sinh được mô hình và test case; phủ 100% các transition hợp lệ đã khai báo; mô hình đúng không có phản ví dụ Safety/Liveness; khi chèn một cạnh cấm, Z3 trả `SAT` và trace tới đúng cạnh đó; toàn bộ unit test và truy vấn SMT-LIB nạp lại khớp. `UNKNOWN`, lỗi thực thi hoặc fingerprint đặc tả không khớp đều **không** được coi là đạt. Phép đo RAM chỉ ghi số thực tế, không đặt ngưỡng cứng.

## 2. Giải đáp ba câu hỏi của giảng viên

**Bound lấy từ đâu?** Với mỗi mô hình, tính `Reach(s₀)` bằng duyệt đồ thị từ state đầu, rồi đặt `k = |Reach(s₀)|`. Kết quả: login 8, attendance 6, leave 4, payroll 4. Nếu một cạnh cấm reachable, đường ngắn nhất tới nguồn cạnh đó có tối đa `k−1` cạnh, thêm cạnh lỗi là tối đa `k`; vì thế checker kiểm Safety từng độ sâu `1..k`. Truy vấn độ sâu `d` dùng `d+1` biến state. Đối với `AF(target)`, tìm đường dài `k` cạnh mà mọi state đều tránh target; trên mô hình hữu hạn có quan hệ chuyển tiếp total, đường này buộc lặp state và suy ra chu trình tránh target. Nếu truy vấn đó `UNSAT`, không có phản ví dụ Liveness theo lập luận này. Đây là bound của **mô hình đã khai báo**, không phải của toàn bộ phần mềm HRM.

**Dựa vào đâu sinh mô hình/test?** [`generate_artifacts.py`](../generate_artifacts.py) đọc `specs/*.json` để sinh mã mô hình Kripke, mô hình lỗi có một cạnh cấm, và [`test_cases.md`](../generated/test_cases.md)/`test_cases.json`. Mỗi transition hợp lệ có một ca tĩnh; mỗi chức năng có thêm một ca âm Safety và một witness Liveness. Tổng: 26 + 4 + 4 = **34 ca tĩnh**. Đây là dữ liệu mô hình hóa có chủ ý, không phải dữ liệu nhân sự đo từ hệ thống thật.

**Z3 biết cấu trúc từng chuyển tiếp bằng cách nào?** Mỗi state được mã hóa thành số nguyên theo thứ tự trong JSON. Cạnh `u → v` ở bước `i` trở thành `state_i = code(u) ∧ state_(i+1) = code(v)`; phép `Or` của tất cả cạnh tạo quan hệ `R`. Solver thêm điều kiện state đầu, miền mã state và `R` cho từng bước. Với Safety, thêm điều kiện cạnh cuối nằm trong tập cạnh cấm suy từ `allowed_predecessors`. Với Liveness, ràng buộc mọi state trên trace tránh `target_labels`. [`README minh chứng Z3`](../generated/z3_evidence/README.md) liệt kê từng cạnh và mã tương ứng; 12 file `.smt2` là truy vấn thực được xuất từ cùng hàm tạo ràng buộc mà checker dùng, không phải công thức vẽ lại bằng tay. File Safety chuẩn ở độ sâu `k` chỉ là một truy vấn đại diện; kết luận tổng thể dựa trên toàn bộ độ sâu `1..k`.

## 3. Lệnh thực thi và kết quả ghi nhận

Chạy từ thư mục gốc `SA25-26_ClassN01_Group05` với `.venv` đã cài `verification/requirements-z3.txt`:

```bash
.venv/bin/python -B verification/generate_artifacts.py
.venv/bin/python -B verification/run_all.py
.venv/bin/python -B verification/export_z3_evidence.py
.venv/bin/python -B verification/replay_z3_evidence.py
.venv/bin/python -B -m unittest discover -s verification/tests -v
.venv/bin/python -B verification/run_z3_demo.py --repeat 20 --results-dir verification/results/teacher_demo_2026-10-24
.venv/bin/python -B verification/show_bmc_memory.py --feature all --results verification/results/teacher_demo_2026-10-24/z3_bmc_memory.json
```

| Mã | Nội dung / kỳ vọng | Kết quả quan sát | Đánh giá |
|---|---|---|---|
| TC-01 | Đọc 4 JSON, sinh 4 mô hình và 34 ca tĩnh | `Generated 4 models and 34 static test cases` | PASS |
| TC-02 | Phủ mọi transition hợp lệ; Safety/Liveness đồ thị đạt | 26/26 transition; 4/4 mô hình chuẩn PASS, 4/4 mô hình lỗi DETECTED, 4/4 Liveness PASS | PASS |
| TC-03 | Bound theo state reachable, không gán tùy ý | login 8; attendance 6; leave 4; payroll 4 | PASS |
| TC-04 | BMC Safety trên mô hình chuẩn | `UNSAT` ở mọi độ sâu `1..k` của cả 4 mô hình | PASS |
| TC-05 | BMC Safety trên mô hình chèn cạnh lỗi | `SAT` ở cả 4; trace và độ sâu xem bảng dưới | PASS |
| TC-06 | BMC Liveness tìm đường tránh target dài `k` | `UNSAT` cho cả 4 mô hình | PASS |
| TC-07 | Nạp lại SMT-LIB từ đĩa, so status và fingerprint | 12/12 truy vấn SAT/UNSAT khớp; 4/4 fingerprint khớp | PASS |
| TC-08 | Chạy unit test sinh mô hình, bound, Z3 và memory view | 12 tests, 0 failures, 0 errors | PASS |
| TC-09 | Chạy 20 vòng, ghi RSS/heap/thời gian CPU | Overall PASS; 20 mẫu RSS; số đo ở mục 5 | PASS |
| TC-10 | Giải mã trace Z3 và kiểm tra kết quả không stale | Viewer hiển thị mã state, cạnh vi phạm; unit test phát hiện log/spec lệch | PASS |

`34 ca tĩnh`, `12 unit test` và `20 lần lặp` là ba số đếm **khác nhau**; không cộng chúng thành một chỉ tiêu test.

## 4. Kết quả theo từng chức năng

| Chức năng | State / transition / ca tĩnh | Bound k | Safety chuẩn / lỗi | Liveness CE | Phản ví dụ ngắn nhất của model lỗi |
|---|---:|---:|---|---|---|
| Đăng nhập | 8 / 10 / 12 | 8 | UNSAT / SAT (d=1) | UNSAT | `UNAUTHENTICATED → AUTHENTICATED` |
| Chấm công | 6 / 7 / 9 | 6 | UNSAT / SAT (d=2) | UNSAT | `READY → AUTHENTICATED → CHECKED_OUT` |
| Nghỉ phép | 4 / 5 / 7 | 4 | UNSAT / SAT (d=1) | UNSAT | `NO_REQUEST → APPROVED` |
| Tính lương | 4 / 4 / 6 | 4 | UNSAT / SAT (d=4) | UNSAT | `NOT_CALCULATED → CALCULATING → DRAFT → PAID → DRAFT` |

Ví dụ minh họa cho thầy: ở login, state `UNAUTHENTICATED` có mã 0, `AUTHENTICATED` có mã 6. Đặc tả chỉ cho phép `AUTHENTICATING_ACTIVE → AUTHENTICATED`, nên truy vấn Safety trên model cố ý thêm cạnh `0 → 6` là `SAT` và giải mã thành phản ví dụ một bước. Ở attendance, `CHECKED_OUT` chỉ được vào từ `CHECKED_IN`; cạnh lỗi `AUTHENTICATED → CHECKED_OUT` chỉ reachable sau `READY → AUTHENTICATED`, nên phản ví dụ có hai cạnh. Các mã/cạnh đầy đủ có trong [`bảng ánh xạ`](../generated/z3_evidence/README.md).

## 5. Biên bản đo RAM và thời gian

Lần chạy Z3 ghi lúc **23/10/2026 17:16:01 UTC**, tương đương **24/10/2026 00:16:01 UTC+07**, với Z3 5.3.1 và 20 vòng lặp. RSS tiến trình trước/sau/đỉnh: **27.980 / 68.420 / 68.420 KiB**. Python heap hiện tại/đỉnh do `tracemalloc` đo: **16.478 / 55.507 byte**. `MemAvailable` toàn hệ thống trước/sau: **6.767.480 / 6.764.228 KiB**. Wall time **7,611546 giây**; CPU user/system **7,581395 / 0,062217 giây**. Log lưu đủ 20 mẫu RSS, không chỉ giá trị đỉnh.

Đây là **số đo thật của tiến trình chạy trên máy này**, nhưng dữ liệu state/transition là mô hình trừu tượng. RSS gồm Python và thư viện native Z3; `tracemalloc` không đo toàn bộ native memory; `MemAvailable` chịu tác động của hệ thống. Một phép smoke test 20 vòng không chứng minh không có memory leak hoặc hiệu năng trên môi trường khác.

## 6. Tệp minh chứng và khả năng tái lập

- [`specs/`](../specs/): đầu vào đặc tả bốn chức năng.
- [`generated/test_cases.md`](../generated/test_cases.md): 34 ca tĩnh, điều kiện đầu vào/đường đi/kỳ vọng.
- [`DESIGN_FLOWS_MEMORY.md`](DESIGN_FLOWS_MEMORY.md): hai sơ đồ luồng và sơ đồ bộ nhớ phục vụ phần trình bày.
- [`results/verification_results.json`](../results/verification_results.json): kết quả checker đồ thị.
- [`generated/z3_evidence/README.md`](../generated/z3_evidence/README.md): bảng state-code, từng transition, bound, các đường liên kết 12 SMT-LIB.
- [`generated/z3_evidence/summary.json`](../generated/z3_evidence/summary.json): kết quả máy đọc, kèm SHA-256 chuẩn hóa cho từng spec.
- [`results/teacher_demo_2026-10-24/z3_bmc_memory.log`](../results/teacher_demo_2026-10-24/z3_bmc_memory.log) và [`z3_bmc_memory.json`](../results/teacher_demo_2026-10-24/z3_bmc_memory.json): kết quả chạy 20 vòng và số đo.

SHA-256 của `summary.json`: `da1691a6e15a28a0de3054dd56c2ff40bef443770f8acfb96b57cd97d23f5e1f`. SHA-256 của `z3_bmc_memory.json` lần này: `5e9e7ebf8dff936b4e93cbe168c901657ab55c238b88118df1bab0434ba6107f`. Nguồn code ở thời điểm test có HEAD `9edc6cf` **và thay đổi chưa commit**; vì vậy khi đối chiếu nên dùng các file kết quả và fingerprint đặc tả, không xem HEAD là toàn bộ phiên bản đã test.

## 7. Kết luận và giới hạn

**Kết luận:** bộ kiểm chứng đạt các tiêu chí test ở mục 1 trong phạm vi **bốn mô hình Kripke đã đặc tả**. BMC-Z3 phát hiện được bốn lỗi chuyển tiếp cố ý; các truy vấn SMT-LIB có thể nạp lại độc lập, và bound có cơ sở từ số state reachable.

**Chưa được chứng minh:** hành vi thực tế của Express/database/frontend, sự khớp hoàn toàn giữa route và đặc tả thủ công, liên kết trạng thái giữa bốn dịch vụ, và các trường hợp dữ liệu nhân sự thật. `SAT` ở model lỗi là minh chứng cho **năng lực phát hiện của checker**, không phải bằng chứng hệ thống sản phẩm hiện đang có chính lỗi ấy. Muốn kết luận về mã ứng dụng, cần đối chiếu yêu cầu với route và bổ sung kiểm thử tích hợp/API bằng dữ liệu được kiểm soát.
