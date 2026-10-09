"""Independent reference solutions and route/heuristic validation."""
import hashlib
import json
import math
import networkx as nx


def network(case):
    graph = nx.DiGraph()
    graph.add_nodes_from(case['graph'])
    for u, arcs in case['graph'].items():
        for v, weight in arcs:
            if v not in case['graph'] or not math.isfinite(weight) or weight < 0:
                raise ValueError(f'Invalid arc: {u}, {v}, {weight}')
            # Adjacency lists may contain parallel arcs; retain the cheapest.
            if not graph.has_edge(u, v) or weight < graph[u][v]['weight']:
                graph.add_edge(u, v, weight=weight)
    return graph


def reference(case):
    graph = network(case)
    try:
        cost = nx.shortest_path_length(graph, case['start'], case['target'], weight='weight', method='bellman-ford')
    except nx.NetworkXNoPath:
        cost = math.inf
    return cost


def validate(result, case, expected):
    cost, path = result
    if math.isinf(expected):
        if not math.isinf(cost) or path:
            raise AssertionError(f'Expected unreachable; received {result}')
        return
    if not math.isclose(cost, expected, rel_tol=1e-9, abs_tol=1e-8):
        raise AssertionError(f'Cost {cost} differs from reference {expected}')
    if not path or path[0] != case['start'] or path[-1] != case['target'] or len(path) != len(set(path)):
        raise AssertionError(f'Invalid route endpoints or cycle: {path}')
    route_cost = 0
    for u, v in zip(path, path[1:]):
        weights = [w for neighbor, w in case['graph'][u] if neighbor == v]
        if not weights:
            raise AssertionError(f'Route traverses nonexistent arc: {u} → {v}')
        route_cost += min(weights)
    if not math.isclose(route_cost, cost, rel_tol=1e-9, abs_tol=1e-8):
        raise AssertionError(f'Route cost {route_cost} differs from reported {cost}')


def heuristic_checks(case):
    graph = network(case)
    remaining = nx.single_source_dijkstra_path_length(graph.reverse(copy=False), case['target'], weight='weight')
    output = {}
    for name, heuristic in case['heuristics'].items():
        if set(heuristic) != set(case['graph']):
            raise ValueError('Heuristic must cover exactly the graph vertices')
        admissible = all(math.isfinite(h) and 0 <= h <= remaining.get(v, math.inf) + 1e-8 for v, h in heuristic.items()) and heuristic[case['target']] == 0
        consistent = all(heuristic[u] <= w + heuristic[v] + 1e-8 for u, arcs in case['graph'].items() for v, w in arcs)
        output[name] = dict(admissible=admissible, consistent=consistent)
        if not admissible or (name != 'inconsistent' and not consistent):
            raise AssertionError(f'Invalid {name} heuristic on {case["name"]}')
    return output


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def graph_fingerprint(case):
    return fingerprint({key: case[key] for key in ['graph', 'coordinates', 'start', 'target']})
