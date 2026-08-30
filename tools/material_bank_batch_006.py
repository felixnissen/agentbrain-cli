#!/usr/bin/env python3
"""Temporary transport copy of AI-Asset-Department Batch 006.
Source of truth: felixnissen/AI-Asset-Department/ingestion/material_bank_batch_006_materials_shaders.py
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, time
from pathlib import Path
PART_BYTES=90*1024*1024

def run(*a): return subprocess.check_output(list(a),text=True).strip()
def snap(repo,dest,paths=None,ref=None):
    dest.parent.mkdir(parents=True,exist_ok=True)
    cmd=['git','clone','--depth','1']
    if paths: cmd += ['--filter=blob:none','--sparse']
    if ref: cmd += ['--branch',ref]
    cmd += [f'https://github.com/{repo}.git',str(dest)]
    subprocess.run(cmd,check=True)
    if paths: subprocess.run(['git','-C',str(dest),'sparse-checkout','set','--skip-checks',*paths],check=True)
    commit=run('git','-C',str(dest),'rev-parse','HEAD')
    (dest/'UPSTREAM_COMMIT.txt').write_text(commit+'\n')
    (dest/'UPSTREAM_REPOSITORY.txt').write_text(f'https://github.com/{repo}\n')
    shutil.rmtree(dest/'.git',ignore_errors=True)
    return commit

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def inv(root,sources):
    files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
    (root/'INVENTORY.json').write_text(json.dumps({'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sources':sources,'files':files},indent=2))
    (root/'SOURCES.md').write_text('# Sources\n\n'+'\n'.join(f"- **{s['name']}** — {s['source']} — `{s['usage_class']}` — commit `{s.get('commit','n/a')}` — {s['rights']}" for s in sources)+'\n')
def split(src,prefix):
    out=[]
    with src.open('rb') as f:
        i=0
        while (data:=f.read(PART_BYTES)):
            p=Path(f'{prefix}.part-{i:03d}'); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data); out.append(p); i+=1
    return out
def transport(root,cats):
    t=root/'transport'; t.mkdir(parents=True,exist_ok=True); parts=[]; originals=[]
    for c in cats:
        tar=root/f'{c}.tar'; subprocess.run(['tar','-cf',str(tar),'-C',str(root/'payload'/c),'.'],check=True)
        originals.append(f'{sha(tar)}  {tar.name}'); parts += split(tar,t/c); tar.unlink()
    (t/'ORIGINAL_SHA256SUMS').write_text('\n'.join(originals)+'\n')
    (t/'SHA256SUMS').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in parts)+'\n')
    (t/'REASSEMBLY.md').write_text('# Batch 006 reassembly\n\nConcatenate numbered parts, verify recreated TARs against ORIGINAL_SHA256SUMS, then extract. rendering_shader_mixed requires file-level license gates.\n')
def src(name,repo,cls,rights,commit): return {'name':name,'source':f'https://github.com/{repo}','usage_class':cls,'rights':rights,'commit':commit}
def build(root):
    p=root/'payload'; standards=p/'material_standards_open'; comp=p/'texture_compression_open'; mixed=p/'rendering_shader_mixed'; catalog=p/'catalog_only'
    for d in [standards,comp,mixed,catalog]: d.mkdir(parents=True,exist_ok=True)
    ss=[]; cs=[]; ms=[]; cats=[]
    c=snap('AcademySoftwareFoundation/MaterialX',standards/'MaterialX',['source','libraries','documents','resources','python','README.md','LICENSE','NOTICE']); ss.append(src('MaterialX','AcademySoftwareFoundation/MaterialX','REUSABLE_APACHE2','Apache-2.0 material interchange/reference libraries; preserve NOTICE.',c))
    c=snap('AcademySoftwareFoundation/OpenPBR',standards/'OpenPBR'); ss.append(src('OpenPBR','AcademySoftwareFoundation/OpenPBR','REUSABLE_APACHE2','Apache-2.0 open PBR surface specification/reference material.',c))
    c=snap('BinomialLLC/basis_universal',comp/'BasisUniversal',['encoder','transcoder','OpenCL','webgl','LICENSE','LICENSES','NOTICE','README.md','CMakeLists.txt','basisu_tool.cpp','basisu_containers.h','basisu_file_headers.h','basisu_gpu_texture.cpp','basisu_gpu_texture.h'],'master'); cs.append(src('Basis Universal','BinomialLLC/basis_universal','REUSABLE_APACHE2','Apache-2.0 core texture supercompression/transcoding slice with NOTICE material.',c))
    c=snap('ARM-software/astc-encoder',comp/'ASTC_Encoder'); cs.append(src('Arm ASTC Encoder','ARM-software/astc-encoder','REUSABLE_APACHE2','Apache-2.0 ASTC texture encoder.',c))
    c=snap('KhronosGroup/KTX-Software',mixed/'KTX_Software',['lib','tools','include','interface','docs','LICENSE.md','LICENSES','.reuse','README.md','CMakeLists.txt']); ms.append(src('KTX-Software','KhronosGroup/KTX-Software','READ_ONLY_MIXED','Upstream documents multiple licenses and a non-open special-case file; require file-level license gates.',c))
    c=snap('GPUOpen-LibrariesAndSDKs/FidelityFX-SDK',mixed/'FidelityFX_SDK_Knowledge_Slice',['Kits','docs','readme.md','3rdpartynotice.md']); ms.append(src('AMD FidelityFX SDK knowledge/runtime slice','GPUOpen-LibrariesAndSDKs/FidelityFX-SDK','READ_ONLY_MIXED','High-value rendering/shader SDK with per-file and third-party licensing; preserve notices.',c))
    data={'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'entries':[
      {'name':'Poly Haven','source':'https://polyhaven.com/','usage_class':'REUSABLE_CC0','notes':'Curated 1K subset already mirrored earlier; avoid duplication.'},
      {'name':'ambientCG','source':'https://ambientcg.com/','usage_class':'CATALOG_ONLY','notes':'CC0-oriented source; curate/hash after current retrieval terms review.'},
      {'name':'Adobe Substance 3D Assets','source':'https://substance3d.adobe.com/assets/','usage_class':'CATALOG_ONLY','notes':'Proprietary service/content terms.'},
      {'name':'Fab / Megascans','source':'https://www.fab.com/','usage_class':'CATALOG_ONLY','notes':'High-value production source with service/content licensing.'},
      {'name':'ShaderToy','source':'https://www.shadertoy.com/','usage_class':'CATALOG_ONLY','notes':'User-generated/per-item rights; metadata/links only.'}]}
    (catalog/'ASSET_AND_SHADER_SOURCE_CATALOG.json').write_text(json.dumps(data,indent=2)); (catalog/'WHY_THIS_BATCH_MATTERS.md').write_text('# Why Batch 006 matters\n\nPBR/material standards, compression/transcoding, GPU-ready containers and rights-aware shader references are production infrastructure, not optional extras.\n')
    cats.append({'name':'Material/asset/shader service catalog','source':'upstream services','usage_class':'CATALOG_ONLY','rights':'Metadata and lawful links only until exact item/service rights are proven.','commit':'metadata-only'})
    inv(standards,ss); inv(comp,cs); inv(mixed,ms); inv(catalog,cats); transport(root,['material_standards_open','texture_compression_open','rendering_shader_mixed','catalog_only'])
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='material-bank-batch-006'); a=ap.parse_args(); r=Path(a.out).resolve(); shutil.rmtree(r,ignore_errors=True); r.mkdir(parents=True); build(r)
