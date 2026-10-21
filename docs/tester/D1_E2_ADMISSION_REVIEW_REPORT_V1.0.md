# D1 E2 真实 IO 配置独立准入审查报告 V1.0

日期：2026-10-17。依据 D1_E2_TESTER_REQUIREMENTS、负责人正式冻结整包交接及三份 E2 文档，完成配置、真实适配差异、入口门禁和既有合成归档的一次独立审查。

## 1. 结论与可执行范围

**E2 配置候选可接受为下一批适配的输入；当前不具备真实 IO 执行准入。** 真实 2GiB 四窗口、61 分支及原预算一致，逐 case 区分 OS 同步探测与产品 namespace/READY 要求，真实入口保持关闭。未发现需要重开 C01/C02、D01、T02–T05 的新反例。

下一批应集中完成 A02 输入/输出绑定、A05 Java opened-FD 身份、observer 接线与预算，并由负责人明确 durability 目的及阈值。**有一项具体提案冲突：若 G 的 deltaThreads 从 PF 前计算，+8 小于当前代码规划可出现的 +10 线程增量。** 本报告列为执行前须裁定事项，不宣称已实测超限，也不要求配置文档证明尚未执行的真实结果。

本批可认可范围是配置完整性、静态门禁及既有合成材料；不能据此启动真实 PF、媒体读取或设备测试。875 项合成与另 6 项配置进程元数据检查均不是本轮 tester 重跑。D1 未通过、M0 未启动，JNI BLOCKED、C14、P0 和历史 FAIL 保持。

本轮仅运行已审源码的只读 verify、自有 SHA/ZIP/AST/JSON 算术及既有槽解码；未运行 SelfCheck、Targeted、Recover、PF、媒体、构建、Gradle 或 ADB，未 stat/open/hash 真实输入，未新建实验根/helper/worker。全部审查程序已返回，无本轮在途任务，原冻结包未修改。

## 2. 身份与独立核验

| 对象 | 结果 |
| --- | --- |
| freeze-summary SHA256 | 06a799a0ba39eb76c9887fc7b5690fc29f20e1ee826c6067e9f8a322a9273ae2 |
| E2-source.zip SHA256 | 4e3510c4cba3c99919faf26cf5ff72ab2ebe4ada2fcf7db3690fba4451b312c2 |
| 只读 verify | PASS：43 源码、15 冻结文件、216 合成归档文件、13 基线；旧 E1E 188 冻结/自检及 33 源码一致 |
| tester 独立核验 | 清单字节/SHA、ZIP 成员/内容、61 入口符号、R4 逐行控制/query/时间及 E1E 全部原行分配/操作一致 |
| 既有记录解码 | 8KiB 槽 SHA、schema3/身份、展开上界及 32 任务 inventory 一致；两槽 usage 与可信 q 日志取 max 后等于原回执 |

独立证据及原字节副本见 [D1_E2_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E2_EVIDENCE)，包括 configuration-and-budget-audit、preserved-fix-audit、configuration-evidence-review、归档/ZIP/入口核验、三文档和源码/配置副本。完整性通过不等于重新编译或真实执行通过。

## 3. 真实区间、61 映射与版本门槛

L=3,212,959,911B、C=4096B、Z=0B；精确路径及历史 SHA 与既有来源文档一致。历史 SHA 仅作来源身份，2026-10-16 23:33 的 stat 仅是旧元数据事实；均不升级为当前内容、物理对象或版本证明。本轮没有重新访问媒体或祖先路径。

| 窗口 | 实际 offset | N 每方请求 |
| --- | ---: | ---: |
| B−65536 | 2,147,418,112 | 65,536B |
| B−32768 | 2,147,450,880 | 65,536B |
| B | 2,147,483,648 | 65,536B |
| L−65536 | 3,212,894,375 | 65,536B |

P01-S 同一窗口只有原四次 cap1 provider 请求和一次 reference4，依次请求 65536/65535/65534/65533/4，UNFILLED 不补读。真实 geometry 已显式配置；Scenarios 不再根据目录名猜 B，但 Engine 目前只允许严格合成 profile，真实路径尚未接线。这是正确披露的阶段边界。

