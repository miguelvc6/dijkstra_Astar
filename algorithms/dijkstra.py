"""Lazy and eager Dijkstra. Run: python -m algorithms.dijkstra [--eager] [--all].

Public calls validate the graph. check=False is for prevalidated benchmarks only.
With an early target stop, non-finalized distances remain tentative.
Tie-breaking is FIFO by the latest insertion or strict priority improvement.
"""

from __future__ import annotations

from heapq import heappop, heappush
from itertools import count
from math import inf

from .common import Graph, Result, Stats, finish, print_result, validate_graph


def dijkstra_lazy(graph: Graph, start: str, target: str | None = None, *, check: bool = True) -> Result:
    if check:
        validate_graph(graph, start, target)
    dist = dict.fromkeys(graph, inf)
    parent: dict[str, str] = {}
    finalized: set[str] = set()
    stats = Stats(pushes=1, peak_queue=1)
    ticket = count()
    dist[start] = 0
    queue = [(0, next(ticket), start)]
    while queue:
        popped_g, _, u = heappop(queue)
        stats.pops += 1
        if popped_g != dist[u]:
            stats.stale_pops += 1
            continue
        finalized.add(u)
        if u == target:
            return finish(dist, parent, start, target, stats, finalized)
        stats.expansions += 1
        for v, weight in graph[u]:
            stats.relaxations += 1
            candidate = popped_g + weight
            if candidate < dist[v]:
                dist[v] = candidate
                parent[v] = u
                heappush(queue, (candidate, next(ticket), v))
                stats.pushes += 1
                stats.improvements += 1
                stats.peak_queue = max(stats.peak_queue, len(queue))
    return finish(dist, parent, start, target, stats, finalized)


class IndexedMinPQ:
    """Binary min-heap plus node->array-index mapping. Strict decrease-key.

    A new tie ticket is issued on every priority improvement, matching the
    insertion order of replacement records in the lazy implementation.
    heap is NOT sorted; sorted(heap) is a separate explanatory view.
    """

    def __init__(self):
        self.heap: list[tuple[float, int, str]] = []
        self.positions: dict[str, int] = {}
        self.ticket = count()

    def __bool__(self):
        return bool(self.heap)

    def __len__(self):
        return len(self.heap)

    def __contains__(self, node):
        return node in self.positions

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.positions[self.heap[i][2]] = i
        self.positions[self.heap[j][2]] = j

    def _up(self, i):
        while i:
            p = (i - 1) // 2
            if self.heap[p] <= self.heap[i]:
                break
            self._swap(p, i)
            i = p

    def _down(self, i):
        while 2 * i + 1 < len(self.heap):
            j = 2 * i + 1
            if j + 1 < len(self.heap) and self.heap[j + 1] < self.heap[j]:
                j += 1
            if self.heap[i] <= self.heap[j]:
                break
            self._swap(i, j)
            i = j

    def insert(self, node, priority):
        if node in self.positions:
            raise ValueError("Node already in queue; use decrease_key.")
        self.positions[node] = len(self.heap)
        self.heap.append((priority, next(self.ticket), node))
        self._up(len(self.heap) - 1)

    def decrease_key(self, node, priority):
        if node not in self.positions:
            raise KeyError(node)
        i = self.positions[node]
        if priority >= self.heap[i][0]:
            raise ValueError("decrease_key requires a strict improvement.")
        self.heap[i] = (priority, next(self.ticket), node)
        self._up(i)

    def pop_min(self):
        if not self.heap:
            raise IndexError("pop from empty priority queue")
        priority, _, node = self.heap[0]
        last = self.heap.pop()
        del self.positions[node]
        if self.heap:
            self.heap[0] = last
            self.positions[last[2]] = 0
            self._down(0)
        return priority, node

    def check_invariant(self):
        assert len(self.positions) == len(self.heap)
        for i, item in enumerate(self.heap):
            assert self.positions[item[2]] == i
            if i:
                assert self.heap[(i - 1) // 2] <= item


def dijkstra_eager(graph: Graph, start: str, target: str | None = None, *, check: bool = True) -> Result:
    if check:
        validate_graph(graph, start, target)
    dist = dict.fromkeys(graph, inf)
    parent: dict[str, str] = {}
    finalized: set[str] = set()
    stats = Stats(pushes=1, peak_queue=1)
    dist[start] = 0
    queue = IndexedMinPQ()
    queue.insert(start, 0)
    while queue:
        popped_g, u = queue.pop_min()
        stats.pops += 1
        finalized.add(u)
        if u == target:
            return finish(dist, parent, start, target, stats, finalized)
        stats.expansions += 1
        for v, weight in graph[u]:
            stats.relaxations += 1
            candidate = popped_g + weight
            if candidate < dist[v]:
                dist[v] = candidate
                parent[v] = u
                if v in queue:
                    queue.decrease_key(v, candidate)
                    stats.decrease_keys += 1
                else:
                    queue.insert(v, candidate)
                    stats.pushes += 1
                stats.improvements += 1
                stats.peak_queue = max(stats.peak_queue, len(queue))
    return finish(dist, parent, start, target, stats, finalized)


if __name__ == "__main__":
    import argparse

    from graphs.main_graph import GRAPH

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eager", action="store_true")
    p.add_argument("--all", action="store_true", help="Finalize every reachable distance.")
    a = p.parse_args()
    fn = dijkstra_eager if a.eager else dijkstra_lazy
    print_result(fn(GRAPH, "S", None if a.all else "T"))
