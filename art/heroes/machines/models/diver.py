"""Generates diver.kiln.yaml: a deep-sea diver in a canvas suit, copper helmet and breastplate, on a patch of sea floor.

Run from the project folder:  python models/diver.py [--blockout]

The suit is a soft-skinned humanoid (it bends where its parts blend); everything metal is a hard part. The helmet,
breastplate, air tanks, chest weight, knife and lamp are each their own rigid piece on a bone (`separate: true`), so
they stay exact polygons and never stretch when the diver waves. `--blockout` leaves the rivets and small fittings out.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen import P, curve, on_sphere, plate_z, r4, rrect  # noqa: E402

from kiln.api import model, write_model  # noqa: E402

BLOCKOUT = "--blockout" in sys.argv
parts: list[dict[str, Any]] = []


def add(shape: str, color: str | None = None, material: str | None = None, id: str | None = None, **kw: Any) -> None:  # noqa: A002
    parts.append(P(shape, color, material, id, **kw))


def rod(a: list[float], b: list[float], radius: float, color: str, material: str, id: str, sides: int = 8, **kw: Any) -> None:  # noqa: A002
    add("cylinder", color, material, id, radius=radius, sides=sides, aim=[a, b], **kw)


def turned(a: list[float], b: list[float], radius: float, color: str, material: str, id: str, sides: int = 16, bevel: float = 0.0, **kw: Any) -> None:  # noqa: A002
    """A turned disc or drum from a to b with rounded rims (a lathe: its bevel is one ring of faces)."""
    h = math.dist(a, b) / 2
    extra = {"bevel": bevel} if bevel else {}
    add("lathe", color, material, id, profile=[(0, -h), (radius, -h), (radius, h), (0, h)], sides=sides, aim=[a, b], **extra, **kw)


def along(p: list[float], n: list[float], d: float) -> list[float]:
    return [a + b * d for a, b in zip(p, n, strict=True)]


def detail(shape: str, *a: Any, **kw: Any) -> None:
    if not BLOCKOUT:
        add(shape, *a, **kw)


# --- the body: a canvas suit ---------------------------------------------------------------------------------------

GROUND = 0.1  # the rock's top, under the boots
SHOULDER, ELBOW, WRIST = [0.275, 1.31, 0.0], [0.405, 1.07, 0.0], [0.47, 0.84, 0.05]
HIP, KNEE, ANKLE = [0.125, 0.955, 0.0], [0.14, 0.59, 0.012], [0.145, 0.26, 0.0]

parts.append(P("capsule", "canvas", "canvas", "hips", **{"from": [0, 0.955, 0], "to": [0, 0.99, 0], "radius": 0.19}))
parts.append(P("capsule", "canvas", "canvas", "spine", blend=0.05, **{"from": [0, 1.06, 0], "to": [0, 1.1, 0], "radius": 0.204}))
parts.append(P("capsule", "canvas", "canvas", "chest", blend=0.05, **{"from": [0, 1.19, 0], "to": [0, 1.26, 0], "radius": 0.212}))
add("ellipsoid", "canvas", "canvas", "chest", at=[0, 1.3, 0], radii=[0.3, 0.1, 0.175], blend=0.05)


def limb(a: list[float], b: list[float], radius: float, radius_to: float, bone: str, gathers: tuple[float, ...]) -> None:
    """One sleeve or trouser leg with its mirror twin, and rolls of gathered canvas at the given shares of its length."""
    twin = bone[:-1] + "r"
    parts.append(P("capsule", "canvas", "canvas", bone, blend=0.045, mirror="x", mirror_id=twin, **{"from": a, "to": b, "radius": radius, "radius_to": radius_to}))
    d = [(q - p) / math.dist(a, b) for p, q in zip(a, b, strict=True)]
    for share in gathers:
        at = [p + (q - p) * share for p, q in zip(a, b, strict=True)]
        ring = radius + (radius_to - radius) * share
        add("torus", "canvas", "canvas", bone, radius=ring - 0.004, thickness=0.02, blend=0.022, aim=[along(at, d, -0.01), along(at, d, 0.01)], mirror="x", mirror_id=twin)


limb(SHOULDER, ELBOW, 0.09, 0.086, "upperarm_l", (0.62, 0.86))
limb(ELBOW, WRIST, 0.084, 0.072, "lowerarm_l", (0.2, 0.5))
add("ellipsoid", "canvas_dark", "canvas", "lowerarm_l", at=[0.415, 1.06, -0.04], radii=[0.068, 0.085, 0.06], blend=0.02, mirror="x", mirror_id="lowerarm_r")  # elbow patch
limb(HIP, KNEE, 0.116, 0.104, "upperleg_l", (0.72, 0.9))
limb(KNEE, ANKLE, 0.102, 0.094, "lowerleg_l", (0.32, 0.52))
add("ellipsoid", "canvas_dark", "canvas", "lowerleg_l", at=[0.14, 0.595, 0.068], radii=[0.085, 0.1, 0.06], blend=0.02, mirror="x", mirror_id="lowerleg_r")  # knee patch
# gloves with fingers, and a brass cuff ring where each seals to the sleeve
add("hand", "leather", "leather", "hand_l", at=[WRIST[0] + 0.004, WRIST[1] - 0.012, WRIST[2] + 0.004], length=0.235, width=0.13, fingers=4, curl=30, spread=8,
    density=3, mirror="x", mirror_id="hand_r")  # fmt: skip
arm = [(w - e) / math.dist(WRIST, ELBOW) for w, e in zip(WRIST, ELBOW, strict=True)]
turned(along(WRIST, arm, -0.045), along(WRIST, arm, 0.012), 0.083, "brass", "brass", "cuff_l", sides=20, bevel=0.008, mirror="x", mirror_id="cuff_r")
turned(along(WRIST, arm, -0.07), along(WRIST, arm, -0.045), 0.076, "rubber", "rubber", "cuff_l", sides=20, mirror="x", mirror_id="cuff_r")

# --- weighted boots --------------------------------------------------------------------------------------------------

FX = ANKLE[0]
parts.append(P("capsule", "leather", "leather", "foot_l", blend=0.03, mirror="x", mirror_id="foot_r", **{"from": [FX, 0.215, -0.035], "to": [FX, 0.21, 0.13], "radius": 0.082}))
parts.append(P("capsule", "leather", "leather", "foot_l", blend=0.03, mirror="x", mirror_id="foot_r", **{"from": [FX, 0.22, -0.02], "to": [FX, 0.31, -0.008], "radius": 0.1}))
sole = [(x, z) for x, z in rrect(FX - 0.1, -0.135, FX + 0.1, 0.235, 0.075, 4)]
add("extrude", "lead", "iron", "boot_l", points=[[x, z] for x, z in sole], height=0.07, at=[0, GROUND + 0.03, 0], bevel=0.01, mirror="x", mirror_id="boot_r")
add("extrude", "leather_dark", "leather", "boot_l", points=[[x, z] for x, z in rrect(FX - 0.092, -0.127, FX + 0.092, 0.227, 0.07, 4)], height=0.022,
    at=[0, GROUND + 0.075, 0], mirror="x", mirror_id="boot_r")  # fmt: skip
add("ellipsoid", "brass", "brass", "boot_l", at=[FX, 0.2, 0.158], radii=[0.09, 0.078, 0.082], sides=16, mirror="x", mirror_id="boot_r")  # toe cap
for z in (0.02, 0.1):  # straps over the instep, with buckles
    add("torus", "leather_dark", "leather", "boot_l", at=[FX, 0.2, z], rotate=[90, 0, 0], radius=0.088, thickness=0.011, sides=14, mirror="x", mirror_id="boot_r")
    add("box", "brass_bright", "brass", "boot_l", at=[FX + 0.088, 0.24, z], size=[0.02, 0.04, 0.034], mirror="x", mirror_id="boot_r")
detail("rivets", "brass", "brass", "boot_l", count=5, size=0.018, along=[[FX + 0.101, GROUND + 0.035, -0.06], [FX + 0.101, GROUND + 0.035, 0.16]], mirror="x", mirror_id="boot_r")

# --- belt: buckle, lead weights -------------------------------------------------------------------------------------

add("band", "leather", "leather", "hips", fit=["hips", "spine"], at=[0, 1.0, 0], width=0.07, thickness=0.016)
add("box", "brass", "brass", "belt", at=[0, 1.0, 0.203], size=[0.085, 0.07, 0.036], chamfer=0.008, bevel_edges="vertical")
add("box", "leather", "leather", "belt", at=[0, 1.0, 0.219], size=[0.05, 0.034, 0.012])
for a in (52, 128, -128):
    s, c = math.sin(math.radians(a)), math.cos(math.radians(a))
    add("box", "lead", "iron", "belt", at=[0.212 * s, 0.995, 0.212 * c], size=[0.085, 0.095, 0.06], rotate=[0, a, 0], chamfer=0.012, bevel_edges="vertical")

# --- helmet: a copper bonnet with bolted ports ---------------------------------------------------------------------

HEAD = "head"
HC, HR = [0.0, 1.64, 0.0], 0.248
neck_r = 0.195
low = -math.degrees(math.asin(math.sqrt(HR**2 - neck_r**2) / HR))
bonnet = [(0, 1.45), (neck_r, 1.45), *[(HR * math.cos(math.radians(a)), HC[1] + HR * math.sin(math.radians(a))) for a in [low + (90 - low) * k / 16 for k in range(17)]]]
bonnet[-1] = (0, HC[1] + HR)
add("lathe", "copper", "copper", HEAD, at=[0, 0, 0], profile=bonnet, sides=44)


def port(yaw: float, pitch: float, radius: float, depth: float, bolts: int, bars: int = 0) -> None:
    """A round window: a brass frame standing proud of the bonnet, a pane sunk in it, bolts round the frame."""
    _, n = on_sphere(HC, HR, yaw, pitch)
    base = math.sqrt(HR**2 - radius**2) - 0.004
    p0 = along(HC, n, base)
    turn = [90 - pitch, yaw, 0]
    lip = radius * 0.72
    add("lathe", "brass", "brass", HEAD, at=p0, rotate=turn, sides=28, bevel=0.004,
        profile=[(lip, 0), (radius, 0), (radius, depth), (lip, depth)])  # fmt: skip
    turned(along(p0, n, depth * 0.45), along(p0, n, depth * 0.62), lip + 0.004, "glass", "glass", HEAD, sides=20)
    if BLOCKOUT:
        return
    side = [math.cos(math.radians(yaw)), 0.0, -math.sin(math.radians(yaw))]
    up = [n[1] * side[2] - n[2] * side[1], n[2] * side[0] - n[0] * side[2], n[0] * side[1] - n[1] * side[0]]
    up = [-v for v in up] if up[1] < 0 else up
    face = along(p0, n, depth)
    ring = (radius + lip) / 2
    for k in range(bolts):
        a = math.radians(360 * (k + 0.5) / bolts)
        at = [f + s * ring * math.cos(a) + u * ring * math.sin(a) for f, s, u in zip(face, side, up, strict=True)]
        add("sphere", "brass_bright", "brass", HEAD, at=at, radius=0.009, sides=6)
    for k in range(bars):  # a guard over the pane
        s = lip * (2 * k / (bars - 1) - 1) * 0.62
        h = math.sqrt(max(radius**2 - s**2, 0)) * 0.93
        a = [f + sd * s + u * h + nn * 0.006 for f, sd, u, nn in zip(face, side, up, n, strict=True)]
        b = [f + sd * s - u * h + nn * 0.006 for f, sd, u, nn in zip(face, side, up, n, strict=True)]
        rod(a, b, 0.0065, "brass_bright", "brass", HEAD, sides=6)
    if bars:
        a = [f + sd * radius * 0.93 + nn * 0.006 for f, sd, nn in zip(face, side, n, strict=True)]
        b = [f - sd * radius * 0.93 + nn * 0.006 for f, sd, nn in zip(face, side, n, strict=True)]
        rod(a, b, 0.0065, "brass_bright", "brass", HEAD, sides=6)


port(0, 3, 0.118, 0.07, 10)
port(72, 6, 0.09, 0.052, 8, bars=3)
port(-72, 6, 0.09, 0.052, 8, bars=3)
port(0, 54, 0.068, 0.04, 6)
# hinge and catch of the front port
front, n = on_sphere(HC, HR, 0, 3)
rod([-0.128, front[1] - 0.05, 0.262], [-0.128, front[1] + 0.05, 0.262], 0.013, "brass_bright", "brass", HEAD)
add("box", "brass", "brass", HEAD, at=[-0.118, front[1], 0.25], size=[0.03, 0.06, 0.03])
add("box", "brass", "brass", HEAD, at=[0.124, front[1], 0.252], size=[0.022, 0.03, 0.03])
add("box", "brass_bright", "brass", HEAD, at=[0.13, front[1], 0.278], size=[0.012, 0.06, 0.018])  # wing of the catch
# straps: one over the crown, one round the neck, both riveted
add("band", "brass", "brass", HEAD, radius=HR - 0.001, at=HC, width=0.034, thickness=0.007, axis="x", sides=44)
NECK_BAND = math.sqrt(HR**2 - (HC[1] - 1.515) ** 2)
add("band", "brass", "brass", HEAD, radius=NECK_BAND - 0.001, at=[0, 1.515, 0], width=0.03, thickness=0.007, axis="y", sides=44)
if not BLOCKOUT:
    crown = [on_sphere(HC, HR + 0.006, 0, a)[0] for a in range(80, 201, 10)]  # from behind the top port, over, down the back
    add("rivets", "brass_bright", "brass", HEAD, count=13, size=0.017, along=crown)
    add("rivets", "brass_bright", "brass", HEAD, count=20, size=0.017, around={"center": [0, 1.515, 0], "radius": NECK_BAND + 0.005, "axis": "y"})
turned([0, 1.42, 0], [0, 1.468, 0], 0.228, "brass", "brass", HEAD, sides=44, bevel=0.008)  # neck ring
for a in (45, 135, 225, 315):  # the lugs that lock it to the breastplate
    s, c = math.sin(math.radians(a)), math.cos(math.radians(a))
    add("box", "brass_bright", "brass", HEAD, at=[0.232 * s, 1.444, 0.232 * c], size=[0.07, 0.03, 0.022], rotate=[0, a, 0])
# air inlets at the back, an exhaust valve, a lifting eye
INLETS = []
for yaw in (152, -152):
    p, n = on_sphere(HC, HR, yaw, -8)
    turned(along(p, n, -0.012), along(p, n, 0.04), 0.03, "brass", "brass", HEAD, sides=12, bevel=0.004)
    rod(along(p, n, 0.03), along(p, n, 0.056), 0.037, "brass_bright", "brass", HEAD, sides=6)
    INLETS.append((along(p, n, 0.05), n))
p, n = on_sphere(HC, HR, -112, -12)
VALVE = along(p, n, 0.085)  # where the exhaust lets its bubbles go
turned(along(p, n, -0.012), along(p, n, 0.045), 0.04, "brass", "brass", HEAD, sides=14, bevel=0.006)
rod(along(p, n, 0.04), along(p, n, 0.07), 0.012, "brass_bright", "brass", HEAD, sides=6)
add("torus", "red", "paint", HEAD, at=along(p, n, 0.07), rotate=[90, -112, 0], radius=0.03, thickness=0.007, sides=12)
p, n = on_sphere(HC, HR, 112, -12)
turned(along(p, n, -0.012), along(p, n, 0.03), 0.034, "brass", "brass", HEAD, sides=8)  # the telephone box's gland
rod(along(p, n, 0.02), along(p, n, 0.05), 0.016, "brass_bright", "brass", HEAD, sides=6)
p, n = on_sphere(HC, HR, 180, 62)
rod(along(p, n, -0.01), along(p, n, 0.02), 0.016, "brass", "brass", HEAD, sides=8)
add("torus", "brass_bright", "brass", HEAD, at=along(p, n, 0.045), rotate=[0, 0, 90], radius=0.03, thickness=0.008, sides=12)

# --- breastplate -----------------------------------------------------------------------------------------------------

PL = "plate"
RIM_R, RIM_Y = 0.338, 1.215
add("lathe", "copper", "copper", PL, at=[0, 0, 0], sides=44, bevel=0.005,
    profile=[(0.185, 1.43), (0.215, 1.43), (0.24, 1.4), (0.282, 1.355), (0.312, 1.3), (0.328, 1.245), (0.328, RIM_Y), (0.306, RIM_Y), (0.302, 1.25), (0.26, 1.335), (0.2, 1.39)])  # fmt: skip
add("lathe", "brass", "brass", PL, at=[0, 0, 0], sides=44, bevel=0.004, profile=[(0.322, RIM_Y - 0.008), (RIM_R, RIM_Y - 0.008), (RIM_R, 1.262), (0.326, 1.268)])
add("lathe", "brass", "brass", PL, at=[0, 0, 0], sides=44, bevel=0.004, profile=[(0.2, 1.4), (0.236, 1.4), (0.243, 1.412), (0.236, 1.428), (0.2, 1.432)])
STUDS = 12
for k in range(STUDS):  # studs and wing nuts holding the brail to the suit's collar
    a = 360 * (k + 0.5) / STUDS
    s, c = math.sin(math.radians(a)), math.cos(math.radians(a))
    y = RIM_Y + 0.022
    rod([0.33 * s, y, 0.33 * c], [0.372 * s, y, 0.372 * c], 0.0075, "brass_bright", "brass", PL, sides=6)
    rod([0.337 * s, y, 0.337 * c], [0.358 * s, y, 0.358 * c], 0.016, "brass_bright", "brass", PL, sides=8)
    add("box", "brass_bright", "brass", PL, at=[0.353 * s, y, 0.353 * c], size=[0.07, 0.028, 0.008], rotate=[0, a, 0])
if not BLOCKOUT:
    add("rivets", "brass_bright", "brass", PL, count=18, size=0.018, around={"center": [0, 1.377, 0], "radius": 0.264, "axis": "y"})
    add("rivets", "copper_bright", "copper", PL, count=24, size=0.016, around={"center": [0, 1.292, 0], "radius": 0.317, "axis": "y"})

# --- air tanks on the back, their hoses ----------------------------------------------------------------------------

TK = "tank"
TX, TZ = 0.095, -0.365
TANK = [(0, 0.9), (0.05, 0.906), (0.076, 0.924), (0.086, 0.952), (0.086, 1.27), (0.076, 1.298), (0.05, 1.316), (0.03, 1.322), (0.03, 1.35), (0, 1.35)]
add("lathe", "steel", "steel", TK, at=[TX, 0, TZ], profile=TANK, sides=24, mirror="x")
for y in (0.99, 1.22):
    add("band", "brass", "brass", TK, radius=0.0855, at=[TX, y, TZ], width=0.028, thickness=0.006, axis="y", sides=24, mirror="x")
    add("box", "iron_dark", "iron", TK, at=[0, y, TZ + 0.075], size=[0.36, 0.03, 0.018])
rod([TX, 1.345, TZ], [TX, 1.375, TZ], 0.038, "brass", "brass", TK, sides=6, mirror="x")
rod([-TX, 1.36, TZ], [TX, 1.36, TZ], 0.016, "brass", "brass", TK)
rod([0, 1.36, TZ], [0, 1.36, TZ - 0.055], 0.012, "brass_bright", "brass", TK, sides=6)
add("torus", "red", "paint", TK, at=[0, 1.36, TZ - 0.055], rotate=[90, 0, 0], radius=0.036, thickness=0.008, sides=12)
for a in (0, 90):
    dx, dy = 0.036 * math.cos(math.radians(a)), 0.036 * math.sin(math.radians(a))
    rod([-dx, 1.36 - dy, TZ - 0.055], [dx, 1.36 + dy, TZ - 0.055], 0.005, "red", "paint", TK, sides=6)
add("box", "leather_dark", "leather", TK, at=[0, 1.1, -0.245], size=[0.3, 0.4, 0.09], chamfer=0.02, bevel_edges="vertical")  # the pad they ride on
turned([TX, 0.895, TZ], [TX, 0.91, TZ], 0.03, "brass", "brass", TK, sides=10, mirror="x")
for (start, n), side in zip(INLETS, (1, -1), strict=True):
    hose = [along(start, n, -0.02), along(start, [n[0], n[1] - 0.45, n[2]], 0.065), [side * 0.165, 1.5, -0.39], [side * 0.13, 1.43, -0.398], [side * TX, 1.36, TZ]]
    add("tube", "rubber", "rubber", TK, points=hose, radius=0.02, smooth=True, hard=False)  # rubber: a smooth part

# --- chest weight ----------------------------------------------------------------------------------------------------

WT = "weight"
parts.append(plate_z(rrect(-0.1, 1.045, 0.1, 1.19, 0.04, 4), 0.25, 0.055, "lead", "iron", WT, bevel=0.01))
parts.append(plate_z(rrect(-0.068, 1.072, 0.068, 1.163, 0.022, 3), 0.28, 0.008, "lead", "iron", WT, holes=[rrect(-0.054, 1.086, 0.054, 1.149, 0.012, 3)]))
for x in (-0.07, 0.07):
    add("torus", "brass", "brass", WT, at=[x, 1.19, 0.25], rotate=[90, 0, 0], radius=0.02, thickness=0.006, sides=10)
    rod([x, 1.2, 0.252], [x * 1.5, RIM_Y + 0.02, 0.318], 0.014, "leather_dark", "leather", WT, sides=6)

# --- knife and lamp on the belt ------------------------------------------------------------------------------------

KN = "knife"
top, tip = [0.258, 0.97, 0.02], [0.283, 0.715, 0.035]
kd = [(b - a) / math.dist(top, tip) for a, b in zip(top, tip, strict=True)]
add("cone", "leather_dark", "leather", KN, radius=0.017, radius_top=0.03, sides=10, aim=[tip, top])
turned(along(top, kd, -0.004), along(top, kd, 0.03), 0.033, "brass", "brass", KN, sides=10, bevel=0.004)
add("cone", "brass", "brass", KN, radius=0.006, radius_top=0.02, sides=10, aim=[along(tip, kd, 0.03), along(tip, kd, -0.03)])
turned(along(top, kd, -0.016), along(top, kd, -0.004), 0.04, "brass_bright", "brass", KN, sides=10)  # guard
rod(along(top, kd, -0.016), along(top, kd, -0.12), 0.019, "wood_dark", "wood", KN, sides=10)
for d in (-0.045, -0.07, -0.095):
    detail("lathe", "brass", "brass", KN, profile=[(0, -0.004), (0.021, -0.004), (0.021, 0.004), (0, 0.004)], sides=10, aim=[along(top, kd, d - 0.004), along(top, kd, d + 0.004)])
add("sphere", "brass_bright", "brass", KN, at=along(top, kd, -0.13), radius=0.025, sides=10)
add("box", "leather", "leather", KN, at=[0.228, 0.99, 0.02], size=[0.06, 0.07, 0.05])  # frog on the belt

LP = "lamp"
HOOK = [-0.2, 0.99, 0.135]
LY = 0.845
rod(HOOK, [HOOK[0], LY + 0.085, HOOK[2]], 0.007, "brass_bright", "brass", LP, sides=6)
add("box", "leather", "leather", LP, at=[-0.185, 1.0, 0.125], size=[0.05, 0.05, 0.04])
add("torus", "brass", "brass", LP, at=[HOOK[0], LY + 0.07, HOOK[2]], rotate=[0, 0, 90], radius=0.036, thickness=0.007, sides=12)
turned([HOOK[0], LY, 0.07], [HOOK[0], LY, 0.2], 0.056, "brass", "brass", LP, sides=20, bevel=0.008)
turned([HOOK[0], LY, 0.19], [HOOK[0], LY, 0.225], 0.068, "brass_bright", "brass", LP, sides=20, bevel=0.006)
add("lathe", "lamp_glow", "lamp", LP, at=[HOOK[0], LY, 0.222], rotate=[90, 0, 0], sides=16, profile=[(0, 0), (0.054, 0), (0.045, 0.012), (0.025, 0.02), (0, 0.022)])
turned([HOOK[0], LY, 0.052], [HOOK[0], LY, 0.072], 0.04, "copper", "copper", LP, sides=12)
for a in (0, 60, 120):  # a cage over the glass
    dx, dy = 0.066 * math.cos(math.radians(a)), 0.066 * math.sin(math.radians(a))
    detail("tube", "brass_bright", "brass", LP, radius=0.005, sides=6,
           points=[[HOOK[0] - dx, LY - dy, 0.225], [HOOK[0] - dx * 0.6, LY - dy * 0.6, 0.26], [HOOK[0] + dx * 0.6, LY + dy * 0.6, 0.26], [HOOK[0] + dx, LY + dy, 0.225]])  # fmt: skip

# --- sea floor -------------------------------------------------------------------------------------------------------

BS = "base"
add("cylinder", "rock", "stone", BS, at=[0, 0.056, 0.03], radius=0.62, height=0.088, round=0.04, hard=False, scale=[1, 1, 0.82], noise={"amount": 0.012, "scale": 0.11, "seed": 3})
for at, radii, color, seed in (([0.46, 0.135, -0.26], [0.2, 0.12, 0.17], "rock_dark", 5), ([-0.5, 0.11, 0.12], [0.15, 0.095, 0.2], "rock_dark", 6),
                               ([0.25, 0.095, 0.43], [0.18, 0.08, 0.12], "rock", 7), ([-0.3, 0.15, -0.37], [0.22, 0.135, 0.17], "rock", 8),
                               ([-0.28, 0.085, 0.42], [0.12, 0.07, 0.1], "rock_dark", 9)):  # (their bottoms stay above y = 0)  # fmt: skip
    add("ellipsoid", color, "stone", BS, at=at, radii=radii, blend=0.03, noise={"amount": 0.02, "scale": 0.09, "seed": seed})
STAR = [0.36, 0.118, 0.26]
add("sphere", "coral", "canvas", BS, at=STAR, radius=0.03, sides=8)
for k in range(5):
    a = math.radians(72 * k + 20)
    add("cone", "coral", "canvas", BS, radius=0.027, radius_top=0.007, sides=6, aim=[STAR, [STAR[0] + 0.105 * math.cos(a), STAR[1] - 0.012, STAR[2] + 0.105 * math.sin(a)]])
for base, tips in (([-0.36, 0.2, -0.33], ([-0.44, 0.47, -0.37], [-0.33, 0.52, -0.42], [-0.27, 0.43, -0.3])), ([0.5, 0.17, -0.22], ([0.56, 0.4, -0.27], [0.47, 0.37, -0.15]))):
    for tip in tips:  # branching coral
        mid = [(a + b) / 2 + d for a, b, d in zip(base, tip, (0.0, -0.03, 0.0), strict=True)]
        add("tube", "coral", "canvas", BS, points=[[base[0], base[1] - 0.06, base[2]], mid, tip], radius=0.022, radius_to=0.011, sides=6)
        add("sphere", "coral", "canvas", BS, at=tip, radius=0.016, sides=6)
for k, (x, z) in enumerate(((-0.52, 0.02), (-0.47, 0.2), (0.33, -0.36))):  # weed
    sway = [[x, 0.08, z], [x + 0.03, 0.25, z + 0.02], [x - 0.02, 0.4, z - 0.01], [x + 0.03, 0.56 + 0.05 * k, z + 0.03]]
    add("tube", "weed", "canvas", BS, points=curve(sway, 3), radius=0.02, radius_to=0.006, sides=6)

# --- breath: four bubbles that wait inside the helmet and leave by the exhaust valve in turn ------------------------

BUBBLES = 4


def bubble_rest(k: int) -> list[float]:
    return [0.07 * (k - 1.5), HC[1] + 0.03 * (k % 2), -0.02]


for k in range(BUBBLES):
    rest = bubble_rest(k)
    add("sphere", "bubble", "glass", f"bubble{k + 1}", at=rest, radius=0.032, sides=12, loose=True)
    add("sphere", "bubble", "glass", f"bubble{k + 1}", at=[rest[0] + 0.036 * (-1) ** k, rest[1] + 0.042, rest[2] + 0.014], radius=0.016, sides=8, loose=True)


def bubbles(f: int, frames: int) -> dict[str, Any]:
    """Frame f of a loop of `frames`: each bubble swells at the valve, wobbles up past the helmet and is gone."""
    out = {}
    for k in range(BUBBLES):
        age = (f - k * frames // BUBBLES) % frames
        t = age / frames
        rest = bubble_rest(k)
        size = 0.05 if age in (0, frames - 1) else (0.5 + 2.2 * t if t < 0.3 else 1.16 + 0.5 * t) * (1.0 if t < 0.8 else (0.96 - t) / 0.16)
        at = [VALVE[0] - 0.05 * t + 0.035 * math.sin(7 * t + k), VALVE[1] + 0.02 + 0.85 * t**1.2, VALVE[2] - 0.04 * t + 0.03 * math.cos(6 * t + 2 * k)]
        out[f"bubble{k + 1}"] = {"offset": [a - b for a, b in zip(at, rest, strict=True)], "scale": max(size, 0.05)}
    return out


# --- rig and animations ------------------------------------------------------------------------------------------

rig = {
    "head": {"separate": True},
    "plate": {"parent": "chest", "separate": True},
    "tank": {"parent": "chest", "separate": True},
    "weight": {"parent": "chest", "separate": True, "pivot": [0, 1.2, 0.25]},
    "knife": {"parent": "hips", "separate": True, "pivot": [0.25, 0.99, 0.02]},
    "lamp": {"parent": "hips", "separate": True, "pivot": HOOK},
    "base": {"separate": True},
    "cuff_l": {"parent": "lowerarm_l", "separate": True},
    "boot_l": {"parent": "foot_l", "separate": True},
    "belt": {"parent": "hips", "separate": True},
    **{f"bubble{k + 1}": {"separate": True, "pivot": bubble_rest(k)} for k in range(BUBBLES)},
}
FRAMES = 24
swing = []
for f in range(FRAMES):
    t = 2 * math.pi * f / FRAMES
    swing.append(r4({"lamp": {"rotate": [5 * math.sin(t), 0, 3 * math.sin(t + 1.2)]}, "knife": {"rotate": [2 * math.sin(t + 0.6), 0, 0]},
                     "weight": {"rotate": [1.5 * math.sin(t + 2.0), 0, 0]}, **bubbles(f, FRAMES)}))  # fmt: skip
animations = {
    "idle": {"fps": 8, "cycle": {"type": "idle", "frames": FRAMES, "look": 0, "nod": 0, "breathe": 0.02, "sway": 2, "arm_sway": 4, "elbow": 10}, "poses": swing},
    "wave": {"fps": 10, "cycle": {"type": "wave", "frames": 12, "raise": 72, "bend": 85, "angle": 24},
             "poses": [r4({"lamp": {"rotate": [4 * math.sin(2 * math.pi * f / 12), 0, 0]}, **bubbles(f, 12)}) for f in range(12)]},  # fmt: skip
}

data = model(
    "diver",
    parts,
    cls="character",
    description="deep-sea diver in a canvas suit: riveted copper helmet with bolted ports, breastplate with wing nuts, weighted boots, air tanks",
    status="draft",
    tags=["hero", "showpiece"],
    style_version=1,
    budget=60000,
    resolution=0.006,
    origin="ground",
    skeleton="humanoid",
    rig=r4(rig),
    skin="soft",
    animations=animations,
)
out = Path(__file__).with_name("diver.kiln.yaml")
write_model(out, data)
out.write_text("# Generated by models/diver.py: edit that and run it again.\n" + out.read_text(encoding="utf-8"), encoding="utf-8")
print(f"{out.name}: {len(data['parts'])} parts")
