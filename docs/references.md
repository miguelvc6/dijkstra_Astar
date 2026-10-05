# References and provenance

The numerical graphs, illustrations, code, exercises, and experimental measurements in this repository are original teaching material. The following sources support the general theory and historical context. No third-party slide images, game sprites, fonts, or book chapters are redistributed.

## Algorithmic sources

**[R1] E. W. Dijkstra (1959).** A Note on Two Problems in Connexion with Graphs. *Numerische Mathematik* 1, 269-271. DOI: 10.1007/BF01386390. Original article: https://ir.cwi.nl/pub/9256/9256D.pdf

**[R2] Python Software Foundation.** `heapq` documentation, especially Priority Queue Implementation Notes. Supports the heap invariant, replacement entries, and counter-based tie-breaking. https://docs.python.org/3/library/heapq.html

**[R3] UC Berkeley CS188.** Informed Search. Supports greedy best-first search, A*, admissibility, and heuristics from relaxed problems. Note: the lecture separately makes graph-search reopening explicit. https://inst.eecs.berkeley.edu/~cs188/textbook/search/informed.html

**[R4] Stanford CS221.** Search II, Spring 2023 lecture materials. See slides 22-23 (uniform-cost correctness), 34-43 (reweighting and consistency), and 54 onward (relaxations). https://stanford-cs221.github.io/spring2023-extra/modules/search/search2.pdf

**[R5] NetworkX developers.** `all_simple_paths` documentation. Supports the distinction between simple-path enumeration and a single DFS traversal, and factorial growth in complete graphs. https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.all_simple_paths.html

**[R6] J. Moy (1998).** OSPF Version 2, RFC 2328, section 16.1. Concrete application of shortest-path trees, next hops, and outgoing interfaces. https://www.rfc-editor.org/rfc/rfc2328.html#section-16.1

**[R7] Mo Chen et al. (2007).** Priority Queues and Dijkstra's Algorithm. Technical Report TR-07-54. Experimental evidence that a decrease-key implementation need not be faster on a given workload. https://www3.cs.stonybrook.edu/~rezaul/papers/TR-07-54.pdf

**[R8] Ran Duan, Jiayi Mao, Xiao Mao, Xinkai Shu, Longhui Yin (2025).** Breaking the Sorting Barrier for Directed Single-Source Shortest Paths. arXiv:2504.17033, version 2. A deterministic O(m log^(2/3) n) bound in the comparison-addition model. This is a research note, not an algorithm implemented here or a claim about the current best bound in every model. https://arxiv.org/abs/2504.17033v2

## Pedagogical inspiration

**[P1] Otto Toeplitz.** *The Calculus: A Genetic Approach*. University of Chicago Press. The approach motivates concepts through their intellectual genesis; this lecture is a rational reconstruction, not a historical account of Dijkstra or A*. https://press.uchicago.edu/ucp/books/book/chicago/C/bo5485725.html

**[P2] Imre Lakatos (1976).** *Proofs and Refutations: The Logic of Mathematical Discovery*. Edited by John Worrall and Elie Zahar. Cambridge University Press. https://www.cambridge.org/core/books/proofs-and-refutations/575FC8A6B4FAB79E649EDF5FBB9C6E10

## Citation and implementation notes

References such as [R2] in the slides and guide point to these entries. The lecturer's questions, proofs, graph designs, and implementations are newly written. A cited source need not use the same exact code variant or counting convention. The implementation contract and measured counters are defined in `docs/technical_notes.md`; they take precedence when interpreting the supplied results.
