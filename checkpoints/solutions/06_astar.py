"""68-77 min. Change priority, not the meaning of the stored route cost.
Worked solution. Assumes a valid graph; reference APIs perform validation.
Run from the repo root: python -m checkpoints.06_astar
"""
from heapq import heappop, heappush
from itertools import count
from math import inf
from algorithms.dijkstra import IndexedMinPQ
from algorithms.common import recover
from graphs.main_graph import GRAPH, HEURISTIC

def search(graph, start, target, h):
    dist, parent = {start: 0}, {}
    ticket = count()
    queue = [(h[start], next(ticket), 0, start)]
    while queue:
        f, _, g, u = heappop(queue)
        if g != dist[u]:
            continue
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            candidate = g + weight
            if candidate < dist.get(v, inf):
                dist[v] = candidate
                parent[v] = u
                priority = candidate + h[v]
                heappush(queue, (priority, next(ticket), candidate, v))
    return inf, []

if __name__ == '__main__':
    print(search(GRAPH, 'S', 'T', HEURISTIC))
