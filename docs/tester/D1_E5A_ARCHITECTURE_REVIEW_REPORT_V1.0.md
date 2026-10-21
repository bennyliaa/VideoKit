# D1 E5A 整包架构独立复审报告 V1.0

日期：2026-10-17；tester。依据 `docs/milestones/D1_E5A_TESTER_REQUIREMENTS_V1.0.md`，审查 E5A 四文档、冻结源码、最终构建输入、双 APK 和已有验证证据。

**结论：REQUEST_CHANGES，新增 1 项 P1（E5A-F01）。** 原 E5-F01、E5-F02 的静态修复及相应既有模型记录已核验；新的最终观察路径却会创建缺失的原锁文件，不能作为完整的原状态证明。请集中修复后重新提交整包复审。本轮不准入最终观察及产品四项回归，不把静态修复记为设备问题关闭。

本轮未调用 ADB、安装、QUERY、ABORT、编码或真实媒体 stat/read/hash，未运行 Java、Gradle 或重跑模型。tester 只执行封存身份与既有记录的只读审计。原 N2 仍为 FAIL/PENDING，D1 NOT_PASSED、M0 NOT_STARTED，历史 P0/JNI/旧 signal FAIL 与 C14 待测状态不变。

## 1. 冻结身份与构建证据

| 项目 | 核验结果 |
| --- | --- |
| 候选根 | docs/coder/d1e5a；D1-20261017-E5A |
| 外 seal SHA256 | f2d7a6905eaf67c1979ae29c4e15ea9975417a15e3a421f4197b31288a70a841 |
| 源 ZIP | 19202352B；9c4b8bb12701e0de331e43075b9218037aa76e491acdaca1f5ce5c2ef3aef00e |
| 清单 | 2243 源文件、2247 不可变文件，集合/大小/SHA 与 ZIP 成员核验 PASS |
| 最终 build snapshot SHA256 | 10d7f7eb36b2c685620b2f214148d1bdc9ec4c0ff4b1b41bcd1402d1be8cb76d |
| 构建记录 | main-001、repair-001、repair-002 均离线 exit 0；最终采用 repair-002 |
| app APK | 10726780B；d490b9abcbc5f47074ff2e20e8163f26ab0c200b452a8c187524a6caf98eca33 |
| test APK | 2757370B；4b088c49ce864d029555c664208b60bb0a04fdaf19d095a7465b3a98b3ce324e |

两包已有签名审计通过，证书 SHA256 均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮核封存记录及 APK 身份，没有重跑签名工具。applicationId 为 com.videokit.app / com.videokit.app.test，versionCode 3 / D1-E5A，服务和权限边界继承。最终 APK 七个 native 条目与 E5 字节相同；依赖锁与 E5/E4A 相同，35 坐标差异 0。Media3 1.9.3、FFmpeg 8.0.3 的继承不关闭安全扫描、许可或发布 P0。

JVM repair-004 的失败和后续修订记录保留；repair-005 通过后补充绝对截止边界，最终依据 repair-006。不把不同轮次断言累计成最终成功数。

## 2. 新增 E5A-F01 / P1：最终观察创建缺失的原 guard 文件

位置：[E5AFinalObservation.java:62](/D:/CodexProjects/VideoKit/docs/coder/d1e5a/src/com/videokit/spike/e4/E5AFinalObservation.java:62)、[Android 适配器:37](/D:/CodexProjects/VideoKit/docs/coder/d1e5a/android/com/videokit/spike/e4/E5N2RecoveryAndroid.java:37)、[AndroidLease.java:34](/D:/CodexProjects/VideoKit/docs/coder/d1e5a/android/com/videokit/spike/c14/AndroidLease.java:34)。

