# D1 E7 独立静态复审报告 V1.0

日期：2026-10-17。Tester。依据 `docs/milestones/D1_E7_TESTER_REQUIREMENTS_V1.0.md` 审查完整冻结 E7、四文档、来源和已有证据。本轮设备/ADB/安装/媒体及导出件读取/Gradle/native/模型重跑均0。

## 结论

**NOT_SUPPORTED_FOR_READ_ONLY_DEVICE_DISPATCH：发现 E7-F01/P1，原任务生命周期与 instrumentation 结束之间存在缺口，建议修复后冻结再审。** 已有生产死亡门的有界诊断和保守谓词得到支持；27场景/316断言只支持该纯生产 gate，不覆盖专用 Android 只读任务的超时/close 在途生命周期。

E6B-OBS-F01/P1 仍 OPEN；持久协议 DESIGN_BLOCKED/未实现，不作长期准入解决。原 MP4 限定实机 PASS 保留；AVI/能力/cancel 不准入，D1 NOT_PASSED/M0 NOT_STARTED。未部署 E7，也未重复观察或测试旧任务。

## E7-F01/P1：JUnit 可先于未返回的原 owner 结束

定位 `docs/coder/d1e7/app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java`：

- 第25行用进程内 static Job original 保持原任务引用。
- 第68行 `original.done.await(10,TimeUnit.SECONDS)` 超时后，第69～70行发送 PENDING 元数据，但第71行立即 `assertTrue(...,completed)` 失败，测试方法结束。
- 第72行在 Job.failure 非空时同样直接结束测试；若异常来自原 allocate/close 且 fd.state 为 UNKNOWN，尚无实际关闭返回证明。仅角色校验失败且从未打开资源的情况不属于此缺口。
- 方法没有在上述路径阻止 instrumentation 整体完成，也没有独立于该 instrumentation 进程生命周期的任务持有者。Java 强引用能防止进程内对象回收，不能保证目标进程在 runner 完成后仍存活。

这不是对 E7 超时的设备复现。本次证据由 E7 静态分支和同一平板/runner 的既有实际结束行为组成：`docs/tester/D1_E6B_NORMAL_EVIDENCE/normalAviSixRealFrames-logcat-stdout.txt:51` 记录 `Force stopping com.videokit.app ... finished inst`，紧接第52行 Killing11809。该既有日志 SHA256 `f32af4816cf0926594648d0fb85ad821d16e122c928580c63a10d4a41c3f8955`。因此当前单方法计划不能保证文档所称“10秒只停止等待、原 Job/owner 强保留”；自动的 runner 结束清理仍可能中断原 open/read/close/history 操作，丢失其最终返回证据。

本入口只读且未伪报 ownerFdReturned=true，此项不指控账本写入或死亡门放宽。问题是它明确要求的在途生命周期保证尚不成立，不能用“未主动 cancel/kill”或 static 引用代替实际保留，也不能将系统进程退出当成原 close ACK。

建议先修生命周期：10秒到期应永久记为本次 PENDING/不通过并停止依赖，同时保证未返回的原 owner/操作不会因该测试方法完成而被提前终止；原动作实际返回后才按真实结果归档，不能迟到返回改判10秒内成功。也可提出与 runner 生命周期隔离的、可验证且不增业务写入/权限的原任务持有方案。需有直接覆盖实际任务/结束边界的有限证据，包含 open/close 在途或失败、超时后不重开/不强关/不丢原 holder；不能仅补纯 gate 测试或延时求 PASS。新计划也必须与真实持有者生命周期一致。

## 生产死亡门与结构诊断

`E5N2RecoveryAndroid.requireRecoveryWriterDead` 实际委托新 `E7WriterDeathGate.inspect`，不是未使用 helper。原较早 N2 host/codec death、guard/fence/账本/观察与资源门保持；原 App/独立空闲 host 身份检查在调用前。

核对通过的边界：

