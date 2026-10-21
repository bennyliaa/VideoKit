from pathlib import Path
import json,hashlib,datetime,zipfile,stat,re,collections
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1fixture-six01-evidence';T=R/'docs/coder/d1fixture-tool02';MEDIA='docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4'
E.mkdir(exist_ok=True)
assert not (E/'independent-review.json').exists(),'IMMUTABLE_ONCE_REVIEW_NO_REPLAY'
reads=[]
def sha(p,kind='CONTROL_IDENTITY'):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for x in iter(lambda:f.read(65536),b''):n+=len(x);h.update(x)
 if p==R/MEDIA:reads.append(dict(kind=kind,source='ORIGINAL_MEDIA',bytes=n,driverInputCharged=False))
 return h.hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
seal=B/'fixture-six01-freeze.json';assert sha(seal)=='ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4';s=load(seal)
assert len(s['files'])==38 and len({x['path'] for x in s['files']})==38
report=R/'docs/coder/D1_FIXTURE_SIX01_GENERATE_DELIVERY_V1.0.md';assert sha(report)=='27a370bbb5b39cc0b9c8e81a9ea3a9ec4806f043f21415914e34ab125122ca03'
audited=[]
for x in s['files']:
 p=R/x['path'];a=p.stat();assert p.is_file() and not p.is_symlink() and a.st_size==x['bytes'];actual=sha(p,'FROZEN38_IDENTITY_HASH');assert actual==x['sha256'];audited.append(dict(**x,independentSha256=actual))
with zipfile.ZipFile(R/s['archive']['path']) as z:
 rows={x['path']:x for x in s['files'] if x['path']!=s['archive']['path']}
 assert len(z.namelist())==len(set(z.namelist()))==37 and set(z.namelist())==set(rows)
 for n,x in rows.items():
  assert z.getinfo(n).file_size==x['bytes'];v=z.read(n);assert hashlib.sha256(v).hexdigest()==x['sha256']
  if n==MEDIA:reads.append(dict(kind='ZIP_MEMBER_HASH_AND_CRC_SINGLE_READ',source='ARCHIVE_MEDIA_COPY',bytes=len(v),driverInputCharged=False))
