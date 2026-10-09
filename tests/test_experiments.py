import json
import math
import unittest

import networkx as nx

from experiments.observe import observe
from experiments.registry import arguments, function, variants
from experiments.validation import graph_fingerprint, heuristic_checks, network, reference, validate
from experiments.worker import run
from graphs.scenarios import complete, grid, main, maze, queue_stress, reopening, street, unreachable


class ExperimentTests(unittest.TestCase):
    def test_known_costs_and_paths(self):
        for case, expected in [(main(), 8), (reopening(), 5), (unreachable(), math.inf), (complete(5), 1)]:
            self.assertEqual(reference(case), expected)
            for key in variants(case):
                validate(function(key)(*arguments(key, case)), case, expected)

    def test_observation_preserves_results_and_measures_actual_queue_work(self):
        case = queue_stress(4)
        stats = {}
        for key in ['list', 'lazy', 'eager', 'astar-zero']:
            result, counts, trace = observe(key, case, record=True)
            validate(result, case, reference(case))
            self.assertEqual(result, function(key)(*arguments(key, case)))
            stats[key] = counts
            self.assertEqual(trace['events'][-1]['path'], result[1])
        self.assertEqual(stats['lazy']['stale_pops'], 12)
        self.assertEqual(stats['eager']['decrease_keys'], 12)
        self.assertEqual(stats['eager']['stale_pops'], 0)
        self.assertGreater(stats['lazy']['peak_frontier'], stats['eager']['peak_frontier'])
        self.assertEqual(stats['list']['expansions'], stats['lazy']['expansions'])

    def test_reopening_is_counted(self):
        result, counts, _ = observe('astar-inconsistent', reopening(), record=True)
        self.assertEqual(result[0], 5)
        self.assertEqual(counts['reexpansions'], 1)
        self.assertEqual(counts['expansions'], 4)
        self.assertEqual(counts['unique_expanded'], 3)

    def test_maze_tree_and_loops(self):
        perfect, braided = maze(8), maze(8, braided=True)
        graph = network(perfect).to_undirected()
        self.assertTrue(nx.is_tree(graph))
        self.assertGreater(len(nx.cycle_basis(network(braided).to_undirected())), 0)
        self.assertEqual(graph_fingerprint(maze(8)), graph_fingerprint(perfect))
        for item in [perfect, braided]:
            self.assertTrue(all(v['consistent'] for v in heuristic_checks(item).values()))

    def test_grids_reachable_and_diagonal_does_not_cut_corners(self):
        for style in ['open', 'wall', 'obstacles', 'terrain']:
            for diagonal in [False, True]:
                case = grid(16, 12, style=style, diagonal=diagonal)
                self.assertTrue(math.isfinite(reference(case)))
                heuristic_checks(case)
                for u, arcs in case['graph'].items():
                    x, y = case['coordinates'][u]
                    for v, _ in arcs:
                        nx_, ny_ = case['coordinates'][v]
                        if x != nx_ and y != ny_:
                            self.assertIn(f'{x},{ny_}', case['graph'])
                            self.assertIn(f'{nx_},{y}', case['graph'])

    def test_real_street_snapshot(self):
        case = street()
        self.assertEqual(case['metadata']['provenance']['license'], 'ODbL-1.0')
        self.assertGreater(len(case['graph']), 100)
        self.assertTrue(math.isfinite(reference(case)))
        heuristic_checks(case)
        self.assertTrue(any(u not in [v for v, _ in case['graph'][neighbor]]
                            for u, arcs in case['graph'].items() for neighbor, _ in arcs))

    def test_worker_timing_memory_and_timeout(self):
        job = dict(case=main(), algorithm='lazy', expected=8, timeout=2, repeats=3, sample_ms=1)
        row = run(job)
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(len(row['timing_samples_ns']), 3)
        self.assertGreater(row['peak_python_bytes'], 0)
        self.assertGreater(row['median_ns'], 0)
        row = run(dict(case=complete(11), algorithm='depth_first', expected=1, timeout=.001))
        self.assertEqual(row['status'], 'timeout')
        self.assertEqual(row['phase'], 'correctness')

    def test_validation_rejects_wrong_route_even_with_correct_cost(self):
        with self.assertRaises(AssertionError):
            validate((8, ['S']), main(), 8)


if __name__ == '__main__':
    unittest.main()
