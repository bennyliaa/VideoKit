# D1 C12 集中测试报告 V1.0

报告时间：2026-10-16T11:11:58+08:00。候选 D1-20261016-C12，git_commit=null。执行依据：D1_PHONE_TEST_EXECUTION_V1.0 顶部 C12 正式交接、D1_C12_TESTER_REQUIREMENTS_V1.0、C12交付、HANDSHAKE_BINDING_DESIGN、DEVICE_APPENDIX、LICENSE_BUILD_ADMISSION及冻结device_plan.json。

## 结论

**本批结束：平板52项全部PASS，手机52项ENVIRONMENT_BLOCKED。D1仍未通过，不进入M0。** 平板正常注册/解码、取消撤销、代次隔离及指定host/legacy路径已有本轮实测通过证据；手机被系统禁用、App trace未取得及完整产品/发行门禁分别保留，不外推全面完成。

| 设备 | CPU37 | host7 | legacy8 | 合计 |
| --- | --- | --- | --- | --- |
| OPPO PDYM20 / U4999DLBNRR89DOR | 37 ENVIRONMENT_BLOCKED | 7 ENVIRONMENT_BLOCKED | 8 ENVIRONMENT_BLOCKED | 52环境阻断，0次C12 instrumentation |
| Lenovo TB138FC / HA1Q6WXR | 37 PASS | 7 PASS | 8 PASS | 52 PASS，52次单方法完整执行 |

两设备实际API31、ARM64、4096字节页。手机当前及结束enabled=2、lastDisabledCaller=com.oplus.athena；有限预检/备份后停止相关组，未启用、安装C12、卸载、清数据或启动测试。用户正确设置页没有启用按钮的既有证据保留，没有重复要求用户寻找或绕过。

## 候选与安装身份

独立冻结核验 179 源文件、115 证据文件、5产物PASS，独占复制并复核字节/hash。冻结时间2026-10-16T10:58:49.608887+08:00。冻结ZIP而非浮动工作树是本轮源码身份；未运行Gradle或修改产品/冻结件。详见 [freeze-check](D1_C12_EVIDENCE/freeze-check.json)、[admission-check](D1_C12_EVIDENCE/admission-check.json)。

| 对象 | SHA256 |
| --- | --- |
| freeze-summary | 8fbde727e4ef900088ee17739bf2382ad9ed8cdb54bb3af99eb65a4b9847ddc6 |
| source ZIP | cf6c67bde094a53dfc14a9d0e59bc2cb2c549db2ec49199b388c17901a0c39b5 |
| app-debug-androidTest.apk | 597773c8114a35803081958c3d02652fcd640521446fb28b89e850e68a17f56c |
| app-debug.apk | 63d68e172f0723a90a9eba525c21c407d2307314cdc996415d73e0580b78a981 |
| app-release-unsigned.apk | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | ad48aa864583d8a86532ec22bd3a57dfd0e0976f23afae4da89a49cd0b91b135 |

三个Debug包签名PASS，证书SHA256：5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。平板旧C11 main/test和可读缓存先备份，再同签名保留数据更新；实际安装main/test回读hash与冻结一致。CPU仅main/test，host结束才备份并更新legacy worker，最终回读worker hash一致。手机旧包/缓存备份后因禁用未更新。未安装release-unsigned。

16个native条目独立核验实际库hash、ZIP_STORED/偏移和ELF对齐，五个FFmpeg/allocator库与既有准入基线逐字节一致；release仍与旧对照一致。静态16KiB布局不是16KiB页设备运行。交付707 JVM＋28脚本＝735项为本机自检证据，未计入52设备PASS。

## 执行及逐项结果

手机→平板串行，每次一个明确方法及独占attempt目录；只运行冻结52项，不按整类批跑。正常MP4/AVI先通过完整资源前置后运行依赖项。没有失败或超时，没有续跑、重试、强停、覆盖证据或同条件碰理想信号；两SIGSEGV因注册/撤销代次路径改变各只验证一次。所有实际方法均有OK(1 test)和instrumentation终态，随后独立审查账本及raw。框架正常结束instrumentation与tester手动force-stop分开，本轮未手动kill/force-stop。

