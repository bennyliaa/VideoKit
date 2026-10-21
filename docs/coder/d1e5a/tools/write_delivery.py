"""Produce complete E5A review documents only from final local artifacts; no execution authority."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];BASE='docs/coder/d1e5a/'
def load(n):return json.loads((B/'evidence'/n).read_text(encoding='utf-8'))
def link(p,t):return '['+t+']('+str(R/p).replace('\\','/')+')'
def main():
 if (B/'evidence/e5a-freeze.json').exists():raise ValueError('FROZEN')
 audit=load('apk-audit.json');checks=load('local-check-results.json');build=load('build-results.json');external=load('external-readonly-verification.json')
 assert all(x['status']=='PASS' for x in [audit,checks,build,external])
 rows='\n'.join('| '+a['role']+' | '+str(a['bytes'])+' | `'+a['sha256']+'` | '+link(a['path'],'APK')+' |' for a in audit['apks'])
 cert=audit['apks'][0]['signerCertificateSha256'];snapshot=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()
 delivery=f"""# D1 E5A 完整交付 V1.0

2026-10-17。D1-20261017-E5A / docs/coder/d1e5a。仅本机关键路径与离线构建通过，等待独立复审。Android/设备/真实媒体/恢复QUERY/ABORT/最终观察均NOT_RUN；没有安装、下载或新fault。D1未通过、M0未启动、全部P0/JNI和旧signal/N2 FAIL保留。

## 批次与结果

按 {link('docs/milestones/D1_E5A_CODER_REQUIREMENTS_V1.0.md','E5A集中需求')} 修 {link('docs/tester/D1_E5_ARCHITECTURE_REVIEW_REPORT_V1.0.md','E5独立复审')} 的F01/P1、F02/P1。新候选封存；旧E5及旧候选/工具/报告/设备现场只读。提交的是完整两项修复、集中证据和可审下一阶段计划，不将本机通过外推Android。

F01：原稳定N2预算永久要求本进程真实操作的活准入证明，完成文件/归档存在不提供正向许可。新host默认拒绝，即使恢复标记条目都缺失仍不能凭原预算身份追加R。完全实际返回的原恢复可仅在本进程准入；跨host需另正式派发独立最终观察，核确切恢复writer身份与实际死亡，重核原ABORT/S/保留产物，执行本次独立force/读回/实际关闭及目录同步，全部返回后才发本进程证明。旧force/close未知和旧FAIL不回填成功；不递归增加最后自证文件。

F02：生产Session接入统一E5ALifecycle。失败初轮返回后同原owner至多一次排队接续，不先完成Future；真实source/codec/Image/mux/FD/callback/CONTROL/预算归还且最后owner回调返回，或首次取消30秒绝对截止，才允许仪器结束。截止仍未知报告PENDING而不扣在途、不清账；首错保留、失败不改READY。正向、negative、cancel、await超时/异常、资源close及JUnit @After共用终局门。向外Future视图被取消不影响内部终局。

## 集中本机证据

最终JVM repair-006：Core89＋E5主路径48＋旧close未知3＋旧早期durability未知2＋E5A128＝270项顶层/既有断言。E5A父检查含子进程退出/结果核验；子JVM内部断言另保日志，不再叠加求数量。八个晚期场景为正常全返以及completion force异常、close异常/未返、最终dir force异常/未返、dir close异常/未返。完成内容均确实完整可见；全新JVM直接生产reserve均拒绝且无新R；未返时原真实FileChannel仍open、原operation强引用。实际writer退出后另做独立新观察、当前文件force/close，才可当前进程reserve。OS退出不被计为旧closeACK或旧操作成功。

生命周期用真正单线程owner队列、原FileChannel关闭、原E4ReturnGate和生产E4OutputBudget结算，虚拟单调时钟只驱动60/30秒事件。覆盖初轮PENDING后原窗口内迟到返回、绝对截止仍UNKNOWN、原CONTROL迟到、计时任务调度迟到、取消外部Future视图、真实中断等待线程。初轮不会先结束仪器；原S唯一，原首错不变；截止后受控归还不升级原PENDING；延迟派发截止事件也不能准入迟到完成。Android Handler/Binder/目录fsync/native未执行。共享E5ADirectoryBarrier在本机以自有文件FD代替Android目录FD，仅证明所有权/异常/返回分支，不声称Windows证明Android持久化或掉电保证。

