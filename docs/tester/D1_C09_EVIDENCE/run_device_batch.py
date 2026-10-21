import argparse,datetime,hashlib,io,json,pathlib,re,subprocess,tarfile
B=pathlib.Path(__file__).resolve().parent;ADB=r'D:\Android\SDK\platform-tools\adb.exe'
p=argparse.ArgumentParser();p.add_argument('device',choices=['phone','tablet']);p.add_argument('group',choices=['cpu','host','legacy']);p.add_argument('--continue-after-environment-fix',action='store_true');a=p.parse_args()
O=B/a.device;pre=json.loads((O/'preflight.json').read_text());SERIAL=pre['serial']
def adb(parts,timeout=30):return subprocess.run([ADB,'-s',SERIAL]+parts,capture_output=True,timeout=timeout)
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
uidtext=(O/('uids-legacy.txt' if a.group=='legacy' else 'uids.txt')).read_text();uids={m.group(1):m.group(2) for m in re.finditer(r'package:(\S+) uid:(\d+)',uidtext)}
record=O/'results.json';results=json.loads(record.read_text()) if record.exists() else []
M='cpuMp4H264ActualPtsFrame';V='cpuAviMpeg4ActualPtsFrame'
if a.group=='cpu':
 plan=[(M,[]),(V,[]),('cpuSeekUsesNewEpochAndDecodedTimestamp',[M]),('cpuActualAggregateAllocationQuotaAndDecode',[M]),('cpuOversizedDeclarationRejectedBeforeDecoderOpen',[V]),('cpuTruncatedInputRejectsAndReleases',[M]),('cpuValidAviHeaderBadPacketRejects',[V]),('cpuWrongDeclaredFormatRejects',[M,V]),('cpuCompiledH263DoesNotExpandAcceptedInputCodec',[V]),('cpuForgedFrameRejectedBeforeHostAllocation',[]),('cpuForgedEpochAndClaimedIdentityRejected',[]),('cpuUnknownAndEmptyLengthRejectWithActualClose',[]),('cpuCancelActiveReadRetainsPendingSourceLedger',[M]),('cpuCancelAfterActualFrame',[M]),('cpuHungTaskBoundedStopAndDeath',[M]),('cpuSelfSigsegvSignalMustBeProven',[M]),('cpuSecondSlotAndHostSurviveFirstSelfCrash',[M])]
 cls='C09CpuDeviceTests'
elif a.group=='host':
 plan=[('realEncoderOutput',[]),('outputValidationCounterexamples',[])]+[(m,['realEncoderOutput']) for m in ['exportReadyResponseLoss','exportWriteFault','exportFlushFault','exportValidationFault']]+[('writingJournalRecovery',[])]
 cls='C09DeviceTests'
else:
 N='isolatedActualEncodeAndReadyRecovery';plan=[('nativeLeaseSurvivesDuplicateDescriptorClose',[]),(N,[])]+[(m,[N]) for m in ['cancelAfterActualVideoSample','workerExitDuringActualEncoding','workerSigsegvDuringActualEncoding','secondCodecTaskSurvivesFirstNativeCrash','actualHostDeathDuringEncodingAndCrossOwnerAbort','actualHostDeathAfterReadyAndSameTaskQuery']];cls='C09IsolatedDeviceTests'
assert len(plan)=={'cpu':17,'host':7,'legacy':8}[a.group]
halt=None
app_state=adb(['shell','dumpsys','package','com.videokit.app']).stdout.decode(errors='replace')
enabled_match=re.search(r'User 0:.*?enabled=(\d+)',app_state)
environment=None if enabled_match and int(enabled_match.group(1)) in [0,1] else 'WAITING_FOR_USER_ENABLE_OR_PACKAGE_STATE_UNKNOWN'
def budget():
 logs=sum(f.stat().st_size for f in O.glob('*.log'))
 if logs>33554432:return 'LOG_BUDGET_EXCEEDED'
 if a.group=='cpu':return None
 r=adb(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],60)
 if r.returncode:return 'CACHE_BUDGET_NOT_OBSERVABLE'
 with tarfile.open(fileobj=io.BytesIO(r.stdout)) as t:
  files=[m for m in t.getmembers() if m.isfile() and m.name.startswith('cache/d1_c09_')]
  size=sum(m.size for m in files);tasks=sum(m.name.endswith(('.task','.journal')) for m in files)
 (O/('budget-'+a.group+'.json')).write_text(json.dumps(dict(bytes=size,terminalTaskRecords=tasks,limitBytes=8388608,limitTasks=32)),encoding='utf-8')
 if size>8388608 or tasks>32:return 'OUTPUT_BUDGET_EXCEEDED'
 return None
