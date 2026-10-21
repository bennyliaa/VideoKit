# D1 E5 架构与威胁边界 V1.0

2026-10-17。本候选仅修 E4A Debug 原型。应用壳/独立 Kit/未来 Flutter 控制边界保持；RGBA 不跨 Dart，压缩媒体解析仍在普通 isolated CPU 服务，同 APK :e4_codec 同 UID 仅提供故障进程边界，不构成权限/RCE 沙箱。无新依赖，输出与源凭据仍分离。

## N2 已证事实与未证原因

原 task 86cafdb30fc4447d920bb19c884bf494、epoch 5131975343750146374/gen1、service 775a5ee9-fff3-4340-a03b-97751099c0c4、host24853/codec24873/UID10221。合法 MP4 BEGIN 后约15秒未证 STARTED，0帧、PENDING/E4_REMOTE_PENDING。R2MiB、operation.pending、WRITING、原0B输出保留。原 logcat 无足够 codec 阶段/崩溃堆栈；finished inst 后系统杀两进程是系统证据，不是原 close ACK。

源码检查发现独立成立的风险，未能从原日志确定哪个实际触发：

| 原行为 | E5 生产行为 | 验证范围 |
|---|---|---|
| flags!=0 拒绝 callback | 只拒绝 FLAG_ONEWAY，仍核完整 Parcel/原 UID/PID/task/epoch/gen/instance/ACK身份 | JVM 标志策略通过，实际 Binder 待测 |
| 枚举/CREATE/CONFIGURE 阶段同步 CODEC_EVENT | owner 写本地64条有界阶段，不做诊断 Binder 回调；QUERY 读取快照 | 生产源码/离线编译 |
| callback 内置 STARTED | startedSignal 单独保存；同原身份 QUERY 必须证明 STARTED 原同步 ACK 实际返回、open owner 返回、真实 encoder/sink 已启动，才开放 source | Gate JVM 通过，Android待测 |
| ACK 异常永久计作 callbackUnknown | 原 Call 到 finally 才扣在途；ACK失败保失败、禁 READY，但已返回与仍在途分列。未返回不扣账、不补造 ACK | JVM 原线程/取消迟到/失败ACK通过 |
| 失败有限查询后停止推进 | 同原 host owner 接续 CANCEL/QUERY/close/abort，使用首次 cancelAt 的同一个30秒截止 | 生产源码；真实收尾待测 |

Android 12 AOSP BinderProxy.transact 中，同步事务在 AppOps 采集启用时可附加 FLAG_COLLECT_NOTED_APP_OPS，说明 flags==0 并非正确同步判据：[原 AOSP 源码](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/core/java/android/os/BinderProxy.java)。N2 未保存 flags，不能据此断言原机已启用该分支。

## 原启动链与诊断

HELLO owner ready→原身份 BEGIN/FD adopt→codec Handler owner open→能力枚举/至多四提案→MediaCodec create/configure/start→真实 mux sink open→STARTED 同步 callback/有界 ACK→原 QUERY startProven/openReturned→source 解码→六帧→真实 EOS/close→普通 isolated CPU 独立 EOF/时间线/缩略图复核→READY。任一原 native/Binder 不返回，原对象与 slot 继续保留。

E5Trace 每任务最多64条，保前16条和最近48条；字符串每条160字符，尾8条随 Bundle 展示，另保存首错、当前阶段/相对时间/dropped。无锁跨 Binder/codec/文件操作。host 和 codec PID/UID、原 task/epoch/gen/instance、枚举候选名、四提案 name/color/baseline、固定256x144/600000/5fps配置、创建阶段异常类/公共 codec error/首错、cleanupError、实际 callback enter/return/ACK/inFlight 分列。Vendor diagnosticInfo 只认固定公共格式，不打印任意 MediaFormat、源 URI/凭据或媒体数据。

仪器摘要分别打印 REPORT、HOST_DIAGNOSTICS、REMOTE_IDENTITY、REMOTE_CODEC、REMOTE_OWNERS、REMOTE_STAGE_TAIL；总64事件/每条4096字符。超时 await 也先 query 原本地 Report 留阶段再抛错。始终报告最近一次原 remote Bundle，不用通用 PENDING 覆盖首错。90秒仪器外壳等待仅为保留原诊断，不改变60秒产品、12秒协商、首次取消30秒门。

