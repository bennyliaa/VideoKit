from pathlib import Path
import hashlib,json,subprocess,shutil,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/host-001';E.mkdir(parents=True,exist_ok=False);C=B/'.checks/host-001';C.mkdir(parents=True,exist_ok=False);OLD=R/'docs/coder/d1e13f';J=Path('D:/Android/Android Studio/jbr/bin');A=B/'artifacts';A.mkdir(exist_ok=True)
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
base=json.loads((OLD/'evidence/host-jar-manifest.json').read_text());original=R/base['jar']['path'];assert pin(original)==base['jar'];baseJar=A/'e13f-reviewed-base.jar';shutil.copyfile(original,baseJar)
sources={row['source']['path']:row['source'] for row in base['classes']}
for name,row in sources.items():
 p=R/name;assert pin(p)==row;q=B/'baseline-source'/p.relative_to(OLD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
write(E/'base-inputs.json',dict(jar=pin(original),copiedJar=pin(baseJar),sources=list(sources.values()),baseClassCount=len(base['classes'])))
inputs=[B/'tools/E13GReadOnly.java',B/'tools/HCheck.java'];write(E/'inputs.json',[pin(p) for p in inputs]);commands=[]
def run(name,cmd,expected=0):
 cmd=[str(x) for x in cmd];commands.append(dict(name=name,argv=cmd));write(E/'commands.json',commands)
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se)
  try:code=p.wait(timeout=15)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,killed=False,originalPending=True));raise
 write(E/(name+'.exit.json'),dict(pid=p.pid,exitCode=code,naturalReturn=True));assert code==expected,(name,(E/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));print(name,'PASS',flush=True)
run('compile',[J/'javac.exe','-encoding','UTF-8','-cp',baseJar,'-d',C,*inputs])
for mode in ['SUCCESS','TIMEOUT','POLICY','WRITE_FAILURE','VERSION_OK','VERSION_BAD','VERSION_TIMEOUT']:run(mode,[J/'java.exe','-cp',str(C)+';'+str(baseJar),'com.videokit.spike.e4.HCheck',mode,E/mode])
run('describe',[J/'java.exe','-cp',str(C)+';'+str(baseJar),'com.videokit.spike.e4.E13GReadOnly','--describe'])
run('public-reject',[J/'java.exe','-cp',str(C)+';'+str(baseJar),'com.videokit.spike.e4.E13GReadOnly','--g-readonly'],1)
assert 'G_PRODUCTION_REJECTED_BEFORE_OWNER_OR_NETWORK' in (E/'public-reject.stderr.txt').read_text()
write(E/'results.json',dict(status='PASS_LIMITED_OFFLINE_PREPARE_PRODUCTION_DISABLED',modes=7,compileAttempts=1,productionAdbStarts=0,actual5037Connections=0,originalHandleReads=0,publicDispatch='REJECTED_BEFORE_OWNER_OR_NETWORK',writeFailureScope='Direct original archive IO fault, not full public chain',versionScope='Ephemeral local fixture port, candidate protocol literal0029 is not exact SDK binary proof',chainScope='Production package-private Chain with local JVM child substitution; public CLI intentionally refuses',oldClassesRecompiled=False))
