#!/usr/bin/env python3
"""Material Bank Batch 003 — rendering, shaders/VFX, procedural generation and motion references.

All mirrored sources are explicitly classified. Protected material whose host forbids
rehosting is catalogued only. Transport parts are capped at 90 MiB for Drive ingestion.
"""
from __future__ import annotations

import argparse, hashlib, json, shutil, subprocess, time, urllib.request
from pathlib import Path

UA = "AI-Asset-Department/0.3 (+https://github.com/felixnissen/AI-Asset-Department)"
PART = 90 * 1024 * 1024


def clone(repo: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(dest)], check=True)
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print("OK clone", repo)


def sparse_clone(repo: str, dest: Path, paths: list[str]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", f"https://github.com/{repo}.git", str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--skip-checks", *paths], check=True)
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print("OK sparse clone", repo, paths)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r, dest.open("wb") as f:
        shutil.copyfileobj(r, f)
    if dest.stat().st_size == 0:
        raise RuntimeError(f"empty download {url}")
    print("OK download", url, dest.stat().st_size)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_inventory(root: Path, sources: list[dict]) -> None:
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


def split(src: Path, prefix: Path) -> list[Path]:
    out = []
    with src.open("rb") as f:
        i = 0
        while True:
            b = f.read(PART)
            if not b: break
            p = Path(f"{prefix}.part-{i:03d}")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b)
            out.append(p)
            i += 1
    return out


def transport(root: Path, categories: list[str]) -> None:
    t = root / "transport"; t.mkdir()
    parts = []; originals = []
    for name in categories:
        src = root / "payload" / name
        tar = root / f"{name}.tar"
        subprocess.run(["tar", "-cf", str(tar), "-C", str(src), "."], check=True)
        originals.append(f"{sha256(tar)}  {tar.name}")
        parts.extend(split(tar, t / name))
        tar.unlink()
    (t / "ORIGINAL_SHA256SUMS").write_text("\n".join(originals)+"\n", encoding="utf-8")
    (t / "SHA256SUMS").write_text("\n".join(f"{sha256(p)}  {p.name}" for p in parts)+"\n", encoding="utf-8")
    (t / "REASSEMBLY.md").write_text("# Batch 003\n\nConcatenate each category's `.part-NNN` files in lexical order, verify the recreated TAR against `ORIGINAL_SHA256SUMS`, then extract.\n", encoding="utf-8")
    for i in range(0, len(parts), 4):
        g = t / f"group-{i//4:02d}"; g.mkdir()
        for p in parts[i:i+4]: shutil.copy2(p, g/p.name)
        for m in ["ORIGINAL_SHA256SUMS","SHA256SUMS","REASSEMBLY.md"]: shutil.copy2(t/m, g/m)


