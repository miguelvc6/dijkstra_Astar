"""Small counterexamples and deterministic graph families."""
from copy import deepcopy
from math import hypot
from random import Random
from .main_graph import GRAPH, COORDINATES, HEURISTIC


def main_case():
    return dict(name='Main graph', graph=deepcopy(GRAPH), h=dict(HEURISTIC),
                coordinates=dict(COORDINATES), start='S', target='T', optimal=8)


def reopening_case():
    return dict(name='Admissible but inconsistent',
                graph={'S': [('A', 3), ('B', 1)], 'A': [('T', 3)],
                       'B': [('A', 1)], 'T': []},
                h={'S': 0, 'A': 0, 'B': 4, 'T': 0},
                coordinates={'S': (0, 1), 'A': (2, 2), 'B': (2, 0), 'T': (4, 1)},
                start='S', target='T', optimal=5)


def overestimate_case():
    case = main_case()
    case['name'] = 'Overestimate at A (optimality not guaranteed)'
    case['h']['A'] = 20  # hides the optimal prefix; reference A* returns cost 11
    case['optimal'] = 8
    return case


def negative_case():
    return dict(name='Negative edge: outside Dijkstra contract',
                graph={'S': [('T', 2), ('B', 5)], 'B': [('T', -4)], 'T': []},
                h={'S': 0, 'B': 0, 'T': 0},
                coordinates={'S': (0, 1), 'B': (2, 0), 'T': (4, 1)},
                start='S', target='T', optimal=1)


def complete_case(n):
    """Complete directed unit-weight graph: factorial simple-path growth."""
    nodes = [str(i) for i in range(n)]
    g = {u: [(v, 1) for v in nodes if u != v] for u in nodes}
    return dict(name=f'Complete-{n}', graph=g, h={u: int(u != nodes[-1]) for u in nodes},
                start=nodes[0], target=nodes[-1], optimal=1)


def grid_case(width=24, height=16, walls=True, heuristic='manhattan'):
    """Four-neighbor unit grid, with a vertical barrier and one low gap."""
    if width < 5 or height < 5:
        raise ValueError('Use grid dimensions >= 5.')
    blocked = {(width // 2, y) for y in range(height) if y != height - 2} if walls else set()
    xy = {f'{x},{y}': (x, y) for y in range(height) for x in range(width)
          if (x, y) not in blocked}
    g = {}
    for u, (x, y) in xy.items():
        g[u] = [(f'{a},{b}', 1) for a, b in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)]
                if f'{a},{b}' in xy]
    start, target = f'1,{height//2}', f'{width-2},{height//2}'
    tx, ty = xy[target]
    if heuristic not in {'manhattan', 'euclidean', 'zero'}:
        raise ValueError('Unknown heuristic.')
    h = {u: (abs(x-tx)+abs(y-ty) if heuristic == 'manhattan' else
             hypot(x-tx,y-ty) if heuristic == 'euclidean' else 0)
         for u, (x,y) in xy.items()}
    return dict(name=f'Grid-{width}x{height}-{"wall" if walls else "open"}-{heuristic}',
                graph=g, h=h, coordinates=xy, start=start, target=target)


def random_case(n=30, seed=17):
    """Weighted directed graph with a reachable target and zero heuristic."""
    r = Random(seed)
    g = {str(i): [] for i in range(n)}
    for i in range(n):
        for j in range(n):
            if i != j and (j == i+1 or r.random() < 0.13):
                g[str(i)].append((str(j), r.randint(0, 20)))
    return dict(name=f'Random-{n}-seed{seed}', graph=g,
                h={u: 0 for u in g}, start='0', target=str(n-1))
