# D1 E2A 有限真实 IO 适配与准入说明 V1.0

2026-10-17。**适配已实现并完成自有非媒体文件范围的验证，真实媒体执行仍关闭；当前实际 OS 资源门禁结论为 `BLOCKED_R_HANDLES_519_GT_512`。** 本文件不构成真实 PF、61 分支或任何 `test_media` 字节读取的执行授权。

依据：[E2A 正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2A_CODER_REQUIREMENTS_V1.0.md)。配置与适配事实见 [adapter-feasibility.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/evidence/adapter-feasibility.json)、[runtime-policy.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/profiles/runtime-policy.json) 和 [cases.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/profiles/cases.json)。交付与执行明细分别见 [DELIVERY](D:/CodexProjects/VideoKit/docs/coder/D1_E2A_DELIVERY_V1.0.md)、[EXECUTION_APPENDIX](D:/CodexProjects/VideoKit/docs/coder/D1_E2A_EXECUTION_APPENDIX_V1.0.md)。

## 当前准入结论

本批允许必要适配、编译和自建非媒体文件验证。工具资源停止策略已获裁定，状态为 `APPROVED_TOOL_STRATEGY`；这项批准不等于真实批次批准。`manifest.realExecutionEnabled`、profile 的执行标志均为 false。`admission.request_real_run` 始终返回非零拒绝回执，不调用媒体读取器或 helper 启动器，不做输入 stat，不创建输出根。

本版本在整个生命周期保持 `REAL_IO` 入口关闭。修改 JSON 的 `approved` 或执行标志、传入看似批准的字典、改名为 SelfCheck、使用 `CANDIDATE_IO` 别名映射，均不能获得执行能力。后续真实批次须经过独立冻结审查，由负责人另派唯一批次，并通过另行受审的授权及启动层绑定冻结身份、原 owner 和全新输出根；本包不铸造这种授权，也不提供自行解锁通道。

实际 observer 已经在自建文件整批启动期间正确阻断一次：R 原实例在 PF/n05 建立首字节前基线时，句柄数为 **519，超过批准绝对上限 512**。回执为 `STOP_PENDING`，原因 `METRIC_THRESHOLD_EXCEEDED:R:handles`；外层 exitCode=1，原始 witness 保留 FAIL。该次输入请求字节与调用数均为 0，原 J/R helper 最终均实际退出且 code=0，callback worker 已 join，剩余账本资源为 0。该结果证明停止路径生效，不能写成实际资源准入通过，也没有据此提高阈值。

原始证据为 [selfcheck-1792168123102649100.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/evidence/selfcheck-1792168123102649100.json)。其实际 reader 完成 3 个采样周期，自有句柄 opened=closed=10、同时最多 1 个，未保留 UNKNOWN close 或在途 native query。现场 availablePhysical=3,004,215,296B，虽然达到 2GiB 内存门槛，仍不能覆盖 R 的句柄超限。

## 裁定、实现、负例及边界

| 项目 | 裁定与实现 | 负例或实际证据 | 结论边界 |
|---|---|---|---|
| A02 输入及输出命名空间 | 明确 L/C/Z 只读别名；独立输出根、单层安全输出名及 CREATE_NEW；逐祖先拒绝 reparse；输出 opened identity 与已证明输入 registry 比较 | 非法路径、输入名充当输出、已有目标、缺别名或身份、身份重绑均拒绝；祖先 reparse 位注入；实际 hardlink 创建遇 WinError 5、symlink 创建受权限限制，失败及限制保留 | 路径预检不是防敌对祖先替换的原子保证；未声称实际跨路径 hardlink、symlink 或所有 junction 场景已验证 |
| A05 J 原 FD 身份 | 固定 Windows x64/JBR 21.0.10 FFM 桥；借用原 RandomAccessFile 的 FileDescriptor.handle；原 OPEN 回执带身份、长度、mtime、原 object/ticket | 十个独立自有文件进程覆盖成功、路径属性分离、query/字段/类型/符号/flags 失败和 close 竞争；回执无在途且均观察到进程退出 | 只证明固定工具运行时及自有文件行为；不解除宿主 JNI/P0，也不证明真实媒体当前版本 |
| observer | G 原进程 PF/n01 前固定基线；J/R 原 HELLO 实例；既有 IO pool、安全等待点采样、单临时信用、原 global.log 分区 | 实际 R519>512 首字节前停止；缺指标、身份变化、增量、gap、周期、日志短写、满额与 UNKNOWN 等受控负例保留 | 实际资源准入未通过；mock 指标完整回归只能支持协议及停止逻辑验证 |

