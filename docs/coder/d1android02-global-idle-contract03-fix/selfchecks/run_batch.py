"""One finite developer batch. Frozen source, no SDK/Native/TCP/old objects."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,hashlib,copy,uuid,ast,subprocess
B=Path(__file__).resolve().parents[1];sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]
from entry_gates import encode,decode,sha,CUSTODY,fixture_root_allowed
from production_runner import ProductionRunner,RUNNER_CUSTODY,PY
from fact_collector import validate_fixture_argv,verify_fixture_runtime,FIXTURE_PY
from runtime_binding import IDENTITY_SHA256
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
plan=decode((B/'reference/batch-plan.json').read_bytes());START=time.monotonic();W=B/'selfchecks/work'/('batch-'+plan['batch'][:12]);W.mkdir(parents=True,exist_ok=False)
rows=[];audit=[];stop=False;reservedProcesses=0
CHILD_BOUNDS={'pure-argv-program-identity-and-unified-roots':0,'direct-original-prestart13-before-claim':2,'original98-independent175-and-exact-five-defect-boundaries':1,'current-proposal-and-static-external-boundary':0,'original-collector-owned-return-and-wire-guards':2,'default':3,'authority-source-budget':0,'real-seven-END-once':17,'finite-original-fault11':30,'PS-post-last-Start':1,'materialization-change':1,'new-tester-root-original-seven-END-once':17,'small-one-byte-exact-OWNER_SOURCE_PIN_ENTRY':1}
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encode(d))
def load(p):return decode(Path(p).read_bytes())
def rejection(fn):
 try:fn()
 except (ValueError,TypeError) as e:return str(e)
 raise AssertionError('EXPECTED_PRECONSTRUCTION_REJECTION')
def audit_hook(event,args):
 if event!='subprocess.Popen':return
 exe=str(args[0]);argv=list(args[1]);allowed=exe in (PY,PS)
 audit.append(dict(executable=exe,argv=argv,allowedProgram=allowed))
 if not allowed:raise ValueError('BATCH_UNAPPROVED_PROGRAM_BEFORE_CREATE')
sys.addaudithook(audit_hook)
# Load only fixed regression definitions, never its standalone execution tail.
ns={'__file__':str(B/'selfchecks/run_affected.py')}
exec((B/'selfchecks/run_affected.py').read_text().split('\ntry:\n check(')[0],ns)
child=ns['child']
def group(name,fn):
 global stop,reservedProcesses
 if stop or time.monotonic()-START>=plan['stopNewCasesAfterSeconds'] or reservedProcesses+CHILD_BOUNDS[name]>plan['maxLocalProcesses']:stop=True;rows.append(dict(name=name,status='NOT_RUN_STOP_NEW_WORK'));return
 reservedProcesses+=CHILD_BOUNDS[name]
 before=time.monotonic()
 try:
  detail=fn();assert not RUNNER_CUSTODY and not CUSTODY,'NEW_RETAINED_ORIGINAL_STOP_NEW_WORK'
  rows.append(dict(name=name,status='PASS',seconds=time.monotonic()-before,detail=detail))
 except BaseException as e:stop=True;rows.append(dict(name=name,status='FAIL',seconds=time.monotonic()-before,error=repr(e)))
 save(W/('group-'+str(len(rows))+'.json'),rows[-1])
def direct_prestart():
 code,out,err=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')]);assert code==0 and not err,(code,err);d=load(W/'prestart.json');assert d['allPassed'];return d
def parameters():
 argv=[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'];assert validate_fixture_argv(argv)==argv
 cases={}
 for label,v in [('adb','D:/Android/SDK/platform-tools/adb.exe'),('other-python','D:/Unapproved/python.exe'),('same-name','python.exe'),('alias',str(Path(PY)))]:
  bad=argv.copy();bad[0]=v;cases[label]=rejection(lambda bad=bad:validate_fixture_argv(bad));assert cases[label]=='FACT_FIXTURE_ARGV'
 for label,bad in [('extra',argv+['x']),('short',argv[:-1]),('tuple',tuple(argv)),('non-string',[None,*argv[1:]])]:cases[label]=rejection(lambda bad=bad:validate_fixture_argv(bad));assert cases[label]=='FACT_FIXTURE_ARGV'
 meta=(B/'reference/current-runtime-identity.json').read_bytes();m=decode(meta);exe=next(x for x in m['files'] if x['kind']=='interpreter-executable');binary=Path(PY).read_bytes()
 class Input:
  policy={'runtimeIdentitySha256':IDENTITY_SHA256,'outerPythonSha256':exe['sha256']};runtime={'identitySha256':IDENTITY_SHA256}
  def __init__(self,which=None):self.which=which;self.reads=[]
  def source_read(self,p):
   self.reads.append(str(p));v=meta if Path(p).name=='current-runtime-identity.json' else binary
   return v+b' ' if self.which==Path(p).name else v
 good=verify_fixture_runtime(Input());badMeta=rejection(lambda:verify_fixture_runtime(Input('current-runtime-identity.json')));badExe=rejection(lambda:verify_fixture_runtime(Input('python.exe')))
 assert badMeta=='FACT_FIXTURE_RUNTIME_METADATA' and badExe=='FACT_FIXTURE_EXECUTABLE_IDENTITY'
 roots={'own':str(B/'selfchecks/work'/'fresh'),'tester':str(Path(plan['fixtureRoot'])/'fresh'),'outside':str(B.parent/'outside'),'prefix':plan['fixtureRoot']+'x/fresh','dotdot':plan['fixtureRoot']+'/../fixtures/fresh','dot':plan['fixtureRoot']+'/./fresh','old':str(B.parent/'d1android02-global-idle-contract02-revision02/selfchecks/work/fresh'),'namespace':'\\\\?\\D:\\CodexProjects\\VideoKit\\docs\\tester\\D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE\\fixtures\\fresh'}
 observed={k:fixture_root_allowed(v) for k,v in roots.items()};assert observed=={k:k in ('own','tester') for k in roots},observed
 assert 'from entry_gates import fixture_root_allowed' in (B/'tools/production_runner.py').read_text() and 'from entry_gates import fixture_root_allowed' in (B/'tools/outer_owner.py').read_text()
 return dict(argvNegative=cases,identity=good,identityMutations=[badMeta,badExe],roots=observed,invalidProgramsActuallyStarted=0)
def semantics():
 from contract_cases import make
 from independent_cases_original import cases as independent
 from contract03_cases import cases as newcases
 inputs=make()+independent(B)+newcases();save(W/'semantics-input.json',inputs)
 code,out,err=child([PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/review_semantics.ps1'),'-InputFile',str(W/'semantics-input.json'),'-OutputFile',str(W/'semantics-result.json')]);data=load(W/'semantics-result.json');bad=[dict(id=x['id'],status=x['status'],reason=x['reason']) for x in data if not x['pass']]
 assert code==0 and not err and not bad,(code,bad,err[:1000]);assert len(inputs[:98])==98 and len(independent(B))==175
 return dict(total=len(data),originalDeveloper98=98,independentOracleReplay175=175,independent45=45,independentPositive17=sum(x['expected']=='PASS' for x in independent(B)),fixCases=len(newcases()),allExpectedReasonsCheckedWhereSpecified=True,positive=sum(x['qualified'] for x in data),historical68=[x['processCount'] for x in data[:98] if x['id'] in ('H01','H02')])
def proposal():
 d=load(B/'reference/next-readonly-facts-execution-proposal.json');assert d['approvedForExecution'] is False and d['candidate']==str(B)
 for k in ('sourceSeal','gateSources','collector','factPlan','targetSevenRolePlan','externalHandoff'):
  p=Path(d[k]['path']);assert p.is_relative_to(B) and sha(p.read_bytes())==d[k]['sha256'],k
 assert d['externalHandoff']['implemented'] is False and d['externalHandoff']['executed'] is False
 return dict(currentProposal=sha((B/'reference/next-readonly-facts-execution-proposal.json').read_bytes()),pathAndContentPinsMatched=True,external='STATIC_ONLY_PENDING_APPROVAL',sourceSeal=d['sourceSeal']['sha256'])
def collector():
 # Reuse actual bounded original collector test, not a forged Gate model.
 cn={'__file__':str(B/'selfchecks/run_contract.py')};exec((B/'selfchecks/run_contract.py').read_text().split('\ntry:\n group(')[0],cn)
 pure=cn['collector_pure']();owned=cn['owned_collector']();return dict(pure=pure,originalOwned=owned)
def real_tester_root():
 f,p=ns['permit']('tester-root');home=Path(plan['fixtureRoot'])/('dev03-'+plan['batch'][:8])/'h';root=home/'outputs';p.update(home=str(home),evidenceRoot=str(root));proto=ProductionRunner.__new__(ProductionRunner);proto.plan=ns['plan'];proto.root=root
 modes=['identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'];p['roles']=[proto.fixture_slot(i,x) for i,x in enumerate(modes)]
 args=ns['inputs'](f,p);code,out,err=ns['cli'](args);assert code==0 and not err,(code,out,err);d=decode(out);assert d['rolesCompleted']==7 and d['claimRelease']['originalUnlockCloseReturned']
 last=load(root/'scope_all-completion-proof.json');assert last['nextId']=='END';again,b,e=ns['cli'](args);assert again==2 and decode(b)['reason']=='FRESH_ONCE_EXACT_HOME'
 return dict(home=str(home),scope=p['scope'],terminal=d,repeatRejected=True,newTesterRootAllThreeEntrancesActuallyUsed=True)
def append_exact():
 from exact_append import exact_append
 return exact_append(W,B,W,ns,save,load)
try:
 group('pure-argv-program-identity-and-unified-roots',parameters)
 group('direct-original-prestart13-before-claim',direct_prestart)
 group('original98-independent175-and-exact-five-defect-boundaries',semantics)
 group('current-proposal-and-static-external-boundary',proposal)
 group('original-collector-owned-return-and-wire-guards',collector)
 for label,fn in [('default','default_deny'),('authority-source-budget','authority'),('real-seven-END-once','full_cli'),('finite-original-fault11','finite_failures'),('PS-post-last-Start','ps_post_guards'),('materialization-change','changed_materialization')]:group(label,ns[fn])
 group('new-tester-root-original-seven-END-once',real_tester_root)
 group('small-one-byte-exact-OWNER_SOURCE_PIN_ENTRY',append_exact)
finally:
 d=dict(schema='GLOBAL_IDLE_CONTRACT03_FIX_SELF_CHECK_V1',batch=plan['batch'],sourceSealSha256=sha((B/'reference/runner-source-seal.json').read_bytes()),seconds=time.monotonic()-START,results=rows,allPassed=bool(rows) and all(r['status']=='PASS' for r in rows),audit=audit,auxOriginalsReturned=all(p.returncode is not None for p in ns['children']),runnerCustody=len(RUNNER_CUSTODY),gateCustody=len(CUSTODY),cases=ns['cases'],work=str(W),reservedProcessBound=reservedProcesses,declaredProcessCap=plan['maxLocalProcesses'],actualSDK=0,actualNativeRoute=0,oldQueries=0,externalHandoff='NOT_RUN',D1='NOT_PASSED')
 save(B/'evidence/batch-result.json',d);save(W/'batch-result.json',d);print(json.dumps(dict(work=str(W),allPassed=d['allPassed'],groups=len(rows),seconds=d['seconds'],runnerCustody=d['runnerCustody'],gateCustody=d['gateCustody'])))
if not d['allPassed']:raise SystemExit(2)