toolSeal=T/'evidence/fixture-tool02-freeze.json';assert sha(toolSeal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d';tool=load(toolSeal)
for x in tool['files']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert len(tool['files'])==2774
for x in load(T/'evidence/compiler-identity.json')['files']:
 p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert load(B/'reference/compiler-identity.json')==load(T/'evidence/compiler-identity.json')
for p in (B/'reference/frozen-tool02-driver').glob('*.java'):assert p.read_bytes()==(T/'driver/com/videokit/fixturetool'/p.name).read_bytes()
for p in (B/'reference/tool-licenses').iterdir():assert p.read_bytes()==(T/'licenses'/p.name).read_bytes()
prior=[]
for rel,expected in [('D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/review-evidence-manifest.json','4cf38051ed21b927da639418ef9ef58629219fbe042645f46b0ccf946c900109'),('D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE/phase-a-evidence-manifest.json','b4a85884adf6fca216131f0ed46ff41a5e8692f822146016edb96708f143c5e2'),('D1_FIXTURE_SIX01_QUALIFIER_PREPARATION/review-evidence-manifest.json','6c570d2ac81c20f3bebf28d141c92edf85a153ccecfe7462e367ea8f011d412f')]:
 p=R/'docs/tester'/rel;assert sha(p)==expected;v=load(p);assert sha(R/v['report'])==v['reportSha256']
 for x in v['evidenceFiles']:q=R/x['path'];assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
 prior.append(dict(manifest=rel,sha256=expected,unchangedEvidenceFiles=len(v['evidenceFiles'])))
stdout=(B/'control-001/stdout.raw').read_bytes();stderr=(B/'control-001/stderr.raw').read_bytes();assert len(stdout)==12297 and len(stderr)==0 and len(stdout)+len(stderr)<=1048576
text=stdout.decode('utf8',errors='strict');assert stderr.decode('utf8',errors='strict')==''
lines=text.splitlines();receipts=[json.loads(x) for x in lines];assert len(receipts)==1 and all(isinstance(x,dict) for x in receipts)
assert load(B/'control-001/nonreceipt-output-lines.json')==[] and load(B/'control-001/all-original-json-receipts.json')==receipts
r=receipts[0];assert load(B/'last-original-driver-receipt.json')==r
assert r['tool']=='D1_FIXTURE_TOOL02_FIX' and r['scopeLabelNotAuthorization']=='D1GEN01-CANDIDATE-001' and r['status']=='GENERATED_CANDIDATE_NOT_QUALIFIED' and r['firstError'] is None
assert not any(x['deadlineUnknownSticky'] or x['status'].startswith('UNKNOWN') for x in receipts)
for n,data in [('original-stdout.raw',stdout),('original-stderr.raw',stderr)]:
 with (E/n).open('xb') as f:f.write(data)
o=load(B/'control-001/owner.json');pre=load(B/'control-001/preflight.json');g=load(B/'generation-result.json');m=load(B/'media-manifest.json');cv=load(B/'budget-and-return-validation.json');post=load(R/'docs/coder/D1_FIXTURE_SIX01_GENERATE_POST_FREEZE_RECEIPT.json')
expectedArgv=['D:/Android/Android Studio/jbr/bin/java.exe','-Xmx256m','-XX:-UsePerfData','-jar','D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar','--generate-six','--scope=D1GEN01-CANDIDATE-001']
assert o['argv']==expectedArgv and Path(o['cwd'])==B/'control-001' and o['processInvocations']==1 and o['state']=='ORIGINAL_NATURAL_RETURN' and o['exitCode']==0
assert o['originalProcessReturned'] and o['stdoutHandleClosed'] and o['stderrHandleClosed'] and not o['controllerObservationUnknownSticky'] and not o['receiptBudgetExceededSticky'] and o['killInterruptSecondCloseRetryRefundActions']==0
assert set(o['environmentInjectionKeysCleared'])=={'JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH'} and all(not x['presentAfterClear'] for x in o['environmentInjectionKeysCleared'].values())
assert datetime.datetime.fromisoformat(o['registeredUtc'])<datetime.datetime.fromisoformat(pre['checkedUtc'])<=datetime.datetime.fromisoformat(o['startUtc'])<datetime.datetime.fromisoformat(o['endUtc']) and 0<=o['elapsedSeconds']<60
assert g['originalProcessOwner']==o and g['generationInvocations']==1 and all(g['requirements'].values()) and g['output']==s['output']==m['file']
assert pre['outputRootAbsent'] and pre['controllerDidNotCreateOutputRoot'] and not pre['inputOriginalMediaOpened'] and pre['oldSessionQueriesOrInterventions']==0
originalReq=B/'reference/D1_FIXTURE_SIX01_GENERATE_CODER_REQUIREMENTS_V1.0.md';assert sha(originalReq)==pre['requirementsSha256']
controller=(B/'run_once.py').read_text();assert controller.count('subprocess.Popen(')==1 and 'shell=False' in controller and 'code=proc.wait()' in controller and 'out.close()' in controller and 'err.close()' in controller
assert not any(x in controller for x in ['proc.kill(', 'proc.terminate(', 'subprocess.run(', 'os.kill('])
for who in ['writer','reader']:
 a=r[who];assert a['ownerRegisteredBeforeOpen'] and a['state']=='CLOSE_RETURNED' and a['closeAttempted'] and a['sameOriginalCloseReturned']
assert r['writer']['forceAttempted'] and r['writer']['forceReturned'] and r['writer']['finalSizeObservedBeforeClose']==8849 and not r['reader']['forceAttempted']
assert r['reader']['nativeReadCalls']==2 and r['reader']['nativeReadBytes']==8849 and r['reader']['nativeEofCalls']==1
for k in ['workerBodyCleanupCompleted','sameWorkerExternallyJoined','originalResourceOwnersReturned','directoryCreatedByThisRun','rootCreatedByThisRun','encoderCreationReturned','muxCreationReturned','muxFinishReturned','outputReadOnly','wholeOutputEof','noForceKillInterruptSecondCloseOrRefund']:assert r[k] is True
for k in ['admissionClosed','deadlineUnknownSticky','directoryDeleted','unknownOwnersStronglyRetained','allocationUnknown','qualifiedFixture','e6EmptyEosWritten']:assert r[k] is False
d=r['workerDeadline'];assert d['bodyCompletedNanoTime']-d['startNanoTime']==d['completionElapsedNanos']==152633600 and d['observerElapsedNanos']>=d['completionElapsedNanos'] and d['completionElapsedNanos']<d['deadlineNanos']==60000000000
assert d['completionPointRecordedBySameWorker'] and d['sameOriginalExternallyJoined'] and d['timelyBodyAndOriginalJoin'] and not d['deadlineUnknownSticky'] and not d['invalidMonotonicRange'] and d['equalDeadlineIsLate']
b=r['outputBudget'];ev=b['nativeOperationEvents'];close=b['terminalCloseEvent'];assert len(ev)==19 and close==dict(operation='CLOSE',nativeCall=20,outcome='RESULT_ADOPTED')
assert [x['nativeCall'] for x in ev]==list(range(1,20)) and all(x['outcome']=='RESULT_ADOPTED' for x in ev)
attempt=0;returned=0;pos=0;extent=0;rw=0;events=[];counts=collections.Counter()
for x in ev:
 op=x['operation'];counts[op]+=1;assert x['knownReturnedBefore']==returned and x['lastAcknowledgedPositionBefore']==pos
 if op=='WRITE':
  n=x['requestedAndReserved'];assert 0<n<=65536 and 0<x['returned']<=n and x['sourceBufferPositionAfter']-x['sourceBufferPositionBefore']==x['returned']
  if pos<extent:rw+=n
  attempt+=n;returned+=x['returned'];pos+=x['returned'];extent=max(extent,pos)
  assert x['knownReturnedAfter']==returned and x['knownPositionAfter']==pos and x['knownExtentAfter']==extent
 else:
  assert x['requestedAndReserved']==0
  if op=='SEEK':assert ev[x['nativeCall']]['operation']=='WRITE';pos=ev[x['nativeCall']]['lastAcknowledgedPositionBefore']
  if op=='SIZE':assert x['nativeSize']==8849
 assert x['attemptedCumulative']==attempt
 events.append(dict(nativeCall=x['nativeCall'],operation=op,cumulativeRequested=attempt,cumulativeReturned=returned,lastAdoptedPosition=pos,lastAdoptedExtent=extent))
assert counts==dict(WRITE=9,POSITION=7,SEEK=1,FORCE=1,SIZE=1)
assert attempt==returned==b['attemptedBytes']==b['acknowledgedLowerBound']==8857 and rw==b['headerOrOtherRewriteAttemptedBytes']==8 and pos==56 and extent==8849
for k in ['nativeCallsEntered','nativeReturnsObserved','resultsAdopted']:assert b[k]==20
for k in ['nativeThrowsObserved','nativeInFlight','resultAdoptionPending','queued','initialMeterOnlyReservation','budgetRefundedBytes']:assert b[k]==0
assert b['activeOperation']=='NONE' and b['peakNativeInFlight']==1 and b['seekCallsAttempted']==b['seekResultsAdopted']==1 and b['forceResultAdopted'] and b['originalCloseResultAdopted'] and not b['failedOrUncertain'] and not b['physicalUnknownSticky']
assert b['lastAcknowledgedLogicalPosition']==b['actualPhysicalPosition']==56 and b['acknowledgedExtentLowerBound']==b['actualPhysicalExtent']==8849 and b['physicalValueScope']=='LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE'
assert r['sourceOwnersMax']==2 and r['nativeOwnersLive']==0 and r['nativeOwnersPeak']==1 and r['queue']==0
pixels=6*256*144*3//2;assert pixels==331776 and r['inputActuallyObserved']==pixels+8849==340625 and r['inputAttemptedReserved']==pixels+8849+1==340626<=8388608
assert attempt<=16777216 and len(ev)<=512 and max(x['requestedAndReserved'] for x in ev)==1340
au=r['sixRawEncoderSamples'];assert len(au)==6 and au==m['rawEncoderAuObservations'] and r['actualMuxTrackCsd']==m['internalCsdObservations']
for i,x in enumerate(au):
 assert x['index']==i and x['ptsUnits']==i and x['timescale']==5 and x['durationUnits']==1 and x['ptsUs']==i*200000 and x['isKeyframe'] and x['actualIdrNalObserved'] and x['rawEncoderAnnexBBytes']==1360<=262144
 assert re.fullmatch('[0-9a-f]{64}',x['rawEncoderAnnexBSha256']) and [n['type'] for n in x['nals']]==[7,8,5]
 assert sum(n['bytes']+4 for n in x['nals'])==1360 and all(re.fullmatch('[0-9a-f]{64}',n['sha256']) for n in x['nals'])
assert sum(x['rawEncoderAnnexBBytes'] for x in au)==8160<=1572864 and not m['rawAuBytesPreserved'] and not m['rawAuHashesIndependentlyRecomputed']
csd=[]
for x in r['actualMuxTrackCsd']:
 v=bytes.fromhex(x['hex']);assert len(v)==x['bytes'] and hashlib.sha256(v).hexdigest()==x['sha256'];csd.append(dict(kind=x['kind'],bytes=len(v),sha256=hashlib.sha256(v).hexdigest(),result='PASS_RECEIPT_HEX_SELF_CONSISTENCY_ONLY_NOT_FILE_EXTRACTION'))
assert [x['bytes'] for x in csd]==[7,3,20] and sum(x['bytes'] for x in csd)==30 and r['rawCsdObservedCumulativeBytes']==120<=65536
assert r['packetTimescaleDeclared']==5 and r['actualMuxTrackDurationUnits']==6 and r['expectedPacketEndUs']==1200000 and r['packetDurationObserved'] and r['actualIndependentContainerDuration']=='NOT_RUN'
assert m['independentContainerDurationUs'] is None and m['independentContainerTrackOrSampleMap'] is None and m['actualMedia3Qualification'] is None and not m['newAndroidEmbedding'] and not m['decodePlaybackIsolatedValidationReadyCommit']
assert r['media3Qualification']==r['platformIsolationOrPlayback']=='NOT_RUN'
mp=R/MEDIA;a=mp.stat();assert a.st_size==r['outputBytes']==8849 and (a.st_file_attributes&stat.FILE_ATTRIBUTE_READONLY) and not (a.st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT) and not mp.is_symlink()
assert r['outputSha256']==s['output']['sha256']=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c'
assert sha(mp,'POST_REVIEW_PRESERVATION_HASH')==r['outputSha256'] and mp.stat().st_file_attributes==a.st_file_attributes
assert cv['writeRequestedSum']==attempt and cv['validWriteReturnedSum']==returned and cv['inputAttemptedReserved']==340626 and cv['inputActuallyObserved']==340625 and cv['physicalOutputSize']==8849 and cv['nativeCallsReturnsAdoptions']==20
assert post['frozenRowsUnchanged']==38 and post['zipMembersMatched']==37 and post['controllerExecEvidence']['originalPythonControllerExitCode']==0 and post['controllerExecEvidence']['generationPopenNaturalExitCode']==0
for x in s['externalPreservationLedger']['entries']:assert x['bytes']==8849 and not x['driver8MiBLedger']
assert s['externalPreservationLedger']['originalMediaDirectBytes']==35396 and s['externalPreservationLedger']['archiveCopyMediaBytes']==17698
oracles=load(R/'docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE/independent-gs01-gs24-oracles.json')['cases'];coder=load(B/'gs01-gs24-completion-matrix.json')['rows'];assert len(oracles)==len(coder)==24
rows=[]
notes={1:'准确scope/argv/JAR/JDK/原许可快照一致；旧plan不改',2:'正常准入原记录吻合；已有目录/身份错误拒绝分支未运行',3:'原创像素公式与固定driver/许可证链一致；非专利/发行许可',4:'同原Popen及两流/环境清理返回记录与控制器源码吻合，未用PID查询替代',5:'原12297B stdout+0 stderr完整审阅，一final零pending零杂行',6:'原body152633600ns与实际join/原进程返回分层；超时负例未运行',7:'候选状态、firstError/null、timely、EOF/close/join及外部身份全吻合',8:'没有本次pending/超界/异常；负例未运行，不能凭正常返回冒覆盖',9:'固定新路径、driver独占create与原owner-before-open记录/源码吻合',10:'writer实际finish/force/close返回记录齐；不代业务COMMIT或掉电持久化',11:'原只读reader2calls/8849bytes/EOF1/close返回；live0仅辅助',12:'9WRITE requested/returned8857含8rewrite；初始预留0退款0；partial分支未运行',13:'20entered/returned/adopted，inFlight0、uncertain false、close后LAST_CONFIRMED',14:'position56与extent/真实size8849分层，attempt8857不得以size代替',15:'inputReserved340626/observed340625含像素331776/文件8849/EOF预留1；外读另账',16:'六AU各1360总8160/IDR/key/NAL仅原内部观察；缺raw bytes不能重算hash',17:'CSD三表示7/3/20B hex/hash自一致通过，非文件提取；raw PS120B',18:'Packet单位0..5/scale5/duration1、内部duration6吻合；真实文件时长未查',19:'实际媒体8849B/准确SHA/只读属性与原EOF/hash一致，仅身份',20:'真实轨道/sample/PTS-DTS/duration/CSD独立提取全部null/NOT_RUN',21:'原成熟库Date保留，仅冻结本次hash，不保证重生成hash',22:'seal38/ZIP37、tool2774、原报告/阶段A/准备证据均原样；新增B另封存',23:'旧48945/17257 UNKNOWN未查询或干预；不证明host全空闲',24:'本B只Python证据/身份；helper编译已另封存，实际运行/Android另准确批'}
for i,(x,y) in enumerate(zip(oracles,coder),1):
 assert x['id']==y['id']==f'GS{i:02}' and x['oracle']==y['oracle'] and x['status']=='PREPARED_NOT_RUN' and y['phaseAStatusPreserved']=='PREPARED_NOT_RUN'
 status='PASS_EVIDENCE_ONLY'
 if i in [2,8]:status='PASS_NORMAL_PATH_RECORD_NEGATIVE_BRANCH_NOT_RUN'
 if i==16:status='PASS_INTERNAL_OBSERVATION_RECORD_RAW_HASH_NOT_RECOMPUTED'
 if i==17:status='PASS_RECEIPT_CSD_SELF_CONSISTENCY_ONLY'
 if i==18:status='PASS_INTERNAL_TIMEBASE_RECORD_FILE_TIMELINE_NOT_RUN'
 if i==20:status='PASS_LIMITATION_DISCLOSURE_CONTAINER_NOT_RUN'
 rows.append(dict(id=x['id'],area=x['area'],oracle=x['oracle'],status=status,independentEvidenceResult=notes[i],actualContainerQualification='NOT_RUN',phaseAStatusPreserved='PREPARED_NOT_RUN'))
save('independent-gs01-gs24-results.json',dict(overall='PASS_GENERATION_EVIDENCE_AND_FILE_IDENTITY_ONLY',cases=rows,actualContainerQualification='NOT_RUN',negativeFailureBranches='NOT_RUN'))
save('independent-event-ledger.json',dict(events=events,terminalClose=close,counts=dict(counts),attemptedBytes=attempt,validReturnedBytes=returned,headerRewriteBytes=rw,lastAdoptedPosition=pos,lastAdoptedExtent=extent,physicalSize=8849,inputReserved=340626,inputObserved=340625,syntheticPixels=pixels,originalFileReadBytes=8849,eofReservedBytes=1,receiptCsdSelfConsistency=csd,rawAuIndependentRecomputation=False))
save('frozen-input-validation.json',dict(reportSha256=sha(report),sealSha256=sha(seal),frozenRecords=audited,zipUniqueMembers=37,tool02FrozenRowsUnchanged=2774,previousEvidencePreserved=prior,newMediaIdentity=dict(path=MEDIA,bytes=8849,sha256=r['outputSha256'],dosReadOnly=True,fileAttributes=a.st_file_attributes),originalRequirementsSnapshotSha256=sha(originalReq),postfreezeReceipt=post))
save('independent-review.json',dict(result='PASS_GENERATION_EVIDENCE_AND_FILE_IDENTITY_ONLY',reviewUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actualGeneratorJvmCallsByTester=0,helperDemuxParserEncoderDecoderDeviceCallsByTester=0,oldSessionQueriesOrInterventions=0,rawStdoutBytes=len(stdout),rawStderrBytes=len(stderr),receipts=1,pending=0,final=1,originalOwner=o,workerDeadline=d,actualRawAuBytesAvailable=False,actualCsdExtractedFromFile=False,containerTracks=None,containerSamples=None,containerDurationUs=None,media3Qualification='NOT_RUN',newFindings=0,classification='GENERATED_CANDIDATE_NOT_QUALIFIED',D1='NOT_PASSED',M0='NOT_STARTED',externalReviewerMediaReads=reads,externalOriginalMediaReadBytes=sum(x['bytes'] for x in reads if x['source']=='ORIGINAL_MEDIA'),externalArchiveMediaReadBytes=sum(x['bytes'] for x in reads if x['source']=='ARCHIVE_MEDIA_COPY'),readMeasurement='Logical application payload, not physical disk/cache traffic; external identity/control reads separately from original driver8MiB',coderSealedExternalReadLedger=s['externalPreservationLedger'],coderPostfreezeSeparateOriginalBytes=post['thisAdditionalOriginalMediaHashBytes']))
print('PASS_GENERATION_EVIDENCE_AND_FILE_IDENTITY_ONLY seal38 ZIP37 GS24 originalRead17698 archiveRead8849; no container runtime')
