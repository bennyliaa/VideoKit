from pathlib import Path
import json,hashlib,shutil,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'media3-android01-freeze.json').exists()
review=R/'docs/tester/D1_MEDIA3_ANDROID01_REVIEW_EVIDENCE/coder-documented-entry-prefreeze-001';summary=json.loads((review/'summary.json').read_text());assert len(summary['runs'])==62 and summary['allOriginalProcessesReturned'] and all(x['exitCode']==0 for x in summary['runs'])
dest=E/'documented-entry-prefreeze';assert not dest.exists();shutil.copytree(review,dest,ignore=shutil.ignore_patterns('classes'))
runs=[]
for row in summary['runs']:
 p=dest/(row['name']+'.json');receipt=json.loads(p.read_text());assert receipt['exitCode']==0 and receipt['originalProcessReturned']
 if row['mode']=='production':assert receipt['productionJarFirst'] and receipt['jarSha256']==sha(B/'artifacts/media3-android01-classes.jar')
 runs.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'mode':row['mode']})
dump(E/'batch-validation.json',{'candidate':'D1_MEDIA3_ANDROID01_READY','finalBuild':'004','finalLocal':'002','runs':runs,'hostReadinessGroups':6,'sourceAndProductionJarPass':True,'actualAndroid':'NOT_RUN','platformProbe':'EXPECTED_NOT_RUN_NOT_FUNCTIONAL_PASS','extraEarlierSuite':'See earlier-suite-pending.json:29 completed receipts, remaining original JDK child NOT_RETURNED; not counted among62 positive receipts'})
pending=E/'earlier-suite-snapshot';pending.mkdir();completed=[]
for p in sorted((E/'suites-001').iterdir()):
 if p.is_file() and p.suffix in ['.json','.stdout','.stderr']:
  shutil.copyfile(p,pending/p.name)
  if p.suffix=='.json':completed.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'exitCode':json.loads(p.read_text())['exitCode']})
