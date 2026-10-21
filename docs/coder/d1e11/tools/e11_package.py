"""E9B exact provenance/build binding/targeted evidence/freeze and read-only verification. No device."""
import argparse,datetime,difflib,hashlib,json,pathlib,re,shutil,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e10a';ID='D1-20261018-E11'
DOCS=[R/f'docs/coder/D1_E11_{s}_V1.0.md' for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
def sha(b):return hashlib.sha256(b).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def data(p):
 if p.is_symlink() or not p.is_file() or p.stat().st_size>96*1024*1024:raise ValueError('FILE_ROLE_BOUND:'+str(p))
 return p.read_bytes()
def row(p):raw=data(p);return dict(path=rel(p),bytes=len(raw),sha256=sha(raw))
def read(p):return json.loads(data(p))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert read(p)==d,'EXISTING_DIFFERENT:'+str(p);return
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
def check(x):assert row(R/x['path'])==x,'CHANGED:'+x['path']
def sources():
 paths=[]
 for d in ['src','android','app/src','gradle','upstream-c14','native']:paths += [p for p in (B/d).rglob('*') if p.is_file()]
 paths += [B/p for p in ['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile']]
 return sorted(set(paths))
def snapshot():write(B/'evidence/final-build-inputs.json',dict(schema=1,candidateId=ID,files=[row(p) for p in sources()],localPropertiesExcluded=True,deviceCalls=0))
def verify_inputs():assert read(B/'evidence/final-build-inputs.json')['files']==[row(p) for p in sources()],'BUILD_INPUTS_CHANGED'
def external():
 verified=[]
 for name,pin in [('d1e10a/evidence/e10a-freeze.json','0a2d1c3a6c02f6194427ca93688a804f7df8d7966ffedb1ee0324cbccaf7d090'),('d1e9b/evidence/e9b-freeze.json','6f8c1ffffa6bff17da48b7067594d33980c443ff03a7c547e917f0814add2c92'),('d1e10/evidence/e10-freeze.json','d9b684b1d5946533738139c170b95aae1c4cc4743ccc9c14fae07ad46e8f81c1'),('d1e9a/evidence/e9a-freeze.json','edfb13109b1cc5103ed348f3ce757165597fe16fe8320a1426afd4cd9651fdfb'),('d1e9/evidence/e9-freeze.json','6cd4844610a8ed6df9f15a9809740dcf37d5b2d5c4597701388e792852830131'),('d1e7a/evidence/e7a-freeze.json','1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'),('d1e8a/evidence/e8a-design-seal.json','dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86')]:
  seal=R/'docs/coder'/name;assert sha(data(seal))==pin;d=read(seal)
  for x in d['immutableFiles']:check(x)
  verified.append(dict(seal=row(seal),immutableVerified=len(d['immutableFiles'])))
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',baselines=verified,deviceCalls=0,realMediaReads=0,mutation=False))
def provenance():
 mapping=[];changed=[]
 for p in sources()+sorted((B/'tools').glob('*')):
  if not p.is_file():continue
  old=OLD/p.relative_to(B);prior=row(old) if old.is_file() else None;current=row(p);relation='NEW' if prior is None else 'BYTE_IDENTICAL' if current['sha256']==prior['sha256'] else 'DERIVED_E10A';mapping.append(dict(current=current,baseline=prior,relationship=relation))
  if relation!='BYTE_IDENTICAL':
   changed.append(rel(p))
   if p.suffix in ['.java','.py','.ps1','.kts','.xml','.properties','.txt','.toml']:
    before=data(old).decode('utf-8-sig').splitlines(True) if prior else [];after=data(p).decode('utf-8-sig').splitlines(True);q=B/'evidence/diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(''.join(difflib.unified_diff(before,after,fromfile=rel(old) if prior else '/dev/null',tofile=rel(p))),encoding='utf-8')
 write(B/'evidence/source-derivation.json',dict(schema=1,status='PASS',baseline='D1-20261018-E10A',files=mapping,changedOrNew=changed,scope='E11 actual catalog ACTIVATION, source-head/type/selection/lifetime boundaries, detached readonly registry deployment, and one necessary v15 dual APK build'))
 strict=[]
 for p in sources():
  if p.suffix in ['.c','.h','.so'] or p.name in ['E4Owned.java','E4Broker.java','E4OutputBudget.java','E4FencedTask.java','E5BGuard.java','E5BFileId.java','E5ALifecycle.java','E4Session.java','E4CpuAdapter.java','CpuTaskClient.java','CpuIsolatedService.java','E4Encoder.java','E4EncoderNegotiation.java','PipelineRules.java','PipelineValidationReceipt.java','CpuFrameRules.java']:
   old=OLD/p.relative_to(B);assert data(p)==data(old),str(p);strict.append(dict(current=row(p),baseline=row(old)))
 lock=data(B/'app/gradle.lockfile');assert lock==data(OLD/'app/gradle.lockfile');coordinates=[l for l in lock.decode().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')];assert len(coordinates)==35
 native=[]
 for p in sorted((B/'upstream-c14/native-libs/arm64-v8a').glob('*.so')):assert data(p)==data(OLD/p.relative_to(B));native.append(row(p))
 assert len(native)==7
 bom=read(OLD/'evidence/sbom.json');bom['metadata']['component']['name']='VideoKit E11 ACTIVATION';bom['metadata']['component']['version']=ID;write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,status='PASS',baseline='D1-20261018-E10A',coordinates=35,coordinateDelta=[],lockSha256=sha(lock),nativeLibraries=7,native=native,nativeDelta=[],nativeRebuild=False,downloads=0,media3='1.9.3',ffmpeg='8.0.3',licenseClearance='UNCHANGED_NOT_GRANTED'))
 write(B/'evidence/native-and-strict-logic-inheritance.json',dict(schema=1,status='PASS',exactUnchanged=strict,frameworkLimitsChanged=False,nativeRebuild=False,strictSixFramesFullEof1000us='UNCHANGED',originalBudgetConsumption107218='INHERITED_NO_DEVICE_READ'))
 external()
