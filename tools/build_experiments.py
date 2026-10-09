"""Build the self-contained, offline side-by-side pathfinding animation lab."""
import argparse
import base64
import gzip
import hashlib
import json
import math
from pathlib import Path

from experiments.observe import observe
from experiments.registry import label, variants
from experiments.validation import graph_fingerprint, heuristic_checks, reference, validate
from experiments.worker import deadline
from graphs.scenarios import demo_cases

ROOT = Path(__file__).resolve().parents[1]


def build(results='results/latest'):
    output = []
    measured = {}
    manifest_path = ROOT / results / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        for source_path, digest in manifest['source_hashes'].items():
            if source_path.startswith('algorithms/') and hashlib.sha256((ROOT / source_path).read_bytes()).hexdigest() != digest:
                raise ValueError('Algorithm sources differ from the recorded measurements; benchmark the current sources first.')
        by_id = {c['case_id']: c['graph_sha256'] for c in manifest['cases']}
        for line in (manifest_path.parent / 'raw.jsonl').read_text().splitlines():
            row = json.loads(line)
            if row['status'] == 'ok':
                measured[(by_id[row['case_id']], row['algorithm'])] = {k: row[k] for k in ['median_ns', 'q1_ns', 'q3_ns', 'peak_python_bytes']}
    for case in demo_cases():
        expected = reference(case)
        checks = heuristic_checks(case)
        runs = {}
        for key in variants(case, include_dfs=len(case['graph']) <= 11):
            with deadline(10):
                result, stats, trace = observe(key, case, record=True)
            validate(result, case, expected)
            runs[key] = dict(label=label(key), result=dict(cost=None if math.isinf(result[0]) else result[0], path=result[1]),
                             stats=stats, **trace, measured=measured.get((graph_fingerprint(case), key)))
        output.append(dict(case=case, graph_sha256=graph_fingerprint(case), heuristic_checks=checks, runs=runs))
    sprite_path = ROOT / 'web/assets/tiny-dungeon/tilemap_packed.png'
    data = dict(scenarios=output, sprites='data:image/png;base64,' + base64.b64encode(sprite_path.read_bytes()).decode(),
                sprite_roles=dict(wall=[0, 3], floor=[0, 0], hero=[1, 7], enemy=[4, 8]),
                attribution='Tiny Dungeon by Kenney · CC0; street data © OpenStreetMap contributors · ODbL')
    encoded = json.dumps(data, separators=(',', ':'), allow_nan=False).encode()
    packed = base64.b64encode(gzip.compress(encoded, mtime=0)).decode()
    template = (ROOT / 'web/experiments-template.html').read_text()
    assert template.count('__EXPERIMENT_DATA__') == 1
    (ROOT / 'web/experiments.html').write_text(template.replace('__EXPERIMENT_DATA__', packed))
    (ROOT / 'results/demo-validation.json').write_text(json.dumps(dict(scenarios=len(output), runs=sum(len(s['runs']) for s in output),
        cases=[dict(name=s['case']['name'], graph_sha256=s['graph_sha256'], heuristic_checks=s['heuristic_checks'],
                    results={k: r['result'] for k, r in s['runs'].items()}) for s in output]), indent=2) + '\n')
    print(f'Built {len(output)} scenarios and {sum(len(s["runs"]) for s in output)} validated animation runs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='results/latest')
    args = parser.parse_args()
    build(args.results)
