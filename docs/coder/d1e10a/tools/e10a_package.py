"""E9B exact provenance/build binding/targeted evidence/freeze and read-only verification. No device."""
import argparse,datetime,difflib,hashlib,json,pathlib,re,shutil,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e9b';ID='D1-20261018-E10A'
DOCS=[R/f'docs/coder/D1_E10A_{s}_V1.0.md' for s in ['DELIVERY','EXECUTION_RUNBOOK','FAILURE_AND_FINAL_REVIEW','ACTIVATION_INPUT_DAG']]
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
 for name,pin in [('d1e9b/evidence/e9b-freeze.json','6f8c1ffffa6bff17da48b7067594d33980c443ff03a7c547e917f0814add2c92'),('d1e10/evidence/e10-freeze.json','d9b684b1d5946533738139c170b95aae1c4cc4743ccc9c14fae07ad46e8f81c1'),('d1e9a/evidence/e9a-freeze.json','edfb13109b1cc5103ed348f3ce757165597fe16fe8320a1426afd4cd9651fdfb'),('d1e9/evidence/e9-freeze.json','6cd4844610a8ed6df9f15a9809740dcf37d5b2d5c4597701388e792852830131'),('d1e7a/evidence/e7a-freeze.json','1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'),('d1e8a/evidence/e8a-design-seal.json','dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86')]:
  seal=R/'docs/coder'/name;assert sha(data(seal))==pin;d=read(seal)
  for x in d['immutableFiles']:check(x)
  verified.append(dict(seal=row(seal),immutableVerified=len(d['immutableFiles'])))
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',baselines=verified,deviceCalls=0,realMediaReads=0,mutation=False))
def provenance():
 mapping=[];changed=[]
 for p in sources()+sorted((B/'tools').glob('*')):
  if not p.is_file():continue
  old=OLD/p.relative_to(B);prior=row(old) if old.is_file() else None;current=row(p);relation='NEW' if prior is None else 'BYTE_IDENTICAL' if current['sha256']==prior['sha256'] else 'DERIVED_E9B';mapping.append(dict(current=current,baseline=prior,relationship=relation))
  if relation!='BYTE_IDENTICAL':
   changed.append(rel(p))
   if p.suffix in ['.java','.py','.ps1','.kts','.xml','.properties','.txt','.toml']:
    before=data(old).decode('utf-8-sig').splitlines(True) if prior else [];after=data(p).decode('utf-8-sig').splitlines(True);q=B/'evidence/diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(''.join(difflib.unified_diff(before,after,fromfile=rel(old) if prior else '/dev/null',tofile=rel(p))),encoding='utf-8')
 write(B/'evidence/source-derivation.json',dict(schema=1,status='PASS',baseline='D1-20261018-E9B',files=mapping,changedOrNew=changed,scope='E10A strict BOUND no-execute cancellation and host pre-wire STOP/ACK gates; shared Registry change requires one new PREPARE build'))
 strict=[]
 for p in sources():
  if p.suffix in ['.c','.h','.so'] or p.name in ['E4Owned.java','E4Broker.java','E4OutputBudget.java','E4FencedTask.java','E5BGuard.java','E5BFileId.java','E5ALifecycle.java','E4Session.java','E4CpuAdapter.java','CpuTaskClient.java','CpuIsolatedService.java','E4Encoder.java','E4EncoderNegotiation.java','PipelineRules.java','PipelineValidationReceipt.java','CpuFrameRules.java']:
   old=OLD/p.relative_to(B);assert data(p)==data(old),str(p);strict.append(dict(current=row(p),baseline=row(old)))
 lock=data(B/'app/gradle.lockfile');assert lock==data(OLD/'app/gradle.lockfile');coordinates=[l for l in lock.decode().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')];assert len(coordinates)==35
 native=[]
 for p in sorted((B/'upstream-c14/native-libs/arm64-v8a').glob('*.so')):assert data(p)==data(OLD/p.relative_to(B));native.append(row(p))
 assert len(native)==7
 bom=read(OLD/'evidence/sbom.json');bom['metadata']['component']['name']='VideoKit E10A PREPARE';bom['metadata']['component']['version']=ID;write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,status='PASS',baseline='D1-20261018-E9B',coordinates=35,coordinateDelta=[],lockSha256=sha(lock),nativeLibraries=7,native=native,nativeDelta=[],nativeRebuild=False,downloads=0,media3='1.9.3',ffmpeg='8.0.3',licenseClearance='UNCHANGED_NOT_GRANTED'))
 write(B/'evidence/native-and-strict-logic-inheritance.json',dict(schema=1,status='PASS',exactUnchanged=strict,frameworkLimitsChanged=False,nativeRebuild=False,strictSixFramesFullEof1000us='UNCHANGED',originalBudgetConsumption107218='INHERITED_NO_DEVICE_READ'))
 external()
