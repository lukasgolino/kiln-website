# Style

How the showpieces look, so a third one would fit beside them. The style file (`styles/showpiece.style.toml`, shown
by `kiln style show`) holds the numbers; this file holds the words and the history.

## Look

- **Preset / style file:** `showpiece`, which extends the `skin` preset: matte painted surfaces, colours that fade
  where parts blend, shade paint in the crevices. It adds material presets for scale, plate, membrane, feather,
  horn, claw, ivory, eye, bark and moss, and an 80 000 triangle budget for creatures.
- **Shapes:** one continuous sculpted body per creature, made of a few big blended forms: chunky, readable from far
  away. Nothing is thin unless it is meant to be (membranes, feathers, blades).
- **Detail in three kinds:**
  1. The coat (scales, small feathers, bark, moss) is `relief:` on the body, displaced, with a lighter tip colour
     and a darker shade under each tip. It costs no parts and no triangles.
  2. What makes the silhouette is real parts, written in rows by the generator scripts: back spines, belly plates,
     horns, teeth, wing fingers and membranes; wing and tail feathers, ear tufts, the skirt over the legs, toes and
     talons.
  3. Hard things sit on the surface with a crisp seam (`blend: 0`): claws, teeth, beak, eyes, pupils. Soft things
     melt in with `color_blend`: a throat, a facial disc, the dark band down a back.
- **Proportions:** big heads (the dragon's is drawn at 1 : 1.3), heavy feet, large eyes with a clear pupil.
- **Colours:** palette `creatures`. Forest greens, creams and browns; one warm accent per creature (rust wings and
  spines on the dragon, gold eyes on the owl). Repeated parts run from a darker root to a lighter tip (`gradient`),
  so every row reads as a row.
- **Materials:** everything matte, except eyes (roughness 0.12), claws, teeth and horn (0.35 to 0.45).
- **Lighting:** none of ours. The models are shown in a browser through the standard glTF material, so the look
  comes from geometry, vertex and map colour, shade paint and the baked normal map. Previews use the `skin`
  preset's soft light; that light is not part of the look.

## Rules

- Units are metres; models stand on y = 0 and face +Z.
- Every colour comes from the palette (names, not hexes).
- The `.kiln.yaml` files are generated: edit `models/<name>.py` and run it again, never the YAML.
- Generators are deterministic: fixed seeds, numbers rounded to a tenth of a millimetre. Running one twice writes the
  same file.
- A coat is relief, not parts. A repeated part earns its place only when it shows in the silhouette or in a close-up.
- Rows overlap like roof tiles: each part's root is sunk into the surface, its tip stands proud, and the next row
  starts under it.
- Relief layers name the colours they cover (`on_colors`), so they stay off plates, horn, membranes and the feather
  parts.
- Parts that move get their own id and a pivot at the joint: jaws, eyelids, ear tufts, wing tips, tail segments.
- What stands on the ground stays there: feet hang from a bone no animation moves (the dragon's `body`, the owl's
  `feet`), and a perch keeps its own weights (`skin_falloff: 0`).
- Maps are 2048: at 1024 the dragon's scales come out as blocks.
- `export = ["glb"]` only; the maps (`<name>.color.png`, `<name>.normal.png`) are written beside the glb.

## Changelog

- v1: first version. Dragon and owl.
