"""E9A exact provenance/build binding/targeted evidence/freeze and read-only verification. No device."""
import argparse,datetime,difflib,hashlib,json,pathlib,re,shutil,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e9';ID='D1-20261018-E9A'
DOCS=[R/f'docs/coder/D1_E9A_{s}_V1.0.md' for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
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
 for name,pin in [('d1e9/evidence/e9-freeze.json','6cd4844610a8ed6df9f15a9809740dcf37d5b2d5c4597701388e792852830131'),('d1e7a/evidence/e7a-freeze.json','1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'),('d1e8a/evidence/e8a-design-seal.json','dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86')]:
  seal=R/'docs/coder'/name;assert sha(data(seal))==pin;d=read(seal)
  for x in d['immutableFiles']:check(x)
  verified.append(dict(seal=row(seal),immutableVerified=len(d['immutableFiles'])))
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',baselines=verified,deviceCalls=0,realMediaReads=0,mutation=False))
def provenance():
 mapping=[];changed=[]
 for p in sources()+sorted((B/'tools').glob('*')):
  if not p.is_file():continue
  old=OLD/p.relative_to(B);prior=row(old) if old.is_file() else None;current=row(p);relation='NEW' if prior is None else 'BYTE_IDENTICAL' if current['sha256']==prior['sha256'] else 'DERIVED_E9A';mapping.append(dict(current=current,baseline=prior,relationship=relation))
  if relation!='BYTE_IDENTICAL':
   changed.append(rel(p))
   if p.suffix in ['.java','.py','.ps1','.kts','.xml','.properties','.txt','.toml']:
    before=data(old).decode('utf-8-sig').splitlines(True) if prior else [];after=data(p).decode('utf-8-sig').splitlines(True);q=B/'evidence/diffs'/p.relative_to(B);q=q.with_suffix(q.suffix+'.diff');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(''.join(difflib.unified_diff(before,after,fromfile=rel(old) if prior else '/dev/null',tofile=rel(p))),encoding='utf-8')
 write(B/'evidence/source-derivation.json',dict(schema=1,status='PASS',baseline='D1-20261018-E9',files=mapping,changedOrNew=changed,scope='E9A four finding fixes; host lifetime/transport/deadline and grant invalidation; one necessary runner build'))
 strict=[]
 for p in sources():
  if p.suffix in ['.c','.h','.so'] or p.name in ['E4Owned.java','E4Broker.java','E4OutputBudget.java','E4FencedTask.java','E5BGuard.java','E5BFileId.java','E5ALifecycle.java','E4Session.java','E4CpuAdapter.java','CpuTaskClient.java','CpuIsolatedService.java','E4Encoder.java','E4EncoderNegotiation.java','PipelineRules.java','PipelineValidationReceipt.java','CpuFrameRules.java']:
   old=OLD/p.relative_to(B);assert data(p)==data(old),str(p);strict.append(dict(current=row(p),baseline=row(old)))
 lock=data(B/'app/gradle.lockfile');assert lock==data(OLD/'app/gradle.lockfile');coordinates=[l for l in lock.decode().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')];assert len(coordinates)==35
 native=[]
 for p in sorted((B/'upstream-c14/native-libs/arm64-v8a').glob('*.so')):assert data(p)==data(OLD/p.relative_to(B));native.append(row(p))
 assert len(native)==7
 bom=read(OLD/'evidence/sbom.json');bom['metadata']['component']['name']='VideoKit E9A PREPARE';bom['metadata']['component']['version']=ID;write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,status='PASS',baseline='D1-20261018-E9',coordinates=35,coordinateDelta=[],lockSha256=sha(lock),nativeLibraries=7,native=native,nativeDelta=[],nativeRebuild=False,downloads=0,media3='1.9.3',ffmpeg='8.0.3',licenseClearance='UNCHANGED_NOT_GRANTED'))
 write(B/'evidence/native-and-strict-logic-inheritance.json',dict(schema=1,status='PASS',exactUnchanged=strict,frameworkLimitsChanged=False,nativeRebuild=False,strictSixFramesFullEof1000us='UNCHANGED',originalBudgetConsumption107218='INHERITED_NO_DEVICE_READ'))
 external()