手机EB=ENVIRONMENT_BLOCKED，统一证据phone/environment.json、preflight.json、package-at-end.txt。平板每项原始证据在 `D1_C12_EVIDENCE/tablet/attempts/方法名/`，含command/result/post；总表为results.json。[runtime-review](D1_C12_EVIDENCE/runtime-review.json)独立审查首次/每代身份、媒体仅主端点、真实death与slot顺序、注册flags及最终解绑/Source/在途；[execution-audit](D1_C12_EVIDENCE/execution-audit.json)核对52次终态和原始legacy故障。

| 序号 | 组 | 方法 | 手机 | 平板 |
| --- | --- | --- | --- | --- |
| 01 | cpu | cpuEnvironmentPreflight | EB | PASS |
| 02 | cpu | cpuMp4H264ActualPtsFrame | EB | PASS |
| 03 | cpu | cpuAviMpeg4ActualPtsFrame | EB | PASS |
| 04 | cpu | cpuCleanupWithoutBindProvesNoWorker | EB | PASS |
| 05 | cpu | cpuFirstFailureSurvivesCleanupFailure | EB | PASS |
| 06 | cpu | cpuActualAggregateAllocationQuotaAndDecode | EB | PASS |
| 07 | cpu | cpuSeekUsesNewEpochAndDecodedTimestamp | EB | PASS |
| 08 | cpu | cpuOversizedDeclarationRejectedBeforeDecoderOpen | EB | PASS |
| 09 | cpu | cpuTruncatedInputRejectsAndReleases | EB | PASS |
| 10 | cpu | cpuValidAviHeaderBadPacketRejects | EB | PASS |
| 11 | cpu | cpuWrongDeclaredFormatRejects | EB | PASS |
| 12 | cpu | cpuCompiledH263DoesNotExpandAcceptedInputCodec | EB | PASS |
| 13 | cpu | cpuForgedFrameRejectedBeforeHostAllocation | EB | PASS |
| 14 | cpu | cpuForgedEpochAndClaimedIdentityRejected | EB | PASS |
| 15 | cpu | cpuUnknownAndEmptyLengthRejectWithActualClose | EB | PASS |
| 16 | cpu | cpuCancelActiveReadRetainsPendingSourceLedger | EB | PASS |
| 17 | cpu | cpuCancelAfterActualFrame | EB | PASS |
| 18 | cpu | cpuHungTaskBoundedStopAndDeath | EB | PASS |
| 19 | cpu | cpuStopAckLossStillRequiresActualDeath | EB | PASS |
| 20 | cpu | cpuStalledStopDoesNotConsumeSecondRpcSlot | EB | PASS |
| 21 | cpu | cpuCancelFromMainThreadDoesNotBlockSecondTask | EB | PASS |
| 22 | cpu | cpuWrongStopEpochRejectedAndTaskContinues | EB | PASS |
| 23 | cpu | cpuOnewayStopRejectedAndTaskContinues | EB | PASS |
| 24 | cpu | cpuRegistrarSynchronousMetadataAndRejects | EB | PASS |
| 25 | cpu | cpuRegistrarLocalHostIdentityRejected | EB | PASS |
| 26 | cpu | cpuRegistrationBadMagicPreservesFirstCause | EB | PASS |
| 27 | cpu | cpuRegistrationTrailingReplyPreservesFirstCause | EB | PASS |
| 28 | cpu | cpuCancelBeforeRegistrationClosesBindingAndRetainsUnknown | EB | PASS |
| 29 | cpu | cpuCancelBeforeBindReturnRevokesLateAcceptance | EB | PASS |
| 30 | cpu | cpuUnbindFailureRequiresExplicitRecovery | EB | PASS |
| 31 | cpu | cpuDuplicateConnectionKeepsOriginalIdentity | EB | PASS |
| 32 | cpu | cpuCancelDuringHelloCannotStartOrRevive | EB | PASS |
| 33 | cpu | cpuRejectedExtraWorkerRetainsSlotAndSecondTask | EB | PASS |
| 34 | cpu | cpuLateWorkerCannotBorrowOriginalDeath | EB | PASS |
| 35 | cpu | cpuExitCollectionRejectsMainThread | EB | PASS |
| 36 | cpu | cpuSelfSigsegvSignalMustBeProven | EB | PASS |
| 37 | cpu | cpuSecondSlotAndHostSurviveFirstSelfCrash | EB | PASS |
| 38 | host | realEncoderOutput | EB | PASS |
| 39 | host | outputValidationCounterexamples | EB | PASS |
| 40 | host | exportReadyResponseLoss | EB | PASS |
| 41 | host | exportWriteFault | EB | PASS |
| 42 | host | exportFlushFault | EB | PASS |
| 43 | host | exportValidationFault | EB | PASS |
| 44 | host | writingJournalRecovery | EB | PASS |
| 45 | legacy | nativeLeaseSurvivesDuplicateDescriptorClose | EB | PASS |
| 46 | legacy | isolatedActualEncodeAndReadyRecovery | EB | PASS |
| 47 | legacy | cancelAfterActualVideoSample | EB | PASS |
| 48 | legacy | workerExitDuringActualEncoding | EB | PASS |
| 49 | legacy | workerSigsegvDuringActualEncoding | EB | PASS |
| 50 | legacy | secondCodecTaskSurvivesFirstNativeCrash | EB | PASS |
| 51 | legacy | actualHostDeathDuringEncodingAndCrossOwnerAbort | EB | PASS |
| 52 | legacy | actualHostDeathAfterReadyAndSameTaskQuery | EB | PASS |

