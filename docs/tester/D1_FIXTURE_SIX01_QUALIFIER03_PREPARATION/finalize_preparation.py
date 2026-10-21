from pathlib import Path
import json,hashlib,datetime,difflib,shutil
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;OLD=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER02_FIX_PREPARATION';B=R/'docs/coder/d1jcodec-observation01';TOOL=R/'docs/coder/d1fixture-tool02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
d=load(E/'policy-results.json');c=load(E/'compile-and-class-identities.json');s=load(E/'support-and-source-provenance.json');assert d['result']=='PASS_PREPARATION_LIMITED34_POLICY_MEDIA_NOT_RUN' and len(d['cases'])==34
for x in c['sources']+c['classes']+c['support']:
 p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
def body(text,needle):
 start=text.index('{',text.index(needle));n=1;end=start+1
 while n:
  if text[end]=='{':n+=1
  if text[end]=='}':n-=1
  end+=1
 return text[start:end]
old=(OLD/'Six01ContainerQualifier02.java').read_text();new=(E/'Six01ContainerQualifier03.java').read_text();preserved=[]
for name in ['static final class InputOwner','static long us(','void preflight()','void hashOriginal()','List<Map<String,Object>> rootAtoms()','int walk(Box box','void identityMatrix(','List<Map<String,Object>> csd(','@Override public void run()']:
 assert body(old,name)==body(new,name),name;preserved.append(dict(sourceRegion=name,sha256=hashlib.sha256(body(new,name).encode()).hexdigest(),unchanged=True))
