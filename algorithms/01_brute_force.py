"""Backtracking Depth-First Search (DFS) designed for Simple Pathfinding."""
# python3 -m algorithms.01_brute_force

class BudgetExceeded(Exception):
    pass


def brute_force(graph, start: str, target: str, *, max_iter: int = 100_000) -> tuple[float, list[str]]:
    """Finds the lowest-cost simple path between start and target using backtracking."""
    path: list[str] = [start]
    on_path: set[str] = {start}

    def explore(
        u: str, cost: float, best_cost: float, best_path: list[str], iter: int
    ) -> tuple[float, list[str], int]:
        """Recursively traverses graph nodes to update the lowest-cost path."""

        # Budget max iterations
        iter += 1
        if iter >= max_iter:
            raise BudgetExceeded

        # Exit condition
        if u == target:
            if cost < best_cost:
                return cost, path, iter
            return best_cost, best_path, iter

        for v, weight in graph[u]: # Iterate on vertices of u
            if v not in on_path:
                on_path.add(v)
                path.append(v)
                best_cost, best_path, iter = explore(v, cost + weight, best_cost, best_path, iter)
                path.pop()
                on_path.remove(v)

        return best_cost, best_path, iter

    best_cost, best_path, _ = explore(start, 0.0, float("inf"), [], 0)

    return best_cost, best_path


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print(brute_force(GRAPH, "S", "T"))
