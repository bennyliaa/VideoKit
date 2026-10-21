# D1 R4 控制操作清单独立复审报告 V1.0

日期：2026-10-16。按R4测试需求、开发需求及负责人正式整包交接，对两份材料完成一次离线复审。本轮只读文档、历史记录并解析表格；未运行harness、媒体IO、JDK/.NET预检、Gradle、构建、ADB或设备任务。

## 1. 结论与可裁定意见

**R3-R01的材料缺口已闭合，R4材料足以供负责人另派有限本机harness实现。** 18项记录：18 SUPPORTED、0 CONTRADICTED、0 MISSING。未发现需要继续补设计材料才能派该有限实现的阻断；不建议重复重写已认可的close/writer语义。

该意见的范围是有限工具实现准备，不是实验执行授权、公共API冻结、产品/设备通过或完整P0闭合。真实backend、guard/Java兼容、稳定版本、DuplicateHandle、mailbox、实际ticket关闭、durability、退出及性能均待实现验证。10ms/N只是规划假设；实现后仍须按既定门禁审查、冻结，再由负责人明确派发实验，不能以本报告自动开始运行。

独立重算61行具名token全部与N列相符：P176、Q127、PF16、GC32，非query351；query101，总控制452≤544。R3各行query与时间分配逐项未变，媒体/输出/记录硬预算保持。T05已有完整14次独立请求，不再依靠每行6或组合finalize解释。

宿主JNI仍BLOCKED、全P0和历史FAIL不变，C14继续等待负责人安排。D1未通过、M0未启动。无本批实验、设备或构建任务在途。

## 2. 输入身份与证据

| 文件 | 本轮实际SHA256 | 结果 |
| --- | --- | --- |
| D1_R4_CONTROL_OPERATION_MANIFEST_V1.0.md | 6492f598b8b9f605239648277d08a56beae565c65de0f1dac5cee6db2ffa40bd | 与正式交接和回执一致 |
| D1_R4_DELIVERY_V1.0.md | ebca0ae145b162f29e19e5d0921fed99f3f0bd6118f16226f52e7ef93c227f88 | 与正式交接一致 |

两份原字节副本、链接/身份核查、引用锚点、61行token独立解析与PF/GC序列记录保存于[D1_R4_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_R4_EVIDENCE)。7处本地链接、5个唯一目标可访问。R2五份及R3三份原件逐项SHA与既交付值一致；本轮没有修改主体、旧报告、C14、产品、原需求或媒体。

另核R3独立报告R3-R01、R3分支表及close/writer契约、R4开发/测试需求。源路径/历史hash仅沿已有记录引用，没有打开媒体、重新验真整片或运行任何工具实验。文档解析是审阅辅助，不计为功能PASS。

## 3. 逐项判定

SUPPORTED表示材料在限定范围内完整、有据，不能解释为实现或实验通过。