(E/'checker02-to03-source-diff.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='frozen_checker02',tofile='new_checker03')),encoding='utf8')
save(E/'preserved-framework-and-diff-audit.json',dict(preservedSourceRegions=preserved,onlyNewMetadataAdmissionAndClassSourceIntegration=True,matureForkOrSupportModified=False,mediaRead=0))
lic=E/'licenses';lic.mkdir(exist_ok=False)
for p in (B/'licenses').iterdir():
 if p.is_file():shutil.copyfile(p,lic/p.name)
shutil.copyfile(TOOL/'licenses/PROJECT-CODE-NOTICE.txt',lic/'SUPPORT_PROJECT_CODE_NOTICE.txt')
(lic/'CHECKER03_PROVENANCE.txt').write_text('Internal VideoKit independent checker03 preparation. Sole JCodec runtime artifact is the audited0.2.5-videokit-observation01 fork SHA1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86. WorkerDeadline and ReceiptJson class bytes only extracted unchanged from original tool SHA c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd; old full JAR is not a runtime dependency. Source notices and project modification notices retained separately. No product, distribution, patent or FFmpeg clearance inferred.\n',encoding='utf8')
fields=[
 ('dref.original','complete required, original VF0/version0/flags0, unsigned declared1 == actual parsed children1','MetadataPolicy03.dref/parent; actual raw observation getters, never builder/write values'),
 ('dref.child','actual sample entry index1, one typed AliasBox/alis or UrlBox/url, child FullBoxversion0flags1, original child body4/normal header8, no URL/alias fields/extras','DataReferencePolicy03 inherited strict child guards plus original parent policy'),
 ('stsd.original','complete required, original VF0/version0/flags0, unsigned declared1 == actual child1, exact header body8+actualchild size','MetadataPolicy03.stsd/parent; full checker retains actual VideoSampleEntry avc1 256x144/dref1'),
 ('parent.body','actual ordinary8 header, original body size equals original prefix8 plus real child headers/sizes; reject unconsumed tail','Mature Header/NodeBox public APIs; no rescan/parser or serialized parsed object'),
 ('avcc.original','complete required, configurationVersion1, full rawLengthByte reserved high6 allones and lowbits+1=actual NalLengthSize4','MetadataPolicy03.avcc; mature fork original consumed getters'),
 ('avcc.counts','rawSpsByte top3 allones, low5 actual declaredSPS1..16 == actual list size; original PPSuint8 1..16 == actual list size','Declared and actual retained independently, never from builder'),
 ('avcc.body','actual normal8 header and body7+sum(each SPS/PPS payload bytes+3), no extensions/tail; original payload sum bounded64KiB','Mature Header/list buffers only; no avcC byte parser'),
 ('csd/samples','original existing actual SPS dimensions/PPS parse, actual CSD/NAL representations/count/6samples/AVCC and normalized hashes','unchanged mature H264Utils usage, no decoder'),
 ('timeline/tracks','onevideo/noother, identity matrices, protected box rejects, stts-derived DTS/zeroctts/noedits, actual integer1200000us layers','unchanged original qualification gates'),
 ('origin','exact helper6/support2/fork oneJar pin before future runtime; package version and actual class CodeSource asserts','OriginFence03 metadata tested15classes; futureRuntime adds demux/MP4Util/H264Utils/NALUnit source assertions, not executed in preparation'),
 ('owner/ledger','same readonly fd/hash+all rereads requested1MiB, block64K/read4096/seek128, once close/body-last-point/join/Popen separate','InputOwner/WorkerDeadline/ReceiptJson unchanged; external receipt combined cap1MiB'),
 ('observation','partial metadata and class provenance emitted only after actual original worker join; complete only prior actual parse return','No default/counter/generator golden as field proof, failure retains partial facts and unproven fields')]
save(E/'all-field-policy-and-api-contract.json',dict(status='PREPARATION_ONLY_ACTUAL_MEDIA_FIELDS_UNBOUND',fields=[dict(field=a,criterion=b,source=c) for a,b,c in fields],remainingLimits=['Finite metadata test not real video track/file qualification','Mature internal metadata allocation bound remains unproven before postparse checks','No full MP4/AVC/RCE or cryptographic no-encryption proof, no decoder equivalence','AvcC original PS header bits and other fields outside exposed getter subset are not a complete raw-byte observability claim','Mature parse observation complete never stands for all structure valid or EOF; exact admitted body-size/count/version/reserved checks remain separate','No concurrency safety claim for mutable original parsed lists; owned synchronous worker does not share them','Extended boxes/edit/nonzeroctts/unknown roots or unsupported fields block rather than infer success'],mandatoryFieldsForThisScopeAllIntegrated=True,actualMediaDataReference=None,actualMediaStsd=None,actualMediaAvcc=None,actualMediaSamples=None,actualMediaTimeline=None))
helper=[x for x in c['classes'] if x['category']=='helper'];tests=[x for x in c['classes'] if x['category']!='helper']
save(E/'future-execution-contract03.json',dict(state='FROZEN_PREPARATION_NO_ACTUAL_MEDIA_RUNTIME_AUTHORITY',inputPath='D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4',expectedSha256=None,expectedBytes=None,scope=None,scopeBinding='Await coordinator exact new D1QUAL03 dispatch; old D1QUAL01 scope never reused',exactHelperClassSet=helper,exactSupportClassSet=c['support'],uniqueJcodecJar=c['uniqueJcodecJar'],sourceIdentities=c['sources'],javaIdentity=c['javaIdentity'],excludedRuntimeClasses=tests,oldFullToolJarRuntimeAllowed=False,argvTemplate=['D:/Android/Android Studio/jbr/bin/java.exe','-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp',str(E/'helper-classes')+';'+str(E/'support')+';'+str(B/'artifacts/jcodec-0.2.5-videokit-observation01.jar'),'com.videokit.fixturetool.Six01ContainerQualifier03','--expected-sha256=<NEW_EXACT_AUTHORIZED_HASH>','--expected-bytes=<NEW_EXACT_AUTHORIZED_SIZE>','--scope=<NEW_EXACT_AUTHORIZED_SCOPE>'],budgets=dict(inputMax=1048576,cumulativeNativeRequestedReadIncludingHashAndAllDemuxRereads=1048576,blockMax=65536,readCalls=4096,seeks=128,samples=6,sampleMax=262144,csdMax=65536,nalsPerSampleMax=64,rootsMax=16,boxesMax=512,depthMax=16,jvm=1,worker=1,heapMiB=256,bodyObserveSeconds=60,allOriginalStdoutStderrUtf8=1048576,mediaOutputs=0),controllerObligations=['Bind exact frozen benign input readonly canonical regular no-reparse identity after NEW authority; no media query in this preparation','Verify six helper/two support exact class-file sets/hashes and source/JDK/fork manifest/hash; no org.jcodec or JAAD or Main/Job classes in support; no original full JAR classpath/fallback','Fresh unique cwd/temp; clear Java injection keys/CLASSPATH; shellFalse/stdinNull; original Popen+both streams registered before allocation; one exact invocation only','Keep every pending/final and all strictUTF8 stdout+stderr combined1MiB; exit0 not enough; actual firstError/status/metadata/fields required','Same original input native close once and library facade return, body-completion marker and original worker actual join, exact original process natural return+stream close separately evidence','UNKNOWN sticky closes admission but retains original handles/Job/streams, no kill interrupt second close refund or retry; no successor if any return unknown','Pre/post exact immutable input/fork/helper/support/JDK identities, external hash/control/classload reads separately budgeted not hidden in original1MiB ledger or physical IO claims','Verify all loaded JCodec classes source unique fork, support source exact directory, helper source exact helper classes; do not classify JDK charset as media codec','Full HOST_CONTAINER assertion only if actual complete raw metadata and every unchanged track/sample/timeline/NAL/protection/budget/return condition proven. No automatic Android/Media3/isolated/READY COMMIT/playback'],actualPreparationQualifierRuns=0,actualPreparationMediaReads=0))
save(E/'future-receipt-schema03.json',dict(state='CONTRACT_NOT_ACTUAL_FILE_OBSERVATIONS',newRequiredFields=['actualCodeSourceProof','actualDataReferenceChildObservation.originalDrefHeader','actualOriginalMetadataObservation.originalStsdHeader','actualOriginalMetadataObservation.originalAvccHeader'],originalParentFields=['observed','rawVersionFlagsWord','version','flags','declaredCountUnsigned','actualParsedChildren','actualHeaderBodyBytes','bodyFromActualChildrenAndOriginalPrefix'],avccFields=['observed','configurationVersion','rawLengthSizeByte','lengthReservedHigh6','actualNalLengthSize','rawSpsCountByte','spsReservedHigh3','declaredSpsCount','declaredPpsCount','actualSpsCount','actualPpsCount','actualHeaderBodyBytes','bodyFromObservedCountsAndActualPayloads','actualCsdPayloadBytes'],existingRequiredFields='all original whole-file hash EOF, raw demux6samples/CSD/key/NAL/PTS-DTS/duration/rotation/protection and original owner ledger/worker/process returns retained',actualFileValues=None))
comp=d['compiler'];proc=d['policyProcess'];summary=d['summary'];supportTable='\n'.join('| '+Path(x['path']).name+' | '+str(x['bytes'])+' | '+x['sha256']+' |' for x in c['support']);caseTable='\n'.join('| '+x['case']+' | '+x['result']+' | '+x.get('actualReason','有限metadata政策接受，非完整文件资格')+' |' for x in d['cases'])
report=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION_REPORT_V1.0.md'
text=f'''# D1 FIXTURE SIX01 Qualifier03 观测后端接入准备报告 V1.0

2026-10-21；tester；QUALIFIER03_PREPARATION。

## 结论

**PASS_PREPARATION_LIMITED34_POLICY_MEDIA_NOT_RUN**。基于冻结checker02接入已独立审定的观测fork，必须的dref/stsd原VF/unsigned声明count及avcC原版本/reserved/count、actual对照与完成来源全部接入；原typed-child严格门及其他track/sample/timeline/hash/预算/原返回门未削弱。一次新helper编译与单个非媒体政策JVM成功，**34case=4接受+30拒绝**，实际原worker/loader/Popen两流归还。

本阶段**actual qualifier调用0、实际MP4读/查询/hash0、demux/生成/encoder/decoder/设备0**，未来input hash/bytes/scope保持UNBOUND；未取得HOST_CONTAINER资格，不接Android/Media3/隔离READY COMMIT/播放。原QUAL01实际BLOCKED及coder旧辅助FAIL不回写，不因准备通过称旧原媒体已合格。整体容器目标仍待新准确实际批，D1未过M0未启，旧48945/17257不碰。

依据 docs/milestones/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION_TESTER_REQUIREMENTS_V1.0.md；原要求快照随证据，所有新产物仅新tester目录。没有改fork/原支持类/原工具或产品依赖，没有自写MP4/AVC parser。

## 唯一JCodec来源与精确支持集

准确fork JAR **1930955B/SHA2561a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86**，版本0.2.5-videokit-observation01；前置核其原seal8a62ef8e...全部2738记录、已独立B报告6b71997ce6ad6136cdea7f7908e102bc460e6933b7c288e78657c6fb5cbbf59b与25证据不变。checker02报告18bc...及31证据准备时亦核不变。没有把原c4ed全JAR放进编译或运行classpath。

原工具仅静态读取准确JAR c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd，提取已审现有支持class，不重新编译：

| 支持class | 大小B | 原class SHA256 |
| --- | --- | --- |
{supportTable}

support目录**严格只有这2class**，SourceFile/major55/方法Code SHA与原JAR、原class-origin02、原源hash/seal绑定一致；无嵌套支持class需要附带、无org.jcodec/JAAD/encoder/Main/Job。原WorkerDeadline/ReceiptJson语义和字节均不改，来源与项目通知单列，不用源码重编译产生“看似同名”类。

未来runtime唯一classpath为**helper-classes6 + support2 + 准确fork JAR**，不含测试/launcher/原全工具JAR。OriginFence03核fork Implementation-Version和actualCodeSource：本非媒体JVM实际核10个成熟metadata/interface类、2支持、3checker policy/origin类共15个；未来helper main另核MP4Demuxer/Track、MP4Util/H264Utils/NALUnit来源，**该媒体来源分支本阶段未执行**。全部JCodec类的唯一来源还依赖准确classpath及无额外org类的冻结类集合/外部classload审计，不用一小部分class断言冒977类逐个runtime执行。

## 原始字段准入合同

dref/stsd必须hasOriginalParseObservation=true，再读真实原raw VF word/version/flags/unsigned declared count，要求VF0/version0/flags0、declared1且等actual children1。声明与actual分列，不从children或doWrite反填。实际普通8B parent Header的body必须恰为原prefix8+实际child完整size总和，拒绝parse正常返回但未消费的tail；完整模式还保留stsd实际VideoSampleEntry avc1/256×144/dref1原检查。

dref child保留原checker02严格门：唯一实际entry/index1，fourcc与真实class对应AliasBox/alis或UrlBox/url，child原FullBoxversion0/flags**恰1**、普通8B header/body**恰4**，无aliasfileName/extras/record或externalURL。没有LeafBox白名单、只看alis名字、flags仅&1、builder default或序列化parsed对象造原值。

avcC必须原parse observation真；原configurationVersion1；完整rawLengthSizeByte reserved高6全1、low2+1等actual NalLengthSize4；原SPS count byte高3全1、low5声明SPS与实际list count相等；原PPSuint8与actuallist count相等，SPS/PPS各1..16。原Header body精确 **7+Σ(每SPS/PPS实际payload bytes+3)**，不接额外extension/tail；原payload总量受64KiB约束，原CSD/SPS尺寸/PPS解析、normalized CSD与6sample数据/NAL/时基门仍继续核。

完成位只表示原parse正常返回，**不是合法性或全EOF**；这些version/flags/reserved/count/body政策独立在complete后拒绝。失败时partial原观测保留到joined receipt，默认/未完成不填0冒观测；不能由生成内部receipt复制golden。完整字段/API限制与未来schema分别见all-field-policy-and-api-contract.json、future-receipt-schema03.json。

## 已审框架保持及实际编译

checker02→03完整diff封存，静态逐区核InputOwner整个class、us整数映射、preflight、hashOriginal、rootAtoms、walk、identityMatrix、csd、原Job.run cleanup正文完全一致并记录区域SHA。只变新类/收据名称、新metadata政策/source proof接入与输出；只在新fork getter可实际观察且政策通过时移除旧“API永远不可得”的硬阻塞，不删必须字段门。

固定JDK原身份精确核；一次javac PID{comp['pid']}，{comp['startUtc']}至{comp['endUtc']}自然exit0/约{comp['elapsedSeconds']:.3f}s，原stdout/stderr及两捕获handle归还、unknown false。-J-Xmx512m/--release11/UTF8/-proc:none/-implicit:none/空source/processorpath，classpath仅support+准确fork，未隐式补源/重建成熟库/打JAR或联网。

实际9个新class major55，source/class/方法Code hash与原javac输出/复制一致：**6 helper +2 test-only +1纯JDK launcher**。运行测试时主classpath仅launcher，原worker分配前登记自有URLClassLoader，子classpath为test/helper/support/fork，parent=platform；不存在旧JCodec fallback。后续实际helper runtime只用6+2+fork，不用测试loader/launcher。

## 唯一非媒体政策JVM及34项结果

原policy JVM PID{proc['pid']}，{proc['startUtc']}至{proc['endUtc']}自然exit0/约{proc['elapsedSeconds']:.3f}s；heap256MiB/总5秒、原worker清理后elapsed **{summary['elapsedNanos']}ns**。holder-before-loader、allocation returned、同原worker单次loader close returned、body returned和实际join全有真实receipt；同原Popen自然退出/原两流关闭分别有回执，unknown false，无kill/interrupt/二close/重试。没有以源代码推测不存在的返回字段。

显式metadata payload **3133B**+成熟Header/fourcc等保守scratch **2048B**=**5181B≤8192B**；原stdout{d['rawStdoutBytes']}B/stderr0、strictUTF8全量≤1MiB，正反case的实际partial观测/拒绝理由、CodeSource与最终原返回日志均完整保留。实际classload确认所有已加载JCodec来自fork，支持来自support，原videokit-fixture-tool02.jar未加载；无资格helper/SixFrameDriver/demux/mux/编码器解码器类加载，JDK charset不误报。

测试只构造自有有限metadata、调用成熟parse和真实getter。stsd正例只验original-header/唯一实际entry政策，使用有限free child；**不冒真实VideoSampleEntry/完整轨道正例**，全checker原VideoSampleEntry门仍在。avcC自有23B metadata源于之前批准冻结CSD payload，仅元数据测试不冒有效媒体。count不一致用真实原头，实际list差异通过公开既有可变API构造拒绝对象，不反射改私有状态。full external alias路径未在此解析，未知/外引用门不放宽。

| 用例 | 实际结果 | 接受范围或拒绝原因 |
| --- | --- | --- |
{caseTable}

## 未来准确命令、原预算与限制

future-execution-contract03.json列完整6helper+2support集合/hash、6源码/JDK/fork唯一身份、排除test/launcher、固定输入路径、未来argv模板；**expectedSha256/expectedBytes/scope全null/UNBOUND**，不读取或查询媒体来填它们。只有负责人另派准确D1QUAL03才能绑定执行，不重用D1QUAL01或任何旧失败scope。

未来仅一个原JVM/worker，heap256MiB/body观察60秒；同一只读NOFOLLOW原fd先核完整SHA及实际EOF再raw demux，累计native requested **1MiB包括hash+全部重读**，块64KiB/read4096/seek128。原sample6/每个262144/CSD64KiB/NAL64/root16/boxes512/depth16不变，原sample key/实际IDR/AVCC与独立AnnexB hash/精确stts DTS及ctts PTS/timebase/layered1200000us/第七EOF/identity矩阵/有限保护box门不减。

原holder在分配前、同原close一次、facade return、body最后完成点、原worker join、同原Popen/全两流自然返回和前后immutable身份分别举证。60秒超窗或异常关准入、sticky UNKNOWN保管原Job/句柄/流，不kill/interrupt/二close/退款/重试，不以exit0/后迟返或最后JSON补绿。所有pending+final/stdout+stderr UTF8合计1MiB，不tail；外部hash/工具身份/control/classload读另列，不能倒灌原1MiB或冒物理磁盘流量。

本合同所需新增观测字段已有真实API与有限政策接入证据，**这不等所有原MP4/AVC字节信息完整保留**；PS头其他bit/保留字段、全语法/RCE、密码学无加密、并发可变对象与成熟库内部metadata allocation边界、解码等效仍有限或未证。可信准确良性文件范围之外不推断安全，不添加坏atom/资源探针或另parser。未知/不支持、edit/nonzeroctts/不完整字段继续BLOCKED。

fork原版权/FreeBSD/JAAD PublicDomain+FreeBSD/GuavaApache2、新修改通知/SBOM与原support项目说明均保留在licenses；不冒官方未修改身份、产品发行/专利/FFmpeg许可。原工具、fork、旧helper、产品依赖均未改。

本准备新增缺陷0，实际文件资格尚未运行。完整源码/class/support/CodeSource/编译与政策原返回/字段schema/未来合同冻结发负责人，等待准确实际D1QUAL03另派，不自动读MP4或做后续测试；D1未过M0未启，旧UNKNOWN保持。
'''
assert not report.exists();report.write_text(text,encoding='utf8')
files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json'];assert sum(x['bytes'] for x in files)<16777216
save(E/'review-evidence-manifest.json',dict(frozenUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=report.relative_to(R).as_posix(),reportBytes=report.stat().st_size,reportSha256=sha(report),overall='PASS_PREPARATION_LIMITED34_POLICY_MEDIA_NOT_RUN',evidenceFiles=files,evidenceBytes=sum(x['bytes'] for x in files),compileCalls=1,policyJvmCalls=1,actualQualifierCalls=0,mediaReads=0,oldSessionsTouched=False))
print(json.dumps(dict(report=str(report),reportBytes=report.stat().st_size,reportSha256=sha(report),evidenceFiles=len(files),manifestSha256=sha(E/'review-evidence-manifest.json')),ensure_ascii=False))
