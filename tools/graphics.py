"""Original vector diagrams, rendered from shared fixtures. No third-party art."""

# Allow both direct execution and package imports.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import json
from html import escape
from math import hypot
from pathlib import Path

import cairosvg
from graphs.fixtures import main_case

INK = "#17323d"
MUTED = "#64777b"
TEAL = "#087e79"
PAPER = "#fffefb"


def svg_graph(case, show_h=False, solution=False, mono=False, reweight=False, state=None):
    g = case["graph"]
    nine = len(g) == 9
    pos = (
        {
            "S": (100, 310),
            "A": (210, 310),
            "B": (320, 310),
            "C": (430, 310),
            "T": (760, 310),
            "D": (100, 230),
            "E": (100, 150),
            "F": (210, 150),
            "G": (210, 70),
        }
        if nine
        else {"S": (100, 260), "A": (430, 90), "B": (430, 400), "T": (760, 260)}
    )
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520"><rect width="900" height="520" fill="{PAPER}"/>'
    ]
    route = ["S", "A", "B", "C", "T"] if nine else ["S", "B", "A", "T"]
    bends = {("S", "B"): 100, ("S", "T"): 320, ("A", "C"): 190, ("B", "T"): 130, ("B", "A"): -70}
    for u, arcs in g.items():
        for v, w in arcs:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            if nine:
                cy += bends.get((u, v), 0)
            if nine and u == "G" and v == "T":
                cx, cy = 660, 10
            d1 = hypot(cx - x1, cy - y1)
            d2 = hypot(x2 - cx, y2 - cy)
            sx, sy = x1 + 22 * (cx - x1) / d1, y1 + 22 * (cy - y1) / d1
            ex, ey = x2 - 26 * (x2 - cx) / d2, y2 - 26 * (y2 - cy) / d2
            lx = 0.25 * x1 + 0.5 * cx + 0.25 * x2
            ly = 0.25 * y1 + 0.5 * cy + 0.25 * y2
            highlighted = solution and any(a == u and b == v for a, b in zip(route, route[1:]))
            col = INK if mono else TEAL if highlighted else "#829796"
            width = 5 if highlighted else 2
            if reweight:
                w = w + case["h"][v] - case["h"][u]
            parts.append(
                f'<path d="M{sx},{sy} Q{cx},{cy} {ex},{ey}" fill="none" stroke="{col}" stroke-width="{width}"/>'
            )
            # Draw the marker explicitly: CairoSVG's marker orientation differs
            # from the browser. Match its triangle size and final edge tangent.
            tx, ty = (ex - cx) / hypot(ex - cx, ey - cy), (ey - cy) / hypot(ex - cx, ey - cy)
            scale = width * 0.6
            tip = (ex + scale * tx, ey + scale * ty)
            base = (ex - 9 * scale * tx, ey - 9 * scale * ty)
            left = (base[0] - 5 * scale * ty, base[1] + 5 * scale * tx)
            right = (base[0] + 5 * scale * ty, base[1] - 5 * scale * tx)
            points = " ".join(f"{x},{y}" for x, y in [tip, left, right])
            parts.append(f'<polygon points="{points}" fill="{col}"/>')
            parts.append(
                f'<rect x="{lx - 16}" y="{ly - 15}" width="32" height="27" rx="5" fill="{PAPER}"/><text x="{lx}" y="{ly + 6}" text-anchor="middle" font-family="sans-serif" font-size="21" font-weight="bold" fill="{INK}">{w}</text>'
            )
    for u in g:
        x, y = pos[u]
        fill = PAPER if mono else "#def0e4" if solution and u in route else PAPER
        if state:
            front = {e["node"] for e in state["queue"] if not e["stale"]}
            seen = set(state["finalized"]) | set(state["expanded"])
            fill = (
                "#f3c88d"
                if u == state["variables"].get("u")
                else "#a7d9c2"
                if u in front
                else "#c8d3e8"
                if u in seen
                else PAPER
            )
        parts.append(f'<circle cx="{x}" cy="{y}" r="22" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
        if show_h:
            parts.append(
                f'<text x="{x}" y="{y - 2}" text-anchor="middle" font-family="sans-serif" font-size="18" font-weight="bold" fill="{INK}">{escape(u)}</text><text x="{x}" y="{y + 13}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="{MUTED}">h={case["h"][u]}</text>'
            )
        else:
            parts.append(
                f'<text x="{x}" y="{y + 7}" text-anchor="middle" font-family="sans-serif" font-size="21" font-weight="bold" fill="{INK}">{escape(u)}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def build(root):
    root = Path(root)
    p = root / "graphs"
    p.mkdir(exist_ok=True)
    variants = [
        ("main_graph", main_case(), False, False, False, False),
        ("main_graph_heuristic", main_case(), True, False, False, False),
        ("main_graph_solution", main_case(), False, True, False, False),
        ("main_graph_print", main_case(), False, False, True, False),
    ]
    for name, case, show_h, sol, mono, rw in variants:
        s = svg_graph(case, show_h, sol, mono, rw)
        (p / (name + ".svg")).write_text(s)
        cairosvg.svg2png(
            bytestring=s.encode(), write_to=str(p / (name + ".png")), output_width=1800, output_height=1040
        )
    (p / "main_graph.json").write_text(json.dumps(main_case(), indent=2) + "\n")


if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
