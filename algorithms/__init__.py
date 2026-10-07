"""Dependency-free lecture implementations (Python 3.10+).

Lazy exports let the numbered modules run with ``python -m`` without
runpy's double-import warning.
"""

from importlib import import_module

_EXPORTS = {
    "brute_force": (".01_brute_force", "brute_force"),
    "dijkstra_lazy_list": (".02_dijkstra_lazy_list", "dijkstra_lazy_list"),
    "dijkstra_lazy_heap": (".03_dijkstra_lazy_heap", "dijkstra_lazy_heap"),
    "dijkstra_eager_heap": (".04_dijkstra_eager_heap", "dijkstra_eager_heap"),
    "astar": (".05_astar", "astar"),
    # Keep existing callers working after the numbered-module rename.
    "dijkstra_lazy": (".03_dijkstra_lazy_heap", "dijkstra_lazy_heap"),
    "dijkstra_eager": (".04_dijkstra_eager_heap", "dijkstra_eager_heap"),
}
__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module, function = _EXPORTS[name]
    fn = getattr(import_module(module, __name__), function)
    globals()[name] = fn
    return fn
