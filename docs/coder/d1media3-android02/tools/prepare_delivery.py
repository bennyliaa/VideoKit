from pathlib import Path
import json,hashlib,shutil,datetime,zipfile,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';O=R/'docs/coder/d1media3-android01'
assert not (E/'media3-android02-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
for x in json.loads((E/'build-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
receipt=json.loads((E/'build-main-001/receipt.json').read_text(encoding='utf-8-sig'));assert receipt['exitCode']==1
assert 'Could not connect to the Gradle daemon.' in (E/'build-main-001/gradle.log').read_text()
assert not list((B/'app').rglob('*.apk')) and not list((B/'artifacts').glob('*.apk'))
shutil.copyfile(B/'build-tools-gradle-home/daemon/9.5.0/daemon-35512.out.log',E/'build-main-001/daemon-35512-preserved.log')
for n in ['javac','metadata']:
 p=E/f'nonmedia-001/{n}-owner.json';x=json.loads(p.read_text());assert x['exitCode']==0 and x['originalProcessReturned'] and x['captureHandlesClosed']
assert 'DONE nonMediaChecks=20 originalsReturned=true' in (E/'nonmedia-001/metadata.stdout').read_text()
assert 'DONE independentBoundaryPasses=8' in (E/'nonmedia-001/metadata.stdout').read_text()
orig=[]
for rel,expected in [('docs/coder/d1media3-android01/evidence/media3-android01-freeze.json','fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a'),('docs/coder/d1media3-container02/evidence/media3-container02-freeze.json','0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d'),('docs/coder/d1jcodec-observation01/evidence/observation01-freeze.json','8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725')]:
 p=R/rel;assert sha(p)==expected;rows=json.loads(p.read_text())['files']
 for x in rows:assert sha(R/x['path'])==x['sha256']
 orig.append({'seal':rel,'sha256':expected,'verifiedRows':len(rows)})
dump(E/'baseline-preservation.json',orig)
qual=R/'docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION03/review-evidence-manifest.json';m=json.loads(qual.read_text());assert sha(R/m['report'])=='a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926'
for x in m['evidenceFiles']:assert sha(R/x['path'])==x['sha256']
dump(E/'qualification-preservation.json',{'manifest':pin(qual),'report':pin(R/m['report']),'evidenceFiles':len(m['evidenceFiles']),'allUnchanged':True,'onlyFrozenFileIdentityAndReportsNoMediaParserRun':True})
changes=[]
for folder in ['src','android','upstream','instrumentation']:
 for p in sorted((B/folder).rglob('*.java')):
  rel=p.relative_to(B).as_posix();old=O/rel.replace('/android02/','/android01/')
  if old.exists() and old.read_bytes()==p.read_bytes():continue
  changes.append({'path':rel,'oldSha256':sha(old) if old.exists() else None,'newSha256':sha(p)})
  delta=''.join(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],p.read_text().splitlines(True),fromfile='frozen-android01/'+str(old.relative_to(O)),tofile='android02/'+rel))
  d=B/'patches'/Path(rel).with_suffix('.patch');d.parent.mkdir(parents=True,exist_ok=True);d.write_text(delta,encoding='utf-8')
dump(E/'source-differences.json',changes)
# No build success or actual consumption is inferred from inherited artifact hashes.
for name in ['gradle/verification-metadata.xml','app/gradle.lockfile','settings-gradle.lockfile']:
 assert (B/name).read_bytes()==(O/name).read_bytes()
deps=[]
for p in sorted((B/'deps').glob('*.jar')):
 assert sha(p)==sha(O/'deps'/p.name)
 with zipfile.ZipFile(p) as z:assert not any(n.startswith('org/jcodec/') for n in z.namelist())
 deps.append(pin(p))
dump(E/'dependency-license-and-consumption.json',{'candidateDependencyChanges':[],'verificationAndLocksByteIdentical':True,'runtimeAndTestClosures':'NOT_RESOLVED_IN_ANDROID02_DAEMON_CONNECT_FAILED','intendedInheritedAppRuntime':17,'intendedInheritedTestRuntime':0,'actualAndroidJavacClasspath':'NOT_OBSERVED','nonMediaJvmOnlyDependencies':deps,'licenses':'All inherited Android01/Container02 source/binary/metadata closure and Apache2 notices preserved; no new dependency or download; Android SDK Os.open built-in API used only by experiment','jcodecIncludedInSourceSetsOrDeps':False,'sourceOriginEvidence':'reference/android01 and reference/android01-sbom.cdx.json; references are outside every APK sourceSet'})
cases=[('inspectKnown','actual qualified MP4 full hash/EOF,one track,6 AnnexB samples/CSD/PTS/duration'),('inspectShort3','same actual parser with max3-byte provider reads; cumulative attempts not reset'),('inspectUnknown','same parser with unknown length; real native EOF mandatory'),('inspectSeek1s','same file; actual seekable SeekMap and1s replay; unsupported map is unsupported, not PASS'),('muxQualified','actual captured6 through FragmentedMp4Muxer and same TemporaryOutput; sync/close/original return/read-only grant; actual FragmentedMp4Extractor comparison'),('preopenAdmission','capability/container/seek guards before source open'),('rejectFixture','reject BBB hash before IO/writer'),('cancelLateRead','controlled non-media provider future: caller returns cancelled, same original read/close withheld then returned, caller bytes unchanged'),('writerPending','controlled non-media writer ACK before same original thread return; no reopen/no release/no duplicate close; then actual join'),('bbbObserve','inherited approved BBB observation only; cannot reach mux')]
plan={'status':'NOT_EXECUTABLE_NO_ANDROID02_APKS_NO_DEVICE_AUTHORIZATION','app':'com.videokit.d1media3.android02','test':'com.videokit.d1media3.android02.test','runner':'com.videokit.d1media3.android02.test.Media3Instrumentation','process':'com.videokit.d1media3.android02:media3','version':'D1-MEDIA3-ANDROID02-CONTAINER','apks':None,'signer':'NOT_VERIFIED_NO_ARTIFACTS','fixtureSha256':'19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c','futureScopeId':None,'futureDeviceSerial':None,'freshIdleGate':None,'cases':[{'case':n,'entry':'Media3Instrumentation.onStart -> ExperimentJob.run','expected':v,'requiredArguments':['case='+n,'fixtureSha256=19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c','runId=D1MA02-<fresh reviewed unique id>'],'AndroidRuntime':'NOT_RUN'} for n,v in cases],'sameScopeBudget':{'sources':2,'perSourceReadConcurrency':1,'queuedReads':0,'inputAttemptedBytesAllCopyHashParseSeekReopen':8388608,'outputAttemptedBytesIncludingPartialUnknownNoRefund':16777216,'blockBytes':65536,'sampleBytes':262144,'receiptUtf8PerStatus':262144,'methodDeadlineMs':60000},'allFutureOperations':{'preflightTextMaxBytes':1048576,'installOutboundBinaryBytes':'exact future frozen appBytes+testBytes once; currently UNBUILT, no permitted binary egress','fixture':'test APK embedded8849B included in future exact APK transfer, no arbitrary push','instrumentationTextInboundBytesPerMethod':4096,'receiptCaptureTotalBytesPerMethod':1048576,'methodsMaximum':10,'totalRuntimeReceiptCaptureBytes':10485760,'logcatOrUnboundedShell':False,'retryReinstallClearForceStopPullOtherProjects':False,'evidenceDestination':'new coordinator-bound absolute tester directory, original stdout/stderr/status/full raw owner evidence; no external messages by runner'},'stopConditions':['no exact APK/hash/signer/fresh gate => do not start','any UNKNOWN/timeout/original FD/thread pending => close admission, retain same owners; no force-stop/interrupt/second close/retry','fixture/CSD/sample/PTS/duration mismatch => fail, no fallback fixture or normalization tolerance','no READY COMMIT/isolated-format/decoder/audio/player/MediaCodec/GPU'], 'deviceOperationsThisBatch':0}
dump(E/'execution-plan.json',plan)
oracle={'fixtureQualification':'HOST_CONTAINER only, not Android','fileComparison':'source exact8849/hash; output wholefile hash recorded, NEVER equal-to-source requirement','sampleComparison':'actual Media3 AnnexB4 one IDR NAL1340B, exact six independent qualification AnnexB digests; flags exactlykeyframe1,PTS0..1000000 step200000; samples actual not golden-filled','csdComparison':'actual Media3 initializationData each AnnexB4; concatenate in actual order;20B digest f6dc...a8, original extraction and fMP4 reopen same; grouping may be1 or2 arrays, no injected SPS/PPS','eos':'existing E6Muxer empty size0 EOS flag4 at1200000; never7th payload. Reopened actual SeekMap or TrackOutput duration must1200000','dts':'Media3 TrackOutput exposes presentation timestamps, no independent DTS output. Host qualified noCTTS/noedits DTS=PTS facts are independent host evidence; Android receipt declares capability gap rather than fabricate DTS','seek':'actual point position/time/ranges/epoch and replay hashes recorded; no manifest-filled seek points','nativeOwnership':'CREATE_NEW O_EXCL O_NOFOLLOW0600, same E4Owned synchronous FD sync/close then read-only before parser; reused grant only after original writer/host tasks returned','retention':'new runId root preserved as private evidence after success; existing roots reject before writes. No old file removal','deadline':'body completion recorded after cleanup; completed-start must be nonnegative and strictly<60s plus actual original worker join; equality or late return sticky UNKNOWN, no process-disappearance inference','currentEvidence':'20 nonmedia parent groups including inherited8; actual Android extraction/mux/reopen/FD sync=NOT_RUN'}
dump(E/'comparison-and-lifecycle-contract.json',oracle)
matrix=[{'area':a,'implementation':i,'evidence':v,'status':s} for a,i,v,s in [
 ('fixture','exact source asset and report/hash bound','instrumentation-assets/qualified-fixture.json','PREPARED_NOT_ANDROID_RUN'),('Media3 extraction','actual pinned Mp4Extractor,short/unknown/seek,shared job input budget','source + execution-plan','IMPLEMENTED_UNCOMPILED_ANDROID'),('mux/reopen','capture6 binding/E6 EOS/temp sink/native ownership/fMP4 extractor','source + comparison contract','IMPLEMENTED_UNCOMPILED_ANDROID'),('admission/cancellation/writer return','controlled nonmedia real futures/threads/owners','nonmedia-001/metadata.stdout','PASS_LIMITED_NONMEDIA'),('MC-B01','inherited exact8 nonmedia regression','nonmedia-001/metadata.stdout','PASS_LIMITED_NONMEDIA'),('strict app/test build','one exact offline invocation, client exit1 before connection','build-main-001','BLOCKED_DAEMON_CONNECT'),('APK/signature/DEX/JAR consumption','no new artifact produced','artifact-status.json','NOT_BUILT_NOT_AUDITED'),('real Android functional cases','ten finite method entries ready as source, no execution permission','execution-plan.json','NOT_RUN'),('P0/J11/isolated format/READY/COMMIT/playback','no claim or implementation expansion','baseline + source restrictions','OPEN')]]
dump(E/'completion-matrix.json',matrix)
dump(E/'artifact-status.json',{'appApk':None,'testApk':None,'appJar':None,'testJar':None,'status':'UNBUILT_GRADLE_DAEMON_CONNECT_FAILED_BEFORE_COMPILE','signaturesDexSourceJarConsumption':'NOT_RUN_NO_ARTIFACT','intendedPackage':'com.videokit.d1media3.android02','intendedTest':'com.videokit.d1media3.android02.test','noAndroid01ArtifactCopiedAsAndroid02':True})
dump(E/'build-failure-audit.json',{'buildInvocations':1,'clientOriginalExitCode':1,'failure':'Could not connect to the Gradle daemon','firstProjectTaskReached':False,'actualStrictResolutionOrCompileObserved':False,'receiptFlagsMeanIntendedConfigurationOnly':True,'daemonHistoricalPid':35512,'daemonUid':'445eecb5-f5d5-4eba-95e5-4adeb0112c78','daemonOriginalReturn':'UNKNOWN_NOT_QUERIED_NO_PID_ATTACH_OR_KILL','newBuildRetry':0,'potentialNextPlan':'Coordinator review first; if separately authorized diagnose exact local daemon transport/sandbox before another precise build. No network-download, force-stop, occupancy probe or dependency change proposed.','oldUnknownSessionsActions':0})
report='''# D1_MEDIA3_ANDROID02_CONTAINER 完整阻塞交付 V1.0

2026-10-21。**BLOCKED_ANDROID_BUILD_DAEMON_CONNECT；没有新APK，未完成Android功能交付或执行就绪。** 本批源码、准确资产、判据、有限方法与原失败构建及非媒体自检材料集中冻结，供负责人统一审查后安排下一批；不是分片成功交付。不得安装旧APK冒Android02、自动重试或直接接实机。D1未过、M0未启。

## 1. 实现与准确样本

独立目录D:/CodexProjects/VideoKit/docs/coder/d1media3-android02，基于原Android01/Container02冻结源，不修改旧候选。新app/test包com.videokit.d1media3.android02及.test，版本D1-MEDIA3-ANDROID02-CONTAINER；原com.videokit.app不变。严格17坐标/Media3 1.9.3/锁与verification metadata原字节不变，无新下载/运行时依赖、JCodec或审计fork进入sourceSet或APK输入。

qualification03准确报告a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926及完整证据复制reference，原manifest逐项hash保持。准确8849B/SHA25619e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c合成文件原字节复制到instrumentation-assets/qualified-six-avc.mp4，与来源/qualification manifest同包准备。原文件未改/未重生成。BBB349102B旧片只留bbbObserve观察，不能送mux；任意参数path/URI或BBB hash注册被准入门拒绝。

每新runId私有root必须原不存在，输入及输出用Os.open O_CREAT|O_EXCL|O_NOFOLLOW0600再包同FileDescriptor的原FileOutputStream。原copy全EOF/hash、flush/getFD.sync/同原close真实返回及setReadOnly之后才交provider；能力与成功回执分列。成功也保留新私有run目录作证，不覆盖或删旧文件。

真实方法源码接同HostInputFactory/readAt/DataSource→Mp4Extractor，known/max3短读/unknown/真实SeekMap1秒及capture6。QualifiedObservation只比较实际getter证据与独立host资格事实，不用manifest填观测。正常muxQualified接捕获的六实际payload→MatureMuxerBinding/E6Muxer→真实FragmentedMp4Muxer→TemporaryOutput→原OutputCapability flush/sync/close/原任务归还→同只读grant→真实FragmentedMp4Extractor重开。未换框架、未加parser/转码/decoder/播放。

## 2. 预先比较合同与预算

比较合同详evidence/comparison-and-lifecycle-contract.json：Media3实际输出AnnexB4表示，每sample1340B、各1个IDR、六hash按qualification03归一摘要、keyflag1及PTS0/200000/.../1000000严格比对；不拼回旧1360B原AU。实际CSD初始化数组每项AnnexB4，按实际顺序拼接20B规范化hashf6dcad95142c58fce67217fc175449c88b9c697f07db35952c617a66199e75a8；允许成熟库自身分一或两数组，绝不回填SPS/PPS。输出容器全hash记录但不要求与输入相同。现有空EOS size0/flag4/time1200000只指定末帧200000us，非第七payload；重开必须实际duration1200000且恰六sample、同hash/CSD/PTS。

Media3 TrackOutput没有独立DTS getter。本候选显式标明其能力缺口：host已证无CTTS/edits且DTS=PTS，不冒Android独立观测DTS；Android仍比较实际PTS和容器时长。seek必须使用实际SeekMap/point/ranges/epoch/replay，无能力则UNSUPPORTED而不是用黄金表补成PASS。

同一Job跨copy/hash/parse/seek/输出重开累计输入attempt8MiB，不能换factory退款；最多2source/每源1read/queue0/块64KiB/sample262144。输出attempt16MiB：TemporaryOutput及native Host均在调用前累计预留，不以短写/未知结果退款，不只看ack字节。60秒只关准入，worker清理后记录body completion；严格<deadline且实际同worker join才可报告及时；等于/迟返保持UNKNOWN。未归还原writer/host任务不重开、不重复close、不释放原owner；真实超时/取消仍sticky。无强停/二close/自动重试/旧占用查询。

## 3. 这次构建实际失败，不伪造产物

唯一集中离线strict构建请求tasks :app:assembleDebug和:app:assembleDebugAndroidTest，--offline --no-daemon --max-workers=2 --rerun-tasks --dependency-verification strict，固定JDK/Gradle9.5.0/继承锁与17依赖，原日志/配置输入pin完整保留。客户端在UTC03:19:16.6260945至03:19:19.9766371自然exit1：**Could not connect to the Gradle daemon.** 新daemon历史PID35512/UID445eecb5-f5d5-4eba-95e5-4adeb0112c78；复制当次原daemon启动日志。未进入项目任务/实际解析classpath/Android javac/签名DEX阶段。

receipt中strict/verifyMetadata标志是请求配置，不是本次实际消费验证成功。无Android02 app/test APK、生产JAR、签名/DEX/产物来源结果，artifacts为空；未用Android01产物冒充。应用src的非平台部分虽在单独非媒体编译中通过，instrumentation/Android端未由本次Android构建编译，不能算可执行验证。新daemon最终物理返回未观测，记UNKNOWN，不查询/attach/kill、不假设host空闲。原48945/17257另保持原UNKNOWN，未触碰。

本批没有第二次Gradle构建、改缓存/锁/依赖或换环境盲试。下一步建议负责人先审完整失败包，再单独明确本次local daemon transport/必要权限和准确新构建范围；无新增执行许可可交付。旧SOURCE/预算/许可/P0不降门。

## 4. 有界非媒体自检实际证据

一次JDK javac -J-Xmx512m --release11编译src/upstream/checks/platform-fixtures及原PlatformOutputErrors，一次-Xmx256m非媒体JVM30秒观察窗，均自然exit0/原两流关闭。metadata JVM历史PID32356，UTC03:20:26.195199至03:20:27.907042。完整source pins/原class/stdout/stderr/owner在evidence/nonmedia-001；没有实际文件解析、mux、编码或设备。

Android02NonMediaCheck完成20父组：固定registry、10方法参数准入、4参数拒绝、非媒体copy EOF/hash及错hash、controlled late-read取消、controlled writer pending和继承MC-B01回归组。继承组内部8边界另外逐项有原PASS行（计数不可把20和8当28互斥顶层组）。controlled ports用真实future/thread/生产adapter/原return门，清理后同原线程join/sourceKeepers0/outputKeepers0；不是注入真实native FD故障。MC-B01原REOPEN ACK后物理尾段暂待不sticky、同原grant后续继续等8回归仍有限通过。没有重跑旧未知ContainerPendingOrderCheck或全旧套件，也不将这次退出替旧UNKNOWN收尾。

## 5. 完整方法与执行阻塞

evidence/execution-plan.json准备10有限方法：inspectKnown/inspectShort3/inspectUnknown/inspectSeek1s/muxQualified/preopenAdmission/rejectFixture/cancelLateRead/writerPending/bbbObserve；固定runner、3项参数、精确runId格式、每case入口/预期/证据出口/停止条件均列明。每case新私有root不复用旧scope。当前计划明确NOT_EXECUTABLE_NO_ANDROID02_APKS_NO_DEVICE_AUTHORIZATION，APK/hash/signer/fresh gate/scope/serial未取得，不能补旧身份就执行。

全操作出站控制：未来准确双APK各一次，bytes必须取未来冻结真实产物，本批无可用二进制传输额度；fixture只随test APK，不任意push。preflight文本≤1MiB，单次参数≤4096B，每status receipt≤262144B，每方法原输出capture≤1MiB，最多10方法总≤10MiB；不开放无界logcat/shell/其他项目pull或自动重装清数据/重试。任何UNKNOWN、原FD/thread未归还、格式/hash/时序不符即停新准入并保管原任务，不能强停求空闲或绕过门。

当前device操作0，Android提取/mux/fMP4重开/native FD fsync真实功能均NOT_RUN。完整离线B也不能签产品isolated format/READY COMMIT/J11/RCE/播放；同UID仅良性实验。evidence/completion-matrix.json逐项列实现、已证和阻塞，APK/签名/DEX/真实classpath消费待新构建，未隐藏功能缺口。

## 6. 冻结与交接

材料入口tools/review_materials.py只做Python文件/hash/ZIP/日志身份检查，不编译/JVM/Gradle/设备；冻结evidence/media3-android02-freeze.json及外置D1-20261021-MEDIA3-ANDROID02-CONTAINER-source.zip涵盖本候选相关源、准确asset/来源、依赖/原许可/继承SBOM、变更patch、原构建失败和daemon快照、有界非媒体源码/class/全流、判据/计划/矩阵。大Gradle缓存/新local mirror未作为运行结果封存；镜像与依赖约束继承原冻结身份，实际新Android消费未发生。

原Android01全部740、Container02全部676、审计fork2738封存行逐hash不变；qualification03原manifest证据逐hash不变。未修改产品、旧媒体/encoder/fork/JAR或旧session，不自行设备/生成/嵌入产品。集中交负责人完整阻塞结果，候选冻结待统一新批安排。
'''
main=R/'docs/coder/D1_MEDIA3_ANDROID02_CONTAINER_DELIVERY_V1.0.md';main.write_text(report,encoding='utf-8');dump(E/'delivery-report-identity.json',pin(main))
dump(E/'pre-freeze-summary.json',{'status':'BLOCKED_ANDROID_BUILD_DAEMON_CONNECT','mainReport':pin(main),'sourceDifferences':len(changes),'nonmediaGroups':20,'inheritedSubcases':8,'AndroidApks':0,'AndroidMethodsRun':0,'newGradleCalls':1,'oldSessionActions':0})
print(json.dumps({'report':pin(main),'changes':len(changes),'status':'BLOCKED_ANDROID_BUILD_DAEMON_CONNECT','qualificationEvidenceFiles':len(m['evidenceFiles'])},ensure_ascii=False))
