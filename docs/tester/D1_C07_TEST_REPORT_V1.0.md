# D1 C07 集中回归测试报告 V1.0

日期：2026-10-05；候选D1-20261005-C07。依据D1_C07_TESTER_REQUIREMENTS_V1.0.md顶部15:01交接及C07_DEVICE_APPENDIX。自动批次电脑时间15:07:13～15:10:25。

结论：28计划项均执行，27 PASS、1 FAIL、0 BLOCKED/NOT_RUN（计划内方法级）。三个格式守卫新入口及MP4/AVI采帧实际sniff匹配门禁通过，C06 sniff覆盖缺口在此候选/平板/样本范围得到复验。唯一当前方法FAIL为普通broker SIGSEGV的App退出signal与原始崩溃不一致。ordinary编译方法本轮NOT_SCHEDULED，历史UNKNOWN=FAIL保留，不改判通过。两CPU方案仅独立文档审核，未准入/实现，不计设备通过。D1仍未通过、不进入M0。

## 身份、更新与预算

仅HA1Q6WXR/TB138FC、Android12 API31/arm64-v8a，包UID app10221/test10222/worker10220。实际C06三包先拉回核验SHA对应冻结记录，保存APK、路径/dumpsys及cache原字节恢复备份，再同签名授权install-r，三包Success。证书SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。

最终清单SHA256 b6bc17f919adba3bb2d837fb456382ec02650229d6ce352607136dea3d557572、ZIP0f642a5e389d932bc97521f14b0444bf5ad0cd0efd9dcdd6ccc4c4fe10313b4e与交接指定一致；冻结2026-10-05T14:53:43.658880+08:00，5产物/99证据/119源码及ZIP条目全部匹配。

| 安装APK | 字节 | SHA256 |
| --- | ---: | --- |
| app-debug-androidTest.apk | 2383433 | e1fd95912071c03a299fd81950f91cd33f9ea98de196b50e0f9516553750911f |
| app-debug.apk | 40623273 | bc04b7401477ae4e5cccc7c9195f0c6f9abb76d63f4a3e757a2f7827f4922d6b |
| worker-debug.apk | 17045480 | d4d94f539a27796c59cba63ef0fc459ed4c4e991cfd14c72ee4771827c0e95bd |

[冻结核验](D1_C07_EVIDENCE/freeze-check.json)、[旧包身份/恢复路径](D1_C07_EVIDENCE/c06-update-preflight.json)、[安装](D1_C07_EVIDENCE/update.log)。c06-installed-*.apk与c06-cache-before-update.tar保留，不自动恢复/降级。未卸载/清数据、unsigned release、Gradle、手机/模拟器或CPU二进制集成。

更新前/data可用94600532 KiB，实际cache9308 KiB；C06两capture输出443451/456031字节及对应账本确认保留。结束cache12980 KiB；本次只新增两份C07 capture输出，每份≤2MiB，未按前缀无限重置预算。用前后原字节tar逐一比对C06两输出/两账本，SHA和长度未变；[存量及新预算核验](D1_C07_EVIDENCE/capture-budget-check.json)。当前授权两条新增预算已满，不重跑增加或自动删除。

## 素材与执行

核验旧C06四私有副本SHA后生成新files/d1_c07_fixtures，目标长度/SHA一致；basic349102、AVI736454656、SRT93550、MKV3212959911字节，总3949857219。旧目录/电脑源只读，不上传、不共享目录中转；结束再验C07 basic、C07 AVI、旧C06 AVI，hash不变。[素材身份](D1_C07_EVIDENCE/fixture-hash-check.json)、[结束源hash](D1_C07_EVIDENCE/source-after-hashes.txt)。私有cp不是Windows传输设备通过。

先三个独立格式控制/反例，再正常编码、MP4采帧及对应依赖安全回归；故障没有遮蔽独立后续项。逐方法单独instrumentation、外部180～360秒上限，本轮无外部超时；只按当前方法设备开始时间/App与companion UID采集协议，再按对应PID截取原始crash，不移用旧候选日志。时钟有偏差，不混用设备/电脑时间计算性能。

## 28计划项实际结果