def checks():
 attempts=[B/'evidence/selfcheck-attempts/targeted-002',B/'evidence/selfcheck-attempts/console-003'];results=[];trace=[]
 for attempt in attempts:
  d=read(attempt/'results.json');assert all(x['exitCode']==0 for x in d['results'])
  for x in read(attempt/'inputs.json'):
   p=B/'evidence/E10AProductionCheck.before-console-check.java.txt' if attempt.name=='targeted-002' and x['path'].endswith('/E10AProductionCheck.java') else R/x['path'];raw=data(p);assert len(raw)==x['bytes'] and sha(raw)==x['sha256'],x['path']
  for x in d['results']:
   case=x['case'];work=B/'.selfcheck'/attempt.name/case;v=read(work/'result.json');assert v['status']=='PASS_FINITE_LOCAL_SCOPE';item=dict(case=case,**v,stdout=row(attempt/(case+'.stdout.txt')),stderr=row(attempt/(case+'.stderr.txt')))
   if not v['productionExitAllowed']:
    t=read(attempt/(case+'.fixture-teardown.json'));assert not t['originalCloseAck'] and t['notASafeExitProof'];item['fixtureTeardown']=row(attempt/(case+'.fixture-teardown.json'))
   results.append(item)
   for p in work.iterdir():
    if not p.is_file() or not (p.name in ['result.json','final-supervisor.json'] or p.name.startswith(('wire-','child-','frame-'))):continue
    target=attempt/'platform'/case/p.name;target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert data(target)==data(p)
    else:shutil.copyfile(p,target)
    trace.append(row(target))
 assert len(results)==12
 for p in (B/'.selfcheck/targeted-002/classes').rglob('*.class'):
  if p.name.startswith('E10AProductionCheck'):continue
  assert data(p)==data(B/'.selfcheck/console-003/classes'/p.relative_to(B/'.selfcheck/targeted-002/classes'))
 write(B/'evidence/targeted-check-results.json',dict(schema=1,status='PASS',groups=12,assertions=sum(x['assertions'] for x in results),sharedFixtureAssertions=sum(x['sharedFixtureAssertions'] for x in results),results=results,inputs=[row(a/'inputs.json') for a in attempts],commands=[row(a/'commands.json') for a in attempts],trace=trace,scope='Actual shared production prepareControl pre-wire gate / Registry / Run / original Process+5s decoder / actual console failure+custodial ACK and common entry exit; synthetic identity/metadata/control/system-finish platform only. No approved DEVICE CLI.',unknown='Controller finite teardown ONLY synthetic fixture JVM after production refused exit; all original child processes already returned; never a close ACK',old19SuiteReexecuted=False,old32SuiteReexecuted=False,old24SuiteReexecuted=False,nativeExecution='NOT_RUN',deviceCalls=0,realMediaReads=0))

def payload():
 paths=sources()+DOCS+[B/'E10A_PROGRESS_FINAL.md']
 for directory in ['tools','reference','evidence','artifacts','plan','templates']:paths += [p for p in (B/directory).rglob('*') if p.is_file() and p.name not in ['e10a-freeze.json','source-manifest.json'] and '__pycache__' not in p.parts]
 return sorted(set(paths))
def freeze():
 verify_inputs()
 for name in ['targeted-check-results.json','build-results.json','apk-audit.json','source-derivation.json','sbom-difference.json','external-readonly-verification.json','native-and-strict-logic-inheritance.json','host-binary-provenance.json','android-entry-inheritance.json','execution-package-validation.json','final-static-review.json']:assert read(B/'evidence'/name)['status']=='PASS',name
 build=read(B/'evidence/build-results.json');assert len(build['attempts'])==1 and build['attempts'][0]['exitCode']==0 and build['attempts'][0]['inputSnapshotSha256']==sha(data(B/'evidence/final-build-inputs.json'));assert '--offline' in build['attempts'][0]['arguments']
 files=payload();write(B/'evidence/source-manifest.json',dict(schema=1,candidateId=ID,files=[row(p) for p in files]));files.append(B/'evidence/source-manifest.json');archive=R/f'docs/coder/{ID}-source.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,rel(p))
 write(B/'evidence/e10a-freeze.json',dict(schema=1,candidateId=ID,status='FROZEN_E10A_PREPARE_STATIC_LOCAL_PENDING_REVIEW',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceFiles=len(files),archive=row(archive),immutableFiles=[row(p) for p in files]+[row(archive)],deviceCalls=0,activation='NOT_BUILT',actualHActor='NOT_CREATED',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN'));verify()
def verify():
 seal=read(B/'evidence/e10a-freeze.json')
 for x in seal['immutableFiles']:check(x)
 expected={x['path']:x for x in seal['immutableFiles'] if x['path']!=seal['archive']['path']}
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  assert set(z.namelist())==set(expected)
  for n,x in expected.items():raw=z.read(n);assert len(raw)==x['bytes'] and sha(raw)==x['sha256']
 print(json.dumps(dict(status='PASS',seal=row(B/'evidence/e10a-freeze.json'),archive=seal['archive'],immutableVerified=len(seal['immutableFiles']),mutation=False)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['snapshot','provenance','checks','freeze','verify']);a=p.parse_args();globals()[a.operation]()
