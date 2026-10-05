"""Dependency-free lecture implementations (Python 3.10+).

Lazy exports keep `python -m algorithms.dijkstra` and the other CLIs free of
runpy's double-import warning. Import specific modules for library internals.
"""
from importlib import import_module
__all__ = ['brute_force', 'dijkstra_lazy', 'dijkstra_eager', 'astar']

def __getattr__(name):
    modules = {'brute_force': '.brute_force', 'dijkstra_lazy': '.dijkstra',
               'dijkstra_eager': '.dijkstra', 'astar': '.astar'}
    if name not in modules:
        raise AttributeError(name)
    fn = getattr(import_module(modules[name], __name__), name)
    globals()[name] = fn
    return fn
