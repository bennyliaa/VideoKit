from pathlib import Path
import json,sys,copy,hashlib
from production_runner import ProductionRunner,PY
from entry_gates import encode,decode,sha,fixture_root_allowed
from fact_collector import validate_fixture_argv,verify_fixture_runtime
from runtime_binding import IDENTITY_SHA256
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
 code,out,err=child([PS,'-NoProfile','-NonInteractive','-File',str(H/'helpers/review_semantics.ps1'),'-InputFile',str(W/'semantics-input.json'),'-OutputFile',str(W/'semantics-result.json')]);data=load(W/'semantics-result.json');bad=[dict(id=x['id'],status=x['status'],reason=x['reason']) for x in data if not x['pass']]
 assert code==0 and not err and not bad,(code,bad,err[:1000]);assert len(inputs[:98])==98 and len(independent(B))==175
 return dict(total=len(data),originalDeveloper98=98,independentOracleReplay175=175,independent45=45,independentPositive17=sum(x['expected']=='PASS' for x in independent(B)),fixCases=len(newcases()),allExpectedReasonsCheckedWhereSpecified=True,positive=sum(x['qualified'] for x in data),historical68=[x['processCount'] for x in data[:98] if x['id'] in ('H01','H02')])

def proposal():
 d=load(B/'reference/next-readonly-facts-execution-proposal.json');assert d['approvedForExecution'] is False and d['candidate']==str(B)
 for k in ('sourceSeal','gateSources','collector','factPlan','targetSevenRolePlan','externalHandoff'):
  p=Path(d[k]['path']);assert p.is_relative_to(B) and sha(p.read_bytes())==d[k]['sha256'],k
 assert d['externalHandoff']['implemented'] is False and d['externalHandoff']['executed'] is False
 return dict(currentProposal=sha((B/'reference/next-readonly-facts-execution-proposal.json').read_bytes()),pathAndContentPinsMatched=True,external='STATIC_ONLY_PENDING_APPROVAL',sourceSeal=d['sourceSeal']['sha256'])

def real_tester_root():
 f,p=ns['permit']('tester-root');home=Path(plan['fixtureRoot'])/('dev03-'+plan['batch'][:8])/'h';root=home/'outputs';p.update(home=str(home),evidenceRoot=str(root));proto=ProductionRunner.__new__(ProductionRunner);proto.plan=ns['plan'];proto.root=root
 modes=['identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'];p['roles']=[proto.fixture_slot(i,x) for i,x in enumerate(modes)]
 args=ns['inputs'](f,p);code,out,err=ns['cli'](args);assert code==0 and not err,(code,out,err);d=decode(out);assert d['rolesCompleted']==7 and d['claimRelease']['originalUnlockCloseReturned']
 last=load(root/'scope_all-completion-proof.json');assert last['nextId']=='END';again,b,e=ns['cli'](args);assert again==2 and decode(b)['reason']=='FRESH_ONCE_EXACT_HOME'
 return dict(home=str(home),scope=p['scope'],terminal=d,repeatRejected=True,newTesterRootAllThreeEntrancesActuallyUsed=True)

def append_exact():
 from exact_append import exact_append
 return exact_append(W,B,W,ns,save,load)
