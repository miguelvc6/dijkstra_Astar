# Live-coding checkpoints

Run modules from the repository root, e.g. `python -m checkpoints.solutions.02_lazy_relaxation`.
The numbered student files intentionally contain blanks; they are not reference implementations.
Solutions assume valid nonnegative graphs and, for A*, an admissible h with h(T)=0.
The reference modules in `algorithms/` additionally validate inputs and collect counters.

| Checkpoint | Minutes | Edit |
|---|---|---|
| 01 | 09-16 | Path-local cycle guard and recursive extension |
| 02 | 28-34 | Accumulated cost and strict improvement |
| 03 | 34-38 | Stale record and predecessor |
| 04 | 38-41 | Goal check at extraction |
| 05 | 41-48 | Indexed queue insert/decrease |
| 06 | 68-77 | A* priority and queued-g stale check |

For the intentionally wrong early-stop behavior, use `algorithms.experiments.stop_on_generation_bug` rather than accidentally treating an incomplete checkpoint as correct.
