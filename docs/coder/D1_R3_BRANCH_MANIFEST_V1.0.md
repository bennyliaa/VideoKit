# D1 R3 冻结分支清单与累计预算 V1.0

2026-10-16。回应R2-R03；本表是待独立评审的**设计manifest，不是执行结果**。覆盖R2的P01–P13/Q01–Q09全部明示分支，并补close三类/耗尽及writer交付窗口；原22个用例族展开为**61个具名P/Q分支**。无harness、媒体IO、故障、构建或设备执行。

依据：[R3需求](D:/CodexProjects/VideoKit/docs/milestones/D1_R3_CODER_REQUIREMENTS_V1.0.md)、[R2评审R03](D:/CodexProjects/VideoKit/docs/tester/D1_R2_REVIEW_REPORT_V1.0.md)、[R2 provider原计划](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md)、[R3 close/writer修订](D:/CodexProjects/VideoKit/docs/coder/D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md)。本文件**覆盖R2 provider§2的“22项各一次/每项10秒”、§3笼统分支与P01最多16次补齐承诺**；不删除原分支，不放大硬限额。

## 1. 执行身份、共享任务与结果口径

原始输入L/C/Z沿R2路径、长度及历史SHA：L为3,212,959,911B大MKV；C为4096B损坏MP4（这里只当字节）；Z为0B空MKV，均在`D:\CodexProjects\VideoKit\test_media`只读。历史hash不当现场全片验真。guard＋Java实际ReadHandle＋独立reference的版本条件保持，未通过预检则后续不开始。

同一S/T编号是同一个逻辑任务记录，分支按表顺序执行/断言，**不重新创建task或重复IO**；终态栏为该任务最终允许状态，分支中间检查点另写。不同编号独立。共享仅用于终态相容的断言：T01成功流式、READY丢回复及READY胜出均归同READY；T04空间失败单独ABORTED，不被“未知空间成功”吞掉。T02的random/dup正向IO后故意验证取消，记录IO能力成功事实但整个任务ABORTED，不宣称导出成功。

- `D`：相关consumer及所有句柄/guard/reference/操作实际归还、case版本SEALED_DRAINED；不是移动原文件。
- `A/R`：同输出任务ABORTED或READY，资源实际归还；均只限IO_BYTE_PROBE，不是有效媒体。
- `P→X`：指定检查点PENDING；若本行受控清理如期完成才到X，否则全局停止，不能只拿X覆盖PENDING观察。
- `U`：观察终点保留UNKNOWN/PENDING；只允许最终全局清理，不开始后续分支。

每次输出task只一个writer attempt。T01–T10各最多一个物理目标；T11/T12能力拒绝、T13输入别名拒绝、T14 grant记录后、目标创建前owner退休只有元数据。S01–S17共17源任务，输出14任务，预检/运行头1记录，**共32个顶层任务记录**。操作ticket/descriptor/事件嵌于所属记录和有界日志，不作为可无限增生的旁路：每记录快照≤16KiB，事件和查询响应≤1KiB/条，全部文件仍受日志4MiB硬限额。

## 2. 列定义与分配规则

`I/C`=本分支原始输入请求字节/调用**上限**，包括provider及独立reference、EOF和失败/未知请求；不是实际读成功量。对包装器采用保守`charge=max(outerRequested,该次delegate实际请求总量)`，嵌套一次不重复计调用，实际delegate调用另记，且不得超过已预留调用额度。零请求在进入provider前返回，媒体IO为0。`V`为输出验证读取请求预算。未使用额度不自动挪给别的行。

`G/M/O`=本行新目标/新顶层记录/该新目标最大写预算；同任务后续行均0，不重复收费。O=65536时实际probe只需少量字节，不能因预留64KiB去无理由填充。`H/B`=本行媒体/输出/guard/reference句柄和64KiB缓冲的并发上限；同任务既有引用也计入。`Qr/Qn`分别为同queryRequestId缓存重放和新观察次数上限；query都是同资源身份，不新授writer/open。

