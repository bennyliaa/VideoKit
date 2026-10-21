# D1 E9 整包独立静态复审报告 V1.0

2026-10-18；tester；依据 `docs/milestones/D1_E9_TESTER_REQUIREMENTS_V1.0.md`。复用前段已完成的源码审阅，补齐实际 PC 管理器、Android 原 holder、部署端及证据链核验。本报告不是原 N2 ABORT 报告的重复交付。

**结论：冻结完整性 PASS；整包实现复审 NEEDS_FIX / NOT_SUPPORTED_FOR_DEVICE_MIGRATION。共 2 项 P1、2 项 P2，建议集中修复后整包复审。** PREPARE 固定拒绝产品激活、外部 registry/canonical catalog 的主要权限链和原资源返回门有实际实现，不能因本地自检通过忽略 PC 管理链路缺陷。未发现本轮 PREPARE 已获得产品执行许可的证据。

本轮 tester 仅执行自编元数据核验和静态阅读：设备/ADB、安装、构建、候选自检重跑、真实媒体、迁移、ABORT、approval token、实际 H_actor/catalog 和 activation 均为 0 或 NOT_CREATED。未改动 coder 冻结文件。D1 NOT_PASSED、M0 NOT_STARTED；E6B-OBS-F01 长期准入 OPEN，其他框架/许可/P0 和历史 FAIL 保持。

## 1. 冻结身份和构建交付

独立审计保存于 [independent-metadata-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E9_EVIDENCE/independent-metadata-audit.json)。脚本只读取并解析文件、ZIP、ELF 和已有日志，没有运行候选程序。

| 对象 | 独立核验结果 |
| --- | --- |
| E9 seal | SHA256 `6cd4844610a8ed6df9f15a9809740dcf37d5b2d5c4597701388e792852830131`；1045 项 immutable 全部匹配 |
| source-manifest / ZIP | manifest 1043 项逐项匹配；ZIP 1044 项文件，含 source-manifest；seal 的 sourceFiles=1044 与此口径相符；无缺失或摘要错误 |
| ZIP | 24596860B；SHA256 `d350f9335ef08e16a4137c739c7920b13a0a41efa19d465e8acdd5abac432976` |
| app version11 PREPARE | 10643010B；SHA256 `4c09d1abed854555f16e277dbcda605c37c47c11cb4d55b9712676cc5bc6a287` |
| androidTest | 2749765B；SHA256 `9f693e30babead370ff2f632242b4ebc033de58b867b3e2e6887ec5776ca3ca8` |
| 最终构建输入 | SHA256 `8f3ebeadcc73cbbcc297dbfcb5d86fec1c698cd8512443c382f5df377c40003d`；163 项匹配 |
| 签名 | 两份已归档签名校验日志与 APK audit 记录一致，证书 SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮未重新运行签名工具 |
| 历史冻结 | E7A seal `1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76` / 200 项；E8A seal `dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86` / 42 项均匹配 |
| 原生与依赖 | APK 内 7 个 ARM64 so 的内容摘要匹配，ELF LOAD alignment 均满足 16KiB；7 个上游 native 与 E7A 逐字节相同，35 个 Maven 坐标差集为空；118 项严格逻辑继承输入及14项 native 基线输入核验匹配 |

主双 APK 构建 `main-001` 原日志确实因 SDK 不公开 `OsConstants.O_DIRECTORY` 编译失败；`repair-001` 移除该不可用 flag，保留 lstat/fstat 目录角色检查，最终日志 `BUILD SUCCESSFUL in 29s`。失败前输入/源码、必要修复及两个原始日志均保留。这是一次主构建加一次必要修复，不能描述为首次构建即成功。没有原生重编译或新增依赖/许可结论；Flutter、独立 Kit 和全部既定框架要求没有因本报告被豁免。

## 2. 已确认的实际实现

### 2.1 共享 phase、原操作与 Android 返回

`E9Record` 严格检查 canonical JSON、键集合、重复键、字段编码、尺寸及 hash。app/PC 共用 `E9Actor/E9Evidence/E9Catalog`，不是只放在测试目录的状态模型。

