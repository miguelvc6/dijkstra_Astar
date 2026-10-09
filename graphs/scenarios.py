"""Deterministic benchmark families and offline lecture demonstration problems."""
import json
import math
from pathlib import Path
from random import Random

from graphs.fixtures import main_case

ROOT = Path(__file__).resolve().parents[1]


def case(name, family, graph, coordinates, start, target, *, renderer='graph', **metadata):
    item = dict(name=name, family=family, graph=graph, coordinates=coordinates,
                start=start, target=target, renderer=renderer, metadata=metadata)
    item['heuristics'] = {'zero': dict.fromkeys(graph, 0)}
    if coordinates:
        # A scaled Euclidean metric is consistent even for arbitrary weights.
        scale = min((weight / math.dist(coordinates[u], coordinates[v])
                     for u, arcs in graph.items() for v, weight in arcs
                     if math.dist(coordinates[u], coordinates[v]) > 0), default=1)
        scale *= 1 - 1e-12  # Avoid tiny floating-point inequality violations.
        item['heuristics']['euclidean'] = {v: scale * math.dist(xy, coordinates[target]) for v, xy in coordinates.items()}
        item['metadata']['euclidean_scale'] = scale
    item['h'] = item['heuristics'].get('euclidean', item['heuristics']['zero'])
    return item


def main():
    base = main_case()
    item = case('Main weighted graph', 'small_weighted', base['graph'], base['coordinates'], 'S', 'T')
    item['heuristics']['manhattan'] = base['h']
    item['h'] = base['h']
    return item


def unreachable():
    return case('Unreachable target', 'unreachable',
                {'S': [('A', 2), ('B', 1)], 'A': [('B', 1)], 'B': [('S', 1)], 'T': []},
                {'S': (0, 1), 'A': (1, 0), 'B': (1, 2), 'T': (3, 1)}, 'S', 'T')


def reopening():
    item = case('A* reopening', 'reopening', {'S': [('A', 3), ('B', 1)], 'A': [('T', 3)], 'B': [('A', 1)], 'T': []},
                {'S': (0, 1), 'A': (2, 2), 'B': (2, 0), 'T': (4, 1)}, 'S', 'T')
    item['heuristics']['inconsistent'] = {'S': 0, 'A': 0, 'B': 4, 'T': 0}
    return item


def complete(size):
    graph = {str(i): [(str(j), 1) for j in range(size) if j != i] for i in range(size)}
    xy = {str(i): (math.cos(2 * math.pi * i / size), math.sin(2 * math.pi * i / size)) for i in range(size)}
    return case(f'Complete graph ({size})', 'complete', graph, xy, '0', str(size - 1), size=size)


def random_graph(size, *, dense=False, seed=17):
    rng = Random(seed)
    xy = {str(i): (rng.random(), rng.random()) for i in range(size)}
    graph = {}
    for i in range(size):
        neighbors = set(range(size)) - {i} if dense else {(i + 1) % size}
        while not dense and len(neighbors) < min(4, size - 1):
            j = rng.randrange(size)
            if j != i:
                neighbors.add(j)
        # High target entry costs make the search inspect most of the graph.
        graph[str(i)] = [(str(j), rng.randint(1, 20) + (250 if j == size - 1 else 0)) for j in sorted(neighbors)]
    family = 'dense' if dense else 'sparse'
    return case(f'{family.title()} weighted graph ({size}, seed {seed})', family, graph, xy, '0', str(size - 1), size=size, seed=seed)


def queue_stress(size):
    """Many successive improvements before target extraction; all weights positive."""
    graph = {'S': [(f'A{i}', i) for i in range(1, size + 1)], 'T': []}
    xy = {'S': (0, 0), 'T': (3, 0)}
    for i in range(1, size + 1):
        graph[f'A{i}'] = [(f'B{j}', 2 * size - 2 * i + j) for j in range(1, size + 1)]
        graph[f'B{i}'] = [('T', 4 * size)]
        xy[f'A{i}'], xy[f'B{i}'] = (1, i), (2, i)
    return case(f'Queue improvement stress ({size})', 'queue_stress', graph, xy, 'S', 'T', size=size)


