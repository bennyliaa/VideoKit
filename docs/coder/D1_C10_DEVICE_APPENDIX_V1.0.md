# C10 手机/平板集中验证说明

2026-10-16。本文件是冻结后的统一计划，coder未执行设备命令。用户已有手机/平板测试授权；负责人统一交tester，串行安排、不得与构建或其他设备批次争用。最新状态仍须现场核验，不从C09型号/serial/连接推断已就绪。

## 先硬性检查环境和身份

C09手机U4999DLBNRR89DOR/PDYM20曾enabled=2，系统拒绝shell启用，保持人工解除前置；平板HA1Q6WXR/TB138FC曾可用。这只是历史定位，C10实际serial/型号/API/ABI/页大小、包和组件enabled、Service可见性、已装包hash/签名/用途及空间须重新核验。CPU要求ARM64/API31+；4KiB设备成功不代表16KiB页运行。

App禁用/隐藏/挂起、组件禁用或Service不可见：标ENVIRONMENT_BLOCKED/UNKNOWN并停止相关组，不跑到解码器反例求FAIL，不尝试绕过系统启用限制、卸载或清数据。确需人工解除时只说明手机实际必要动作，不重新索取已有测试授权。脚本不包含启用命令。安装成功、命令exit0或host纯方法通过都不代表Service可用。

`device_guard.py` 检查命令退出、当前user、实际enabled与独立Service查询；只接受独立组件行，错误文本即使exit0也拒绝。App内@Before及每次start另读实际PackageManager状态；输出C10_ENVIRONMENT_READY/BLOCKED，assumption/blocked不能计PASS。

## 包、数据和记录预算

按 `apk-audit.json` 核验主包和测试包实际hash，再核验三debug包同证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。版本名1.0不足以识别候选。CPU只用主/测试APK，不安装或调用companion；旧companion若已保留不当作CPU证据。

保留C01–C09私有数据、旧包/cache及C06/C07 capture，不清理或覆盖未知目录。新 `files/d1_c10_fixtures` 仅需basic.mp4和subtitle.avi，共736803758字节；输入源hash沿用已核验清单。transfer工具默认PLAN_ONLY，显式执行前也硬性检查enabled/Service与命令退出，已有结果文件拒绝覆盖。需要暂存空间时沿用总fixture＋最大单文件＋256MiB余量检查。允许只读复核后的已知数据复用，不把存在当身份一致。

每设备日志总预算32MiB，新legacy终态输出建议≤32项/8MiB。CPU不写持久帧/READY输出。`run_device_c10.py` 默认PLAN_ONLY；执行时必须指定已复核的serial/method、独占attempt-dir、设备级log-budget-root与candidate/data review。读取时限制日志并独占创建文件，不先写完整输出再检查大小。只运行一个明确方法，失败退出非0，不继续调度；每次尝试保留，不覆盖之前结果。

结果必须区分ENVIRONMENT_BLOCKED、ENVIRONMENT_UNKNOWN/PREPARATION_FAILED、TEST_FAILED、EXECUTION_UNKNOWN和方法断言通过。真实断言FAIL不能改记环境阻断；超时/本机adb子进程结束不能当远端停工/释放证明。辅助工具不会force-stop或任意PID kill；遇未收回执行，停止下一方法并由负责人查明状态。

## 一次整组：25 CPU/生命周期 + 7 host + 8 legacy

先 `cpuEnvironmentPreflight`，正常 `cpuMp4H264ActualPtsFrame`、`cpuAviMpeg4ActualPtsFrame` 必须包含finally最终门禁。之后按依赖执行全部冻结 `C10CpuDeviceTests` 25方法，不逐功能换包：

