"""Exactly scoped OWNER2 recheck, single conditional TERM and bounded original-identity observation."""
from pathlib import Path
import sys,json,hashlib,datetime,os,time
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at3/tools'
sys.path.insert(0,str(B));import exact_process as ep
from remote_command import run_as_argv
from command_response import complete_stdout
for name,h in [('exact_process.py','f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'),('remote_command.py','db349901205ab4018ca5878b05cfc704b93db16c00b6f04622b23e749762b974')]:assert hashlib.sha256((B/name).read_bytes()).hexdigest()==h
def new(name,value):
 assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())+131072<1048576
 with (E/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
new('attempt.json',{'at':datetime.datetime.now().astimezone().isoformat(),'authority':'docs/milestones/D1_E4A_OWNER2_TESTER_REQUIREMENTS_V1.0.md','pid':7722,'startTicks':7571831,'signal':'TERM','signalCap':1,'parentProcReadAuthorized':False})
records=[]
def command(name,script):
 assert len(records)<4
 p=ep.collect(run_as_argv('D:/Android/SDK/platform-tools/adb.exe','HA1Q6WXR','shell',script),ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));records.append(p);new(f'{len(records):02d}-{name}.json',p);return p
script=r'''
set -eu
test "$(id -u)" = 10221; test "$(pwd)" = /data/user/0/com.videokit.app
if [ ! -d /proc/7722 ]; then printf 'OWNER2_ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL\n'; exit 0; fi
s=$(cat /proc/7722/stat); printf 'OWNER2_ORIGINAL_STAT|%s\n' "$s"
case "$s" in '7722 (tee) '*) ;; *) exit 51;; esac
r=${s##*) }; set -- $r; test "$2" = 7718; shift 19; test "$1" = 7571831
u=$(/system/bin/toybox awk '/^Uid:/ {print $2" "$3" "$4" "$5}' /proc/7722/status); printf 'OWNER2_UIDS|%s\n' "$u"; test "$u" = '10221 10221 10221 10221'
h=$(/system/bin/toybox od -An -v -tx1 /proc/7722/cmdline | /system/bin/toybox tr -d ' \n'); printf 'OWNER2_CMDHEX|%s\n' "$h"; test "$h" = 7465650066696c65732f65345f66697874757265732f62617369632e6d703400
c=$(/system/bin/toybox readlink /proc/7722/cwd); printf 'OWNER2_CWD|%s\n' "$c"; test "$c" = /data/user/0/com.videokit.app
x=$(/system/bin/toybox readlink /proc/7722/exe); printf 'OWNER2_EXE|%s\n' "$x"; test "$x" = /system/bin/toybox
l=$(/system/bin/toybox readlink /proc/7722/fd/3); printf 'OWNER2_FD3_LINK|%s\n' "$l"; test "$l" = /data/user/0/com.videokit.app/files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
a=files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
test -f "$a"; test ! -L "$a"
f=$(/system/bin/toybox stat -L -c '%d|%i|%u|%f' -- /proc/7722/fd/3); printf 'OWNER2_FD3_TARGET_STAT|%s\n' "$f"
v=$(/system/bin/toybox stat -c '%d|%i|%u|%f' -- "$a"); printf 'OWNER2_ARCHIVE_STAT|%s\n' "$v"; test "$f" = "$v"
test "$(/system/bin/toybox stat -c %u -- "$a")" = 10221
start=$(/system/bin/toybox date +%s%N); case "$start" in ''|*[!0-9]*) exit 52;; esac; end=$((start+2000000000))
s=$(cat /proc/7722/stat); case "$s" in '7722 (tee) '*) ;; *) exit 53;; esac; r=${s##*) }; set -- $r; test "$2" = 7718; shift 19; test "$1" = 7571831
printf 'OWNER2_RECHECK_COMPLETE|pid=7722|ticks=7571831|uid=10221|ppid=7718|fd=3\n'
printf 'OWNER2_TERM_ATTEMPT|pid=7722\n'
if /system/bin/toybox kill -TERM 7722; then printf 'OWNER2_TERM_RETURN|rc=0\n'; else r=$?; printf 'OWNER2_TERM_RETURN|rc=%s\n' "$r"; exit "$r"; fi
count=0; state=UNKNOWN
while [ "$count" -lt 20 ]; do
 now=$(/system/bin/toybox date +%s%N); if [ "$now" -ge "$end" ]; then break; fi
 if [ ! -d /proc/7722 ]; then printf 'OWNER2_ORIGINAL_PROC_GONE|pid=7722|ticks=7571831\n'; exit 0; fi
 if ! s=$(cat /proc/7722/stat); then printf 'OWNER2_OBSERVATION_UNKNOWN\n'; exit 0; fi
 r=${s##*) }; set -- $r; state=$1; shift 19
 if [ "$1" != 7571831 ]; then printf 'OWNER2_ORIGINAL_IDENTITY_ENDED_PID_REUSED|pid=7722\n'; exit 0; fi
 if [ "$state" = Z ]; then printf 'OWNER2_ORIGINAL_ZOMBIE|pid=7722|ticks=7571831|parent_reap=UNPROVEN\n'; exit 0; fi
 now=$(/system/bin/toybox date +%s%N); left=$((end-now)); if [ "$left" -lt 100000000 ]; then break; fi
 /system/bin/toybox sleep 0.1; count=$((count+1))
done
printf 'OWNER2_ORIGINAL_STILL_VISIBLE_OR_UNPROVEN|pid=7722|state=%s\n' "$state"
'''
result={'batch':'D1-E4A-OWNER2-20261017','status':'UNPROVEN','priorOtherRemoteOwnership':'UNKNOWN_NOT_CLEARED','mediaContentBytes':0}
try:
 p=command('conditional-term-and-original-observation',script)
 raw=bytes.fromhex(p['stdout']['prefixHex']).decode('utf-8','strict')
 result['originalControlOutput']=raw
 result['signalAttemptMarkers']=raw.count('OWNER2_TERM_ATTEMPT|pid=7722') if not p['stdout']['prefixTruncated'] else 'UNKNOWN'
 result['termReturnObserved']= 'OWNER2_TERM_RETURN|rc=0' in raw
 complete_stdout(p)
 if 'OWNER2_ORIGINAL_PROC_GONE|' in raw or 'OWNER2_ORIGINAL_IDENTITY_ENDED_PID_REUSED|' in raw:result['status']='ONLY_ORIGINAL_IDENTITY_ENDED'
 elif 'OWNER2_ORIGINAL_ZOMBIE|' in raw:result['status']='ORIGINAL_ZOMBIE_ADDRESS_SPACE_RELEASED_PARENT_REAP_UNPROVEN'
 elif 'OWNER2_ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL' in raw:result['status']='ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL'
 else:result['status']='ORIGINAL_IDENTITY_END_UNPROVEN'
 if result['termReturnObserved']:
  post=command('one-post-uid-snapshot','set -eu; test "$(id -u)" = 10221; test "$(pwd)" = /data/user/0/com.videokit.app; /system/bin/toybox ps -u 10221 -o PID,PPID,UID,ARGS')
  result['postUidSnapshot']=complete_stdout(post).decode('utf-8','strict')
except Exception as error:result['failure']={'type':type(error).__name__,'message':str(error)}
result.update(at=datetime.datetime.now().astimezone().isoformat(),metadataCommands=len(records),retainedLocalOwners=ep.retained_owners(),nextDiagnosticOrPreloadAuthorized=False)
new('result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if ep.retained_owners():
 print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED_DO_NOT_TERMINATE',flush=True)
 while ep.retained_owners():time.sleep(1)