本机main/repair-001/002/003通过；repair-004因同host拒绝优先级变更而旧断言预期不符失败，原日志保留；repair-005仅修此预期后通过，cold-host严格拒绝检查保持；绝对截止调度迟到资格补强后repair-006通过。最终Gradle main-001成功，稳定预算准入补强后的repair-001再次离线成功，绝对截止资格补强后repair-002最终通过，采用最后一次源码与APK；原main输入/成功结果完整保留。未并发Gradle。

{link(BASE+'evidence/local-check-results.json','最终JVM结果与输入')}；{link(BASE+'evidence/build-results.json','最终离线构建')}；{link(BASE+'evidence/build-input-lineage.json','构建沿革')}；{link(BASE+'evidence/final-build-inputs.json','最终build输入')}，SHA256 `{snapshot}`。

## 精确双APK

| 角色 | 字节 | SHA-256 | 文件 |
|---|---:|---|---|
{rows}

两包证书SHA256 `{cert}`，与E5/E4A一致；com.videokit.app / test、versionCode3/D1-E5A、两个非导出服务和原权限保持，无INTERNET/companion。{link(BASE+'evidence/apk-audit.json','原签名/Manifest/七native审计')}。真实六帧、普通isolated EOF/PTS/缩略图复核、E5 flags/STARTED实际ACK/阶段诊断保持；同UID codec只是故障边界。

## 来源、依赖与封存

Media3 1.9.3 / FFmpeg 8.0.3，35个Maven坐标、七native字节与E5/E4A差异0，无新依赖。完整C14对应native源码容器、NOTICE和许可映射保留；非漏洞/许可/发布放行。{link(BASE+'evidence/sbom.json','SBOM')}、{link(BASE+'evidence/sbom-difference.json','差异')}、{link(BASE+'evidence/source-derivation.json','E5衍生关系')}、{link(BASE+'evidence/upstream-copy-map.json','C14映射')}。

{link(BASE+'artifacts/D1-20261017-E5A/D1-20261017-E5A-source.zip','完整源码ZIP')} 收入全部候选源码、工具、原日志和自有模型文件、四文档、基线证据与完整C14对应源码容器；排除local.properties、私钥、build/classes/Gradle缓存、真实媒体。双APK独立列为immutable。{link(BASE+'evidence/e5a-freeze.json','外部freeze')} 绑定ZIP/manifest/逐文件及双APK。ZIP大小/SHA与freeze自身SHA由集中交接外给，避免自身ZIP哈希循环。只读核验：Python -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1e5a/tools/e5_package.py verify。

旧E5 452、E4A207、T6 54、MPREP165共878个immutable只读验证，原seal一致。{link(BASE+'evidence/external-readonly-verification.json','旧冻结只读结果')}。原fixture/设备缓存/预算/失败产物未改。下一顺序仍为正式部署QUERY→独立审阅→另派原ABORT→独立结算审查→准确正常四方法；每个新host还必须执行明确派发的本次最终观察，静态报告或旧观察不自动授权。
"""
 architecture="""# D1 E5A 架构、线性化与威胁边界 V1.0

2026-10-17。修复E5-F01/F02，不改既定框架、真实编码/验证门和既有权限边界。独立Kit/未来Flutter控制边界保持，压缩解析在普通isolated CPU，RGBA不跨Dart；同APK :e4_codec 同UID仅是故障进程边界，不是权限/RCE沙箱。N2实际唯一根因仍UNKNOWN，原FAIL不改。

## F01：持久负向阻断与活正向证明

E5尾部窗口成立：完成文件完整字节已可见，不证明force/实际close/最后目录sync或目录FDclose已返回。E5进程内ACTIVE不保护新host。E5A的原N2固定预算730a73e1-50e1-4198-a515-047104f00e31在生产reserve中始终要求E5AAdmission活证明；恢复目录、归档marker或completion任何一个存在也触发该门。标记全缺也不解除这个固定账户的阻断。改UUID会与原anchor不符，计划亦禁止换账户/路径/清数据。