观察阶段先对原 task 的 `.owner` 和 `.lease` 调用 lock，随后才运行 metadata 校验。Android lock 复用 `AndroidLease.exclusiveInto`，其打开参数为 `MODE_CREATE | MODE_READ_WRITE`。Android 官方定义明确：文件不存在时 MODE_CREATE 创建该文件。[ParcelFileDescriptor.MODE_CREATE](https://developer.android.com/reference/android/os/ParcelFileDescriptor#MODE_CREATE)

静态触发路径：其他 ABORT/S/归档/完成字节及 writer 死亡证明均合法，但原 `.owner` 已缺失。观察会新建一个 0B `.owner` 并取得新文件的锁。metadata 两轮均不校验 `.owner`，后续同步列表也不提供原 `.owner` 身份证明，因此该状态可以沿正常路径取得 FRESH_OBSERVATION_ADMITTED 和当前 host 的 live proof，继而允许正常 reserve。取得替代文件的锁无法证明原锁仍存在及其排他性。

原 `.lease` 缺失时同样先创建空文件，之后才因内容不符而失败。虽然该分支没有取得准入，它已经改变被观察状态，违反“只观察当前确定状态、不补文件、缺失即 BLOCKED”的要求。

**证据等级：生产源码调用链推导，未进行设备或模型复现。** 此处不需要假定恶意同 UID 攻击；缺失状态本身就应被拒绝。既有模型所有夹具均带原 `.owner/.lease`，未覆盖缺失 guard 的负例，不能用 270 项通过排除此路径。此问题独立于旧 E5-F01 的尾部关闭/同步窗口。

修复要求：为观察提供只打开既有文件的 guard 获取路径；缺失、符号链接或类型不符时拒绝且不创建。核对既有 `.owner` 的普通文件/0B 角色、`.lease` 的普通文件/36B/准确 fence，并将身份校验绑定实际打开的句柄；不能只增加前置 exists 后仍保留 MODE_CREATE。正常创建新任务的接口可继续独立承担创建职责。

补充有限验证：直接覆盖生产观察路径的缺失 owner、缺失 lease、错误角色及符号链接；断言没有新文件、没有新 R/S、没有 live grant，健康原文件仍可通过。提交修复源码、最终 APK/构建输入及新证据整包，tester 不通过删除设备原文件进行演示。

## 3. 原 E5-F01：跨 host 默认拒绝与真实返回资格

**静态修复及已有有限证据核验通过，设备闭环未执行。** 固定原 N2 budget 的 reserve 在检查 pending/R 前必须取得当前进程 live proof，即使完成标记存在、甚至恢复标记全部缺失，也不直接信任磁盘字节。非固定 identity 检出恢复痕迹时同样要求 proof；固定 budget/identity 不允许通过换 UUID 绕开。

recovery.owner 在恢复修改前记录实际 writer 的 PID/UID/main process、attempt 和开始时间；旧 close ACK 始终 false。恢复只有在所有持有者实际 force/close 和目录同步返回、移除 ACTIVE 后才发布进程内资格。晚失败保持该 host 的 UNKNOWN/retained；新 host 没有原进程 grant，完成文件完整可见也不能直接 reserve。reserve 先检查恢复/观察的 retained，旧 grant 不能绕开后来未返回的操作。

独立最终观察要求实际 writer 已死亡：Android 路径使用当前 ApplicationExitInfo 的准确 PID/UID/name、限定时间与唯一匹配，并核对 /proc ENOENT；PID 可见、复用或权限未知均拒绝。随后核对原 before images、原 journal/lease、唯一 S 和完整 ledger 链、anchor、归档与完成字段，要求无 operation.pending、reserved=0；对 14 个既有文件实际 force/close，做目录同步并复读，最后所有 guard 实际返回后才发布当前 host 资格。观察自身未返回或失败不会向下一 host 发放资格，也不升级旧 BLOCKED。

上述结构解决旧完成文件可见即跨 host 放行的窗口，但第 2 节缺失 guard 问题使最终观察整体仍需修改。每个独立正常 instrumentation 必须先按明确参数执行本次观察，外部 receipt SHA 只作关联字段，不能替代 live proof。单独观察进程退出后的许可不跨进程继承。

## 4. 原 E5-F02：统一收尾与首次取消截止

**静态修复及已有有限证据核验通过，设备闭环未执行。** E5ALifecycle 不再先完成失败 Future 再排队收尾；原 owner 返回和排队 continuation、CONTROL 返回及真实资源谓词共同决定终局。首次 cancelAt 只写一次，先安装绝对 30 秒截止，再通知平台取消；重复取消不重置截止。

产品 60 秒 watchdog、正负测试、取消、异常、await 超时、非 UI close 与 @After 全部走同一 terminal gate。外部 Future 是 dependent view，取消外部 Future 不会取消内部收尾。等待线程被中断时继续等待原终局，结束后恢复中断标志。

达到首次取消截止时仍未具备原 owner/资源真实返回资格，结果保持 ORIGINAL_CANCEL_DEADLINE_PENDING，保留原计数和 UNKNOWN；计时回调调度迟到也比较绝对时间，不能把截止后才返回的资源变为成功。终局已封存后，迟到关闭不能升级报告。READY/released 需要 ACTUAL_OWNERS_RETURNED 及 ownerReturnProven，不以系统结束 instrumentation、杀进程或单纯计数归零代替。

实际目录 barrier 在打开前登记 holder，FD 返回后先存入 slot，再进行类型/force 检查；Android 使用 O_NOFOLLOW、目录 fstat/fsync 和实际 close。既有握手、source gate、隔离 EOF、PTS、六帧及缩略图条件保留。本轮不将代码覆盖等同 Android Handler/Binder、codec 或真实目录持久化证明。

## 5. 既有 270 项证据的准确边界

最终计数为 core 89 + E5 main 48 + close-unknown 3 + durability-unknown 2 + E5A parent 128 = **270**。子进程内部断言不再叠加。旧 unknown 场景 retained=1 表示保守保留，不是系统资源释放证明。

八个 writer 场景为 healthy、completion force、completion close、completion close held、directory force、directory force held、directory close、directory close held。记录显示完成字节已真实可见；异常 writer 保持 BLOCKED/retained=1，held 场景保留真实 FileChannel 和 ACTIVE，在原调用未返回期间拒绝新 host reserve 及观察。释放原 held 调用后原 writer 可正常返回；writer 退出后，新 host reserve 仍先拒绝，仅本次明确观察并实际同步返回后才获得当前 host 资格。healthy 另覆盖只复制 anchor/ledger 时新 host 拒绝。

生命周期使用真实单线程 owner、FileChannel、CONTROL 与生产预算结算路径，但使用虚拟单调时钟推进 60/30 秒。覆盖初轮返回后迟到收尾、截止、计时回调迟到、CONTROL 阻塞、中断等待和外 Future 取消；UNKNOWN 后晚返回不升级，满足真实资格后只结算一次 S。

这些是已有本机有限记录，不是 Android 真机、真实 30 秒、Binder/codec、断电或目录 fsync 实测。观察自身每种 force/close 故障未逐项独立注入；尤其未覆盖第 2 节的缺失原 guard。tester 本轮只读取记录和核对源码，没有重跑模型或补写成功记录。

## 6. 后续准入与保全

原 N2 只读 QUERY 从静态上支持另行准确派发；QUERY_ELIGIBLE 不授权 ABORT、最终观察或正常编码。本报告未执行 QUERY，也不自动授权安装。

建议负责人先修复 E5A-F01，再提交完整冻结候选复审。复审通过后仍按单独正式任务顺序安排：原 N2 QUERY 采证、评审后的 ABORT_ORIGINAL_N2、独立当前状态最终观察，再按真实归还/预算状态决定正常四项回归。ABORT 路径本轮未发现同类新增缺口，但没有实际恢复证据，不能写成已通过。新 pending 不在原 N2 狭义恢复授权范围内。

原固定 budget `730a73e1-50e1-4198-a515-047104f00e31`、原 task `86cafdb3-0fc4-447d-920b-b19c884bf494`、原 epoch `5131975343750146374`、ledger R2MiB 无 S、operation.pending、原输出和失败证据均保持；不清理、不换账、不卸载。平板仍依据既有 E4A 安装身份记录，E5/E5A 未由 tester 部署；手机禁用状态不绕过、不另行请求连接。

独立审计：[identity-and-recorded-static-audit.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5A_EVIDENCE/identity-and-recorded-static-audit.json)。审计 PASS 表示封存身份及既有记录核验通过，不能覆盖本报告的 REQUEST_CHANGES。
