# D1 E7 设备执行附录 V1.0

2026-10-17。本批coder未连接设备；下列是待独立复审后由负责人正式派发的计划，不是许可或已执行记录。所有正常/能力/cancel仍BLOCKED，不自动串行恢复。

仅原平板 HA1Q6WXR / user0 / App UID10221、test UID10222；独立核包外seal、源码ZIP、双APK hash/原证书、versionCode9/D1-E7。新只读入口编译在test APK中，若负责人正式派发，再由tester按保留数据的同签名 install-r 部署app/test；不得卸载/clear/降级/force-stop/删档/换budget。部署会更新应用包，故它也须纳入正式设备派发；当前未执行。

精确唯一方法 `com.videokit.spike.e4.E7WriterDeathDiagnosticTests#originalRecoveryWriterReadOnly`，runner `androidx.test.runner.AndroidJUnitRunner`，target test package `com.videokit.app.test`。参数 e7Case=originalRecoveryWriterReadOnly；e7Batch=D1-E7-WRITER-DIAG-TABLET-20261017；e7Scope=READ_ONLY_NO_ADMISSION。不选E4DeviceTests，不带e5aObservation，不运行任何@Before原观察，不增QUERY/ABORT/独立结算。

固定元数据 `files/e4a_output_budget/N2-e5-recovery/recovery.owner`，精确V1 owner tuple见架构文档；最多256B内容+1B超限哨兵。仅固定owner元数据和系统退出历史/proc，历史query一次max8；原FD在open前保留，NOFOLLOW/NONBLOCK/只读/逐级目录角色UID、文件dev/inode/大小/时间校验，实际close返回。新线程原owner最多等10秒，超时记录PENDING但不取消、重试或声称资源释放，立即停止批次保留现场。诊断metadata日志外部上限1MiB，不读取媒体源/失败导出/任何真实视频，不启动CPU/codec，不force/sync/改ledger/归档。

原稳定budget identity=730a73e1-50e1-4198-a515-047104f00e31、累计消费107218/reserved0与全部原产物按最后tester证据保留；tester可沿已批准只读元数据清单对账，不能读媒体体或新写恢复。原恢复batch D1-E5B-N2-RECOVERY-20261017不变，不重新使用旧执行许可。若UID、owner字节、身份、资源状态或任何记录不符，停止保留，不修改为预期值。

收集原instrumentation stdout/exitcode/精确单方法收据与结构化E7_READ_ONLY：history状态、limit、returned、matches、各reject计数、唯一匹配timestamp/reason/status、proc状态、ownerFdReturned、admission=NONE。不得将NOT_COLLECTED补0，不得把BLOCKED_CURRENT_GATE当产品失败已修复或把JUnit PASS当死亡证据通过。没有匹配时根因仍须按实际字段陈述；可见/proc未知都不能断言PID复用，缺历史也不能断言淘汰或重启。

本次诊断完成即归档交负责人，不启动normalAVI/能力/cancel，不重新跑已通过MP4，不以诊断Report替代下一host当前原观察。若结果提供足够新证据，也需独立复审新协议及精确设备计划后再派发；若仍缺启动代次/可信持久保证，继续设计阻塞。任何FAIL/PENDING/UNKNOWN不强制清理、不重试。

`tools/e7_package.py verify`为冻结包只读核验入口；`tools/run_gate_checks.py`默认INSPECT且冻结后拒绝测试写，`tools/build_local.ps1`默认INSPECT且冻结后拒绝构建。独立复现应从完整源码ZIP解至新目录，自备原已缓存SDK/JDK/依赖及签名环境，保持离线，不改冻结候选；ZIP不含设备/私钥/真实媒体/local.properties/build cache。
