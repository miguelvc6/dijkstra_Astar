"""Generate exportable scientific figures and an offline benchmark dashboard."""
import argparse
import collections
import html
import json
import math
import statistics
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

ROOT = Path(__file__).resolve().parents[1]
COLORS = {'depth_first': '#983d47', 'list': '#d78033', 'lazy': '#087e79', 'eager': '#735eaa',
          'astar-zero': '#7a8583', 'astar-euclidean': '#3988b5', 'astar-manhattan': '#5c9b33',
          'astar-octile': '#ae5c8f', 'astar-inconsistent': '#b85842'}
FAMILIES = [('sparse', 'Sparse weighted graphs'), ('dense', 'Dense weighted graphs'),
            ('queue_stress', 'Repeated improvements'), ('grid_wall', 'Grid with a wall'),
            ('grid_obstacles', 'Obstacle grids'), ('maze_braided', 'Mazes with loops')]


def save_scaling(rows, field, filename, ylabel):
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), layout='constrained')
    for ax, (family, title) in zip(axes.flat, FAMILIES):
        subset = [r for r in rows if r['family'] == family and r['status'] == 'ok']
        groups = collections.defaultdict(list)
        for row in subset:
            groups[(row['algorithm'], row['size'])].append(row)
        for algorithm in sorted({r['algorithm'] for r in subset}):
            x, y, low, high = [], [], [], []
            for (key, size), group in sorted(groups.items(), key=lambda p: p[0][1]):
                if key != algorithm:
                    continue
                values = [r[field] / (1e6 if field == 'median_ns' else 1024) for r in group]
                median = statistics.median(values)
                x.append(statistics.median(r['V'] for r in group))
                y.append(median)
                low.append(median - min(values))
                high.append(max(values) - median)
            ax.errorbar(x, y, yerr=[low, high], label=next(r['label'] for r in subset if r['algorithm'] == algorithm),
                        color=COLORS[algorithm], marker='o', markersize=4, linewidth=1.4, capsize=2)
        ax.set(xscale='log', yscale='log', title=title, xlabel='Vertices (median for each configured size)', ylabel=ylabel)
        ticks = sorted({statistics.median(r['V'] for r in group) for group in groups.values()})
        ax.set_xticks(ticks, [str(round(value)) for value in ticks])
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.grid(True, alpha=.22, which='both')
    unique = {}
    for ax in axes.flat:
        handles, labels = ax.get_legend_handles_labels()
        unique.update(zip(labels, handles))
    fig.legend(unique.values(), unique.keys(), loc='outside lower center', ncol=3, frameon=False)
    fig.suptitle(('Runtime' if field == 'median_ns' else 'Peak Python search allocations') + ' on this machine\nPoints: median of instance measurements; whiskers: instance range (one to three instances)', fontsize=15)
    fig.savefig(filename, dpi=180)
    fig.savefig(filename.with_suffix('.svg'))
    plt.close(fig)


def save_heuristics(rows, filename):
    families = ['grid_wall', 'grid_obstacles', 'grid_terrain', 'grid_obstacles-diagonal', 'maze_perfect', 'maze_braided']
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), layout='constrained')
    for ax, family in zip(axes.flat, families):
        subset = [r for r in rows if r['family'] == family and r['status'] == 'ok']
        selected = max(subset, key=lambda r: (r['V'], -int(r['seed'] or 0)))['case_id']
        group = [r for r in subset if r['case_id'] == selected and (r['algorithm'] == 'lazy' or r['algorithm'].startswith('astar-'))]
        group.sort(key=lambda r: ['lazy', 'astar-zero', 'astar-euclidean', 'astar-manhattan', 'astar-octile'].index(r['algorithm']))
        ax.barh([r['label'] for r in group], [r['operations']['expansions'] for r in group], color=[COLORS[r['algorithm']] for r in group])
        ax.set_title(f'{family.replace("_", " ")}\nV={group[0]["V"]}, seed={group[0]["seed"]}')
        ax.set_xlabel('Expansions (terminal target extraction excluded)')
        ax.grid(axis='x', alpha=.2)
    fig.suptitle('Heuristics compared on identical graphs and endpoints', fontsize=15)
    fig.savefig(filename, dpi=180)
    fig.savefig(filename.with_suffix('.svg'))
    plt.close(fig)


