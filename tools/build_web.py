"""Embed actual Python execution traces in a self-contained offline HTML file."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import json
from pathlib import Path

from tools.trace_search import build_traces


def build(root):
    root = Path(root)
    data = build_traces()
    encoded = json.dumps(data, separators=(",", ":"), allow_nan=False)
    template = (root / "web/template.html").read_text()
    assert template.count("__TRACE_DATA__") == 1
    (root / "web/traces.json").write_text(encoded + "\n")
    # Escaping '<' keeps source code unable to terminate its enclosing script tag.
    (root / "web/visualizer.html").write_text(template.replace("__TRACE_DATA__", encoded.replace("<", "\\u003c")))
    return data


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
