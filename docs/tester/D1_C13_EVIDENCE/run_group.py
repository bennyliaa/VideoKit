"""C13 fail-stop coordinator: frozen single-method executor, bounded evidence, no retry/kill."""
import argparse,datetime,importlib.util,json,pathlib,re,subprocess,sys,threading
R=pathlib.Path(r'D:\CodexProjects\VideoKit');B=pathlib.Path(__file__).resolve().parent;ADB=r'D:\Android\SDK\platform-tools\adb.exe';TOOL=R/'docs/coder/d1c13/tools/run_device_c13.py'
spec=importlib.util.spec_from_file_location('c13executor',TOOL);sys.path.insert(0,str(TOOL.parent));executor=importlib.util.module_from_spec(spec);spec.loader.exec_module(executor)
p=argparse.ArgumentParser();p.add_argument('device',choices=['phone','tablet']);p.add_argument('group',choices=['cpu','host','legacy','pipeline','blocked']);a=p.parse_args();O=B/a.device
pre=json.loads((O/'preflight.json').read_text());SERIAL=pre['serial'];uids=pre['packages'];record=O/'results.json';results=json.loads(record.read_text()) if record.exists() else []
M='cpuMp4H264ActualPtsFrame';V='cpuAviMpeg4ActualPtsFrame'
cpu=[('cpuEnvironmentPreflight',[]),(M,[]),(V,[]),('cpuCleanupWithoutBindProvesNoWorker',[]),('cpuFirstFailureSurvivesCleanupFailure',[]),('cpuActualAggregateAllocationQuotaAndDecode',[M]),('cpuSeekUsesNewEpochAndDecodedTimestamp',[M]),('cpuOversizedDeclarationRejectedBeforeDecoderOpen',[V]),('cpuTruncatedInputRejectsAndReleases',[M]),('cpuValidAviHeaderBadPacketRejects',[V]),('cpuWrongDeclaredFormatRejects',[M,V]),('cpuCompiledH263DoesNotExpandAcceptedInputCodec',[V]),('cpuForgedFrameRejectedBeforeHostAllocation',[M]),('cpuForgedEpochAndClaimedIdentityRejected',[M]),('cpuUnknownAndEmptyLengthRejectWithActualClose',[]),('cpuCancelActiveReadRetainsPendingSourceLedger',[M]),('cpuCancelAfterActualFrame',[M]),('cpuHungTaskBoundedStopAndDeath',[M]),('cpuStopAckLossStillRequiresActualDeath',[M]),('cpuStalledStopDoesNotConsumeSecondRpcSlot',[M]),('cpuCancelFromMainThreadDoesNotBlockSecondTask',[M]),('cpuWrongStopEpochRejectedAndTaskContinues',[M]),('cpuOnewayStopRejectedAndTaskContinues',[M]),('cpuRegistrarSynchronousMetadataAndRejects',[M]),('cpuRegistrarLocalHostIdentityRejected',[]),('cpuRegistrationBadMagicPreservesFirstCause',[M]),('cpuRegistrationTrailingReplyPreservesFirstCause',[M]),('cpuCancelBeforeRegistrationClosesBindingAndRetainsUnknown',[M]),('cpuCancelBeforeBindReturnRevokesLateAcceptance',[M]),('cpuUnbindFailureRequiresExplicitRecovery',[M]),('cpuDuplicateConnectionKeepsOriginalIdentity',[M]),('cpuCancelDuringHelloCannotStartOrRevive',[M]),('cpuRejectedExtraWorkerRetainsSlotAndSecondTask',[M]),('cpuLateWorkerCannotBorrowOriginalDeath',[M]),('cpuExitCollectionRejectsMainThread',[]),('cpuSelfSigsegvSignalMustBeProven',[M]),('cpuSecondSlotAndHostSurviveFirstSelfCrash',[M])]
host=[('realEncoderOutput',[]),('outputValidationCounterexamples',[])]+[(m,['realEncoderOutput']) for m in ['exportReadyResponseLoss','exportWriteFault','exportFlushFault','exportValidationFault']]+[('writingJournalRecovery',[])]
N='isolatedActualEncodeAndReadyRecovery';legacy=[('nativeLeaseSurvivesDuplicateDescriptorClose',[]),(N,[])]+[(m,[N]) for m in ['cancelAfterActualVideoSample','workerExitDuringActualEncoding','workerSigsegvDuringActualEncoding','secondCodecTaskSurvivesFirstNativeCrash','actualHostDeathDuringEncodingAndCrossOwnerAbort','actualHostDeathAfterReadyAndSameTaskQuery']]
P='pipelineMp4RealFramesVideoOnly';A='pipelineAviRealFramesVideoOnly';pipe_names= json.loads((TOOL.parent/'device_plan.json').read_text(encoding='utf-8'))['groups']['pipeline'];pipeline=[(m,[M] if m==P else [V] if m==A else ['cpuEnvironmentPreflight'] if m=='pipelineOwnerRecoveryFencesIncompleteWriting' else [P,A]) for m in pipe_names]
plans={'cpu':cpu,'host':host,'legacy':legacy,'pipeline':pipeline};frozen=json.loads((TOOL.parent/'device_plan.json').read_text(encoding='utf-8'));assert all([m for m,d in plans[g]]==frozen['groups'][g] for g in plans);assert len(cpu)==37 and len(host)==7 and len(legacy)==8
(B/'plan.json').write_text(json.dumps(plans,indent=2),encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def save():record.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
if a.group=='blocked':
 assert json.loads((O/'environment.json').read_text())['state']=='ENVIRONMENT_BLOCKED'
 assert not results
 for group,plan in plans.items():
  for method,deps in plan:results.append(dict(device=a.device,serial=SERIAL,group=group,method=method,result='ENVIRONMENT_BLOCKED',reason='App disabled in actual preflight; no C13 install or instrumentation',dependency=deps,start=now(),end=now(),evidence='environment.json'))
 save();print('69 ENVIRONMENT_BLOCKED; no instrumentation dispatched');raise SystemExit(0)
for prior in results:
 if prior['result'] not in ['PASS','BLOCKED'] and not (O/prior.get('attempt','')/'review.json').is_file():raise RuntimeError('UNREVIEWED_FAILURE_STOP')
def remaining():return 33554432-sum(p.stat().st_size for p in O.rglob('*.log') if p.is_file())
def capture(parts,path,limit=1048576,timeout=25):
 return executor.capture([ADB,'-s',SERIAL]+parts,path,timeout,min(limit,remaining()))
def memory(parts,limit=1048576,timeout=25):
 """Bound reads too, retaining only task-specific filtered data afterwards."""
 proc=subprocess.Popen([ADB,'-s',SERIAL]+parts,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);chunks=[];error=[]
 def read():
  size=0
  try:
   while True:
    b=proc.stdout.read1(min(65536,limit-size+1))
    if not b:break
    size+=len(b)
    if size>limit:raise RuntimeError('BOUNDED_READ_EXCEEDED')
    chunks.append(b)
  except Exception as e:error.append(str(e));proc.kill()
 t=threading.Thread(target=read,daemon=True);t.start();t.join(timeout)
 if t.is_alive():proc.kill();t.join(2);raise RuntimeError('READ_DEADLINE')
 code=proc.wait(timeout=2);proc.stdout.close()
 if error or code:raise RuntimeError(error[0] if error else 'READ_COMMAND_FAILED')
 return b''.join(chunks).decode(errors='replace')
def output_budget():
 # Names are generated UUIDs; avoid consuming or changing any files.
 names=memory(['shell','run-as','com.videokit.app','find','cache','-type','f']).splitlines()
 names=[n for n in names if re.fullmatch(r'cache/d1_c13_[A-Za-z0-9_/.-]+',n)]
 size=0;pipe_bytes=0;pipe_tasks=0
 for name in names:
  n=memory(['shell','run-as','com.videokit.app','stat','-c','%s',name],limit=2048).strip();assert n.isdigit();size+=int(n)
  if name.startswith('cache/d1_c13_pipeline_outputs/'):
   pipe_bytes+=int(n);pipe_tasks+=int(name.endswith(('.task','.journal')))
   if name.endswith('.mp4'):assert int(n)<=2097152,'PIPE_SINGLE_OUTPUT_EXCEEDED'
 tasks=sum(n.endswith(('.task','.journal')) for n in names)
 (O/'output-budget-current.json').write_text(json.dumps(dict(bytes=size,taskRecords=tasks,limitBytes=8388608,limitTasks=32)),encoding='utf-8')
 assert size<=8388608 and tasks<=32,'OUTPUT_BUDGET_EXCEEDED'
 assert pipe_bytes<=4194304 and pipe_tasks<=24,'PIPELINE_OUTPUT_BUDGET_EXCEEDED'
 if a.group=='pipeline':assert pipe_bytes+2097152<=4194304 and size+2097152<=8388608 and pipe_tasks<24,'PIPELINE_RESERVATION_BLOCKED'
for method,deps in plans[a.group]:
 if any(r['method']==method for r in results):continue
 absent=[d for d in deps if not any(r['method']==d and r['result']=='PASS' for r in results)]
 if absent:
  results.append(dict(device=a.device,serial=SERIAL,group=a.group,method=method,result='BLOCKED',dependency=deps,reason='PRECONDITION_FAILED:'+','.join(absent),start=now(),end=now()));save();print('BLOCKED '+method,flush=True);continue
 if a.group!='cpu':output_budget()
 assert remaining()>1048576,'LOG_BUDGET_INSUFFICIENT_STOP'
 attempt=O/'attempts'/method;assert not attempt.exists(),'NO_RETRY_OR_OVERWRITE'
 start=now();device_start=memory(['shell','date '+chr(34)+'+%m-%d %H:%M:%S.000'+chr(34)],limit=2048).strip()
 print('START '+a.device+' '+a.group+' '+method+' '+start,flush=True)
 command=[sys.executable,str(TOOL),'--serial',SERIAL,'--method',method,'--group',a.group,'--attempt-dir',str(attempt),'--log-budget-root',str(O),'--execute','--candidate-and-data-reviewed']
 child=subprocess.run(command);state=json.loads((attempt/'result.json').read_text());post=attempt/'post';post.mkdir();ownlog='';ledger={};rawproof=[];notes=[];generations={};bindings={};unbinds={};pipeledgers={}
 result={'TEST_FAILED':'FAIL','ENVIRONMENT_BLOCKED':'ENVIRONMENT_BLOCKED','ENVIRONMENT_UNKNOWN':'ENVIRONMENT_UNKNOWN','PREPARATION_FAILED':'PREPARATION_FAILED','EXECUTION_UNKNOWN':'EXECUTION_UNKNOWN','CAPABILITY_BLOCKED':'CAPABILITY_BLOCKED'}.get(state['state'],'PASS')
 try:
  ownlog=capture(['logcat','-d','--uid='+str(uids['com.videokit.app']),'-v','threadtime','-T',device_start],post/'host.log',2097152)
  if a.group=='legacy':
   legacy_uid=memory(['shell','pm','list','packages','-U','com.videokit.worker.spike'],limit=4096);u=re.search(r'uid:(\d+)',legacy_uid);assert u;capture(['logcat','-d','--uid='+u.group(1),'-v','threadtime','-T',device_start],post/'legacy-worker.log')
  pairs=set(re.findall(r'pid=(\d+) uid=(\d+)',ownlog))
  for pid,uid in sorted(pairs):
   if int(pid)<1 or int(uid)%100000<90000:continue
   capture(['logcat','-d','--uid='+uid,'-v','threadtime','-T',device_start],post/('isolated-uid'+uid+'.log'))
  if any(x in method for x in ['Sigsegv','SelfCrash','NativeCrash']) or result=='FAIL':
   raw=memory(['logcat','-b','crash','-d','-v','threadtime','-T',device_start],limit=min(2097152,remaining()))
   blocks=re.split(r'(?=^.*\*\*\* \*\*\* \*\*\*)',raw,flags=re.M)
   for pid,uid in pairs:
    selected=[s for s in blocks if re.search(r'pid:\s*'+pid+r'\s*,',s) and re.search(r'uid:\s*'+uid+r'\b',s) and 'com.videokit.' in s]
    if selected:
     body='\n'.join(selected);encoded=body.encode();assert len(encoded)<remaining();(post/('tombstone-pid'+pid+'.log')).write_bytes(encoded)
     rawproof.append(dict(pid=int(pid),uid=int(uid),signal11=bool(re.search(r'signal 11\b',body))))
  for line in ownlog.splitlines():
   if 'stage=CPU_LEDGER ' in line:
    fields=dict(re.findall(r'(\w+)=([^\s]+)',line));ledger[fields['task']]=fields
  for line in ownlog.splitlines():
   fields=dict(re.findall(r'(\w+)=([^\s]+)',line))
   if 'stage=CPU_GENERATION_LEDGER ' in line:generations[fields['task']+':'+fields['generation']]=fields
   if 'stage=CPU_BINDING_LEDGER ' in line:bindings[fields['task']]=fields
   if 'stage=CPU_UNBIND_LEDGER ' in line:unbinds[fields['task']]=fields
   if 'stage=PIPE_LEDGER ' in line:pipeledgers[fields['export']]=fields
  for task,fields in unbinds.items():
   no_worker=ledger.get(task,{}).get('no_worker_proven')=='true'
   if fields.get('pending')!='false' or fields.get('bind_in_flight')!='false' or (fields.get('closed')!='true' and not no_worker):notes.append('FINAL_UNBIND_UNPROVEN')
  for fields in generations.values():
   if fields.get('actual_death')!='true' or fields.get('stop_pending')!='false':notes.append('FINAL_GENERATION_UNPROVEN')
  for task,fields in bindings.items():
   no_worker=ledger.get(task,{}).get('no_worker_proven')=='true'
   if (fields.get('binding_closed')!='true' and not no_worker) or fields.get('unresolved_workers')!='0':notes.append('FINAL_BINDING_UNPROVEN')
  if bindings and list(bindings.values())[-1].get('reserved_cpu_slots')!='0':notes.append('FINAL_GLOBAL_SLOT_UNPROVEN')
  for fields in ledger.values():
   if fields.get('slot_released')!='true' or fields.get('source_released')!='true' or fields.get('pending_calls')!='0' or fields.get('stop_pending')!='false':notes.append('FINAL_LEDGER_UNPROVEN')
  for fields in pipeledgers.values():
   if any(fields.get(k)!='true' for k in ['source_released','codec_released','writer_released','frames_released','resources_released']) or fields.get('encoder_output_slots')!='0' or fields.get('frame_consumers')!='0':notes.append('FINAL_PIPELINE_RESOURCE_UNPROVEN')
  if a.group=='pipeline' and method!='pipelineOwnerRecoveryFencesIncompleteWriting' and not pipeledgers:notes.append('FINAL_PIPELINE_LEDGER_MISSING')
  if a.group in ['cpu','pipeline'] and result=='PASS' and notes:result='EVIDENCE_INCOMPLETE'
  if a.group=='cpu' and method in ['cpuSelfSigsegvSignalMustBeProven','cpuSecondSlotAndHostSurviveFirstSelfCrash'] and result=='PASS' and not any(p['signal11'] for p in rawproof):result='EVIDENCE_INCOMPLETE';notes.append('EXTERNAL_SIGSEGV_UNPROVEN')
  processes=memory(['shell','ps','-A','-o','PID,UID,NAME'],limit=262144);lines=[s for s in processes.splitlines() if 'com.videokit.' in s];(post/'processes.log').write_text('\n'.join(lines),encoding='utf-8')
  active_workers=[s for s in lines if ':d1_cpu_worker' in s or ':d1_media_worker' in s]
  completion=any('INSTRUMENTATION_CODE:' in f.read_text(encoding='utf-8',errors='replace') for f in attempt.glob('*-command.log'))
  evidence=dict(deviceLogStart=device_start,commandReturned=child.returncode,instrumentationCompletion=completion,activeWorkerLines=active_workers,lastCpuLedger=ledger,lastGenerationLedger=generations,lastBindingLedger=bindings,lastUnbindLedger=unbinds,lastPipelineLedger=pipeledgers,rawProof=rawproof,reviewNotes=notes)
  (post/'evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 except Exception as error:
  result='EVIDENCE_INCOMPLETE' if result=='PASS' else result;notes.append('POST_COLLECTION_FAILED:'+str(error));(post/'collection-error.txt').write_text('\n'.join(notes),encoding='utf-8')
 r=dict(candidateId='D1-20261016-C13',device=a.device,serial=SERIAL,group=a.group,method=method,result=result,scriptState=state['state'],scriptCode=state['code'],dependency=deps,start=start,end=now(),attempt=str(attempt.relative_to(O)),deviceLogStart=device_start,notes=notes)
 results.append(r);save();print('END '+method+' '+result+' '+now(),flush=True)
 if result!='PASS':print('FAIL_STOP: inspect attempt/post/evidence.json before independent continuation',flush=True);raise SystemExit(2)
print('GROUP_FINISHED '+a.device+' '+a.group+' '+now(),flush=True)
