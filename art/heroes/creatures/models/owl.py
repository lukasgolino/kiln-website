"""Generates owl.kiln.yaml: a great horned owl perched on a mossy log.

Run from the project folder:  python models/owl.py [--blockout] [--quick]

The owl is a few blended shapes; its small plumage (breast, back, head) is relief in the baked maps. The feathers
that make the silhouette are parts written here in rows: wing coverts over secondaries over primaries, a tail fan,
ear tufts, a skirt over the legs. `--blockout` leaves the rows and the relief out, for `kiln preview owl --draft`; `--quick` bakes 1024 maps instead of 2048.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen import P, keyed, matrix, norm, tidy, vec
from kiln.api import model, write_model

BLOCKOUT = "--blockout" in sys.argv
QUICK = "--quick" in sys.argv
rng = random.Random(11)
parts: list[dict] = []
STILL = ("log", "feet")


def add(shape: str, color: str | None = None, id: str | None = None, **kw) -> dict:
    if id in STILL and not kw.get("cut") and not kw.get("keep"):
        kw["skin_falloff"] = 0      # the perch and the feet on it never follow a wing or the tail that hangs near them
    parts.append(P(shape, color, id, **kw))
    return parts[-1]


def left(shape: str, color: str | None, id: str, **kw) -> dict:
    """A part of the left side (+x) whose mirror image is the right side's own part (`wing_l` -> `wing_r`)."""
    return add(shape, color, id, mirror="x", mirror_id=id[:-2] + "_r", **kw)


# ------------------------------------------------------------------ the log
LOG_R, LOG_Y = 0.085, 0.083


def on_log(x: float, degrees: float, out: float = 0.0) -> np.ndarray:
    """A point `out` metres off the log's bark: `degrees` round it from the top (positive: to the front)."""
    a = math.radians(degrees)
    return vec(x, LOG_Y + (LOG_R + out) * math.cos(a), (LOG_R + out) * math.sin(a))


add("cylinder", "bark", "log", material="bark", at=[0, LOG_Y, 0], rotate=[0, 0, 90], radius=LOG_R, height=0.62, round=0.012,
    noise={"amount": 0.005, "scale": 0.035, "seed": 4})
add("cylinder", "heartwood", "log", material="bark", at=[0, LOG_Y, 0], rotate=[0, 0, 90], radius=LOG_R - 0.014, height=0.628, round=0.004)
for ring_r in (0.022, 0.046):   # growth rings on the cut ends
    add("torus", "bark", "log", material="bark", at=[0.314, LOG_Y, 0], rotate=[0, 0, 90], radius=ring_r, thickness=0.0035, mirror="x")
add("capsule", "bark", "log", material="bark", from_=on_log(-0.2, -50, -0.02), to=on_log(-0.26, -62, 0.07), radius=0.024, radius_to=0.02,
    blend=0.015, noise={"amount": 0.003, "scale": 0.02, "seed": 2})                                                      # a broken stub
add("ellipsoid", "heartwood", "log", material="bark", at=on_log(-0.264, -62, 0.084), radii=[0.014, 0.014, 0.014])
# moss cushions and two mushrooms
for x, deg, rad, seed in [(-0.19, 12, (0.085, 0.022, 0.06), 1), (0.2, -20, (0.07, 0.02, 0.055), 2), (0.14, 62, (0.06, 0.018, 0.04), 3),
                          (-0.06, 75, (0.05, 0.016, 0.035), 4), (-0.27, 48, (0.035, 0.016, 0.04), 5), (0.27, 30, (0.03, 0.015, 0.04), 6)]:
    add("ellipsoid", "moss", "log", material="moss", at=on_log(x, deg, 0.004), radii=rad, rotate=[deg, 0, 0], blend=0.012, blend_to=["log"],
        color_blend=0.008, noise={"amount": 0.004, "scale": 0.014, "seed": seed})
