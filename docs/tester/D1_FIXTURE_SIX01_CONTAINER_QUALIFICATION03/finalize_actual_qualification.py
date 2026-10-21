from pathlib import Path
import json,hashlib,datetime,urllib.parse
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;PRE=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION';GEN=R/'docs/coder/d1fixture-six01-evidence'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
d=load(E/'execution-result.json');r=d['finalOriginalReceipt'];o=d['actualContainerObservation'];m=d['actualOriginalMetadataObservation'];dr=d['actualDataReferenceChildObservation'];i=r['originalInputOwner'];w=r['workerDeadline'];owner=d['originalProcessOwner']
assert d['status']=='PASS_HOST_CONTAINER_QUALIFICATION_ONLY' and all(d['conditions'].values()) and r['firstError'] is None
raw=(E/'control-001/stdout.raw').read_bytes();assert len(raw)==13708 and json.loads(raw)==r and (E/'control-001/stderr.raw').read_bytes()==b'' and d['allOriginalReceiptCount']==1 and d['nonreceiptLineCount']==0
assert r['wholeHashEof'] and r['wholeHash']=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c' and r['sameOriginalCheckerThreadJoined'] and r['originalInputAndLibraryReaderReturn']
assert i['state']=='CLOSE_RETURNED' and i['originalCloseEntered'] and i['sameOriginalCloseReturned'] and i['nativeInFlight']==0 and not i['uncertainSticky']
assert i['mediaReadRequestedCumulative']==17787 and i['mediaReadReturnedCumulative']==17786 and i['readCalls']==18 and i['seekCalls']==20 and i['actualNativeEofReads']==1 and i['lastAdoptedPosition']==8096
assert w['bodyCompletedNanoTime']-w['startNanoTime']==w['completionElapsedNanos']==111550000 and w['timelyBodyAndOriginalJoin'] and w['sameOriginalExternallyJoined'] and not w['deadlineUnknownSticky'] and not w['invalidMonotonicRange']
assert owner['processInvocations']==1 and owner['exitCode']==0 and owner['originalProcessReturned'] and owner['stdoutHandleClosed'] and owner['stderrHandleClosed'] and not owner['controllerTimeoutUnknownSticky'] and not owner['outputLimitUnknownSticky']
assert load(E/'preflight.json')['inputSha256']==load(E/'post-return-preservation.json')['inputSha256']==r['wholeHash']
assert o['trackCount']==o['videoTracks']==1 and o['audioTracks']==0 and o['sampleEntry']=='avc1' and o['widthFromEntry']==256 and o['heightFromEntry']==144 and o['rotation0IdentityObserved'] and o['noProtectionSignalingInAcceptedBoxScope']
roots=o['rootAtoms'];cursor=0
for root in roots:assert root['offset']==cursor and root['size']>=root['headerBytes'];cursor+=root['size']
assert cursor==8849 and [x['fourcc'] for x in roots]==['ftyp','wide','mdat','moov']
mdat=next(x for x in roots if x['fourcc']=='mdat');start=mdat['offset']+mdat['headerBytes'];end=mdat['offset']+mdat['size'];assert (start,end)==(56,8096)
for h in [dr['originalDrefHeader'],m['originalStsdHeader']]:assert h['observed'] and h['rawVersionFlagsWord']==h['version']==h['flags']==0 and h['declaredCountUnsigned']==h['actualParsedChildren']==1 and h['actualHeaderBodyBytes']==h['bodyFromActualChildrenAndOriginalPrefix']
assert dr['actualChildFourcc']=='alis' and dr['actualChildClass']=='org.jcodec.containers.mp4.boxes.AliasBox' and dr['sampleEntryDataReferenceIndex']==1 and dr['childVersion']==0 and dr['childFlags']==1 and dr['actualChildBodyBytes']==4 and dr['matureAliasIsSelfRef'] and dr['aliasFileName'] is None and dr['aliasExtrasCount'] is None and dr['aliasRecordSize']==0
av=m['originalAvccHeader'];assert av['observed'] and av['configurationVersion']==1 and av['rawLengthSizeByte']==255 and av['lengthReservedHigh6']==63 and av['actualNalLengthSize']==4 and av['rawSpsCountByte']==225 and av['spsReservedHigh3']==7 and av['declaredSpsCount']==av['actualSpsCount']==av['declaredPpsCount']==av['actualPpsCount']==1 and av['actualHeaderBodyBytes']==av['bodyFromObservedCountsAndActualPayloads']==23 and av['actualCsdPayloadBytes']==10
csd=o['csd'];assert [x['bytes'] for x in csd]==[7,3,20]
for x in csd:v=bytes.fromhex(x['hex']);assert len(v)==x['bytes'] and hashlib.sha256(v).hexdigest()==x['sha256']
assert csd[0]['actualSpsWidth']==256 and csd[0]['actualSpsHeight']==144 and csd[1]['maturePpsParsed']
samples=o['samples'];assert len(samples)==6 and o['mediaTimescale']==o['movieTimescale']==5 and o['actualMediaDurationUnits']==o['actualSttsDurationUnits']==o['movieDurationUnits']==6 and o['actualDurationUs']==1200000
cursor=start
for n,sample in enumerate(samples):
 assert sample['index']==n and sample['fileOffset']==cursor and sample['avccBytes']==sample['matureNormalizedAnnexBBytes']==1340 and sample['ptsUnits']==sample['mediaCompositionPtsUnits']==sample['dtsDerivedFromActualSttsUnits']==n and sample['durationUnits']==1 and sample['timescale']==5 and sample['ptsUs']==sample['dtsUs']==n*200000 and sample['durationUs']==200000 and sample['containerKeyFlag'] and sample['actualIdrNal']
 assert len(sample['nals'])==1 and sample['nals'][0]['type']==5 and sample['nals'][0]['bytes']==1336 and sample['nals'][0]['bytes']+4==sample['avccBytes']
 cursor+=sample['avccBytes']
