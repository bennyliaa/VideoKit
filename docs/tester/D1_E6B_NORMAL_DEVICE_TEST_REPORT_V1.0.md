# D1 E6B NORMAL 真机测试报告 V1.0

日期：2026-10-17。Tester。正式派发存 `docs/milestones/D1_E6B_NORMAL_TESTER_REQUIREMENTS_V1.0.md`，使用已审冻结 `docs/coder/d1e6b/tools/device_plan.json`，未改 REVIEW_ONLY 原计划文件。

## 结论

**MP4 PASS；AVI 在 Before 最终观察阶段 BLOCKED（JUnit 1 failure）；能力拒绝和 cancel 未执行。批次未通过。** 发现阻塞项 **E6B-OBS-F01/P1：下一新 host 无法重新证明原恢复写进程死亡**。已按正式停止条件保留现场，不重试产品/观察，不执行依赖后项。

E5C-REG-F01/P1 的原六帧编码输出校验失败，在本次 E6B/本平板/本 MP4 范围已取得真实六帧完整 READY，限定该范围关闭；原失败报告、失败产物和原生诊断历史保持。AVI 编码能力没有测试到，不能记为编解码失败或通过。D1 NOT_PASSED/M0 NOT_STARTED，全 P0、许可及其他未完成项保持。

| 正式单方法 | 实际结果 | 时长/边界 |
|---|---|---|
| normalMp4SixRealFrames | PASS，READY，独立原始证据审证通过 | JUnit2.699s，ADB3.953s；新 host 原最终观察通过 |
| normalAviSixRealFrames | BLOCKED_BEFORE_TEST_BODY，JUnit FAIL | JUnit0.028s，ADB1.344s；Before WRITER_DEATH 被拒，未读 AVI fixture/未创建媒体 session |
| capabilityDenialDoesNotOpenSource | NOT_RUN/BLOCKED_AFTER_AVI | 没有调用 |
| cancelRejectsWrongEpochOversizeAndLateFrame | NOT_RUN/NO_TWO_NORMAL_RECEIPT | 没有调用；未创建两正常联合 receipt，未替换占位符 |

## 环境、部署和连续性

唯一设备 HA1Q6WXR，Lenovo TB138FC，API31/ARM64/user0；原 app UID10221/test UID10222。正式批次 D1-E4A-E6B-NORMAL-TABLET-20261017。预检无 app/isolated worker owner 或活动 instrumentation，既有源文件 stat/原安装身份及账本连续性符合既有证据。

同签名 app→test 各执行 install-r **一次**且 Success，无卸载/clear/降级/重试。安装后真实 base.apk 指纹、版本8/D1-E6B、原 UID/user0 和可用状态核实：

- app：1930ff1cde30ab48adb184128c1313ac6a0ab6957ce425dfe4974c970a91a987，10,544,590字节。
- test：ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69，2,718,669字节。
- 候选外 seal：21ef22f4e92535a0d4e50703d87ff46849c4228f5a20dd6f9721c31c87dddc33；同签名证书沿已审冻结核验，不重新执行签名工具。

安装前后原 N2 settled 元数据、归档/beforeimages、旧失败输出元数据、fixture identity 和账本逐字节保持。源 basic.mp4 为 dev64522/inode20198/349102B，subtitle.avi 为 dev64522/inode20199/736454656B；无重新传输或冗余全文件 hash。手机和模拟器未操作。

## MP4 独立审证

单项报告 `docs/tester/D1_E6B_MP4_NORMAL_RECEIPT_V1.0.md`；原始证据与逐任务审证见 `docs/tester/D1_E6B_NORMAL_EVIDENCE/normalMp4SixRealFrames-*`。

host11353/codec11374/UID10221，task fbe4330b111b4b05a93c467413eb8d34；epoch968264325322937788/generation1/service de9431fb-d89b-4bd7-804a-0304e699fa1f。新 host Before 真实观察得到原 writer4869 的唯一死亡记录 timestamp1792224193337/reason10/status0/proc absent=true，原 oldCloseACK=false 保持。

六真实源帧、六 encoder inputs、六 samples、六输出完整 accepted。实际源 PTS 2000000/2208333/2416667/2625000/2833333/3000000us；输出 PTS 0/208333/416667/625000/833333/1000000us，最大偏差0us，原1000us门保持。输出容器 time_base1/90000，末帧 raw90000；双 EOF/drain 都为1。

验证器 task72f1f659d51a4a618c337ef1c116e978，PID11532/UID99061，scope VALIDATOR/mode11/phaseVERIFIED；E6_NATIVE_OK/site0/stage5/av_error0、packets6/decoded6/accepted6/last_pts1000000，真实 read_at1/compressed53567。六个 mode10 源任务使用不同 task/PID/isolated UID，最后源 task e01967ce6909476ca219e22158ae34fc/PID11509/UID99060；其 accepted0/EOF0 只描述单帧提取，不混为输出验收。

真实六帧 thumbnail/content/映射严格验收及 PIPE_VISUAL_CHECK full_eof=true，最大 luma MAE1.3194444444444444，source distinction19.479166666666668、output distinction19.520833333333332。此项是程序画面内容比较，不冒充人工观看或音频验收；音轨并非本六帧输出需求。

七 CPU 任务的最终 CPU_LEDGER 均 actual_death/source_released/slot_released=true，source_close=CLOSED，pending_calls/operations/consumers/failed_closes=0；实际远端 native/live/unknown=0，encoder/sink/lease/frames 归还；callback8进8返且无 ackFailed/unknown，CONTROL0、ownerFinishEntries1、ACTUAL_OWNERS_RETURNED、originalOwnerReturned=true。最终 test After 再次确认终局。未以普通字段 workerDied=false 推断 CPU 未死亡，该字段描述 codec 异常死亡，CPU 原始记录单独审查。