## 注册与正常媒体证据

MP4 task=feb617eb678f435eb7e30d29e4b8fbc0 / epoch3016554717990026504，generation1，PID11177/UID99066。接收端CPU_REGISTRATION_DIAG记录code1、flags18、input_bytes204、CPU_REG_OK；真实RGBA147456 bytes，raw24576、time_base1/12288、pts_us2000000、best_effort0。最终该代实际death、Source CLOSED、pending_calls0、stop_pendingfalse、binding_closedtrue、global_unproven0、reserved_cpu_slots0、slot_releasedtrue均有记录。解绑result=UNBOUND_WAIT_DEATH本身不充当死亡证明。

AVI真实帧raw300、time_base83417/2500000、pts_us10010040、best_effort1、RGBA147456 bytes；allocation_peak15179327、peak_rss173444KiB。只证明本片段真实帧/时间戳，best-effort不写成原始PTS，FFmpeg申请额度不冒充全进程RSS限制。

registrar远端正/负例：PID13500/UID99089，同步接收flags18/50成功或DUPLICATE；OK1次、DUPLICATE5次，始终generation1，只有一次CPU_TASK_STARTED。oneway实际flags17两次、19一次、51一次，caller_pid0，全部CPU_REG_ONEWAY拒绝，无登记权限；CODE、DESCRIPTOR、SESSION、ENDPOINT、INPUT各拒绝一次。实际接收值与发送参数分开，不能由C12 flags反推C11未记录的实际值。LocalHostIdentity仅Android本地Binder负例，未冒充远端错误内核身份覆盖。

BadMagic/TrailingReply各PASS，实际worker失败回报进入REGISTER阶段，宿主首次原因分别CPU_REG_REPLY_MAGIC、CPU_REG_REPLY_TRAILING，未降为CONNECT超时；start_ack=false、native_stage0、Source撤销及端点实际死亡/绑定/slot最终回收有证据。固定primitive应答校验与反例通过，不使用异常反序列化放行。

## 撤销、代次和全局预算证据

