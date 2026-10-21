"""Exact official Gradle launcher arguments, scoped current-daemon read-only return handle.
No port probing, process enumeration, stop, kill or network/policy mutation."""
from pathlib import Path
import ctypes,datetime,hashlib,json,os,re,subprocess,sys,threading,time
B=Path(__file__).resolve().parents[1];E=B/'evidence';attempt=sys.argv[1];assert attempt in ['001','002'];assert not (E/'fix02-freeze.json').exists()
if attempt=='002':
 prior=json.loads((E/'build-001/owner.json').read_text());assert prior.get('daemonOriginalReturned') and prior.get('exitCode')==1 and prior.get('sourceCompileFailure')
D=E/('build-'+attempt);D.mkdir(exist_ok=False);G=Path('C:/Users/benny/.gradle/wrapper/dists/gradle-9.5.0-bin/bvnork1r7n8i6kp5cnkibsc9q/gradle-9.5.0');J=Path('D:/Android/Android Studio/jbr');HOME=B/'fix02-gradle-home'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
argv=[str(J/'bin/java.exe'),'-Xmx64m','-Xms64m','-javaagent:'+str(G/'lib/agents/gradle-instrumentation-agent-9.5.0.jar'),'-Dorg.gradle.appname=gradle','-jar',str(G/'lib/gradle-gradle-cli-main-9.5.0.jar'),'--offline','--no-daemon','--max-workers=2','--rerun-tasks','--info','--dependency-verification','strict','--init-script','tools/consumption.init.gradle','-Drender02.operations='+str(D/'consumption.jsonl'),':app:assembleDebug',':app:assembleDebugAndroidTest']
assert '-jar "%APP_HOME%\\lib\\gradle-gradle-cli-main-9.5.0.jar"' in (G/'bin/gradle.bat').read_text()
env=os.environ.copy();removed={}
for k in ['JAVA_TOOL_OPTIONS','_JAVA_OPTIONS','JDK_JAVA_OPTIONS','JAVA_OPTS','GRADLE_OPTS','CLASSPATH']:
 if k in env:removed[k]='CLEARED_WITHOUT_VALUE_DISCLOSURE';env.pop(k)
env['JAVA_HOME']=str(J);env['GRADLE_USER_HOME']=str(HOME)
start=time.monotonic();owner={'argv':argv,'cwd':str(B),'startUtc':now(),'observationSeconds':600,'heapClientMiB':64,'heapDaemonMiB':2048,'originalClientReturned':False,'daemonOriginalReturned':False,'killInterruptStopRetry':0,'deviceOrPortProbe':0,'scope':'D1_MEDIA3_ANDROID02_FIX02','attempt':attempt,'clearedInjectionKeys':removed,'launcherEquivalentToOfficialBat':True,'launcherScriptSha256':sha(G/'bin/gradle.bat'),'launcherJarSha256':sha(G/'lib/gradle-gradle-cli-main-9.5.0.jar')};dump(D/'owner.json',owner)
# Only hold the new daemon identified by THIS launcher's current log. Never enumerate processes.
kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];kernel.OpenProcess.restype=ctypes.c_void_p
kernel.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)];kernel.GetProcessTimes.argtypes=[ctypes.c_void_p]+[ctypes.POINTER(ctypes.c_uint64)]*4
kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32];kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];kernel.CloseHandle.argtypes=[ctypes.c_void_p]
daemon={};lock=threading.Lock();captureErrors=[]
def observe_line(line):
 match=re.search(rb'daemon \(pid: (\d+)\)|Daemon pid: (\d+)',line)
 if not match:return
 pid=int(next(x for x in match.groups() if x));
 with lock:
  if daemon:return
  handle=kernel.OpenProcess(0x100000|0x1000,False,pid)
  if not handle:daemon.update(pid=pid,handleUnavailableError=ctypes.get_last_error());return
  image=ctypes.create_unicode_buffer(32768);n=ctypes.c_uint32(len(image));created=ctypes.c_uint64();exitTime=ctypes.c_uint64();kt=ctypes.c_uint64();ut=ctypes.c_uint64()
  assert kernel.QueryFullProcessImageNameW(handle,0,image,ctypes.byref(n)) and Path(image.value).resolve()==(J/'bin/java.exe').resolve()
  assert kernel.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(exitTime),ctypes.byref(kt),ctypes.byref(ut))
  createdUnix=(created.value-116444736000000000)/10000000
  assert createdUnix>=datetime.datetime.fromisoformat(owner['startUtc']).timestamp()-1
  daemon.update(pid=pid,handle=handle,image=image.value,creationUtc=datetime.datetime.fromtimestamp(createdUnix,datetime.timezone.utc).isoformat(),creationFileTime=created.value,identitySource='THIS original Gradle client stdout daemon(pid); exact image and creation verified; handle retained')