| ID | 审阅对象 | 判定 | 独立意见 |
| --- | --- | --- | --- |
| R01 | 输入身份/原始材料保留 | SUPPORTED | 两SHA匹配，R2/R3八原件未变，副本留证 |
| R02 | 覆盖旧计数规则与授权范围 | SUPPORTED | R4只替代非query分配515的解释，负责人已允许在544内重分配；101 query/180秒/32记录及close/writer等约束保留 |
| R03 | 61行ID、逐行token及PF/GC编号 | SUPPORTED | 61个ID与R3集合一致，无增删；忽略参数内逗号、展开并发花括号后逐行token=N，PF01–16/GC01–32连续 |
| R04 | 控制请求、数据D及完成回报边界 | SUPPORTED | 独立提交/拒绝/重放计N，read/write/seek有D ID和请求预算；原操作一次完成回报不再发新客户端命令。open/close/claim/放闸均未藏进D |
| R05 | token的有界实际副作用/owner | SUPPORTED | grant只元数据；alloc/dup/send/take/claim/flush/ca/cb/v+/cv各独立，ticket与G/J/R归属明确。一个N下单次factory/native动作和元数据事务有边界 |
| R06 | T05完整独立路径 | SUPPORTED | Q07-TAKEFIRST从空初态14N，包含create前置、两份写引用关闭、独立验证lease/receipt、新epoch、旧ready拒绝和新abort，不借T01/T02 |
| R07 | T01/T02/T03/T04共享前置及终态 | SUPPORTED | T01逐行沿用原A/B后最终READY；T02第二验证取消、T03写引用关闭扣留、T04空间错误/未知/排空独立ABORTED。未将IO能力事实混写为成功导出 |
| R08 | P11双consumer/future open | SUPPORTED | FUTURE13N、SEALED12N，res(A/B)都落账；第一end后仍第二预留，seal先赢时第二open请求计费而factory0 |
| R09 | P10-B旧close与新对象 | SUPPORTED | 13N，旧close实际一次，q1后新分配对象，旧command重放及旧revision重试各计且native0。未强制发生数值复用就不伪称复用实证 |
| R10 | P12旧通知/ACTIVE版本及H=0 | SUPPORTED | OLDOPEN完成v2读/三close/end后保留v2 ACTIVE；NOTICE不能替它seal，CHANGED才seal(v2)。H=0有前置，旧通知仍可由ACTIVE/sealSequence验证不能授权移动 |
| R11 | S17预登记、次数/未知及顺序 | SUPPORTED | D行11N先登两close再放首次闸门，第四请求拒绝；C行4N只放原请求和拒绝重试/围栏，无UNKNOWN后新open。尾部转GC，非新组合API |
| R12 | PF16及两个既有helper | SUPPORTED | 两进程实例、hello版本、res/guard/H/ref、两个真实16B D、独立close/end/能力预检逐项计费。元数据随原open返回，不再免费额外stat RPC |
| R13 | GC32、退出证明与逐引用归还 | SUPPORTED | 清理/停止共用32槽，无额外query；安全close资格明确，J/R死亡分别通知S/O；父guard/pipe/process/log不因helper死清账，未证保留PENDING |
| R14 | 元数据事务/日志文件峰值 | SUPPORTED | 每接纳N/D至多两事务，open/write/sync/close/namespace ACK逐项有界，query重放不新读journal；快照双槽合计16KiB，行日志32KiB。详见§5，实际IO时延/字节仍待测 |
| R15 | 非query/query/全控制求和 | SUPPORTED | 176+127+16+32=351≤443；+101=452≤544，余92不授权扩分支。每行query与R3一致 |
| R16 | 媒体、目标/记录、时间及资源预算 | SUPPORTED | 原分配1,573,522B/59调用、10目标/32记录、写655,360B/验证262,144B、180秒均保留；新增控制未改变D分配 |
| R17 | 行时间余量与最终GC/n32 | SUPPORTED | 10ms/N规划下61行余量均正、最小710ms；明确不保证native/同步时延。GC/n32记账后最后调用，结果走原有返回通道，未在log关闭后再开新log |
| R18 | 实现准入与其余门禁边界 | SUPPORTED | 足以建议负责人派有限工具实现；真实backend/效果均未证。F03四次仅encoder，宿主JNI/P0、历史signal FAIL/C14 NOT_RUN、Kit/Flutter/C ABI/许可边界未放宽 |

## 4. 独立计算及关键顺序

解析结果见[control-and-budget-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_R4_EVIDENCE/control-and-budget-audit.json)。每个分支保留具体token列表、原始行号、N、Qr/Qn、秒数及规划余量；没有执行这些请求。

| 项 | 独立重算 | 限界 |
| --- | ---:| --- |
| 分支/非query | P31行176；Q30行127 | 每行与token实际展开数相符 |
| PF/GC | 16/32 | 序号连续，GC不用槽不挪用，清理/停止不各发32次 |
| 非query总分配 | 303+16+32=351 | ≤443，余92不授权额外操作 |
| query | 重放18+新观察83=101 | 与R3各行逐项一致，无PF/GC隐含额外query |
| 全控制 | 351+101=452 | ≤544；92余量不能绕过逐行分配 |
| 原始输入请求/调用 | 1,573,522B/59 | ≤4MiB/256，继承R3逐行分配；失败/未知不返还 |
| 目标/顶层记录 | 10/32 | ≤12/32；17S+14T+PF1 |
| 输出写/验证读取分配 | 655,360B/262,144B | ≤2MiB/4MiB；4份独立验证lease |
| 文件峰值分配 | 61×32768+131072+32×16384+524288=3,178,496B | ≤4MiB，剩余1,015,808B只作停止证据 |
| 时间分区 | 20+52+55+5+20+10+18=180秒 | 控制/native/D/等待/落盘在行及分区内，不在180外追加 |
| 规划最小余量 | 710ms，P12-OLDOPEN | 1秒−19×10ms−1×100ms；不是真实测量 |
| 其他重点行规划余量 | T05 2660ms；S17-D 1590ms；C 2560ms | 仅在所述快速路径假设下成立，阻塞即停止/PENDING |

T05的顺序可直接复核为grant→allocA→dupB→sendB→takeB→claim→flushB→cb→ca→v+→cv→takeover→旧ready→新abort，共14次N。write及验证read另有D ID，既不免费授writer/验证lease，也不借用其他task receipt；q1在READY_ELIGIBLE，最后重放旧q1不得倒退终态。

输出副作用向量也可由各T任务独立累计：目标10、dup9、send8、take7、claim提交6；claim拒绝/重放不重复提交；数据write请求9、delegate至多8，随机seek3；flush/syncB各4；A10+B9共19份写descriptor关闭，validator open/read/close各4。W3安装未知时保留区间，不能把计划计数当运行时精确0。T02含dup后1B小写及后续三次随机写，未少算前者。

