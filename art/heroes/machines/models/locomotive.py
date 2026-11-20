"""Generates locomotive.kiln.yaml: a narrow-gauge side-tank engine, 3.2 m over the buffers, on a length of track.

Run from the project folder:  python models/locomotive.py [--blockout]

Everything machined is a hard part. The hardware (rivet rows, bolt rings, bands, planks) is KILN's own notation; this
script places it, and works out the running gear: where each crank pin is at every frame, how far the crossheads slide
and how the connecting rods tilt, written out as the `run` animation. `--blockout` leaves the rivets and lining out.

Each group of parts has its own id (a bone of the rigid skin, `union: per_bone`), so it is joined as its own solid:
the boiler doesn't have to be cut again for every rivet that sits on it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen import P, arc, circle, lettering, plate_x, plate_z, r4, rrect  # noqa: E402

from kiln.api import model, write_model  # noqa: E402

BLOCKOUT = "--blockout" in sys.argv
parts: list[dict[str, Any]] = []


def add(shape: str, color: str | None = None, material: str | None = None, id: str | None = None, **kw: Any) -> None:  # noqa: A002
    parts.append(P(shape, color, material, id, **kw))


def rod(a: list[float], b: list[float], radius: float, color: str, material: str, id: str, sides: int = 10, **kw: Any) -> None:  # noqa: A002
    """A round bar from a to b."""
    add("cylinder", color, material, id, radius=radius, sides=sides, aim=[a, b], **kw)


def turned(a: list[float], b: list[float], radius: float, color: str, material: str, id: str, sides: int = 16, bevel: float = 0.0, **kw: Any) -> None:  # noqa: A002
    """A turned disc or drum from a to b with rounded rims: a lathe, whose bevel costs a ring of faces, not a cylinder's."""
    h = math.dist(a, b) / 2
    extra = {"bevel": bevel} if bevel else {}
    add("lathe", color, material, id, profile=[(0, -h), (radius, -h), (radius, h), (0, h)], sides=sides, aim=[a, b], **extra, **kw)


def rivets(color: str, material: str, id: str, count: int, size: float = 0.022, **kw: Any) -> None:  # noqa: A002
    if not BLOCKOUT:
        add("rivets", color, material, id, count=count, size=size, **kw)


# --- the numbers everything hangs on -----------------------------------------------------------------------------------

RAIL_TOP = 0.20
WHEEL_R = 0.29
AXLE_Y = RAIL_TOP + WHEEL_R
AXLES = (0.66, 0.0, -0.66)  # front, driven, rear
CRANK = 0.12
PIN_L, PIN_R = -35.0, 55.0  # the cranks at rest (degrees: 0 forward, 90 up); the right side leads by a quarter turn
ROD_X, CON_X, CYL_X = 0.43, 0.462, 0.50  # coupling rods, connecting rods, cylinder centre lines
CON_LEN = 0.72
FOOT = 0.87  # top of the footplate
BOILER_Y, BOILER_R, SMOKE_R = 1.30, 0.34, 0.365
TANK_TOP, HALF = 1.44, 0.66
ROOF_R, ROOF_CY = 1.95, 0.18  # the cab roof's arc


def pin(angle: float) -> tuple[float, float]:
    """A crank pin's (y, z) from its axle."""
    return CRANK * math.sin(math.radians(angle)), CRANK * math.cos(math.radians(angle))


def crosshead_z(angle: float) -> float:
    py, pz = pin(angle)
    return pz + math.sqrt(CON_LEN**2 - py**2)


def roof_y(x: float, r: float = ROOF_R) -> float:
    return ROOF_CY + math.sqrt(r * r - x * x)


# --- track -------------------------------------------------------------------------------------------------------------

add("box", "ballast", "stone", at=[0, 0.02, 0], size=[1.95, 0.04, 3.9], round=0.02, noise={"amount": 0.01, "scale": 0.05, "seed": 4})
add("box", "ballast", "stone", at=[0, 0.06, 0], size=[1.55, 0.07, 3.82], round=0.035, blend=0.04, noise={"amount": 0.016, "scale": 0.045, "seed": 7})
add("box", "wood_dark", "wood", "track", at=[0, 0.095, -1.7], size=[1.3, 0.07, 0.18], chamfer=0.012, bevel_edges="top", array={"count": 11, "step": [0, 0, 0.34]})
RAIL = [(-0.055, 0), (0.055, 0), (0.055, 0.01), (0.012, 0.02), (0.012, 0.048), (0.026, 0.055), (0.026, 0.075), (-0.026, 0.075), (-0.026, 0.055),
        (-0.012, 0.048), (-0.012, 0.02), (-0.055, 0.01)]  # fmt: skip
parts.append(plate_z([(0.325 + u, 0.125 + v) for u, v in RAIL], 0, 3.8, "iron", "steel", "track", mirror="x"))
add("box", "iron_dark", "iron", "spikes", at=[0.325, 0.133, -1.7], size=[0.17, 0.012, 0.1], array={"count": 11, "step": [0, 0, 0.34]}, mirror="x")

# --- wheels: an axle, two wheels, their crank pins and balance weights ---------------------------------------------

