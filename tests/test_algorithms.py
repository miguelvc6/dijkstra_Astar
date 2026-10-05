import math
import random
import unittest
from algorithms import brute_force, dijkstra_lazy, dijkstra_eager, astar
from algorithms.common import path_cost, validate_graph
from algorithms.dijkstra import IndexedMinPQ
from algorithms.experiments import astar_closed_bug, stop_on_generation_bug
from graphs.main_graph import GRAPH, HEURISTIC, COORDINATES
from graphs.fixtures import reopening_case, random_case, grid_case, negative_case, overestimate_case


def bellman_ford(g, s):
    """Independent small-graph oracle, including zero costs."""
    d = dict.fromkeys(g, math.inf)
    d[s] = 0
    for _ in range(len(g)-1):
        changed = False
        for u, arcs in g.items():
            for v, w in arcs:
                if d[u]+w < d[v]:
                    d[v] = d[u]+w
                    changed = True
        if not changed:
            break
    return d


class Algorithms(unittest.TestCase):
    def all_results(self, g, s, t, h=None):
        h = h or dict.fromkeys(g, 0)
        return [brute_force(g,s,t), dijkstra_lazy(g,s,t),
                dijkstra_eager(g,s,t), astar(g,s,t,h)]

    def test_main_path(self):
        for result in self.all_results(GRAPH,'S','T',HEURISTIC):
            self.assertEqual(result.distance,8)
            self.assertEqual(path_cost(GRAPH,result.path),8)
            self.assertEqual(result.status,'found')

    def test_main_counts(self):
        b,l,e,a = self.all_results(GRAPH,'S','T',HEURISTIC)
        self.assertEqual(b.stats.paths_examined,8)
        self.assertEqual(l.stats.expansions,8)
        self.assertEqual(l.stats.stale_pops,2)
        self.assertEqual(e.stats.expansions,8)
        self.assertEqual(e.stats.stale_pops,0)
        self.assertEqual(a.stats.expansions,4)
        self.assertEqual(a.stats.reexpansions,0)

    def test_main_consistency(self):
        for u, arcs in GRAPH.items():
            for v,w in arcs:
                self.assertLessEqual(HEURISTIC[u],w+HEURISTIC[v])
                x,y=COORDINATES[u]; a,b=COORDINATES[v]
                self.assertGreaterEqual(w,abs(x-a)+abs(y-b))

    def test_reopening(self):
        c=reopening_case(); g,h=c['graph'],c['h']
        r=astar(g,'S','T',h)
        self.assertEqual(r.distance,5)
        self.assertEqual(r.stats.reexpansions,1)
        self.assertEqual(r.stats.expansions,4)
        self.assertEqual(astar_closed_bug(g,'S','T',h).distance,6)
        for u in g:
            self.assertLessEqual(h[u],bellman_ford(g,u)['T'])
        self.assertGreater(h['B'],dict(g['B'])['A']+h['A'])

    def test_generation_bug(self):
        self.assertEqual(stop_on_generation_bug(GRAPH,'S','T'),15)

    def test_overestimate_counterexample(self):
        c=overestimate_case()
        self.assertEqual(astar(c['graph'],'S','T',c['h']).distance,11)

    def test_start_is_target(self):
        for r in self.all_results(GRAPH,'S','S',dict.fromkeys(GRAPH,0)):
            self.assertEqual(r.distance,0)
            self.assertEqual(r.path,['S'])
            self.assertEqual(r.stats.expansions,0)

    def test_unreachable(self):
        g={'S': [('A',1)],'A':[],'T':[]}
        for r in self.all_results(g,'S','T'):
            self.assertEqual(r.distance,math.inf)
            self.assertEqual(r.path,[])
            self.assertEqual(r.status,'unreachable')

    def test_zero_cycles_and_ties(self):
        g={'S':[('A',0),('B',0)],'A':[('S',0),('T',1)],
           'B':[('T',1)],'T':[]}
        for r in self.all_results(g,'S','T'):
            self.assertEqual(r.distance,1)
            self.assertEqual(path_cost(g,r.path),1)

    def test_all_distances(self):
        for fn in [dijkstra_lazy,dijkstra_eager]:
            r=fn(GRAPH,'S')
            self.assertEqual(r.dist,bellman_ford(GRAPH,'S'))
            self.assertEqual(r.status,'all_distances')
            self.assertEqual(r.finalized,set(GRAPH))

    def test_early_stop_tentative(self):
        g={'S':[('T',1),('A',7),('B',2)],'B':[('A',1)],'A':[],'T':[]}
        for fn in [dijkstra_lazy,dijkstra_eager]:
            r=fn(g,'S','T')
            self.assertEqual(r.dist['A'],7)
            self.assertNotIn('A',r.finalized)
            self.assertEqual(fn(g,'S').dist['A'],3)

    def test_invalid_costs(self):
        for value in [-1,math.inf,math.nan]:
            g={'S':[('T',value)],'T':[]}
            for fn in [brute_force,dijkstra_lazy,dijkstra_eager]:
                with self.assertRaises(ValueError): fn(g,'S','T')
            with self.assertRaises(ValueError): astar(g,'S','T',{'S':0,'T':0})

    def test_invalid_nodes(self):
        with self.assertRaises(ValueError): dijkstra_lazy(GRAPH,'missing','T')
        with self.assertRaises(ValueError): validate_graph({'S':[('T',1)]},'S')
        with self.assertRaises(ValueError): validate_graph({'S':[('T',1),('T',2)],'T':[]},'S')

    def test_invalid_heuristic(self):
        for h in [{'S':0,'T':1},{'S':-1,'T':0},{'S':math.nan,'T':0}]:
            with self.assertRaises(ValueError): astar({'S':[('T',1)],'T':[]},'S','T',h)

    def test_budget_is_not_optimum(self):
        r=brute_force(GRAPH,'S','T',max_prefixes=1)
        self.assertEqual(r.status,'budget_exhausted')
        self.assertEqual(r.finalized,set())

    def test_no_input_mutation(self):
        import copy
        g=copy.deepcopy(GRAPH)
        self.all_results(g,'S','T',HEURISTIC)
        self.assertEqual(g,GRAPH)

    def test_zero_heuristic_reproduces_lazy(self):
        for seed in range(20):
            c=random_case(15,seed); g=c['graph']
            l=dijkstra_lazy(g,c['start'],c['target'])
            a=astar(g,c['start'],c['target'],c['h'])
            self.assertEqual(l.distance,a.distance)
            self.assertEqual(l.path,a.path)
            for k in ['expansions','pops','pushes','stale_pops','peak_queue']:
                self.assertEqual(getattr(l.stats,k),getattr(a.stats,k))

    def test_random_against_independent_oracle(self):
        for seed in range(60):
            c=random_case(7,seed); g=c['graph']; s=c['start']; t=c['target']
            optimal=bellman_ford(g,s)[t]
            for r in self.all_results(g,s,t):
                self.assertEqual(r.distance,optimal)
                self.assertEqual(path_cost(g,r.path),optimal)

    def test_grid_heuristics(self):
        for walls in [False,True]:
            for kind in ['zero','euclidean','manhattan']:
                c=grid_case(10,8,walls,kind); g=c['graph']; h=c['h']
                for u,arcs in g.items():
                    for v,w in arcs: self.assertLessEqual(h[u],w+h[v]+1e-10)
                l=dijkstra_lazy(g,c['start'],c['target'])
                a=astar(g,c['start'],c['target'],h)
                self.assertEqual(l.distance,a.distance)
                self.assertEqual(a.stats.reexpansions,0)

    def test_admissible_random_inconsistent(self):
        # Choose arbitrary nodewise lower bounds on exact distances to target.
        # They need not be consistent, so this exercises reopening correctness.
        for seed in range(60):
            c=random_case(9,seed); g=c['graph']; t=c['target']
            rng=random.Random(seed+101)
            h={u:(rng.random()*bellman_ford(g,u)[t] if
                   math.isfinite(bellman_ford(g,u)[t]) else 0) for u in g}
            h[t]=0
            a=astar(g,c['start'],t,h)
            self.assertEqual(a.distance,bellman_ford(g,c['start'])[t])


