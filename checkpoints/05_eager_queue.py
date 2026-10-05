"""41-48 min. Keep one queue entry per frontier node.
Student scaffold. Assumes a valid graph; reference APIs perform validation.
Run from the repo root: python -m checkpoints.05_eager_queue
"""
from heapq import heappop, heappush
from itertools import count
from math import inf
from algorithms.dijkstra import IndexedMinPQ
from algorithms.common import recover
from graphs.main_graph import GRAPH, HEURISTIC

def search(graph, start, target):
    dist, parent = {start: 0}, {}
    queue = IndexedMinPQ()
    queue.insert(start, 0)
    while queue:
        g, u = queue.pop_min()
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            candidate = g + weight
            if candidate < dist.get(v, inf):
                dist[v] = candidate
                parent[v] = u
                if v in queue:
                    raise NotImplementedError("Update existing priority")
                else:
                    raise NotImplementedError("Insert new node")
    return inf, []

if __name__ == '__main__':
    print(search(GRAPH, 'S', 'T'))
