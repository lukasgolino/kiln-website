# Style

How the machine showpieces look, so a third one would fit beside them. The style file
(`styles/foundry.style.toml`, shown by `kiln style show`) holds the numbers; this file holds the words and the
history.

## Look

- **Preset / style file:** `foundry`, which extends the `soft_toy` preset: smooth shading with crisp designed
  edges, `hard_surface = "always"` (every part that can be is exact polygons), 24 sides on round shapes that don't
  say, material presets for paint, iron, steel, brass, copper, wood, canvas, rubber, leather, stone, glass, lamp
  and steam, and shade paint (cavity 0.26, top 0.06, under 0.12).
- **Shapes:** chunky and a little exaggerated, like a well-made model on a shelf: a fat boiler, a tall chimney, a
  big round helmet, heavy boots. Machined things are hard parts; only cloth, rubber, coal, ballast and rock are
  smooth parts.
- **Detail in three tiers:**
  1. The big forms carry the silhouette: boiler, tanks, cab, chimney and dome; helmet, breastplate, tanks, boots.
  2. Each big form is broken by things a few centimetres proud: bands, flanges, port frames, lining, beading,
     nameplates, straps, hinge straps, lids.
  3. Hardware in rows and rings: rivets, bolts, studs and wing nuts, handrail knobs, buckles. Hardware is always a
     real part, never paint, and sits half sunk in the surface it holds.
- **Proportions:** the engine is 3.2 m long, 1.4 m wide and 2.3 m to the chimney's lip on 0.58 m wheels. The diver
  is about four helmets tall, with thick limbs and big gloves.
- **Colours:** palette `workshop`. One painted body colour per machine (the engine's green, the suit's canvas) with
  a lining colour (cream), red for buffer beams, wheels and valve wheels, brass and copper for everything a fitter
  would polish, dark iron for frames and running gear, bright steel for rods and tyres, warm wood where hands and
  feet go. Rivets take the colour of the plate they are in; bolts on brass are a shade brighter.
- **Materials:** paint is smooth and barely metallic; iron, steel, brass and copper are 0.3 to 0.42 metallic with
  roughness 0.3 to 0.6; canvas, wood, stone and steam are matte. Lamps and the firehole glow.
- **Lighting:** a high sun from the front left, a pale sky and a warm ground colour, with a weak fill from the
  other side. The website's viewer takes these from the style's `[look]`; the previews use the same.

## Rules

- Units are metres; models stand on y = 0 and face +Z.
- Every colour comes from the palette (names, not hexes).
- The `.kiln.yaml` files are generated: edit `models/<name>.py` and run it again, never the YAML.
- Generators are deterministic: no random numbers, numbers rounded to a tenth of a millimetre. Running one twice
  writes the same file.
- Rounded rims on round things: a `lathe` with a `bevel`. A `cylinder` with a bevel is ten times the triangles.
  Bevels on boxes only where the edge shows (`bevel_edges`); small boxes stay plain.
- Round shapes say their `sides`: 44 to 48 for the big forms, 16 to 28 for fittings, 6 to 8 for bars, nuts and
  rivets.
- Parts that belong together share an id, and each id is joined as its own solid: keep hardware in its own id
  (`rivets`, `lining`), sunk a little into the plate so the two pieces overlap.
- Parts that move get their own id and a pivot at the joint or axle. Rods are moved by offsets worked out from the
  crank angle, never by eye.
- Things that only show in an animation (smoke, bubbles) wait inside a solid, each in its own place.
- `export = ["glb"]` only; no maps: the colours are materials and the shade is in the vertex colours.

## Changelog

`kiln style bump --message "..."` adds an entry here and raises `style_version`; `kiln status` then lists models
made under an older style for review.

- v1: first version. Locomotive and diver.
