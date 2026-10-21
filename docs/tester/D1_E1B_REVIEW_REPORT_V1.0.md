# D1 E1B 冻结实现独立审查报告 V1.0

日期：2026-10-16。依据D1_E1_TESTER_REQUIREMENTS及负责人正式整包交接，对E1B源码、归档、机器manifest和既有合成证据一次完成独立静态审查。

## 1. 结论

**暂不建议另派真实本机实验。发现4项P1实现/验证阻断、1项P2持久记录完整性缺口。** 应集中修复、补有针对性的合成负例并另批冻结后复审；本轮不修改或重跑冻结包。

18项审阅记录：13 SUPPORTED、4 CONTRADICTED、1 MISSING。这是实现材料审查，不是测试执行统计。主要问题为：迟到open/read及取消超时只有事后状态标记；已结束consumer仍可重新open；旧owner ready由测试布尔值直接拒绝；恢复可能降低已消费query额度且无法判别缺失任务记录；底层短写未核验便认定元数据记录已提交。

源码和归档身份可信、真实平台绑定及正常路径有代码和既有证据，但“148+20=168项检查”不覆盖上述反例。正常运行的预算和退出记录可以支持其限定事实，不能据此将五项原缺口整体视为验收通过。

本轮没有重跑SelfCheck、NegativeChecks、Recover、PF、媒体、构建、Gradle或ADB，没有启动J/R/harness。仅运行已读过的只读verify及tester自有归档/AST/证据解码脚本；均已返回，无本批在途任务。宿主JNI仍BLOCKED，C14未恢复，D1未通过、M0未启动。

## 2. 身份、范围与独立核查

| 对象 | 实际SHA256/结果 |
| --- | --- |
| freeze-summary.json | 231782d7bf337d0c2b3a9062f9a2b92a107b6c870d03637ab8fb40fe433abbcb |
| E1B-source.zip | 770d77af488f21f2cbc20456eefe8f81e5b2d93589c53336010a9843b50431e0 |
| E1B.dll | 3f16ab845f8246c3cdd1c742c9ff2263571c106cc768c8bd7784e8d90703f49c |
| 三份交付文档 | 与freeze的字节数/SHA逐项一致；副本留证 |
| 只读verify | PASS：26源码、18冻结文件、836合成记录文件、13份既有基线 |

tester另用独立脚本重算上述清单所有字节/SHA、源ZIP成员集合与内容，逐行比较61分支N/query/时间与已审R4，并以AST核对每个入口符号存在。没有用“verify显示PASS”替代源码审查，也没有编译判断二进制行为。原E1依赖源码ZIP和对应清单随包提供，旧失败DLL/联调日志保留；0字节before-repair-1.dll仅是失败痕迹，不当有效产物。

证据目录：[D1_E1B_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E1B_EVIDENCE)，包含三文档和26源码/工具/manifest副本、archive-and-manifest-audit.json、source-anchors.json、既有外层回执/关闭前摘要、独立解码的archived-synthetic-review.json及相关q日志。没有复制或读取test_media原样本字节；hash核查中的.bin/.out均为冻结合成证据。

## 3. 逐项独立判定

