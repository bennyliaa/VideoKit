# D1 E5B 原锁身份整包独立复审报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E5B_TESTER_REQUIREMENTS_V1.0.md`，集中审查四份 E5B 文档、完整冻结候选、最终构建输入/双 APK、已有定点证据及补验计划。

**结论：STATIC_SUPPORTED / VALIDATION_INCOMPLETE。新增源码阻断 0 项，未满足验证门 1 项（E5B-G01：真实文件符号链接反例 NOT_RUN）。** E5A-F01 的非创建打开与原句柄身份修复在静态及已有支持场景中成立，不能登记为全部验证关闭。允许负责人另行正式派发同签名保数据部署及原 N2 只读 QUERY；写入式 ABORT、最终观察和正常产品回归暂不准入。

本轮只执行 tester 自有只读审计；ADB、安装、QUERY/ABORT、设备观察、真实媒体 stat/read/hash、Java/Gradle/模型重跑均为 0。冻结包内日志属于开发既有记录。D1 NOT_PASSED、M0 NOT_STARTED、全部 P0/JNI、N2 FAIL/PENDING、旧 signal FAIL 与 C14 待测保持。

## 1. 冻结、来源、构建与 APK

| 项目 | 独立核验 |
| --- | --- |
| 候选根 | docs/coder/d1e5b；D1-20261017-E5B |
| 外 seal | 376268B；3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee |
| 源 ZIP | 18906785B；366417dd96f3c6a65824a845f7e7334cdeb96a1815a152288151824931cc1a33 |
| 成员 | 1557 源、1561 不可变；全部大小/SHA、ZIP 顺序/成员/字节 PASS |
| 最终 build 输入 | 8d9004bfd016ca1aed4340b67e2d020b03bebc4c58a3f93b99ac17d0cb4a091e；逐输入核验 PASS |
| 构建 | main-001，一次 offline exit 0，日志 BUILD SUCCESSFUL，绑定上述输入 |
| app APK | 10527157B；324247d61e0c6bab7e218cd859cd7b857572ce17a87e67e0cf941d5d3b60694a |
| test APK | 2718585B；63b5d31f74190d8be2e32870bce24ea0e88a3f665f4bb901a04e2e4fa6942708 |

既有签名日志与封存 APK 身份核验通过，证书均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。本轮没有重跑签名器。appId com.videokit.app / com.videokit.app.test，versionCode 4 / D1-E5B；普通 isolated CPU 服务及同 UID :e4_codec 两个非导出服务保持；权限为 ACCESS_NETWORK_STATE，没有 INTERNET 或 companion。

独立逐 APK native 字节比对：七项与 E5A 及对应 upstream 文件一致；依赖锁与 E5A/E4A 一致，35 Maven 坐标差异 0。Media3 1.9.3、FFmpeg 8.0.3 和对应源/NOTICE 继承不表示漏洞、许可或发布 P0 关闭。:e4_codec 仍不是同 UID 权限/RCE 沙箱。

来源变更集中在 guard、原任务/恢复/观察、账本打开和对应适配器/测试。开发封存的 E5A/E4A 外部核验仍是旧来源保全记录；tester 未借此重跑历史设备或模型。源码 ZIP 不含构建缓存/真实媒体，历史失败日志和 E5B main/repair 记录保留。

## 2. E5A-F01 修复：非创建打开及实际 FD 身份

[E5BGuard.existing](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/src/com/videokit/spike/e4/E5BGuard.java:20) 与 createNew 分离。原资源入口只调用 openExistingNoFollow；[Android 实现](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/android/com/videokit/spike/e4/E5BAndroidGuardIO.java:16) 使用 O_RDWR | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK，未包含 O_CREAT/O_TRUNC。缺失原文件没有补建回退。新任务创建独立使用 O_CREAT | O_EXCL | O_NOFOLLOW、0600；旧 MODE_CREATE / exclusiveInto 工厂已移除。

existing 在注册 holder 后先 lstat 核普通文件/UID/长度，再打开原 FD；fstat 与打开前路径及指定历史 dev/inode/UID 对比，取得锁前后复核实际句柄与当前路径。owner 必须 0B，lease 必须 36B，lease 从实际 FD 最多读 37B 并与准确 UUID 字节核对；fileId 与 fence 的使用也调用 verifyExisting。O_NONBLOCK 避免类型竞态造成 FIFO 打开无界等待，仍要求实际 FD 是普通文件。

raw FD 返回后立即存入 Descriptor，再登记 dup，dup 设置 FD_CLOEXEC；flock 在同一打开文件描述所派生的 dup 上进行，fstat 核 raw。关闭前对已取得的 guard 复核身份，逐实际 unlock、dup.close、raw.close 尝试一次；失败保留 UNKNOWN，不以重复关闭推断返回。尚未取得锁就拒绝的 initializer 正常关闭 FD 后可如实记返回，但观察/恢复失败不会因此授予 live proof。