| 类别 | 入口 |
| --- | --- |
| 原17项覆盖 | 真实MP4/AVI/PTS、新task/epoch seek、真实累计配额拒绝和恢复、超大声明、截断头/有效头坏packet、错格式/H263拒绝、伪frame/epoch/claimed UID、未知/空长度实际close、实际read后取消、帧后取消、HANG、native SIGSEGV、第二CPU槽存活 |
| 新环境/诊断/资源 | cpuEnvironmentPreflight；cpuCleanupWithoutBindProvesNoWorker；cpuFirstFailureSurvivesCleanupFailure |
| 新停止/并发 | cpuStopAckLossStillRequiresActualDeath；cpuStalledStopDoesNotConsumeSecondRpcSlot；cpuCancelFromMainThreadDoesNotBlockSecondTask |
| 新严格认证反例 | cpuWrongStopEpochRejectedAndTaskContinues；cpuOnewayStopRejectedAndTaskContinues |

正常控制未过只阻断相关native依赖，独立项的可运行性另判，不能把任意异常当反例通过。开启参考故障模式仅限这些Debug测试；STOP_STALL须在finally经认证释放闸门，无法收回则保留quarantine/FAIL。

记录task/epoch、宿主与worker实际UID/PID、调用flags、CPU_HELLO_VALIDATED、CPU_STOP_GRANTED/RESULT、first_code/phase/category、primary及suppressed cleanup、binding/identity/start_ack、stop_attempts/ack/pending/result、pending_calls、实际death、source operations/consumers/failedCloses/close和slot。保存oneway反例实际caller PID/UID，不预写一定为0；必须见拒绝计数且原任务可继续。错误epochSTOP必须被拒且worker存活，随后合法STOP成功。

正常STOP允许ACK已见后实际死亡、或ACK未获而真实死亡独立证据闭合；ACK本身不等于死亡。ACK-loss专项应保存服务授权日志和宿主响应分类。没有worker创建可证时no_worker_proven=true、actual_death=false可以释放纯宿主资源；不能把它记成实际worker死亡。已绑定、连接超时/身份未知均不能靠超时回收slot；在途调用/未完成provider也不能清零。

显式恢复可查 `lifecycle()/sourceLedger()/abandonedSourceLedgers()`，后台线程调用 `recover`、`recoverRetainedTasks` 或 `recoverAbandonedSources`，单预算1～15000ms；STOP最多3次且不重叠，真实pending期间不可叠加调用。失败close沿用原3次有界恢复。`close()`只发起取消/记录，不在UI做同步STOP、等待或unbind；实际完成必须由后台stopAndAwait/recover证实。

native自身SIGSEGV必须在真实帧后ARMED、cleanup之前实际death，精确匹配PID/isolated UID/task/时间/进程名原始crash。App历史reason/status/trace/cause与外部raw分别保存，status0仍UNKNOWN/FAIL，不用cleanup死亡、系统isolated not needed或末尾ps为空替代故障和期限内释放证明。第二槽必须有真实帧并继续完成，宿主实际存活。PTS raw/time_base/best_effort逐项留存，AVI best-effort不是精确原始PTS质量通过。

CPU组结束后同包执行host七项：realEncoderOutput、outputValidationCounterexamples、exportReadyResponseLoss、exportWriteFault、exportFlushFault、exportValidationFault、writingJournalRecovery。legacy八项另核验/使用worker-debug.apk：nativeLeaseSurvivesDuplicateDescriptorClose、isolatedActualEncodeAndReadyRecovery、cancelAfterActualVideoSample、workerExitDuringActualEncoding、workerSigsegvDuringActualEncoding、secondCodecTaskSurvivesFirstNativeCrash、actualHostDeathDuringEncodingAndCrossOwnerAbort、actualHostDeathAfterReadyAndSameTaskQuery。两组不与CPU并发。

正式H264/AAC双轨各自非零、真实PTS/full decode及T02精确stage/hits/cause不降低；CPU裸帧和旧companion互不替代。旧ordinary UNKNOWN、C07 signal FAIL不自动重跑/回写。每设备40项按实际方法/依赖/前置分类，不以旧C09 PASS冒充C10。D1/正式Kit/AAR/Flutter产品/模型权利/全P0和发行仍未通过。
