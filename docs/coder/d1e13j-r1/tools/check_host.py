"""Diagnostic faults cannot bypass original wait/file custody. Default suite only focused J fixes."""
from pathlib import Path
import subprocess,json,hashlib,time,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence/host-001';C=B/'.checks/host-001';J=Path('D:/Android/Android Studio/jbr/bin');OWNERS={};commands=[]
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,cmd,expected=0):
 cmd=[str(x) for x in cmd];holder=dict(argv=cmd,process=None,stdout=None,stderr=None,qualified=True,waitReturned=False,filesClosed=False,diagnosticFailures=[],closeResults={});OWNERS[name]=holder
 def diagnostic(role,action):
  try:action();return True
  except BaseException as failure:
   holder['qualified']=False
   if len(holder['diagnosticFailures'])<16:holder['diagnosticFailures'].append(role+':'+type(failure).__name__)
   return False
 commands.append(dict(name=name,argv=cmd));diagnostic('command-record',lambda:write(E/'commands.json',commands))
 try:
  holder['stdout']=(E/(name+'.stdout.txt')).open('xb');holder['stderr']=(E/(name+'.stderr.txt')).open('xb');p=subprocess.Popen(cmd,stdout=holder['stdout'],stderr=holder['stderr']);holder['process']=p
  try:code=p.wait(timeout=20);holder['waitReturned']=True
  except subprocess.TimeoutExpired:
   holder['qualified']=False
   diagnostic('pending-record',lambda:write(E/(name+'.pending.json'),dict(pid=p.pid,originalPending=True,killed=False,parentCustody='SAME_POPEN_AND_FILES_RETAINED')))
   diagnostic('pending-console',lambda:print(name,'PENDING same parent custody retained',flush=True))
 finally:
  # Always reach same original wait, even if pending disk/console failed. No logging is a prerequisite.
  p=holder['process']
  if p is not None:
   while not holder['waitReturned']:
    try:code=p.wait();holder['waitReturned']=True
    except BaseException as failure:
     holder['qualified']=False
     if len(holder['diagnosticFailures'])<16:holder['diagnosticFailures'].append('original-wait:'+type(failure).__name__)
     time.sleep(0.1)
  if holder['waitReturned']:
   for role in ['stdout','stderr']:
    stream=holder[role]
    if stream is not None:
     try:stream.close();holder['closeResults'][role]=True
     except BaseException as failure:
      holder['closeResults'][role]=False;holder['qualified']=False
      if len(holder['diagnosticFailures'])<16:holder['diagnosticFailures'].append(role+'-close:'+type(failure).__name__)
   holder['filesClosed']=all(holder['closeResults'].get(role,False) for role in ['stdout','stderr'])
   if not holder['filesClosed']:
    # Same holder and parent remain alive; no second close and no diagnostic escape.
    while True:time.sleep(1)
 if holder['waitReturned'] and holder['filesClosed']:
  diagnostic('exit-record',lambda:write(E/(name+'.exit.json'),dict(argv=cmd,pid=p.pid,exitCode=code,naturalReturn=True,parentOriginalWaitReturned=True,parentRecordingFilesCloseReturned=True,qualificationPreserved=holder['qualified'],diagnosticFailures=list(holder['diagnosticFailures']))))
  OWNERS.pop(name)
 diagnostic('result-console',lambda:print(name,'PASS' if holder['qualified'] else 'FAILED_QUALIFICATION_OR_DIAGNOSTIC',flush=True))
 assert code==expected and holder['qualified'],(name,holder['diagnosticFailures'])
def main():
 E.mkdir(exist_ok=False);C.mkdir(parents=True,exist_ok=False);base=B/'artifacts/e13f-reviewed-base.jar';sources=sorted((B/'tools').glob('*.java'));write(E/'inputs.json',[pin(p) for p in sources]+[pin(base)]);run('compile',[J/'javac.exe','-encoding','UTF-8','-cp',base,'-d',C,*sources])
 for mode in ['OK','EXIT_NO_EOF','WRITE_FAIL','CHAIN_OK','CLOSE_PENDING','TAIL_PENDING']:run(mode,[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.ICheck',mode,E/mode])
 for mode in ['BUDGET_BOUNDARY','BUDGET_TX','PRODUCTION_AUDIT']:run(mode,[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.JCheck',mode,E/mode])
 run('AUDIT_AFTER_RAW_FAILURE',[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.R1Check',E/'AUDIT_AFTER_RAW_FAILURE'])
 run('describe',[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.E13JReadOnly','--describe']);run('public-reject',[J/'java.exe','-cp',str(C)+';'+str(base),'com.videokit.spike.e4.E13JReadOnly','--g-readonly','UNISSUED','0'*64],1)
 write(E/'results.json',dict(status='PASS_J_R1_FOCUSED_FIXES',modes=10,productionCompileAttempts=1,parentCustodyOutstanding=len(OWNERS),actual5037Connections=0,SDKStarts=0,oldHandleReads=0))
if __name__=='__main__':main()
