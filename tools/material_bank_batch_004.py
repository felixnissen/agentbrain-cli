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
    # Existing carrier has an academic slot; create no artifact unless data exists.
    b6.transport(root,['h3_ecosystem','realtime_world_models','video_acceleration','catalog_only'])
    print('Batch 006 carrier mapping complete')
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='material-bank-batch-004'); a=ap.parse_args(); build(Path(a.out).resolve())