CancelBeforeRegistration与BeforeBindReturn各PASS。中间实际记录binding_closed=true、unresolved_workers1、global_unproven_workers2、reserved_cpu_slots2；目标pid/uid=-1、actual_death=false、no_worker_proven=false、pending_calls1、source CLOSED、slot_releasedfalse。第三任务被拒、第二任务继续真实完成。说明解绑成功没有抹掉已在途注册/未知端点，等待start不占有清理监视器。解除调试闸门后迟到端点返回RETIRED，仅认证撤销；每代真实death、全部调用返回后才回收至全局0。此处迟到登记是已记录在途的REGISTER，不是解绑后凭空创建并放行的新未知进程。

UnbindFailureRequiresExplicitRecovery：第一次attempt1为UNBIND_FAILED，closed=false且slot保留；重复cancel不自动重试；显式recover产生attempt2并实际closed=true，之后再结合真实death与无在途释放。未把解绑成功或恢复返回替代死亡。

重复连接/HELLO取消、额外worker与旧death重放各PASS。额外端点样例：第一任务generation1 PID14563/UID99099、generation2 PID14627/UID99101；晚到样例generation1 PID14736/UID99102、generation2 PID14784/UID99104。初始身份没有改写，旧death不赋给generation2；额外端点仍活时slot不释放、第三任务被拒且第二任务继续解码。host日志中START/预算/帧仅来自原两主端点，额外端点没有START/source/媒体配额，最终所有已记录代次实际死亡。

独立逐事件审查未发现generation身份改变、媒体发给非primary、登记发生在slot已释放之后，或已登记代次未证死亡时slot放行；最终各任务pending_calls/STOP pending/解绑pending/bind_in_flight均清零，Source实际关闭，已绑定任务closed=true。MAX_WORKERS4仍是每任务历史/异常端点记录上限，不是2×4解码许可；本轮实际额外端点覆盖不外推全部framework创建顺序或永久溢出实测。

ACK丢失、STOP在途不占普通RPC、主线程取消、wrong epoch/oneway拒绝、未知空长度/无绑定源关闭及原始异常保留均PASS。无绑定释放是no_worker_proven，不是已创建worker死亡；ACK丢失仍独立要求真实death。调试解绑闸门只用于指定反例，未将其作为生产行为。

## SIGSEGV与App退出/trace分栏

| 入口 | 原任务worker / 外部raw | App原始系统字段 | App trace | 方法 |
| --- | --- | --- | --- | --- |
| self SIGSEGV | PID15059 / UID99105 / raw11 | matched=true、reason5、signal11、SYSTEM_SIGNAL_PROVEN | 三次APP_TRACE_ABSENT，trace_signal=-1、trace_sha空、cause UNKNOWN | PASS |
| 双槽首任务SIGSEGV | PID15175 / UID99106 / raw11 | matched=true、reason5、signal11、SYSTEM_SIGNAL_PROVEN | 三次APP_TRACE_ABSENT，trace_signal=-1、trace_sha空、cause UNKNOWN | PASS |

两项均真实帧→ARMED→cleanup前代次death，任务/epoch/PID/isolated UID/时间/进程的raw匹配；目标stop_attempts0，未用STOP的SIG9充当目标11。双槽第二worker PID15193/UID99107在首任务死亡后实际继续完成、宿主PID不变。没有重复尝试求signal11；这是本次改变路径后的单次观察，不证明OEM状态永远稳定。

每次采集器线程有3条读取结果日志，加1条调用方返回日志，不是4次打开流。CPU严格规则原本允许原OS非零11且native trace缺失，此次PASS依据真实系统signal11，不是外部raw回填或trace替代。App trace未取得，不能声称protobuf匹配或死因解释通过；status0路径本次未出现，仍UNKNOWN/FAIL，历史C10原status0 FAIL不回写。主线程拒绝用例PASS；永久读阻塞、close失败等更广条件仍不能由本次无trace外推已实测。

host7全部PASS，覆盖真实H264/AAC双轨/PTS/full decode及READY/abort/reconcile、响应丢失与写/flush/验证故障、journal恢复。legacy8全部PASS，仅为历史companion路径回归，不代替正式CPU/Kit隔离或App trace能力。

