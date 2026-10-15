class KripkeStructure:
    def __init__(self):
        self.initial = set()
        self.labels = {}
        self.transitions = {}

    def add_state(self, state, labels=None, initial=False):
        self.labels.setdefault(state, set()).update(labels or [])
        self.transitions.setdefault(state, set())
        if initial:
            self.initial.add(state)

    def add_transition(self, source, target):
        if source not in self.labels or target not in self.labels:
            raise ValueError(f"Transition references unknown state: {source} -> {target}")
        self.transitions[source].add(target)

    def reachable_states(self):
        reached = set()
        pending = list(self.initial)
        while pending:
            state = pending.pop()
            if state in reached:
                continue
            reached.add(state)
            pending.extend(self.transitions.get(state, set()) - reached)
        return reached
