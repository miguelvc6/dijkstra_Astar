"""34-38 min. Skip obsolete records; replace the predecessor on every improvement.
Student scaffold. Assumes a valid graph; reference APIs perform validation.
Run from the repo root: python -m checkpoints.03_stale_and_parent
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
        if ...:  # TODO: detect stale record
            continue
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            candidate = g + weight
            if candidate < dist.get(v, inf):
                dist[v] = candidate
                raise NotImplementedError("Update the predecessor")
                heappush(queue, (candidate, next(ticket), v))
    return inf, []

if __name__ == '__main__':
    print(search(GRAPH, 'S', 'T'))