独立逐行算术：351N、83 新 query、18 重放，共 452/544；101 query，输入请求 1,573,492B/59，相对原分配 1,573,522B/59 留 30B 在原行；验证请求 128B、原验证分配 262,144B，目标 10、记录 32、输出信用 655,360B，元数据峰分配 3,178,496B/硬 4MiB，180 秒均保持。不得把预算余量作为新增媒体请求、身份 RPC 或补读许可。

A02 尚需独立的只读 L/C/Z 别名与 CREATE_NEW 输出/日志根，保留 helper sandbox，检查祖先/reparse 条件及输出物理身份不与任何输入别名重合，不能复制素材进 SelfCheck 绕过。唯一新根须尚不存在并绑定批准批次、nonce 和冻结身份。失败时在首字节前停，不写源、不放宽 shareMask=1。

G guard、J 和已分配 R reference 须比较实际 opened-object 的 volume/index、长度、lastWriteTime 与原 object/ticket/owner，绑定源版本/consumer/generation，并持有到实际排空。P03 等未分配 reference 的分支不加 r+。PF 样本同样必须先核身份，不能先读 16B 再补版本证明。P12 版本变化仍是模型注入，不能当真实文件已改变。

## 4. A05 建议路线：限定 J helper 内的 FFM 借用原 FD

