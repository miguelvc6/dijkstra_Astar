"""Enumerate ALL simple paths; no branch-and-bound or global visited set.

Run: python -m algorithms.brute_force
A deterministic prefix budget prevents a classroom run from becoming stuck.
A budget-exhausted incumbent is NOT reported as a proven optimum.
"""

from __future__ import annotations
from math import inf
from .common import Graph, Result, Stats, print_result, validate_graph


class BudgetExceeded(Exception):
    pass


def brute_force(graph: Graph, start: str, target: str, *, max_prefixes: int = 100_000, check: bool = True) -> Result:
    if check:
        validate_graph(graph, start, target)
    if max_prefixes < 1:
        raise ValueError("max_prefixes must be positive.")
    stats = Stats()
    best_cost = inf
    best_path: list[str] = []
    path = [start]
    on_path = {start}  # local to the current route, not a global visited set

    def explore(u: str, cost: float) -> None:
        nonlocal best_cost, best_path
        if stats.prefixes >= max_prefixes:
            raise BudgetExceeded
        stats.prefixes += 1
        if u == target:
            stats.paths_examined += 1
            if cost < best_cost:
                best_cost, best_path = cost, path.copy()
            return
        stats.expansions += 1
        for v, weight in graph[u]:
            stats.relaxations += 1
            if v not in on_path:
                on_path.add(v)
                path.append(v)
                try:
                    explore(v, cost + weight)
                finally:
                    path.pop()
                    on_path.remove(v)

    status = "found"
    try:
        explore(start, 0)
    except (BudgetExceeded, RecursionError):
        status = "budget_exhausted"
    if best_cost == inf and status == "found":
        status = "unreachable"
    parent = {v: u for u, v in zip(best_path, best_path[1:])}
    return Result(
        best_cost, best_path, {target: best_cost}, parent, stats, status, {target} if status == "found" else set()
    )


if __name__ == "__main__":
    from graphs.main_graph import GRAPH

    print_result(brute_force(GRAPH, "S", "T"))
