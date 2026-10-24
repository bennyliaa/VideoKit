"""Verify fixed candidate; derive independent driver only. Never run coder worker."""
from pathlib import Path
import ast,json,hashlib,zipfile
R=Path(__file__).resolve().parent;C=R.parents[1]/'coder/d1android02-facts-v2-qualification07';B=C/'rev2';O=R.parent/'D1_FACTS_V2_QUALIFICATION04_INDEPENDENT_B_EVIDENCE';A=R.parent/'D1_FACTS_V2_QUALIFICATION05_PHASE_A_EVIDENCE'
sha=lambda b:hashlib.sha256(b).hexdigest()
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def save(n,d):put(R/n,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
m=(C/'full-manifest.json').read_bytes();assert sha(m)=='e9a275eba60347706fee8ed622350368b1fb0a87f6100c361297952f5a204e7f';rows=json.loads(m)['files'];assert len(rows)==567 and sum(x['bytes'] for x in rows)==8138358
with zipfile.ZipFile(C/'QUALIFICATION07-frozen.zip') as z:
 assert sha((C/'QUALIFICATION07-frozen.zip').read_bytes())=='bd3d716c2e8a5cd928f52ef4e90c290c0af32b8b1226ce04cbdef8d11ae78def'
 assert len(z.namelist())==len(set(z.namelist()))==568
 for x in rows:
  b=(C/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'] and b==z.read(x['path'])
assert sha((C/'DELIVERY.md').read_bytes())=='a0ac936116a6cd01f148aad5aaeea75a7236cda1442f287fa71a126e9c4247af'
for n,h in [('reference/runner-source-seal.json','0db36468464dcfb92c2da87de8d6bff678b09af173bb21b41ed9e3d4d58157de'),('reference/gate-sources.json','ba8fbd645e4c8403525c111ba2943cb81f3fbf6fbfc11a9f6d7c7c5a49026f81'),('tools/runtime_binding.py','47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982'),('reference/current-runtime-identity.json','2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48')]:assert sha((B/n).read_bytes())==h
save('candidate-before.json',dict(files=567,bytes=8138358,members=568,bad=0,manifestSha256=sha(m)))
for n in ['parent_controller.py','parent_profile.py','parent_observer.py','parent_identity.py','parent_policy.py','self_io.py']:
 put(R/n,(O/n).read_bytes())
for n in ['context_child.py','host_context.py','owned_child.ps1']:put(R/'driver'/n,(B/'driver'/n).read_bytes())
for n in ['independent_budget.ps1','independent_driver.py']:
 s=(A/n).read_text(encoding='utf-8-sig').replace('INDEPENDENT_Q05_BUDGET_RESULT_V1','INDEPENDENT_Q07_BUDGET_RESULT_V1');put(R/n,s.encode())
reasonDoc=json.loads((A/'helper-fields-and-reasons.json').read_bytes());reasonRows=next(v for v in reasonDoc.values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'expectedReason' in v[0]);save('helper-reasons.json',{x['id']:x['expectedReason'] for x in reasonRows})
s=(B/'selfchecks/call_plan07.py').read_text();s=s.replace("H=Path(__file__).resolve().parents[1]","R=Path(__file__).resolve().parent;H=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2'")
s=s.replace("str(H/'selfchecks/offline_reviewer.py')","str(R/'offline_reviewer.py')")
s=s.replace(" return [PS,'-NoProfile','-NonInteractive','-File',str(H/'selfchecks'/script),'-InputFile',str(w/(label+'-input.json')),'-OutputFile',str(w/(label+'-result.json'))]"," if label=='budget':\n  from independent_driver import build_budget_spec\n  return list(build_budget_spec(R,w).argv)\n return [PS,'-NoProfile','-NonInteractive','-File',str(H/'selfchecks'/script),'-InputFile',str(w/(label+'-input.json')),'-OutputFile',str(w/(label+'-result.json'))]")
put(R/'call_plan.py',s.encode())
s=(B/'driver/driver_guard07.py').read_text();s=s.replace("H=Path(__file__).resolve().parents[1];sys.path.insert(0,str(H/'selfchecks'))","R=Path(__file__).resolve().parent;H=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2';sys.path.insert(0,str(R))").replace('from call_plan07 import','from call_plan import').replace("H/'reference/plan07.json'","R/'plan.json'").replace("H/'reference/profile07.json'","R/'profile.json'").replace("START=PLAN['batchStart']","START=time.monotonic()")
s=s.replace("H/'driver/context_child.py'","R/'driver/context_child.py'").replace("H/'driver/owned_child.ps1'","R/'driver/owned_child.ps1'")
s=s.replace("  return key","  if source.is_relative_to(R) and not source.is_relative_to(W):\n   pin=next(x['sha256'] for x in json.loads((R/'tester-profile.json').read_bytes()) if x['path']==source.relative_to(R).as_posix())\n   if digest(source)!=pin:raise ValueError('TESTER_FIXED_SOURCE')\n  return key")
put(R/'guard.py',s.encode())
s=(B/'selfchecks/offline_reviewer.py').read_text();s=s.replace("B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'tools'))","R=Path(__file__).resolve().parent;B=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2';sys.path.insert(0,str(B/'tools'))").replace("B/'selfchecks/work'","R/'fixtures'");put(R/'offline_reviewer.py',s.encode())
s=(B/'worker07.py').read_text();s=s.replace("H=Path(__file__).resolve().parent;sys.path[:0]=[str(H),str(H/'tools'),str(H/'selfchecks')]","R=Path(__file__).resolve().parent;H=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2';sys.path[:0]=[str(R),str(R/'driver'),str(H/'tools'),str(H/'selfchecks')]").replace('from call_plan07 import','from call_plan import').replace('from driver_guard07 import Guard','from guard import Guard').replace("H/'reference/plan07.json'","R/'plan.json'").replace("H/'reference/profile07.json'","R/'profile.json'").replace("START=PLAN['batchStart']","START=time.monotonic()").replace("sys.path.insert(0,str(H/'driver'))","sys.path.insert(0,str(R))").replace("H/'driver/context_child.py'","R/'driver/context_child.py'").replace("H/'driver/owned_child.ps1'","R/'driver/owned_child.ps1'").replace("save(H/'evidence","save(R/'evidence")
s=s.replace("planned=load(H/'reference/fact-source-plan07.json')['rows']","planned=load(R/'fact-source-plan.json')['rows']")
s=s.replace("artifactRoot=str(H/'selfchecks')","artifactRoot=str(R)")
# Persist native output before independent exact result validation; never let
# a missing result file obscure original exit/streams.
s=s.replace("from write_guard import install as install_writes,allowed,EVENTS","from write_guard import install as install_writes,allowed,EVENTS\nfrom independent_driver import inspect_result_file,build_budget_spec")
start=s.index("assert (W/'budget-result.json').is_file()");end=s.index('\ndef regression():',start)
s=s[:start]+"result=inspect_result_file(build_budget_spec(R,W),BUDGET_CASES,load(R/'helper-reasons.json'),lambda p,cap:Path(p).read_bytes());save(W/'budget-independent-inspection.json',result);assert c.exit_code==0 and not c.buffers[1] and result['status']=='RESULT_CASES_MATCHED',result;return result\n"+s[end:]
s=s.replace("save(root/'return.json',dict(returned=c.returned,exitCode=c.exit_code,counts=c.counts,facts=c.facts,disposition=ans,failure=c.failure))","save(root/'return.json',dict(returned=c.returned,exitCode=c.exit_code,counts=c.counts,facts=c.facts,disposition=ans,failure=c.failure));(root/'stdout.bin').write_bytes(bytes(c.buffers[0]));(root/'stderr.bin').write_bytes(bytes(c.buffers[1]))")
# Parent original handle admission applies to this new independent worker only.
needle='for x in PROFILE:assert'
at=s.index(needle);s=s[:at]+"from parent_controller import order\nfrom parent_identity import own_identity\no=order(sys.argv[1]);ident=own_identity();ident['nonce']=o['nonce'];save(R/'worker-self.json',ident)\nuntil=time.monotonic()+8\nwhile not (R/'worker-admit.json').exists():\n if time.monotonic()>until:raise ValueError('NO_ORIGINAL_ADMISSION')\n time.sleep(.025)\nassert load(R/'worker-admit.json')==dict(orderSha256=sys.argv[1],selfSha256=digest(R/'worker-self.json'))\n"+s[at:]
put(R/'worker.py',s.encode())
s=(O/'write_guard.py').read_text();put(R/'write_guard.py',s.encode())
save('harness-provenance.json',dict(candidateRoot=str(B),derivedSequence=str(B/'worker07.py'),developerWorkerExecuted=False,independentScopeAndInputs=True,helperSource=str(A/'independent_budget.ps1'),helperSchemaBound='INDEPENDENT_Q07_BUDGET_RESULT_V1',originalParentObserver=str(O),oracle='own case-reasons, exact result inspection, final pins/schema/event/receipt/fee audit',candidateModified=False))
for f in R.rglob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
print(json.dumps(dict(candidateFiles=567,zipMembers=568,bad=0,driverPrepared=True,productResources=0)))
