# D1 E5 架构与原 N2 恢复独立复审报告 V1.0

日期：2026-10-17；tester。依据 `docs/milestones/D1_E5_TESTER_REQUIREMENTS_V1.0.md`，对完整冻结源码、四文档、最终APK/构建输入和已有本机证据集中静态审查。未ADB、安装、读取真实媒体、执行Java/Gradle、恢复、codec或fault。

**结论：REQUEST_CHANGES，2项P1静态阻断。** 主要握手修复和原N2狭义恢复方向成立，但完成凭据存在跨host放行窗口，正常失败又可能提前结束instrumentation而杀掉刚排队的主动收尾。写入式ABORT_ORIGINAL_N2与产品四项回归暂不准入。

**可先单独正式派发原N2只读QUERY采证。** 该动作只检查原metadata、两个实际退出记录和/proc ENOENT，不锁/fence/hash输出、不写S或移动marker，不经过两项阻断中的修改路径。QUERY_ELIGIBLE只代表查询前置成立，不准入ABORT或编码；安装更新和QUERY仍须负责人另行准确派发，本报告没有执行许可。若存在部分恢复痕迹或原字段不符，必须BLOCKED另审。

原N2实际根因仍UNKNOWN；N2 FAIL/PENDING/R2MiB、失败产物和fixture保持。D1 NOT_PASSED、M0 NOT_STARTED、全部P0/JNI/旧signal FAIL不关闭。

## 1. 冻结、产物和既有证据身份

| 项目 | 核验结果 |
| --- | --- |
| 候选/根 | D1-20261017-E5 / docs/coder/d1e5 |
| 外seal SHA256 | c80c6d32fcbef17fbbffbe5a369dd26cbca72f004ea08fe4d7765dbfc83e568a |
| ZIP | 18444352B，7e74d97e5cc3e28f62a289ce75b97dad3c30490086390851b89f5a2a99812026 |
| 清单/ZIP准确成员 | 448源/452不可变，大小/SHA/集合PASS |
| 包内只读verify | PASS，未启动候选、设备或构建 |
| tester独立审计 | PASS，逐清单、ZIP、最终build输入、既有日志/双APK/native/源码失败路径核验；不导入或重跑生产实现 |
| 最终build snapshot | 76abb4c497dc842a042ce5368abac44383bdb0333f1e99c1d6020bd04844ef51，与repair-004绑定 |

最终双APK：app10663736B/SHA `05d382960573399c6cba78302171f9c058ac9df599b63268d59a6ab3f21d00f8`；test2753602B/SHA `d93ad2de80ed7b523258cdb7005d97010f8d6950b43a6f9dade9e46f2dddbcc5`。已有v2签名审计PASS，两包证书均 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮核封存APK身份和原审计，不重跑签名工具或安装。

appId仍com.videokit.app，versionCode2/D1-E5；两个非导出服务维持普通isolated CPU和同UID :e4_codec。单app/原权限边界保持，不构成同UID权限/RCE沙箱。gradle.lockfile与E4A逐字节一致，35坐标差异0；独立比对最终APK内七native与E4A同名条目哈希全部相同。Media3 1.9.3/FFmpeg8.0.3继承不等漏洞、许可或发布通过。

原main/repair构建和JVM失败日志/输入沿革均封存。构建main-001/repair-001失败，repair-002/003/004通过，采用最后repair-004且全部offline；不将旧成功APK混作最终源码构建。原JVM模型main/repair-001失败也保留，不叠加断言求PASS。

## 2. E5-F01 / P1：完成凭据先可见，后续关闭/同步失败可被新host洗成准入

位置：[E5N2Recovery.java](/D:/CodexProjects/VideoKit/docs/coder/d1e5/src/com/videokit/spike/e4/E5N2Recovery.java:108)，结合 [E4OutputBudget.reserve](/D:/CodexProjects/VideoKit/docs/coder/d1e5/src/com/videokit/spike/e4/E4OutputBudget.java:88) 和writeNew的实际close路径。

原修改路径先完成S并关闭原ledger/lease/owner，然后归档operation.pending。接着 `writeNew(N2-e5-recovery.complete, COMPLETE)` 先把全部准确内容写入并force，再close，最后另做platform.sync(budget)。该阶段可能发生以下失败：完成文件force异常但内容已可见、完成文件close未正常返回，或最后目录fsync/目录FD close失败。

这些路径会返回BLOCKED并保留当前进程ACTIVE/poison，符合当前host拒绝要求；**但完成文件和归档marker已可能完整存在**，原operation.pending已不存在，ledger内S也已存在。新host没有原ACTIVE集合，reserve仅核archive存在、完成文件完整字节及归档marker0B；它既不能证明原完成FD close，也不能区分最后sync失败。条件相符时仍可追加新R/启动后续编码，把未完成恢复变成可用许可。

这是可由冻结源码直接推出的失败路径，不是已运行设备/JVM故障复现，也不是恶意同UID修改。它违反“部分执行不可新host洗许可”和“所有本次FD/锁实际关闭及持久边界齐全才完成”的要求。原旧host/codec已经死亡、输出0B或S已写入，均不能补造本次恢复最后资源/持久化的返回证据。