每query控制观察≤100ms且计本行时间；新观察最多3、缓存重放最多1，表中可更低。一次查询超时停止该观察，不自动再给1秒；同副作用command/claim重放的次数另由分支说明限定，不能当查询绕过计数。非query控制命令逐行最多6次（P10-D为8次、P10-C为4次，两行仍合计12）；包括任务授权/seal、open/claim及其重放、cancel/abort/takeover和close请求，不把拒绝或失败排除。PF另最多16次、全局清理/停止合用最多32次，Final-accounting无控制副作用。query按表另计18次重放＋83次新观察＝101；总分配为61×6＋101＋16＋32＝515次，新增本清单控制命令硬门禁544次。29次余量不授权新增行/重放；每行与全局门禁同时生效，全部占既定行/分区时间。所需控制步骤无法在本行额度完成即预算停止，不暗中转为内部命令绕过。所有实际delegate/dup/send/claim/close计数另逐项记录；native调用不是可绕过时间/资源上限的额外授权。

### 2.1 预检、清理及全局分区

| 分区 | 内容 | I/C | 新记录 | 时间硬分配 |
|---|---|---:|---:|---:|
| PF | JDK/.NET版本与受控helper启动；guard+Java+另一进程reference兼容/同对象核查；C各读16B比较；能力/目录/日志预留 | 32/2 | 1 | 20秒 |
| Source-body | §3除P10-C/D的29行 | 见表 | 16 | 52秒 |
| Output-body | §4全部30行 | 见表 | 14 | 55秒 |
| Close-tail | 最后P10-D→P10-C，两对象先预留，见§5 | 0/0 | 1 | 5秒 |
| Global-cleanup | 所有task/FD/ticket核对；受控Java helper正常退出、匹配实例死亡证明；parent guard/reference及控制资源实际归还 | 0/0 | 0 | 20秒 |
| Final-accounting | 预算/结果/未启动清单落盘，禁止媒体IO | 0/0 | 0 | 10秒 |
| Stop-reserve | 仅全局停止/取消和未知资源证据，不补读、不重跑、不扩分支deadline | 0/0 | 0 | 18秒 |
| 合计 | 单调时钟从PF前开始，不重置 | 另见§6 | 32 | **180秒** |

预检失败立即记PF失败/环境或版本BLOCKED，61个分支均NOT_RUN_PREFLIGHT；已经分配的helper/guard只在清理分区处理，不能重新启动PF碰运气。全部新增实验OS资源同时≤24：媒体类≤6、两个受控helper的pipe端点≤12、进程句柄≤2、log/journal同时≤2，剩余2为停止余量；不得因为H列只列媒体就忽略控制句柄。8个64KiB缓冲总上限不变；JVM/.NET基线另记，不能把它描述为整个runtime内存上限。

## 3. 源分支manifest（31行，57秒）

N1–N4为四个真实窗口：B=2147483648，分别`B−65536/B−32768/B/L−65536`，长度均65536。每N行给provider/reference各一次64KiB请求，**满读且hash一致才WINDOW_VERIFIED**。合法短读时记录WINDOW_UNFILLED，不以违规失败，不在该行追加补读；可以继续独立窗口，不能宣称四窗都完成。

S1–S4对应相同四窗口的合法短返回预算对照：包装器每次仅向真实delegate读1B，外层请求剩余窗口仍保守收费。四次请求收费`65536+65535+65534+65533=262138`，独立reference读4B收费4，第五次剩余请求65532不能预留，故止于262142/262144、5调用，4B前缀一致但整窗**BUDGET_STOP_UNFILLED**。不是磁盘真实短读故障；不将其记provider违规/完整窗口PASS。正常满读和该预算出口是不同分支。

