import importlib
import unittest
from algorithms import astar, dijkstra_lazy, dijkstra_eager
from graphs.fixtures import main_case, reopening_case
from tools.trace_search import trace_function

class SourceAndTrace(unittest.TestCase):
    def test_trace_matches_result(self):
        for fn in [dijkstra_lazy,dijkstra_eager,astar]:
            case=main_case()
            t=trace_function(fn,case)
            self.assertEqual(t['result']['distance'],8)
            self.assertEqual(t['events'][-1]['kind'],'finish')
            lines=t['source'].splitlines()
            for event in t['events']:
                self.assertEqual(lines[event['line']-1].strip(),event['code'])
                if event['kind']=='stale':
                    u=event['variables']['u']
                    self.assertNotEqual(event['variables']['popped_g'],event['dist'][u])

    def test_reopening_is_visible(self):
        t=trace_function(astar,reopening_case())
        events=[e for e in t['events'] if e['kind']=='reopen']
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]['variables']['u'],'A')
        self.assertEqual(events[0]['dist']['A'],2)

if __name__=='__main__':unittest.main()

class Checkpoints(unittest.TestCase):
    def test_all_solved_checkpoints(self):
        from tools.make_checkpoints import SPECS, HEADER
        from graphs.main_graph import GRAPH, HEURISTIC
        for name, timing, prompt, code, blanks in SPECS:
            with self.subTest(checkpoint=name):
                ns={}
                exec(HEADER+code,ns)
                args=(GRAPH,'S','T',HEURISTIC) if name.startswith('06') else (GRAPH,'S','T')
                result=ns['search'](*args)
                self.assertEqual(result[0] if isinstance(result,tuple) else result,8)
