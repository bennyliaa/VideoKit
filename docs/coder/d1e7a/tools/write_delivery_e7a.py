"""Generate the four explicitly requested documents and non-executing device/control plan."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(n):return json.loads((B/'evidence'/n).read_text(encoding='utf-8'))
def write(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
def main():
 if (B/'evidence/e7a-freeze.json').exists():raise RuntimeError('FROZEN')
 checks=load('local-check-results.json');audit=load('apk-audit.json');delta=load('source-derivation.json')
 apks='\n'.join(f"- {a['role']}：{a['bytes']} B，SHA256 `{a['sha256']}`，`{a['path']}`。" for a in audit['apks'])
 changes='\n'.join('- `'+x+'`' for x in delta['changedOrNew'])
 handle='9f19bfb5-60e0-4bcc-9666-852409cfe3b4'
 delivery=f'''# D1 E7A 交付 V1.0

2026-10-17，D1-20261017-E7A / versionCode10 / D1-E7A。修复E7-F01/P1的实际诊断任务与instrumentation结束边界；本地有限证据支持新边界，Android进程生命周期及控制权限尚未实测，须独立静态复审后再正式派发。旧E7全195项保持冻结，未部署E7或E7A。

旧入口的问题成立：await10s后assert/throw可让JUnit结束，runner.finish实际会退出目标进程，static Job不能保住在途/UNKNOWN owner。新E7AReadOnlyInstrumentation直接继承Instrumentation，不用JUnit；onStart异步返回后没有自动finish，实际E7ADiagnosticRun拥有原E4Owned和全部原操作。旧JUnit入口在创建任何Job前明确禁用。正常/故障类不运行，本批不是普通JUnit单方法执行。

10秒仍为原诊断资格截止，单调时钟从run创建起计。截止仍在途、分配/close未知、中断/异常控制状态等永久PENDING，不因迟到返回改PASS。原任务只运行一次，open前已登记原holder，read失败仍由原holder尝试一次原close；UNKNOWN不重开、不重试close。history/proc未返时即使FD已close，也不能结束。外部用预存handle经权限保护的控制接口读状态、停止依赖或归档确认；实际作业的finish需精确handle/sequence归档ACK且全部原操作真实返回、holderEMPTY未分配或CLOSED实际归还。启动前可证明任何原操作尚未发起的拒绝，允许在同一门下直接失败结束，无作业假close。

本地最终{checks['actualJobFinishCases']}场景/{checks['assertions']}断言PASS，直接运行实际Job/run/deadline/finish-ACK和原E4Owned，并经过同一E7WriterDeathGate；只替换clock和平台操作、平台finish计数。覆盖快成功/收尾失败/七处在途/迟到/close UNKNOWN/Exception或Error分配窗口/InterruptedException/实际线程中断标记/错或过期ACK/提前结束/异常finish/重复任务。初次27/327后补真实线程中断标记用例，最终28/338；两次日志及旧测试源精确SHA保留，不累计成55项。旧死亡门27/316为继承未重跑。

main-001一次离线双APK构建成功（38秒，无修复/下载），最终输入SHA `{hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()}` 与build记录绑定。app/test DEX及test manifest确认新实际边界/custom runner，非AndroidJUnitRunner。125个生产/native/upstream文件逐字节继承E7，max8只读死亡门、guard/fence/账本/每host原观察/实际close/六帧EOF/1000us等均未动。七native相同，35Maven锁坐标无delta，原FFmpeg8.0.3/Media3 1.9.3/全部许可P0保持。zipalign-P16静态PASS，不作设备16KiB实测。

{apks}

双APK证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。没有新增app权限或service；控制广播接收器仅诊断存活期间动态注册，要求发送者持有现有signature/privileged DUMP权限，普通app不能发送。Android shell是否具备并能正确调用该入口需设备复审验证，尚无实测保证。

精确构建输入变化：

{changes}

四文档、全源码/diff/输入/日志/SBOM/原native完整对应源及来源入完整ZIP。最终seal=evidence/e7a-freeze.json、完整ZIP=artifacts/D1-20261017-E7A，身份由包外 docs/coder/D1_E7A_READONLY_VERIFICATION_V1.0.json 给出，无自指；ZIP无私钥/local.properties/classes/cache/真实媒体。tools/e7a_package.py verify只读，冻结后不重跑检查或构建。

E6B-OBS-F01长期准入继续OPEN，旧writer缺boot/start代次与可信防回滚依据，持久事实协议仍DESIGN_BLOCKED，无格式/读写/迁移/fallback/no grant。原平板MP4限定PASS保留；AVI/能力/cancel不准入。最后tester预算累计107218/reserved0及全部旧输出/N2归档保持，非本批实时重测。无ADB/设备/真实媒体源或导出件/下载/新恢复写，E3已耗许可不复用。D1未过/M0未启，历史signal门及既定P0不变。
'''
 architecture='''# D1 E7A 架构与威胁边界 V1.0

2026-10-17。E7-F01修复范围为实际任务/runner结束路径；Android实测仍NOT_RUN，不等于持续准入已解决。

Android Instrumentation官方接口支持异步实现；onStart返回本身不等于finish，finish会结束被测进程。[Instrumentation官方文档](https://developer.android.com/reference/android/app/Instrumentation)。AOSP的非等待am instrument路径在不使用-w/proto时不建立watcher或UiAutomationConnection，启动命令返回与被测instrumentation结束分离；本计划据此设计，不把AOSP源码当本平板实测。[AOSP Instrument.java](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/cmds/am/src/com/android/commands/am/Instrument.java)。

实际路径：E7AReadOnlyInstrumentation.onCreate校验专用参数并建立original E7ADiagnosticRun；onStart检查原App/UID/空闲产品host，注册控制receiver和一次10s事件，beginLaunch先保留启动窗口，再启动原Job线程。onStart随即返回，不运行JUnit。原Job严格串行 preflight→open→read/fstat→原close→afterClose lstat→原生产history/proc，资源使用原E4Owned。所有正常操作/Exception/Error被原Job收集；实际资源close只由原Job执行一次，控制线程不close、不interrupt、不cancel、不重开。open抛异常会留UNKNOWN，Error窗口可能ALLOCATING，均不补造未获得的FD。读失败保原首错，随后原close真实返回才可能证明归还。

E7ADiagnosticRun既是实际Job也是唯一finish决策边界，非旁置模型。snapshot.originalOperationsReturned表示平台操作链已逐一真实返回并进入终结记账，不声称Java线程已死亡；末尾仅有内存结果发布。safeToFinish还要求原holder EMPTY（从未分配）或CLOSED（原close真实返回）。即使FD已归还，history/proc阻塞时操作链未返仍拒绝finish。ALLOCATING/OPEN/CLOSING/UNKNOWN或任何平台操作未返都拒绝。初始化在launch前明确拒绝、没有发起任何原操作时可失败结束；launch尝试窗口不明则不能套用这个例外。

单调10秒从run创建时刻起计，不从超时再加时间。定时事件只记录资格失败，不中断任务；完成路径也核实际当前时间，防主线程定时消息迟到导致假PASS。截止时未返/到界才返均PENDING；PENDING不可变，真实迟到close和API返回只能令safeToFinish从false变true，不能改为QUALIFIED_DIAGNOSTIC。中断标记、InterruptedException、控制异常、过早finish请求等也永久PENDING。QUALIFIED_DIAGNOSTIC只表示限内完成诊断收集，BLOCKED_CURRENT_GATE依然可能是内容结果，不是死亡门/观察/产品准入。

结束协议：实际作业需要外部先归档一个包含精确handle和sequence、原操作链已返且holder可证归还的snapshot，再以同一handle/sequence发送ACK_FINISH。核心在锁内核身份、版本、实际返回、只允许一次finish；过期/错handle/重复ACK无效，未知资源不能越过。实际Android平台finish只存在于一个私有出口，由这个核心callback调用，并排在控制广播回复后。先实际unregisterReceiver返回，再super.finish；若移除receiver/队列/finish抛异常，不把它当正常结束，保留PENDING/不伪ACK。完成时重新取当前PENDING等结果，避免排队后外部STOP被旧PASS覆盖。普通finish覆盖方法、onException均不转发到平台finish，只记PENDING；意外onDestroy标为控制生命周期不明。已安全申请结束时的正常销毁不再冒充未返资源。

控制与权限：动态receiver action=com.videokit.app.E7A_DIAGNOSTIC_CONTROL，注册要求发送方有android.permission.DUMP；本app不申请新权限，不增加service或前台服务。仅接受精确handle，以及STATUS、STOP_DEPENDENCIES、ACK_FINISH三种固定命令。STATUS只是内存快照和截止检查，不重查owner/历史/proc；STOP只永久停依赖，不取消原作业；ACK仍受上述资源门。发送端需user0 shell/system有现成DUMP资格，外部须先验证实际可达性。公开广播resultCode1仅表示处理了命令，必须读snapshot的safeToFinish/finishClaimed等，不能当实际close或退出ACK。handle是单次派发识别码，不是超越DUMP的安全凭证；receiver普通app不可用，但不能抵抗有DUMP/root的外部杀进程。

PENDING处置是事件驱动隔离，不是延长10秒或在Job/runner里无限join/await/轮询。唯一原操作继续自己运行；原instrumentation受管实例保持未finish并拥有Job。外部仅有限读取状态（计划最多6个控制请求），将handle/原PID/UID/组件/状态及原始日志归档，停止全部依赖并交负责人。原操作迟到真正返回且可证归还后，可归档新sequence并ACK，以PENDING/非通过结束。close UNKNOWN/分配UNKNOWN不会自动恢复，也没有再次close/retry接口；无法证时没有有限安全结束保证，协议明确不承诺固定时刻退出。外部完成隔离登记后可返回协调界面，原受管任务仍在；这是有标识、有停止依赖动作的隔离状态，不是静默延时求PASS。

外部STOP_DEPENDENCIES不是停止进程。禁止force-stop/新instrumentation/升级/清数据/断电充当归还。若系统崩溃、用户强停、进程/设备意外死亡、控制receiver不可达或连接丢失，外部归档状态为LOST_OWNER_UNKNOWN，不能从进程不存在推出原close ACK。不能把新host当同handle恢复器，不能重放旧snapshot放行；原Java holder/FD无法跨死亡恢复。没有app持久作业文件或跨进程托管；恢复须负责人另审原始外部收据、真实死亡/资源证据与安全处置计划，不自动重启诊断/normal/恢复写。外部记录属于tester证据，不是持久死亡事实/产品准入入口。任何Android进程都可能被系统终止，因此本批只阻止自己过早finish，不能声称设备绝不杀进程。

只读边界继续固定原recovery.owner、目录/文件UID角色、NOFOLLOW/NONBLOCK、257B哨兵、精确原字节/dev/inode/mtime/ctime和原holder close。生产max8一次/history匹配与reason/proc门全字节继承E7，无新observe、guard/fence/ledger/业务持久写、CPU/codec/媒体、grant。读取可能更新系统访问时间，不声称物理零写。持久死亡协议仍缺可信旧writer启动代次及完整性/防回滚根；本批不实现任何该格式、解析器、写入、迁移或fallback。

有限证据：最终28场景338断言，实际E7ADiagnosticRun.run/deadline/acknowledgeFinish、原E4Owned与生产gate；clock替为可控单调值，平台open/read/close/history/proc以有限latch控制，finish替为计数callback。七处原操作在途均证明结束计数0，迟到释放后仍PENDING才可ACK；UNKNOWN不能ACK；中断异常不替代close。并测错/过期/重复ACK、launch窗口、close异常、实际线程中断标记、平台finish异常和重复Job。不是Android广播权限/handler/进程保活/OS finish杀进程/真实FD/退出history API实测，不能以本地测试宣称这些已获设备保证。首轮27/327及追加实际线程中断后的28/338日志与精确源保留，只采最终数。
'''
 review='''# D1 E7A 剩余门槛复审 V1.0

2026-10-17。请求tester先完整独立静态复审，不直接设备部署。本批不提供一次性执行许可。

|项目|当前状态|
|---|---|
|E7-F01/P1|本地实际Job/finish边界28/338支持；Android异步runner/控制权限与真实操作返回尚未实测，交独立复审，不自行登记设备关闭|
|E6B-OBS-F01/P1持续准入|OPEN，旧writer启动代次与可信持久根缺失，持久方案设计阻塞|
|原E6B_NORMAL MP4|原平板限定真实6/6/6/6 READY/PTS0/双EOF/画面/全部资源/S53567 PASS保留|
|AVI/能力/cancel|不准入，不能因只读诊断QUALIFIED解锁|
|原预算与产物|最后tester107218/reserved0及全部旧输出/N2归档保留，非本轮重测|
|构建/来源|一次38秒离线双APK、原证书/version10，125生产文件不变、七native/35依赖无delta、旧E7全195只读核验|
|D1/M0/signal/许可及其余P0|D1未过/M0未启，原门与未决P0保持|

复审应从新test manifest的custom Instrumentation到onStart、原Job、唯一super.finish出口逐段核对，而非只数纯gate用例。确认旧JUnit入口禁用；onStart返回不触发AndroidJUnitRunner；预留启动窗口后才启动；核心返回标记包含全部真实平台调用，关闭未知/分配未知不能被失败报告绕过；10s PENDING不可变；ACK严格handle/sequence/资源返回且只调用一次；初始化例外确实没有发起作业；最后receiver实际unregister异常也不以正常退出掩盖。

核权限：不新增app uses-permission/service，动态receiver要求发送方现有DUMP，STATUS/STOP不取消、不重查、不写业务状态；外部协议仅非等待am instrument（无-w/proto/UiAutomation），避免启动命令结束牵连目标。核有实际可识别handle和有限状态查询、外部隔离记录、迟到/UNKNOWN/进程死亡不可恢复资源的真实限制，不接受静态引用、线程非daemon或无穷等待本身当证据。

本地平台替身只支持实际核心决策；Android进程生命周期、DUMP shell权限/广播递达/无watcher启动、原FD与系统调用仍需新正式设备派发实证。若静态协议仍有缺口，继续阻断设备；不得为通过而延长资格时间、结束未知原任务、丢UNKNOWN或取消原future。

完整材料：source-derivation逐输入精确diff、local-check-results最终28/338原日志、001追加测试来源、integration-static-check生产目录字节比较、输入SHA绑定main-001、signer/aapt/testmanifest/DEX/zipalign、SBOM/native对应源、四文档和device_plan、ZIP/freeze/包外只读receipt。旧E7不再构建或部署，旧27项死亡gate仅继承。持久损坏/重复/过期/在途均无准入消费入口，未虚构解析器或Android重启/PID复用测试。
'''
 appendix=f'''# D1 E7A 设备执行附录 V1.0

2026-10-17。以下仅待复审计划，需负责人新正式派发；coder本批设备/ADB/媒体读取0。禁止部署旧E7，禁止normalAVI/能力/cancel/恢复写。不得将本附录视为许可。

仅HA1Q6WXR/user0，原app UID10221/test10222。独立核外seal、ZIP、versionCode10/D1-E7A双APK hash/原证书，同签名保留数据install-r，仅在正式派发后执行；不卸载/clear/降级/force-stop/换预算/改旧档。必须先确认没有未归档在途旧instrumentation，不通过新启动杀掉旧任务。原稳定budget=730a73e1-50e1-4198-a515-047104f00e31，最后107218/reserved0，全部输出和原恢复batch保持，非当前新测值。

唯一component：com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation。不是JUnit class#method，不调用旧E7WriterDeathDiagnosticTests/E4DeviceTests。专用参数e7aCase=originalRecoveryWriterReadOnly，e7aBatch=D1-E7A-WRITER-DIAG-TABLET-20261017，e7aScope=READ_ONLY_MANAGED_NO_ADMISSION，e7aHandle={handle}。该handle只对应本计划的一次派发，外部启动前保存其serial/user/组件/双APK身份/原PID_UID核对与证据路径；不复用已耗E3许可或旧作业handle。

启动用am instrument非等待模式，不带-w/-m/-f/proto/类选择/UiAutomation/性能profile，不把命令exit0当作业完成。无watcher时sendStatus可能无接收方，实际状态通过带DUMP发送资格的shell有序广播及E7A_READ_ONLY日志取得。固定action=com.videokit.app.E7A_DIAGNOSTIC_CONTROL、-p com.videokit.app、user0、handle精确；command只允许STATUS/STOP_DEPENDENCIES/ACK_FINISH。广播可用--receiver-foreground确保控制事件及时调度，不引入前台service。是否实际可达必须在新设备批次核证，不能借AOSP说明冒充实测。

外部有限控制计划：总请求最多6次，单次响应预算5秒、日志总1MiB，最多在启动后约1s和>=10s各取一次STATUS。10秒为设备单调诊断资格截止，不受主机钟误差或后续状态读取延长。若已RETURNED且originalOperationsReturned=true、safeToFinish=true、holder=EMPTY或CLOSED，先完整归档该snapshot和准确sequence，再用同handle+archivedSequence发送一次ACK_FINISH。没有任一条件不得发完成ACK；错误/过期ACK不会被接受。广播resultCode1不是close ACK或finish证据，须审safeToFinish/finishClaimed及此前真实原资源证据。

若截止仍在途或UNKNOWN，记录PENDING，有限发送一次STOP_DEPENDENCIES并取其结果；不结束、不取消、不重启instrumentation，不开启依赖。外部归档handle/PID/UID/组件/seq/phase/holder/截止/PENDING原始日志后交负责人，原受管instrumentation保持未finish。不能用主机命令超时/关闭窗口/退出进程当原close，不能无限轮询等PASS。若后续自然有新真实返回事件，负责人可另派同handle只读STATUS；安全归还已证才可归档新seq后ACK，以PENDING/非通过结束。close/allocate UNKNOWN没有自动修复或二次close接口，不承诺有限时刻能安全退出；外部须明确登记隔离处置，无法取证时不擅自杀进程。

如意外OS进程死亡/设备重启/外部force-stop/receiver不可达/通信丢失，记LOST_OWNER_UNKNOWN，不把内核回收当Java原close ACK；禁止新host恢复同handle、重放旧成功或重新读owner自动放行。由负责人审已有外部收据、真实死亡与资源证据后另行设计安全处置。外部“停止依赖”与“终止原进程”严格分开，后者不是本计划允许动作。

读取仅固定原recovery.owner元数据（最多257B哨兵）、system history一次max8及/proc；目录/文件UID角色/noFollow/dev+inode/精确原字节/前后属性及原close保持，无observe/force/sync/guard/ledger业务写、无source/export媒体/CPU/codec/grant。资格限内QUALIFIED_DIAGNOSTIC也仅表示收集完成，BLOCKED_CURRENT_GATE仍可出现；10s后PENDING永不改PASS。新结果归档后仍不串接normal/能力/cancel，长期持久准入仍需独立协议保证。

冻结包只读核验tools/e7a_package.py verify；本地run_lifecycle_checks.py默认INSPECT，冻结拒写；build_local.ps1默认INSPECT，冻结拒构建。独立复现解ZIP至新目录、自备既有缓存/SDK/JDK/签名环境并离线；不改变冻结包，不下载依赖或把本地替身结果当Android实测。
'''
 for name,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',review),('DEVICE_EXECUTION_APPENDIX',appendix)]:write(R/('docs/coder/D1_E7A_'+name+'_V1.0.md'),text)
 plan=dict(schema=1,candidateId='D1-20261017-E7A',state='REVIEW_ONLY_NOT_PERMISSION',serial='HA1Q6WXR',user=0,appUid=10221,testUid=10222,versionCode=10,versionName='D1-E7A',apks=audit['apks'],component='com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation',launchMode='AM_INSTRUMENT_WITHOUT_WAIT_OR_PROTO_OR_UIAUTOMATION',arguments=dict(e7aCase='originalRecoveryWriterReadOnly',e7aBatch='D1-E7A-WRITER-DIAG-TABLET-20261017',e7aScope='READ_ONLY_MANAGED_NO_ADMISSION',e7aHandle=handle),control=dict(action='com.videokit.app.E7A_DIAGNOSTIC_CONTROL',package='com.videokit.app',senderPermission='android.permission.DUMP',commands=['STATUS','STOP_DEPENDENCIES','ACK_FINISH'],maxRequests=6,responseBudgetSeconds=5,ackRequires=['sameHandle','exactArchivedSequence','actualOperationsReturned','holderEMPTY_or_CLOSED'],stopMeans='STOP_DEPENDENCIES_NOT_CANCEL_OR_PROCESS_STOP'),qualificationNs=10000000000,deadlineOutcome='PERMANENT_PENDING_NO_LATE_PROMOTION',unknownOutcome='MANAGED_QUARANTINE_RETAIN_NO_FINISH_NO_BLIND_POLL',processLoss='LOST_OWNER_UNKNOWN_NO_CLOSE_ACK_NO_AUTOMATIC_RESTART',ownerReadMaxBytes=257,historyCallsMax=1,historyLimit=8,logMaxBytes=1048576,afterDiagnostic='ARCHIVE_STOP_NO_NORMAL',lastTesterConsumption=107218,lastTesterReserved=0,newlyObservedBudget=False,deviceCalls=0,mediaReads=0,recoveryWrites=0,admission='NONE',persistentProtocol='DESIGN_BLOCKED',D1='NOT_PASSED',M0='NOT_STARTED')
 write(B/'tools/device_plan.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 write(B/'evidence/delivery-consistency.json',json.dumps(dict(schema=1,status='PASS',finalActualJobCases=checks['actualJobFinishCases'],finalAssertions=checks['assertions'],androidRuntime='NOT_RUN',productionFilesUnchanged=125,oldE7ImmutableVerified=195,documents=4,planMode=plan['state'],E7_F01='LOCAL_CORE_SUPPORTED_ANDROID_NOT_RUN',E6B_OBS_F01='OPEN',persistentProtocol='DESIGN_BLOCKED',D1='NOT_PASSED',M0='NOT_STARTED',deviceCalls=0,mediaReads=0),indent=2)+'\n')
 print('Written E7A four docs and exact managed-control review plan; no device execution')
if __name__=='__main__':main()
