# D1 E5C 原 N2 最终观察及正常回归集中报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E5C_OBSERVE_REGRESSION_TESTER_REQUIREMENTS_V1.0.md`。已从负责人窗口读取并确认真实用户新指令“安排原N2最终观察和后续正常播放回归，完成后集中报告”，覆盖上一轮等待要求；证据见 verified-human-dispatch.json。

**结论：最终观察 PASS；四项产品回归 0 PASS / 1 FAIL / 3 BLOCKED。新增 P1：E5C-REG-F01。** MP4 实际取得6源帧/6编码输入/6输出样本，但隔离输出验证失败，最终 ABORTED / E4_HOST_OPERATION_FAILED，不能 READY。已按失败即停要求阻断 AVI、能力拒绝及条件取消，没有重试或自动下一批。

本次失败资源已真实归还，53651B 原产物保留并按实际消费结算，无新 pending 或未结算预留。原 N2 的合法 ABORTED_SETTLED/原 R+唯一 S0/归档与完成状态保持；原历史 FAIL、原协议 closeACKfalse、原失败根因 UNKNOWN 不改写。D1 NOT_PASSED、M0 NOT_STARTED、全部 P0/JNI/历史 signal FAIL/C14 待测保持。

## 1. 范围、部署适用性与结果

仅 HA1Q6WXR/user0，已装 E5C versionCode5/D1-E5C、app UID10221/test UID10222；当前包状态与旧部署一致。复用最终双 APK、签名及来源证据，不重装或重复设备 APK 全 hash。再次绑定 E5C seal `75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c` 和结算报告 SHA `5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962`，稳定预算 `730a73e1-50e1-4198-a515-047104f00e31` 不变。

| 项目 | 实际结果 | 说明 |
| --- | --- | --- |
| 独立 OBSERVE_SETTLED_N2 | PASS | 新 host 实际死亡/状态/force-close-sync 门通过，JUnit1/1 |
| normalMp4SixRealFrames | FAIL | 6/6/6 后隔离验证 native 拒绝，非 READY |
| normalAviSixRealFrames | BLOCKED | 前置 MP4 失败，未调用、未读 AVI 内容 |
| capabilityDenialDoesNotOpenSource | BLOCKED | 按本批顺序停止，未调用 |
| cancelRejectsWrongEpochOversizeAndLateFrame | BLOCKED | 两正常真实报告未通过，无取消准入、未调用 |

本批精确冻结方法验证六帧编码及隔离解码结果，没有另做人工声音、字幕或完整播放器界面测试。

## 2. 原 N2 当前最终观察 PASS

准确一次 `E5RecoveryDeviceTests#originalN2QueryOrAbort`，显式 OBSERVE_SETTLED_N2，固定原 task/budget/recoveryBatch 与结算 SHA。实际返回 `FRESH_OBSERVATION_ADMITTED oldRecoveryResult=UNCHANGED oldSyncReturn=NOT_INFERRED oldCloseACK=false`，JUnit OK(1 test)/0.074s，ADB1.422s。

当前恢复 writer 事实：attempt `8c6673b7-38a5-4a24-838d-ca8466d8b75f`，PID4869/UID10221/com.videokit.app，ownerRecordedAt1792224193301，实际 exitTimestamp1792224193337，reason10/status0，/proc absent=true。冻结 Android 适配器要求准确唯一匹配，实际通过；没有把旧报告替代本次死亡证明。

原前像/guard.identity/ABORTED fence/原 R+S0 链、无活动 pending 均通过。15个当前文件的实际 force/close、三个目录同步及原 guards 真实关闭全部经过冻结实现的实际返回门；成功资格不是由完成文件存在或系统结束仪器推断。没有另采逐 FD 数字或系统调用 trace，不据此补旧 UNKNOWN/sync/closeACK。

观察前后准确 metadata 字节一致，ledger仍371B、消费0/预留0、无 pending。完整审证落 [observation-independent-admission.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_OBSERVE_REGRESSION_EVIDENCE/observation-independent-admission.json) 后才允许 MP4。独立观察进程的 live proof 不跨进程；MP4 新 host @Before 再次实际观察，并再次返回 FRESH_OBSERVATION_ADMITTED，才读取 fixture/创建 Session。