| ID | 审阅项 | 判定 | 结论与限界 |
| --- | --- | --- | --- |
| R01 | 冻结源码/ZIP/产物身份 | SUPPORTED | 与正式交接一致，ZIP成员逐个匹配，不是功能PASS |
| R02 | 61机器分支/入口/分配 | SUPPORTED | 集合、operation数、N/query/秒数与R4一致；符号存在不等对应断言有效 |
| R03 | 上游依赖、编译/失败痕迹范围 | SUPPORTED | Core/Native/RHost和Java源码在包内，原E1关系清楚，历史失败未被删除；未独立重编 |
| R04 | 168项合成检查范围 | SUPPORTED | 148来自既有合成联调，20来自独立逻辑负例；L=131072/边界65536，绝不计真实2GiB/媒体/设备；旧80项不混计 |
| R05 | 行/任务/全局额度及一次RPC接纳 | SUPPORTED | Budget三层先核再记，Flow在外部effect前记ADMITTED，Engine.remote限制一次白名单RPC；不是所有反例均已覆盖 |
| R06 | G/J/R真实绑定及身份消息 | SUPPORTED | J真实RandomAccessFile；R真实CreateFile/DuplicateHandle/ReadFile/WriteFile/FlushFileBuffers/CloseHandle；HMAC、请求缓存、角色/claim检查存在。此为可信工具进程协议，不等RCE/产品权限隔离 |
| R07 | close ticket三类、安全retry/耗尽 | SUPPORTED | 活动Java及C#CloseTicket保留object/ticket/revision，不凭closed布尔；已关只查、UNKNOWN不重试；S17原事实保留 |
| R08 | writer唯一grant/dup/send/take/claim正常路径 | SUPPORTED | 不向客户端传裸HANDLE，mailbox转同一B，确认未知abort-only，A/B独立ticket；不据此关闭R11的旧ready仲裁缺口 |
| R09 | 迟到open/read、取消/超时及零请求 | CONTRADICTED | hold在真实结果返回后才记ops，数据/对象已同步返回，timeout仅sleep；ZERO为0==0。见E1B-T01 |
| R10 | consumer结束/handle绑定后的接纳围栏 | CONTRADICTED | open/read未核finished及handle.consumer一致，P11可构造已end(A)后复开A。见E1B-T02 |
| R11 | Q07旧owner ready的实际epoch仲裁 | CONTRADICTED | ready(old=True)先直接抛STALE_OWNER，未提交原ownerEpoch进行真实比较。见E1B-T03，不声称已产生错误READY |
| R12 | 中断恢复的完整预算/未知记录 | CONTRADICTED | 恢复直接用q日志数量覆盖快照额度，并跳过不存在task目录；完整正常32记录不能证明这些反例。见E1B-T04 |
| R13 | 元数据整条写入确认 | MISSING | 原始FileIO.write返回长度未核验，短写出口缺失；未在本轮制造磁盘故障。见E1B-T05 |
| R14 | query日志与只读权威语义 | SUPPORTED | view来自G状态，重放不改终态、不重授writer；但每次q包括重放均append/fsync事件文件，非零磁盘IO，需如实归入证据/cache层。其恢复合并正确性仍受T04阻断 |
| R15 | PF版本/身份/共享模式的范围 | SUPPORTED | 合成guard与reference物理ID相等、Java长度/样本SHA对照；未完整关联Java handle的fileKey到guard，也未证明真实媒体版本，文档已保留限制，不能以PF声明cap替代实证 |
| R16 | S17/GC/n32正常证据与原实例退出 | SUPPORTED | 既有原实例wait/exit0、D耗尽/native0、C原UNKNOWN/native1、n32外层返回与关闭前摘要分开。异常停止分支未因此获得完整释放证明 |
| R17 | 文件峰值/累计写与受管资源口径 | SUPPORTED | 本次文件峰630431B、累计写6141446B分开；受管峰21/媒体5/缓冲1是工具账本，非整个JVM/.NET内核资源总数，不能外推24总句柄已实证 |
| R18 | 实验入口/requiredDurability与其他门禁 | SUPPORTED | experimentEnabled=false、CLI只有显式合成入口；requiredDurability仍UNPROVEN，合成READY不等真实耐久READY。真实实验配置未交，不得直接改SelfCheck当实验；JNI/P0/C14/历史FAIL不变 |

## 4. 集中缺陷、静态反例和修订建议

以下均为源码静态结论或尚未封闭的分支；**未执行反例，不写成实际崩溃、越限、泄漏或源损坏。** 严重度针对工具实现及真实实验准入，不追改历史设备结果。

### E1B-T01｜P1｜迟到/取消/超时用状态标记代替待完成操作

来源：[open_j:204](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:204)、[read_j:236](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:236)、[gate:252](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:252)、[场景:61](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/scenarios.py:61)。

open_j(hold=True)在J已返回后设置currentH和ops/open=未done，仍立即向调用方返回对象；read_j(hold=True)完成真实RPC、离开buffer作用域后才设置ops/read，仍返回已含字节/摘要的value。Flow.transaction也将该D记DONE。后续gate只是把ops.done置true，既没有扣住供消费者等待的completion，也没有保留与该完成关联的私有buffer所有权。

P09-TIMEOUT只sleep(1)再查operations==1，没有实际产生并断言SOURCE_TIMEOUT响应；P09-CANCEL只改cancelled并查计数，没有取消一个仍在等待的read响应。P08也不证明取消时晚H从未交给消费者。P02-ZERO直接断言0==0，未调用实际零请求适配路径。这些可以支持“状态标记/账本对照”，不足以支持所映射的迟到响应/取消/超时语义。