`E9MigrationRun` 构造时开始 identity 资格钟；接受绑定时先保留 execute 和独立资格钟，再启动 worker。队列尚未执行且 FD=0 不能当已返回。两 phase 各10秒；到界、原资源 UNKNOWN、中断或控制异常进入永久 PENDING，晚返仅提供非合格收尾资格。`actualSafe()` 同时检查原 identity 与已预留 execute 的完成/实际返回；ACK 要求原 handle/commandSeq/stateSeq 和已归档 return hash，finish 仅领取一次。没有以重新取得锁代替原 holder 归还。

`E9OwnedFiles` 在平台 open 前登记原可变 handle；数据 holder 先关，只有全部数据返回后才释放 guards；UNKNOWN 不重关成成功。`E9AndroidFiles` 实际保存 raw FD、PFD duplicate、stream、ledger FileLock、directory stream 及分配/关闭尝试状态。ledger 用 duplicate 的 FileChannel 排他锁，读/force 使用持有的原 raw FD；没有在锁内另开另关同一 ledger 的读 FD。关闭依次处理 unlock、stream/duplicate、raw，分配结果不明与 close 异常均抛出并阻断实际返回。目录 LIST 保留 `/proc/self/fd/<dup>` 的锚定 FD。Android raw/dup 与目录 barrier 的真实平台失败仍为 NOT_RUN，不能从 Java 替身扩大结论。

静态调用数核对：commit 的正常新建最宽路径为2个 guard、13个历史文件、1个0B输出、1个 ledger、最多3个创建目录同步、3个目录枚举、3个新控制文件、3个控制目录同步、3个收尾同步，共32个文件/guard holder；actor2 既有内容核验至多增加3次读取，而目录新建同步不会更多。identity 路径上限8个单独 holder，合计保守上界43，低于48；当前观察最多30个文件/guard holder。未知路径不自动重试，不能借失败累计扩大48界。本地断言只证明已覆盖调用路径，不是设备运行计数。

Android 自定义 `E9MigrationInstrumentation` 在 onStart 后受管运行，DUMP 权限接收控制、拒绝 FD extras 和错误键；真实 return hash 归档 ACK 之后才排队调用唯一 `super.finish`。日志 finish anchor、独立 PID 缺席和正常系统结束记录由 PC registry 再核。仅 `finishClaimed` 或磁盘 commit 不足以 final。PC 端仍有第3节缺陷，故不能宣布完整链路已通过。

### 2.2 外部 authority、恢复与部署

受信 PC 配置 pin 精确绑定 plan、授权/评审引用、registry/migration、PREPARE APK pair、证书、版本与 environment。设备侧不是靠自报 APK hash 获得 external authority；精确 pair 由可信部署管理端检查。此结论限协作故障模型，不声称阻止同 UID 恶意程序或人为绕过部署门。

registry 先落盘 descriptor/授权/prepare-plan，身份返回后 BOUND reserve，之后才允许 commit。returned、正常 finish 或确切终止处分、事件链、checkpoint/seal、catalog、未来 activation APK 与外置 release 的顺序没有要求未来 APK 对自身摘要签名的环。`openKnownHead` 校验授权与链及对应证据；有活 actor、错 head 或无终局 authority 不能靠重启管理器续写。actor2 只接受原 actor 真实晚返+正常 finish 或确切 OS 终止处分，再取新身份、新资源和新返回；旧 UNKNOWN/无 Java return 不被填造成 close。actor2 再未知时没有 actor3。

`E9HostDeployment/E9DeploymentGate` 有真实 PC dispatch port，候选完整 pair SHA、角色/ABI、签名、原已装精确 pair/UID/版本、无相关进程与安装后 pair 共同构成门；dispatch 前重新核本次候选字节，只允许固定平板的 app/test 两条 install-r。D05 的检查后替换旧候选漏洞已在本批 host-only repair 修复，原失败输入/日志保留。无参数 CLI 只 inspect；合成 environment 无法导出真实 release policy。后续 activation 使用同一 registry/catalog/gate，但本轮没有真实发布材料。