S17的D/C异步close均在第一次故障前登记；D的两次获权重试、第四拒绝和C的不同op/新owner重试均有收费，UNKNOWN后不新增关闭资格。GC正常路径先关父guard，J实际退出后S按原实例分别核D/C，最后end消费者；D实际nativeclose仍0、C原close仍UNKNOWN。若helper未退出或父引用未证，不能报告全源DRAINED。

P12在v2引用结束后仍保留ACTIVE，与“0句柄便可移动”不同：NOTICE操作不得产生v2 seal/移动许可；CHANGED才显式seal(v2)。v3只是授权版本事件、未创建consumer/open，不外推为真实文件变化。此设计没有要求在guard归还后再次读取源；状态变更、releaseSequence与版本墓碑应由实现保留证据。

## 5. 元数据、日志与最后关闭的解释

元数据持久写是接纳/完成同一操作的有限子事务，不是另一个可授资源的控制请求。R4已给出每个接纳N/D最多两次、每次≤8KiB，native open/write/sync/close及必要namespace ACK各≤1；新query最多一份≤16KiB只读事务，缓存重放不再读。真实调用仍须记录并受时间、句柄和文件峰值门禁，不能据此放宽为任意内部RPC或无限重试。

累计写入字节与磁盘上同时存活文件字节是不同量：两次事务会重复写，可能使元数据累计写入大于文件峰值。这里4MiB按已定日志/元数据文件峰值控制，不能把3,178,496B误称总磁盘写入；实际事务次数、native副作用和时延均应另外报告。当前没有新规定元数据累计写入等于媒体请求预算，也没有因此扩大媒体I/C/V/O。journal必须按当前/备用两槽复用且总≤16KiB/记录，不生成无限历史副本。

每N/D接纳+完成事件合计≤768B，每query≤1KiB；最大明确行P12-OLDOPEN为19×768+4×768+1024=18,688B，低于32KiB行额度。PF128KiB、32记录双槽快照512KiB及全局512KiB纳入总峰值。不能只截短UNKNOWN/首错字段求符合字节预算；超限必须停止。controller log与journal/恢复reader同时最多2，J恢复读取前需确认写句柄已关闭，query读取也应顺序执行；真实实现如果需要额外句柄或文件须先暴露，不可漏计。

GC/n32的逻辑ID归32清理槽，但实际在Final-accounting10秒内最后执行，与其余GC31槽的20秒清理/18秒停止不重复计时。所有最终快照须在close前完成；调用者通过原controller返回通道取得该次flush/close事实，不能拿关闭前记录的“将关闭”当证明。返回通道也丢失时外层保留PENDING，不重开新log来无限证明上一log。该安排可作为有限实现要求，不是本轮已证明实际关闭成功。

## 6. 有限实现的准入范围与待实证出口

建议负责人据此另派**有限本机harness实现和实现审查**，绑定R2/R3已认可语义及R4操作分配，不扩大产品范围、不改冻结C14。无需为了准备实现继续要求设计文档提供真实OS运行结果。

实现应能逐项给出：G/S/O/J/R固定owner与原进程实例、单请求/数据操作/ticket账本、前置预算预留、真实delegate与元数据事务计数、独立reference、逐份FD关闭和UNKNOWN收敛、实际文件峰值及单调时钟。代码审查后才能冻结可执行候选；是否运行仍由负责人另行派发。

预检的JDK/.NET共享模式或同对象版本证据不满足则BLOCKED/NOT_RUN_PREFLIGHT；真实dup/必要durability不支持则保留对应NOT_RUN；native/IO超时、资源或日志关闭未证则PENDING并停止后续。10ms/N不满足时报告具体实耗/超限，不能删控制步骤、暗改期限或把61项未执行记通过。合法短读预算出口仍UNFILLED，不能改成provider错误或完整窗口成功。

以上为需要实现和以后实测的既定要求，不是本报告新增的设计阻断。有限IO工具无法关闭宿主JNI故障屏障、完整显示/PCM、真实NAS/Android transport、跟踪质量、正式Kit/Flutter/可移除AAR、许可等其他门禁；这些继续按原计划保留，不因本轮18 SUPPORTED变成P0通过。

## 7. 交付状态

本报告、输入副本、input-and-link-audit.json、reference-anchors.json、control-and-budget-audit.json及review-summary.json均保存于tester目录。无实验、媒体窗口、设备、构建、故障注入或新harness进程在途；本轮运行的只是文档解析核查，均已返回。

R2/R3原件与C14未改；D1未通过、M0未启动。主动通知送达情况以本窗口最终回复为准；此前自动审批拒绝跨窗口通知，本轮不反复尝试，供负责人既定定时检查收取。