for x, deg, tall, cap in [(-0.235, 28, 0.045, 0.024), (-0.265, 14, 0.028, 0.016)]:
    foot, top = on_log(x, deg, -0.004), on_log(x, deg, tall)
    add("capsule", "stem_cream", "log", from_=foot, to=top, radius=cap * 0.26, radius_to=cap * 0.2)
    add("ellipsoid", "cap_red", "log", at=top + vec(0, cap * 0.1, 0), radii=[cap, cap * 0.55, cap], rotate=[deg * 0.5, 0, 0])

# ------------------------------------------------------------------ body and head
PERCH = LOG_Y + LOG_R                       # the top of the log
BODY = vec(0, PERCH + 0.185, -0.012)
HEAD = vec(0, PERCH + 0.385, 0.01)
add("ellipsoid", "feather_brown", "body", material="feather", at=BODY, radii=[0.128, 0.16, 0.115], rotate=[-6, 0, 0])
add("ellipsoid", "feather_buff", "body", material="feather", at=BODY + vec(0, -0.012, 0.042), radii=[0.108, 0.14, 0.09], blend=0.03,
    color_blend=0.018)                                                                                                    # breast
add("ellipsoid", "feather_brown", "head", material="feather", at=HEAD, radii=[0.118, 0.092, 0.1], blend=0.035, density=2)
add("ellipsoid", "feather_cream", "body", material="feather", at=HEAD + vec(0, -0.095, 0.068), radii=[0.07, 0.026, 0.036], blend=0.02,
    color_blend=0.012)                                                                                                    # the white throat
# the facial disc: two shallow dishes, a dark bracket round each one's outer edge
DISC = HEAD + vec(0.052, -0.004, 0.072)
DISC_YAW = 22
add("ellipsoid", "disc_russet", "head", material="feather", at=DISC, radii=[0.058, 0.062, 0.032], rotate=[0, DISC_YAW, 0], blend=0.012,
    color_blend=0.008, mirror="x", density=2)
yaw = math.radians(DISC_YAW)
across, facing = vec(math.cos(yaw), 0, -math.sin(yaw)), vec(math.sin(yaw), 0, math.cos(yaw))
rim = [DISC + (across * math.cos(math.radians(a)) * 0.059 + vec(0, 1, 0) * math.sin(math.radians(a)) * 0.063) + facing * 0.012
       for a in range(118, -100, -24)]
add("tube", "disc_rim", "head", material="feather", points=rim, radius=0.0085, radius_to=0.006, smooth=True, blend=0.006, mirror="x")
add("lock", "feather_cream", "head", material="feather", points=[HEAD + vec(0.004, 0.014, 0.103), HEAD + vec(0.045, 0.056, 0.094), HEAD + vec(0.09, 0.074, 0.066)],
    width=0.024, width_to=0.014, thickness=0.012, thickness_to=0.008, facing=[0, 0.5, 1], smooth=True, blend=0.006, mirror="x")   # brows
add("ellipsoid", "feather_cream", "head", material="feather", at=HEAD + vec(0.019, -0.034, 0.1), radii=[0.022, 0.018, 0.015], blend=0.008,
    mirror="x")                                                                                                           # bristles by the beak
# eyes: a gold ball in a socket, a big pupil, a glint; lids are their own bones (they close in the blink)
EYE = HEAD + vec(0.05, 0.002, 0.083)
EYE_FACE = norm(vec(0.12, 0, 1))
EYE_R = 0.027
add("sphere", "disc_rim", None, at=EYE + EYE_FACE * 0.004, radius=EYE_R + 0.0015, cut=True, mirror="x")
add("sphere", "eye_gold", "head", material="eye", at=EYE, radius=EYE_R, mirror="x", keep=True)
add("ellipsoid", "ink", "head", material="eye", at=EYE + EYE_FACE * (EYE_R - 0.0075), radii=[0.0138, 0.0138, 0.009], rotate=[0, 7, 0],
    mirror="x", keep=True)
