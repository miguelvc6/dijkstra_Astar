# Saved street data

`vienna-osm.json` is a public OpenStreetMap road snapshot fetched through the Overpass API. The matching provenance file records the exact query, requested bounding box, retrieval time, OSM database timestamp, endpoint, and SHA-256 hash. Complete intersecting ways are retained, so their nodes can extend beyond the requested box.

**Attribution: © OpenStreetMap contributors.** The data is available under the [Open Database License (ODbL)](https://www.openstreetmap.org/copyright). Preserve this attribution and provenance when redistributing the data or derived graphs.

The teaching graph in `graphs/scenarios.py` includes selected road classes, ignores private/no-access ways and ways tagged `motor_vehicle=no`, honors basic one-way/roundabout tags, and retains the largest strongly connected component. Edge weights are lengths in a local equirectangular projection. Euclidean heuristics are scaled against actual edge weights and checked for consistency.

This model omits turn restrictions, conditional access, speeds, traffic, and other navigation rules. It demonstrates graph search on real street geometry.

Existing snapshots are reused by default. Fetch missing assets with:

```sh
python -m tools.fetch_demo_assets --only streets
```

The query uses a read-only [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) request. Normal benchmark, report, test, and animation commands use local files and require no network access.
