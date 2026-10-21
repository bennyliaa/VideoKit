# C07 集中设备追加说明 V1.0

日期：2026-10-05；候选D1-20261005-C07；计划，未执行。29入口编译保留（20 host+9 isolated），当前集中计划28项；ordinary历史严格FAIL不改，不再同条件派测。仅负责人明确授权后由tester独占指定设备/候选；coder本轮不ADB/设备，不改冻结包，不进入M0。CPU方案尚未选定，本批设备计划只验证已有Media3格式守卫及受影响回归，不测试未实现CPU方案。

## 身份、资料与保留边界

按freeze-summary/source-manifest/ZIP逐一核验源码与全部证据/4 APK hash，三debug同签名；只安装负责人所选Debug/Test/实验worker，unsigned Release只审计。先审目标旧包/签名/UID/私有副本/账本/成功输出和cache，保留C02–C06数据与备份，无自动卸载/清数据/恢复/删capture。C06两条capture已用满，其记录保留；C07只允许新前缀最多两条、每份2MiB输出上限，旧数据与总空间/预算须负责人审查，不按新前缀自动豁免存量。

fixtures仅basic.mp4、subtitle.avi、subtitle.srt、large.mkv，可信身份复用media-inventory及冻结原hash。新files/d1_c07_fixtures的复制/alias须长度/hash一致，不能以扩展名验证格式。私有cp复用不算Windows二进制传输工具通过，手机另行安排。新反例由测试内受控byte[]或只读provider映射生成，不改原媒体、不写共享目录、不上传。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| app-debug.apk | 40623273 | bc04b7401477ae4e5cccc7c9195f0c6f9abb76d63f4a3e757a2f7827f4922d6b |
| app-debug-androidTest.apk | 2383433 | e1fd95912071c03a299fd81950f91cd33f9ea98de196b50e0f9516553750911f |
| app-release-unsigned.apk | 21607782 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | 17045480 | d4d94f539a27796c59cba63ef0fc459ed4c4e991cfd14c72ee4771827c0e95bd |

## 顺序、真实断言与失败处理

1. sourceFormatValidControls：真实AVI/MP4各一次extractor.sniff、starts=matches=1/rejects=0，peek/read origin=0且重置；实际source归零。无Transformer/Sink/token。
2. sourceFormatWrongRouteAndInvalidHeaders：AVI路由给真实MP4、MP4路由给真实AVI，以及两种kind各空/4字节截断/64字节坏头。调用guard.read而非框架选型，必须在parser进入前得到SOURCE_FORMAT_*，attempts=1/matches=0，失败后第二read不得重新sniff绕过，源字节位置/peek reset和实际释放成立。
3. sourceFormatMatchedHeaderTruncatedBody：12字节RIFF/AVI头实际sniff匹配，但缺失body；真实AVI parser在最多8次read内因EOF/ParserException拒绝，不以sniff匹配宣称全容器有效，最终源释放，无Sink/token。
4. videoFrameCaptureMp4Control：通过相同MediaEngine显式guard，真实starts=matches>0/rejects=0的SOURCE_FORMAT_CAPTURE_GATE必须出现并断言；原2秒映射1–4秒片段内1秒，专用1视频0音频/full decode/fsync/非空帧/释放。
5. offlinePlatformFaceFeasibility：直接MP4控制，原AVI10秒retriever不足才用9–12秒片段内1秒回退；同guard实际匹配证据、专用验证/bitmap/取消和source/FD释放。MP4采帧控制失败则此依赖项BLOCKED；不得换0秒/空帧/仅MP4。actual source PTS UNKNOWN，候选数不是质量PASS。
6. 宿主realEncoderOutput与companion isolatedActualEncodeAndReadyRecovery正常前置后完整T01/T02和既有真实sample/跨owner/第二槽/租约回归；broker SIGSEGV/HANG各自独立NORMAL前置。播放MP4、AVI无SRT/有SRT、MKV/ASS受影响结构/Seek/释放也执行，自动静音不能判声音/字幕字形同步。

