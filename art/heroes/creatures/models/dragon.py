"""Generates dragon.kiln.yaml: a stocky forest dragon on four legs, wings half open.

Run from the project folder:  python models/dragon.py [--blockout] [--quick]

The body is a handful of big blended shapes. The parts that repeat along it (back spines, belly plates, teeth,
wing fingers and membranes) are written here from a few curves, so moving a curve moves them
all. The scale coat itself is relief (baked maps), not parts.

  --blockout  no repeated parts, no relief: shapes and proportions in seconds with `kiln preview dragon --draft`
  --quick     1024 maps instead of 2048 (the bake is most of the build)
"""

from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen import (
    P,
    at_length,
    curve,
    grow,
    keyed,
    lengths,
    matrix,
    norm,
    panel,
    pitch,
    tidy,
    turn,
    vec,
)
from kiln.api import model, write_model

BLOCKOUT = "--blockout" in sys.argv
QUICK = "--quick" in sys.argv
UP = vec(0, 1, 0)
parts: list[dict] = []


def add(shape: str, color: str | None = None, id: str | None = None, **kw) -> dict:
    parts.append(P(shape, color, id, **kw))
    return parts[-1]


def left(shape: str, color: str | None, id: str, **kw) -> dict:
    """A part of the left side (+x) whose mirror image is the right side's own part (`thigh_l` -> `thigh_r`)."""
    return add(shape, color, id, mirror="x", mirror_id=id[:-2] + "_r", **kw)


def sub(path: np.ndarray, a: float, b: float, n: int = 4) -> list:
    """`n` points of a curve between two distances along it."""
    return [at_length(path, a + (b - a) * k / (n - 1))[0] for k in range(n)]


def dorsal(travel: np.ndarray) -> np.ndarray:
    """Straight out of the back, for a line running in direction `travel`."""
    return norm(UP - travel * float(UP @ travel))


# ------------------------------------------------------------------ the lines everything hangs on
NECK = curve([[0, 1.02, 0.5], [0, 1.2, 0.7], [0, 1.35, 0.78], [0, 1.46, 0.86]])       # chest to skull
NECK_R = (0.29, 0.175)                                                                 # radius at its ends
TAIL = curve([[0, 0.9, -0.7], [0, 0.76, -1.0], [0.06, 0.55, -1.27], [0.22, 0.36, -1.48], [0.45, 0.25, -1.6],
              [0.7, 0.22, -1.56], [0.9, 0.27, -1.4]])                                  # hips to tip, curling to its left
TAIL_R = (0.28, 0.045)
TAIL_CUTS = [0.0, 0.24, 0.48, 0.72, 1.0]                                               # where its four bones start, as shares
NECK_LEN, TAIL_LEN = float(lengths(NECK)[-1]), float(lengths(TAIL)[-1])
NECK_HALF = NECK_LEN * 0.52
SPINE_IDS = ["chest", "body", "neck1", "neck2", "tail1", "tail2", "tail3", "tail4"]


def neck_r(s: float) -> float:
    return NECK_R[0] + (NECK_R[1] - NECK_R[0]) * s / NECK_LEN


def tail_r(share: float) -> float:
    return TAIL_R[0] + (TAIL_R[1] - TAIL_R[0]) * share ** 0.85


# ------------------------------------------------------------------ trunk
add("ellipsoid", "scale_moss", "chest", at=[0, 0.95, 0.32], radii=[0.37, 0.4, 0.43])
add("ellipsoid", "scale_moss", "body", at=[0, 0.89, -0.12], radii=[0.385, 0.38, 0.47], blend=0.1)
add("ellipsoid", "scale_moss", "body", at=[0, 0.92, -0.52], radii=[0.34, 0.33, 0.37], blend=0.1)
add("ellipsoid", "scale_pine", "chest", at=[0, 1.26, 0.2], radii=[0.25, 0.13, 0.34], blend=0.1, color_blend=0.1)     # withers
add("ellipsoid", "scale_pine", "body", at=[0, 1.2, -0.36], radii=[0.23, 0.11, 0.46], blend=0.1, color_blend=0.1)     # back

