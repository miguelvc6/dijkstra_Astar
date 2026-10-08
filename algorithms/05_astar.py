"""A* pathfinding with a lazy heap and node reopening."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""
1. Define heuristic variable
2. Define heuristic in astar input
3. Update heappop output
4. Use heuristic to compute priority
"""

from heapq import heappop, heappush
from itertools import count


# 2. Define heuristic in astar input
def astar(graph, start: str, target: str, heuristic) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using A* with lazy priority updates."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    dist[start] = 0.0
    parent: dict[str, str] = {}
    ticket = count()

    # 1. Define heuristic variable
    h = heuristic if callable(heuristic) else lambda node: heuristic[node]
    queue = [(h(start), next(ticket), 0.0, start)]

    while queue:
        # 3. Update heappop output
        _, _, popped_dist, u = heappop(queue)

        if popped_dist != dist[u]:
            continue

        if u == target:
            path = [target]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return dist[target], path[::-1]

        for v, weight in graph[u]:
            candidate_dist = popped_dist + weight
            if candidate_dist < dist[v]:
                dist[v] = candidate_dist
                parent[v] = u
                # 4. Use heuristic to compute priority
                priority = candidate_dist + h(v)
                heappush(queue, (priority, next(ticket), candidate_dist, v))

    return float("inf"), []


if __name__ == "__main__":
    from graphs.main_graph import GRAPH, HEURISTIC

    print(astar(GRAPH, "S", "T", HEURISTIC))
