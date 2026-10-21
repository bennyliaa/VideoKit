"""Continue same compiled bytecode after local-loopback sandbox restriction; do not recompile."""
from pathlib import Path
import subprocess,json,hashlib,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/final-002';E.mkdir(exist_ok=False);C=B/'.checks/host-001';J=Path('D:/Android/Android Studio/jbr/bin');base=B/'artifacts/e13f-reviewed-base.jar'
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,cmd,expected=0):
 cmd=[str(x) for x in cmd]
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se)
  try:code=p.wait(timeout=15)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,killed=False));raise
 write(E/(name+'.exit.json'),dict(argv=cmd,pid=p.pid,exitCode=code,naturalReturn=True));assert code==expected,(name,(E/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));print(name,'PASS',flush=True)
for mode in ['VERSION_OK','VERSION_BAD','VERSION_TIMEOUT']:run(mode,[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.HCheck',mode,E/mode])
run('describe',[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.E13GReadOnly','--describe'])
run('public-reject',[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.E13GReadOnly','--g-readonly'],1)
assert 'G_PRODUCTION_REJECTED_BEFORE_OWNER_OR_NETWORK' in (E/'public-reject.stderr.txt').read_text()
ps=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe');observer=B/'tools/observe_g_only.ps1'
run('observer-parse',[ps,'-NoProfile','-File',B/'tools/check_observer.ps1','-ScriptPath',observer])
original=(R/'docs/coder/d1e13f/tools/observe_original.ps1').read_text(encoding='utf-8-sig');current=observer.read_text();marker='# Same original local context';assert original[original.index(marker):]==current[current.index(marker):]
for mode in ['correct-role-disabled','wrong-exe','wrong-serial-argv-role']:
 req=dict(evidenceRoot='D:/CodexProjects/VideoKit/docs/tester/D1_E13G_SUPPLEMENT_EVIDENCE',pins=[],argv=['D:/Android/Android Studio/jbr/bin/java.exe','-cp','D:/CodexProjects/VideoKit/docs/coder/d1e13h/artifacts/e13h-host-tools.jar','com.videokit.spike.e4.E13GReadOnly','--g-readonly'],maxTextBytes=32768,id='E13G-SUPPLEMENT-ONCE',scope='116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef')
 if mode=='wrong-exe':req['argv'][0]='D:/bad.exe'
 if mode=='wrong-serial-argv-role':req['argv'][3]='com.videokit.spike.e4.E13HostCase'
 p=E/(mode+'.json');write(p,req);run(mode,[ps,'-NoProfile','-File',observer,'-RequestPath',p],1)
 assert ('G_PRODUCTION_REJECTED_SERVER_REPLACEMENT_RACE' if mode=='correct-role-disabled' else 'Exact G-only host role required') in (E/(mode+'.stderr.txt')).read_text(encoding='utf-8',errors='replace')
write(E/'results.json',dict(status='PASS_LIMITED_OFFLINE_PREPARE_PRODUCTION_DISABLED',sameCompiledClasses='host-001',additionalCompilations=0,versionGroups=3,actual5037Connections=0,SDKStarts=0,originalSessionReads=0,observerOwnedBodyByteIdenticalToE13F=True,publicJavaAndPowerShellRejectBeforeDispatch=True,oldOriginalTask='UNTOUCHED',supportedSdkProtocolMapping='UNPROVEN_OFFICIAL_SOURCE_CANDIDATE41_ONLY',serverReplacementRace='UNRESOLVED_PRODUCTION_DISABLED'))
