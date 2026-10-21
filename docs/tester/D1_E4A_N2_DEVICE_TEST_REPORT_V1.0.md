# D1 E4A-N2 平板产品链路测试报告 V1.0

日期：2026-10-17，约11:47—11:51；tester。仅HA1Q6WXR/TB138FC/API31/ARM64/用户0；原app UID10221，instrumentation包UID10222。批次D1-E4A-N2-TABLET-20261017，稳定预算UUID `730a73e1-50e1-4198-a515-047104f00e31`。

**结论：NOT_PASSED，0 PASS / 1 FAIL / 3 BLOCKED。** 唯一执行的normalMp4SixRealFrames返回PENDING/E4_REMOTE_PENDING，六源/六输入/六输出均未建立，resourcesReleased=false。原账本R预留2MiB和pending保留，无S结算。依据原停止门，AVI、能力拒绝和取消均未启动。新增产品阻断 **E4AN2-F01 / P1**；没有重试、清pending、改UUID或重启求通过。D1 NOT_PASSED、M0 NOT_STARTED、P0/历史FAIL/C14待测保持。

## 1. 授权、冻结与安装适用性

依据 `docs/milestones/D1_E4A_N2_TESTER_REQUIREMENTS_V1.0.md`。E4A只读verify PASS：外freeze `a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d`，201源/207不可变，68既有本机断言身份核验，不重跑它们。verify未访问媒体/设备。

当前pm path两包与原E4A-N安装记录逐路径一致，原APK身份沿用app `e4d9d5df28e5dbc5bcb9ac24e8555e457f80822a889fe3736e698fdfa6b9db2f`、test `1f7c0e5be2cb1694ef44bc2ae2f5e0e12a32da161c70d976ac4112384c2366be`，无重建重装。未追加一次设备APK全hash，路径连续和既有安装证据不冒充新APK逐字节观察。

新证据目录 `docs/tester/D1_E4A_N2_EVIDENCE`。设备准入UID/pwd正确；两fixture stat与MPREP原stamp完全相同：MP4 `64522,20198,349102,10221,8180,1792207996`；AVI `64522,20199,736454656,10221,8180,1792208513`。可用空间85360316KiB。初始budget目录、anchor、ledger、pending及output目录均不存在；tester未创建或重置这些对象，随后由原产品在稳定UUID下初始化。

## 2. 四方法实际结果

| 准确方法 | 调用次数 | 结果 | 原因/证据 |
| --- | ---: | --- | --- |
| normalMp4SixRealFrames | 1 | FAIL | 预期READY，实际PENDING/E4_REMOTE_PENDING，received0/inputs0/outputs0，released=false |
| normalAviSixRealFrames | 0 | BLOCKED | 正常MP4失败且原资源/预算未归还，禁止后续encoder |
| capabilityDenialDoesNotOpenSource | 0 | BLOCKED | 该方法也创建原E4Session/Sink、使用同service与稳定账本；已有未知/pending，无法证明是独立无复用项 |
| cancelRejectsWrongEpochOversizeAndLateFrame | 0 | BLOCKED | 两正常真实回执未通过，原pending存在，无合法normal receipt准入 |

未执行整类、已PASS binder方法、三个quarantine/fault或压力分支。没有生成“正常通过”receipt摘要，没有创建cancel-admission，不把字符串或MPREP/T6P传输报告替代产品正常回执。

## 3. 唯一产品调用及完整原失败

准确调用为 `am instrument -w -r`，class精确 `com.videokit.spike.e4.E4DeviceTests#normalMp4SixRealFrames`，e4Case同方法，e4Batch同本批，e4BudgetIdentity同稳定UUID；原参数完整保留在 `normalMp4SixRealFrames-instrumentation.json`。没有修改已安装APK或原device_plan。

原ADB客户端exit0、RETURNED，elapsed17.750s；原JUnit Time15.272s，Tests run1/Failures1，FAILURES!!!，INSTRUMENTATION_STATUS_CODE=-2。`INSTRUMENTATION_CODE: -1`和客户端exit0不能判产品PASS。完整原stdout2500B/SHA `6dd62e481bf2322a76b8149c59beb9ad9cff9b48c94dc835e1d26f053f31d3e8`，stderr0B：

