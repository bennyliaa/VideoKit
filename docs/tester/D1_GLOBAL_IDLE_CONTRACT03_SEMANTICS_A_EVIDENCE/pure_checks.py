"""Exact selected production guards; no collector/Gate instances or DLL calls."""
from pathlib import Path
import ast,sys,hashlib,json,struct,copy
def run(B,R,read,save):
 def sha(b):return hashlib.sha256(b).hexdigest()
 source=read(B/'tools/fact_collector.py').decode();tree=ast.parse(source);names={'validate_fixture_argv','verify_fixture_runtime','sha','unique_json'};defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(defs)==4
 ns=dict(Path=Path,B=B,FIXTURE_PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',sys=sys,struct=struct,hashlib=hashlib,json=json)
 exec(compile(ast.fix_missing_locations(ast.Module(body=defs,type_ignores=[])),'<frozen-four-pure-guards-only>','exec'),ns)
 rows=[]
 def check(name,fn,expected=None):
  try:value=fn();actual='ACCEPTED'
  except (ValueError,TypeError) as e:actual=str(e);value=None
  ok=actual==('ACCEPTED' if expected is None else expected);rows.append(dict(name=name,passed=ok,expected=expected or 'ACCEPTED',actual=actual,value=value))
 good=[ns['FIXTURE_PY'],'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE']
 argv=[('exact',good,None),('adb',['D:/Android/SDK/platform-tools/adb.exe',*good[1:]],'FACT_FIXTURE_ARGV'),('foreign',['C:/Other/python.exe',*good[1:]],'FACT_FIXTURE_ARGV'),('tuple',tuple(good),'FACT_FIXTURE_ARGV'),('short',good[:-1],'FACT_FIXTURE_ARGV'),('extra',good+['X'],'FACT_FIXTURE_ARGV'),('bool',[True,*good[1:]],'FACT_FIXTURE_ARGV'),('case',[good[0].upper(),*good[1:]],'FACT_FIXTURE_ARGV'),('alias',[good[0].replace('/','\\'),*good[1:]],'FACT_FIXTURE_ARGV'),('flag',[good[0],'-E',*good[2:]],'FACT_FIXTURE_ARGV'),('script',[*good[:5],str(R/'fact_fixture.py'),'COMPLETE'],'FACT_FIXTURE_ARGV'),('mode',[*good[:-1],'OTHER'],'FACT_FIXTURE_ARGV')]
 for name,a,why in argv:check('ARGV_'+name,lambda a=a:ns['validate_fixture_argv'](a),why)
 # Source provider is a pure protocol double; no Original Gate or runtime API.
 sys.path.insert(0,str(B/'tools'));meta=read(B/'reference/current-runtime-identity.json');mb=json.loads(meta);exe=read(ns['FIXTURE_PY']);identity=sha(meta);exehash=sha(exe)
 class SourceProvider:
  def __init__(self,change=None):self.policy=dict(runtimeIdentitySha256=identity,outerPythonSha256=exehash);self.runtime=dict(identitySha256=identity);self.change=change;self.reads=[]
  def source_read(self,p):
   self.reads.append(str(p));b=meta if str(p).endswith('.json') else exe
   return b+b'X' if self.change==('meta' if str(p).endswith('.json') else 'exe') else b
 for name in ('valid','meta','exe','policy'):
  provider=SourceProvider(name)
  if name=='policy':provider.policy['runtimeIdentitySha256']='0'*64
  check('IDENTITY_'+name,lambda provider=provider:ns['verify_fixture_runtime'](provider),None if name=='valid' else 'FACT_FIXTURE_EXECUTABLE_IDENTITY' if name=='exe' else 'FACT_FIXTURE_RUNTIME_METADATA')
 entry=read(B/'tools/entry_gates.py').decode();et=ast.parse(entry);fn=next(n for n in et.body if isinstance(n,ast.FunctionDef) and n.name=='fixture_root_allowed');env=dict(Path=Path,BASE=B,no_links=lambda p:None)
 exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<frozen-root-predicate-no-link-IO-model>','exec'),env)
 root=Path('D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures')
 paths=[(B/'selfchecks/work/new-a',True),(root/'new-a',True),(root,False),(str(root)+'-other/x',False),('C:/outside/a',False),(str(root)+'/../escape',False),(str(root)+'/./x',False),(B.parent/'d1android02-global-idle-contract02-revision02/selfchecks/work/old-x',False)]
 for i,(p,want) in enumerate(paths):
  actual=env['fixture_root_allowed'](p);rows.append(dict(name='ROOT_'+str(i),passed=actual is want,actual=actual,expected=want,linkFilesystemGate='NOT_RUN_PURE_DEPENDENCY_STUB'))
 proposal=json.loads(read(B/'reference/next-readonly-facts-execution-proposal.json'))
 for key,rel in [('sourceSeal','reference/runner-source-seal.json'),('gateSources','reference/gate-sources.json'),('collector','tools/fact_collector.py'),('factPlan','reference/fact-plan.json'),('targetSevenRolePlan','reference/exact-seven-role-plan.json'),('externalHandoff','EXTERNAL_HANDOFF.md')]:
  row=proposal[key];ok=Path(row['path']).resolve()==(B/rel).resolve() and row['sha256']==sha(read(B/rel)) and proposal['approvedForExecution'] is False;rows.append(dict(name='PROPOSAL_'+key,passed=ok,currentOnly=True))
 for rel in ('tools/production_runner.py','tools/outer_owner.py','tools/capture_android02.ps1'):
  text=read(B/rel).decode();ok='fixture_root_allowed' in text if rel.endswith('.py') else 'D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE' in text
  rows.append(dict(name='REFERENCE_'+rel,passed=ok,fullConstructedChain='NOT_RUN'))
 handoff=read(B/'EXTERNAL_HANDOFF.md').decode();ok=proposal['externalHandoff']['implemented'] is False and proposal['externalHandoff']['executed'] is False and all(x in handoff for x in ('NOT_RUN','NOT_PROVEN','10s','30s','300'))
 rows.append(dict(name='EXTERNAL_STATIC_UNIMPLEMENTED_BOUNDARY',passed=ok,externalApproval='NOT_APPROVED',actualExternalReturn='NOT_RUN_NOT_PROVEN',signatureIPCImplementation='NOT_RUN'))
 assert len(rows)==34
 save(R/'pure-static-results.json',dict(results=rows,allPassed=all(x['passed'] for x in rows),count=34,actualPopen=0,actualGate=0,actualCollector=0,actualNativeRoute=0));return rows