既有durability-unknown模型只在fence后首次sync失败，仍有原pending；缺completion文件反例也不能覆盖**completion内容已经完整可见**的窗口。需要集中修复持久阻断/跨host完成准入，使上述晚期失败在新host继续BLOCKED；不能仅信完成文件内容或依赖原进程内布尔值。新增有限反例应分别覆盖完成文件force/close、最后目录sync/close及新host重新reserve，保留原失败/原文件、不以OS退出清信用。修复方案不应无限递归添加自证文件，把最后一个文件close未知再次遗漏。

该项阻断写入式ABORT及其后产品准入；不阻断独立、无修改原文件的QUERY。

## 3. E5-F02 / P1：失败Future提前完成，instrumentation可杀掉待接续的原owner

位置：[E4Session.run](/D:/CodexProjects/VideoKit/docs/coder/d1e5/android/com/videokit/spike/e4/E4Session.java:168) 与 [E4DeviceTests.positive](/D:/CodexProjects/VideoKit/docs/coder/d1e5/app/src/androidTest/java/com/videokit/spike/e4/E4DeviceTests.java:90)。

初轮advanceCleanup(101)未证归还后，run先设置ownerFinished并 `result.complete(report())`，之后才将continueOriginalCleanup排进同owner队列。normal positive拿到这个PENDING报告即记录并assert READY失败，没有在原首次取消30秒截止内等待同一原Session的收尾。try-with-resources的close在ownerFinished=true时也不推动等待。

于是对于“初轮约5秒未完成、原调用稍后在30秒内返回”的路径，JUnit可以先结束；原N2系统实证已经表明finished inst会终止host/codec。即便continuation刚开始，它仍可能被这个生命周期结束打断，来不及形成最终ABORT/关闭/预算S，留下新pending。加90秒await外壳不能修复它，因为Future已经提前完成，并非等待超时。

这是源码及既有系统生命周期证据支持的缺口，未运行E5设备或时序模型复现。它不表示已出现假归还；问题是正常失败主动收尾在真实instrumentation流程中得不到所宣称的原剩余窗口。

修复应让失败终局/测试结束与同原owner的真实收尾或原首次30秒截止绑定，继续保首错和失败结果，不将失败改READY、不延长60/12/30秒，也不提前扣CONTROL/native/close在途。新增有限证据应覆盖初轮后迟到、但仍在原窗口内的原返回，以及窗口结束仍UNKNOWN两种路径；证明测试不会先结束并回收原host。仅测E5CallbackGate返回不等覆盖Android Session与JUnit生命周期。

该项阻断宣称失败主动收尾已完整修复及后续正常产品回归，不影响查询原N2静态metadata的路径。

## 4. 握手、ACK、阶段诊断的有效改进

host callback不再以flags==0判同步，而是拒FLAG_ONEWAY并保留Parcel上界/完整消费、UID/PID/task/epoch/generation/instance及显式ACK身份。Android12 AOSP BinderProxy在同步且AppOps采集启用时会附加FLAG_COLLECT_NOTED_APP_OPS，支持该修复依据；N2未记录原flags，不能据此认定它就是原机唯一根因。[AOSP Android12 BinderProxy源码](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/core/java/android/os/BinderProxy.java)

codec owner能力枚举/CREATE/CONFIGURE等阶段只写本地E5Trace，不再为诊断同步回调host。trace保首16/近48共64条、每条160字符、尾8条；query读快照，不在Binder/codec/文件调用期间持有trace锁。标准化codec候选、配置、公共错误与cleanup/首错分列，有界字段避免泄漏任意媒体路径或原异常文本。

STARTED callback只设置startedSignal，不立即放源。codec侧E5CallbackGate只有原线程实际finally returned(ack)才减少在途；ACK异常是已返回失败，未返回仍计在途；cancel/迟到ACK不恢复startProven。host同原身份QUERY必须看到原STARTED ACK返回、ownerOpenReturned、真实encoderStarted/sink opened、无callback失败/在途，才允许source.next；FRAME入口也核startProven/openReturned。能力四提案/12秒和原15秒STARTED等待未放宽。

六组仪器证据新增REPORT、HOST_DIAGNOSTICS、REMOTE_IDENTITY、REMOTE_CODEC、REMOTE_OWNERS、REMOTE_STAGE_TAIL；原详细Bundle取最近快照，记录flags/调用者、codec候选/硬软/颜色/配置/公共错误、open/callback enter-return、live/unknown/native/Image、原阶段/首错/cleanup。await异常也先保存同本地query。它能改善N2可观测性，仍需真机证明字段完整及实际分支，不能由编译或JVM代替。

正常仍须6源/6encoder输入/6样本、真实EOS/关闭、独立普通isolated CPU完整EOF/PTS/缩略图内容、源/worker实际死亡和slot、Sink/codec/Image/callback/CONTROL及输出预算归还才READY。没有用forwarded6或Fake绕过真实链路。

