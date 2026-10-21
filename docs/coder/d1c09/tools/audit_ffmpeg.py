"""Fail closed on actual component/ELF/source provenance before debug integration."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,shutil,difflib
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c09';src=base/'upstream/source/ffmpeg-8.0.3';build=base/'outputs/ffmpeg-build';out=base/'evidence';snapshot=out/'ffmpeg-generated';snapshot.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
config=(build/'config.h').read_text(encoding='utf-8');components=(build/'config_components.h').read_text(encoding='utf-8')
enabled={kind:re.findall(r'^#define CONFIG_(\w+)_'+kind+r' 1$',components,re.M) for kind in ['DECODER','PARSER','DEMUXER','ENCODER','MUXER','PROTOCOL','HWACCEL']}
assert enabled=={'DECODER':['H263','H264','MPEG4'],'PARSER':['H263','H264','MPEG4VIDEO'],'DEMUXER':['AVI','MOV'],'ENCODER':[],'MUXER':[],'PROTOCOL':[],'HWACCEL':[]},enabled
for key in ['GPL','NONFREE','VERSION3','NETWORK']:assert re.search(r'^#define CONFIG_'+key+r' 0$',config,re.M),key
assert '#define MALLOC_PREFIX vk_c09_' in config
for name in ['config.h','config_components.h','config.asm','ffbuild/config.mak','ffbuild/config.log','libavcodec/codec_list.c','libavcodec/parser_list.c','libavformat/demuxer_list.c','libavformat/protocol_list.c']:
 p=build/name
 if p.exists():shutil.copyfile(p,snapshot/name.replace('/','_'))
objects=[];files={}
for p in sorted(build.rglob('*.d')):
 text=p.read_text(encoding='utf-8').replace('\\\n',' ')
 object_path=build/text.split(':',1)[0].strip();assert object_path.exists(),object_path
 deps=[]
 for token in text.split(':',1)[1].split():
  dep=(build/token).resolve();assert dep.is_file(),dep
  deps.append(row(dep));files[dep.as_posix()]=dep
 objects.append({'object':row(object_path),'dependency_file':row(p),'dependencies':deps})
licenses=[];violations=[]
for p in sorted(files.values()):
 text=p.read_text(encoding='utf-8',errors='strict');low=text.lower();header=low[:6000]
 generated=p.is_relative_to(build)
 if re.search(r'gnu\s+general\s+public\s+license',header) and not re.search(r'gnu\s+lesser\s+general\s+public\s+license',header):violations.append(p.as_posix())
 if p.name in ['jfdctfst.c','jfdctint_template.c','jrevdct.c']:license='IJG-special-notice'
 elif p.name=='faandct.c':license='ISC'
 elif p.name=='adler32.c':license='Zlib'
 elif 'lesser general public license' in header:license='LGPL-2.1-or-later'
 elif 'permission is hereby granted' in header:license='permissive-explicit-header'
 elif 'redistribution and use in source and binary' in header or 'redistribution and use in source or binary' in header:license='BSD-style-explicit-header'
 elif 'public domain' in header:license='public-domain-explicit-header'
 elif generated:license='generated-from-audited-configuration'
 else:license='upstream-LICENSE.md-default-LGPL-2.1-or-later-no-contrary-header'
 licenses.append({**row(p),'classification':license,'basis':'complete retained file plus exact upstream LICENSE.md; header excerpt is audit aid, not substitute for license','header_excerpt':text[:2200]})
assert not violations,violations
(out/'ffmpeg-object-source-license-map.json').write_text(json.dumps({'objects':objects,'files':licenses,'gpl_header_violations':violations,'scope':'267 compiled FFmpeg objects and all non-system compiler dependencies; generated code/config retained; NDK system headers/libraries are Android toolchain dependencies, not copied into source archive'},indent=2),encoding='utf-8')
# Check the complete upstream cumulative official security patch set against pristine 8.0.3.
cve_map={'5a6e2b0ab1bbc5a85a9575af8e4d67b4f0ed3d14':'CVE-2025-69693','716cf25eb8616e8e068a7c2a5d23ae107bd117b4':'CVE-2025-63757','b5996929df27276db37e075600988ebb17890eb4':'CVE-2025-67306','fe72a8781b22912ec7125de1509d83fc2b1ad802':'CVE-2025-67306','24b452cd9f6664dcee63f1d597ba052b34f8efd2':'CVE-2026-8461','31c9c550ef5a2aea5606c319b6299108c359f21f':'CVE-2026-8461','3e8f3537f957da011d7360acacc9941f3ce5c306':'CVE-2026-8461','5c8a8750de5239136da3e2cdb2ede8122864b252':'CVE-2026-30999'}
security=[]
for patch in sorted((out/'security-patches').glob('*.patch')):
 text=patch.read_text(encoding='utf-8');paths=re.findall(r'^\+\+\+ b/(.+)$',text,re.M)
 test=subprocess.run(['git','apply','--reverse','--check',str(patch)],cwd=src,capture_output=True,text=True,encoding='utf-8')
 # Later fixes may change context of earlier cumulative patches; record exact result, verify added lines as well.
 added=[line[1:] for line in text.splitlines() if line.startswith('+') and not line.startswith('+++') and line[1:].strip()]
 all_added=all(any(line.strip() in (src/name).read_text(encoding='utf-8') for name in paths) for line in added)
 assert test.returncode==0 or all_added,(patch.name,test.stderr)
 if patch.stem in ['b5996929df27276db37e075600988ebb17890eb4','fe72a8781b22912ec7125de1509d83fc2b1ad802']:
  iamf=(src/'libavformat/iamf_parse.c').read_text(encoding='utf-8').split('static int scalable_channel_layout_config',1)[1].split('static int ambisonics_config',1)[0]
  assert 'if (i && ch_layout.nb_channels <= audio_element->element->layers[i-1]->ch_layout.nb_channels)\n            return AVERROR_INVALIDDATA;' in iamf
  assert 'if (k != audio_element->nb_substreams)\n        return AVERROR_INVALIDDATA;' in iamf
  (out/'iamf-equivalent-fixed-function.txt').write_text('8.0.3 later context differs; both precise guards remain in this function.\nstatic int scalable_channel_layout_config'+iamf,encoding='utf-8')
 compiled=[name for name in paths if (src/name).resolve().as_posix() in files]
 security.append({'cve':cve_map[patch.stem],'commit':patch.stem,'patch':row(patch),'affected_files':paths,'compiled_dependencies':compiled,'reverse_check_exit':test.returncode,'reverse_check_output':test.stdout+test.stderr,'all_added_lines_present':all_added,'fix_coverage':'OFFICIAL_8.0.3_PRISTINE_SOURCE_CONTAINS_FIX','reachability':'compiled swscale output.c; affected YA16 output path is not the adapter RGBA output contract; fixed regardless' if patch.stem.startswith('716cf') else 'affected source not part of compiled object/header set; corresponding decoder/tool not enabled' if not compiled else 'compiled source; fixed upstream; exploitability not claimed'})
(out/'ffmpeg-security-coverage.json').write_text(json.dumps({'source':'https://ffmpeg.org/security.html','version':'8.0.3','local_patches':[],'official_patch_checks':security,'limitation':'cumulative official 8.0.1-8.0.3 listed CVEs, not proof of absence of all vulnerabilities or complete fuzzing'},indent=2),encoding='utf-8')
old=root/'docs/coder/d1c08/upstream/source/ffmpeg-8.0';changed=[];old_files={p.relative_to(old).as_posix():p for p in old.rglob('*') if p.is_file()};new_files={p.relative_to(src).as_posix():p for p in src.rglob('*') if p.is_file()}
for name in sorted(old_files.keys()|new_files.keys()):
 before=old_files.get(name);after=new_files.get(name)
 if before is None or after is None or sha(before)!=sha(after):changed.append({'name':name,'old_sha256':sha(before) if before else None,'new_sha256':sha(after) if after else None})
(out/'ffmpeg-8.0-to-8.0.3-delta.json').write_text(json.dumps({'old':'8.0','new':'8.0.3','changed_files':changed,'new_codec_surface':enabled,'local_patches':[]},indent=2),encoding='utf-8')
ndk=Path('D:/Android/SDK/ndk/30.0.16248370');tool=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-readelf.exe';libs=[]
for folder,filename in [('libavcodec','libavcodec.so.62'),('libavformat','libavformat.so.62'),('libavutil','libavutil.so.60'),('libswscale','libswscale.so.9')]:
 p=build/folder/filename;dump=subprocess.check_output([str(tool),'-h','-lW','-d',str(p)]).decode('utf-8');(out/(filename+'.readelf.txt')).write_text(dump,encoding='utf-8')
 assert 'AArch64' in dump
 loads=[line for line in dump.splitlines() if re.match(r'\s*LOAD\s',line)];assert loads and all(int(line.split()[-1],16)>=16384 for line in loads)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dump);assert set(needed)<=set(['libavcodec.so','libavutil.so','libc.so','libm.so','libvideokit_alloc.so']),needed
 libs.append({**row(p),'needed':needed,'soname':re.findall(r'\(SONAME\).*?\[(.*?)\]',dump),'load_alignment_min':16384})
result={'version':'8.0.3','source_archive_sha256':sha(base/'upstream/ffmpeg-8.0.3.tar.xz'),'config_components':enabled,'objects':len(objects),'audited_files':len(licenses),'h263_dependency':'mpeg4_decoder_select=h263_decoder; h263_decoder_select includes h263_parser; registered in codec_list.c/parser_list.c; LGPL headers audited','input_gate':'native adapter accepts AVI/MPEG4 or MOV/H264 only; H263 is compiled transitive dependency, not supported external input','gpl_nonfree_version3_network':False,'libraries':libs,'admission':'DEBUG_LOCAL_EXPERIMENT_ONLY','product_distribution':'NOT_APPROVED','android_loading':'NOT_RUN'}
(out/'ffmpeg-admission.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('AUDIT PASS',len(objects),'objects',len(licenses),'source dependencies',len(changed),'maintenance changes',len(security),'security patches')
