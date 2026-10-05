"""BMC extension for the course softsec-toolkit.

The supplied ch3_verify/03_bmc_manual.py demonstrates BMC with a bounded
transition relation and Z3. This project keeps the same idea but uses finite
Kripke-path enumeration, so the project is reproducible even when Z3 is not
installed. The completeness threshold is obtained from the finite-state
reachable graph (diameter) for the safety properties.
"""
from collections import deque


def all_paths(model, bound, starts=None):
    starts = sorted(starts if starts is not None else model.initial)
    frontier = [[s] for s in starts]
    for _ in range(bound):
        nxt = []
        for path in frontier:
            for state in sorted(model.transitions.get(path[-1], ())):
                nxt.append(path + [state])
        frontier = nxt
    yield from frontier


def find_edge_counterexample(model, forbidden_edge, bound):
    for path in all_paths(model, bound):
        for a, b in zip(path, path[1:]):
            if (a, b) == forbidden_edge:
                return path
    return None


def shortest_edge_counterexample(model, forbidden_edge):
    q = deque((s, [s]) for s in sorted(model.initial))
    seen = set(model.initial)
    while q:
        s, path = q.popleft()
        for nxt in sorted(model.transitions.get(s, ())):
            if (s, nxt) == forbidden_edge:
                return path + [nxt]
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, path + [nxt]))
    return None


def graph_diameter(model):
    max_depth = 0
    for start in model.initial:
        q = deque([(start, 0)])
        seen = {start}
        while q:
            s, d = q.popleft()
            max_depth = max(max_depth, d)
            for nxt in model.transitions.get(s, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
    return max_depth


def check_ag_not_edge(model, forbidden_edge):
    return shortest_edge_counterexample(model, forbidden_edge) is None


def check_af_label_from(model, label, starts):
    """Check AF(label) from the specified reachable states."""
    starts = set(starts)
    states = set(model.reachable_states())
    good = {s for s in states if label in model.labels.get(s, set())}
    changed = True
    while changed:
        changed = False
        for s in list(states - good):
            succ = model.transitions.get(s, set())
            if succ and all(x in good for x in succ):
                good.add(s)
                changed = True
    return starts.issubset(good)


def bmc_af_from(model, label, starts, bound):
    """Return a bounded path that avoids label for the whole prefix."""
    for path in all_paths(model, bound, starts):
        if all(label not in model.labels.get(s, set()) for s in path):
            return path
    return None
