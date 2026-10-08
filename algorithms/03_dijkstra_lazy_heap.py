"""Dijkstra's shortest path algorithm using a lazy binary-heap-based priority queue."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.03_dijkstra_lazy_heap

"""
1. Import heap
2. Replace extract_min for heappop
3. Replace queue.append for heappush
4. Add ticket count iterator and fix inputs and outputs of queue
"""

# 1. Import heap
from heapq import heappop, heappush
from itertools import count


def dijkstra_lazy_heap(graph, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using a lazy binary heap."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    dist[start] = 0.0
    parent: dict[str, str] = {}
    # 4. Add ticket count iterator and fix inputs and outputs of queue
    ticket = count()  # Tie-Breaking (FIFO Order)
    queue = [(dist[start], next(ticket), start)]

    while queue:
        # 2. Replace extract_min for heappop
        popped_dist, _, u = heappop(queue)

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
                # 3. Replace queue.append for heappush
                heappush(queue, (candidate_dist, next(ticket), v))

    return float("inf"), []


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(dijkstra_lazy_heap(GRAPH, "S", "T"))
