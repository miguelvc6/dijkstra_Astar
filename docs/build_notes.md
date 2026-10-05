# Build design and validation

## Ready to teach versus rebuilding

The committed PPTX, PDFs, PNGs, notebooks, CSVs, and standalone HTML can be used immediately. The algorithms and tests require only Python 3.10+. Regenerating documents additionally requires `requirements-build.txt`, a functioning Cairo runtime, and system fonts. On Debian/Ubuntu, `libcairo2` and `fonts-dejavu-core` cover these system prerequisites. No font files are distributed by this repository.

Run `python tools/build_all.py` from any working directory. The build writes into the repository, reruns the benchmark, validates the outputs, and replaces the distributable ZIP. Do not run it on uncommitted artifact edits you intend to preserve: edit the corresponding source instead.

## Single sources of truth

`graphs/main_graph.py` contains the recurring graph, real coordinates, and heuristic. `graphs/fixtures.py` provides counterexamples and comparison families. Graph drawings are rendered by `tools/graphics.py`; edges are labeled costs, not pixel distances.

`algorithms/` holds the four reference implementations and clearly separated incorrect experiments. `tools/trace_search.py` records their real line execution, and `tools/build_web.py` embeds those traces in `web/template.html`. No independent JavaScript search algorithm substitutes for the displayed Python. Source highlighting reports the line that just executed. Heap helpers are atomic operations at the teaching level. Choosing the heap-array view in the eager tab also displays the node-to-index mapping.

`slides/content.py` is the editable content source. `tools/make_slides.py` creates native text and shapes in PowerPoint plus a geometrically matched PDF. The PDF is generated from the same layout, not by a required Office installation. The delivered PowerPoint was also rendered in LibreOffice during authoring to check the actual presentation file. Minor font-metric and theme-shadow differences between Office renderers are possible. Sources for all graph images are provided as SVG and Python.

The Markdown files under `handouts/` are the editable print sources. The source explicitly marks intended page breaks; a build assertion protects the two-page student worksheet. A separate reference sheet resolves citations in printed material.

`tools/make_checkpoints.py` writes six student checkpoints, six solutions, and the notebooks. Worked notebook outputs are computed by executing the code during the build, not manually typed. Student blanks are intentionally incomplete. The standalone compact notebook code prioritizes reading; the fully instrumented reference implementation is in `algorithms/`.

`tools/make_fallback.py` turns selected real trace events into PDF/PNG state panels. These are static teaching snapshots, not browser screenshots and not another search simulation. `fallback/snapshot_manifest.json` identifies the exact events.

## Measurements and validation

`results/comparison.meta.json` records the interpreter, platform, repeat count, budgets, tie-breaking, and timing scope. Timings are recomputed on every build. They are machine-specific educational measurements; operation counts and exact fixture results are the stronger regression checks.

`results/test_report.txt` contains the current unit-test output. Random small graphs are cross-checked against an independent Bellman-Ford oracle, including admissible but inconsistent heuristics. Tests also cover queue invariants, zero-cost cycles, incorrect algorithms' intended failures, stale and reopening traces, and all solved checkpoints.

`results/build_validation.json` records document page counts, dependencies, test count, and benchmark rows. `docs/artifact_manifest.json` records SHA-256 checksums. The manifest excludes itself, the distributable ZIP, caches, and publication transport files.

Optional browser test:

```bash
python -m pip install playwright
python -m playwright install chromium
python -m tools.browser_smoke
```

`CHROMIUM_PATH` can point to an existing Chromium/Chrome executable. The smoke test injects the self-contained HTML into Chromium so it also works where a managed browser forbids file URLs. It checks controls, scenario outcomes, stale/reopening states, heuristic hiding, queue views, responsive layout, and absence of network requests. This browser dependency is not needed by learners or by the artifact build.

## Repository publication

The repository publication workflow reconstructs a checksum-verified source bundle uploaded through the GitHub connector, installs build dependencies, runs tests, regenerates all artifacts, and commits the result to `main`. The `publication/` transport files and `package-ready.json` are build inputs, not lecture content and are omitted from the classroom ZIP. The normal local build does not depend on them.

No private data, authentication material, fonts, or third-party game artwork is part of the bundle. A project license has deliberately not been chosen on the owner's behalf.

## Deferred scope

The separate closing-demo application (large interactive maps, maze/game scenes, and 3D renderings) is not implemented in this release. The 77-86 minute block remains deliverable through the worked notebook, saved comparisons, and static material.