# ------------------------------------------------------------------ neck (two bones) and tail (four), a darker band down their backs
neck_mid = neck_r(NECK_HALF)
add("tube", "scale_moss", "neck1", points=sub(NECK, 0, NECK_HALF), radius=NECK_R[0], radius_to=neck_mid, smooth=True, blend=0.1)
add("tube", "scale_moss", "neck2", points=sub(NECK, NECK_HALF, NECK_LEN), radius=neck_mid, radius_to=NECK_R[1], smooth=True, blend=0.06)
for bone, a, b in (("neck2", NECK_HALF - 0.04, NECK_LEN - 0.03),):
    pts = [at_length(NECK, s)[0] + dorsal(at_length(NECK, s)[1]) * neck_r(s) * 0.5 for s in np.linspace(a, b, 4)]
    add("tube", "scale_pine", bone, points=pts, radius=neck_r(a) * 0.66, radius_to=neck_r(b) * 0.66, smooth=True, blend=0.05, color_blend=0.08)
for k in range(4):
    a, b = TAIL_CUTS[k], TAIL_CUTS[k + 1]
    add("tube", "scale_moss", f"tail{k + 1}", points=sub(TAIL, a * TAIL_LEN, b * TAIL_LEN), radius=tail_r(a), radius_to=tail_r(b), smooth=True,
        blend=0.1 if k == 0 else 0.05)
    if k < 3:
        pts = [at_length(TAIL, t * TAIL_LEN)[0] + dorsal(at_length(TAIL, t * TAIL_LEN)[1]) * tail_r(t) * 0.5 for t in np.linspace(a, b, 4)]
        add("tube", "scale_pine", f"tail{k + 1}", points=pts, radius=tail_r(a) * 0.66, radius_to=tail_r(b) * 0.66, smooth=True, blend=0.05,
            color_blend=0.08)
# the tail ends in a leaf: two flat blades, widening then closing to a point
tip, tip_dir = at_length(TAIL, TAIL_LEN)
leaf_mid, leaf_end = tip + tip_dir * 0.2 + UP * 0.04, tip + tip_dir * 0.5 + UP * 0.14
leaf_face = norm(np.cross(tip_dir, np.cross(UP, tip_dir)) + vec(0, 0.2, 0))
add("lock", "wing_wine", "tail4", material="membrane", points=[tip - tip_dir * 0.05, leaf_mid], width=0.06, width_to=0.27, thickness=0.06,
    thickness_to=0.034, facing=leaf_face, blend=0.03, blend_to=["tail4"], color_blend=0.03)
add("lock", "wing_wine", "tail4", material="membrane", points=[leaf_mid, leaf_end], width=0.27, width_to=0, thickness=0.034,
    thickness_to=0.016, facing=leaf_face, blend=0.012, blend_to=["tail4"], gradient={"to": "wing_ember", "steps": 4})