活证明仅可从本次E5N2Recovery或E5AFinalObservation原操作实例发布，绑定准确budget绝对路径，逐原holder/目录barrier/预算校验FD全部CLOSED、非poison/failed、ACTIVE已移除；不能由文件内容、字符串返回、receipt语法或caller布尔制造。它只存当前进程内存，不持久化成新最后自证文件。原操作的所有force/close/目录sync真正返回后，移除ACTIVE并发布证明，是当前进程准入线性化点。任何尾部异常/不返回无证明，原对象强引用；新的进程证明恒为空。

原恢复仍严格固定N2 task86cafdb3-0fc4-447d-920b-b19c884bf494、epoch5131975343750146374/gen1、service775a5ee9-fff3-4340-a03b-97751099c0c4、host24853/codec24873/UID10221、原batch/lease/R链。QUERY不锁/fence/hash输出。ABORT仍核两个真实唯一退出记录和/proc ENOENT、原owner/worker实际排他flock、完整前像/原ledger锁、fence/ABORT_PENDING→ABORTED/readback、保留输出实际SHA/字节、唯一S/fsync/readback/实际关闭，再归档marker和完成内容。完成文件只是后续观察的候选状态，不是许可。

归档内新增recovery.owner是fence之前写入并同步的实际writer身份：E5A_N2_RECOVERY_OWNER_V1、随机attempt UUID、真实PID/UID/主进程名、记录墙钟时间。它不声称操作完成。旧E5或任意部分状态缺该身份时拒绝，不倒填记录、不从任意PID参数构造证据。

## 明确的独立最终观察

这是另一次正式派发的操作，而不是重启自动继承许可，也不重做原ABORT/S。当前适配器要求原包/UID10221与主进程com.videokit.app、无活动Session/slot；从固定私有owner记录取得唯一原writer身份，要求本进程PID不同、ApplicationExitInfo最多8条中原PID/UID/name且timestamp在owner记录之后至当前各唯一有效匹配，/proc原PID为ENOENT。实际writer还活着、PID复用可见、记录歧义/不可用均拒绝。

随后取得原N2 owner/worker实际排他lease；核四份before images、原identity、ABORTED journal/新fence、原proof的两个原N2退出字段/原closeACK=false、唯一S及其链、当前稳定anchor、归档marker0B、完整completion。用生产E4OutputBudget.inspect核完整累计账链且无在途R；任何新的普通任务pending同样拒绝，不能借旧N2观察清别的任务账。

观察对现有14个有界文件执行本次force和实际close，包括原保留输出≤2MiB并重算SHA与唯一S一致；对archive/output/budget三个目录实际fsync/close，再独立读回整套metadata，最后实际关闭原排他lease/owner。文件内容、journal、R/S、marker、完成文件均不改写；没有第二份S，没有新增observer-complete文件。只有本次全部真正返回才发布当前进程活证明。若观察force/close/sync未知，本次强引用并BLOCKED；新进程仍默认拒绝，不能因旧文件可见洗成许可。

这里证明的是“原writer已经实际死亡，当前观察到的确定状态经本次独立同步和资源归还后可在本host使用”，不是补写旧force返回，不把旧BLOCKED/FAIL或原closeACK改成成功，不宣称绝对抗掉电。只依赖Android公开退出信息与文件系统fsync正常返回契约；这些证据实际是否可得仍待设备正式检验。

每次独立instrumentation结束活证明消失。下一次正常方法在同一新host、任何fixture读取之前，以明确e5aObservation派发参数和独立结算报告标识执行新的实际观察。独立观察报告本身不持久授权未来host。Android主进程/UID及受控FD拓扑是协议边界；不抵抗恶意同UID任意文件修改/RCE。

E5ADirectoryBarrier在打开原目录FD之前注册Slot；open返回的FD先写入Slot再做fstat/force，close只由原holder执行。UNKNOWN/CLOSING不重试。恢复最多32个holder/16目录barrier，观察最多48个holder，另保validationBudget所有原holder及至多16目录barrier；任何未归还metadata/预算/目录FD会继续保原排他guard。有限metadata读取，不递归扫描；observer两次固定metadata快照，ledger每份≤128KiB、owner≤256B、proof≤2048B、输出hash≤2MiB。

## F02：同一原任务的终局与时限