`E9CurrentObservation` 实际持有原两把 guard、核当前历史文件和账本、无 active pending、控制清单及 catalog 绑定字节，force/readback/目录同步/本 host 实际 close 返回后授 live proof。它不再查询旧 writer PID4869 的易失历史。第3节 F04 是此边界的独立缺陷，不能因主要路径正确而省略。

PREPARE 编译常量 ROLE=PREPARE、CATALOG_SHA/BASE64=ABSENT；E4Session、CpuTaskClient、E4CpuAdapter、预算/任务与旧恢复入口在进入相关平台操作前拒绝。六个最终 Gradle 编译 Android 公共入口的已执行检查使用 SDK 桩；Binder/service 事务只完成源码/DEX 静态核查，没有实机调用。

## 3. 集中缺陷

以下为静态控制流确认，不冒称新增运行复现；既有32组未覆盖相应完整 PC 路径或后置断言。

### E9-F01 / P1：实际 launch 回到等待式 instrumentation，偏离已评审的非等待管理路径

位置：[E9HostManager.java:42](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9HostManager.java:42)，`launch()` 构造 `am instrument -w -r`；Android `publish()` 的完整 actor/returned transport 由 sendStatus 输出，Log.i 只有 snapshot。

E8A 迁移计划第52行明确采用 E7A 非等待 instrumentation/有限 STATUS/归档 ACK 路径。现在 PC 反而依赖长驻等待命令的 stdout 取得首帧，`finishCapture()` 又以这个命令退出为条件；交付未申明并评审这种管理关系变化，也没有对应 Android 证据。该差异使新的受管执行仍绑定等待式连接，不能直接继承 E7A 已验证的管理路径资格。**本轮没有证明等待连接实际导致设备进程结束或资源丢失，相关行为 NOT_RUN。**

修复要求：落实非等待启动及可用的、权限和身份绑定的首次 identity/return 状态取得方式；同时调整正常 finish 的独立证据，不把删掉 `-w` 后空 stdout 当成功。若要改变设计，必须明确设计差异和失联语义并先独立评审。当前不批准直接做真实写迁移。

### E9-F02 / P1：reader 结束不等于原进程归还，EOF 路径可丢失原管理者

位置：[E9HostManager.java:21](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9HostManager.java:21)、[E9HostManager.java:79](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9HostManager.java:79) 及 [E9HostDeployment.java:18](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9HostDeployment.java:18)。

静态见证：Managed 输出超1MiB、单行超界或 IO/close 失败 → reader catch/finally 退出且 `returned=false` → 原 Process 仍可能 alive → stdin EOF 只 `reader.join()`，因 reader 已结束立即返回 → main 正常离开。reader 是 daemon；代码没有在此继续等待/监督原 Process，也没有要求 output 真正返回。超长 console 行的 throw 还会跳过末尾保留逻辑。另一个路径是 Processes.run 超55秒将原子进程放在 retained 列表后抛错；未 launch Managed 时 main 的 EOF 分支完全不检查该列表。对象存在于即将结束的 JVM 中不能实现承诺的持续保留。

影响：未知原客户端/管道或仍在途原命令时，PC 管理会话可自行结束；无法按附录“PC进程及reader必须保持至原命令真实返回”证明完整管理生命周期。没有证据表明现有检查会伪造 final，但阻断真实迁移准入。不能把永久等待求 PASS 作为修复。

修复要求：所有出口，包括解析失败、启动失败、输出失败、超时和 EOF，都由统一原操作生命周期管理；未知时继续明确隔离/保留，而非只 join 已死 reader 或只存局部列表。补一次实际 PC 子进程/管道的有限故障验证，证明 reader 先结束而 child 仍活、命令超时、stdin EOF 时不会丢失管理者；不得以 kill/retry/假 close 收尾。没有必要为此先接 Android 或重复原生构建。

### E9-F03 / P2：控制回复沿用55秒通用命令等待，违反每响应5秒预算