# ------------------------------------------------------------------ legs: the haunches are the trunk's, the limbs hang clear of it
SHOULDER, ELBOW, WRIST = vec(0.35, 0.78, 0.38), vec(0.44, 0.44, 0.29), vec(0.44, 0.14, 0.42)
HIP, KNEE, HOCK = vec(0.36, 0.78, -0.5), vec(0.46, 0.47, -0.3), vec(0.46, 0.17, -0.57)
add("ellipsoid", "scale_moss", "chest", at=SHOULDER + vec(-0.02, 0.06, 0), radii=[0.17, 0.27, 0.22], blend=0.07, mirror="x")
left("capsule", "scale_moss", "foreleg_l", from_=SHOULDER, to=ELBOW, radius=0.155, radius_to=0.12, blend=0.06)
left("capsule", "scale_moss", "forearm_l", from_=ELBOW, to=WRIST, radius=0.115, radius_to=0.09, blend=0.05)
left("cone", "horn_bone", "foreleg_l", material="horn", aim=[ELBOW + vec(0.01, 0.02, -0.06), ELBOW + vec(0.03, 0.09, -0.24)], radius=0.04)   # elbow spur
add("ellipsoid", "scale_moss", "body", at=HIP + vec(-0.02, 0.0, 0.04), radii=[0.19, 0.32, 0.28], rotate=[-20, 0, 0], blend=0.07, mirror="x")
left("capsule", "scale_moss", "thigh_l", from_=HIP, to=KNEE, radius=0.18, radius_to=0.125, blend=0.06)
left("capsule", "scale_moss", "shin_l", from_=KNEE, to=HOCK, radius=0.12, radius_to=0.085, blend=0.05)
left("cone", "horn_bone", "shin_l", material="horn", aim=[HOCK + vec(0.0, 0.03, -0.04), HOCK + vec(0.01, 0.12, -0.19)], radius=0.035)         # hock spur
# feet: soles on the ground, toes forward and a little out, heavy claws
left("foot", "scale_moss", "forefoot_l", at=[WRIST[0], 0, WRIST[2] - 0.12], rotate=[0, 12, 0], length=0.44, width=0.32, toes=4, curl=22,
     spread=13, nail=0.09, nail_color="claw", blend=0.035, density=1.8)
left("foot", "scale_moss", "hindfoot_l", at=[HOCK[0], 0, HOCK[2] - 0.1], rotate=[0, 14, 0], length=0.47, width=0.33, toes=4, curl=22,
     spread=13, nail=0.095, nail_color="claw", blend=0.035, density=1.8)

# ------------------------------------------------------------------ head: drawn level about H at 1 : 1.3, then grown and pitched down
H = vec(0, 1.5, 0.95)
HEAD_SCALE = 1.3
HEAD_FROM = len(parts)
JAW_PIVOT = vec(0, -0.06, -0.02)


def h(x: float, y: float, z: float) -> np.ndarray:
    return H + vec(x, y, z)


SNOUT = [((0, -0.01, 0.2), (0.097, 0.07, 0.17)), ((0, -0.014, 0.33), (0.076, 0.058, 0.1))]   # two ovals, wide to narrow
JAW = ((0, -0.1, 0.18), (0.078, 0.036, 0.2))


def side_of(ovals: list, y: float, z: float) -> float:
    """How far out (x) the surface of the widest of some ovals is at height y and depth z (head coordinates)."""
    best = 0.0
    for (cx, cy, cz), (rx, ry, rz) in ovals:
        inside = 1 - ((y - cy) / ry) ** 2 - ((z - cz) / rz) ** 2
        best = max(best, rx * math.sqrt(inside)) if inside > 0 else best
    return best


add("ellipsoid", "scale_moss", "head", at=H, radii=[0.132, 0.108, 0.16], blend=0.05, density=2.5)                                    # skull
for c, rad in SNOUT:
    add("ellipsoid", "scale_moss", "head", at=h(*c), radii=rad, blend=0.04, density=2.5)
add("ellipsoid", "scale_moss", "head", at=h(0.036, 0.034, 0.385), radii=[0.026, 0.024, 0.036], blend=0.014, mirror="x")                # nostril bumps
add("capsule", "scale_moss", "head", from_=h(0, 0.045, 0.14), to=h(0, 0.036, 0.36), radius=0.03, radius_to=0.022, blend=0.03)          # the ridge of the nose
add("capsule", "scale_pine", "head", from_=h(0.045, 0.066, 0.2), to=h(0.124, 0.09, -0.03), radius=0.02, radius_to=0.032, blend=0.035,
    color_blend=0.04, mirror="x")                                                                                                     # brows
