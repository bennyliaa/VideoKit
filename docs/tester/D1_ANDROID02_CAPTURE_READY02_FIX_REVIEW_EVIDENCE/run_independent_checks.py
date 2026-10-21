from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess,threading,time
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready02-fix';E=Path(__file__).resolve().parent;W=E/'fixtures';assert not W.exists();W.mkdir()
spec=importlib.util.spec_from_file_location('ready02_fixed_owner',B/'tools/outer_owner.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M);Owner=M.Owner;PY=M.PY;PS=M.PS;START=time.monotonic();results=[];owners=[];payload=0;extra_text=0
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):
 with Path(p).open('x',encoding='utf-8') as f:f.write(json.dumps(d,ensure_ascii=False,indent=2)+'\n');f.flush()
def write(p,d):Path(p).write_bytes(M.encode(d))
plan=read(B/'reference/exact-seven-role-plan.json')
def case(name,modes=('identity',),**changes):
 global payload
 home=W/name;root=home/'outputs';root.mkdir(parents=True)
 for folder in ['tools','reference','release']:(home/folder).mkdir()
 for rel in ['tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/legacy-tool-route-contract.json']:(home/rel).write_bytes((B/rel).read_bytes())
 policy=read(B/'release/capture-policy.json');policy.update(mode='OFFLINE_FIXTURE',scope=hashlib.sha256(('INDEPENDENT-'+name).encode()).hexdigest(),evidenceRoot=str(root),toolSha256=sha(PY),fixtureScriptSha256=sha(B/'selfchecks/capture_fixture.py'),fixtureFault='NONE',fixtureGatePath=str(root/'fixture-gate'),fixtureOuterSeconds=10,fixtureProofSeconds=2)
 slots=[]
 for n,mode in enumerate(modes):
  s=dict(plan['steps'][n]);s.update(argv=[PY,'-I','-X','utf8','-B',(B/'selfchecks/capture_fixture.py').as_posix(),mode,str(root/'fixture-gate')],maxTextBytes=min(s['maxTextBytes'],8192),qualificationSeconds=2)
  if mode in ['payload_app','payload_test']:
   size=4096 if mode=='payload_app' else 2048;p=root/(s['id']+'-fixture-input.bin');p.write_bytes(bytes(range(256))*(size//256));payload+=size;s['payloadPin']={'path':str(p),'bytes':size,'sha256':sha(p)}
  slots.append(s)
 policy['slots']=slots;policy.update(changes);write(home/'release/capture-policy.json',policy);return home,root,policy
def owner(c):
 if time.monotonic()-START>=26:raise AssertionError('SUITE_STOP_NEW_OWNER_26S')
 o=Owner(c[0]);owners.append(o);return o
def check(name,fn):
 try:d=fn();results.append({'name':name,'pass':True,'detail':d})
 except BaseException as e:results.append({'name':name,'pass':False,'detail':repr(e)});raise
positive=None;first=None
def prepare():
 try:Owner();raise AssertionError('PREPARE_ACCEPTED')
 except ValueError as e:assert str(e)=='PREPARATION_ONLY_NO_OUTER_CHILD'
 return {'popenEntered':False}
def seven():
 global positive,first
 positive=case('seven',('identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'));o=owner(positive);rs=o.run_seven();first=rs[0]
 for r in rs:
  d=r['proof']['outerDelta'];assert r['proofWriter']['closeReturned'] and r['proof']['candidateOnlyWriterCloseNotProven'] and r['proof']['batchGroups']['control']==r['console']['batchGroups']['control']+d['nativeWriteBytes']+d['proofWriteBytes'] and r['proof']['batchTextChargedBytesKnown']==r['console']['batchTextChargedBytesKnown']+d['nativeWriteBytes']+d['proofWriteBytes']
 assert rs[-1]['proof']['nextId']=='END' and rs[-1]['proof']['batchGroups']['payload']==6144
 assert b'INSTRUMENTATION_STATUS:' in (positive[1]/'scope_all-stdout.bin').read_bytes()
 return {'firstBase':first['console']['batchTextChargedBytesKnown'],'firstActualDelta':first['proof']['batchTextChargedBytesKnown']-first['console']['batchTextChargedBytesKnown'],'lastEndDelta':rs[-1]['proof']['batchTextChargedBytesKnown']-rs[-1]['console']['batchTextChargedBytesKnown'],'lastControl':rs[-1]['proof']['batchGroups']['control'],'lastTotal':rs[-1]['proof']['batchTextChargedBytesKnown'],'allOriginalProofWritersReturned':True}
def busy():
 c=case('busy',('identity','global_busy','app_absence'));o=owner(c)
 try:o.run_seven();raise AssertionError('BUSY_ACCEPTED')
 except ValueError:pass
 assert o.failure=='CAPTURE_FAILED_STICKY' and o.next==2 and o.records[-1]['console']['semantic'].startswith('ENV_WAIT') and not (c[1]/'app_absence-entered.json').exists();return {'busyActualLocalCapture':True,'nextNotEntered':True}
def failed(name,expected,**kw):
 c=case(name,**kw);o=owner(c)
 try:o.run_seven();raise AssertionError('ERROR_ACCEPTED')
 except ValueError:pass
 assert o.failure==expected and all(r['proofWriter']['closeReturned'] for r in o.records)
 before=o.next
 try:o.run_one();raise AssertionError('LATE_SUCCESS_UPGRADE')
 except ValueError:pass
 assert o.next==before
 if expected.startswith(('OUTER_WALL','PROOF_WALL')):assert any(v['code']==expected and v['pendingOriginalThreads']>0 for v in o.timeout_observations)
 return {'failure':o.failure,'nextRejected':True,'actualPendingObservations':o.timeout_observations}
def overrun():
 c=case('overrun',('overrun',));c[2]['slots'][0]['maxTextBytes']=80;write(c[0]/'release/capture-policy.json',c[2]);o=owner(c)
 try:o.run_seven();raise AssertionError('OVERRUN_ACCEPTED')
 except ValueError:pass
 co=o.records[-1]['console'];assert o.failure=='CAPTURE_FAILED_STICKY' and co['rawBytesKnown']==192 and co['rawTextSavedBytesKnown']<192;return {'read':192,'saved':co['rawTextSavedBytesKnown'],'failureSticky':True}
def late_digest():
 # One bounded local return gate at the actual post-writer digest invocation.
 # Same original digest result; no candidate-file/state edits or native fault.
 c=case('post-proof-digest',('identity','global_idle'),fixtureProofSeconds=.03);o=owner(c);target=c[1]/'identity-completion-proof.json';original=M.digest;seen=[]
 def gated(path):
  value=original(path)
  if Path(path)==target and not seen:
   begin=time.monotonic();time.sleep(.08);seen.append({'start':begin,'end':time.monotonic(),'delay':time.monotonic()-begin,'returnedSameDigest':True})
  return value
 M.digest=gated
 try:r=o.run_one()
 finally:M.digest=original
 assert len(seen)==1 and seen[0]['delay']>o.proof and o.failure is None and r['proofWriter']['closeReturned']
 o.run_one();assert o.next==2 and o.failure is None
 return {'controlledLocalDigestReturnGate':seen,'localProofSeconds':o.proof,'ownerAcceptedLateTail':True,'nextPopenActuallyEntered':True,'noAndroidOrActualDiskLatencyClaim':True}
def policies():
 global extra_text
 h,r,p=positive;pp=r/'identity-completion-proof.json';ad=r/'global_idle-owner-admission.json';oldproof=pp.read_bytes();oldadm=ad.read_bytes();orig=read(pp)
 base=read_counterexample();samples=[]
 def sample(name,d,ok):
  q=h/('policy-'+name+'.txt');q.write_text('INSTRUMENTATION_RESULT: receipt='+json.dumps(d,separators=(',',':'))+'\nINSTRUMENTATION_CODE: -1\n',encoding='utf-8');samples.append({'name':name,'path':str(q),'ok':ok})
 sample('valid-zero',base,True);d=copy.deepcopy(base);d['meter'].update(scopeInputReserved=8388608,scopeOutputRequested=16777216,scopeOutputAttempted=16777216);sample('equal-upper',d,True)
 for name,value in [('negative',-1),('boolean',True),('string','0'),('fraction',.25),('over',8388609),('null',None)]:
  d=copy.deepcopy(base);d['meter']['scopeInputReserved']=value;sample(name,d,False)
 d=copy.deepcopy(base);d['meter'].update(scopeInputReserved=-1,scopeOutputRequested=-1,scopeOutputAttempted=-1);d['firstFailure']='OLD_COMBINED_COUNTEREXAMPLE';sample('old-combined',d,False)
 d=copy.deepcopy(base);d['firstFailure']='ERROR';sample('first-error-alone',d,False)
 d=copy.deepcopy(base);del d['firstFailure'];sample('missing-error-field',d,False)
 d=copy.deepcopy(base);d['completedNano']=60000000000;sample('deadline-equal',d,False)
 d=copy.deepcopy(base);d['workerActuallyJoined']=1;sample('boolean-as-int',d,False)
 d=copy.deepcopy(base);d['caseReceipts'][2]['caseOriginalResourcesReturned']='true';sample('history-type',d,False)
 guards=[]
 for name,edit in [('reset',lambda d:d['batchGroups'].__setitem__('control',first['console']['batchGroups']['control'])),('fake-source',lambda d:d['outerDelta'].__setitem__('nativeWriteBytes',0)),('double',lambda d:d['batchGroups'].__setitem__('control',d['batchGroups']['control']+d['outerDelta']['nativeWriteBytes']+d['outerDelta']['proofWriteBytes']))]:
  d=copy.deepcopy(orig);edit(d);d['batchTextChargedBytesKnown']=sum(d['batchGroups'][k] for k in ['preflight','install','instrument','control']);q=h/(name+'-proof.json');write(q,d);guards.append({'name':name,'proof':str(q)})
 args=h/'policy-args.json';save(args,{'source':str(B/'tools/capture_android02.ps1'),'entry':str(h/'tools/capture_android02.ps1'),'plan':str(h/'reference/exact-seven-role-plan.json'),'samples':samples,'guards':guards,'proofPath':str(pp),'admission':str(ad),'request':str(h/'request-global_idle.json')})
 script=h/'independent-policy.ps1';script.write_text('''param([string]$Inputs)
$ErrorActionPreference='Stop';$a=Get-Content -LiteralPath $Inputs -Raw|ConvertFrom-Json;$src=[IO.File]::ReadAllText($a.source);$b=$src.IndexOf('function IntField');$e=$src.IndexOf('$policyPath=');. ([scriptblock]::Create($src.Substring($b,$e-$b)));$plan=Get-Content -LiteralPath $a.plan -Raw|ConvertFrom-Json;$policy=@{runId='D1MA02-INDEPENDENT'};$answer=@()
foreach($s in $a.samples){$v=RoleSemantic 'scope_all' $s.path $false;$ok=$v -ceq 'PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN';if($ok -ne $s.ok){throw ('WRONG_SEMANTIC '+$s.name+' '+$v)};$answer+=@{name=$s.name;value=$v}}
foreach($g in $a.guards){[IO.File]::WriteAllBytes($a.proofPath,[IO.File]::ReadAllBytes($g.proof));$hash=(Get-FileHash -LiteralPath $a.proofPath).Hash.ToLowerInvariant();$ad=Get-Content -LiteralPath $a.admission -Raw|ConvertFrom-Json;$ad.predecessorProofSha256=$hash;for($i=0;$i -lt 6;$i++){$t=($ad|ConvertTo-Json -Compress)+"`n";$ad.admissionWriteBytes=[Text.Encoding]::UTF8.GetByteCount($t)};[IO.File]::WriteAllText($a.admission,($ad|ConvertTo-Json -Compress)+"`n",[Text.UTF8Encoding]::new($false));$ash=(Get-FileHash -LiteralPath $a.admission).Hash.ToLowerInvariant();$err='';try{& $a.entry -RequestPath $a.request -PredecessorProofSha $hash -OwnerAdmissionSha $ash;throw 'UNEXPECTED_DELTA_ACCEPT'}catch{$err=$_.Exception.Message};if($err -cnotin @('OUTER_DELTA_RESET_OR_DUPLICATE','ORIGINAL_OUTER_DELTA_SOURCE_BYTES','EXACT_BASE_PLUS_DELTA_REQUIRED')){throw ('WRONG_DELTA '+$g.name+' '+$err)};$answer+=@{name=$g.name;value=$err}}
@{cases=$answer;semanticCount=$a.samples.Count;deltaCount=$a.guards.Count;classification='LOCAL_POLICY_AND_CHILD_BEFORE_GUARDS_NOT_ANDROID'}|ConvertTo-Json -Depth 5 -Compress
''',encoding='utf-8')
 try:
  proc=subprocess.Popen([PS,'-NoProfile','-NonInteractive','-File',str(script),'-Inputs',str(args)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=proc.communicate();proc._handle.Close();extra_text+=len(out)+len(err);save(h/'policy-owner-return.json',{'pid':proc.pid,'originalWaitReturned':True,'originalStreamsReturned':True,'originalHandleClosed':True,'exitCode':proc.returncode,'stdoutBytes':len(out),'stderrBytes':len(err)});(h/'policy.stdout').write_bytes(out);(h/'policy.stderr').write_bytes(err);assert proc.returncode==0,(out,err);return json.loads(out)
 finally:pp.write_bytes(oldproof);ad.write_bytes(oldadm)
def read_counterexample():
 text=(B/'reference/local-policy-counterexample-NOT-ANDROID.txt').read_text();d=json.loads(text.split('receipt=',1)[1].split('\n',1)[0]);d.update(firstFailure=None,runnerFinalizerOwnerAtReceipt=1,runnerFinishReturn='EXTERNAL_ORIGINAL_CAPTURE_REQUIRED',scopeBudgetsSharedAcrossAllCases=True,startedNano=0,completedNano=1);d['meter'].update(scopeInputReserved=0,scopeOutputRequested=0,scopeOutputAttempted=0)
 for pkg in ['com.videokit.d1media3.android02','com.videokit.d1media3.android02.test']:d['identity'][pkg]['versionCode']=1
 return d
try:
 check('prepare-owner-rejects',prepare);check('whole-seven-base-plus-delta-and-END',seven);check('fresh-local-busy-stops',busy);check('partial-save-overrun',overrun);check('outer-live-thread-timeout-sticky',lambda:failed('outer-timeout','OUTER_WALL_TIMEOUT_STICKY',fixtureOuterSeconds=.1));check('shared-proof-close-window-sticky',lambda:failed('proof-timeout','PROOF_WALL_TIMEOUT_STICKY',fixtureProofSeconds=.03,fixtureProofCloseDelay=.12));check('post-proof-hash-tail-deadline-counterexample',late_digest);check('strict-policy-and-three-delta-guards',policies)
finally:
 elapsed=time.monotonic()-START;summary={'status':'COMPLETE_INDEPENDENT_CHECKS_WITH_COUNTEREXAMPLE' if len(results)==8 and all(x['pass'] for x in results) and elapsed<=30 else 'INCOMPLETE_OR_FAILED','seconds':elapsed,'textObservedAndWritten':sum(o.text for o in owners)+extra_text,'fixtureStdinBytes':payload,'sdkDeviceJvmGradleMediaCalls':0,'killInterruptUnknownRetry':0,'results':results,'ownerFacts':[{'records':o.records,'failure':o.failure,'timeoutObservations':o.timeout_observations} for o in owners]};save(E/'independent-suite-results.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='ownerFacts'},ensure_ascii=False))
