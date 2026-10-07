"""A* pathfinding with a lazy heap and node reopening."""

from heapq import heappop, heappush
from itertools import count


def astar(graph, start: str, target: str, heuristic) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using A* with lazy priority updates."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    parent: dict[str, str] = {}
    ticket = count()

    h = heuristic if callable(heuristic) else lambda node: heuristic[node]

    dist[start] = 0.0
    queue = [(h(start), next(ticket), 0.0, start)]

    while queue:
        _, _, popped_g, u = heappop(queue)

        if popped_g != dist[u]:
            continue

        if u == target:
            path = [target]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return dist[target], path[::-1]

        for v, weight in graph[u]:
            candidate = popped_g + weight
            if candidate < dist[v]:
                dist[v] = candidate
                parent[v] = u
                priority = candidate + h(v)
                heappush(queue, (priority, next(ticket), candidate, v))

    return float("inf"), []


if __name__ == "__main__":
    from graphs.main_graph import GRAPH, HEURISTIC

    print(astar(GRAPH, "S", "T", HEURISTIC))
