from collections import deque


def shortest_edge_counterexample(model, forbidden_edge, bound=None):
    queue = deque((state, [state]) for state in sorted(model.initial))
    shortest_depth = {state: 0 for state in model.initial}
    while queue:
        state, path = queue.popleft()
        depth = len(path) - 1
        if bound is not None and depth >= bound:
            continue
        for target in sorted(model.transitions.get(state, set())):
            if (state, target) == tuple(forbidden_edge):
                return path + [target]
            next_depth = depth + 1
            if next_depth < shortest_depth.get(target, float("inf")):
                shortest_depth[target] = next_depth
                queue.append((target, path + [target]))
    return None


def reachable_state_count(model):
    return len(model.reachable_states())


def graph_diameter(model):
    max_depth = 0
    for start in model.initial:
        queue = deque([(start, 0)])
        seen = {start}
        while queue:
            state, depth = queue.popleft()
            max_depth = max(max_depth, depth)
            for target in model.transitions.get(state, set()):
                if target not in seen:
                    seen.add(target)
                    queue.append((target, depth + 1))
    return max_depth


def check_af_labels_from(model, target_labels, starts):
    target_labels = set(target_labels)
    states = model.reachable_states()
    reaches_target = {
        state for state in states
        if target_labels.intersection(model.labels.get(state, set()))
    }
    changed = True
    while changed:
        changed = False
        for state in states - reaches_target:
            successors = model.transitions.get(state, set())
            if successors and successors.issubset(reaches_target):
                reaches_target.add(state)
                changed = True
    return set(starts).issubset(reaches_target)