## A02：只读别名与独立 CREATE_NEW 输出

`Namespaces` 和 G/J/R helper 的命名空间检查采用精确 L/C/Z 别名，helper 帧使用 `L.bin`、`C.bin`、`Z.bin`。输入映射经 `E2A_INPUT_BINDINGS` 传递精确绝对路径；该环境变量只是数据，不携带执行授权。`SYNTHETIC` 输入及输出限于本包 `selfcheck` 的自建文件范围；`CANDIDATE_IO` 的输出只能位于本包既有 `runs` 后代，输入不得位于输出根内。解析器不创建候选根，未来唯一新根的独占创建归独立授权启动层负责。

G guard 与 R 输入原打开继续使用只读 `OPEN_EXISTING`、shareMask=1，不放宽共享以换取成功；J 保持原只读 RandomAccessFile。每个被原分支实际分配的 J/R 源对象必须在首源字节前，与仍存活的 G guard 比较实际 opened identity、length 和 lastWriteTime100ns，并绑定原 owner/object/ticket。没有分配 R reference 的分支不补加 `r+` 或额外 RPC。真实对象查询失败时，已分配对象及原 close ticket 先登记并保留，再阻断；不能把一次成功 open 从账本中抹掉。

guard、原对象及其 buffer/reference 保留到 native 实际返回、gate 完成且同步 callback 真正结束后才可排空。等待超时或取消意图不构成释放证明，晚返回也不撤销原停止事实。

输出名禁止路径分隔符、跳出路径、ADS、输入别名及输入精确路径。最终打开使用 CREATE_NEW，已有目标拒绝，不覆盖、不截断，也不先 touch 输入。祖先及最终项按 metadata 拒绝 reparse。原 CREATE_A 帧携带 G 已获的输入物理身份 registry，R 在原输出句柄内查询身份并拒绝与输入相同的对象；该比较不增加 RPC，不用路径或 hash 充当物理身份。

命名空间自检使用自建小文件。实际 hardlink 尝试收到 `PermissionError: [WinError 5]`，原 [targeted-1792168285935793100.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/evidence/targeted-1792168285935793100.json) 的失败保留。选定 [targeted-1792168592014078700.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/evidence/targeted-1792168592014078700.json) 中 namespace 32 项检查通过：硬链接不可建时，用同一自建源的两个独立实际打开 FD 调用 `fstat`，形成相同物理身份并验证 `INPUT_ALIAS` 拒绝。这项覆盖只证明已知相同 opened identity 的拒绝，不把它写成跨路径硬链接创建成功。`fstat` 自检也不替代 J FFM 或 Win32 ABI 验证。

祖先 reparse 位有受控注入检查。实际 symlink 创建受权限限制，选定回执在 limitations 中保留 `OS_SYMLINK_CREATION_NOT_AVAILABLE:OSError`；没有实际 symlink 创建成功的证据，不能据注入结果宣称实际 symlink/junction 全覆盖。所有祖先检查与实际 open 之间仍存在 TOCTOU 窗口；CREATE_NEW 和 post-open identity 比较是后续必要门槛，当前实现没有原子锁定整个目录链。范围限本机受控命名空间，不声称抵御敌对祖先替换、已有可写映射、异常磁盘或 NAS 行为。

## A05：原 J 描述符身份桥