## 原正常失败主动收尾

首次失败保首错，cancelAt 仅设一次；取消 source 与 broker；原 endpoint CANCEL/QUERY。原 callback/native/resource lease 确实返回、worker lease 可排他后才持久 ABORT_PENDING→fence→ABORTED、保留输出、关闭 owner。source/sink/hash/CONTROL/目录 FD 原对象全部返回才追加 S；按实际保留输出字节消费，不删除失败输出求退款。正常 S 写入/fsync/原 ledger lock与文件close返回后才移除本次 marker 并同步目录。首错、cleanup 与系统reason/status分列。

初次约5秒有限清理未证时，同一 owner 至多一次接续，受同一首次取消30秒边界控制，不重置计时、不以超时扣在途、不重发 UNKNOWN close。原调用卡住或 close未知继续 PENDING；调用迟到返回不倒改旧用例结果。进程死亡仍保原隔离/异常门，不能一般化为所有任务可自动恢复。

## 仅原 N2 合法恢复

E5N2Recovery 构造仅接 app 私有 files 根与内置实际证据适配器；所有 task/epoch/gen/instance/PID/UID/budget/batch/lease 常量固定。没有任意任务、任意预算、任意 PID 参数或通用 reset。debug 仪器单独入口，默认 QUERY，ABORT_ORIGINAL_N2 必须另正式派发。生产 UI 不自动调用。

1. bounded/no-follow 读取225B原identity、85B WRITING journal、36B lease/anchor、0B owner/marker、原 ledger 完整 R 链；原输出仅核 regular/≤2MiB，QUERY不读取/哈希输出。任一原身份、原链或状态不一致拒绝，含已有 S/重复恢复。
2. Android ApplicationExitInfo 每原PID最多8条；要求原 UID、进程名、PID、N2精确时间窗口1792208947872..1792208970000各唯一匹配。两个原PID当前 /proc lstat 都须 ENOENT；可见/复用/权限未知均拒绝。检查当前 appUID10221、产品 host无活动/保留session。ps缺席、finished inst、空输出、调用者布尔值均不能单独证明释放。系统reason/status原样保存，不补旧 ACK，也不冒认signal成功。
3. E4A FD 拓扑只将输出传原 host 与原 sameUID codec，尚未转首帧或隔离验证。上述两进程实际死亡与实际 `.owner`/`.lease` 原 flock 排他取得相结合，才说明原写者不能继续写。锁已取得后完整重核原metadata/death；获取原ledger实际独占FileLock。
4. CREATE_NEW 预算目录下 N2-e5-recovery 恢复归档（不向正常输出纯文件目录加入子目录），原 identity/journal/lease/ledger 原字节前像各 fsync+目录sync；新 lease epoch 只用于 fence，不改变原 task/budget。持久ABORT_PENDING→ABORTED，实际读取 fence/journal 验证。
5. 锁内读取保留输出≤2MiB并 SHA-256，原读FD实际close返回后，写可追溯死亡/fence/actual bytes/hash证据；在原 R 链后追加唯一 S ABORTED 实际字节/hash/fsync/readback。原非空17B模型消费17B；只有完整证据齐全的0B才结算0B，绝不按空文件自动退款。
6. 原 ledger/filelock、worker lease、owner及所有恢复读写FD实际close返回，才同目录原子将 operation.pending 改名 operation.pending.N2-e5-aborted（不删除），sync预算目录。最后 CREATE_NEW 固定task/budget完成凭据并fsync+目录sync。失败产物、旧R与before images均保留。
7. UNKNOWN原对象/目录持有者在静态ACTIVE集合强引用，无GC/重试close；fence之后持久化失败也保poison，即使新FD都返回仍禁本进程后续编码。正常 reserve 还检查恢复归档对应 marker archive 与精确完成凭据，因此缺少完成凭据的部分恢复在新 host中同样拒绝。中间失败只许另审，不自动接续半完成恢复，不开新UUID规避。

本机 Model 的范围 FileLock/死亡记录/目录sync故障仅用于反例，不声称 Windows 模型证明 Linux flock、真实 ApplicationExitInfo、fsync抗断电或真实 Binder。实机记录不可用时结果必须 BLOCKED；本批并未取得任何原 N2 新设备证据。
