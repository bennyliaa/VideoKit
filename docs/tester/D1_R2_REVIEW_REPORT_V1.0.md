# D1 R2 契约与故障判据独立评审报告 V1.0

日期：2026-10-16；任务：R2整包离线设计评审。依据正式tester需求、负责人R1处置决定及R1独立报告，对五份R2交付一次完成审阅。

## 1. 结论

**材料方向有依据，整包仍需补充后复审，不建议直接按当前文字实现并执行全部实验。** 20项审阅记录：17 SUPPORTED、0 CONTRADICTED、3 MISSING。此统计是设计材料分类，不是功能用例通过数；三项问题均为P1实验/契约封口前提，详见R2-R01–R03。

源版本与整任务预留、seal/reserve/open的原子点、Sink显式能力与READY仲裁、故障功能与精确原因分栏已比R1明确。剩余问题集中在失败close的安全重试条件、writer命令重放与真实句柄交付的关系、带分支的完整执行清单和累计预算。宿主JNI致命调用缺少故障屏障仍是明确的架构BLOCKED；文档正确保留该事实，不能因此称原P0已闭合。

本轮没有运行harness、媒体窗口、Gradle、ADB、设备或故障注入，没有安装包、模型或依赖下载，没有修改五份交付主体、产品、原文、C14和历史统计。D1未通过，M0未启动。C14继续等待负责人安排；R2不改变已保存的设备可用通知或冻结测试计划。

## 2. 输入身份与独立核验

| 输入 | 本轮实际SHA256 | 核对 |
| --- | --- | --- |
| D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md | b0bae695abdb189251ca81c40a45f2a6a27dacb2a9d740fbbe5d153f3a0dea17 | 与回执一致 |
| D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md | b64ba9c1ce43cff8c353e17dff2370c7de407342c63a0130652f1ddca5d67a52 | 与回执一致 |
| D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md | c070320396513c5d23d31535df62297f2961b6a4a0648716fc72c93439e75bf1 | 与回执一致 |
| D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md | e3adbcda852d421df0beda8c228e74de38f3e00421982da04089bbf476df07ec | 与回执一致 |
| D1_R2_DELIVERY_V1.0.md | c1ce4ae44be23219c41e1089db94aa6a67f3e68512c7a5f26f617dfddab74454 | 与正式交接一致 |

五份原始字节副本和核验记录保存于[D1_R2_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_R2_EVIDENCE)。41处本地链接、29个唯一目标均存在，带行号者在目标范围内；链接有效不等于语义已经实现。24份关键源码/manifest逐一与C14源ZIP及source-manifest比较一致，副本留证；此为静态字节核验，没有重跑本机断言或C14设备方法。

三份输入的路径、长度和历史SHA与C02冻结media-inventory一致。本轮仅读清单，没有打开媒体或重算3.21GB文件SHA；不据历史hash宣称现场源版本已经保证。另交叉核原文§14/17/26–31、公共API、集成/编辑/系统设计与项目执行决定、C13报告、C14计划和R1报告。未对外部API兼容或许可新增法律/运行保证。

## 3. 逐项判定

SUPPORTED表示材料在所声明范围内有来源支持，不表示实现或真机PASS；MISSING表示后续实现/实验尚需决定；本轮未发现应将五份材料中的主张直接定为CONTRADICTED的证据。