add("sphere", "ivory", "head", material="eye", at=EYE + EYE_FACE * (EYE_R + 0.0005) + vec(0.006, 0.007, 0), radius=0.0032, mirror="x", keep=True)
left("sphere", "disc_russet", "lid_l", material="feather", at=EYE, radius=EYE_R + 0.0028)
LID_REST = math.radians(-50)             # the lids are the top half of a ball round each eye, tipped back: a hooded stare
lid_cut = P("box", None, None, at=EYE + vec(0, -0.03 * math.cos(LID_REST), -0.03 * math.sin(LID_REST)), size=[0.07, 0.06, 0.07],
            rotate=[math.degrees(LID_REST), 0, 0], cut=True, mirror="x")
lid_cut["cut"] = ["lid_l", "lid_r"]     # the box takes the lower half off the lids only
parts.append(lid_cut)
# beak: hooked, dark
add("tube", "beak_slate", "head", material="claw", points=[HEAD + vec(0, 0.002, 0.097), HEAD + vec(0, -0.016, 0.124), HEAD + vec(0, -0.04, 0.122),
                                                           HEAD + vec(0, -0.05, 0.112)],
    radius=0.0175, radius_to=0.003, smooth=True, scale=[0.8, 1, 1])
# ear tufts: two broad feathers a side, the front one over the back one (their own bones: they twitch)
for dx, dz, long, col, tip_col in [(0.012, -0.012, 0.07, "feather_brown", "feather_tawny"), (0.0, 0.004, 0.086, "feather_umber", "feather_brown")]:
    root = HEAD + vec(0.07 + dx, 0.058, 0.01 + dz)
    tip = root + vec(0.05 + dx, long, -0.02 + dz)
    left("lock", col, "tuft_l", material="feather", points=[root - vec(0.006, 0.022, 0), (root + tip) / 2 + vec(0.014, 0, 0.004), tip], width=0.06,
         width_to=0.018, thickness=0.014, thickness_to=0.007, facing=[-0.3, 0.1, 1], smooth=True, blend=0.012, blend_to=["head"],
         gradient={"to": tip_col, "steps": 3})

# ------------------------------------------------------------------ legs and feet: toes round the log, talons dug in
FOOT_X = 0.058
add("capsule", "feather_buff", "body", material="feather", from_=vec(FOOT_X, PERCH + 0.1, 0.012), to=vec(FOOT_X, PERCH + 0.024, 0.006),
    radius=0.036, radius_to=0.026, blend=0.02, mirror="x")
for dx, a0, a1 in [(-0.024, 6, 44), (0.0, 6, 49), (0.027, 3, 40), (0.006, -5, -40)]:     # x offset at the tip, start and end angle round the log
    pts = [on_log(FOOT_X + dx * t, a0 + (a1 - a0) * t, 0.0085 + 0.004 * math.sin(math.pi * t)) for t in (0, 0.35, 0.7, 1)]
    add("tube", "toe_grey", "feet", points=pts, radius=0.012, radius_to=0.0095, smooth=True, blend=0.004, mirror="x")
    step = 1 if a1 > a0 else -1
    claw = [on_log(FOOT_X + dx, a1 - step * 3, 0.0095), on_log(FOOT_X + dx * 1.1, a1 + step * 10, 0.013), on_log(FOOT_X + dx * 1.15, a1 + step * 23, 0.001)]
    add("tube", "claw", "feet", material="claw", points=claw, radius=0.008, radius_to=0.0015, smooth=True, mirror="x", keep=True)