def pump(pipe,name):
 try:
  total=0;line=b''
  with (D/(name+'.raw')).open('xb') as out:
   while True:
    data=pipe.read1(65536)
    if not data:break
    total+=len(data);out.write(data)
    if total>16777216:owner['outputBudgetExceeded']=True
    line+=data
    parts=line.split(b'\n');line=parts.pop()
    for item in parts:observe_line(item)
   if line:observe_line(line)
  pipe.close();owner[name+'Bytes']=total
 except BaseException as e:captureErrors.append(type(e).__name__)
with subprocess.Popen(argv,cwd=B,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False) as p:
 owner['clientPid']=p.pid;dump(D/'owner.json',owner)
 # Non-daemon readers retain original streams if the observation window expires.
 threads=[threading.Thread(target=pump,args=(p.stdout,'stdout')),threading.Thread(target=pump,args=(p.stderr,'stderr'))]
 for t in threads:t.start()
 try:code=p.wait(max(1,600-(time.monotonic()-start)))
 except subprocess.TimeoutExpired:
  owner.update(status='UNKNOWN_ORIGINAL_CLIENT_RETURN_PENDING',endObservationUtc=now());dump(D/'owner.json',owner)
  # Retain the same originals without cancellation, relaunch or forced cleanup.
  code=p.wait()
  owner['lateClientReturn']=True
 owner.update(exitCode=code,clientReturnUtc=now(),originalClientReturned=True)
 for t in threads:t.join()
 owner['captureHandlesClosed']=all(not t.is_alive() for t in threads) and not captureErrors
 owner['captureErrors']=captureErrors
if daemon.get('handle'):
 handle=daemon.pop('handle');wait=kernel.WaitForSingleObject(handle,int(max(0,600-(time.monotonic()-start))*1000));daemon['waitResult']=wait
 if wait==0:
  code=ctypes.c_uint32();assert kernel.GetExitCodeProcess(handle,ctypes.byref(code));daemon['exitCode']=code.value;daemon['sameHandleSignalled']=True;owner['daemonOriginalReturned']=True
 kernel.CloseHandle(handle)
owner['daemon']=daemon
log=HOME/'daemon/9.5.0'/('daemon-'+str(daemon.get('pid','UNOBSERVED'))+'.out.log')
if log.exists():
 data=log.read_bytes();assert len(data)<=16777216;(D/'single-use-daemon.raw.log').write_bytes(data);text=data.decode('utf-8',errors='replace');uid=re.search(r'DefaultDaemonContext\[uid=([^,]+)',text);owner['daemonUid']=uid.group(1) if uid else None;owner['daemonLogSha256']=hashlib.sha256(data).hexdigest();owner['daemonLogShutdownMessageObserved']='Daemon vm is shutting down' in text
raw=(D/'stdout.raw').read_text(encoding='utf-8',errors='replace')+(D/'stderr.raw').read_text(encoding='utf-8',errors='replace')
owner.update(transportFailure='Could not connect to the Gradle daemon' in raw,sourceCompileFailure=bool(re.search(r'compileDebug(?:AndroidTest)?JavaWithJavac FAILED',raw)) and 'error:' in raw,status='BUILD_RETURNED',endUtc=now())
if owner.get('lateClientReturn') or not owner['daemonOriginalReturned']:owner['status']='UNKNOWN_ORIGINAL_RETURN_NOT_FULLY_PROVEN'
if owner.get('outputBudgetExceeded'):owner['status']='OUTPUT_BUDGET_EXCEEDED_NO_NEXT_TASK'
dump(D/'owner.json',owner);print(json.dumps(owner,ensure_ascii=False));assert owner['captureHandlesClosed'] and owner['daemonOriginalReturned'] and not owner.get('lateClientReturn') and not owner.get('outputBudgetExceeded')
sys.exit(owner['exitCode'])