| ID | 审阅项 | 判定 | 证据与限界 |
| --- | --- | --- | --- |
| R01 | 五份交付身份及交接完整性 | SUPPORTED | 四主体和回执SHA匹配；原件副本留存 |
| R02 | 本地引用与源码身份 | SUPPORTED | 41处链接/29目标可访问，24份源码/manifest匹配冻结ZIP；不等于完成全部实现验证 |
| R03 | 物理源归并/版本/别名与整任务future-open预留 | SUPPORTED | 源§1明确宿主权威、token非路径、consumer/generation预留；S01/S02/S10覆盖异token及后发现别名，不以句柄0允许移动 |
| R04 | reserve/seal/open/read线性化 | SUPPORTED | 源§2同一串行器先登记后锁外IO；seal先则拒绝、open先则晚句柄清理，S03/S04有唯一结果；物理事务还须核版本/seq并独占，不靠旧DRAINED快照 |
| R05 | 资源向量/终态通知/query/换版和恢复 | SUPPORTED | 源§2/3与S05/S06/S08/S09不以新epoch、worker死或通知丢失抹除宿主在途；最终控制通知不进入自身释放条件，未知不可移动 |
| R06 | 失败close后安全重试的前提 | MISSING | 有次数/不重叠，但未区分未执行、已关闭后失败与底层结果未知；P10只覆盖delegate前失败，见R2-R01 |
| R07 | Sink能力/空间/持久性/输入别名目标拒绝 | SUPPORTED | 输出§1先协商再发writer，验证不可读不得暗建副本；sync/close/命名空间ACK分列，未知空间不无限。对不可证明的新目标必须拒绝 |
| R08 | FD模式/每份引用和关闭权 | SUPPORTED | 输出§2 BORROW/DUP/TRANSFER分表，首轮只候选DUP；同UID/合作式ACK不能证明恶意FD撤权，未证写引用保留PENDING |
| R09 | 一次writer授权与同命令真实交付的幂等关系 | MISSING | 输出§3/O06限制一个授权，但缺grant交付/认领状态和同command响应重放规则，见R2-R02；不据此声称已有重复交付漏洞 |
| R10 | writer封存/只读验证lease/receipt及输入收尾 | SUPPORTED | 输出§4/O03/O05/O10/O11要求所有写引用清空、同revision验证并真实归还，READY_ELIGIBLE前输入收尾；无“等待READY才能释放”的循环，其他消费者不阻止本导出READY |
| R11 | 同export恢复与READY/abort/COMMIT唯一终态 | SUPPORTED | O01/O02/O08/O09/O12保留同token、新owner仅清理/query、旧owner拒绝、READY不被迟到abort撤销；业务COMMIT仍宿主。首轮不续编码是有限提案，未删工程恢复P0 |
| R12 | 真实provider、2GiB窗口和独立对照 | SUPPORTED | 三输入历史清单相符，HostFixtures真实RandomAccessFile读；P01窗口含跨2GiB，另一进程reference不复用待测缓冲；不外推MKV解码/NAS |
| R13 | Windows guard版本证据与Java兼容前置 | SUPPORTED | provider:17–21明确受控普通共享范围，已有可写映射/敌对存储不在证明内；identity不可靠或Java不兼容则BLOCKED，不改共享模式放行。这是条件性计划，当前兼容与稳定版本均未实证 |
| R14 | 未知/空/短读/0进展/提前EOF分类 | SUPPORTED | P03–P07分开真实delegate与注入；提前EOF无可靠换版证据不称SOURCE_CHANGED，明确承认现Bridge仍返回−1的差距；新码/兼容未冒称冻结 |
| R15 | 全分支清单、累计IO/目标/记录/180秒可执行性 | MISSING | 硬上限和停止方向明确，但22编号不等22次执行，分支展开及全批最坏预算缺表，见R2-R03；安全停止不能证明整包能完成 |
| R16 | J01–J11危险调用、owner/UID/观察/回收与缺证 | SUPPORTED | CPU JNI与宿主MediaCodec/Image/lease JNI确实有不同边界；矩阵明确系统服务/Java catch/有界像素不等故障屏障，F08先机制再实验，未自行采纳同UID替代 |
| R17 | F01–F08功能判据及O01–O04可观测性分栏 | SUPPORTED | 要同宿主实例、另一真实任务、目标命中、源/输出与真实归还；F02必须有独立native见证，F01死因可UNKNOWN；配额失败、实际OOM、全局压力及强杀分开。新命名仍需负责人派发 |
| R18 | C12/C13精确信号历史及C14两项NOT_RUN | SUPPORTED | C13 self系统0/raw11/trace缺失仍严格FAIL；双槽原OS11和另一任务完成独立保留；没有追认F01/F02全项或覆盖历史FAIL。C14计划不变，不重复同条件注入 |
| R19 | R1-R05固定证据勘误 | SUPPORTED | 固定快照实际SHA为1f8fa4c6ca11c271d19fab16da06a3e490723c50251837219f6b0e3d49ca3d7a，at=12:38:18、WAITING_FOR_TABLET_CONNECTION；附加说明未回写已审R1主体 |
| R20 | Kit/Flutter/C ABI/Android先行、许可、全P0及阶段 | SUPPORTED | 回执§4映射§29十二项，.bin/协议READY不代真实视频，Windows工具不称Windows Kit，FFmpeg受限Debug/Media3方向未改；新码/公共schema仍待审，D1/M0未放行 |

## 4. 集中问题、反例和可执行修订建议

### R2-R01｜MISSING｜P1：失败close的重试资格与实际关闭证明未封口

