"""Archive build facts without admitting any native library to the App."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys, zipfile
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c08';build=base/'outputs/ffmpeg-build';out=base/'evidence'
art=base/'artifacts/D1-20261005-C08';art.mkdir(parents=True,exist_ok=True)
def record(p):
 return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
snapshot=out/'ffmpeg-generated';snapshot.mkdir(exist_ok=True)
for name in ['config.h','config_components.h','config.asm','ffbuild/config.mak','ffbuild/config.log']:
 p=build/name
 if p.exists():shutil.copyfile(p,snapshot/Path(name).name)
components=(build/'config_components.h').read_text(encoding='utf-8')
enabled={kind:re.findall(r'^#define CONFIG_(\w+)_'+kind+r' 1$',components,re.M) for kind in ['DECODER','PARSER','DEMUXER','ENCODER','MUXER','PROTOCOL','HWACCEL']}
config=(build/'config.h').read_text(encoding='utf-8')
guards={k:bool(re.search(r'^#define CONFIG_'+k+r' 0$',config,re.M)) for k in ['GPL','NONFREE','VERSION3','NETWORK']}
readelf=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-readelf.exe')
libs=[]
with zipfile.ZipFile(art/'ffmpeg-arm64-NOT-ADMITTED.zip','w',zipfile.ZIP_DEFLATED) as z:
 for directory,filename in [('libavcodec','libavcodec.so.62'),('libavformat','libavformat.so.62'),('libavutil','libavutil.so.60'),('libswscale','libswscale.so.9')]:
  p=build/directory/filename
  elf=subprocess.check_output([str(readelf),'-h','-l','-d',str(p)]).decode('utf-8')
  (out/(filename+'.readelf.txt')).write_text(elf,encoding='utf-8')
  row=record(p);row['needed']=re.findall(r'\(NEEDED\).*?\[(.*?)\]',elf);row['soname']=re.findall(r'\(SONAME\).*?\[(.*?)\]',elf);row['android_execution']='NOT_RUN';libs.append(row)
  assert 'AArch64' in elf
  z.write(p,filename)
objects=[record(p) for p in sorted(build.rglob('*.o'))]
dependencies=[{'path':p.relative_to(root).as_posix(),'content':p.read_text(encoding='utf-8',errors='replace')} for p in sorted(build.rglob('*.d'))]
(out/'ffmpeg-compiled-dependencies.json').write_text(json.dumps({'objects':objects,'dependency_files':dependencies},indent=2),encoding='utf-8')
result={'candidateId':'D1-20261005-C08','source_version':'8.0','target':'aarch64-linux-android31','build':'PASS_LOCAL_COMPILE_ONLY','upstream_patches':[],
 'host_compiler_workaround':'configure uses target clang for host C11 syntax probe; hardcoded tables enabled; successful make log contains no HOSTCC/HOSTLD invocation. Native Windows generator execution not claimed.',
 'generated_configuration':enabled,'disabled_guard_checks':guards,'libraries':libs,'compiled_objects':len(objects),
 'integration':'STOPPED_NOT_ADMITTED','composition_gate':'BLOCKED_STRICT_WHITELIST',
 'expected_decoders':['H264','MPEG4'],'unexpected_decoders':sorted(set(enabled['DECODER'])-{'H264','MPEG4'}),
 'expected_parsers':['H264','MPEG4VIDEO'],'unexpected_parsers':sorted(set(enabled['PARSER'])-{'H264','MPEG4VIDEO'}),
 'dependency_reason':'upstream configure mpeg4_decoder_select=h263_decoder; h263_decoder_select includes h263_parser',
 'license_observation':'Configure reports LGPL 2.1 or later and GPL/nonfree/version3 disabled. This is not full compiled-code license clearance; unexpected H263 surface has not been admitted.',
 'next_step':'After user resumes: review reproducible upstream dependency/registration patch that preserves MPEG4 decoding without exposing extra H263 decoder/parser; rerun configuration, build, ELF/compiled-source license audit before any debug JNI integration.',
 'apk_built':False,'native_copied_to_jniLibs':False,'device_execution':'NOT_RUN'}
assert all(guards.values());assert result['unexpected_decoders']==['H263'];assert result['unexpected_parsers']==['H263']
assert not list((base/'native-libs').rglob('*av*.so*'))
(out/'ffmpeg-build-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