位置：[E9HostManager.java:50](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9HostManager.java:50) 调用共享 `commands.run()`；[E9HostDeployment.java:21](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9HostDeployment.java:21) 固定 waitFor(55s)，之后还可 join(1s)。

E8A 第52行限定每控制响应5秒；实际 STATUS/EXECUTE_COMMIT/ACK_FINISH 广播未传独立期限。即使 Android phase 已在10秒后永久 PENDING，PC 控制调用仍可超5秒继续阻塞。8请求/STATUS3的计数门存在，不能代替时间门。

修复要求：控制命令采用独立5秒响应预算；到界登记未知并消耗已发请求，不重复 EXECUTE/ACK、不强杀原子进程，且与 F02 的原对象保留兼容。补受控延迟/不返回的 PC port 切点记录。安装与本地工具可有单独既定期限，不要求一律改成5秒。

### E9-F04 / P2：重复观察先返回 BLOCKED，旧成功 grant 却未失效

位置：[E9CurrentObservation.java:19](D:/CodexProjects/VideoKit/docs/coder/d1e9/src/com/videokit/spike/e4/E9CurrentObservation.java:19)、[E5AAdmission.java:14](D:/CodexProjects/VideoKit/docs/coder/d1e9/src/com/videokit/spike/e4/E5AAdmission.java:14)、[E9ProductionSelfCheck.java:255](D:/CodexProjects/VideoKit/docs/coder/d1e9/tools/E9ProductionSelfCheck.java:255)。

静态见证：同一个 observation 第一次成功，completed=true/failed=false、ACTIVE 已移除且 grant 指向它；第二次 observe 因 used=true 在 invalidateCurrent() 之前返回 BLOCKED。其 actualReturnProven() 仍 true，retained()=0，所以随后 requireCurrent() 仍通过。既有 A22 恰好调用第二次 observe 并断言 BLOCKED，却没有在第二次之后断言准入被拒；它不能证明失败会撤销旧 grant。

影响限未来 ACTIVATION/共享观察对象；当前 PREPARE 的 phase 拒绝仍有效。公共 E9Runtime 每次新建 observation，不能据此证明常见调用路径已绕过，但公开对象与“失败先失效旧grant”的实现承诺不一致。

修复要求：本次观察的所有拒绝出口都清除可沿用的当前 grant，或明确且一致地废止对应旧 proof；不能误把其他在途操作认作完成。补“成功→重复/提前拒绝→requireCurrent 拒绝”的真实生产对象断言，并保留 PREPARE 固定禁用的证据。

## 4. 32组本地证据的有效范围与缺口

`test-mapping.csv` 为 A01-A23/D01-D09 共32组，断言合计2027；最终映射36个 JVM 调用（A21含4个隔离子例），加2个 D05 targeted 调用，共38次记录；最终映射 exit 均0。输入快照 final-production-009/dispatch-fix-010/replacement-cut-011 各105项。前两次历史工具源码与当前路径不同，已分别匹配冻结的 before-dispatch/before-replacement 文本；是可追溯的历史修复，不是悄悄覆盖。最终 snapshot 全匹配。tester 未重跑这些调用。