| 分支 | 任务/前置与独立性 | 终态/检查点 | I/C | V | G/M/O | H/B | Qr/Qn | 秒 |
|---|---|---|---:|---:|---|---|---|---:|
| P01-N1 | S01/PF，窗口1 | D；仅满读才窗口成功 | 131072/2 | 0 | 0/1/0 | 3/2 | 0/1 | 2 |
| P01-N2 | S01/N1已返回，窗口2 | 同S01；独立窗口结果 | 131072/2 | 0 | 0/0/0 | 3/2 | 0/1 | 2 |
| P01-N3 | S01/窗口3 | 同上 | 131072/2 | 0 | 0/0/0 | 3/2 | 0/1 | 2 |
| P01-N4 | S01/窗口4，S01还须P02 | 同上，不先关guard | 131072/2 | 0 | 0/0/0 | 3/2 | 0/1 | 2 |
| P02-EOF | S01/沿同对象在L读1 | EOF−1，不截断offset；保留S01至ZERO后D | 1/1 | 0 | 0/0/0 | 3/1 | 0/1 | 1 |
| P02-ZERO | S01/零请求，结束S01 | 返回0，真实媒体IO0，D | 0/0 | 0 | 0/0/0 | 3/0 | 0/1 | 1 |
| P01-S1 | S02/PF，窗口1短返回对照 | D；BUDGET_STOP_UNFILLED | 262144/5 | 0 | 0/1/0 | 3/2 | 0/1 | 2 |
| P01-S2 | S02/窗口2，前行资源操作已完成 | 同上，非provider错误 | 262144/5 | 0 | 0/0/0 | 3/2 | 0/1 | 2 |
| P01-S3 | S02/窗口3 | 同上 | 262144/5 | 0 | 0/0/0 | 3/2 | 0/1 | 2 |
| P01-S4 | S02/窗口4，结束S02 | 同上 | 262144/5 | 0 | 0/0/0 | 3/2 | 0/1 | 2 |
| P03-RAW | S03/Z真实空文件 | length0/EOF−1，D | 16/1 | 0 | 0/1/0 | 2/1 | 0/1 | 1 |
| P03-MEDIA | S03/同空对象媒体preflight | CORRUPT_MEDIA/EMPTY_MEDIA，无decoder，D | 0/0 | 0 | 0/0/0 | 2/0 | 0/1 | 1 |
| P04-SEQ | S04/C，注入length=null，真实读32及reference32 | 未知非空，字节一致后D | 64/2 | 0 | 0/1/0 | 3/2 | 0/1 | 1 |
| P04-CPU | S04/同未知长度描述，CPU能力负例 | SOURCE_CAPABILITY_UNSUPPORTED候选码，无decoder，D | 0/0 | 0 | 0/0/0 | 3/0 | 0/1 | 1 |
| P05-SHORT7 | S05/C，请求32，每delegate≤7，5次＋reference | 32字节/来源hash一致，D；非SOURCE_CHANGED | 128/6 | 0 | 0/1/0 | 3/2 | 0/1 | 2 |
| P06-ZERO | S06/C，注入非零请求返回0，delegate0 | INTERNAL_ERROR_REDACTED/INVALID_PROVIDER_RESULT，D | 32/1 | 0 | 0/1/0 | 2/1 | 0/1 | 1 |
| P07-EARLY | S07/C，声明4097，在4096读1，真实EOF | CORRUPT_MEDIA/EARLY_EOF，D，不冒称换版 | 1/1 | 0 | 0/1/0 | 2/1 | 0/1 | 1 |
| P08-LATEOPEN | S08/C，真实open后扣完成，再seal/cancel | 取消响应CANCELLED且先PENDING，晚H只close，最终D | 0/0 | 0 | 0/1/0 | 2/0 | 0/2 | 3 |
| P09-CANCEL | S09/C，真实读32后扣完成，再cancel | CANCELLED＋操作仍1；放闸排空才D | 32/1 | 0 | 0/1/0 | 2/1 | 1/2 | 3 |
| P09-TIMEOUT | S10/C，同延迟但不先cancel | SOURCE_TIMEOUT；1秒响应后仍PENDING，排空才D | 32/1 | 0 | 0/1/0 | 2/1 | 1/3 | 3 |
| P10-A | S11/C，delegate前失败；两retry同revision并发 | 仅一个attempt2实际close；D，首错保留 | 0/0 | 0 | 0/1/0 | 2/0 | 1/2 | 3 |
| P10-B | S12/C，actual close后ACK丢失；旧ticket并发重放，再开新对象读32＋reference | CLOSED_PROVEN仅确认，旧delegate1；新对象不被旧关闭伤及，D | 64/2 | 0 | 0/1/0 | 3/2 | 1/2 | 3 |
| P11-FUTURE | S13/C，异token同L/v，两预留；第一关闭后第二才open/read | 检查点仍预留1不可移动；最后seal排空D | 64/3 | 0 | 0/1/0 | 4/2 | 0/2 | 3 |
| P11-SEALED | S14/C，第一真实读；seal先于第二future-open | SESSION_RELEASED，额外factory0，D | 32/2 | 0 | 0/1/0 | 3/2 | 0/2 | 3 |
| P12-OLDOPEN | S15/C，v1排空再授权v2，读版本对照，旧open到达 | 拒旧SESSION_RELEASED；v2计数不变，D | 64/4 | 0 | 0/1/0 | 3/2 | 0/1 | 1 |
| P12-NOTICE | S15/旧releaseSequence通知迟到 | 只更新v1墓碑，不给v2移动许可，D | 0/0 | 0 | 0/0/0 | 0/0 | 1/1 | 1 |
| P12-CHANGED | S15/可信宿主授权换版事件 | SOURCE_CHANGED候选只指该证据；原文件未变，D | 0/0 | 0 | 0/0/0 | 0/0 | 0/1 | 1 |
| P13-SEQ | S16/C，注入SEQUENTIAL_ONLY，真实顺序8＋reference | 字节一致，D | 32/2 | 0 | 0/1/0 | 3/2 | 0/1 | 1 |
| P13-SEEK | S16/同能力seek请求，结束S16 | SEEK_UNSUPPORTED，delegate seek0，D | 0/0 | 0 | 0/0/0 | 3/0 | 0/1 | 1 |
| P10-D | **S17/全部Q结束后**，先为D/C两对象登记；D安全未执行失败3次，第四请求 | EXHAUSTED/PENDING；attempts3/delegate0，拒第四 | 0/0 | 0 | 0/1/0 | 3/0 | 1/2 | 2 |
| P10-C | S17/另一个已登记对象close结果未知，禁止重试 | U；不同op/新epoch不产生第二close；转全局清理 | 0/0 | 0 | 0/0/0 | 3/0 | 1/3 | 3 |

