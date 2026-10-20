# KILN website

The website for [KILN](https://github.com/lukasgolino/KILN) (Keyed Implicit Language & Notation): one long page
(hero, styles, features, comparison, gallery, install, FAQ) and docs generated from KILN's own files. Static Astro
site, no backend, deployed to GitHub Pages.

**Every model and image on the site is real KILN output**, built from the KILN projects in `art/`. The 3D viewer
(`src/scripts/viewer.ts`, three.js) loads the same `.glb` files a game would and lights them with each style's look.

## Layout

```
art/
  demo/                 the demo project (a toy airline and a toy siege), built once per style
  features/archer-v1/   the archer's first draft, with the bow left floating (the lint feature)
  brand/                the icon: a clay pot (models/pot.kiln.yaml)
tools/build_site_assets.py   builds everything with KILN -> public/models, public/data, public/img, public/brand,
                             public/og, src/content/docs
src/                    the Astro site (components/, scripts/viewer.ts for the 3D viewer)
```

## Commands

```sh
npm ci
npm run dev                  # http://localhost:4321
npm run build                # -> dist/

# after changing anything in art/ or upgrading KILN (needs Python 3.11+; takes a few minutes)
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python tools/build_site_assets.py --kiln-repo ../KILN   # a KILN checkout, for CHANGELOG.md and the Godot screenshot
```

Commit `public/` and `src/content/docs` with the art. Upgrading KILN: bump the tag in `requirements.txt`, rebuild,
look at the result.

There is no CI check that the committed assets match a fresh build (as the PAGAN site has): KILN's `.glb` output is
deterministic on one machine but not yet byte-identical across machines.

Deep links: `/?style=toon&model=knight#styles` opens the style picker on that style and model.

## Deploy

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every push to `main` (Pages source: GitHub
Actions). The base path comes from the Pages settings, so it works as a project page or on a custom domain.

## License

MIT, like KILN: see [LICENSE](LICENSE).