| 方法 | 结果 | 覆盖及限制 | 日志 |
| --- | --- | --- | --- |
| sourceFormatValidControls | PASS | 真实AVI/MP4各一次sniff，starts/matches1、rejects0、origin与peek重置/释放。 | [日志](D1_C07_EVIDENCE/sourceFormatValidControls.log) |
| sourceFormatWrongRouteAndInvalidHeaders | PASS | 2错路由＋2种kind各空/4字节截断/64坏头，共8反例；首read拒绝、不允许重试绕过、源释放。 | [日志](D1_C07_EVIDENCE/sourceFormatWrongRouteAndInvalidHeaders.log) |
| sourceFormatMatchedHeaderTruncatedBody | PASS | 12字节RIFF/AVI头sniff匹配；真实parser最多8次read内EOF/ParserException拒绝；无Sink/token。 | [日志](D1_C07_EVIDENCE/sourceFormatMatchedHeaderTruncatedBody.log) |
| realEncoderOutput | PASS | 宿主 H264/AAC、256×144、3秒、非零双轨/严格PTS/视频decode/READY 门禁通过。 | [日志](D1_C07_EVIDENCE/realEncoderOutput.log) |
| videoFrameCaptureMp4Control | PASS | 实际SOURCE_FORMAT_CAPTURE_GATE starts1/matches1/rejects0；专用单视频验证/非空帧/释放。 | [日志](D1_C07_EVIDENCE/videoFrameCaptureMp4Control.log) |
| isolatedActualEncodeAndReadyRecovery | PASS | companion异UID/PID、broker字节、有效真实视频sample、decode验证、死亡/源排空、READY同task恢复。 | [日志](D1_C07_EVIDENCE/isolatedActualEncodeAndReadyRecovery.log) |
| outputValidationCounterexamples | PASS | 12个规则反例与拒绝未缩放剪辑原片；不是 decoder fuzz。 | [日志](D1_C07_EVIDENCE/outputValidationCounterexamples.log) |
| exportReadyResponseLoss | PASS | 编码完成；响应丢失后同task查询 READY/token，重开一致。 | [日志](D1_C07_EVIDENCE/exportReadyResponseLoss.log) |
| exportWriteFault | PASS | stage=write、hits=1、code7001、正确注入cause、abort 无 READY。 | [日志](D1_C07_EVIDENCE/exportWriteFault.log) |
| exportFlushFault | PASS | stage=flush、hits=1、code7001；已有字节、正确注入cause、abort 无 READY。 | [日志](D1_C07_EVIDENCE/exportFlushFault.log) |
| exportValidationFault | PASS | 编码/fsync/字节完成后 stage=validate、hits=1、OUTPUT_VALIDATION_FAILED。 | [日志](D1_C07_EVIDENCE/exportValidationFault.log) |
| realPipelineImmediateCancel | PASS | 实际 Transformer 立即取消及输入排空；不是sample后取消。 | [日志](D1_C07_EVIDENCE/realPipelineImmediateCancel.log) |
| writingJournalRecovery | PASS | WRITING账本恢复/abort；不是宿主实际死亡。 | [日志](D1_C07_EVIDENCE/writingJournalRecovery.log) |
| isolatedWorkerDeathAndTimeout | PASS | 本轮NORMAL/PRESSURE/EXIT、认证模式ACK、故障与实际死亡/source排空断言通过。 | [日志](D1_C07_EVIDENCE/isolatedWorkerDeathAndTimeout.log) |
| isolatedBrokerSigsegvIndependently | FAIL | FAIL：App历史记录signal0，原始本次tombstone signal11；死亡/源排空true，不改自动结果。 | [日志](D1_C07_EVIDENCE/isolatedBrokerSigsegvIndependently.log) |
| isolatedBrokerHangIndependently | PASS | 独立NORMAL后HANG，WAIT_BEGIN/hits1、精确WORKER_TIMEOUT、有界等待/死亡/source排空。 | [日志](D1_C07_EVIDENCE/isolatedBrokerHangIndependently.log) |
| nativeLeaseSurvivesDuplicateDescriptorClose | PASS | 锁竞争、重复FD关闭及abort原生语义。 | [日志](D1_C07_EVIDENCE/nativeLeaseSurvivesDuplicateDescriptorClose.log) |
| cancelAfterActualVideoSample | PASS | 实际H264 sample后取消、死亡、租约/source释放、partial删除且无READY。 | [日志](D1_C07_EVIDENCE/cancelAfterActualVideoSample.log) |
| workerExitDuringActualEncoding | PASS | 实际H264 sample后自身EXIT、死亡与abort/source门禁。 | [日志](D1_C07_EVIDENCE/workerExitDuringActualEncoding.log) |
| workerSigsegvDuringActualEncoding | PASS | companion实际H264 sample后自身SIGSEGV、死亡与abort/source门禁。 | [日志](D1_C07_EVIDENCE/workerSigsegvDuringActualEncoding.log) |
| secondCodecTaskSurvivesFirstNativeCrash | PASS | 两任务真实sample，不同PID同UID；首任务崩溃后第二任务存活、完成验证/READY。 | [日志](D1_C07_EVIDENCE/secondCodecTaskSurvivesFirstNativeCrash.log) |
| actualHostDeathDuringEncodingAndCrossOwnerAbort | PASS | sample后helper宿主自杀；新owner租约恢复并同task abort，无READY。 | [日志](D1_C07_EVIDENCE/actualHostDeathDuringEncodingAndCrossOwnerAbort.log) |
| actualHostDeathAfterReadyAndSameTaskQuery | PASS | durable READY后helper死亡；新owner原task/token一致且abort保留成功输出。 | [日志](D1_C07_EVIDENCE/actualHostDeathAfterReadyAndSameTaskQuery.log) |
| playbackMp4 | PASS | 结构/5次Seek/短播放/源排空通过；静音自动用例。 | [日志](D1_C07_EVIDENCE/playbackMp4.log) |
| playbackAviWithoutSrt | PASS | 无SRT对照结构/Seek/短播放/释放通过。 | [日志](D1_C07_EVIDENCE/playbackAviWithoutSrt.log) |
| playbackAviSrt | PASS | 有SRT轨选择/开关/Seek/播放/释放通过；字形效果另核查。 | [日志](D1_C07_EVIDENCE/playbackAviSrt.log) |
| playbackMkvAss | PASS | ASS轨选择/开关/Seek/播放/释放通过；自动静音不判声音。 | [日志](D1_C07_EVIDENCE/playbackMkvAss.log) |
| offlinePlatformFaceFeasibility | PASS | AVI原10秒直接空，9～12秒回退；实际匹配gate、90样本/full decode/非空帧与释放；质量NOT_RUN。 | [日志](D1_C07_EVIDENCE/offlinePlatformFaceFeasibility.log) |