def lattice(name, family, width, height, blocked, start, target, *, diagonal=False, terrain=None, renderer='grid', **metadata):
    terrain = terrain or {}
    xy = {f'{x},{y}': (x, y) for y in range(height) for x in range(width) if (x, y) not in blocked}
    graph = {}
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    if diagonal:
        directions += [(1, 1), (-1, 1), (-1, -1), (1, -1)]
    for u, (x, y) in xy.items():
        arcs = []
        for dx, dy in directions:
            v = f'{x + dx},{y + dy}'
            if v not in xy:
                continue
            if dx and dy and (f'{x + dx},{y}' not in xy or f'{x},{y + dy}' not in xy):
                continue  # Diagonal movement cannot cut through obstacle corners.
            arcs.append((v, math.hypot(dx, dy) * terrain.get(v, 1)))
        graph[u] = arcs
    item = case(name, family, graph, xy, f'{start[0]},{start[1]}', f'{target[0]},{target[1]}', renderer=renderer,
                width=width, height=height, blocked=[list(p) for p in sorted(blocked)], terrain=terrain,
                movement='8-neighbor, no corner cutting' if diagonal else '4-neighbor', **metadata)
    tx, ty = target
    minimum_cost = min([1, *terrain.values()])
    item['heuristics']['euclidean'] = {v: minimum_cost * math.hypot(x - tx, y - ty) for v, (x, y) in xy.items()}
    if diagonal:
        item['heuristics']['octile'] = {v: minimum_cost * (max(abs(x - tx), abs(y - ty)) + (math.sqrt(2) - 1) * min(abs(x - tx), abs(y - ty))) for v, (x, y) in xy.items()}
    else:
        item['heuristics']['manhattan'] = {v: minimum_cost * (abs(x - tx) + abs(y - ty)) for v, (x, y) in xy.items()}
    item['h'] = item['heuristics'].get('manhattan', item['heuristics'].get('octile'))
    return item


