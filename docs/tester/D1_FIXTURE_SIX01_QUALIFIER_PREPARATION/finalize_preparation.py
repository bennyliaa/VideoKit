from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1fixture-tool02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
summary=load(E/'compilation-summary.json');o=summary['originalCompilerOwner'];assert summary['result']=='COMPILED_ONLY_RUNTIME_NOT_RUN' and o['exitCode']==0 and o['originalProcessReturned'] and o['outputHandlesClosed'] and not o['timedOutSticky']
assert sha(E/'Six01ContainerQualifier.java')==o['source']['sha256']
for row in summary['classFiles']:assert sha(Path(row['path']))==row['sha256']
apis=[
 ('raw container','MP4Demuxer.createRawMP4Demuxer / getMovie / getTracks / getVideoTracks / getAudioTracks / getTimecodeTrack','AVCC preserved; default createMP4Demuxer converts packets and is deliberately excluded'),
 ('root boxes','MP4Util.getRootAtoms; Atom.getOffset/getHeader; Header.getSize/headerSize/getFourcc','exact full-file root coverage; one ftyp/moov/mdat; only ftyp/wide/free/mdat/moov'),
 ('tracks/rotation','MovieBox.getTracks; TrakBox.getTrackHeader/getEdits/isVideo/isAudio; MovieHeaderBox/TrackHeaderBox.getMatrix','one video/no audio/no timecode; identity matrices; edits rejected'),
 ('entry/protection','NodeBox.getBoxes/findFirst/findFirstPath; VideoSampleEntry.getWidth/getHeight; SampleEntry.getDrefInd; DataRefBox/UrlBox','single avc1 256x144, self-contained URL data reference; protected/unsupported boxes blocked in admitted parsed scope'),
 ('CSD','H264Utils.parseAVCC/readSPS/readPPS/getPicSize/saveCodecPrivate; AvcCBox getters','actual payload hex/hash plus normalized CSD; parsed SPS dimensions; no decoded-pixel assertion'),
 ('DTS','TrakBox.getStts; TimeToSampleBox.TimeToSampleEntry getters','DTS derived from actual stts; reject edits and nonzero ctts. MP4Packet.getMediaPts is composition PTS, never independently DTS'),
 ('timestamps/duration','getCtts/getTimescale/getMediaDuration; MovieBox.getDuration/getTimescale; MP4Packet getters','integer microsecond mapping via exact BigInteger rational; six actual 200000us samples/total1200000us checked, not filled from receipt'),
 ('sample bytes','SampleSizesBox getters; MP4DemuxerTrack.getNextFrame(reused262144Buffer); MP4Packet.getFileOff/getSize/getEntryNo/getData','check six real sizes before buffer; each real file range in mdat; seventh packet null'),
 ('NAL/key','H264Utils.splitMOVPacket/decodeMOVPacket; NALUnit.read/NALUnitType; Packet.isKeyFrame/isPsync','mature AVCC split, actual NAL count/type/hash and IDR, container keyflag; separate AVCC and normalized AnnexB hashes'),
 ('return','original InputOwner/WorkerDeadline/ReceiptJson from exact jar','registered original holder; one native close; original library facade, worker completion and actual join separate; external process return remains controller evidence')]