assert len(completed)==29 and all(x['exitCode']==0 for x in completed)
dump(E/'earlier-suite-pending.json',{'status':'UNKNOWN_ORIGINAL_JDK_TEST_PROCESS_NOT_RETURNED','observedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'toolSession':48945,'parentPythonPidAtObservation':35988,'originalJavaPidAtObservation':39256,'originalJavaClass':'com.videokit.d1input.ContainerPendingOrderCheck','completedReceipts':completed,'remainingCases':['inspection-orders','android-ready-host'],'nativeDeviceOperation':False,'productAndroidCase':False,'sameCasePassedElsewhere':'Full documented-entry source and production modes returned exit0; this does not replace the earlier original process return','threadDumpAttempt':{'toolSession':17257,'status':'ORIGINAL_JCMD_NOT_RETURNED','pidArgument':39256,'readOnly':True,'defaultSandboxAttempt':'Access denied; escalated attach still pending; no thread-stack conclusion'},'processKilledInterruptedOrForceClosed':False,'processReturnProven':False,'scopeDisposition':'Retain original tool sessions/processes; no retry/return/refund/success claim for this earlier run. Pending run directory excluded from immutable snapshot because its original caller may still write later. Snapshot of29 completed receipts separately sealed. Local pending owner is an explicit handoff limitation, not device idle proof.'})
prior=[]
for folder,name in [('D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE','review-evidence-manifest.json'),('D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE','review-evidence-manifest.json'),('D1_INPUT_SINK05_REVIEW_EVIDENCE','review-evidence-manifest.json'),('D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json'),('D1_MEDIA3_ANDROID01_READY_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json')]:
 p=R/'docs/tester'/folder/name;m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles']);prior.append({'manifestPath':p.relative_to(R).as_posix(),'manifestSha256':sha(p),'reportSha256':m['reportSha256'],'unchangedEvidenceFiles':len(m['evidenceFiles'])})
dump(E/'prior-independent-evidence-preservation.json',prior)
audit=json.loads((E/'artifact-audit.json').read_text());deps=json.loads((E/'actual-consumption/configuration-closure-summary.json').read_text());table='\n'.join('|'+x['path']+'|'+str(x['bytes'])+'|'+x['sha256']+'|' for x in audit['apks']+audit['jarArtifacts'])
report=f'''# D1_MEDIA3_ANDROID01_READY 完整交付报告 V1.0

2026-10-21。本批完成实际Android instrumentation候选开发、双APK strict离线构建、来源/签名/清单/依赖审计、主机自检与冻结准备。提交负责人及tester阶段B独立离线审查；当前没有任何Android实机结果。六样本fixture仍FIXTURE_BLOCKED，生成方案为待审提案。另有一次较早重复JDK自测原进程未返回，明确UNKNOWN并保留，不能把本批称为全部本地owner已回收或可执行放行。D1未过、M0未启。

## 1. 实际交付与来源

目录D:/CodexProjects/VideoKit/docs/coder/d1media3-android01。以冻结CONTAINER02为实现来源，继承其独立报告e857e11a919475562587ff300223472076e8c190388f838e61a8417fecd46649的PASS_LIMITED_FIX_WITH_FUNCTIONAL_SCOPE_OPEN；MC-B01只在检查前准入/原返回范围关闭，旧FAIL不改。阶段A报告36c5d4fecfe13b955a96e9194a4f59024df115d85ab3a6292db1794ab205a4cf及24项oracle/证据契约/fixture/生成检查单原文均纳入reference，最终映射evidence/completion-matrix.json，全部真实Android仍NOT_RUN，不能把准备登记为tester新实现PASS。

新增独立app com.videokit.d1media3.android01、test com.videokit.d1media3.android01.test，进程com.videokit.d1media3.android01:media3，versionCode1/versionName D1-MEDIA3-ANDROID01-READY，min31/target36/compile36.1。built-in android.app.Instrumentation入口，无新AndroidX test runner依赖。新包无权限/业务组件/native库，不安装升级、不查旧com.videokit.app或其他项目，空数据同UID沙箱不冒RCE隔离或生产J11/P0。

## 2. 实现与差异

instrumentation/下Media3Instrumentation、ExperimentJob、OwnedFiles接真实HostProvider/readAt→实际HostDataSource/DefaultExtractorInput→Mp4Extractor/FragmentedMp4Extractor→有界track/sample/CSD/PTS/hash观察。src/新增ExperimentContract精确参数/空fixture门与VerifiedFixtureCopy定长/hash/实际EOF流式复制；没有加JVM平台替身。复制继承生产源码仅改3文件：HostInputFactory只读同原source identity；HostMp4Inspection增加有界实际range/seek/replay/EOF/release记录及真实TrackOutput duration callback；TemporaryOutput新增显式实际host UID/PID重载，旧构造语义不变。upstream包括原E13FinishOwner不变，MC-B01检查准入helper保留。evidence/source-differences.json和三个patch提供逐字差异。

唯一批准349102B样本hash720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9固定在test APK asset；每次限定到新包私有目录，实际EOF/hash确认、原同步/close返回后设只读，再解析。输出不覆盖原媒体。测试只接受case/fixtureSha256/runId三个字符串键，不接受路径、URI、encoder选择或运行时fixture注册。

inspectKnown/inspectShort3/inspectUnknown普通cap=true、MP4、seek=-1、capture=false；inspectSeek1s只以实际SeekMap准入和真实point byte/time/new epoch重放。已知/短读/未知的归一化track/CSD/样本指纹用于实际receipt比较，不预填轨道id/数量/PTS/hash golden。preopenAdmission覆盖false capability/null container/-2/2000001在factory/adaptor/source open前拒绝。muxQualified当前registry=null，在文件/输出/mux创建前FIXTURE_BLOCKED、write0；正路径实现仍待新fixture资格化，不能跳门称mux通过。

输入累计8MiB、输出attempt16MiB、块64KiB、全局两源、单源inflight1/queue0；复制/hash/sniff/parse/seek/读回/EOF探测都计输入，不退款。E4Owned先登记再分配原FD；源/worker/observer/原native close与原caller join分别记录，counter0或Future.isDone不代原返回。期限60000ms只关准入、保留首错误/UNKNOWN/原强引用；不kill/interrupt/二close/退款/换owner。原E13FinishOwner是唯一platform finish gate，等待同原case worker+source/observer真实返回。receipt生成时finalizer仍在，最终platform finish原返回另由既有外层采集证明。

仅HOST_MEDIA3_MP4_STRUCTURE_V1结构观察，真实内容隔离验证未执行，不给HOST_ISOLATED_FORMAT_V1/validated/READY/COMMIT/播放结论。无解码/播放/Surface/AudioTrack/音量/MediaCodec/ordinary-isolated/GPU探针。原FFmpeg/发布/媒体许可、P0/J11/C13缺口均不关闭。

## 3. 准确产物身份

|产物|字节|SHA256|
|---|---:|---|
{table}

两APK实际签名证书SHA256 {audit['signerCertificateSha256']}，apksig验证原进程均exit0返回；二进制manifest分别确认无权限、无业务组件、无sharedUID，无native库。DEX未包含Uri/ErrnoException/OsConstants JVM替身或checks/JCodec。构建生成的280个android命名类集合与旧02 APK完全相同；记录这一继承事实，不虚称整个DEX没有android定义。test只含自身instrumentation+构建生成类，实际Media3由target app提供。主/测试JAR逐class与各自最终Android javac输出一致，JAR不是主机伪装Android执行。

最终build-main-004离线strict、metadata verification、strict locks，app+test63任务全部执行成功，真实编译Android SDK android.jar，只是编译不等于SDK现场/设备调用。debugCompile外部12、debugRuntime17、AndroidTestCompile12、AndroidTestRuntime0，两个真实javac classpath分别16/17文件，独立从实际解析/编译事件取得，不照搬app17。共300实际核验对象=123binary+37module+140POM，身份集合与02完全相同；新runtime/test坐标与版本/二进制下载0。settings锁和verification metadata与02逐字一致；app锁只为12个已有compile坐标增加准确AndroidTestCompile scope，空runtime等配置加空锁。来源许可继承有限准入，无商业清权扩大。

构建001曾因审计监听器过早解析self-project artifact触发歧义失败，保留日志及修复前脚本；换为incoming resolutionResult只读closure记录后002/003/004成功。local001是新增主机check的lambda变量编译问题，修复前文件及失败receipt保留；local002最终20组core成功。初始审计过宽拒绝所有android命名DEX定义，已改为核对旧02完全相同的280集合并准确排除三个JVM替身；没有为通过审计修改APK。

## 4. 自检三栏与未返回重复会话

实际Android：0次。真实FD/fsync/Extractor/Muxer/重放/原platform finish/1.2秒duration/内容隔离/播放均NOT_RUN。

主机有限：documented-entry-prefreeze完整62个顶层子进程exit0且实际返回；源码与production JAR优先classpath两轮均通过，新增6组host readiness、继承20组core、MC-B01原8界与22顺序等保留。platform-availability是准确缺平台NOT_RUN探测，不作真实容器PASS。local_check与review_all各8种错误输出根拒绝，正确新review根可真实编译/运行；不会写旧冻结或旧tester目录。evidence/batch-validation.json、documented-entry-prefreeze和两gate目录有原始argv/stdout/stderr/exit/原进程返回证据。

必须单列的未完成记录：较早evidence/suites-001在29个已返回exit0后，原Java PID39256/父Python35988停留ContainerPendingOrderCheck，tool session48945尚无最终返回；原read-only jcmd39256 Thread.print尝试session17257也未返回，默认沙箱另一次attach access-denied，未取得线程栈，不能推断根因或已归还。没有强停/二close/退款；这条早先调用不是后续62进程通过所能替代。其29已返回记录另冻earlier-suite-snapshot，状态UNKNOWN见earlier-suite-pending.json；活动原目录suites-001从不可变快照排除以免后续原写入破坏身份。此限制需负责人处理，不能据此声明host全空闲或放行设备。不把它隐为全绿、也不把未知原因凭空诊断成生产容器故障。

未来NOT_RUN：六个精确case/参数/runner/runId/进程、60000ms/receipt262144B、14操作全预算/错误停点已冻结在execution-plan.json与METHODS_AND_BUDGET文档。任何UNKNOWN/首错/外层预算不足停止余下用例，无重试或强停；正归还前不得自动卸载。device/build/tool/fresh idle/scope绑定均空NOT_AUTHORIZED，旧停止scope/once/余额不复用。

## 5. fixture 与完整生成提案

8视频manifest只有320x180+音频约8秒，不读其他7载荷，不合格。test asset仅BBB派生approved sample，署名CC BY3.0/00:30–00:38节选与转码修改记录保全。六帧registry=null，实际mux写入0，MA16–MA20为FIXTURE_BLOCKED正例NOT_RUN。

FIXTURE_PROPOSAL文档、GENERATION_API_SEQUENCE_PROPOSAL.txt及generation-proposal.json交准确JCodec0.2.5官方source archive+POM+FreeBSD LICENSE、原始source SHA、编译器精确hash/API参数/原创YUV公式/新CREATE_NEW路径/所有预算/原线程退出清理。source archive1246282B、807ZIP条目、可执行条目0，未加到Gradle/classpath、未编译加载编码。JCodec源码只供静态方案核查；不是新增运行工具批准。重要未完成门：未来可执行工具build hash=UNBUILT，source hash不能冒build hash；先另签固定tool build并冻结driver/source list/compiled JAR精确hash独立审，再另签生成。此字段阻塞生成准入，当前不造编码二进制或假NAL/hash。

原创六帧256x144 YUV420J、5fps、PTS0/200000/400000/600000/800000/1000000、EOS1200000、单无音频无加密rotation0。真实H264Encoder keyInterval1/motionSearch0/DumbRateControl初QP20，不能标constantQP；MP4Muxer timescale5整数，无重复AnnexB转AVCC。未来实际SPS/PPS/CSD、每帧size/flags/key/hash/表示、actualduration与文件bytes/hash必须生成后独立实际Media3资格化再嵌入另一个新候选，当前无golden。工具/专利/发布/旧FFmpeg缺口不冒清权。

## 6. 冻结、重放与交接

seal为evidence/media3-android01-freeze.json；源码ZIP为D:/CodexProjects/VideoKit/docs/coder/D1-20261021-MEDIA3-ANDROID01-READY-source.zip。seal列精确源码/产物/报告/原始证据/生成source提案身份；ZIP不含镜像、缓存、SDK/JDK、build/classes、密钥或原媒体目录。唯一.mp4是本批明确批准349102B的instrumentation-assets只读构建输入，test APK含同字节，来源许可完整；不是扩大媒体范围。

只读入口：固定Python执行tools/review_all.py --output D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_ANDROID01_REVIEW_EVIDENCE/NEW_UNIQUE_CHILD。只写全新独立tester子目录，源码编译和production JAR两轮62receipt，先核seal，不构建/修改冻结candidate、不执行Android、不替代独立审查。不能复用已存在输出路径。详尽主机argv以冻结receipt为准。

旧10候选6232文件逐hash不变，02/01/05独立审查及两阶段A原manifest全部逐项保存复核。旧FAIL、UNKNOWN与历史许可/once账不改。交负责人整批审与tester阶段B，除上述本地重复JDK原owner UNKNOWN与fixture/toolbuild/真实Android未执行外不隐去限制；本报告不是新实机令或正式产品交付通过。
'''
main=R/'docs/coder/D1_MEDIA3_ANDROID01_READY_DELIVERY_V1.0.md';main.write_text(report,encoding='utf-8')
dump(E/'delivery-report-identity.json',{'path':main.relative_to(R).as_posix(),'bytes':main.stat().st_size,'sha256':sha(main)})
print('HANDOFF_PREPARED_62_POSITIVE_RECEIPTS_PLUS_EXPLICIT_EARLIER_LOCAL_UNKNOWN')
