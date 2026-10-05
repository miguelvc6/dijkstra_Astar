# Slide map and speaker notes

25 core slides; the appendix is not part of the 90-minute schedule.

## 01. Dijkstra and A* (00-01)

Open with the question of certification, not the names of data structures. Ask: finding a route is one task; how would we know no cheaper route remains? Explain that the lecture reconstructs decisions through counterexamples rather than retelling historical discovery. Prerequisites: graphs, elementary Python, asymptotic notation. Do not show the solution path yet. Pedagogical inspiration: P1, P2.

## 02. Finding a route is only half the problem. (01-03)

Use Google Maps only as a familiar application, not a claim about its current implementation. Distinguish satellite positioning from road routing. For networks say next-hop router and outgoing interface, not application port. OSPF RFC 2328 section 16.1 is the documented Dijkstra example. Ask what objective each model optimizes; distance and travel time need not agree.

## 03. First, agree on the problem. (03-05)

Establish fixed additive nonnegative costs. We will later test why the sign assumption is needed. Distinguish cost, path, and all single-source distances. Expected boundary answers: unreachable gives infinity / no route; s=t gives cost zero and [s]. A target-limited run does not necessarily finalize all other labels.

## 04. A graph model is not a storage format. (05-09)

Show graphs/main_graph.py with heuristic values hidden. Separate navigation meshes and geographic modeling from matrix/list storage. Mention a turn-dependent cost may require the incoming direction in the state. Avoid a survey of mesh formats. Exit at minute 9 with the objective and adjacency representation agreed.

## 05. Could we simply try every route? (09-12)

Draw the main graph once on the board. Ask for the cost of S->T and any cheaper candidate. Then expose the A-B cycle. Refine unrestricted walks to simple paths. With nonnegative edge costs removing a cycle cannot worsen the route, so an optimal simple path exists whenever the goal is reachable.

## 06. Simple does not mean few. (12-16)

Complete checkpoint 01 or its notebook cell. The slide is an excerpt; the checkpoint includes adding/removing nodes from on_path. Reference result: 8 simple S-to-T paths, optimum 8. Show prepared complete-graph scaling; factorial path count is not the complexity of one DFS traversal. Do not wait for unbounded enumeration. Transition: which expensive prefixes can we discard?

## 07. Which prefixes are already dominated? (16-18)

Ask whether the expensive prefix can lead to a cheaper total using the same continuation. Under this state model it cannot. Clarify that a state must contain sufficient history; otherwise dominance can fail. Define tentative g and predecessors before naming relaxation. Do not call g the true shortest distance yet.

## 08. What should we process next? (18-22)

Trace changed labels at the board. Correct non-stale order: S, A, D, B, E, C, F, G, T. B improves 6->3; C 8->4; T 15->11->8. Use neighbor order and FIFO tickets for ties. Ask whether discovering T at 15 permits stopping. Distinguish a priority based on accumulated cost from choosing the cheapest next edge.

## 09. Why is the smallest label final? (22-26)

Collaborative proof. Let S be finalized. By induction dist(x)=delta(x); optimal-prefix relaxation gives dist(y)=delta(y). Nonnegative suffix yields delta(y)<=delta(u), while minimum extraction yields dist(u)<=dist(y). Contradiction if dist(u)>delta(u). Ask which inequality needs nonnegativity. The heap does not prove the theorem; it implements the selection rule. Full proof in appendix and technical notes.

## 10. Attack the assumption, not the conclusion. (26-28)

S->T=2, S->B=5, B->T=-4. First target extraction costs 2; optimum via B is 1. The nonnegative-suffix inequality fails. The normal reference code rejects this input. Keep Bellman-Ford as a named alternative only. Move to implementation at minute 28.

## 11. Make the proof executable. (28-34)

Use checkpoint 02; imports and initialization are prepared. The displayed ticket is shorthand for next(ticket) in the full implementation. Fill candidate and comparison, ask for a prediction, and run. Do not live-implement heapq. Keep proof meanings aligned with variables.

## 12. What happens to the old B = 6 entry? (34-38)

Use visualizer lazy/main, next meaningful events until the first stale skip. Show the sorted queue and actual heap-array views. Main target run skips B6 and C8; later old T records remain in the queue at termination. Emphasize that an obsolete path need not be nonexistent; it has just been superseded. Finish checkpoint 03.

## 13. Stop at discovery—or at certification? (38-41)

Demonstrate experiments.stop_on_generation_bug returning 15. The correct main graph returns 8. Place target check after rejecting stale records. Use target=None or --all to compute all reachable distances. Explain Result.finalized. In some graphs early target extraction leaves other finite labels improvable.

## 14. Can each frontier node have one entry? (41-46)

Use the already written IndexedMinPQ and complete checkpoint 05. Do not build the heap live. Demonstrate one decrease-key event. Main graph eager uses 9 insertions, 4 decreases and peak queue 4, versus lazy 13 insertions and peak queue 6. The FIFO ticket is refreshed on improvement so variants use aligned tie policies.

## 15. Smaller queues do not prove faster runs. (46-48)

Lazy: O(n+m log(m+1)) time and O(n+m) auxiliary memory. Eager: O((n+m)log(n+1)) time and O(n) auxiliary memory. Both exclude graph storage. Eager is not guaranteed faster; the pure-Python indexed heap and standard heapq differ in constants. Mention d-ary/Fibonacci only as an appendix extension. Protect the 54-minute A* start.

## 16. Which term in the priority mentions T? (48-51)

Point to D-E-F-G as the tempting low-cost branch. Ask students how they might avoid it without risking optimality. Use saved grid results or the notebook for the wavefront intuition; the closing application is deferred. Always compare target-stopped Dijkstra with target-stopped A*.

