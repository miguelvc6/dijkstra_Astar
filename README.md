# Dijkstra and A*: when can a route be finalized?

A **90-minute PhD lecture** built as a guided reconstruction: propose a search rule, test it, identify a failed assumption, and repair it. The package follows a genetic / proofs-and-refutations approach rather than presenting two finished algorithms back to back.

**Ready-to-use teaching artifacts are committed in this repository.** No closing-demo application is included; that separate application is deferred. The current notebook and saved comparisons cover the final experiment block.

## Start here

| Artifact | Open this file |
|---|---|
| PowerPoint, with speaker notes | [slides/dijkstra_astar.pptx](slides/dijkstra_astar.pptx) |
| Slide PDF | [slides/dijkstra_astar.pdf](slides/dijkstra_astar.pdf) |
| Printable teacher's guide | [handouts/teacher_guide.pdf](handouts/teacher_guide.pdf) |
| Editable teacher's guide | [handouts/teacher_guide.md](handouts/teacher_guide.md) |
| Two-page student worksheet | [handouts/student_worksheet.pdf](handouts/student_worksheet.pdf) |
| Worked answers | [handouts/worksheet_solutions.pdf](handouts/worksheet_solutions.pdf) |
| Offline code visualizer | [web/visualizer.html](web/visualizer.html) — download and open locally |
| Student / worked notebooks | [notebooks/](notebooks/) |
| Main graph: PNG, SVG, Python, JSON | [graphs/](graphs/) |
| Saved comparisons and metadata | [results/](results/) |
| Emergency static snapshots | [fallback/fallback.pdf](fallback/fallback.pdf) |
| Complete downloadable pack | [dist/dijkstra-astar-lecture.zip](dist/dijkstra-astar-lecture.zip) |

The HTML runs from `file://` without a server, internet connection, external assets, or Python. GitHub displays its source; use **Download raw file** and open the downloaded file in a browser. Keyboard: arrows = next/previous meaningful event; Shift+arrows = executed line; R = reset; Space = play/pause.

## Run the algorithms

Python **3.10+**; no pip installation is required for the reference algorithms, tests, or comparison runner. Run commands from the repository root:

```bash
python -m algorithms.brute_force
python -m algorithms.dijkstra
python -m algorithms.dijkstra --eager
python -m algorithms.dijkstra --all
python -m algorithms.astar
python -m algorithms.astar --reopening
python -m algorithms.astar --zero
python -m unittest discover -s tests -v
python -m tools.benchmark --repeats 9 --output results/comparison.csv
```

`algorithms/dijkstra.py` contains both lazy and eager variants plus a complete indexed binary heap. The A* reference supports reopening. Intentionally incorrect algorithms are isolated in `algorithms/experiments.py` and clearly labeled. All simple paths are enumerated by the brute-force reference; this is not a single DFS traversal or BFS.

## Live coding

Use `notebooks/lecture_student.ipynb` for blanks or `notebooks/lecture_solutions.ipynb` for a ready-to-run demonstration. Jupyter is optional and is not needed for scripts. To install notebook support in your own environment: `python -m pip install jupyterlab`.

The six checkpoints also run as modules, for example:

```bash
python -m checkpoints.solutions.02_lazy_relaxation
python -m checkpoints.solutions.05_eager_queue
python -m checkpoints.solutions.06_astar
```

Student checkpoints intentionally raise `NotImplementedError` or contain incomplete conditions. They are exercises, not runnable reference solutions. Use `checkpoints/README.md` to match each checkpoint to the lecture time.

## The recurring graph and guarantees

The main graph has **9 nodes and 14 directed edges**. Its optimum is **S -> A -> B -> C -> T**, cost **8**. Its coordinate-based Manhattan heuristic is consistent. The reference tests establish these illustrative counts:

| Implementation | Cost | Expansions | Pops | Stale skips | Decrease-key | Peak queue |
|---|---:|---:|---:|---:|---:|---:|
| Lazy Dijkstra | 8 | 8 | 11 | 2 | 0 | 6 |
| Eager Dijkstra | 8 | 8 | 9 | 0 | 4 | 4 |
| A* | 8 | 4 | 5 | 0 | 0 | 6 |

Goal extraction is not an expansion. Ties are FIFO by the latest insertion or strict priority improvement. Brute force examines 8 complete simple paths; its recursive-prefix work is a different counting unit.

The separate four-node example uses an **admissible but inconsistent** heuristic. Correct reopening A* returns cost 5 with one re-expansion; the intentionally permanently closed variant returns 6. The main graph's overestimation preset sets h(A)=20 and returns cost 11, illustrating loss of the optimality guarantee.

See [technical notes](docs/technical_notes.md) for complete assumptions, proof details, complexity, numerical limitations, result semantics, and measurement conventions. An early-stopped Dijkstra run does **not** certify every tentative label. A*'s expanded set is not automatically a finalized set.

## Lecture schedule

| Minutes | Topic |
|---|---|
| 00-09 | Applications, problem model, graph representation |
| 09-16 | Brute-force simple-path enumeration |
| 16-28 | Relaxation, Dijkstra finalization, negative-edge refutation |
| 28-41 | Lazy Dijkstra, stale records, parents, early stop |
| 41-48 | Eager queue and complexity |
| 48-54 | Why target information might help |
| 54-68 | A*, admissibility, consistency, reopening |
| 68-77 | A* code and conditional complexity |
| 77-86 | Comparative notebook experiments |
| 86-90 | Synthesis and exit exercise |

## Rebuild the artifacts

Editable sources are the Python build tools, `slides/content.py`, the Markdown handouts, graph fixtures, and `web/template.html`. Traces come from the actual Python implementations through `sys.settrace`; the browser does not run a parallel search implementation.

```bash
python -m pip install -r requirements-build.txt
python tools/build_all.py
```

This regenerates PNG/SVG graphs, code traces, the standalone visualizer, checkpoint notebooks, instrumented benchmark outputs, the PowerPoint, PDFs, static fallbacks, and the distributable ZIP. Rebuilding reruns benchmarks on the current machine, so elapsed times can change. Python source, fixtures, operation counts, and tie-breaking are deterministic. See `docs/build_notes.md` for the build design and validation steps.

Optional browser smoke tests use Playwright; they are separate from the dependency-free algorithm tests. The test runner checks small random graphs against an independent Bellman-Ford oracle and exercises the indexed heap, zero-cost cycles, ties, unreachable goals, all-distances mode, reopening, and invalid inputs.

## Sources, scope, and reuse

The diagrams and examples are original. [References](docs/references.md) link to original papers, official documentation, and university lecture sources. No Google Maps implementation claim is made; no third-party game sprites, book chapters, or font files are distributed. A project license has not been selected.

The closing-demo application (street maps, game/maze scenes, or Three.js) is intentionally absent. This does not prevent delivering the planned 90-minute lecture using the supplied notebook comparisons and static fallbacks.
