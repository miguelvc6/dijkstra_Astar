"""28-34 min. Fill the accumulated cost and improvement condition.
Student scaffold. Assumes a valid graph; reference APIs perform validation.
Run from the repo root: python -m checkpoints.02_lazy_relaxation
"""
from heapq import heappop, heappush
from itertools import count
from math import inf
from algorithms.dijkstra import IndexedMinPQ
from algorithms.common import recover
from graphs.main_graph import GRAPH, HEURISTIC

def search(graph, start, target):
    dist, parent = {start: 0}, {}
    ticket = count()
    queue = [(0, next(ticket), start)]
    while queue:
        g, _, u = heappop(queue)
        if g != dist[u]:
            continue
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            raise NotImplementedError("Compute candidate")
            if ...:  # TODO: compare against the best known distance
                dist[v] = candidate
                parent[v] = u
                heappush(queue, (candidate, next(ticket), v))
    return inf, []

if __name__ == '__main__':
    print(search(GRAPH, 'S', 'T'))