def save_dfs(rows, filename):
    group = sorted([r for r in rows if r['family'] == 'complete' and r['algorithm'] == 'depth_first'], key=lambda r: r['V'])
    success = [r for r in group if 'median_ns' in r]
    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    if not group:
        ax.text(.5, .5, 'No complete-graph DFS growth sweep in this run.\nUse the full benchmark suite.',
                transform=ax.transAxes, ha='center', va='center')
        ax.set_axis_off()
        fig.savefig(filename, dpi=180)
        fig.savefig(filename.with_suffix('.svg'))
        plt.close(fig)
        return
    ax.plot([r['V'] for r in success], [r['median_ns'] / 1e6 for r in success], 'o-', color=COLORS['depth_first'], label='Measured exhaustive DFS median')
    if success:
        anchor = success[0]
        factor = anchor['median_ns'] / 1e6 / math.factorial(anchor['V'] - 1)
        xs = list(range(min(r['V'] for r in group), max(r['V'] for r in group) + 1))
        ax.plot(xs, [factor * math.factorial(n - 1) for n in xs], '--', color='#7a8583', label='(V−1)! growth guide, scaled to first point')
    for row in group:
        if row['status'] != 'ok':
            ax.axvline(row['V'], color='#aaa', linestyle=':')
            if 'median_ns' in row:
                ax.annotate(f'{row.get("phase", "").title()} phase timeout\nTiming completed', (row['V'], row['median_ns'] / 1e6),
                            xytext=(-115, -55), textcoords='offset points', ha='center', fontsize=9,
                            arrowprops=dict(arrowstyle='-', color='#aaa'), bbox=dict(facecolor='#fffefb', edgecolor='none', alpha=.9))
            else:
                ax.annotate(f'{row["status"]}\n{row.get("phase", "")}', (row['V'], .5), xycoords=('data', 'axes fraction'), ha='center')
    ax.set(yscale='log', xlabel='Vertices in complete directed graph', ylabel='Milliseconds per search', title='Exhaustive enumeration grows rapidly')
    ax.grid(alpha=.2, which='both')
    ax.legend(fontsize=9)
    fig.savefig(filename, dpi=180)
    fig.savefig(filename.with_suffix('.svg'))
    plt.close(fig)


