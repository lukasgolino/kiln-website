# KILN reference

Everything an agent needs to write KILN models, one section per `kiln docs` topic.

## Setup

Start of every session, a new project, kiln.toml and the project layout.

### Start of every session

1. `kiln status` (or MCP `status`): what exists, what needs review. No `kiln.toml`? `kiln init <dir> --style <preset>`
   (inside a Godot project it writes `.gdignore` in the KILN folder, so Godot skips the sources, and sets `output_dir` to the
   Godot project's `assets/kiln` with `export = ["glb", "godot"]`; `kiln build` with Godot export refuses an output Godot ignores).
2. Read `BRIEF.md` (what the game needs, decisions) and `STYLE.md` (how it looks). They are the project's memory.
3. `kiln style show`: the style's notes (shape language, proportions) and numbers. Follow them.

New project: ask the owner (one batch, each with your recommended default):
- the game and the camera (how close does it get? that decides how much detail matters);
- the style: a preset (`kiln style list`: soft_toy = vinyl toys, low_poly, toon, clay, diorama) or
  inspirations. With inspirations, ask for 3-6 screenshots into `styles/<name>/inspiration/`, look at them, and write a
  style that `extends` the closest preset (`kiln docs styles`);
- the palette (the starter `palettes/main.pal.yaml`, or their colours);
- whether the game is in Godot (then `export = ["glb", "godot"]` and `output_dir` inside the Godot project).
Write the answers into BRIEF.md and STYLE.md.


### Project

```
kiln.toml            settings (kiln config show)
palettes/main.pal.yaml   colours (PAGAN format): models use their names
models/<name>.kiln.yaml  one model per file (name = file name)
styles/<name>.style.toml own styles; styles/<name>/inspiration/*.png|jpg reference images
decals/  imports/        images for decals and textures (or a textures/ folder: paths are relative to the project); imported .glb/.gltf files
BRIEF.md  STYLE.md       what the game needs; how it looks (+ changelog)
```

```toml
# kiln.toml
default_style = "soft_toy"     # kiln style list
default_palette = "main"
output_dir = "build"           # inside the Godot project when export has "godot"
preview_dir = "previews"
preview_size = 400             # optional: kiln preview tile size in pixels (64-1024; a hero face needs ~400+)
export = ["glb", "godot"]
style_version = 1
variant_glbs = true            # false: no .glb per variant; Godot gets <name>.<variant>.tscn recolouring the base glb
merge_rigid = false            # true: a rigid skin is one skinned mesh (one draw call; every vertex 100% on its part's bone;
                               #   separate parts stay nodes; hide a part by scaling its bone to 0); manifest merged_rigid
vertex_colors = false          # true: colours in the vertices, one surface per material preset (fewer draw calls)
atlas = false                  # true: one material per model from small palette textures (1 surface, +1 per decal or texture; normal_map models keep a material per colour)
atlas_ao = false               # true or a strength 0..1 (with atlas): ambient occlusion baked into the vertex colours (normal_map models too)
godot_bonemap = false          # true: humanoids get models/<name>.bonemap.tres in their glb's .import; Godot RENAMES
                               #   their bones to SkeletonProfileHumanoid's (see Humanoids)
looks = []                     # more look kits to build (looks/<style>.tscn), e.g. ["retro_st", "retro_cga"]: a game switching looks
[lint]
disable = ["W106"]
```

## Making

Making a model: plan in metres, scaffold, parts, lint, look, fit with the rest; the model file.

### Making a model

1. **Plan on paper first, in metres.** Real sizes: a door is 2 m, a soldier 1.7 m (a toy-style bean 1-1.2 m), a
   chair seat 0.45 m high, a barrel 0.9 m. Sketch the parts as a list: shape, centre, size, colour. Models stand on
   y = 0, face +Z (their front), +X is their left.
2. **Scaffold:** `kiln new model <name> --template bean|prop|empty --class character|prop|building|...`.
3. **Write the parts** (`kiln docs parts`; patterns, hardware: `kiln docs surfaces`; decals, textures: `kiln docs textures`). Big shapes first, details after. Rules of thumb:
   - Join body parts with `blend` (0.02-0.06 m in soft styles); give crisp seams (`blend: 0`, the default) to things
     that sit ON a surface: eyes, buttons, belts, trims.
   - Symmetric things: write the left one (+X) with `mirror: x`; if it must move separately (arms, legs) add
     `mirror_id: arm_r` so the copy is its own part.
   - Holes and openings: a `cut: true` part after the solid. Hollow things: `shell: <thickness>`.
   - Many regular repeats: `array` (in a row or a ring), or a generator script with `kiln.api` (`kiln docs api`).
   - Before a model gets big, know what is slow (`kiln docs build`, "What things cost"): hundreds of parts, a
     `gradient` or `pattern` on each of many parts, many hard parts (more so with bevels and many sides).
     `kiln preview <name> --draft` while shapes are moving.
   - Every colour is a palette name. Materials are the style's presets (plastic, fabric, skin, leather, wood, stone,
     metal, gold, leaf, glass, clear, rubber, paint, glow). Toy styles' `metal` is part metallic: faces turned down or away
     take a little of the ground's warm colour. For cool cartoon steel pick a blue-grey and `plastic`, or add a preset
     with `metallic` 0.1-0.2 (`kiln docs styles`).
   - See-through (`clear`, or a preset with `alpha` < 1): blended parts share one surface, so a solid clear part
     blended into others shows a hole, not what is behind it. Give it its own surface: a `shell` (a bottle, a dome
     over a dial) or rig it `separate: true` (a window pane). Previews dither it; `atlas = true` draws it opaque (W131).
   - Mechanical props (flat faces, holes, bolts, panels): `hard: true` parts (with `bevel`). Smooth parts blend and
     then get reduced to the budget, so big flats come out dented and holes jagged; hard parts keep flats flat and
     edges straight. Smooth parts are for organic shapes (bodies, cloth, food, rocks).
   - Big plain areas read better with geometry than patterns: planks, trims and shields as parts. Patterns cost
     triangles (W110); keep them for clothes and small props.
   - Things meant to float (flames, bees, sparks, rubble bits): `loose: true` on the part, so W103 stays meaningful.
   - Many similar models (8 soldier types, 5 trees): one `template: true` base and `extends: <base>` models that
     `remove:` and add parts (Model families, below), instead of copies.
4. **Lint:** `kiln lint <name>`. Fix every error; read every warning (W101 a part is hidden, W102 too thin to mesh,
   W103 floating pieces, W106 not standing on the ground, W108 size wrong for the class).
5. **Look:** `kiln preview <name>` writes a turntable (8 sides x below / eye level / above). Open it and check:
   silhouette from every side, proportions, nothing floating, nothing poking through, the face reads, colours
   balanced. Then `--closeup <part>` for anything seen up close (faces, hands, hit zones), and `--detach` when the
   model has detachable (`separate`) parts: each one off, and what's under it. Iterate until it's right.
   You will misjudge proportions without looking: always look.
   For people, start from the template library (`kiln library`; `extends: [body_..., head_..., helmet_..., armour_...]`)
   and add or override parts, instead of building bodies and faces from scratch. To hide the head's hair under a
   helmet (its own piece, shown again when the helmet comes off): `rig: { hair: { parent: head, revealed: [helmet], fold: true } }`.
6. **Fit with the rest:** `kiln lineup` (same scale, one ground line, a 1 m bar) and `kiln preview <name> --vs`
   (beside the inspiration images). Does it look like it belongs in the same game?
7. **Report** to the owner with the preview images. When they approve: `kiln mark <name> --approved`, tick it in
   BRIEF.md, and `kiln build`.


### Model file

```yaml
name: pilot                    # = file name (pilot.kiln.yaml)
description: bean crew member in a pilot cap
class: character               # size class: picks the triangle budget (style [budgets]) and size checks
tags: [crew]
status: draft                  # draft | approved
style_version: 1
style: soft_toy                # optional: else kiln.toml default_style
palette: main                  # optional: else default_palette
budget: 6000                   # optional: triangles (overrides the style's budget for the class)
resolution: 0.004              # optional: metres per mesh cell for this model, as is (not scaled by size): finer detail
normal_map: 1024               # optional: bake a normal map (256-4096 texels, the texture is exactly that size, square; needs kiln-gen[bake]; not with source:; under atlas = true the model keeps a material per colour): detail from the shapes, not triangles
normal_strength: 1             # optional: scales the map's tilt (0.5 softer grooves, 0 flat), up to 4 (steep slopes cap)
relief: [...]                  # optional: fur as patches in the baked maps, not parts (Relief, below)
shade: { cavity: 0.3, top: 0.12, under: 0.1 }  # optional: shade paint in the vertex colours, over the style's [shade] (kiln docs styles)
max_cells: 640                 # optional: mesh cells across at most (64-1024, style default 256); W120 says when it decides
lod: [2500, 800]               # optional: extra lower-detail .glb files
origin: center                 # optional: the .glb's origin: base (bottom centre of the box) | center (spinning debris) | ground
                               #   ([0, lowest point, 0]: the built mesh lifted onto y = 0, W123) | [x, y, z]
                               #   (default: model space as written; manifest `origin` = that point, other manifest values stay model space)
node_prefix: Knight_           # optional: mesh nodes are Knight_<id> children of the part nodes (bones keep the ids;
                               # a soft skin's mesh is Knight_mesh); manifest parts get mesh_node
animation_library: soldier_anims # optional: play that clip carrier's animations (its glb has them; this one none)
animations_only: true          # optional: this model is a clip carrier for others' animation_library
parts: [...]                   # the shapes (below)
rig: {...}                     # optional: bones (below)
skin: soft                     # none (static) | rigid | soft; default rigid when there is a rig
union: whole                   # rigid skins: whole | per_bone (each bone its own closed surface: joints can't tear)
animations: {...}              # optional
variants:                      # optional: recoloured copies (<name>.<variant>.glb, or swap tables: variant_glbs)
  copilot: { swap: { red: green } }   # palette colours; or whole ramps by name, shade for shade: { robes: golds } (colour entries win; a shade in two ramps only when named)
lint: { disable: [W106] }
```

#### Model families

A model can `extends: <base>` a `template: true` model in the same folder (templates are checked but not built):
soldiers sharing one body, trees sharing one trunk.

```yaml
# models/soldier.kiln.yaml
name: soldier
template: true
class: character
parts: [...]                   # body, arms, hat (id: hat)
rig: {...}
animations: {...}

# models/archer.kiln.yaml
name: archer
extends: soldier
remove: [hat]                  # base parts with these ids (or mirror_ids) are left out
parts: [...]                   # added after the base's parts
variants: { blue: { swap: { red: blue } } }
```

The base's parts come first, then the model's own; `rig`, `animations` and `variants` merge by name (the model's
win); every other field is inherited unless the model sets it, except its identity (name, description, tags, status,
style_version, template). Templates can extend templates.

Size classes in the built-in styles: prop, character, hero, creature, vehicle, machine, building, nature (and
`default` for anything else). Size sanity (W108, largest side): character 0.2-4 m, prop 0.02-6 m, building 1-200 m...

### On the surface: `on`

Clumps, straps, scales, spikes and tufts belong on the body's blended surface, which isn't any one part's shape.
`on` puts a part there instead of `at`:

```yaml
  - cone: { radius: 0.03, height: 0.12 }
    color: fur_dark
    on: { part: [body, head], near: [0.25, 0.8, 0.05], offset: -0.02, roll: 0 }
    mirror_id: tuft_r
    mirror: x
```

