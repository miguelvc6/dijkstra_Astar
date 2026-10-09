from itertools import count


class IndexedMinPQ:
    """Binary min-heap with node-to-index mapping for decrease-key operations."""

    def __init__(self):
        self.heap: list[tuple[float, int, str]] = []
        self.positions: dict[str, int] = {}
        self.ticket = count()

    def __bool__(self):
        return bool(self.heap)

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

    def insert(self, node: str, priority: float):
        self.positions[node] = len(self.heap)
        self.heap.append((priority, next(self.ticket), node))
        self._up(len(self.heap) - 1)

    def decrease_key(self, node: str, priority: float):
        i = self.positions[node]
        self.heap[i] = (priority, next(self.ticket), node)
        self._up(i)

    def pop_min(self) -> tuple[float, str]:
        priority, _, node = self.heap[0]
        last = self.heap.pop()
        del self.positions[node]
        if self.heap:
            self.heap[0] = last
            self.positions[last[2]] = 0
            self._down(0)
        return priority, node