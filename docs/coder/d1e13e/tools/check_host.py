from pathlib import Path
import subprocess,json,hashlib,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];J=Path('D:/Android/Android Studio/jbr/bin');attempt=sys.argv[1];E=B/'evidence'/attempt;W=B/'.checks'/attempt;E.mkdir(exist_ok=False);W.mkdir(parents=True,exist_ok=False)
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'upstream-c14/src').rglob('*.java'))+sorted((B/'binding').rglob('*.java'))+sorted((B/'tools').glob('*.java'))+[B/'checks/E13EHostCheck.java']
write(E/'inputs.json',[pin(p) for p in sources]);arg=E/'compile.args';arg.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources));commands=[]
def run(name,args,timeout=30,code=0,needle=None):
 argv=[str(x) for x in args];commands.append(dict(name=name,argv=argv));write(E/'commands.json',commands)
 with (E/(name+'.stdout.txt')).open('xb') as so,(E/(name+'.stderr.txt')).open('xb') as se:
  p=subprocess.Popen(argv,stdout=so,stderr=se)
  try:r=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:write(E/(name+'.pending.json'),dict(pid=p.pid,state='ORIGINAL_LOCAL_PENDING_NO_KILL'));raise
 write(E/(name+'.exit.json'),dict(pid=p.pid,exitCode=r,naturalReturn=True));raw=(E/(name+'.stdout.txt')).read_bytes()+(E/(name+'.stderr.txt')).read_bytes();assert r==code,(name,r,raw.decode(errors='replace'))
 if needle:assert needle.encode() in raw
 print(name,'PASS',flush=True)
run('compile',[J/'javac.exe','-encoding','UTF-8','-d',W,'@'+str(arg)],60)
selected=sys.argv[2:] or ['GUARD','ARCHIVE_OK','ARCHIVE_OPEN_DENIED','ARCHIVE_WRITE_FAIL','ARCHIVE_WRITE_PENDING','ARCHIVE_CLOSE_UNKNOWN','PC_LATE']
for mode in selected:
 run(mode,[J/'java.exe','-cp',W,'com.videokit.spike.e4.E13EHostCheck',mode,E/mode],70 if mode=='PC_LATE' else 15,needle='PASS '+mode)
write(E/'results.json',dict(status='PASS_E13E_HOST_BOUNDARIES',cases=selected,deviceCalls=0,sdkCalls=0,localChildRawIsNotAndroidEvidence=True))
