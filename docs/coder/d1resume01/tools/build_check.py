"""One javac compilation, finite directly relevant selfcheck, package the exact tested production classes."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,re,base64,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];J=Path('D:/Android/Android Studio/jbr/bin');E=B/'evidence/build-001';C=B/'build/classes'
repair=sys.argv[1:]==['--repair-test-only']
if repair:
 assert (E/'javac.exit.json').exists() and not (E/'results.json').exists()
 assert json.loads((E/'javac.exit.json').read_text())['exitCode']==0
else:
 assert not E.exists(),'one build attempt already reserved'
 E.mkdir(parents=True);C.mkdir(parents=True)
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sourceRows=json.loads((B/'evidence/source-derivation.json').read_text());sources=[R/r['current'] for r in sourceRows];checks=[B/'selfchecks/ResumeCheck.java'];allSources=sources+checks
if not repair:write(E/'inputs.json',[pin(p) for p in allSources])
else:
 for row in json.loads((E/'inputs.json').read_text())[:-1]:assert pin(R/row['path'])==row
 write(E/'test-repair-inputs.json',[pin(p) for p in checks])
arg=E/('test-repair.args' if repair else 'compile.args');arg.write_text('\n'.join('"'+p.as_posix()+'"' for p in (checks if repair else allSources)),encoding='utf-8')
commands=json.loads((E/'commands.json').read_text()) if repair else []
def run(name,argv):
 command=[str(a) for a in argv];commands.append(dict(name=name,argv=command));write(E/'commands.json',commands)
 with (E/(name+'.stdout.txt')).open('xb') as stdout,(E/(name+'.stderr.txt')).open('xb') as stderr:
  p=subprocess.Popen(command,stdout=stdout,stderr=stderr)
  try:code=p.wait(timeout=25)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,originalPending=True,killed=False));raise
 write(E/(name+'.exit.json'),dict(pid=p.pid,exitCode=code,naturalReturn=True));assert code==0,(name,(E/(name+'.stderr.txt')).read_text(encoding='utf-8'));print(name,'PASS',flush=True)
run('javac-test-repair' if repair else 'javac',[J/'javac.exe','-encoding','UTF-8',*(['-cp',C] if repair else []),'-d',C,'@'+str(arg)])
testName='selfcheck-repair' if repair else 'selfcheck'
run(testName,[J/'java.exe','-cp',C,'com.videokit.spike.e4.ResumeCheck',E/('local-fixtures-repair' if repair else 'local-fixtures'),B/'disposition/reviewed-original-disposition.json'])
raw=(E/(testName+'.stdout.txt')).read_text();assert 'PASS_RESUME_OFFLINE' in raw
trace=[]
for line in raw.splitlines():
 if not line.startswith('TRACE '):continue
 _,number,cap,value=line.split();argv=base64.urlsafe_b64decode(value+'='*(-len(value)%4)).decode().split('\n');trace.append(dict(operation=int(number),maxBytes=int(cap),argv=argv,executed='SCRIPTED_PORT_ONLY_NO_SDK'))
assert len(trace)==35
write(E/'deployment-command-trace.json',dict(children=trace,total=35,scope='real E9HostDeployment methods with local scripted outputs; no registry or actual Android install success claim'))
allow={}
for p in sources:
 package=re.search(r'package\s+([\w.]+);',p.read_text(encoding='utf-8-sig')).group(1);allow[package.replace('.','/')+'/'+p.stem]=p
jar=B/'artifacts/resume01-host-tools.jar';jar.parent.mkdir();rows=[]
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(C.rglob('*.class')):
  entry=p.relative_to(C).as_posix();top=entry[:-6].split('$')[0]
  if top not in allow:continue
  data=p.read_bytes();z.writestr(entry,data);rows.append(dict(entry=entry,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),source=pin(allow[top]),testedClass=pin(p)))
assert len(rows)==183 and all('ResumeCheck' not in r['entry'] for r in rows)
write(E/'host-jar-manifest.json',dict(jar=pin(jar),classes=rows,testClassesIncluded=False,recompiledAfterTests=False))
write(E/'results.json',dict(status='PASS_RESUME_OFFLINE',hostProductionCompilations=1,testOnlyRepairCompilations=int(repair),selfcheckAttempts=2 if repair else 1,initialSelfcheck='FAIL_TEST_FIXTURE_OMITTED_OUTPUT0' if repair else 'PASS',androidBuilds=0,deviceCalls=0,sdkCalls=0,originalCustodyRootAccesses=0,productionClasses=183,traceOperations=35,sourceReview='PENDING_INDEPENDENT_STATIC_REVIEW'))
print(json.dumps(dict(jar=pin(jar),status='PASS_RESUME_OFFLINE')))