def report(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    rows = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines()]
    if not manifest.get('finished_utc'):
        raise ValueError('Run is incomplete; finish or resume it before reporting.')
    figures = directory / 'figures'
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False, 'figure.facecolor': '#fffefb', 'axes.facecolor': '#fffefb'})
    save_scaling(rows, 'median_ns', figures / 'runtime.png', 'Median runtime per search (ms)')
    save_scaling(rows, 'peak_python_bytes', figures / 'memory.png', 'Peak traced Python allocations (KiB)')
    save_heuristics(rows, figures / 'heuristics.png')
    save_dfs(rows, figures / 'dfs.png')
    by_id = {case['case_id']: case for case in manifest['cases']}
    dataset = []
    for row in rows:
        dataset.append({**row, 'graph_sha256': by_id[row['case_id']]['graph_sha256']})
    encoded = json.dumps(dataset, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    rel = '../' + str(directory.relative_to(ROOT))
    status_text = ', '.join(f'{count} {status}' for status, count in manifest['statuses'].items())
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pathfinding · measured results</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f1eb;color:#17323d;font:14px system-ui,sans-serif}header,main{padding:24px 32px;max-width:1500px;margin:auto}h1{font-size:30px;margin:0 0 8px;letter-spacing:-1px}h2{font-size:20px}p{line-height:1.6;color:#61777b}a{color:#087e79}nav{display:flex;gap:20px;margin:12px 0}.badge{padding:10px 16px;background:#e2eee4;border-radius:8px}.figure{background:#fffefb;border:1px solid #d4ddd5;border-radius:10px;padding:12px;margin:20px 0}.figure img{width:100%;height:auto}.filters{display:flex;flex-wrap:wrap;gap:12px;margin:16px 0}select,input{font:inherit;padding:8px;border-radius:6px;border:1px solid #bbc9c1}label{display:flex;align-items:center;gap:6px}.scroll{overflow:auto;max-height:650px;border:1px solid #d4ddd5;background:#fffefb}table{border-collapse:collapse;min-width:1050px;width:100%;font-variant-numeric:tabular-nums}td,th{padding:8px 10px;text-align:left;border-bottom:1px solid #e0e5dd}th{position:sticky;top:0;background:#e7eee5}tr:hover{background:#edf2e9}.muted{color:#61777b}.timeout{color:#983d47}details{margin:18px 0;line-height:1.7}code{font-size:12px} @media(max-width:700px){header,main{padding:18px}}
</style></head><body><header><h1>Pathfinding · measured results</h1><p>Observed performance of the unchanged lecture implementations.</p><nav><a href="experiments.html">Animation field lab</a><a href="visualizer.html">Code laboratory</a><a href="__REL__/summary.csv">Summary CSV</a><a href="__REL__/samples.csv">Raw timing samples</a><a href="__REL__/manifest.json">Run metadata</a></nav><div class="badge">__STATUS__ · __CASES__ scenarios / __INPUTS__ unique graph–endpoint inputs · __REPEATS__ timing samples per successful configuration</div><p>__MACHINE__ · __DATE__</p></header><main>
<p>Each runtime point is measured without tracing or memory instrumentation. Peak allocations and operation counts come from separate runs. All completed results passed route and cost validation against NetworkX Bellman–Ford. These results describe this machine and these inputs; the figures do not prove asymptotic complexity or a universal ranking.</p>
<div class="figure"><h2>Runtime as problems grow</h2><img src="__REL__/figures/runtime.png" alt="Runtime scaling across sparse graphs, dense graphs, repeated improvements, obstacle grids, and mazes"><p>Logarithmic axes. Points summarize per-instance timing medians; whiskers show the range across available instances, not confidence intervals.</p></div>
<div class="figure"><h2>Memory during search</h2><img src="__REL__/figures/memory.png" alt="Peak Python allocation scaling across graph families"><p>Peak traced Python allocations include the returned route. The graph and supplied heuristic exist before tracing starts. This is not peak total resident process memory.</p></div>
<div class="figure"><h2>Heuristic quality on the same problem</h2><img src="__REL__/figures/heuristics.png" alt="Expansions for Dijkstra and several A-star heuristics on identical graphs"></div>
<div class="figure"><h2>Exhaustive DFS growth</h2><img src="__REL__/figures/dfs.png" alt="Exhaustive DFS timing on increasing complete graphs"><p>The runtime plot includes completed timing phases. A timeout in a later phase preserves earlier measurements; the unfinished phase has no estimate. DFS is deliberately skipped above eleven vertices.</p></div>
<h2>Every configuration</h2><div class="filters"><label>Family <select id="family"><option value="">All</option></select></label><label>Algorithm <select id="algorithm"><option value="">All</option></select></label><label>Status <select id="status"><option value="">All</option></select></label><label>Search <input id="search" placeholder="Problem name"></label><label>Sort <select id="sort"><option value="case">Problem</option><option value="runtime">Runtime</option><option value="memory">Memory</option></select></label><span id="count"></span></div>
<div class="scroll"><table><thead><tr><th>Problem</th><th>Algorithm</th><th>V / E</th><th>Median ms</th><th>Q1–Q3 ms</th><th>Peak KiB</th><th>Expansions</th><th>Peak queue</th><th>Cost</th><th>Status</th></tr></thead><tbody id="rows"></tbody></table></div>
<details><summary>Measurement protocol and reproducibility</summary><p>Sequential fresh Python workers; no competing benchmark jobs. Imports, graph construction, reference validation, and garbage collection between samples are outside the timing window. Garbage collection remains enabled during calls. __WARMUPS__ warm-ups and a calibration precede timing. Fast searches are batched toward __SAMPLEMS__ milliseconds per sample, capped at one thousand calls; the actual batch size is saved with each result.</p><p>Memory is measured in one separate call with <code>tracemalloc</code>, started after graph construction. Counts come from another call using <code>sys.settrace</code>. Expansions count outgoing-edge processing and exclude terminal target extraction. DFS counts recursive path-prefix expansions rather than unique states. Inputs use deterministic seeds 17, 29, and 43 where generation is random; identical deterministic grids are deduplicated. Graph fingerprints, heuristic fingerprints, package versions, source hashes, and raw samples are saved in the run directory.</p><p>Street inputs are a saved OpenStreetMap snapshot from Vienna, with projected-distance weights and basic one-way handling. Turn restrictions and conditional access are outside the teaching model. Sprites are Kenney Tiny Dungeon, CC0. Playback speed is unrelated to runtime.</p></details></main><script>
const DATA=__ROWS__;const $=id=>document.getElementById(id),esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
for(const key of ['family','algorithm','status'])for(const value of [...new Set(DATA.map(r=>r[key]))].sort())$(key).innerHTML+=`<option value="${esc(value)}">${esc(value)}</option>`;
function render(){let rows=DATA.filter(r=>(!$('family').value||r.family===$('family').value)&&(!$('algorithm').value||r.algorithm===$('algorithm').value)&&(!$('status').value||r.status===$('status').value)&&r.case.toLowerCase().includes($('search').value.toLowerCase()));rows.sort((a,b)=>$('sort').value==='runtime'?(a.median_ns??Infinity)-(b.median_ns??Infinity):$('sort').value==='memory'?(a.peak_python_bytes??Infinity)-(b.peak_python_bytes??Infinity):a.case_id.localeCompare(b.case_id)||a.algorithm.localeCompare(b.algorithm));const ms=v=>v===undefined?'—':(v/1e6).toFixed(3);$('rows').innerHTML=rows.map(r=>`<tr><td>${esc(r.case)}</td><td>${esc(r.label)}</td><td>${r.V} / ${r.E}</td><td>${ms(r.median_ns)}</td><td>${r.q1_ns===undefined?'—':ms(r.q1_ns)+'–'+ms(r.q3_ns)}</td><td>${r.peak_python_bytes===undefined?'—':(r.peak_python_bytes/1024).toFixed(1)}</td><td>${r.operations?.expansions??'—'}</td><td>${r.operations?.peak_frontier??'—'}</td><td>${r.cost===undefined?'—':r.cost===null?'unreachable':Number(r.cost.toFixed(3))}</td><td class="${r.status==='ok'?'muted':'timeout'}" title="${esc(r.error||'Validated')}">${esc(r.status)}${r.phase?' · '+esc(r.phase):''}</td></tr>`).join('');$('count').textContent=rows.length+' rows';}for(const key of ['family','algorithm','status','sort'])$(key).onchange=render;$('search').oninput=render;window.BENCHMARKS={data:DATA,render};render();
</script></body></html>'''
    replacements = {'__REL__': rel, '__STATUS__': html.escape(status_text), '__CASES__': str(len(manifest['cases'])),
                    '__INPUTS__': str(len({c['graph_sha256'] for c in manifest['cases']})),
                    '__REPEATS__': str(manifest['config']['repeats']), '__MACHINE__': html.escape(manifest['cpu_model'] + ' · Python ' + manifest['python'].split()[0]),
                    '__DATE__': html.escape(manifest['finished_utc']), '__ROWS__': encoded,
                    '__WARMUPS__': str(manifest['config']['warmups']), '__SAMPLEMS__': str(manifest['config']['sample_ms'])}
    for token, value in replacements.items():
        page = page.replace(token, value)
    (ROOT / 'web/benchmarks.html').write_text(page)
    print(f'Wrote figures to {figures} and dashboard to web/benchmarks.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='results/latest')
    args = parser.parse_args()
    report(ROOT / args.results)
