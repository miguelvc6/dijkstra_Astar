"""Dijkstra's shortest path algorithm using an eager indexed-heap-based priority queue."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.04_dijkstra_eager_heap

from algorithms.indexed_min_heap import IndexedMinPQ


def dijkstra_eager_heap(graph, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using an eager indexed priority queue."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    parent: dict[str, str] = {}

    dist[start] = 0.0
    queue = IndexedMinPQ()
    queue.insert(start, 0.0)

    while queue:
        popped_g, u = queue.pop_min()

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
                if v in queue:
                    queue.decrease_key(v, candidate)
                else:
                    queue.insert(v, candidate)

    return float("inf"), []


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(dijkstra_eager_heap(GRAPH, "S", "T"))