[原 N2 恢复](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/src/com/videokit/spike/e4/E5N2Recovery.java:94) 取得两原锁、复核原状态，在 fence 前把实际两 FD 的 dev/inode/UID 写入 82B guard.identity，绑定原 task；追加 S 前及关闭前仍复核。观察先读该记录与 ABORTED journal 的当前 fence，再以记录身份打开原 owner/lease；[最终观察](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/src/com/videokit/spike/e4/E5AFinalObservation.java:63) 两轮 metadata 核 guard.identity 不变，结束前核实际 guards 并等待真实关闭。原 owner 同字节替代 inode 不再仅凭 0B 和新锁通过；缺记录的旧 E5A 半恢复不能补填。

新增 guard.identity 使观察 force 文件从 14 增至 15；输入与 holder 仍有界：record 82B、writer ≤256B、proof ≤2048B、ledger ≤128KiB、输出 hash ≤2MiB，恢复 holder ≤32、观察 ≤48，目录 barrier ≤16。没有递归设备扫描或无限重试。

## 3. 相关重开与账本路径

[E4FencedTask](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/src/com/videokit/spike/e4/E4FencedTask.java:38) 初始化 owner 与首次 issue lease 使用 createNew，捕获其身份；workerLeaseClear、READY、abortRetaining 改用 openExisting，绑定已捕获身份和 epoch。abort 在取得正确原 lease 前不会修改 ABORT_PENDING journal，缺 lease 时不补文件或 journal。

WorkerLease 继续接收已授权 PFD 并核 epoch，没有路径创建接口。Session transfer 为 READ_ONLY/WRITE_ONLY，没有 CREATE；本报告不把 transfer 当新增对恶意同 UID 进程的安全边界。

恢复和预算既有 ledger 改用 READ/WRITE/NOFOLLOW FileChannel，去除 RandomAccessFile("rw") 的隐式创建可能。只有全新预算初始化单独 CREATE_NEW；现有 anchor/ledger 任一缺失均不能按正常既有账户补建。原 R/S 格式、链、累计实际消费及实际 force/close 门保留。

## 4. 旧跨 host 与终局要求未回退

独立逐字节确认 E5AAdmission、E5ALifecycle、E5CallbackGate、E5ADirectoryBarrier 与 E5A 相同。固定 N2 budget 在新 host 默认拒绝，完成文件/磁盘 S 不自动提供许可；retained 恢复/观察优先阻断 reserve。只有实际恢复返回或本次独立最终观察返回才给当前进程 live proof；下一 host 必须重新明确观察。

原 writer 死亡与当前实际 force/close/目录同步的证明职责仍分开。观察要求真实 writer 死亡及当前确定结算状态，失败/未返回不升级旧 BLOCKED，也不向未来 host 洗成许可。原协议 closeACK 始终 false，系统杀进程不补 ACK。

首次 cancelAt/绝对 30 秒、原 owner continuation、CONTROL 与所有真实资源返回条件保持；外 Future 取消、await 中断、@After、失败/正负/取消路径仍共用终局门。回调派发迟到或真实返回越过首次截止，不能取得窗口内 ACTUAL_OWNERS_RETURNED，也不能将封存 UNKNOWN 改 READY。60 秒产品、12 秒协商、15 秒 STARTED 门不扩展。旧 270 项只引用，未重跑也未与本轮 82 相加。

## 5. 已有 82 项及 E5B-G01 验证缺口

repair-003 最终 82 项父检查日志和对应源码输入 SHA 一致，子进程断言不另累计。16 个观察场景为健康、missing owner/lease、两个目录角色、owner 1B、lease 0/35/37B、错误 36B fence、两个同字节替代 inode、两个 Junction、缺 guard.identity、替代身份记录。它们直接调用生产观察，实现侧包含逐原路径/角色/volume-fileID/字节清单不变、createCalls=0、拒绝项无 live grant，后续 reserve 拒绝且无新 R/S 的断言；tester 逐日志核结果。

另有生产恢复 missing owner/lease、正常两次创建后非创建重开、缺 lease 时 worker-clear/READY/abort 不补写、completion-close UNKNOWN 后新 host 拒绝及明确观察的对照、首次截止/迟到计时定点记录。健康观察确实打开两原 guards 并通过实际句柄身份校验后才允许新预算 reserve/finish。UNKNOWN producer 保持 BLOCKED，后续观察成功没有改写原 producer 结果。