## 17. What if we use only the estimated distance? (51-54)

Introduce greedy best-first search briefly as the natural suggestion, not an extra implementation project. On this graph direct T is available at h=0 and would be selected, giving cost15. Reveal the main graph coordinate-based Manhattan heuristic. Ask how to retain the useful information from Dijkstra.

## 18. Keep the past. Estimate the future. (54-58)

Derive f=g+h before showing the trace. Four expansions exclude the goal pop. h is the exact cost of a relaxed Manhattan problem; every main-graph arc costs at least its Manhattan displacement. Coordinates are in graphs/main_graph.py. Now ask why adding any arbitrary estimate should preserve correctness.

## 19. What promise must the estimate make? (58-61)

Before displaying the formal definition, run visualizer overestimate/A*. It returns11 via S-B-C-T instead of8. h*(A)=6 so20 overestimates. Give the optimal-prefix frontier argument f<=C*; a suboptimal goal has f=g>C*. Do not say every f-value is a lower bound on the global optimum. Leave duplicate handling as the next proof obligation.

## 20. Does admissibility let us close forever? (61-66)

Ask for the true remaining cost from B (4). A expanded at g3 discovers T6; B at f5 improves A to2. Permanently closed A yields6; reopening yields5 with one re-expansion. Use the Broken: never reopen toggle, clearly labeled. Distinguish stale records from genuinely improved states. Keep students accountable for the queue prediction.

## 21. Recover the finalization argument. (66-68)

At B->A the inequality fails4>1+0; reweighted cost becomes-3. Explain the telescope and constant shift. Consistency gives the Dijkstra-like no-reopening guarantee. Under admissibility alone retain reopening. Full proof and reweighted diagram in the appendix. Do not exceed minute68.

## 22. A small code change. A new proof obligation. (68-73)

Complete checkpoint06, which uses the same ideas as this excerpt. Ticket is next(ticket) in the full code. Reference expanded set records statistics and never blocks improved routes. Run main, reopening, and h=0. With aligned ties, h=0 reproduces lazy Dijkstra behavior.

## 23. Which improvements did we actually obtain? (73-77)

The displayed counts are generated from the reference main graph. All correct algorithms return8. A* expands4 vs8 but peak queue6 equals lazy Dijkstra here. Eager reduces peak queue to4. Brute force examines8 complete paths with a different prefix-work unit. With consistent constant-time h the explicit-graph worst-case order remains the lazy Dijkstra bound; inconsistency can require repeated expansions. Avoid claiming universal speedup.

## 24. Compare before concluding. (77-86)

This block is currently delivered using notebooks/lecture_solutions.ipynb and results/comparison.md. No separate closing-demo application is in this release. 77-79 scaling;79-83 grid zero/Euclidean/Manhattan;83-85 diagonal unit move refutes Manhattan with (0,0)->(1,1);85-86 distinguish expansions, memory and runtime. A future closing app can replace the visual form without changing these questions.

## 25. What justifies an irreversible decision? (86-90)

Give students one minute to answer before summarizing. Discovery only supplies an upper bound. Nonnegative costs certify minimum-g extraction; A* needs a justified heuristic and correct duplicate handling. Consistency supports permanent closure; admissibility alone requires improvements to propagate, potentially through reopening. Stale rejection removes superseded records; reopening propagates a new better route. Return to the central question.

## 26. Appendix: the complete finalization proof (Appendix)

Not in the timed core. The base case is s with cost0. The equality of an optimal prefix uses the shortest-path optimal substructure. Explain unreachable states remain at infinity and are never extracted.

## 27. Appendix: the same failure in another graph (Appendix)

This is the four-node reopening example with reweighted costs. Original edges remain nonnegative. The sum telescopes to original path cost plus h(t)-h(s). The f ordering agrees with reweighted Dijkstra up to h(s).

## 28. Appendix: count paths, not just vertices. (Appendix)

Fixed distinct source and target. Choose an ordered subset of the other n-2 nodes. The complete counts grow16,326,13700,986410 for n5,7,9,11. A classroom budget may stop before reaching the complete count; do not confuse measured partial counts with this exact combinatorial count.

## 29. Appendix: a heap is a design choice. (Appendix)

Not a live implementation block. For d-ary heap height log_d n; decrease costs O(log_d n), extraction O(d log_d n). Discuss operation mix and constants. Do not equate theoretical asymptotic improvement with measured runtime superiority.

## 30. Appendix: the movement model is part of h. (Appendix)

Derive Chebyshev by using diagonals for min(|dx|,|dy|) steps, then cardinal steps for the remaining difference. If diagonal costs sqrt(2), use the corresponding relaxed metric instead. For time costs, a geometric distance must be converted with a valid speed bound.

## 31. Appendix: beyond the classical bound (Appendix)

Optional PhD-level context. Source arXiv2504.17033v2, Breaking the Sorting Barrier for Directed Single-Source Shortest Paths. It breaks the O(m+nlogn) bound on sparse graphs in the stated model. Do not label Fibonacci Dijkstra as the unqualified current state of the art. No claim is made about every computational model or current best bound.

## 32. References / algorithmic foundations (Appendix)

Full clickable URLs and additional provenance are in docs/references.md. All figures, graph examples, code and exercises in this package are newly created; cited lecture figures are not redistributed.

## 33. References / applications and perspective (Appendix)

Pedagogical inspiration: Toeplitz, The Calculus: A Genetic Approach (University of Chicago Press); Lakatos, Proofs and Refutations (Cambridge,1976). P1 and P2, including links, are in docs/references.md. This lecture reconstructs motivations and proof obligations; it does not purport to reenact the algorithms’ history.