1. history 调用一次，常量 LIMIT8，不重试、不扩大查询、不读取旧成功报告。查询前固定 now 作上限，比原逐行更新时间更保守；owner起始及now包含边界保持。
2. 先按 PID/realUID/process/timestamp 计所有身份时间匹配，再判断唯一性，之后判断 reason>0；两条匹配中一条 UNKNOWN 也不准入。唯一正 reason 后才查 proc，仅 ENOENT 映射 ABSENT，通过当前门；EXISTS/UNAVAILABLE/异常/null 都拒绝。
3. 诊断区分 NOT_REQUESTED/AVAILABLE/UNAVAILABLE/MALFORMED/OVER_BUDGET；未知计数为 NOT_COLLECTED，真实空列表才returned0/matches0。reject计数可重叠，reasonNonPositive仅数身份/时间匹配行；唯一匹配才输出timestamp/reason/status。无无关行身份或异常正文。
4. proc 不查和不可用分别表示，pidReuse/reboot始终NOT_PROVEN；Report不是Admission.Proof，grantNONE/persistentFactDISABLED。正常观察仍必须通过原完整链路，而非只通过死亡 gate。

实际 API 只保证最近有限记录的环形历史，不能由“缺记录”推出本次淘汰；UNKNOWN reason 的常量值为0。本次核对官方说明，仅用于评价协议约束，不补造旧 AVI 实际返回列表。[ActivityManager官方API](https://developer.android.com/reference/android/app/ActivityManager#getHistoricalProcessExitReasons(java.lang.String,int,int))、[ApplicationExitInfo官方API](https://developer.android.com/reference/android/app/ApplicationExitInfo#REASON_UNKNOWN)。

原 E6B AVI 仅知发生 WRITER_DEATH 未证，未到 proc；具体匹配数量/reason/淘汰/PID复用/重启仍UNKNOWN。E7新增诊断只能描述未来那次实际调用，不能回溯冒充旧调用事实。

## 已有有限证据与只读入口

核 `tools/E7WriterDeathGateSelfCheck.java`、local-check-results 输入大小/hash、两条原命令及 gate-compile-001/gate-run-001 日志：**27场景/316断言**，实际直接调用同一生产 gate，只替换 history/proc port；Tester未重跑。覆盖空/重复匹配、UNKNOWN及负reason、错PID/UID/process/起始前/未来时间、重叠拒绝、API异常/null/损坏/超8、proc EXISTS/UNAVAILABLE/异常/null、旧成功后新查询缺失仍拒绝、包含时间边界、now早于owner、未请求及八条边界。

不是 Android API/重启/PID复用/持久格式/专用 FD 在途实测。Android适配器和测试入口只有构建与静态集成证据；纯gate的316断言不能证明E7-F01生命周期。既有旧套件只继承，不累计成新执行数。

只读入口其他范围得到源码支持：独立类/单方法，不继承 E4DeviceTests.Before；固定 recovery.owner 元数据、精确V1 owner字节；逐级目录lstat/UID/角色，文件预检；O_RDONLY|O_NOFOLLOW|O_NONBLOCK，fstat角色/UID/大小/dev+inode，最大257字节哨兵拒超256，前后文件身份/大小/mtime/ctime比较。E4Owned在open前挂在原Job，成功路径实际fd.close返回后才输出ownerFdReturned；不调用observe/force/sync/settle/grant、不开媒体/CPU/codec/service，不写业务文件。读取可能有常规文件访问时间副作用，不宣称物理零写入。

在这些支持范围之外，超时/UNKNOWN失败分支按E7-F01保留问题，不把其文档承诺算成已验证事实。

## 持久协议与可行后续方向

同意本批明确停止在设计。原V1仅有attempt/PID/UID/process/墙钟began，缺少可验证的启动代次/boot绑定，且未给出超出同UID本地文件的完整性、防回滚与死亡证据信任根。旧成功日志或receipt SHA不能补写未采集代次；当前/proc缺席也不证明旧启动代次的完整历史。

E7没有持久格式/解析器/写入/迁移/fallback，损坏、重复、过期、在途、缺失记录均没有可授予准入的消费入口；这些是明确未实现，不登记为已执行负例通过。不要求开发为旧writer补造从未采集的boot/start数据。

可行后续须分开审定：未来新writer可在任何恢复写之前建立可验证启动代次及任务/fence/budget/guard绑定，再设计可信取证者、完整性/单调防回滚、提交与原owner实际force/close/目录屏障的原子边界；每新host仍真实核当前guard独占/fence/完整账本/文件/资源。旧V1迁移需要独立可信外部证据或正式安全处置/隔离方案，不能无授权重写旧档、清账或自动套V2。若取不到这些保证，继续设计阻塞是正确状态；只读诊断未必能解锁长期准入。

## 完整冻结与产物核验

独立静态核验 `docs/tester/D1_E7_EVIDENCE/audit.py` 及 `identity-and-recorded-static-audit.json`：身份/来源核验 PASS，与上方功能准入结论分开。

| 项目 | 核验结果 |
|---|---|
| 包外seal | b69200b6599144894382e46af0f9555407894f8ce8dd57fad5b71d96bcc63599 |
| 源码ZIP | 18507067B；SHA256596cc53c9b76727659c922a8d501aef06b82d8f82d448ccbba90f0cc33a82a9a；191个有序唯一成员逐项大小/hash一致 |
| 冻结与旧包 | E7共195项一致；旧E6B seal及191项不可变文件保持 |
| 最终输入/构建 | e35aadf762b21cd7ce3f77f847ae88e1468c86f2fa696213c28927518feaa62b；唯一main-001、offline/exit0/BUILD SUCCESSFUL，原记录约39.9秒；未重建 |
| version9 app | 10544590B，SHA256f709314107a44ab71a6036e4e17c61a4d7ba2f67429c00be35b95775822b805b |
| test | 2724977B，SHA25650437ade1e7eacf232da015dc88fc86aecd209d4cca68507a7e34540faed7567 |
| 签名/集成 | 原双签名核验记录通过，证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；app DEX含生产gate，test DEX含准确只读入口，本机selfcheck未入包 |
| native/依赖 | 七native与E6B APK/来源逐字节相同；源码/header/config保持；35 Maven坐标锁一致/delta空，FFmpeg8.0.3/Media3 1.9.3不变，无本批native重编 |
| 对齐/许可 | 独立解析七ELF PT_LOAD及APK内native偏移满足静态16KiB；不作设备16KiB实测；原NOTICE/对应源/框架许可与安全P0仍保留 |

精确变化为生产E5N2RecoveryAndroid、新gate、新只读test和版本/项目元数据；原guard/owner/观察/准入/输出预算、严格六帧/EOF/1000us/画面、每host资源和deadline代码保持字节。原107218消费/reserved0及产物沿最后设备报告，本轮不冒充实时重新测量。

## 准确计划与处理建议

已核计划仅HA1Q6WXR/user0、原UID10221/test10222，version9同签名保数据更新后唯一 `E7WriterDeathDiagnosticTests#originalRecoveryWriterReadOnly`；e7Case/e7Batch/e7Scope精确，max8/一次/257B/日志1MiB、无admission或媒体恢复写，无正常AVI/能力/cancel串接。

计划中的10秒PENDING后原任务保留承诺受E7-F01阻塞，**当前不建议正式派该候选只读设备诊断**。先修复该生命周期并冻结完整交付复审。后续即使诊断JUnit PASS，也只表示收集完成，BLOCKED_CURRENT_GATE并非死亡门通过，更不等于FRESH_OBSERVATION_ADMITTED。长期问题仍OPEN，诊断结束后仍需另行审定安全协议/迁移及正式派发。
