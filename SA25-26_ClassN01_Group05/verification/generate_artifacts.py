"""Sinh mô hình Kripke và test case tĩnh từ các đặc tả JSON của HRM."""
from collections import deque
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC_DIR = ROOT / "specs"
MODEL_DIR = ROOT / "models"
FAULTY_DIR = ROOT / "faulty_models"
GENERATED_DIR = ROOT / "generated"


def spec_fingerprint(spec):
    """Tạo mã SHA-256 ổn định để phát hiện kết quả BMC cũ so với đặc tả hiện tại."""
    encoded = json.dumps(spec, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def load_specs():
    """Đọc, kiểm tra và trả về toàn bộ đặc tả chức năng trong thư mục specs."""
    specs = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(SPEC_DIR.glob("*.json"))]
    if not specs:
        raise ValueError(f"No model specifications found in {SPEC_DIR}")
    names = [spec["name"] for spec in specs]
    if len(names) != len(set(names)):
        raise ValueError("Model names must be unique")
    for spec in specs:
        validate_spec(spec)
    return specs


def forbidden_edges_for_spec(spec):
    """Quy đổi ràng buộc Safety thành danh sách cạnh mà checker phải xem là vi phạm."""
    safety = spec["properties"]["safety"]
    if "forbidden_edges" in safety:
        return [tuple(edge) for edge in safety["forbidden_edges"]]
    if "allowed_predecessors" in safety:
        states = {state["id"] for state in spec["states"]}
        return [
            (source, target)
            for target, allowed in safety["allowed_predecessors"].items()
            for source in sorted(states - set(allowed))
        ]
    return [tuple(safety["forbidden_edge"])]


def validate_spec(spec):
    """Bảo đảm đặc tả tạo thành Kripke hợp lệ trước khi sinh model và test."""
    source = spec.get("implementation_source")
    if not source or not (ROOT.parent / source).is_file():
        raise ValueError(f"{spec['name']}: implementation source file is missing")
    states = spec["states"]
    state_ids = [state["id"] for state in states]
    if len(state_ids) != len(set(state_ids)):
        raise ValueError(f"{spec['name']}: state IDs must be unique")
    if sum(bool(state.get("initial")) for state in states) != 1:
        raise ValueError(f"{spec['name']}: exactly one initial state is required")
    known = set(state_ids)
    edges = [tuple(edge) for edge in spec["transitions"]]
    if len(edges) != len(set(edges)):
        raise ValueError(f"{spec['name']}: transitions must be unique")
    # Transition chỉ được nối các state đã khai báo để tránh mô hình tham chiếu nhầm state.
    if any(source not in known or target not in known for source, target in edges):
        raise ValueError(f"{spec['name']}: transition references an unknown state")
    safety = spec["properties"]["safety"]
    forbidden = tuple(safety["forbidden_edge"])
    forbidden_edges = set(forbidden_edges_for_spec(spec))
    faulty = tuple(spec["faulty_transition"])
    if forbidden_edges.intersection(edges) or faulty not in forbidden_edges or faulty != forbidden:
        raise ValueError(f"{spec['name']}: safe and faulty transition declarations conflict")
    if any(source not in known or target not in known for source, target in forbidden_edges):
        raise ValueError(f"{spec['name']}: safety property references an unknown state")
    for target, allowed in safety.get("allowed_predecessors", {}).items():
        if target not in known or not set(allowed).issubset(known):
            raise ValueError(f"{spec['name']}: allowed predecessor references an unknown state")
    labels = {label for state in states for label in state.get("labels", [])}
    liveness = spec["properties"]["liveness"]
    if not set(liveness["target_labels"]).issubset(labels):
        raise ValueError(f"{spec['name']}: liveness target label is not defined")
    if not set(liveness["starts"]).issubset(known):
        raise ValueError(f"{spec['name']}: liveness start state is not defined")
    # Kripke cần quan hệ chuyển tiếp total: mọi state đều phải có ít nhất một bước kế tiếp.
    outgoing = {source for source, _ in edges}
    deadlocks = known - outgoing
    if deadlocks:
        raise ValueError(f"{spec['name']}: every Kripke state must have a successor: {sorted(deadlocks)}")
    adjacency = {state: set() for state in known}
    for source, target in edges:
        adjacency[source].add(target)
    reached = set()
    pending = [next(state["id"] for state in states if state.get("initial"))]
    while pending:
        state = pending.pop()
        if state not in reached:
            reached.add(state)
            pending.extend(adjacency[state] - reached)
    if reached != known:
        raise ValueError(f"{spec['name']}: unreachable states: {sorted(known - reached)}")


