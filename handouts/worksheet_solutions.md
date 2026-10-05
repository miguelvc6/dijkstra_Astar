# Worksheet solutions and trace key

Instructor copy. Distribute after the discussion, not beside the original conjectures.

## 1. Main graph

The first discovered target route is S->T with cost 15. An optimal route is S->A->B->C->T, costing 2+1+1+4=8. Exhaustive enumeration finds 8 simple S-to-T paths. The cycle A->B->A must be excluded only from the current candidate route, not globally from all candidates.

| Non-stale selected node | Improved labels | New predecessor |
|---|---|---|
| S, 0 | A=2; B=6; D=2; T=15 | S for each |
| A, 2 | B=3; C=8 | A for B and C |
| D, 2 | E=3 | D |
| B, 3 | C=4; T=11 | B for C and T |
| E, 3 | F=4 | E |
| C, 4 | T=8 | C |
| F, 4 | G=5 | F |
| G, 5 | None | None |
| T, 8 | Goal extracted; stop | Final path recovered |

Lazy Dijkstra pops and skips B=6 and C=8 before the current T=8 entry. T=11 and T=15 remain unprocessed at early termination. The complete pop sequence is S0, A2, D2, B3, E3, C4, F4, G5, B6(stale), C8(stale), T8.

**Proof:** Let u be the current minimum non-stale frontier node. On a supposedly cheaper route to u, take its first unfinalized node y and finalized predecessor x. Relaxation from x supplied a frontier label no greater than that optimal prefix cost. The nonnegative suffix means that prefix is no more costly than the whole route to u. This contradicts u's minimum label if u were suboptimal. The essential inequality is delta(y)<=delta(u). [R1, R4]

**Negative-edge refutation:** S->T=2, S->B=5, B->T=-4. A Dijkstra-style early goal pop gives 2, but the optimum is 1. The suffix can now reduce cost. The reference API rejects this graph.

<!-- PAGEBREAK -->
## 2. A* and the reopening counterexample

The main-graph heuristic is consistent. Its A* selections are S(g=0,f=6), A(2,7), B(3,7), C(4,7), T(8,8). The distracting D branch remains at f=9. The terminal target extraction is not counted as an expansion.

For the separate four-node example:

| Selected state | g | h | f | Consequence |
|---|---|---|---|---|
| S | 0 | 0 | 0 | Queue A at f=3 and B at f=5 |
| A | 3 | 0 | 3 | Discover T at g=6 |
| B | 1 | 4 | 5 | Discover improved A at g=2 |
| A again | 2 | 0 | 2 | Improve T to g=5 |
| T | 5 | 0 | 5 | Return optimum 5 |

All heuristic values are admissible: h*(S)=5, h*(A)=3, h*(B)=4, h*(T)=0. But the edge B->A violates consistency because 4 > 1+0. Permanent closure suppresses the second A expansion and returns cost 6.

**Two repairs:** Allow improved routes to reopen expanded states; or establish consistency so the Dijkstra-like finalization argument holds. Under the reference implementation, `expanded` is for statistics only.

**Reweighting:** S->A becomes 3; S->B becomes 5; B->A becomes -3; A->T remains 3. The negative reweighted edge explains the same finalization failure. This does not make the original edge weights negative.

**Overestimation test on the main graph:** Changing h(A) to 20 hides the optimal prefix. The reference A* returns cost 11 via S->B->C->T. h*(A)=6, so h(A)=20 violates admissibility.

## 3. Movement model and exit ticket

For start (0,0) and target (1,1), a unit-cost diagonal costs 1 while Manhattan gives 2. On an unobstructed eight-neighbor grid with all moves costing 1, Chebyshev distance max(|dx|,|dy|) is the exact relaxed cost. A different diagonal price requires a different argument; do not reuse this formula without the move-cost assumption.

**Exit A:** Goal discovery gives the cost of a known route, an upper bound on the optimum. Correct non-stale goal extraction is certified only under the algorithm's assumptions: nonnegative costs for Dijkstra; admissibility plus correct improvement propagation for reopening A*, or a suitable consistent-heuristic finalization implementation.

**Exit B:** A stale record was superseded by a better route already known. Reopening propagates a new, genuinely improved route after an earlier expansion. Discarding the former and allowing the latter are compatible and necessary in the lazy reopening A* implementation.

**Exit C:** Expansion count ignores heuristic-evaluation cost, queue operations, implementation constants, and per-state neighbor-generation cost. The supplied benchmarks also include initialization and path recovery. Runtime must be measured separately from animation speed.

References: `docs/references.md`. Exact conventions: `docs/technical_notes.md`.