TYRE = [(0.258, -0.045), (0.284, -0.045), (0.29, -0.038), (0.29, 0.04), (0.318, 0.047), (0.318, 0.065), (0.258, 0.065)]  # (radius, inwards)
for i, z in enumerate(AXLES):
    wid = f"wheel{i + 1}"
    rod([-0.37, AXLE_Y, z], [0.37, AXLE_Y, z], 0.04, "iron", "iron", wid, sides=12)
    add("lathe", "steel", "steel", wid, at=[0.345, AXLE_Y, z], rotate=[0, 0, 90], profile=TYRE, sides=32, mirror="x")
    add("lathe", "red", "paint", wid, at=[0.345, AXLE_Y, z], rotate=[0, 0, 90], sides=32, mirror="x",
        profile=[(0.212, -0.034), (0.262, -0.034), (0.262, 0.04), (0.212, 0.04)])  # fmt: skip
    turned([0.295, AXLE_Y, z], [0.405, AXLE_Y, z], 0.075, "red", "paint", wid, sides=16, bevel=0.012, mirror="x")
    add("cylinder", "steel_bright", "steel", wid, at=[0.408, AXLE_Y, z], rotate=[0, 0, 90], radius=0.036, height=0.012, sides=12, mirror="x")
    add("cone", "red", "paint", wid, at=[0.35, AXLE_Y + 0.142, z], radius=0.025, radius_top=0.018, height=0.16, sides=6, mirror="x",
        array={"count": 10, "around": "x", "center": [0.35, AXLE_Y, z]})  # fmt: skip
    for side, rest in ((1, PIN_L), (-1, PIN_R)):
        py, pz = pin(rest)
        reach = 0.497 if i == 1 else 0.452  # the driven axle's pins also carry the connecting rods
        weight = [(z + r * math.cos(math.radians(a)), AXLE_Y + r * math.sin(math.radians(a)))
                  for r, span in ((0.215, range(-52, 53, 13)), (0.1, range(52, -53, -26))) for a in (rest + 180 + s for s in span)]  # fmt: skip
        parts.append(plate_x([(wz, wy) for wz, wy in weight], side * 0.352, 0.066, "red", "paint", wid))
        rod([side * 0.385, AXLE_Y + py, z + pz], [side * 0.412, AXLE_Y + py, z + pz], 0.05, "red", "paint", wid, sides=12)
        rod([side * 0.4, AXLE_Y + py, z + pz], [side * reach, AXLE_Y + py, z + pz], 0.021, "steel_bright", "steel", wid)
        rod([side * (reach - 0.002), AXLE_Y + py, z + pz], [side * (reach + 0.012), AXLE_Y + py, z + pz], 0.034, "brass", "brass", wid, sides=6)

# --- coupling rods, connecting rods, crossheads ------------------------------------------------------------------

for side, rest, s in ((1, PIN_L, "l"), (-1, PIN_R, "r")):
    py, pz = pin(rest)
    y = AXLE_Y + py
    add("box", "steel", "steel", f"rod_{s}", at=[side * ROD_X, y, pz], size=[0.024, 0.05, 1.32], chamfer=0.007)
    add("box", "steel_bright", "steel", f"rod_{s}", at=[side * (ROD_X + 0.012), y, pz], size=[0.006, 0.022, 1.14])
    for z in AXLES:
        turned([side * (ROD_X - 0.015), y, z + pz], [side * (ROD_X + 0.015), y, z + pz], 0.052, "steel", "steel", f"rod_{s}", sides=14, bevel=0.006)
        rod([side * (ROD_X - 0.017), y, z + pz], [side * (ROD_X + 0.017), y, z + pz], 0.033, "brass", "brass", f"rod_{s}", sides=10)
    zc = crosshead_z(rest)
    big, small = [side * CON_X, y, pz], [side * CON_X, AXLE_Y, zc]
    add("box", "steel", "steel", f"conrod_{s}", size=[0.022, CON_LEN, 0.046], chamfer=0.007, aim=[small, big])
    for at, radius in ((big, 0.056), (small, 0.04)):
        turned([at[0] - 0.015, at[1], at[2]], [at[0] + 0.015, at[1], at[2]], radius, "steel", "steel", f"conrod_{s}", sides=14, bevel=0.006)
        rod([at[0] - 0.017, at[1], at[2]], [at[0] + 0.017, at[1], at[2]], radius * 0.62, "brass", "brass", f"conrod_{s}", sides=10)
    add("box", "steel_bright", "steel", f"cross_{s}", at=[side * 0.508, AXLE_Y, zc], size=[0.06, 0.134, 0.11], chamfer=0.01, bevel_edges="vertical")
    rod([side * 0.444, AXLE_Y, zc], [side * 0.546, AXLE_Y, zc], 0.019, "iron", "steel", f"cross_{s}")
    rod([side * CYL_X, AXLE_Y, zc + 0.05], [side * CYL_X, AXLE_Y, zc + 0.42], 0.016, "steel_bright", "steel", f"cross_{s}")

# --- frames, footplate, buffer beams -----------------------------------------------------------------------------

C = "chassis"
add("box", "iron_dark", "iron", C, at=[0.24, 0.63, 0], size=[0.03, 0.42, 2.86], mirror="x")
add("box", "iron_dark", "iron", C, at=[0, FOOT - 0.015, 0], size=[1.34, 0.03, 2.94])
add("box", "iron_dark", "iron", C, at=[HALF - 0.01, FOOT - 0.07, 0], size=[0.02, 0.09, 2.94], mirror="x")
add("box", "soot", "iron", C, at=[0, 0.62, -0.42], size=[0.45, 0.42, 0.62])  # ashpan under the firebox
add("box", "iron_dark", "iron", C, at=[0, 0.66, 0.34], size=[0.45, 0.1, 0.2], array={"count": 2, "step": [0, 0, 0.66]})  # stretchers
add("box", "iron_dark", "iron", C, at=[0, 1.0, 1.09], size=[0.5, 0.3, 0.4], chamfer=0.02, bevel_edges="vertical")  # smokebox saddle
for z in (1.487, -1.487):
    add("box", "red", "paint", C, at=[0, 0.7, z], size=[1.36, 0.26, 0.07], chamfer=0.012)
for z in AXLES:  # axleboxes and their springs, seen between the spokes
    add("box", "iron", "iron", C, at=[0.262, AXLE_Y, z], size=[0.03, 0.2, 0.2], mirror="x")
    add("box", "iron", "iron", C, at=[0.265, AXLE_Y + 0.2, z], size=[0.03, 0.035, 0.44], mirror="x")