def checks():
 attempt=B/'evidence/selfcheck-attempts/final-pc-007';d=read(attempt/'results.json');expected=['TRANSPORT','STATUS_GAP','IDENTITY_CLEANUP','NO_REPLAY','DECODE_DEADLINE','GRANT','CONCURRENT_GRANT','CUSTODY_PIN','REMOTE','EARLY_EOF','READER_ERROR','OUTPUT_BOUND','CONSOLE_EOF','CONSOLE_TRUNCATED','CONSOLE_OVERFLOW','CONTROL5','LATE_VERDICT','CLOSE_LATCH','CLOSE_UNKNOWN'];assert [x['case'] for x in d['results']]==expected and all(x['exitCode']==0 for x in d['results'])
 override=B/'evidence/selfcheck-attempts/frame-validation-008';extra=read(override/'results.json');assert [x['case'] for x in extra['results']]==['TRANSPORT','DECODE_DEADLINE'] and all(x['exitCode']==0 for x in extra['results'])
 preserved={f'docs/coder/d1e9a/tools/{n}':B/'evidence'/(n+'.before-final-frame-validation.txt') for n in ['E9HostManager.java','E9HostDeployment.java','E9AProductionCheck.java']}
 for x in read(attempt/'inputs.json'):
  p=preserved.get(x['path'],R/x['path']);raw=data(p);assert len(raw)==x['bytes'] and sha(raw)==x['sha256'],x['path']
 for x in read(override/'inputs.json'):check(x)
 results=[]
 for x in d['results']:
  caseAttempt=override if x['case'] in ['TRANSPORT','DECODE_DEADLINE'] else attempt;raw=(caseAttempt/(x['case']+'.stdout.txt')).read_text(encoding='utf-8');m=re.search(r'assertions=(\d+) boundaryAssertions=(\d+) sharedFixtureAssertions=(\d+) realPCProcess=(true|false)',raw);assert m
  results.append(dict(case=x['case'],status='PASS_FINITE_LOCAL_SCOPE',assertions=int(m[1]),boundaryAssertions=int(m[2]),sharedFixtureAssertions=int(m[3]),realPCProcess=m[4]=='true',sourceAttempt=rel(caseAttempt),stdout=row(caseAttempt/(x['case']+'.stdout.txt')),stderr=row(caseAttempt/(x['case']+'.stderr.txt'))))
 # Only trace/command/status/teardown files, never fixture .mp4/data-directory metadata or classes.
 trace=[]
 for work in sorted((B/'.selfcheck').iterdir()):
  evidence=B/'evidence/selfcheck-attempts'/work.name
  if not evidence.is_dir():continue
  for p in work.rglob('*'):
   if not p.is_file() or 'classes' in p.parts or p.name not in ['stdout.txt','stderr.txt','argv.txt','supervisor.json','main-returned.json','unknown-hold-before-fixture-teardown.json','fixture-teardown.json','compile.args','child-ready','release','close-entered','close-release'] and not p.name.startswith('metadata-platform-'):continue
   if any(part.startswith('synthetic-') for part in p.relative_to(work).parts):continue
   assert p.stat().st_size<=262144;target=evidence/'platform'/p.relative_to(work);target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists():assert data(target)==data(p)
   else:shutil.copyfile(p,target)
   trace.append(row(target))
 write(B/'evidence/targeted-check-results.json',dict(schema=1,status='PASS',groups=19,finalMappedInvocations=19,finalValidationInvocations=21,targetedFinalInputSnapshot=row(override/'inputs.json'),assertions=sum(x['assertions'] for x in results),boundaryAssertions=sum(x['boundaryAssertions'] for x in results),sharedFixtureAssertions=sum(x['sharedFixtureAssertions'] for x in results),results=results,inputSnapshot=row(attempt/'inputs.json'),commands=row(attempt/'commands.json'),scope='Actual production ProcessBuilder/pipe reader/console/custodian/query client; controlled platform hooks and synthetic shared metadata only; Android NOT_RUN',unknownCloseTest='Production refused exit; known synthetic fixture controller teardown after assertions explicitly NOT a Java close ACK',old32SuiteReexecuted=False,nativeExecution='NOT_RUN',deviceCalls=0,realMediaReads=0))
 write(B/'evidence/test-trace-inventory.json',dict(schema=1,status='PASS',files=trace,bytes=sum(x['bytes'] for x in trace),deviceCalls=0,fixtureMediaIncluded=False))
def payload():
 paths=sources()+DOCS+[B/'E9A_PROGRESS_FINAL.md']
 for directory in ['tools','reference','evidence','artifacts']:paths += [p for p in (B/directory).rglob('*') if p.is_file() and p.name not in ['e9a-freeze.json','source-manifest.json'] and '__pycache__' not in p.parts]
 return sorted(set(paths))
def freeze():
 verify_inputs()
 for name in ['targeted-check-results.json','build-results.json','apk-audit.json','source-derivation.json','sbom-difference.json','external-readonly-verification.json','native-and-strict-logic-inheritance.json','public-android-entry-check.json','host-binary-provenance.json','final-static-review.json']:assert read(B/'evidence'/name)['status']=='PASS',name
 build=read(B/'evidence/build-results.json');assert len(build['attempts'])==1 and build['attempts'][0]['exitCode']==0 and build['attempts'][0]['inputSnapshotSha256']==sha(data(B/'evidence/final-build-inputs.json'));assert '--offline' in build['attempts'][0]['arguments']
 files=payload();write(B/'evidence/source-manifest.json',dict(schema=1,candidateId=ID,files=[row(p) for p in files]));files.append(B/'evidence/source-manifest.json');archive=R/f'docs/coder/{ID}-source.zip'
 with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,rel(p))
 write(B/'evidence/e9a-freeze.json',dict(schema=1,candidateId=ID,status='FROZEN_E9A_PREPARE_STATIC_ONLY',atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceFiles=len(files),archive=row(archive),immutableFiles=[row(p) for p in files]+[row(archive)],deviceCalls=0,activation='NOT_BUILT',actualHActor='NOT_CREATED',d1='NOT_PASSED',m0='NOT_STARTED',longTermAdmission='OPEN'));verify()
def verify():
 seal=read(B/'evidence/e9a-freeze.json')
 for x in seal['immutableFiles']:check(x)
 expected={x['path']:x for x in seal['immutableFiles'] if x['path']!=seal['archive']['path']}
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  assert set(z.namelist())==set(expected)
  for n,x in expected.items():raw=z.read(n);assert len(raw)==x['bytes'] and sha(raw)==x['sha256']
 print(json.dumps(dict(status='PASS',seal=row(B/'evidence/e9a-freeze.json'),archive=seal['archive'],immutableVerified=len(seal['immutableFiles']),mutation=False)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['snapshot','provenance','checks','freeze','verify']);a=p.parse_args();globals()[a.operation]()