**E5B-G01：真实文件 SymbolicLink 反例仍为 NOT_RUN_OS_PRIVILEGE_1314。** 普通与提升上下文均因 Windows 1314 无法创建，环境记录表明不是自动审批拒绝。两个 Junction 是实际重解析节点，但目标为目录，不能覆盖“链接指向准确原 inode/字节的普通文件”这一关键反例。支持场景 PASS 不能关闭此验证要求。

Windows 模型实际读取打开的 FileChannel 内核句柄 volume/fileIndex，并非只检查路径 exists；UID 是模型映射、锁是 Windows 范围锁、目录 FD 为普通自有文件替身。上述结果不证明 Android UID/fstat/flock、真实目录 fsync、Binder/codec 或断电行为。Android 公共 API 编译成功亦不能替代运行验证。本轮新增源码阻断 0，不表示全部竞态或系统失败路径已穷尽。

## 6. 缺证对准入的影响及补验方案

| 阶段 | 本次结论与条件 |
| --- | --- |
| 完整静态审查 | 源码修复获支持，验证未完成；E5A-F01 不登记整体关闭 |
| 同签名保数据部署及只读 QUERY | 可另行正式准确派发；该路径在 originals/death 核验后返回，不调用 existingGuard/fence/hash 输出/写 S/创建 guard.identity，因此文件符号链接 guard 反例缺证不阻断此狭义查询 |
| ABORT_ORIGINAL_N2 | 暂不准入；先补真实文件符号链接拒绝证据并独立评审，再依据实际 QUERY 证据另派 |
| 最终观察、正常 MP4/AVI/能力/取消 | 暂不准入；依赖上述验证、实际恢复结算及每次当前 host 的实际观察资格 |

可行补验一：在已有真实文件符号链接权限的本机上下文，另行派发精确 freeze 与一次 ExecutionId 的已封存脚本。它把夹具原 guard 移至相邻目标，再建立真正 SymbolicLink 指回原 inode；若错误跟随仍将见到相同身份/字节，因而比目录 Junction 更有判别力。需核 owner/lease 两 LinkType=SymbolicLink、生产观察均拒绝、无原字节/ID修改、无新 R/S/live grant、实际 FD 关闭和原日志。现有计划 `D1_E5B_TRUE_SYMLINK_ONCE_PLAN_V1.0.json` 的 ID `4a38729d-0275-4172-b853-1aa582dd2a4f` 仅保管未运行，本报告不激活、不复用、不自动提升或改系统设置。

可行补验二：后续另派隔离自有 Android 夹具，在唯一新目录内使用同一生产 Guard/观察与实际 Android lstat/fstat/open/flock/close，创建指回同一原夹具文件的真 symlink，另做健康对照。只能使用自有假 identity/ledger/output；原 N2 files/e4a_outputs、e4a_output_budget、真实 fixture/媒体均不得触碰。合成死亡/UID前提必须明确标为夹具，不可写成原 N2 恢复或实际 writer 证明。若当前冻结 APK 没有该专用入口，先交付冻结测试入口与有限执行计划复审，再执行；不能拿原 N2 ABORT 当补验夹具。成功后单独评审补验证据，不自动放行产品回归。

本次没有运行补验脚本、JVM、权限探测或 ADB；不能把上述方案计成已执行。缺证属于真实验证门，当前没有另一个已证实的新源码 P1。

## 7. 后续执行界限及证据保存

QUERY 只能精确选择 E5RecoveryDeviceTests#originalN2QueryOrAbort，e5N2Action=QUERY，固定原 task/budget 与 E5B recovery batch；不能运行整类或使用默认动作猜测授权。部署须保持 appId/原 UID/签名/数据，不卸载清数据。任何实际字段不符、退出证明不足或部分恢复痕迹均 BLOCKED 另审，QUERY_ELIGIBLE 不授权写恢复。

原 budget `730a73e1-50e1-4198-a515-047104f00e31`、task `86cafdb3-0fc4-447d-920b-b19c884bf494`、epoch `5131975343750146374`/gen1、service `775a5ee9-fff3-4340-a03b-97751099c0c4`、旧 host24853/codec24873 与原 R2MiB 无 S/pending/输出/失败报告保持。不清 marker、不换 UUID 或账户、不补旧 guard.identity、不重复 S，不以新目录绕过原待结算。

本轮没有更新设备状态记录；E5B 未由 tester 部署。手机禁用状态不绕过；平板连接不在本轮要求内。审计 PASS 只表示本包身份及已有记录核验成功。

独立证据：[identity-and-recorded-static-audit.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5B_EVIDENCE/identity-and-recorded-static-audit.json)。正式报告完成后主动通知负责人，并保存通知回执。