三个新format方法可独立执行；前置FAIL只阻断依赖项，不遮蔽其他安全恢复测试。格式反例只覆盖指定错误，不是全面恶意媒体fuzz。正式导出必须继续H264/AAC双轨各非零样本/3秒±150ms/严格PTS/full视频decode，video-only仅采帧、不发产品READY/token。

预算：sniff总32KiB/合作式5秒，每Routing read最多5秒，逐短读检查；不能因此声称native无条件可中断。format方法实际finally await source10秒、无输出FD；采帧done90秒、retriever20秒、主线程取消5秒、源释放10秒，默认无sample watchdog仍10秒。外部测试超时只收集当前task/PID/UID/阶段，不能代替实际source/FD/death/lease；未知quarantine，不主动清文件。日志须当前候选/源身份/设备/时间，不能复用C06运行PASS或旧PID8974作本轮事实。

## 入口清单

| 编译方法 | 本批状态 |
| --- | --- |
| C07DeviceTests.playbackMp4 | NOT_RUN |
| C07DeviceTests.playbackAviWithoutSrt | NOT_RUN |
| C07DeviceTests.playbackAviSrt | NOT_RUN |
| C07DeviceTests.playbackMkvAss | NOT_RUN |
| C07DeviceTests.realEncoderOutput | NOT_RUN |
| C07DeviceTests.outputValidationCounterexamples | NOT_RUN |
| C07DeviceTests.exportReadyResponseLoss | NOT_RUN |
| C07DeviceTests.exportWriteFault | NOT_RUN |
| C07DeviceTests.exportFlushFault | NOT_RUN |
| C07DeviceTests.exportValidationFault | NOT_RUN |
| C07DeviceTests.realPipelineImmediateCancel | NOT_RUN |
| C07DeviceTests.writingJournalRecovery | NOT_RUN |
| C07DeviceTests.isolatedWorkerDeathAndTimeout | NOT_RUN |
| C07DeviceTests.isolatedBrokerSigsegvIndependently | NOT_RUN |
| C07DeviceTests.isolatedBrokerHangIndependently | NOT_RUN |
| C07DeviceTests.videoFrameCaptureMp4Control | NOT_RUN |
| C07DeviceTests.sourceFormatValidControls | NOT_RUN |
| C07DeviceTests.sourceFormatWrongRouteAndInvalidHeaders | NOT_RUN |
| C07DeviceTests.sourceFormatMatchedHeaderTruncatedBody | NOT_RUN |
| C07DeviceTests.offlinePlatformFaceFeasibility | NOT_RUN |
| C07IsolatedDeviceTests.ordinaryIsolatedCodecOutcomeDoesNotReady | NOT_SCHEDULED；历史UNKNOWN=FAIL保留 |
| C07IsolatedDeviceTests.nativeLeaseSurvivesDuplicateDescriptorClose | NOT_RUN |
| C07IsolatedDeviceTests.isolatedActualEncodeAndReadyRecovery | NOT_RUN |
| C07IsolatedDeviceTests.cancelAfterActualVideoSample | NOT_RUN |
| C07IsolatedDeviceTests.workerExitDuringActualEncoding | NOT_RUN |
| C07IsolatedDeviceTests.workerSigsegvDuringActualEncoding | NOT_RUN |
| C07IsolatedDeviceTests.secondCodecTaskSurvivesFirstNativeCrash | NOT_RUN |
| C07IsolatedDeviceTests.actualHostDeathDuringEncodingAndCrossOwnerAbort | NOT_RUN |
| C07IsolatedDeviceTests.actualHostDeathAfterReadyAndSameTaskQuery | NOT_RUN |

结束统一报告28计划项实际PASS/FAIL/BLOCKED/NOT_RUN，单列未派测ordinary历史FAIL和“当前未执行”；不能以29个编译方法作29个设备通过。保留所有旧任务/素材及新成功/失败capture账本；无自动手机切换、Gradle设备任务或CPU二进制集成。SOURCE_FORMAT_*匹配门禁成功也只关闭本候选/设备覆盖，CPU产品路线和全部P0仍待独立准入。
