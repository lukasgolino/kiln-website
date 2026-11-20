# Art brief

What this project is for, what is in it, and the decisions made along the way. Read it with STYLE.md before changing
a model, and keep it up to date. `kiln status` lists what exists; this file says what is wanted and why.

## What it is for

- **Where it is shown:** the KILN website's hero section, beside the creature showpieces. The gallery in `art/demo`
  is nine simple toy models; these two show what the hard-surface side of the notation does at high detail.
- **How it is shown:** a browser loads each `.glb` with three.js and the standard glTF material: one material per
  colour and preset (base colour, roughness, metalness), shade paint in the vertex colours. The viewer lights it
  with a sun and a sky colour from the style's `[look]`; there is no environment to reflect, no custom shader and no
  look kit. Everything has to be in the geometry, the colours and the material presets.
- **Camera:** an orbiting close-up. The visitor turns the model, so every side has to hold up, and the rows of
  rivets, the lettering and the running gear are seen from close by.
- **Style:** `foundry` (see STYLE.md).
- **Limits per model:** 40 000 to 90 000 triangles, a glb under 5 MB, `export = ["glb"]` only, no lint errors.
  A hard-surface triangle costs about 68 bytes in the glb (its corners are not shared), so 5 MB is about 65 000
  triangles: that, not the triangle limit, sets the budgets.
- **Originals:** both are our own designs. They recreate no existing engine, suit, product or character, and carry
  no real name or mark: the engine's name and number are invented.

## The models

- **Locomotive** (`models/locomotive.py` -> `models/locomotive.kiln.yaml`): a six-coupled narrow-gauge side-tank
  engine, 3.2 m over the buffers, on 3.8 m of track with sleepers and a ballast bed. Boiler with brass bands, a
  riveted smokebox whose door has hinge straps, a handwheel and a handrail over it, a copper-capped chimney, a brass
  dome, safety valves and a whistle; side tanks with cream lining, filler lids and cast nameplates (EMBERWICK, in
  block letters drawn for it); a cab with spectacle windows, beaded side openings, a planked floor and a backhead
  with gauges, regulator and firehole; a coal bunker with plank boards; cylinders with slide bars, crossheads,
  connecting and coupling rods on spoked wheels with balance weights; buffer beams, buffers, hooks and chains, four
  lamps, brake hoses, copper steam and feed pipes. Rigid skin, `union: per_bone`. Animations: `run` (one wheel turn
  in 16 frames: the pins carry the coupling rods round, the crossheads slide, the connecting rods tilt, and four
  puffs leave the chimney, one each quarter turn) and `whistle` (the whistle shakes and blows a plume).
- **Diver** (`models/diver.py` -> `models/diver.kiln.yaml`): a deep-sea diver, 1.9 m with the rock under the boots.
  A padded canvas suit (a soft-skinned humanoid) with rolls of gathered cloth, knee and elbow patches and gloves
  with fingers; a copper helmet with four bolted ports (two with guards), riveted straps, air inlets, an exhaust
  valve and a lifting eye; a copper breastplate with a brass brail held by twelve studs and wing nuts; twin air
  tanks with a valve and two rubber hoses; a lead chest weight; a belt with buckle, lead blocks, a sheathed knife
  and a caged lamp; boots with lead soles, brass toe caps and straps; a patch of sea floor with coral, weed and a
  starfish. The helmet, breastplate, tanks, weight, knife, lamp, cuffs, boot fittings and belt fittings are rigid
  pieces on their bones. Animations: `idle` (breathing, a slow sway, the lamp and knife swinging, bubbles rising
  from the exhaust valve) and `wave`.

## Rebuilding

```sh
python models/locomotive.py && python models/diver.py   # writes the two .kiln.yaml files (deterministic)
KILN_JOBS=1 kiln lint locomotive && KILN_JOBS=1 kiln lint diver
kiln build                                               # build/models/<name>.glb and manifest.json
kiln preview locomotive --views 34,side,back-right,front --pitch 14 --tight
```

`--blockout` on a generator leaves out the rivets, lining and small fittings (for `kiln preview <name> --draft`).
A full build takes about a minute per model.

## Wishlist

- [ ] Valve gear on the locomotive (eccentric rods and a rocking link behind the slide bars).
- [ ] A driver for the cab, sharing the diver's skeleton.
- [ ] A `walk` for the diver, on a longer strip of sea floor.

## Done

- [x] Locomotive
- [x] Diver

## Decisions and feedback log

- 2026-11-19: Hardware is real parts, written with the notation's own `rivets`, `band`, `planks` and `bolt`; the
  generators only place them and work out the running gear.
- 2026-11-19: Groups of parts have their own ids, so each is joined as its own solid (`union: per_bone` on the
  engine, `separate: true` pieces on the diver). Joining every rivet into the boiler took minutes; rivets in their
  own piece take seconds, and the pieces overlap where they meet.
- 2026-11-19: Round things with rounded rims are `lathe` parts with a `bevel` (one ring of faces), not `cylinder`
  parts with one (every side edge bevelled too: ten times the triangles, and flat-shaded sides). Boxes take
  `bevel_edges` where only some edges show.
- 2026-11-19: Metals are at most 0.42 metallic. The viewer has no environment map, and a fully metallic surface
  would have nothing to reflect and turn dark; bright base colours and low roughness carry the shine instead.
- 2026-11-19: The nameplate letters are our own block alphabet, written as SVG path data in `models/gen.py`, rather
  than a font's glyphs: no font file or licence to ship.
- 2026-11-19: Smoke and bubbles are parts that wait hidden inside the smokebox and the helmet and are moved and
  scaled by the animations; at rest and in a still they don't show.
- 2026-11-19: The diver's helmet does not turn (it is bolted to the breastplate, and its hoses run to the tanks on
  the chest): the `idle` cycle runs with `look: 0, nod: 0`.
- 2026-11-19: The diver's hoses are smooth parts; as hard tubes their tight bends left open edges.
