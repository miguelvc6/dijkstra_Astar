"""Count operations and record compact events from the actual Python functions.

Observation runs are intentionally separate from runtime and memory measurements.
No function in algorithms/ is edited, copied, or replaced by another search.
"""
import inspect
import sys
from collections import Counter

from algorithms.indexed_min_heap import IndexedMinPQ
from experiments.registry import arguments, function
from tools.trace_search import display_source


def observe(key, case, *, record=False):
    fn = function(key)
    source_lines, start = inspect.getsourcelines(fn)
    source, line_map = display_source(source_lines)
    code = fn.__code__
    pending = {}
    events = []
    stats = dict(expansions=0, unique_expanded=0, reexpansions=0, edge_examinations=0,
                 pushes=0, pops=0, stale_pops=0, decrease_keys=0, peak_frontier=0,
                 recursive_calls=0, max_depth=0)
    expanded = Counter()
    pop_number = 0
    expanded_pop = -1
    is_dfs = key == 'depth_first'

    def emit(kind, lineno, **values):
        if record:
            events.append(dict(kind=kind, line=line_map.get(lineno - start + 1, 0), **values))

    def snapshot(frame, lineno):
        nonlocal pop_number, expanded_pop
        local = frame.f_locals
        text = source_lines[lineno - start].strip().split('#')[0].strip()
        if is_dfs:
            if text == 'if u == target:':
                stats['recursive_calls'] += 1
                stats['max_depth'] = max(stats['max_depth'], len(local['path']))
                emit('enter', lineno, u=local['u'], g=local['cost'], path=list(local['path']))
            elif text.startswith('if v not in '):
                stats['edge_examinations'] += 1
            elif text.startswith('for v, weight in ') and id(frame) not in dfs_expanded_frames:
                dfs_expanded_frames.add(id(frame))
                stats['expansions'] += 1
                expanded[local['u']] += 1
                stats['unique_expanded'] = len(expanded)
                emit('expand', lineno, u=local['u'], g=local['cost'])
            elif text == 'path.pop()':
                emit('backtrack', lineno, path=list(local['path']))
            elif text == 'return cost, path.copy()':
                emit('best', lineno, path=list(local['path']), g=local['cost'])
            return
        if 'dist' not in local:
            return
        queue = local.get('queue', [])
        heap = queue.heap if isinstance(queue, IndexedMinPQ) else queue
        stats['peak_frontier'] = max(stats['peak_frontier'], len(heap))
        if 'heappop(queue)' in text or 'queue.pop_min()' in text or 'extract_min(queue)' in text and text.startswith('popped_dist'):
            stats['pops'] += 1
            pop_number += 1
            u, g = local['u'], local['popped_dist']
            stale = g != local['dist'][u]
            if stale:
                stats['stale_pops'] += 1
            emit('stale' if stale else 'goal' if u == case['target'] else 'pop', lineno, u=u, g=g)
        elif text.startswith('for v, weight in ') and expanded_pop != pop_number:
            expanded_pop = pop_number
            u = local['u']
            if expanded[u]:
                stats['reexpansions'] += 1
            expanded[u] += 1
            stats['expansions'] += 1
            stats['unique_expanded'] = len(expanded)
            emit('expand', lineno, u=u, g=local['dist'][u])
        elif text.startswith('candidate_dist ='):
            stats['edge_examinations'] += 1
        elif 'heappush(queue,' in text or text.startswith('queue.append(') or text.startswith('queue.insert('):
            stats['pushes'] += 1
            v = case['start'] if text.startswith('queue.insert(start') else local['v']
            emit('relax', lineno, v=v, g=local['dist'][v], parent=local.get('parent', {}).get(v))
        elif 'queue.decrease_key(' in text:
            stats['decrease_keys'] += 1
            v = local['v']
            emit('relax', lineno, v=v, g=local['dist'][v], parent=local['parent'][v])
        elif text.startswith('queue =') or text.startswith('queue:'):
            if not isinstance(queue, IndexedMinPQ):
                stats['pushes'] += len(queue)
                emit('relax', lineno, v=case['start'], g=0, parent=None)

    dfs_expanded_frames = set()

    def relevant(frame):
        return frame.f_code is code or is_dfs and frame.f_code.co_name == 'explore' and frame.f_code.co_filename == code.co_filename

    def tracer(frame, event, arg):
        if not relevant(frame):
            return None
        fid = id(frame)
        if event in {'line', 'return'} and fid in pending:
            snapshot(frame, pending.pop(fid))
        if event == 'line':
            pending[fid] = frame.f_lineno
        elif event == 'return':
            dfs_expanded_frames.discard(fid)
        return tracer

    previous = sys.gettrace()
    try:
        sys.settrace(tracer)
        result = fn(*arguments(key, case))
    finally:
        sys.settrace(previous)
    emit('finish', start, distance=None if result[0] == float('inf') else result[0], path=result[1])
    return result, stats, dict(source=source, source_file=fn.__module__.replace('.', '/') + '.py', events=events)
