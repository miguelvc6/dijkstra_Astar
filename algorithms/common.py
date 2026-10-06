"""Types, validation, counters, and path recovery; not live-coding material."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from math import inf, isfinite

Graph = dict[str, list[tuple[str, float]]]
Heuristic = Mapping[str, float] | Callable[[str], float]


@dataclass
class Stats:
    expansions: int = 0  # outgoing adjacency lists processed; excludes goal
    reexpansions: int = 0  # expansions after the first for the same state
    pushes: int = 0  # includes initial insertion; eager: insertions only
    pops: int = 0  # includes stale entries and goal extraction
    stale_pops: int = 0
    relaxations: int = 0  # outgoing edges examined
    improvements: int = 0  # successful strict distance improvements
    decrease_keys: int = 0
    peak_queue: int = 0  # includes obsolete records for lazy queues
    paths_examined: int = 0  # brute force: complete simple s-to-t paths
    prefixes: int = 0  # brute force: recursive calls
    h_evals: int = 0  # cache misses, including h(target) validation


@dataclass
class Result:
    distance: float | None
    path: list[str]
    dist: dict[str, float]
    parent: dict[str, str]
    stats: Stats
    status: str
    finalized: set[str] = field(default_factory=set)
    # For A*, only the target is certified on success (assuming admissibility).
    # A*'s expanded states must NOT be mistaken for a permanent settled set.

    def as_dict(self) -> dict:
        obj = asdict(self)
        obj["finalized"] = sorted(self.finalized)
        obj["dist"] = {k: (v if isfinite(v) else None) for k, v in self.dist.items()}
        if self.distance is not None and not isfinite(self.distance):
            obj["distance"] = None
        return obj


def validate_graph(graph: Graph, start: str, target: str | None = None) -> None:
    """Require explicit string nodes, finite nonnegative costs, no parallel arcs."""
    if start not in graph or (target is not None and target not in graph):
        raise ValueError("Start and target must be explicit graph nodes.")
    for u, edges in graph.items():
        if not isinstance(u, str):
            raise TypeError("This educational API uses string node IDs.")
        destinations: set[str] = set()
        for v, weight in edges:
            if v not in graph:
                raise ValueError(f"Edge {u}->{v} has an undeclared endpoint.")
            if v in destinations:
                raise ValueError("Parallel arcs are excluded from this educational API.")
            destinations.add(v)
            if isinstance(weight, bool) or not isinstance(weight, (int, float)):
                raise TypeError("Edge costs must be real int/float values.")
            if not isfinite(weight) or weight < 0:
                raise ValueError("Finite, nonnegative edge costs are required.")


def recover(parent: dict[str, str], start: str, target: str) -> list[str]:
    path = [target]
    while path[-1] != start:
        if path[-1] not in parent:
            return []
        path.append(parent[path[-1]])
        if len(path) > len(parent) + 1:
            raise RuntimeError("Cycle in predecessor map.")
    return list(reversed(path))


def finish(dist, parent, start, target, stats, finalized) -> Result:
    if target is None:
        return Result(None, [], dist, parent, stats, "all_distances", set(finalized))
    cost = dist[target]
    return Result(
        cost,
        recover(parent, start, target) if cost < inf else [],
        dist,
        parent,
        stats,
        "found" if cost < inf else "unreachable",
        set(finalized),
    )


def path_cost(graph: Graph, path: list[str]) -> float:
    if not path:
        return inf
    return sum(dict(graph[u])[v] for u, v in zip(path, path[1:]))


def heuristic_cache(heuristic: Heuristic, target: str, stats: Stats):
    cache: dict[str, float] = {}

    def h(node: str) -> float:
        if node not in cache:
            value = heuristic(node) if callable(heuristic) else heuristic[node]
            if not isinstance(value, (int, float)) or not isfinite(value) or value < 0:
                raise ValueError("Heuristic values must be finite and nonnegative.")
            cache[node] = value
            stats.h_evals += 1
        return cache[node]

    if h(target) != 0:
        raise ValueError("The lecture contract requires h(target) == 0.")
    return h


def print_result(result: Result) -> None:
    import json

    print(json.dumps(result.as_dict(), indent=2, allow_nan=False))