# ------------------------------------------------------------------ wings, folded: rows of feathers over a pad
# (the pad is turned to lie round the side and back of the body; everything on it is written in its own frame)
WING_C, WING_RAD, WING_TURN = BODY + vec(0.112, 0.0, -0.038), vec(0.036, 0.15, 0.094), [0, 25, 8]
WING_M = matrix(WING_TURN)
SHOULDER = BODY + vec(0.09, 0.12, -0.01)
WRIST = WING_C + WING_M @ vec(0.02, -0.03, 0.0)
WING_TIP = WING_C + WING_M @ vec(-0.01, -0.31, -0.07)      # where the long feathers gather
left("ellipsoid", "feather_brown", "wing_l", material="feather", at=WING_C, radii=WING_RAD, rotate=WING_TURN)
left("ellipsoid", "feather_buff", "wing_l", material="feather", at=WING_C - WING_M @ vec(0.012, 0, 0), radii=WING_RAD * vec(1, 0.9, 0.88),
     rotate=WING_TURN)                                                                                       # the pale underwing


def on_wing(y: float, z: float) -> tuple[np.ndarray, np.ndarray]:
    """The point of the wing pad's outer face at height y and depth z (shares of its radii, -1..1) and the way out there."""
    y, z = y * 0.96, z * 0.96
    q = vec(math.sqrt(max(1e-4, 1 - y * y - z * z)), y, z)
    return WING_C + WING_M @ (q * WING_RAD), WING_M @ norm(q / WING_RAD)


def feather(root: np.ndarray, out: np.ndarray, along: np.ndarray, length: float, width: float, bone: str, col: str, tip_col: str,
            lift: float = 0.011, thick: float = 0.009) -> None:
    """One feather lying on the wing: its root sunk, its tip standing a little proud, so each row lies over the next."""
    along = norm(along - out * float(along @ out) * 0.6)
    pts = [root - out * 0.005 - along * length * 0.12, root + along * length * 0.5 + out * lift * 0.75, root + along * length + out * lift]
    left("lock", col, bone, material="feather", points=pts, width=width, width_to=width * 0.45, thickness=thick, thickness_to=thick * 0.6,
         facing=out, smooth=True, gradient={"to": tip_col, "steps": 3})


if not BLOCKOUT:
    ROWS = [  # height on the pad, feathers, length, bone: coverts, then secondaries, then primaries
        (0.74, 4, 0.058, "wing_l"), (0.5, 5, 0.068, "wing_l"), (0.24, 5, 0.078, "wing_l"), (-0.04, 5, 0.092, "wing_l"),
        (-0.3, 5, 0.12, "wingtip_l"), (-0.54, 4, 0.15, "wingtip_l"),
    ]
    for row, (y, count, length, bone) in enumerate(ROWS):
        reach = math.sqrt(1 - (y * 0.96) ** 2) * 0.84
        col, tip_col = [("feather_brown", "feather_buff"), ("feather_umber", "feather_tawny")][row % 2]
        for k in range(count):
            root, out = on_wing(y, reach * (1 - 2 * (k + 0.5) / count))
            along = norm(WING_TIP - root) * 0.6 + WING_M @ vec(0, -1, -0.15) * 0.4      # down and back, gathering to the tip
            feather(root, out, along, length * rng.uniform(0.94, 1.06), 0.047, bone, col, tip_col)
    for k in range(6):          # small coverts down the wing's leading edge, so it shows feathers from the front too
        y = 0.72 - 0.24 * k
        root, out = on_wing(y, math.sqrt(1 - (y * 0.96) ** 2) * 0.9)
        feather(root, out, WING_M @ vec(0, -1, -0.45), 0.055, 0.04, "wing_l", "feather_brown", "feather_buff", lift=0.008)