add("ellipsoid", "scale_moss", "head", at=h(0.096, -0.04, 0.0), radii=[0.052, 0.066, 0.095], blend=0.04, mirror="x")                   # jaw muscles
add("sphere", "mouth", None, at=h(0.05, 0.042, 0.412), radius=0.0105, cut=True, mirror="x")                                           # nostrils
# mouth: a dark inside, the tongue, and the lower jaw as its own bone (`transforms` open it a little)
add("ellipsoid", "mouth", "head", at=h(0, -0.066, 0.2), radii=[0.064, 0.024, 0.18])
add("ellipsoid", "scale_moss", "jaw", at=h(*JAW[0]), radii=JAW[1], density=2.5)
add("ellipsoid", "scale_moss", "jaw", at=h(0, -0.098, 0.34), radii=[0.058, 0.032, 0.062], blend=0.03, density=2.5)                    # chin
add("ellipsoid", "scale_moss", "jaw", at=h(0.066, -0.088, 0.01), radii=[0.04, 0.046, 0.075], blend=0.035, mirror="x")                  # hinge
add("ellipsoid", "belly_cream", "jaw", material="plate", at=h(0, -0.125, 0.2), radii=[0.05, 0.018, 0.16], blend=0.02, color_blend=0.03)
add("ellipsoid", "tongue", "jaw", at=h(0, -0.071, 0.2), radii=[0.038, 0.014, 0.14])
# eyes: an amber ball under the brow, a slit pupil, a lower lid
# (placed on the head's own surface and sunk into it, so they sit right whatever the skull's shapes do; their own bones)
EYE_OUT, EYE_R = vec(0.2, 0.03, 0.105), 0.038
left("sphere", "eye_amber", "eye_l", material="eye", radius=EYE_R, keep=True, on={"part": ["head"], "near": tidy(H + EYE_OUT), "offset": -EYE_R * 0.52})
left("ellipsoid", "ink", "eye_l", material="eye", radii=[0.027, 0.006, 0.0095], keep=True,
     on={"part": ["eye_l"], "near": tidy(H + EYE_OUT), "offset": -0.002})
add("capsule", "scale_pine", "head", from_=h(0.085, 0.0, 0.16), to=h(0.128, 0.004, 0.05), radius=0.015, blend=0.012, color_blend=0.02,
    mirror="x")                                                                                                                       # lower lids
# horns: a long swept pair growing out of the brows, a short pair under them, two crest blades
add("tube", "horn_umber", "head", material="horn", points=[h(0.088, 0.08, -0.05), h(0.128, 0.165, -0.2), h(0.152, 0.215, -0.37),
                                                          h(0.15, 0.218, -0.52)],
    radius=0.047, radius_to=0.008, smooth=True, mirror="x", blend=0.012, gradient={"to": "horn_bone", "steps": 5})
add("tube", "horn_umber", "head", material="horn", points=[h(0.118, -0.005, -0.08), h(0.18, 0.012, -0.2), h(0.205, 0.045, -0.31)],
    radius=0.03, radius_to=0.006, smooth=True, mirror="x", blend=0.01, gradient={"to": "horn_bone", "steps": 3})
if not BLOCKOUT:
    for z, tall in ((-0.07, 0.06),):
        add("lock", "wing_wine", "head", material="horn", points=[h(0, 0.09, z + 0.01), h(0, 0.105 + tall, z - tall * 0.9)], width=tall * 1.1,
            width_to=0, thickness=0.024, thickness_to=0.01, facing=[1, 0, 0], gradient={"to": "wing_ember", "steps": 3})
    for z, tall in ((0.3, 0.035), (0.23, 0.045), (0.15, 0.04)):   # chin barbs
        base = h(0.03, -0.122, z)
        add("cone", "horn_bone", "jaw", material="horn", keep=True, aim=[base, base + vec(0.012, -tall, -tall * 0.7)], radius=0.014, mirror="x")
    # teeth: the upper row hangs outside the lip, the lower row stands on the jaw between them
    for k in range(7):
        z = 0.105 + 0.046 * k
        x = side_of(SNOUT, -0.052, z)
        long = 0.058 if k == 5 else 0.034 if k % 2 else 0.04
        base = h(x - 0.01, -0.046, z)
        add("cone", "ivory", "head", material="ivory", keep=True, aim=[base, base + vec(0.008, -long, 0.004)], radius=0.016 if k == 5 else 0.0125, mirror="x")
    for x in (0.022, 0.05):   # front teeth
        add("cone", "ivory", "head", material="ivory", keep=True, aim=[h(x, -0.05, 0.415 - x * 0.35), h(x, -0.085, 0.425 - x * 0.35)], radius=0.011, mirror="x")
    for k in range(5):
        z = 0.13 + 0.05 * k
        x = side_of([JAW], -0.078, z)
        base = h(x - 0.012, -0.082, z)
        add("cone", "ivory", "jaw", material="ivory", keep=True, aim=[base, base + vec(0.004, 0.05 if k == 3 else 0.034, 0)], radius=0.0115, mirror="x")