def checks():
 mapped={};invocations=[]
 for name in ['activation-001','activation-002','activation-003','activation-004']:
  attempt=B/'evidence/selfcheck-attempts'/name;d=read(attempt/'results.json');assert d['status']=='PASS'
  for x in read(attempt/'inputs.json'):
   label=x['path'].replace('\\','/');p=B/'evidence/E9HostManager.before-activation-guard.java.txt' if name=='activation-001' and label.endswith('/E9HostManager.java') else B/'evidence/E11ProductionCheck.before-router.java.txt' if name=='activation-001' and label.endswith('/E11ProductionCheck.java') else B/'evidence/E11ProductionCheck.before-deployment-extra.java.txt' if name=='activation-002' and label.endswith('/E11ProductionCheck.java') else B/'evidence/E11ProductionCheck.before-export-roundtrip.java.txt' if name=='activation-003' and label.endswith('/E11ProductionCheck.java') else B/'evidence/E9ActivationPolicyExport.before-head-field.java.txt' if name!='activation-004' and label.endswith('/E9ActivationPolicyExport.java') else pathlib.Path(x['path']) if ':' in x['path'] else R/x['path']
   raw=data(p);assert len(raw)==x['bytes'] and sha(raw)==x['sha256'],x['path']
  for x in d['results']:
   case=x['case'];raw=data(attempt/(case+'.stdout.txt')).decode();m=re.search(r'assertions=(\d+)',raw);assert m and x['exitCode']==0;item=dict(case=case,assertions=int(m[1]),stdout=row(attempt/(case+'.stdout.txt')),stderr=row(attempt/(case+'.stderr.txt')));invocations.append(item);mapped[case]=item
 assert len(mapped)==12 and len(invocations)==13
 for prior,current in [('activation-001','activation-002'),('activation-002','activation-003'),('activation-003','activation-004')]:
  for p in (B/'.selfcheck'/prior/'classes').rglob('*.class'):
   if p.name.startswith('E11ProductionCheck') or prior=='activation-001' and p.name=='E9HostManager.class' or prior=='activation-003' and p.name=='E9ActivationPolicyExport.class':continue
   assert data(p)==data(B/'.selfcheck'/current/'classes'/p.relative_to(B/'.selfcheck'/prior/'classes')),str(p)
 write(B/'evidence/targeted-check-results.json',dict(schema=1,status='PASS',groups=12,finalMappedAssertions=sum(x['assertions'] for x in mapped.values()),totalValidationInvocations=13,results=list(mapped.values()),allInvocations=invocations,scope='Actual production parser/Phase/selection/current observer/finish-lifetime/deploy gate with real accepted catalog and synthetic Windows UID-inode/dir-fsync/deployment port. No Android/ADB/media tests.',unknown='Synthetic native facsimiles cleaned after denial assertions, never original close ACK/grant; actual runner finish hook compile/static plus used lifetime gate, Android runtime NOT_RUN',oldSuitesReexecuted=False,nativeExecution='NOT_RUN',deviceCalls=0))

