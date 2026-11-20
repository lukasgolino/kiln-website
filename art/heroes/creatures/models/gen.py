"""Helpers shared by the generator scripts in this folder (dragon.py, owl.py).

Everything here is plain geometry on top of `kiln.api`: vectors, smooth curves, frames turned into the notation's
`rotate` angles, and a `P()` that also sorts out the part options `kiln.api.part` doesn't know yet.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from kiln.api import part as _api_part

# part-level options kiln.api.part leaves inside the shape
PART_LEVEL = ("on", "density", "color_blend", "resolution", "detail", "skin_falloff")


def vec(*a: float) -> np.ndarray:
    return np.array(a, dtype=float)


def norm(v: Any) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    return v / max(float(np.linalg.norm(v)), 1e-12)


def tidy(v: Any) -> Any:
    """Numbers rounded to a tenth of a millimetre, arrays as plain lists: tidy, stable YAML."""
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    if isinstance(v, dict):
        return {k: tidy(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, np.ndarray)):
        return [tidy(x) for x in v]
    if isinstance(v, (int, np.integer)):
        return int(v)
    out = round(float(v), 4)
    return 0.0 if out == 0 else out


def P(shape: str, color: str | None = None, id: str | None = None, material: str = "default", **kw: Any) -> dict[str, Any]:
    """One part. Like `kiln.api.part`, with numbers rounded and `on`, `density`, `color_blend`, ... at the part level."""
    extra = {k: kw.pop(k) for k in PART_LEVEL if k in kw}
    out = _api_part(shape, color, material, id, **{k: tidy(v) for k, v in kw.items()})
    if out.get("material") == "default":
        out.pop("material")
    out.update({k: tidy(v) for k, v in extra.items()})
    return out


def curve(points: list[Any], per_span: int = 8) -> np.ndarray:
    """A smooth curve through the points (a uniform Catmull-Rom spline), `per_span` samples per span, ends included."""
    pts = [np.asarray(p, dtype=float) for p in points]
    ext = [pts[0] * 2 - pts[1], *pts, pts[-1] * 2 - pts[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(per_span):
            t = k / per_span
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return np.array(out)


def lengths(path: np.ndarray) -> np.ndarray:
    """Distance along a polyline at each of its points."""
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])


def at_length(path: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray]:
    """The point `s` metres along a polyline and the direction of travel there."""
    acc = lengths(path)
    s = min(max(s, 0.0), float(acc[-1]))
    i = int(min(np.searchsorted(acc, s, side="right") - 1, len(path) - 2))
    f = (s - acc[i]) / max(float(acc[i + 1] - acc[i]), 1e-12)
    a, b = path[max(i - 1, 0)], path[min(i + 2, len(path) - 1)]
    return path[i] + (path[i + 1] - path[i]) * f, norm(b - a)


def euler(ex: Any, ey: Any, ez: Any) -> list[float]:
    """The notation's `rotate: [x, y, z]` (degrees, applied x then y then z) for a frame given by its three axes."""
    m = np.column_stack([norm(ex), norm(ey), norm(ez)])
    b = -math.asin(max(-1.0, min(1.0, float(m[2, 0]))))
    a = math.atan2(float(m[2, 1]), float(m[2, 2]))
    c = math.atan2(float(m[1, 0]), float(m[0, 0]))
    return [math.degrees(a), math.degrees(b), math.degrees(c)]


def panel(corners: list[Any], thickness: float, sag: dict[int, float] | None = None, steps: int = 7) -> dict[str, Any]:
    """The shape parameters of an `extrude` lying in the plane of a 3D polygon (its corners in order). `sag` curves
    the edge starting at corner k inwards by that many metres (a membrane's scalloped trailing edge)."""
    pts = [np.asarray(c, dtype=float) for c in corners]
    centre = np.mean(pts, axis=0)
    u = norm(pts[1] - pts[0])
    n = norm(np.cross(pts[1] - pts[0], pts[2] - pts[0]))
    v = np.cross(u, n)
    outline: list[np.ndarray] = []
    for k, p in enumerate(pts):
        q = pts[(k + 1) % len(pts)]
        outline.append(p)
        depth = (sag or {}).get(k, 0.0)
        if depth:
            inward = norm(centre - (p + q) / 2)
            for j in range(1, steps):
                t = j / steps
                outline.append(p + (q - p) * t + inward * depth * 4 * t * (1 - t))
    flat = [[float((p - centre) @ u), float((p - centre) @ v)] for p in outline]
    return {"points": flat, "height": thickness, "at": centre, "rotate": euler(u, n, v)}


