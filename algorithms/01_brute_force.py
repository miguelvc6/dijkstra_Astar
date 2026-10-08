"""Backtracking Depth-First Search (DFS) designed for Simple Pathfinding."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.01_depth_first


def depth_first(graph, start: str, target: str) -> tuple[float, list[str]]:
    """Finds the lowest-cost simple path between start and target using backtracking."""
    path: list[str] = [start] # currently taken path
    visited: set[str] = {start} # visited nodes

    def explore(
        u: str, cost: float, best_cost: float, best_path: list[str]
    ) -> tuple[float, list[str]]:
        """Recursively traverses graph nodes to update the lowest-cost path."""

        # Exit condition
        if u == target:
            if cost < best_cost:
                return cost, path
            return best_cost, best_path

        for v, weight in graph[u]:  # Iterate on neighbours of u
            if v not in visited:
                visited.add(v)
                path.append(v)
                best_cost, best_path = explore(v, cost + weight, best_cost, best_path)
                path.pop()
                visited.remove(v)

        return best_cost, best_path

    best_cost, best_path = explore(start, 0.0, float("inf"), [])

    return best_cost, best_path


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(depth_first(GRAPH, "S", "T"))
