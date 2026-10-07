"""Dijkstra's shortest path algorithm using a lazy list-based priority queue."""
# python3 -m algorithms.02_dijkstra_lazy_list

def dijkstra_lazy_list(graph, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost path from start to target using an unsorted list as a lazy queue."""
    dist: dict[str, float] = dict.fromkeys(graph, float("inf"))
    parent: dict[str, str] = {}

    dist[start] = 0.0
    # Store entries as (cost, node); new candidates are appended lazily
    queue: list[tuple[float, str]] = [(0.0, start)]

    def extract_min(queue: list[tuple[float, str]]) -> tuple[float, str]:
        """Finds, removes, and returns the element with the minimum cost from the queue."""
        min_idx = 0
        min_cost = queue[0][0]
        for i in range(1, len(queue)):
            if queue[i][0] < min_cost:
                min_cost = queue[i][0]
                min_idx = i

        return queue.pop(min_idx)

    while queue:
        popped_g, u = extract_min(queue)

        # Skip stale entries
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
                queue.append((candidate, v))

    return float("inf"), []


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(dijkstra_lazy_list(GRAPH, "S", "T"))
