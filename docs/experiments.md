# Pathfinding experiments and animation laboratory

The experiment suite calls the lecture functions in `algorithms/` without changing them. Runtime measurement, peak allocation measurement, and operation observation are separate runs. Animation events also come from those actual functions, not a second browser implementation of search.

## Open the lecture material

- [Animation field lab](../web/experiments.html): fifteen problems, side-by-side search playback, heuristic comparisons, optional comment-free Python code, street routes, and a sprite-based dungeon pursuit.
- [Measured results](../web/benchmarks.html): runtime and memory figures, heuristic expansion comparisons, exhaustive DFS growth, and a filterable table of every configuration.
- [Existing code laboratory](../web/visualizer.html): the original line-by-line main-graph/grid demonstration.

Open the HTML files directly in a modern browser. The animation data and sprite atlas are embedded, and the results page loads its figures from the local `results/` directory. The pages have been tested with network requests blocked. Keep the repository directory structure when copying the material to another computer. Loading uses the browser's built-in gzip `DecompressionStream`.

Use **Step event** to reveal individual search events, **Step expansion** to move each side to its next expansion, or **Play** for continuous playback. **Show route** completes both searches. The progress slider supports replay. Space toggles playback, right arrow steps expansions, and R resets. In the dungeon, the enemy follows the returned route after its search completes. Toggle the overlay to reveal or hide the search state beneath the sprites.

Playback advances by events; it is not a runtime race. The measured median and peak Python allocations beside each animation come from the benchmark on that same graph and algorithm.

## Problem collection

| Family | Instances and purpose |
| --- | --- |
| Small weighted graphs | Canonical nine-node example, unreachable target, and an admissible inconsistent heuristic that forces A* to reopen a vertex |
| Complete graphs | 5, 7, 9, and 11 vertices; reveal exhaustive simple-path enumeration growth |
| Sparse weighted graphs | 64, 256, and 1,024 vertices, plus a small animation example; four outgoing arcs per vertex and a reachability backbone |
| Dense weighted graphs | 32, 64, and 128 vertices, plus a small animation example; all ordered vertex pairs are connected |
| Queue-improvement stress | Successive cheaper routes create many lazy records and eager decrease-key operations |
| Open and wall grids | Four-neighbor unit moves; a wall with a low gap forces a detour |
| Random obstacle grids | Seeded obstacles with a guaranteed route; four-neighbor and eight-neighbor variants |
| Weighted terrain | Entering the central terrain band costs six times as much; cheaper paths can use more steps |
| Perfect mazes | A seeded spanning-tree maze has exactly one simple route between any two floor cells |
| Mazes with loops | Extra openings create alternative routes |
| Streets | Saved Vienna geometry: 1,865 vertices and 2,711 directed arcs, with three origin–destination queries |
| Dungeon pursuit | A maze-with-loops graph rendered with pixel sprites, followed by enemy movement along the computed route |

Random graph, obstacle, and maze families use seeds 17, 29, and 43. Identical deterministic instances are deduplicated. Grid scaling uses widths 16, 32, and 64, with height three quarters of width; maze scaling uses 8, 16, and 24 rooms per side. Additional instances match the animation scenes. The catalogue contains **90 scenario entries and 86 unique graph/start–target inputs**. Four dungeon scenarios deliberately reuse the maze-with-loops inputs to demonstrate that changing the visual presentation does not change the search problem. Their measurements are retained as separate scenario runs, not treated as independent random graph instances.

Grid heuristics are zero, Euclidean, and Manhattan for four-neighbor movement, or zero, Euclidean, and octile for diagonal movement. Diagonal edges cost √2 and cannot cut through blocked corners. Weighted-terrain estimates use the minimum step cost. Arbitrary weighted graphs use Euclidean distance scaled by the minimum edge-cost/displacement ratio. All heuristics are checked against exact remaining costs for admissibility and against every arc for consistency. The named reopening heuristic is deliberately inconsistent but remains admissible.

