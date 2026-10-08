"""Dijkstra's shortest path algorithm using an eager indexed-heap-based priority queue."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.04_dijkstra_eager_heap

"""
1. Import IndexedMinPQ
2. Replace queue with a IndexedMinPQ and remove ticket
3. Replace heapop with queue.pop_min()
4. Replace heappush with queue.decrease_key() and queue.insert()
5. Remove skip stales
"""

# 1. Import IndexedMinPQ
from algorithms.indexed_min_heap import IndexedMinPQ


def dijkstra_eager_heap(graph, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using an eager indexed priority queue."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    dist[start] = 0.0
    parent: dict[str, str] = {}

    # 2. Replace queue with a IndexedMinPQ and remove ticket
    queue = IndexedMinPQ()
    queue.insert(start, 0.0)

    while queue:
        # 3. Replace heapop with queue.pop_min()
        popped_dist, u = queue.pop_min()

        # 5. Remove skip stales
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
                # 4. Replace heappush with queue.decrease_key() and queue.insert()
                if v in queue:
                    queue.decrease_key(v, candidate_dist)
                else:
                    queue.insert(v, candidate_dist)

    return float("inf"), []


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(dijkstra_eager_heap(GRAPH, "S", "T"))
