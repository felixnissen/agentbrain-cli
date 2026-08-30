#!/usr/bin/env python3
"""Carrier adapter for AI-Asset-Department Batch 006."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path
import material_bank_batch_006 as b6

def build(root: Path):
    shutil.rmtree(root,ignore_errors=True); root.mkdir(parents=True,exist_ok=True); b6.build(root)
    p=root/'payload'; shutil.rmtree(root/'transport',ignore_errors=True)
    (p/'material_standards_open').rename(p/'h3_ecosystem')
    (p/'texture_compression_open').rename(p/'realtime_world_models')
    (p/'rendering_shader_mixed').rename(p/'video_acceleration')
    b6.transport(root,['h3_ecosystem','realtime_world_models','video_acceleration','catalog_only'])
    # The fixed carrier workflow only exposes h3 slots 000-001. Batch 006
    # material standards have a third part, so mirror only that missing part
    # into the otherwise-unused academic slot for transport. It is renamed
    # back to material-standards-002 before entering Drive.
    missing=root/'transport'/'h3_ecosystem.part-002'
    if missing.exists():
        shutil.copy2(missing, root/'transport'/'academic_noncommercial.part-000')
    print('Batch 006 carrier mapping + part-002 recovery complete')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='material-bank-batch-004'); a=ap.parse_args(); build(Path(a.out).resolve())
