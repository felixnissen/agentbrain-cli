#!/usr/bin/env python3
"""Build material-bank batch 002: game-dev knowledge, reference implementations and CC0 assets.

Conservative rules:
- exact source snapshots may be stored when redistribution is explicitly permitted;
- NO-DERIVATIVES prose is tagged READ_ONLY and must never be fed to derivative skill generation;
- reusable code/assets are tagged by license class;
- every downloaded file receives provenance + SHA-256 inventory;
- transport volumes are <=90 MiB for the current Drive bridge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "AI-Asset-Department/0.2 (+https://github.com/felixnissen/AI-Asset-Department)"
PART_BYTES = 90 * 1024 * 1024


def get_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def get_json(url: str):
    return json.loads(get_bytes(url).decode("utf-8"))


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)
    if dest.stat().st_size == 0:
        raise RuntimeError(f"empty download: {url}")
    print(f"OK download {url} -> {dest} ({dest.stat().st_size} bytes)")


def clone(repo: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(dest)], check=True)
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print(f"OK clone {repo} -> {dest}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root: Path, sources: list[dict]) -> None:
    files = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            files.append({"path": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)})
    (root / "INVENTORY.json").write_text(json.dumps({
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": sources,
        "files": files,
    }, indent=2), encoding="utf-8")
    (root / "SOURCES.md").write_text("# Sources\n\n" + "\n".join(
        f"- **{s['name']}** — {s['source']} — `{s['usage_class']}` — {s['rights']}" for s in sources
    ) + "\n", encoding="utf-8")


def walk_download_leaves(value, path=()):
    leaves = []
    if isinstance(value, dict):
        if isinstance(value.get("url"), str):
            leaves.append((path, value))
        for k, v in value.items():
            leaves.extend(walk_download_leaves(v, path + (str(k),)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            leaves.extend(walk_download_leaves(v, path + (str(i),)))
    return leaves


def polyhaven_assets(out: Path, sources: list[dict]) -> None:
    catalog = get_json("https://api.polyhaven.com/assets")
    known_hdri = ["sunset_jhbcentral", "kloppenheim_01", "preller_drive", "green_sanctuary", "montorfano", "barnaslingan_01"]
    known_tex = ["concrete_floor_01", "book_pattern", "red_plaster_weathered"]

    def top_ids(asset_type: int, count: int, exclude: set[str]):
        rows = [(int(meta.get("download_count") or 0), aid) for aid, meta in catalog.items() if meta.get("type") == asset_type and aid not in exclude]
        rows.sort(reverse=True)
        return [aid for _, aid in rows[:count]]

    tex_ids = known_tex + top_ids(1, 3, set(known_tex))
    model_ids = top_ids(2, 5, set())
    selections = [(0, aid) for aid in known_hdri] + [(1, aid) for aid in tex_ids] + [(2, aid) for aid in model_ids]

    for typ, aid in selections:
        meta = catalog[aid]
        files = get_json(f"https://api.polyhaven.com/files/{aid}")
        target = out / "PolyHaven_CC0_1K" / aid
        target.mkdir(parents=True, exist_ok=True)
        (target / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        (target / "files_api.json").write_text(json.dumps(files, indent=2), encoding="utf-8")
        leaves = walk_download_leaves(files)

        candidates = []
        for keypath, leaf in leaves:
            url = leaf.get("url", "")
            size = int(leaf.get("size") or 10**18)
            text = ("/".join(keypath) + " " + url).lower()
            ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
            if size > 20 * 1024 * 1024:
                continue
            if typ == 0:
                if "1k" in text and ext in {".hdr", ".exr"}:
                    score = (0 if ext == ".hdr" else 1, size)
                    candidates.append((score, url, size))
            elif typ == 1:
                useful = any(k in text for k in ["diff", "col", "albedo", "nor_gl", "normal", "rough", "arm", "disp", "ao"])
                if "1k" in text and useful and ext in {".jpg", ".jpeg", ".png", ".exr"}:
                    candidates.append(((size,), url, size))
            else:
                if "1k" in text and ext in {".gltf", ".glb", ".bin", ".jpg", ".jpeg", ".png"}:
                    candidates.append(((0 if ext in {".gltf", ".glb"} else 1, size), url, size))

        candidates.sort(key=lambda x: x[0])
        limit = 1 if typ == 0 else (6 if typ == 1 else 10)
        used = set()
        for _, url, _ in candidates[:limit]:
            name = Path(urllib.parse.unquote(urllib.parse.urlparse(url).path)).name
            if name in used:
                continue
            used.add(name)
            download(url, target / name)

        sources.append({
            "name": f"Poly Haven: {aid}",
            "source": f"https://polyhaven.com/a/{aid}",
            "usage_class": "REUSABLE_CC0",
            "rights": "Asset is CC0. Live API requires attribution to Poly Haven and a unique User-Agent; source metadata preserved.",
        })


def split_file(src: Path, prefix: Path) -> list[Path]:
    parts = []
    with src.open("rb") as f:
        i = 0
        while True:
            data = f.read(PART_BYTES)
            if not data:
                break
            p = Path(f"{prefix}.part-{i:03d}")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            parts.append(p)
            i += 1
    return parts


def build_transport(root: Path) -> None:
    transport = root / "transport"
    payload = root / "payload"
    transport.mkdir(parents=True, exist_ok=True)
    all_parts = []
    original_hashes = []
    for category in ["books", "references", "assets"]:
        src = payload / category
        tar = root / f"{category}.tar"
        subprocess.run(["tar", "-cf", str(tar), "-C", str(src), "."], check=True)
        original_hashes.append(f"{sha256(tar)}  {tar.name}")
        all_parts.extend(split_file(tar, transport / category))
        tar.unlink()

    (transport / "ORIGINAL_SHA256SUMS").write_text("\n".join(original_hashes) + "\n", encoding="utf-8")
    (transport / "SHA256SUMS").write_text("\n".join(f"{sha256(p)}  {p.name}" for p in all_parts) + "\n", encoding="utf-8")
    (transport / "REASSEMBLY.md").write_text(
        "# Batch 002 reassembly\n\nConcatenate each category's numbered parts in lexical order to recreate `<category>.tar`, verify `ORIGINAL_SHA256SUMS`, then extract the tar.\n",
        encoding="utf-8",
    )

    for i in range(0, len(all_parts), 4):
        group = transport / f"group-{i // 4:02d}"
        group.mkdir()
        for p in all_parts[i:i+4]:
            shutil.copy2(p, group / p.name)
        for meta in ["ORIGINAL_SHA256SUMS", "SHA256SUMS", "REASSEMBLY.md"]:
            shutil.copy2(transport / meta, group / meta)


def build(root: Path) -> None:
    payload = root / "payload"
    books = payload / "books"
    refs = payload / "references"
    assets = payload / "assets"
    for d in [books, refs, assets]:
        d.mkdir(parents=True, exist_ok=True)

    book_sources = []
    ref_sources = []
    asset_sources = []

    clone("munificent/game-programming-patterns", books / "Game_Programming_Patterns")
    book_sources.append({"name":"Game Programming Patterns source snapshot","source":"https://github.com/munificent/game-programming-patterns","usage_class":"READ_ONLY_MIXED","rights":"Prose/site files are CC BY-NC-ND 4.0; code files are MIT. Preserve exact source. Do not generate derivative prose/skills from NC-ND files."})

    clone("munificent/craftinginterpreters", books / "Crafting_Interpreters")
    book_sources.append({"name":"Crafting Interpreters source snapshot","source":"https://github.com/munificent/craftinginterpreters","usage_class":"READ_ONLY_MIXED","rights":"Book/illustrations/site are CC BY-NC-ND 4.0; interpreter code extensions listed in LICENSE are MIT. Preserve exact source; only MIT files are derivative-safe."})

    (books / "CATALOG_ONLY.md").write_text(
        "# Useful references not mirrored as derivative-safe source\n\n"
        "- Physically Based Rendering online book — https://pbr-book.org/ — book text CC BY-NC-ND; pbrt code is separately BSD.\n"
        "- The Book of Shaders — https://thebookofshaders.com/ — current repository states all rights reserved; catalog/link only.\n",
        encoding="utf-8",
    )

    repos = [
        ("mmp/pbrt-v4", "pbrt-v4", "REUSABLE_BSD", "pbrt implementation source; BSD-licensed code."),
        ("ssloy/tinyrenderer", "tinyrenderer", "REUSABLE_PERMISSIVE", "Tiny Renderer graphics course/code; permissive zlib-style license preserved."),
        ("recastnavigation/recastnavigation", "recastnavigation", "REUSABLE_ZLIB", "Industry-standard navmesh/pathfinding; Zlib license."),
        ("zeux/meshoptimizer", "meshoptimizer", "REUSABLE_MIT", "Mesh optimization/compression; MIT license."),
        ("skypjack/entt", "entt", "REUSABLE_MIT", "ECS code MIT; docs CC BY 4.0; logos CC BY-SA."),
        ("SanderMertens/flecs", "flecs", "REUSABLE_MIT", "ECS framework; MIT license."),
        ("jrouwe/JoltPhysics", "JoltPhysics", "REUSABLE_MIT", "Rigid body physics/collision; MIT license."),
        ("guillaumeblanc/ozz-animation", "ozz-animation", "REUSABLE_MIT", "Skeletal animation library/toolset; MIT license."),
        ("BehaviorTree/BehaviorTree.CPP", "BehaviorTree.CPP", "REUSABLE_MIT", "Behavior tree implementation; MIT license."),
        ("ocornut/imgui", "Dear_ImGui", "REUSABLE_MIT", "Immediate-mode tooling/game UI; MIT license."),
        ("mackron/miniaudio", "miniaudio", "REUSABLE_PD_OR_MIT0", "Audio playback/capture; public-domain or MIT-0 choice."),
    ]
    for repo, name, usage, rights in repos:
        clone(repo, refs / name)
        ref_sources.append({"name":name,"source":f"https://github.com/{repo}","usage_class":usage,"rights":rights + " Repository license file preserved."})

    polyhaven_assets(assets, asset_sources)

    inventory(books, book_sources)
    inventory(refs, ref_sources)
    inventory(assets, asset_sources)
    build_transport(root)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="material-bank-batch-002")
    args = ap.parse_args()
    root = Path(args.out).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    build(root)
    print(f"Batch 002 complete: {root}")