建议实现有界的pending completion/私有结果cell：真实delegate可以先返回，但交付闸门未开时消费者仍等待，取消/响应deadline明确完成相应错误而底层资源继续留账；gate后只走正确清理/丢弃路径。将buffer/结果cell生命周期计入账本并断言未交付、未复用。零请求调用真实bridge零长入口且delegate计数不增。合成自检需观测响应/实际状态，不能只断言测试自己设置的ops标志。

### E1B-T02｜P1｜end后的consumer仍可获得新open/read

来源：[end:188](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:188)、[open接纳:207](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:207)、[read接纳:239](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:239)。活动权威是Python gengine；Core.cs旧SourceAuthority虽有Quiescing检查，不能当本路径已经受保护。

end只将consumer.finished=true；open_j检查sealed/cancelled/recovered/PF围栏，未检查finished，read_j也未检查finished或handle.consumer==请求consumer。在P11-FUTURE“HA已关、end(A)、B预留仍在、版本尚ACTIVE”的合法中间态，将下一次h+参数改为已结束A和新对象名，当前接纳条件全部成立，可进入J OPEN，而不是SESSION_RELEASED。相同h+标签检查不会核manifest参数必须是B。对read则可把另一个未取消consumer作为c绕过原对象所属consumer的状态。

建议在同一源权威原子点检查reservation仍ACTIVE/未finished、version/generation/consumer和handle精确绑定；end不可逆停止future-open和新read，旧已接纳操作只排空。补已end(A)/B仍活时复开A、旧handle借B身份read、结束/取消与open/read并发三个有限负例，断言delegate0和他消费者状态不变。

### E1B-T03｜P1｜旧ready断言由布尔值触发，未验证原owner身份仲裁

来源：[ready:334](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:334)、[Q07:126](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/scenarios.py:126)。

Ops.ready(old=False)的第一条是need(not old,'STALE_OWNER')，Q07传True便必定得到期望错误。方法没有接收原请求的ownerEpoch/owner实例；因此即使没有发生takeover，True同样被拒绝。后面的receipt.epoch==当前epoch检查有保护价值，但不使这个用例成为“旧e1请求在e2持久接管后实际到权威被围栏”的独立证明。

本报告不声称已绕过receipt产生错误READY。问题是关键仲裁检查依赖测试告知“这是旧owner”，不是校验不可替代身份；正常epoch/claim的HMAC数据面检查不能补上G内ready入口缺失的调用者身份。

建议ready提交真实捕获的ownerInstance/epoch、export/handle/attempt/revision/receipt，权威从持久当前owner比较并稳定返回STALE_OWNER；Q07应在e1捕获待发请求，e2接管后原样发出，去掉old布尔快捷拒绝。同时覆盖“未接管的合法原owner可ready”和错误epoch/receipt各自拒绝原因，不能借新增多次实验反复求通过。

### E1B-T04｜P1｜恢复可降低query预留，且缺失任务记录没有明确未知出口

来源：[恢复:9](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/recovery.py:9)、[恢复额度:17](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/recovery.py:17)、[query:152](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:152)、[Budget.restore:103](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gcore.py:103)。

query先计费并更新usage，再写/fsync q事件。恢复却把快照usage.qn/qr直接赋为可见事件条数。静态反例：快照已保留qn=2，第二次q的事件尚未完整提交，可读日志只有1个new条目；当前合并将2降成1。未知/超时请求也不得退款；GC跨shard取max的正确处理不覆盖这里的普通行覆盖赋值。

另一个窗口是已接纳任务的整个目录/两个槽缺失：recover对不存在目录直接continue，未用受恢复保护的任务清单区分“从未接纳”和“记录丢失”，也不列为unresolved。现代码恢复始终writeCapability=false并加围栏，故没有证明会重开writer或已造成越限；但其usage/未证资源不能被当作完整批次事实。仅对正常32份现存记录的回读比对不足以补该缺口。

建议按同身份单调合并快照与可信日志，已预留但结果未知的计数不能下降；q事件不全时标UNKNOWN并禁止使用差额。持久记录已接纳任务inventory/最小恢复总信用，缺失shard必须区分未创建与丢失；信息不足保留批次未知，不将遗漏项视为0。补“快照额度大于日志数”“已接纳shard缺失”“GC跨shard max仍保留”的负例，继续无raw handle重造/无副作用恢复。

### E1B-T05｜P2｜元数据短写未核验，提交字节计数按请求值记成功

来源：[Store.save:144](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gcore.py:144)、[Store.event:171](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gcore.py:171)、[ADMITTED门禁:119](D:/CodexProjects/VideoKit/docs/coder/d1e1b/src/gengine.py:119)。

