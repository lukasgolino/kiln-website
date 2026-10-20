"""Build every KILN asset the site shows, with the pinned KILN release (requirements.txt).

    python tools/build_site_assets.py --kiln-repo ../KILN

Writes:
  public/models/<style>/<model>.glb   the demo project (art/demo) built once per style: the real files a game loads
  public/data/site.json               per style: the resolved look; per model: manifest entry, triangles per style
  public/img/                         KILN's own previews: line-up, turntable, filmstrip, the lint story, Godot screenshot
  public/brand/                       the icon (art/brand/models/pot.kiln.yaml) rendered by KILN
  public/og/                          the social card
  src/content/docs/                   reference.md, SKILL.md (workflow) and CHANGELOG.md, plus meta.json
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import shutil
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

import kiln
from kiln.builder import build_cached
from kiln.preview import filmstrip, lineup, turntable
from kiln.project import load_project
from kiln.render import View, render

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "art"
STYLES = ["soft_toy", "low_poly", "toon"]
KILN = [sys.executable, "-m", "kiln"]


def kiln_cli(args: list[str], cwd: Path) -> dict[str, Any]:
    done = subprocess.run([*KILN, *args, "--json"], cwd=cwd, capture_output=True, text=True)
    result: dict[str, Any] = json.loads(done.stdout)
    if done.returncode and args[0] != "lint":
        raise SystemExit(f"kiln {' '.join(args)} failed in {cwd}:\n{done.stdout}\n{done.stderr}")
    return result


def copy_project(src: Path, dst: Path, style: str | None = None) -> Path:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("build", "previews", ".kiln-cache"))
    if style:
        toml = dst / "kiln.toml"
        text = toml.read_text(encoding="utf-8").replace('default_style = "soft_toy"', f'default_style = "{style}"')
        toml.write_text(text, encoding="utf-8")
    return dst


def builts(root: Path) -> dict[str, Any]:
    project = load_project(root)
    palette, _ = project.palette()
    out = {}
    for path in project.model_paths():
        model, style, findings = project.load(path)
        assert model and style, findings
        out[model.name] = build_cached(model, style, palette, None)
    return out


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def models(public: Path, work: Path) -> dict[str, Any]:
    """The demo once per style: glbs + manifest entries + the style's resolved look."""
    data: dict[str, Any] = {"styles": {}, "models": {}}
    for style in STYLES:
        project = copy_project(ART / "demo", work / style, style)
        kiln_cli(["build"], project)
        manifest = json.loads((project / "build" / "manifest.json").read_text(encoding="utf-8"))
        (public / "models" / style).mkdir(parents=True, exist_ok=True)
        for name, entry in manifest["models"].items():
            shutil.copyfile(project / "build" / entry["glb"], public / "models" / style / f"{name}.glb")
            model = data["models"].setdefault(name, {"triangles": {}})
            model["triangles"][style] = entry["triangles"]
            if style == "soft_toy":
                source = (ART / "demo" / "models" / f"{name}.kiln.yaml").read_text(encoding="utf-8")
                model.update(
                    description=entry["description"],
                    cls=entry["class"],
                    height=round(entry["bounds"]["max"][1] - entry["bounds"]["min"][1], 2),
                    parts=len(entry["parts"]),
                    animations={k: {"loop": a["loop"], "fps": a["fps"], "gltf": a["gltf_name"]} for k, a in entry["animations"].items()},
                    variants=sorted(entry.get("variants", {})),
                    source_lines=len(source.rstrip("\n").split("\n")),
                )
        loaded, _ = load_project(project).style()
        assert loaded
        data["styles"][style] = {
            "description": loaded.description,
            "smooth": loaded.smooth,
            "look": dataclasses.asdict(loaded.look),
            "materials": {k: dataclasses.asdict(v) for k, v in sorted(loaded.materials.items())},
        }
    return data