桥仅适用于固定 **Windows x64 / JetBrains JBR 21.0.10** 工具。启动参数限定为 `--enable-preview`、`--enable-native-access=ALL-UNNAMED`、`--add-opens=java.base/java.io=ALL-UNNAMED`，不开放全部模块，不下载替代运行时。J 强引用原 RandomAccessFile 和其 FileDescriptor，身份查询与 close 使用同一同步边界。FFM 借用反射取得的 `long FileDescriptor.handle`，以缓存的 `GetFileInformationByHandle` 查询 52B、align4 的 BY_HANDLE_FILE_INFORMATION，得到 opaque 物理身份、长度和 FILETIME。

查询不另 open、dup 或 close 借用 HANDLE，不读源字节、不 seek、不改变原 position；raw HANDLE 不离开 J、不进入 journal。原 `h+`/OPEN 回执直接带 metadata 和原 object/ticket，因此不新增身份 RPC 或控制 token。J 的每次原 OPEN 最多执行 66 次 `GetFileAttributesW` 祖先 metadata 查询及 1 次原 HANDLE 的 `GetFileInformationByHandle`；超深、属性不可得或 reparse 均在该操作内阻断。它们是明确列出的新增原操作内 metadata 副作用，不算媒体字节读取，也不隐去 native 调用成本。

owner 由会话上下文组合证明：HELLO 的 PID 核对原 Popen，借原 hProcess 核 creationTime，固定 Channel.owner，G 在 add_object 中登记该 owner，再将同一原私有 stdout 管道、相同 request id 的 OPEN object/ticket 绑定进去。11 字段字串没有 inline owner，不能脱离原 Channel、PF actors 与实例 witness 当独立可移植证明。请求带 HMAC；回执依靠原管道及 request id 绑定，回执自身没有额外 HMAC。这里不扩大为对敌对 helper 的独立签名证明。

缺 flags、字段不存在、字段类型不符、符号不可用或查询失败，都保留 `BLOCKED_VERSION_NOT_PROVEN`。已分配原对象仍留在 helper map 和 G 的原资源记录中，由原 ticket 清理；重复回执不重做身份查询，不回退 path 属性、历史 hash、重新开文件或换 owner。query 与 close 竞争的验证要求 close 等待查询结束，随后原 owning close 实际返回一次。

[java-bridge-1792168105652835000.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/evidence/java-bridge-1792168105652835000.json) 记录十个独立进程，plannedProcesses=completedProcesses=10、status=PASS、pending=null、noInFlight=true。检查包括 success、path-separation、query-failure、field-missing、field-type、symbol-missing、close-race、missing-native-access、missing-java-io-open 和 missing-preview。该 JSON 的 87 项断言单列于 driver 回归之外。缺 preview 时 JVM 启动拒绝并实际返回非零，是预期负例，不要求生成成功 OPEN 回执。

桥探针仅用新建 L.bin 4096B 与 C.bin 17B，共 4113B；nativeReads=nativeSeeks=0，各有效探针保持原对象一次实际 close。path-separation 用 17B decoy 的路径属性与已打开 4096B 对象证明分离，**未实施文件 rename/replace**，不能扩展成对任意替换竞争的完整保证。

## observer：批准阈值与固定基线

资源停止策略同时检查绝对量与原基线增量。G 的基线是原 G 进程 PF/n01 前的采样，不在 HELLO 后重置；J/R 的基线是各原 HELLO 实例，必须先于首源字节。身份由 role、PID、creationTime100ns 及原 HELLO owner 关联，PID 单独不能证明相同实例。G 创建时间捕获使用一个自有查询句柄；J/R 捕获借用原 Popen hProcess，不 open/dup/close 该借用句柄。helper 退出只按原 PID/owner 的实际 exit witness 退休，保留历史基线和峰值，不启动替代实例。