grow(parts[HEAD_FROM:], HEAD_SCALE, H)
JAW_PIVOT = H + JAW_PIVOT * HEAD_SCALE
# the jaw hangs open a little, the whole head looks down a little (turned here, about x, so mirrored parts stay mirrored)
JAW_OPEN, HEAD_PITCH = 10, 13
pitch([p for p in parts[HEAD_FROM:] if p.get("id") == "jaw"], JAW_OPEN, JAW_PIVOT)
pitch(parts[HEAD_FROM:], HEAD_PITCH, NECK[-1])
JAW_PIVOT = NECK[-1] + matrix([HEAD_PITCH, 0, 0]) @ (JAW_PIVOT - NECK[-1])

# ------------------------------------------------------------------ wings: arm, three fingers, membranes between
S, E, W = vec(0.22, 1.27, 0.2), vec(0.52, 1.55, -0.14), vec(0.7, 1.92, 0.18)
TIPS = [vec(1.3, 1.7, -0.15), vec(1.18, 1.2, -0.72), vec(0.8, 0.94, -1.0)]
FLANK = vec(0.3, 1.06, -0.5)
left("tube", "scale_pine", "wing_l", points=[S - vec(0.06, 0.08, 0), S, (S + E) / 2 + vec(0, 0.02, -0.02), E], radius=0.075, radius_to=0.045,
     smooth=True, blend=0.06)
left("tube", "scale_pine", "wing_l", points=[E, (E + W) / 2 + vec(0.01, 0, -0.03), W], radius=0.045, radius_to=0.036, smooth=True, blend=0.03)
left("sphere", "scale_pine", "wingtip_l", at=W, radius=0.045, blend=0.02)
left("cone", "horn_bone", "wingtip_l", material="horn", aim=[W, W + vec(0.02, 0.11, 0.13)], radius=0.028)             # the thumb claw
for tip_pt in TIPS:
    bow = norm(np.cross(tip_pt - W, vec(1, 0, 0))) * 0.05
    left("tube", "scale_pine", "wingtip_l", points=[W, (W + tip_pt) / 2 + bow, tip_pt], radius=0.03, radius_to=0.011, smooth=True, blend=0.012)
MEMBRANE = 0.05 if BLOCKOUT else 0.016   # a draft's cells are three times coarser
skin = {"material": "membrane", "blend": 0.012, "density": 0.6, "gradient": {"from": "wing_wine", "to": "wing_ember", "steps": 12, "along": "x"}}
left("extrude", "wing_rust", "wingtip_l", **panel([W, TIPS[0], TIPS[1]], MEMBRANE, sag={1: 0.1}), **skin)
left("extrude", "wing_rust", "wingtip_l", **panel([W, TIPS[1], TIPS[2]], MEMBRANE, sag={1: 0.1}), **skin)
left("extrude", "wing_rust", "wing_l", **panel([W, TIPS[2], E], MEMBRANE), **skin)
left("extrude", "wing_rust", "wing_l", **panel([E, TIPS[2], FLANK], MEMBRANE, sag={1: 0.12}), **skin)
left("extrude", "wing_rust", "wing_l", **panel([E, FLANK, S], MEMBRANE), **skin)

