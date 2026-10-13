"""Backtracking Depth-First Search (DFS) designed for Simple Pathfinding."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# python3 -m algorithms.01_depth_first

"""
1. Declare variables
2. Define explore function
3. Exit condition
4. Explore loop
5. Call explore
"""


def depth_first(graph, start: str, target: str):
    """Finds the lowest-cost simple path between start and target using backtracking."""
    # 1. Declare variables
    path: list[str] = [start]  # currently taken path
    visited: set[str] = {start}  # visited nodes

    # 2. Define explore function
    def explore(u: str, cost: float, best_cost: float, best_path: list[str]):
        """Recursively traverses graph nodes to update the lowest-cost path."""

        # 3. Exit condition
        if u == target:
            if cost < best_cost:
                return cost, path.copy()
            return best_cost, best_path

        # 4. Explore loop
        for v, weight in graph[u]:  # Iterate on neighbours of u
            if v not in visited:
                visited.add(v)
                path.append(v)
                best_cost, best_path = explore(v, cost + weight, best_cost, best_path)
                path.pop()
                visited.remove(v)

        return best_cost, best_path

    # 5. Call explore
    best_cost, best_path = explore(start, 0.0, float("inf"), [])

    return best_cost, best_path


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(depth_first(GRAPH, "S", "T"))