| 原进程 | 线程绝对 / 增量 | 句柄绝对 / 增量 | 工作集绝对 / 增量 | private 绝对 / 增量 |
|---|---:|---:|---:|---:|
| G | 16 / +12 | 256 / +64 | 256MiB / +128MiB | 256MiB / +128MiB |
| J | 64 / +32 | 512 / +128 | 768MiB / +256MiB | 768MiB / +256MiB |
| R | 64 / +32 | 512 / +128 | 512MiB / +256MiB | 512MiB / +256MiB |

采样间隔 1 秒，最多 201 周期，实际 gap≤2.5 秒；单次查询返回后检查 0.1 秒期限。查询耗时计入原行及整批 180 秒，不另补时间。采样值只能称 sampled peaks，不能称绝对内核峰；短尖峰和未返回 native 调用期间可能漏采。0.1 秒及外层 200 秒都是停止等待边界，不能强制打断 OS、伪造 native return、强杀 helper 或回收未知所有权。

observer 使用原两 worker native pool，由创建线程及安全、无应用锁等待点提交，不增加进程、线程、RPC 或 journal 事务；worker 不同步提交并等待自身 pool。一个查询未返回时保留原 Future/pending，不补发替代查询。每周期先取一个 thread-only snapshot，最多枚举 16384 项，只保目标 PID 的线程计数并先关闭 snapshot；随后逐目标查询 process metadata 并关闭，所以同一时刻最多 1 个 observer 自有句柄。native 前必须先预留原 Ledger 的 1 个临时信用；24 个受管资源满额时拒绝查询，不能扩界。

缺指标、None、非有限值、负值、身份变化、绝对/增量阈值超限、gap 或周期额度耗尽均停止新接纳。close UNKNOWN 保留原句柄及信用，停止继续查询，不重试 close，不以 PENDING 推断 CLOSED。受控负例对这些状态和原 Future 的晚返回均有明确边界；接口 mock 所产生的 UNKNOWN 信用单独标注，不写成实际 OS 句柄泄漏或已释放证明。

已有 global.log 的 131072B 上限拆分并强制为 **events≤104320B、metrics≤26752B**。metrics 为头≤1024B 加最多 201 条、每条≤128B；原字节阈值先检查，再以毫秒及线程/句柄/WS KiB/private KiB 写 compact 行。两类额度独立计数，写入均经过 exact_write；短写会污染原 Store 并停止后续查询或写入，容量不足为 `BLOCKED_OBSERVER_LOG_CREDIT`。没有新增日志、目标、文件峰或时间额度。

选定 mock full 的最终 global.log 为 93462B，其中 events92902B、metrics560B（头及6行）。runtimeObservation 快照在 n32 前记录 eventBytes92828B，最后 n32 事件另占74B，仍计入原 events 上限；不能把快照数当作最终事件文件总量。

任何未来真实准入还必须现场新鲜检查 availablePhysical≥2,147,483,648B；`profiles/machine.json` 是继承的历史机器快照，不能沿用它、E2 旧快照或本次合成启动的瞬时值，不自动降低门槛。该检查只读机器 metadata，不扫描媒体。通过内存门槛也不能覆盖其他指标超限。

## mock 指标完整回归的含义

在上述真实 OS 门禁停止后，显式 `--synthetic-observer-mock` 仅替换指标读取器，以继续验证旧 61 分支协议和收尾语义。选定 [selfcheck-1792168565737747500.json](D:/CodexProjects/VideoKit/docs/coder/d1e2a/evidence/selfcheck-1792168565737747500.json) 为 62 行、159 项断言 PASS，原 J/R 均退出 0，剩余资源 0；原预算使用为 nonquery351、query83+18、输入请求1,573,492B/59、验证128B、10目标和32记录。数据与输出仍是自建非媒体文件；J 原 FD 桥、G guard、已分配 R reference、命名空间检查、真实文件 IO 和 close 没有换成指标 mock。