POINT_KEYS = ("at", "from", "to", "base")
SIZE_KEYS = ("radius", "radius_to", "radius_top", "radii", "size", "round", "height", "width", "width_to", "thickness", "thickness_to", "length")
PATH_SHAPES = ("capsule", "tube", "lock")        # written by their points: they need no `rotate` to be turned
ROUND_SHAPES = ("sphere",)


def matrix(degrees: Any) -> np.ndarray:
    """The rotation of the notation's `rotate: [x, y, z]` (degrees, applied x then y then z)."""
    a, b, c = (math.radians(float(v)) for v in degrees)
    rx = np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])
    ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    rz = np.array([[math.cos(c), -math.sin(c), 0], [math.sin(c), math.cos(c), 0], [0, 0, 1]])
    return rz @ ry @ rx


def _each_point(p: dict[str, Any], move: Any) -> None:
    """Apply `move` to every model-space point a part is written with."""
    shape = next(iter(p))
    g = p[shape]
    for key in POINT_KEYS:
        if key in g:
            g[key] = tidy(move(g[key]))
    if "points" in g and shape != "extrude":
        g["points"] = [tidy(move(q)) for q in g["points"]]
    if "aim" in p:
        p["aim"] = [tidy(move(q)) for q in p["aim"]]
    if "on" in p:
        p["on"] = {**p["on"], "near": tidy(move(p["on"]["near"]))}


def grow(parts: list[dict[str, Any]], k: float, about: Any) -> None:
    """Scale parts written in model space by `k` about a point, in place (a head drawn first, sized afterwards)."""
    o = np.asarray(about, dtype=float)
    for p in parts:
        _each_point(p, lambda q: o + (np.asarray(q, dtype=float) - o) * k)
        g = p[next(iter(p))]
        for key in SIZE_KEYS:
            if key in g:
                g[key] = tidy(np.asarray(g[key], dtype=float) * k)
        if "on" in p and "offset" in p["on"]:
            p["on"]["offset"] = tidy(p["on"]["offset"] * k)


def pitch(parts: list[dict[str, Any]], degrees: float, pivot: Any) -> None:
    """Turn parts written in model space about the x axis through `pivot`, in place: positive tips their tops to the
    front. A turn about x keeps `mirror: x` parts mirrored, so the two sides stay one part."""
    o = np.asarray(pivot, dtype=float)
    m = matrix([degrees, 0, 0])
    for p in parts:
        shape = next(iter(p))
        g = p[shape]
        _each_point(p, lambda q: o + m @ (np.asarray(q, dtype=float) - o))
        if "facing" in g:
            g["facing"] = tidy(m @ np.asarray(g["facing"], dtype=float))
        if shape in PATH_SHAPES or shape in ROUND_SHAPES or "aim" in p:
            continue
        if "on" in p and p["on"].get("align", True):
            continue                # it takes its turn from the surface it is placed on
        new = m @ matrix(g.get("rotate", [0, 0, 0]))
        g["rotate"] = tidy(euler(new[:, 0], new[:, 1], new[:, 2]))


def turn(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> dict[str, Any]:
    """A pose entry turning a part (degrees about x, y, z)."""
    return {"rotate": tidy([x, y, z])}


def keyed(keys: list[tuple[int, dict[str, Any]]], frames: int) -> list[dict[str, Any]]:
    """Poses for every frame from a few keyed ones (frame, {part: [x, y, z] degrees}), eased between the keys."""
    names = sorted({b for _, pose in keys for b in pose})
    out = []
    for i in range(frames):
        k = max(j for j, (f, _) in enumerate(keys) if f <= i)
        (f0, p0), (f1, p1) = keys[k], keys[min(k + 1, len(keys) - 1)]
        t = 0.0 if f1 == f0 else (i - f0) / (f1 - f0)
        t = t * t * (3 - 2 * t)
        pose = {}
        for b in names:
            a, c = np.array(p0.get(b, [0, 0, 0]), dtype=float), np.array(p1.get(b, [0, 0, 0]), dtype=float)
            v = a + (c - a) * t
            if float(np.abs(v).max()) > 1e-6:
                pose[b] = turn(*v)
        out.append(pose)
    return out
