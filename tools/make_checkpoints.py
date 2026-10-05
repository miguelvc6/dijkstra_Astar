"""Generate student blanks, runnable solutions, and matching notebooks."""
import contextlib
import io
import json
from pathlib import Path

HEADER='''from heapq import heappop, heappush
from itertools import count
from math import inf
from algorithms.dijkstra import IndexedMinPQ
from algorithms.common import recover
from graphs.main_graph import GRAPH, HEURISTIC

'''
BF='''def search(graph, start, target):
    best_cost, best_path = inf, []
    def visit(u, cost, path, on_path):
        nonlocal best_cost, best_path
        if u == target:
            if cost < best_cost:
                best_cost, best_path = cost, path.copy()
            return
        for v, weight in graph[u]:
            if v not in on_path:
                visit(v, cost + weight, path + [v], on_path | {v})
    visit(start, 0, [start], {start})
    return best_cost, best_path
'''
LAZY='''def search(graph, start, target):
    dist, parent = {start: 0}, {}
    ticket = count()
    queue = [(0, next(ticket), start)]
    while queue:
        g, _, u = heappop(queue)
        if g != dist[u]:
            continue
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            candidate = g + weight
            if candidate < dist.get(v, inf):
                dist[v] = candidate
                parent[v] = u
                heappush(queue, (candidate, next(ticket), v))
    return inf, []
'''
EAGER='''def search(graph, start, target):
    dist, parent = {start: 0}, {}
    queue = IndexedMinPQ()
    queue.insert(start, 0)
    while queue:
        g, u = queue.pop_min()
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            candidate = g + weight
            if candidate < dist.get(v, inf):
                dist[v] = candidate
                parent[v] = u
                if v in queue:
                    queue.decrease_key(v, candidate)
                else:
                    queue.insert(v, candidate)
    return inf, []
'''
ASTAR='''def search(graph, start, target, h):
    dist, parent = {start: 0}, {}
    ticket = count()
    queue = [(h[start], next(ticket), 0, start)]
    while queue:
        f, _, g, u = heappop(queue)
        if g != dist[u]:
            continue
        if u == target:
            return g, recover(parent, start, target)
        for v, weight in graph[u]:
            candidate = g + weight
            if candidate < dist.get(v, inf):
                dist[v] = candidate
                parent[v] = u
                priority = candidate + h[v]
                heappush(queue, (priority, next(ticket), candidate, v))
    return inf, []
'''

SPECS=[
 ('01_bruteforce','09-16','Enumerate simple routes. Why must the visited set be path-local?',BF,
  [('if v not in on_path:','if ...:  # TODO: allow only nodes not on the current route'),
   ('visit(v, cost + weight, path + [v], on_path | {v})',
    'raise NotImplementedError("Extend cost, path and on_path")')]),
 ('02_lazy_relaxation','28-34','Fill the accumulated cost and improvement condition.',LAZY,
  [('candidate = g + weight','raise NotImplementedError("Compute candidate")'),
   ('if candidate < dist.get(v, inf):','if ...:  # TODO: compare against the best known distance')]),
 ('03_stale_and_parent','34-38','Skip obsolete records; replace the predecessor on every improvement.',LAZY,
  [('if g != dist[u]:','if ...:  # TODO: detect stale record'),
   ('parent[v] = u','raise NotImplementedError("Update the predecessor")')]),
 ('04_goal_check','38-41','The solution below checks extraction. Explain why generation is too early.',LAZY,
  [('if u == target:\n            return g, recover(parent, start, target)',
    '# TODO: insert a correct goal test after the stale-entry guard')]),
 ('05_eager_queue','41-48','Keep one queue entry per frontier node.',EAGER,
  [('queue.decrease_key(v, candidate)','raise NotImplementedError("Update existing priority")'),
   ('queue.insert(v, candidate)','raise NotImplementedError("Insert new node")')]),
 ('06_astar','68-77','Change priority, not the meaning of the stored route cost.',ASTAR,
  [('if g != dist[u]:','if ...:  # TODO: stale check must compare queued g, not f'),
   ('priority = candidate + h[v]','raise NotImplementedError("Compute f = g + h")')]),
]


def make_cell(kind,text,outputs=None,count=None):
    cell={'cell_type':kind,'metadata':{},'source':text.splitlines(keepends=True)}
    if kind=='code':cell.update(execution_count=count,outputs=outputs or [])
    return cell