add("box", "iron_dark", "iron", C, at=[0.325, 0.42, 1.5], size=[0.016, 0.32, 0.04], mirror="x")  # guard irons
# cab steps
add("box", "iron_dark", "iron", C, at=[0.645, 0.62, -1.06], size=[0.014, 0.46, 0.2], mirror="x")
add("box", "iron", "iron", C, at=[0.7, 0.4, -1.06], size=[0.12, 0.018, 0.2], array={"count": 2, "step": [0, 0.23, 0]}, mirror="x")

# --- boiler and smokebox -------------------------------------------------------------------------------------------

B = "boiler"
add("cylinder", "green", "paint", B, at=[0, BOILER_Y, 0.15], rotate=[90, 0, 0], radius=BOILER_R, height=1.42, sides=48)
for z in (0.8, 0.66, -0.02):
    add("band", "brass", "brass", B, radius=BOILER_R - 0.002, at=[0, BOILER_Y, z], width=0.04, thickness=0.009, axis="z", sides=48)
S = "smokebox"
turned([0, BOILER_Y, 0.85], [0, BOILER_Y, 1.32], SMOKE_R, "soot", "iron", S, sides=48, bevel=0.014)
turned([0, BOILER_Y, 1.317], [0, BOILER_Y, 1.351], 0.3, "iron_dark", "iron", S, sides=36, bevel=0.014)
add("lathe", "iron_dark", "iron", S, at=[0, BOILER_Y, 1.35], rotate=[90, 0, 0], sides=32,
    profile=[(0, 0), (0.27, 0), (0.24, 0.012), (0.17, 0.024), (0.08, 0.031), (0, 0.033)])  # fmt: skip
for dy in (0.13, -0.13):  # hinge straps
    add("box", "iron", "iron", S, at=[-0.15, BOILER_Y + dy, 1.372], size=[0.4, 0.04, 0.02], chamfer=0.006, bevel_edges="vertical")
    rod([-0.345, BOILER_Y + dy - 0.04, 1.368], [-0.345, BOILER_Y + dy + 0.04, 1.368], 0.022, "iron", "iron", S)
rod([-0.345, BOILER_Y - 0.2, 1.368], [-0.345, BOILER_Y + 0.2, 1.368], 0.011, "steel_bright", "steel", S, sides=8)
add("box", "iron", "iron", S, at=[-0.36, BOILER_Y, 1.345], size=[0.05, 0.42, 0.03])
# the door's handwheel on its dart
rod([0, BOILER_Y, 1.37], [0, BOILER_Y, 1.445], 0.02, "steel_bright", "steel", S)
add("torus", "brass", "brass", S, at=[0, BOILER_Y, 1.425], rotate=[90, 0, 0], radius=0.085, thickness=0.011, sides=16)
for a in (0, 60, 120):
    dx, dy = 0.085 * math.cos(math.radians(a)), 0.085 * math.sin(math.radians(a))
    rod([-dx, BOILER_Y - dy, 1.425], [dx, BOILER_Y + dy, 1.425], 0.007, "brass", "brass", S, sides=6)
add("cylinder", "brass", "brass", S, at=[0, BOILER_Y, 1.435], rotate=[90, 0, 0], radius=0.028, height=0.03, sides=6)
add("box", "steel_bright", "steel", S, at=[0, BOILER_Y - 0.075, 1.392], size=[0.03, 0.2, 0.014], rotate=[0, 0, 28])  # locking handle
# handrail over the door
rail = [(0.405 * math.sin(math.radians(a)), BOILER_Y + 0.405 * math.cos(math.radians(a))) for a in range(-112, 113, 16)]
add("tube", "steel_bright", "steel", S, points=[[x, y, 1.27] for x, y in rail], radius=0.011, sides=8)
for a in (-112, -56, 0, 56, 112):
    sx, sy = math.sin(math.radians(a)), math.cos(math.radians(a))
    rod([0.35 * sx, BOILER_Y + 0.35 * sy, 1.27], [0.405 * sx, BOILER_Y + 0.405 * sy, 1.27], 0.012, "brass", "brass", S, sides=8)
    add("sphere", "brass", "brass", S, at=[0.405 * sx, BOILER_Y + 0.405 * sy, 1.27], radius=0.02, sides=6)

# --- chimney, dome, safety valves, whistle -----------------------------------------------------------------------

F = "fittings"
add("lathe", "soot", "iron", F, at=[0, 0, 1.08], sides=24,
    profile=[(0, 1.58), (0.215, 1.58), (0.2, 1.63), (0.165, 1.685), (0.128, 1.73), (0.108, 1.79), (0.098, 1.86), (0.094, 2.19), (0.086, 2.19), (0.086, 2.0), (0, 2.0)])  # fmt: skip
add("lathe", "copper", "copper", F, at=[0, 0, 1.08], sides=24,
    profile=[(0.086, 2.18), (0.097, 2.18), (0.104, 2.215), (0.128, 2.25), (0.147, 2.275), (0.15, 2.3), (0.14, 2.325), (0.118, 2.338), (0.086, 2.338)])  # fmt: skip
add("lathe", "brass", "brass", F, at=[0, 0, 0.3], sides=28,
    profile=[(0, 1.55), (0.225, 1.55), (0.205, 1.6), (0.178, 1.655), (0.162, 1.7), (0.158, 1.84), (0.15, 1.9), (0.128, 1.95), (0.09, 1.985), (0.045, 2.003), (0, 2.008)])  # fmt: skip
add("cylinder", "brass_bright", "brass", F, at=[0, 2.02, 0.3], radius=0.022, height=0.03, sides=6)
# safety valves on their seat
add("lathe", "brass", "brass", F, at=[0, 0, -0.2], sides=24, profile=[(0, 1.6), (0.12, 1.6), (0.105, 1.66), (0.085, 1.69), (0, 1.69)])
for dx in (-0.045, 0.045):
    add("lathe", "brass", "brass", F, at=[dx, 0, -0.2], sides=12, profile=[(0, 1.68), (0.03, 1.68), (0.026, 1.8), (0.036, 1.82), (0.036, 1.85), (0.02, 1.87), (0, 1.87)])
