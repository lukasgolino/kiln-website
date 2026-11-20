# Art brief

What this project is for, what is in it, and the decisions made along the way. Read it with STYLE.md before changing
a model, and keep it up to date. `kiln status` lists what exists; this file says what is wanted and why.

## What it is for

- **Where it is shown:** the KILN website's hero section. The gallery in `art/demo` is nine simple toy models; these
  two are the showpieces for what the notation does at high detail.
- **How it is shown:** a browser loads each `.glb` with three.js and the standard glTF material: per-colour
  materials, a base colour map and a normal map. No custom shaders and no look kit, so everything has to be in the
  geometry, the colours and the baked maps.
- **Camera:** an orbiting close-up. The visitor turns the model and zooms to the face, so faces, feet and the rows of
  scales and feathers have to hold up at close range.
- **Style:** `showpiece` (see STYLE.md).
- **Limits per model:** 40 000 to 90 000 triangles, a glb under 5 MB, `export = ["glb"]` only, no lint errors.
- **Originals:** both creatures are our own designs. They recreate no existing character.

## The models

- **Dragon** (`models/dragon.py` -> `models/dragon.kiln.yaml`): a stocky forest dragon on four legs, 1.7 m at the
  head, 3.3 m long, wings half open.
  - Scale coat as relief, darker down the back; belly plates from the throat to under the tail; a row of back spines.
  - Head: horns growing out of the brows, a second short pair, teeth outside the lip, a tongue, amber eyes with slit
    pupils, chin barbs.
  - Wings: an arm, three fingers and five membrane panels a side, scalloped along the trailing edge.
  - Clawed feet (`foot`), spurs at the elbows and hocks, a leaf-shaped tail tip.
  - Bones: body, chest, neck1, neck2, head, jaw, eye_l/r, tail1 to tail4; per side foreleg, forearm, forefoot, thigh,
    shin, hindfoot, wing, wingtip.
  - Animations: `idle` (3 s loop: breathing, a slow look, a wave down the tail) and `roar` (2.3 s, plays once: draws
    back, head up, jaw wide, wings thrown open, tail lifted).
- **Owl** (`models/owl.py` -> `models/owl.kiln.yaml`): a great horned owl on a mossy log, 0.7 m with the log.
  - Small plumage (breast, back, crown, throat) as relief; six rows of wing feathers a side, coverts over secondaries
    over primaries, and a column of coverts down the leading edge; a tail fan; two ear tufts a side; a skirt of
    breast feathers over the legs.
  - Face: a russet disc with a dark bracket, pale brows, gold eyes with a pupil and a glint, lids that close, a
    hooked beak.
  - Feet: four toes a foot wrapped round the log, talons dug in.
  - Perch: a log with bark as relief shingles, growth rings on the cut ends, a broken stub, moss cushions, two
    mushrooms.
  - Bones: log, feet, body, head, lid_l/r, tuft_l/r, wing_l/r, wingtip_l/r, tail, skirt.
  - Animations: `idle` (5 s loop: breathing, a long head turn, two blinks, a tuft twitch) and `flap` (1.5 s, plays
    once: leans in, opens the wings, three beats, folds them).

Each model builds to three files that ship together: `<name>.glb`, `<name>.color.png` and `<name>.normal.png` (the glb
names the two maps by relative path). Clips keep glTF names from the manifest: a looping clip is `idle-loop`.

## Rebuilding

```sh
python models/dragon.py && python models/owl.py     # writes the two .kiln.yaml files (deterministic)
KILN_JOBS=1 kiln lint dragon                         # about 8 minutes, 2.5 GB
KILN_JOBS=1 kiln lint owl                            # about 5 minutes
kiln build                                           # build/models/<name>.glb, .color.png, .normal.png, manifest.json
kiln preview dragon --views front,34,side,back --tight
```

`--blockout` on a generator leaves out the repeated parts and the relief (for `kiln preview <name> --draft`);
`--quick` bakes 1024 maps instead of 2048. Build one model at a time.

## Wishlist

- [ ] Veins in the wing membranes as `detail` grooves in the normal map.
- [ ] A `walk` for the dragon (the legs are rigged for it: three bones each).
- [ ] A real unfolding wing for the owl (the flap opens the folded wing as two rigid pieces).
- [ ] A third showpiece with fur, to show the third relief kind.

## Done

- [x] Dragon
- [x] Owl

## Decisions and feedback log

- 2026-11-19: Coats are relief, silhouette features are parts. Relief gives layered scales and feathers at no part
  cost; the dragon is 145 written parts and the owl 90, and both build in minutes.
- 2026-11-19: Cell sizes are set in the models (`resolution: 0.006` and `0.0024`), not left to the style: a style's
  resolution is scaled up with a model's size, which gave 11 mm cells on the 3.3 m dragon.
- 2026-11-19: Maps are 2048. At 1024 a texel is 10 mm on the dragon and its scales come out as blocks.
- 2026-11-19: Wing membranes are flat `extrude` panels turned into the plane of their three corners, 16 mm thick
  (under three cells they break up). A straight fold where two panels meet reads as a half-folded wing.
- 2026-11-19: The dragon's haunches and shoulders belong to the trunk's bones and the legs start below them, so a
  leg that turns does not drag the flank with it. The forelegs hang from `body`, not `chest`: the chest swells and
  turns in the animations and the feet must stay planted.
- 2026-11-19: The head is drawn level and at 1 : 1 about its centre, then grown 1.3 times, the jaw opened 10 degrees
  and the head pitched down 13 degrees, all by the generator (`grow`, `pitch` in `models/gen.py`). The model's
  `transforms:` field was tried for the two turns first; with it the teeth and chin barbs did not come out in the
  mesh, so the generator turns the parts itself.
- 2026-11-19: Eyes are placed with `on:` (sunk into the head's own surface) and are their own bones.
- 2026-11-19: Scutes beside the dragon's spines were tried and taken out: at that size they read as warts.
- 2026-11-19: The owl's eyelids are the top half of a ball round each eye, tipped back at rest, each its own rigid
  bone: turning it forward closes the eye.
- 2026-11-19: The owl's wings are `separate` rigid pieces lying over the body, so opening them stretches no skin.
  The log and the feet have `skin_falloff: 0`: without it the moss followed the wing tips that hang beside it.
- 2026-11-19: Feather parts have their own ids (`skirt`, `tuft_l`, wings, tail) and the relief layers name the
  colours they cover, so no small relief feathers are stamped onto the big ones.
