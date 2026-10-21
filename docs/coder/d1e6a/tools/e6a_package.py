"""Bounded E5 snapshot/freeze/read-only verification. No device, media, network or dependency download."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];ID='D1-20261017-E6A'
DOCS=[R/('docs/coder/D1_E6A_'+s+'_V1.0.md') for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
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
 if (B/'evidence/e6a-freeze.json').exists():raise ValueError('FROZEN')
 write(B/'evidence/final-build-inputs.json',dict(schema=1,candidateId=ID,files=inputs(),localPropertiesExcluded=True,deviceCalls=0))
def verify_inputs():
 d=json.loads(data(B/'evidence/final-build-inputs.json'))
 if d['files']!=inputs():raise ValueError('FINAL_BUILD_INPUTS_CHANGED')
 return d
def provenance():
 import difflib
 old=R/'docs/coder/d1e6';mapping=[];changed=[]
 for directory in ['src','android','app/src','upstream-c14']:
  for p in sorted((B/directory).rglob('*')):
   if not p.is_file():continue
   previous=old/p.relative_to(B);current=row(p);prior=row(previous) if previous.exists() else None
   relation='NEW' if prior is None else 'BYTE_IDENTICAL' if prior['sha256']==current['sha256'] else 'DERIVED_E6A'
   mapping.append(dict(current=current,baseline=prior,relationship=relation))
   if relation!='BYTE_IDENTICAL':
    changed.append(rel(p))
    if p.suffix in ['.java','.txt']:
     before=data(previous).decode('utf-8').splitlines(True) if prior else [];after=data(p).decode('utf-8').splitlines(True)
     q=B/'evidence/diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True)
     q.write_text(''.join(difflib.unified_diff(before,after,fromfile=rel(previous),tofile=rel(p))),encoding='utf-8')
 nativeOld=R/'docs/coder/d1e6/native/cpu.c';q=B/'evidence/diffs/native-cpu.c.diff';q.write_text(''.join(difflib.unified_diff(data(nativeOld).decode().splitlines(True),data(B/'native/cpu.c').decode().splitlines(True),fromfile=rel(nativeOld),tofile=rel(B/'native/cpu.c'))),encoding='utf-8')
 for name in ['E5AFinalObservation.java','E5N2Recovery.java','E5AAdmission.java','E5ALifecycle.java','E5BGuard.java','E5BFileId.java','E4OutputBudget.java']:
  assert data(B/'src/com/videokit/spike/e4'/name)==data(old/'src/com/videokit/spike/e4'/name),name
 write(B/'evidence/source-derivation.json',dict(schema=1,status='PASS',files=mapping,changedOrNew=changed,scope='Exact immediate E6 production/Android source delta plus E6A Java boundary fixes. Guard/recovery/observation/admission/lifecycle/budget bytes unchanged',nativeSourceOrigin=row(nativeOld),nativeRebuilt=False))

def sbom():
 old=R/'docs/coder/d1e6';lock=data(B/'app/gradle.lockfile');prior=data(old/'app/gradle.lockfile');assert lock==prior
 bom=json.loads(data(old/'evidence/sbom.json'));bom['metadata']['component']['name']='VideoKit E6A diagnostic scope and ownership fix';bom['metadata']['component']['version']=ID
 native=[]
 for p in sorted((B/'upstream-c14/native-libs/arm64-v8a').glob('*.so')):
  previous=old/p.relative_to(B);assert data(previous)==data(p);native.append(dict(current=row(p),baseline=row(previous),relationship='BYTE_IDENTICAL'))
 assert len(native)==7
 write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,status='PASS',baseline='D1-20261017-E6',baselineLockSha256=sha(prior),currentLockSha256=sha(lock),coordinates=35,coordinateDelta=[],nativeDelta=[],nativeLibraries=7,unchangedNativeLibraries=7,native=native,nativeRebuild=False,media3='1.9.3',ffmpeg='8.0.3',newDependencies=False,downloads=0,notice='upstream-c14/notice-assets/NOTICE-E6A.txt',scope='Exact E6 native and locked Maven inheritance, original native source/header/config and E6 build evidence retained; no third-party version/config/license change or clearance'))

def external():
 p=R/'docs/coder/d1e6/evidence/e6-freeze.json';expected='362429a40889e84df49228c684feaec93faca036eeb26a5fd535147329d32265';assert sha(data(p))==expected
 f=json.loads(data(p))
 for entry in f['immutableFiles']:check(entry)
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',freeze=row(p),immutableFilesVerified=len(f['immutableFiles']),mutation=False,mediaReads=0,scope='E6 all254 immutable items, no old-model execution or media/device read'))

def freeze():
 verify_inputs()
 checks=json.loads(data(B/'evidence/local-check-results.json'))
 for entry in checks.get('inputs',[]):check(entry)
 build=json.loads(data(B/'evidence/build-results.json'));passing=[x for x in build['attempts'] if x['exitCode']==0]
 if not passing or passing[-1].get('inputSnapshotSha256')!=sha(data(B/'evidence/final-build-inputs.json')):raise ValueError('BUILD_SNAPSHOT_BINDING')
 if not all('--offline' in x['arguments'] for x in build['attempts']):raise ValueError('NON_OFFLINE_BUILD')
 for name in ['local-check-results.json','build-results.json','apk-audit.json','external-readonly-verification.json','source-derivation.json','sbom-difference.json','native-and-strict-logic-inheritance.json','integration-static-check.json','delivery-consistency.json']:
  if json.loads(data(B/'evidence'/name))['status']!='PASS':raise ValueError('UNPASSED_'+name)
 paths=[]
 for d in ['src','android','app/src','gradle','upstream-c14','native','tools','reference','evidence']:
  paths.extend(p for p in (B/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in [B/'evidence/e6a-freeze.json',B/'evidence/source-manifest.json'])
 paths.extend(B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile'])
 paths.extend(DOCS);paths=sorted(set(paths));files=[row(p) for p in paths]
 if len(files)>4096 or sum(x['bytes'] for x in files)>256*1024*1024:raise ValueError('PACKAGE_BOUND')
 manifest=B/'evidence/source-manifest.json';write(manifest,dict(schema=1,candidateId=ID,files=files,scope='Complete E6A sources, tools, logs, synthetic evidence, inherited full C14 corresponding-source container; no private key, local properties, classes, build cache, real media'))
 z=B/'artifacts'/ID/(ID+'-source.zip');z.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for p in paths:out.writestr(rel(p),data(p))
 apks=json.loads(data(B/'evidence/apk-audit.json'))['apks'];preserved=[row(p) for p in sorted((B/'artifacts'/ID).glob('pre-*/*.apk'))];immutable=preserved+files+[row(manifest),row(z)]+[{k:a[k] for k in ['path','bytes','sha256']} for a in apks]
 seal=dict(schema=1,candidateId=ID,state='FROZEN_E6A_DIAGNOSTIC_BOUNDARIES_ANDROID_NOT_RUN',frozenAtUtc=datetime.now(timezone.utc).isoformat(),sourceManifest=row(manifest),sourceZip=row(z),apks=apks,documents=[rel(p) for p in DOCS],immutableFiles=immutable,D1='NOT_PASSED',M0='NOT_STARTED',allP0='REMAIN_OPEN',historicalSignalGate='FAIL_UNCHANGED',androidExecution='NOT_RUN',deviceCalls=0,originalRealSourceReads=0,authorizedFailedExportReads=0,authorizedFailedExportReadBytes=0,desktopDecode='NOT_RUN',G01='PRIOR_E5C_ACTUAL_BOUNDARY_ACCEPTED_UNCHANGED',E5CREGF01='INHERITED_E6_FIX_ANDROID_NOT_RUN',E6F01='PRODUCTION_BOUNDARY_LOCAL_SUPPORTED',E6F02='PRODUCTION_BOUNDARY_LOCAL_SUPPORTED',E6F03='PRODUCTION_RECEIVE_CONCURRENCY_LOCAL_SUPPORTED',scope='20 direct production adapter/receipt/receive/routing boundary cases,112 assertions with simulated platform operations; no JNI/Binder/Android system execution. E6 native/mux/strict validation unchanged.')
 write(B/'evidence/e6a-freeze.json',seal);print(json.dumps(dict(freeze=row(B/'evidence/e6a-freeze.json'),sourceZip=seal['sourceZip'],sourceFiles=len(files),immutableFiles=len(immutable))))
def verify():
 p=B/'evidence/e6a-freeze.json';f=json.loads(data(p))
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
