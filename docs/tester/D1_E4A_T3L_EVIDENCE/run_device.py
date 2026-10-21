"""One bounded read-only localization, existing synthetic target only."""
from pathlib import Path
import sys,json,hashlib,datetime,os,time
E=Path(__file__).resolve().parent;R=E.parents[2];B=R/'docs/coder/d1e4at3/tools';review=json.loads((E/'local-review.json').read_text());assert review['status']=='PASS'
for row in review['scripts']:assert hashlib.sha256((E/row['file']).read_bytes()).hexdigest()==row['sha256']
sys.path.insert(0,str(B));import exact_process as ep
from remote_command import run_as_argv
from command_response import complete_stdout
assert hashlib.sha256((B/'exact_process.py').read_bytes()).hexdigest()=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
def new(name,value):
 assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())+131072<1048576
 with (E/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
new('attempt.json',{'at':datetime.datetime.now().astimezone().isoformat(),'authority':'docs/milestones/D1_E4A_T3L_TESTER_REQUIREMENTS_V1.0.md','metadataCap':5,'syntheticHashCapBytes':256,'shaCallsCap':1,'targetStatCap':2,'producerCap':0,'procPid':16643})
records=[];result={'batch':'D1-E4A-T3L-TABLET-20261017','status':'UNPROVEN','producerAttempts':0,'mediaContentBytes':0,'priorRemoteOwnership':'UNKNOWN_NOT_CLEARED','originalT3RStatusUnchanged':True}
try:
 for name,file in [('guards-options-and-bounded-hash','read_guards.sh'),('one-original-pid-metadata','read_receiver.sh')]:
  assert len(records)<5
  p=ep.collect(run_as_argv('D:/Android/SDK/platform-tools/adb.exe','HA1Q6WXR','shell',(E/file).read_text()),ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));records.append(p);new(f'{len(records):02d}-{name}.json',p);text=complete_stdout(p).decode('utf-8','strict');result[name]=text
  if 'T3L_CONTEXT_REJECT' in text or 'T3L_PROC_CONTEXT_REJECT' in text:break
 result['status']='READONLY_OBSERVATIONS_RECORDED_NOT_A_DIAGNOSTIC_PASS'
except Exception as error:result['failure']={'type':type(error).__name__,'message':str(error)}
result.update(at=datetime.datetime.now().astimezone().isoformat(),metadataCommands=len(records),retainedLocalOwners=ep.retained_owners(),nextDiagnosticOrPreloadAuthorized=False)
new('result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if ep.retained_owners():
 print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED_DO_NOT_TERMINATE',flush=True)
 while ep.retained_owners():time.sleep(1)