**建议负责人选择固定 Windows x64/JBR 21 的小型 FFM 身份桥，作为下一批首选适配路线；本报告没有批准其执行。** 使用原 RandomAccessFile.getFD 的现有对象，限定访问该 JDK 的 FileDescriptor.handle，以 J 内 FFM 调用 GetFileInformationByHandle；只返回 opaque volume/index、opened length/mtime 和原对象绑定。OpenJDK 21 的该字段为内部实现，实际 JBR 21.0.10 构建仍须本地核对，不能假定跨 JDK 兼容。[OpenJDK 21 FileDescriptor 源码](https://github.com/openjdk/jdk21u/blob/master/src/java.base/share/classes/java/io/FileDescriptor.java)、[Windows opened-handle 信息](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle)。

选择理由是可以复用现有 JDK 的 Java/FFM 能力，避免额外引入 JNI C/C++ 桥产物；FFM 在 JDK21 仍是 preview，且 native ABI/内存布局错误仍有原生风险，不能因此清除宿主 JNI BLOCKED。需明确审定编译 preview/21 版本、运行 preview/native-access 及仅 java.io 的反射开放参数，绑定实际 JBR 和产物身份；禁止全模块开放或自动下载依赖。[JDK21 FFM](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/foreign/package-summary.html)、[restricted native access](https://docs.oracle.com/en/java/javase/21/core/restricted-methods.html)。

实现应在原 h+/OPEN 内取得并验证身份，借用已有 HANDLE，不另开、dup 或关闭它，不改变文件位置，不新增 byte-read/N/RPC。raw HANDLE 不出 J、不入 journal；按原 owner/object/ticket 和 OPEN 回执缓存绑定。查询与 close 互斥、保持原 RandomAccessFile 强引用，内存和库 lookup 生命周期显式有界，失败保留原已打开对象进入原清理出口，不把 bridge 失败当 OPEN 未分配。既有 PF/n10 比较加上 J 身份；其他任务利用原 g+/h+/r+ 返回元数据在本地核，不添加 per-case identity RPC。

后续小范围验证应包括真实已打开对象与路径属性不一致、字段/符号/flags 不支持、关闭竞争与 query 失败的安全出口；先用自有非媒体文件验证，不借此开放真实素材。若实际 JBR/ABI 不支持，保持 CASE_BLOCKED_VERSION_NOT_PROVEN，交负责人选择另一明确方案；不能回退到 path fileKey、历史 hash、匹配样本或另开路径所得身份。FFM 建议是工程判断，并非现包已实现或已测的事实。

## 5. 逐 case durability 与终态

31 源分支为 NONE；30 输出分支为 OS_DATA_SYNC_ACK 的限定 probe。其 appliesTo 明确是已确认的 task journal，以及原 flushB 已分配的输出数据；没有给 grant/abort 等行补造 sync，也不要求无输出分支产生持久结果。失败/缺 ACK 时依赖该层的 case 保持 NOT_RUN_DURABILITY_UNPROVEN，UNKNOWN/PENDING 不当完成。

Q01-SEQ、Q05-STREAM、Q06-LOST、Q08-READY、Q07-READYFIRST 的产品 namespace/READY 变体另列 NOT_RUN_DURABILITY_UNPROVEN。协议 READY 与产品 OutputToken/业务 COMMIT 分开，不能用本次 OS_ACK 目的降低产品 P0。负责人可审定下一批仅做原始字节/协议及 OS_ACK probe，五项产品变体继续 NOT_RUN；若目标改为 namespace/掉电保证，则依赖 case 阻断直至具备相应证明和方案。

Q06 当前是原活 J 读 G 已 sync 日志、原活 G 重载权威，不是 G 崩溃/重启或断电。P06 零 delegate、P07 声明 4097/物理 EOF4096、cap 短读、晚完成、丢 ACK、owner/版本变化等均保留注入标签；不能作为真实磁盘故障、系统进程死亡或源内容变更结果。目的变更须单独核控制/实例/预算，不暗加 kill/restart/helper。

## 6. 资源阈值与 observer：可审定提案及具体冲突

受管 24/6/8 与原 G/J/R 完整进程计数分栏合理；原 23/5/1 不能称系统总量。PID＋creationTime＋HELLO owner、缺指标/身份改变/超阈值停止、同一原实例和采样峰限界可接受为接线约束。Win32 reader 最大一个临时 observer 句柄/信用，snapshot 关闭后逐个查询进程，无新线程/RPC，close 未证保留信用。旧合成峰 23 加 observer 1 在算术上等于 24，不能据旧峰保证现场有槽；没有信用必须停止。

| 提案/事项 | 审查意见与执行前裁定 |
| --- | --- |
| G 16线程/+8；J/R 各64线程/+32 | G 的 delta 锚点与规划线程数有冲突，见下文。J/R 数值可作为待裁定停止阈值，不是已测基线或成功保证 |
| G256/J512/R512 句柄及增量64/128/128 | 可作为有限停止提案，须绑定同一原实例及明确基线；采样本身的 G 临时句柄计数不能隐去 |
| G256/J768/R512 MiB WS/private，各增量128/256/256 MiB | 可审定为提案；不是可用内存预留，不因内存低自动提高或降低阈值 |
| availablePhysical≥2GiB | 建议维持待审门槛。964,145,152B 是旧瞬时快照，不代表现在；未来获批时做新鲜准入，不使用旧快照放行或直接降门槛 |
| 1s、最多201周期、gap≤2.5s、返回后0.1s | 数量/时间有界且只称采样峰；必须接入既有等待点，记录实际 gap/duration，不能保证 OS 阻塞可被0.1s中断 |
| events104320＋metrics26752 | 算术上恰等于原 global.log131072；201×128＋1024=26752。需要批准分配并实现强制编码/容量门禁，旧 events92901B 不是未来容量证明 |

**E2-C01｜配置裁定项：G deltaThreads 基线不明确，PF 前锚点的 +8 不能覆盖现有线程规划上界。** [Engine 原 IO pool](D:/CodexProjects/VideoKit/docs/coder/d1e2/src/gengine.py:19) 最多新增 2，[两 Channel](D:/CodexProjects/VideoKit/docs/coder/d1e2/src/gcore.py:241) 合计 4 条 pipe reader/drainer，CompletionHub 新增 2，[P10-A pool](D:/CodexProjects/VideoKit/docs/coder/d1e2/src/scenarios.py:79) 临时最多 2，总规划增量 10。runtime-policy 同时列 G PF前和 HELLO后基线，但未定义 G 的 delta 比较锚点。若取 PF前，其 +8 对允许的并发线程规划偏紧；采样可能漏掉短暂重叠，不能靠漏采宣称相容。这是静态可发生的预算冲突，不是实测达到 10 或代码必失败。

建议负责人明确保持 G 的 PF前基线和启动期观察，若以该基线计算全程 delta，可将 **+12** 作为待批准替代提案，同时保留绝对 16；+12 仅覆盖已知 +10 规划并留有限余量，不是本报告擅自修改或成功保证。也可另行明确分阶段锚点/启动期限制，但不能重建 observer 悄悄抹掉早期基线或超限峰。J/R 以各自 HELLO 后原实例作基线。确定后再冻结 policy 和接线验证。

observer 尚未接入真实 runner：需核每次观察在原行/180 秒中扣时，最长允许等待与 2.5s gap 的关系；不可返回的 OS 调用交原 IO pool/pending 保留所有权，不能偷偷加线程或在同一 IO worker 再提交并同步等待自身。早期 G 基线在 log 打开前的记录可有界暂存；采样到 n32 关闭前结束，关闭后不得再写。observer 耗时上限累加可能占用原场景时间，预算不足即 Stop，不能额外延长 180 秒。

未来须实现 ≤128B 单条编码、≤1024B 头、两分区容量/总容量门禁、exact_write 和累计 metadata 计数；放不下为 BLOCKED_OBSERVER_LOG_CREDIT，不加文件/句柄/事务或扩原峰。proposal 的196608额外内存/内部遍历上界和 runtime 开销仍须在实际接线中有界，不把逻辑字节当全部语言堆。J cache 编码单位保守上界202752已披露，不误报196608为全堆硬界。

## 7. 875 合成、另6项检查与既有修复保持

完整合成159＋最终定向716=875，定向分组为 E2 97、D01 205、completion153、authority139、恢复33、metadata69、通用20。没有累加早期712或旧E1E。E2 97 核配置篡改、未计费非零请求、假 approved/stat、namespace不降级、拒绝入口零副作用以及纯 mock 指标；不证明真实 G/J/R 采样接线、身份桥或真实版本。

另6项仅配置 Python 自身元数据检查；原回执 snapshot/query 两句柄先后真实关闭、同时峰1、剩余信用0。其4线程/140句柄/工作集21,393,408B/private12,365,824B 不作为实验 G 基线，更不代 J/R 基线。两实际 CLI 拒绝回执均 code2、executionAllowed=false、无真实输出根。

SourceAuthority、恢复、metadata检查及 Native/Core 与 E1E 原字节一致；notifications/startup_checks 仅 E1E→E2 标签/线程名/scope 变化。原修复静态认可保持。受限 Future 契约、实际 callback drain、部分启动 UNKNOWN、原错误及原 owner 退出事实均不改变。

正常合成 Hub CLOSED/信用0/无未知，64 cell 排空、两原 J/R wait code0，受管23/5/1、最终0；metadata requested=written=6,397,708B、unknown0/HEALTHY，文件峰630,540B。原 n32 见证关联摘要 SHA 3ff2bf65c61b5c6bc49740d981089a20a518735deced45942d2748ca0ac3e2c4。磁盘 READY_TO_CLOSE 意图不替代实际关闭，外层200秒只停止等待，不证明原实例退出。

## 8. 集中下一批建议

请负责人按一批集中安排：审定限定 OS_ACK probe 目的、A05 FFM/实际JBR与flags路线、G deltaThreads及其余runtime阈值/新鲜2GiB门槛、observer日志分配；随后实现 A02/A05/observer 必要接线及自有文件/合成验证，冻结新整包再交 tester 复审。

实际实验仍须独立的新批次授权和现场准入：新冻结身份、唯一未存在输出根、原 owner绑定、首字节前 opened-object/共享证明、当前资源/指标/log信用满足。A02/A05未完成、版本未知、durability目的不匹配、G阈值锚点未裁定或observer未接线/无信用，均不能执行真实依赖项。不要求本配置阶段预先证明实际实验通过。

本报告不直接派实验、不修改阈值、不解除真实入口。报告与证据已保存，按用户直接授权完成后主动发给 VideoKit项目助理；通知送达记录另存证据。D1未通过、M0未启动，JNI/C14/P0/历史FAIL不变。
