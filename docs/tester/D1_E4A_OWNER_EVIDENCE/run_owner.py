"""Scoped metadata and conditional one TERM, authorized by E4A-OWNER requirements."""
from pathlib import Path
import sys,json,hashlib,datetime,shlex,time,os
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at3/tools'
sys.path.insert(0,str(B));import exact_process as ep
from command_response import complete_stdout
from remote_command import run_as_argv
assert hashlib.sha256((B/'exact_process.py').read_bytes()).hexdigest()=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
ADB='D:/Android/SDK/platform-tools/adb.exe';S='HA1Q6WXR';calls=[];result={'batch':'D1-E4A-OWNER-20261017','status':'NOT_PROVEN_NO_SIGNAL','signalAttempts':0,'priorRemoteOwnership':'UNKNOWN_NOT_CLEARED','mediaContentBytes':0}
def new(name,data):
 assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())+131072<1048576
 with (E/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def call(name,script):
 assert len(calls)<12
 p=ep.collect(run_as_argv(ADB,S,'shell',script),ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));calls.append({'stage':name,'record':p});new(f'{len(calls):02d}-{name}.json',p)
 return complete_stdout(p).decode('utf-8','strict')
def q(s):return shlex.quote(str(s))
new('attempt.json',{'at':datetime.datetime.now().astimezone().isoformat(),'authority':'docs/milestones/D1_E4A_OWNER_TESTER_REQUIREMENTS_V1.0.md','pid':7722,'parent':7718,'maxMetadataCommands':12,'maxFdEntries':16,'termCap':1})
base='set -eu; test "$(id -u)" = 10221; test "$(pwd)" = /data/user/0/com.videokit.app; '
snapshot=base+r'''
if [ ! -d /proc/7722 ]; then printf 'OWNER_ORIGINAL_PID_ABSENT\n'; exit 0; fi
emit_pid() {
 p=$1
 printf 'OWNER_STAT|%s|' "$p"; cat /proc/$p/stat
 printf 'OWNER_STATUS_BEGIN|%s\n' "$p"; /system/bin/toybox grep -E '^(Name|State|PPid|Uid|Gid):' /proc/$p/status; printf 'OWNER_STATUS_END|%s\n' "$p"
 h=$(/system/bin/toybox od -An -v -tx1 /proc/$p/cmdline | /system/bin/toybox tr -d ' \n'); printf 'OWNER_CMDHEX|%s|%s\n' "$p" "$h"
 l=$(/system/bin/toybox readlink /proc/$p/cwd); printf 'OWNER_CWD|%s|%s\n' "$p" "$l"
 l=$(/system/bin/toybox readlink /proc/$p/exe); printf 'OWNER_EXE|%s|%s\n' "$p" "$l"
}
emit_fd() {
 p=$1; n=$2
 if [ -L /proc/$p/fd/$n ]; then
  l=$(/system/bin/toybox readlink /proc/$p/fd/$n); printf 'OWNER_FD_LINK|%s|%s|%s\n' "$p" "$n" "$l"
  printf 'OWNER_FDINFO_BEGIN|%s|%s\n' "$p" "$n"; cat /proc/$p/fdinfo/$n; printf 'OWNER_FDINFO_END|%s|%s\n' "$p" "$n"
 fi
}
emit_pid 7722
for n in 0 1 2 3 4 5 6 7 8 9 10 11 12; do emit_fd 7722 "$n"; done
emit_pid 7718
for n in 0 1 2; do emit_fd 7718 "$n"; done
printf 'OWNER_APPDIR|'; /system/bin/toybox stat -c '%d|%i|%u|%f' .
printf 'OWNER_CWDDIR|'; /system/bin/toybox stat -c '%d|%i|%u|%f' /proc/7722/cwd/.
printf 'OWNER_ARCHIVE|'; /system/bin/toybox stat -c '%i|%u|%f' files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep
printf 'OWNER_SNAPSHOT_COMPLETE\n'
'''
try:
 raw=call('identity-and-fds',snapshot)
 if raw.strip()=='OWNER_ORIGINAL_PID_ABSENT':result['status']='ORIGINAL_PID_NOT_VISIBLE_NO_SIGNAL'
 else:
  lines=raw.splitlines();assert lines[-1]=='OWNER_SNAPSHOT_COMPLETE'
  def field(prefix):
   found=[x[len(prefix):] for x in lines if x.startswith(prefix)];assert len(found)==1;return found[0]
  stat=field('OWNER_STAT|7722|');assert stat.startswith('7722 (tee) ');parts=stat.rsplit(') ',1)[1].split();ticks=parts[19];assert parts[1]=='7718' and ticks.isdigit()
  status=raw.split('OWNER_STATUS_BEGIN|7722\n',1)[1].split('OWNER_STATUS_END|7722',1)[0]
  uid=next(x for x in status.splitlines() if x.startswith('Uid:')).split()[1:];assert uid==['10221']*4
  cmdhex=field('OWNER_CMDHEX|7722|');assert bytes.fromhex(cmdhex)==b'tee\x00files/e4_fixtures/basic.mp4\x00'
  cwd=field('OWNER_CWD|7722|');assert cwd in ['/data/user/0/com.videokit.app','/data/data/com.videokit.app']
  assert field('OWNER_APPDIR|').split('|')[:2]==field('OWNER_CWDDIR|').split('|')[:2]
  archive=field('OWNER_ARCHIVE|').split('|');assert archive[1]=='10221' and int(archive[2],16)&0o170000==0o100000
  candidates=[]
  for line in lines:
   if not line.startswith('OWNER_FD_LINK|7722|'):continue
   _,_,fd,link=line.split('|',3)
   if link not in [p+'/files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep' for p in ['/data/user/0/com.videokit.app','/data/data/com.videokit.app']]:continue
   info=raw.split(f'OWNER_FDINFO_BEGIN|7722|{fd}\n',1)[1].split(f'OWNER_FDINFO_END|7722|{fd}',1)[0];kv=dict(x.split(':',1) for x in info.splitlines() if ':' in x)
   if kv.get('ino','').strip()==archive[0] and int(kv['flags'].strip(),8)&3 in [1,2]:candidates.append((fd,link,archive[0]))
  assert len(candidates)==1
  fd,link,inode=candidates[0];result['originalIdentity']={'pid':7722,'ppid':7718,'startTicks':ticks,'uid':10221,'cmdlineHex':cmdhex,'cwd':cwd,'outputFd':int(fd),'outputLink':link,'outputInode':inode}
  new('conditional-admission.json',result['originalIdentity'])
  # All identity checks and the single signal are in this ONE original remote control command.
  control=base+f'''
s=$(cat /proc/7722/stat); case "$s" in '7722 (tee) '*) ;; *) exit 51;; esac
r=${{s##*) }}; set -- $r; test "$2" = 7718; shift 19; test "$1" = {q(ticks)}
u=$(/system/bin/toybox awk '/^Uid:/ {{print $2" "$3" "$4" "$5}}' /proc/7722/status); test "$u" = '10221 10221 10221 10221'
h=$(/system/bin/toybox od -An -v -tx1 /proc/7722/cmdline | /system/bin/toybox tr -d ' \\n'); test "$h" = {q(cmdhex)}
test "$(/system/bin/toybox readlink /proc/7722/cwd)" = {q(cwd)}
test "$(/system/bin/toybox readlink /proc/7722/fd/{fd})" = {q(link)}
i=$(/system/bin/toybox awk '/^ino:/ {{print $2}}' /proc/7722/fdinfo/{fd}); test "$i" = {q(inode)}
test "$(/system/bin/toybox stat -c '%i|%u|%f' files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep)" = {q('|'.join(archive))}
printf 'OWNER_RECHECK_COMPLETE|pid=7722|ticks={ticks}|uid=10221|fd={fd}|ino={inode}\\n'
printf 'OWNER_TERM_ATTEMPT|pid=7722\\n'
if /system/bin/toybox kill -TERM 7722; then printf 'OWNER_TERM_RETURN|rc=0\\n'; else r=$?; printf 'OWNER_TERM_RETURN|rc=%s\\n' "$r"; exit "$r"; fi
start=$(/system/bin/toybox date +%s%N); end=$((start+2000000000)); count=0
while [ "$count" -lt 20 ]; do
 if [ ! -d /proc/7722 ]; then printf 'OWNER_ORIGINAL_PROC_GONE|pid=7722|ticks={ticks}\\n'; exit 0; fi
 if ! s=$(cat /proc/7722/stat); then printf 'OWNER_OBSERVATION_UNKNOWN\\n'; exit 0; fi
 r=${{s##*) }}; set -- $r; state=$1; shift 19
 if [ "$1" != {q(ticks)} ]; then printf 'OWNER_ORIGINAL_IDENTITY_ENDED_PID_REUSED|pid=7722\\n'; exit 0; fi
 now=$(/system/bin/toybox date +%s%N); if [ "$now" -ge "$end" ]; then break; fi
 left=$((end-now)); if [ "$left" -lt 100000000 ]; then break; fi
 /system/bin/toybox sleep 0.1; count=$((count+1))
done
printf 'OWNER_ORIGINAL_STILL_VISIBLE_OR_UNPROVEN|pid=7722|state=%s\\n' "$state"
'''
  returned=call('conditional-term-and-observation',control);result['controlOutput']=returned;result['signalAttempts']=returned.count('OWNER_TERM_ATTEMPT|pid=7722')
  assert result['signalAttempts']==1 and 'OWNER_TERM_RETURN|rc=0' in returned
  result['status']='ORIGINAL_IDENTITY_ENDED' if 'OWNER_ORIGINAL_PROC_GONE|' in returned or 'OWNER_ORIGINAL_IDENTITY_ENDED_PID_REUSED|' in returned else 'TERM_RETURNED_END_UNPROVEN'
  result['postUidSnapshot']=call('one-post-uid-snapshot',base+"/system/bin/toybox ps -u 10221 -o PID,PPID,UID,ARGS")
except Exception as error:result['failure']={'type':type(error).__name__,'message':str(error)}
result.update(at=datetime.datetime.now().astimezone().isoformat(),metadataCommands=len(calls),retainedLocalOwners=ep.retained_owners(),nextDiagnosticOrPreloadAuthorized=False)
new('result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if ep.retained_owners():
 print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED_DO_NOT_TERMINATE',flush=True)
 while ep.retained_owners():time.sleep(1)
