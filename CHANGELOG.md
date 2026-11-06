# Changelog

All notable changes to this site are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the site uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-11-06

### Added

- A standard icon set: `favicon.ico` (16/32/48 px), a 96 px icon, a 180 px apple-touch icon and `site.webmanifest`
  with 192/512 px and maskable icons, so search results, tabs, bookmarks and home-screen shortcuts all show the
  icon ([#7](https://github.com/lukasgolino/kiln-website/issues/7)).
- schema.org structured data (JSON-LD) on the home page, an `llms.txt` summary for AI assistants, and robots.txt
  content signals allowing search and AI use; the home page title names what the site is for
  ([#8](https://github.com/lukasgolino/kiln-website/issues/8)).

## [0.1.0] - 2026-11-06

### Added

- The site moves to its own domain, https://kiln3d.dev/ (it was https://lukasgolino.com/kiln-website/, which now
  redirects) ([#3](https://github.com/lukasgolino/kiln-website/issues/3)).
- `sitemap.xml` and `robots.txt`, generated from the pages and the site URL
  ([#2](https://github.com/lukasgolino/kiln-website/issues/2)).
- Cloudflare Web Analytics beacon on every page, production builds only
  ([#4](https://github.com/lukasgolino/kiln-website/issues/4)).
- This changelog, version tags, a notes-only GitHub release per `vX.Y.Z` tag, and a check on every push (`astro
  check`, build, and `tools/check-dist.mjs`: the sitemap lists exactly the built pages, robots.txt points to it, every
  page loads the beacon). Deploys run the same built-site check
  ([#5](https://github.com/lukasgolino/kiln-website/issues/5)).

### Fixed

- `astro check` errors: `aria-pressed` was passed as a string in the gallery and style pickers
  ([#1](https://github.com/lukasgolino/kiln-website/issues/1)).

[Unreleased]: https://github.com/lukasgolino/kiln-website/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/lukasgolino/kiln-website/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/lukasgolino/kiln-website/releases/tag/v0.1.0
