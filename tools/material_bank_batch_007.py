#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, time
from pathlib import Path
PART_BYTES=90*1024*1024

def run(*a): return subprocess.check_output(list(a),text=True).strip()
def snap(repo,dest,ref=None):
    dest.parent.mkdir(parents=True,exist_ok=True); cmd=['git','clone','--depth','1'];
    if ref: cmd += ['--branch',ref]
    cmd += [f'https://github.com/{repo}.git',str(dest)]; subprocess.run(cmd,check=True)
    c=run('git','-C',str(dest),'rev-parse','HEAD'); (dest/'UPSTREAM_COMMIT.txt').write_text(c+'\n'); (dest/'UPSTREAM_REPOSITORY.txt').write_text(f'https://github.com/{repo}\n'); shutil.rmtree(dest/'.git',ignore_errors=True); return c
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for x in iter(lambda:f.read(1024*1024),b''): h.update(x)
    return h.hexdigest()
def inv(root,s):
    files=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file()]
    (root/'INVENTORY.json').write_text(json.dumps({'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'sources':s,'files':files},indent=2))
    (root/'SOURCES.md').write_text('# Sources\n\n'+'\n'.join(f"- **{x['name']}** — {x['source']} — `{x['usage_class']}` — commit `{x.get('commit','n/a')}` — {x['rights']}" for x in s)+'\n')
def src(name,repo,cls,rights,c): return {'name':name,'source':f'https://github.com/{repo}','usage_class':cls,'rights':rights,'commit':c}
def split(f,prefix):
    out=[]
    with f.open('rb') as h:
        i=0
        while (d:=h.read(PART_BYTES)):
            p=Path(f'{prefix}.part-{i:03d}'); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(d); out.append(p); i+=1
    return out
def transport(root,cats):
    t=root/'transport'; t.mkdir(parents=True,exist_ok=True); ps=[]; originals=[]
    for c in cats:
        tar=root/f'{c}.tar'; subprocess.run(['tar','-cf',str(tar),'-C',str(root/'payload'/c),'.'],check=True); originals.append(f'{sha(tar)}  {tar.name}'); ps += split(tar,t/c); tar.unlink()
    (t/'ORIGINAL_SHA256SUMS').write_text('\n'.join(originals)+'\n'); (t/'SHA256SUMS').write_text('\n'.join(f'{sha(p)}  {p.name}' for p in ps)+'\n'); (t/'REASSEMBLY.md').write_text('# Batch 007 reassembly\n\nConcatenate numbered parts, verify recreated TARs, then extract. Model/checkpoint rights remain separate from code. research_noncommercial stays outside commercial pipelines.\n')
def build(root):
    p=root/'payload'; runtime=p/'runtime_spatial_open'; codecs=p/'codecs_signal_open'; gen=p/'generative_voice_code_open'; research=p/'research_noncommercial'; catalog=p/'catalog_only'
    for d in [runtime,codecs,gen,research,catalog]: d.mkdir(parents=True,exist_ok=True)
    rs=[]; cs=[]; gs=[]; ns=[]; cats=[]
    c=snap('ValveSoftware/steam-audio',runtime/'SteamAudio','master'); rs.append(src('Steam Audio','ValveSoftware/steam-audio','REUSABLE_APACHE2','Apache-2.0 spatial/acoustic audio source; preserve third-party/trademark notices.',c))
    c=snap('resonance-audio/resonance-audio',runtime/'ResonanceAudio','master'); rs.append(src('Resonance Audio','resonance-audio/resonance-audio','REUSABLE_APACHE2','Apache-2.0 spatial audio reference; archived upstream.',c))
    c=snap('jarikomppa/soloud',runtime/'SoLoud','master'); rs.append(src('SoLoud','jarikomppa/soloud','REUSABLE_ZLIB','SoLoud core zlib/libpng; bundled third parties retain own permissive notices.',c))
    c=snap('xiph/opus',codecs/'Opus'); cs.append(src('Opus','xiph/opus','REUSABLE_BSD','BSD-style codec source plus royalty-free patent references.',c))
    c=snap('facebookresearch/encodec',codecs/'EnCodec'); cs.append(src('EnCodec','facebookresearch/encodec','REUSABLE_MIT','MIT neural codec code; hosted checkpoints separate.',c))
    c=snap('facebookresearch/audiocraft',gen/'AudioCraft'); gs.append(src('AudioCraft','facebookresearch/audiocraft','REUSABLE_MIT','MIT source framework; model/data rights separate.',c))
    c=snap('Stability-AI/stable-audio-tools',gen/'StableAudioTools'); gs.append(src('Stable Audio Tools','Stability-AI/stable-audio-tools','REUSABLE_MIT','MIT source toolkit; model/service rights separate.',c))
    c=snap('QwenAudio/CosyVoice',gen/'CosyVoice'); gs.append(src('CosyVoice','QwenAudio/CosyVoice','REUSABLE_APACHE2','Apache-2.0 multilingual TTS/voice source; checkpoints separate.',c))
    c=snap('QwenLM/Qwen3-TTS',gen/'Qwen3_TTS'); gs.append(src('Qwen3-TTS','QwenLM/Qwen3-TTS','REUSABLE_APACHE2','Apache-2.0 2026 Qwen TTS source; checkpoints separate.',c))
    c=snap('fishaudio/fish-speech',research/'FishSpeech'); ns.append(src('Fish Speech','fishaudio/fish-speech','NONCOMMERCIAL_DERIVATIVE','Fish Audio Research License: commercial use requires separate written license.',c))
    data={'generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'entries':[
      {'name':'AudioCraft/MusicGen checkpoints','source':'https://huggingface.co/facebook','usage_class':'CATALOG_ONLY','notes':'Code MIT; exact model/data terms separate.'},
      {'name':'Stable Audio checkpoints','source':'https://huggingface.co/stabilityai','usage_class':'CATALOG_ONLY','notes':'Code MIT; weights/services separate.'},
      {'name':'CosyVoice checkpoints','source':'https://huggingface.co/FunAudioLLM','usage_class':'CATALOG_ONLY','notes':'Verify per-model card/license before mirror.'},
      {'name':'Qwen3-TTS checkpoints','source':'https://huggingface.co/Qwen','usage_class':'CATALOG_ONLY','notes':'Verify exact release/model-card rights.'},
      {'name':'Freesound','source':'https://freesound.org/','usage_class':'CATALOG_ONLY','notes':'Per-file Creative Commons licenses; no blanket corpus rights.'},
      {'name':'Sonniss GDC Game Audio Bundle','source':'https://sonniss.com/gameaudiogdc','usage_class':'CATALOG_ONLY','notes':'High-value royalty-free source; rehosting/redistribution terms matter.'},
      {'name':'BBC Sound Effects','source':'https://sound-effects.bbcrewind.co.uk/','usage_class':'CATALOG_ONLY','notes':'Specific library licensing; no blanket commercial mirror.'},
      {'name':'OpenGameArt audio','source':'https://opengameart.org/','usage_class':'CATALOG_ONLY','notes':'Per-asset mixed licensing.'},
      {'name':'Audiokinetic Wwise','source':'https://www.audiokinetic.com/','usage_class':'CATALOG_ONLY','notes':'Proprietary middleware/content terms.'},
      {'name':'FMOD','source':'https://www.fmod.com/','usage_class':'CATALOG_ONLY','notes':'Proprietary middleware.'},
      {'name':'Kenney audio packs','source':'https://kenney.nl/assets','usage_class':'REUSABLE_CC0','notes':'Several packs already mirrored earlier; avoid duplicates.'}]}
    (catalog/'AUDIO_MODEL_ASSET_SERVICE_CATALOG.json').write_text(json.dumps(data,indent=2)); (catalog/'WHY_THIS_BATCH_MATTERS.md').write_text('# Why Batch 007 matters\n\nGame audio needs runtime/spatial acoustics, codecs, generative tooling, voice/TTS and rights-clean libraries. Code, weights, recordings, performers and service terms are separate provenance layers.\n'); cats.append({'name':'Audio model / asset / service catalog','source':'upstream hubs/libraries','usage_class':'CATALOG_ONLY','rights':'Metadata/links until exact per-item or checkpoint rights are captured.','commit':'metadata-only'})
    inv(runtime,rs); inv(codecs,cs); inv(gen,gs); inv(research,ns); inv(catalog,cats); transport(root,['runtime_spatial_open','codecs_signal_open','generative_voice_code_open','research_noncommercial','catalog_only'])
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='material-bank-batch-007'); a=ap.parse_args(); r=Path(a.out).resolve(); shutil.rmtree(r,ignore_errors=True); r.mkdir(parents=True); build(r)
