# D1 C06 集中回归测试报告 V1.0

日期：2026-10-05；冻结候选D1-20261005-C06。依据D1_C06_TESTER_REQUIREMENTS_V1.0.md顶部14:11交接。自动批次电脑时间14:15:03～14:18:06。

结论：批次已结束，26入口全部执行，25 PASS、1 FAIL、0 BLOCKED/NOT_RUN（方法级）。新增MP4视频采帧控制通过，AVI原10秒映射回退取得非空帧并完成视频专用完整验证；正式双轨导出与全部既有安全恢复门禁重新通过。唯一自动失败是ordinary codec探针的App原因UNKNOWN，按当前未改变的退出准则维持FAIL。外部匹配native死因与实际最终释放单独记录。报告复核另发现采帧typed Extractor的实际sniff匹配事件缺失，单列需求覆盖缺口，不改冻结方法结果。D1仍未通过、不进入M0，手机、源帧实际PTS和检测质量仍未闭合。

## 候选、设备与保留数据更新

仅操作HA1Q6WXR / TB138FC、Android12 API31、arm64-v8a；原平板1536×2560/density320，包UID app10221/test10222/worker10220。更新前空间98472836 KiB。实际C05三包先拉回核验SHA与C05冻结APK完全一致，保存APK、包路径/dumpsys及cache原字节备份；任务用途明确后执行授权install-r，三包全部Success，同签名证书SHA256为5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。

核验最终清单1fc7ef1b294c8e2dd11d3b547385bcec2875540bbc1428f939bfdbd198ae6f0d及源码ZIP fc0e041aa3048f9fbce301aa3d3b80b95bda8343e5dee4dc696ab159aaf77634，与正式交接指定值一致。冻结时点2026-10-05T14:04:31.962588+08:00；5个产物、97个证据文件、114个源码/ZIP条目全部核验通过。

| 安装APK | 字节 | SHA256 |
| --- | ---: | --- |
| app-debug-androidTest.apk | 2308821 | de25e0fe50eb5e0c30e554b67b06a91cd6f5a42f543a4edd756cd935b09e6687 |
| app-debug.apk | 40623273 | a01b2b088dc9e8284d308b3bec774d33609870000f634ade228579646a27e969 |
| worker-debug.apk | 17045480 | 616769985e150841743007379ec456d9e5e00a01792981424778d5c751026e16 |

[冻结核验](D1_C06_EVIDENCE/freeze-check.json)、[旧包身份及恢复路径](D1_C06_EVIDENCE/c05-update-preflight.json)、[安装日志](D1_C06_EVIDENCE/update.log)。c05-installed-*.apk、c05-cache-before-update.tar保留；[备份SHA及目录清单](D1_C06_EVIDENCE/backup-manifest.json)。不自动降级或恢复；没有卸载/清数据、unsigned release安装、Gradle、手机/模拟器操作或修改冻结件。

## 可信素材与执行边界

重新核验C05四份私有副本SHA后，在全新files/d1_c06_fixtures生成C06副本并验证长度/hash，保留旧目录和电脑源，不上传、不共享目录中转。basic.mp4 349102字节、subtitle.avi736454656、subtitle.srt93550、large.mkv3212959911，共3949857219字节；[完整素材身份](D1_C06_EVIDENCE/fixture-hash-check.json)。结束再次验证C06 basic/C06 AVI/旧C05 AVI仍与可信hash一致，见[source-after-hashes](D1_C06_EVIDENCE/source-after-hashes.txt)。私有cp复用不是Windows传输工具设备通过。

逐方法instrumentation，180～360秒外部上限，本轮无外部超时。宿主正常导出、companion正常编码和新增MP4采帧控制均先成功，对应依赖项实际执行。SIGSEGV和HANG各自独立NORMAL前置、互不遮蔽。日志按当前方法设备开始时间和App/companion UID采集；isolated PID从当前协议确认，原始crash只保存匹配本次PID/com.videokit进程块，不用旧C05 PID5588。设备与电脑时钟有偏差，不混算执行性能。

## 26入口结果