观察原回执 SHA `84ff34d8d0a4b0f6320d149ff775c1fb35b6c3858bee59ddcbfea2fb3df6d76a`。

## 3. E5C-REG-F01 / P1：6个编码样本后隔离验证拒绝，正常 MP4 不能 READY

触发：已装 E5C、已审原 N2 结算并完成本 host 实际观察后，准确调用一次 `E4DeviceTests#normalMp4SixRealFrames`；e4Batch=D1-E4A-E5B-NORMAL-TABLET-20261017、稳定 budget、e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT、准确结算 SHA。未传 fault 或 normal receipt。

预期：真实6源/6输入/6样本、isolated输出完整6帧与EOF/PTS/缩略图、实际资源与预算归还后 READY。实际 JUnit1项失败，2.780s；ADB4.110s。核心断言 `expected:<[READY]> but was:<[ABORTED]>`，位于 E4DeviceTests.positive:97。

本次身份：host PID6499/UID10221，codec PID6521/UID10221，task `0ee155508952463991ac83ab9d14d36c`，outputTask `0ee15550-8952-4639-91ac-83ab9d14d36c`，epoch7900878330677138412/gen1，service `0abcce92-d857-4eff-9c56-7fbcd36c94ab`。

| 阶段 | 实际证据 |
| --- | --- |
| 原握手 | host startedSignal=true/startProven=true；callbackFlags18，原 caller PID6521/UID10221；ownerOpenReturned/startAckReturned=true |
| 六个真实源帧 | 六个不同 isolated CPU task，PID6552/6582/6607/6634/6656/6677，UID99048…99053；各源帧 sequence1…6、真实RGBA SHA/时间基存在 |
| 源 PTS | 2000000、2208333、2416667、2625000、2833333、3000000µs；相对0、208333、416667、625000、833333、1000000µs |
| 编码结果 | received=6/inputs=6/outputs=6；远端 ENCODED_AWAITING_ISOLATED_VALIDATION，选 OMX.qcom.video.encoder.avc，colorFormat21/hardware=true |
| 输出验证 | 第7个 isolated task `fbd96159a22f4b709c8e8bdc3c555d14`，PID6699/UID99054，kind2/mode11 |
| 验证帧日志 | sequence1…5，PTS0/208333/416667/625000/833333µs，time_base1/90000；未取得第6帧通过日志 |
| 实际拒绝 | CPU_WORKER_REJECTED_CATEGORY_2，cause_chain=java.io.IOException:CPU_NATIVE_REJECTED；CPU_DIAGNOSIS code=CPU_DECODE_FAILED / phase=NATIVE_STAGE_5 / category=LOCAL / original_type=NONE |
| 最终 | ABORTED / E4_HOST_OPERATION_FAILED；没有 PIPE_CONTENT_FRAME 或 PIPE_VISUAL_CHECK/full_eof=true 成功证明 |

结论范围：已定位到隔离输出验证失败。前5帧日志不证明实际只解出了5帧；也可能第6帧解出后校验被拒。当前证据不足以断定具体是末帧、PTS、EOS、内容或其他 native 条件，根因仍 UNKNOWN，不能仅凭 outputs6 或前5帧放行。

最终远端 encoderStarted/startProven=false 是收尾后的状态快照；已有实际 host STARTED 资格、8次 callback 成功 ACK 与6输入/6样本，因此本次不能归为旧 N2 的“未到实际编码”阶段。

建议开发集中核查 [E4Session 验证入口](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/android/com/videokit/spike/e4/E4Session.java:154)、[E4CpuAdapter.validate](/D:/CodexProjects/VideoKit/docs/coder/d1e5b/android/com/videokit/spike/c14/E4CpuAdapter.java:69) 及 native 输出验证链，保留可定位的原 native 拒绝细节。当前 host safe() 把非大写短码消息收敛为 E4_HOST_OPERATION_FAILED，日志又只留下 CPU_NATIVE_REJECTED，影响精确归因。修复不能删除第6帧/EOF/PTS/缩略图条件或降低预期为ABORTED；请完整冻结源码、构建输入、最终 APK 与验证证据集中交审，tester 不临时改生产代码求通过。

## 4. 此次失败实际资源已归还