来源：[源契约:52](D:/CodexProjects/VideoKit/docs/coder/D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md:52)、[S07:72](D:/CodexProjects/VideoKit/docs/coder/D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md:72)、[provider P10:48](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:48)、[HostFixtures:22](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/HostFixtures.java:22)、[Bridge:66](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/AsyncReadBridge.java:66)。公共API原有“close幂等”原则有效，但尚不足以说明发生部分副作用后由谁保证和如何证明。

当前方案把close失败统一留账并允许新attempt，正确限制了并发和总次数，却没有把“确定尚未调用底层close”“底层已关闭但应答/日志失败”“调用已返回失败但关闭状态未知”分开。反例是第一次实际释放了句柄，随后包装层失败；新attempt若直接再次操作可复用的裸句柄标识，会把重试副作用和另一对象混淆。另一方向是首次未能证明关闭，下一次仅因本地closed标志返回成功便清failedCloses；这同样不足以证明底层归还。

冻结HostFixtures的静态代码确实先`closed=true`再`file.close()`；若该调用异常，随后closeAsync可跳过底层调用而返回成功。此为反例路径，不表示本轮发生过IOException、实际泄漏或误关，也不要求修改冻结C14。P10只在delegate前注入失败，无法裁定这两个分支。

建议补close disposition与恢复表：仅“确定仍拥有原对象且关闭可安全再执行”才能新attempt；已实际关闭只补查询/完成确认，不再关闭；未知则PENDING，不能拿新operationId绕过。适配器保留稳定对象/关闭ticket和每层引用，规定close幂等的实现责任，不能重用裸数值身份。追加有限反例覆盖delegate前失败、delegate后应答丢失/异常、未知close和并发retry；实际资源确认和首因分开。先补设计，再决定后续有限harness如何验证，不在本轮注入系统close故障。

### R2-R02｜MISSING｜P1：一个writer授权不等于只交付一份可写能力

来源：[输出身份:47](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md:47)、[commandId:51](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md:51)、[O06:96](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md:96)、[缓存响应:110](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md:110)、[provider Q09:60](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:60)。

文档明确拒绝第二writer、禁止用新command取FD，方向正确。但“重复同请求返回同逻辑handle/状态”“附着唯一open记录”“重复合法命令返回缓存状态”没有区分可缓存的控制结果与不可重复交付的实际writer能力。

反例：同owner的两个调用者并发提交同command，或首次响应已经携writer交付而调用方超时重放。若缓存响应重送一个dup或把同对象暴露给两个独立owner/wrapper，账本中的writerLease仍可能只有1，真实可写引用却不止1；即使不新建目标，也不能据单个close允许验证/READY。另一窗口是grant已持久、实际交付/接收未知后的owner恢复。仅规定“不得第二FD作为第二writer”尚未给这些窗口的可实现裁定。

建议补一张grant状态/交付表：一次writerLease的唯一接收owner和deliveryId，创建/发出/认领/关闭的原子记录及恢复出口；同command重放只返回不可写的状态/handle元数据，或明确受控单接收者认领机制，不缓存重送FD/stream。交付未知时query不得再授writer，首轮按既定只清理/abort策略收敛。每份真实descriptor单独计账；旧owner或第二认领稳定拒绝。增加同command并发、已送达后丢应答、grant落账后owner死亡三个有限序列，并断言实际dup/交付数和全部引用，不只断言writer计数=1。此为通用契约补充，不声称当前C14已有重复交付缺陷，也不要求首轮扩为Android跨进程FD实验。

### R2-R03｜MISSING｜P1：分支执行清单和累计预算不足以审定完整一轮

来源：[provider预算:25](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:25)、[分支:26](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:26)、[目标/记录:27](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:27)、[180秒:28](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:28)、[分支说明:62](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md:62)。

22是用例族数。P09取消/超时、Q03两个能力负例、Q05未知空间/注入不足、Q07两仲裁顺序、Q08 writer/validation引用以及Q09合法重放/意图冲突/输入别名至少需要分别界定执行。按这些最少拆分已有29个场景；Q08终态顺序及Q09不同意图字段是否再展开尚未确定，29不是代拟的正式调度数。Q05成功bounded流式和注入失败的终态也应分列，不让族内“无READY”误判正例。