E5ALifecycle由生产E4Session直接使用。start时设原产品60秒看门；首次失败/取消只设一次cancelAt及cancelAt+30秒绝对截止，并在触及平台取消前安装截止事件。原协商12秒、STARTED15秒、实际六帧/isolated验证门保持。控制请求仍计原E4ReturnGate，callback/native/Image/FD不因计时器扣账。

失败初轮advanceCleanup返回后，不先完成Future，也不先unbind原service/标owner完成。同一单线程executor至多排一次continuation，并核仍为原Thread；原窗口内接续有限QUERY/实际close/abort。最后finisher执行真实unbind、原owner标志、CONTROL归还栅栏、唯一预算结算；该回调真正返回后且所有实际资源/预算都已归还才完成失败Future。正常成功也经同一实际终局门。finishEntries与originalOwnerReturned分开，不把进入finisher当已归还。

即使计时任务调度迟到，resourcesChanged也按原绝对时钟判断；到截止后才完成实际归还时，原计数可如实为0但终局资格仍失败，Report保持PENDING，所有device released断言必须另核ACTUAL_OWNERS_RETURNED及originalOwnerReturned。不能把迟到采样时raw resourcesReleased=true当按时通过。若原调用/close/CONTROL到首次30秒截止仍未返回，时钟仅完成一个明确PENDING/ORIGINAL_CANCEL_DEADLINE_PENDING报告，保原in-flight、对象、slot、R/marker；不假造归还、不调用通用reset。迟到实际归还可产生事实更新，但不能升级已封存的原PENDING/FAIL。原首错AtomicReference保持，Report失败永不因cleanup成功改READY。

Session.await超时转同一finishForInstrumentation；非UI AutoCloseable.close和JUnit @After也调用该门。positive/negative/cancel、await异常/中断均不能先终结仪器；等待被中断时继续同一门，最后恢复中断标志。外部start/Future投影被cancel/complete不会控制私有内部终局。UI close只请求取消，仪器入口明确非UI。

90秒仪器外壳只是卡住时取诊断，不延长产品60/12/15或首次取消30秒。截止时结束并报告UNKNOWN允许系统结束进程，但系统死亡不是原protocol closeACK，也不将本批原任务计通过。原native永不返回时仍可在明确截止报告PENDING，未还原资源均保留。

## 验证范围

直接执行生产recovery、Admission、OutputBudget、DirectoryBarrier与Lifecycle；自有文件/真实JVM进程、真实FileChannel及单owner/CONTROL线程。八个完成尾部场景和新host reserve均有独立日志；未返时实际FD open/ACTIVE=1；真实旧writer JVM退出之后另观察现有状态并实际force/close，旧结果保持。另以只复制原anchor/ledger、不带任何恢复标记的新host副本证明固定账户仍拒绝，不删除原现场。

生命周期用虚拟单调时钟推进边界，实际执行原close、CONTROL finally和账本S，证明初轮后同owner排队、截止前迟到、截止UNKNOWN、唯一finish/S与中断等待/外部Future取消。它不是Android Handler/Binder/进程结束或实际30秒墙钟实验。目录FD本机替身是实际自有FileChannel，不能据此声称Android目录fsync、codec或掉电已通过。
"""
 gates="""# D1 E5A 剩余门禁 V1.0

2026-10-17。本批是E5两项P1修复候选，待独立静态复审。旧E5 REQUEST_CHANGES及N2 FAIL不回写。

| 门禁 | 本批结论 | 剩余要求 |
|---|---|---|
| E5-F01完成可见跨host窗口 | 固定N2账户默认拒绝；完成/归档不授予许可；新JVM直接reserve反例通过 | 独立审明确活证明线性化/独立最终观察；设备尚未执行 |
| 独立最终观察 | 原writer实际身份/死亡、原ABORT/S、保留输出、当前force/close/dirsync全返才准入 | ApplicationExitInfo/proc/flock/目录fsync实际可得性待证 |
| E5-F02提前结束JUnit | 统一原owner终局或同首次30秒截止；真正线程/原FD/预算路径通过 | Android Handler/Binder/仪器结束时序后测 |
| flags/STARTED ACK/阶段诊断 | E5修复保留，原值有界可审 | 原N2实际唯一根因仍UNKNOWN |
| 六真实帧/普通isolated EOF/PTS/缩略图 | 生产门保持，未执行 | 原合法MP4→AVI真实运行 |
| capability/cancel | 生产选择与时限保持 | 正常两项先通过，取消原首次30秒/源0等真实证明 |
| 旧signal/JNI/P0/独立Kit正式门 | 未通过/旧FAIL保持 | 不由本批关闭 |
| 依赖/许可/发布 | 坐标/native差异0，原完整对应源保留 | 非漏洞、许可或发布放行 |

