# D1 E4A 集中修复完整交付 V1.0

2026-10-17。候选 D1-20261017-E4A；依据负责人 [E4A 开发要求](D:/CodexProjects/VideoKit/docs/milestones/D1_E4A_CODER_REQUIREMENTS_V1.0.md)及 tester [E4 REQUEST_CHANGES](D:/CodexProjects/VideoKit/docs/tester/D1_E4_ARCHITECTURE_REVIEW_REPORT_V1.0.md)，集中实施 F01/P1、F02/P1、F03/P2，待独立复审。本机通过不等 Android 行为通过。**全部新设备/安装/ADB/codec/native fault/真实媒体/PF 均未执行；D1 NOT_PASSED、M0 NOT_STARTED、原全部 P0 保持。**

工程为 [d1e4a](D:/CodexProjects/VideoKit/docs/coder/d1e4a)，只一个 app 模块，applicationId com.videokit.app，Debug ARM64/API31+。旧 E4/C14 冻结、根 app/settings、原结果不修改。源码 ZIP 含完整 E4/C14 原源码容器及原来源证明；其中 C14 AndroidLease 原字节以 .java.orig 留存，运行时编入22个未改原类及一个同 JNI 类名的本地衍生 AndroidLease，新增 E4FencedTask 不替换旧 C14 文件。

## 三项集中修复

| 缺陷 | 实际实现 | 本机有限结果与保留限制 |
|---|---|---|
| F01 失败输出及累计预算 | [E4FencedTask.abortRetaining](D:/CodexProjects/VideoKit/docs/coder/d1e4a/src/com/videokit/spike/e4/E4FencedTask.java)分离持久 ABORT/epoch 围栏与产物保留；[E4OutputBudget](D:/CodexProjects/VideoKit/docs/coder/d1e4a/src/com/videokit/spike/e4/E4OutputBudget.java)提供固定私有目录、跨方法/host 的追加账本与 pending marker；[Sink](D:/CodexProjects/VideoKit/docs/coder/d1e4a/android/com/videokit/spike/e4/E4Session.java)在授 FD 前落完整原身份 | 真正写入自有7B部分输出→ABORT→实际关闭→原文件/长度/SHA仍在；两次实际1MiB+1B自有输出结算后即使删除其中一个独立dummy也不退款，后续预留被拒；独立新 JVM 读取同一账本、文件不存在仍见原11B消费。不是 Android host 重启/磁盘故障证明 |
| F02 初始化双失败原 owner | [E4Owned](D:/CodexProjects/VideoKit/docs/coder/d1e4a/src/com/videokit/spike/e4/E4Owned.java)先登记 holder，再 allocate/initialize；E4FencedTask 构造不 IO，Sink.task 赋值后 initialize；衍生 [AndroidLease.exclusiveInto](D:/CodexProjects/VideoKit/docs/coder/d1e4a/android/com/videokit/spike/c14/AndroidLease.java)先将 guard 交给原 holder，再 open/acquire；fence 用原 FD 的 pwrite/fsync，不另开未登记 dup | 自有小文件实际 owner，加假 acquire/directory-sync/close 失败；close 成功、屏障内未返回、异常分别验证 CLOSED/CLOSING/UNKNOWN。原 guard、RandomAccessFile/FD、路径、初始化异常与 cleanup 异常保持可达；异常 close 不重试，不靠 GC 归还。没有运行 Android PFD/native fault |
| F03 CONTROL 末次返回观察 | [E4ReturnGate.runAdmitted](D:/CodexProjects/VideoKit/docs/coder/d1e4a/src/com/videokit/spike/e4/E4ReturnGate.java)供真实 CONTROL 线程使用，实际 finally 才扣数；owner-finally 或最后 CONTROL-finally 竞争唯一 finish；资源确认后完成预算结算、归还许可。query 只观察/释放已证逻辑许可，不做文件 IO | 实际线程与双屏障验证 owner 已返回但 CONTROL 在途仍 PENDING；CONTROL 真返回后唯一 finish 可领取，不能提前扣数/重复发布。设备取消用例在原30s截止内 query 同一 Session，包括预算结算在途窗口，不只取一次旧不可变报告；未知不延时重跑 |

## 产物与集中本机证据

本批 JVM 保留一个 MAIN 65项，以及一次必要元数据持有补强后的 REPAIR，最终每次为一次 javac、一次主要检查 JVM、一次独立恢复 JVM，**66+2=68 项断言 PASS**；不将前后断言相加。使用生产 E4Owned/E4FencedTask/E4OutputBudget/E4ReturnGate，不重跑旧 E4 的89条。原命令、日志、源码身份及自有文件留在 [local-check-results.json](D:/CodexProjects/VideoKit/docs/coder/d1e4a/evidence/local-check-results.json) 和 evidence/jvm-attempts/main-001。少量故意 UNKNOWN 的自有 owner 强保留到检查 JVM 退出；JVM 退出的 OS 清理不记成协议归还。

Android 保留一个 MAIN offline 成功构建（07:55:52—07:56:36）及一次必要元数据holder补强后的 REPAIR成功构建（08:00:06—08:00:23），均未下载。旧主构建双APK/审计/三个确切旧源码版本与源快照保留；最终交付只采用 repair-001。44个最终源码/manifest/Gradle输入由 final-build-inputs.json 绑定。构建日志和原退出码见 [build-results.json](D:/CodexProjects/VideoKit/docs/coder/d1e4a/evidence/build-results.json)。各自不同主/修复产物的签名/manifest/native只读审计均通过，旧审计单列，不对同一产物重复求PASS，不安装或启动 APK。