S17的两个对象/关闭请求在进入负例前均已登记；P10-D/C是最终预定close清理操作，不是UNKNOWN后再开新源或授新数据请求。其余source分支先完成、再全部Q、最后S17两行，避免中途留UNKNOWN却继续分配。

## 4. 输出/交付分支manifest（30行，55秒）

先完成PF和非S17源任务。T01的实际源payload32B及reference32B只在Q01收费，此后私有不可变probe字节复用于IO协议任务，不冒充播放缓存/真实帧或新源授权。所有Q均使用独占新目录.bin，禁止覆盖输入。metadata-only响应永不携writer能力。

| 分支 | 任务/前置与共享关系 | 终态/检查点与断言 | I/C | V | G/M/O | H/B | Qr/Qn | 秒 |
|---|---|---|---:|---:|---|---|---|---:|
| Q09-OPEN2 | T01/两个调用者同command并发 | R；grant1、元数据响应2，create/dup/send0 | 0/0 | 0 | 0/1/0 | 0/0 | 1/1 | 2 |
| Q09-CLAIM | T01/唯一receiver/delivery正常认领 | R；目标1、A+B、dup/send/take/claim各1 | 0/0 | 0 | 1/0/65536 | 2/0 | 0/1 | 2 |
| Q09-SECOND | T01/第二receiver或第二claimId | R；稳定拒绝，真实引用/dup/send不增 | 0/0 | 0 | 0/0/0 | 2/0 | 0/1 | 1 |
| Q09-REPLAY | T01/能力已交后同open/claim重放，各1次 | R；只不可写元数据，无第二owning wrapper | 0/0 | 0 | 0/0/0 | 2/0 | 1/1 | 1 |
| Q09-PLAN | T01/同export不同planVersion | 原任务R；EXPORT_FAILED/INTENT_CONFLICT，无副作用 | 0/0 | 0 | 0/0/0 | 2/0 | 0/1 | 1 |
| Q09-SOURCE | T01/同export不同sourceVersions | 同上，身份字段单独覆盖 | 0/0 | 0 | 0/0/0 | 2/0 | 0/1 | 1 |
| Q09-PRESET | T01/同export不同preset | 同上，不合并遗漏字段 | 0/0 | 0 | 0/0/0 | 2/0 | 0/1 | 1 |
| Q01-SEQ | T01/真实C32B＋ref32B→顺序写/close/验证 | R；字节probe一致，所有写/验证引用归还 | 64/2 | 65536 | 0/0/0 | 5/2 | 0/1 | 2 |
| Q05-STREAM | T01/与Q01同一次真实流式IO，space=null且已允许bounded模式 | **R成功流式**；不是“无READY”负例 | 0/0 | 0 | 0/0/0 | 0/0 | 0/1 | 1 |
| Q06-LOST | T01/READY真实提交后丢回复，另一预启helper读回/query | R；同token/handle/intent，无新writer；必要durability未证则NOT_RUN | 0/0 | 0 | 0/0/0 | 0/0 | 1/2 | 3 |
| Q08-READY | T01/既有READY后cancel/query回包暂失 | R胜出；不是CANCELLED，无在途writer/validator | 0/0 | 0 | 0/0/0 | 0/0 | 1/2 | 2 |
| Q07-READYFIRST | T01/READY先于takeover/abort | R同token，ownerEpoch不因读终态增加 | 0/0 | 0 | 0/0/0 | 0/0 | 0/1 | 1 |
| Q04-DUP | T02/真实Windows同进程A→B一次dup，正常交付 | 最终A；先关A，B仍可小写，dup1/双ticket独立 | 0/0 | 0 | 1/1/65536 | 2/1 | 0/1 | 2 |
| Q02-RANDOM | T02/同B三次有界seek/写，关闭后第一次只读验证 | 最终A；随机IO/读回确实成功，不称READY | 0/0 | 65536 | 0/0/0 | 2/2 | 0/1 | 3 |
| Q08-VALIDATOR | T02/第一次验证归还后显式再授一次验证lease，读后扣完成，再cancel | P→A；第二验证lease未归还不abort终结，放闸清空后A | 0/0 | 65536 | 0/0/0 | 1/1 | 1/3 | 3 |
| Q04-CLOSEACK | T03/真实A/B，B实际close后扣ACK | 最终A；B只query确认不重close，A仍计1 | 0/0 | 0 | 1/1/65536 | 2/1 | 1/2 | 3 |
| Q08-WRITER | T03/A的实际关闭暂扣住，再cancel/query | P→A；A不归还不终结，放闸后归还 | 0/0 | 0 | 0/0/0 | 1/1 | 1/3 | 3 |
| Q05-SPACEFAIL | T04/不同任务，真实少量写后注入空间不足 | **A失败分支**；OUTPUT_SPACE_INSUFFICIENT注入，非真实磁盘满 | 0/0 | 0 | 1/1/65536 | 2/1 | 0/1 | 2 |
| Q08-UNKNOWN | T04/两写引用仍持有、query保持不确定 | 检查点PENDING，停止新grant，不称已取消/释放 | 0/0 | 0 | 0/0/0 | 2/1 | 1/3 | 2 |
| Q08-DRAIN | T04/仅清理已登记引用，打开已定测试闸门 | 如真实close完成则A；未完成全局STOP，后续NOT_RUN | 0/0 | 0 | 0/0/0 | 2/1 | 0/1 | 2 |
| Q07-TAKEFIRST | T05/原writer关闭并验证到READY_ELIGIBLE，takeover先于已排队旧ready | A；旧ready STALE_OWNER、新owner仅abort | 0/0 | 65536 | 1/1/65536 | 2/2 | 1/1 | 3 |
| Q09-W1 | T06/owner退休于A已创建、dup前 | A；create1/dup0/send0，A真实关闭 | 0/0 | 0 | 1/1/65536 | 1/0 | 0/1 | 2 |
| Q09-W2 | T07/A+B已创建、send前owner退休 | A；dup1/send0，两个ticket真实归还 | 0/0 | 0 | 1/1/65536 | 2/0 | 0/1 | 2 |
| Q09-W3 | T08/send已调用、交付ACK未知 | P→A；send1、不重发，位置未知不能计引用0 | 0/0 | 0 | 1/1/65536 | 2/0 | 1/2 | 2 |
| Q09-W4 | T09/receiver已take、claim前退休 | A；take1/claim0，receiver引用不可漏账 | 0/0 | 0 | 1/1/65536 | 2/0 | 0/1 | 2 |
| Q09-W5 | T10/claim持久、确认丢失或随后owner退休 | P→A；claim1，abort-only，不恢复写/不重送FD | 0/0 | 0 | 1/1/65536 | 2/0 | 1/2 | 2 |
| Q09-W0 | T14/grant记录后、目标创建前退休 | A；create/dup/send/take0，native引用0 | 0/0 | 0 | 0/1/0 | 0/0 | 0/1 | 1 |
| Q03-RANDOM | T11/只顺序但要求random | REJECTED；OUTPUT_CAPABILITY_UNSUPPORTED、writer0 | 0/0 | 0 | 0/1/0 | 0/0 | 0/1 | 1 |
| Q03-VERIFY | T12/validationReadLease=NONE | REJECTED；同上，不能暗建副本 | 0/0 | 0 | 0/1/0 | 0/0 | 0/1 | 1 |
| Q09-ALIAS | T13/目标别名实际指输入，写前身份检查 | REJECTED；OUTPUT_CAPABILITY_UNSUPPORTED、写/截断0 | 0/0 | 0 | 0/1/0 | 1/0 | 0/1 | 1 |