不能将complete字节、archive存在、进程重启、外部receipt语法、原0B输出或旧S存在视作新host准入；固定原账户即使标记丢失也拒绝无活证明的reserve。任意新目录/UUID/卸载清数据替代原账户不在授权计划中。

ABORT尾部失败报告仍BLOCKED。只有原writer确实死亡、owner身份完整且当前ABORT/唯一S/保留输出/全部候选状态可核时，负责人才能另派一次新的独立最终观察；本次观察证明当前状态，不回填旧未证sync。缺owner记录、缺complete、journal/链/长度/SHA不符、新pending、锁忙、退出证据不足或任何实际close未知均拒绝；不自动补文件、重复S、清marker或恢复半事务。旧E5部分状态不能倒填E5A owner身份。

正常四项每个新host都需显式本次观察，不能凭前一host观察报告直接放行。观察失败停在BLOCKED；首个正常MP4失败/PENDING立即保存原详细诊断、终局原因、原账本和产物，阻断余项并交负责人，不循环重跑或增加等待求PASS。后续普通任务的新pending不能由固定N2观察器恢复。

E5A本批ADB/设备/真实媒体stat-read-hash/部署/QUERY/ABORT/观察/新fault/下载均0。原fixture、失败产物、R/marker、设备缓存与旧冻结保留。D1 NOT_PASSED、M0 NOT_STARTED、全部P0和历史FAIL保持。
"""
 appendix="""# D1 E5A 设备执行附录 V1.0

2026-10-17。STATIC PLAN ONLY，无本批执行许可。完整冻结独立复审通过后，由负责人准确分段派发。不得测试浮动源码、先安装QUERY或做临时恢复。真实时限仍60秒产品/12秒协商/15秒STARTED/首次取消30秒；不得因新await或query重新计时。

## 顺序与原现场

正式同签名保数据部署versionCode3/D1-E5A→原N2 QUERY→独立审QUERY→另派原ABORT→独立结算/原结果审查→明确最终观察→正常MP4→正常AVI→能力拒绝→条件取消。每个独立正常方法的新host必须在本方法@Before重新实际观察，Standalone观察不能持久授权别的host。不得卸载/清数据/换UID或budget、清旧cache/marker/失败输出、重传fixture求替代产品修复。

appIdcom.videokit.app、UID10221、budget730a73e1-50e1-4198-a515-047104f00e31和所有N2旧身份固定。旧源basic.mp4 349102B/SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9；subtitle.avi 736454656B/SHA3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f，均已MPREP合法预置，不重新导入。本批coder未stat/read/hash它们。

## QUERY与原ABORT

只选com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort。固定e5N2Task=86cafdb3-0fc4-447d-920b-b19c884bf494，e5N2Budget=730a73e1-50e1-4198-a515-047104f00e31，e5RecoveryBatch=D1-E5A-N2-RECOVERY-20261017。QUERY参数e5N2Action=QUERY，默认也是QUERY。仅核有界原metadata/两个实际退出记录/proc，不锁/fence/hash输出、不写S。QUERY_ELIGIBLE不代表恢复完成或编码准入。

独立审后另派e5N2Action=ABORT_ORIGINAL_N2。原N2进程退出证据仍核原host24853/codec24873/UID10221与1792208947872..1792208970000唯一时间窗口，保原reason/status，不补原closeACK。归档在预算N2-e5-recovery；原before/R/实际保留输出不删，实际字节计唯一S，不按空文件退款。新recovery.owner必须在fence前记录实际writer身份。所有真实FD/guard/目录资源返回与原S/readback成立后才返回ABORTED_SETTLED；尾部失败BLOCKED保全原结果。

ABORT结束会结束该instrumentation，活准入不跨进程。负责人独立核其原报告/唯一S/前像/原输出/实际所有者和完成候选后，才准确派观察。若ABORT尾部BLOCKED，不自动当成功；需审其具体候选状态，另决定是否允许新的独立当前状态观察。缺任何字段的半事务仍BLOCKED，禁止补写或再次ABORT。