Street costs and heuristics use meters in a local projection. Roads preserve basic one-way direction. See [street provenance and modeling details](../graphs/data/README.md). The game uses [Kenney Tiny Dungeon](https://kenney.nl/assets/tiny-dungeon), licensed CC0; the original license, atlas, source URL, retrieval timestamp, and archive hash are in `web/assets/tiny-dungeon/`. These are actual licensed sprites, not Nintendo assets.

## Recorded experiment

The delivered run is in [results/latest](../results/latest/manifest.json). It contains **598 configurations**:

- **515** completed timing, memory, and operation-count measurements, all validated.
- **82** explicit DFS skips on graphs larger than eleven vertices.
- **1** DFS memory-observation timeout on the eleven-vertex complete graph. Its correctness and nine uninstrumented timing samples completed; the unfinished memory/operation phases have no estimates.

There are **4,644 raw timing samples** across 516 completed timing phases. Each completed search result was checked against an independent NetworkX Bellman–Ford distance and validated for endpoints, real arcs, absence of cycles, and matching path cost. Equal-cost alternative routes are accepted. The verification tool independently replays completed timing configurations and rechecks every input fingerprint.

The original implementations in `algorithms/` remained byte-for-byte unchanged. Source hashes, machine and Python details, package versions, seeds, input fingerprints, and phase-specific failures are recorded alongside the data. The [verification record](../results/latest/verification.json) and [browser verification record](../results/browser-checks/verification.json) provide the audit results.

### Examples from this machine

| Problem | Algorithm | Median runtime | Peak Python allocations | Peak frontier |
| --- | --- | --- | --- | --- |
| Queue stress, 130 vertices / 4,224 arcs | Lazy-list Dijkstra | 98.379 ms | 393.0 KiB | 4,096 |
| Same problem | Lazy-heap Dijkstra | 1.609 ms | 546.5 KiB | 4,096 |
| Same problem | Eager-heap Dijkstra | 0.861 ms | 25.1 KiB | 127 |

This constructed workload makes queue differences visible. It does not establish a universal winner: eager Python heap bookkeeping can cost more time on other families, and a smaller queue does not always imply fewer total Python allocations. For example, on the 64×48 wall grid, Manhattan A* expanded 2,128 vertices versus Dijkstra's 2,675, while their measured runtimes were similar. Runtime also depends on heuristic evaluation, queue behavior, and implementation overhead.

The exhaustive DFS medians on complete graphs grew from approximately 0.0043 ms at V=5, to 0.0813 ms at V=7, 3.699 ms at V=9, and 285.235 ms at V=11. The V=11 memory phase exceeded its separate 0.5-second instrumented-call deadline. The runtime plot preserves its completed timing samples and labels the failed phase.

These figures describe this machine and these chosen inputs. Timing plots provide empirical evidence of growth, not a proof of asymptotic bounds. Consult the saved sample spread rather than interpreting tiny timing differences as definitive.

## Measurement protocol

Each algorithm–problem configuration uses a fresh, sequential worker process. Imports and graph construction happen before measurement. Two warm-ups and one calibration precede nine timed samples. Fast searches are batched toward 10 ms per sample, with at most 1,000 calls; actual batch size and every per-call sample are saved. Samples can be shorter than the target when the cap is reached. Garbage collection stays enabled during search, with a collection outside the timer before each sample.

Time uses [`time.perf_counter_ns`](https://docs.python.org/3/library/time.html#time.perf_counter_ns). Only the algorithm call, including path construction and ordinary allocation/cleanup, is inside the timer. Validation, rendering, observation, graph generation, and process startup are excluded.

Memory uses [`tracemalloc`](https://docs.python.org/3/library/tracemalloc.html#tracemalloc.get_traced_memory) during one separate call. Reported values are **peak traced Python allocations**, including the output path. They exclude the graph and supplied heuristic that already exist before tracing starts, and exclude the observer. They are not peak process resident memory or a theoretical minimum memory requirement.

Operation counts use `sys.settrace` in another separate call. Expansions count outgoing-edge processing and exclude terminal target extraction. Re-expansions count repeated processing of a vertex; stale records are counted separately. Edge examinations count every adjacency entry tested. Insertions include the initial frontier entry, decrease-key counts only in-place eager updates, and peak frontier includes lazy duplicates. For DFS, expansions are recursive path-prefix expansions; recursive call count and maximum depth are reported separately. Its frontier-size field is zero because it has no priority queue.

Each call has a deadline: 0.5 seconds for DFS, 10 seconds for other algorithms, plus a parent process timeout. A timeout preserves completed earlier phases and records the phase that was interrupted. Skips and failures carry no fabricated estimates. The runner fails on correctness or worker errors.

Runtime and memory scaling figures show medians across available instance measurements, with the instance range as whiskers. Those whiskers are not confidence intervals. The table also gives the first and third quartiles of the nine samples for each configuration. Heuristic charts compare algorithms on one identical graph and endpoint pair per panel.

## Reproduce and extend

Install experiment dependencies in your Python environment:

```sh
python -m pip install -r requirements-experiments.txt
```

The saved data and sprites are already included. Only if assets are missing, fetch them with:

```sh
python -m tools.fetch_demo_assets
```

Run the full suite into a new directory, preserving the delivered results:

```sh
python -m tools.benchmark --output results/my-run
python -m tools.verify_experiments --results results/my-run
python -m tools.report_experiments --results results/my-run
python -m tools.build_experiments --results results/my-run
```

Use `--resume` with the same parameters and output directory to continue an interrupted run. Resume refuses changed sources, configuration, or inputs. For a smaller run, use `--suite demo --repeats 3 --sample-ms 1`; it still covers every animation family.

To rebuild animations with the delivered measurements:

```sh
python -m tools.build_experiments
```

The animation builder defaults to measurements from `results/latest`; use `--results` to attach another run. It refuses measurements from different algorithm sources. All delivered pages refer to the delivered run.

Validate the generators, adapters, operation counts, heuristics, and worker behavior:

```sh
python -m unittest discover -s tests -v
```

Run the isolated headless browser checks:

```sh
npm ci
npx playwright install chromium
npm run test:browser
```

The browser check exercises all 89 animation runs, stepping, completion, overlays, heuristic/code toggles, playback, scrubbing, dungeon actor motion, mobile layout, dashboard filters, local figures, and the existing visualizer. Screenshots and a verification record are saved in `results/browser-checks/`.

Add new problem generators in `graphs/scenarios.py`, benchmark adapters in `experiments/`, and visual presentation in `web/experiments-template.html`. Keep modifications for instrumentation outside `algorithms/`; the current observer requires no algorithm edits or copies.

## Artifacts

- `results/latest/manifest.json`: protocol, source hashes, environment, case catalogue, and statuses.
- `results/latest/raw.jsonl`: per-configuration measurements, raw samples, operation counts, and any phase-specific failure.
- `results/latest/summary.csv` and `samples.csv`: analysis-friendly exports.
- `results/latest/cases.json.gz`: exact input snapshots, independently checked against the recorded fingerprints.
- `results/latest/verification.json`: coverage, replay, and source/data integrity audit.
- `results/latest/figures/`: standalone PNG and SVG figures for lecture slides.
- `results/demo-validation.json`: all animation results and heuristic checks.
- `results/browser-checks/`: screenshots and offline browser verification.
