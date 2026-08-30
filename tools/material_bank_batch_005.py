#!/usr/bin/env python3
"""Temporary transport copy of AI-Asset-Department material bank Batch 005.

Source of truth: felixnissen/AI-Asset-Department/ingestion/material_bank_batch_005_3d_animation.py
This public runner copy exists only to build Drive-safe transport artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path

PART_BYTES = 90 * 1024 * 1024


def run(*args: str) -> str:
    return subprocess.check_output(list(args), text=True).strip()


def clone_snapshot(repo: str, dest: Path, ref: str | None = None) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [f"https://github.com/{repo}.git", str(dest)]
    subprocess.run(cmd, check=True)
    commit = run("git", "-C", str(dest), "rev-parse", "HEAD")
    (dest / "UPSTREAM_COMMIT.txt").write_text(commit + "\n", encoding="utf-8")
    (dest / "UPSTREAM_REPOSITORY.txt").write_text(f"https://github.com/{repo}\n", encoding="utf-8")
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print(f"OK clone {repo}@{commit[:12]} -> {dest}")
    return commit


def sparse_clone_snapshot(repo: str, dest: Path, paths: list[str], ref: str | None = None) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse"]
    if ref:
        cmd += ["--branch", ref]
    cmd += [f"https://github.com/{repo}.git", str(dest)]
    subprocess.run(cmd, check=True)
    subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", "--skip-checks", *paths], check=True)
    commit = run("git", "-C", str(dest), "rev-parse", "HEAD")
    (dest / "UPSTREAM_COMMIT.txt").write_text(commit + "\n", encoding="utf-8")
    (dest / "UPSTREAM_REPOSITORY.txt").write_text(f"https://github.com/{repo}\n", encoding="utf-8")
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print(f"OK sparse clone {repo}@{commit[:12]}: {paths}")
    return commit


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
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
    (root / "SOURCES.md").write_text(
        "# Sources\n\n" + "\n".join(
            f"- **{s['name']}** — {s['source']} — `{s['usage_class']}` — commit `{s.get('commit', 'n/a')}` — {s['rights']}"
            for s in sources
        ) + "\n",
        encoding="utf-8",
    )


def split_file(src: Path, prefix: Path) -> list[Path]:
    parts: list[Path] = []
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


def build_transport(root: Path, categories: list[str]) -> None:
    transport = root / "transport"
    transport.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    originals: list[str] = []
    for category in categories:
        src = root / "payload" / category
        tar = root / f"{category}.tar"
        subprocess.run(["tar", "-cf", str(tar), "-C", str(src), "."], check=True)
        originals.append(f"{sha256(tar)}  {tar.name}")
        parts.extend(split_file(tar, transport / category))
        tar.unlink()
    (transport / "ORIGINAL_SHA256SUMS").write_text("\n".join(originals) + "\n", encoding="utf-8")
    (transport / "SHA256SUMS").write_text("\n".join(f"{sha256(p)}  {p.name}" for p in parts) + "\n", encoding="utf-8")
    (transport / "REASSEMBLY.md").write_text(
        "# Batch 005 reassembly\n\n"
        "Each Actions artifact contains Drive-safe `.part-NNN` files. Concatenate a category's numbered parts in lexical order, verify the recreated TAR against `ORIGINAL_SHA256SUMS`, then extract.\n\n"
        "`academic_noncommercial` is physically excluded from commercial indexes/generation. `catalog_only` and `territory_blocked` contain metadata only. Repository licenses never imply that separately hosted model weights, training datasets, demo assets or API services share the same rights.\n",
        encoding="utf-8",
    )


def add_source(bucket: list[dict], *, name: str, repo: str, usage_class: str, rights: str, commit: str) -> None:
    bucket.append({"name": name, "source": f"https://github.com/{repo}", "usage_class": usage_class, "rights": rights, "commit": commit})


def build(root: Path) -> None:
    payload = root / "payload"
    motion = payload / "motion_generation_open"
    rigging = payload / "rigging_skinning_open"
    threed = payload / "three_d_generation_open"
    retarget = payload / "retargeting_tools_open"
    academic = payload / "academic_noncommercial"
    catalog = payload / "catalog_only"
    territory = payload / "territory_blocked"
    for d in [motion, rigging, threed, retarget, academic, catalog, territory]:
        d.mkdir(parents=True, exist_ok=True)

    motion_sources: list[dict] = []
    rigging_sources: list[dict] = []
    threed_sources: list[dict] = []
    retarget_sources: list[dict] = []
    academic_sources: list[dict] = []
    catalog_sources: list[dict] = []
    territory_sources: list[dict] = []

    commit = clone_snapshot("nv-tlabs/kimodo", motion / "Kimodo")
    add_source(motion_sources, name="NVIDIA Kimodo", repo="nv-tlabs/kimodo", usage_class="REUSABLE_APACHE2", commit=commit, rights="Apache-2.0 repository. Motion-model checkpoints and datasets use separate licenses and require independent review.")
    commit = clone_snapshot("nv-tlabs/ardy", motion / "ARDY")
    add_source(motion_sources, name="NVIDIA ARDY", repo="nv-tlabs/ardy", usage_class="REUSABLE_APACHE2", commit=commit, rights="Apache-2.0 repository for interactive/real-time character motion. Checkpoints/data remain separate licensed artifacts.")

    commit = clone_snapshot("VAST-AI-Research/SkinTokens", rigging / "SkinTokens")
    add_source(rigging_sources, name="SkinTokens", repo="VAST-AI-Research/SkinTokens", usage_class="REUSABLE_MIT", commit=commit, rights="MIT repository. Model/checkpoint/training-data provenance remains separate.")
    commit = clone_snapshot("VAST-AI-Research/UniRig", rigging / "UniRig")
    add_source(rigging_sources, name="UniRig", repo="VAST-AI-Research/UniRig", usage_class="REUSABLE_MIT", commit=commit, rights="MIT repository for automatic skeleton and skinning. Model/data artifacts require independent rights evidence.")
    commit = clone_snapshot("jasongzy/Make-It-Animatable", rigging / "Make-It-Animatable")
    add_source(rigging_sources, name="Make-It-Animatable", repo="jasongzy/Make-It-Animatable", usage_class="REUSABLE_MIT", commit=commit, rights="MIT repository for animation-ready 3D character rigging/skinning/pose workflows. Hosted checkpoints and example assets are evaluated separately.")

    commit = sparse_clone_snapshot("microsoft/TRELLIS.2", threed / "TRELLIS2_Knowledge_Runtime", [
        "trellis2", "configs", "data_toolkit", "o-voxel", "README.md", "LICENSE", "setup.sh",
        "train.py", "example.py", "example_texturing.py", "app.py", "app_texturing.py"
    ])
    add_source(threed_sources, name="Microsoft TRELLIS.2 runtime/knowledge slice", repo="microsoft/TRELLIS.2", usage_class="REUSABLE_MIT", commit=commit, rights="MIT repository snapshot excluding bulk demo assets. Separately hosted weights/datasets require their own model-card/data-license evidence.")
    commit = clone_snapshot("VAST-AI-Research/GeoSAM2", threed / "GeoSAM2")
    add_source(threed_sources, name="GeoSAM2", repo="VAST-AI-Research/GeoSAM2", usage_class="REUSABLE_APACHE2", commit=commit, rights="Apache-2.0 repository for geometry-aware 3D part segmentation. Third-party dependencies retain their own terms.")
    commit = clone_snapshot("neko-legends/image-to-3D", threed / "ImageTo3D_Desktop_Reference")
    add_source(threed_sources, name="image-to-3D desktop workflow reference", repo="neko-legends/image-to-3D", usage_class="REUSABLE_MIT", commit=commit, rights="MIT desktop orchestration/UI code. Wrapped backends/models keep their own licenses and territory restrictions.")

    commit = clone_snapshot("NVIDIA/soma-retargeter", retarget / "SOMA_Retargeter")
    add_source(retarget_sources, name="NVIDIA SOMA Retargeter", repo="NVIDIA/soma-retargeter", usage_class="REUSABLE_APACHE2", commit=commit, rights="Apache-2.0 BVH/motion retargeting implementation. Preserve licenses for bundled sample data if they differ.")
    commit = clone_snapshot("eherr/anim_utils", retarget / "anim_utils", ref="master")
    add_source(retarget_sources, name="anim_utils", repo="eherr/anim_utils", usage_class="REUSABLE_MIT", commit=commit, rights="MIT skeletal animation/BVH/IK/retargeting utility library.")

    commit = clone_snapshot("Isabella98Liu/RigAnything", academic / "RigAnything")
    add_source(academic_sources, name="RigAnything", repo="Isabella98Liu/RigAnything", usage_class="NONCOMMERCIAL_DERIVATIVE", commit=commit, rights="Adobe Research License: noncommercial research/teaching only; commercial product development/distribution is expressly excluded. Physically isolated.")

    hunyuan = {
        "name": "Tencent Hunyuan3D-2.1",
        "source": "https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1",
        "usage_class": "TERRITORY_BLOCKED",
        "license_evidence": "Tencent Hunyuan 3D 2.1 Community License Agreement",
        "restriction": "License states that the agreement does not apply in the European Union, United Kingdom or South Korea; the defined Territory excludes those regions.",
        "action": "Do not mirror or run the Hunyuan3D-2.1 Works in a blocked territory. Keep metadata/link only unless separate rights/legal review establishes a permitted scope."
    }
    (territory / "HUNYUAN3D_2_1.json").write_text(json.dumps(hunyuan, indent=2), encoding="utf-8")
    territory_sources.append({"name": hunyuan["name"], "source": hunyuan["source"], "usage_class": "TERRITORY_BLOCKED", "rights": hunyuan["restriction"], "commit": "not-mirrored"})

    model_catalog = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entries": [
            {"name":"Kimodo checkpoints / RP vs R&D variants","source":"https://github.com/nv-tlabs/kimodo","usage_class":"CATALOG_ONLY","notes":"Repository code is Apache-2.0; model variants and datasets have separate licenses. Ingest weights only after exact model-card license + data provenance review."},
            {"name":"ARDY checkpoints","source":"https://github.com/nv-tlabs/ardy","usage_class":"CATALOG_ONLY","notes":"Code is Apache-2.0. Checkpoint/data licenses must be retained and reviewed separately."},
            {"name":"TRELLIS.2 hosted weights/datasets","source":"https://github.com/microsoft/TRELLIS.2","usage_class":"CATALOG_ONLY","notes":"Code snapshot is MIT. Do not infer model/dataset rights from repository code license."},
            {"name":"Mixamo animation library","source":"https://www.mixamo.com/","usage_class":"CATALOG_ONLY","notes":"Useful production reference/retarget target but proprietary service/content terms; do not bulk mirror into the material bank."},
            {"name":"AMASS motion dataset","source":"https://amass.is.tue.mpg.de/","usage_class":"CATALOG_ONLY","notes":"Valuable motion research dataset with registration/source-specific terms. Catalog until exact permitted storage/use scope is reviewed."}
        ]
    }
    (catalog / "MODEL_DATA_SERVICE_CATALOG.json").write_text(json.dumps(model_catalog, indent=2), encoding="utf-8")
    catalog_sources.append({"name":"3D/motion model-data-service catalog","source":"upstream model cards/services","usage_class":"CATALOG_ONLY","rights":"Metadata only; code licenses never silently grant rights to model weights, datasets or proprietary asset services.","commit":"metadata-only"})
    (catalog / "WHY_THIS_BATCH_MATTERS.md").write_text(
        "# Why Batch 005 matters\n\nA production-ready character path is closer to: concept/image -> geometry/PBR -> part understanding -> skeleton -> skin weights -> motion generation -> retargeting -> QA -> baked engine-ready animation. This batch preserves open implementations across that chain while keeping restricted model/data rights out of the commercial-safe lane.\n",
        encoding="utf-8"
    )

    write_inventory(motion, motion_sources)
    write_inventory(rigging, rigging_sources)
    write_inventory(threed, threed_sources)
    write_inventory(retarget, retarget_sources)
    write_inventory(academic, academic_sources)
    write_inventory(catalog, catalog_sources)
    write_inventory(territory, territory_sources)
    build_transport(root, ["motion_generation_open", "rigging_skinning_open", "three_d_generation_open", "retargeting_tools_open", "academic_noncommercial", "catalog_only", "territory_blocked"])
    print(f"Batch 005 complete: {root}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="material-bank-batch-005")
    args = ap.parse_args()
    root = Path(args.out).resolve()
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    build(root)
