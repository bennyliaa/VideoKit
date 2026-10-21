"""Explicit bounded wrapper-only rebuild. No third-party rebuild, downloads, devices or native fault."""
from pathlib import Path
import json,hashlib,subprocess,os
B=Path(__file__).resolve().parents[1];R=B.parents[2]
TOOL=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin')
def row(p):
 raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')
if (B/'evidence/e6-freeze.json').exists() or (B/'evidence/cpu-native-build.json').exists():raise RuntimeError('FROZEN_OR_NATIVE_ATTEMPT_USED')
expected={}
for name,key in [('ffmpeg-source-identity.json','files'),('ffmpeg-object-source-license-map.json','files'),('jni-source-dependency-map.json','dependencies')]:
 for x in json.loads((B/'reference'/name).read_text())[key]:expected[x['path']]=x['sha256']
headers=[]
for p in sorted((B/'native/headers').rglob('*')):
 if not p.is_file():continue
 part=p.relative_to(B/'native/headers');prefix='upstream/source/ffmpeg-8.0.3/' if part.parts[0]=='source' else 'outputs/ffmpeg-build/'
 suffix=prefix+Path(*part.parts[1:]).as_posix();matches={h for k,h in expected.items() if k.endswith(suffix)}
 if hashlib.sha256(p.read_bytes()).hexdigest() not in matches:raise RuntimeError('HEADER_IDENTITY:'+str(part))
 headers.append(row(p))
write(B/'evidence/native-header-verification.json',dict(status='PASS',scope='Exact prior FFmpeg 8.0.3 source/generated configuration header hashes; no configuration or third-party source changes',files=headers))
out=B/'upstream-c14/native-libs/arm64-v8a';prior={p.name:row(p) for p in out.glob('*.so')};assert len(prior)==7
tmp=B/'.native-temp';tmp.mkdir(exist_ok=False);source=B/'native/cpu.c';library=out/'libvideokit_cpu.so'
inputs=[row(source),row(B/'native/e6_verify.h')]+headers
write(B/'evidence/native-build-inputs.json',dict(files=inputs,baselineLibraries=list(prior.values())))
cmd=[str(TOOL/'clang.exe'),'--target=aarch64-linux-android31','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-Wl,--no-undefined','-Wl,-z,max-page-size=16384','-Wl,-soname,libvideokit_cpu.so','-I'+str(B/'native/headers/source'),'-I'+str(B/'native/headers/build'),str(source),'-L'+str(out),'-lavformat','-lavcodec','-lswscale','-lavutil','-lvideokit_alloc','-MMD','-MF',str(tmp/'cpu-native.d'),'-o',str(library)]
result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp)));(B/'evidence/cpu-native-compile.log').write_bytes(result.stdout)
if result.returncode:raise RuntimeError('NATIVE_COMPILE_FAILED; see preserved log')
after={p.name:row(p) for p in out.glob('*.so')};changes=[];elf=[]
for name,current in sorted(after.items()):
 relationship='CHANGED_PROJECT_WRAPPER' if current['sha256']!=prior[name]['sha256'] else 'BYTE_IDENTICAL'
 if relationship!='BYTE_IDENTICAL':assert name=='libvideokit_cpu.so'
 changes.append(dict(name=name,before=prior[name],after=current,relationship=relationship))
 p=out/name;dump=subprocess.check_output([str(TOOL/'llvm-readelf.exe'),'-h','-lW','-d',str(p)],timeout=20).decode();report=B/('evidence/native-'+name+'.readelf.txt');report.write_text(dump)
 alignments=[line.split()[-1] for line in dump.splitlines() if line.strip().startswith('LOAD ')]
 assert alignments and all(int(a,0)>=16384 for a in alignments),name
 elf.append(dict(name=name,loadSegmentAlignments=alignments,static16KiBAligned=True,report=row(report)))
symbols=subprocess.check_output([str(TOOL/'llvm-nm.exe'),'-D',str(library)],timeout=20).decode();(B/'evidence/cpu-native-symbols.txt').write_text(symbols)
assert all(s in symbols for s in ['NativeCpu_decode','NativeCpu_decodePipelineFrame','NativeCpu_verifyOutput'])
siteMap=[dict(line=n,source=line.strip()) for n,line in enumerate(source.read_text().splitlines(),1) if 'E6_FAIL(' in line or 'reason=E6_INCOMPLETE_EOF' in line]
write(B/'evidence/native-diagnostic-sites.json',dict(source=row(source),sites=siteMap,namedPredicates={'1':'DIMENSIONS','2':'EXTRA_FRAME','3':'PTS','4':'MISSING_PTS','5':'DEMUX','6':'SEND','7':'RECEIVE','8':'DRAIN','9':'INCOMPLETE_EOF'},siteZero='Success',reasonZeroNonzeroSite='Other exact source predicate at indicated frozen source line'))
write(B/'evidence/cpu-native-build.json',dict(status='PASS',command=cmd,inputs=inputs,output=row(library),changes=changes,elf=elf,ndk='30.0.16248370',target='aarch64-linux-android31',ffmpeg='8.0.3',thirdPartyVersionOrWhitelistChanged=False,scope='Only project JNI wrapper, diagnostic telemetry and equivalent strict gate helper changed; static ELF alignment not actual Android 16KiB execution',deviceCalls=0))
print('PASS E6 wrapper rebuild; exactly libvideokit_cpu.so changed; seven ELF LOAD alignments >=16KiB')