def grid(width=24, height=16, *, style='wall', diagonal=False, seed=17):
    rng = Random(seed)
    start, target = (1, height // 2), (width - 2, height // 2)
    blocked = set()
    if style == 'wall':
        blocked = {(width // 2, y) for y in range(height) if y != height - 2}
    elif style == 'obstacles':
        blocked = {(x, y) for y in range(height) for x in range(width) if rng.random() < .27}
        # Keep a known detour available without changing connectivity after generation.
        blocked -= {(1, y) for y in range(start[1], height - 1)}
        blocked -= {(x, height - 2) for x in range(1, width - 1)}
        blocked -= {(target[0], y) for y in range(target[1], height - 1)}
    elif style not in {'open', 'terrain'}:
        raise ValueError(style)
    blocked -= {start, target}
    terrain = {f'{x},{y}': 6 for y in range(2, height - 2) for x in range(width // 3, 2 * width // 3)} if style == 'terrain' else {}
    suffix = '-diagonal' if diagonal else ''
    return lattice(f'Grid {width}×{height} · {style}{suffix}', f'grid_{style}{suffix}', width, height, blocked, start, target,
                   diagonal=diagonal, terrain=terrain, seed=seed, size=width)


def maze(cells=10, *, braided=False, seed=17, game=False):
    rng = Random(seed)
    width = height = 2 * cells + 1
    open_cells = {(1, 1)}
    stack = [(1, 1)]
    while stack:
        x, y = stack[-1]
        candidates = [(x + dx, y + dy) for dx, dy in [(2, 0), (0, 2), (-2, 0), (0, -2)]
                      if 0 < x + dx < width - 1 and 0 < y + dy < height - 1 and (x + dx, y + dy) not in open_cells]
        if not candidates:
            stack.pop()
            continue
        nx, ny = rng.choice(candidates)
        open_cells.update({(nx, ny), ((x + nx) // 2, (y + ny) // 2)})
        stack.append((nx, ny))
    if braided:
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if (x, y) in open_cells:
                    continue
                joins = ((x - 1, y) in open_cells and (x + 1, y) in open_cells) or ((x, y - 1) in open_cells and (x, y + 1) in open_cells)
                if joins and rng.random() < .18:
                    open_cells.add((x, y))
    blocked = {(x, y) for y in range(height) for x in range(width)} - open_cells
    family = 'game_dungeon' if game else 'maze_braided' if braided else 'maze_perfect'
    name = 'Dungeon pursuit' if game else 'Maze with loops' if braided else 'Perfect maze'
    return lattice(f'{name} · {cells}×{cells} rooms', family, width, height, blocked, (1, 1), (width - 2, height - 2),
                   renderer='game' if game else 'grid', seed=seed, size=cells)


def street(*, query=0):
    raw = json.loads((ROOT / 'graphs/data/vienna-osm.json').read_text())
    provenance = json.loads((ROOT / 'graphs/data/vienna-osm-provenance.json').read_text())
    nodes = {str(e['id']): (e['lon'], e['lat']) for e in raw['elements'] if e['type'] == 'node'}
    lat0 = math.radians(sum(p[1] for p in nodes.values()) / len(nodes))
    lon0, base_lat = min(p[0] for p in nodes.values()), min(p[1] for p in nodes.values())
    xy = {v: (6371000 * math.radians(lon - lon0) * math.cos(lat0), 6371000 * math.radians(lat - base_lat)) for v, (lon, lat) in nodes.items()}
    graph, roads = {}, []
    for way in raw['elements']:
        if way['type'] != 'way':
            continue
        tags = way.get('tags', {})
        if tags.get('access') in {'no', 'private'} or tags.get('motor_vehicle') == 'no':
            continue
        refs = list(map(str, way['nodes']))
        one_way = tags.get('oneway', 'yes' if tags.get('junction') == 'roundabout' else 'no')
        if one_way == '-1':
            refs.reverse()
        roads.append(dict(nodes=refs, name=tags.get('name', tags.get('highway', 'Road')), oneway=one_way in {'yes', '1', 'true', '-1'}))
        for u, v in zip(refs, refs[1:]):
            if u == v or u not in xy or v not in xy:
                continue
            weight = math.dist(xy[u], xy[v])
            if weight <= 0:
                continue
            graph.setdefault(u, []).append((v, weight))
            graph.setdefault(v, [])
            if one_way not in {'yes', '1', 'true', '-1'}:
                graph[v].append((u, weight))
    # Use the largest strongly connected component so all selected OD pairs exist.
    import networkx as nx
    network = nx.DiGraph()
    network.add_nodes_from(graph)
    network.add_edges_from((u, v) for u, arcs in graph.items() for v, _ in arcs)
    keep = max(nx.strongly_connected_components(network), key=len)
    graph = {u: [(v, w) for v, w in graph[u] if v in keep] for u in sorted(keep)}
    xy = {v: xy[v] for v in graph}
    ordered = sorted(graph, key=lambda v: (xy[v][0], xy[v][1]))
    pairs = [(ordered[0], ordered[-1]), (min(graph, key=lambda v: xy[v][1]), max(graph, key=lambda v: xy[v][1])),
             (ordered[len(ordered) // 4], ordered[3 * len(ordered) // 4])]
    start, target = pairs[query % len(pairs)]
    item = case(f'Vienna streets · route {query + 1}', 'streets', graph, xy, start, target, renderer='streets',
                size=len(graph), query=query, weight_units='meters in local projection', attribution='© OpenStreetMap contributors · ODbL',
                provenance=provenance, roads=[r for r in roads if all(v in keep for v in r['nodes'])])
    return item


def demo_cases():
    return [main(), unreachable(), reopening(), random_graph(18), random_graph(12, dense=True), queue_stress(4),
            grid(), grid(style='open'), grid(style='obstacles'), grid(style='terrain'), grid(style='obstacles', diagonal=True),
            maze(10), maze(10, braided=True), street(), maze(10, braided=True, game=True)]


def benchmark_cases():
    cases = [main(), unreachable(), reopening()]
    cases += [complete(n) for n in [5, 7, 9, 11]]
    for seed in [17, 29, 43]:
        cases += [random_graph(n, seed=seed) for n in [64, 256, 1024]]
        cases += [random_graph(n, dense=True, seed=seed) for n in [32, 64, 128]]
        for n in [16, 32, 64]:
            cases += [grid(n, 3 * n // 4, style=style, seed=seed) for style in ['open', 'wall', 'obstacles', 'terrain']]
            cases += [grid(n, 3 * n // 4, style='obstacles', diagonal=True, seed=seed)]
        cases += [maze(n, braided=braided, seed=seed) for n in [8, 16, 24] for braided in [False, True]]
    cases += [queue_stress(n) for n in [8, 24, 64]]
    cases += [street(query=q) for q in range(3)]
    cases += [maze(n, braided=True, game=True) for n in [8, 16, 24]]
    cases += demo_cases()
    # Open/wall/terrain grids do not depend on the seed. Measure each distinct
    # instance once instead of presenting repeated identical graphs as new data.
    unique = {}
    for item in cases:
        key = (item['family'], json.dumps(item['graph'], sort_keys=True), item['start'], item['target'])
        unique.setdefault(key, item)
    return list(unique.values())