# ------------------------------------------------------------------ tail fan and the skirt of feathers over the legs
TAIL_ROOT = BODY + vec(0, -0.115, -0.08)
if not BLOCKOUT:
    for k in range(5):
        f = (k - 2) / 2
        tip = TAIL_ROOT + vec(f * 0.07, -0.155 + abs(f) * 0.02, -0.075 - abs(f) * 0.008)
        add("lock", "feather_umber", "tail", material="feather", points=[TAIL_ROOT + vec(f * 0.02, 0.05, 0.05), (TAIL_ROOT + tip) / 2 + vec(0, 0, -0.01), tip],
            width=0.042, width_to=0.028, thickness=0.011, thickness_to=0.007, facing=[f * 0.4, -0.45, -1], smooth=True, blend=0.006,
            blend_to=["body"], gradient={"to": "feather_tawny", "steps": 4})
    for k in range(7):                      # the skirt: broad breast feathers hanging over the tops of the legs
        a = math.radians(-63 + 21 * k)
        out = vec(math.sin(a), 0, math.cos(a))
        root = BODY + vec(out[0] * 0.1, -0.085, 0.034 + out[2] * 0.08)
        tip = root + vec(out[0] * 0.01, -0.062 * rng.uniform(0.85, 1.12), out[2] * 0.01)
        add("lock", "feather_buff", "skirt", material="feather", points=[root + vec(0, 0.02, 0) - out * 0.012, (root + tip) / 2 + out * 0.008, tip],
            width=0.062, width_to=0.02, thickness=0.016, thickness_to=0.007, facing=out, smooth=True, blend=0.012, blend_to=["body"],
            gradient={"to": "feather_tawny", "steps": 3})
else:
    add("lock", "feather_umber", "tail", material="feather", points=[TAIL_ROOT, TAIL_ROOT + vec(0, -0.155, -0.075)], width=0.1, width_to=0.14,
        thickness=0.03, thickness_to=0.03, facing=[0, -0.45, -1])

# ------------------------------------------------------------------ plumage: relief feathers, bark, moss
relief = [] if BLOCKOUT else [
    {"on": ["body"], "on_colors": ["feather_buff"], "kind": "feathers", "length": 0.034, "width": 0.03, "lift": 0.004, "density": 1.7,
     "flow": "down", "jitter": 0.3, "under": 0.4, "color": "feather_cream", "color_to": "feather_brown", "displace": True, "fade": 0.02, "seed": 2},
    {"on": ["body", "head"], "on_colors": ["feather_cream"], "kind": "feathers", "length": 0.02, "width": 0.016, "lift": 0.0025, "density": 1.6,
     "flow": "down", "under": 0.3, "fade": 0.012, "seed": 3},
    {"on": ["body"], "on_colors": ["feather_brown"], "kind": "feathers", "length": 0.036, "width": 0.03,
     "lift": 0.004, "density": 1.7, "flow": "down", "jitter": 0.3, "under": 0.45, "color": "feather_umber", "color_to": "feather_tawny",
     "displace": True, "seed": 4},
    {"on": ["head"], "on_colors": ["feather_brown"], "kind": "feathers", "length": 0.022, "width": 0.018, "lift": 0.003, "density": 1.7,
     "flow": [0, -0.6, -1], "jitter": 0.3, "under": 0.45, "color": "feather_umber", "color_to": "feather_tawny", "displace": True, "seed": 5},
    {"on": ["head"], "on_colors": ["disc_russet"], "kind": "fur", "length": 0.018, "width": 0.01, "lift": 0.0015, "density": 1.5,
     "flow": [0, -0.3, 1], "tips": 2, "under": 0.25, "fade": 0.01, "seed": 6},
    {"on": ["log"], "on_colors": ["bark"], "kind": "shingles", "length": 0.05, "width": 0.022, "lift": 0.004, "density": 1.3, "flow": [1, 0, 0],
     "jitter": 0.5, "under": 0.5, "color": "bark", "color_to": "bark_dark", "displace": True, "seed": 7},
    {"on": ["log"], "on_colors": ["moss"], "kind": "fur", "length": 0.014, "width": 0.01, "lift": 0.003, "density": 2.0, "flow": "up",
     "jitter": 0.6, "under": 0.35, "color": "moss", "color_to": "moss_light", "displace": True, "fade": 0.008, "seed": 8},
]