add("box", "steel_bright", "steel", F, at=[0, 1.885, -0.24], size=[0.022, 0.014, 0.24])
W = "whistle"
WHISTLE = [0.13, 1.585, -0.36]
rod(WHISTLE, [WHISTLE[0], 1.75, WHISTLE[2]], 0.014, "brass", "brass", W, sides=8)
add("lathe", "brass", "brass", W, at=[WHISTLE[0], 0, WHISTLE[2]], sides=12,
    profile=[(0, 1.74), (0.03, 1.74), (0.03, 1.765), (0.012, 1.775), (0.012, 1.79), (0.033, 1.795), (0.033, 1.87), (0.02, 1.895), (0, 1.9)])  # fmt: skip
add("box", "steel_bright", "steel", W, at=[WHISTLE[0], 1.75, WHISTLE[2] - 0.06], size=[0.012, 0.012, 0.14])
rod([WHISTLE[0], 1.75, WHISTLE[2] - 0.125], [WHISTLE[0], 1.9, -0.5], 0.006, "steel_bright", "steel", F, sides=6)

# --- side tanks, their lining and nameplates ---------------------------------------------------------------------

T = "tanks"
TANK_Z0, TANK_Z1 = -0.5, 0.62
add("box", "green", "paint", T, at=[(0.31 + HALF) / 2, (FOOT + TANK_TOP) / 2, (TANK_Z0 + TANK_Z1) / 2], size=[HALF - 0.31, TANK_TOP - FOOT, TANK_Z1 - TANK_Z0],
    bevel=0.022, mirror="x")  # fmt: skip
turned([0.5, TANK_TOP, 0.3], [0.5, TANK_TOP + 0.034, 0.3], 0.085, "brass", "brass", T, sides=24, bevel=0.01, mirror="x")
add("box", "brass_bright", "brass", T, at=[0.5, TANK_TOP + 0.042, 0.3], size=[0.03, 0.02, 0.1], mirror="x")
add("box", "iron_dark", "iron", T, at=[0.5, TANK_TOP + 0.01, -0.2], size=[0.2, 0.02, 0.3], mirror="x")  # tank-top tread plate
L = "lining"
if not BLOCKOUT:
    line = rrect(TANK_Z0 + 0.06, FOOT + 0.06, TANK_Z1 - 0.06, TANK_TOP - 0.06, 0.05)
    inner = rrect(TANK_Z0 + 0.074, FOOT + 0.074, TANK_Z1 - 0.074, TANK_TOP - 0.074, 0.036)
    parts.append(plate_x(line, HALF, 0.006, "cream", "paint", L, holes=[inner], mirror="x"))
# nameplates: a red field, a brass rim and the name cast proud of it
NAME_Y, NAME_Z = 1.165, 0.06
letters, units = lettering("EMBERWICK")
UNIT = 0.0092
half_w, half_h = units * UNIT / 2 + 0.04, 0.062
field = rrect(NAME_Z - half_w, NAME_Y - half_h, NAME_Z + half_w, NAME_Y + half_h, 0.02)
parts.append(plate_x(field, HALF + 0.003, 0.008, "red_dark", "paint", L, mirror="x"))
parts.append(plate_x(field, HALF + 0.005, 0.012, "brass", "brass", L, mirror="x",
                     holes=[rrect(NAME_Z - half_w + 0.014, NAME_Y - half_h + 0.014, NAME_Z + half_w - 0.014, NAME_Y + half_h - 0.014, 0.01)]))  # fmt: skip
for side in (1, -1):
    add("extrude", "brass_bright", "brass", L, path=letters, path_scale=UNIT, height=0.012, at=[side * (HALF + 0.005), NAME_Y, NAME_Z], rotate=[90, side * 90, 0])

# --- cab -------------------------------------------------------------------------------------------------------------

K = "cab"
CAB_Z0, CAB_Z1 = -1.15, -0.5
EAVES = roof_y(HALF) - 0.004
side_sheet = [(CAB_Z0, FOOT), (CAB_Z1, FOOT), (CAB_Z1, EAVES), (CAB_Z0, EAVES)]
opening = rrect(-1.03, 1.42, -0.63, 1.86, 0.1, 5)
parts.append(plate_x(side_sheet, HALF - 0.0125, 0.025, "green", "paint", K, holes=[opening], mirror="x"))
gable = [(-HALF, FOOT), (HALF, FOOT), *[(x / 100, roof_y(x / 100) - 0.004) for x in range(66, -67, -11)]]
parts.append(plate_z(gable, CAB_Z1 - 0.015, 0.03, "green", "paint", K, holes=[circle(0.41, 1.78, 0.092, 24), circle(-0.41, 1.78, 0.092, 24)]))
parts.append(plate_z(gable, CAB_Z0 + 0.0125, 0.025, "green", "paint", K, holes=[rrect(-0.47, 1.47, 0.47, 1.9, 0.1, 5)]))
for x in (0.41, -0.41):  # spectacles: a brass rim and a pane
    add("torus", "brass", "brass", K, at=[x, 1.78, CAB_Z1 + 0.002], rotate=[90, 0, 0], radius=0.094, thickness=0.013, sides=16)
    add("cylinder", "glass", "glass", K, at=[x, 1.78, CAB_Z1 - 0.015], rotate=[90, 0, 0], radius=0.094, height=0.008, sides=16)
if not BLOCKOUT:  # brass beading round the side openings
    parts.append(plate_x(rrect(-1.045, 1.405, -0.615, 1.875, 0.115, 5), HALF, 0.012, "brass", "brass", K, holes=[opening], mirror="x"))