W0–W5的owner退休是**明确的owner身份/调度模型注入**，不冒充真实OS死亡；A/B是真实harness句柄，由稳定ticket实际归还。W3的同进程mailbox转移不产生额外OS dup，实际native引用仍2；其“接收位置未知”不能被其他跨进程transport套用。真实Android Binder/OS进程死亡的窗口需未来backend实证，本轮NOT_RUN。W6对应Q09-SECOND/REPLAY，W7对应Q04-CLOSEACK及P10三类close对照。

共享T01/T02等只共享同一任务的不同断言，不把“正向IO能力事实”与“任务终态”混写：T02最终A不取消其成功读回事实，也不算成功导出；T04永不READY；query/命令重放只控制元数据，实际dup/send/take/owning wrapper数量须逐项保持。

## 5. 最后未知close与停止后记账

先预留S17两对象/ticket，再seal，按P10-D、P10-C执行预先登记的关闭操作。D为确定未执行的3次安全失败＋拒第四；C为delegate结果未知且无安全重试资格。任何新的源open/read/writer授权均已禁止。结束观察仍PENDING，不强写D。

Global-cleanup安排受控Java测试helper正常退出，由外部controller按启动实例核实际退出；ticket强引用保留至进程终结，不装shutdown hook盲重关UNKNOWN数值。其独有descriptor可记RELEASED_BY_OWNER_EXIT，原close结果/首错仍UNKNOWN；parent guard/reference/pipe等另外实际close。helper未退出或其他引用未证，保留PENDING与具体owner，180秒决策期限到仍不报资源释放。该退出是本机harness收尾，不是SIGSEGV、Android worker或宿主JNI隔离实验。