输出 fbe4330b-111b-4b05-a93c-467413eb8d34.mp4，53567字节，dev64522/inode4176，SHA2566877567a65c7811131fe38d17bb642fa906bcb0c10fa38c3ba636c70dcaafb5e；journal实际 READY ordinal3、唯一 R/S READY53567、无pending。Tester 未导出或额外 hash 该媒体。

## E6B-OBS-F01/P1：下一新 host 原 writer 死亡证明不可用

复现路径为同一已授权批次：MP4 完成且独立审证通过后，准确调用独立新 host 的 normalAviSixRealFrames。host11809 在 `E4DeviceTests.selectedFormalCaseOnly:71` 的 Before 返回：

`BLOCKED WRITER_DEATH:IOException:E5A_RECOVERY_WRITER_DEATH_UNPROVEN`

JUnit记录1项失败，未出现 FIXTURE/REPORT/TERMINAL_EXIT、CPU_TASK_STARTED/E4_SOURCE_FRAME/native diagnostic。AVI 没有进入测试主体，新增 CPU/输出/预留/消费均0；能力和 cancel 随即停止。原 writer 身份仍为 attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f/PID4869/UID10221/com.videokit.app/began1792224193301，未篡改归档或重新 ABORT。

静态定位 `android/com/videokit/spike/e4/E5N2RecoveryAndroid.java` 的 requireRecoveryWriterDead：查询既有 API `getHistoricalProcessExitReasons(package,owner.pid,8)`，按 PID/realUID/process/起始时间筛选；唯一匹配数量不为1，或匹配 reason≤0，均返回同一错误。该错误发生在 /proc absent 检查之前。**本次原日志未暴露实际列表、匹配数或 reason，具体根因 UNKNOWN**；不将历史记录淘汰、PID复用或旧 writer 仍活着当作已证事实。

前一个 host 的成功死亡证据不能替代本 host 的新观察。没有扩大历史读取、旁路门、伪造 proof、追加独立 OBSERVE、重试 AVI 或清理归档。该现象阻塞正常批次继续，交负责人/开发评估有界诊断及连续可审证的处理方案；不能直接弱化死亡/资源门。

AVI 的当前观察没有 admitted/actualReturnProven 成功证明，不记为观察成功；它在原 writer 校验阶段尚未进入 guard/媒体 session。instrumentation 客户端已返回，测试结束的系统进程清理见原日志；Tester 未发 force-stop/kill，也未以系统清理代替失败观察的实际成功证明。

## 资源与账本结算

稳定 budget730a73e1-50e1-4198-a515-047104f00e31，累计上限4194304/单输出2097152；未换 UUID、清账或删除产物。

| 输出任务 | 状态 | 已消费字节 |
|---|---|---:|
| 原 N2 86cafdb3-0fc4-447d-920b-b19c884bf494 | ABORTED；S0及原归档保持 | 0 |
| 原失败 0ee15550-8952-4639-91ac-83ab9d14d36c | ABORTED；失败产物保留 | 53651 |
| 本次 MP4 fbe4330b-111b-4b05-a93c-467413eb8d34 | READY；新产物保留 | 53567 |
| AVI及未执行后项 | 无新 R/S/输出 | 0 |

累计107218，reserved0，operation.pending不存在。逐行 hash 链/唯一 R/S 核验通过，账本 SHA256 f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba。AVI后账本与MP4后逐字节相同，原 N2归档/原fence/beforeimages/旧失败元数据保持。

本批19次ADB：安装2、instrumentation2、有限只读元数据15；全部客户端已返回/无溢出，保存219988字节原始输出。无设备/Gradle并发，产品方法各1次，无主动 force-stop/kill、QUERY/ABORT/独立 OBSERVE/G01、产品重试或超时放宽。

七 CPU 实际 readAt 共18次/压缩1167679字节（包含验证器1次/53567字节），逐任务与 broker 计数相符，均低于8192/64MiB。fixture 前后 hash 沿冻结正常路径推算仅2×349102=698204字节；AVI在fixture前停止，0次AVI全量hash。MP4输出生产三次digest沿冻结路径推算160701字节（前验/后验/结算），低于原三hash/6MiB；这些推算与实际 native 压缩读取按用途分开，不冒充独立I/O追踪。Tester额外媒体读取/导出/全量hash均0。

## 证据、审证修正及后续

完整原始输出、每次不可覆盖 attempt/receipt、安装前后私有元数据、分方法独立审证和资源账本汇总位于 `docs/tester/D1_E6B_NORMAL_EVIDENCE/`；总汇 `final-independent-review.json`，两正常准入状态 `two-normal-receipt-status.json` 明确 NOT_CREATED_NOT_ADMITTED/cancelAdmitted=false。

只读审证脚本发生两次留痕兼容修正：stage正则补数字以识别E4_SOURCE_FRAME；READY journal ordinal按冻结枚举纠正为3。只重新解析已保存原始证据，没有重跑产品或重复成功设备检查，未改变产品预期/原始结果；两次修正记录均保留。之后无额外兼容重试。

本次 MP4 单项 receipt 不满足两个正常前提，不能据其 SHA 启动 cancel。报告集中发负责人；保留阻塞现场，等待正式安排，不自动继续设备、复测或 M0。
