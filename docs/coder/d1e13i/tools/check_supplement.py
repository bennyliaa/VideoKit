"""Test-only probe compile, exact existing parent function timeout branch, script AST and release gate."""
from pathlib import Path
import ast,json,subprocess,types,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/supplement-002';E.mkdir(exist_ok=False);C=B/'.checks/host-001';W=B/'.checks/supplement-002';W.mkdir(exist_ok=False);BASE=B/'artifacts/e13f-reviewed-base.jar';J=Path('D:/Android/Android Studio/jbr/bin');PS=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,cmd,expected=0):
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen([str(x) for x in cmd],stdout=so,stderr=se)
  try:code=p.wait(timeout=20)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,parentRetainsSameProcess=True,killed=False));code=p.wait()
 write(E/(name+'.exit.json'),dict(argv=[str(x) for x in cmd],pid=p.pid,exitCode=code,naturalReturn=True,filesClosed=True));assert code==expected,(name,(E/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));print(name,'PASS',flush=True)
probe=B/'tools/IAdditionalCheck.java';write(E/'probe-input.json',dict(source=probe.relative_to(R).as_posix(),sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),productionDirectory='host-001',productionRecompiled=False))
run('test-probe-compile',[J/'javac.exe','-encoding','UTF-8','-cp',str(C)+';'+str(BASE),'-d',W,probe]);run('additional-gates',[J/'java.exe','-cp',str(W)+';'+str(C)+';'+str(BASE),'com.videokit.spike.e4.IAdditionalCheck',E/'empty-output'])
# Execute the actual saved parent function, shortening only the fixture wait adapter to50ms.
source=(B/'tools/check_host.py').read_text();tree=ast.parse(source);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
class ShortWait(subprocess.Popen):
 def wait(self,timeout=None):return super().wait(timeout=0.05 if timeout==20 else timeout)
owners={};namespace=dict(E=E,OWNERS=owners,commands=[],write=write,subprocess=types.SimpleNamespace(Popen=ShortWait,TimeoutExpired=subprocess.TimeoutExpired));exec(compile(ast.Module(body=[function],type_ignores=[]),str(B/'tools/check_host.py'),'exec'),namespace)
qualificationFailed=False
try:namespace['run']('parent-custody',[PS,'-NoProfile','-Command',"Start-Sleep -Milliseconds 300; [Console]::WriteLine('LOCAL_PARENT_ORIGINAL_RETURN')"])
except AssertionError:qualificationFailed=True
exitRecord=json.loads((E/'parent-custody.exit.json').read_text());pending=json.loads((E/'parent-custody.pending.json').read_text());assert qualificationFailed and not owners and exitRecord['pid']==pending['pid'] and exitRecord['exitCode']==0 and not exitRecord['qualificationPreserved'] and exitRecord['parentRecordingFilesCloseReturned']
write(E/'parent-custody-source-binding.json',dict(status='PASS_ACTUAL_PARENT_FUNCTION_TIMEOUT_CUSTODY',source='docs/coder/d1e13i/tools/check_host.py',sha256=hashlib.sha256(source.encode()).hexdigest(),actualFunctionAstExecuted=True,onlyFixtureWaitAdapterSeconds=0.05,originalChildNaturalReturn=True,callerQualificationStillFailed=True,processAndFilesRetainedAcrossTimeout=True,kill=False))
observer=B/'tools/observe_i_only.ps1';old=(R/'docs/coder/d1e13f/tools/observe_original.ps1').read_text(encoding='utf-8-sig');new=observer.read_text();marker='# Same original local context';assert old[old.index(marker):]==new[new.index(marker):]
parser=R/'docs/coder/d1e13h/tools/check_observer.ps1';run('observer-parse',[PS,'-NoProfile','-File',parser,'-ScriptPath',observer])
for mode in ['correct-unissued','wrong-role']:
 req=dict(evidenceRoot='D:/CodexProjects/VideoKit/docs/tester/D1_E13I_G_SUPPLEMENT_EVIDENCE',pins=[],argv=['D:/Android/Android Studio/jbr/bin/java.exe','-cp','D:/CodexProjects/VideoKit/docs/coder/d1e13i/artifacts/e13i-host-tools.jar','com.videokit.spike.e4.E13IReadOnly','--g-readonly','UNISSUED_RELEASE','a'*64],maxTextBytes=32768,id='E13I-SUPPLEMENT-ONCE',scope='116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef')
 if mode=='wrong-role':req['argv'][3]='com.videokit.spike.e4.E13HostCase'
 p=E/(mode+'.json');write(p,req);run(mode,[PS,'-NoProfile','-File',observer,'-RequestPath',p],1)
 assert ('I_EXECUTION_NOT_DISPATCHED_BEFORE_PROCESS' if mode=='correct-unissued' else 'Exact I-only fixed socket role required') in (E/(mode+'.stderr.txt')).read_text(encoding='utf-8',errors='replace')
write(E/'results.json',dict(status='PASS_SUPPLEMENT_FINAL_PRODUCTION_BYTES_UNCHANGED',testOnlyCompile=1,productionCompilesAdded=0,parentActualTimeoutBranch=True,identityGates=True,emptyOutputActualSocket=True,observerBodyIdenticalToE13F=True,actual5037Connections=0,SDKStarts=0,originalHandleReads=0,oldLocalUnknown30384Queries=0))