def build(root: Path) -> None:
    learning = root/"payload"/"learning"
    rendering = root/"payload"/"rendering_vfx"
    procedural = root/"payload"/"procedural_ai_motion"
    catalog = root/"payload"/"catalog_only"
    for d in [learning, rendering, procedural, catalog]: d.mkdir(parents=True, exist_ok=True)

    lsrc=[]; rsrc=[]; psrc=[]; csrc=[]

    clone("KhronosGroup/Vulkan-Tutorial", learning/"Khronos_Vulkan_Tutorial")
    lsrc.append({"name":"Khronos Vulkan Tutorial","source":"https://github.com/KhronosGroup/Vulkan-Tutorial","usage_class":"REUSABLE_PERMISSIVE","rights":"Repository content is CC BY-SA 4.0 unless otherwise stated; original code listings include CC0; newer tutorials include Apache-2.0/MIT/BSD components. File-level license remains authoritative."})

    download("https://learnopengl.com/book/learnopengl_book_bw.pdf", learning/"LearnOpenGL"/"learnopengl_book_bw.pdf")
    lsrc.append({"name":"LearnOpenGL free PDF","source":"https://learnopengl.com/","usage_class":"NONCOMMERCIAL_DERIVATIVE","rights":"Official free PDF is CC BY-NC 3.0; site code samples currently CC BY-NC 4.0 and images/videos CC BY 4.0. Keep this PDF outside commercial indexes."})

    clone("KhronosGroup/Vulkan-Samples", rendering/"Vulkan_Samples")
    rsrc.append({"name":"Khronos Vulkan Samples","source":"https://github.com/KhronosGroup/Vulkan-Samples","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 repository; preserve third-party/asset-specific notices."})
    clone("SaschaWillems/Vulkan", rendering/"SaschaWillems_Vulkan")
    rsrc.append({"name":"Sascha Willems Vulkan examples","source":"https://github.com/SaschaWillems/Vulkan","usage_class":"REUSABLE_MIT","rights":"MIT source; individual assets/dependencies may carry their own terms."})
    clone("shader-slang/slang", rendering/"Slang")
    rsrc.append({"name":"Slang shader language/compiler","source":"https://github.com/shader-slang/slang","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 WITH LLVM-exception; preserve license and third-party notices."})
    clone("effekseer/Effekseer", rendering/"Effekseer")
    rsrc.append({"name":"Effekseer VFX engine/editor","source":"https://github.com/effekseer/Effekseer","usage_class":"REUSABLE_MIT","rights":"MIT repository; preserve bundled third-party notices."})
    clone("bkaradzic/bgfx", rendering/"bgfx")
    rsrc.append({"name":"bgfx rendering library","source":"https://github.com/bkaradzic/bgfx","usage_class":"REUSABLE_BSD","rights":"BSD-2-Clause style license; preserve third-party licenses."})
    sparse_clone("google/filament", rendering/"Filament_Knowledge_Slice", ["docs", "filament", "samples", "README.md", "LICENSE"])
    rsrc.append({"name":"Google Filament knowledge/source slice","source":"https://github.com/google/filament","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 core source/docs slice. Excludes most asset-heavy/third-party tree; per-file notices remain authoritative."})

    clone("redblobgames/mapgen2", procedural/"RedBlob_mapgen2")
    psrc.append({"name":"Red Blob Games mapgen2","source":"https://github.com/redblobgames/mapgen2","usage_class":"REUSABLE_APACHE2","rights":"Procedural island/map generation code published under Apache-2.0; preserve source notices."})
    clone("Auburn/FastNoiseLite", procedural/"FastNoiseLite")
    psrc.append({"name":"FastNoiseLite","source":"https://github.com/Auburn/FastNoiseLite","usage_class":"REUSABLE_MIT","rights":"MIT procedural noise implementation in multiple languages."})
    clone("xbpeng/DeepMimic", procedural/"DeepMimic")
    psrc.append({"name":"DeepMimic","source":"https://github.com/xbpeng/DeepMimic","usage_class":"REUSABLE_MIT","rights":"MIT repository with physics-based character imitation code and motion clips. Deprecated upstream but still useful reference/data."})

    catalog_text = """# Catalog-only high-value sources\n\nThese are intentionally NOT mirrored because redistribution/commercial-use terms do not support our reusable material bank.\n\n- **Game AI Pro series** — https://www.gameaipro.com/ — chapters are free to download from the official host, but the site explicitly says authors/CRC Press retain copyright and the files may not be redistributed, reprinted or hosted elsewhere. Use lawful source links only.\n- **GPU Gems 1–3** — https://developer.nvidia.com/gpugems — free to read online. Book text remains copyrighted; source/CD items have separate terms. Catalogue chapters and link to official pages instead of mirroring the books.\n- **Ubisoft LaFAN1** — https://github.com/ubisoft/ubisoft-laforge-animation-dataset — valuable BVH mocap dataset, but CC BY-NC-ND 4.0. Do not put it in commercial transformation/training pipelines.\n- **AMASS** — https://amass.is.tue.mpg.de/ — valuable human-motion collection with registration/source-dataset restrictions; obtain/use only under its current terms.\n- **Mixamo** — Adobe service/assets; do not scrape or redistribute as an open asset bank.\n- **The Art of Game Design / Game Engine Architecture / Real-Time Rendering / AI for Games** — commercial standard references; catalogue/buy/borrow lawfully rather than mirroring unauthorized copies.\n"""
    (catalog/"GAME_DEV_REFERENCE_CATALOG.md").write_text(catalog_text, encoding="utf-8")
    csrc.append({"name":"Protected/high-restriction reference catalog","source":"multiple official sources listed in file","usage_class":"CATALOG_ONLY","rights":"Metadata and lawful links only; protected works are not mirrored."})

    write_inventory(learning, lsrc); write_inventory(rendering, rsrc); write_inventory(procedural, psrc); write_inventory(catalog, csrc)
    transport(root, ["learning","rendering_vfx","procedural_ai_motion","catalog_only"])

if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--out", default="material-bank-batch-003"); a=ap.parse_args()
    root=Path(a.out).resolve(); shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
    build(root); print("Batch 003 complete", root)