[完整结果/依赖/命令/时间](D1_C07_EVIDENCE/tablet-batch-results.json)、[控制台](D1_C07_EVIDENCE/tablet-batch-console.log)。另有编译入口ordinaryIsolatedCodecOutcomeDoesNotReady：NOT_SCHEDULED，当前未执行，历史严格UNKNOWN FAIL保留；不能以29编译方法声称29设备通过。

## 实际sniff与采帧门禁复验

有效控制真实AVI/MP4各执行一次实际extractor.sniff，attempts/matches1、rejects0，原输入位置与peek均归零，source实际释放。错误路由2项和两kind各空/4字节截断/64字节坏头共8反例，经guard.read在parser前得到SOURCE_FORMAT_*；attempts1/matches0，第二read返回原拒绝异常，不能更换输入重试绕过，最终源排空，无Sink/token。12字节RIFF/AVI头的sniff实际匹配后，真实parser在最多8read内拒绝截断body，证明头匹配不等于全容器有效。仅这些指定反例，不是完整恶意媒体fuzz。

MP4采帧和AVI回退各自记录SOURCE_FORMAT_CAPTURE_GATE starts=1 matches=1 rejects=0，并断言allMatched才准输出验证。实际匹配发生在当前采帧源读取链，补上C06只有typed init/read而无独立sniff的缺口；格式探测32KiB/合作式5秒及短读预算仍不能证明任意native调用可硬中断。

AVI先直接原10秒scaled/unscaled空，稳定错误后使用同源9～12秒片段内1秒OPTION_CLOSEST，H264256×144、1视频0音频、90有效样本/payload56608字节、严格PTS/全视频decode/EOS/帧数/fsync及非空bitmap通过。MP4控制同独立契约先通过；采帧不发产品READY/token，正式宿主/companion双轨H264/AAC导出门禁保持并复验通过。

AVI最终source_released=true、transformer_cancel_returned=true、output_descriptors_closed=true，capture账本/片段保留。actual_source_frame_pts=UNKNOWN，platform_face_candidates=0、quality=NOT_RUN；不等于精确源帧或检测率通过，不将原10秒换成0秒/MP4替代。

