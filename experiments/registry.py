"""Adapters call the unmodified lecture functions."""
from algorithms import depth_first, dijkstra_lazy_list, dijkstra_lazy_heap, dijkstra_eager_heap, astar

FUNCTIONS = {'depth_first': depth_first, 'list': dijkstra_lazy_list, 'lazy': dijkstra_lazy_heap, 'eager': dijkstra_eager_heap}
LABELS = {'depth_first': 'Exhaustive DFS', 'list': 'Dijkstra · list', 'lazy': 'Dijkstra · lazy heap', 'eager': 'Dijkstra · eager heap'}


def variants(case, *, include_dfs=True):
    return (['depth_first'] if include_dfs else []) + ['list', 'lazy', 'eager'] + ['astar-' + name for name in case['heuristics']]


def function(key):
    return astar if key.startswith('astar-') else FUNCTIONS[key]


def label(key):
    return 'A* · ' + key.removeprefix('astar-') if key.startswith('astar-') else LABELS[key]


def arguments(key, case):
    args = (case['graph'], case['start'], case['target'])
    return args + (case['heuristics'][key.removeprefix('astar-')],) if key.startswith('astar-') else args