| 方法 | 结果 | 实际覆盖及限制 | 日志 |
| --- | --- | --- | --- |
| realEncoderOutput | PASS | 宿主 H264/AAC、256×144、3秒、非零双轨/严格PTS/视频decode/READY 门禁通过。 | [日志](D1_C06_EVIDENCE/realEncoderOutput.log) |
| videoFrameCaptureMp4Control | PASS | 采帧专用MP4原2秒映射1～4秒片段内1秒；1视频0音频/full decode/fsync/非空帧与最终释放。 | [日志](D1_C06_EVIDENCE/videoFrameCaptureMp4Control.log) |
| isolatedActualEncodeAndReadyRecovery | PASS | companion异UID/PID、broker字节、有效真实视频sample、decode验证、死亡/源排空、READY同task恢复。 | [日志](D1_C06_EVIDENCE/isolatedActualEncodeAndReadyRecovery.log) |
| outputValidationCounterexamples | PASS | 12个规则反例与拒绝未缩放剪辑原片；不是 decoder fuzz。 | [日志](D1_C06_EVIDENCE/outputValidationCounterexamples.log) |
| exportReadyResponseLoss | PASS | 编码完成；响应丢失后同task查询 READY/token，重开一致。 | [日志](D1_C06_EVIDENCE/exportReadyResponseLoss.log) |
| exportWriteFault | PASS | stage=write、hits=1、code7001、正确注入cause、abort 无 READY。 | [日志](D1_C06_EVIDENCE/exportWriteFault.log) |
| exportFlushFault | PASS | stage=flush、hits=1、code7001；已有字节、正确注入cause、abort 无 READY。 | [日志](D1_C06_EVIDENCE/exportFlushFault.log) |
| exportValidationFault | PASS | 编码/fsync/字节完成后 stage=validate、hits=1、OUTPUT_VALIDATION_FAILED。 | [日志](D1_C06_EVIDENCE/exportValidationFault.log) |
| realPipelineImmediateCancel | PASS | 实际 Transformer 立即取消及输入排空；不是sample后取消。 | [日志](D1_C06_EVIDENCE/realPipelineImmediateCancel.log) |
| writingJournalRecovery | PASS | WRITING账本恢复/abort；不是宿主实际死亡。 | [日志](D1_C06_EVIDENCE/writingJournalRecovery.log) |
| isolatedWorkerDeathAndTimeout | PASS | 本轮NORMAL/PRESSURE/EXIT、认证模式ACK、故障与实际死亡/source排空断言通过。 | [日志](D1_C06_EVIDENCE/isolatedWorkerDeathAndTimeout.log) |
| isolatedBrokerSigsegvIndependently | PASS | 独立NORMAL后SIGSEGV，ARMED/hits1、无正常RPC、实际死亡及匹配OS signal11/source排空。 | [日志](D1_C06_EVIDENCE/isolatedBrokerSigsegvIndependently.log) |
| isolatedBrokerHangIndependently | PASS | 独立NORMAL后HANG，WAIT_BEGIN/hits1、精确WORKER_TIMEOUT、有界等待/死亡/source排空。 | [日志](D1_C06_EVIDENCE/isolatedBrokerHangIndependently.log) |
| ordinaryIsolatedCodecOutcomeDoesNotReady | FAIL | App trace_status=APP_TRACE_ABSENT，UNKNOWN维持FAIL；外部死因独立保存，最终释放全true。 | [日志](D1_C06_EVIDENCE/ordinaryIsolatedCodecOutcomeDoesNotReady.log) |
| nativeLeaseSurvivesDuplicateDescriptorClose | PASS | 锁竞争、重复FD关闭及abort原生语义。 | [日志](D1_C06_EVIDENCE/nativeLeaseSurvivesDuplicateDescriptorClose.log) |
| cancelAfterActualVideoSample | PASS | 实际H264 sample后取消、死亡、租约/source释放、partial删除且无READY。 | [日志](D1_C06_EVIDENCE/cancelAfterActualVideoSample.log) |
| workerExitDuringActualEncoding | PASS | 实际H264 sample后自身EXIT、死亡与abort/source门禁。 | [日志](D1_C06_EVIDENCE/workerExitDuringActualEncoding.log) |
| workerSigsegvDuringActualEncoding | PASS | companion实际H264 sample后自身SIGSEGV、死亡与abort/source门禁。 | [日志](D1_C06_EVIDENCE/workerSigsegvDuringActualEncoding.log) |
| secondCodecTaskSurvivesFirstNativeCrash | PASS | 两任务真实sample，不同PID同UID；首任务崩溃后第二任务存活、完成验证/READY。 | [日志](D1_C06_EVIDENCE/secondCodecTaskSurvivesFirstNativeCrash.log) |
| actualHostDeathDuringEncodingAndCrossOwnerAbort | PASS | sample后helper宿主自杀；新owner租约恢复并同task abort，无READY。 | [日志](D1_C06_EVIDENCE/actualHostDeathDuringEncodingAndCrossOwnerAbort.log) |
| actualHostDeathAfterReadyAndSameTaskQuery | PASS | durable READY后helper死亡；新owner原task/token一致且abort保留成功输出。 | [日志](D1_C06_EVIDENCE/actualHostDeathAfterReadyAndSameTaskQuery.log) |
| playbackMp4 | PASS | 结构/5次Seek/短播放/源排空通过；静音自动用例。 | [日志](D1_C06_EVIDENCE/playbackMp4.log) |
| playbackAviWithoutSrt | PASS | 无SRT对照结构/Seek/短播放/释放通过。 | [日志](D1_C06_EVIDENCE/playbackAviWithoutSrt.log) |
| playbackAviSrt | PASS | 有SRT轨选择/开关/Seek/播放/释放通过；字形效果另核查。 | [日志](D1_C06_EVIDENCE/playbackAviSrt.log) |
| playbackMkvAss | PASS | ASS轨选择/开关/Seek/播放/释放通过；自动静音不判声音。 | [日志](D1_C06_EVIDENCE/playbackMkvAss.log) |
| offlinePlatformFaceFeasibility | PASS | 直接AVI原10秒空；视频-only回退9～12秒片段内1秒非空，90样本/full decode/fsync/释放；质量NOT_RUN。 | [日志](D1_C06_EVIDENCE/offlinePlatformFaceFeasibility.log) |