[有效sniff协议](D1_C07_EVIDENCE/sourceFormatValidControls-uid10221.log)、[错格式](D1_C07_EVIDENCE/sourceFormatWrongRouteAndInvalidHeaders-uid10221.log)、[截断body](D1_C07_EVIDENCE/sourceFormatMatchedHeaderTruncatedBody-uid10221.log)、[MP4实际匹配](D1_C07_EVIDENCE/videoFrameCaptureMp4Control-uid10221.log)、[AVI匹配/验证/释放](D1_C07_EVIDENCE/offlinePlatformFaceFeasibility-uid10221.log)。

## 剩余失败与释放独立事实

TABLET-C07-01（高）：isolatedBrokerSigsegvIndependently在mode2的OS匹配SIGSEGV断言FAIL。同步SIGSEGV_ARMED、模式/hits1、无正常RPC和实际Binder death已到达；App ExitEvidence PID12438/isolated UID99025、matched=true、reason5、signal0、causeUNKNOWN、APP_TRACE_ABSENT，未满足signal11。最终death=true、source_released=true、operations/consumers/failed_closes全0。

本次对应原始tombstone匹配同PID12438/UID99025/进程/时间，signal11(SIGSEGV)、SI_TKILL。据此可独立记录实际native SIGSEGV事实，但不能注入App原因、代替其历史记录断言或改自动FAIL。为何App匹配记录status0与原始signal11不同尚未证明，可能的记录时序问题仅是假设；不无限重跑获取偶然PASS。真实媒体companion sample后SIGSEGV、独立HANG本轮PASS，不能互相替代。

[当前协议/最终排空](D1_C07_EVIDENCE/isolatedBrokerSigsegvIndependently-uid10221.log)、[对应原始crash](D1_C07_EVIDENCE/isolatedBrokerSigsegvIndependently-tombstone-pid12438.log)。这条分类断言FAIL的实际源释放已证明，不笼统标quarantine；其他未知资源仍按实际事实保留隔离。ordinary本轮不派测，不新增其死亡或资源结论。

## CPU两方案独立文档审核

[独立审核报告](D1_C07_CPU_OPTIONS_REVIEW_V1.0.md)对照原需求与精确版本官方文本；仅文档审查，不计上述28项设备通过，也不选择或批准路线。

方案A是FFmpeg CPU解析/解码＋宿主系统编码，方案B是FFmpeg＋OpenH264 CPU全编码/封装；两者规划ordinary isolated、独立CPU输出验证、单App/AAR、opaque source/Sink、TOCTOU复制校验和资源协议。共同未实现项包括检测/跟踪/图片/复杂字幕、独立Kit接入、真实高风险完整链、崩溃/挂起终止/资源边界与最低设备性能。A仍需证明宿主JNI/渲染/系统codec客户端不会违反§27；B仍需性能、输出质量及软件编码发行准入。文档边界充分说明这些缺口，没有实际产品证据。

FFmpeg n8.0的LGPL基线/GPL组件与外部配置条件及OpenH264 v2.6.0源码许可/Cisco二进制专利安排已按官方文本独立核对，原文区分方向正确；完整源码/config/ELF/SBOM/hash、真实漏洞和宿主/商店/专利义务仍未审定，不以禁gpl参数或动态链接单独批准。详见独立审核的官方链接。两方案均NOT_ADMITTED/NOT_IMPLEMENTED，无CPU二进制进入当前候选。

## 结束与未覆盖项

本次App和companion已停止，所有旧素材/任务/成功输出及C06/C07 capture保留；cache-before/after原字节备份可审查。没有自动清理或手机切换，App停止不能代替实际死亡/Source/FD/lease证明。

正式正常编码、T01规则反例、T02精确stage/hits/cause、READY恢复、真实sample cancel/EXIT/SIGSEGV、第二槽、跨owner及锁语义按表范围通过；不外推全产品隔离或native OOM。播放自动静音只验结构/Seek/字幕轨及源排空，C07人工声音/完整字形/ASS样式/同步/旋转/前后台仍NOT_RUN，不移用C04用户反馈。

手机AVI/SRT与AC3、Windows真实传输、模型权利/标注质量/精确PTS、NAS/权限满盘/native OOM/12路并发/完整P0和供应链仍未闭合。当前28计划项全部执行不等于D1通过，ordinary历史FAIL和本轮SIGSEGV证据差异均保留；下一批由负责人整体交接。
