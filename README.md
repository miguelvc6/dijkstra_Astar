# Dijkstra and A* pathfinding study

This project compares several shortest-path algorithms on the same graph scenarios:

- brute-force depth-first search
- Dijkstra with a lazy list queue
- Dijkstra with a lazy binary heap
- Dijkstra with an eager indexed heap
- A* with a heuristic and reopening policy

The code is designed for teaching, experimentation, and benchmarking, with small reproducible cases plus larger graph fixtures and generated result artifacts.

## Repository layout

- `algorithms/` — pathfinding implementations
- `graphs/` — graph fixtures and scenarios
- `experiments/` — validation, metrics, and experiment runner
- `tools/` — reporting and benchmark helpers
- `docs/` — notes on complexity and references
- `results/` — generated outputs and figures
- `tests/` — automated validation checks

## Quick start

No requirements needed for the algorithms.

```bash
python -m venv .venv
source .venv/bin/activate

python algorithms/05_astar.py
```

Requirements for build only:

```bash
pip install -r requirements-build.txt

```

## Example

The canonical example in `graphs/main_graph.py` defines a nine-node graph with a Manhattan-distance heuristic. Running `python algorithms/05_astar.py` yields the optimal path and total cost.

## Notes

- The implementations intentionally favor clarity over production polish.
- Complexity notes live in `docs/complexity.md`.
- Experiment outputs and summaries are stored under `results/`.
