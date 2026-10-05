"""Compare four implementations without visualization overhead.

python -m tools.benchmark --repeats 9 --output results/comparison.csv
Timing includes initialization, counters, heuristic work, search, and path
reconstruction. Graph validation is performed ONCE before timing. Rendering,
trace recording, printing, fixture generation, and oracle checks are excluded.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
from dataclasses import asdict
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from algorithms import brute_force, dijkstra_lazy, dijkstra_eager, astar
from algorithms.common import validate_graph, path_cost, Stats
from graphs.fixtures import main_case, reopening_case, complete_case, grid_case, random_case


def run_benchmarks(repeats=9, output='results/comparison.csv'):
    if repeats < 1:
        raise ValueError('repeats must be positive')
    cases = [main_case(), reopening_case()]
    cases += [complete_case(n) for n in [5,7,9,11]]
    cases += [random_case(n) for n in [40,180]]
    cases += [grid_case(24,16,walls,h) for walls in [False,True]
              for h in ['zero','euclidean','manhattan']]
    rows = []
    for case in cases:
        g,s,t,h = case['graph'],case['start'],case['target'],case['h']
        validate_graph(g,s,t)
        oracle = dijkstra_lazy(g,s,t,check=False).distance
        funcs = {
            'brute_force': lambda: brute_force(g,s,t,max_prefixes=25_000,check=False),
            'dijkstra_lazy': lambda: dijkstra_lazy(g,s,t,check=False),
            'dijkstra_eager': lambda: dijkstra_eager(g,s,t,check=False),
            'astar': lambda: astar(g,s,t,h,check=False),
        }
        for name,fn in funcs.items():
            row = dict(case=case['name'], algorithm=name, nodes=len(g),
                       edges=sum(map(len,g.values())), status='', optimal_cost=oracle,
                       returned_cost='', median_ms='', min_ms='', repeats=0,
                       **{k:'' for k in asdict(Stats())})
            if name == 'brute_force' and len(g)>11:
                row['status']='not_run_size_limit'
                rows.append(row)
                continue
            result = fn()  # warmup, not timed
            if result.status=='found':
                assert result.distance==oracle
                assert path_cost(g,result.path)==oracle
            timings=[]
            for _ in range(repeats):
                before=perf_counter_ns(); result=fn(); after=perf_counter_ns()
                timings.append((after-before)/1e6)
            row.update(status=result.status,
                       returned_cost=result.distance if math.isfinite(result.distance) else '',
                       median_ms=round(median(timings),6), min_ms=round(min(timings),6),
                       repeats=repeats, **asdict(result.stats))
            rows.append(row)
    out=Path(output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    meta=dict(python=platform.python_version(),platform=platform.platform(),
              machine=platform.machine(),repeats=repeats,
              timing_scope='Initialization + instrumented search + path recovery; no validation, rendering, tracing, I/O or oracle checks.',
              ties='FIFO by most recent insertion/strict improvement',
              brute_force_prefix_budget=25000, brute_force_node_limit=11,
              warning='Runtime is machine- and implementation-dependent, not a complexity proof. CPython heapq and the Python indexed heap have different constant costs.')
    out.with_suffix('.meta.json').write_text(json.dumps(meta,indent=2)+'\n')
    text=['Case | Algorithm | Status | Cost | Expansions | Stale | Reopen | Median ms',
          '--- | --- | --- | ---: | ---: | ---: | ---: | ---:']
    for r in rows:
        text.append(' | '.join(str(r[k]) for k in ['case','algorithm','status','returned_cost',
                                                  'expansions','stale_pops','reexpansions','median_ms']))
    out.with_suffix('.md').write_text('# Comparison results\n\n'+meta['timing_scope']+'\n\n'+
                                   meta['warning']+'\n\n'+'\n'.join(text)+'\n')
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repeats',type=int,default=9)
    p.add_argument('--output',default='results/comparison.csv')
    a=p.parse_args()
    for row in run_benchmarks(a.repeats,a.output):
        print(f"{row['case'][:32]:32} {row['algorithm']:15} {row['status']:19} "
              f"cost={str(row['returned_cost']):4} expand={str(row['expansions']):5} "
              f"median_ms={row['median_ms']}")
