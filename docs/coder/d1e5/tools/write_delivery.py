"""Write the four required E5 review documents from final local evidence, before freeze only."""
import json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(n):return json.loads((B/'evidence'/n).read_text(encoding='utf-8'))
def link(path,label=None):return '['+(label or path)+']('+str(R/path).replace('\\','/')+')'
def main():
 if (B/'evidence/e5-freeze.json').exists():raise ValueError('FROZEN')
 checks=load('local-check-results.json');build=load('build-results.json');audit=load('apk-audit.json');external=load('external-readonly-verification.json');diff=load('sbom-difference.json')
 assert all(x['status']=='PASS' for x in [checks,build,audit,external])
 apks='\n'.join('| '+a['role']+' | '+str(a['bytes'])+' | `'+a['sha256']+'` | '+link(a['path'],'安装包')+' |' for a in audit['apks'])
 cert=audit['apks'][0]['signerCertificateSha256'];base='docs/coder/d1e5/'
 delivery=f'''# D1 E5 交付 V1.0

2026-10-17。候选 D1-20261017-E5，仅本机 JVM 与离线构建通过；Android/真实 codec/Binder/原 N2 恢复执行均 NOT_RUN。N2 原 FAIL 不回写；D1 未通过、M0 未启动、全部 P0/JNI 与旧 signal FAIL 保持。

## 本批结果与证据边界

需求为 {link('docs/milestones/D1_E5_CODER_REQUIREMENTS_V1.0.md','E5 集中需求')}。实现生产启动握手修复、有限阶段诊断、失败后原 owner 主动收尾、仅限 N2 身份的查询/合法 abort/fence/实际消费结算入口。真实六帧编码、隔离 CPU EOF/时间线/缩略图验证、Media3 1.9.3 与受限 FFmpeg 8.0.3 均保留。没有用 Fake 生成真实 READY。

已证源码问题：旧 host 用 flags==0 拒绝同步 Binder 的框架附加标志；诊断 CODEC_EVENT 从 codec owner 同步调用 host；host 在 STARTED callback 返回 ACK 前即可置就绪；旧 callback ACK 异常与仍在途混为永久 UNKNOWN；失败有限查询后缺少同原 owner 的主动接续。修复与证据详见架构文档。N2 原记录缺少具体 callback flags、ACK、codec 阶段，所以实际唯一根因仍 UNKNOWN，不宣称本批已治愈设备故障。

## 本机验证

最终 JVM repair-004：原协议/资源/旧代 Core 89 项，新增回调/能力/取消/恢复主路径 48 项，独立 close-unknown 子 JVM 3 项、durability-unknown 子 JVM 2 项，合计 142 断言。后两者各保留 1 个原操作至解释器结束；不把解释器退出计为资源归还，也不将模型 FileLock 认作 Android flock/Binder 验证。初次 main 与 repair-001 的模型失败日志保留，原因是 Windows 强制文件锁阻止重读；repair-002 改为本机模型的范围锁，生产完成凭据补强 repair-003 通过，归档与正常输出准入兼容修复后 repair-004 通过。并未改 Android 原 flock。

构建 main-001 被现有 Gradle 缓存写锁权限阻断；repair-001 得到公共 API O_DIRECTORY 不存在的编译错误；repair-002 改 O_RDONLY|O_NOFOLLOW 并 fstat 验目录后编译通过；repair-003 增补恢复查询原系统证据，repair-004 将恢复前像归档移入预算子目录，避免违反正常输出的纯文件清单，最终完成离线 assembleDebug、assembleDebugAndroidTest、debugRuntimeClasspath。未新增依赖、未下载、未安装/启动 APK。所有尝试原日志与失败输入快照保留。

{link(base+'evidence/local-check-results.json','最终 JVM 输入与结果')}；{link(base+'evidence/build-results.json','离线构建结果')}；{link(base+'evidence/final-build-inputs.json','最终 build 输入')}；{link(base+'evidence/build-input-lineage.json','构建输入沿革')}；{link(base+'evidence/apk-audit.json','签名/Manifest/native 审计')}。

## 精确安装包身份

| 角色 | 字节 | SHA-256 | 文件 |
|---|---:|---|---|
{apks}

两包签名证书 SHA-256：`{cert}`，与原 E4A 一致。appId com.videokit.app（test 为 com.videokit.app.test），versionCode 2 / D1-E5，普通独立 CPU :d1_cpu_worker 与同 UID :e4_codec 两个非导出服务。无 INTERNET/companion APK。签名私钥未打包。

## 完整来源与冻结

{link(base+'artifacts/D1-20261017-E5/D1-20261017-E5-source.zip','完整 E5 源码 ZIP')} 包含本候选源码、构建/检查工具、原始日志、小型自有假数据、四文档、基线映射与完整 C14 对应源码容器。排除本机 local.properties、密钥、Gradle/build/classes 缓存和真实媒体。双 APK 作为外部 immutable 项独立封存；ZIP 成员由 source-manifest 精确枚举，不递归解包历史对应源码容器。

{link(base+'evidence/e5-freeze.json','外部冻结清单')} 绑定源码 ZIP/manifest/每文件/双 APK；最终 ZIP 大小、SHA 与冻结文件 SHA 在集中交接中给出，避免文档包含自身 ZIP 哈希形成循环。只读核验命令：Python -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1e5/tools/e5_package.py verify。该命令只核本地冻结，不执行设备、媒体或构建。

SBOM 35 个 Maven 坐标，E4A→E5 坐标差异 0，七个 native 字节差异 0。保完整 C14 native 对应源码与许可映射。此为精确继承审计，不是漏洞/许可放行。{link(base+'evidence/sbom.json','SBOM')}；{link(base+'evidence/sbom-difference.json','差异')}；{link(base+'evidence/upstream-copy-map.json','C14 复制映射')}；{link(base+'evidence/source-derivation.json','E4A 衍生关系')}。

E4A 207、T6 54、MPREP 165 个旧 immutable 项只读核验通过，各外部 seal 与原值一致；未改旧候选/报告/fixture/设备缓存/预算/失败产物。{link(base+'evidence/external-readonly-verification.json','旧冻结只读结果')}。本批 coder 设备调用 0，真实媒体 stat/read/hash 0，新 fault 设备执行 0。

一次完整冻结交负责人审阅后才可正式交 tester；下一顺序为原 N2 处置准入→正常 MP4→正常 AVI→能力拒绝→条件取消。没有部分交接或本窗口执行许可。
'''
 architecture='''# D1 E5 架构与威胁边界 V1.0

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
'''
 gates='''# D1 E5 剩余门禁 V1.0

2026-10-17。仅本机实现、模型与离线 APK 构建可审；D1 NOT_PASSED、M0 NOT_STARTED、全部P0/JNI/独立Kit正式交付门和旧signal FAIL保持。

| 门禁 | 当前结论 | 下一证据 |
|---|---|---|
| N2 实际启动根因 | UNKNOWN，原日志缺flags/阶段/ACK | 一次正常MP4有限观测，保存E5原字段 |
| 同步callback标志/原ACK准入 | 生产修复+JVM通过 | 真机原UID/PID/flags/ACK/openReturned/startProven |
| 能力四提案/真实六帧 | 未执行 | 原12秒协商/60秒总门内实际6入6出 |
| 原source/native/Image/mux/FD/CONTROL收尾 | 模型与静态审，设备待证 | 原任务实际归还，失败保产物+实际消费S |
| 原N2 pending处置 | 狭义实现存在；设备准入未通过 | 原两个退出记录、原真实排他lease/fence/ABORT/S与所有恢复owner返回 |
| 恢复证据不足/重复/部分持久化 | 本机反例通过 | 设备不足时拒绝，不以人工清账绕过 |
| MP4/AVI 正常 | 原N2为1FAIL，AVI阻断 | 原pending合法处置通过后按顺序实测 |
| capability/条件cancel | 原N2均BLOCKED | 两正常先通过；0源读、无假READY；同首次cancel30秒 |
| CPU/codec隔离威胁 | :e4_codec同UID仅故障边界 | 不宣称恶意RCE/权限隔离；原CPU普通isolated边界保留 |
| native signal/JNI/全P0 | 历史FAIL/未通过 | 本批不重跑不覆盖 |
| 依赖与许可 | E4A lock/native差异0，完整对应源码保留 | 非发布许可或安全清零 |

首个正常MP4仍失败时，记录当前原身份/Bundle/host诊断、codec候选与具体阶段/首错/ACK enter-return计数、source与output实际资源、原journal/R/marker/S与文件身份，立即停止后续正常AVI/能力/cancel，不换预算或延长等待。若仍无足够根因，交一次有限观测结果给负责人再派修复；不得循环重跑或猜测设备已修好。

原N2恢复 QUERY可仅给出metadata/death已核的查询结论，不代表排他lease/关闭/结算已证；必须单独正式ABORT才能推进。记录不足、UID/PID/时间歧义、marker非0、原journal不符、原ledger已变、锁忙、native调用/close未知、fsync失败或中间恢复归档已存在均保持BLOCKED。不得删除归档/marker/输出/ledger、换UUID/目录、清数据、卸载重装洗状态。

下一整批只含原pending处置准入→正常MP4→正常AVI→能力→条件cancel。旧三个quarantine与Binder方法虽保源码历史，本批选择表不含它们。任何将旧ADB exit0、JUnit失败、进程系统结束、0B输出或本机模型通过计为真实产品PASS均无效。
'''
 appendix='''# D1 E5 设备执行附录 V1.0

2026-10-17。只供负责人冻结审阅与另派tester；本窗口本批没有ADB/设备/真实媒体stat-read-hash/新fault/安装/下载权限，也没有执行这些动作。必须用完整冻结双APK，先独立静态审查。不得对浮动源码测试。

## A. 原现场与安装准入

保留原N2整包报告/原stdout/logcat/private identity/journal/ledger/marker、全部失败输出；MPREP两fixture与原归档/26B诊断文件不动。原appId与UID10221、budget730a73e1-50e1-4198-a515-047104f00e31必须保持。只在正式派发允许的保数据同签名更新条件下部署E5（versionCode2），不得卸载/清数据/换UID/新预算。部署若导致历史退出记录不可查，恢复仍BLOCKED。安装、查询与恢复必须先由负责人明确派发，静态审阅不自动放设备。

## B. 单独原N2查询

选择 com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort。参数固定：e5N2Action=QUERY，e5N2Task=86cafdb3-0fc4-447d-920b-b19c884bf494，e5N2Budget=730a73e1-50e1-4198-a515-047104f00e31，e5RecoveryBatch=D1-E5-N2-RECOVERY-20261017。缺参数拒绝。默认不接受其他方法/整类运行。

QUERY最多读取五份原metadata（identity225、journal85、lease36、anchor36、ledger≤128KiB），核owner/marker为regular0B、输出regular≤2MiB，查询每PID最多8条退出记录与两个/proc存在性；不哈希输出、不fence、不改任何原文件。QUERY_ELIGIBLE仅表示metadata与两死亡记录已核，未证明真实排他lease/结算。

只读查询入口若失败需保存阶段/原因与原系统证据，停在BLOCKED。禁止把系统finished inst文本换成调用者的death=true。原journal仍必须WRITING/旧lease epoch；有任何先前部分恢复痕迹都需另审。

## C. 单独正式原N2 abort

仅负责人审QUERY与原现场后另正式派发。选择同一方法、同一固定参数，将e5N2Action改为ABORT_ORIGINAL_N2。此为单次原N2事务，不是E3旧执行许可/通用reset。产品host应无活动或保留session，不运行其他设备/构建/媒体任务。

操作顺序与架构文档一致：重新全部metadata/death核验→原owner及worker lease实际排他flock→再次完整核验→原ledger独占→CREATE_NEW前像归档→新lease fence→原journal ABORT_PENDING/ABORTED/readback→实际保留输出hash≤2MiB→原S追加/fsync/readback→实际关闭所有原恢复FD/锁/owner→原marker同目录原子归档/fsync→固定完成凭据/fsync。原closeACK始终false，死亡关闭与协议ACK分开记录。S实际消费不重置预算、不删除失败输出；重复操作拒绝不再追加。

最多32个注册持有者、Android目录sync至多16、原metadata每次有界，归档只保原4份metadata/1份proof/1份完成记录，journal tmp只固定2个；无目录递归扫描/媒体探测。ABORT两次原metadata读取预算≤2×(225+85+36+36+131072)=262908B；额外fence/journal回读121B，输出哈希≤2097152B；ledger锁内精确192B读取与小于512B追加回读。无文件删除。若不能证明有限内返回或任何FD关闭，保存PENDING/BLOCKED，不再次操作原close/不推进产品。设备所有外部调用必须采用已经审过的原进程实际归还工具，不用超时退出代原资源归还。

验收须保存原identity/before journal/lease/R、两个原PID的ApplicationExitInfo reason/status/timestamp/UID/name与/proc判据、fence前后、实际flock与close返回、ABORTED回读、原输出dev/inode/length/实际SHA、唯一S和累计消费、归档marker/完成凭据、所有本次owner返回。N2原输出0B仅当全部条件齐全才允许S0；若实际非空按字节消费并保产物。任何中间状态失败均停止，禁止再造另一次事务绕过。

## D. 完成后产品四项整批

恢复ABORTED_SETTLED与全部持久现场由tester独立核验通过后才准入。沿用稳定budget；产品batch参数固定D1-E4A-E5-NORMAL-TABLET-20261017（沿用E4A持久schema前缀，候选为E5），e4BudgetIdentity为原budget，e4Case为单个方法名；执行前核现行E4DeviceTests参数枚举，禁止整类运行。

| 顺序 | 单方法 | 前提与原门 |
|---|---|---|
| 1 | E4DeviceTests#normalMp4SixRealFrames | 合法原basic.mp4；同原60秒，6入6出、EOF验证、READY/all released |
| 2 | E4DeviceTests#normalAviSixRealFrames | 首项通过；合法原subtitle.avi；同60秒与真实隔离验证 |
| 3 | E4DeviceTests#capabilityDenialDoesNotOpenSource | 两正常通过；至多四提案/12秒；source opens/read bytes=0、0帧、ABORTED且原资源全归还 |
| 4 | E4DeviceTests#cancelRejectsWrongEpochOversizeAndLateFrame | 两正常报告独立审过；e4NormalReceiptSha256为该原报告SHA；同首次cancel30秒、无READY、原资源全归还 |

e4NormalReceiptSha256 必须为独立审过的两正常报告摘要；此参数语法通过不等于报告独立通过。前三项有任一失败或PENDING即停止余项，不以source fixture再次传输替代产品定位。主60秒、协商12秒、取消30秒均不放宽，原15秒STARTED等待不延长。仪器90秒外壳只捕获卡住时诊断，不改变产品验收。

每个原调用stdout/实际exit/原owner返回、JUnit原tests/failures/code与E5六组诊断完整保留；ADB exit0本身无效。保存task/epoch/gen/instance、host/codecPID UID、候选及配置、首codec错误/cleanup/系统reason分列、callback enter/returned/inFlight/ACK、原output/identity/journal/ledger/marker/S与allReleased。首次MP4仍失败则只提交本次有限观测，不重跑、不探测其他三个quarantine/旧Binder入口。

报告区分恢复诊断、产品PASS/FAIL/BLOCKED与历史FAIL。D1仍未通过，M0未启动；完整结果主动交负责人，后续动作待正式新批次。
'''
 for name,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gates),('DEVICE_EXECUTION_APPENDIX',appendix)]:
  p=R/('docs/coder/D1_E5_'+name+'_V1.0.md')
  with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
 print(json.dumps(dict(documents=4,deviceCalls=0)))
if __name__=='__main__':main()