def build(root):
    root=Path(root); cp=root/'checkpoints'; (cp/'solutions').mkdir(parents=True,exist_ok=True)
    student=[make_cell('markdown','# Dijkstra and A*: guided reconstruction\n\n90-minute PhD lecture. Predict first; then edit a small number of lines. The intentionally incomplete cells must be repaired before Run All. Full reference implementations are in `algorithms/`.')]
    setup='''# Works when launched from the repository root or notebooks/.
import os, sys
from pathlib import Path
ROOT = Path.cwd()
if not (ROOT / "algorithms").exists():
    ROOT = ROOT.parent
assert (ROOT / "algorithms").exists(), "Open this notebook inside the repository"
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
'''+HEADER
    student.append(make_cell('code',setup))
    solved=[make_cell('markdown','# Dijkstra and A*: worked lecture notebook\n\nAll outputs are computed from the accompanying code. Compare costs rather than one path when ties exist.')]
    ns={}; exec(setup,ns); solved.append(make_cell('code',setup,[],1)); cellno=1
    for name,time,prompt,code,blanks in SPECS:
        incomplete=code
        for a,b in blanks: incomplete=incomplete.replace(a,b)
        args="GRAPH, 'S', 'T', HEURISTIC" if name.startswith('06') else "GRAPH, 'S', 'T'"
        end=f"\nif __name__ == '__main__':\n    print(search({args}))\n"
        pre=f'"""{time} min. {prompt}\nStudent scaffold. Assumes a valid graph; reference APIs perform validation.\nRun from the repo root: python -m checkpoints.{name}\n"""\n'
        (cp/(name+'.py')).write_text(pre+HEADER+incomplete+end)
        (cp/'solutions'/(name+'.py')).write_text(pre.replace('Student scaffold.','Worked solution.')+HEADER+code+end)
        md=f'## {time} min — {name[3:].replace("_"," ").title()}\n\n{prompt}'
        student.append(make_cell('markdown',md)); solved.append(make_cell('markdown',md))
        student.append(make_cell('code',incomplete+f'\nprint(search({args}))\n'))
        src=code+f'\nprint(search({args}))\n'; out=io.StringIO()
        with contextlib.redirect_stdout(out):exec(src,ns)
        cellno+=1
        solved.append(make_cell('code',src,[{'output_type':'stream','name':'stdout','text':out.getvalue().splitlines(keepends=True)}],cellno))
    extra='''from algorithms import astar, dijkstra_lazy
from algorithms.experiments import astar_closed_bug, stop_on_generation_bug
from graphs.fixtures import reopening_case, grid_case
case = reopening_case()
for fn in (astar_closed_bug, astar):
    r = fn(case['graph'], 'S', 'T', case['h'])
    print(fn.__name__, 'cost=', r.distance, 're-expansions=', r.stats.reexpansions)
print('Stop-on-generation bug:', stop_on_generation_bug(GRAPH, 'S', 'T'))
for kind in ('zero', 'euclidean', 'manhattan'):
    case = grid_case(24, 16, True, kind)
    r = astar(case['graph'], case['start'], case['target'], case['h'])
    print(kind, 'cost=', r.distance, 'expansions=', r.stats.expansions)
'''
    md='## 77-86 min — comparative experiment\n\nBefore running: predict which claims are guarantees and which are empirical. This notebook provides a ready-to-use substitute while the separate closing-demo application is deferred.'
    for notebook in (student,solved):notebook.append(make_cell('markdown',md))
    student.append(make_cell('code',extra));out=io.StringIO()
    with contextlib.redirect_stdout(out):exec(extra,ns)
    solved.append(make_cell('code',extra,[{'output_type':'stream','name':'stdout','text':out.getvalue().splitlines(keepends=True)}],cellno+1))
    for name,cells in [('lecture_student',student),('lecture_solutions',solved)]:
        obj=dict(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.10'}},nbformat=4,nbformat_minor=4)
        (root/'notebooks'/(name+'.ipynb')).write_text(json.dumps(obj,indent=1)+'\n')
    (cp/'__init__.py').write_text('"""Intentional student exercises; see solutions/."""\n')
    (cp/'solutions'/'__init__.py').write_text('"""Runnable checkpoint solutions."""\n')
    (cp/'README.md').write_text('''# Live-coding checkpoints

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
''')

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
