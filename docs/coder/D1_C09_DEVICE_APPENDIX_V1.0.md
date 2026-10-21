# C09 手机和平板统一交测说明

2026-10-16。coder仅本机，设备执行全部NOT_RUN。用户已明确授权手机和平板直接连接测试，无需重复询问；由负责人统一交tester，按手机→平板串行执行，不与开发构建交叉。不能把11天前型号/serial/UID当本次已核验事实。

## 前置、身份和数据

先核验冻结链和 `apk-audit.json` 的四包hash/签名，再有界记录本次serial、型号/API/ABI、页面大小、调试状态、实际已安装包/签名/用途、空间及现存数据。CPU要求ARM64/API31+；4KiB页成功不证明16KiB页运行。新app-debug和测试包同证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。版本名1.0不足以识别候选，需核对实际包hash与C09类/测试入口。

不卸载、不清数据、不覆盖未知文件；保留C01–C08及两份C06、两份C07 capture。CPU输入只需C09私有fixture目录的 `basic.mp4`（349102字节，hash720957c9…，实际已知8秒控制）及 `subtitle.avi`（736454656字节，hash3f0bf3e9…）。完整hash在既有素材清单/transfer工具；SRT和大MKV不属CPU本批必需。每设备新增fixture预算两文件共736803758字节，无CPU持久帧或输出文件；日志建议≤32MiB。只有识别清楚的C09目标可写，不默认删除或自动扩容；可在只读核验后复用相同内容，不能把旧目录存在当hash相同。工具 `transfer_fixtures.py` 默认PLAN_ONLY；coder没有执行其设备分支。

## 一次集中CPU组

只安装主APK及测试APK即可执行 `com.videokit.spike.c09.C09CpuDeviceTests`。CPU代码直接绑定同APK的nonexported ordinary isolated Service，完全不调用companion；即使设备保留旧companion也不能把其进程当CPU worker。所有17个方法已编译，均未运行：

| 组 | 方法 |
| --- | --- |
| 正常及seek | cpuMp4H264ActualPtsFrame；cpuAviMpeg4ActualPtsFrame；cpuSeekUsesNewEpochAndDecodedTimestamp |
| 原生累计配额/分配前检查 | cpuActualAggregateAllocationQuotaAndDecode；cpuOversizedDeclarationRejectedBeforeDecoderOpen |
| 损坏与格式 | cpuTruncatedInputRejectsAndReleases；cpuValidAviHeaderBadPacketRejects；cpuWrongDeclaredFormatRejects；cpuCompiledH263DoesNotExpandAcceptedInputCodec |
| 协议与契约 | cpuForgedFrameRejectedBeforeHostAllocation；cpuForgedEpochAndClaimedIdentityRejected；cpuUnknownAndEmptyLengthRejectWithActualClose |
| 取消/挂起/故障/第二槽 | cpuCancelActiveReadRetainsPendingSourceLedger；cpuCancelAfterActualFrame；cpuHungTaskBoundedStopAndDeath；cpuSelfSigsegvSignalMustBeProven；cpuSecondSlotAndHostSurviveFirstSelfCrash |

先正常MP4/AVI控制，再做相关反例及故障；正常native加载前置失败不能把负例泛化为通过，独立协议/纯账本项可独立继续。每方法一次有界执行，不为取得偶然PASS反复重跑未知信号。

记录CPU_TASK_STARTED、CPU_PREALLOC_BUDGET、CPU_NATIVE_STAGE、CPU_FRAME、CPU_EVENT和finally CPU_LEDGER。阶段1=header打开，2=实际codec/声明尺寸接受，3=decoder打开，4=seek完成，5=真实帧归一化，6=输入元数据策略拒绝且未创建decoder。超大声明反例须阶段6；有效头坏packet反例须真实decoder已开但无帧。正常帧记录FFmpeg版本、task/epoch、实际PID/isolated UID、源raw时间戳/time_base、best_effort标志、换算PTS、RGBA尺寸/字节、allocator current/peak及采样ru_maxrss。必要时与独立可信源帧时序比对；best-effort不能伪装精确PTS或效果质量通过。

SIGSEGV必须在真实CPU帧之后，先ARMED再实际death，不能先cleanup STOP。保存匹配task/PID/isolated UID/时间/进程名的原始crash/tombstone，同时分别保存App历史reason/status/trace/cause。App status0仍UNKNOWN/FAIL；原始signal11不能写回App cause，cleanup kill9不能冒充目标故障。双槽须第二任务真实帧、不同PID/isolated UID、故障后继续完成及宿主实际存活。系统原始证据无法取得则明确独立故障证据未闭合，不宣称全P0隔离。

finally须查询实际Binder death、source operations/consumers/failedCloses/close和slot状态。timeout不是停工：pending provider即使worker死也保持未释放，待其实际完成才归零。未知death/失败close保留slot/quarantine，不靠任意PID kill或force-stop制造释放。CPU不创建READY/输出token；无文件不是释放证明。

## 同批受影响旧回归，分组报告

CPU组结束后可统一执行host组 `realEncoderOutput`、`outputValidationCounterexamples`、`exportReadyResponseLoss`、`exportWriteFault`、`exportFlushFault`、`exportValidationFault`、`writingJournalRecovery`。需要旧companion回归时再核验并使用冻结 `worker-debug.apk`，只归入legacy组：`nativeLeaseSurvivesDuplicateDescriptorClose`、`isolatedActualEncodeAndReadyRecovery`、`cancelAfterActualVideoSample`、`workerExitDuringActualEncoding`、`workerSigsegvDuringActualEncoding`、`secondCodecTaskSurvivesFirstNativeCrash`、`actualHostDeathDuringEncodingAndCrossOwnerAbort`、`actualHostDeathAfterReadyAndSameTaskQuery`。不与CPU组并发；跨后端统一预算不是本批已证能力。

正式导出仍要求H264/AAC双轨各自非零、实际PTS/full decode及T02精确stage/hits/cause；采帧1视频0音频与CPU裸帧不能替代。新终态输出建议≤32项/8MiB，超预算停止新增并记录，不自动清理。既有capture不增设新批次来消耗缓存。

`ordinaryIsolatedCodecOutcomeDoesNotReady` 和C07旧broker SIGSEGV FAIL不列自动重跑，历史UNKNOWN/FAIL不改写。其他已编译入口未调度则写NOT_SCHEDULED。手机/平板、CPU/legacy/纯规则、App信号/外部raw、人工效果分别报告。设备测试结果由tester另出，不能从本说明生成PASS。