- legacy raw：workerSigsegvDuringActualEncoding PID16936/UID10220，signal11；原始证据post/legacy-worker.log。该方法未额外断言App退出分类，不能补足App trace证据。
- legacy raw：secondCodecTaskSurvivesFirstNativeCrash PID17133/UID10220，signal11；原始证据post/legacy-worker.log。该方法未额外断言App退出分类，不能补足App trace证据。

## 集中缺陷/门禁状态

| 编号/输入 | 本轮状态 | 限定结论/剩余 |
| --- | --- | --- |
| C11-T01 注册握手 | 已覆盖路径PASS | 正常MP4/AVI、实际metadata/oneway/坏reply及稳定首因实测通过；旧C11 FAIL不改 |
| C11-T02 未知绑定取消收敛 | 已覆盖路径PASS | 注册在途/迟到bind、独立解绑、显式失败恢复和预算保留通过；不承诺全部系统竞态 |
| C10-T02 代次身份/旧death混用 | 已覆盖路径PASS | 额外端点和迟到death反例、原SIGSEGV路径首次身份固定；不以末尾ps空补PASS |
| C10-T01 App退出信号/trace | 当前两方法PASS，trace限制保留 | 本轮原OS11，三次trace为空；历史status0未改判、也未在本次复现 |
| C12-ENV01 手机禁用 | ENVIRONMENT_BLOCKED | 52项未执行；不据平板结果外推手机，不要求寻找不存在按钮 |
| C12-LIM01 App native trace缺失 | 证据限制OPEN | 实际APP_TRACE_ABSENT；不降低门槛，不在同条件下重跑求trace |

本轮合格平板指定52项未发现新的断言或独立资源证据失败；这不等于关闭完整D1、产品/发行门禁。C01–C11历史报告保持。

## 数据、预算与结束状态

| 设备 | 新C12输出字节 | task/journal | 日志/文本字节 | 旧capture |
| --- | ---: | ---: | ---: | --- |
| 手机 | 0 / 8388608 | 0 / 32 | 31700 / 33554432 | 0文件哈希未变 |
| 平板 | 2735217 / 8388608 | 15 / 32 | 1925949 / 33554432 | 8文件哈希未变 |

日志读取/写入时实施限额，最终预算非删除旧证据所得。cache-before/after-c12.tar、output-budget-final.json、log-budget-final.json已留存；平板旧C06/C07 capture8文件未变，手机0文件，未生成新capture。CPU不落持久帧/READY。新fixture只basic.mp4与subtitle.avi，总736803758字节，前后hash一致：720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9、3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f。源只读/旧fixture和原素材保留，空间满足前置；fixture不计新输出预算。

52次平板instrumentation均完整结束，无重试或未知执行；结束进程/服务快照无VideoKit残留，当前无在途设备方法。手机未启动C12方法，结束仍禁用且无VideoKit进程/服务。未清理数据、降级或修改启用状态。末尾快照仅证明结束状态，方法PASS另有期限内代次/Source/slot证据。

## 设计、开源与未完成范围

正式Flutter＋独立Kit/AAR、Media3薄适配保持。本轮是单APK普通隔离Debug胶水；FFmpeg官方8.0.3及配额/输入白名单继承，未重写codec、未扩新依赖/权限/组件、模型或crash handler。自有变化限RegistrationProtocol/BindingRevocation及必要JNI/生命周期适配。完整对应源、NOTICE/SBOM、266对象/608依赖及既有维护/安全证据继承；未宣称重跑GPG、重建FFmpeg或新全面漏洞扫描。动态链接/Debug通过不自动满足外发、替换/再链接、商店、专利或产品授权条件。

仍需手机合格环境覆盖、16KiB页设备、完整Kit/多宿主/Flutter产品、可信媒体质量全变体、系统编码显示和宿主JNI、模型/其他流水线、全P0及发行条件。历史ordinary UNKNOWN未调度或关闭；人工声音/字幕反馈仅属于旧候选。本批不自行派下一候选或追加方法，提交集中结果后等待负责人安排。D1未通过，不进入M0。
