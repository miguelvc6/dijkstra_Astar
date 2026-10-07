"""Record the ACTUAL Python function, not a parallel animation algorithm.

sys.settrace delivers a line event BEFORE execution. At the NEXT event we
snapshot locals and mark the previous line as executed. Heap helpers are not
line-stepped: an insert/decrease-key is one atomic classroom operation.
No tracing is enabled by benchmark.py.
"""

from __future__ import annotations
import inspect
import json
import math
import sys
from dataclasses import asdict
from pathlib import Path
from algorithms import dijkstra_lazy, dijkstra_eager, astar
from algorithms.dijkstra import IndexedMinPQ
from graphs.fixtures import main_case, reopening_case, overestimate_case


def trace_function(fn, case, *, all_distances=False):
    source_lines, start_line = inspect.getsourcelines(fn)
    code = fn.__code__
    pending = {}
    events = []
    g = case["graph"]

    def snapshot(frame, lineno):
        local = frame.f_locals
        if "dist" not in local:
            return
        queue = local.get("queue", [])
        heap = queue.heap if isinstance(queue, IndexedMinPQ) else queue
        entries = []
        for entry in heap:
            if len(entry) == 4:
                priority, ticket, queued_g, node = entry
            else:
                priority, ticket, node = entry
                queued_g = priority
            entries.append(
                dict(
                    node=node,
                    priority=priority,
                    g=queued_g,
                    ticket=ticket,
                    stale=queued_g != local["dist"].get(node, math.inf),
                )
            )
        relative = lineno - start_line + 1
        text = source_lines[relative - 1].strip()
        scalar = {
            k: local[k]
            for k in ["u", "v", "weight", "candidate", "popped_g", "popped_f", "priority"]
            if k in local
            and isinstance(local[k], (str, int, float))
            and (not isinstance(local[k], float) or math.isfinite(local[k]))
        }
        stats = asdict(local["stats"]) if "stats" in local else {}
        event = dict(
            line=relative,
            code=text,
            variables=scalar,
            dist={v: (d if math.isfinite(d) else None) for v, d in local["dist"].items()},
            parent=dict(local.get("parent", {})),
            queue=entries,
            positions=dict(queue.positions) if isinstance(queue, IndexedMinPQ) else {},
            finalized=sorted(local.get("finalized", set())),
            expanded=sorted(local.get("expanded", local.get("closed", set()))),
            stats=stats,
        )
        previous = events[-1] if events else None
        changed = []
        if previous:
            changed = [v for v in g if previous["dist"].get(v) != event["dist"].get(v)]
        event["changed"] = changed
        if "heappop(" in text or ".pop_min(" in text:
            event["kind"] = "pop"
            event["message"] = f"Extract {scalar.get('u', '?')} with queued g = {scalar.get('popped_g', '?')}."
        elif "heappush(" in text or "queue.insert(" in text:
            event["kind"] = "push"
            event["message"] = (
                "Insert a new queue record. Older lazy records remain in the heap."
                if len(heap) and not isinstance(queue, IndexedMinPQ)
                else "Insert one live frontier entry."
            )
        elif "decrease_key(" in text:
            event["kind"] = "decrease"
            event["message"] = "Decrease the existing priority and repair the indexed heap."
        elif "stale_pops +=" in text:
            event["kind"] = "stale"
            event["message"] = "Obsolete queue entry: skip it without scanning outgoing edges."
        elif (
            "reexpansions +=" in text
            and previous
            and stats.get("reexpansions", 0) > previous["stats"].get("reexpansions", 0)
        ):
            event["kind"] = "reopen"
            event["message"] = "Reopen this state: its best route improved after an earlier expansion."
        elif changed:
            event["kind"] = "improve"
            event["message"] = "Best-known distance improved: " + ", ".join(changed) + "."
        elif "parent[v]" in text:
            event["kind"] = "parent"
            event["message"] = "Replace the predecessor to match the improved route."
        elif text.startswith("return finish"):
            event["kind"] = "finish"
            event["message"] = "Return the result. Target extraction is distinct from target discovery."
        elif "closed" in text and "if v in" in text:
            event["kind"] = "warning"
            event["message"] = "BROKEN policy: a closed state can block a genuinely cheaper route."
        else:
            event["kind"] = "line"
            event["message"] = "Executed: " + text
        event["index"] = len(events)
        events.append(event)

    def tracer(frame, event, arg):
        if frame.f_code is not code:
            return None
        if event == "line":
            if id(frame) in pending:
                snapshot(frame, pending[id(frame)])
            pending[id(frame)] = frame.f_lineno
        elif event == "return":
            if id(frame) in pending:
                snapshot(frame, pending.pop(id(frame)))
        return tracer

    old = sys.gettrace()
    try:
        sys.settrace(tracer)
        args = (g, case["start"], None if all_distances else case["target"])
        result = fn(*args, case["h"]) if fn in [astar, astar_closed_bug] else fn(*args)
    finally:
        sys.settrace(old)
    return dict(
        name=case["name"],
        algorithm=fn.__name__,
        case=case,
        source="".join(source_lines),
        first_source_line=start_line,
        source_file=str(Path(inspect.getsourcefile(fn)).relative_to(Path(__file__).resolve().parents[1])),∏
        events=events,
        result=result.as_dict(),
        all_distances=all_distances,
    )


def build_traces():
    cases = {"main": main_case(), "reopening": reopening_case(), "overestimate": overestimate_case()}
    result = {}
    for key, case in cases.items():
        result[key] = {
            name: trace_function(fn, case)
            for name, fn in [("lazy", dijkstra_lazy), ("eager", dijkstra_eager), ("astar", astar)]
        }
    result["all"] = {
        name: trace_function(fn, main_case(), all_distances=True)
        for name, fn in [("lazy", dijkstra_lazy), ("eager", dijkstra_eager)]
    }
    return result


if __name__ == "__main__":
    out = Path("web/traces.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(build_traces(), separators=(",", ":"), allow_nan=False))
    print(out)