# ------------------------------------------------------------------ rig
rig = {
    "log": {"pivot": [0, 0, 0]},
    "feet": {"pivot": [0, tidy(PERCH), 0]},
    "body": {"pivot": [0, tidy(PERCH + 0.02), 0]},
    "head": {"pivot": tidy(HEAD + vec(0, -0.08, -0.01)), "parent": "body"},
    "lid_l": {"pivot": tidy(EYE), "parent": "head", "separate": True},
    "tuft_l": {"pivot": tidy(HEAD + vec(0.072, 0.06, 0.01)), "parent": "head"},
    "skirt": {"pivot": tidy(BODY + vec(0, -0.07, 0.03)), "parent": "body"},
    "wing_l": {"pivot": tidy(SHOULDER), "parent": "body", "separate": True},        # rigid pieces lying over the body: opening
    "wingtip_l": {"pivot": tidy(WRIST), "parent": "wing_l", "separate": True},     # them stretches no skin
    "tail": {"pivot": tidy(TAIL_ROOT), "parent": "body"},
}

# ------------------------------------------------------------------ animations
def idle(frames: int = 40) -> list[dict]:
    """Sits breathing; turns its head far to one side, holds, comes back; blinks; an ear tuft twitches."""
    look = {"head": [4, 62, 5], "tuft_l": [0, 0, -5], "tuft_r": [0, 0, 5]}
    shut = {"lid_l": [66, 0, 0], "lid_r": [66, 0, 0]}
    poses = keyed([(0, {}), (4, {}), (9, look), (11, {**look, **shut}), (13, look), (20, look), (25, {}), (29, {}), (30, shut), (32, {}),
                   (35, {"tuft_l": [0, 0, -9]}), (37, {}), (39, {})], frames)
    for i, pose in enumerate(poses):
        breath = (1 - math.cos(4 * math.pi * i / frames)) / 2
        pose["body"] = {"scale": tidy([1 + 0.016 * breath, 1 + 0.008 * breath, 1 + 0.02 * breath])}
    return poses


def flap() -> list[dict]:
    """Leans in, lifts and opens both wings, beats them three times and folds them away again."""
    up = {"body": [9, 0, 0], "head": [-8, 0, 0], "wing_l": [-18, -10, 82], "wing_r": [-18, 10, -82], "wingtip_l": [0, 0, 42],
          "wingtip_r": [0, 0, -42], "tail": [-12, 0, 0]}
    down = {"body": [3, 0, 0], "head": [-3, 0, 0], "wing_l": [14, 6, 30], "wing_r": [14, -6, -30], "wingtip_l": [0, 0, 8],
            "wingtip_r": [0, 0, -8], "tail": [6, 0, 0]}
    return keyed([(0, {}), (3, up), (5, down), (7, up), (9, down), (11, up), (13, down), (17, {})], 18)


animations = {
    "idle": {"fps": 8, "poses": idle()},
    "flap": {"fps": 12, "loop": False, "poses": flap()},
}

if BLOCKOUT:     # the block-out has no feather rows: no bones or clips for them
    for gone in ("wingtip_l", "skirt"):
        rig.pop(gone)
    animations = {}

fields = {
    "tags": ["hero", "showpiece"], "style_version": 1, "budget": 60000, "resolution": 0.0024, "max_cells": 400, "origin": "ground",
    "rig": rig, "skin": "soft", "animations": animations,
}
if relief:
    fields["normal_map"] = 1024 if QUICK else 2048
    fields["relief"] = relief

out = Path(__file__).with_name("owl.kiln.yaml")
data = model("owl", parts, cls="creature", description="great horned owl on a mossy log, 0.7 m: layered wing and tail feathers, ear tufts, gripping talons",
             **fields)
write_model(out, data)
out.write_text("# Generated by models/owl.py: edit that and run it again.\n" + out.read_text(encoding="utf-8"), encoding="utf-8")
print(f"wrote {out.name}: {len(parts)} parts")