即使仅按22族每族观察/清理10秒，允许上界已220秒；29场景各10秒为290秒，均未包含运行时/guard兼容预检和另一进程reference启动。全局180秒硬停可以保证不无限运行，但不能证明“全部分支一次完成”。这不是已发生超时，也不要求将硬限额放大；缺的是可执行的分配和到期时每项如何记账。

IO同样应分正常计划和预算耗尽分支。P01四窗口两侧各满读一次，媒体请求为524,288B；若每次请求剩余窗口但每次只返回1B，16次有限短读仍符合请求上限，四窗口两侧的请求和可达8,387,648B，超过4MiB。现有全局拒绝能安全停止，但该出口须是预算限制/未收齐，不能误判合法短读为provider错误或声称全部窗口完成。其他case、失败/未知预留和reference也需计入。

建议提供冻结branch manifest：case/branch、前置、独立还是同任务、唯一预期终态、真实输入请求/调用最大值、输出验证读取、创建目标/元数据条数、最大并发句柄/缓冲、deadline/清理/全局停止后的状态。将query“同任务身份”与queryRequestId重放/新观察分开计数。把JDK/.NET版本、guard+Java+reference同对象兼容预检纳入时间/IO预算并明确预检失败不启后续。列出总和≤4MiB/256调用、12目标/32记录、2MiB输出、4MiB验证/日志及180秒的分配；无法保证完成的场景明确依赖停止/NOT_RUN，不笼统承诺全项完成。后续实现须在剩余预算内先预留再副作用，无新池/重复attempt求PASS。

## 5. Windows、故障判据与原P0的独立意见

Windows guard提案限定普通文件共享，明确不证明已有可写映射、敌对磁盘或全文件快照，边界表述可接受。opaque v是宿主授权身份，不是内容不可变证明；fileKey/length/mtime前后相同也不能被扩写成完整SHA验真。实施前必须满足文中兼容/身份条件，否则CASE_BLOCKED_VERSION_NOT_PROVEN。Java文档版本引用不证明当前运行时共享行为已兼容；本轮没有启动JVM、guard或reference做预检。

F01允许App cause UNKNOWN但必须证明原实例death及后果，F02另需实际native命中见证，O01/O02/O03分别保留系统字段/trace/分类能力，逻辑可以用于负责人后续制定新用例。它们不自动替换追加的严格signal门槛：C13 self系统0仍FAIL、独立raw11不回填App；双槽原OS11只归本任务；C14两方法仍NOT_RUN_UNCHANGED_PLATFORM_LIMIT。新功能方法在另一真实任务前置未成立时不得借单任务历史变PASS。F03有限回退次数只适用于已声明的encoder协商路径，其他Java/API失败不应由此获得四次重试授权；具体未来触发仍须单独派发。

J03–J06等宿主JNI同地址空间致命调用仍无故障屏障。报告将其判SUPPORTED仅支持“缺证且继续BLOCKED”的材料事实；没有支持该路线满足§27。显示/PCM、旧双轨验证、压缩图片/字幕和跟踪GL等亦不能被CPU worker隔离覆盖。不能将所有危险调用留BLOCKED之后反过来宣布P0安全闭合，也不应为证明已知缺口继续无变化地杀宿主或重跑ordinary isolated codec/GPU。

原文§27十一条发布阻断、全部P0、§29十二项和独立Kit/AAR/Fake/Flutter/C ABI、宿主业务/源事务边界均保留。有限.bin输出READY不证明正式媒体、六真实帧、音频、遮罩/跟踪质量或NAS。仅设计字段和错误兼容候选，不构成公共API冻结；Media3薄适配、受限Debug FFmpeg与模型/素材权利准入不因本报告扩权。Windows工具评估不等Windows Kit开发或支持。

## 6. 交付与下一步条件

交付本报告、原始五文档副本、input-and-link-audit.json、reference-anchors.json、24份关键源码副本及selected-source-audit.json、historical-input-identities.json、budget-review.json和review-summary.json。审阅脚本只处理文档、清单和源码字节，不运行实验。

建议负责人集中处置R2-R01–R03，补齐close与writer交付语义及branch预算后再整包复审；不要仅以“实现时注意”替代契约决定。审定后可另派有限本机harness实现/变更审查及一轮执行；不在本轮自动启动下一批。宿主JNI机制须另有可满足方案和准入决定，不能被本机IO结果代替。

本批工作全部完成；无harness/设备/构建/故障任务在途，只有已保存的离线评审材料。C14未因本批启动、未更改门槛或结果。通知送达状态以本窗口最终回复为准，不将跨窗口通知当作测试证据。