| 产物 | 大小 B | SHA256 |
|---|---:|---|
| app-debug.apk | 10597168 | e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f |
| app-debug-androidTest.apk | 2712637 | 1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be |

最终两 APK 位于 docs/coder/d1e4a/artifacts/D1-20261017-E4A/final，v2 签名 PASS，证书均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，私钥不交付。测试 APK 是 instrumentation，非媒体 companion。

实际 manifest 仅两个 exported=false service：ordinary isolated :d1_cpu_worker 和同 UID、非 isolated :e4_codec。唯一应用权限 ACCESS_NETWORK_STATE，无 INTERNET 或 companion 查询/绑定权限。普通权限允许 host/codec 查网络状态，CPU isolated 不继承应用权限；不称零网络权限。

SBOM 35个实际 Maven 坐标；相比原 E4，新增/删除坐标与配置差异均0。相比较大的 C14 图仍有14个 GA 所选版本集合差异，新增 GA=0。Media3 1.9.3、FFmpeg8.0.3及实物7库逐字节不变，没有新 JNI/native 编译或依赖下载；host 新账本仍会走 Java 文件、FileChannel lock、fsync 等平台 native。SBOM/NOTICE/来源完整不等 SCA、许可、专利或商店发行通过。

## 预算、身份与 UNKNOWN

固定 app-private e4a_output_budget，与 e4Batch/方法/host 实例无关；外部审定的 e4BudgetIdentity UUID 必须匹配原 anchor，换 UUID/批次不重置。每输出 R 先持久预留2MiB，已结算的实际字节消费只增不减；准入检查累计消费+未决预留≤4MiB且无其他未决任务。只有原 fully-drained Session 能 S 结算实际长度/SHA/READY或ABORTED并取消未用预留，不能由恢复 host 猜账。实际消费单调不减，预留与消费不混称同一数值。

operation.pending 在初始化/FD分配前 CREATE_NEW 并目录同步；任何初始化、持久化、close、原资源/CONTROL未知都保留它，跨 host 拒绝准入。仅原实际关闭并完成同步结算后删除 marker。保留128输出记录/256追加事件、账本≤128KiB、anchor36B、pending0B；输出目录128文件且 identity/journal等元数据另限128KiB，数据总4MiB、单个2MiB。不是靠剩余文件长度推算累计；删除输出不改变账本，删除 ledger 但 anchor 仍在保守拒绝。产品不提供 reset/reconcile API；协作协议不防同 UID 攻陷后任意篡改或人为清全部 app 数据，不宣称掉电绝对安全。

每输出 UUID 与原 Session.task32hex直接对应，授FD前的 .identity 文件持久记录 batch、预算UUID、task/epoch/generation/service instance/UID及输出UUID。已关闭结算产物保实际长度/hash；未证者报告 length=-1、sha=UNKNOWN，R 保完整预留，不删除部分文件。即使长度/hash已读出而账本持久化未知，也不归还许可。

本批六帧/queue2/consumer1/CPU2/encoder1、12s四提案及60s正常计划不扩；可达16份RGBA2359296B+YUV55296B不等全RSS。正常21 QUERY/取消101 QUERY/50ms为名义窗口，不能中断不返回的同步 native/Binder。新增末尾预算结算每输出至多再读2MiB，合计输出摘要最多3次/6MiB；不是实际已用流量。两fixture前后hash若原8项各执行一次计划读取1477098536B，另加CPU请求；真实源本机从未访问。

## 完整冻结与下一步

四文档与完整源码、原容器/来源、双APK、签名、SBOM、JVM/构建/设备计划由 source-manifest/e4a-freeze 绑定。最终 freeze/源码 ZIP hash在外部完整交付报告中，避免循环自绑定。只读 verify_e4.py 需 -X utf8 -B 和外部 --expected-freeze；不调用 Gradle、设备、媒体或消费许可。ZIP精确成员、直接来源哈希、原E4/C14容器和最终编译源绑定均检查，历史容器不递归展开。

同 UID codec 仍只提供待实测崩溃边界，不是权限/RCE隔离。host lease JNI/J06、其余 J01–J11、原§29/所有P0仍未闭合，详见[架构](D:/CodexProjects/VideoKit/docs/coder/D1_E4A_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md)及[剩余门禁](D:/CodexProjects/VideoKit/docs/coder/D1_E4A_REMAINING_GATE_REVIEW_V1.0.md)。C14 73项待设备+两项 unchanged signal NOT_RUN、旧 self system signal0 FAIL/ordinary UNKNOWN不改。iOS/macOS/Windows只设计，Flutter/正式独立Kit/AAR未完成。

完整封存无在途后一次主动交负责人；由负责人整包交 tester 复审，再另派合法有限设备批次。八项计划全部 NOT_RUN；三quarantine是分别可选的最后分支，首个未知后持续阻止余下分支，不能换host/预算标识/目录或清数据求下一项。见[设备附录](D:/CodexProjects/VideoKit/docs/coder/D1_E4A_DEVICE_EXECUTION_APPENDIX_V1.0.md)。
