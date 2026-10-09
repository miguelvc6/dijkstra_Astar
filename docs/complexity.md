# Complexity of the graph algorithms

This document analyzes the implementations in `algorithms/`. The bounds are derived from the code in this repository, rather than from a generic version of each algorithm.

## Notation and assumptions

- **V**: number of vertices, including isolated vertices.
- **E**: number of directed adjacency-list entries. An undirected edge stored in both directions counts twice.
- **L**: number of vertices in the returned path, at most V under the assumptions below.
- **Q**: maximum number of queue entries held simultaneously, including stale entries.

Dictionary and set operations take expected O(1) time; list append takes amortized O(1). Arithmetic, hashing, priority comparisons, and heuristic evaluation are treated as O(1). 

**Auxiliary space excludes the supplied graph**, whose storage is O(V + E), and any supplied heuristic dictionary. It includes queues, distance and parent dictionaries, recursion, and path reconstruction. 

Dijkstra requires finite, nonnegative edge weights. For A* optimality, assume those weights and a fixed admissible heuristic with `h(target) = 0`; consistency gives the stronger complexity guarantee discussed below. The importance of nonnegative costs and consistent heuristics is explained in [Stanford CS221&#39;s Search II lecture](https://stanford-cs221.github.io/spring2023-extra/modules/search/search2.pdf).

## Overview

| Implementation                                                 | Time bound                                            | Auxiliary space | Key reason                                                                    |
| -------------------------------------------------------------- | ----------------------------------------------------- | --------------- | ----------------------------------------------------------------------------- |
| [Brute force](../algorithms/01_depth_first.py)                  | O(V!) without the iteration budget, for simple graphs | O(V)            | Enumerates simple paths by backtracking                                       |
| [Dijkstra, lazy list](../algorithms/02_dijkstra_lazy_list.py)   | O(V + E²)                                            | O(V + E)        | Up to O(E) extractions, each scanning up to O(E) entries                      |
| [Dijkstra, lazy heap](../algorithms/03_dijkstra_lazy_heap.py)   | O(V + E log(E + 2))                                   | O(V + E)        | Up to O(E) insertions and extractions from a binary heap                      |
| [Dijkstra, eager heap](../algorithms/04_dijkstra_eager_heap.py) | O((V + E) log(V + 2))                                 | O(V)            | At most one queue entry per vertex; priority improvements use decrease-key    |
| [A*, consistent heuristic](../algorithms/05_astar.py)           | O(V + E log(E + 2))                                   | O(V + E)        | Lazy heap, with no vertex re-expansion needed                                 |
| A*, admissible but inconsistent heuristic                      | O(V + A + (I + 1) log(Q + 2))                         | O(V + Q)        | A counts arc examinations including repeats; I counts successful improvements |

The polynomial bounds are worst-case upper bounds in the operation model above. Target-based early stopping can reduce the search work, but the Dijkstra and A* implementations still initialize `dist` for all V vertices.

## 1. Brute-force simple-path search

**File:** [01_depth_first.py](../algorithms/01_depth_first.py), function `depth_first`.

The nested `explore` function maintains one current path and an `on_path` set. It recursively visits every neighbor that is absent from that current path. Reaching the target ends that branch, but finding a route does not stop the overall search. There is no pruning based on `best_cost`.

### Time

Let P be the number of recursive calls and A the total number of adjacency entries examined across those calls. Without budget interruption, the implementation takes **Θ(P + A)** time. A vertex can appear in many calls through different path prefixes, so this is not the O(V + E) bound of a DFS that visits each vertex once.

In a complete directed graph with distinct start and target, there are V − 2 possible intermediate vertices. The number of complete start-to-target simple paths is

```text
sum from k = 0 to V − 2 of (V − 2)! / (V − 2 − k)!
= Θ((V − 2)!).
```

Nonterminal recursive calls also scan V − 1 neighbors, including neighbors already on the path. Consequently, this implementation takes **Θ(V · (V − 2)!)**, equivalently **Θ((V − 1)!)**, on that family as V grows. The familiar **O(V!)** bound is a convenient, looser summary. Factorial simple-path growth is also described in [NetworkX&#39;s `all_simple_paths` documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html).

### Space and current behavior

The recursion depth, current path, and `on_path` set are each at most O(V). Paths are explored sequentially rather than stored together, giving **O(V) auxiliary space** despite factorial time.

The current code returns the mutable `path` object when a better route is found. Backtracking later changes that same object, so the saved route is not preserved: the main example returns cost 8 with path `['S']`. This analysis describes that implementation. Saving a copy would preserve the route and add O(L) work whenever a new best path is recorded, while keeping O(V) live auxiliary space.

## 2. Dijkstra with a lazy list

**File:** [02_dijkstra_lazy_list.py](../algorithms/02_dijkstra_lazy_list.py), function `dijkstra_lazy_list`.

Each successful relaxation appends a new `(cost, node)` entry. Previous entries for the same vertex remain in the queue. `extract_min` scans the entire list, then removes the minimum using `queue.pop(min_idx)`.

### Time

With nonnegative weights, a vertex's first valid minimum extraction determines its shortest distance. Its outgoing arcs are examined at most once. Old entries fail `popped_g != dist[u]` and skip the adjacency loop, but extracting those entries still costs time.

Across the run:

- Initializing `dist` costs O(V).
- All adjacency examinations cost O(E).
- There are at most E successful relaxations and therefore at most E + 1 queue insertions and extractions.
- An extraction from a list of size q costs O(q): both the minimum scan and a middle removal can be linear.

If the extraction sizes are q₁, q₂, …, the time is **O(V + E + Σ qᵢ)**. Since every qᵢ is O(E + 1), the overall upper bound is **O(V + E²)**.

This differs from **O(V² + E)** textbook Dijkstra with an unsorted collection containing one tentative entry per vertex. This implementation allows duplicate entries and can perform O(E) extractions rather than O(V).

### Space

The dictionaries use O(V), and the lazy queue can hold O(E) records. Including path reconstruction, auxiliary space is **O(V + E)**.

## 3. Dijkstra with a lazy binary heap

**File:** [03_dijkstra_lazy_heap.py](../algorithms/03_dijkstra_lazy_heap.py), function `dijkstra_lazy_heap`.

This has the same relaxation and stale-entry policy as the lazy list, but uses `heapq` for insertion and minimum extraction. Tickets break equal-cost ties without comparing node names.

### Time

There are at most E successful relaxations, E + 1 insertions, and E + 1 extractions. A binary-heap operation costs O(log(q + 2)) for heap size q. The heap can contain O(E) entries, so the resulting bound is **O(V + E log(E + 2))**. Python's [heap documentation](https://docs.python.org/3/library/heapq.html) explains logarithmic heap maintenance and the replacement-entry approach to priority updates.

For simple graphs, E = O(V²), so a common alternative bound is **O((V + E) log(V + 2))**. The E-based logarithm directly describes the potentially larger lazy heap and remains appropriate when parallel arcs are allowed.

### Space

Distance and parent dictionaries take O(V); pending and stale heap entries take O(E). Auxiliary space is **O(V + E)**. Laziness simplifies priority updates but can retain more queue records than the eager implementation.

## 4. Dijkstra with an eager indexed heap

**File:** [04_dijkstra_eager_heap.py](../algorithms/04_dijkstra_eager_heap.py), function `dijkstra_eager_heap`.

`IndexedMinPQ` keeps a vertex-to-index dictionary. If a queued vertex improves, `decrease_key` updates its existing record instead of adding a duplicate.

### Time

Under the nonnegative-weight assumption, an extracted vertex cannot later obtain a strictly smaller distance. Although this code has no explicit finalized set, it therefore needs at most V insertions and V minimum extractions. Across O(E) adjacency examinations, at most E successful improvements trigger an insertion or decrease-key.

The heap contains at most V entries. Initialization costs O(V), adjacency examinations cost O(E), and heap operations cost at most

```text
O((V + E) log(V + 2)).
```

This gives **O((V + E) log(V + 2)) overall time**. There are no stale records to extract.

### Space

`dist`, `parent`, the heap, and its index dictionary each use O(V). Auxiliary space is **O(V)**, in addition to the supplied graph.

## 5. A* with a lazy heap and reopening

**File:** [05_astar.py](../algorithms/05_astar.py), function `astar`.

The queue priority is `f(v) = g(v) + h(v)`. Entries also retain their queued g value so obsolete records can be skipped. There is no permanent closed set: if a vertex improves after an earlier expansion, it is queued again and can be re-expanded.

### Consistent heuristic

A heuristic is consistent when every arc satisfies

```text
h(u) ≤ weight(u, v) + h(v).
```

Equivalently, the reweighted cost `weight(u, v) + h(v) − h(u)` is nonnegative. Ordering by g + h behaves like Dijkstra on these reweighted costs. Each vertex needs at most one expansion, each arc is examined at most once, and at most E relaxations improve a distance. See [Stanford CS221&#39;s A* analysis](https://stanford-cs221.github.io/spring2023-extra/modules/search/search2.pdf) for the reweighting argument.

For this lazy-heap implementation, time is therefore **O(V + E log(E + 2))** and auxiliary space is **O(V + E)**. A useful heuristic can reduce the actual work before target extraction without changing that worst-case upper bound. With `h = 0`, this function uses the same search priorities as lazy-heap Dijkstra.

### Admissible but inconsistent heuristic

Admissibility means h never overestimates the true remaining cost; assume `h(target) = 0`. Reopening preserves optimality under the stated assumptions, but a valid extraction no longer guarantees that a vertex will never improve again.

Define A as the total number of arc examinations, **counting re-examinations**, and I as the total number of successful distance improvements, **counting repeated improvements to the same vertex**. There are I + 1 insertions and at most I + 1 extractions. If Q is the maximum live heap size, the bounds are:

```text
Time:  O(V + A + (I + 1) log(Q + 2))
Space: O(V + Q), with Q ≤ I + 1.
```

Unlike the consistent case, A and I need not be O(E). Inconsistent heuristics can produce exponentially many re-expansions on pathological graph families, so the polynomial Dijkstra bound cannot be assumed. This behavior is analyzed in [Zhang et al., A* Search with Inconsistent Heuristics (IJCAI 2009)](https://www.ijcai.org/Abstract/09/111). Inconsistency does not imply that every run will be slow.

If each heuristic evaluation costs Cₕ rather than O(1), add **O((I + 1) · Cₕ)** time. A heuristic callable is evaluated again on each successful improvement; the function does not cache its results.

### The repository's heuristics

The main graph uses Manhattan distance, and every arc costs at least its Manhattan displacement. The grid has four-neighbor unit-cost moves, so Manhattan distance is also consistent; obstacles preserve that property. Both satisfy the consistent-case bounds.

In the grid, E = O(V), yielding **O(V log(V + 2)) time and O(V) auxiliary space** for A*, lazy-heap Dijkstra, and eager-heap Dijkstra. The lazy list has an O(V²) upper bound there.

The O(bᵈ) bound sometimes given for A* refers to an implicit search tree with branching factor b and depth d. Here V and E describe an explicit finite graph, with distances shared between routes to the same vertex; the graph-based bounds above are the relevant ones.

## 6. Indexed minimum-priority queue

**File:** [indexed_min_heap.py](../algorithms/indexed_min_heap.py), class `IndexedMinPQ`.

For q currently queued vertices:

| Operation                        | Time                    | Reason                                                            |
| -------------------------------- | ----------------------- | ----------------------------------------------------------------- |
| Construction                     | O(1)                    | Creates an empty heap, dictionary, and ticket counter             |
| Truth test,`bool(queue)`       | O(1)                    | Checks whether the heap is empty                                  |
| Membership,`node in queue`     | Expected O(1)           | Dictionary lookup                                                 |
| `_swap(i, j)`                  | Expected O(1)           | Exchanges two records and updates two index entries               |
| `_up(i)`                       | O(log(q + 2))           | Moves through at most the heap height                             |
| `_down(i)`                     | O(log(q + 2))           | Moves through at most the heap height                             |
| `insert(node, priority)`       | Amortized O(log(q + 2)) | Appends a record, records its index, and sifts upward             |
| `decrease_key(node, priority)` | Expected O(log(q + 2))  | Looks up the index, replaces the record, and sifts upward         |
| `pop_min()`                    | Expected O(log(q + 2))  | Removes the root, moves the last record to it, and sifts downward |

Heap storage and the position dictionary together use **O(q) space**. Sifting is iterative, so its extra working space is O(1). In eager Dijkstra, q ≤ V.

These bounds assume correct use: insert only absent vertices, decrease only an existing vertex's priority, and pop only a nonempty queue. `decrease_key` only sifts upward, so increasing a priority is outside its contract.

## Comparing sparse and dense graphs

For simple graphs and consistent A* heuristics:

| Implementation           | Sparse, E = Θ(V) | Dense, E = Θ(V²) |
| ------------------------ | ----------------- | ------------------ |
| Lazy-list Dijkstra       | O(V²)            | O(V⁴)             |
| Lazy-heap Dijkstra       | O(V log(V + 2))   | O(V² log(V + 2))  |
| Eager-heap Dijkstra      | O(V log(V + 2))   | O(V² log(V + 2))  |
| A*, consistent heuristic | O(V log(V + 2))   | O(V² log(V + 2))  |

The two heap-based Dijkstra variants share these time upper bounds, but their queue-space bounds differ: O(E) for lazy records versus O(V) for eager records. Big-O alone does not establish which implementation runs faster on a particular example.

All three Dijkstra variants and A* reconstruct a successful route by following parent pointers and reversing the resulting list. This costs **O(L) time and O(L) space**, already included above. If no route exists, they return `(inf, [])` after exhausting the queue.
