# Comparison results

Initialization + instrumented search + path recovery; no validation, rendering, tracing, I/O or oracle checks.

Runtime is machine- and implementation-dependent, not a complexity proof. CPython heapq and the Python indexed heap have different constant costs.

Case | Algorithm | Status | Cost | Expansions | Stale | Reopen | Median ms
--- | --- | --- | ---: | ---: | ---: | ---: | ---:
Main graph | brute_force | found | 8 | 13 | 0 | 0 | 0.008682
Main graph | dijkstra_lazy | found | 8 | 8 | 2 | 0 | 0.010238
Main graph | dijkstra_eager | found | 8 | 8 | 0 | 0 | 0.017913
Main graph | astar | found | 8 | 4 | 0 | 0 | 0.010403
Admissible but inconsistent | brute_force | found | 5 | 4 | 0 | 0 | 0.003609
Admissible but inconsistent | dijkstra_lazy | found | 5 | 3 | 1 | 0 | 0.004823
Admissible but inconsistent | dijkstra_eager | found | 5 | 3 | 0 | 0 | 0.007747
Admissible but inconsistent | astar | found | 5 | 4 | 0 | 1 | 0.006865
Complete-5 | brute_force | found | 1 | 16 | 0 | 0 | 0.01297
Complete-5 | dijkstra_lazy | found | 1 | 4 | 0 | 0 | 0.005608
Complete-5 | dijkstra_eager | found | 1 | 4 | 0 | 0 | 0.009015
Complete-5 | astar | found | 1 | 1 | 0 | 0 | 0.005908
Complete-7 | brute_force | found | 1 | 326 | 0 | 0 | 0.205872
Complete-7 | dijkstra_lazy | found | 1 | 6 | 0 | 0 | 0.008188
Complete-7 | dijkstra_eager | found | 1 | 6 | 0 | 0 | 0.013116
Complete-7 | astar | found | 1 | 1 | 0 | 0 | 0.007499
Complete-9 | brute_force | budget_exhausted | 2 | 12504 | 0 | 0 | 8.789333
Complete-9 | dijkstra_lazy | found | 1 | 8 | 0 | 0 | 0.011048
Complete-9 | dijkstra_eager | found | 1 | 8 | 0 | 0 | 0.018515
Complete-9 | astar | found | 1 | 1 | 0 | 0 | 0.00902
Complete-11 | brute_force | budget_exhausted | 4 | 12504 | 0 | 0 | 9.518159
Complete-11 | dijkstra_lazy | found | 1 | 10 | 0 | 0 | 0.013923
Complete-11 | dijkstra_eager | found | 1 | 10 | 0 | 0 | 0.024255
Complete-11 | astar | found | 1 | 1 | 0 | 0 | 0.010136
Random-40-seed17 | brute_force | not_run_size_limit |  |  |  |  | 
Random-40-seed17 | dijkstra_lazy | found | 29 | 26 | 8 | 0 | 0.042781
Random-40-seed17 | dijkstra_eager | found | 29 | 26 | 0 | 0 | 0.099328
Random-40-seed17 | astar | found | 29 | 26 | 8 | 0 | 0.060127
Random-180-seed17 | brute_force | not_run_size_limit |  |  |  |  | 
Random-180-seed17 | dijkstra_lazy | found | 3 | 151 | 28 | 0 | 0.505682
Random-180-seed17 | dijkstra_eager | found | 3 | 151 | 0 | 0 | 1.08661
Random-180-seed17 | astar | found | 3 | 151 | 28 | 0 | 0.608085
Grid-24x16-open-zero | brute_force | not_run_size_limit |  |  |  |  | 
Grid-24x16-open-zero | dijkstra_lazy | found | 21 | 288 | 0 | 0 | 0.291969
Grid-24x16-open-zero | dijkstra_eager | found | 21 | 288 | 0 | 0 | 0.758912
Grid-24x16-open-zero | astar | found | 21 | 288 | 0 | 0 | 0.409366
Grid-24x16-open-euclidean | brute_force | not_run_size_limit |  |  |  |  | 
Grid-24x16-open-euclidean | dijkstra_lazy | found | 21 | 288 | 0 | 0 | 0.294044
Grid-24x16-open-euclidean | dijkstra_eager | found | 21 | 288 | 0 | 0 | 0.755437
Grid-24x16-open-euclidean | astar | found | 21 | 21 | 0 | 0 | 0.070073
Grid-24x16-open-manhattan | brute_force | not_run_size_limit |  |  |  |  | 
Grid-24x16-open-manhattan | dijkstra_lazy | found | 21 | 288 | 0 | 0 | 0.290177
Grid-24x16-open-manhattan | dijkstra_eager | found | 21 | 288 | 0 | 0 | 0.748295
Grid-24x16-open-manhattan | astar | found | 21 | 21 | 0 | 0 | 0.06925
Grid-24x16-wall-zero | brute_force | not_run_size_limit |  |  |  |  | 
Grid-24x16-wall-zero | dijkstra_lazy | found | 33 | 315 | 0 | 0 | 0.318604
Grid-24x16-wall-zero | dijkstra_eager | found | 33 | 315 | 0 | 0 | 0.769667
Grid-24x16-wall-zero | astar | found | 33 | 315 | 0 | 0 | 0.436612
Grid-24x16-wall-euclidean | brute_force | not_run_size_limit |  |  |  |  | 
Grid-24x16-wall-euclidean | dijkstra_lazy | found | 33 | 315 | 0 | 0 | 0.31373
Grid-24x16-wall-euclidean | dijkstra_eager | found | 33 | 315 | 0 | 0 | 0.773509
Grid-24x16-wall-euclidean | astar | found | 33 | 269 | 0 | 0 | 0.400778
Grid-24x16-wall-manhattan | brute_force | not_run_size_limit |  |  |  |  | 
Grid-24x16-wall-manhattan | dijkstra_lazy | found | 33 | 315 | 0 | 0 | 0.321277
Grid-24x16-wall-manhattan | dijkstra_eager | found | 33 | 315 | 0 | 0 | 0.772002
Grid-24x16-wall-manhattan | astar | found | 33 | 224 | 0 | 0 | 0.359991