# ------------------------------------------------------------------ the repeated parts along the back and the belly
def line_samples() -> list[tuple[np.ndarray, np.ndarray, float, str]]:
    """Points along the creature from the skull to the tail tip: (centre, direction towards the head, radius, bone)."""
    out: list[tuple[np.ndarray, np.ndarray, float, str]] = []
    for s in np.arange(NECK_LEN - 0.04, 0.12, -0.02):
        c, d = at_length(NECK, float(s))
        out.append((c, d, neck_r(s), "neck2" if s > NECK_HALF else "neck1"))
    for z in np.arange(0.36, -0.66, -0.02):
        out.append((vec(0, 0.95, z), vec(0, 0, 1), 0.38, "chest" if z > 0.05 else "body"))
    for s in np.arange(0.06, TAIL_LEN - 0.03, 0.02):
        c, d = at_length(TAIL, float(s))
        t = s / TAIL_LEN
        out.append((c, -d, tail_r(t), f"tail{sum(t >= cut for cut in TAIL_CUTS[:4])}"))
    return out


LINE = line_samples()
LINE_AT = lengths(np.array([c for c, _, _, _ in LINE]))


def spines() -> None:
    """A row of flat blades down the back, leaning towards the tail: small behind the skull, tallest over the withers."""
    s = 0.07
    while s < LINE_AT[-1] - 0.14:
        c, d, rad, bone = LINE[int(np.searchsorted(LINE_AT, s))]
        share = s / LINE_AT[-1]
        out = dorsal(d)
        size = 0.1 + 0.15 * math.sin(math.pi / 2 * share / 0.28) if share < 0.28 else 0.25 - 0.19 * ((share - 0.28) / 0.72) ** 0.8
        lean = norm(out * 0.8 - d * 0.6)
        add("lock", "wing_wine", bone, material="horn",
            points=[-out * 0.04 + d * size * 0.1, lean * size], width=size * 0.8, width_to=0, thickness=max(0.03, size * 0.19),
            thickness_to=0.014, facing=norm(np.cross(d, out)), gradient={"to": "wing_ember", "steps": 3},
            on={"part": SPINE_IDS, "near": tidy(c + out * (rad * 1.2 + 0.07)), "align": False})
        s += size * 0.68 + 0.02


def plates() -> None:
    """Belly plates from the throat to under the tail: lens-shaped scutes across the body, each one's rear edge over the next."""
    rough: list[tuple[np.ndarray, np.ndarray, float, str]] = []   # (a point just outside the surface, the way out, radius, bone)
    for k, (c, d, rad, bone) in enumerate(LINE):
        if bone in ("tail3", "tail4"):
            break
        if bone in ("chest", "body") and c[2] > 0.3:    # the chest's front is rounded by hand, below
            continue
        rough.append((c - dorsal(d) * (rad + 0.08), -dorsal(d), rad, bone))
        if bone == "neck1" and LINE[k + 1][3] == "chest":
            rough.append((vec(0, 0.7, 0.8), norm(vec(0, -0.6, 0.8)), 0.32, "chest"))
            rough.append((vec(0, 0.5, 0.6), norm(vec(0, -0.92, 0.4)), 0.36, "chest"))
    ventral = []
    for (p0, o0, r0, b0), (p1, o1, r1, _) in itertools.pairwise(rough):   # a sample every centimetre
        n = max(1, int(np.linalg.norm(p1 - p0) / 0.01))
        ventral += [(p0 + (p1 - p0) * k / n, norm(o0 + (o1 - o0) * k / n), r0 + (r1 - r0) * k / n, b0) for k in range(n)]
    acc = lengths(np.array([p for p, _, _, _ in ventral]))
    s = 0.04
    while s < acc[-1] - 0.04:
        i = int(np.searchsorted(acc, s))
        near, out, rad, bone = ventral[i]
        tailward = norm(ventral[min(i + 3, len(ventral) - 1)][0] - ventral[max(i - 3, 0)][0])
        long = 0.08 + rad * 0.2
        y_axis = norm(out - tailward * 0.17)    # the slab's own y axis: the way out, tipped so its tailward edge stands proud
        wide = rad * 0.78 if bone.startswith(("neck", "tail")) else min(0.36, rad * 0.9) - 0.4 * max(0.0, -0.25 - near[2])     # narrower under the hips
        # a scute: a lens across the body, its thin side edges sunk into the coat (a flat slab reads as a ladder)
        add("ellipsoid", "belly_cream", bone, material="plate", radii=[round(wide * 0.56, 4), 0.024, round(long * 0.6, 4)],
            rotate=[math.degrees(math.atan2(float(y_axis[2]), float(y_axis[1]))), 0, 0],
            density=1.6, on={"part": SPINE_IDS, "near": tidy(near), "align": False, "offset": -0.013})
        s += long * 0.52


