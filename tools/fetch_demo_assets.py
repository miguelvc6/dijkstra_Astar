"""Fetch and preserve the public data/assets used by offline lecture demos."""
import argparse
import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
KENNEY_URL = 'https://kenney.nl/media/pages/assets/tiny-dungeon/f8422efb44-1674742415/kenney_tiny-dungeon.zip'
BBOX = [48.205, 16.352, 48.218, 16.373]
QUERY = f'[out:json][timeout:25];way["highway"~"^(primary|secondary|tertiary|residential|living_street|unclassified|service)$"]({",".join(map(str, BBOX))});(._;>;);out body;'


def download(url, data=None):
    request = Request(url, data=data, headers={'User-Agent': 'GraphAlgorithmsLecture/1.0 (offline educational data snapshot)'})
    with urlopen(request, timeout=40) as response:
        return response.read()


def fetch_streets():
    destination = ROOT / 'graphs/data/vienna-osm.json'
    if destination.exists():
        return
    errors = []
    for endpoint in ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter']:
        try:
            raw = download(endpoint, urlencode({'data': QUERY}).encode())
            parsed = json.loads(raw)
            if 'remark' in parsed or not parsed.get('elements'):
                raise ValueError(parsed.get('remark', 'Empty OSM response'))
            destination.write_bytes(raw)
            provenance = dict(source='OpenStreetMap contributors', source_url='https://www.openstreetmap.org/copyright',
                              license='ODbL-1.0', endpoint=endpoint, query=QUERY, bbox=BBOX,
                              retrieved_utc=datetime.now(timezone.utc).isoformat(),
                              sha256=hashlib.sha256(raw).hexdigest(), osm_timestamp=parsed.get('osm3s', {}).get('timestamp_osm_base'))
            (destination.parent / 'vienna-osm-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
            print(f'Saved {len(parsed["elements"])} OSM elements to {destination}')
            return
        except Exception as error:
            errors.append(f'{endpoint}: {error}')
    raise RuntimeError('\n'.join(errors))


def fetch_sprites():
    destination = ROOT / 'web/assets/tiny-dungeon'
    if (destination / 'manifest.json').exists():
        return
    raw = download(KENNEY_URL)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        # Preserve the original atlas and license; individual roles are selected
        # from the atlas after inspecting it, without altering the original.
        for name in names:
            if name.lower().endswith('license.txt') or ('tilemap' in name.lower() and name.endswith('.png')):
                (destination / Path(name).name).write_bytes(archive.read(name))
        (destination / 'manifest.json').write_text(json.dumps(dict(
            creator='Kenney', pack='Tiny Dungeon', source_url='https://kenney.nl/assets/tiny-dungeon',
            download_url=KENNEY_URL, license='CC0-1.0', archive_sha256=hashlib.sha256(raw).hexdigest(),
            retrieved_utc=datetime.now(timezone.utc).isoformat(), archive_files=names,
        ), indent=2) + '\n')
    print(f'Saved Kenney atlas and license to {destination}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=['streets', 'sprites'])
    args = parser.parse_args()
    if args.only != 'sprites':
        fetch_streets()
    if args.only != 'streets':
        fetch_sprites()
