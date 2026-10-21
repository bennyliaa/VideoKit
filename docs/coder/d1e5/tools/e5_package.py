"""Bounded E5 snapshot/freeze/read-only verification. No device, media, network or dependency download."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];ID='D1-20261017-E5'
DOCS=[R/('docs/coder/D1_E5_'+s+'_V1.0.md') for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
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
 for d in ['src','android','app/src','gradle','upstream-c14']:
  paths.extend(p for p in (B/d).rglob('*') if p.is_file())
 paths.extend(B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile'])
 return [row(p) for p in sorted(set(paths))]
def snapshot():
 if (B/'evidence/e5-freeze.json').exists():raise ValueError('FROZEN')
 write(B/'evidence/final-build-inputs.json',dict(schema=1,candidateId=ID,files=inputs(),localPropertiesExcluded=True,deviceCalls=0))
def verify_inputs():
 d=json.loads(data(B/'evidence/final-build-inputs.json'))
 if d['files']!=inputs():raise ValueError('FINAL_BUILD_INPUTS_CHANGED')
 return d
def provenance():
 source=json.loads(data(B/'reference/E4A-upstream-copy-map.json'));mapped=[]
 for item in source['files']:
  q=dict(item);p=R/item['destination'].replace('/d1e4a/','/d1e5/');actual=row(p)
  q.update(destination=actual['path'],bytes=actual['bytes'],sha256=actual['sha256'],originalBytes=item['bytes'],originalSha256=item['sha256'])
  q['relationship']='BYTE_IDENTICAL' if q['sha256']==item['sha256'] else 'DERIVED_E5'
  if '/upstream-c14/' in q['destination'] and q['relationship']!='BYTE_IDENTICAL':raise ValueError('C14_CHANGED')
  mapped.append(q)
 write(B/'evidence/upstream-copy-map.json',dict(schema=1,scope='E5_C14_AND_E4A_PROVENANCE',files=mapped,originalE4AFreezeSha256=sha(data(B/'reference/E4A-freeze.json')),mediaReads=0))
 baseline=json.loads(data(B/'reference/E4A-source-manifest.json'));by={x['path']:x for x in baseline['files']};changes=[]
 for p in [p for d in ['src','android','app/src'] for p in (B/d).rglob('*') if p.is_file()]:
  current=row(p);old=by.get(current['path'].replace('/d1e5/','/d1e4a/'));changes.append(dict(current=current,baseline=old,relationship='NEW' if old is None else 'BYTE_IDENTICAL' if old['sha256']==current['sha256'] else 'DERIVED_E5'))
 write(B/'evidence/source-derivation.json',dict(schema=1,files=changes))
def sbom():
 lock=data(B/'app/gradle.lockfile');old=data(R/'docs/coder/d1e4a/app/gradle.lockfile')
 if lock!=old:raise ValueError('UNEXPECTED_DEPENDENCY_LOCK_DELTA')
 bom=json.loads(data(B/'reference/E4A-sbom.json'));bom['metadata']['component']['name']='VideoKit E5 single-APK Debug prototype';bom['metadata']['component']['version']=ID
 coords=[x for x in lock.decode().splitlines() if re.match(r'[^#=]+:[^:]+:[^=]+=',x)]
 if len(coords)!=35:raise ValueError('UNEXPECTED_COORDINATE_COUNT')
 write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,baseline='D1-20261017-E4A',baselineLockSha256=sha(old),currentLockSha256=sha(lock),coordinates=len(coords),coordinateDelta=[],nativeDelta=[],nativeLibraries=7,media3='1.9.3',ffmpeg='8.0.3',newDependencies=False,downloads=0,scope='Exact E4A lock/native identity inheritance; not vulnerability or license clearance',inheritedC14Difference='reference/E4A-sbom-difference.json'))
def external():
 reports=[]
 for folder,filename in [('d1e4a','e4a-freeze.json'),('d1e4at6','e4at6-freeze.json'),('d1e4amprep','mprep-freeze.json')]:
  p=R/'docs/coder'/folder/'evidence'/filename
  if not p.exists():
   found=list((R/'docs/coder'/folder/'evidence').glob('*freeze*.json'))
   if len(found)!=1:raise ValueError('EXTERNAL_FREEZE_IDENTITY')
   p=found[0]
  expected={'d1e4a':'a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d','d1e4at6':'861d2e179c66801f80353d79c6c2420a10f5748dfdd090db991a95e3ac0d6f37','d1e4amprep':'96f62df6a902a8b20eab73d97de63ea82321ceffe42c15f983530a245c3b2660'}
  if sha(data(p))!=expected[folder]:raise ValueError('EXTERNAL_SEAL_CHANGED')
  f=json.loads(data(p));immutable=f.get('immutableFiles',f.get('immutable',f.get('files')))
  if not isinstance(immutable,list):raise ValueError('EXTERNAL_SCHEMA')
  for entry in immutable:check(entry)
  reports.append(dict(freeze=row(p),immutableFilesVerified=len(immutable),mutation=False))
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',reports=reports,mediaReads=0,oldBudgetAccess=False,oldCacheMutation=False))
def freeze():
 verify_inputs()
 checks=json.loads(data(B/'evidence/local-check-results.json'))
 for entry in checks['inputs']:check(entry)
 build=json.loads(data(B/'evidence/build-results.json'));passing=[x for x in build['attempts'] if x['exitCode']==0]
 if not passing or passing[-1].get('inputSnapshotSha256')!=sha(data(B/'evidence/final-build-inputs.json')):raise ValueError('BUILD_SNAPSHOT_BINDING')
 if not all('--offline' in x['arguments'] for x in build['attempts']):raise ValueError('NON_OFFLINE_BUILD')
 for name in ['local-check-results.json','build-results.json','apk-audit.json','external-readonly-verification.json']:
  if json.loads(data(B/'evidence'/name))['status']!='PASS':raise ValueError('UNPASSED_'+name)
 paths=[]
 for d in ['src','android','app/src','gradle','upstream-c14','tools','reference','evidence']:
  paths.extend(p for p in (B/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['e5-freeze.json','source-manifest.json'])
 paths.extend(B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile'])
 paths.extend(DOCS);paths=sorted(set(paths));files=[row(p) for p in paths]
 if len(files)>4096 or sum(x['bytes'] for x in files)>256*1024*1024:raise ValueError('PACKAGE_BOUND')
 manifest=B/'evidence/source-manifest.json';write(manifest,dict(schema=1,candidateId=ID,files=files,scope='Complete E5 sources, tools, logs, synthetic evidence, inherited full C14 corresponding-source container; no private key, local properties, classes, build cache, real media'))
 z=B/'artifacts'/ID/(ID+'-source.zip');z.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for p in paths:out.writestr(rel(p),data(p))
 apks=json.loads(data(B/'evidence/apk-audit.json'))['apks'];immutable=files+[row(manifest),row(z)]+[{k:a[k] for k in ['path','bytes','sha256']} for a in apks]
 seal=dict(schema=1,candidateId=ID,state='FROZEN_LOCAL_ONLY_PENDING_COORDINATOR_REVIEW',frozenAtUtc=datetime.now(timezone.utc).isoformat(),sourceManifest=row(manifest),sourceZip=row(z),apks=apks,documents=[rel(p) for p in DOCS],immutableFiles=immutable,D1='NOT_PASSED',M0='NOT_STARTED',allP0='REMAIN_OPEN',historicalSignalGate='FAIL_UNCHANGED',androidExecution='NOT_RUN',deviceCalls=0,realMediaReads=0,scope='JVM models and offline compilation only; recovery/normal-codec acceptance requires separately dispatched actual Android evidence')
 write(B/'evidence/e5-freeze.json',seal);print(json.dumps(dict(freeze=row(B/'evidence/e5-freeze.json'),sourceZip=seal['sourceZip'],sourceFiles=len(files),immutableFiles=len(immutable))))
def verify():
 p=B/'evidence/e5-freeze.json';f=json.loads(data(p))
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