def render_safe_model(spec):
    """Kết xuất Python builder cho mô hình đúng; JSON vẫn là nguồn đặc tả chính."""
    lines = [
        f'"""Generated from verification/specs/{spec["name"]}.json; edit the spec instead."""',
        "from pathlib import Path",
        "import sys",
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / \"lib\"))",
        "from kripke_adapter import KripkeStructure",
        "",
        "def build_model():",
        "    model = KripkeStructure()",
    ]
    for state in spec["states"]:
        lines.append(
            f"    model.add_state({state['id']!r}, {state.get('labels', [])!r}, {bool(state.get('initial'))!r})"
        )
    for source, target in spec["transitions"]:
        lines.append(f"    model.add_transition({source!r}, {target!r})")
    lines.extend(["    return model", ""])
    return "\n".join(lines)


def render_faulty_model(spec):
    """Sinh builder mô hình thử lỗi bằng cách thêm đúng cạnh vi phạm đã khai báo."""
    source, target = spec["faulty_transition"]
    return "\n".join([
        f'"""Generated faulty model for {spec["name"]}; used to check counterexample detection."""',
        "from pathlib import Path",
        "import sys",
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1] / \"models\"))",
        f"from {spec['name']}_kripke import build_model as build_safe_model",
        "",
        "def build_model():",
        "    model = build_safe_model()",
        f"    model.add_transition({source!r}, {target!r})",
        "    return model",
        "",
    ])


def shortest_paths(model):
    """Tìm đường ngắn nhất từ state đầu tới mỗi state để làm tiền tố cho test case."""
    paths = {}
    queue = deque([[state] for state in sorted(model.initial)])
    while queue:
        path = queue.popleft()
        state = path[-1]
        if state in paths:
            continue
        paths[state] = path
        for target in sorted(model.transitions.get(state, set())):
            if target not in paths:
                queue.append(path + [target])
    return paths


def shortest_path_to_label(model, start, target_labels):
    """Tìm witness path ngắn nhất từ state bắt đầu tới state mang nhãn đích Liveness."""
    target_labels = set(target_labels)
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        state = path[-1]
        if target_labels.intersection(model.labels.get(state, set())):
            return path
        for target in sorted(model.transitions.get(state, set())):
            if target not in seen:
                seen.add(target)
                queue.append(path + [target])
    return None


def case_steps(state_path):
    """Chuyển danh sách state thành các bước chuyển dạng chuỗi để đưa vào báo cáo test."""
    return [f"{source} -> {target}" for source, target in zip(state_path, state_path[1:])]


def render_test_cases_markdown(test_cases):
    """Trình bày danh sách test case sinh ra thành bảng Markdown dễ đọc."""
    coverage_names = {
        "transition": "Phủ chuyển tiếp",
        "safety_constraint": "Kiểm tra ràng buộc an toàn (Safety)",
        "liveness_witness": "Đường chứng kiến tính sống (Liveness)",
    }
    rows = [
        "# Ca kiểm thử tĩnh được sinh từ mô hình Kripke",
        "",
        "Các ca dưới đây kiểm tra đường đi trạng thái, chuyển tiếp và thuộc tính trên mô hình Kripke. Đây là kiểm thử tĩnh ở mức mô hình; chương trình không gửi yêu cầu HTTP đến API HRM.",
        "",
        "Tên state, ID kiểm thử và đường dẫn mã nguồn được giữ nguyên để có thể đối chiếu trực tiếp với đặc tả JSON và repository.",
        "",
        "| ID | Chức năng | Mã nguồn triển khai | Loại kiểm thử / độ phủ | Đường trạng thái | Kết quả mong đợi |",
        "|---|---|---|---|---|---|",
    ]
    for case in test_cases:
        path = " → ".join(case["state_path"])
        coverage = coverage_names.get(case["coverage"], case["coverage"])
        if case["coverage"] == "transition":
            expected = f"Đi đến trạng thái {case['transition'][1]} theo chuyển tiếp đã khai báo."
        elif case["coverage"] == "safety_constraint":
            source, target = case["transition"]
            expected = f"Từ chối chuyển tiếp {source} → {target} vì vi phạm ràng buộc {case['property_id']}."
        elif case["coverage"] == "liveness_witness":
            labels = ", ".join(case["target_labels"])
            expected = f"Đạt trạng thái mang một trong các nhãn mục tiêu: {labels}."
        else:
            expected = case["expected"]
        expected = expected.replace("|", "\\|")
        rows.append(
            f"| {case['id']} | {case['feature']} | `{case['implementation_source']}` | {coverage} | `{path}` | {expected} |"
        )
    return "\n".join(rows) + "\n"


