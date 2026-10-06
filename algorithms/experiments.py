"""Deliberately incorrect variants, isolated from the reference algorithms.

Never use these for real routing. They exist to falsify classroom conjectures.
"""

from heapq import heappop, heappush
from itertools import count
from math import inf

from .common import Stats, finish, heuristic_cache, validate_graph


def astar_closed_bug(graph, start, target, heuristic):
    """BROKEN with admissible but inconsistent heuristics: no reopening."""
    validate_graph(graph, start, target)
    dist = dict.fromkeys(graph, inf)
    parent = {}
    closed = set()
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
            return finish(dist, parent, start, target, stats, set())
        closed.add(u)
        stats.expansions += 1
        for v, weight in graph[u]:
            stats.relaxations += 1
            if v in closed:  # WRONG under admissibility alone
                continue
            candidate = popped_g + weight
            if candidate < dist[v]:
                dist[v] = candidate
                parent[v] = u
                heappush(queue, (candidate + h(v), next(ticket), candidate, v))
                stats.pushes += 1
                stats.improvements += 1
                stats.peak_queue = max(stats.peak_queue, len(queue))
    return finish(dist, parent, start, target, stats, set())


def stop_on_generation_bug(graph, start, target):
    """BROKEN: returns the first complete route generated, not certified."""
    queue = [(0, start)]
    dist = {start: 0}
    while queue:
        g, u = heappop(queue)
        if g != dist[u]:
            continue
        for v, w in graph[u]:
            if v == target:  # WRONG: a cheaper route can remain on the frontier
                return g + w
            if g + w < dist.get(v, inf):
                dist[v] = g + w
                heappush(queue, (g + w, v))
    return inf