| 组 | 已有证据支持 | 仍然 NOT_RUN / 不足范围 |
| --- | --- | --- |
| A01-A04 | 生产 identity/run/registry；身份异常、未BIND、reserve持久化失败、队列仍在途不能 finish | identity FD close UNKNOWN 专门切点、全部 Android 身份异常；F02完整 PC 管理路径 |
| A05-A06 | intent/payload/commit 的有限 open/write/force/read/close Exception/Error；不能 final | 全部目录 Error/永久阻塞、任意截断字节/掉电排列 |
| A07-A09 | 本地真实锁可重获但原 close latch 在途，10秒受控钟晚返仍 PENDING；close 已发生却 UNKNOWN 仍保留 | Android raw/dup/目录关闭与真实墙钟、内核故障 |
| A10-A13 | 错回执、伪 finish、存档失败、错误head/活actor重开和控制seq拒绝 | 原 PC Process/reader 超时/EOF/失联；F01-F03 |
| A14-A17 | PREPARE 拒绝合成 catalog；无终局不能 actor2；两种有限恢复保留旧 UNKNOWN | 实际 OS boot/PID复用、ActivityManager正常finish/原PID缺席均替身 |
| A18-A20 | 完整payload无commit可只补缺；0B torn commit隔离；无actor3、无环、合成catalog不能发布 | 全缺席/torn intent/全部长度矩阵；实际 PC 崩溃和 DEVICE H_actor/catalog |
| A21-A23 | 当前payload/pending/guard/ledger/close失败无grant；合法追加7B R/S受认可；只读关闭写入口后ACK | F04成功后重复拒绝的准入后置断言；Android UID/inode/dirsync和广播竞争 |
| D01-D04 | 新鲜编译冻结E7A真实旧reader确实忽略新marker；未知高version旧字节安装前拒绝，错phase/相关进程拒绝 | 旧reader平台死亡/guard/fsync为替身；未实际重签旧APK或重装 |
| D05-D06 | 生产 PC port + Commands 替身，检查后换旧候选 install0；固定双install-r和后检查拒绝 | 无真实 adb.exe/安装/实际base.apk或组件检查；F03未验证 |
| D07 | 六个最终 Android 公共入口使用 SDK 桩在平台前拒绝，205项输入匹配；共享phase/预算拒绝 | 真实 Android/Binder/service 调用 |
| D08-D09 | 未登记release/撤销文件不能当代码撤销；同head合成兼容release可过门，PREPARE仍拒绝 | 真实 activation APK/独立复核/安装均未发生 |

原始命令索引保留的 argv 是从执行脚本和 response files 重建的清单，不应另称为 shell 录屏；输入摘要、原 stdout/stderr/平台 trace 和映射共同界定证据范围。五个 host-surface 检查仅包含编译、两个默认 inspect、两个 synthetic release 拒绝；没有覆盖真实 approved-session 的管理生命周期。不能拿它们替代 F01-F03 验证。

## 5. 历史保全和下一准确准入

原 N2 task `86cafdb3-0fc4-447d-920b-b19c884bf494` 的一次 ABORTED_SETTLED/S0=0B 已完成；新 fence `662e9ecd-bede-42e6-bb58-ce81d668ff44`、原 guard 身份、原0B输出、同inode pending归档、前像和 proof 均不得删除或覆盖。budget `730a73e1-50e1-4198-a515-047104f00e31`，最近已接受 ledger 前缀1011B SHA `f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba`、107218B/三R三S/reserved0 保持历史事实。本轮未查询当前设备，不把历史数值冒充新实机观测。

实现校验固定前缀同时遍历完整合法链，允许后续合法R/S追加，不能永久强求整个账本仍1011B。单产物2MiB、总4MiB、128任务、严格六帧/完整EOF/1000us不变。旧 closeACK=false、旧N2无帧根因UNKNOWN、原MP4限定实机PASS、AVI/能力/cancel待完成都不因E9静态检查升级。

控制成本仍限设备4文件/8448B/3目录、PC20种元数据文件/155648B且≤192KiB、原日志1MiB、catalog实现16KiB（合同24KiB以内）、最多2actor、各8控制且STATUS≤3、两phase各10秒、48新owner；F03明确指出5秒响应界尚未满足。不能靠新增文件、第三actor、扩大旧框架配额或重置预算修复。

下一步应由负责人安排一次集中实现修复：先完成 F01-F03 的 PC 管理/时限协议及有限本机故障切点，再将 F04 观察失效修复和后置断言合并交付，重冻完整包。工具层修复不要求提前重编原生或重复全套自检；涉及 Android源的最终候选再按必要范围统一构建和核身份。tester 复审关闭缺陷之后，负责人才能派准确、有限的设备身份/控制批次；真实写迁移还需最终可审 scope、当前资格和有效授权，真实 final catalog 形成后 activation 是单独发布阶段。

本报告不生成任何许可、迁移UUID、actor identity、外部授权文件或最终 catalog，不请求用户重复平板使用授权，不自动进入后续测试。报告冻结后主动发送负责人并另存通知回执。
