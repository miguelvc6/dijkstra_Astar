"""Dijkstra's shortest path algorithm using a lazy list-based priority queue."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.02_dijkstra_lazy_list

"""
1. Declare variables
2. while queue loop
3. extract_min
4. Iterate on neighbours
5. Skip stales
6. Target reached
7. Return empty path when queue empty and target not reached
"""

def dijkstra_lazy_list(graph: dict, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using an unsorted list as a lazy queue."""

    # 1. Declare variables
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    dist[start] = 0.0
    parent: dict[str, str] = {}
    queue: list[tuple[float, str]] = [(dist[start], start)] # Store entries as (cost, node)

    def extract_min(queue: list[tuple[float, str]]) -> tuple[float, str]:
        """Finds, removes, and returns the element with the minimum cost from the queue."""
        min_idx = 0
        min_cost = queue[0][0]
        for i in range(1, len(queue)):
            if queue[i][0] < min_cost:
                min_cost = queue[i][0]
                min_idx = i

        return queue.pop(min_idx)

    while queue: # 2. While queue loop
        popped_dist, u = extract_min(queue) # 3. extract_min

        if popped_dist != dist[u]: # 5. Skip stales
            continue

        if u == target: # 6. Target reached
            path = [target]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return dist[target], path[::-1]

        for v, weight in graph[u]: # 4. Iterate on neighbours
            candidate_dist = popped_dist + weight
            if candidate_dist < dist[v]:
                dist[v] = candidate_dist
                parent[v] = u
                queue.append((candidate_dist, v))

    return float("inf"), [] # 7. Return empty path when queue empty and target not reached


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(dijkstra_lazy_list(GRAPH, "S", "T"))