def payload():
 paths=sources()+DOCS+[B/'E11_PROGRESS_FINAL.md']
 for directory in ['tools','reference','evidence','artifacts','release','source-export']:paths += [p for p in (B/directory).rglob('*') if p.is_file() and p.name not in ['e11-freeze.json','source-manifest.json'] and '__pycache__' not in p.parts]
 return sorted(set(paths))
def freeze():
 verify_inputs()
 for name in ['targeted-check-results.json','build-results.json','apk-audit.json','source-derivation.json','sbom-difference.json','external-readonly-verification.json','native-and-strict-logic-inheritance.json','host-binary-provenance.json','public-android-entry-check.json','release-binding-validation.json','final-static-review.json']:assert read(B/'evidence'/name)['status']=='PASS',name
 build=read(B/'evidence/build-results.json');assert len(build['attempts'])==1 and build['attempts'][0]['exitCode']==0 and build['attempts'][0]['inputSnapshotSha256']==sha(data(B/'evidence/final-build-inputs.json'));assert '--offline' in build['attempts'][0]['arguments']
 files=payload();write(B/'evidence/source-manifest.json',dict(schema=1,candidateId=ID,files=[row(p) for p in files]));files.append(B/'evidence/source-manifest.json');archive=R/f'docs/coder/{ID}-source.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,rel(p))
 write(B/'evidence/e11-freeze.json',dict(schema=1,candidateId=ID,status='FROZEN_E11_ACTIVATION_CANDIDATE_NOT_DEPLOYED',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceFiles=len(files),archive=row(archive),immutableFiles=[row(p) for p in files]+[row(archive)],deviceCalls=0,activation='BUILT_NOT_DEPLOYED',actualHActor='EXISTING_ACCEPTED_ONLY_NO_NEW_CATALOG',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN'));verify()
def verify():
 seal=read(B/'evidence/e11-freeze.json')
 for x in seal['immutableFiles']:check(x)
 expected={x['path']:x for x in seal['immutableFiles'] if x['path']!=seal['archive']['path']}
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  assert set(z.namelist())==set(expected)
  for n,x in expected.items():raw=z.read(n);assert len(raw)==x['bytes'] and sha(raw)==x['sha256']
 print(json.dumps(dict(status='PASS',seal=row(B/'evidence/e11-freeze.json'),archive=seal['archive'],immutableVerified=len(seal['immutableFiles']),mutation=False)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['snapshot','provenance','checks','freeze','verify']);a=p.parse_args();globals()[a.operation]()
