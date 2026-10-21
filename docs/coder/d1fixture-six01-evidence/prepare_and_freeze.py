from pathlib import Path
import json,hashlib,datetime,zipfile,shutil,collections
E=Path(__file__).resolve().parent;R=E.parents[2];T=R/'docs/coder/d1fixture-tool02';ROOT=R/'docs/coder/d1fixture-six01';OUTPUT=ROOT/'new-output/avc6-candidate.mp4';seal=E/'fixture-six01-freeze.json';assert not seal.exists()
ledger=[{'actor':'run_once.py preservation after original process return','kind':'ORIGINAL_MEDIA_HASH_READ','bytes':8849,'driver8MiBLedger':False,'alreadyOccurred':True}]
def sha(p,purpose='non-media identity'):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);n+=len(b)
 if p==OUTPUT:ledger.append({'actor':purpose,'kind':'ORIGINAL_MEDIA_HASH_READ','bytes':n,'driver8MiBLedger':False})
 return h.hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result=json.loads((E/'generation-result.json').read_text());receipt=json.loads((E/'last-original-driver-receipt.json').read_text());owner=json.loads((E/'control-001/owner.json').read_text())
assert result['status']==receipt['status']=='GENERATED_CANDIDATE_NOT_QUALIFIED' and all(result['requirements'].values())
assert owner['processInvocations']==1 and owner['originalProcessReturned'] and owner['exitCode']==0 and owner['stdoutHandleClosed'] and owner['stderrHandleClosed'] and not owner['controllerObservationUnknownSticky'] and not owner['receiptBudgetExceededSticky']
raw=(E/'control-001/stdout.raw').read_bytes();err=(E/'control-001/stderr.raw').read_bytes();assert len(raw)==12297 and len(err)==0 and len(raw)+len(err)<=1048576
assert len(json.loads((E/'control-001/all-original-json-receipts.json').read_text()))==1
assert json.loads(raw.decode('utf-8'))==receipt
budget=receipt['outputBudget'];events=budget['nativeOperationEvents'];writes=[x for x in events if x['operation']=='WRITE'];metadata=[x for x in events if x['operation']!='WRITE'];terminal=budget['terminalCloseEvent']
assert len(events)==19 and len(writes)==9 and len(metadata)==10 and terminal['operation']=='CLOSE'
assert sum(x['requestedAndReserved'] for x in writes)==budget['attemptedBytes']==8857
assert sum(x['returned'] for x in writes)==budget['acknowledgedLowerBound']==8857
assert all(x['requestedAndReserved']==0 for x in metadata) and max(x['requestedAndReserved'] for x in writes)==1340
assert all(x['requestedAndReserved']==x['returned'] and x['outcome']=='RESULT_ADOPTED' for x in writes)
assert budget['nativeCallsEntered']==budget['nativeReturnsObserved']==budget['resultsAdopted']==20
assert budget['nativeInFlight']==budget['resultAdoptionPending']==budget['nativeThrowsObserved']==budget['budgetRefundedBytes']==budget['initialMeterOnlyReservation']==0
assert budget['physicalUnknownSticky']==budget['failedOrUncertain']==False and budget['peakNativeInFlight']==1
assert budget['headerOrOtherRewriteAttemptedBytes']==8 and budget['lastAcknowledgedLogicalPosition']==56 and budget['acknowledgedExtentLowerBound']==8849
samples=receipt['sixRawEncoderSamples'];assert len(samples)==6
for i,s in enumerate(samples):
 assert s['index']==i and s['ptsUnits']==i and s['timescale']==5 and s['durationUnits']==1 and s['ptsUs']==i*200000
 assert s['isKeyframe'] and s['actualIdrNalObserved'] and 0<s['rawEncoderAnnexBBytes']<=262144 and len(s['rawEncoderAnnexBSha256'])==64
 assert s['actualExtractorRepresentation']=='NOT_RUN_REQUIRES_LATER_QUALIFICATION'
assert sum(x['rawEncoderAnnexBBytes'] for x in samples)==8160
csd=receipt['actualMuxTrackCsd'];assert len(csd)==3
for x in csd:
 b=bytes.fromhex(x['hex']);assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