def generate_artifacts():
    """Sinh safe/faulty model, test phủ transition, test Safety âm và witness Liveness."""
    MODEL_DIR.mkdir(exist_ok=True)
    FAULTY_DIR.mkdir(exist_ok=True)
    GENERATED_DIR.mkdir(exist_ok=True)
    specs = load_specs()
    test_cases = []
    for spec in specs:
        (MODEL_DIR / f"{spec['name']}_kripke.py").write_text(render_safe_model(spec), encoding="utf-8")
        (FAULTY_DIR / f"{spec['name']}_faulty.py").write_text(render_faulty_model(spec), encoding="utf-8")
        model = build_model_from_spec(spec)
        paths = shortest_paths(model)
        reachable = model.reachable_states()
        # Mỗi cạnh nghiệp vụ được biến thành một test riêng, với đường đi từ state đầu.
        for index, (source, target) in enumerate(spec["transitions"], start=1):
            if source not in paths:
                continue
            state_path = paths[source] + [target]
            test_cases.append({
                "id": f"GEN-{spec['name'].upper()}-{index:02d}",
                "feature": spec["title"],
                "implementation_source": spec["implementation_source"],
                "coverage": "transition",
                "transition": [source, target],
                "state_path": state_path,
                "steps": case_steps(state_path),
                "expected_result": "accepted",
                "expected": f"Reach {target} through the declared transition.",
            })
        safety = spec["properties"]["safety"]
        source, target = spec["faulty_transition"]
        if source not in paths:
            raise ValueError(f"{spec['name']}: faulty transition source is unreachable")
        violation_path = paths[source] + [target]
        test_cases.append({
            "id": f"GEN-{spec['name'].upper()}-SAFETY-01",
            "feature": spec["title"],
            "implementation_source": spec["implementation_source"],
            "coverage": "safety_constraint",
            "property_id": safety["id"],
            "transition": [source, target],
            "state_path": violation_path,
            "steps": case_steps(violation_path),
            "expected_result": "rejected",
            "expected": f"Reject {source} -> {target}; it violates {safety['id']}.",
        })
        liveness = spec["properties"]["liveness"]
        for start_index, start in enumerate(liveness["starts"], start=1):
            witness = shortest_path_to_label(model, start, liveness["target_labels"])
            if witness is None:
                raise ValueError(f"{spec['name']}: liveness target is unreachable from {start}")
            test_cases.append({
                "id": f"GEN-{spec['name'].upper()}-LIVENESS-{start_index:02d}",
                "feature": spec["title"],
                "implementation_source": spec["implementation_source"],
                "coverage": "liveness_witness",
                "property_id": liveness["id"],
                "start_state": start,
                "target_labels": liveness["target_labels"],
                "state_path": witness,
                "steps": case_steps(witness),
                "expected_result": "eventually_reaches_target",
                "expected": f"Reach a state labelled with {', '.join(liveness['target_labels'])}.",
            })
        if set(paths) != reachable:
            raise ValueError(f"{spec['name']}: generated paths do not cover all reachable states")
    (GENERATED_DIR / "test_cases.json").write_text(
        json.dumps(test_cases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (GENERATED_DIR / "test_cases.md").write_text(
        render_test_cases_markdown(test_cases), encoding="utf-8"
    )
    return specs, test_cases


def build_model_from_spec(spec):
    """Tạo đối tượng Kripke trong bộ nhớ trực tiếp từ một đặc tả JSON."""
    sys_path = str(ROOT / "lib")
    import sys
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from kripke_adapter import KripkeStructure

    model = KripkeStructure()
    for state in spec["states"]:
        model.add_state(state["id"], state.get("labels", []), state.get("initial", False))
    for source, target in spec["transitions"]:
        model.add_transition(source, target)
    return model


if __name__ == "__main__":
    generated_specs, cases = generate_artifacts()
    print(f"Generated {len(generated_specs)} models and {len(cases)} static test cases.")
