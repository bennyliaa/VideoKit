"""Local E9 provenance, finite test evidence, offline build binding, freeze and read-only verification."""
import argparse,datetime,difflib,hashlib,json,pathlib,zipfile,re
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e7a';ID='D1-20261018-E9'
DOCS=[R/('docs/coder/D1_E9_'+s+'_V1.0.md') for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
def sha(b):return hashlib.sha256(b).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def data(p):
 if p.is_symlink() or not p.is_file() or p.stat().st_size>96*1024*1024:raise ValueError('FILE_ROLE_BOUND:'+str(p))
 return p.read_bytes()
def row(p):
 b=data(p);return dict(path=rel(p),bytes=len(b),sha256=sha(b))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():
  assert json.loads(p.read_bytes())==d,'EXISTING_DIFFERENT:'+str(p)
  return
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def read(p):return json.loads(data(p))
def check(x):
 if row(R/x['path'])!=x:raise ValueError('CHANGED:'+x['path'])
def sourcepaths():
 paths=[]
 for d in ['src','android','app/src','gradle','upstream-c14','native']:
  paths += [p for p in (B/d).rglob('*') if p.is_file()]
 paths += [B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile']]
 return sorted(set(paths))
def snapshot():write(B/'evidence/final-build-inputs.json',dict(schema=1,candidateId=ID,files=[row(p) for p in sourcepaths()],localPropertiesExcluded=True,deviceCalls=0))
def verify_inputs():
 d=read(B/'evidence/final-build-inputs.json')
 if d['files']!=[row(p) for p in sourcepaths()]:raise ValueError('FINAL_BUILD_INPUTS_CHANGED')
 return d
def provenance():
 mapping=[];changed=[]
 for p in sourcepaths():
  previous=OLD/p.relative_to(B);prior=row(previous) if previous.exists() else None;current=row(p);relationship='NEW' if prior is None else 'BYTE_IDENTICAL' if current['sha256']==prior['sha256'] else 'DERIVED_E9'
  mapping.append(dict(current=current,baseline=prior,relationship=relationship))
  if relationship!='BYTE_IDENTICAL':
   changed.append(rel(p))
   if p.suffix in ['.java','.kts','.xml','.properties','.lockfile','.toml','.txt','.c']:
    before=data(previous).decode('utf-8').splitlines(True) if prior else [];after=data(p).decode('utf-8').splitlines(True);q=B/'evidence/diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(''.join(difflib.unified_diff(before,after,fromfile=rel(previous) if prior else '/dev/null',tofile=rel(p))),encoding='utf-8')
 write(B/'evidence/source-derivation.json',dict(schema=1,status='PASS',baseline='D1-20261017-E7A',files=mapping,changedOrNew=changed))
 # Exact unchanged primitives and strict validation; gated entry files have explicit reviewed diffs above.
 exact=[]
 for x in mapping:
  p=R/x['current']['path']
  if p.suffix in ['.c','.h','.so'] or p.name in ['E4Owned.java','E5BGuard.java','E5BFileId.java','E4Protocol.java','E4Broker.java','E5ALifecycle.java','E4EncoderNegotiation.java','PipelineRules.java','PipelineValidationReceipt.java','PipelineOutputValidation.java','CpuFrameRules.java','E6BDiagnosticState.java']:
   if x['relationship']!='BYTE_IDENTICAL':raise ValueError('UNEXPECTED_CORE_CHANGE:'+str(p))
   exact.append(x)
 lock=data(B/'app/gradle.lockfile');assert lock==data(OLD/'app/gradle.lockfile')
 coordinates=[line for line in lock.decode().splitlines() if line and not line.startswith('#') and not line.startswith('empty=')]
 assert len(coordinates)==35,len(coordinates)
 native=[x for x in mapping if x['current']['path'].endswith('.so')];assert len(native)==7
 bom=read(OLD/'evidence/sbom.json');bom['metadata']['component']['name']='VideoKit E9 PREPARE';bom['metadata']['component']['version']=ID
 write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,status='PASS',baseline='D1-20261017-E7A',lockSha256=sha(lock),coordinates=35,coordinateDelta=[],nativeLibraries=7,nativeDelta=[],native=native,nativeRebuild=False,downloads=0,ffmpeg='8.0.3',media3='1.9.3',licenseClearance='UNCHANGED_NOT_GRANTED'))
 write(B/'evidence/native-and-strict-logic-inheritance.json',dict(schema=1,status='PASS',exactUnchanged=exact,nativeRebuild=False,strictGate='6 frames/full EOF/1000us/content/thumb; no native execution',entryGatesChanged=True,frameworkLimitsChanged=False))
 verified=[]
 for path,pin in [('docs/coder/d1e7a/evidence/e7a-freeze.json','1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'),('docs/coder/d1e8a/evidence/e8a-design-seal.json','dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86')]:
  p=R/path;assert sha(data(p))==pin;d=read(p)
  for x in d['immutableFiles']:check(x)
  verified.append(dict(seal=row(p),immutableVerified=len(d['immutableFiles'])))
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',baselines=verified,mutation=False,deviceCalls=0,mediaReads=0))
def checks():
 attempt=B/'evidence/selfcheck-attempts/final-production-009';r=read(attempt/'results.json');expected=['A%02d'%i for i in range(1,24)]+['D%02d'%i for i in range(1,10)]+['A21-'+s for s in ['pending','guard','ledger','close']]
 assert [x['case'] for x in r['results']]==expected and all(x['exitCode']==0 for x in r['results'])
 override=B/'evidence/selfcheck-attempts/replacement-cut-011';extra=read(override/'results.json');assert len(extra['results'])==1 and extra['results'][0]['case']=='D05' and extra['results'][0]['exitCode']==0
 for i,x in enumerate(r['results']):
  if x['case']=='D05':r['results'][i]=extra['results'][0]
 inputs=read(attempt/'inputs.json');preserved={'docs/coder/d1e9/tools/E9HostDeployment.java':B/'evidence/host-deployment-before-dispatch-fix.java.txt','docs/coder/d1e9/tools/E9ProductionSelfCheck.java':B/'evidence/selfcheck-before-dispatch-fix.java.txt'}
 for path,x in inputs.items():
  p=preserved.get(path,R/path);assert len(data(p))==x['bytes'] and sha(data(p))==x['sha256'],path
 for path,x in read(override/'inputs.json').items():
  p=R/path;assert len(data(p))==x['bytes'] and sha(data(p))==x['sha256'],path
 assertions=sum(int(re.search(r'assertions=(\d+)',x['stdout']).group(1)) for x in r['results'])
 write(B/'evidence/local-check-results.json',dict(schema=1,status='PASS',groups=32,processInvocations=38,finalMappedInvocations=36,assertions=assertions,targetedRepair='D05 host dispatch candidate-only rehash; original source snapshots preserved; no APK source change',targetedInputSnapshot=row(override/'inputs.json'),results=r['results'],inputSnapshot=row(attempt/'inputs.json'),rawAttempt=rel(attempt),productionFiles='shared actual classes; real JVM files/locks; Android OS, UID, inode, directory fsync, system-log origin and clocks substituted',androidExecution='NOT_RUN',nativeExecution='NOT_RUN',realMediaReads=0,actualDeviceCatalog='NOT_CREATED',testCleanup='native facsimile cleanup does not change original E4Owned UNKNOWN or provide ACK'))