assert sum(x['bytes'] for x in csd)==30 and receipt['rawCsdObservedCumulativeBytes']==120
assert receipt['inputAttemptedReserved']==340626 and receipt['inputActuallyObserved']==331776+8849==340625
assert receipt['reader']['nativeReadBytes']==8849 and receipt['reader']['nativeEofCalls']==1 and receipt['reader']['nativeReadCalls']==2
assert receipt['writer']['state']==receipt['reader']['state']=='CLOSE_RETURNED' and receipt['writer']['forceReturned'] and receipt['writer']['sameOriginalCloseReturned'] and receipt['reader']['sameOriginalCloseReturned']
assert receipt['workerDeadline']['timelyBodyAndOriginalJoin'] and receipt['sameWorkerExternallyJoined'] and receipt['originalResourceOwnersReturned'] and not receipt['workerDeadline']['deadlineUnknownSticky']
assert receipt['nativeOwnersLive']==0 and receipt['nativeOwnersPeak']==1
fixedSeal=T/'evidence/fixture-tool02-freeze.json';assert sha(fixedSeal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d';fixed=json.loads(fixedSeal.read_text());assert len(fixed['files'])==2774 and all(sha(R/x['path'])==x['sha256'] for x in fixed['files'])
stage=R/'docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_EVIDENCE';a=R/'docs/tester/D1_FIXTURE_SIX01_GENERATE_PHASE_A_REPORT_V1.0.md';assert sha(a)=='b7a58c1bdcd87abfa1105cf85999b74ff8d78b610b63cee8ef7509180ea1fa08'
shutil.copyfile(a,E/'reference'/a.name)
for p in stage.glob('*.json'):shutil.copyfile(p,E/'reference'/('phase-a-'+p.name))
req=R/'docs/milestones/D1_FIXTURE_SIX01_GENERATE_CODER_REQUIREMENTS_V1.0.md';shutil.copyfile(req,E/'reference/CODER_REQUIREMENTS_WITH_STAGE_A.md')
for p in (T/'driver/com/videokit/fixturetool').glob('*.java'):
 d=E/'reference/frozen-tool02-driver'/p.name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
identity=result['output'];assert OUTPUT.stat().st_size==8849 and bool(OUTPUT.stat().st_file_attributes&1)
manifest={'candidate':'D1_FIXTURE_SIX01_GENERATE','scope':'D1GEN01-CANDIDATE-001','classification':'GENERATED_CANDIDATE_NOT_QUALIFIED','file':identity,'fileIdentityEvidence':'Original private readonly reopen rawEOF/hash from same driver plus separately budgeted external SHA preservation. No media parser/demuxer/decoder invoked.','tool':{'jarPath':'docs/coder/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar','bytes':1954730,'sha256':'c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd','sealSha256':sha(fixedSeal),'verifiedFrozenRows':2774,'sourceArchiveSha256':'9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db','independentLimitedReview':'4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4'},'contentRights':{'source':'VideoKit project-authored deterministic synthetic YUV420J formula from exact reviewed driver','externalMediaFontsLogosAudioOrBbbUsed':False,'pattern':'Y unsigned16+16*((x/16+y/16+i)%14), stored signed minus128; U/V signed0; i0..5','rawFrameBytes':55296,'totalSyntheticPixelBytes':331776,'distributionOrPatentClearance':'Not granted by this test; upstream code notices retained separately'},'declaredTrackParameters':{'source':'Original approved MP4Muxer API/VideoCodecMeta input, NOT independent file parser','container':'MP4','videoCodec':'AVC','width':256,'height':144,'rotation':0,'audio':False,'encrypted':False,'timescale':5,'packetPts':[0,1,2,3,4,5],'packetDuration':1,'ptsUs':[0,200000,400000,600000,800000,1000000],'expectedPacketEndUs':1200000},'internalMuxTrackDurationUnits':6,'independentContainerDurationUs':None,'independentContainerTrackOrSampleMap':None,'rawEncoderAuObservations':samples,'rawAuBytesPreserved':False,'rawAuHashesIndependentlyRecomputed':False,'rawAuHashProvenance':'Computed by exact reviewed driver before mature mux-track mutation. No raw AU bytes preserved, no independent demux. Not container AU hashes.','internalCsdObservations':csd,'csdHexSizeShaRecheckedFromReceiptBytes':True,'csdOrigin':'Actual driver mux-track AvcCBox after finish, NOT independent file reopen; library converted AnnexB marked separately','actualMedia3Qualification':None,'newAndroidEmbedding':False,'decodePlaybackIsolatedValidationReadyCommit':False,'dateRule':'Original MP4Muxer Date unchanged; only this actual generated byte identity frozen, no repeat-file-hash guarantee','processAndReturnFacts':{'ownerReceipt':'control-001/owner.json','driverReceipt':'last-original-driver-receipt.json','generationCalls':1,'retry':False,'sameOriginalWorkerJoined':True,'driverForceAndTwoOriginalClosesReturned':True,'originalNaturalProcessReturn':True},'driverBudgetLedger':{'inputReserved':340626,'syntheticPixels':331776,'originalFileReadBytes':8849,'originalEofProbeReservation':1,'inputActuallyObserved':340625,'inputLimit':8388608,'outputAttempt':8857,'knownWriteReturns':8857,'outputLimit':16777216,'headerRewriteAttempt':8,'lastConfirmedPositionBeforeClose':56,'confirmedExtentAndFileSize':8849,'nativeOwnersPeak':1,'nativeOwnersLiveAtReceipt':0,'nativeInFlightPeak':1,'regularEvents':19,'terminalCloseRecords':1},'externalPreservationReads':'seal.externalPreservationLedger plus separate later postfreeze receipt; never added to or refunded from original driver input8MiB','D1':'NOT_PASSED','M0':'NOT_STARTED'}
dump(E/'media-manifest.json',manifest)
dump(E/'budget-and-return-validation.json',{'status':'ORIGINAL_RECEIPT_ACCOUNTING_MATCHED_ONLY_NOT_FORMAT_QUALIFICATION','originalStdoutBytes':len(raw),'originalStderrBytes':len(err),'originalJsonReceipts':1,'pendingUnknownReceipts':0,'nonreceiptOutputLines':0,'writeOperations':len(writes),'writeRequestedSum':8857,'validWriteReturnedSum':8857,'metadataOperations':dict(collections.Counter(x['operation'] for x in metadata)),'metadataRequestPayloadSum':0,'terminalCloseRecords':1,'nativeCallsReturnsAdoptions':20,'actualPartialWriteCalls':0,'maxActualNativeWriteRequest':1340,'physicalOutputSize':8849,'lastConfirmedLogicalPosition':56,'physicalValueScope':'LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE','syntheticPixels':331776,'fileReadBytes':8849,'inputAttemptedReserved':340626,'inputActuallyObserved':340625,'eofReadCalls':1,'bodyCompletionElapsedNanos':receipt['workerDeadline']['completionElapsedNanos'],'bodyPointNotOsThreadExit':True,'sameOriginalWorkerJoinAndProcessNaturalReturn':True,'csdHexSizeHashSelfConsistency':True,'rawAuHashesWithoutBytesRecomputed':False,'containerSamplesTracksDurationIndependentlyParsed':False,'noProcessKillInterruptSecondCloseRetry':True})
phase=json.loads((E/'reference/phase-a-independent-gs01-gs24-oracles.json').read_text());rows=[]
for old in phase['cases']:
 x=dict(old);n=int(x['id'][2:]);x['phaseAStatusPreserved']=x['status'];x['coderEvidenceStatus']='ORIGINAL_GENERATION_RECEIPT_AND_BYTE_IDENTITY_RECORDED_NOT_INDEPENDENT_VERDICT';x['status']='PENDING_INDEPENDENT_B_EVIDENCE_REVIEW';x['newGenerationResultRead']=True;x['independentFormatQualification']='NOT_RUN';x['bindings']=['media-manifest.json','last-original-driver-receipt.json','generation-result.json','budget-and-return-validation.json','control-001/owner.json']
 if n in [2,8]:x['negativeOrFailurePathExecution']='NOT_RUN; actual approved identity/absent-root successful path only; no injected failure/retry'
 if n==16:x['rawAuIndependentHashRecomputation']='NOT_POSSIBLE_WITHOUT_RAW_BYTES; report six original observations only'
 if n in [17,18,20]:x['evidenceLevel']='Internal CSD/Packet/track observation only; no independent media container parsing'
 rows.append(x)
dump(E/'gs01-gs24-completion-matrix.json',{'sourceStageAReportSha256':sha(a),'rows':rows,'actualGenerationCalls':1,'coderStatus':'GENERATED_CANDIDATE_NOT_QUALIFIED','independentB':'PENDING','trueContainerOrMedia3Qualification':'NOT_RUN','D1':'NOT_PASSED','M0':'NOT_STARTED'})
report=f'''# D1_FIXTURE_SIX01_GENERATE 一次真实生成完整报告 V1.0

2026-10-21。本批按负责人新准确许可D1GEN01-CANDIDATE-001执行冻结工具一次，成功产生**GENERATED_CANDIDATE_NOT_QUALIFIED**。仅证原受控生成/文件字节身份与返回事实；还没有独立容器AU/轨道/PTS/duration/解码或Media3资格化，不嵌Android、不播放，不签隔离格式/READY/COMMIT。D1未过、M0未启。

## 1. 准确产物和一次范围

输出D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4，**8849B，SHA25619e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c**。driver完成后设置只读，外部DOS readonly属性一致。根目录和new-output都由原driver独占createDirectory，输出CREATE_NEW；控制器只建独立d1fixture-six01-evidence，未预建生成根、未覆盖文件、未换scope或重试。

唯一argv逐项与正式要求相同：固定D:/Android/Android Studio/jbr/bin/java.exe、-Xmx256m、-XX:-UsePerfData、-jar、固定d1fixture-tool02/artifacts/videokit-fixture-tool02.jar、--generate-six、--scope=D1GEN01-CANDIDATE-001。JAR1954730B/SHA256c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd；tool seal5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d的2774文件先全核、封存前再核不变。固定JDK java/release/modules及其余原工具hash全吻合，无版本查询进程/新编译/网络/PATH fallback/追加flag或其他codec/CLI调用。

原4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4的FT-B01/B02有限非媒体通过不冒原来生成已运行；本批权限来自新明确要求，旧plan generationAuthorized=false历史文件不改。初始执行要求原字节与preflight hash保留，阶段A追加要求另存CODER_REQUIREMENTS_WITH_STAGE_A.md，不覆盖执行时的初始许可记录。

## 2. 同一次控制器、原输出与返回

外置run_once.py登记唯一原Popen/捕获流，shell=False，cwd独立control-001；精确清除JAVA_TOOL_OPTIONS/JDK_JAVA_OPTIONS/_JAVA_OPTIONS/JDK_JAVAC_OPTIONS/CLASSPATH注入项，未记录可能敏感的原值，实际清除后不存在。原JVM历史PID8044，UTC2026-10-21T01:10:24.391727至01:10:24.686044（本地09:10:24），Popen观察elapsed约0.281秒，自然exit0；该PID只为本次原句柄回执，不作未来身份或host idle证明。

完整stdout.raw12297B、stderr.raw0B，严格UTF8全量≤1048576B。恰1条原JSON final、0条pending、0条其他输出；全部原字节和逐条JSON均保留，没有tail/丢pending/按每行分别算上限。捕获handle只在同原process自然返回后由控制器各关一次。原控制器tool调用也自然exit0；没有丢管道、自动kill/interrupt/二close/退款或重生成。控制器超观察窗/超输出界本会记sticky UNKNOWN并保管原Popen/流、停新准入，本次未触发，不能冒测过失败路径。

最终原status准确GENERATED_CANDIDATE_NOT_QUALIFIED、firstError=null、deadlineUnknownSticky=false、原body清理完成、原资源返回、sameWorkerExternallyJoined=true。原单调body点elapsed152633600ns、observer elapsed152939400ns，均与60s契约相符；body marker是同原worker cleanup后最后受控语句，不是OS线程退出时间戳。实际同Thread.join、writer/reader原close与Popen自然退出各自独立记录，没有只凭exit0补成功。

## 3. 实际FileChannel、原force/close和预算

此次是实际原FileChannel输出/只读重开：writer先于mux构造/header分配登记，实际mux.finish返回，同原FileChannel.force(true)返回、同原close返回；之后设只读、reader同一新路径只读开并全EOF/hash、再原close。两holder最终CLOSE_RETURNED，各closeAttempted/原closeReturned=true；writer forceAttempted/forceReturned=true，reader无force。实际登记owner峰1/live0只是辅助，不能代原close/workerjoin/Popen证据；没有把force返回冒业务COMMIT或全平台持久化保证。

原input预留340626B≤8MiB：原创内存像素331776B，实际文件read8849B，EOF探测预留1B；actualObserved340625B。reader实际read调用2，其中EOF1，nativeReadBytes8849。不能把内存像素量称OS原媒体读取；其他原视频/BBB未输入。

从原事件独立求和9次WRITE requested=8857B、有效returned=8857B，全部请求与返回相等，无本次实际partial/throw；其中header回写8B，initialMeterOnlyReservation=0、refund0。10个metadata事件request0：POSITION7、SEEK1、FORCE1、SIZE1；加一个终态CLOSE，共20 entered/return-observed/adopted，inFlight/adoption/throws最终0、physicalUnknown/failed均false。常规19事件+单close≤512+1，实际最大WRITE请求1340B≤65536，输出attempt≤16MiB。

最终关闭前lastConfirmed position56，extent8849、实际文件size8849，二者不强求相等；header seek从原事件中可见，不能用size代attempt。post-close physical scope明确LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE，不冒关闭后新FD测量。原input/outputattempt账完全保留；随后Python hash/ZIP保存/验证另列seal.externalPreservationLedger及后封存回执，不倒灌原8MiB、不退款。JDK/tool身份核验是外部身份审计输入，也不是原生成像素/文件预算。

## 4. 六个raw AU与内部CSD：可证及不可证

driver一次调用六个原创YUV420J256x144帧，单帧55296B，Y unsigned16+16*((x/16+y/16+i)%14)转signed减128，U/V signed0。无外部媒体、字体、商标、音频、解码输入。keyInterval1/motionSearch0/DumbRateControl初QP20不冒constant-QP；成熟JCodec source及许可证/版权原样保留，无新增fallback或专利/商业发行/FFmpeg清权。

六条原rawEncoderAnnexB观察index0..5，每条1360B、总8160B≤1572864B，实际isKeyFrame和IDR观察均true，NAL类型记录7/8/5及各size/hash。**未保存原AU字节，未demux，所以这些hash仅原driver在成熟mux变更前计算的内部观察，不能称本次Python或tester独立重算，更不是文件容器AU hash。** mature CodecMP4MuxerTrack去PS/AVCC转换仍一次；writer实际chunk回执也不自动等于独立container sample map。

原CSD来自finish后的实际mux-track AvcCBox：SPS payload7B/PPS payload3B（不含NAL头）、另有库转换AnnexB20B，NAL长度字段4。JSON原hex/size/SHA已用Python自一致复核，每种表示/来源独立保留，3条共30B，raw PS观测累计120B，均≤64KiB。这只证原收据hex和hash一致，不证从文件重新提取了CSD。

Packet实际输入ptsUnits0..5/timescale5/duration1，声明PTS0,200000,400000,600000,800000,1000000us，expectedEnd1200000；内部mux trackDurationUnits=6。**这不是独立文件duration1.2s/轨道单AVC、无音频/加密、rotation0或AVC语法正确的验证。** 这些track参数来自已审API输入，文件本身尚未解析。JCodec六Packet+finish没有第七payload/E6空EOS；未来Media3 E6 flags4 EOS1200000/fragment3000ms另批，不混写当前结果。

## 5. 文件身份、权属与不可变封存

原driver在writer已close后只读readback取得wholeEOF/hash；外部仅有限读取新8849B文件做SHA保全，大小/hash与原receipt一致，DOS readonly一致，没有新增parser/demuxer/decoder、ffprobe或Media3。整文件hash只证这份字节身份，不独立证明结构/帧数/时长/内容安全或资格。原MovieHeader仍current Date，未修改时间戳或重生成求目标hash；只冻结本次实际文件，不许诺另次全片hash相同。

media-manifest.json保全准确文件身份、scope、tool/JDK/许可、原内容权属、原AU/CSD及来源、Packet与内部duration、原预算/返回，独立container map/duration/Media3字段null/NOT_RUN，不把无原AU字节的hash回算成“独立已验”。license来自固定tool02/FreeBSD、JAAD Public Domain+FreeBSD变更、Guava Apache2及项目自有driver声明；原创合成内容不依赖BBB归属，发行/专利许可门保持。

新seal fixture-six01-freeze.json覆盖新media路径和外置证据/报告；ZIP D:/CodexProjects/VideoKit/docs/coder/D1-20261021-FIXTURE-SIX01-GENERATE-source.zip保存同一真实文件和原证据。Hash/封存操作只能读原新媒体，不改属性/字节、不删除目录、不重复Main。外部复核读取逐项另记，不以“还是同文件”去重冒实际读取量。

## 6. 阶段A映射与集中交接

阶段A报告b7a58c1bdcd87abfa1105cf85999b74ff8d78b610b63cee8ef7509180ea1fa08及GS01–GS24/证据合同/结果分层全纳入reference；其PREPARED_NOT_RUN保持原状，自己的gs01-gs24-completion-matrix分开实际原生成和独立B待审。GS02拒绝分支/GS08失败超窗未注入运行，不把本次正常路径冒负例验证；GS16 rawAU缺原字节和GS17/18内部CSD/时基的证据上限明确。

本次只一次获准Main/H264Encoder/MP4Muxer生成，零额外编译、codec/CLI、原视频读取、网络/Gradle/设备/Android/Media3/播放或原48945/17257/PID/attach操作。旧UNKNOWN和人类强制收尾待批不变，独立本地生成不等host全空闲。固定tool02的2774身份保全，不修改旧plan/旧FAIL或扩大FT-B01/B02有限非媒体结论。

完整材料交负责人后另派B，只审证据/有限文件身份；独立成熟框架容器重开/Media3资格、有效fixture准入、新Android mux嵌入/播放等仍需新准确范围，本批没有自动执行或宣称完成。D1未过M0未启，P0/J11/C13及旧许可/发布门保持。
'''
main=R/'docs/coder/D1_FIXTURE_SIX01_GENERATE_DELIVERY_V1.0.md';assert not main.exists();main.write_text(report,encoding='utf-8')
files=sorted([p for p in E.rglob('*') if p.is_file()]+[main,OUTPUT]);assert len(list(ROOT.rglob('*.mp4')))==1
rows=[]
for p in files:rows.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p,'freeze identity table')})
archive=R/'docs/coder/D1-20261021-FIXTURE-SIX01-GENERATE-source.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  z.write(p,p.relative_to(R).as_posix())
  if p==OUTPUT:ledger.append({'actor':'ZIP preservation copy','kind':'ORIGINAL_MEDIA_ZIP_COPY_READ','bytes':8849,'driver8MiBLedger':False})
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist()))==len(rows) and z.testzip() is None
 ledger.append({'actor':'ZIP CRC verification','kind':'ARCHIVE_MEDIA_COPY_READ','bytes':8849,'driver8MiBLedger':False})
 for x in rows:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
 ledger.append({'actor':'ZIP member hash comparison','kind':'ARCHIVE_MEDIA_COPY_READ','bytes':8849,'driver8MiBLedger':False})
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
for x in rows+[arch]:assert sha(R/x['path'],'seal final original-media hash recheck')==x['sha256']
externalLedger={'status':'COMPLETED_FINITE_EXTERNAL_PRESERVATION_APPLICATION_READS_SEPARATE_FROM_DRIVER_INPUT','entries':ledger,'originalMediaDirectBytes':sum(x['bytes'] for x in ledger if x['kind'].startswith('ORIGINAL_MEDIA')),'archiveCopyMediaBytes':sum(x['bytes'] for x in ledger if x['kind'].startswith('ARCHIVE_MEDIA')),'measurement':'Application logical read payload, not physical disk/cache traffic. Identity reads of JDK/tool are separate from media.','additionalFutureReads':'Later postfreeze/B reads separately recorded, never alter this sealed ledger or original driver8MiB meter.'}
value={'candidate':'D1_FIXTURE_SIX01_GENERATE','scope':'D1GEN01-CANDIDATE-001','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'GENERATED_CANDIDATE_NOT_QUALIFIED_PENDING_INDEPENDENT_EVIDENCE_REVIEW','actualGenerationProcesses':1,'naturalExitCode':0,'output':identity,'toolJarSha256':'c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd','tool02SealSha256':sha(fixedSeal),'tool02FrozenIdentityRowsUnchanged':2774,'allOriginalRawReceipts':1,'originalStdoutBytes':12297,'originalStderrBytes':0,'originalInputReserved':340626,'originalOutputAttempt':8857,'originalFileSize':8849,'rawAuObservations':6,'rawAuTotalBytes':8160,'rawAuHashesIndependentlyRecomputed':False,'independentContainerMedia3Qualification':'NOT_RUN','retryKillInterruptSecondCloseActions':0,'oldSessionOrDeviceActions':0,'D1':'NOT_PASSED','M0':'NOT_STARTED','archiveMembers':len(rows),'externalPreservationLedger':externalLedger,'archive':arch,'files':rows+[arch]}
seal.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Media was rehashed immediately before seal construction; do not silently reread it after sealing its audit ledger.
for x in value['files']:
 if R/x['path']!=OUTPUT:assert sha(R/x['path'])==x['sha256']
print(json.dumps({'sealPath':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'reportSha256':sha(main),'mediaSha256':identity['sha256'],'status':value['status']},ensure_ascii=False,indent=2))
