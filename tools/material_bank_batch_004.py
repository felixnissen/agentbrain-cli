#!/usr/bin/env python3
"""Material Bank Batch 004 — realtime generative video, world models and H3 ecosystem.

Purpose:
- preserve high-value open source implementations that explain/enable faster-than-realtime video;
- keep code/repository rights separate from model-weight rights;
- physically isolate academic/non-commercial implementations;
- catalogue hosted/custom-license model systems without silently mirroring restricted weights;
- emit <=90 MiB transport parts for the current Drive bridge.
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


def clone(repo: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(dest)], check=True)
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print(f"OK clone {repo} -> {dest}")


def sparse_clone(repo: str, dest: Path, paths: list[str]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
        f"https://github.com/{repo}.git", str(dest)
    ], check=True)
    subprocess.run([
        "git", "-C", str(dest), "sparse-checkout", "set", "--skip-checks", *paths
    ], check=True)
    shutil.rmtree(dest / ".git", ignore_errors=True)
    print(f"OK sparse clone {repo}: {paths}")


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
            files.append({
                "path": str(p.relative_to(root)),
                "bytes": p.stat().st_size,
                "sha256": sha256(p),
            })
    (root / "INVENTORY.json").write_text(json.dumps({
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": sources,
        "files": files,
    }, indent=2), encoding="utf-8")
    (root / "SOURCES.md").write_text(
        "# Sources\n\n" + "\n".join(
            f"- **{s['name']}** — {s['source']} — `{s['usage_class']}` — {s['rights']}"
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
    (transport / "SHA256SUMS").write_text(
        "\n".join(f"{sha256(p)}  {p.name}" for p in parts) + "\n", encoding="utf-8"
    )
    (transport / "REASSEMBLY.md").write_text(
        "# Batch 004 reassembly\n\n"
        "Each Actions artifact contains one Drive-safe `.part-NNN`. Unzip the artifact wrapper, "
        "concatenate a category's numbered parts in lexical order, verify the recreated TAR with "
        "`ORIGINAL_SHA256SUMS`, then extract. `academic_noncommercial` MUST stay outside commercial "
        "indexes/generation pipelines. Repository licenses do not grant rights to separately hosted model weights.\n",
        encoding="utf-8",
    )


def build(root: Path) -> None:
    payload = root / "payload"
    h3 = payload / "h3_ecosystem"
    realtime = payload / "realtime_world_models"
    acceleration = payload / "video_acceleration"
    academic = payload / "academic_noncommercial"
    catalog = payload / "catalog_only"
    for d in [h3, realtime, acceleration, academic, catalog]:
        d.mkdir(parents=True, exist_ok=True)

    h3_sources: list[dict] = []
    rt_sources: list[dict] = []
    acc_sources: list[dict] = []
    academic_sources: list[dict] = []
    catalog_sources: list[dict] = []

    clone("ModelTC/LightX2V", h3 / "LightX2V")
    h3_sources.append({"name":"LightX2V","source":"https://github.com/ModelTC/LightX2V","usage_class":"REUSABLE_APACHE2","rights":"Repository is Apache-2.0. Supports MiniMax-H3 inference, H3 Turbo distillation, caching, quantization, parallelism and world-model workflows. Hosted model weights retain their own licenses."})
    clone("ModelTC/Minimax-H3-Turbo", h3 / "Minimax-H3-Turbo")
    h3_sources.append({"name":"MiniMax H3 Turbo LoRA tooling/workflows","source":"https://github.com/ModelTC/Minimax-H3-Turbo","usage_class":"REUSABLE_APACHE2","rights":"Repository is Apache-2.0. Hugging Face lightx2v/Minimax-h3-Turbo is currently tagged Apache-2.0; preserve the model card/license alongside any future weight snapshot."})

    clone("PKU-YuanGroup/Helios", realtime / "Helios")
    rt_sources.append({"name":"Helios","source":"https://github.com/PKU-YuanGroup/Helios","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 implementation of real-time long video generation; model checkpoints are separate artifacts and must retain their own model-card license."})
    clone("thu-ml/Causal-Forcing", realtime / "Causal-Forcing")
    rt_sources.append({"name":"Causal Forcing / Causal Forcing++","source":"https://github.com/thu-ml/Causal-Forcing","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 code for few-step frame/chunk autoregressive diffusion and interactive/long-video research."})
    clone("guandeh17/Self-Forcing", realtime / "Self-Forcing")
    rt_sources.append({"name":"Self-Forcing","source":"https://github.com/guandeh17/Self-Forcing","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 autoregressive video generation research implementation."})
    clone("shengshu-ai/minWM", realtime / "minWM")
    rt_sources.append({"name":"minWM","source":"https://github.com/shengshu-ai/minWM","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 interactive/action-conditioned world-model implementation."})
    clone("lllyasviel/FramePack", realtime / "FramePack")
    rt_sources.append({"name":"FramePack","source":"https://github.com/lllyasviel/FramePack","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 long-video/context-packing implementation; downstream model licenses remain separate."})

    sparse_clone("hao-ai-lab/FastVideo", acceleration / "FastVideo_Knowledge_Slice", ["fastvideo", "apps/dreamverse", "examples/inference", "examples/distill", "docs", "README.md", "LICENSE", "AGENTS.md"])
    acc_sources.append({"name":"FastVideo knowledge/runtime slice","source":"https://github.com/hao-ai-lab/FastVideo","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 framework. Sparse snapshot keeps core runtime, realtime Dreamverse, inference/distillation examples and docs while excluding unrelated bulk. Individual hosted model checkpoints may use different licenses."})
    sparse_clone("vipshop/cache-dit", acceleration / "Cache-DiT_Knowledge_Slice", ["src", "csrc", "docs", "bench", "tests", "README.md", "LICENSE", "pyproject.toml"])
    acc_sources.append({"name":"Cache-DiT knowledge/runtime slice","source":"https://github.com/vipshop/cache-dit","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 acceleration/cache framework snapshot. Third-party components/notices remain authoritative."})
    clone("ali-vilab/TeaCache", acceleration / "TeaCache")
    acc_sources.append({"name":"TeaCache","source":"https://github.com/ali-vilab/TeaCache","usage_class":"REUSABLE_APACHE2","rights":"Apache-2.0 cache acceleration research/code; bundled/derived third-party notices remain authoritative."})

    clone("TencentARC/RollingForcing", academic / "RollingForcing")
    academic_sources.append({"name":"RollingForcing","source":"https://github.com/TencentARC/RollingForcing","usage_class":"NONCOMMERCIAL_DERIVATIVE","rights":"Tencent license permits use only for academic purposes and explicitly forbids commercial/production use. Physically isolated from commercial-safe material."})

    model_catalog = {
        "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "entries": [
            {"name":"fal H3 Max","source":"https://fal.ai/minimax-h3-max","usage_class":"CATALOG_ONLY","notes":"fal post-trained/served MiniMax H3 variant. Faster-than-realtime hosted endpoint; no assumption of downloadable/open H3 Max weights. fal reports 5s 768p in under 3s."},
            {"name":"MiniMaxAI/MiniMax-H3","source":"https://huggingface.co/MiniMaxAI/MiniMax-H3","usage_class":"CATALOG_ONLY","notes":"Open-weight base model metadata currently reports license=other / MiniMax H3 Community License. Review exact license before mirroring weights or using in commercial derivative pipelines."},
            {"name":"lightx2v/Minimax-h3-Turbo","source":"https://huggingface.co/lightx2v/Minimax-h3-Turbo","usage_class":"REUSABLE_APACHE2","notes":"HF metadata currently reports Apache-2.0; includes 4-step/8-step H3 Turbo LoRA variants. Future weight download must preserve model card and exact file hashes."},
            {"name":"FastVideo/FastVideo-Minimax-FastH3-Preview-v0.2","source":"https://huggingface.co/FastVideo/FastVideo-Minimax-FastH3-Preview-v0.2","usage_class":"CATALOG_ONLY","notes":"FastH3 few-step checkpoint metadata currently reports license=other. Code framework is Apache-2.0, checkpoint rights are not assumed from code license."},
            {"name":"BestWishYsh/Helios-Distilled","source":"https://huggingface.co/BestWishYsh/Helios-Distilled","usage_class":"REUSABLE_APACHE2","notes":"HF metadata currently reports Apache-2.0. Large model weights should be mirrored only in a dedicated model-bank batch with quota/storage review and hashes."}
        ]
    }
    (catalog / "MODEL_AND_HOSTED_SYSTEM_CATALOG.json").write_text(json.dumps(model_catalog, indent=2), encoding="utf-8")
    (catalog / "WHY_THIS_BATCH_MATTERS.md").write_text("# Why realtime video belongs in the Asset Department\n\nFaster-than-playback video changes generation from an offline render step into potential runtime media. The near-term Asset Department use is not 'replace the game engine': it is continuously generating motion references, shot/layout options, animated Design-DNA previews, previsualization, cinematic variants and director-agent visual feedback while a human is still reviewing the previous option. World-model/control repos are retained because they explore the next step: action-conditioned, stateful and prompt-switchable generated worlds.\n", encoding="utf-8")
    catalog_sources.append({"name":"Realtime video hosted/model catalog","source":"fal + Hugging Face metadata + upstream repos","usage_class":"CATALOG_ONLY","rights":"Separates repository/code licenses from model-weight/service licenses. Restricted/custom-license weights are not mirrored by this batch."})

    write_inventory(h3, h3_sources)
    write_inventory(realtime, rt_sources)
    write_inventory(acceleration, acc_sources)
    write_inventory(academic, academic_sources)
    write_inventory(catalog, catalog_sources)
    build_transport(root, ["h3_ecosystem", "realtime_world_models", "video_acceleration", "academic_noncommercial", "catalog_only"])
    print(f"Batch 004 complete: {root}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="material-bank-batch-004")
    args = ap.parse_args()
    root = Path(args.out).resolve()
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    build(root)
