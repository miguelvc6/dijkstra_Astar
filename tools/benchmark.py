"""Run reproducible pathfinding experiments without editing lecture algorithms."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from experiments.registry import label, variants
from experiments.validation import fingerprint, graph_fingerprint, heuristic_checks, reference
from graphs.scenarios import benchmark_cases, demo_cases

ROOT = Path(__file__).resolve().parents[1]


def source_hashes():
    files = [path for folder in ['algorithms', 'experiments', 'graphs'] for path in sorted((ROOT / folder).glob('*.py'))]
    files += [ROOT / 'tools/benchmark.py', ROOT / 'tools/trace_search.py']
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}


def write_tables(destination, rows):
    columns = ['case_id', 'case', 'family', 'V', 'E', 'seed', 'size', 'algorithm', 'label', 'status', 'phase',
               'validated', 'cost', 'path_length', 'median_ns', 'q1_ns', 'q3_ns', 'peak_python_bytes',
               'iterations_per_sample', 'expansions', 'unique_expanded', 'reexpansions', 'edge_examinations',
               'pushes', 'pops', 'stale_pops', 'decrease_keys', 'peak_frontier', 'recursive_calls', 'max_depth', 'error']
    with (destination / 'summary.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, **row.get('operations', {})})
    with (destination / 'samples.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=['case_id', 'algorithm', 'sample', 'elapsed_ns_per_call', 'iterations_per_sample'])
        writer.writeheader()
        for row in rows:
            for index, elapsed in enumerate(row.get('timing_samples_ns', [])):
                writer.writerow(dict(case_id=row['case_id'], algorithm=row['algorithm'], sample=index,
                                     elapsed_ns_per_call=elapsed, iterations_per_sample=row['iterations_per_sample']))


def run(args):
    cases = benchmark_cases() if args.suite == 'full' else demo_cases()
    destination = ROOT / args.output
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / 'manifest.json'
    hashes = source_hashes()
    config = dict(suite=args.suite, repeats=args.repeats, warmups=args.warmups, sample_ms=args.sample_ms,
                  dfs_timeout=args.dfs_timeout, timeout=args.timeout, order_seed=20261008)
    catalogue, jobs = [], []
    print(f'Validating {len(cases)} cases against NetworkX Bellman–Ford…', flush=True)
    for index, case in enumerate(cases):
        expected = reference(case)
        checks = heuristic_checks(case)
        case_id = f'{index:03d}-{case["family"]}'
        description = dict(case_id=case_id, case=case['name'], family=case['family'], V=len(case['graph']),
                           E=sum(map(len, case['graph'].values())), seed=case['metadata'].get('seed'),
                           size=case['metadata'].get('size', len(case['graph'])), metadata=case['metadata'],
                           graph_sha256=graph_fingerprint(case), reference_cost=None if math.isinf(expected) else expected,
                           heuristic_checks=checks, heuristic_sha256={k: fingerprint(v) for k, v in case['heuristics'].items()})
        catalogue.append(description)
        for key in variants(case):
            jobs.append((description, key, case, expected))
    random.Random(config['order_seed']).shuffle(jobs)
    signature = fingerprint(dict(config=config, source_hashes=hashes, cases=catalogue))
    rows = []
    if args.resume and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest['signature'] != signature:
            raise ValueError('Resume configuration, sources, or cases changed; choose another output directory.')
        if (destination / 'raw.jsonl').exists():
            rows = [json.loads(line) for line in (destination / 'raw.jsonl').read_text().splitlines() if line]
    else:
        if (destination / 'raw.jsonl').exists():
            raise ValueError('Existing run: use --resume or a new --output directory.')
        manifest = dict(schema_version=1, started_utc=datetime.now(timezone.utc).isoformat(), signature=signature,
                        config=config, source_hashes=hashes, python=sys.version, platform=platform.platform(),
                        machine=platform.machine(), processor=platform.processor(), cpu_model=subprocess.run(
                            ['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True, text=True).stdout.strip() if sys.platform == 'darwin' else platform.processor(),
                        packages={name: importlib.metadata.version(name) for name in ['networkx', 'matplotlib', 'Pillow']},
                        gc='Enabled; collection before each timed sample', measurement='Sequential fresh workers; graph construction/imports/validation excluded from timing',
                        memory='Peak traced Python allocations during one algorithm call, including output; graph and supplied heuristic pre-exist tracing',
                        operations='Separate sys.settrace observation of unchanged lecture functions', cases=catalogue)
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    completed = {(row['case_id'], row['algorithm']) for row in rows}
    with (destination / 'raw.jsonl').open('a') as out:
        for index, (description, key, case, expected) in enumerate(jobs):
            if (description['case_id'], key) in completed:
                continue
            base = {k: description[k] for k in ['case_id', 'case', 'family', 'V', 'E', 'seed', 'size']}
            base.update(algorithm=key, label=label(key))
            # Enumeration is intentionally limited to small cyclic graphs and tiny
            # complete-graph growth experiments; never present a skip as a timing.
            if key == 'depth_first' and len(case['graph']) > 11:
                result = dict(status='skipped', validated=False, error='Exhaustive DFS limited to V ≤ 11; factorial growth / recursion depth.')
            else:
                timeout = args.dfs_timeout if key == 'depth_first' else args.timeout
                job = dict(case=case, algorithm=key, expected=None if math.isinf(expected) else expected,
                           timeout=timeout, repeats=args.repeats, warmups=args.warmups, sample_ms=args.sample_ms)
                try:
                    process = subprocess.run([sys.executable, '-m', 'experiments.worker'], cwd=ROOT,
                                             input=json.dumps(job), capture_output=True, text=True,
                                             timeout=max(30, timeout * (args.repeats + args.warmups + 5)))
                    result = json.loads(process.stdout) if process.returncode == 0 else dict(status='worker_error', error=process.stderr[-2000:])
                except subprocess.TimeoutExpired:
                    result = dict(status='timeout', phase='worker', validated=False, error='Parent hard timeout')
            row = {**base, **result}
            rows.append(row)
            out.write(json.dumps(row, allow_nan=False) + '\n')
            out.flush()
            if index % 15 == 0 or result['status'] not in {'ok', 'skipped'}:
                print(f'{index + 1}/{len(jobs)} · {case["name"]} · {key}: {result["status"]}', flush=True)
    if hashes != source_hashes():
        raise RuntimeError('Sources changed during the experiment; results cannot be certified as one source snapshot.')
    write_tables(destination, rows)
    manifest.update(finished_utc=datetime.now(timezone.utc).isoformat(), rows=len(rows),
                    statuses={status: sum(row['status'] == status for row in rows) for status in sorted({row['status'] for row in rows})})
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest['statuses']), flush=True)
    if any(row['status'] in {'error', 'worker_error'} for row in rows):
        raise RuntimeError('Experiment errors recorded; inspect raw.jsonl')
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=['full', 'demo'], default='full')
    parser.add_argument('--output', default='results/latest')
    parser.add_argument('--repeats', type=int, default=9)
    parser.add_argument('--warmups', type=int, default=2)
    parser.add_argument('--sample-ms', type=float, default=10)
    parser.add_argument('--dfs-timeout', type=float, default=.5)
    parser.add_argument('--timeout', type=float, default=10)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if args.repeats < 3 or min(args.dfs_timeout, args.timeout, args.sample_ms) <= 0 or args.warmups < 0:
        parser.error('Use at least three repeats, nonnegative warmups and positive durations.')
    run(args)
