#!/usr/bin/env python3
"""Carrier adapter: run Batch 005 through the already-approved Batch 004 Actions workflow.

This file is transport-only. Source of truth remains
felixnissen/AI-Asset-Department/ingestion/material_bank_batch_005_3d_animation.py.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import material_bank_batch_005 as b5


def build(root: Path) -> None:
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    b5.build(root)

    payload = root / "payload"
    shutil.rmtree(root / "transport", ignore_errors=True)

    # Re-map Batch 005 semantic categories onto the fixed slots already accepted
    # by the Batch 004 carrier workflow. These names never become source-of-truth.
    (payload / "motion_generation_open").rename(payload / "h3_ecosystem")

    realtime = payload / "realtime_world_models"
    realtime.mkdir(parents=True, exist_ok=True)
    (payload / "rigging_skinning_open").rename(realtime / "rigging_skinning_open")
    (payload / "retargeting_tools_open").rename(realtime / "retargeting_tools_open")

    (payload / "three_d_generation_open").rename(payload / "video_acceleration")

    # Territory-blocked metadata is metadata-only and travels inside the catalog
    # carrier slot so it cannot be confused with reusable 3D code.
    territory = payload / "territory_blocked"
    catalog = payload / "catalog_only"
    territory.rename(catalog / "territory_blocked")

    b5.build_transport(
        root,
        [
            "h3_ecosystem",
            "realtime_world_models",
            "video_acceleration",
            "academic_noncommercial",
            "catalog_only",
        ],
    )
    print("Batch 005 carrier mapping complete")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="material-bank-batch-004")
    args = ap.parse_args()
    build(Path(args.out).resolve())
