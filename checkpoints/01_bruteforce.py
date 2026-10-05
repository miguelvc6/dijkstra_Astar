"""09-16 min. Enumerate simple routes. Why must the visited set be path-local?
Student scaffold. Assumes a valid graph; reference APIs perform validation.
Run from the repo root: python -m checkpoints.01_bruteforce
"""
from heapq import heappop, heappush
from itertools import count
from math import inf
from algorithms.dijkstra import IndexedMinPQ
from algorithms.common import recover
from graphs.main_graph import GRAPH, HEURISTIC

def search(graph, start, target):
    best_cost, best_path = inf, []
    def visit(u, cost, path, on_path):
        nonlocal best_cost, best_path
        if u == target:
            if cost < best_cost:
                best_cost, best_path = cost, path.copy()
            return
        for v, weight in graph[u]:
            if ...:  # TODO: allow only nodes not on the current route
                raise NotImplementedError("Extend cost, path and on_path")
    visit(start, 0, [start], {start})
    return best_cost, best_path

if __name__ == '__main__':
    print(search(GRAPH, 'S', 'T'))
