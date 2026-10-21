from pathlib import Path
import ast
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent
s=(R/'docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE/run_independent_checks.py').read_text()
s=s.replace('d1android02-capture-ready02-fix','d1android02-capture-ready03-fix').replace('D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE','D1_ANDROID02_CAPTURE_READY03_FIX_REVIEW_EVIDENCE').replace('ready02_fixed_owner','ready03_fixed_owner')
# Keep own prior original-owner driver; remove the prior inconclusive injected digest test.
a=s.index('def late_digest():');b=s.index('def policies():',a)
s=s[:a]+'''def tail_gate(end):
 c=case('tail-END' if end else 'tail-next',('identity',) if end else ('identity','global_idle'),fixtureProofSeconds=1,fixtureProofTailGate='CROSS_SAME_DEADLINE_AFTER_TIMELY_WRITER');o=owner(c)
 try:o.run_one();raise AssertionError('TAIL_ACCEPTED')
 except ValueError:pass
 assert o.failure=='PROOF_WALL_TIMEOUT_STICKY' and o.next==1 and len(o.records)==1
 r=o.records[0];g=r['tailGate'];assert g is not None and g['writerTimelyBeforeGate'] and r['proofWriter']['closeReturned']
 assert g['writerReturnedAt']<=g['writerJoinObservedBy']<g['deadline']<=g['tailGateReturnedAt']<=r['lastControlledObservationAboutToStartAt']
 assert r['sharedProofWindowStart']+o.proof==g['deadline']
 if end:assert r['proof']['nextId']=='END'
 else:assert r['proof']['nextId']=='global_idle' and not (c[1]/'global_idle-entered.json').exists()
 before=o.next
 try:o.run_one();raise AssertionError('TAIL_SUCCESSOR_ADMITTED')
 except ValueError:pass
 assert o.next==before
 return {'timelyOriginalWriterThenLateTail':g,'lastControlledPoint':r['lastControlledObservationAboutToStartAt'],'pendingThreadsAtTimeout':o.timeout_observations[-1]['pendingOriginalThreads'],'END':end,'laterAdmissionRejected':True,'fixtureGateNotProductionDelay':True}
''' +s[b:]
# Delta-only original entry guard host, after the first strict schema host and seven good roles.
a=s.index(' base=read_counterexample();samples=[]',s.index('def policies():'));b=s.index(' guards=[]',a)
s=s[:a]+' samples=[]\n'+s[b:]
# Add actual same-source request read assertions to the existing seven-step positive test.
needle=" assert rs[-1]['proof']['nextId']=='END' and rs[-1]['proof']['batchGroups']['payload']==6144"
replacement=needle+'''
 readrows=[]
 for k,r in enumerate(rs):
  co=r['console'];v=co['logicalControlReads'];rid=r['id'];requestBytes=(positive[0]/('request-'+rid+'.json')).stat().st_size;admissionBytes=(positive[1]/(rid+'-owner-admission.json')).stat().st_size
  priorBytes=0 if k==0 else sum((positive[1]/(rs[k-1]['id']+suffix)).stat().st_size for suffix in ['-completion-proof.json','-outer-return.json'])
  assert v['requestBodyReadCalls']==1 and v['requestBodyBytes']==requestBytes and v['ownerAdmissionBytes']==admissionBytes and v['predecessorProofAndNativeBytes']==priorBytes and co['proofReadBytes']==requestBytes+admissionBytes+priorBytes
  readrows.append({'id':rid,'request':requestBytes,'admission':admissionBytes,'previousProofNative':priorBytes,'logicalReadTotal':co['proofReadBytes']})
 save(E/'independent-seven-read-accounting.json',readrows)
'''
assert needle in s;s=s.replace(needle,replacement)
at=s.index('try:\n check(\'prepare-owner-rejects\'')
head=s[:at]
extra=r'''def schema_first():
 global extra_text
 h=W/'strict-schema-first';h.mkdir();base=read_counterexample();samples=[]
 def sample(name,d,ok):
  q=h/(name+'.txt');q.write_text('INSTRUMENTATION_RESULT: receipt='+json.dumps(d,separators=(',',':'))+'\nINSTRUMENTATION_CODE: -1\n',encoding='utf-8');samples.append({'name':name,'path':str(q),'ok':ok})
 sample('zero',base,True);d=copy.deepcopy(base);d['meter'].update(scopeInputReserved=8388608,scopeOutputRequested=16777216,scopeOutputAttempted=16777216);sample('upper-equal',d,True)
 for name,value in [('negative',-1),('bool',True),('string','0'),('fraction',.5),('over',8388609),('null',None)]:
  d=copy.deepcopy(base);d['meter']['scopeInputReserved']=value;sample(name,d,False)
 d=copy.deepcopy(base);del d['meter']['scopeOutputRequested'];sample('missing-budget',d,False)
 d=copy.deepcopy(base);d['firstFailure']='ERROR';sample('first-failure',d,False)
 d=copy.deepcopy(base);del d['firstFailure'];sample('missing-failure',d,False)
 d=copy.deepcopy(base);d['workerActuallyJoined']=1;sample('int-as-bool',d,False)
 d=copy.deepcopy(base);d['caseReceipts'][0]['caseOriginalResourcesReturned']='true';sample('history-type',d,False)
 d=copy.deepcopy(base);d['meter'].update(scopeInputReserved=-1,scopeOutputRequested=-1,scopeOutputAttempted=-1);d['firstFailure']='OLD_COUNTEREXAMPLE';sample('old-combination',d,False)
 d=copy.deepcopy(base);d['completedNano']=60000000000;sample('deadline-equal',d,False)
 args=h/'inputs.json';save(args,{'source':str(B/'tools/capture_android02.ps1'),'plan':str(B/'reference/exact-seven-role-plan.json'),'samples':samples})
 script=h/'schema.ps1';script.write_text("""param([string]$Inputs)
$ErrorActionPreference='Stop';$a=Get-Content -LiteralPath $Inputs -Raw|ConvertFrom-Json;$src=[IO.File]::ReadAllText($a.source);$b=$src.IndexOf('function IntField');$e=$src.IndexOf('$policyPath=');. ([scriptblock]::Create($src.Substring($b,$e-$b)));$plan=Get-Content -LiteralPath $a.plan -Raw|ConvertFrom-Json;$policy=@{runId='D1MA02-INDEPENDENT'};$answer=@();foreach($s in $a.samples){$v=RoleSemantic 'scope_all' $s.path $false;$ok=$v -ceq 'PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN';if($ok -ne $s.ok){throw ('SCHEMA_ASSERT '+$s.name+' '+$v)};$answer+=@{name=$s.name;value=$v}};@{results=$answer;count=$a.samples.Count;kind='PURE_LOCAL_POLICY_NOT_ANDROID'}|ConvertTo-Json -Depth 5 -Compress
""",encoding='utf-8')
 p=subprocess.Popen([PS,'-NoProfile','-NonInteractive','-File',str(script),'-Inputs',str(args)],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out,err=p.communicate();p._handle.Close();extra_text+=len(out)+len(err);(h/'stdout.raw').write_bytes(out);(h/'stderr.raw').write_bytes(err);save(h/'original-return.json',{'pid':p.pid,'waitReturned':True,'streamsReturned':True,'handleClosed':True,'exitCode':p.returncode,'stdoutBytes':len(out),'stderrBytes':len(err)});assert p.returncode==0,(out,err);v=json.loads(out);assert v['count']==15;return v
'''
end=r'''try:
 check('strict-schema-first-15-policy-cases',schema_first)
 check('prepare-owner-rejects',prepare)
 check('whole-seven-same-request-read-base-delta-END',seven)
 check('three-original-delta-guards-before-timeouts',policies)
 check('fresh-local-busy-stops',busy)
 check('partial-save-overrun',overrun)
 check('outer-live-thread-timeout-sticky',lambda:failed('outer-timeout','OUTER_WALL_TIMEOUT_STICKY',fixtureOuterSeconds=.1))
 check('shared-proof-close-window-sticky',lambda:failed('proof-timeout','PROOF_WALL_TIMEOUT_STICKY',fixtureProofSeconds=.03,fixtureProofCloseDelay=.12))
 check('timely-writer-late-tail-no-successor',lambda:tail_gate(False))
 check('timely-writer-late-tail-END',lambda:tail_gate(True))
finally:
 elapsed=time.monotonic()-START;summary={'status':'COMPLETE_INDEPENDENT_LIMITED_SUITE' if len(results)==10 and all(x['pass'] for x in results) and elapsed<=30 else 'INCOMPLETE_OR_FAILED','seconds':elapsed,'textObservedAndWritten':sum(o.text for o in owners)+extra_text,'fixtureStdinBytes':payload,'sdkDeviceJvmGradleMediaCalls':0,'killInterruptUnknownRetry':0,'results':results,'ownerFacts':[{'records':o.records,'failure':o.failure,'timeoutObservations':o.timeout_observations} for o in owners]};save(E/'independent-suite-results.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='ownerFacts'},ensure_ascii=False))
'''
target=E/'run_independent_checks.py';assert not target.exists();result=head+extra+end;ast.parse(result);target.write_text(result,encoding='utf-8');print('Prepared tester-owned driver; no processes started')