```text
E4 FIXTURE name=basic.mp4 length=349102 sha=720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9
E4 REPORT task=86cafdb30fc4447d920bb19c884bf494 status=PENDING error=E4_REMOTE_PENDING received=0 inputs=0 outputs=0 outputTask=86cafdb3-0fc4-447d-920b-b19c884bf494 outputBytes=-1 outputSha=UNKNOWN controlInFlight=0 released=false workerDied=false rawReason=-1 rawStatus=-1 signalVerdict=NOT_COLLECTED
```

原断言 `E4DeviceTests.positive:83` 预期READY而得到PENDING。normal方法调用返回，没有触发tester60s外层截止；四提案12s/管线60s原产品限制未改。取消未启动，没有续期或预先减少CONTROL计数。

## 4. E4AN2-F01 / P1：合法MP4正常链路在远端就绪阶段未完成

合法fixture准备和产品前置hash已通过；原task已分配持久输出身份和预算R，但尚无源帧/编码输入/输出，约15s后E4_REMOTE_PENDING，原资源未能证明返回，导致同账本后续链路阻断。这是正常产品链路失败，不能归因于之前媒体传输失败，也不将PENDING保留本身误报成预算门应放宽。

源码 `E4Session.run` 在BEGIN后、第一次source.next前有15s serviceStarted等待；本次0帧和耗时与此阶段一致。**这是源码与实测的定位推断，不是已证明的驱动/codec或callback根因。** 原remote Bundle详细codec字段未输出到测试摘要；不能确认具体硬/软codec候选、Image/ByteBuffer分支、错误类别或更细的远端未就绪原因。

建议开发集中定位STARTED/回调/远端owner状态及原异常链，提交完整修复和可审证据；保留原PENDING、R、输出与稳定UUID，不以清数据/删marker、换预算身份、重装/重启或重复调用洗掉未知。修复和原未知资源的合法后续处置应一并评审，本报告不提供reset许可。

## 5. 身份、系统原退出和资源事实分列

只读logcat从本次原设备时钟范围读取，原6789B，未清空log缓冲。它记录：

- host PID24853、UID10221，codec PID24873、UID10221；同UID独立进程，不是权限/RCE隔离。
- 本次测试失败后，ActivityManager以`finished inst`执行系统instrumentation收尾，终止host和codec。tester没有发force-stop/kill/reset或再次启动App。
- 没有本次E4_SOURCE_FRAME、CPU验证帧或完整EOF日志；没有六源/六encoder输入/六样本/PTS/画面实证。

原新.identity（225B）经有界od原字节离线解析：batch同本批，budget同UUID，task `86cafdb30fc4447d920bb19c884bf494`，epoch5131975343750146374，generation1，serviceInstance `775a5ee9-fff3-4340-a03b-97751099c0c4`，hostUid/serviceUid10221，outputTask同UUID。没有伪造或借用其他batch实例。

原REPORT controlInFlight0仍released=false；Source/Sink、worker/codec/Image/callback/原owner及末尾预算完整归还均未证。系统进程终止或后续ps不见进程不等于原协议close ACK、S结算或许可可复用。原workerDied=false/rawReason=-1/rawStatus=-1/signalVerdict NOT_COLLECTED是报告时刻原值；后续系统杀进程不回填为本次受控故障或历史signal通过。

硬/软codec、Image实际进入、RGBA/YUV持有和完整codec诊断均UNKNOWN/未取得；不称某分支通过。失败收尾后无法取得本轮活动host/codec RSS/PSS或FD/线程峰值，不把16份RGBA等源码逻辑数组预算当实际RSS。host JNI/J01—J11/§29历史残余不关闭。

## 6. 原预算和产物保留

post只读确认稳定anchor匹配UUID，原ledger只有：

```text
E4A1 730a73e1-50e1-4198-a515-047104f00e31 4194304 2097152 128
R 86cafdb3-0fc4-447d-920b-b19c884bf494 D1-E4A-N2-TABLET-20261017 6660cfb1b19dee6ced8fb9427d6605eb394ba9ecd9ab5931905a9a8727ffd026
```

离线核ledger原链式SHA关系成立；已结算消费0B，未决预留2097152B，无S事件，operation.pending存在。不能把物理空输出或进程退出当作预留可退款；即便算术剩余2MiB也因pending不准入任何新encoder。

