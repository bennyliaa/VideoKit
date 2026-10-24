"""Complete pure preflight before the once-only actual batch."""
from pathlib import Path
import sys,json,hashlib,ast,re,copy,subprocess
H=Path(__file__).resolve().parent;sys.path[:0]=[str(H/'tools'),str(H/'selfchecks'),str(H/'driver')]
def load(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
def check(n,v,d=None):rows.append(dict(id=n,pass_=bool(v),detail=d));assert v,n
src=load(H/'reference/runner-source-seal.json')['sources'];gate=load(H/'reference/gate-sources.json')['files'];profile=load(H/'reference/profile07.json');plan=load(H/'reference/plan07.json')
check('30-original-source-pins',len(src)==30 and all(sha(H/k)==v for k,v in src.items()))
check('22-gate-pins',len(gate)==22 and all(sha(H/e['path'])==e['sha256'] for e in gate))
check('all-profile-pins',all(sha(H/e['path'])==e['sha256'] for e in profile),len(profile))
check('all-input-pins',all(sha(p)==s for p,s in plan['inputPins'].items()))
helper=H/'tools/runtime_binding.py';check('original-fixed-runtime-bytes',sha(helper)=='47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982' and helper.stat().st_size==2056 and helper.read_bytes().count(b'\r\n')==20)
from runtime_binding import require_runtime
rt=require_runtime(load(H/'release/capture-policy.json'),'PURE_PREFLIGHT05');check('exact-runtime-14-dependencies',rt['filesChecked']==14,rt)
a=(H/'tools/admission_checks.ps1').read_text();c=(H/'tools/capture_android02.ps1').read_text();r=(H/'tools/production_runner.py').read_text();o=(H/'tools/outer_owner.py').read_text()
for n,rel,text in [('runner-owner','tools/production_runner.py',o),('runner-PS','tools/production_runner.py',a),('owner-entry','tools/outer_owner.py',c),('admission-entry','tools/admission_checks.ps1',c),('gate-owner','reference/gate-sources.json',o),('gate-entry','reference/gate-sources.json',c)]:check(n,sha(H/rel) in text)
check('PS-exact30-source-set',set(re.findall("'([^']+)'",re.search(r' \$srcKeys=@\(([^\n]+)\)',a).group(1)))==set(src))
check('capacity-before-once-resource',r.index('self.control_admission=admit')<r.index(' def prepare_home') and r.index('self.creation_attempted=True')>r.index('self.control_admission=admit'))
check('writer-identity-before-original-close',c.index('$r.originalRef=@{')<c.index('$r.closeEntered=$true;try{$r.stream.Close()'))
check('receiver-before-merge',o.index('self.runner.read_receipt')<o.index('self.source_budget.merge'))
check('expected-reference-from-original-writer','receiptRef=OriginalReceiptReference' in c and "co.get('receiptRef')" in o)
check('source-reserve-before-Popen',o.index('self.source_budget.reserve')<o.index('subprocess.Popen(argv'))
check('merge-after-original-returns',o.index('self.source_budget.merge')>o.index("if returned['error'] or not returned['handleClose']"))
from entry_gates import fixture_root_allowed
future='D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION07_INDEPENDENT_B_EVIDENCE/fixtures/new/home'
check('own-and-future-exact-roots',fixture_root_allowed(H/'selfchecks/work/new/home') and fixture_root_allowed(future) and not fixture_root_allowed(future.replace('QUALIFICATION07','QUALIFICATION04')) and not fixture_root_allowed(future.replace('/fixtures/','/fixturesx/')))
from production_runner import ProductionRunner
fake=ProductionRunner.__new__(ProductionRunner);fake.fixture=False
for fixture,prefix in [(False,2),(True,True),(True,2.0),(True,'2')]:
 fake.fixture=fixture
 try:fake.run(prefix);why='ACCEPT'
 except ValueError as e:why=str(e)
 check('prefix-reject-before-resource:'+repr((fixture,prefix)),why=='OFFLINE_IDENTITY_GLOBAL_PREFIX_ONLY' and not hasattr(fake,'consumed'))
from driver_guard07 import Guard
from call_plan07 import facts_argv,review_argv,aux_argv,BUDGET_CASES
g=Guard();kw=dict(executable=None,cwd=None,env=None,shell=False,close_fds=True,stdin=-3,stdout=-1,stderr=-1)
calls=[('facts',facts_argv(plan))]+[('review-'+k,review_argv(plan,k)) for k in plan['targets']]+[(k,aux_argv(plan,k)) for k in ('budget','v1')]
for name,argv in calls:check('actual-call-factory:'+name,g.check(argv,kw)==name)
for name,mut in [('wrong-source',lambda a,k:a.__setitem__(4,str(H/'selfchecks/review_semantics.ps1'))),('wrong-executable',lambda a,k:k.__setitem__('executable','wrong.exe')),('wrong-cwd',lambda a,k:k.__setitem__('cwd',str(H))),('wrong-env',lambda a,k:k.__setitem__('env',{})),('extra-argument',lambda a,k:a.append('EXTRA'))]:
 av=aux_argv(plan,'budget');k=copy.deepcopy(kw);mut(av,k)
 try:g.check(av,k);why='ACCEPT'
 except ValueError as e:why=str(e)
 check('pre-Capture-reject:'+name,why!='ACCEPT',why)
check('preflight-no-Popen-constructor',len(g.calls)==0)
check('helper18-correct-result-path',len(BUDGET_CASES)==18 and '$script:complete=$true' in (H/'selfchecks/budget_models.ps1').read_text())
check('capacity-pure-original-function',load(H/'evidence/control-envelope-pure07.json')['allPassed'])
check('source-budget-pure-model',load(H/'evidence/pure-budget-arithmetic.json')['allPassed'])
ps=load(H/'evidence/ps-parse07.json');check('PowerShell-parse-and-bools',ps['allPassed'],ps)
from fact_preauth import check_complete_source_plan,USED
source_plan=load(H/'reference/fact-source-plan07.json');check('complete-read-plan-64',source_plan['sourceReads']==64 and len(source_plan['rows'])==64,source_plan)
from fact_preauth import complete_source_plan,FACT_RUNTIME_FILES06
size_map={x['path']:Path(x['path']).stat().st_size for x in source_plan['rows']}
policy0=load(Path(plan['facts']['root'])/'policy.json');gf=load(H/'reference/gate-sources.json')['files']
complete=complete_source_plan(policy0,gf,FACT_RUNTIME_FILES06,size_map)
check('COMPLETE-explicit-obligations61',complete['sourceReads']==61,complete)
livep=copy.deepcopy(policy0);livep['mode']='PRODUCTION';livep['gateAuthorization']={'path':str(H/'selfchecks/work/pure-live/home/release/gate-local-authorization.json'),'sha256':'b'*64};size_map[livep['gateAuthorization']['path']]=600;size_map[str(Path('D:/Android/SDK/platform-tools/adb.exe'))]=8273560
live=complete_source_plan(livep,gf,FACT_RUNTIME_FILES06,size_map)
check('LIVE-explicit-obligations58-model-only',live['sourceReads']==58,dict(plan=live,SDKRead=0))
check('unchanged-64-256MiB-caps',source_plan['capReads']==64 and source_plan['capBytes']==268435456 and check_complete_source_plan(source_plan))
for name,field in [('65th-read','reads'),('byte-overflow','bytes')]:
 bad=copy.deepcopy(source_plan)
 if field=='reads':bad['rows'].append(dict(bad['rows'][-1]));bad['sourceReads']+=1;bad['sourceBytes']+=bad['rows'][-1]['chargedBytes']
 else:bad['rows'][0]['chargedBytes']+=268435457;bad['sourceBytes']+=268435457
 try:check_complete_source_plan(bad);reason='ACCEPT'
 except ValueError as e:reason=str(e)
 check('before-USED-resource-reject:'+name,reason=='FACT_COMPLETE_SOURCE_BUDGET_BEFORE_USED' and len(USED)==0,reason)
from facts_entry import validate_fixture_call
expected=[str(x) for x in [PY,'-I','-X','utf8','-B',H/'selfchecks/fact_fixture.py','COMPLETE']] if False else ['C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-I','-X','utf8','-B',str(H/'selfchecks/fact_fixture.py'),'COMPLETE']
opts=dict(stdin=-3,stdout=-1,stderr=-1,shell=False)
check('original-fixture-guard-pure-positive',validate_fixture_call(expected,list(expected),(),opts))
for name,argv,kw,ctx in [('wrong-source',expected[:-2]+[str(H/'selfchecks/route_fixture.py'),'COMPLETE'],opts,True),('wrong-context',expected,opts,False),('wrong-options',expected,dict(opts,shell=True),True)]:
 try:validate_fixture_call(expected,argv,(),kw,ctx);reason='ACCEPT'
 except ValueError as e:reason=str(e)
 check('fixture-preconstructor-reject:'+name,reason.endswith('BEFORE_CONSTRUCTOR') and len(USED)==0,reason)
from fact_collector import constructor_failure_state
check('known-preconstructor-is-not-UNKNOWN',constructor_failure_state(False)=='FACT_KNOWN_PRECONSTRUCTOR_REJECT')
check('entered-constructor-is-retained-UNKNOWN',constructor_failure_state(True)=='FACT_START_UNKNOWN')
check('fixed-runtime-shapes-consolidated','CAPACITY_SHAPES06=' in (H/'tools/source_budget.py').read_text() and 'control_admission05' not in r and 'control-message-shapes05' not in r)
check('no-hidden-facts-constructor-checks','prepared=subprocess.Popen.preflight' in (H/'tools/fact_collector.py').read_text() and 'p=prepared(mark_original_constructor_entered)' in (H/'tools/fact_collector.py').read_text())
check('one-closed-batch-graph',plan['totalProcessGraph']==23 and plan['conditionalFailureMaxProcessGraph']==25 and plan['retry']==0 and plan['SDK']==0)
for f in H.rglob('*.py'):
 if 'work' not in f.parts:compile(f.read_text(),str(f),'exec')
check('all-Python-compile',True)
check('full-named-consumers-and-source-fees',load(H/'evidence/pin-and-fee-registry07.json')['allPassed'])
check('schema-full-value-preserved',load(H/'reference/source-schema-consolidation07.json')['completeRawContractEmbedded'])
check('two-revision-budget-declared',plan['sourceReservation']['total']==469762048 and load(H.parent/'batch-declaration07.json')['totalReadReservation']==1006632960)
prefix=re.search(r"\$prefix='([^']+)'",c).group(1)
check('PS-canonical-revision-fixture-prefix',prefix==str(H/'selfchecks/work')+'\\',prefix)
from contract_cases import make
from independent_cases_original import cases
from contract03_cases import cases as extra_cases
check('actual-V1-generator-inputs-before-Capture',len(make()+cases(H)+extra_cases())==346)
out=dict(allPassed=True,checks=rows,sourceSha256=sha(H/'reference/runner-source-seal.json'),gateSha256=sha(H/'reference/gate-sources.json'),profileSha256=sha(H/'reference/profile07.json'),planSha256=sha(H/'reference/plan07.json'),Capture=0,Popen=0,Gate=0,claim=0,once=0)
(H/'evidence/complete-pure-preflight07.json').write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(pureAllPassed=True,checks=len(rows),productResources=0)))
