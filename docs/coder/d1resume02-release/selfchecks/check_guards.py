"""Seven actual unchanged entry invocations must reject before child/root/custody setup. No SDK invocation."""
from pathlib import Path
import json,subprocess,time,hashlib,importlib.util
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/guard-001';assert not E.exists();E.mkdir(parents=True)
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
spec=importlib.util.spec_from_file_location('release_verify',B/'tools/package_delivery.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);c=m.materials()
def write(p,o):p.write_text(json.dumps(o,indent=2)+'\n',encoding='utf-8')
rows=[]
for i,request in enumerate(c['captureRequests']+c['observerRequests']):
 metadata=i<5;entry=B/'tools'/('capture_metadata.ps1' if metadata else 'observe_original.ps1');name='metadata-'+str(i+1) if metadata else ('java-deploy' if i==5 else 'java-case')
 argv=[PS,'-NoLogo','-NoProfile','-NonInteractive','-File',str(entry),'-RequestPath',str(R/request['path'])];write(E/(name+'.request.json'),dict(argv=argv,entry=m.pin(entry),request=request))
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(argv,stdout=so,stderr=se)
  try:code=p.wait(timeout=12)
  except subprocess.TimeoutExpired:
   write(E/(name+'.pending.json'),dict(pid=p.pid,originalControllerPending=True,killed=False));print('PENDING SAME ORIGINAL CONTROLLER '+name,flush=True)
   while p.poll() is None:time.sleep(.25)
   code=p.returncode
 out=(E/(name+'.stdout.txt')).read_bytes();err=(E/(name+'.stderr.txt')).read_bytes();token=b'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION' if metadata else b'Reviewed input pin changed'
 assert code!=0 and token in err and not out,(name,code,err)
 row=dict(name=name,pid=p.pid,exitCode=code,naturalReturn=True,stdoutBytes=len(out),stderrBytes=len(err),expectedRejection=token.decode(),noChildDerivedFromExactReviewedEntryStage=True);rows.append(row);write(E/(name+'.exit.json'),row);print(name,'EXPECTED_PRESTART_REJECTION',flush=True)
code=(B/'tools/capture_metadata.ps1').read_text();assert code.index('PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION')<code.index('$c=@{')
old=(B/'tools/observe_original.ps1').read_text();assert old.index('Reviewed input pin changed')<old.index('$c=@{') and old.index('Reviewed input pin changed')<old.index('[IO.Directory]::CreateDirectory')
write(E/'results.json',dict(status='PASS_PREPARATION_GUARDS',rejectedBeforeChild=7,invocations=rows,sdkCalls=0,deviceCalls=0,liveDirectoryChecks=0,hostBuilds=0,androidBuilds=0,actualControlStdoutBytes=sum(r['stdoutBytes'] for r in rows),actualControlStderrBytes=sum(r['stderrBytes'] for r in rows),executionAuthorization=None,permissionMinted=False));print('PASS_PREPARATION_GUARDS',flush=True)