新output目录仅本task已观察元数据：`.identity`225B、`.journal`85B、`.lease`36B、`.mp4`0B、`.owner`0B，全部保留。journal离线解析magic E4A1、state0/WRITING、granted=true、lease epoch `a256356e-361b-47a0-b2e9-32dce4ccea8e`；未变成READY或ABORTED。REPORT outputLength=-1/outputSha=UNKNOWN保持，不把后续stat0B猜成原产品已关闭/结算或填空SHA。

两fixture post stat与MPREP及本轮pre相同，不追加相同完整hash。没有触碰旧归档、26B、T6P状态、预置temp/ready或旧cache；没有清budget/产物腾空间。

## 7. 实际调用、字节预算及工具限制

共8个ADB原调用：环境0.344s、logcat帮助0.093s、private准入0.328s、方法前时钟0.109s、唯一产品17.750s、该次logcat0.250s、失败后private元数据0.516s、失败后进程/辅助状态0.187s。均客户端原返回/管道实际close，原stdout/stderr长度SHA核验，无在途本机exec/session或UNKNOWN本机client handle。原产品UNKNOWN和pending单独保留，不由客户端归还清零。

辅助`dumpsys activity instrumentation`在本设备返回Unknown command/Bad activity command，保留原文本，未换命令重试，也不据其判断在途；ps只作有限快照。logcat help正常输出在stderr，属于原帮助行为而非产品异常。所有真实原JSON及文件SHA见receipt-audit.json。

实际仅MP4正常方法执行，按原Fixture构造verify和try-with-resources close/verify路径，前后hash共698204B；close若异常会作为JUnit附加异常保留，本次没有该异常。prehash原结果明确输出，posthash通过由未修改close路径/原测试正常收尾及无附加异常支持，不伪造第二条hash日志。AVI/其他MP4方法未调度，未读其内容；四方法总规划数学为3×2×349102＋2×736454656=1475003924B。tester额外fixture内容hash0。

在source.next前失败，观察到CPU任务/CPU实际内容读取0；没有provider计数器回执，不将源码推断和日志缺失冒充独立流量仪表。输出摘要原产品未完成，已证输出hash读0B，未追加hash失败输出；原每产物6MiB界不扩。新输出0B但R保2MiB；原累计4MiB/每输出2MiB、128记录/256事件、ledger及其他元数据128KiB界保持。

本机单方法相关artifact审核时34020B<4MiB；整批audit前160881B<32MiB，后续小报告/审计仍远低界。metadata每次最多128KiB，本次最大22784B；方法日志采集设置1MiB子界，实际6789B完整，没有触界或截断。原日志不清理/覆盖。

tester runner为本轮准入与证据收集辅助文件，未修改产品/冻结文件；instrumentation原客户端有独立wait/drain/关闭owner，若到原截止仍在途则强保原对象/解释器、不杀原client、不续期。此次未触发该路径。系统instrumentation自带的start/finish强停行为按原系统日志披露，不能冒充tester协议归还。

## 8. 独立审核和交付

原回执及判定在 `normalMp4SixRealFrames-independent-review.json`：原stdout SHA `6dd62e481bf2322a76b8149c59beb9ad9cff9b48c94dc835e1d26f053f31d3e8`，dependentEncoderAdmitted=false/cancelAdmitted=false。方法原JSON SHA `bdd4c062849c239336194ad0dc6fcd8ff5873c1c0eb615de54e04638901712de`；原logcat JSON SHA `0d4ab0f1fbc092645e4057d4a110552a9dd1ab7ad962feae4160fa40efa60231`。

receipt-audit.json只读核原8调用完整字节/SHA、identity/journal、ledger链和四项状态，PASS仅指证据完整性，不是产品PASS。原会话99921已正常结束、无本机在途；原产品对象协议状态UNKNOWN及持久pending仍待负责人/开发评审，未恢复执行。

完整报告主动反馈负责人。后续须集中修复/审查原未知资源事实和合法处置，不自动下一批；手机既有阻断不重查、不催连接，无安装/Gradle/模拟器/Binder重跑/故障/产品取消调用。MPREP预置PASS不撤销，但不能代替本次产品失败；D1未通过/M0未启动/P0历史FAIL保持。
