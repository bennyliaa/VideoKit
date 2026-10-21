"""After the one local review, one compatibility gate and one exact OWNER3 control only."""
from pathlib import Path
import hashlib,json,sys,os,time,datetime
E=Path(__file__).resolve().parent;R=E.parents[2];B=R/'docs/coder/d1e4at3/tools'
review=json.loads((E/'local-review.json').read_text());control=(E/'owner3_control.sh').read_bytes();assert review['status']=='PASS' and hashlib.sha256(control).hexdigest()==review['controlSha256']
sys.path.insert(0,str(B));import exact_process as ep
from remote_command import run_as_argv
from command_response import complete_stdout
assert hashlib.sha256((B/'exact_process.py').read_bytes()).hexdigest()=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
def new(name,value):
 assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())+131072<1048576
 with (E/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
new('device-attempt.json',{'at':datetime.datetime.now().astimezone().isoformat(),'authority':'docs/milestones/D1_E4A_OWNER3_TESTER_REQUIREMENTS_V1.0.md','localReviewControlSha256':review['controlSha256'],'pid':7722,'startTicks':7571831,'maxMetadataCommands':4,'maxTermAttempts':1})
calls=[]
def command(name,script):
 assert len(calls)<4
 p=ep.collect(run_as_argv('D:/Android/SDK/platform-tools/adb.exe','HA1Q6WXR','shell',script),ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));calls.append(p);new(f'{len(calls):02d}-{name}.json',p);return p
compat=r'''
set -efu
test "$(id -u)" = 10221; test "$(pwd)" = /data/user/0/com.videokit.app
command -v cat >/dev/null
printf 'OWNER3_COMPAT|readlink-od-tr-ps\n'
/system/bin/toybox readlink --help >/dev/null
/system/bin/toybox od --help >/dev/null
/system/bin/toybox tr --help >/dev/null
/system/bin/toybox ps --help >/dev/null
printf 'OWNER3_COMPAT_STAT|'; /system/bin/toybox stat -L -c '%d|%i|%u' -- .
t=$(/system/bin/toybox date +%s%N); case "$t" in ''|*[!0-9]*) exit 52;; esac; e=$((t+2000000000)); test "$e" -gt "$t"
/system/bin/toybox sleep 0.001
printf 'OWNER3_COMPAT_SIGNAL_NAMES|'; /system/bin/toybox kill -l
printf 'OWNER3_COMPAT_COMPLETE\n'
'''
new('compatibility-script.json',{'script':compat,'scope':'command help, current directory stat, time and signal-name list only; no signal sent'})
result={'batch':'D1-E4A-OWNER3-20261017','status':'NOT_PROVEN','termControlDispatched':False,'termAttempts':0,'priorOtherRemoteOwnership':'UNKNOWN_NOT_CLEARED','mediaContentBytes':0}
try:
 p=command('harmless-compatibility',compat);out=complete_stdout(p).decode('utf-8','strict');assert 'OWNER3_COMPAT_COMPLETE' in out and 'TERM' in out
 result['compatibility']='PASS'
 result['termControlDispatched']=True;p=command('exact-control-and-observation',control.decode('utf-8'));out=bytes.fromhex(p['stdout']['prefixHex']).decode('utf-8','strict');result['controlOutput']=out
 result['termAttempts']=out.count('OWNER3_TERM_ATTEMPT|pid=7722') if not p['stdout']['prefixTruncated'] else 'UNKNOWN'
 result['termReturnObserved']='OWNER3_TERM_RETURN|rc=0' in out
 complete_stdout(p)
 if 'OWNER3_OBSERVATION|GONE|' in out or 'OWNER3_OBSERVATION|REUSED|' in out:result['status']='EXACT_ORIGINAL_IDENTITY_ENDED'
 elif 'OWNER3_OBSERVATION|ZOMBIE|' in out:result['status']='ORIGINAL_ZOMBIE_ADDRESS_SPACE_RELEASED_PARENT_REAP_UNPROVEN'
 elif 'OWNER3_ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL' in out:result['status']='ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL'
 else:result['status']='ORIGINAL_END_UNPROVEN'
 if result['termReturnObserved']:
  post=command('one-post-uid-snapshot','set -eu; test "$(id -u)" = 10221; test "$(pwd)" = /data/user/0/com.videokit.app; /system/bin/toybox ps -u 10221 -o PID,PPID,UID,ARGS');result['postUidSnapshot']=complete_stdout(post).decode('utf-8','strict')
except Exception as error:result['failure']={'type':type(error).__name__,'message':str(error)}
result.update(at=datetime.datetime.now().astimezone().isoformat(),metadataCommands=len(calls),retainedLocalOwners=ep.retained_owners(),nextDiagnosticOrPreloadAuthorized=False)
new('result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if ep.retained_owners():
 print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED_DO_NOT_TERMINATE',flush=True)
 while ep.retained_owners():time.sleep(1)
