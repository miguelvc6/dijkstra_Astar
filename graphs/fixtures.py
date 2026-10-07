"""Small counterexamples and deterministic graph families."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from copy import deepcopy
from math import hypot
from random import Random
from graphs.main_graph import GRAPH, COORDINATES, HEURISTIC


def main_case():
    return dict(name='Main graph', graph=deepcopy(GRAPH), h=dict(HEURISTIC),
                coordinates=dict(COORDINATES), start='S', target='T', optimal=8)


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