def payload():
 paths=sourcepaths()+DOCS+[B/"E9_PROGRESS_FINAL.md"]
 for d in ['tools','reference','evidence','artifacts']:
  paths += [p for p in (B/d).rglob('*') if p.is_file() and p.name not in ['e9-freeze.json','source-manifest.json'] and '__pycache__' not in p.parts]
 return sorted(set(paths))
def freeze():
 verify_inputs()
 for name in ['local-check-results.json','build-results.json','apk-audit.json','source-derivation.json','sbom-difference.json','external-readonly-verification.json','native-and-strict-logic-inheritance.json','public-android-entry-check.json','host-surface-check.json','final-static-review.json','test-trace-inventory.json']:
  assert read(B/'evidence'/name)['status']=='PASS',name
 build=read(B/'evidence/build-results.json');assert build['attempts'][-1]['inputSnapshotSha256']==sha(data(B/'evidence/final-build-inputs.json'));assert all('--offline' in a['arguments'] for a in build['attempts'])
 files=payload();manifest=dict(schema=1,candidateId=ID,files=[row(p) for p in files]);write(B/'evidence/source-manifest.json',manifest);files.append(B/'evidence/source-manifest.json')
 archive=R/'docs/coder'/f'{ID}-source.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,rel(p))
 entries=[row(p) for p in files];entries.append(row(archive))
 seal=dict(schema=1,candidateId=ID,status='FROZEN_PREPARE_STATIC_ONLY',createdUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceFiles=len(files),archive=row(archive),immutableFiles=entries,androidExecution='NOT_RUN',activation='NOT_BUILT',actualHActor='NOT_CREATED',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN')
 write(B/'evidence/e9-freeze.json',seal);verify()
def verify():
 seal=read(B/'evidence/e9-freeze.json')
 for x in seal['immutableFiles']:check(x)
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  expected={x['path']:x for x in seal['immutableFiles'] if x['path']!=seal['archive']['path']};assert set(z.namelist())==set(expected)
  for name,x in expected.items():b=z.read(name);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 print(json.dumps(dict(status='PASS',seal=row(B/'evidence/e9-freeze.json'),immutableVerified=len(seal['immutableFiles']),archive=seal['archive'],mutation=False),ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['snapshot','provenance','checks','freeze','verify']);a=p.parse_args();globals()[a.operation]()
