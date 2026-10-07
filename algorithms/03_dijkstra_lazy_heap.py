"""Dijkstra's shortest path algorithm using a lazy binary-heap-based priority queue."""
# python3 -m algorithms.03_dijkstra_lazy_heap

from heapq import heappop, heappush
from itertools import count


def dijkstra_lazy_heap(graph, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using a lazy binary heap."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    parent: dict[str, str] = {}
    ticket = count()

    dist[start] = 0.0
    queue = [(0.0, next(ticket), start)]

    while queue:
        popped_g, _, u = heappop(queue)

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
                heappush(queue, (candidate, next(ticket), v))

    return float("inf"), []



if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(dijkstra_lazy_heap(GRAPH, "S", "T"))
