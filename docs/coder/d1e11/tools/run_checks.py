"""Affected E11 finite local checks only. No old suite, native or device execution."""
import argparse,hashlib,json,pathlib,subprocess,sys
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];J=pathlib.Path('D:/Android/Android Studio/jbr/bin');support=R/'docs/coder/d1e10a/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';sdk=pathlib.Path('D:/Android/SDK/platforms/android-36.1/android.jar')
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--cases',nargs='*');a=p.parse_args();out=B/'evidence/selfcheck-attempts'/a.attempt;out.mkdir(parents=True,exist_ok=False);work=B/'.selfcheck'/a.attempt;classes=work/'classes';classes.mkdir(parents=True,exist_ok=False)
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'upstream-c14/src').rglob('*.java'))+[B/'android/com/videokit/spike/e4/E11ActivationLifetime.java']+[B/'tools'/n for n in ['E9HostRegistry.java','E9PcSupervisor.java','E9PcClient.java','E9HostDeployment.java','E9HostManager.java','E9HostActivationSession.java','E9ActivationPolicyExport.java','E9TestFiles.java','E11ProductionCheck.java']]
def row(p):raw=p.read_bytes();return dict(path=str(p.relative_to(R)) if p.is_relative_to(R) else str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
(out/'inputs.json').write_text(json.dumps([row(p) for p in sources]+[row(sdk)],indent=2)+'\n',encoding='utf-8');args=work/'compile.args';args.write_text('\n'.join('"'+str(p).replace('\\','/')+'"' for p in sources),encoding='utf-8');cp=str(classes)+';'+str(support)+';'+str(sdk);commands=[]
def run(name,argv):
 cmd=[str(v) for v in argv];commands.append(dict(name=name,argv=cmd));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
 with (out/(name+'.stdout.txt')).open('xb') as stdout,(out/(name+'.stderr.txt')).open('xb') as stderr:
  result=subprocess.Popen(cmd,stdout=stdout,stderr=stderr)
  try:code=result.wait(timeout=90 if name=='compile' else 25)
  except subprocess.TimeoutExpired:
   # Only a synthetic local fixture may be cleaned by its controller; never call this a close ACK.
   (out/(name+'.timeout.json')).write_text(json.dumps(dict(pid=result.pid,status='FAILED_FINITE_TEST_TIMEOUT',originalCloseAck=False))+'\n');result.terminate();result.wait(timeout=5);raise
 print(name,code,flush=True)
 if code:print((out/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));raise SystemExit(code)
 return code
run('compile',[J/'javac.exe','-encoding','UTF-8','-cp',str(support)+';'+str(sdk),'-d',classes,'@'+str(args)])
results=[];reg=R/'docs/tester/D1_E10A_EXECUTION/4f21f71a-bf66-4a44-a287-320f0ae25fde/registry'
for case in a.cases or ['PARSER','SELECTION','DEPLOYMENT','OBSERVE_SUCCESS','OBSERVE_REPEAT','OBSERVE_LEGAL_SUFFIX','OBSERVE_KNOWN_FAILURE','OBSERVE_UNKNOWN','OBSERVE_OVERLAP','OBSERVE_REVOKE']:
 code=run(case,[J/'java.exe','-cp',cp,'com.videokit.spike.e4.E11ProductionCheck',case,work/case,B/'reference',reg]);results.append(dict(case=case,exitCode=code))
(out/'results.json').write_text(json.dumps(dict(schema=1,status='PASS',results=results,scope='Original production code with real catalog and synthetic platform/control/deployment port; no device',oldSuitesReexecuted=False,deviceCalls=0),indent=2)+'\n',encoding='utf-8')
