"""Audit coverage, sources, saved inputs, and every completed measured result."""
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

from experiments.registry import arguments, function, variants
from experiments.validation import graph_fingerprint, heuristic_checks, reference, validate
from graphs.scenarios import benchmark_cases, demo_cases
from tools.benchmark import source_hashes

ROOT = Path(__file__).resolve().parents[1]


def verify(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    rows = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines()]
    assert manifest.get('finished_utc'), 'Experiment is not complete'
    assert source_hashes() == manifest['source_hashes'], 'Measurement sources changed'
    assert len(rows) == manifest['rows']
    ids = [(row['case_id'], row['algorithm']) for row in rows]
    assert len(ids) == len(set(ids)), 'Duplicate measurement rows'
    cases = benchmark_cases() if manifest['config']['suite'] == 'full' else demo_cases()
    assert len(cases) == len(manifest['cases'])
    expected_jobs = set()
    reconstructed = []
    checked = 0
    for item, description in zip(cases, manifest['cases']):
        assert graph_fingerprint(item) == description['graph_sha256']
        heuristic_checks(item)
        expected = reference(item)
        assert (None if math.isinf(expected) else expected) == description['reference_cost']
        case_id = description['case_id']
        reconstructed.append(dict(case_id=case_id, case=item))
        for key in variants(item):
            expected_jobs.add((case_id, key))
            row = next(r for r in rows if r['case_id'] == case_id and r['algorithm'] == key)
            if row['status'] == 'ok' or row.get('timing_samples_ns'):
                assert row['validated'], (case_id, key)
                assert len(row['timing_samples_ns']) == manifest['config']['repeats']
                assert all(value > 0 for value in row['timing_samples_ns'])
                result = function(key)(*arguments(key, item))
                validate(result, item, expected)
                assert (None if math.isinf(result[0]) else result[0]) == row['cost']
                if row['status'] == 'ok':
                    assert row['peak_python_bytes'] > 0 and 'operations' in row
                checked += 1
            elif row['status'] == 'skipped':
                assert key == 'depth_first' and len(item['graph']) > 11
            elif row['status'] == 'timeout':
                assert 'phase' in row and 'error' in row
            else:
                raise AssertionError(f'Unexpected status: {row}')
    assert set(ids) == expected_jobs, 'Missing or extra configurations'
    with (directory / 'samples.csv').open() as source:
        samples = list(csv.DictReader(source))
    assert len(samples) == sum(len(row.get('timing_samples_ns', [])) for row in rows)
    raw_osm = ROOT / 'graphs/data/vienna-osm.json'
    provenance = json.loads((raw_osm.parent / 'vienna-osm-provenance.json').read_text())
    assert hashlib.sha256(raw_osm.read_bytes()).hexdigest() == provenance['sha256']
    encoded = json.dumps(reconstructed, separators=(',', ':'), allow_nan=False).encode()
    archive = directory / 'cases.json.gz'
    archive.write_bytes(gzip.compress(encoded, mtime=0))
    proof = dict(cases=len(cases), unique_graph_endpoint_inputs=len({c['graph_sha256'] for c in manifest['cases']}),
                 configurations=len(rows), validated_replays=checked, raw_timing_samples=len(samples),
                 source_hashes_match=True, algorithms_unchanged_from_run_start=True, osm_hash_matches=True,
                 input_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                 cases_archive='cases.json.gz', statuses=manifest['statuses'])
    (directory / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', default='results/latest')
    args = parser.parse_args()
    verify(ROOT / args.results)
