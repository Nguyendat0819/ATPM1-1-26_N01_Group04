"""Lớp dữ liệu tối giản biểu diễn S, S₀, R và L của cấu trúc Kripke."""

class KripkeStructure:
    """Lưu state đầu, nhãn mệnh đề và các cạnh chuyển tiếp của một mô hình."""

    def __init__(self):
        """Khởi tạo ba cấu trúc rỗng tương ứng với thành phần của mô hình Kripke."""
        self.initial = set()
        self.labels = {}
        self.transitions = {}

    def add_state(self, state, labels=None, initial=False):
        """Khai báo state, hợp nhất nhãn L(state), và đánh dấu state đầu nếu cần."""
        self.labels.setdefault(state, set()).update(labels or [])
        self.transitions.setdefault(state, set())
        if initial:
            self.initial.add(state)

    def add_transition(self, source, target):
        """Thêm cạnh R(source,target); từ chối cạnh nếu một đầu mút chưa được khai báo."""
        if source not in self.labels or target not in self.labels:
            raise ValueError(f"Transition references unknown state: {source} -> {target}")
        self.transitions[source].add(target)

    def reachable_states(self):
        """Duyệt đồ thị từ các state đầu và trả về tất cả state có thể đạt tới."""
        reached = set()
        pending = list(self.initial)
        while pending:
            state = pending.pop()
            if state in reached:
                continue
            reached.add(state)
            pending.extend(self.transitions.get(state, set()) - reached)
        return reached