for method,deps in plan:
 if a.continue_after_environment_fix and any(r['method']==method and r['result']=='PASS' for r in results):
  print('PRESERVE_PRIOR_PASS '+method,flush=True);continue
 assert not any(r['method']==method for r in results),'NO_UNPLANNED_RETRY'
 start=now();device_start=adb(['shell','date '+chr(34)+'+%m-%d %H:%M:%S.000'+chr(34)]).stdout.decode().strip()
 print('START '+a.device+' '+a.group+' '+method+' '+start,flush=True)
 missing=[d for d in deps if not any(r['method']==d and r['result']=='PASS' for r in results)]
 needs_service=a.group=='legacy' or (a.group=='cpu' and method!='cpuUnknownAndEmptyLengthRejectWithActualClose')
 reason=halt or (environment if needs_service else None) or ('PRECONDITION_FAILED:'+','.join(missing) if missing else None)
 if not reason:reason=budget()
 command=['shell','am','instrument','-w','-e','class','com.videokit.spike.c09.'+cls+'#'+method,'com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner']
 limit=360 if method=='secondCodecTaskSurvivesFirstNativeCrash' else (240 if a.group=='legacy' else 180)
 if reason:status,code,output='BLOCKED',None,reason
 else:
  try:
   r=adb(command,limit);output=(r.stdout+r.stderr).decode(errors='replace');code=r.returncode
   status='PASS' if code==0 and 'OK (1 test)' in output and 'FAILURES!!!' not in output else 'FAIL'
  except subprocess.TimeoutExpired as e:
   output=((e.stdout or b'')+(e.stderr or b'')).decode(errors='replace')+'\nEXTERNAL_TIMEOUT: no cleanup stop or release claim\n';status,code='BLOCKED',None;halt='EXTERNAL_TIMEOUT_RESOURCE_STATE_UNKNOWN';reason=halt
  hostlog=''
  for package in (['com.videokit.app','com.videokit.worker.spike'] if a.group=='legacy' else ['com.videokit.app']):
   uid=uids[package];r=adb(['logcat','-d','--uid='+uid,'-v','threadtime','-T',device_start])
   raw=r.stdout+r.stderr
   if len(raw)>4194304:raw=raw[-4194304:];halt='LOG_OUTPUT_TRUNCATED_REVIEW_REQUIRED'
   (O/(method+'-uid'+uid+'.log')).write_bytes(raw)
   if package=='com.videokit.app':hostlog=raw.decode(errors='replace')
  pids=set(re.findall(r'pid=(\d+)',hostlog))
  isolated_uids=set(re.findall(r'uid=(\d+)',hostlog))
  for isolated_uid in sorted(isolated_uids):
   if int(isolated_uid)%100000<90000:continue
   r=adb(['logcat','-d','--uid='+isolated_uid,'-v','threadtime','-T',device_start])
   (O/(method+'-isolated-uid'+isolated_uid+'.log')).write_bytes((r.stdout+r.stderr)[-4194304:])
  for pid in sorted(pids):
   if int(pid)<=0:continue
   r=adb(['logcat','-b','crash','-d','-v','threadtime','-T',device_start])
   blocks=re.split(r'(?=^.*\*\*\* \*\*\* \*\*\*)',r.stdout.decode(errors='replace'),flags=re.MULTILINE)
   own=[s for s in blocks if re.search(r'pid:\s*'+pid+r'\s*,',s) and 'com.videokit.' in s]
   if own:(O/(method+'-tombstone-pid'+pid+'.log')).write_text('\n'.join(own),encoding='utf-8')
  if a.group=='cpu' and ('released=false' in hostlog or 'failedClose=1' in hostlog):
   (O/(method+'-resource-review.txt')).write_text('Inspect actual ledger; no force-stop used to manufacture release.',encoding='utf-8')
 (O/(method+'.log')).write_text(output,encoding='utf-8')
 results.append(dict(candidateId='D1-20261016-C09',device=a.device,serial=SERIAL,group=a.group,method=method,className=cls,start=start,end=now(),result=status,processExitCode=code,reason=reason,dependency=deps,timeoutSeconds=limit,deviceLogStart=device_start,log=method+'.log',command=[ADB,'-s',SERIAL]+command))
 record.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 print('END '+method+' '+status+' '+now(),flush=True)
 if status=='BLOCKED' and reason and 'BUDGET' in reason:halt=reason
if halt:(O/('halt-'+a.group+'.txt')).write_text(halt,encoding='utf-8')
snapshot=adb(['shell','ps','-A','-o','PID,UID,NAME']);lines=[line for line in snapshot.stdout.decode(errors='replace').splitlines() if 'com.videokit.' in line]
(O/('processes-after-'+a.group+'.txt')).write_text('\n'.join(lines),encoding='utf-8')
print('GROUP_FINISHED '+a.device+' '+a.group+' '+now(),flush=True)