for z in (-1.1, -0.56):  # handrails either side of the opening
    rod([HALF + 0.03, 0.98, z], [HALF + 0.03, 1.36, z], 0.011, "steel_bright", "steel", K, sides=8, mirror="x")
    for y in (0.99, 1.35):
        add("sphere", "brass", "brass", K, at=[HALF + 0.022, y, z], radius=0.02, sides=6, mirror="x")
R = "roof"
roof = [*[(x / 100, roof_y(x / 100, ROOF_R + 0.03)) for x in range(-74, 75, 12)][:-1], (0.74, roof_y(0.74, ROOF_R + 0.03)),
        (0.74, roof_y(0.74)), *[(x / 100, roof_y(x / 100)) for x in range(62, -63, -12)], (-0.74, roof_y(0.74))]  # fmt: skip
parts.append(plate_z(roof, -0.825, 0.86, "iron_dark", "paint", R))
slope = math.degrees(math.atan2(-0.45, math.sqrt((ROOF_R + 0.03) ** 2 - 0.45**2)))
add("box", "iron", "iron", R, at=[0.45, roof_y(0.45, ROOF_R + 0.03) + 0.004, -0.825], size=[0.02, 0.014, 0.86], rotate=[0, 0, slope], mirror="x")
add("box", "iron", "iron", R, at=[0, roof_y(0, ROOF_R + 0.03) + 0.008, -0.825], size=[0.36, 0.03, 0.34])
add("box", "iron_dark", "paint", R, at=[0, roof_y(0, ROOF_R + 0.03) + 0.03, -0.825], size=[0.42, 0.016, 0.4], chamfer=0.006, bevel_edges="top")

# inside the cab: planked floor, the boiler's backhead and its fittings
I = "footplate"
add("planks", "wood", "wood", I, at=[0, FOOT + 0.012, -0.825], size=[1.26, 0.024, 0.6], count=7, gap=0.008, axis="x", jitter=0.02, seed=3)
turned([0, BOILER_Y, CAB_Z1 - 0.11], [0, BOILER_Y, CAB_Z1 - 0.03], BOILER_R + 0.01, "soot", "iron", I, sides=28, bevel=0.015)
add("box", "soot", "iron", I, at=[0, 1.08, CAB_Z1 - 0.07], size=[0.7, 0.42, 0.08])
add("cylinder", "brass", "brass", I, at=[0, 1.12, CAB_Z1 - 0.115], rotate=[90, 0, 0], radius=0.105, height=0.02, sides=14)  # firehole ring
add("cylinder", "red_dark", "paint", I, at=[0, 1.12, CAB_Z1 - 0.122], rotate=[90, 0, 0], radius=0.085, height=0.02, sides=14)
add("box", "lamp_glow", "lamp", I, at=[0, 1.12, CAB_Z1 - 0.13], size=[0.11, 0.022, 0.012])  # the fire through the door's slot
for x in (-0.16, 0.16):  # pressure gauges
    add("cylinder", "brass", "brass", I, at=[x, 1.5, CAB_Z1 - 0.125], rotate=[90, 0, 0], radius=0.055, height=0.04, sides=12)
    add("cylinder", "cream", "paint", I, at=[x, 1.5, CAB_Z1 - 0.143], rotate=[90, 0, 0], radius=0.042, height=0.008, sides=12)
    add("box", "soot", "paint", I, at=[x + 0.01, 1.512, CAB_Z1 - 0.149], size=[0.006, 0.04, 0.004], rotate=[0, 0, -35])
rod([0, 1.36, CAB_Z1 - 0.11], [0, 1.36, CAB_Z1 - 0.17], 0.03, "brass", "brass", I, sides=12)  # regulator
add("box", "red", "paint", I, at=[0.11, 1.385, CAB_Z1 - 0.16], size=[0.3, 0.03, 0.016], rotate=[0, 0, 12])
rod([0.27, 1.2, CAB_Z1 - 0.14], [0.27, 1.42, CAB_Z1 - 0.14], 0.012, "glass", "glass", I, sides=8)  # water gauge
for y in (1.2, 1.42):
    add("cylinder", "brass", "brass", I, at=[0.27, y, CAB_Z1 - 0.13], radius=0.02, height=0.03, sides=8)
add("tube", "copper", "copper", I, points=[[-0.27, 1.5, CAB_Z1 - 0.12], [-0.27, 1.25, CAB_Z1 - 0.12], [-0.4, 1.1, CAB_Z1 - 0.12], [-0.4, FOOT, CAB_Z1 - 0.12]], radius=0.014, sides=8)
# handbrake column in the corner
rod([0.5, FOOT, -1.02], [0.5, 1.5, -1.02], 0.02, "iron_dark", "iron", I, sides=10)
add("torus", "red", "paint", I, at=[0.5, 1.5, -1.02], radius=0.08, thickness=0.012, sides=12)
rod([0.42, 1.5, -1.02], [0.58, 1.5, -1.02], 0.008, "red", "paint", I, sides=6)

# --- bunker ------------------------------------------------------------------------------------------------------------