assert cursor==end and sum(x['durationUs'] for x in samples)==1200000
internal=load(GEN/'last-original-driver-receipt.json');comparison=[]
for old,new in zip(internal['sixRawEncoderSamples'],samples):
 oldIdr=next(n for n in old['nals'] if n['type']==5);newIdr=new['nals'][0];assert old['index']==new['index'] and oldIdr['sha256']==newIdr['sha256'] and oldIdr['bytes']==newIdr['bytes']
 comparison.append(dict(index=new['index'],actualFileAvccBytes=new['avccBytes'],actualFileAvccSha256=new['avccSha256'],actualFileNormalizedAnnexBBytes=new['matureNormalizedAnnexBBytes'],actualFileNormalizedAnnexBSha256=new['matureNormalizedAnnexBSha256'],originalInternalRawAuBytes=old['rawEncoderAnnexBBytes'],originalInternalRawAuSha256=old['rawEncoderAnnexBSha256'],actualFileIdrBytes=newIdr['bytes'],actualFileIdrSha256=newIdr['sha256'],matchesPriorInternalIdrRecord=True,originalRawAuIndependentlyRecomputed=False))
for old,new in zip(internal['actualMuxTrackCsd'],csd):assert old['hex']==new['hex'] and old['sha256']==new['sha256'] and old['bytes']==new['bytes']
sources=d['actualCodeSourceProof'];assert len(sources['classes'])==15 and len(sources['additionalActualRuntimeTypes'])==5 and sources['forkVersion']=='0.2.5-videokit-observation01' and not sources['fullJcodecJarFallback']
loaded=(E/'control-001/loaded-classes.log').read_text();comSourceRows=[]
for line in loaded.splitlines():
 if '[class,load] com.videokit.fixturetool.' in line:
  if '$$Lambda/' in line:
   assert 'source: com.videokit.fixturetool.Six01ContainerQualifier03' in line;comSourceRows.append(line);continue
  isSupport=any(' '+name+' ' in line for name in ['com.videokit.fixturetool.WorkerDeadline','com.videokit.fixturetool.ReceiptJson']);expected=PRE/('support' if isSupport else 'helper-classes');normalized=urllib.parse.unquote(line).replace('\\','/').lower();assert str(expected).replace('\\','/').lower() in normalized;comSourceRows.append(line)
