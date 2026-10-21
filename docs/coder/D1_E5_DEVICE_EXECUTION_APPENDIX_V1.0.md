# D1 E5 设备执行附录 V1.0

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