U = "bunker"
add("box", "green", "paint", U, at=[0, 1.095, -1.3], size=[2 * HALF, 0.45, 0.3], bevel=0.022)
add("planks", "wood", "wood", U, at=[0, 1.4, -1.437], size=[1.3, 0.17, 0.022], count=2, gap=0.008, axis="y", jitter=0.0, seed=1)
add("planks", "wood", "wood", U, at=[HALF - 0.012, 1.4, -1.3], size=[0.022, 0.17, 0.27], count=2, gap=0.008, axis="y", jitter=0.0, seed=2, mirror="x")
add("box", "iron_dark", "iron", U, at=[HALF - 0.012, 1.4, -1.437], size=[0.034, 0.19, 0.034], mirror="x")
add("ellipsoid", "coal", "stone", U, at=[0, 1.37, -1.29], radii=[0.6, 0.13, 0.125], noise={"amount": 0.035, "scale": 0.06, "seed": 9})
if not BLOCKOUT:
    parts.append(plate_z(rrect(-0.6, FOOT + 0.06, 0.6, 1.26, 0.05), -1.45, 0.006, "cream", "paint", L, holes=[rrect(-0.586, FOOT + 0.074, 0.586, 1.246, 0.036)]))
    for side in (1, -1):
        seven, _ = lettering("7")
        add("extrude", "brass_bright", "brass", L, path=seven, path_scale=0.019, height=0.012, at=[side * (HALF + 0.003), 1.15, -0.83], rotate=[90, side * 90, 0])
    oval = [(-0.83 + 0.075 * math.cos(math.radians(a)), 0.985 + 0.042 * math.sin(math.radians(a))) for a in range(0, 360, 20)]
    parts.append(plate_x(oval, HALF + 0.002, 0.008, "brass", "brass", L, bevel=0.003, mirror="x"))
    parts.append(plate_x([(-0.83 + 0.72 * (z + 0.83), 0.985 + 0.6 * (y - 0.985)) for z, y in oval], HALF + 0.004, 0.008, "red_dark", "paint", L, mirror="x"))

# --- cylinders, slide bars and steam pipes -----------------------------------------------------------------------

Y = "cylinders"
add("cylinder", "green", "paint", Y, at=[CYL_X, AXLE_Y, 1.13], rotate=[90, 0, 0], radius=0.118, height=0.3, sides=24, mirror="x")
for z in (0.972, 1.288):
    turned([CYL_X, AXLE_Y, z - 0.013], [CYL_X, AXLE_Y, z + 0.013], 0.128, "steel", "steel", Y, sides=24, bevel=0.007, mirror="x")
add("band", "brass", "brass", Y, radius=0.117, at=[CYL_X, AXLE_Y, 1.13], width=0.03, thickness=0.006, axis="z", sides=24, mirror="x")
add("box", "green", "paint", Y, at=[0.45, 0.72, 1.13], size=[0.22, 0.24, 0.3], chamfer=0.016, bevel_edges="vertical", mirror="x")  # steam chest
add("cylinder", "brass", "brass", Y, at=[CYL_X, AXLE_Y, 0.95], rotate=[90, 0, 0], radius=0.032, height=0.03, sides=12, mirror="x")  # gland
add("lathe", "steel_bright", "steel", Y, at=[CYL_X, AXLE_Y, 1.3], rotate=[90, 0, 0], sides=12, mirror="x", profile=[(0, 0), (0.07, 0), (0.05, 0.016), (0, 0.022)])
for dy in (0.079, -0.079):
    add("box", "steel_bright", "steel", Y, at=[CYL_X + 0.008, AXLE_Y + dy, 0.74], size=[0.056, 0.022, 0.46], mirror="x")
add("box", "iron_dark", "iron", Y, at=[CYL_X + 0.008, AXLE_Y, 0.515], size=[0.056, 0.2, 0.022], mirror="x")  # the bars' end bracket
for z in (1.02, 1.24):  # drain cocks
    rod([CYL_X, AXLE_Y - 0.11, z], [CYL_X, AXLE_Y - 0.17, z], 0.01, "copper", "copper", Y, sides=6, mirror="x")
add("tube", "copper", "copper", "pipes", points=[[0.3, 1.2, 1.1], [0.37, 1.16, 1.1], [0.43, 1.08, 1.105], [0.46, 0.97, 1.11], [0.46, 0.8, 1.12]], radius=0.034, sides=10, mirror="x")
add("band", "brass", "brass", "pipes", radius=0.034, at=[0.46, 0.9, 1.115], width=0.03, thickness=0.008, axis="y", sides=10, mirror="x")
# feed pipes and clack valves ahead of the tanks
add("tube", "copper", "copper", "pipes", points=[[0.45, FOOT, 0.72], [0.45, 1.19, 0.72], [0.435, 1.26, 0.72], [0.4, 1.295, 0.72], [0.32, 1.3, 0.72]], radius=0.018, sides=8, mirror="x")
add("cylinder", "brass", "brass", "pipes", at=[0.37, 1.3, 0.72], rotate=[0, 0, 90], radius=0.034, height=0.05, sides=8, mirror="x")

# --- buffers, hooks, lamps, hoses --------------------------------------------------------------------------------


def buffers(z: float, face: int, id: str) -> None:  # noqa: A002
    for side in (1, -1):
        add("box", "iron_dark", "iron", id, at=[side * 0.43, 0.7, z + face * 0.008], size=[0.17, 0.17, 0.016])
        rod([side * 0.43, 0.7, z], [side * 0.43, 0.7, z + face * 0.1], 0.056, "iron_dark", "iron", id, sides=12)
        rod([side * 0.43, 0.7, z + face * 0.08], [side * 0.43, 0.7, z + face * 0.125], 0.04, "steel_bright", "steel", id, sides=12)
        add("lathe", "steel", "steel", id, at=[side * 0.43, 0.7, z + face * 0.125], rotate=[face * 90, 0, 0], sides=18,
            profile=[(0, 0), (0.115, 0), (0.115, 0.012), (0.085, 0.022), (0, 0.027)])  # fmt: skip
        if not BLOCKOUT:
            add("rivets", "iron", "iron", id, count=4, size=0.02, around={"center": [side * 0.43, 0.7, z + face * 0.016], "radius": 0.098, "axis": "z"})
    add("box", "iron_dark", "iron", id, at=[0, 0.7, z + face * 0.006], size=[0.15, 0.17, 0.012])
    hook = [[0, 0.7, z], [0, 0.7, z + face * 0.07], [0, 0.735, z + face * 0.112], [0, 0.778, z + face * 0.09], [0, 0.772, z + face * 0.055]]
    add("tube", "steel", "steel", id, points=hook, radius=0.017, sides=8)
    for k, turn in enumerate(([0, 0, 90], [90, 0, 0], [0, 0, 90])):
        add("torus", "steel", "steel", id, at=[0, 0.672 - 0.062 * k, z + face * 0.09], rotate=turn, radius=0.036, thickness=0.011, sides=8)


