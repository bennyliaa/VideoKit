"""Only affected E13 production Java, new source scenarios and exact successor gate. No device/media/native."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];J=Path('D:/Android/Android Studio/jbr/bin')
attempt=sys.argv[1];out=B/'evidence/local-checks'/attempt;out.mkdir(parents=True,exist_ok=False);work=B/'.checks'/attempt;classes=work/'classes';classes.mkdir(parents=True)
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'upstream-c14/src').rglob('*.java'))+sorted((B/'checks').rglob('*.java'))+sorted((B/'tools').glob('*.java'))
def pin(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
(out/'inputs.json').write_text(json.dumps([pin(p) for p in sources],indent=2)+'\n')
args=work/'compile.args';args.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources),encoding='utf-8')
commands=[]
def run(name,argv):
 cmd=[str(v) for v in argv];commands.append({'name':name,'argv':cmd});(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 with (out/(name+'.stdout.txt')).open('xb') as so,(out/(name+'.stderr.txt')).open('xb') as se:
  child=subprocess.Popen(cmd,stdout=so,stderr=se)
  try:code=child.wait(timeout=60 if name=='compile' else 20)
  except subprocess.TimeoutExpired:
   (out/'pending-original.json').write_text(json.dumps({'pid':child.pid,'state':'PENDING_ORIGINAL_LOCAL_CHECK_NO_KILL','name':name})+'\n');raise
 (out/(name+'.exit.json')).write_text(json.dumps({'exitCode':code,'scope':'local E13 synthetic fixture only'})+'\n')
 print(name,code,flush=True)
 if code:print((out/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));raise SystemExit(code)
run('compile',[J/'javac.exe','-encoding','UTF-8','-d',classes,'@'+str(args)])
for method in ['authorizedHostSourceReadAndClose','oldGenerationNeverOpensSource','twoConsumersHoldSourceUntilLastReturn','cancelLateOpenRetainsOriginalOwner','lateReadAndCloseFailureDoNotReleaseEarly']:
 run(method,[J/'java.exe','-cp',classes,'com.videokit.spike.e4.E13SourceCases',method])
registry=work/'accepted-registry-copy';original=R/'docs/coder/d1e11/source-export/accepted-registry-snapshot';shutil.copytree(original,registry)
before=[pin(p) for p in sorted(registry.rglob('*')) if p.is_file()]
run('DEPLOYMENT',[J/'java.exe','-cp',classes,'com.videokit.spike.e4.E13ProductionCheck','DEPLOYMENT',registry])
run('BOUNDARIES',[J/'java.exe','-cp',classes,'com.videokit.spike.e4.E13ProductionCheck','BOUNDARIES'])
after=[pin(p) for p in sorted(registry.rglob('*')) if p.is_file()];assert before==after
(out/'results.json').write_text(json.dumps({'status':'PASS_AFFECTED_E13_LOCAL_CHECKS','groups':7,'sources':len(sources),'deviceCalls':0,'nativeBuilds':0,'oldSuites':0,'registrySnapshotUnchanged':True,'scope':'Production source bridge/tickets on JVM and synthetic deployment ports; NOT Android binder/native tests'},indent=2)+'\n')
print('PASS_AFFECTED_E13_LOCAL_CHECKS')