[完整结果/时间/依赖/命令](D1_C06_EVIDENCE/tablet-batch-results.json)、[控制台](D1_C06_EVIDENCE/tablet-batch-console.log)。PASS只覆盖冻结断言，不表示所有效果、性能或产品验收通过。

## 视频采帧控制与AVI原10秒回退

MP4采帧控制实际请求原2秒，片段1～4秒、片段内1秒；输出H264256×144、1视频0音频，经3秒时长/严格PTS/非零样本/全视频decode/EOS/帧数/末PTS及fsync门禁。71个编码样本、编码payload43856字节，片段metadata时长2958ms，取帧非空，最终source_released=true、transformer_cancel_returned=true、output_descriptors_closed=true。

AVI方法先运行直接MP4 2秒控制，然后原AVI10秒scaled/unscaled均空，稳定FRAME_AT_REQUESTED_TIME_UNAVAILABLE触发回退。回退记录source=AVI、clip_start_ms9000/end12000、requested_source_us10000000、requested_clip_us1000000、watchdog_ms10000。typed AviExtractor实际init/read成功，输入视频video/mp4v-es624×352及音频audio/mpeg被识别，视频decoder实际创建；音频输入存在不代表采帧输出带音频。当前采帧日志未出现EXTRACTOR_SNIFF_BEGIN/END，不能宣称实际sniff匹配已证明。

AVI回退输出90个有效视频样本、编码payload56608字节，H264256×144、1视频0音频，完成fsync/严格PTS/full decode/EOS/帧数及3秒验证；片段metadata3003ms，在片段内1秒OPTION_CLOSEST取帧非空。FRAME_CAPTURE_VIDEO_VALIDATED source=AVI、product_ready=false；最终源和输出描述符释放均true，retriever generation也released=true。默认10秒无sample watchdog没有延长，本轮不再触发C05无sample失败。

保留两份.capture账本及对应片段：MP4控制1109c78a-d8ba-4323-ae72-1c44dc44410d、AVI6dda0d88-4d49-41ed-822e-07af2e92da33；当前文件长度443451与456031字节（区别于编码payload），完整cache已备份。两条采帧预算已用完，不重跑/清理；下一批须按负责人审查安排。

这只是独立VIDEO_CAPTURE_ONLY契约，sink不产生产品READY/token。正式编辑导出仍强制H264/AAC双轨，各自非零样本、3秒±150ms、严格PTS和完整视频解码；本轮realEncoderOutput及T01/T02均通过，未用视频-only替代正式双轨输出。

actual_source_frame_pts=UNKNOWN；platform_face_candidates=0，仅检测调用可行性，不是无漏检、正确率或精确10秒源帧验收。转码可有损，quality=NOT_RUN；此host Debug采帧方案不是已隔离的最终检测/遮罩流水线。