def lamp(x: float, y: float, z: float, face: int, lens: str, id: str) -> None:  # noqa: A002
    add("box", "iron_dark", "paint", id, at=[x, y + 0.085, z], size=[0.11, 0.15, 0.1], chamfer=0.014, bevel_edges="vertical")
    add("box", "iron", "iron", id, at=[x, y + 0.005, z], size=[0.07, 0.012, 0.07])
    add("cylinder", "iron_dark", "paint", id, at=[x, y + 0.172, z], radius=0.03, height=0.03, sides=8)
    add("cone", "iron_dark", "paint", id, at=[x, y + 0.197, z], radius=0.044, radius_top=0.012, height=0.024, sides=8)
    add("torus", "brass", "brass", id, at=[x, y + 0.205, z], rotate=[90, 0, 0], radius=0.034, thickness=0.006, sides=8)
    add("cylinder", "brass", "brass", id, at=[x, y + 0.088, z + face * 0.054], rotate=[90, 0, 0], radius=0.043, height=0.016, sides=12)
    add("lathe", lens, "lamp", id, at=[x, y + 0.088, z + face * 0.06], rotate=[face * 90, 0, 0], sides=12, profile=[(0, 0), (0.034, 0), (0.026, 0.01), (0, 0.014)])


buffers(1.522, 1, "front")
buffers(-1.522, -1, "rear")
for x in (0.5, -0.5):
    lamp(x, FOOT, 1.4, 1, "lamp_glow", "front")
lamp(0, BOILER_Y + SMOKE_R - 0.012, 1.2, 1, "lamp_glow", "front")
lamp(0.46, 1.32, -1.46, -1, "red", "rear")
add("box", "iron", "iron", "rear", at=[0.46, 1.315, -1.45], size=[0.12, 0.014, 0.1])
for z, face, bone in ((1.522, 1, "front"), (-1.522, -1, "rear")):  # brake pipe and hose
    rod([-0.2, 0.62, z], [-0.2, 0.86, z + face * 0.02], 0.016, "iron", "iron", bone, sides=8)
    add("tube", "rubber", "rubber", bone, hard=False, radius=0.022, smooth=True,
        points=[[-0.2, 0.86, z + face * 0.02], [-0.2, 0.9, z + face * 0.07], [-0.17, 0.82, z + face * 0.11], [-0.12, 0.7, z + face * 0.1], [-0.1, 0.62, z + face * 0.07]])  # fmt: skip
    add("cylinder", "brass", "brass", bone, at=[-0.1, 0.61, z + face * 0.068], radius=0.028, height=0.04, sides=10)

# --- rivets ------------------------------------------------------------------------------------------------------------

V = "rivets"
for z in (1.3, 0.875):
    rivets("soot", "iron", V, 30, around={"center": [0, BOILER_Y, z], "radius": SMOKE_R, "axis": "z"})
rivets("soot", "iron", V, 24, around={"center": [0, BOILER_Y, 1.32], "radius": 0.335, "axis": "z"})
for dy in (0.13, -0.13):
    rivets("iron", "iron", V, 4, size=0.018, along=[[-0.3, BOILER_Y + dy, 1.382], [0.02, BOILER_Y + dy, 1.382]])
for side in (1, -1):
    x = side * HALF
    for y in (FOOT + 0.028, TANK_TOP - 0.028):
        rivets("green", "paint", V, 20, along=[[x, y, TANK_Z0 + 0.03], [x, y, TANK_Z1 - 0.03]])
    for z in (TANK_Z0 + 0.03, TANK_Z1 - 0.03):
        rivets("green", "paint", V, 8, along=[[x, FOOT + 0.075, z], [x, TANK_TOP - 0.075, z]])
    rivets("green", "paint", V, 18, along=[[side * 0.36, TANK_TOP, TANK_Z0 + 0.03], [side * 0.36, TANK_TOP, TANK_Z1 - 0.03]])
    rivets("green", "paint", V, 11, along=[[x, FOOT + 0.03, CAB_Z0 + 0.03], [x, FOOT + 0.03, CAB_Z1 - 0.03]])
    rivets("green", "paint", V, 11, along=[[x, 1.95, CAB_Z0 + 0.03], [x, 1.95, CAB_Z1 - 0.03]])
    for z in (CAB_Z0 + 0.03, CAB_Z1 - 0.03):
        rivets("green", "paint", V, 16, along=[[x, FOOT + 0.08, z], [x, 1.9, z]])
    rivets("green", "paint", V, 5, along=[[x, FOOT + 0.03, -1.42], [x, FOOT + 0.03, -1.18]])
    rivets("green", "paint", V, 5, along=[[x, 1.29, -1.42], [x, 1.29, -1.18]])
    rivets("iron_dark", "iron", V, 34, size=0.018, along=[[side * (HALF + 0.001), FOOT - 0.07, -1.42], [side * (HALF + 0.001), FOOT - 0.07, 1.42]])
    rivets("iron", "iron", V, 9, size=0.018, along=[[side * 0.45, roof_y(0.45, ROOF_R + 0.03) + 0.012, -1.22], [side * 0.45, roof_y(0.45, ROOF_R + 0.03) + 0.012, -0.43]])
    for z in (1.3, 0.96):
        rivets("steel_bright", "steel", V, 8, size=0.02, around={"center": [side * CYL_X, AXLE_Y, z + (0.003 if z > 1 else -0.003)], "radius": 0.098, "axis": "z"})