任一较早行真实IO/close超时、身份冲突或必需能力失败：当行记实际失败/未证及已消耗预留，全部后续未接纳行记NOT_RUN_STOPPED_AFTER(branchId)，已接纳操作保留原ledger交Global-cleanup，不回退计数；此时不为“收齐61项”再授资源。预期的局部短读配额出口在操作已返回并归还后可继续独立窗口；它不等于全局IO/资源未知停止。

## 6. 可复算总预算（不是实耗或完成保证）

| 项 | 清单分配上界 | 保持的硬上限/处理 |
|---|---:|---|
| 原始输入请求字节 | Source 1,573,426＋PF32＋Q01 64＝**1,573,522B** | ≤4,194,304；剩余未分配，不借给短读补齐 |
| 原始输入调用 | Source55＋PF2＋Q01 2＝**59次** | ≤256；失败/未知预留不返还，实际delegate另记 |
| 新物理目标 | T01–T10＝**10** | ≤12；2个余量不授权新增case/补发目标 |
| 顶层任务记录 | S17＋T14＋PF1＝**32** | ≤32；记录/嵌套ticket/事件均有字节与数量边界 |
| 目标写预算 | 10×65536＝**655,360B** | ≤2,097,152；每目标≤128KiB原上限保持，本清单只预留64KiB |
| 输出验证读取 | Q01/Q02/Q08-VALIDATOR/Q07-TAKEFIRST各65536＝**262,144B** | ≤4,194,304；原始reference计I，不在V重复计 |
| query重放/新观察 | 按61行Qr/Qn逐项计数，见回执算术核对 | 18次重放＋83次新观察＝101；行上限不变，合计另限160；全部控制分配515≤544，均占行时间 |
| 日志/元数据文件 | 行日志61×32KiB＋PF128KiB＋快照32×16KiB＋全局清理/回执512KiB＝**3,178,496B** | ≤4,194,304；剩余1,015,808B仅停止证据，不扩字段/无限日志 |
| 时间 | 20＋52＋55＋5＋20＋10＋18＝**180秒** | 包含PF、reference启动、query/重放、清理和落盘；不是每行再加10秒 |

H/B不相加为同时峰值：行串行、共享任务资源按行上限保留，媒体峰值5≤6、控制资源合计新增OS句柄≤24、缓冲峰值4≤8；未达到终态/未知时禁止开始新的独立任务。预算控制器在每个副作用前原子预留**该行、该任务和全局**三层剩余额度，任一不足即STOP/UNFILLED而非provider违规，不用事后实际少读冲回预算。

上述180秒是controller不再接纳/等待的最坏决策预算，不声称能中断所有底层系统调用。原生IO若不返回，时限到记录PENDING及NOT_RUN，不在后台无限重试/延长；不能同时承诺任意合法短读都收齐全窗口或任意环境都完成61项。只有真实完成的分支才给结果，全部计划仍未实现、未运行；有限IO不能放行宿主JNI BLOCKED、D1或M0。
