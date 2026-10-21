# D1 E7A 设备执行附录 V1.0

2026-10-17。以下仅待复审计划，需负责人新正式派发；coder本批设备/ADB/媒体读取0。禁止部署旧E7，禁止normalAVI/能力/cancel/恢复写。不得将本附录视为许可。

仅HA1Q6WXR/user0，原app UID10221/test10222。独立核外seal、ZIP、versionCode10/D1-E7A双APK hash/原证书，同签名保留数据install-r，仅在正式派发后执行；不卸载/clear/降级/force-stop/换预算/改旧档。必须先确认没有未归档在途旧instrumentation，不通过新启动杀掉旧任务。原稳定budget=730a73e1-50e1-4198-a515-047104f00e31，最后107218/reserved0，全部输出和原恢复batch保持，非当前新测值。

唯一component：com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation。不是JUnit class#method，不调用旧E7WriterDeathDiagnosticTests/E4DeviceTests。专用参数e7aCase=originalRecoveryWriterReadOnly，e7aBatch=D1-E7A-WRITER-DIAG-TABLET-20261017，e7aScope=READ_ONLY_MANAGED_NO_ADMISSION，e7aHandle=9f19bfb5-60e0-4bcc-9666-852409cfe3b4。该handle只对应本计划的一次派发，外部启动前保存其serial/user/组件/双APK身份/原PID_UID核对与证据路径；不复用已耗E3许可或旧作业handle。

启动用am instrument非等待模式，不带-w/-m/-f/proto/类选择/UiAutomation/性能profile，不把命令exit0当作业完成。无watcher时sendStatus可能无接收方，实际状态通过带DUMP发送资格的shell有序广播及E7A_READ_ONLY日志取得。固定action=com.videokit.app.E7A_DIAGNOSTIC_CONTROL、-p com.videokit.app、user0、handle精确；command只允许STATUS/STOP_DEPENDENCIES/ACK_FINISH。广播可用--receiver-foreground确保控制事件及时调度，不引入前台service。是否实际可达必须在新设备批次核证，不能借AOSP说明冒充实测。

外部有限控制计划：总请求最多6次，单次响应预算5秒、日志总1MiB，最多在启动后约1s和>=10s各取一次STATUS。10秒为设备单调诊断资格截止，不受主机钟误差或后续状态读取延长。若已RETURNED且originalOperationsReturned=true、safeToFinish=true、holder=EMPTY或CLOSED，先完整归档该snapshot和准确sequence，再用同handle+archivedSequence发送一次ACK_FINISH。没有任一条件不得发完成ACK；错误/过期ACK不会被接受。广播resultCode1不是close ACK或finish证据，须审safeToFinish/finishClaimed及此前真实原资源证据。

若截止仍在途或UNKNOWN，记录PENDING，有限发送一次STOP_DEPENDENCIES并取其结果；不结束、不取消、不重启instrumentation，不开启依赖。外部归档handle/PID/UID/组件/seq/phase/holder/截止/PENDING原始日志后交负责人，原受管instrumentation保持未finish。不能用主机命令超时/关闭窗口/退出进程当原close，不能无限轮询等PASS。若后续自然有新真实返回事件，负责人可另派同handle只读STATUS；安全归还已证才可归档新seq后ACK，以PENDING/非通过结束。close/allocate UNKNOWN没有自动修复或二次close接口，不承诺有限时刻能安全退出；外部须明确登记隔离处置，无法取证时不擅自杀进程。

如意外OS进程死亡/设备重启/外部force-stop/receiver不可达/通信丢失，记LOST_OWNER_UNKNOWN，不把内核回收当Java原close ACK；禁止新host恢复同handle、重放旧成功或重新读owner自动放行。由负责人审已有外部收据、真实死亡与资源证据后另行设计安全处置。外部“停止依赖”与“终止原进程”严格分开，后者不是本计划允许动作。

读取仅固定原recovery.owner元数据（最多257B哨兵）、system history一次max8及/proc；目录/文件UID角色/noFollow/dev+inode/精确原字节/前后属性及原close保持，无observe/force/sync/guard/ledger业务写、无source/export媒体/CPU/codec/grant。资格限内QUALIFIED_DIAGNOSTIC也仅表示收集完成，BLOCKED_CURRENT_GATE仍可出现；10s后PENDING永不改PASS。新结果归档后仍不串接normal/能力/cancel，长期持久准入仍需独立协议保证。

冻结包只读核验tools/e7a_package.py verify；本地run_lifecycle_checks.py默认INSPECT，冻结拒写；build_local.ps1默认INSPECT，冻结拒构建。独立复现解ZIP至新目录、自备既有缓存/SDK/JDK/签名环境并离线；不改变冻结包，不下载依赖或把本地替身结果当Android实测。