for z, face in ((1.522, 1), (-1.522, -1)):
    for y in (0.6, 0.8):
        rivets("red", "paint", V, 12, size=0.024, along=[[-0.64, y, z], [0.64, y, z]])
rivets("green", "paint", V, 18, along=[[-0.62, 1.29, -1.45], [0.62, 1.29, -1.45]])
rivets("green", "paint", V, 18, along=[[-0.62, FOOT + 0.03, -1.45], [0.62, FOOT + 0.03, -1.45]])

# --- exhaust: four puffs that wait in the smokebox and are blown out in turn while it runs ----------------------

PUFFS = 4
STACK = [0, 2.32, 1.08]  # the chimney's mouth
LOBES = [([0, 0, 0], 0.05), ([0.03, 0.015, -0.02], 0.036), ([-0.028, -0.02, 0.015], 0.038), ([0.005, 0.03, 0.02], 0.03)]


def puff_rest(k: int) -> list[float]:
    """Where a puff waits, inside the smokebox (each in its own place: meshes lying exactly on each other weld)."""
    return [0.12 * (k - 1.5), 1.42 + 0.02 * (k % 2), 1.08]


for k in range(PUFFS):
    for at, radius in LOBES:
        add("sphere", "shell", "steam", f"puff{k + 1}", at=[c + d * (-1) ** k for c, d in zip(puff_rest(k), at, strict=True)], radius=radius, sides=10, loose=True)
TOOT = [WHISTLE[0], 1.45, WHISTLE[2]]
for at, radius in LOBES[:3]:
    add("sphere", "shell", "steam", "toot", at=[c + d * 0.7 for c, d in zip(TOOT, at, strict=True)], radius=radius * 0.7, sides=10, loose=True)

# --- rig and animations ------------------------------------------------------------------------------------------

rig: dict[str, Any] = {f"wheel{i + 1}": {"pivot": [0, AXLE_Y, z]} for i, z in enumerate(AXLES)}
for side, rest, s in ((1, PIN_L, "l"), (-1, PIN_R, "r")):
    py, pz = pin(rest)
    rig[f"rod_{s}"] = {"pivot": [side * ROD_X, AXLE_Y + py, pz]}
    rig[f"conrod_{s}"] = {"pivot": [side * CON_X, AXLE_Y, crosshead_z(rest)]}
    rig[f"cross_{s}"] = {"pivot": [side * CYL_X, AXLE_Y, crosshead_z(rest)]}
rig["whistle"] = {"pivot": WHISTLE, "parent": "fittings"}
for k in range(PUFFS):
    rig[f"puff{k + 1}"] = {"pivot": puff_rest(k)}
rig["toot"] = {"pivot": TOOT}

FRAMES = 16
run = []
for f in range(FRAMES):
    turn = 360.0 * f / FRAMES
    pose: dict[str, Any] = {f"wheel{i + 1}": {"rotate": [turn, 0, 0]} for i in range(3)}
    for rest, s in ((PIN_L, "l"), (PIN_R, "r")):
        (y0, z0), (y1, z1) = pin(rest), pin(rest - turn)  # rolling forwards carries a pin over the top towards the front
        pose[f"rod_{s}"] = {"offset": [0, y1 - y0, z1 - z0]}
        slide = crosshead_z(rest - turn) - crosshead_z(rest)
        tilt = math.degrees(math.asin(y1 / CON_LEN) - math.asin(y0 / CON_LEN))
        pose[f"cross_{s}"] = {"offset": [0, 0, slide]}
        pose[f"conrod_{s}"] = {"offset": [0, 0, slide], "rotate": [tilt, 0, 0]}
    for k in range(PUFFS):  # one puff leaves every quarter turn, grows as it climbs and trails back, then thins to nothing
        age = (f - k * FRAMES // PUFFS) % FRAMES
        t = age / FRAMES
        fade = 1.0 if t < 0.6 else max(0.0, (0.94 - t) / 0.34)
        size = 0.05 if age in (0, FRAMES - 1) else max(0.05, (1.1 + 3.6 * t) * fade)
        rest = puff_rest(k)
        pose[f"puff{k + 1}"] = {"offset": [STACK[0] - rest[0], STACK[1] + 1.2 * t - rest[1], STACK[2] - 1.1 * t**1.5 - rest[2]], "scale": size}
    run.append(r4(pose))

whistle = []
for f in range(16):
    pose = {}
    if 2 <= f <= 10:
        pose["whistle"] = {"offset": [0, 0.004 if f % 2 else 0, 0], "scale": [1.0, 1.06 if f % 2 else 1.0, 1.0]}
    if f == 1 or f == 13:
        pose["toot"] = {"scale": 0.05}
    elif 2 <= f <= 12:
        t = (f - 2) / 10
        grow = 0.05 if f in (2, 12) else (1.2 + 3.2 * t) * (1.0 if t < 0.7 else (1.0 - t) / 0.3 + 0.1)
        pose["toot"] = {"offset": [0.06 * t, 0.47 + 0.6 * t, 0.22 * t], "scale": grow}
    whistle.append(r4(pose))

data = model(
    "locomotive",
    parts,
    cls="machine",
    description="narrow-gauge side-tank engine on a length of track: riveted tanks, brass dome, spoked wheels and working rods",
    status="draft",
    tags=["hero", "showpiece"],
    style_version=1,
    budget=64000,
    origin="ground",
    rig=r4(rig),
    skin="rigid",
    union="per_bone",
    animations={"run": {"fps": 16, "poses": run}, "whistle": {"fps": 8, "poses": whistle}},
)
out = Path(__file__).with_name("locomotive.kiln.yaml")
write_model(out, data)
out.write_text("# Generated by models/locomotive.py: edit that and run it again.\n" + out.read_text(encoding="utf-8"), encoding="utf-8")
print(f"{out.name}: {len(parts)} parts")
