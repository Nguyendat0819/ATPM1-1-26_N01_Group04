"""Mã hóa transition system HRM hữu hạn thành truy vấn BMC cho Z3."""
from z3 import And, Int, Not, Or, Solver, sat, unsat


def reachable_states(initial, transitions):
    """Tính tập state reachable từ initial; dùng để xác định kích thước bound hữu hạn."""
    reached = set()
    pending = [initial]
    while pending:
        state = pending.pop()
        if state in reached:
            continue
        reached.add(state)
        pending.extend(target for source, target in transitions if source == state and target not in reached)
    return reached


def build_safety_query(states, transitions, initial, forbidden_edges, depth, timeout_ms=5000):
    """Trả truy vấn và biến trace cho đúng `depth` cạnh; `depth` phải dương."""
    if depth < 1:
        raise ValueError("Safety query depth must be positive")
    state_code = {state: index for index, state in enumerate(states)}
    encoded_edges = [(state_code[source], state_code[target]) for source, target in transitions]
    encoded_forbidden = [(state_code[source], state_code[target]) for source, target in forbidden_edges]
    solver = Solver()
    solver.set(timeout=timeout_ms)
    trace = [Int(f"state_{depth}_{index}") for index in range(depth + 1)]
    for variable in trace:
        solver.add(Or([variable == code for code in state_code.values()]))
    solver.add(trace[0] == state_code[initial])

    for index in range(depth):
        solver.add(Or([
            And(trace[index] == source, trace[index + 1] == target)
            for source, target in encoded_edges
        ]))
    solver.add(Or([
        And(trace[-2] == source, trace[-1] == target)
        for source, target in encoded_forbidden
    ]))
    return solver, trace, state_code


def find_counterexample(states, transitions, initial, forbidden_edges, bound, timeout_ms=5000):
    """Tăng dần độ sâu tới bound, hỏi Z3 có trace đi qua cạnh cấm hay không."""
    # Tăng depth từng bước nên SAT đầu tiên trả về phản ví dụ ngắn nhất theo số cạnh.
    for depth in range(1, bound + 1):
        solver, trace, state_code = build_safety_query(
            states, transitions, initial, forbidden_edges, depth, timeout_ms
        )

        result = solver.check()
        if result == sat:
            model = solver.model()
            reverse_codes = {code: state for state, code in state_code.items()}
            return {
                "status": "sat",
                "depth": depth,
                "path": [reverse_codes[model.eval(variable).as_long()] for variable in trace],
            }
        if result == unsat:
            continue
        return {"status": "unknown", "depth": depth, "reason": solver.reason_unknown()}

    return {"status": "unsat", "bound": bound, "path": None}


def build_liveness_query(states, transitions, start, target_states, bound, timeout_ms=5000, start_index=0):
    """Trả truy vấn tránh target qua `bound` cạnh; các state đầu và đích phải đã khai báo."""
    state_code = {state: index for index, state in enumerate(states)}
    encoded_edges = [(state_code[source], state_code[target]) for source, target in transitions]
    encoded_targets = [state_code[state] for state in target_states]
    solver = Solver()
    solver.set(timeout=timeout_ms)
    trace = [Int(f"liveness_{start_index}_{index}") for index in range(bound + 1)]
    for variable in trace:
        solver.add(Or([variable == code for code in state_code.values()]))
        solver.add(Not(Or([variable == code for code in encoded_targets])))
    solver.add(trace[0] == state_code[start])
    for index in range(bound):
        solver.add(Or([
            And(trace[index] == source, trace[index + 1] == target)
            for source, target in encoded_edges
        ]))
    return solver, trace, state_code


def find_liveness_counterexample(states, transitions, starts, target_states, bound, timeout_ms=5000):
    """Tìm đường tránh target dài bound; trên đồ thị hữu hạn total, đường đó lặp state và tạo chu trình."""
    state_code = {state: index for index, state in enumerate(states)}
    if not starts or not target_states:
        raise ValueError("Liveness checking requires start and target states")
    if bound < 1:
        raise ValueError("Liveness bound must be positive")
    if any(state not in state_code for state in [*starts, *target_states]):
        raise ValueError("Liveness property references an unknown state")

    reached = reachable_states(starts[0], transitions)
    for start in starts[1:]:
        reached.update(reachable_states(start, transitions))
    # AF reasoning ở đây giả định Kripke total; deadlock sẽ làm kết luận chu trình không hợp lệ.
    deadlocks = {
        state for state in reached
        if not any(source == state for source, _ in transitions)
    }
    if deadlocks:
        raise ValueError(f"AF checking requires a total transition relation; deadlocks: {sorted(deadlocks)}")

    for start_index, start in enumerate(starts):
        solver, trace, state_code = build_liveness_query(
            states, transitions, start, target_states, bound, timeout_ms, start_index
        )

        result = solver.check()
        if result == sat:
            model = solver.model()
            reverse_codes = {code: state for state, code in state_code.items()}
            return {
                "status": "sat",
                "start": start,
                "depth": bound,
                "path": [reverse_codes[model.eval(variable).as_long()] for variable in trace],
            }
        if result != unsat:
            return {"status": "unknown", "start": start, "bound": bound, "reason": solver.reason_unknown()}

    return {"status": "unsat", "bound": bound, "path": None}
