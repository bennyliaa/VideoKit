from pathlib import Path
import json,hashlib,subprocess,sys,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'/sys.argv[1];E.mkdir(parents=True,exist_ok=False);C=B/'.checks'/sys.argv[1];C.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin')
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
sources=[]
for folder in ['src','upstream-c14/src','binding']:sources+=sorted((B/folder).rglob('*.java'))
sources+=sorted((B/'tools').glob('*.java'))+[B/'selfchecks/FCompletionCheck.java'];write(E/'inputs.json',[pin(p) for p in sources]);arg=E/'compile.args';arg.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources));commands=[]
def run(name,argv):
 cmd=[str(x) for x in argv];commands.append(dict(name=name,argv=cmd));write(E/'commands.json',commands)
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se)
  try:code=p.wait(timeout=20)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,originalPending=True,killed=False));raise
 write(E/(name+'.exit.json'),dict(pid=p.pid,exitCode=code,naturalReturn=True));assert code==0,(name,(E/(name+'.stderr.txt')).read_text());print(name,'PASS',flush=True)
run('compile',[J/'javac.exe','-encoding','UTF-8','-d',C,'@'+str(arg)])
for mode in ['BLOCKED','THROWS']:run('finish-'+mode,[J/'java.exe','-cp',C,'com.videokit.spike.e4.FCompletionCheck',mode])
write(E/'results.json',dict(status='PASS_F02_ACTUAL_REQUEST_FAIL',modes=['BLOCKED','THROWS'],deviceCalls=0))
