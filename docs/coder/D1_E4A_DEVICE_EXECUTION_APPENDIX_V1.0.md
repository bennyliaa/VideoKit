# D1 E4A 新设备计划附录 V1.0

2026-10-17。**整份计划NOT_RUN，executionAuthorized=false。** 只有集中离线构建/JVM和只读产物证据，不ADB、不轮询设备、不安装、不运行codec/native fault、不访问真实媒体/PF。负责人须先整包交独立tester复审，随后另派准确有限设备批次。本附录不自行放行。D1未通过、M0未启动、原P0/C14/历史FAIL不变。

测试类仍com.videokit.spike.e4.E4DeviceTests，实物测试APK在artifacts/D1-20261017-E4A/final。必须指定单一方法，禁止整类执行。目标App仍com.videokit.app，测试APK不是companion；原包启用/安装/签名/API/ABI、手机既有阻断、空间、当前fixture身份在正式批次先只读核，不猜当前连接，不卸载清数据/换包名或强启绕过。

## 准入参数及累计预算

- e4Case：准确方法名；e4Batch：负责人审定的D1-E4A-[A-Za-z0-9-]{8,80}。
- e4BudgetIdentity：外部审定的稳定小写UUID，必须匹配固定app-private e4a_output_budget/identity.anchor。所有方法/host共用；新batch或UUID不能取得新4MiB。格式本身不等授权或原资源已归还。
- e4NormalReceiptSha256：取消及三个quarantine共四项必须有同设备真实正常报告的外部核验SHA256；四个依赖方法的字符串校验不作通过证据。两个正常及两个独立反例按自身前置。
- e4Quarantine=LAST_SINGLE_CASE：三个quarantine各自单独最后调用。它们是可选的最后分支，不是可连跑6→7→8序列。

全局账本R预留2MiB，原Session全部关闭/CONTROL返回后S结算实际长度/SHA，累计消费4MiB/128输出记录，未知保完整预留和pending marker。目录数据存量4MiB/128文件仅额外限制，不代替累计。输出identity/journal等元数据128KiB、ledger128KiB/256事件、anchor36B/pending0B单列。预留不足、元数据异常、已有marker即拒绝停止，不删除失败产物/历史cache凑额度。

第一个quarantine/PENDING后，后续encoder即使换host仍由原marker拒绝；余下分支BLOCKED，须负责人另行评审原资源事实及合法后续机制。本包没有reset/reconcile API，不能自动清marker、换预算UUID/目录、清app数据或重复启动洗未知。另一独立CPU任务不授新encoder，仍须其源/退出/槽真实归还。

## 八项准确方法

| 计划序 | 方法 | 前置与关键真实观察 |
|---:|---|---|
| 1 | normalMp4SixRealFrames | basic.mp4，实际6源/6编码输入/6样本/isolated完整EOF6帧，原PTS/内容、Source/Sink/codec/callback/CONTROL/预算与许可全部归还；原失败/成功产物和identity/实际长度SHA保留 |
| 2 | normalAviSixRealFrames | subtitle.avi，同上；能力/软件硬件/实际路径各列，不由MP4或编译替代 |
| 3 | capabilityDenialDoesNotOpenSource | 原Source open/read/bytes为0；BEGIN可能已授空Sink FD，必须实际close、ABORT保留0B产物及SHA并S结算0，不写“从未分配FD” |
| 4 | binderRefusesBeforeBeginAndOversizeParcel | 实际远端 beforeBEGIN/wrong epoch/old instance/超Parcel拒绝；不BEGIN、不枚举codec、不授Sink，不消费新输出R |
| 5 | cancelRejectsWrongEpochOversizeAndLateFrame | 外部正常receipt；ACTIVE且真实源read在途，错误epoch/长度及取消迟到拒绝，0编码输入；撤销不删已创建空/部分输出，原源/FD/owner/CONTROL关闭后才S结算与许可0 |
| 6可选最后 | selfKillOtherCpuContinuesAndOldGenerationRejected | 正常receipt+LAST_SINGLE_CASE；原codec ACTIVE、另一isolated任务read已实际接纳且受控等待，own service arm/commit命中；原Binderdeath后释放另一read并看实际RGBA/源关闭/slot；host原实例/主线程响应。故障前read在途不等底层字节已读完 |
| 7可选最后 | nativeSegvOtherCpuContinuesAndOldGenerationRejected | 同上，仅自身Debug :e4_codec、原task/epoch/gen/UID/PID/实例一次token；raw OS status原样保留，不借外部raw补系统signal0，未执行分支仍NOT_RUN |
| 8可选最后 | closeUnprovenRetainsPermitAndNeverReady | 同上前置，close ACK未知必须PENDING，原对象/许可/pending marker保留，第二encoder拒绝；不把UNKNOWN保留当实际release |