class IndexedHeap(unittest.TestCase):
    def test_random_operations_and_positions(self):
        r=random.Random(81); q=IndexedMinPQ(); truth={}
        for i in range(100):
            value=r.randrange(1000)
            q.insert(str(i),value); truth[str(i)]=value
            q.check_invariant()
        for _ in range(300):
            u=r.choice(list(truth)); value=truth[u]-r.randrange(1,20)
            q.decrease_key(u,value); truth[u]=value; q.check_invariant()
        while truth:
            value,u=q.pop_min()
            self.assertEqual(value,min(truth.values()))
            self.assertEqual(value,truth.pop(u)); q.check_invariant()
        with self.assertRaises(IndexError): q.pop_min()

    def test_bad_operations(self):
        q=IndexedMinPQ(); q.insert('A',4)
        with self.assertRaises(ValueError): q.insert('A',2)
        with self.assertRaises(ValueError): q.decrease_key('A',4)
        with self.assertRaises(KeyError): q.decrease_key('B',1)

    def test_tie_ticket_on_improvement(self):
        q=IndexedMinPQ(); q.insert('A',4); q.insert('B',2); q.decrease_key('A',2)
        self.assertEqual(q.pop_min(),(2,'B'))
        self.assertEqual(q.pop_min(),(2,'A'))


if __name__=='__main__': unittest.main()
