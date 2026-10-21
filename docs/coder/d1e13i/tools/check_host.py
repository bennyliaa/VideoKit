"""One necessary compile. Parent holds original Popen and output handles across qualification failures."""
from pathlib import Path
import subprocess,json,hashlib,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/host-001';C=B/'.checks/host-001';E.mkdir(exist_ok=False);C.mkdir(parents=True,exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');BASE=B/'artifacts/e13f-reviewed-base.jar';OWNERS={}
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=sorted((B/'tools').glob('*.java'));write(E/'inputs.json',[pin(p) for p in sources]+[pin(BASE)]);commands=[]
def run(name,cmd,expected=0):
 cmd=[str(x) for x in cmd];commands.append(dict(name=name,argv=cmd));write(E/'commands.json',commands);holder=dict(argv=cmd,process=None,stdout=None,stderr=None,qualified=True,waitReturned=False,filesClosed=False);OWNERS[name]=holder
 try:
  holder['stdout']=(E/(name+'.stdout.txt')).open('xb');holder['stderr']=(E/(name+'.stderr.txt')).open('xb');p=subprocess.Popen(cmd,stdout=holder['stdout'],stderr=holder['stderr']);holder['process']=p
  try:code=p.wait(timeout=20)
  except subprocess.TimeoutExpired:
   holder['qualified']=False;write(E/(name+'.pending.json'),dict(pid=p.pid,originalPending=True,killed=False,parentCustody='SAME_POPEN_AND_FILES_RETAINED_PARENT_WAITS_NO_RAISE'));print(name,'PENDING same parent custody retained',flush=True);code=p.wait()
  holder['waitReturned']=True
 finally:
  # These files are not pipes/readers; preserve handles until same child actually returns.
  if holder['waitReturned']:
   holder['stdout'].close();holder['stderr'].close();holder['filesClosed']=True
 if holder['waitReturned'] and holder['filesClosed']:
  write(E/(name+'.exit.json'),dict(argv=cmd,pid=p.pid,exitCode=code,naturalReturn=True,parentOriginalWaitReturned=True,parentRecordingFilesCloseReturned=True,qualificationPreserved=holder['qualified']));OWNERS.pop(name)
 assert code==expected and holder['qualified'],(name,(E/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'));print(name,'PASS',flush=True)
run('compile',[J/'javac.exe','-encoding','UTF-8','-cp',BASE,'-d',C,*sources])
modes=['OK','SPLIT','INTERLEAVED','LIMIT','BAD_STATUS','FAIL','LONG_FAIL','SHELL_FAIL','TRUNC_HEADER','TRUNC_PAYLOAD','BAD_ID','LONG_FRAME','BAD_EXIT_LENGTH','FRAME_OVER','RAW_OVER','WIRE_OVER','EOF_NO_EXIT','EXIT_NO_EOF','DOUBLE_EXIT','AFTER_EXIT','STDERR','EXIT_NONZERO','CLOSE_PENDING','TAIL_PENDING','WRITE_PENDING','WRITE_FAIL','CONNECT_FAIL','CLOSE_UNKNOWN_CONTRACT','CHAIN_OK','CHAIN_BAD_SCOPE','CHAIN_PENDING']
for mode in modes:run(mode,[J/'java.exe','-cp',str(C)+';'+str(BASE),'com.videokit.spike.e4.ICheck',mode,E/mode])
run('describe',[J/'java.exe','-cp',str(C)+';'+str(BASE),'com.videokit.spike.e4.E13IReadOnly','--describe'])
run('public-reject',[J/'java.exe','-cp',str(C)+';'+str(BASE),'com.videokit.spike.e4.E13IReadOnly','--g-readonly','NOT_A_REQUEST','0'*64],1)
write(E/'results.json',dict(status='PASS_FINITE_FIXED_SOCKET_OFFLINE',modes=modes,compileAttempts=1,actual5037Connections=0,SDKStarts=0,oldHandleReads=0,parentCustodyOutstanding=len(OWNERS),permanentSocketCloseException='Not induced live; direct E4Owned UNKNOWN no-second-close plus actual Socket close-pending tests and static non-daemon retention',oldLocalProbe30384='ARCHIVE_ONLY_NOT_QUERIED'))
