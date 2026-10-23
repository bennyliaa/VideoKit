"""Deterministic whole source assembly, never execution authority."""
from pathlib import Path
import sys,json,hashlib
B=Path(__file__).resolve().parents[1];OLD=B.parent/'d1android02-compat03-schema-parity01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def change(s,a,b):
 if a not in s:raise ValueError('ASSEMBLY_EXPECTED:'+a[:90])
 return s.replace(a,b)
oldseal=json.loads((OLD/'reference/runner-source-seal.json').read_text())['sources']
for rel in oldseal:
 if rel not in ('tools/outer_owner.py','tools/production_runner.py','tools/capture_android02.ps1','tools/admission_checks.ps1','reference/exact-seven-role-plan.json','reference/gate-sources.json','selfchecks/capture_fixture.py'):
  p=B/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((OLD/rel).read_bytes())
sys.path.insert(0,str(B/'tools'))
from contract03_patches import gate_patch,runner_patch,owner_patch
put(B/'tools/entry_gates.py',gate_patch((B/'tools/entry_gates.py').read_text()))
from fact_collector import plan
sys.path.insert(0,str(B/'selfchecks'))
from fixture_inputs import wire,home_detail
put(B/'selfchecks/fact_fixture.py',"\"\"\"Frozen synthetic bytes only; never SDK/device evidence.\"\"\"\nimport sys\nif sys.argv[1:]!=['COMPLETE']:raise SystemExit('EXACT_FIXTURE_ONLY')\nsys.stdout.buffer.write("+repr(wire())+")\n")
put(B/'reference/fact-plan.json',json.dumps(plan(),indent=2)+'\n')
plan7=json.loads((OLD/'reference/exact-seven-role-plan.json').read_text())
plan7['allowedForegroundSystemPackages']=[]
plan7['globalIdleContract']={'schema':'GLOBAL_IDLE_CONTRACT02_V1','qualification':'globalIdleQualification in externally approved once permit; exact targetScope/source/plan; <=16384 bytes; expires <=300s; no implicit cross-scope reuse','grammar':'API31_APP_PERS_V1','enumSha256':'343c60effa4ce83ce42296527bae8bd4341a9da942a670a83b1c86a7ef307881','factPlanSha256':sha(B/'reference/fact-plan.json'),'collectorSha256':sha(B/'tools/fact_collector.py'),'services':'no default approved services; exact per-snapshot reviewed entries only','factsScope':'future independent scope with original Native gate, same shared LIVE claim; not an eighth seven-role child'}
put(B/'reference/exact-seven-role-plan.json',json.dumps(plan7,indent=2)+'\n');ph=sha(B/'reference/exact-seven-role-plan.json')
def common(s):return s.replace('d1android02-compat03-schema-parity01','d1android02-global-idle-contract03-fix').replace('D1_COMPAT03_SCHEMA_PARITY01_REVIEW_EVIDENCE','D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE')
r=common((OLD/'tools/production_runner.py').read_text())
r=change(r,"fixtureScenario routeBackend'.split()","fixtureScenario routeBackend globalIdleQualification'.split()")
r=change(r,"'tools/admission_checks.ps1')","'tools/admission_checks.ps1','tools/fact_collector.py','reference/fact-plan.json','selfchecks/fact_fixture.py')")
r=change(r,"  if p['planId'] in self.plan['forbiddenOldPlanIds']", "  q=p['globalIdleQualification']\n  if type(q) is not dict or len(encode(q))>16384 or q.get('targetScope')!=p['scope'] or q.get('targetRunId')!=p['runId'] or q.get('mode')!=self.kind or q.get('fixtureOnly') is not self.fixture or q.get('targetSourceSealSha256')!=p['sourceSeal']['sha256'] or q.get('targetPlanSha256')!=p['sources']['reference/exact-seven-role-plan.json'] or q.get('reviewEvidenceSha256')!=p['review']['sha256']:raise ValueError('GLOBAL_IDLE_PRIOR_QUALIFICATION_BINDING')\n  if p['planId'] in self.plan['forbiddenOldPlanIds']")
r=change(r,"  p['routeBackend']=BACKEND", "  p['routeBackend']=BACKEND\n  p['globalIdleQualification']=self.permit['globalIdleQualification']")
r=change(r,"'OWNER_END_TAIL','NO_SDK_ABORT')","'OWNER_END_TAIL','NO_SDK_ABORT','PRESTART_KNOWN_REJECT')")
r=change(r,"fixtureProofSeconds=1)","fixtureProofSeconds=2)")
r=change(r,"  if self.fixture and self.permit['fixtureScenario']=='OWNER_END_TAIL':","  if self.fixture and self.permit['fixtureScenario']=='PRESTART_KNOWN_REJECT':p.update(fixtureFault='PRESTART_KNOWN_REJECT')\n  if self.fixture and self.permit['fixtureScenario']=='OWNER_END_TAIL':")
r=runner_patch(r)
put(B/'tools/production_runner.py',r);rh=sha(B/'tools/production_runner.py')
f=common((OLD/'selfchecks/capture_fixture.py').read_text())
f=change(f,"    curProcState=2 cached=false\\n    mInstr=null", "    user #0 uid=10012\\n    packageList={com.zui.launcher}\\n    curProcState=2 cached=false\\n    mInstr=null")
f=change(f,"ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)\\n  mResumedActivity", "ACTIVITY MANAGER ACTIVITIES (dumpsys activity activities)\\nDisplay #0 (activities from top to bottom):\\n  mResumedActivity")
f=change(f,"com.zui.launcher/.Launcher t1}\\nANDROID02_GLOBAL_COMPLETE", "com.zui.launcher/.Launcher t1}\\n  mFocusedApp=ActivityRecord{abc u0 com.zui.launcher/.Launcher t1}\\nANDROID02_GLOBAL_COMPLETE")
f=f.replace('\\nANDROID02_GLOBAL_COMPLETE', '\\n'+home_detail().replace('\n','\\n')+'ANDROID02_GLOBAL_COMPLETE')
f=f.replace('LOCAL_FAKE_FINGERPRINT_NOT_DEVICE','SYNTHETIC_FIXTURE_FIRMWARE_API31')
put(B/'selfchecks/capture_fixture.py',f);fh=sha(B/'selfchecks/capture_fixture.py')
a=common((OLD/'tools/admission_checks.ps1').read_text())
a=change(a,"'fixtureScenario','routeBackend')", "'fixtureScenario','routeBackend','globalIdleQualification')")
a=change(a,"'tools/admission_checks.ps1')", "'tools/admission_checks.ps1','tools/fact_collector.py','reference/fact-plan.json','selfchecks/fact_fixture.py')")
a=change(a," $now=[DateTimeOffset]::UtcNow;", " if(($policy.globalIdleQualification|ConvertTo-Json -Depth 16 -Compress) -cne ($permit.globalIdleQualification|ConvertTo-Json -Depth 16 -Compress)){throw 'GLOBAL_IDLE_APPROVED_QUALIFICATION_CHANGED'}\n $now=[DateTimeOffset]::UtcNow;")
a=a.replace(oldseal['tools/production_runner.py'],rh)
a+="\n$script:GICollectorSha256='"+sha(B/'tools/fact_collector.py')+"'\n$script:GIFactPlanSha256='"+sha(B/'reference/fact-plan.json')+"'\n"+(B/'tools/qualification.ps1.txt').read_text()+'\n'+(B/'tools/semantics.ps1.txt').read_text()
a+='\n'+(B/'tools/prestart.ps1.txt').read_text()
put(B/'tools/admission_checks.ps1',a);ah=sha(B/'tools/admission_checks.ps1')
gf=('tools/entry_gates.py','tools/win32_route.py','selfchecks/route_fixture.py','reference/route-backend-contract.json','selfchecks/route_model.py','tools/admission_checks.ps1','tools/fact_collector.py','reference/fact-plan.json','selfchecks/fact_fixture.py')
put(B/'reference/gate-sources.json',json.dumps({'schema':'ENTRY_GATE_SOURCES_V2','files':[{'path':p,'sha256':sha(B/p)} for p in gf]},indent=2)+'\n');gh=sha(B/'reference/gate-sources.json')
owner=common((OLD/'tools/outer_owner.py').read_text()).replace(oldseal['tools/production_runner.py'],rh).replace(oldseal['reference/gate-sources.json'],gh)
owner=owner_patch(owner)
put(B/'tools/outer_owner.py',owner);oh=sha(B/'tools/outer_owner.py')
s=common((OLD/'tools/capture_android02.ps1').read_text())
for old,new in ((oldseal['tools/production_runner.py'],rh),(oldseal['tools/outer_owner.py'],oh),(oldseal['tools/admission_checks.ps1'],ah),(oldseal['reference/gate-sources.json'],gh),(oldseal['reference/exact-seven-role-plan.json'],ph),(oldseal['selfchecks/capture_fixture.py'],fh)):s=s.replace(old,new)
s=change(s,"  if(-not $IsFixture -and $lines[3]","  if($lines[3] -cne $policy.globalIdleQualification.fingerprint){return 'FACT_IDENTITY_FIRMWARE_DISAGREEMENT'}\n  if(-not $IsFixture -and $lines[3]")
start=s.index(" if($Id -ceq 'global_idle'){");end=s.index(" if($Id -cin @('app_absence'",start)
s=s[:start]+''' if($Id -ceq 'global_idle'){
  # Invoked only after original WaitForExit, EOF/saved readers and input return;
  # current controller return remains the unchanged outer owner's obligation.
  $ctx=[pscustomobject]@{scope=$policy.scope;runId=$policy.runId;mode=if($IsFixture){'OFFLINE_FIXTURE'}else{'LIVE'};rawSha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($raw)).ToLowerInvariant();rawBytes=$raw.Length;captureBodyReturned=($c.waitReturned -and (ReadersReturned) -and (InputReturned) -and $null -eq $c.firstFailure);sourceSealSha256=$policy.toolCandidateSeal.sha256;planSha256=$policy.planSha256;reviewEvidenceSha256=$policy.independentReview.sha256;nowUtc=[DateTimeOffset]::UtcNow.ToString('o')}
  $decision=Get-GlobalIdleDecision $text $policy.globalIdleQualification $ctx
  if($decision.qualified -and $decision.status -ceq 'PASS'){return 'PASS'};return $decision.reason
 }
''' +s[end:]
# Predecessor semantic replay runs in the next controller, whose current c is
# not started. Its predecessor's qualified proof was already read/validated.
old="  $ctx=[pscustomobject]@{scope="
s=change(s,old,"  $bodyReturnedForSemantic=if($request.id -ceq 'global_idle'){$c.waitReturned -and (ReadersReturned) -and (InputReturned) -and $null -eq $c.firstFailure}else{$true}\n"+old)
s=s.replace('captureBodyReturned=($c.waitReturned -and (ReadersReturned) -and (InputReturned) -and $null -eq $c.firstFailure)','captureBodyReturned=[bool]$bodyReturnedForSemantic')
from patch_prestart import patch
s=patch(s)
put(B/'tools/capture_android02.ps1',s)
p=json.loads((OLD/'release/capture-policy.json').read_text());p.update(entrySha256=sha(B/'tools/capture_android02.ps1'),outerOwnerSha256=oh,gateSourcesSha256=gh,runnerSourceSha256=rh,planSha256=ph,globalIdleQualification=None)
put(B/'release/capture-policy.json',json.dumps(p,indent=2)+'\n')
# Parse tuple without importing runtime/starting a gate.
import ast
t=ast.parse(r);sources=next(ast.literal_eval(x.value) for x in t.body if isinstance(x,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='SOURCE_FILES' for n in x.targets))
put(B/'reference/runner-source-seal.json',json.dumps({'schema':'PRODUCTION_RUNNER_SOURCE_SEAL_V1','sources':{p:sha(B/p) for p in sources}},indent=2)+'\n')
print(json.dumps({'sourceCount':len(sources),'gateCount':len(gf),'sourceSeal':sha(B/'reference/runner-source-seal.json'),'entry':p['entrySha256'],'plan':ph,'mode':p['mode']}))
