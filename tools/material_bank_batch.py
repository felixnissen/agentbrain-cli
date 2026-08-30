#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

UA = "AI-Asset-Department/0.1 (+https://github.com/felixnissen/AI-Asset-Department)"


def download(url: str, dest: Path, required: bool = True) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180) as r, dest.open("wb") as f:
            shutil.copyfileobj(r, f)
        if dest.stat().st_size == 0:
            raise RuntimeError("empty download")
        print(f"OK {url} -> {dest} ({dest.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"WARN {url}: {e}", file=sys.stderr)
        if dest.exists():
            dest.unlink()
        if required:
            raise
        return False


def download_first(urls: list[str], dest: Path, required: bool = True) -> bool:
    for url in urls:
        if download(url, dest, required=False):
            return True
    if required:
        raise RuntimeError(f"All download URLs failed for {dest}")
    return False


def clone(repo: str, dest: Path, branch: str | None = None, required: bool = True) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd += ["--branch", branch]
    cmd += [f"https://github.com/{repo}.git", str(dest)]
    try:
        subprocess.run(cmd, check=True)
        shutil.rmtree(dest / ".git", ignore_errors=True)
        print(f"OK clone {repo} -> {dest}")
        return True
    except Exception as e:
        print(f"WARN clone {repo}: {e}", file=sys.stderr)
        shutil.rmtree(dest, ignore_errors=True)
        if required:
            raise
        return False


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(root: Path, sources: list[dict]) -> None:
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            files.append({"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)})
    payload = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sources": sources, "files": files}
    (root / "INVENTORY.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (root / "SOURCES.md").write_text("# Sources\n\n" + "\n".join(
        f"- **{s['name']}** — {s['source']} — {s['rights']} — status: {s['status']}" for s in sources
    ) + "\n", encoding="utf-8")


def add(records: list[dict], name: str, source: str, rights: str, ok: bool) -> None:
    records.append({"name": name, "source": source, "rights": rights, "status": "downloaded" if ok else "failed"})


def build(root: Path) -> None:
    books, assets, datasets, repos = (root / x for x in ["books", "assets", "datasets", "repos"])
    for d in [books, assets, datasets, repos]: d.mkdir(parents=True, exist_ok=True)
    br: list[dict] = []; ar: list[dict] = []; dr: list[dict] = []; rr: list[dict] = []

    # BOOKS / LONG-FORM KNOWLEDGE
    ok = clone("RayTracing/raytracing.github.io", books / "Ray_Tracing_in_One_Weekend_Series", branch="release")
    add(br, "Ray Tracing in One Weekend series", "https://raytracing.github.io/", "CC0-1.0; official repo contains all three books and code.", ok)

    ok = clone("nature-of-code/noc-book-2-archive", books / "The_Nature_of_Code_Source", branch="source")
    add(br, "The Nature of Code source archive", "https://github.com/nature-of-code/noc-book-2-archive", "Book content Creative Commons Attribution-NonCommercial; example code MIT. Preserve attribution/non-commercial restriction.", ok)

    pcg = books / "Procedural_Content_Generation_in_Games"
    pcg_ok = True
    for n in ["preface.pdf"] + [f"chapter{i:02d}.pdf" for i in range(1, 13)] + ["interviews.pdf"]:
        pcg_ok = download(f"https://www.pcgbook.com/{n}", pcg / n, required=False) and pcg_ok
    add(br, "Procedural Content Generation in Games — author PDFs", "https://www.pcgbook.com/", "Official final author-version PDFs retained online under publication agreement; private research use, do not infer redistribution rights.", pcg_ok)

    # REFERENCE REPOS
    for name, repo, rights in [
        ("book-to-skill", "virgiliojr94/book-to-skill", "MIT converter; source-document rights still apply to generated skills."),
        ("book2skills", "simbajigege/book2skills", "MIT repository code; individual distilled skill content may carry source-specific restrictions."),
        ("Godot demo projects", "godotengine/godot-demo-projects", "MIT project; demo assets are required to be redistributable/modifiable by contribution policy."),
    ]:
        ok = clone(repo, repos / name.replace(" ", "_"), required=False)
        add(rr, name, f"https://github.com/{repo}", rights, ok)

    # OPEN GAME ASSET PACKS — official OpenGameArt mirrors of Kenney CC0 packs
    kenney = [
        ("UI Pack", "https://opengameart.org/sites/default/files/kenney_ui-pack.zip", "kenney_ui-pack.zip"),
        ("Prototype Kit", "https://opengameart.org/sites/default/files/kenney_prototype-kit.zip", "kenney_prototype-kit.zip"),
        ("Nature Kit", "https://opengameart.org/sites/default/files/Nature%20Kit%20%282.1%29.zip", "kenney_nature-kit_2.1.zip"),
        ("Space Kit Remade", "https://opengameart.org/sites/default/files/spacekit_2.0.zip", "kenney_spacekit_2.0.zip"),
        ("Platformer Kit", "https://opengameart.org/sites/default/files/kenney_platformer-kit_4.1.zip", "kenney_platformer-kit_4.1.zip"),
        ("RPG Sound Effects", "https://opengameart.org/sites/default/files/RPGsounds_Kenney.zip", "kenney_rpg_sounds.zip"),
        ("UI Sound Effects", "https://opengameart.org/sites/default/files/UI_SFX_Set.zip", "kenney_ui_sfx.zip"),
        ("Sci-Fi Sounds", "https://opengameart.org/sites/default/files/sci-fi_sounds.zip", "kenney_scifi_sounds.zip"),
        ("Game Icons", "https://opengameart.org/sites/default/files/Kenney_gameIcons.zip", "kenney_game_icons.zip"),
        ("Short Music Jingles", "https://opengameart.org/sites/default/files/jingleSounds_Kenney.zip", "kenney_music_jingles.zip"),
    ]
    for name, url, fn in kenney:
        ok = download(url, assets / "Kenney_CC0" / fn, required=False)
        add(ar, f"Kenney {name}", url, "CC0 on the corresponding OpenGameArt source page.", ok)

    ok = clone("J-Beardmore/FreeMotionPack1", assets / "Animation_CC0" / "FreeMotionPack1", required=False)
    add(ar, "FreeMotionPack1 — 21 FBX mocap animations", "https://github.com/J-Beardmore/FreeMotionPack1", "CC0-1.0.", ok)

    # DATASETS
    ok = download_first(["https://mocap.cs.cmu.edu/allasfamc.zip", "http://mocap.cs.cmu.edu/allasfamc.zip"], datasets / "CMU_Mocap" / "allasfamc.zip", required=False)
    add(dr, "CMU Motion Capture Database bulk ASF/AMC", "https://mocap.cs.cmu.edu/", "Free for all uses incl. commercial; copy/modify/redistribute allowed; may not resell motion data itself; acknowledgement requested.", ok)

    ok = clone("KhronosGroup/glTF-Sample-Assets", datasets / "Khronos_glTF_Sample_Assets", required=False)
    add(dr, "Khronos glTF Sample Assets", "https://github.com/KhronosGroup/glTF-Sample-Assets", "Per-asset SPDX/REUSE licensing is authoritative; preserve each asset's license metadata.", ok)

    for directory, records in [(books, br), (assets, ar), (datasets, dr), (repos, rr)]:
        manifest(directory, records)

    failures = [x for x in br + ar + dr + rr if x["status"] != "downloaded"]
    (root / "BATCH_STATUS.json").write_text(json.dumps({"failures": failures, "failure_count": len(failures)}, indent=2), encoding="utf-8")
    print(f"Batch complete with {len(failures)} non-fatal source failures")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="material-bank-batch-001"); args = ap.parse_args()
    out = Path(args.out).resolve(); shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
    build(out)