## 独立最终观察

Standalone仍选上述同方法/同固定参数，e5N2Action=OBSERVE_SETTLED_N2，增加e5aSettlementReceiptSha256=独立结算审查报告真实SHA256。此值只标识外部审阅，语法不是授权或资源证明。

观察从原私有recovery.owner读取attempt/PID/UID/name/记录时间，核本host为不同的正确主进程、真实唯一退出记录与/proc ENOENT。原writer未死/可见复用/记录不足则BLOCKED。核原ABORTED/lease fence、before、proof、稳定anchor/完整链和唯一S、完整completion、归档marker、保留输出当前SHA/实际字节；任何新的普通任务pending也拒绝。随后本次独立force现有文件/关闭、三个目录fsync/关闭、metadata复读、两排他guard实际close；不写R/S、不移动/补文件。全部返回才FRESH_OBSERVATION_ADMITTED且仅本host有效。

旧force/close未知永远仍未证；新的观察只证明当前状态已由本次实际原对象同步并归还，不回填原旧结果，不声称绝对掉电。观察方法卡在实际调用不返不能超时计归还；保存阶段与原对象PENDING。失败的观察不在同进程自动重试。后续任何新host默认再拒绝，必须有新的明确派发与当前实际观察。

## 正常四项单方法

共同参数e4Batch=D1-E4A-E5A-NORMAL-TABLET-20261017、e4BudgetIdentity=原稳定budget、e4Case=该单方法名；e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT、e5aSettlementReceiptSha256=独立结算审查真实报告SHA。每方法@Before在任何fixture读取和Session创建前做本次观察，不能直接复用已结束进程内许可。

| 顺序 | E4DeviceTests 单方法 | 通过前提 |
|---|---|---|
| 1 | normalMp4SixRealFrames | 原MP4合法，真实6入6出、isolated EOF/PTS/缩略图、资源与S真实归还才READY |
| 2 | normalAviSixRealFrames | 首项通过，原AVI，所有同原门 |
| 3 | capabilityDenialDoesNotOpenSource | 两正常通过，0源open/read bytes、0帧、无假READY、原资源终局 |
| 4 | cancelRejectsWrongEpochOversizeAndLateFrame | 两正常独立审过；e4NormalReceiptSha256为真实正常报告SHA，原首次cancel30秒，不接迟到帧、不READY |

只运行准确单方法，不整类；不含三个quarantine、旧Binder或新signal/nativefault，不扩到手机/其他平台。观察失败或任一产品FAIL/PENDING即阻断后续，保全部原输入/失败产物/账链，不反复变体尝试。

## 终局证据与仪器结束

正向、negative、cancel、await异常/中断、try-with-resources close与JUnit @After共用finishForInstrumentation。记录terminalPhase、terminalReason、firstCancelAtNs、cancelDeadlineNs、cleanupContinuations、ownerFinishEntries、originalOwnerReturned，以及原六组host/remote细阶段、原identity/epoch/gen/instance、PID/UID、候选/公共错误、callback/native/Image/FD/CONTROL在途、首错/cleanup/system reason分列。

初轮PENDING不得立即assert结束；Future等待同原owner接续和原资源/预算实际返回后报告ABORTED（首错仍失败），或到同首次30秒截止报告PENDING/ORIGINAL_CANCEL_DEADLINE_PENDING。截止仍未知时所有原对象/计数/预留保留，不以系统finished inst算closeACK。原调用在截止后真返回也不提升原FAIL/PENDING。90秒await外壳不改变60/12/15/30秒验收。

保存每个原host调用stdout/实际exit/原owner返回、JUnit tests/failures/code、全部原状态与单调消费S；ADB exit0、语法receipt、fixture可读、完成文件完整均不等PASS。完整结果主动报负责人再派下段。D1未通过/M0未启动/全部P0与历史FAIL保持。
"""
 for name,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gates),('DEVICE_EXECUTION_APPENDIX',appendix)]:
  with (R/('docs/coder/D1_E5A_'+name+'_V1.0.md')).open('x',encoding='utf-8',newline='\n') as f:f.write(text)
 print(json.dumps(dict(documents=4,deviceCalls=0)))
if __name__=='__main__':main()