save(E/'api-capability-matrix.json',dict(result='API_COMPILE_VERIFIED_RUNTIME_NOT_RUN',items=[dict(field=a,realApi=b,scope=c,runtime='NOT_RUN') for a,b,c in apis],missingOrUnproven=['Actual input hash and bytes deliberately unbound for this preparation','All actual container fields NOT_RUN','Internal mature-library metadata allocation bounds UNPROVEN before postparse guards','Encrypted-content cryptographic proof and decoder equivalence UNPROVEN','General edits/nonzero ctts/alternate tracks or nonidentity transformations BLOCKED rather than inferred','Read-only attribute and immutable-file preservation require external controller pre/post identity checks; single descriptor is not protection against external mutation','No runtime performance, platform permission or raw-versus-normalized AU equality proof','No original process return exists for helper because no helper JVM was launched']))
save(E/'future-execution-contract.json',dict(state='PREPARATION_ONLY_NO_EXECUTION_AUTHORITY',inputPath='D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4',expectedSha256=None,expectedBytes=None,scope=None,unboundReason='Only bind after complete generation freeze and new exact qualification dispatch; preparation never queried media identity',javaIdentity=o['compilerFiles'],jarIdentity=o['jar'],helperSource=o['source'],classIdentities=summary['classFiles'],argvTemplate=['D:/Android/Android Studio/jbr/bin/java.exe','-Xmx256m','-XX:-UsePerfData','-cp',str(E/'classes')+';'+str(B/'artifacts/videokit-fixture-tool02.jar'),'com.videokit.fixturetool.Six01ContainerQualifier','--expected-sha256=<FUTURE_EXACT_64HEX>','--expected-bytes=<FUTURE_EXACT_SIZE>','--scope=<FUTURE_AUTHORIZED_SCOPE>'],runtimeControllerRequirements=['Verify whole exact helper class set with no added classes, source/JAR/JDK pins; canonical regular immutable readonly file; bind exact authorized input tuple without searching candidates','Fresh separate controller/evidence directory and one original Popen; clear JAVA_TOOL_OPTIONS,JDK_JAVA_OPTIONS,_JAVA_OPTIONS,JDK_JAVAC_OPTIONS,CLASSPATH; fixed temp/cwd; stdin null; retain both original streams and original process before dispatch','One invocation only. 60s observation closes admission; preserve UNKNOWN and same original process/streams/Job, no kill/interrupt/terminate/attach/second close/retry or automatic later dispatch','Count full stdout/stderr UTF8 bytes <=1048576 including every pending/final, not tail. Observe original process natural return and close original streams separately; exit0 alone insufficient','Recheck file/tool/helper/JDK immutability after original return; external hash and control-metadata reads measured separately, never refunded or hidden in helper read ledger','Accept only exact HOST_CONTAINER_QUALIFICATION plus no firstError/no sticky unknown, timely body AND same original worker join, original input/library facade close, EOF+matching hash, original JVM exit and all actual fields. Any gap remains BLOCKED/UNKNOWN; stop'],budgets=dict(inputBytesMax=1048576,cumulativeNativeReadRequestedMax=1048576,hashIncluded=True,allDemuxRereadsIncluded=True,blockMax=65536,readCallsMax=4096,seekCallsMax=128,samples=6,sampleBytesMax=262144,csdPayloadAndNormalizedMax=65536,nalsPerSampleMax=64,rootBoxesMax=16,parsedBoxesMax=512,parsedDepthMax=16,checkerJvmMax=1,heapMiB=256,originalWorkerMax=1,observationSeconds=60,stdoutStderrCombinedUtf8Max=1048576),strictBudgetCaveat='Input <=1MiB is an admission ceiling, not a promise any such file fits hash+demux cumulative1MiB; budget failure blocks qualification without retry',outputMediaFiles=0,allowedFinalClassification='HOST_CONTAINER_QUALIFICATION_ONLY',notAuthorized=['helper invocation','media read/demux/normalization','encoder/decoder/Main/Job or generation replay','Android/Media3/host isolated format/READY/COMMIT','old48945/17257 intervention']))
save(E/'receipt-schema.json',dict(schemaState='FIELD_CONTRACT_NOT_ACTUAL_MEDIA_RESULT',requiredReceiptFields=['scopeLabelNotAuthority','inputPath','expectedBytes','expectedSha256','wholeHash','wholeHashEof','status','firstError','sameOriginalCheckerThreadJoined','originalInputAndLibraryReaderReturn','originalInputOwner','workerDeadline','actualContainerObservation'],ownerFields=['holderRegisteredBeforeOpen','state','originalCloseEntered','sameOriginalCloseReturned','uncertainSticky','nativeInFlight','operation','mediaReadRequestedCumulative','mediaReadReturnedCumulative','readCalls','seekCalls','actualNativeEofReads','lastAdoptedPosition','actualPhysicalPosition','positionScope','originalSeekTrace'],containerFields=['rootAtoms','parsedBoxNames','trackCount','videoTracks','audioTracks','sampleEntry','widthFromEntry','heightFromEntry','rotationMatrix','movieMatrix','rotation0IdentityObserved','noProtectionSignalingInAcceptedBoxScope','mediaTimescale','actualMediaDurationUnits','actualSttsDurationUnits','movieTimescale','movieDurationUnits','actualDurationUs','dtsSource','csd','samples'],sampleFields=['index','fileOffset','avccBytes','avccSha256','matureNormalizedAnnexBBytes','matureNormalizedAnnexBSha256','ptsUnits','mediaCompositionPtsUnits','dtsDerivedFromActualSttsUnits','durationUnits','timescale','ptsUs','dtsUs','durationUs','containerKeyFlag','actualIdrNal','nals'],independentExternalFields=['sameOriginalProcessReturned','actualExitCode','allOriginalStdoutStderrBytes','allPendingAndFinalReceipts','postReturnIdentityPreserved'],actualInput=None,actualTracks=None,actualSamples=None,actualCsd=None,actualTimeline=None,actualContainerQualification='NOT_RUN'))
report=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION_REPORT_V1.0.md'
text=f'''# D1 FIXTURE SIX01 独立容器资格检查器准备报告 V1.0

2026-10-21；tester；范围 SIX01_QUALIFIER_PREPARATION。

## 结论

**PASS_PREPARATION_COMPILED_ONLY_RUNTIME_NOT_RUN**。独立 helper 已完成源码/API审查并一次编译成功，具备后续准确只读资格批的准备条件。本阶段没有启动 helper JVM、Main、生成器、编码器、decoder、demux或设备；实际媒体字段全部 NOT_RUN，输入 hash/大小/scope 保持未绑定。不能据此签容器合格、HOST_ISOLATED_FORMAT_V1、READY、COMMIT、解码等效或 Media3 资格。

本报告按既有 tester Markdown 报告惯例交付。依据 docs/milestones/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION_TESTER_REQUIREMENTS_V1.0.md；源码及全部新产物仅在 docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION。本准备批未读取或查询浮动生成媒体/生成证据内容；负责人后来派发的完整生成B证据审按顺序在本准备整包封存后另做，不计入这里的结果。

## 准确依赖与原编译返回

原 tool02 seal SHA256 5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d 的2774项及ZIP2773唯一成员均独立核验；原独立报告4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4和其36项证据保持原样。准确生产JAR1954730B SHA256 c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd；仅用其原JCodec0.2.5和既有WorkerDeadline/ReceiptJson。未修改coder、未重建库、无新依赖或网络。

固定 JDK D:/Android/Android Studio/jbr，release/java.exe/javac.exe/jar.exe/lib/modules准确身份均复核，见 compilation-summary.json。javac原PID {o['pid']}，{o['startUtc']}启动，{o['endUtc']}自然返回，实际{round(o['elapsedSeconds'],3)}秒，exit0，原两个输出句柄关闭；stdout0B/stderr0B，sticky timeout false，强停/重试0。仅一次 -J-Xmx512m --release11 -proc:none -implicit:none 编译，空 sourcepath/processorpath、唯一准确JAR classpath、清除Java注入环境。完整argv与原返回见 compile/owner.json，未执行新class。

源码21809B SHA256 {o['source']['sha256']}。实际产出3个class，class major55，SourceFile均为Six01ContainerQualifier.java，静态独立读取classfile核身份/方法Code hash，未加载类。准备目录在汇总前65317B，完整封存后亦小于16MiB；没有首次失败、补编译或运行验收。一次编译控制器保留原Popen、60秒观察及UNKNOWN自然等待分支，无kill或自动后继。

## API能力、观察口径与未来合同

选择成熟库 **createRawMP4Demuxer**，明确避开默认 createMP4Demuxer 的H.264包自动转换。实际file root/box/track/sample数据来自原MP4Util、MovieBox、TrakBox、SampleSizesBox和MP4DemuxerTrack API，没有自写MP4/AVC字节解析器。H264Utils.decodeMOVPacket只是成熟库AVCC→AnnexB字节表示转换，未调用解码器，而且本阶段尚未运行转换。

未来会验证一个视频零音频、无其他轨道、单avc1、entry与实际SPS均256×144、track/movie均identity matrix、self-contained data reference、允许box范围内无保护信号。root atom需精确覆盖整个文件且仅一ftyp/moov/mdat；未知root、edits、非零ctts、保护box和不支持字段直接BLOCKED，不默认成功。没有把有限元数据检查冒称密码学未加密证明。

六个样本均读取实际stsz与真实packet，预检每个<=262144B，固定复用同一buffer，文件偏移落在实际mdat，记录实际AVCC hash、NAL type/hash、容器keyflag与真实IDR，检查第七packet为null。实际avcC的SPS/PPS提供hex/hash并通过成熟库读SPS/PPS与尺寸，累计CSD64KiB。归一化AnnexB hash单列，不能与生成器含SPS/PPS的raw AU hash直接相等；生成内部观察不代文件读取结果。

**getMediaPts是composition PTS，不能当独立DTS**。DTS通过真实stts条目累计，限定无edits/零ctts后再与packet PTS/时长核对。真实stts/media/track/movie时长与真实时基分别做精确整数有理映射，非整微秒或溢出阻塞。期望六个200000us/总1200000us只作断言，不填充缺失字段。完整字段合同见 receipt-schema.json，真实结果均null/NOT_RUN。

## 预算、原owner与停批

固定唯一输入路径，不支持任意文件参数。未来须另签准确输入sha/字节/scope并先核整个helper class集合/JAR/JDK身份与只读不可变属性；本交付 future-execution-contract.json 仅含命令模板，三项尚未绑定且无执行授权。实际检查原JVM最多1/heap256MiB/原worker1/body观察60秒/所有原stdout+stderr合计1MiB，由后续准确控制器保管原Popen与两流，不以exit0或最后一条JSON替代原返回。

原InputOwner在FileChannel分配前登记；同一个只读NOFOLLOW句柄完成全文件SHA/实际EOF、root扫描、demux所有重读与seek。input<=1MiB且**累计native requested读预算1MiB包括hash与重读**，块64KiB、read4096次、seek128次，实际返回字节另记；预算不退款。接近1MiB输入可能因hash+重读耗尽预算，准确BLOCKED而非重试。控制元数据/JDK/JAR身份读取与未来外部文件hash另列，不混入媒体ledger。

原库facade close委托同一个InputOwner，guard只准一次native close，finally再次到guard不会二次native close。真实close返回、worker body最后完成点、同原worker join以及外部原进程返回分别举证。deadline/异常/不确定关后续准入且sticky UNKNOWN，保留原Job/线程/句柄，不interrupt/kill/第二close/退款/换scope重试。pending位置只报最后adopted或UNKNOWN，close后仅LAST_ADOPTED_BEFORE_ORIGINAL_CLOSE；size明确是原open实际核对过的expected值，不声称每次新OS查询。失败时先前已观察但未完整形成的字段保留未证，不用成功exit补齐。

## 能力缺口与后续门

成熟库内部metadata分配发生在部分postparse守卫前，host文件上限不证明其内部内存安全；只准准确冻结的良性合成文件，禁止恶意atom/资源注入。本批编译通过只证明API/类型和class产出，运行性能、OS权限、实际无加密/实际样本/实际时长尚未验证。readonly与外部不可变性需未来控制器pre/post身份封存；单fd不防外部并发改写。实际Android/Media3资格及HOST_ISOLATED_FORMAT_V1仍另批。

无新缺陷需coder本轮修改；需要下一准确运行批验证所有runtime门，不能将准备通过升级为实际资格通过。原48945/17257 UNKNOWN未查询、未attach、未终止；N2历史ABORT不重复。D1未过、M0未启。准备报告和证据冻结后发送负责人，随后只做已正式派发的完整生成B纯Python证据/身份审，不自动运行helper或后续测试。
'''
report.write_text(text,encoding='utf8')
files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
assert sum(x['bytes'] for x in files)<16777216
save(E/'review-evidence-manifest.json',dict(frozenUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=report.relative_to(R).as_posix(),reportBytes=report.stat().st_size,reportSha256=sha(report),overall='PASS_PREPARATION_COMPILED_ONLY_RUNTIME_NOT_RUN',evidenceFiles=files,evidenceBytes=sum(x['bytes'] for x in files),compileCalls=1,helperRuntimeCalls=0))
print(json.dumps(dict(report=str(report),reportSha256=sha(report),reportBytes=report.stat().st_size,manifestSha256=sha(E/'review-evidence-manifest.json'),evidenceFiles=len(files),evidenceBytes=sum(x['bytes'] for x in files)),ensure_ascii=False))