def images(public: Path, work: Path, kiln_repo: Path) -> dict[str, Any]:
    img = public / "img"
    soft = builts(work / "soft_toy")
    save(lineup([soft[n] for n in ("pilot", "passenger", "knight", "archer", "barrel", "seat", "tree")], 420), img / "lineup.png")
    save(turntable(soft["knight"], 200), img / "knight-turntable.png")
    save(filmstrip(soft["trebuchet"], "fire", 180), img / "trebuchet-fire.png")
    # the lint story: the archer's first draft (bow left floating) and the fix, from the same view
    before = copy_project(ART / "features" / "archer-v1", work / "archer-v1")
    lint = kiln_cli(["lint"], before)
    first = builts(before)["archer"]
    view = View(yaw=35, pitch=12)
    fit = ((first.bounds()[0] + first.bounds()[1]) / 2, 0.95)
    save(render(first, view, 320, fit=fit), img / "archer-before.png")
    save(render(soft["archer"], view, 320, fit=fit), img / "archer-after.png")
    after = kiln_cli(["lint", "archer"], work / "soft_toy")
    # the same pilot in each style, for the style picker's still fallback
    for style in STYLES:
        b = soft["pilot"] if style == "soft_toy" else builts(work / style)["pilot"]
        save(render(b, View(yaw=25, pitch=12), 300), img / f"pilot-{style}.png")
    for name, b in soft.items():
        save(render(b, View(yaw=25, pitch=12), 240), img / "thumbs" / f"{name}.png")
    shutil.copyfile(kiln_repo / "docs" / "showcase.png", img / "godot-showcase.png")
    return {
        "before": {"findings": lint["findings"], "warnings": lint["warnings"]},
        "after": {"warnings": after["warnings"], "errors": after["errors"]},
        "diff": diff_lines(ART / "features" / "archer-v1" / "models" / "archer.kiln.yaml", ART / "demo" / "models" / "archer.kiln.yaml"),
    }


def diff_lines(a: Path, b: Path) -> str:
    import difflib

    lines = difflib.unified_diff(
        a.read_text(encoding="utf-8").splitlines(), b.read_text(encoding="utf-8").splitlines(), "archer.kiln.yaml", "archer.kiln.yaml", n=1, lineterm=""
    )
    return "\n".join(lines)


def brand(public: Path, work: Path) -> Image.Image:
    project = copy_project(ART / "brand", work / "brand")
    pot = builts(project)["pot"]
    big = render(pot, View(yaw=18, pitch=14), 512)
    out = public / "brand"
    for size in (16, 32, 64, 180, 512):
        save(big.resize((size, size), Image.Resampling.LANCZOS), out / f"pot-{size}.png")
    return big


def og(public: Path, pot: Image.Image) -> None:
    line = Image.open(public / "img" / "lineup.png").convert("RGBA")
    card = Image.new("RGBA", (1200, 630), "#1b1310")
    scale = min(1100 / line.width, 380 / line.height)
    line = line.resize((round(line.width * scale), round(line.height * scale)), Image.Resampling.LANCZOS)
    card.alpha_composite(line, ((1200 - line.width) // 2, 630 - line.height - 30))
    card.alpha_composite(pot.resize((150, 150), Image.Resampling.LANCZOS), (50, 40))
    draw = ImageDraw.Draw(card)
    draw.text((215, 52), "KILN", fill="#fff4e4", font=ImageFont.load_default(84))
    draw.text((218, 150), "Smooth 3D game models, written as text by your agent", fill="#ffb347", font=ImageFont.load_default(30))
    save(card.convert("RGB"), public / "og" / "kiln.png")


def docs(content: Path, kiln_repo: Path) -> None:
    """One source of truth: the reference and workflow ship inside the kiln package; the changelog comes from
    a KILN checkout."""
    out = content / "docs"
    out.mkdir(parents=True)
    skill = Path(kiln.__file__).parent / "skill"
    shutil.copyfile(skill / "reference.md", out / "reference.md")
    workflow = (skill / "SKILL.md").read_text(encoding="utf-8")
    workflow = workflow.split("---\n", 2)[2].lstrip() if workflow.startswith("---\n") else workflow
    (out / "workflow.md").write_text(workflow.replace("](reference.md)", "](../reference/)"), encoding="utf-8")
    shutil.copyfile(kiln_repo / "CHANGELOG.md", out / "changelog.md")
    write_json(out / "meta.json", {"kiln": metadata.version("kiln")})


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--kiln-repo", type=Path, default=os.environ.get("KILN_REPO"), required="KILN_REPO" not in os.environ)
    args = parser.parse_args()
    kiln_repo = Path(args.kiln_repo).resolve()
    if not (kiln_repo / "CHANGELOG.md").is_file():
        raise SystemExit(f"{kiln_repo} isn't a KILN checkout (no CHANGELOG.md)")
    public, content = ROOT / "public", ROOT / "src" / "content"
    for target in (public / "models", public / "data", public / "img", public / "brand", public / "og", content / "docs"):
        if target.exists():
            shutil.rmtree(target)
    with tempfile.TemporaryDirectory(prefix="kiln-site-") as tmp:
        work = Path(tmp)
        data = models(public, work)
        data["lint"] = images(public, work, kiln_repo)
        data["kiln"] = metadata.version("kiln")
        write_json(public / "data" / "site.json", data)
        og(public, brand(public, work))
        docs(content, kiln_repo)
    print(f"Built {len(data['models'])} models x {len(STYLES)} styles with kiln {data['kiln']}.")


if __name__ == "__main__":
    main()