`near` is walked along the field onto the surface made by the earlier parts with those ids (blends and fitted shells
included; cuts listed before it apply; detail parts don't): start it just outside the spot, since from deep inside
the walk takes the field's way out, not the nearest point. The part's own y axis turns to the surface normal there (`rotate` turns it in its own frame first; `align:
false` keeps its turn and only moves it), `roll` spins it about the normal, `offset` moves it along the normal
(negative sinks it in: a cone's `at` is its middle). A part may sit on one placed this way before it; a `mirror_id`
twin is placed as its mirror image (`mirror: x` folds it as usual). A walk that doesn't settle on the surface is an
error (E003), as are `on` with `array` (the copies wouldn't follow the surface: a part per spot) and on hardware
parts (give them `at`). Hardware after a placed part sees it placed.

### Clothing: `garment`

A shirt, a robe or a jumper over a soft body, as its own layer (a hem, an open neck, a placket) rather than paint:

```yaml
  - garment: { fit: [chest, spine, upperarm_l, upperarm_r], from_y: 0.9, to_y: 1.42, gap: 0.008, thickness: 0.02, hem: 0.015,
               openings: [{ at: [0, 1.3, 0.2], size: [0.05, 0.2, 0.1] }] }
    id: shirt
    color: shirt_blue
```

It wraps the earlier parts with those ids: a shell `thickness` thick, `gap` off their surface, between `from_y` (the
hem) and `to_y` (default: their own extent); it is open where it ends horizontally (the hem, the neck, and the cuffs of
arms hanging down). A sleeve or a trouser leg takes `length: 0.6` instead (the share of its limb, a capsule or tube,
from the end nearest the body): it runs along the limb and ends square and open there, T-posed or not. List every part under it: an unlisted part pokes through.
`hem` adds a band twice that tall at the bottom, a little thicker. An earlier garment can be wrapped too (a shirt over
trousers: `fit: [chest, trousers]`). `openings` are boxes cut through the garment alone, so it needs an `id` of its
own; a mirrored garment (`mirror`, `mirror_id`) gets them mirrored. An opening with `shape: v` is a V, `size: [w, h,
d]` with w its width at the top (a V neck).

```yaml
  - garment: { fit: [chest], from_y: 1.0, to_y: 1.5, collar: { style: open, height: 0.035, depth: 0.16, lapel: 0.045 },
               placket: { width: 0.03, buttons: 4, button_color: black, to_y: 1.3 } }
    id: shirt
  - garment: { fit: [upperarm_l], length: 0.5, hem: 0 }   # a short sleeve
    id: upperarm_l
    mirror: x
    mirror_id: upperarm_r
```

`collar` is a band round the neck at the garment's top (`fit`: the part(s) it rounds, default `neck`, else `head`;
`height`); `style: open` cuts a V `depth` deep at the front and lays a lapel `lapel` wide along each side of it.
`placket` is a raised strip `width` wide down the front (`from_y`, `to_y`: default the garment's) with `buttons`
(`button_color`). They are fitted shells too, so they lie on the body's shape.

On a rigged, soft-skinned character a garment moves with the bone of its `id`: sleeves as their own garments with the
arm's id (`fit: [upperarm_l]`, `id: upperarm_l`, mirrored) move with the arms (and wholly with `skin_falloff: 0`);
the body garment with `id: chest`. Openings need a garment id that isn't a wrapped part's. Walls under two mesh cells
break up (lint W102): keep `thickness` at least twice the mesh step.

Cloth folds, relief fur and soft colour borders: `kiln docs surfaces`.

## Parts

Part notation: every shape and part option (blend, cut, mirror, array, shell, fit, on, folds, density, ...).

### Parts

Each part is one shape plus options. Parts are combined **in order**: each one joins (or cuts) what came before.
Hard surfaces, hardware (rivets, bands, planks, garments), patterns: `kiln docs surfaces`; decals and textures: `kiln docs textures`.

```yaml
parts:
  - capsule: { from: [0, 0.3, 0], to: [0, 0.75, 0], radius: 0.3 }   # the shape and its parameters
    id: body                   # optional: which bone/node it belongs to (default: root)
    color: red                 # palette colour name
    material: plastic          # a style material preset (default: default)
    blend: 0.04                # smooth join radius with what's before it (0 = crisp seam)
```

#### Shapes

Every shape takes `at: [x, y, z]` (its centre; default [0, 0, 0]) and `rotate: [x, y, z]` (degrees, applied x
then y then z, about its centre).

| shape | parameters |
|---|---|
| `sphere` | `radius` |
| `ellipsoid` | `radii: [x, y, z]` |
| `box` | `size: [x, y, z]`, `round` (edge radius; size kept) |
| `cylinder` | `radius`, `height` (along y), `round`, `sides` (8: an octagonal prism, a flat side facing +z; `radius` reaches its corners, its flats sit at radius x cos(180/sides)). `at` is its middle: half of it is below `at` (or `base: [x, y, z]`, its bottom centre, turned with it; or its ends with `aim`) |
| `cone` | `radius` (bottom), `radius_top` (0 = point), `height` (along y), `sides` (4: a pyramid). `at` is its middle, not its base: a tuft set `at` a surface is half buried (`base:` places its bottom centre instead). Stand it on a point with `aim: [[base], [tip]]` (y runs base to tip; without a `height`, the distance between them) |
| `capsule` | `from: [x, y, z]`, `to: [x, y, z]`, `radius`, `radius_to` (taper) |
| `tube` | `points: [[x, y, z], ...]` (2+; straight unless `smooth: true`), `radius`, `radius_to`: ropes, branches, rails, tails |
| `lock` | `points` (2+), `width`, `thickness`, `width_to`, `thickness_to`, `facing: [x, y, z]`, `smooth` (as tube): a flat blade along a path (fur and hair locks, feathers, leaves, petals); `width_to: 0` is a pointed tip; the flat sides look along `facing` |
| `torus` | `radius` (ring), `thickness` (tube radius); ring in the xz plane (rotate for others) |
| `lathe` | `profile: [[r, y], ...]` spun around y: vases, bottles, bells, caps, chess pieces, round towers. The profile is a closed outline in the (radius, height) plane: go up the outside and come back down the axis (points with r = 0), e.g. a cap `[[0, 1.06], [0.2, 1.02], [0.3, 0.9], [0.3, 0.8], [0, 0.8]]`. Corners are rounded (`smooth: true`, default); `smooth: false` keeps them sharp |
| `extrude` | `points: [[x, z], ...]` outline seen from above (3+ different points; repeats and a closing point are dropped), `height` (along y; `at` is the middle of its height, as a cylinder's), `round`, `holes: [[[x, z], ...], ...]` (outlines cut through: letters O, A, B; `round` rounds their edges too; hard parts: hole edges stay sharp), `offset` (grow the outline by metres, < 0 shrinks: inset face plates). Or `path: "M 0 0 L 1 0 Q 1 1 0 1 Z"` (SVG path data: M L H V C S Q T A Z, absolute and relative; y runs down onto z, so `rotate: [90, 0, 0]` stands it up reading right from the front) with `path_scale` (metres per unit: 0.001 for a 1000-unit font em) and `path_tolerance` (0.002 m): every subpath is an outline, even-odd (counters are holes, separate shapes are islands). Or `text: "OPEN"` in `font: fonts/sign.ttf` (.ttf/.otf, relative to the project folder) with `text_size` (metres per em, 0.1), `text_align` (left, center, right: about x = 0), `letter_spacing` (metres), `line_spacing` (ems, 1.2; `\n` starts a line), `font_axes` (a variable font's instance: `{ wght: 900 }`; default: its default instance): first baseline at z = 0, glyphs toward -z; no kerning or shaping. Glyphs fill like fonts do (nonzero): overlapping contours join instead of cutting holes. Check the font's licence before shipping its shapes. Shields, signs, floor plans, stars, letters |
| `wedge` | `size: [x, y, z]`: a roof (ridge along x at the top) |

`sides` (3-64) also works on `lathe` and `torus`, and on `sphere`, `ellipsoid`, `capsule` and `tube` for hard parts.
`sides` makes a part hard (exact polygons: no blend, folds or pixel patterns on it).

For `capsule` and `tube`, the points are in the part's frame (moved by `at`, turned by `rotate`). Everything else in a
model (decal `at`, rig pivots, poses' offsets) is in model space.

#### Part options

| option | meaning |
|---|---|
| `id` | bone/node name (lowercase). Parts sharing an id move together. No id = `root`. |
| `color` | palette colour name (required for adding parts) |
| `material` | style preset: default, plastic, paint, fabric, skin, leather, rubber, wood, stone, metal, gold, leaf, glass, glow |
| `emission: 0.6` | this part's glow strength over its preset's (eyes softer than a crystal). A glowing colour's strength is capped so it keeps its hue (its brightest channel x strength at most 0.75), so for bright colours a higher number changes nothing (a dark red can glow at 3, a pale pink tops out under 1); its lit colour is dimmed: the glow carries it |
| `blend` | smooth-union radius in metres with everything before it (cuts/intersects: smooth edge) |
| `color_blend` | metres its colour fades into blended neighbours' (`surfaces`) |
| `resolution: 0.004` | a finer mesh cell inside this part's box than the model's (a face, hands): the mesh there is split down to it and moved onto the surface, so lids, nostrils and a nose show on a coarse body; give it `density` too, or the budget reduces it away |
| `density: 3` | weight on the triangle budget (0.25-8, default 1): about 3x the share of the budget it would get, at the same total (a face); 0.5 coarser. Not past its full-resolution mesh; hard and kept parts ignore it |
| `cut: true` | remove this shape from everything before it (holes, slits, windows, eye sockets); an `id` or `mirror_id` on a cut only names it (it moves with nothing) |
| `cut: [case, lid]` | cuts only the parts with these ids (`cut: lid`: one); those parts are then meshed as their own surface (crisp against the rest), so the pad under a watch case or a tray's screws stay whole |
| `cut: true` + `color: black` | the walls the cut makes are painted (an inked groove, a clasp's lid line, panel lines; `material:` too); the surface round it keeps its colour. Not in `--draft` |
| `intersect: true` | keep only what's inside this shape (trim) |
| `mirror: x` | also on the other side of 0 (x, y, z or a list); same id. Write the part on either side |
| `mirror_id: arm_r` | with `mirror: x`: the copy is a separate part with this id (rig entries are mirrored too) |
| `array: { count: 4, step: [1, 0, 0] }` | repeat in a row |
| `array: { count: 8, around: y, center: [0, 0, 0], angle: 360 }` | repeat in a ring (`around` may be any direction `[x, y, z]`: a ring on a tilted wheel). The first copy is the part as written; the others turn about `around` through `center`, counter-clockwise seen from the tip of `around` (right-handed: +90 degrees about y takes +z to +x), and each copy is turned with the ring, not only moved (it faces outwards as the first does, also on a tilted axis). `angle` under 360 is an arc from the part as written to `angle`, both ends included (count - 1 gaps); negative runs clockwise. A fringe across the back only: write the first tuft at one end, e.g. at `[0.1, y, -0.1]` (the model's left is +x, its back -z), and give the arc's span: `angle: 90` ends at `[-0.1, y, -0.1]`. A full ring's count spreads evenly (no copy at 360) |
| `shell: 0.02` | hollow, walls this thick (centred on the surface) |
| `shell: { thickness: 0.02, open: -y }` | a wall inside the surface (the outside stays put), one side cut open at the shape's centre: helmets, bowls, pots, shields with a visible rim (`side: both` centres it) |
| `fit: head` or `fit: { to: head, gap: 0.01 }` | with `shell`: the wall wraps the parts with that id, `gap` away from them, wherever this part's own shape reaches (its shape is the coverage: a sphere around the head, `open: -y` and placed low enough to cover the cheeks). Helmets that sit on the head instead of perching on it; cut a face opening after it (before the head, so the cut doesn't take the face) |
| `twist: 90` | degrees per metre about the shape's y axis |
| `blend_to: torso` (or a list of ids) | with `blend`: melt only into those earlier parts, meet every other part crisply. If this part has `mirror_id`, its copy melts into the mirrored ids (name one side); with plain `mirror`, name both |
| `detail: true` | only in the model's baked normal map (`normal_map:`), never in the mesh: grooves between fur strands (a thin `cut: true` tube), wrinkles, knuckle creases, scratches, fine `noise` on a coarse, light mesh. Lint W121: no map, or thinner than two texels. A texel is about sqrt(2 x surface area) / map size (a 2.4 m character, about 4 m² of surface, at 2048: ~1.5 mm; small maps with many charts are coarser, and lint measures the real one): grooves read when about 4 texels wide or more; finer ones blur out (each texel is filtered), and deep narrow ones make bright specular lines: shallower and wider, or `normal_strength: 0.5` |
| `scale: [1, 1, 0.4]` | stretch the shape in its own frame (or one number); soft parts only |
| `noise: { amount: 0.01, scale: 0.2, seed: 3 }` | lumpy surface (rocks, bark, clay): amount in metres, scale = bump size. Colour borders with other parts follow the smooth shapes, so a patch on a noisy part keeps a clean edge |
| `folds: { count: 12, depth: 0.02, from_y, to_y }` | cloth folds round the part's own axis, deepest at the hem (`surfaces`) |
| `pattern: {...}` | a second colour painted on the part (`kiln docs surfaces`) |
| `gradient: { to: fur_light, steps: 3 }` | the part's colour going to `to` in `steps` bands (2-16, default 3), mixed in OKLab; `from:` replaces the part's colour at the start. `along: path` (the default for tube, capsule and lock: first point to last) or `x`/`y`/`z` (the default for other shapes: across the shape's own box, low to high). Patterns paint over it; variants recolour the mixed bands from the swapped ends |
| `decal: {...}` | an image on the part (`kiln docs textures`) |
| `texture: {...}` | an image tiled over the whole part, box, triplanar or cylindrical, crisp when small, palette-indexed or generated (`kiln docs textures`) |
| `loose: true` | this part may float free (flames, bees, sparks, rubble): W103 doesn't count it |
| `blend: none` | a hard part, joined crisply (`kiln docs surfaces`) |
| `hard: true` / `false` | make this part hard (exact polygons) or smooth, whatever the style says |
| `chamfer: 0.02` | hard parts: one flat band cut along every edge (box, wedge, cylinder, cone, extrude; a lathe: its outline's corners) |
| `bevel: 0.02` | hard parts: rounded edges in `segments: 1-4` flat bands (default 2); where an extrude outline is thinner than about twice the bevel (font serifs, hairlines) it flattens there to fit |
| `keep: true` | this detail survives every reduction (LODs) as its own small mesh, sitting in the surface around it. Crisp (`blend` 0) parts smaller than 2% of the model are kept anyway (rivets, pupils, studs); `keep: false` opts out |
| `aim: [[x, y, z], [x, y, z]]` | points the shape's own y axis from the first point to the second and puts it halfway (instead of `at`); a shape with a `height` that doesn't give one gets the distance. `{ from, to, roll: 30 }` spins it about that line; `rotate` turns it in its own frame first. Arrows, spears, struts, beams at any angle |
| `on: { part: body, near: [x, y, z] }` | instead of `at`: placed on the blended surface of earlier parts, its y axis along the normal there; `offset`, `roll`, `align: false` (`making`) |
| `attr: { heat: 0.9 }` | named numbers a shader reads per vertex (heat, opacity, wind weight); faces of parts without it get 0. Each becomes a custom glTF attribute `_HEAT` (Blender, three.js; Godot 4.7 drops custom attributes), and the first name (alphabetical) also goes in COLOR_0's alpha (Godot: `COLOR.a`; white RGB unless `vertex_colors`). Manifest `attributes` |
| `uv: cylindrical` | texture coordinates projected from the part's shape, in its own frame (they follow `rotate`, mirror, arrays): `cylindrical` (u around, v along the axis over the part's box), `spherical`, `box` (per face, metres / the box's largest side), `along` (tubes and capsules: v = distance along the path, 0..1). `{ project, axis: y, scale: [1, 4] }`. Written to TEXCOORD_0 (Godot UV), or TEXCOORD_1 (UV2) when the atlas or a decal uses the first; manifest `uv: {set, parts}`. Other faces get (0, 0) |

Order matters: details that sit on a surface come **after** it. A part completely inside later parts shows nothing
(W101). A cut removes material from what came before it, and paint follows: a door placed after the cut that made its
archway is painted as the door, not as the wall. Parts thinner than about two mesh cells break up (W102): resolution comes from the style (soft_toy: 8 mm
for a ~1 m model, coarser for bigger models: x sqrt(size), and at most 256 cells across). `kiln lint` and `kiln build`
print the cell size each model got and what set it (model or style resolution, the size scaling, a max_cells cap;
manifest `step`, lint `--json` `cells`); a long build's meshing line says it too. Finer detail on a hero: `resolution: 0.004` and `max_cells: 640` in the model
(lint W120 names the max_cells needed). Halving the cell size about doubles build time (`kiln docs build`); the budget still
decides the final triangles.

Posing a group (a hunched back, a head thrust forward) without retyping its parts: `transforms: [{ ids: [head, neck,
arm_l], rotate: [x, y, z], pivot: [x, y, z], move: [x, y, z] }]` at the top of the model turns the listed parts (arrays
keep their copies) about `pivot`, then moves them; their rig pivots and sockets go with them. Items apply in order.
A `mirror: x` part takes only turns about x and moves in y/z (anything else breaks its mirror: E003).

Scenes (other models placed in this one: `instances:`) and assemblies (`mount:`, `kiln fit`): `kiln docs scenes`.

## Templates

The template library: bodies, heads, helmets, armour to extend.

### Template library

`kiln library` lists KILN's own templates: bodies (`body_slim`, `body_stocky`, `body_big`: standard joints, layered
clothes, gloves, boots, a `grip` socket per hand), heads (`head_young`, `head_old`, `head_bearded`, `head_stern`,
`head_goofy`, `head_female`), helmets (`helmet_kettle`, `helmet_nasal`, `helmet_barbute`, `helmet_great`,
`helmet_sallet`, `helmet_crown`: detachable, fitted to whatever head they go on) and armour (`armour_breastplate`,
`armour_pauldrons`, `armour_gauntlets`, `armour_cape`, `armour_hood`: shells fitted to the body). For toy
proportions (soft_toy: a head about half the height, big eyes) use `body_toy` with `head_toy` (the other heads sit at
an adult's neck). `kiln library <name>` prints one template's YAML: its parts, ids and sizes. Combine them:

```yaml
name: sergeant
class: character
extends: [body_stocky, head_bearded, helmet_nasal, armour_cape]   # in order; a project template of the same name wins
variants: { blue: { swap: { cloth_red: cloth_blue } } }
animations:
  walk: { import: imports/Rig_Medium_MovementBasic.glb, clip: Walking_A }
```

or `kiln new model sergeant --extends body_stocky,head_bearded,helmet_nasal,armour_cape`. Their colours are the
library palette `people` (found without copying; copy it into palettes/ to change it). `extends` takes a list (bases
combine in order); `cut: <id>` (or `[ids]`) cuts only those ids (a helmet's face opening, not the face); `fit: { to: [ids] }` wraps
several parts. Fitted shells are their own meshes.

The heads' hair is the id `hair`, folded into `head` (`fold: true`, see Rig and skin), so helmets fit over it and
follow its lumps. To hide it under the helmet instead (as KayKit's helmets replace the hair), add to the model:

```yaml
rig:
  hair: { parent: head, revealed: [helmet], fold: true }   # hair hidden until the helmet (id helmet) comes off
```

The hair is then its own piece, hidden by the scenes and previews until the helmet comes off, and the helmet fits the
skull (`to: head`). Without a helmet it folds back into `head`. Leave it out for a crown (worn over the hair).

## Styles

Styles and inspirations: presets, extends, the look kit; style notation.

### Styles and inspirations

A style (`styles/<name>.style.toml`, usually `extends = "soft_toy"` or another preset) decides: smooth or faceted
(`[shape]`), mesh resolution, triangle budgets per class, material presets (roughness, metal, glow, rim) and the
look kit (`[look]`: shader standard/toon (bands, softness, shadow colour, specular, banded shadows), outline
(metres or pixels, one colour or each part's darkened), tonemapper, exposure, saturation, contrast, SSAO, glow, sky,
sun, fog). The `notes` field holds the shape language and proportions in words: write it, and follow it.

From inspirations: look at the images; describe shapes (rounded? chunky? faceted?), proportions (head size, limb
thickness, eye size), colour (how saturated, how many per object), materials (glossy? matte?) and light (soft?
warm? outlines?). Pick the closest preset, `kiln style new <name> --extends <preset>`, override what differs, write
the notes, make one test model, compare with `kiln preview <model> --vs`, adjust, and get the owner's yes before
making more. Inspiration images are reference only: never copy another game's characters, and never model real
people.

Changing the look later: edit the style (and the palette): every model follows on the next build. If models
themselves must change, `kiln style bump -m "why"`; `kiln status` then flags older models for review.


### Styles

```toml
# styles/sky_pirates.style.toml
description = "Chunky toy airships, warm sunset light"
extends = "soft_toy"           # soft_toy | low_poly | toon | clay | diorama | skin | another project style
notes = """Shapes, proportions, colours, materials, lighting in words (agents follow this)."""

[shape]
smooth = true                  # false = faceted (flat normals)
sharp_angle = 50               # smooth styles: edges sharper than this stay crisp
resolution = 0.008             # metres per mesh cell for a ~1 m model (finer = rounder, slower)
color_blend = 0.0              # metres: smooth parts blending into another colour fade into it (a part's own wins; 0 there: crisp)
max_cells = 256                # mesh cells across a model at most (64-1024): bigger models get coarser cells past it
scale_with_size = true         # models over 1 m get resolution x sqrt(size); false: resolution as is

[budgets]                      # triangles per class
character = 8000
default = 4000

[materials]                    # roughness, metallic (0..1), emission (glow strength, capped per colour: see parts), rim (soft edge light), alpha (0.05-1: see-through)
                               # grain (0..1): a fine bumpy finish in the normals, no geometry (rough cloth, felt), grain_size (m per bump, 0.01);
                               #   KILN's Godot scenes (standard looks) and previews; not on textured or normal-mapped faces
plastic = { roughness = 0.42 }

[look]                         # the Godot look kit and preview lighting
shader = "standard"            # standard | toon
toon_bands = 3
toon_softness = 0.0            # toon: 0 = hard band steps; up to 1 = each edge blends over a whole band (0.2-0.4: soft cel)
toon_shadow_color = ""         # toon: "" = shadows only darken; "#rrggbb" or a palette colour = the sun's missing light in
                               # that colour (warm/cool shading; a light colour tints more; per model with its palette)
toon_specular = 0.0            # toon: one hard highlight blob, strength 0..1 (size grows and strength fades with roughness)
toon_shadows = "soft"          # toon: soft = Godot's received shadows; band = they drop into the darkest band (Godot only)
outline = 0.0                  # metres (toon outlines), 0 = none; pixels with outline_space = "pixels" (e.g. 2)
outline_color = "#1a1420"      # or "darken": each part's own colour, darkened
outline_space = "metres"       # metres: a shell that thins with distance; pixels: constant thickness on screen
tonemapper = "filmic"          # linear | filmic | aces | agx (previews match filmic exactly; aces and agx closely)
                               # `kiln style check` shows each palette colour lit: a warm, bright look drifts orange to gold
exposure = 1.0
saturation = 1.15
contrast = 1.0
ssao = true
glow = true
ambient = 0.9
sky_top = "#4f8fe0"
sky_horizon = "#bcd7f2"
ground = "#a9c48f"
sun_pitch = -48.0              # degrees (negative = from above)
sun_yaw = 30.0
sun_energy = 1.1
sun_color = "#fff6e8"
fill_energy = 0.0              # a second, weaker sun without shadows (0 = none; skin: 0.3): the shadow side keeps colour and form
fill_pitch = -20.0             #   without raising the ambient everywhere; Godot: a "Fill" DirectionalLight3D, previews the same
fill_yaw = 210.0               #   default: opposite the sun
fill_color = "#dde8ff"
shadows = true
compat_shadows = false         # Godot's Compatibility renderer: the sun drops its shadows there, since that renderer adds the
                               # ambient again per shadowed light (godotengine/godot#90259: several times too bright); true keeps them
fog = 0.0
fog_color = "#c8d8e8"
rim_light = 0.0                # an added fresnel rim on every surface (Godot: a next pass; previews too): 0.5-1 reads on bright skies
rim_light_color = "#ffffff"
rim_light_power = 3.0          # higher: thinner rim
post = ""                      # "retro": a low-res, fixed-palette, dithered screen (see Retro looks); "paint": dabs; "" = none
post_lines = 200               # retro: vertical resolution (200: CGA / Atari ST; 400: ST mono)
pixel_aspect = 0.8333          # retro: pixel width / height (320x200 on a 4:3 screen: 5/6; 640x400: 1.0)
post_palette = "cga"           # retro: the palette every pixel is snapped to (palettes/ or KILN's library), at most 16 colours
dither = "bayer4"              # retro: bayer4 | bayer8 | none | halftone | lines | hatch | noise
dither_strength = 1.0          # retro: 0 (nearest colour only) to 1 (full ordered dithering)
dither_space = "screen"        # retro: screen | view (steady while the camera turns) | world (fixed to surfaces; Forward+)

[shade]                        # shade paint baked into the vertex colours (off by default; each 0 to 0.9)
cavity = 0.25                  # crevices darker: x the field's occlusion (as atlas_ao)
top = 0.12                     # the top keeps its colour; sides darker by this, undersides too
under = 0.1                    # undersides darker still
```

**Shade paint** is the hand-painted look: dark crevices, tops at full colour, shaded sides and bellies, in any colour
mode. It is a grey multiplier per vertex corner in COLOR_0 (glTF multiplies it into the base colour; KILN's Godot scenes and the previews
use it), so it follows the mesh's resolution. A model with a base colour map (relief, `color_blend`) gets it per
texel in `<name>.color.png` instead, from the normal map's normals (relief tilts and grooves count) and the occlusion
at each texel, with the same strengths; its mapped faces then carry no COLOR_0. A model's `shade: { cavity: 0.3 }` goes over its style's fields. Vertex
colours can't go above 1, so `top` darkens everything that doesn't face up rather than lighten the top: pick base
colours for the lit top. Typical: `cavity` 0.2-0.4 for creatures and props with grooves, `top` 0.1-0.15, `under`
0.1. Without the atlas `atlas_ao` doesn't apply; `shade.cavity` is the same occlusion. Gibs get their own shade, from the piece's own shape (a
crevice where it was attached is open once it comes off). With `vertex_colors = true` and `variant_glbs = false`,
COLOR_0 holds the colours times the shade, so an engine recolouring from the manifest's `swap` table matches by
colour within a tolerance, or turns `variant_glbs` on (each variant its own shaded glb).

Every toon key is off by default (today's plain cel look). A painterly cel look: `toon_softness = 0.2`,
`toon_shadow_color` a cool mid tone, `toon_specular = 0.6` on glossy materials, `toon_shadows = "band"`,
`outline_space = "pixels"` with `outline = 2` and `outline_color = "darken"`. Previews follow every key except
`toon_shadows` (the software renderer has no cast shadows; `kiln preview --engine` shows them in Forward+ and Mobile
projects, and on Compatibility only with `compat_shadows = true`).

### The skin preset: stylised game skins

`default_style = "skin"` (or `extends = "skin"`) turns the painted game-skin look on without setting each option:
matte materials (no rim, no shine on skin, fur and cloth), `[shape] color_blend = 0.03` (every smooth part that blends
fades its colour into its neighbours'), `[shade]` on (cavity 0.3, top 0.12, under 0.1), larger budgets, and a soft
look kit (high ambient, warm sun). Fur goes on as relief, faces get `density`. A worked example (builds in ~25 s):

```yaml
name: critter
class: creature
parts:
  - ellipsoid: { at: [0, 0.45, 0], radii: [0.28, 0.4, 0.24] }
    id: body
    color: fur_brown
  - ellipsoid: { at: [0, 0.42, 0.14], radii: [0.18, 0.26, 0.13] }
    id: belly
    color: fur_light            # fades into the body: the style's color_blend
    blend: 0.06
  - sphere: { at: [0, 0.98, 0.02], radius: 0.2 }
    id: head
    color: fur_brown
    blend: 0.08
    density: 2                  # more of the budget on the face
  - ellipsoid: { at: [0, 0.94, 0.19], radii: [0.09, 0.07, 0.07] }
    id: snout
    color: fur_light
    blend: 0.04
relief:
  - { on: [body, head], length: 0.07, width: 0.035, lift: 0.006 }
```

Eyes, teeth and claws: a crisp seam (no `blend`) keeps them out of the fade, or `color_blend: 0` on the part (that
border stays crisp from both sides). The style's fade skips parts made hard (`hard_surface`, `bevel`, `blend: none`)
and parts blending only into their own colour (a one-colour prop bakes no map), and stays off when baking isn't
installed (`kiln-gen[bake]`).

### Retro looks

`retro_st` (Atari ST colour: 320x200, 16 colours), `retro_cga` (CGA: 320x200, black/cyan/magenta/white) and
`retro_mono` (ST mono: 640x400, black and white) draw every frame at a low resolution, snapped to a fixed palette with
ordered dithering (`[look] post = "retro"`). They extend `low_poly` (faceted, flat colours) with hard toon bands, so
light falls into a few clean dither patterns. `kiln init --style retro_cga` writes the matching hardware palette as
`main`, so models paint with colours the screen can show.

- Godot: the look kit (`looks/<style>.tscn`) carries the pass as a CanvasLayer over the whole screen: put the look kit
  in the scene (it takes no input). kiln.toml `looks = ["retro_st", "retro_cga", "retro_mono"]` builds kits no model's
  style asks for, so a game can switch looks at runtime (the demo's showcase: L). The layer is 100: canvas layers
  below it (a HUD) are pixelated and dithered too; put UI that should stay sharp on a layer above 100. Keep
  `rendering/viewport/hdr_2d` off (Godot's default): the pass reads the screen as sRGB.
- Previews draw the same pass, treating each tile as a screen `post_lines` tall; `kiln preview --no-post` shows what's
  under it. `--engine` renders through the real shader (its background comes out black: a game's screen is opaque).
- Method, per low-res pixel: one sample at its centre, the two nearest palette colours, and the pattern's threshold
  choosing between them by how far the colour lies from the first to the second. Patterns: `bayer4`, `bayer8` (fine
  ordered dither), `halftone` (round dots on a 45-degree grid), `lines` (horizontal bands), `hatch` (diagonal lines,
  crossing as it darkens), `noise` (blue-noise-like), `none` (flat posterised colours).
- Runtime: every setting is a shader uniform, and the look kit's `Retro` node is the API: `set_enabled(false)` shows
  the plain render, `set_lines`, `set_pixel_aspect`, `set_strength`, `set_pattern("hatch")`,
  `set_palette(PackedColorArray)` (1-16 colours), `get_settings()`. Each kit instance has its own material.
- Your own palette: copy `cga.pal.yaml`, `atari_st.pal.yaml` or `st_mono.pal.yaml` from KILN's library (they carry
  PAGAN's `hardware:`, so `pagan lint` keeps edits legal), and set `post_palette` in a project style that extends a
  retro preset. A hardware palette's colours are checked when KILN loads it (E004 names the nearest legal colour).
- Model for it: big flat colour areas, few colours per object, strong silhouettes; parts under a few pixels vanish.
  The dither is in screen space by default, so it shimmers when the camera moves: slow or fixed cameras suit it.
- View-space dither (`dither_space = "view"`, or `set_space("view")`): the screen pattern is shifted by the camera's
  yaw and pitch in whole blocks, so turning moves the pattern with the image instead of re-dithering it (measured:
  after a 6-block turn 96% of the centre's blocks are unchanged, against at most 82% in screen space). Cells stay on
  the low-res grid; the match is exact at the centre and drifts a little towards the edges; walking still shimmers.
  Any renderer and pattern, with a perspective camera (others keep screen space); the cheapest fix for first-person
  crawl. Pairs well with turning in whole-block steps.
- World-space dither (`dither_space = "world"`, or `set_space("world")` on the Retro node at runtime): the pattern is
  fixed to surfaces, so it stays put as the camera moves instead of crawling. A full-screen quad in the look kit
  (`Retro/World`) reads the depth buffer, takes each block's pattern cell from the block centre's world position
  (triplanar, flat per face) and dithers there; the canvas pass then only snaps to the palette. Cells are a block's
  footprint rounded up to a power of two metres per axis, so the pattern never goes finer than a block and steps
  (rather than swims) with distance. Trade-offs: cells come out 1 to 2 blocks wide, so ordered patterns (bayer,
  halftone, hatch, lines) look irregular (doubled rows and columns) and receding floors show wood-grain moire;
  `dither = "noise"` reads cleanly (a stable grain on each surface) and suits world space best. The sky gets coarser
  cells on a cube of view directions. Transparent surfaces draw over the dither and are snapped to the palette
  undithered. The colour maths assumes the linear tonemapper (all retro presets). Forward+ only: on Mobile and
  Compatibility the kit stays in screen space (`set_space` warns). Every camera of the World3D draws the quad,
  SubViewports too (a minimap comes out dithered as well). Previews (`kiln preview`, also
  `--engine`) draw screen space.

### Paint look

`paint_pointillist` (`[look] post = "paint"`, extends `soft_toy`) redraws every frame as overlapping dabs of pure
colour from `post_palette` (the library's 16-colour `pointillist`: pastels, violets for shade, no black or grey) that
the eye mixes. It is the retro pass's second mode: one dab per cell (`post_lines` rows, `pixel_aspect`), jittered,
turned and slightly irregular; each takes the scene's colour and coverage at its centre, graded (more colour, shadows
towards violet, lifted towards white), and becomes one of its two nearest palette colours by its own random
threshold (`dither_strength` 0: always the nearest). `dither` is not read (it is the pattern after `set_mode(0)`);
`dither_space` is `screen` or `view` (steady while the camera turns; walking slides the dabs), not `world`. Smooth
shading suits it and models keep any palette. Runtime, on the `Retro` node: `set_mode(1)` (0: retro blocks; a
world-space kit draws dabs in screen space) and `set_paint(name, value)`, clamped: `dab_size` (0.2-2 cells),
`dab_jitter`, `dab_aspect`, `dab_angle`, `dab_turn`, `dab_round`, `dab_skew`, `vivid`, `lift`, `shadow_hue`, and
the Colors `shadow_tint`, `ground`; not style keys yet. Previews draw the dabs too (other dabs than a GPU rolls: the
same look, not the same frame).

## Rigs

Characters, rigs, skins and sockets; rig notation.

### Characters, rigs and animation

- **Characters for the soft styles:** bean/pear body (one capsule, radius 0.25-0.35), stubby limbs (capsules
  0.07-0.1 thick), big eyes (white sphere ~0.1 + black pupil ~0.04 pushed slightly forward), tiny or no mouth.
  Hats, helmets, hair: separate shapes on top, crisp seams. Heads on caricatures: an ellipsoid blended into the
  body with a big nose ellipsoid blended in. Keep hands simple (a sphere or mitten).
- **Rig** what moves: give it an `id`, then `rig: { id: { pivot: [joint], parent: id } }`. Pivots are the joint
  positions (hip, shoulder, hinge, axle). Without a pivot a part turns about its box centre (W109); `skeleton: humanoid` joints get theirs at the joint.
- **Skin:** `rigid` (each part moves as one piece: robots, machines, props, toys) or `soft` (one mesh that bends
  where parts blend: creatures, bean characters). `separate: true` keeps a part rigid inside a soft skin
  (detachable helmet). Rigid joints that turn far (ragdolls): `union: per_bone`, so no turn opens the mesh.
- **Animations:** explicit `poses` (one per frame, per part: offset/rotate/scale) or a `cycle` that writes the
  poses for you: walk, waddle, hop, bob, spin, swing, breathe, wave, chain (`kiln docs animations`). Both together: the cycle
  moves everything, and parts named in the poses follow the poses (walking while carrying).
- **CC0 clip libraries:** a `skeleton: humanoid` character plays imported clips
  (`walk: { import: imports/clips.glb, clip: Walking_A }`); any other skeleton (quadrupeds, birds) plays them through
  `skeleton: { map: { <part id>: <clip joint>, ... }, root_motion: <clip joint> }` (`kiln docs humanoids`, "Clips on any skeleton").
- **Cloth and flags:** split them into 3-4 segments along their length, each its own id parented to the previous one
  (pivots on the seams), crisp seams (`blend: 0`), `skin: soft`, and animate with `cycle: { type: chain, parts: [...] }`. Check every animation with
  `kiln preview <name> --pose <animation>`: the filmstrip shows each frame from 3/4 front and both sides; `--views`,
  `--pitch` and `--size` pick the views and tile size, `--frame 3` (or `0,4`, for every `--pose`) one frame up close.
- Gameplay data on parts: `rig: { helmet: { meta: { hitzone: head, detachable: true, socket: [0, 1.6, 0.1] } } }` ->
  node metadata in Godot and in the manifest, which also gives every part's box (`aabb`) for hit zones.
- Detachables (`separate: true`) are meshed on their own, so they may overlap the body and leave no hole when removed.
- Soft skins weigh each vertex by its distance to every bone's parts, softly over the blend: a sleeve blended into the
  chest half-follows the chest when the arm lifts (a smear down the side). `skin_falloff: 0` on a part keeps the
  surface painted as its bone on that bone alone, except where that paint meets another bone's (one edge ring stays
  blended, wider on coarse LODs); a number fades it over within that many metres of that border (e.g. 0.03). Set it on
  the chest too to keep the torso still. Lint W129: it does nothing on rigid skins and hard, kept or separate parts.
- Points the game needs on a part (a weapon's muzzle, a hand slot, a catapult's load, a seat): `sockets` in the rig
  entry; they become nodes that move with the part.


### Rig and skin

```yaml
rig:
  leg_l: { pivot: [0.12, 0.26, 0] }                 # joint position; parent defaults to root
  arm_l: { pivot: [0.3, 0.6, 0], parent: root }
  head:  { pivot: [0, 0.8, 0], meta: { hitzone: head, seat: [0, 1.56, 0] } }
  helmet: { parent: head, meta: { detachable: true }, separate: true }
  arm:   { pivot: [0, 1.6, 0], sockets: { tip: [0, 3.9, -0.2], load: [0, 3.6, -0.5] } }
skin: soft
```

- Every part id is a bone/node. `pivot` is where it turns (hip, shoulder, hinge, axle); default: its box centre.
- A rig entry for `arm_l` also rigs its `mirror_id` twin (pivot mirrored; parent mapped to its twin if any).
- `skin: rigid`: each id is a separate mesh node that moves as one piece. By default all parts are one surface, cut
  where bones meet: fine while joints stay near their bind pose. `union: per_bone` makes each bone's parts their own
  closed surface; neighbouring bones overlap instead (a few hidden triangles), so turning a joint far (a ragdoll, an
  arm along the chest) never opens a hole. Blends between parts of different bones are then lost.
- `skin: soft`: one skinned mesh; weights come from each part's distance, so blended joints bend smoothly.
  `separate: true` makes a part its own closed, rigid mesh (detachable things): it may overlap the body (a helmet
  on a head) without fusing, and removing it leaves no hole. `under: { color: hair }` (with `separate: true`) paints
  the body where the part covers it (hair under a helmet; `material`, `gap`: how far from it still counts, 0.02 m),
  seen once it falls off. Check with `kiln preview <model> --detach`.
- `revealed: [arm_l]`: a part shown only once one of those is gone (a stump cap at the shoulder, under a
  detachable arm). It is its own piece (separate), hidden by KILN's .tscn scenes, `kiln_revealed_by` in its node's
  extras and `revealed_by` in the manifest's part: the game shows it when it removes the arm. Mirrored twins
  are revealed by the twins (`arm_r`). Previews (and `--vs`) leave it out like the game does; `--detach` shows it
  under the part taken off.
- `fold: true` (with `parent`): while none of its `revealed` parts is in the model, the part folds into its parent:
  its parts take the parent's id (and blend with it) and the entry goes, as if it had no id of its own; with one
  there, it's an ordinary revealed part. Without `revealed` it always folds: the library heads rig their hair
  `hair: { parent: head, fold: true }` (one `head`, as before the hair had an id), and a model opts in to hiding it
  under a helmet with `hair: { parent: head, revealed: [helmet], fold: true }` (see Template library).
- `gib: true` (or `gib: [upperarm_l, lowerarm_l, hand_l]`): the part comes off as a piece of its own. Besides the model,
  `kiln build` writes `models/<name>.gib.<id>.glb`: that part (and, with `true`, every part hanging from it) meshed on
  its own, so it's closed where it met the body; static, at rest, in the model's frame (same origin as the model's glb),
  plain materials (a relief model's gib keeps its fur and fades on a quarter-size map, embedded). Manifest: `gibs: { <id>: { glb, parts } }`. Mirrored twins get theirs. Pair it with a `revealed`
  stump cap on the body.
- `meta`: plain values or flat lists (points: `[x, y, z]`, model space) for game code: Godot node metadata
  (`get_meta("extras")`; on soft skins, bone metadata: `skeleton.get_bone_meta(i, "extras")`) and the manifest.
  Mirrored twins get the same meta (not mirrored).
- `sockets`: named points on the part (model space, as built): a muzzle, a hand slot, a trebuchet's load. Each is an
  empty child node `<id>_<name>` that moves with the part (Godot: a Node3D under a BoneAttachment3D on soft skins), and
  the manifest gives its position and its offset from the pivot. Mirrored twins get mirrored sockets.

## Animations

Animation notation: poses, cycles, imported clips.

### Animations

Names are letters, digits, `_` or `-`, any case (imported clips can keep their library names: `Idle_A`); two names
that differ only in case are an error.

```yaml
animations:
  wave:
    fps: 8
    loop: false                # default true (Godot loops it: glTF name "<name>-loop")
    interpolation: linear      # linear | step
    poses:                     # one per frame; a missing part = its rest pose
      - {}
      - { arm_r: { rotate: [0, 0, -120] } }
      - { arm_r: { rotate: [0, 0, -150] }, root: { offset: [0, 0.02, 0] } }
  walk: { fps: 12, cycle: { type: waddle, legs: [leg_l, leg_r], arms: [arm_l, arm_r] } }
  carry:                       # a cycle plus poses: poses repeat over the cycle's frames, and a part named in a
    fps: 12                    # pose follows the pose instead of the cycle (walking legs + arms holding a crate)
    cycle: { type: walk, legs: [leg_l, leg_r], arms: [] }
    poses: [{ arm_l: { rotate: [-70, 0, 0] }, arm_r: { rotate: [-70, 0, 0] } }]
```

Pose fields per part: `offset: [x, y, z]` (metres), `rotate: [x, y, z]` (degrees, about the pivot), `scale: s` or
`[x, y, z]` (squash and stretch). Signs: positive x tips the part's top towards the front (+Z), so a hanging leg or arm
swings backwards with positive x and forwards with negative x; a drawbridge hinged at its bottom lowers forwards with
positive x. About z: negative raises a right arm (-X side), positive raises a left arm. About y: positive turns
left (counter-clockwise seen from above).

Point instead of turning: `aim: [x, y, z]` (a model-space point, metres) turns the part so it points there (from its
pivot to its only child's joint, else its own far end), the shortest way from where its parent leaves it.
`reach: [x, y, z]` on the upper of two parts (upper arm + forearm, thigh + shin) bends both so the lower one's end is
on the point (out of reach: straight toward it); `pole: [x, y, z]` picks where the middle joint goes (default: the way
the chain bends at rest; a straight leg's knee forward, other straight chains' joint back). One of rotate, aim and
reach per part; reach sets its child's turn. Raise a wand overhead: `upperarm_r: { reach: [-0.2, 2.1, 0.1] }` (a one-part arm: `arm_r: { aim: ... }`); reach on a part without exactly one child part is lint W132.
`kiln preview <m> --pose <anim> --json` lists each part's end per frame (`ends`) to check a pose without looking.

Cycles (8 frames unless the cycle says `frames:`, inside it: `walk: { cycle: { type: walk, frames: 16 } }`):

| type | options (defaults) |
|---|---|
| `walk` | `legs` [leg_l, leg_r] (a humanoid: upperleg_l/_r), `arms` [arm_l, arm_r] (upperarm_l/_r), `body` root, `swing` 30, `arm_swing` 25, `bounce` 0.02, `knee` 40, `knee_rest` 5, `elbow` 20, `lean` 0 (the `torso`, default spine, forward), `crouch` 0 (thighs forward, knees twice that) |
| `waddle` | as walk + `roll` 8 (side-to-side), `swing` 18, `knee` 20, `elbow` 15 |
| `run` | as walk: `swing` 45, `arm_swing` 40, `knee` 80, `knee_rest` 15, `elbow` 85, `lean` 10 |
| `sneak` | as walk: `swing` 20, `arm_swing` 10, `knee` 30, `elbow` 45, `lean` 15, `crouch` 15 |
| `hop` | `part` root, `height` 0.2, `squash` 0.1 |
| `bob` | `part`, `amount` 0.05 |
| `spin` | `part`, `axis` y, `direction` 1 |
| `swing` | `part`, `axis` y, `angle` 20 |
| `breathe` | `part`, `amount` 0.03 |
| `wave` | `arms` (the last one waves), `raise` 150, `angle` 20; an arm with a forearm below it (humanoids): the upper arm out to `raise` 80 degrees from hanging, the forearm `bend` 75 more, waving from the elbow by `angle` |
| `idle` | standing with life (try `frames: 24`, fps 8): `chest` (chest, else spine) `breathe` 0.02 and `sway` 2, `head` `look` 10 (holds to either side) and `nod` 2, `arms` `arm_sway` 3, elbows bent `elbow` 8 |
| `chain` | `parts` [ids in order from the root out; default: every id in file order], `axis` y, `angle` 15, `phase` 0.15: a travelling wave for flags, tails, tentacles, ropes |

Gaits bend lower limbs on a humanoid (`skeleton: humanoid`: lowerleg/lowerarm; listing `legs:` / `arms:` drops these
defaults) or what `knees:` / `elbows:` name: knees fold by `knee` while the leg swings forward, plus `knee_rest`;
elbows hold `elbow`, more as the arm swings forward. Then the feet stay level and the body rides so the lower ankle
stays where it was at rest (no floating or sinking; `bounce` is unused). Each limb swings about its own axis square to
the front, so a T-posed arm swings rather than twists. A model without lower limbs walks as before.

## Humanoids

Humanoids, CC0 clip libraries, clips on any skeleton, attachments for CC0 characters.

### Humanoids and clip libraries

`skeleton: humanoid` names a character's parts after the standard joints: `hips`, `spine`, `chest`, `head`,
`upperarm_l`, `lowerarm_l`, `hand_l`, `upperleg_l`, `lowerleg_l`, `foot_l` (and `_r`, usually by `mirror_id`;
optional `toes_l/_r`). Parents come from the standard hierarchy and pivots default to the joints (limbs at the end of
their longest capsule/cylinder/cone/tube nearest the parent, else of their box; hands, feet and toes where the limb
above them ends, on their own box: wrist, ankle; spine, chest, head at their bottom); give `rig:` pivots where that guess is off. Skin defaults to
soft. The manifest maps each joint to its KayKit, Mixamo and Godot SkeletonProfileHumanoid name.

Then any CC0 clip library on the same joints (KayKit Character Animations' `Rig_Medium_*.glb`: Idle_A, Walking_A,
Running_A, Death_A, Hit_A, Throw, Jump_*, ... ~80 clips) plays on the character, retargeted when it's built. KILN
ships two of them (26 clips: idles, walks, runs, jumps, hits, deaths, throw, pick up): `kiln clips` lists them,
`kiln clips add` copies them into `imports/kaykit-animations/`:

```yaml
animations:
  idle:  { import: imports/kaykit-animations/Rig_Medium_General.glb, clip: Idle_A }
  walk:  { import: imports/kaykit-animations/Rig_Medium_MovementBasic.glb, clip: Walking_A }
  death: { import: imports/kaykit-animations/Rig_Medium_General.glb, clip: Death_A, loop: false, fps: 30, speed: 1 }
```

Each bone points where the clip's bone points (the clip's rest pose may be a T-pose; yours can be anything), bone
lengths stay yours, and the hips move by the clip's motion scaled to your hip height. Check with `--pose <name>`.

Clips made for another body type (KayKit's are chibi: splayed arms, deep knee bends on an adult body) can be toned per
animation: `retarget: { keep: { upperarm: 0.35, lowerleg: 0.5 }, offset: { upperarm_l: [0, 0, 12] } }`. `keep` is the
share of each joint's turn away from rest it keeps (0 = held at rest, 1 = as the clip; a base name like `upperarm`
covers both sides; children follow), `offset` a fixed turn in degrees (model axes) added on top.

`godot_bonemap = true` (kiln.toml, off by default; output inside a Godot project) writes `models/<name>.bonemap.tres`
for each humanoid with a skeleton in its glb (soft skins; rigid ones with `merge_rigid`), clip carriers included: a
`BoneMap` on `SkeletonProfileHumanoid` from the manifest's names (`root` -> `Root`, `hips` -> `Hips`, `upperleg_l` ->
`LeftUpperLeg`, ...), and points the glb's `.import` at it (`_subresources` -> `PATH:Skeleton3D` ->
`retarget/bone_map`; the rest of the sidecar stays). Godot then retargets on import: any humanoid clip made for the
profile (Mixamo, Godot's own retargeted libraries) plays on the character with no renaming in the game. The glb itself
doesn't change, but in Godot **the bones take the profile's names** (`Hips`, `LeftUpperLeg`; unmapped bones keep
theirs), the skeleton node becomes `%GeneralSkeleton`, and clip tracks follow: node paths, `find_bone("hips")` and
BoneAttachment3D names in game code must use the new names (manifest `humanoid` has them; the entry says
`godot_bonemap`). Use it for a new game or one sharing clips with other humanoids; leave it off where code already
names KILN's bones. Turning it off removes the files and the `.import` setting again (Godot reimports with KILN's
names).

#### Clips on any skeleton (joint map)

A creature that isn't a humanoid (a quadruped, a bird) plays a clip library made for another armature through a
map from its part ids (bones) to the clip's joints:

```yaml
skin: rigid
rig: { body: { pivot: [0, 0.5, 0] }, neck: { pivot: [0, 0.55, 0.3], parent: body }, head: { parent: neck }, ... }
skeleton:
  map:
    body: Torso2
    neck: { joint: Neck1, child: head }        # child: the bone whose direction aims this one
    head: Head
    fl_up_l: { joint: FrontUpperLeg.L, child: fl_low_l }
    fl_low_l: FrontLowerLeg.L
    tail1: { joint: Tail1, child: tail2 }
    tail2: Tail4
  root_motion: Torso   # the clip joint whose movement moves the model
animations:
  walk: { import: imports/Horse.glb, clip: Walk, retarget: { keep: { tail1: 0.5 } } }
```

Each mapped bone turns by its joint's world-space turn from the clip's rest. A bone with a `child` (another mapped
bone below it in the rig) is first turned so it points where the clip's joint points to the child's joint (as each
humanoid limb is), so a creature built in its own rest pose plays the clip; without `child` it keeps its parent's
aim. Unmapped bones follow their parent (a saddle on the body); unmapped clip joints are ignored (IK and pole
bones). The map changes nothing else: parents, pivots and skin come from `rig` and `skin` as usual, so give the
creature a hierarchy (`parent:`) and a skin (`rigid` or `soft`). `retarget: { keep, offset }` works per mapped bone
(by id, or a base name for `_l`/`_r` pairs).

`root_motion` names the clip joint whose movement moves the model: its movement, scaled by the moving bone's rest
height over the joint's rest height (a joint at ground level: unscaled), moves the bone mapped to that joint, or,
when it isn't mapped (`Torso` above), the bone mapped to its nearest mapped joint below it (`body`: `Torso2`). Without
`root_motion` nothing moves: the clip plays in place, rotations only (the body's bob and travel are dropped).

`skeleton: humanoid` uses the standard table and takes no map (`skeleton: { ... }` is for every other skeleton).
Findings (E007): a map key that isn't a part id (or is `root`), a `child` that isn't a mapped bone below it; (E008)
a mapped joint or `root_motion` the clip file doesn't have (with the nearest names). Check with `--pose <animation>`.


### Attachments for CC0 characters

A helmet, shield or banner made around a CC0 character (a KayKit Knight) instead of a KILN body:

```yaml
fit_to: { file: imports/Knight.glb, bone: head, meshes: [Knight_Head] }   # meshes: which ones to fit (default all)
parts:
  - sphere: { at: [0, 1.62, 0], radius: 0.8 }        # the coverage: where the helmet reaches
    shell: { thickness: 0.04, open: -y }
    fit: { to: target, gap: 0.015 }                   # wraps the character's own head, 1.5 cm off it
```

The model is made in the character file's space (its units); the glb is exported in the bone's space (root node
`<model>_on_<bone>`), so the game hangs it on that bone (Godot: a BoneAttachment3D); the manifest says `attach: { file,
bone }`. W113 warns when it sinks into the character. `kiln preview <model> --fit` shows it on the character and the
character without it.

## Effects

Effects: pre-rolled particle descriptions (effect.json).

### Effects

A burst (an explosion's debris, sparks, puffs of smoke) as other models thrown out over time. KILN doesn't play
effects: `kiln build` writes `models/<name>.effect.json` (manifest `effect`) with every particle already rolled from
the seed, so an engine-side player shows exactly what `kiln preview <model> --effect` shows.
The preview plays it in 8 evenly spaced frames; `--at 0,0.1,0.25,0.5,1` (seconds) gives a contact sheet at those
times instead (tune particle sizes there). Each piece's `fade` is drawn as ordered dithering (a reversed envelope shows
as pieces that appear instead of vanish) and a `floor` as a thin grid.

```yaml
effect:
  seed: 3                    # same seed, same particles
  duration: 1.2              # seconds (default: the last particle's end); loop: false
  emit:
    - model: spark           # another model in the project (its glb; `origin: center` so it spins about its middle)
      count: 12
      at: [0, 0.5, 0]        # spawn point, spread: 0.1 (a ball's radius)
      delay: [0, 0.2]        # seconds, a number or [lo, hi]; life: [0.5, 1.0]
      velocity: { min: [-0.5, 1, -0.5], max: [0.5, 2, 0.5] }   # m/s, or one [x, y, z]
      burst: [1, 2]          # m/s outward, any direction (added to velocity)
      gravity: 9.8           # m/s^2 down, or [x, y, z]; drag: 1.5 (1/s)
      spin: [-90, 90]        # degrees/s about a random axis
      scale: { 0: 0.2, 0.2: 1, 1: 0 }   # over life (0..1), linear between keys; or one number
      heat: { 0: 1, 1: 0 }   # for the game's shader (e.g. into the attr it reads)
      fade: { 0.8: 1, 1: 0 } # opacity for the game (1 = solid); previews dither it
      bounce: 0.3            # with a floor: vertical speed kept at a hit (0 = stops dead); friction: 0.6 (horizontal)
      settle: true           # with a floor: rest once slower than 0.2 m/s on it (no motion, no spin)
  floor: 0                   # optional: a height (effect frame) debris bounces on and settles on, instead of falling through
```

The JSON: `format`, `duration`, `loop`, `seed`, `motion` (the formula), `emitters` (model, `glb`, `godot_scene`,
`origin`, gravity vector, drag, envelopes as `[life fraction, value]` pairs) and `particles` (`emitter`, `delay`,
`life`, `at`, `velocity`, `axis`, `spin`; with a `floor`: `hits`, each `[age, position, velocity]` where the motion
starts again from that position and velocity, `[0, 0, 0]` = resting there without spin). Position at `age = t - delay`
(alive while 0 <= age <= life):
`at + g/k*age + (velocity - g/k)*(1 - exp(-k*age))/k` with drag k > 0, `at + velocity*age + g*age^2/2` with k = 0.
E011 when an emitted model doesn't exist.

## Terrains

Terrains: height shapes, splats, chunked LOD meshes.

### Terrains

A model with `terrain:` instead of `parts:` is a heightfield (one height per x, z) with up to four splat layers of
palette colours: ground for a level. Only `name`, `description`, `tags`, `status`, `style_version`, `class` (default
`terrain`), `style`, `palette` and `lint` go with it. The map is centred on the origin (x and z from -size/2 to
+size/2), heights in metres. Design point: 256 x 256 m at 0.5 m cells (builds in ~2 s, ~120 MB).

```yaml
name: valley
terrain:
  size: [256, 256]           # metres [x, z] (or one number); a whole number of cells and of chunks
  cell: 0.5                  # grid spacing (m); up to 2048 x 2048 cells
  chunk: 32                  # mesh tile size (m): a whole number of cell x 2^(number of LODs), at most 250 cells
  lod: [64, 160]             # camera distances (m) where LOD 1, 2, ... take over (each halves the grid); [] = none
  skirt: 1.5                 # optional: how far chunk edges hang down (default: from the LODs' height error)
  collision: 1               # HeightMapShape3D sample every 1, 2, 4 or 8 cells; false = none
  seed: 3                    # noise seed; base: 0 (the height everything starts from)
  shapes:                    # applied in order to the running height H
    - noise: { scale: 70, height: 3, octaves: 5 }     # roughness: 0.5, ridged: false, seed: 0 (added to the terrain's)
    - hill: { at: [-70, -50], radius: 55, height: 22 }  # radius m or [x, z] (an oval), rotate: degrees
    - ridge: { points: [[-128, 90], [0, 100], [128, 80]], width: 35, height: 20 }   # a smooth curve through the points
    - plateau: { at: [70, -55], radius: 26, edge: 10, height: 14, blend: max, smooth: 3 }   # flat top, sloping rim
    - hill: { at: [40, 35], radius: 28, height: 5, blend: subtract }  # a hollow
    - path: { points: [[-128, 10], [0, 0], [128, 5]], width: 5, edge: 5, depth: 0.25 }  # smooth: 12 (m along it)
  splat:                     # 1-4 layers; the first is everywhere, each later one painted over where its rules hold
    - grass: { color: grass }
    - dirt: { color: dirt, path: { within: 3.5, fade: 1.5 }, noise: { scale: 6, cover: 0.85 } }
    - rock: { color: rock, slope: { above: 28, fade: 6 } }
    - sand: { color: sand, height: { below: -1.5, fade: 1 } }
```

Each shape has a weight p (1 at its core, a smooth falloff to 0 at its edge: a hill's radius, a ridge's `width` from
its line, a plateau's `edge` past its radius) and a `blend`: `add` (default; H += height x p), `subtract`, `max` /
`min` (raise / lower towards the level `height`; `smooth`: m of crease rounding) or `set` (to the level). Noise only
adds or subtracts (about +-height). A path flattens a band (`width`, banks `edge`) to the ground's own height smoothed
along it (`smooth` m), sunk by `depth`: roads that cut through hills and bridge dips. Layer rules multiply:
`slope: { above, below, fade }` degrees, `height: { above, below, fade }` metres, `path: { within, fade }` metres from a
path's centre line, `noise: { scale, cover (0-1), fade, seed }` patches; `strength` (0-1) caps the layer.

Output: `models/<name>.glb` (LOD 0) and `.lod<k>.glb`: a root node with `chunk_<ix>_<iz>` nodes at the chunks'
centres, each a regular grid mesh (POSITION, NORMAL, COLOR_0 = the blended colours, TEXCOORD_0 = the splat map) with a
skirt; `models/<name>.splat.png` (one pixel per grid point, top = -z; R, G, B = layers 2-4, layer 1 = the rest); with
"godot", `models/<name>.tscn`: the LOD glbs (each chunk shown between its LOD's distances, 4 m overlap), a splat shader
blending the palette colours (the style's toon bands if it has them) and a StaticBody3D with a HeightMapShape3D
(inline, scaled by the sample spacing). Godot imports the chunk glbs without its own LODs. Manifest: the usual fields
plus `terrain` (`size`, `cell`, `samples`, `chunk`, `chunks`, `lod_distances`, `skirt`, `height_range`, `splat`,
`layers` with `channel`, `collision` (`samples`, `spacing`), `probes`: [x, z, height] points `--verify-godot` checks
the collision at). `kiln preview <terrain>`: from above (splat colours, lit) and from four sides. Lint: W116 a layer
covers < 0.5% of the map, W117 a shape is off the map.

Tools (foliage scattering, props on the ground) read the heightfield in Python:
`kiln.terrain.load(project, "valley")` -> `Heightfield` with `height(x, z)`, `normal(x, z)`, `slope(x, z)` (degrees),
`splat(x, z)` (weights in `layer_names` order), `distance_to_path(x, z)`, `distance(points)` (y - height: the
heightfield as a distance field) and `bounds()`; arrays in, arrays out, bilinear between grid points.

## Scatters

Scatters: foliage and props over a terrain or model.

### Scatters

A model with `scatter:` instead of `parts:` places other models many times over a surface: grass, flowers, rocks and
trees on a terrain, moss on a boulder, pebbles on a flat area. Only `name`, `description`, `tags`, `status`,
`style_version`, `class` (default `scatter`), `style`, `palette` and `lint` go with it. KILN rolls every instance at
build time (Python's `random.Random`, one stream per `place` entry: stable across machines, and editing one entry leaves
the others where they were).

```yaml
name: meadow
scatter:
  onto: valley               # a terrain, another model (its top surface, seen from above) or flat (needs size)
  size: [64, 64]             # optional: the area [x, z] in metres (or one number), centred on the origin;
                             # default: the whole terrain / the model's footprint
  seed: 7
  chunk: 32                  # instances are grouped in cells this size (one MultiMesh each: culling, LODs)
  place:                     # in order: later entries keep their distance from earlier ones (spacing)
    - model: tree            # a model, name.variant, or a list picked evenly: [flower, flower.pink]
      density: 0.003         # candidates per m^2 of area (seen from above), before rules and spacing
      spacing: 9             # at least this far (m) from every instance placed before (the larger spacing of the two)
      scale: [0.8, 1.3]      # a factor or [lo, hi]
      rotate: 360            # yaw jitter in degrees (360 = any way round, the default; 0 = none; or [lo, hi])
      tilt: 5                # a random lean up to this many degrees
      align: 0               # 0 upright .. 1 up along the surface's normal
      sink: 0.15             # metres into the surface (hides bases on slopes)
      tint: { color: sand, amount: 0.4, shade: 0.15 }  # or a number: shade only
      slope: { below: 22 }   # degrees, { above, below, fade } as terrain splats
      height: { above: 0 }   # metres
      noise: { scale: 20, cover: 0.6 }   # patches (clumps of flowers)
      splat: grass           # a terrain's layer (or a list): kept as often as their summed weight there
      path: { beyond: 6 }    # a terrain's paths: away from (beyond) or near (within) their centre lines, m
      lod: [70]              # camera distances where the model's lod1, lod2, ... take over (needs its lod: budgets)
      visible: 120           # hidden beyond this camera distance (m); 0 = always
```

How it places: `density` x the area candidates, uniform over the area; a candidate is dropped where there's no surface
(off a model, or under an overhang), else kept with the probability its rules give (multiplied; each a smooth ramp
over its `fade`), then dropped if it is closer than `spacing` to an instance placed before it (entries with spacing 0
skip that check). An instance stands its model's origin (its feet) on the surface, `sink` lower; it leans `align` of
the way to the surface's normal, then by a random `tilt`, turns by `rotate` about its up and is scaled. `tint` makes
an instance colour (linear RGB) that multiplies the model's colours: white leaning towards `color` by up to `amount`,
darkened by up to `shade`. Scatter models made of one mesh (no rig, no skin); keep their budgets small (grass ~100
triangles, trees ~1500 with a `lod:`).

The scatter's frame is the surface's: a terrain's map, a model's exported frame (its glb's: model space minus its
`origin`), or a flat area centred on the origin at y = 0. Put the scatter scene under the terrain or model.

Output: `models/<name>.scatter.json`: `format`, `seed`, `onto` (`kind`: flat, terrain or model; `model`), `area`
(`min`, `max` x, z), `chunk` and `groups`, one per entry and model (`node`, `place`, `model`, `variant`, `glb`, `lods`,
`godot_scene`, `count`, `lod_distances`, `visible`, `chunks` (`node`, `first`, `count`: ranges of `instances`),
`instances` (each `[x, y, z, ax, ay, az, bx, by, bz, cx, cy, cz]`: the model's origin and its x, y, z axes, scale
included) and, with a tint, `colors` (linear RGB per instance)). With "godot", `models/<name>.tscn`: a Node3D per group
holding a `MultiMeshInstance3D` per chunk (transforms and colours inline); its inline script gives each MultiMesh the
model's mesh with the materials the model's own scene sets up (the style's look; tinted groups let instance colours
through: `vertex_color_use_as_albedo`, the toon shader's COLOR), adds `<chunk>_lod<k>` copies with the model's LOD glbs
and sets the visibility ranges (2 m overlap). Manifest: `class`, `style`, `scatter` (the JSON), `onto`, `instances`
(per group), `godot_scene`; no `glb`. `--verify-godot` checks every chunk and LOD against the JSON (instance counts,
each transform times where the mesh sits in its model, colours, materials, distances). `kiln preview <scatter>`: from
above, from two sides and close up where the most instances are (the whole-area views draw every n-th instance of the
costliest groups beyond 200 000 triangles). Lint: E015 (an unknown or unsuitable model or variant, more `lod`
distances than the model has LODs, `splat`/`path` without a terrain, an unknown layer, more than 1 000 000 candidates
in an entry or 200 000 instances in a scatter), W118 an entry places more than 50 000 instances, W119 an entry places
none.

## Imported

Imported models: CC0 packs, kiln import, matching a reference.

### Imported models (free CC0 packs)

For things text does badly (dense foliage, realistic rocks, detailed props), use free packs: Kenney, KayKit,
Quaternius (CC0), Poly Pizza (CC0/CC-BY). `kiln import <file.glb> --licence CC0-1.0 --author ... --url ...
--height 2.5` copies it into `imports/`, writes a model with `source:`; the build scales it, stands it on the
ground, snaps its colours to the palette and applies the style's materials. `kiln credits` and `CREDITS.md` list
authors. Never use assets whose licence forbids it (NC, ND, SA, Synty, anything "no AI"). An .fbx/.blend/.obj
imports the same way when Blender 4.x is installed (`BLENDER=/path/to/blender`): `kiln import` turns it into
`imports/<name>.glb` once, so prefer that over naming the .fbx in `source:` (every build would need Blender).

Shipped CC0 packs: `kiln pack list`; the owner mirrors one with `kiln pack add <pack>` (it downloads; ask first).
`kiln pack search knight --json` (MCP `pack_search`, `lineup: true` for a sheet of the hits) finds models by name and
tags with triangles and size; `kiln pack import <pack> <name> --height 1.8` (MCP `pack_import`) copies it into
`imports/<pack>/` and records it in `kiln.lock`, which the build checks (E014: a changed file, a non-CC0 licence).

**Match a reference** (make a KILN model that holds its own next to a CC0 asset, e.g. a KayKit barrel):
1. Put the reference in `imports/` and ask the owner for thresholds, with defaults: silhouette `iou` >= 0.9 (and
   `iou_min` >= 0.85), `triangle_ratio` <= 1.5, `surfaces` <= the reference's + 1, `colors` within +-2,
   `open_edges` 0, and for a faceted (low poly) target `facet_regularity` >= 0.7 (use a hard-surface style or parts).
2. `kiln preview <model> --vs imports/<ref>.glb --ref-height <the model's intended height> --json` (MCP: `preview`
   with `which: "vs"`, `reference`, `ref_height`). Read `compare` and LOOK at the sheet: the silhouette row shows red
   where the model sticks out and blue where it is missing, per view.
3. Change the model (proportions, part sizes, budget, `sides`, colours), lint, and repeat step 2 until every metric is
   inside the thresholds. Fix the worst view first (`iou_views`). Don't copy the reference's details one for one:
   match its size, outline, density and colour count; the design stays ours.
4. Report both renders (the vs sheet) and the final metrics against the thresholds; say which ones you couldn't meet
   and why.


### Imported models

```yaml
name: oak
class: nature
source: { file: imports/tree_oak.glb, licence: CC0-1.0, author: Kenney, url: https://kenney.nl }
process: { height: 4.0, recolor: auto, rotate: [0, 90, 0] }   # or scale: 1.0; recolor keep = file's colours
```

Static meshes only. Colours snap to the palette (OKLab nearest), the style's materials and budget apply, the model
stands on y = 0, and the build writes CREDITS.md. Files the model refers to (`Textures/colormap.png` in Kenney kits)
are copied with it by `kiln import`, keeping their folders; a missing one is an error, not a white model.

**.fbx, .blend, .obj** (optional, needs Blender 4.x: `blender` on PATH or `BLENDER=/path/to/blender`; `kiln doctor`
shows which). Blender exports the file as a glb (+Y up, modifiers applied, skins, animations, the active vertex
colours, textures as they come), which then imports like any glb. Two ways in:

- `kiln import Knight.fbx --licence CC0-1.0 ...` converts once and writes `imports/Knight.glb` (the original isn't
  copied); the model names the glb, so the project builds anywhere without Blender. Preferred.
- `source.file`, an animation's `import:` and `fit_to.file` may name the .fbx/.blend/.obj directly: every load then
  needs Blender, and the glb is cached in `.kiln-cache/blender/<key>/<name>.glb` (key: the file's sha256, an .obj's
  .mtl and texture maps, the Blender version, the export script version), so only the first build runs it. Credits
  name the original file.

No Blender, or one older than 4: E010 (E008 for an animation `import:`) saying how to fix it; a failed conversion
shows the end of Blender's output. FBX clip names carry Blender's armature prefixes (a `Wave` action came out as
`Rig|Rig|Wave`); a wrong `clip:` lists the real names.

#### CC0 packs (`kiln pack`)

KILN ships recipes for CC0 packs (`kiln pack list`): Kenney (`kenney-mini-dungeon`), KayKit (`kaykit-adventurers`,
`kaykit-furniture-bits`, `kaykit-city-builder-bits`, `kaykit-dungeon-remastered`) and Quaternius
(`quaternius-modular-scifi-megakit`). A recipe pins the archive's URL and sha256; mirroring checks both and that the
pack's licence file says CC0.

```sh
kiln pack add kaykit-adventurers          # the only command that downloads: into ~/.cache/kiln/packs/<pack>@<version>/
kiln pack search knight --json            # file name and tags (the pack's own + its folders); triangles, size, bytes
kiln pack search chair --pack kaykit-furniture-bits --lineup   # + previews/pack-search.png: the hits at one scale
kiln pack import kaykit-adventurers knight --height 1.8 --class character
```

Mirrors are per user, shared between games (`$XDG_CACHE_HOME/kiln/packs`; `KILN_PACK_CACHE` overrides). Search terms
must all match, ranked whole name > a word of the name > part of it > a tag. `kiln pack import <pack>[@version]
<path|name>` copies the model and the files it refers to into `imports/<pack>/`, writes the model (as `kiln import`:
`source:` with CC0-1.0, the pack's author and page) and records every copied file in `kiln.lock` (JSON: path ->
pack, version, url, sha256, licence, file in the pack). Commit `kiln.lock` and `imports/`; the cache stays out of the
repo. A recipe file works too: `kiln pack add my-pack.toml` (fields `name`, `version`, `url`, `sha256`, `licence` =
CC0-1.0 only, `author`, `homepage`, `strip` leading folders, `models` folder, `licence_file`, `textures` shared folder,
`tags`).

With a `kiln.lock`, lint and build check it (E014 errors fail the build): a listed file whose sha256 changed, an
entry whose licence isn't CC0-1.0, a model whose `source.licence` differs from its file's entry; a listed file that's
gone is W115. Files without an entry (local `kiln import`) aren't checked; no `kiln.lock`, no checks. CREDITS.md and
the manifest's `source` name the pack (`pack: kaykit-adventurers@1.0`) for locked files.

## Build

Building for the game: glb, Godot scenes, look kits, colour modes, the manifest, reporting.

### Building for the game

- `kiln build` writes `models/<name>.glb` (+ `<name>.<variant>.glb`, `<name>.lod1.glb`), and with "godot":
  `models/<name>.tscn` (the glb with the style's materials: toon bands, outlines, rim light) and
  `looks/<style>.tscn` (the look kit: sky, sun, tonemapper, SSAO, glow, grading). Tell the owner to instance the
  look kit once in each scene: half of the style is lighting.
- `kiln build --verify-godot` loads everything in headless Godot (in a throwaway copy) and checks parts, animations
  and materials (and that attachments fitted to a CC0 character land on its bone).
- Many team colours: `variant_glbs = false` in kiln.toml keeps one glb per model; each variant becomes a Godot scene
  that recolours it (and a `swap` table in the manifest for other engines; with `shade:` and `vertex_colors`, the
  vertex colours are shaded, so match them within a tolerance).
- Crowds (many instances): `vertex_colors = true` puts colours in the vertices, one surface per material preset,
  so a character costs 2-4 draw calls instead of one per colour.
- Crowds, best: `atlas = true` gives every model without a `normal_map` one material (colours and presets in a small palette texture): 1 draw
  call per mesh (+1 per decal or texture), and team colours become a texture swap on one shared mesh. `atlas_ao = true` adds
  baked ambient occlusion (a number 0..1 sets its strength). Use it instead of `vertex_colors`.
- Warnings W111 (a part lost to the triangle budget) and W112 (a LOD well over its target) mean: raise the budget.
- Ground for a level: a model with `terrain:` instead of `parts:` (hills, ridges, plateaus, noise and paths combined in
  order; up to 4 splat layers of palette colours by slope, height, nearness to paths and noise; see `kiln docs terrains`).
  It builds chunked LOD glbs, a splat map and a Godot scene with a HeightMapShape3D; `kiln preview <name>`
  shows it from above and four sides. Place things on it from Python with `kiln.terrain.load(project, name)`
  (`height`, `normal`, `slope`, `splat` at any x, z).
- Foliage and props over ground: a model with `scatter:` (`kiln docs scatters`) places other models (grass,
  flowers, rocks, trees; one mesh each, small budgets) over a terrain, another model's top or a flat area by density,
  spacing and rules (slope, height, noise patches, splat layers, paths), with random turn, scale, lean and tint. It
  builds `<name>.scatter.json` and a Godot scene of MultiMeshes (with LODs and a fade-out distance); `kiln preview
  <name>` shows it. Lint W118/W119: too many / no instances.
- `kiln preview <name> --engine` renders through Godot itself, offscreen (Linux: a private Xvfb with CPU drivers; never a window on the desktop; `KILN_OFFSCREEN` overrides): use it to confirm the look. It is framed like the software views on the same tile colour; with `--engine`, `--views`, `--pitch` and `--size` pick its views (default: four sides at 15 and 50 degrees).
- `manifest.json` lists every model: glb, scene, size and bounds in metres, triangles, parts (pivot, parent, meta),
  animations (Godot names, loop, fps), variants, LODs, licences. That's the contract with game code.
- Not Godot: `export = ["glb"]`; the per-engine notes (Unity, Unreal, Bevy, three.js, Defold) are in KILN's
  `docs/engines.md` (https://github.com/lukasgolino/kiln/blob/main/docs/engines.md). Outside Godot `atlas = true` is
  usually the best colour mode; look kits, toon, outlines and rim light are Godot-only.


### Build output

`<output_dir>/models/<name>.glb` (+ `.<variant>.glb`, `.lod<N>.glb`), with "godot": `models/<name>.tscn` (glb +
style materials) and `looks/<style>.tscn` (WorldEnvironment + Sun), `manifest.json`, `CREDITS.md` (imports).
Manifest per model: `glb`, `godot_scene`, `class`, `style`, `status`, `triangles`, `bounds` and `size` (metres),
`skin`, `parts` (parent, pivot, meta, separate, `node_path`: glTF node names from the root, `aabb`: the part's box
in model space, rest pose, for hit zones), `animations` (gltf_name, fps, frames, loop, interpolation, duration),
`variants` (`swap`, `glb` unless variant_glbs = false, `godot_scene`), `lods`, `colors`, `source` (imports), `effect`,
`humanoid` (each joint's KayKit, Mixamo, Godot name), `godot_bonemap` (with godot_bonemap = true: the BoneMap file);
parts also have `sockets`, animations a `start` (the parts their first frame moves, e.g. an arm built level but
cocked when the animation starts). With `vertex_colors = true`, a game loading the .glb itself must set
`vertex_color_use_as_albedo = true` on the imported materials (KILN's .tscn scenes do it), and on Godot's
Compatibility renderer, which decodes vertex colours from sRGB once more (darker, more saturated;
`vertex_color_is_srgb` changes nothing there), re-encode each mesh's colours once (`_encode_colours` in a KILN .tscn
does it, as do scatter scenes for LOD glbs; it also covers `atlas_ao`'s occlusion; LOD glbs a game loads itself need
it too); variants are then swap
tables for the game (or `variant_glbs = true`). KILN's .tscn scripts share their materials between instances and
leave any surface override the game set before `add_child` alone.

**Palette atlas** (`atlas = true`; not with `vertex_colors`): every (colour, material preset) pair gets a 4x4-pixel
cell in `models/<name>.palette.png` (colours), `<name>.material.png` (glTF metallicRoughness: G = roughness,
B = metallic), `<name>.glow.png` (emission, only when a preset glows) and, with "godot", `<name>.rim.png` (Godot rim
light: R = rim, G = tint). The glb references them by URI (next to it) and every face's UVs sit on its cell's centre;
samplers are NEAREST without mipmaps. One material for the whole model: 1 surface per mesh (2 where a decal is), soft
or rigid skins alike (rigid parts are nodes sharing the material). A variant is a texture swap:
`<name>.<variant>.palette.png` (+ `.glow.png`), same cells, same mesh; its Godot scene is the base glb with the
variant's textures (variant glbs are still written unless `variant_glbs = false`). Manifest per model: `atlas`
(`palette`, `material`, `glow`, `rim`, `size`, `cell`, `cells`: `color`, `material`, `uv`, `pixel`; `ao`, `ao_strength`), variants
also `palette` (+ `glow`): to recolour at runtime, write other colours into a copy of the palette at the cells'
pixels. `atlas_ao = true` bakes ambient occlusion from the model's distance field (imported models: from the mesh's
dents) into COLOR_0 (a number sets its strength: the darkest corner is x (1 - strength); true = 0.65), a grey multiplier glTF viewers apply; in Godot only KILN's .tscn scenes use it
(`vertex_color_use_as_albedo`). Previews (`kiln preview`, `kiln gallery`, scatters) show it too. When the output is inside a Godot project (with "godot" or
not), KILN writes the palette textures' `.import` settings (lossless, no mipmaps, no VRAM compression on first 3D use: 4x4 cells stay exact); settings Godot adds
later (uid, imported files) are kept. A model with `normal_map:` stays out of the atlas (both need the first UV set): a material per colour,
its normal map, and `atlas_ao`'s occlusion in COLOR_0 all the same (manifest: `ao`, `ao_strength` on the model, no `atlas`).

**Shared clips**: `animations_only: true` makes a model a clip carrier (its animations are what counts; give it the
same rig as the models that use it); `animation_library: <carrier>` on another model plays the carrier's animations
(every part id its clips move must be in the model, E008 otherwise; other ids may differ, e.g. a helmet on one loadout:
they follow their parents, and tracks for carrier parts the model lacks are left out; shared joints more than 1 cm from
the carrier's: W114, since a clip's position tracks put bones where the carrier has them; same skeleton). That model's glb carries no clips; previews and the manifest's `animations` still
list them, plus `animation_library` (`model`, `glb`). Inside a Godot project the carrier's glb is imported as an
AnimationLibrary (no `.tscn`); add it to each model's AnimationPlayer.
`kiln build --verify-godot` checks everything in a throwaway copy of the output (nothing else in the game's project is
imported or touched). Attachments (`fit_to`) are hung on their bone of a copy of the character through a
BoneAttachment3D and must land where they were made.

Other engines: everything but the `.tscn` files, `.import` sidecars and `<name>.rim.png` is plain glTF + JSON. Notes per
engine (axes, scale, vertex colours, palette texture filtering, skins, clips, LODs, approximating the look):
https://github.com/lukasgolino/kiln/blob/main/docs/engines.md

In Godot:

```gdscript
var pilot: Node3D = load("res://assets/kiln/models/pilot.tscn").instantiate()
add_child(pilot)
pilot.get_node("AnimationPlayer").play("walk")
add_child(load("res://assets/kiln/looks/soft_toy.tscn").instantiate())   # once per scene: the style's light
```


### Long builds

Builds say nothing for their first 10 s, then a line per phase (joining hard parts, meshing, painting, reducing,
skinning, baking maps) at least every 10 s, with done/total and roughly how long is left:
`kiln: bigfoot: reducing: passes done 2/5, about 9 min left (662 s)`; a long build ends with where its time went:
`kiln: bigfoot: built in 156 s (meshing 12 s, painting 9 s, reducing 15 s, skinning 4 s, baking maps 112 s)`. A step projected past 2 minutes says
`a long build` at once with what would make it faster:

- joining hard parts: fewer hard parts, or fewer `sides` on round ones (the cell size makes no difference to this phase);
- meshing: a coarser `resolution` or fewer parts;
- painting: fewer gradient or pattern parts;
- reducing: a coarser resolution;
- skinning: `skin: rigid` or fewer parts.

A model with 100 or more parts prints every phase line at once.

`kiln preview <model> --draft` (with the turntable, `--views`, `--closeup`, `--pose`, `--detach`) is for iterating on
a slow model: mesh cells 3 times coarser, each face in its nearest part's colour (ragged colour edges, no patterns
on smooth parts, no `under:` paint beneath detachables), hard parts without bevels, one reducing pass, no normal map
or baked occlusion. A 536-part character that builds in 5 minutes drafts in 14 s; a 23-part one in 5 s. Sheets go to
`previews/<model>/draft/`, each stamped DRAFT; the draft has its own cache and never changes what `kiln build` or
the real previews use. Judge proportions, silhouette and placement on it. Don't judge the surface, the colour edges
(least of all next to cuts), the triangle count (a draft isn't reduced to the budget) or anything lint says: those
are the real preview's. Not for terrains, scatters or imported models, nor with `--engine`, `--vs`, `--fit`, `--effect`.

### What things cost

Build time, measured with KILN 0.22 on one 6-core machine with `kiln-gen[fast]`: read the ranking and the rough
size, not the seconds (without the `fast` extra everything meshed is 2-3 times slower). A 23-part soft-skinned
character at 6 mm cells builds in 16 s; the same model with one thing changed:

| Change | Build | Why |
|---|---|---|
| cells 12 mm instead of 6 | 8 s | fewer field samples and raw triangles; the budget decides the final count either way |
| cells 3 mm (with `max_cells` raised so they aren't capped) | 31 s | halving the cells about doubles the build, and takes more memory |
| 3 mm asked, `max_cells` left at 400 | 20 s | the cap gave 4.5 mm cells: lint W120 says when that happens |
| `budget` doubled (30k -> 60k triangles) | 22 s | more left to place and paint |
| `normal_map: 1024` | 35 s | the bake is a second pass over the surface |
| `noise` on every part | 17 s | one more term per sample: nearly free |
| `skin: rigid` instead of `soft` | 16 s | skinning is small at this size |

What grows with the model:

- **Parts**: about in step with their number. 23 parts 16 s, 94 parts 46 s, 536 parts (about 480 of them fur
  locks) 290 s.
  `blend_to` costs no more than `blend`. If a look needs hundreds of small parts, ask whether it is surface detail
  instead (`detail: true` parts in a `normal_map`, a `pattern`, a `texture`).
- **`gradient` and `pattern` parts**: each is painted on its own: about 0.6 s each on a big model (a gradient on
  every lock of that 536-part character added about 300 s). On a few parts, nothing to worry about.
- **Hard parts** (`hard`, `bevel`, `sides`): joined one by one as exact polygons, whatever the cell size, and the
  time follows their polygons more than their number: 82 mostly plain ones took 45 s of a 54 s build; 13 with many
  sides and bevels, 18 s. Bevels and more `sides` multiply the polygons, and a model over its budget joins them
  again with less detail. A model of hard parts only doesn't get faster with a coarser `resolution`.
- **Size**: a style's resolution gets coarser for models over 1 m (`scale_with_size`) and `max_cells` caps the grid,
  so a big scene costs like a small model unless you force fine cells on it.

What stays cheap after the first build: an edit of animations, variants, description or comments, or of the
style's `[look]` and `[materials]`, reuses the built meshes (seconds). So does a colour edit that keeps which parts
share a colour (a part, pattern, relief or palette colour changed to one no other part has): the meshes, paint
borders and baked maps are reused, recoloured. Two parts that now share a colour (or no longer do) build again. While shapes are still moving,
`kiln preview <model> --draft` shows a slow model in seconds (above). `kiln lint --fast` checks the text without
building.

### Reporting

Keep reports short: what you made, the preview image paths, sizes/triangles if relevant, open questions with your
recommended default. Log owner decisions in BRIEF.md (`log_feedback` over MCP).

## Commands

Every command and its flags.

### Commands

`kiln init [dir] --style soft_toy` · `kiln new model <name> --template bean|prop|empty --class C` ·
`kiln lint [models]` · `kiln preview <model> [--closeup ID|NUMBER] [--pose ANIM [--frame N,N]] [--vs] [--detach] [--fit] [--effect [--at T,T,...]] [--engine] [--variant V | --variants] [--with MODELS] [--views front,34,side,back] [--pitch 5,30] [--size PX] [--draft] [--tight] [--frame-box X0,Y0,Z0,X1,Y1,Z1] [--fill] [--bg auto|light|dark]` ·
`kiln lineup [models] [--pitch DEG]` · `kiln fit <a> <b> [--at X,Y,Z] [--rotate X,Y,Z]` (does b fit a: overlap volume, how deep each goes into the other, the smallest gap, in their shared frame) · `kiln gallery` · `kiln build [models] [--verify-godot] [--no-dependents]` (named models only, and the models placing them: the others keep their last output) · `kiln status` ·
`kiln mark <models> --approved|--draft [--current]` · `kiln style list|show|new|bump|check` (check: each palette colour as the look lights it, beside its hex) ·
`kiln config show|get|set` · `kiln import <file> --licence L` (.glb/.gltf; .fbx/.blend/.obj with Blender 4.x) · `kiln pack list|add|search|import` · `kiln credits` · `kiln doctor` ·
`kiln docs [topic...] [--search words]` (these docs: list, print one, find paragraphs) · `kiln examples [name]` (worked example models: list, print one) · `kiln clips [add]` · `kiln skill install` · `kiln mcp`. Every command takes `--json` (before or after the command). `--closeup` takes a part
id (`root` = parts without one) or a part's number in the file (`--closeup 3`).
Framing: `--tight` fits each tile to what it shows (flat props), `--frame-box` frames the sheets on a region (a scene's
corner; both: turntable and `--views` only), `lineup --pitch 60` looks down on flat props (no ground line past 10). `--fill` adds a neutral light from the
camera (previews only: the game has no such light), so faces seen from below read; `--bg auto` (turntable, views, closeups) is dark for dark skies.
`kiln preview <model> --vs <ref.glb|ref.gltf> [--ref-height METRES]`: the model against a reference mesh (a CC0
pack item, kept as it is: its own colours and normals) at one scale (same pixels per metre, both on y = 0, centred
on each other), in the style's lighting: `previews/<model>/vs_<ref>.png` with paired turntable rows (reference above
the model; from below, eye level, above), the top fifth (head region) close up, and the silhouette difference per
view, and both at gameplay distance (30 m and 60 m at a 60 degree vertical FOV on a 1080 px screen, the style's
outline if it has one, upscaled nearest; an orthographic render at that scale). `--ref-height` scales the reference to that height (default: its own units). Metrics (printed, and in `--json`
under `compare`): `iou` (mean silhouette IoU of 8 views: front, front-left, left, back-left at +10 degrees, front and
left at +50, top, below at -30; 1.0 = same outline), `iou_min`, `iou_views`, `triangle_ratio` (model / reference),
and for `model` and `reference`: `triangles`, `surfaces` (glTF primitives drawn = draw calls; for the model what
`kiln build` writes), `materials`, `colors` (distinct base colours on faces; a textured reference counts each face's
sampled colour), `facet_regularity` (share of surface area in triangles with an edge neighbour facing the same way
within 2 degrees: flat designed facets near 1, smooth or noisily decimated surfaces near 0), `open_edges` (cracks),
`size` (metres). For restyles (where proportions change on purpose):
`band_iou` (mean of `band_ious`: silhouette IoU per body band in 4 side views at 0 degrees, each band cropped, scaled to
one height and centred, so a big head on a short body still matches; `bands` = `humanoid` (`legs`/`torso`/`head` cut at
the hips and head joints: a `skeleton: humanoid` model against a reference with `head` and `hips` nodes) or `thirds`
(`bottom`/`middle`/`top`)), `mass` / `mass_ref` (visual mass: silhouette area / its bounding box, mean of the 8 views)
and `mass_ratio` (model / reference), `screen_px` (height in pixels at 30 m and 60 m, model and reference). All
deterministic. Without a path, `--vs` shows the style's inspiration images.

## Lint

Lint rules: what each means and how to fix it.

### Lint

Errors: E000 usage/config, E001 file/YAML, E002 unknown field, E003 bad value, E004 unknown colour, E005 unknown
material, E006 style problem, E007 rig problem, E008 animation problem, E009 nothing to mesh, E010 import file
problem, E011 decal or texture image missing or unreadable, E012 extends problem (no such model, not a template, a loop, unknown remove id),
W141 a substantial part (15% of the model across and not a thin blade: a leg, a head) vanished when the mesh was reduced to its budget (smaller ones: W111): raise `budget:` or paint fine patterns into the colour map (`paint: map`). E013 the built mesh has open edges (cracks), edges with more than two faces or sheets touching at a vertex (a KILN
bug; report it), E014 `kiln.lock` problem (a pack-imported file changed, a licence that isn't CC0-1.0), E015 scatter problem
(an unknown or unsuitable model to place or stand on, too many instances).

Warnings: W101 part has no visible surface, W102 part thinner than the mesh resolution, W103 separate pieces,
W104 colour not in the palette, W106 not standing on y = 0, W107 made under an older style_version, W108 size
unusual for the class, W109 animated part without a pivot (not humanoid joints), W110 well over the triangle budget (patterns cost
triangles: every stripe border is cut into the mesh; prefer few, large patterns, or model details as parts), W111 a
part lost when reducing to the triangle budget (raise `budget:`), W112 a LOD well above its target (from `kiln build`),
W113 a part pokes through a shell (eyes bigger than a visor slot, a head through a helmet: keep it inside or outside).
W114 (from `kiln build`) joints sit elsewhere than in the model's `animation_library`. W115 `kiln.lock` lists a file
that isn't in the project. W116 a terrain's splat layer covers < 0.5% of the map, W117 a
terrain's height shape is off the map. W118 a scatter entry places more than 50 000 instances, W119 one places none.
W120 the grid cap (`max_cells`), not the resolution, set the mesh cell size: raise `max_cells` to what it says. W121 a `detail` part shows nowhere (no `normal_map`, or under two texels thick). W122 a
`blend_to` target is meshed apart from the part (hard, kept, separate, another bone's piece): they join crisply.
W123 the built mesh dips 2 mm (or a tenth of a cell) or more below y = 0 (blends push feet under the ground): `origin: ground` exports it
lifted onto y = 0. W124 a part shows only a sliver: 97% or more of its own surface is deeper inside other parts than
their blend (clipped flat, nearly gone; W101 is all of it), with the covering parts named; not for hard, shell or
separate parts. W125 the mesh's UV charts don't fit the `normal_map` size (many separate pieces in a small map: the
padding between charts alone fills it) and were squeezed in: use a bigger map. W126 a `relief` layer has no patches:
its parts show no smooth surface of their own. W127 a `color_blend` fades nothing (no blended neighbour of another colour). W128 a round soft part (sphere, ellipsoid, capsule, torus; not hard, kept, stretched or a shell) showing at least half of itself on under 48 triangles per copy (`array`, `mirror` away from the axis) reads as a polygon; it gives the `density` and `budget:` that would lift it. W129 a `skin_falloff` that does nothing (not a soft skin, or a hard, kept, separate or cutting part). W130 a variant leaves a colour the model paints that goes with one it swaps (the same palette ramp, or within 15 degrees of hue; greys don't count): a seam in the old colour; swap it too, or swap whole ramps, or map it to itself to keep it (`skin: skin`). A swap to a shade of the same ramp or hue warns about nothing (`kiln preview --variant` says it too, unless disabled; `kiln lint --fast` gives it). W131 a see-through preset (`alpha` < 1, `clear`) in an atlas project: drawn opaque. W132 a pose's `reach` on a part without exactly one child part: it only aims the part. W133 a relief layer narrower than four texels of the map (it blurs out). W135 on a `skin: soft` body, an articulated limb (a paired side branch with a joint below, e.g. upper arm + forearm) whose skin webs along its length into a part of another branch (an arm into the belly, a leg into the other leg) beyond 55% of its reach from its joint: one lump of skin that stretches when posed; it names both and how far to move the limb (or model an A-pose). W136 a band, pixel or stripes pattern that paints nothing (it misses the part's surface: check where its `at` is measured from). W137 with variants, a pixel-art texture or decal whose pixels aren't palette colours (variants can't swap them: use `rows` + `key`). W138 a part's emission above what its colour can show in the look (the cap: 0.75 / exposure under filmic, 1 / exposure with a linear tone curve, over the colour's brightest channel): the extra changes nothing. W139 the budget took bevels off hard parts (the smallest parts lose theirs first, after a chamfer step): it says what `budget:` keeps them. W140 a part mirrored in one piece (`mirror` without `mirror_id`) whose `blend_to` names one side of a mirror_id pair: add the twin. W134 colour fades per vertex (no maps) in a project without `vertex_colors = true`: the glb keeps crisp borders. Partly floating details have no warning yet: check them in the previews.

`kiln lint --fast` runs only the checks that need no built model (YAML, fields, values, names, the rig's and
animations' structure): quick while writing. It can't give the findings that come from the built model, and its
summary lists them: E009 (nothing to mesh, a build failure), E013, W101-W103, W106, W108, W110, W111, W113, W120-W129, W132, W133, W135, W136, W139, W141. That
includes some that read like text checks (W104 a colour outside the palette, W109 an animated part without a pivot).
A scatter's surface model is still built. Plain `kiln lint` prints the static findings first (a `static checks:` line), then builds each model named (all without names) for the full
list; `kiln build` runs that full lint first on every model, on the same cached meshes, so a model that passes plain
lint passes the build's lint. The build can still stop on what only exporting finds (a clip carrier's users, emitters,
the Godot export).

Disable in `kiln.toml` `[lint] disable` or per model `lint: { disable: [...] }`. Lint meshes models in parallel
(`KILN_JOBS` processes, default: every core) and caches them for build and previews: a model is meshed again when
its parts, paint, rig or skin, its palette, its style's `[shape]` or its triangle budget change. Not for an edit of
its animations (their tracks are made again in seconds), variants, description or comments, nor for a style's
`[look]` or `[materials]`: iterate on poses and looks freely. `pip install "kiln-gen[fast]"`
(numba) evaluates the shapes compiled, 2-3x faster on big models; the output then differs from the plain install in
the last digits, so a game pins one or the other.

## Api

Generator scripts with kiln.api: signatures, what each does, and worked examples.

### Generator scripts (`kiln.api`)

For walls with merlons, fences, stairs, rings of pillars, forests of trees, crowds, or a scene placing other models'
parts: write a short Python script with `kiln.api`, run it, and treat the resulting `.kiln.yaml` like any other model
(lint, preview). Keep the script next to the models (`models/<name>.py`) so it can be re-run.

```python
from kiln.api import model, part, write_model
legs = [part("capsule", "wood", from_=[x, 0, z], to=[x, 0.7, z], radius=0.03) for x in (-0.4, 0.4) for z in (-0.25, 0.25)]
top = part("box", "wood", at=[0, 0.72, 0], size=[1.0, 0.04, 0.6], round=0.01)
write_model("models/table.kiln.yaml", model("table", [top, *legs], cls="furniture"))
```

### Reference

| function | what it does |
|---|---|
| `part(shape, color=None, material="default", id=None, **params)` | one part as a dict. Shape parameters (`at`, `size`, `radius`, `rotate`, ...) go in the shape; part-level options (`blend`, `blend_to`, `cut`, `intersect`, `mirror`, `mirror_id`, `array`, `shell`, `twist`, `scale`, `noise`, `pattern`, `gradient`, `decal`, `texture`, `loose`, `hard`, `bevel`, `chamfer`, `segments`, `fit`, `keep`, `uv`, `attr`, `aim`) are sorted out to the part. `from_=` stands for `from` (a Python keyword). A cut keeps `color` / `material` (they paint its walls) |
| `transform(parts, rotate=(0,0,0), about=(0,0,0), translate=(0,0,0), cut_only=None)` | parts turned by `rotate` (Euler degrees, as a part's) about `about`, then moved: positions, each part's own rotation, tube and lock points and facing, `aim`, array centres, decal and texture centres and axes. Mirrored parts are written out as pairs first (a mirror is about the origin). `cut_only=[ids]`: its unscoped cuts cut only those (a placed group's holes don't cut the scene). A decal axis that no longer lies along x, y or z, or an array turned off its axis, is a ValueError |
| `offset(parts, dx=0, dy=0, dz=0)` | `transform(parts, translate=(dx, dy, dz))` |
| `surface_point(profile, y, angle, at=(0,0,0))` | the point on a lathe at height `y` (its own frame) and `angle` degrees round y (0 = +z, 90 = +x), and the outward normal there, in model space. A cone's profile: `[[radius, -h/2], [radius_top, h/2]]` |
| `ring(count, radius, y, make, start_angle=0)` | `make(x, y, z, angle_degrees)` called at `count` points on a circle; returns its parts |
| `crenellated_wall(length, height, thickness, color, material, merlon=0.5, gap=0.4, round_edges=0.03, noise=0)` | a wall along x, merlons on top |
| `fence(length, posts, height=1, color="wood", material="wood", rails=2)` | posts and rails |
| `stairs(steps, width, rise, run, color="stone", material="stone")` | a flight of steps |
| `tower(radius, height, color="stone", roof_color="red", material="stone")` | a round tower with a cone roof |
| `tree(height=3, crown=1, seed=1, bark="brown", leaves="green", blobs=4)` | a trunk and a lumpy crown |
| `model(name, parts, cls="prop", description="", **fields)` | the model dict (`rig=`, `skin=`, `animations=`, `variants=`, `style=`, `palette=`, ...) |
| `write_model(path, data)` / `dumps(data)` | write it as YAML (short lists inline) |

### A ring of tiles on a cone

```python
from kiln.api import part, surface_point
roof = part("cone", "red", at=[0, 2, 0], radius=1.0, radius_top=0, height=1.0)
tiles = []
for row, y in enumerate([-0.4, -0.2, 0.0]):
    for k in range(12):
        p, n = surface_point([[1.0, -0.5], [0.0, 0.5]], y, k * 30 + row * 15, at=[0, 2, 0])
        tip = [p[i] + n[i] * 0.03 for i in range(3)]
        tiles.append(part("cylinder", "crimson", radius=0.08, height=0.02, aim=[p, tip]))  # flat on the slope
```

`aim: [[base], [tip]]` stands a part's y axis on the line between the points: along the normal, it lies flat on the
surface. Placing another model's parts: read them (`yaml.safe_load(open("models/x.kiln.yaml"))["parts"]`), `transform`
them into place (with `cut_only` for their holes) and append.

## Report

Reporting what got in your way (GitHub issues).

### Help us improve KILN: report what got in your way

KILN is young, and it gets better mostly through reports from agents like you using it on real games. When
something gets in your way, please tell us in a GitHub issue at https://github.com/lukasgolino/kiln/issues. It
is the most useful thing you can do for the project. Whether you do is entirely up to you and your user.

Worth reporting: a crash or traceback; a wrong or misleading message or lint rule; output that looks or behaves
wrong; a workaround you had to invent; a feature you needed and didn't have; this skill or the reference
misleading you.

1. Note it as you go; don't interrupt the task for it.
2. At a natural break (the end of the task, your report), draft the issue: a one-line title; `kiln --version`;
   what you did (commands, a minimal source snippet); what you expected and what you got; the workaround, if
   any. End the body with "Reported by an agent using KILN." Keep it to a minimal repro: no game names, private
   asset content, paths or anything else from the user's project unless they OK it.
3. Look for an existing issue first: `gh issue list --repo lukasgolino/kiln --search "<keywords>"`; if one
   fits, offer a comment on it instead.
4. Show the user the draft and ask whether to file it. Issues are public and posted under their GitHub account,
   so **never file without their OK**. If they agree:
   `gh issue create --repo lukasgolino/kiln --title "..." --body-file <draft>`, or give them the link
   https://github.com/lukasgolino/kiln/issues/new?template=agent-report.md to file it themselves. If they
   decline, drop it.

## Scenes

Other models placed in a model (`instances:`), assemblies of separate models (`mount:`), and checking that they fit.

### Instances and assemblies

Parts of one assembly built as separate models (a watch case, its caseback, its movement) share a frame: `mount: { to:
case, at: [x, y, z], rotate: [x, y, z] }` at the top of the part's model says where it sits on `to`; it skips the
ground checks (W106, W123), goes in the manifest (`mount`) for a game to snap it on, and `kiln preview case --with
lid,movement` shows them together. `kiln fit case movement` checks they fit.

Placing other models (a desk with its props, a tray of screws): `instances: [{ model: screw, at: [x, y, z], rotate:
[x, y, z], scale: 1, id: tray }]` at the top of the model. Each is that model's own build (its mesh at its own cell size
and budget: fine screws stay fine in a coarse scene), merged in after the scene is built. `at`/`rotate` are in the
scene's model space: `rotate` turns the instance about its own origin (its `origin:`, as its own glb), then `at`
places that origin (a flip is `rotate: [0, 180, 0]`; there is no mirror); `id` is the part it moves with
(default root; not mirrored). A scene `lod:` builds every instance at the same share of its triangles. Materials are
read in the scene's style; an instance's decals and textures come along. An instance whose model bakes maps, and every
instance in a scene that does, is a reference: a node `kiln_ref_<model>_<n>` that KILN's Godot scene fills with the
model's own scene (maps and all); a mapped scene's previews don't draw them. In an unskinned or rigid scene a model placed several
times is one mesh in the glb with a node per copy. A scene may be instances only (no `parts:`). Lint sees the scene with its
instances (its size, its pieces: an instance joining two parts makes them one), and holds the model's own parts to
its budget. `kiln build screw` rebuilds the models that place it. Missing models:
E011; templates, terrains, scatters and circles (a model placing itself round about) are errors.

## Surfaces

Hard surfaces (exact polygons), hardware (rivets, bands, planks, bolts, slits, garments, hands, feet, eyes), patterns,
cloth folds, relief fur, soft colour borders. Decals and textures: `kiln docs textures`.

### Hard surface

Smooth parts are sampled from the distance field and reduced to the budget: soft clay-toy shapes. **Hard** parts are
made as exact polygons instead: designed facets, crisp creases, octagonal wheels, planks, beams, armour plates, the
hand-built low-poly look (Kenney, KayKit). A part is hard when it asks (`sides`, `chamfer`, `bevel`, `blend: none` or
`hard: true`), or always with a style's `hard_surface = "always"` (low_poly), except the body of a soft-skinned
character (its joints bend by blending) and parts with `twist` or `noise`. Hard parts join each other exactly
(union, cut, intersect, in order); every later cut or intersect, of any shape, applies to them too. They sit in
smooth parts without blending. A box's `round` is a chamfer on a hard part. Round hard shapes get the style's
`hard_sides` (12 by default; low_poly 8) unless they say `sides`. When hard parts would take most of the budget
(LODs), bevels become chamfers, then go (the smallest parts first; lint W139), then round shapes lose sides.
`bevel_edges: vertical` (or `top`, `bottom`, `horizontal`; default `all`) rounds only those edges, in the part's own
frame: a thin seat's corners without its top and bottom edges (the limit is then half its width, not its thickness). Flat faces stay flat; in smooth styles bevel
bands shade round and designed edges stay crisp.

```yaml
  - box: { at: [0, 0.3, 0], size: [0.6, 0.6, 0.6] }      # a crate
    color: wood
    chamfer: 0.03
  - cylinder: { at: [0.7, 0.26, 0.9], radius: 0.26, height: 0.1, sides: 8, rotate: [0, 0, 90] }   # a wheel
    color: wood_dark
```

### Hardware

Written like a shape, each stands for several ordinary parts (hard by default; `hand`, `foot` and `garment` soft; `eye` a cut, a ball and a ring); the part's other fields (colour,
material, id, mirror, ...) go to each.

| hardware | meaning |
|---|---|
| `rivets: { count: 8, along: [[x, y, z], ...], size: 0.03 }` | rivets evenly along a path (model space, ends included); or `around: { center, radius, axis: y }` in a ring |
| `band: { fit: body, at: [0, 0.12, 0], width: 0.05, thickness: 0.012, axis: y }` | an iron band round an earlier part's surface at `at` (or `radius:` instead of `fit`): barrels, doors, posts. `fit: [hips, belly]` takes several; where their surface isn't round there the band hugs it as a fitted soft shell (a belt), else it is an exact hard ring |
| `planks: { size: [1, 2, 0.08], count: 5, gap: 0.015, axis: x, jitter: 0.05, seed: 1 }` | boards side by side along `axis` with gaps, chamfered; `jitter` shortens each by up to that share of its length (with `at`, `rotate`) |
| `bolt: { at: [x, y, z], radius: 0.02, length: 0.02 }` | a hex bolt head along y (rotate it) |
| `slit: { at: [x, y, z], size: [0.3, 0.04, 0.3] }` | a cut: visor and arrow slits |
| `garment: { fit: [chest, spine], from_y, to_y, hem, openings }` | a fitted layer of clothing round earlier parts, open at the hem and neck (`making` has the full field list and the rigged-character setup) |
| `hand: { at: [x, y, z], length: 0.2, fingers: 4, curl: 30, spread: 8, nail: 0.02, nail_color: black }` | a soft hand from the wrist: palm, curled tapered fingers, thumb, claws; fingers point -y, palm -x, thumb +z (`rotate`, `mirror`); `width`, `thumb`, `knuckles` |
| `foot: { at: [x, y, z], length: 0.26, toes: 5, curl: 10, nail: 0 }` | a soft foot whose sole stands on `at` (under the ankle): sole, toes pointing +z, heel; `width`, `spread`, `heel`, `nail_color` |
| `eye: { at: [x, y, z], facing: [0, 0, 1], radius: 0.03, depth: 0.4, rim: 0.15, rim_color: teal, rim_emission: 1, in: head }` | a recessed eye: a socket cut into `in` (walls in the part's colour), a ball of the part's colour sunk `depth` x radius behind the surface, a thin rim lining the socket's edge, flush (not proud); `at` on the face, `facing` out of it; `rim: 0` for none |

### Patterns

```yaml
    pattern: { type: stripes, color: gold, size: 0.06, width: 0.3, axis: y }
    # several: a list, painted in order (each over the last); frame: part = axes and `at` in the part's own frame
    # (they follow rotate/aim): pattern: [{ type: stripes, ..., frame: part }, { type: band, ..., frame: part }]
```

- `stripes`: bands across `axis`, one every `size` metres, `width` = fraction in the second colour.
- `band`: one band of thickness `size` centred at `at` (one number: metres along `axis`, in model space): belts, trims,
  hat bands. E.g. `{ type: band, color: brown, size: 0.06, at: 0.4, axis: y }` = a belt 0.4 m above the ground
  (with `frame: part`, from the part's own `at`). A pattern that misses its part's surface is lint W136.
- `checker`: checks `size` metres across.
- `dots`: dots on a grid `size` metres apart, diameter `width` x size; `jitter` (0-1: up to half that of a cell each
  way) and `vary` (size +-) at random (`seed`); `offset: [x, y, z]` shifts a repeat (a 2nd dots pattern moves itself).
- `pixel`: a pixel motif tiled round the part's own axis (a hat band, a hem, a cuff): `rows: ["#..#", ".##."]` (`.` or
  space bare, any other character painted; top row first) or `image: trims/key.png` (alpha over half painted, or with
  no transparency its dark pixels; up to 256x64). Each cell is `size` metres tall along `axis` (heights along the axis,
  not the slope: a shallow cone stretches them; a flat brim takes none), the band centred on `at` (from the part's
  own `at`, its origin: `frame: part` is the default here; a lathe's origin, not the middle of its profile); `repeat` times round, or `auto` (the default: about square cells at the
  part's widest radius). It reads left to right seen from outside, like a cylindrical texture; a mirrored part reads
  mirrored. Near the axis (a cone's tip, a cap) columns too narrow aren't painted. One colour per pattern: list several
  for more. Smooth parts only (a hard part with one is an error). E.g. `{ type: pixel, color: gold, size: 0.02, at: -0.1,
  rows: [...] }`.
- Where a pattern is painted: `paint: cut` cuts it into the mesh (exact borders, but every cell costs triangles: many
  pixel trims starve the budget); `paint: map` paints it per texel into the base colour map (no triangles; it brings
  the maps, needs `kiln-gen[bake]`). `auto` (the default): pixel and dots patterns go in the map when the model has
  baked maps anyway (relief, colour fades, `normal_map`), else they are cut. Hard parts' patterns are always cut.

Decals and textures (images on parts, named, triplanar, motif prints, palette-indexed and generated pixel art): `kiln docs textures`.

### Cloth folds: `folds`

Robes, skirts, capes and curtains: `folds: { count: 12, depth: 0.03, from_y: 0, to_y: 1.0, sharp: 0.5 }` on a smooth
part (a cone, a lathe, a cylinder; count 2-48, depth up to 0.1) runs `count` vertical folds round its own y axis,
`depth` metres deep at `from_y` (the hem) and fading out by `to_y` (where the cloth hangs from); `sharp` 0 gives
round waves, 1 narrow ridges between wide hollows. The hem comes out scalloped. Heights run along the part's own axis
(model heights for an upright part; each `array` copy folds round its own). A fold is never deeper than a quarter of
the fold spacing there (2 pi r / count), so near the axis and with many folds they get shallower. They are real
shape: they show in silhouette and in Godot without a normal map; keep `depth` at least two mesh cells. A shell's wall
folds with them; a fitted shell can't fold (fold the parts it wraps); hard parts can't; colour borders follow the
unfolded shapes (a belt doesn't wiggle).

On a capsule or a tube (a trouser leg, a sleeve) the folds run round its own axis (a tube's: from its first point to
its last), wherever it points, faded by the height of the nearest point on that axis. `bunch: true` stacks `count`
rings across the axis instead, over `from_y`..`to_y`: cloth bunched at an ankle or a wrist.

```yaml
  - capsule: { from: [0.1, 0.12, 0], to: [0.1, 0.9, 0], radius: 0.09 }
    id: lowerleg_l
    folds: { count: 4, depth: 0.012, from_y: 0.05, to_y: 0.35, bunch: true }
```

### Relief: fur without parts

Fur, and any coat of small overlapping tufts, is a `relief:` layer on one smooth body, never hundreds of clump
parts: the patches live in the baked normal map and a base colour map, so they cost no parts, no cells and no
triangles (a 12-part cub with three layers builds in 30 s). Needs `kiln-gen[bake]`; turns on a 1024 map unless
`normal_map:` sets the size.

```yaml
relief:
  - on: [body, arm_l, arm_r, leg_l, leg_r]   # ids of the smooth parts it covers (a mirror twin by its own mirror_id)
    # or on_colors: [fur, fur_dark]: only faces painted in those colours (alone: on every smooth part; with on:, both);
    # except: [face, chest]: ids left bare. kind: fur (notched tips), scales (a round lobe), feathers (one point,
    # a rib) or shingles (a straight edge). flow: along follows each part's own axis out from the body (fur down an
    # arm whichever way it points). displace: true also moves the mesh out by the layer (tufts break the silhouette;
    # the mesh must be fine enough to show them). LODs stamp the full build's patches. Lint W133: patches under four
    # texels wide blur out.
    length: 0.08      # metres, root to tip along the flow (default 0.09)
    width: 0.045      # metres across (0.05)
    lift: 0.007       # metres the tip stands off the surface (0.008): the depth of the shading
    density: 1.6      # 1 just covers the surface; more overlaps like roof tiles (1)
    flow: down        # down | up | [x, y, z]: the way the tips point (down)
    tips: 3           # pointed tips along a patch's lower edge (3)
    jitter: 0.3       # 0..1 variation of size and angle (0.3)
    color: bark       # optional root colour and tip colour; without them a patch has the colour of the surface
    color_to: wood
    under: 0.4        # 0..1: how much darker the surface is just below each tip (0.3)
    fade: 0.06        # metres over which patches thin out and shrink toward the edge of `on`: no hard bib (0.06)
    seed: 1
```

- Layers apply in order; give the body long patches, the head and hands shorter ones (`length` about a tenth of the
  part's size), a pale belly or muzzle its own short layer with `fade`.
- Model the body as a few big blended parts first; the silhouette stays the mesh's (relief does not move it).
- A patch is flat: on a thin limb lying across the flow it wraps badly; point `flow` along the limb there.
- Patches stay on the parts in `on`: eyes, a nose, claws and glowing or hard parts next to them stay clean.
  `normal_strength` scales the layer's shading with the rest of the map. `preview --draft` shows no relief.
- The model's colours are then in `<name>.color.png` on the normal map's UVs (one material per preset; a variant has
  its own map and glb). Manifest: `color_map` (`png`, `size`, `patches`). Example: `kiln examples cub` (prints it).

### Soft colour borders: `color_blend`

A part's colour meets its neighbours' in a crisp border by default. `color_blend: 0.05` on a part (metres, 0 to
0.5) fades its colour into theirs over that distance either side of the border: a pale belly or muzzle melting into
the fur, a tan chest, a sunburnt nose.

```yaml
  - ellipsoid: { at: [0, 0.4, 0.13], radii: [0.17, 0.2, 0.12] }
    id: belly
    color: rope
    blend: 0.05
    color_blend: 0.04    # the wider of two neighbours' values is used on their border
```

- The fade is painted in the base colour map (the same map relief uses, `<name>.color.png`; it comes on with a 1024
  map unless `normal_map:` sets the size; needs `kiln-gen[bake]`; under `atlas = true` the model leaves the atlas).
  The mesh and its border don't change. `preview --draft` shows no fade.
- A border fades when one of its two parts asks and the later of them joins the other with a `blend`: a nose or an
  eye set on with a crisp seam (`blend: 0`) stays sharp next to a fading muzzle. The wider of the two values is used.
- Colours mix in OKLab, half and half on the border, toward what the neighbour looks like (its fur, if it has
  relief). A part's own pattern stripes and gradient bands stay crisp.
- Borders with hard parts, glowing materials and decals stay crisp. Lint W127: a `color_blend` that fades nothing.
- Where three colours meet, the two others mix in by their own distances: all three meet as equals at the corner.
- Without the maps (`normal_map: 0` in the model, or `kiln-gen[bake]` not installed) the fade goes per vertex
  instead, in COLOR_0: set `vertex_colors = true` in kiln.toml (else lint W134: the glb keeps crisp borders). It is
  as fine as the mesh (a few cells wide), with no fur under it.

## Textures

Decals (an image on one spot) and textures (an image tiled over a whole part): image files, named textures,
triplanar projection, motif prints, palette-indexed and generated pixel art that variants recolour.

### Decals

```yaml
    decal: { image: decals/logo.png, axis: z, at: [0, 0.6, 0.3], size: [0.2, 0.1] }
```

Projects an image (PNG with transparency, e.g. made with PAGAN) onto the faces of this part that face `axis`
(x, -x, y, -y, z, -z), centred at `at` (model space, on or near the surface), `size` = width, height in metres. It
shows on that side only (a flag needs a second decal with `axis: -z` for its back). Transparent pixels show the part's colour.
The image is upright and unmirrored seen from the side it faces: on a side axis (x, z) its top is +y; facing +y its
top points to -z (the back), facing -y to +z. A part turned 180 degrees with its decal still reads right only if the
decal's `axis` turns with it (write the axis it ends up facing).
Small images (<= 256 px) are sampled crisp (pixel art). `texel: 0.004` instead of `size`: metres per image pixel, so
props at different scales keep the same pixel size. On an arrayed part, `per_copy: true` puts the decal on every
copy, placed on each as written for the first (a badge on each of 12 links); the copies share one texture.

### Textures

```yaml
    texture: { image: textures/brushed.png, project: box, texel: 0.004 }                       # every face, from the side it faces
    texture: { image: textures/trim.png, project: cylindrical, at: [0, 0, 0], axis: y, size: [0.1, 0.05] }
```

Tiles an image over the whole part (a shirt print, pixel-art metal, a trim band), as one material. `box`: each face
takes it from the side it faces (its main normal direction, no blending), upright seen from there. `cylindrical`:
round `axis` through `at` (u = arc length: texels keep their size), caps taken flat; seam at -z for `axis: y`, -y
for x, -x for z (it shows unless the circumference is whole tiles). `at`: the part's centre by default. Cylindrical
can't follow `mirror`/`array` copies: use `mirror_id` or `box`. Tile: `size: [w, h]` metres or `texel:` metres per
pixel. It repeats; images up to 256 px on their longer side are crisp (nearest filtering, no mipmaps: pixel art on
smooth shapes); larger ones are filtered smoothly (linear, with mipmaps), at full size: no cap, so keep them as small
as the look needs. Cylindrical: v = 0 is at the part's `at` height, the image's bottom row toward low y. Clear pixels show the part's colour
(after swaps); its pattern colours paint over it; a `decal` replaces it there. `triplanar`: box UVs in the glb, but
KILN's Godot scenes (standard looks) and the previews blend the three projections by the surface's facing, so no seam
shows where box would switch sides (a sleeve's side).

A texture used on several parts is defined once at the top and named: `textures: { print: { image:
textures/print.png, project: triplanar, texel: 0.004 } }`, then `texture: print` on each part.

A busy multicolour print (flowers, leaves) made in KILN: `motif:` in place of `image` scatters stamps from a list of
PNGs (alpha, any colours) over one seamless tile, seeded: `texture: { motif: { images: [decals/flower.png,
decals/leaf.png], count: 14, scale: [0.12, 0.2], rotate: 180, seed: 2 }, project: triplanar, size: [0.14, 0.14] }`
(`scale`: a stamp's size as a share of the tile, up to 0.5 to wrap cleanly; `pixels`: the tile, 256). The tile is
written once to `.kiln-cache/motifs/`.

### Pixel art in palette colours

A texture written as rows of characters, each a palette colour (`.` or a space: the part's own colour shows), is
recoloured by variants like the parts around it; `generate:` makes one in palette colours (brushed metal, specks,
scratches, a grid, noise; `colors`: base, marks and an optional highlight; `pixels`: 32; `seed`).

```yaml
    texture: { rows: ["ab..", "ba.."], key: { a: red, b: gold }, project: box, texel: 0.01 }
    texture: { generate: brushed, colors: [steel, iron, white], pixels: 32, project: triplanar, texel: 0.004 }
```

A variant then gets its own glb (its texture in its colours). With variants, a pixel-art image (up to 256 px) whose
pixels aren't palette colours is lint W137: the variants can't swap them.