[MP4采帧阶段](D1_C06_EVIDENCE/videoFrameCaptureMp4Control-uid10221.log)、[AVI完整阶段/释放](D1_C06_EVIDENCE/offlinePlatformFaceFeasibility-uid10221.log)、[cache列表](D1_C06_EVIDENCE/cache-after-batch.txt)。TABLET-C05-02在本候选/此平板/当前样本的回退可行性复验通过，直接AVI retriever限制仍存在；不外推手机或所有AVI。

附加覆盖缺口TABLET-C06-02（中）：appendix要求typed Extractor仍实际sniff匹配源，但本轮MP4/AVI采帧日志没有独立sniff事件；冻结MediaEngine的typed factory只返回一个指定Extractor，TracingExtractors的sniff若被调用应记录BEGIN/END。未证实缺失原因，不把单候选与跳过sniff的关联写成已确认根因。冻结方法没有此断言，因此原方法PASS保持，需求层实际sniff门禁未闭合。已有可信fixture身份和真实读取/验证支持当前采帧可行性，但不能替代该指定覆盖；缓存预算已满，不重跑或修改冻结源码补断言。

## ordinary严格FAIL与外部死因分开记录

本次task3fc4f602-80ef-4c85-a27c-c13741363103、PID8974、isolated UID99020。同步阶段PROBE_LEASE_ACQUIRED/PROBE_CODEC_CREATE_BEGIN后WORKER_DIED。App记录matched=true、reason5、signal6、cause=UNKNOWN、trace_status=APP_TRACE_ABSENT、trace_sha空；java_call_failed=false、native_abort_with_cause=false、permission_denial_proven=false。严格分类断言ORDINARY_CODEC_OUTCOME_UNPROVEN仍FAIL，不人工改PASS、不扩大allowlist、不实施退出准则提案。

独立外部原始tombstone匹配此C06 PID/UID/进程与当前时间，signal6(SIGABRT)，Abort message为`Check failed: serviceManager Hardware service manager is not running.` 栈含libcodec2_client.so的Codec2Client::GetServiceNames/ListComponents与Codec2InfoBuilder。它支持“当前匹配进程codec创建阶段枚举codec2服务时native abort”的外部事实，不是App已识别原因，不证明全局服务停机、权限拒绝或产品隔离验收。没有引用旧C05进程原始栈作为本轮原因。

finally实际death=true、source_released=true、lease_clear=true，冻结方法检查无token；分类失败与最终释放事实分开。本轮此条资源释放已证实，不笼统标未排空；若其他路径资源未知仍应quarantine，不能用测试App停止替代证明。

[App内阶段/traceStatus/最终释放](D1_C06_EVIDENCE/ordinaryIsolatedCodecOutcomeDoesNotReady-uid10221.log)、[C06对应原始tombstone](D1_C06_EVIDENCE/ordinaryIsolatedCodecOutcomeDoesNotReady-tombstone-pid8974.log)。剩余TABLET-C06-01：高，App内native trace缺失及严格分类未闭合。按负责人既定UNKNOWN=FAIL继续保留，退出准则须负责人另行审定；本报告不批准降低门禁。

## 既有恢复、人工范围与结束保留

正式宿主及companion正常编码、T01规则反例、T02 write/flush/validate精确stage/hits1/cause、READY丢响应同task/token、即刻取消/账本、普通broker NORMAL/PRESSURE/EXIT及独立SIGSEGV/HANG、真实sample后的cancel/EXIT/SIGSEGV、第二槽存活、实际宿主死亡/跨ownerabort和READY、原生dup-close锁语义全部重新通过。规则反例不是恶意MP4真机fuzz；普通broker源账本不是媒体输出Writer lease。

MP4/AVI无SRT/AVI SRT/MKV ASS静音自动播放、5次Seek、字幕轨开关与源排空通过；不判实际声音或完整字幕效果。C06人工声音、ASS全样式/对白同步、旋转/前后台/RTL均NOT_RUN，未把旧C04人工反馈移作本轮。手机AVI/无声与Windows传输工具仍另行补测。

整批结束已停止本次App和companion，未清数据、卸载、更换候选或操作手机。旧C05账本/失败帧记录、C05/C06私有素材、所有lease/owner、成功输出、两份capture与完整cache备份保留。停止不替代实际释放证明；本轮ordinary和采帧最终状态已分别证明，graphics完全释放不单由cancel返回推断。

模型权利、标注质量、精确PTS、NAS不协作、权限/满盘、native OOM/12路并发、完整P0和产品隔离/分发及供应链风险仍未闭合。D1尚未通过，不据25个限定PASS进入M0；下一批由负责人整体交接。
