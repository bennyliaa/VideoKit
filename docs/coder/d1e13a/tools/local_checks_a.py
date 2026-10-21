"""Affected E13A binding production logic with finite platform substitutes; no old suites/device/native."""
from pathlib import Path
import hashlib,json,subprocess,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];J=Path('D:/Android/Android Studio/jbr/bin');attempt=sys.argv[1]
out=B/'evidence/local-checks'/attempt;out.mkdir(parents=True,exist_ok=False);work=B/'.checks'/attempt;classes=work/'classes';classes.mkdir(parents=True)
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'upstream-c14/src').rglob('*.java'))+sorted((B/'binding').rglob('*.java'))+[p for p in sorted((B/'tools').glob('*.java')) if p.name!='E13ProductionCheck.java']
def pin(p):raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
(out/'inputs.json').write_text(json.dumps([pin(p) for p in sources],indent=2)+'\n')
arg=work/'compile.args';arg.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources),encoding='utf-8')
commands=[]
def run(name,argv):
 command=[str(v) for v in argv];commands.append({'name':name,'argv':command});(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 with (out/(name+'.stdout.txt')).open('xb') as so,(out/(name+'.stderr.txt')).open('xb') as se:
  proc=subprocess.Popen(command,stdout=so,stderr=se)
  try:code=proc.wait(timeout=60 if name=='compile' else 15)
  except subprocess.TimeoutExpired:(out/'pending-original.json').write_text(json.dumps({'pid':proc.pid,'case':name,'state':'LOCAL_ORIGINAL_PENDING_NO_KILL'})+'\n');raise
 (out/(name+'.exit.json')).write_text(json.dumps({'exitCode':code})+'\n');print(name,code,flush=True)
 if code:print((out/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));raise SystemExit(code)
run('compile',[J/'javac.exe','-encoding','UTF-8','-d',classes,'@'+str(arg)])
cases=['FALSE','SECURITY','OTHER_EXCEPTION','TRUE_CALLBACK','BIND_IN_FLIGHT','UNBIND_IN_FLIGHT','CALLBACK_IN_FLIGHT','LATE_CALLBACK','UNBIND_EXCEPTION']
for case in cases:run(case,[J/'java.exe','-cp',classes,'com.videokit.spike.e4.E13ABindingCheck',case])
(out/'results.json').write_text(json.dumps({'status':'PASS_E13A_AFFECTED_PRODUCTION_BINDING_CHECKS','cases':cases,'platformSubstitute':True,'scope':'Only platform bind/unbind and callback scheduling substituted; actual shared owner used by SenderService/PermissionProbe executes','deviceCalls':0,'oldSourceCasesRerun':0,'nativeRuns':0,'expectedUnbindExceptionRetainsOriginal':True},indent=2)+'\n')