if not BLOCKOUT:
    spines()
    plates()

# ------------------------------------------------------------------ the coat: relief scales, displaced so they break the outline
def coat(on: list[str], length: float, width: float, lift: float, flow, seed: int, displace: bool = True, fade: float = 0.06,
         pine: bool = True) -> list[dict]:
    """Scales on the parts in `on`, one layer per coat colour: each scale runs from its ground colour to a lighter tip."""
    grounds = [("scale_moss", "scale_fern"), ("scale_pine", "scale_moss")][: 2 if pine else 1]
    return [{"on": on, "on_colors": [ground], "kind": "scales", "length": length, "width": width, "lift": lift, "density": 1.6, "flow": flow,
             "jitter": 0.25, "under": 0.45, "color": ground, "color_to": tip, "displace": displace, "fade": fade, "seed": seed + k}
            for k, (ground, tip) in enumerate(grounds)]


LIMBS = ["foreleg_l", "foreleg_r", "forearm_l", "forearm_r", "thigh_l", "thigh_r", "shin_l", "shin_r"]
relief = [] if BLOCKOUT else [
    *coat(["chest", "body", "tail1", "tail2"], 0.075, 0.07, 0.009, [0, -0.35, -1], 3),
    *coat(["neck1", "neck2"], 0.06, 0.055, 0.007, "down", 5),
    *coat(LIMBS, 0.055, 0.05, 0.007, "down", 7, pine=False),
    *coat(["tail3", "tail4"], 0.04, 0.036, 0.005, "along", 9),
    *coat(["wing_l", "wing_r", "wingtip_l", "wingtip_r"], 0.04, 0.036, 0.005, "along", 13, displace=False)[1:],
    *coat(["head", "jaw"], 0.034, 0.032, 0.004, [0, -0.2, -1], 11, displace=False, fade=0.03),
    *coat(["forefoot_l", "forefoot_r", "hindfoot_l", "hindfoot_r"], 0.034, 0.032, 0.004, [0, -0.3, -1], 15, displace=False, pine=False),
]

# ------------------------------------------------------------------ rig
rig = {
    "body": {"pivot": [0, 0.9, -0.3]},
    "chest": {"pivot": [0, 0.95, 0.05], "parent": "body"},
    "neck1": {"pivot": tidy(NECK[0]), "parent": "chest"},
    "neck2": {"pivot": tidy(at_length(NECK, NECK_HALF)[0]), "parent": "neck1"},
    "head": {"pivot": tidy(NECK[-1]), "parent": "neck2"},
    "jaw": {"pivot": tidy(JAW_PIVOT), "parent": "head"},
    "eye_l": {"parent": "head"},
    "tail1": {"pivot": tidy(TAIL[0]), "parent": "body"},
    "foreleg_l": {"pivot": tidy(SHOULDER), "parent": "body"},     # not the chest: the feet stay planted while it breathes
    "forearm_l": {"pivot": tidy(ELBOW), "parent": "foreleg_l"},
    "forefoot_l": {"pivot": tidy(WRIST), "parent": "forearm_l"},
    "thigh_l": {"pivot": tidy(HIP), "parent": "body"},
    "shin_l": {"pivot": tidy(KNEE), "parent": "thigh_l"},
    "hindfoot_l": {"pivot": tidy(HOCK), "parent": "shin_l"},
    "wing_l": {"pivot": tidy(S), "parent": "chest"},
    "wingtip_l": {"pivot": tidy(W), "parent": "wing_l"},
}
for k in range(1, 4):
    rig[f"tail{k + 1}"] = {"pivot": tidy(at_length(TAIL, TAIL_CUTS[k] * TAIL_LEN)[0]), "parent": f"tail{k}"}