assert len(comSourceRows)>=8 and not load(E/'actual-classload-audit.json')['originOrForbiddenClassErrors']
external=load(E/'external-read-ledger.json');assert external['originalMediaLogicalReadBytes']==17698 and [x['bytes'] for x in external['entries']]==[8849,8849]
save(E/'independent-actual-field-validation.json',dict(result='PASS_HOST_CONTAINER_QUALIFICATION_ONLY',rawReceiptReparsedExactly=True,originalMetadataAndTracksRechecked=True,rootWholeFileCoverage=8849,mdatPayloadCoverage=dict(start=start,end=end,bytes=8040,actualSamplesContiguous=True),originalMetadata=dict(dref=dr,stsd=m['originalStsdHeader'],avcc=av),csdHexSizeShaSelfConsistent=True,actualContainer=o,sampleHashEvidenceSource='Real original mature getNextFrame buffers hashed by frozen helper; Python does not reread media sample bytes',seventhPacketEvidence='Frozen helper checks getNextFrame()==null before setting actualContainerObservation; successful original observation/status proves gate ran without failure. Not a separately emitted raw field or additional native EOF read.',trackHeaderDurationEvidence='Original frozen helper checked actual track-header duration normalization1200000us before setting observation; raw trackHeaderDuration not separately emitted and not invented here.',originalInputBudget=dict(requested=17787,returned=17786,wholeHashRequestedIncludingEof1=8850,wholeHashReturned=8849,rootAndDemuxMetadataRequestedReturned=897,sampleReadsRequestedReturned=8040,readCalls=18,seeks=20,nativeEof=1,lastPosition=8096,positionScope=i['positionScope']),externalOriginalHashBytes=17698,actualHelperSupportClassloadLines=comSourceRows,originalPythonControllerToolReceipt=dict(chunkId='f1baf3',exitCode=0,originalCheckerExitCode=0),actualMediaWrites=0,scope='D1QUAL03-CANDIDATE-001',noSecondQualificationRun=True))
save(E/'file-to-internal-representation-comparison.json',dict(status='ACTUAL_FILE_PARSE_AND_PRIOR_INTERNAL_RECORD_COMPARISON_ONLY',samples=comparison,actualFileCsdMatchesPriorInternalRecord=True,originalRawAuBytesPreserved=False,originalRawAuWholeHashesIndependentlyRecomputed=False,noHypotheticalReconstructedRawAuHash=True,normalization='Mature H264Utils converts packet AVCC lengths to AnnexB prefixes; no PS reinsertion or encoder/decoder'))
rootsTable='\n'.join('| '+x['fourcc']+' | '+str(x['offset'])+' | '+str(x['size'])+' | '+str(x['headerBytes'])+' |' for x in roots)
samplesTable='\n'.join('| '+str(x['index'])+' | '+str(x['fileOffset'])+' | '+str(x['avccBytes'])+' | '+str(x['ptsUs'])+' / '+str(x['dtsUs'])+' | '+str(x['durationUs'])+' | true / IDR5 |' for x in samples)
hashTable='\n'.join('| '+str(x['index'])+' | '+x['avccSha256']+' | '+x['matureNormalizedAnnexBSha256']+' |' for x in samples)
csdTable='\n'.join('| '+x['kind']+' | '+str(x['bytes'])+' | '+x['hex']+' | '+x['sha256']+' |' for x in csd)
report=R/'docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03_REPORT_V1.0.md'
text=f'''# D1 FIXTURE SIX01 D1QUAL03 一次实际只读容器资格报告 V1.0

2026-10-21；tester；准确scope **D1QUAL03-CANDIDATE-001**。

## 结论

**PASS_HOST_CONTAINER_QUALIFICATION_ONLY**。一次冻结checker03真实只读检查通过，已从准确文件取到原dref/stsd/avcC观测值、typed AliasBox self-ref、单AVC视频零音频/256×144/identity matrices、六实际sample/CSD/NAL/关键帧、真实stts DTS与PTS及1200000us容器时长；全文件hash、原预算、CodeSource和原input/facade/worker/Popen两流返回门全部成立，firstError=null，无UNKNOWN，新增缺陷0。

这只签**此8849B准确文件的有限本机容器资格**。不签全AVC语法安全、密码学无加密、成熟库内部分配隔离、解码等效/Media3/Android/产品隔离HOST_ISOLATED_FORMAT_V1/READY COMMIT/播放。未运行encoder/decoder/生成或设备，输出媒体0，旧48945/17257未查询/attach/终止。D1未过M0未启，不自动进入Android或其他后续测试。

原D1QUAL01实际BLOCKED、checker02整体API缺口与coder旧辅助FAIL等历史报告不改。此结论来自新准确一次范围及已审fork/checker03实际文件运行，不能反写为旧失败已运行成功。

## 准确许可与前后不可变身份

依据 docs/milestones/D1_FIXTURE_SIX01_CONTAINER_QUALIFY03_TESTER_REQUIREMENTS_V1.0.md，原字节快照保全。准确媒体 D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4，**8849B，SHA256 19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c**。前/后生成seal ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4全部38文件实际size/hash相同，媒体readonly、路径各级无symlink/reparse，未修改、重命名或再次生成原文件。

checker03准备报告dbb128a02077e232042f59e1bce8cbe32061e9e2cf0132035798c904d8ab46a3及manifestcf2d8855e991387b887907e69aeacfb64135256aa5d1fae7b0d041709b48353a的52项前后全hash相同；**6helper+2support**完整文件集合与各自源码/class/hash/JDK合同严格一致，无test/launcher/额外类。唯一JCodec fork **1930955B/SHA2561a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86**，版本0.2.5-videokit-observation01；原c4ed全JAR不在runtime，只有原两准确support类独立目录，不重编译或改库/门。

唯一argv逐项使用future-execution-contract03原模板，只绑定三项hash/bytes8849/scope新值，固定java、-Xmx256m、-XX:-UsePerfData、原classload log flag、6helper;2support;唯一fork classpath和Six01ContainerQualifier03主类均不增减；exact-bound-scope.json保留原模板/实际逐项三处差异，未复用D1QUAL01。

## 同一次原Popen、原两流及清理完成

原controller owner登记于preflight及Popen前；新cwd仅本证据root/control-001，所有classload写该新root，shellFalse/stdin null，清五项Java注入环境/CLASSPATH，固定TEMP/TMP/JAVA_HOME。只一次checker JVM，历史PID **{owner['pid']}**，{owner['startUtc']}至{owner['endUtc']}自然exit0，控制器约{owner['elapsedSeconds']:.3f}s；原Popen及stdout/stderr句柄均真实归还。

原stdout **13708B**/stderr **0B**，strictUTF8全量小于1MiB，恰1条final、0pending/杂行。所有原字节保留并重新JSON解析与final原对象完全相等；firstError=null、status HOST_CONTAINER_QUALIFICATION、scope/hash/EOF/timely/close/join全相符，不能仅凭exit0或最后一条JSON补绿。原Python控制器工具chunk f1baf3亦自然exit0，本报告不以当前PID查询代原返回。

InputOwner在原FileChannel打开前登记，同一个只读descriptor完成全hash/EOF、root/metadata与sample读取，最终CLOSE_RETURNED、sameOriginalCloseReturned=true、nativeInFlight0/operationNONE/uncertain false。library facade通过同一guard归还，finally不二次native close；originalInputAndLibraryReaderReturn=true。worker body最后cleanup后完成点elapsed **111550000ns**、observer111832100ns<60000000000ns，原completed-start差重算一致，sameOriginalExternallyJoined/timelyBodyAndOriginalJoin=true。body点非OS退出，原worker join/原input close/facade/原进程两流自然返回分别举证；无kill/interrupt/attach/二close/退款/重试。

## 原字段实际观测：此前缺口现已从文件取得

**dref**：fork原parse observed=true，raw versionFlagsWord0/version0/flags0；原unsigned declared count1、实际children1，body20=原prefix8+child12。实际child是 **alis / org.jcodec.containers.mp4.boxes.AliasBox**，header8/body4、sampleEntry dref index1、childversion0/flags恰1、matureAliasIsSelfRef=true、fileName/extras为null/recordSize0。此次是真实文件解析值，区别于原QUAL01只能从生成源推断alis；没有Leaf白名单或借receipt反填。

**stsd**：原parse observed=true，raw VF0/version0/flags0、原声明count1==actualchild1，实际body125==8+实际sample-entry完整size117；实际entry avc1/256×144，原严格门保留。没有从actual count或builder/write反推原声明头，政策拒绝尾部的门已通过。

**avcC**：原parse observed=true，configurationVersion1；rawLengthSizeByte255、高6reserved63/全1、实际NalLengthSize4；rawSpsCountByte225、高3reserved7/全1、原SPS声明1==actual1，PPS原uint8声明1==actual1。实际body23==7+每PS(payload+3)总和，payload7+3=10B，无本受限格式的额外tail/extension。完成位与这些合法性/count/长度检查分开，均通过；真实原字段不取自生成内部观察。

## 实际root、轨道与保护信号范围

| root | offset | size | header bytes |
| --- | --- | --- | --- |
{rootsTable}

root按真实offset/size连续完整覆盖0..8849；mdat16字节extended header，payload **[56,8096)=8040B**，四root唯一一ftyp/moov/mdat与允许wide。实际parsed tree25个box，含moov/mvhd/trak/tkhd/tapt/clef/prof/enof/mdia/mdhd/hdlr/minf/vmhd/dinf/dref/alis/stbl/stsd/avc1/avcC/stsc/stsz/stts/co64，无ctts或edts记录。

实际总轨道1、视频1、音频0，原检查无timecode/其他轨道；单未保护avc1入口，entry与真实SPS尺寸256×144。track和movie矩阵均 **[65536,0,0,0,65536,0,0,0,1073741824]**，identity/rotation0。有限已解析box范围未见已知保护信号（encv/enca/sinf/senc等拒绝门通过），**不是全内容密码学“无加密”或RCE安全证明**。

## 六实际sample、时间线和第七packet

原成熟createRawMP4Demuxer保持AVCC，固定复用262144B buffer，每个实际sample1340B、总8040B。独立按receipt真实file offset重算连续覆盖mdat payload，无gap/overlap，未再次读取媒体片段或自写parser。

| index | 实际file offset | AVCC bytes | PTS us / DTS us | duration us | container key / actual NAL |
| --- | --- | --- | --- | --- | --- |
{samplesTable}

实际packet PTS/media-composition PTS单位0..5、timescale5、duration1；DTS由**真实stts entries**累积，无edits/零ctts条件，再与packet PTS核对，不能把getMediaPts直接当独立DTS。media/stts/movie实际durationUnits均6，timescale均5，精确整数换算总 **1200000us**，最后PTS1000000+200000结束1200000。实际trackHeader duration也由冻结helper在发observation前核归一1.2s，但raw getter值未单列在原JSON，**本报告不伪造单独raw trackHeaderDuration字段**。

第七getNextFrame在冻结helper中实际检查null后才设置本次actualContainerObservation/HOST状态；原完整成功状态与准确源码门构成该断言成功的证据，**原JSON未单列seventhPacket字段**，不以报告新增bool冒原日志。它是demux sample EOF，不是新native EOF；全文件native EOF来自此前完整hash。

每sample实际1个type5 IDR NAL/1336B，+4字节长度前缀=1340，mature split覆盖全sample；所有container keyflag和actual IDR均true，不只信keyflag。实际AVCC与仅由成熟H264Utils在副本上规范化的AnnexB各自hash独立：

| index | AVCC SHA256 | normalized AnnexB SHA256 |
| --- | --- | --- |
{hashTable}

转换是NAL length-prefix到start-code的表示转换，不是编码/解码。上述sample字节hash来自原helper真实getNextFrame buffer；Python只审原JSON和来源，不声称再次独立重开sample算hash。

## 实际CSD及与原内部记录的有证对应

| 实际表示 | bytes | 实际hex | SHA256 |
| --- | --- | --- | --- |
{csdTable}

SPS真实payload7B成熟解析得到256×144，PPS3B成熟解析成功；normalized CSD20B。Python对原receipt中的实际hex重新算size/SHA自一致吻合；这些现在来自独立文件avcC，不再仅生成器mux-track内部记录。实际文件CSD三个表示的hex/hash与先前内部记录同值，但两者来源明确分开。

六actual IDR NAL hash/1336B分别与原生成内部type5 NAL记录同值；这只是实际文件NAL摘要与原内部摘要的有证对应。原raw encoder AU各1360B含SPS/PPS，与当前AVCC1340B或normalized AnnexB1340B不同，**没有原raw AU字节，仍不能独立重算其whole-AU hash**。本批不拼SPS/PPS回去造假设raw AU、不冒raw wholehash已验证；完整对应表另存file-to-internal-representation-comparison.json。

## 实际累计预算、位置和外部读账

原native requested累计 **17787B**≤1048576，实际returned **17786B**：全文件hash请求8849+EOF预留1=**8850B**/returned8849；root/demux metadata重读**897B**请求/返回；6sample实际**8040B**请求/返回。分项由原seek trace、真实sample sizes和冻结读取顺序及计量差交叉核，总量不只最终文件大小，也不退款；原JSON无每次read事件列表，不能冒逐read独立trace。

实际read18次≤4096、seek20次≤128，块guard64KiB，nativeEOF1；最后原adopted position **8096**而非文件末尾8849，因为最后读取的sample在mdat末尾，metadata已在之前读过。close后scope准确LAST_ADOPTED_BEFORE_ORIGINAL_CLOSE；全hashEOF和第七packet null与当前位置不同，不能要求position=fileSize或重复EOF探测补绿。

六sample每1340≤262144、总8040，CSD10B payload/20B规范化在64KiB内、单NAL各1336、原1worker/heap256MiB/body60秒及root4/boxes25/depth门均在限内。成熟库内部metadata分配界仍UNPROVEN，不因1MiB原文件/读预算就证明隔离；只准这份良性准确hash文件。

外部前38身份核媒体8849B+原返回后38保全核8849B=**17698B**，独立ledger记录，不倒灌原17787读账或原生成340626账本。本窗口未解压ZIP媒体成员读payload，归档文件仅整体控制hash；JDK/JAR/helper/source/支持/classload等控制身份另类。全部口径是逻辑应用读取，非物理磁盘/cache IO推算。新媒体写入0。

## 实际CodeSource、完整结算与停止

实际source proof含metadata/interface10+support2+policy3、另运行MP4Demuxer/Track/MP4Util/H264Utils/NALUnit5，共**20个具体类来源断言**；完整classload另核所有已加载org.jcodec来自唯一fork，8个物理checker/support类属于其准确目录。另有JVM生成的Job$$Lambda，其日志source为已核host Six01ContainerQualifier03而非文件URL，不假装第9个物理class或外部JAR。报告后处理首次将该lambda也按物理路径核而触发静态断言，读取原日志后按JVM host来源分层修正，未重跑资格检查。无旧c4ed full JAR/测试launcher/生成器/codec Encoder-Decoder来源，JDK charset不误报成熟媒体codec。class来源、外部全class/hash集合和真实日志共同举证，不仅看名称。

完整report/原argv/所有原输出/classload/真实字段/预算/来源/前后38+52封存与原Python/controller回执冻结后立即交负责人。新增缺陷0，未缩门、改库、补编译/重试或复用旧scope。原媒体文件仍原路径/readonly及原历史seal不改，有限HOST_CONTAINER通过只登记本新报告；后续Android/Media3或新功能批需负责人另派，本轮已停止后继。
'''
assert not report.exists();report.write_text(text,encoding='utf8')
files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
save(E/'review-evidence-manifest.json',dict(frozenUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=report.relative_to(R).as_posix(),reportBytes=report.stat().st_size,reportSha256=sha(report),overall='PASS_HOST_CONTAINER_QUALIFICATION_ONLY',scope='D1QUAL03-CANDIDATE-001',evidenceFiles=files,actualCheckerJvmCalls=1,newMediaWrites=0,newFindings=0,oldSessionsTouched=False,successorTestAdmitted=False))
print(json.dumps(dict(report=str(report),reportBytes=report.stat().st_size,reportSha256=sha(report),evidenceFiles=len(files),manifestSha256=sha(E/'review-evidence-manifest.json')),ensure_ascii=False))