## 5. 狭义N2恢复的正确门和剩余边界

恢复固定task `86cafdb3-0fc4-447d-920b-b19c884bf494`、HEX、epoch5131975343750146374/gen1、service775a5ee9-fff3-4340-a03b-97751099c0c4、host24853/codec24873/UID10221、原稳定budget及N2 batch/lease/原R链；无任意PID、task、budget或caller-death布尔捷径。

QUERY有界读取identity225B、WRITING journal85B、lease36B、anchor36B、ledger≤128KiB；核owner/marker为0B regular、原输出regular≤2MiB但不读取内容。Android实际适配器核当前app UID/包名且无活动Session/slot；每PID最多8条ApplicationExitInfo，精确原UID/PID/name和1792208947872..1792208970000窗口各唯一匹配；两个/proc的lstat均须ENOENT，权限未知/可见复用/歧义一律拒绝。reason/status原样保留，原closeACK永远false，不补signal。

ABORT设计还要求原owner与worker lease真实排他flock、锁后完整重核、原ledger独占FileLock；保原四份metadata前像，fence旧lease，持久ABORT_PENDING/ABORTED并读回；读取保留输出≤2MiB、读FD实际close、按真实长度/SHA追加唯一S ABORTED/fsync/readback。原17B模型消费17B，完整证据下0B才可S0，不按空输出自动退款。ledger/lease/owner和所有已注册读写FD返回后才归档marker。这些前半门合理，但**不能抵销E5-F01晚期完成窗口**。

归档位于预算子目录，避免给正常纯文件output目录增加子目录；保原R、失败输出和before images，不删除marker，而是准确同目录原子改名。最多32恢复holder、16目录sync，原metadata两遍预算≤262908B，fence/journal回读121B、输出hash≤2MiB及有界ledger读/追加；无递归扫描、媒体操作或新UUID。各系统调用仍可能不按名义时限返回，不能超时假归还。

QUERY_ELIGIBLE不是实际排他锁或结算已证；实际记录在同签名保数据更新后是否仍可用、两/proc ENOENT和Android flock都未观察。QUERY若失败保存BLOCKED即可，不删原metadata或再次变体尝试。实际ABORT必须先修复、本次QUERY和原现场被独立审阅后另派，部分恢复痕迹只能另审，不自动续半事务。

## 6. 142项有限既有证据及未覆盖项

最终repair-004既有Core89＋E5 main48＋close-unknown3＋durability-unknown2=142，不将前次main/repair断言相加。原输入/日志/SHA和最终build snapshot匹配。两隔离JVM各保1原operation到解释器结束，未将OS退出计成归还。

覆盖同步非ONEWAY flags、错线程/重复返回、cancel不扣在途/迟到ACK不复活/ACK失败已返回、能力异常/close未知禁止fallback、缺死亡/锁忙拒绝、QUERY无fence、0/17B真实自有输出保留及S、重复恢复拒绝、正常后续reserve、缺completion拒绝。模型为Windows自有文件/范围FileLock/模拟死亡/目录sync，不是Android flock/Binder/codec/native执行。

其中durability-unknown在fence后首次sync就失败，未走完成文件晚期；现有反例只把完成文件移走，未模拟它内容已经可见但force/close/目录sync未知。也未验证Android仪器会为原cleanup continuation等满同一窗口。故142项PASS与两项静态阻断并不矛盾。本轮未增测/重跑模型、编译或故障注入；证据审计PASS仅表示冻结和记录一致。

## 7. 下一步准入和交付

| 动作 | 本次静态结论 |
| --- | --- |
| 保数据同签名部署E5并仅原N2 QUERY | 可由负责人单独限定派发；本轮未执行，原UID/budget及所有原产物须保持 |
| 原QUERY结果自动视作恢复完成 | 不允许；没有锁/fence/S/最终归还证明 |
| ABORT_ORIGINAL_N2 | BLOCKED，先修E5-F01并复审完整包；实际query另审后再派 |
| 正常MP4→AVI→能力→条件cancel | BLOCKED，先修E5-F01/F02及合法恢复独立验收；不换UUID或延时 |
| 三quarantine、旧Binder、手机/其他平台 | 不在下一选择表，不执行 |

四文档与device_plan将QUERY、独立审阅、另派ABORT、持久结算独立验收和四准确产品方法分开，方向正确；所有ACTION均须正式派发，不能用本报告推导设备/安装许可。仪器90秒外壳只保存诊断，不改变产品60秒/协商12秒/首次取消30秒。

复审证据 `docs/tester/D1_E5_EVIDENCE/identity-and-static-evidence-audit.json`、audit.py及本报告。两项发现均为静态路径推导，非设备复现。tester本轮ADB/媒体stat-read-hash/安装/Java/Gradle/fault均0，无生产在途或原现场改动。报告完成主动交负责人，请集中修复后再整包复审。D1未通过/M0未启动/原N2与全部历史FAIL保持。
