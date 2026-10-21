"""Bounded E5 snapshot/freeze/read-only verification. No device, media, network or dependency download."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];ID='D1-20261017-E6'
DOCS=[R/('docs/coder/D1_E6_'+s+'_V1.0.md') for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def data(p):
 p=p.absolute();p.relative_to(R)
 for parent in [p,*p.parents]:
  if parent==R:break
  if parent.is_symlink():raise ValueError('LINK:'+str(parent))
 if not p.is_file() or p.stat().st_size>96*1024*1024:raise ValueError('ROLE_OR_BOUND:'+str(p))
 return p.read_bytes()
def row(p):
 raw=data(p);return dict(path=rel(p),bytes=len(raw),sha256=sha(raw))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def check(r):
 if row(R/r['path'])!=r:raise ValueError('HASH_MISMATCH:'+r['path'])
def inputs():
 paths=[]
 for d in ['src','android','app/src','gradle','upstream-c14','native']:
  paths.extend(p for p in (B/d).rglob('*') if p.is_file())
 paths.extend(B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile'])
 return [row(p) for p in sorted(set(paths))]
def snapshot():
 if (B/'evidence/e6-freeze.json').exists():raise ValueError('FROZEN')
 write(B/'evidence/final-build-inputs.json',dict(schema=1,candidateId=ID,files=inputs(),localPropertiesExcluded=True,deviceCalls=0))
def verify_inputs():
 d=json.loads(data(B/'evidence/final-build-inputs.json'))
 if d['files']!=inputs():raise ValueError('FINAL_BUILD_INPUTS_CHANGED')
 return d
def provenance():
 import difflib
 old=R/'docs/coder/d1e5b';mapping=[];changed=[]
 for directory in ['src','android','app/src','upstream-c14']:
  for p in sorted((B/directory).rglob('*')):
   if not p.is_file():continue
   previous=old/p.relative_to(B);current=row(p);prior=row(previous) if previous.exists() else None
   relation='NEW' if prior is None else 'BYTE_IDENTICAL' if prior['sha256']==current['sha256'] else 'DERIVED_E6'
   mapping.append(dict(current=current,baseline=prior,relationship=relation))
   if relation!='BYTE_IDENTICAL':
    changed.append(rel(p))
    if p.suffix in ['.java','.txt']:
     before=data(previous).decode('utf-8').splitlines(True) if prior else [];after=data(p).decode('utf-8').splitlines(True)
     q=B/'evidence/diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True)
     q.write_text(''.join(difflib.unified_diff(before,after,fromfile=rel(previous),tofile=rel(p))),encoding='utf-8')
 nativeOld=R/'docs/coder/d1c14/native/cpu.c';q=B/'evidence/diffs/native-cpu.c.diff';q.write_text(''.join(difflib.unified_diff(data(nativeOld).decode().splitlines(True),data(B/'native/cpu.c').decode().splitlines(True),fromfile=rel(nativeOld),tofile=rel(B/'native/cpu.c'))),encoding='utf-8')
 for name in ['E5AFinalObservation.java','E5N2Recovery.java','E5AAdmission.java','E5ALifecycle.java','E5BGuard.java','E5BFileId.java','E4OutputBudget.java']:
  assert data(B/'src/com/videokit/spike/e4'/name)==data(old/'src/com/videokit/spike/e4'/name),name
 write(B/'evidence/source-derivation.json',dict(schema=1,status='PASS',files=mapping,changedOrNew=changed,scope='Exact E5B production/Android source delta plus new E6 wrappers. Guard/recovery/observation/admission/lifecycle/budget bytes unchanged',nativeSourceOrigin=row(nativeOld)))

def sbom():
 old=R/'docs/coder/d1e5b';lock=data(B/'app/gradle.lockfile');prior=data(old/'app/gradle.lockfile');assert lock==prior
 bom=json.loads(data(old/'evidence/sbom.json'));bom['metadata']['component']['name']='VideoKit E6 bounded mux/validator diagnostic fix';bom['metadata']['component']['version']=ID
 native=json.loads(data(B/'evidence/cpu-native-build.json'));delta=[x for x in native['changes'] if x['relationship']!='BYTE_IDENTICAL'];assert len(delta)==1
 updated=[]
 for component in bom.get('components',[]):
  if 'VideoKit CPU JNI/quota project glue' == component.get('name'):
   component['version']=ID;component['components']=[dict(type='library',name='libvideokit_cpu.so',version=ID,hashes=[dict(alg='SHA-256',content=delta[0]['after']['sha256'])],properties=[dict(name='correspondingSource',value='native/cpu.c + native/e6_verify.h; exact source/header/build map packaged')])];updated.append(component.get('name'))
 write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,baseline='D1-20261017-E5B',baselineLockSha256=sha(prior),currentLockSha256=sha(lock),coordinates=35,coordinateDelta=[],nativeDelta=delta,nativeLibraries=7,unchangedNativeLibraries=6,media3='1.9.3',ffmpeg='8.0.3',newDependencies=False,downloads=0,sbomNativeComponentsUpdated=updated,scope='Project libvideokit_cpu wrapper changed; six other natives and third-party config/version/license unchanged; not vulnerability/legal clearance',notice='upstream-c14/notice-assets/NOTICE-E6.txt',correspondingSource='native/cpu.c + native/e6_verify.h + exact verified headers/config + original full C14 corresponding-source container'))

def external():
 reports=[]
 for folder,name,expected in [('d1e5c','e5c-freeze.json','75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c'),('d1e5b','e5b-freeze.json','3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee')]:
  p=R/'docs/coder'/folder/'evidence'/name;assert sha(data(p))==expected
  f=json.loads(data(p))
  for entry in f['immutableFiles']:check(entry)
  reports.append(dict(freeze=row(p),immutableFilesVerified=len(f['immutableFiles']),mutation=False))
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',reports=reports,realMediaReads=0,scope='Prior E5C/E5B frozen candidates only; no historical tests rerun, no device/media'))

def freeze():
 verify_inputs()
 checks=json.loads(data(B/'evidence/local-check-results.json'))
 for entry in checks.get('inputs',[]):check(entry)
 build=json.loads(data(B/'evidence/build-results.json'));passing=[x for x in build['attempts'] if x['exitCode']==0]
 if not passing or passing[-1].get('inputSnapshotSha256')!=sha(data(B/'evidence/final-build-inputs.json')):raise ValueError('BUILD_SNAPSHOT_BINDING')
 if not all('--offline' in x['arguments'] for x in build['attempts']):raise ValueError('NON_OFFLINE_BUILD')
 for name in ['local-check-results.json','build-results.json','apk-audit.json','external-readonly-verification.json']:
  if json.loads(data(B/'evidence'/name))['status']!='PASS':raise ValueError('UNPASSED_'+name)
 paths=[]
 for d in ['src','android','app/src','gradle','upstream-c14','native','tools','reference','evidence']:
  paths.extend(p for p in (B/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [B/'evidence/e6-freeze.json',B/'evidence/source-manifest.json'])
 paths.extend(B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile'])
 paths.extend(DOCS);paths=sorted(set(paths));files=[row(p) for p in paths]
 if len(files)>4096 or sum(x['bytes'] for x in files)>256*1024*1024:raise ValueError('PACKAGE_BOUND')
 manifest=B/'evidence/source-manifest.json';write(manifest,dict(schema=1,candidateId=ID,files=files,scope='Complete E6 sources, tools, logs, synthetic evidence, inherited full C14 corresponding-source container; no private key, local properties, classes, build cache, real media'))
 z=B/'artifacts'/ID/(ID+'-source.zip');z.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for p in paths:out.writestr(rel(p),data(p))
 apks=json.loads(data(B/'evidence/apk-audit.json'))['apks'];preserved=[row(p) for p in sorted((B/'artifacts'/ID).glob('pre-*/*.apk'))];immutable=preserved+files+[row(manifest),row(z)]+[{k:a[k] for k in ['path','bytes','sha256']} for a in apks]
 seal=dict(schema=1,candidateId=ID,state='FROZEN_E6_MUX_AND_DIAGNOSTIC_FIX_ANDROID_REGRESSION_NOT_RUN',frozenAtUtc=datetime.now(timezone.utc).isoformat(),sourceManifest=row(manifest),sourceZip=row(z),apks=apks,documents=[rel(p) for p in DOCS],immutableFiles=immutable,D1='NOT_PASSED',M0='NOT_STARTED',allP0='REMAIN_OPEN',historicalSignalGate='FAIL_UNCHANGED',androidExecution='NOT_RUN',deviceCalls=0,originalRealSourceReads=0,authorizedFailedExportReads=2,authorizedFailedExportReadBytes=107302,desktopDecode='NOT_RUN',G01='PRIOR_E5C_ACTUAL_BOUNDARY_ACCEPTED_UNCHANGED',E5CREGF01='ROOT_CAUSE_REPRODUCED_LOCAL_FIX_ANDROID_NOT_RUN',scope='Actual locked Media3 muxer replay + production C strict predicate and JVM diagnosis/content checks; actual Android decoding/regression pending separate dispatch')
 write(B/'evidence/e6-freeze.json',seal);print(json.dumps(dict(freeze=row(B/'evidence/e6-freeze.json'),sourceZip=seal['sourceZip'],sourceFiles=len(files),immutableFiles=len(immutable))))
def verify():
 p=B/'evidence/e6-freeze.json';f=json.loads(data(p))
 if len(f['immutableFiles'])>4100:raise ValueError('IMMUTABLE_BOUND')
 for entry in f['immutableFiles']:check(entry)
 m=json.loads(data(R/f['sourceManifest']['path']));names=[x['path'] for x in m['files']]
 with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
  if z.namelist()!=names or len(set(names))!=len(names):raise ValueError('ZIP_MEMBERSHIP')
  if sum(x.file_size for x in z.infolist())>256*1024*1024:raise ValueError('ZIP_BOUND')
  for entry in m['files']:
   raw=z.read(entry['path'])
   if len(raw)!=entry['bytes'] or sha(raw)!=entry['sha256']:raise ValueError('ZIP_ENTRY_IDENTITY')
 verify_inputs();print(json.dumps(dict(status='PASS',freeze=row(p),sourceFiles=len(names),immutableFiles=len(f['immutableFiles']),deviceCalls=0,mediaReads=0,mode='READ_ONLY')))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['snapshot','inputs','provenance','sbom','external','freeze','verify']);a=p.parse_args();{'snapshot':snapshot,'inputs':verify_inputs,'provenance':provenance,'sbom':sbom,'external':external,'freeze':freeze,'verify':verify}[a.mode]()
