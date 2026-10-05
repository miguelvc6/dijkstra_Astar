"""Canonical nine-node example; costs and coordinates are distinct concepts.

h(v) is Manhattan distance to T in COORDINATES. Every arc costs at least its
Manhattan displacement, so h is consistent. Neighbor order is deliberate.
"""
GRAPH = {
    'S': [('A', 2), ('B', 6), ('D', 2), ('T', 15)],
    'A': [('B', 1), ('C', 6)],
    'B': [('A', 2), ('C', 1), ('T', 8)],
    'C': [('T', 4)],
    'D': [('E', 1)],
    'E': [('F', 1)],
    'F': [('G', 1)],
    'G': [('T', 10)],
    'T': [],
}
COORDINATES = {'S': (0, 0), 'A': (1, 0), 'B': (2, 0), 'C': (3, 0),
               'D': (0, 1), 'E': (0, 2), 'F': (1, 2), 'G': (1, 3), 'T': (6, 0)}
HEURISTIC = {v: abs(x - 6) + abs(y) for v, (x, y) in COORDINATES.items()}
OPTIMAL_PATH = ['S', 'A', 'B', 'C', 'T']
OPTIMAL_COST = 8

if __name__ == '__main__':
    import json
    print(json.dumps(dict(graph=GRAPH, coordinates=COORDINATES, h=HEURISTIC), indent=2))
