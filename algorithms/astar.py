"""A* with a lazy heap, static cached heuristic, and reopening.

Run: python -m algorithms.astar [--reopening] [--zero]
Optimality assumes h is admissible and h(target)=0. Validation checks finite,
nonnegative values, NOT admissibility (which would require extra knowledge).
The queued g is distinct from f: compare queued g against dist for stale checks.
"""
from __future__ import annotations
from heapq import heappop, heappush
from itertools import count
from math import inf
from .common import (Graph, Heuristic, Result, Stats, finish, heuristic_cache,
                     validate_graph, print_result)


def astar(graph: Graph, start: str, target: str, heuristic: Heuristic,
          *, check: bool = True) -> Result:
    if check:
        validate_graph(graph, start, target)
    dist = dict.fromkeys(graph, inf)
    parent: dict[str, str] = {}
    expanded: set[str] = set()  # instrumentation only, NEVER used to block a route
    stats = Stats(pushes=1, peak_queue=1)
    h = heuristic_cache(heuristic, target, stats)
    ticket = count()
    dist[start] = 0
    queue = [(h(start), next(ticket), 0, start)]
    while queue:
        popped_f, _, popped_g, u = heappop(queue)
        stats.pops += 1
        if popped_g != dist[u]:
            stats.stale_pops += 1
            continue
        if u == target:
            return finish(dist, parent, start, target, stats, {target})
        stats.reexpansions += int(u in expanded)
        expanded.add(u)
        stats.expansions += 1
        for v, weight in graph[u]:
            stats.relaxations += 1
            candidate = popped_g + weight
            if candidate < dist[v]:
                dist[v] = candidate
                parent[v] = u
                priority = candidate + h(v)
                heappush(queue, (priority, next(ticket), candidate, v))
                stats.pushes += 1
                stats.improvements += 1
                stats.peak_queue = max(stats.peak_queue, len(queue))
    return finish(dist, parent, start, target, stats, set())


if __name__ == '__main__':
    import argparse
    from graphs.main_graph import GRAPH, HEURISTIC
    from graphs.fixtures import reopening_case
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reopening', action='store_true')
    p.add_argument('--zero', action='store_true')
    a = p.parse_args()
    case = reopening_case() if a.reopening else dict(graph=GRAPH, h=HEURISTIC)
    h = {v: 0 for v in case['graph']} if a.zero else case['h']
    print_result(astar(case['graph'], 'S', 'T', h))