该回执明确 `mode=SYNTHETIC_OBSERVER_MOCK`、`mockMetricsUsed=true`、`scope=SYNTHETIC_POLICY_CHECK`、`runtimePolicyApproved=false` 和 `realExecutionApproved=false`。5 线程、100 句柄、32MiB 是制造的测试值，不能列为 OS 实测峰值或用于真实准入。真实 reader 在这次回归的 metric cycles=0，只作原身份捕获：identityQueries=3，其中 J/R 两次借用原 hProcess；自有 opened=closed=1、同时峰值1。真实身份捕获不把模拟指标变成真实测量。

选定定向回执为 844 项断言 PASS，与 full159 合计 driverSyntheticAssertions=1003；桥87项独立列示。完整回归 PASS、Java 桥 PASS、受控 observer 负例和实际 R519 阻断分别陈述、分别计数。实际失败、首轮 namespace 权限失败及修正前 mock full 失败记录继续封存，不以选定 PASS 覆盖它们，也不写“资源条件全部通过”。最终 mock full 的 fresh availablePhysical=2,730,434,560B 只是该次自检现场值，不是未来批次的授权或可复用准入结论。

## 输入、逐 case durability 与未改变的硬界

本批没有对 `test_media` 执行 stat、read、hash、复制或扫描；只读取已经存在的历史文档、输入配置与上游清单。L=3,212,959,911B、C=4096B、Z=0B，当前配置中的 stat 与历史 SHA 均为继承资料，不证明当前内容或当前 opened 对象。真实媒体 currentVersionGuarantee 仍为 UNPROVEN。

真实配置保持 B=2,147,483,648，四窗 offset 为 2,147,418,112、2,147,450,880、2,147,483,648 和 3,212,894,375。P01-N 每方原请求65536B；P01-S 保持原 cap1/短读与 reference4 的 UNFILLED 语义，不补读成整窗成功。31 个源分支 requiredDurability=NONE；30 个 Q 分支仅声明本机 `OS_DATA_SYNC_ACK` 字节及协议恢复 probe，不产生产品业务提交。

Q01-SEQ、Q05-STREAM、Q06-LOST、Q08-READY、Q07-READYFIRST 的产品 namespace/READY 变体继续逐项为 **NOT_RUN_DURABILITY_UNPROVEN**。工具 READY 不等于产品 OutputToken 或业务 COMMIT；namespaceRequired 或 NAMESPACE_DURABLE 不能降为 OS_DATA_SYNC_ACK。Q06 保持原 J 独立读 G 已 sync 日志、活 G 重载权威的受控本地恢复 probe，不声称真实 G 死亡重启、断电恢复或 namespace 持久化。P12 换版及短读、晚完成、ACK 丢失等注入不冒充真实媒体故障。

原 61 分支的控制452/硬544、query101、输入硬分配1,573,522B/59、10目标、32记录、输出655360B、验证262144B、元数据峰3,178,496B/硬4MiB、受管24/媒体6/8×64KiB槽、180秒及外层200秒仅停止等待规则均未扩张。副作用只在既有操作内列明，没有新增身份 RPC、控制 token 或 journal 事务。自建 fixture 累计≤2MiB，日志证据累计≤4MiB；旧失败和新负例均纳入封存，不能通过删除或压缩失败证据满足限制。

本包同时保留完整 `upstream-e2` 与 `upstream-e1e` 身份关系。上游 E2-source.zip 为739519B、SHA256 `4e3510c4cba3c99919faf26cf5ff72ab2ebe4ada2fcf7db3690fba4451b312c2`；只读包装校验覆盖旧 E2 的15项冻结文件、216项自检文件、43项源文件，旧 E1E 的188项冻结/自检记录、33项源文件及13项历史基线。核验对象是既有文档、源与证据，不重新运行旧包，也不打开真实媒体。

后续真实工作只有在新授权层、唯一批次/新根、现场原 opened-object 版本、共享、fresh 内存及实际 OS 资源门槛全部满足时才可考虑首字节；本次 R519>512 的结论仍是明确阻断。宿主 JNI 继续 BLOCKED，P0/C14 与历史 FAIL 保留，D1 未通过，M0 未启动；本批无 Gradle、ADB、设备或下载活动。