原始无缓冲file.write(record/data)的返回字节数被忽略，计数直接加请求长度，随后fsync及save返回即被用作ADMITTED已记录。缺少“返回长度必须等于完整8KiB记录/完整事件”的检查；短写若未抛异常，现逻辑不能证明所需接纳记录已完整落下却可继续外部副作用。全局log和关闭前receipt写入也有同类未核验返回值。

这不是本轮观察到磁盘满或Windows发生短写，也不以checksum能在下次恢复发现坏记录替代副作用前的提交门禁。建议保持单次有界写预算，核实际返回长度；不足立即记录提交未知/失败并禁止后续native动作，不无限补写；written按实际量另记请求信用。合成故障层可只对自建元数据writer注入短返回，验证未发下游RPC、无虚假完成，不制造真实磁盘故障。若改多次写需重新显式分配事务/native次数。

## 5. 已有合成记录能够支持的事实

本轮独立解析现有槽：验证8KiB尺寸、头部/压缩payload SHA、64KiB展开上限、schema/batch/task身份，选择各task最新有效记录。32记录存在；普通快照加现存完整q日志后，351N/83新q/18重放及其他维度与外层回执一致。快照本身不总包含最后query的额度，因此不能省略q日志恢复步骤，也不能掩盖T04中“日志少于快照”的反方向风险。

关闭前摘要SHA8401fbe0e78a5911e2a4b1d8f2e1bc58f21ac1a954a3406caee02796fe9bca1f与外层回执一致。记录行数62=PF+61，不是62个媒体分支；GC48总phase控制由PF16+GC32分开核。正常既有数据为输入1,573,492B/59请求，较分配少30B不挪用；验证请求128B、10目标/32记录、输出信用655,360B。

S17.D attempts3/nativeCloses0；S17.C原UNKNOWN/nativeCloses1，实际原J退出后才记OWNER_EXIT。正常记录中的两个原helper均wait code0；n32磁盘状态仍READY_TO_CLOSE，真正flush/fsync/close成功来自外层原返回通道，不能只看磁盘意图。该次正常路径可支持“已记录的受管资源清空”，不能把未知原生调用、非零退出、父guard/log失败等未实证分支一并记通过。

元数据文件峰630,431B与累计写6,141,446B是不同维度，后者不是4MiB文件峰超限。query和重放均会打开.q、append事件并fsync，不是字面上的零磁盘IO；实现将其作为证据和query缓存日志，而非重写task主快照，文档已主动披露。每次仍需受100ms/行deadline/文件峰值及native计数约束；若后续要让该cache成为权威恢复依据，必须先修T04，不能靠称其“只读query”忽略实际写入。

受管资源峰21、媒体5、媒体buffer槽1不包括整个JVM/.NET基线/内部句柄与协议缓冲，不能写成全系统追踪已证明≤24/全部内存≤8×64KiB。另有固定缓存和协议长度上限，仍须在未来明确实验配置中说明可核资源口径，不用合成账本替代完整平台测量。

## 6. 下一批准入条件与交付

建议负责人一次派修T01–T04并补T05的提交完整性出口，保持冻结E1B原件与失败证据，在新批次集中实现、自检、冻结。新增合成检查应直接验证待完成响应/取消错误、end后的接纳拒绝、真实epoch请求仲裁、恢复额度不降与缺失任务未知、元数据短写禁止下游副作用；不要增加只断言文字/布尔标记的检查数量。

重新整包审查后才能判断是否可派真实本机一轮。当前experimentEnabled=false、真实样本绑定/2GiB窗口配置/requiredDurability准入均未获得本包放行；不能直接取消合成入口限制或在旧累计日志信用不足的目录重跑。PF声明OS_DATA_SYNC_ONLY与namespace UNPROVEN应保留，真实READY所需持久性不满足则NOT_RUN/PENDING，不能照搬合成READY。

现有预算/close/dup等正向实现事实保留，不要求重开R2/R3/R4已认可设计问题。工具修复不代正式Kit、Flutter、AAR、Android/NAS、显示/PCM、媒体质量/跟踪/许可准入；宿主JNI仍BLOCKED，原P0和历史signal FAIL/C14两项NOT_RUN不变。

报告和证据全部保存。无本轮SelfCheck/Negative/PF/媒体/构建/设备任务在途；未改候选或原媒体。主动通知状态见最终回复；此前自动审批拒绝跨窗口通知，不以更换内容或工具反复重试，负责人可按既定检查收取。
