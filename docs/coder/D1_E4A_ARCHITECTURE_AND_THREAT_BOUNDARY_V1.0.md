# D1 E4A 架构、威胁边界与原 owner V1.0

2026-10-17。E4A只集中修复F01/F02/F03，待独立复审；本机证据不提供真实Android/硬件/故障通过。D1未通过，M0未启动，所有原P0保持。E4/C14冻结原样保留，完整原容器及来源关系随新ZIP交付。

## 进程与调用位置

| 位置 | 实际职责与授予能力 | 仍需证明 |
|---|---|---|
| host普通UID | Source只读授权/实际read-close broker，原始帧转发、临时Sink权威、原实例围栏、字节摘要；新增本机累计预算与身份日志 | host文件/FileChannel lock/fsync/Binder/ART及原lease JNI仍是native链，不能称零JNI；Source在途/取消/FD实际归还须设备证据 |
| ordinary isolated CPU :d1_cpu_worker | C14受限FFmpeg8.0.3 demux/decode/sws六个真实snapshot；最终产物另授权完整decode至EOF/PTS/画面验证 | isolated不继承应用权限；有限只读broker不证明任意恶意媒体/RCE安全或被攻陷worker不能伪造结果 |
| 同UID :e4_codec | CodecList/至多四提案MediaCodec、Image/Plane、RGBA转换、Media3 1.9.3 fMP4/获授Sink-lease FD，单owner线程 | exported=false、独立地址空间只提供待实测崩溃边界；同UID仍能访问host私有文件/一般能力，不是权限/RCE隔离；系统/vendor/驱动不在自有进程保证内 |

同一com.videokit.app中只有两个未导出service；instrumentation APK不是companion。实际唯一应用权限normal ACCESS_NETWORK_STATE，无INTERNET/companion query或绑定权限；host/codec可查网络状态，isolated CPU不继承。没有源路径/源FD/URI/凭据进入codec协议；裸帧不经Dart/Flutter。释放压缩parser位置与codec位置不同，不因使用系统API自动具备强沙箱。

