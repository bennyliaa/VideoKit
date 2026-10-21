"""One complete finite serial suite; exact production Owner used with local slots.
Never invokes SDK/device/port/media. No kill/retry/interrupt paths.
"""
from pathlib import Path
import sys,json,hashlib,time,uuid,copy,subprocess
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'tools'))
from outer_owner import Owner,digest,encode,read,PY,PS
START=time.monotonic();W=B/'selfchecks/work'/('suite-'+uuid.uuid4().hex[:10]);W.mkdir(parents=True)
for rel in ['tools/outer_owner.py','tools/capture_android02.ps1','selfchecks/run_checks.py']:(W/Path(rel).name).write_bytes((B/rel).read_bytes())
plan=read(B/'reference/exact-seven-role-plan.json');results=[];owners=[];payload=0;text=0
def save(p,d):p.write_bytes(encode(d))
def case(name,modes=('identity',),**changes):
 global payload
 home=W/name;root=home/'outputs';root.mkdir(parents=True)
 for d in ('tools','reference','release'):(home/d).mkdir()
 for r in ['tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/legacy-tool-route-contract.json']:(home/r).write_bytes((B/r).read_bytes())
 policy=read(B/'release/capture-policy.json');policy.update(mode='OFFLINE_FIXTURE',scope=hashlib.sha256(name.encode()).hexdigest(),evidenceRoot=str(root),toolSha256=digest(PY),fixtureScriptSha256=digest(B/'selfchecks/capture_fixture.py'),fixtureFault='NONE',fixtureGatePath=str(root/'fixture-gate'),fixtureOuterSeconds=10,fixtureProofSeconds=2)
 slots=[]
 for i,mode in enumerate(modes):
  s=dict(plan['steps'][i]);s.update(argv=[PY,'-I','-X','utf8','-B',(B/'selfchecks/capture_fixture.py').as_posix(),mode,str(root/'fixture-gate')],maxTextBytes=min(s['maxTextBytes'],8192),qualificationSeconds=2)
  if mode.startswith('payload_'):
   n=4096 if mode=='payload_app' else 2048;p=root/(s['id']+'-fixture-input.bin');p.write_bytes(bytes(range(256))*(n//256));payload+=n;s['payloadPin']={'path':str(p),'bytes':n,'sha256':digest(p)}
  slots.append(s)
 policy['slots']=slots;policy.update(changes);save(home/'release/capture-policy.json',policy)
 return home,root,policy
def owner(c):
 if time.monotonic()-START>26:raise AssertionError('SUITE_STOP_BEFORE_NEW_OWNER_26S')
 o=Owner(c[0]);owners.append(o);return o
def check(name,f):
 start=time.monotonic()
 try:r=f();results.append({'name':name,'pass':True,'detail':r,'seconds':time.monotonic()-start})
 except BaseException as e:results.append({'name':name,'pass':False,'detail':repr(e),'seconds':time.monotonic()-start});raise
positive=None;first=None;po=None
def preparation():
 try:Owner();raise AssertionError('PREPARATION_OWNER_ACCEPTED')
 except ValueError as e:assert str(e)=='PREPARATION_ONLY_NO_OUTER_CHILD'
 return 'Default owner rejected before Popen creation'
def chain():
 global positive,first,po
 positive=case('seven',('identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'));po=owner(positive);rs=po.run_seven();first=rs[0]
 for r in rs:
  co=r['console'];pr=r['proof'];delta=pr['outerDelta'];assert r['proofWriter']['closeReturned'] and not r['stickyFailureAfterWriterReturn']
  lr=co['logicalControlReads'];request=Path(co['bindings']['requestPath'])
  assert lr['requestBodyReadCalls']==1 and lr['requestBodyBytes']==request.stat().st_size
  assert co['proofReadBytes']==sum(lr[k] for k in ('requestBodyBytes','ownerAdmissionBytes','predecessorProofAndNativeBytes'))
  if r['id']=='identity':assert lr['predecessorProofAndNativeBytes']==0 and co['proofReadBytes']==lr['ownerAdmissionBytes']+request.stat().st_size
  assert pr['batchGroups']['control']==co['batchGroups']['control']+delta['nativeWriteBytes']+delta['proofWriteBytes']
  assert pr['batchTextChargedBytesKnown']==co['batchTextChargedBytesKnown']+delta['nativeWriteBytes']+delta['proofWriteBytes']
 assert rs[-1]['proof']['batchGroups']['payload']==6144
 raw=(positive[1]/'scope_all-stdout.bin').read_bytes();assert b'INSTRUMENTATION_STATUS:' in raw and b'INSTRUMENTATION_RESULT:' in raw
 for id,n in [('install_app',4096),('install_test',2048)]:
  co=next(r['console'] for r in rs if r['id']==id);assert co['input']['stdinWriteReturnedBytes']==n and co['input']['sourceCloseReturned']
 return {'roles':7,'firstBase':first['console']['batchTextChargedBytesKnown'],'firstDelta':first['proof']['batchTextChargedBytesKnown']-first['console']['batchTextChargedBytesKnown'],'finalControl':rs[-1]['proof']['batchGroups']['control'],'finalLogicalInbound':rs[-1]['proof']['batchTextChargedBytesKnown'],'allProofWritersReturned':True,'logicalControlReadsByRole':[{'id':r['id'],'reads':r['console']['logicalControlReads'],'total':r['console']['proofReadBytes']} for r in rs]}
def failed(name,c,expected):
 o=owner(c)
 try:o.run_seven();raise AssertionError('SHOULD_STOP')
 except ValueError:pass
 assert o.failure==expected,(o.failure,o.records)
 assert all(r['proofWriter']['closeReturned'] for r in o.records)
 before=o.next
 try:o.run_one();raise AssertionError('STICKY_REENTRY')
 except ValueError:pass
 assert o.next==before
 if expected in ('OUTER_WALL_TIMEOUT_STICKY','PROOF_WALL_TIMEOUT_STICKY'):assert any(r['code']==expected and r['pendingOriginalThreads']>0 for r in o.timeout_observations),o.timeout_observations
 return {'failure':o.failure,'entered':o.next,'originalWritersReturned':True,'noLateUpgrade':True,'timeoutObservations':o.timeout_observations}
def busy():
 c=case('busy',('identity','global_busy','app_absence'));o=owner(c)
 try:o.run_seven();raise AssertionError('BUSY_ACCEPTED')
 except ValueError:pass
 assert o.failure=='CAPTURE_FAILED_STICKY' and o.next==2 and not (c[1]/'app_absence-entered.json').exists()
 assert o.records[-1]['console']['semantic'].startswith('ENV_WAIT')
 return {'actualLocalCaptureBusy':True,'sdk':0,'nextNotEntered':True}
def overrun():
 c=case('overrun',('overrun',));c[2]['slots'][0]['maxTextBytes']=80;save(c[0]/'release/capture-policy.json',c[2]);r=failed('overrun',c,'CAPTURE_FAILED_STICKY');co=owners[-1].records[-1]['console'];assert co['rawBytesKnown']==192 and co['rawTextSavedBytesKnown']<192;r.update(raw=192,saved=co['rawTextSavedBytesKnown']);return r
def outer_timeout():return failed('outer',case('outer',fixtureOuterSeconds=.1),'OUTER_WALL_TIMEOUT_STICKY')
def proof_timeout():return failed('proof',case('proof',fixtureProofSeconds=.03,fixtureProofCloseDelay=.12),'PROOF_WALL_TIMEOUT_STICKY')
def tail_timeout(end=False):
 c=case('tail-END' if end else 'tail-before-next',('identity',) if end else ('identity','global_idle'),fixtureProofSeconds=1,fixtureProofTailGate='CROSS_SAME_DEADLINE_AFTER_TIMELY_WRITER');o=owner(c)
 try:o.run_seven();raise AssertionError('TAIL_SUCCESS_UNEXPECTED')
 except ValueError:pass
 assert o.failure=='PROOF_WALL_TIMEOUT_STICKY' and o.next==1 and len(o.records)==1
 r=o.records[0];g=r['tailGate'];assert g and g['writerTimelyBeforeGate']
 assert r['proofWriter']['closeReturned'] and r['proofWriter']['end']<=g['writerJoinObservedBy']<g['deadline']<=g['tailGateReturnedAt']<=r['lastControlledObservationAboutToStartAt']
 assert r['proof']['nextId']==('END' if end else 'global_idle')
 before=o.next
 try:o.run_one();raise AssertionError('TAIL_REENTRY_ALLOWED')
 except ValueError:pass
 assert o.next==before and not (c[1]/'global_idle-entered.json').exists()
 return {'failure':o.failure,'writerTimelyClosedBeforeTail':True,'gate':g,'lastControlledPoint':r['lastControlledObservationAboutToStartAt'],'nextNotAdmitted':True,'end':end,'sameSharedStart':r['sharedProofWindowStart'],'observations':o.timeout_observations}
def policies():
 """One finite semantic/guard host, all rejection branches before any context."""
 global text
 home,root,p=positive;pp=root/'identity-completion-proof.json';original=pp.read_bytes();orig=read(pp)
 # Three distinct original-ledger mutations, not source-level semantic mocks.
 guards=[]
 for name,edit in [('reset',lambda d:d['batchGroups'].__setitem__('control',first['console']['batchGroups']['control'])),('fake',lambda d:d['outerDelta'].__setitem__('nativeWriteBytes',0)),('duplicate',lambda d:d['batchGroups'].__setitem__('control',d['batchGroups']['control']+d['outerDelta']['nativeWriteBytes']+d['outerDelta']['proofWriteBytes']))]:
  d=copy.deepcopy(orig);edit(d)
  # Keep total consistent so the source-delta validator, not sum typo, must reject.
  d['batchTextChargedBytesKnown']=sum(d['batchGroups'][k] for k in ('preflight','install','instrument','control'))
  q=home/(name+'-proof.json');save(q,d);guards.append({'name':name,'proof':str(q)})
 # Nonfixture policy samples are policy assertions only, never Android receipts.
 source=(B/'reference/local-policy-counterexample-NOT-ANDROID.txt').read_text();base=json.loads(source.split('receipt=',1)[1].split('\n',1)[0]);base.update(firstFailure=None,runnerFinalizerOwnerAtReceipt=1,runnerFinishReturn='EXTERNAL_ORIGINAL_CAPTURE_REQUIRED',scopeBudgetsSharedAcrossAllCases=True,startedNano=0,completedNano=1)
 base['meter'].update(scopeInputReserved=0,scopeOutputRequested=0,scopeOutputAttempted=0)
 for pkg in ['com.videokit.d1media3.android02','com.videokit.d1media3.android02.test']:base['identity'][pkg]['versionCode']=1
 samples=[]
 def sample(name,d,ok):
  fp=home/('sem-'+name+'.txt');fp.write_bytes(('INSTRUMENTATION_RESULT: receipt='+json.dumps(d,separators=(',',':'))+'\nINSTRUMENTATION_CODE: -1\n').encode());samples.append({'name':name,'path':str(fp),'ok':ok})
 sample('zero',base,True)
 d=copy.deepcopy(base);d['meter'].update(scopeInputReserved=8388608,scopeOutputRequested=16777216,scopeOutputAttempted=16777216);sample('upper-equal',d,True)
 for name,val in [('negative',-1),('bool',True),('string','0'),('fraction',.5),('over',8388609),('null',None)]:
  d=copy.deepcopy(base);d['meter']['scopeInputReserved']=val;sample(name,d,False)
 d=copy.deepcopy(base);del d['meter']['scopeOutputRequested'];sample('missing',d,False)
 d=copy.deepcopy(base);d['firstFailure']='LOCAL_POLICY_ERROR';sample('firstFailure',d,False)
 d=copy.deepcopy(base);del d['firstFailure'];sample('missing-firstFailure',d,False)
 d=copy.deepcopy(base);d['workerActuallyJoined']=1;sample('flag-int',d,False)
 d=copy.deepcopy(base);d['caseReceipts'][0]['caseOriginalResourcesReturned']='true';sample('history-type',d,False)
 save(home/'policy-cases.json',{'guards':guards,'samples':samples,'source':str(B/'tools/capture_android02.ps1'),'plan':str(home/'reference/exact-seven-role-plan.json'),'entry':str(home/'tools/capture_android02.ps1'),'proofPath':str(pp),'request':str(home/'request-global_idle.json'),'admission':str(root/'global_idle-owner-admission.json')})
 script=home/'policy-checks.ps1';script.write_text('''param([string]$Inputs)
$ErrorActionPreference='Stop';$a=Get-Content -LiteralPath $Inputs -Raw|ConvertFrom-Json
$src=[IO.File]::ReadAllText($a.source);$begin=$src.IndexOf('function IntField');$end=$src.IndexOf('$policyPath=');. ([scriptblock]::Create($src.Substring($begin,$end-$begin)))
$plan=Get-Content -LiteralPath $a.plan -Raw|ConvertFrom-Json;$policy=@{runId='D1MA02-INDEPENDENT'};$count=0;$observed=@()
foreach($s in $a.samples){$value=RoleSemantic 'scope_all' $s.path $false;$pass=$value -ceq 'PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN';if($pass -ne $s.ok){throw ('SEMANTIC '+$s.name+' '+$value)};$count++;$observed+=@{case=$s.name;value=$value}}
foreach($g in $a.guards){[IO.File]::WriteAllBytes($a.proofPath,[IO.File]::ReadAllBytes($g.proof));$hash=(Get-FileHash -LiteralPath $a.proofPath).Hash.ToLowerInvariant();$ad=Get-Content -LiteralPath $a.admission -Raw|ConvertFrom-Json;$ad.predecessorProofSha256=$hash
 # Negative fixture: preserve exact admission-length binding by iterating size.
 for($i=0;$i -lt 6;$i++){$txt=($ad|ConvertTo-Json -Compress)+"`n";$ad.admissionWriteBytes=[Text.Encoding]::UTF8.GetByteCount($txt)}
 [IO.File]::WriteAllText($a.admission,($ad|ConvertTo-Json -Compress)+"`n",[Text.UTF8Encoding]::new($false));$ash=(Get-FileHash -LiteralPath $a.admission).Hash.ToLowerInvariant();$caught=''
 try{& $a.entry -RequestPath $a.request -PredecessorProofSha $hash -OwnerAdmissionSha $ash;throw 'UNEXPECTED'}catch{$caught=$_.Exception.Message}
 if($caught -cnotin @('OUTER_DELTA_RESET_OR_DUPLICATE','ORIGINAL_OUTER_DELTA_SOURCE_BYTES','EXACT_BASE_PLUS_DELTA_REQUIRED')){throw ('DELTA '+$g.name+' '+$caught)};$count++;$observed+=@{case=$g.name;value=$caught}
}
$budgetStart=$src.IndexOf('if($batchSdkBefore+1 -gt 7');$budgetEnd=$src.IndexOf("`n",$budgetStart);$budgetGate=[scriptblock]::Create($src.Substring($budgetStart,$budgetEnd-$budgetStart))
$batchSdkBefore=1;$group='preflight';$groupCap=1048576;$payloadCost=0;$commandBytes=100;$request=@{maxTextBytes=100};$groups=@{preflight=0;control=1048576;payload=0;command=0};$batchTextBefore=1048576;$caught=''
try{. $budgetGate}catch{$caught=$_.Exception.Message}
if($caught -cne 'WHOLE_SEVEN_ROLE_BUDGET_BEFORE_CHILD'){throw 'BUDGET_OVER_ACCEPTED'};$observed+=@{case='pure-over-limit-group-policy';value=$caught};$count++
@{passed=$count;semanticSamples=$a.samples.Count;deltaGuards=$a.guards.Count;observed=$observed}|ConvertTo-Json -Depth 6 -Compress
''',encoding='utf-8')
 adm=root/'global_idle-owner-admission.json';oldadm=adm.read_bytes()
 try:
  proc=subprocess.Popen([PS,'-NoProfile','-NonInteractive','-File',str(script),'-Inputs',str(home/'policy-cases.json')],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=proc.communicate();proc._handle.Close();text+=len(out)+len(err);assert proc.returncode==0,(out,err);return json.loads(out)
 finally:pp.write_bytes(original);adm.write_bytes(oldadm)
try:
 check('preparation-owner-zero-child',preparation)
 check('full-seven-original-owner-and-delta',chain)
 check('strict-semantics-and-ledger-mutations',policies)
 check('actual-local-busy-capture-halt',busy)
 check('overrun-partial-save',overrun)
 check('outer-window-sticky-original-return',outer_timeout)
 check('proof-writer-window-sticky-original-return',proof_timeout)
 check('timely-writer-late-tail-blocks-next',lambda:tail_timeout(False))
 check('timely-writer-late-tail-END',lambda:tail_timeout(True))
finally:
 elapsed=time.monotonic()-START
 # A text accounting ceiling, not a claim of physical disk reads or wire bytes.
 text+=sum(o.text for o in owners)
 summary={'schema':'READY03_FIX_LOCAL_SUITE_V1','entrySha256':digest(B/'tools/capture_android02.ps1'),'ownerSha256':digest(B/'tools/outer_owner.py'),'producerSha256':digest(B/'selfchecks/capture_fixture.py'),'runRoot':str(W),'elapsedSeconds':elapsed,'textObservedAndWrittenBytes':text,'fixturePayloadBytes':payload,'sdkChildren':0,'deviceQueries':0,'oldUnknownQueries':0,'kills':0,'results':results,'allPassed':len(results)==9 and all(r['pass'] for r in results) and elapsed<=30 and text<=4194304 and payload<=65536,'originalOwnerFacts':[{'records':o.records,'failure':o.failure,'timeoutObservations':o.timeout_observations} for o in owners]}
 save(W/'summary.json',summary);save(B/'evidence/local-selfchecks.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='originalOwnerFacts'},ensure_ascii=False))
