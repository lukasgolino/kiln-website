"""Helpers shared by the generator scripts in this folder (locomotive.py, diver.py).

Plain geometry on top of the notation: a `P()` that writes one part with tidy numbers, outlines for plates standing
in a vertical plane, arcs, and block letters as SVG path data for cast nameplates.
"""

from __future__ import annotations

import math
from typing import Any

# options that belong to the part, not to its shape
PART_LEVEL = {
    "emission", "blend", "blend_to", "color_blend", "resolution", "density", "cut", "intersect", "mirror", "mirror_id", "array", "shell",
    "fit", "twist", "detail", "scale", "noise", "folds", "pattern", "gradient", "loose", "hard", "chamfer", "bevel", "segments",
    "bevel_edges", "keep", "aim", "on", "skin_falloff",
}  # fmt: skip


def r4(v: Any) -> Any:
    """Numbers rounded to a tenth of a millimetre, tuples as lists: tidy, stable YAML."""
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    if isinstance(v, dict):
        return {k: r4(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [r4(x) for x in v]
    if isinstance(v, int):
        return v
    out = round(float(v), 4)
    return 0.0 if out == 0 else out


def P(shape: str, color: str | None = None, material: str | None = None, id: str | None = None, **kw: Any) -> dict[str, Any]:  # noqa: A002
    """One part: the shape's own parameters stay in the shape, part options go beside it."""
    options = {k: kw.pop(k) for k in list(kw) if k in PART_LEVEL and not (shape == "band" and k == "fit")}  # a band's `fit` is its own
    out: dict[str, Any] = {shape: r4(kw)}
    if id:
        out["id"] = id
    if color:
        out["color"] = color
    if material:
        out["material"] = material
    out.update(r4(options))
    return out


def arc(cx: float, cy: float, r: float, a0: float, a1: float, n: int) -> list[tuple[float, float]]:
    """`n` + 1 points on a circle from angle a0 to a1 (degrees, counter-clockwise from +x)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def circle(cx: float, cy: float, r: float, n: int = 20) -> list[tuple[float, float]]:
    return arc(cx, cy, r, 0, 360, n)[:-1]


def rrect(x0: float, y0: float, x1: float, y1: float, r: float, n: int = 4) -> list[tuple[float, float]]:
    """A rectangle with rounded corners, counter-clockwise."""
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return [*arc(x1 - r, y0 + r, r, -90, 0, n), *arc(x1 - r, y1 - r, r, 0, 90, n), *arc(x0 + r, y1 - r, r, 90, 180, n), *arc(x0 + r, y0 + r, r, 180, 270, n)]


def plate_x(points: list[tuple[float, float]], x: float, thick: float, color: str, material: str | None = None, id: str | None = None,  # noqa: A002
            holes: list[list[tuple[float, float]]] | None = None, **kw: Any) -> dict[str, Any]:  # fmt: skip
    """A plate whose faces look along x, centred on `x`: outline points are (z, y) in model space."""
    extra: dict[str, Any] = {"holes": [[[y, z] for z, y in h] for h in holes]} if holes else {}
    return P("extrude", color, material, id, points=[[y, z] for z, y in points], height=thick, at=[x, 0, 0], rotate=[0, 0, 90], **extra, **kw)


def plate_z(points: list[tuple[float, float]], z: float, thick: float, color: str, material: str | None = None, id: str | None = None,  # noqa: A002
            holes: list[list[tuple[float, float]]] | None = None, **kw: Any) -> dict[str, Any]:  # fmt: skip
    """A plate whose faces look along z, centred on `z`: outline points are (x, y) in model space."""
    extra: dict[str, Any] = {"holes": [[[x, -y] for x, y in h] for h in holes]} if holes else {}
    return P("extrude", color, material, id, points=[[x, -y] for x, y in points], height=thick, at=[0, 0, z], rotate=[90, 0, 0], **extra, **kw)


# Block letters on a grid 7 units tall (y runs down, as SVG): straight strokes and cut corners, like letters cast in a
# foundry pattern. Each glyph: its width and its outlines (the first is the body, the others are counters).
GLYPHS: dict[str, tuple[float, list[list[tuple[float, float]]]]] = {
    "E": (5, [[(0, 0), (5, 0), (5, 1.3), (1.4, 1.3), (1.4, 2.85), (4, 2.85), (4, 4.15), (1.4, 4.15), (1.4, 5.7), (5, 5.7), (5, 7), (0, 7)]]),
    "M": (6, [[(0, 7), (0, 0), (1.5, 0), (3, 3.2), (4.5, 0), (6, 0), (6, 7), (4.6, 7), (4.6, 2.6), (3.4, 5.2), (2.6, 5.2), (1.4, 2.6), (1.4, 7)]]),
    "B": (5, [[(0, 0), (3.9, 0), (5, 1.0), (5, 2.7), (4.3, 3.5), (5, 4.3), (5, 6.0), (3.9, 7), (0, 7)],
              [(1.4, 1.3), (3.3, 1.3), (3.6, 1.6), (3.6, 2.5), (3.3, 2.85), (1.4, 2.85)],
              [(1.4, 4.15), (3.3, 4.15), (3.6, 4.5), (3.6, 5.4), (3.3, 5.7), (1.4, 5.7)]]),
    "R": (5, [[(0, 0), (3.9, 0), (5, 1.0), (5, 3.2), (4.1, 4.1), (5, 7), (3.5, 7), (2.7, 4.15), (1.4, 4.15), (1.4, 7), (0, 7)],
              [(1.4, 1.3), (3.3, 1.3), (3.6, 1.6), (3.6, 2.5), (3.3, 2.85), (1.4, 2.85)]]),
    "W": (7, [[(0, 0), (1.4, 0), (2.1, 4.6), (2.9, 1.6), (4.1, 1.6), (4.9, 4.6), (5.6, 0), (7, 0), (5.8, 7), (4.3, 7), (3.5, 3.9), (2.7, 7), (1.2, 7)]]),
    "I": (1.4, [[(0, 0), (1.4, 0), (1.4, 7), (0, 7)]]),
    "C": (5, [[(1.0, 0), (4.0, 0), (5, 1.0), (5, 2.2), (3.6, 2.2), (3.6, 1.6), (3.3, 1.3), (1.7, 1.3), (1.4, 1.6), (1.4, 5.4), (1.7, 5.7), (3.3, 5.7),
               (3.6, 5.4), (3.6, 4.8), (5, 4.8), (5, 6.0), (4.0, 7), (1.0, 7), (0, 6.0), (0, 1.0)]]),
    "K": (5, [[(0, 0), (1.4, 0), (1.4, 2.9), (3.4, 0), (5.1, 0), (2.8, 3.3), (5.2, 7), (3.5, 7), (1.9, 4.4), (1.4, 5.1), (1.4, 7), (0, 7)]]),
    "7": (5, [[(0, 0), (5, 0), (5, 1.2), (2.6, 7), (1.1, 7), (3.3, 1.3), (0, 1.3)]]),
}  # fmt: skip


def lettering(text: str, gap: float = 0.9) -> tuple[str, float]:
    """SVG path data for `text` in the block letters, centred on the origin, and its width (units: a letter is 7 tall)."""
    width = sum(GLYPHS[c][0] for c in text) + gap * (len(text) - 1)
    x = -width / 2
    out = []
    for c in text:
        w, outlines = GLYPHS[c]
        for outline in outlines:
            out.append("M " + " L ".join(f"{round(x + px, 3):g} {round(py - 3.5, 3):g}" for px, py in outline) + " Z")
        x += w + gap
    return " ".join(out), width


def curve(points: list[list[float]], per_span: int = 4) -> list[list[float]]:
    """A smooth curve through 3D points (a uniform Catmull-Rom spline), `per_span` samples per span, ends included."""
    ext = [[2 * a - b for a, b in zip(points[0], points[1], strict=True)], *points, [2 * a - b for a, b in zip(points[-1], points[-2], strict=True)]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(per_span):
            t = k / per_span
            out.append([0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t**3) for a, b, c, d in zip(p0, p1, p2, p3, strict=True)])
    out.append(list(points[-1]))
    return out


def on_sphere(centre: list[float], radius: float, yaw: float, pitch: float) -> tuple[list[float], list[float]]:
    """The point on a sphere `yaw` degrees round from the front (+z towards +x) and `pitch` up, and the way out there."""
    y, p = math.radians(yaw), math.radians(pitch)
    n = [math.sin(y) * math.cos(p), math.sin(p), math.cos(y) * math.cos(p)]
    return [c + radius * v for c, v in zip(centre, n, strict=True)], n