原 REPORT 及 @After TERMINAL_EXIT 一致：terminalReason/phase=ACTUAL_OWNERS_RETURNED，originalOwnerReturned=true，cleanupContinuations=1，ownerFinishEntries=1，controlInFlight=0，released=true，workerDied=false，cleanupError空。

首次取消时钟101220863240656ns，绝对 deadline101250863240656ns；实际终局在原首次30s内具备资格，没有延长或用迟到返回升级。远端 callbackInFlight0、callbackEntered/Returned8/8、ackFailed=false、callbackUnknown=false；nativeCalls/liveResources/unknownResources均0、creating/imageHeld=false、encoder/sink/lease/framesReleased均true。

六个源 CPU job 和一个输出 verifier 的最后 CPU_LEDGER 均有实际 death=true、source_released/slot_released=true、pending_calls/operations/consumers/failed_closes=0、source_close=CLOSED；没有把系统杀进程单独当 source close 或 slot 归还证明。verifier虽业务验证失败，原资源仍完成返回。

rawReason=-1/rawStatus=-1/signalVerdict=NOT_COLLECTED 保留，当前未执行 codec 死亡/信号用例，不能写成历史 signal 验收成功。

## 5. 账本、产物及旧现场

53651B 失败产物保留在 `files/e4a_outputs/0ee15550-8952-4639-91ac-83ab9d14d36c.mp4`，dev64522/inode20174/UID10221；生产结算 SHA `20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd`。新 task journal为ABORTED、lease fence `b62c60cb-bdc3-44d2-a92a-c1179cc0a820`，identity/owner/lease/journal全部保留。没有额外读取该输出内容做独立 hash。

稳定原账本在原 N2 的 header/R/S0 之后追加本次 R/S ABORTED53651，逐条链独立重算准确；当前消费53651、未结算预留0、活动 pending不存在，最终 ledger SHA `8bcfddf657df9910df69161271909657f4b0d99fdae31cf89a439aa3810488bf`。停止后续是产品失败规则，并非额度不足或新 UNKNOWN；没有自动 ABORT、清账、换 UUID/账户或删失败输出。

原 N2 metadata 除共享 ledger 合法追加外逐字节保持：原 identity/ABORTED journal/fence、四前像、writer/guard.identity/proof、完成记录与原 pending归档不变，原0B输出仍 inode20386。原协议closeACKfalse、原历史FAIL不改写。

两个预置 fixture 的 stat 均保持，AVI未调用未读内容。MP4方法前校验与异常收尾的未改 Fixture.close 路径核验支持两次349102B hash，合计698204B（路径推导，非额外I/O监控），低于四方法数学上限1475003924B；tester没有重复完整源 hash。实际7个CPU任务请求已单列，CPU readAt请求数/压缩字节总量未采集，不能记为0。

输出hash按本次冻结路径推导为验证前一次digest和原owner结算一次digest，共107302B；验证失败未到 digestAfter。未独立读取/监控该字节数；原每产物最多三次/6MiB门保持。

## 6. 次数、预算、停止及交付

本批8次实际ADB：6次有界metadata/时钟/logcat、1次独立观察、1次MP4方法。各一次实际返回、exit0；其中MP4的ADB exit0不等JUnit通过。原始日志130188B <32MiB，每方法原记录及logcat各<4MiB，metadata记录<256KiB，原客户端管道/wait均返回，当前无在途client/handle。原方法/时限/预算未修改，未发生兼容修正或执行重试。

当前候选产品实际新资源已返回；所有历史 UNKNOWN 不做全局清理或信用重置。没有 AVI/能力/取消调用，没有取消准入或伪造正常 receipt。安装、Gradle/开发模型、故障/信号/force-stop、手机、媒体传输、新 ABORT均0。平板常设使用授权沿用，不再询问设备权限。

本批已按规则结束。集中报告负责人安排开发修复 P1；修复整包复审及下一批测试另行准确安排，不自动下一批。

证据：[final-independent-review.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_OBSERVE_REGRESSION_EVIDENCE/final-independent-review.json)、[MP4独立审证](/D:/CodexProjects/VideoKit/docs/tester/D1_E5C_OBSERVE_REGRESSION_EVIDENCE/normalMp4SixRealFrames-independent-review.json)。MP4原回执SHA `481d6b70d99b3fd064909fe512dbab466828f3a0fe15ee7e8e86dc6297754bda`；最终通知另存回执。