新的.metadata重连仅HELLO/原旧身份QUERY拒绝，不BEGIN/不授新Sink/不启动encoder、不改变原UNKNOWN和账本。不能写成恢复编码成功。

## F03取消的原时限观察

在第一次取消前设30s绝对截止。s.await只等剩余时间，首次不可变Report可为PENDING；随后同Session.query最多601轮/50ms且不越原截止，等待实际CONTROL及末尾预算收尾。不得只检查CONTROL计数0，因为归零后的最终文件同步仍可能在途。query不发新控制/不读媒体/不换身份。超时或未知保PENDING、断言失败归档，不续30s、重跑或提前减计数。

HELLO≤51次名义5s，正常末尾21 QUERY/取消101 QUERY、50ms名义1/5s；单次同步Binder/native若不返回，轮询上限不是强中断。正常四提案/12s、管线60s/六帧界保持；真实方言/驱动挂住只能保owner，禁止杀宿主求资源0。

## 真实源、输出与日志读取预算

fixture必须由正式tester在另行授权批次预置为只读使用，coder本次无stat/读取/复制/hash/下载：

| 精确文件 | files/e4_fixtures下长度 B | 历史声明SHA256，须正式批次重核 |
|---|---:|---|
| basic.mp4 | 349102 | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |
| subtitle.avi | 736454656 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f |

若原8项全各一次，6个MP4方法+1个AVI方法的前后完整hash共1477098536B；这是上限规划，实际遇第一个未知后的BLOCKED分支不执行。每次hash64KiB buffer并检查精确长度/EOF；另列实际CPU decode/verify请求，不把hash成本藏进样本“只取六帧”。fixture只读占用约736.8MB，不属于新输出信用。每个已准入输出的before-validation/after-validation/最终结算摘要至多三次、每次2MiB、合计6MiB；失败/能力分支可能只有末次或未知。输出改变/增长/close未知不得结算。

固定256×144/stride1024/147456B、queue2/consumer1/CPU2/encoder1，主Parcel196608B/callback16384B，可达RGBA16份2359296B+YUV55296B；非整个RSS、GC后垃圾、Binder/framework/vendor缓存上限。每方法日志≤4MiB、整批≤32MiB；收原process/FD/线程/PSS/RSS及首因/cleanup/OS退出各自证据，有限快照不等长期性能。

本机自有小文件检查中主动删除独立dummy用于证明账本不退款，未删除实际7B失败产物；不能据此给正式设备计划增加清理权限。JVM进程退出清理未知自有FD不计协议归还。

## 停止与归档

正常、fixture、预算、身份、能力或原归还前置失败立即停止依赖项；未知保原owner/文件/marker，不强制GC/全局归零。三quarantine一个触发后不自动开下一host/encoder。系统reason/status原值、App WORKER_DIED、trace有无、外部观测分栏，system0严格UNKNOWN_FAIL；不改历史C14/C13判定，不同条件结果不回填。

手机/平板独立审定，Image未进入/ByteBuffer通过/软件codec成功各分列，不能互代。Surface/音频/字幕/图片/跟踪GL/Flutter/独立Kit、Apple/Windows仅原后续门禁，不由这8项关闭。所有执行均需负责人后续准确派发，本附录不包含可自行启动设备的runner。