# ------------------------------------------------------------------ animations
def idle(frames: int = 24) -> list[dict]:
    """Breathing (the chest swells, the wings ride on it), a slow look to one side, a wave running down the tail."""
    poses = []
    for i in range(frames):
        ph = 2 * math.pi * i / frames
        breath = (1 - math.cos(ph)) / 2
        pose = {
            "chest": {"scale": tidy([1 + 0.02 * breath, 1 + 0.02 * breath, 1 + 0.006 * breath])},
            "neck1": turn(-1.6 * breath, 2.0 * math.sin(ph)),
            "neck2": turn(-1.0 * breath, 2.5 * math.sin(ph)),
            "head": turn(1.5 * breath, 3.0 * math.sin(ph - 0.5)),
            "jaw": turn(2.5 * breath),
            "wing_l": turn(0, 0, 3.0 * breath), "wing_r": turn(0, 0, -3.0 * breath),
            "wingtip_l": turn(0, 0, 2.0 * breath), "wingtip_r": turn(0, 0, -2.0 * breath),
        }
        for k in range(4):
            pose[f"tail{k + 1}"] = turn(0, (3 + 2.5 * k) * math.sin(ph - 0.7 * k))
        poses.append(pose)
    return poses


def roar() -> list[dict]:
    """Draws back, then throws the head up with the jaw wide and the wings thrown open; the tail lifts behind it."""
    crouch = {"chest": [4, 0, 0], "neck1": [12, 0, 0], "neck2": [8, 0, 0], "head": [6, 0, 0], "wing_l": [0, 0, -8], "wing_r": [0, 0, 8],
              "tail1": [-4, 0, 0]}
    shout = {"chest": [-6, 0, 0], "neck1": [-20, 0, 0], "neck2": [-16, 0, 0], "head": [-16, 0, 0], "jaw": [30, 0, 0],
             "wing_l": [-10, -12, 26], "wing_r": [-10, 12, -26], "wingtip_l": [0, 0, 16], "wingtip_r": [0, 0, -16],
             "tail1": [9, 0, 0], "tail2": [9, -6, 0], "tail3": [8, -8, 0], "tail4": [8, -10, 0]}
    shake_a = {**shout, "head": [-17, 5, 3], "jaw": [33, 0, 0], "neck2": [-16, 4, 0]}
    shake_b = {**shout, "head": [-15, -5, -3], "jaw": [31, 0, 0], "neck2": [-16, -4, 0]}
    return keyed([(0, {}), (4, crouch), (8, shout), (10, shake_a), (12, shake_b), (14, shake_a), (16, shout), (22, {})], 23)


animations = {
    "idle": {"fps": 8, "poses": idle()},
    "roar": {"fps": 10, "loop": False, "poses": roar()},
}

fields = {
    "tags": ["hero", "showpiece"], "style_version": 1, "budget": 74000, "resolution": 0.006, "max_cells": 560, "origin": "ground",
    "rig": rig, "skin": "soft", "animations": animations,
}
if relief:
    fields["normal_map"] = 1024 if QUICK else 2048
    fields["relief"] = relief

out = Path(__file__).with_name("dragon.kiln.yaml")
data = model("dragon", parts, cls="creature", description="forest dragon, 1.7 m at the head: scale coat, belly plates, back spines, half-open wings",
             **fields)
write_model(out, data)
out.write_text("# Generated by models/dragon.py: edit that and run it again.\n" + out.read_text(encoding="utf-8"), encoding="utf-8")
print(f"wrote {out.name}: {len(parts)} parts")