同步Binder核原UID、endpoint/实例、task/epoch/generation，PID仅一致性观测，非独立安全身份；[Binder官方限制](https://developer.android.com/reference/android/os/Binder#getCallingPid())说明oneway没有发送PID。同步callback只保存有限metadata并ACK原magic/hostUID/实例，不回调等待owner；实际ACK返回后才扣callback调用。最终事件不证明自身已返回，后续原QUERY须callbackInFlight=0且!callbackUnknown。BEGIN前transferAttempted，拒绝需要显式rejectedGrantCloseProven，!adopted/无回复/workerLeaseClear都不证明远端无FD。

## F01：撤销与保留、累计消费

E4FencedTask是本地衍生host authority，不改原C14 FencedTask。abortRetaining先持久ABORT_PENDING，再实际独占worker lease、更新fence、持久ABORTED；它从不删除输出。READY也需原worker归还、六输入/样本、isolated EOF/内容/PTS验证及原owner关闭，不是业务COMMIT。部分失败文件、journal、identity与lease元数据一并保留。

E4OutputBudget在固定私有目录e4a_output_budget持ledger.bin、identity.anchor、operation.pending。与方法/e4Batch/host/generation无关，不能新建实例就重新获得4MiB。batch和外部稳定预算UUID是审定参数，字符串格式不等授权。所有输出先R预留2MiB；S只在原Session所有资源/CONTROL实际返回后记录实际长度、SHA、READY或ABORTED，实际消费只增不减，预留未用部分才可释放。未结算保2MiB并阻止任意后续编码；新host不拥有原ticket，不能从目录、旧true或残余文件猜结算。

CREATE_NEW pending先于初始化/ledger FD；有marker的新holder/host拒绝，无论ledger当前是否看似完整。初始化/写/sync/close失败都留marker，原holder及资源继续强留。原结算文件同步、lock及FD实际close返回后，才删除marker；目录项移除本身不作掉电保证。ledger丢失但anchor存在拒绝；header/链/尾换行/长度/身份/128记录/256事件/128KiB任一异常拒绝。追加链用SHA256检错，不提供同UID恶意篡改认证。用户清空整个app数据或攻击者改全部文件不在此协作机制保证内，正式批次禁止。

输入文件在授权域只读，输出taskUUID与原Session.task对应；授FD前.identity持久化原epoch/generation/service instance/UID、预算UUID和batch。已证关闭产物S记录实际字节/SHA，未知则R+原文件和length=-1/hashUNKNOWN保持；实际hash已知但预算未知仍PENDING。输出目录128文件/数据4MiB，metadata另128KiB；ledger128KiB+36B anchor+0B marker单列。新输出需预留足够目录记录和1KiB元数据。预算不足停止，不删失败产物凑额度。

## F02：真实资源交接先于初始化

Sink先在broker注册；E4FencedTask的构造只建立字段/原holder，不做IO。Sink.task赋值后才initialize。task.owner holder在guard分配前已进入可达列表；AndroidLease.exclusiveInto先分配纯Guard并存入该holder，再打开PFD和执行acquire。PFD字段属于这个已登记Guard，acquire失败后的close无论成功、未返回或异常都不会丢外部可达路径。fence直接在原FD pwrite/fsync，不另建未登记dup。

E4Owned状态EMPTY→ALLOCATING→OPEN→INITIALIZING→READY，以及CLOSING/CLOSED/UNKNOWN。只有实际closer返回才CLOSED。初始异常与cleanup异常分别保存并保suppressed关系；实际对象和原参数不清空，UNKNOWN不得重试/换owner/退款，不依赖GC。close挂住则CLOSING仍保原对象；close成功即使初始化失败，也可证明对应资源已归还，不能将所有构造失败都当泄漏。

初次journal持久化/目录sync失败时，已登记task仍持原ownerGuard；即使其close也失败，两个异常和原PFD/guard都留在同一个task/holder。journal原流、预算lock/file、identity流和输出摘要流也在实际open前登记holder；未知不会被opening布尔值代替。目录sync原FD继续由Sink持有；关闭未知不再使用/重试该FD。未证owner/permit留PENDING，不宣称操作超时能强制关闭。

## F03：最后 CONTROL 返回与终态

E4ReturnGate.admit先计接纳调用，真实CONTROL线程runAdmitted的finally在同步调用返回后才returned。owner-finally只标owner完成；若CONTROL未返回仍不能claim唯一finish。最后返回线程或owner线程通过claimFinish竞争一次收尾，确认原资源均已排空，再做实际产物摘要、预算S结算、归还编码许可。cleanup异常保首因及原owner，不把PENDING算ABORTED/READY。

result首次发布可能是PENDING快照，这是合法事实；query观察同一Session最新账本，无媒体/文件IO，不重新接纳控制或重建实例。设备取消测试沿原30s绝对截止有限query，包括CONTROL=0但预算收尾尚未返回的窗口，不能续期/重试方法。同步Binder/native若一直不返回，真实调用保持在途，既定轮询次数不构成硬中断。

## 原边界不扩大

固定六帧256×144/stride1024/RGBA147456B/rotation0、实际PTS，queue2/consumer1、CPU2/encoder1、主Parcel196608B/callback16384B；可达RGBA保守16份2359296B+YUV55296B不含未回收ART/Binder/framework/vendor池或整个RSS。四提案12s、正常60s；HELLO同Binder≤51名义5s，末尾21QUERY/取消101QUERY/50ms名义1/5s，无法终止不返回的系统调用。

新service自身Debug白名单和两阶段ownPID fault只编译、不执行。死亡只核原Binder实例，App WORKER_DIED与原OS reason/status分列；system0仍UNKNOWN_FAIL，trace缺失/ordinary UNKNOWN不补成信号。dead代的许可与pending持久marker保留，新代只metadata旧身份拒绝，不新编码；另一真实CPU任务有独立预算但真实完成仍待设备。

本机最终68断言/JVM线程和自有文件仅验证这些生产helper有限交接，不是设备线程压力、Android FD/native或崩溃回收证明。原7native字节及Media3不扩，新增host Java文件锁与同步仍须J06风险评审。正式Kit/AAR公共API、多host/Flutter/Surface、Android12手机平板各矩阵及Apple/Windows adapter均未因此完成。详见[剩余门禁](D:/CodexProjects/VideoKit/docs/coder/D1_E4A_REMAINING_GATE_REVIEW_V1.0.md)。
