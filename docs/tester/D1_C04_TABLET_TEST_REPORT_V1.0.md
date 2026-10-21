# D1 C04 平板测试报告 V1.0

日期：2026-10-05。候选 D1-20261005-C04；依据 D1_C04_TABLET_TESTER_REQUIREMENTS_V1.0.md。自动批次电脑时间 12:15:49～12:21:42。

结论：23入口均已执行，20 PASS、3 FAIL、0 BLOCKED、0 NOT_RUN（方法级）。核心正常导出和companion恢复前置通过，全部依赖项实际执行。仍有普通isolated能力探针、broker SIGSEGV、AVI同时间点取帧三项失败；D1 未全量通过，C04仍 NOT_READY，不进入M0。人工矩阵及手机回归不计入这23个自动方法。

## 设备与保留数据更新

目标HA1Q6WXR / TB138FC，Android12 API31，arm64-v8a；原C03平板1536×2560/density320。首次检查不在线，记录WAITING_FOR_TABLET；用户回复“平板已连接”后复核身份再继续。更新前可用106206132 KiB，包UID app10221/test10222/worker10220。

更新前三包身份/dumpsys/路径及实际已安装APK保存于证据目录，分别与冻结C03 hash一致；cache原字节备份 c03-cache-before-update.tar，包括任务账本/owner/lease。恢复审查路径见 c03-update-preflight.json 和对应 c03-installed-*.apk；备份保留，不自动降级/恢复或清数据。随后三包 install-r 全部Success，UID未变；未卸载、未覆盖未知数据、未运行Gradle、未修改冻结件。没有操作手机或模拟器。

[更新前身份和恢复清单](D1_C04_TABLET_EVIDENCE/c03-update-preflight.json)、[安装日志](D1_C04_TABLET_EVIDENCE/update.log)、[更新后UID](D1_C04_TABLET_EVIDENCE/c04-package-uids.txt)。

## 已完成的离线门禁

冻结时点 2026-10-05T12:06:25.396182+08:00；独立运行只读冻结核验工具，5 个产物、97 个证据文件、ZIP 100 个源码文件及对应源码 hash 全部通过。源码 ZIP SHA256 37088cfc579db1f9ac7ad567d78d12ba1d6cd71fd21b5b4c9023c21fc4943402；freeze-summary SHA256 3085520db7458d3bf2da45df0361b2ede350b3b9b02ab1be84cc63a93bf9a472。

三份 APK 独立验证同签名，证书 SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f，与本任务 C03 证书一致。重连后已逐包拉取实际安装APK，hash与本任务C03三包一致，身份可核对；之后才执行授权保留数据更新。

| APK | SHA256 |
| --- | --- |
| app-debug.apk | f2d3a9473f27f5281a0214e04a821bca7a6fc579a5f9a1d9ffb50c539e62e937 |
| app-debug-androidTest.apk | c70362b629030f4a27e66a51a50e69b5e4834f7e54718d23682ab2b6969a8c13 |
| worker-debug.apk | ad1f9785218bb996c5b25c8f24eeb7e1080101c7690b0ec857f5a51a4d90fdc5 |

[冻结检查](D1_C04_TABLET_EVIDENCE/freeze-check.json)、[连接检查](D1_C04_TABLET_EVIDENCE/connection-preflight.txt)，三份签名日志和按 ZIP 原字节提取的测试源码见同证据目录。


## 素材与源保护

冻结源码 DeviceFixtures 读取独立 files/d1_c04_fixtures。已逐一重新核验C03四份私有副本与原可信SHA，然后在同App私有目录复制到全新C04目录并验证目标长度/hash；原C03目录及电脑源未修改，没有上传或共享目录中转，没有再次传输约4GB。

basic.mp4 349102字节；subtitle.avi 736454656；subtitle.srt 93550；large.mkv 3212959911，总3949857219字节。每项完整SHA、源/目的路径见[素材校验](D1_C04_TABLET_EVIDENCE/fixture-hash-check.json)。本轮没有执行C04传输工具的设备跨Windows复制，故该工具设备能力仍NOT_RUN；旧传输缺陷不能据私有cp绕过关闭。

## 逐方法结果

| 方法 | 结果 | 实际覆盖 | 证据 |
| --- | --- | --- | --- |
| isolatedWorkerDeathAndTimeout | FAIL | FAIL 在 SIGSEGV mode2；NORMAL0、PRESSURE3、EXIT1 已进入并继续，HANG 未执行。 | [日志](D1_C04_TABLET_EVIDENCE/isolatedWorkerDeathAndTimeout.log) |
| realEncoderOutput | PASS | 宿主 H264/AAC、256×144、3秒、非零双轨/严格PTS/视频decode/READY 门禁通过。 | [日志](D1_C04_TABLET_EVIDENCE/realEncoderOutput.log) |
| outputValidationCounterexamples | PASS | 12个规则反例与拒绝未缩放剪辑原片；不是 decoder fuzz。 | [日志](D1_C04_TABLET_EVIDENCE/outputValidationCounterexamples.log) |
| exportReadyResponseLoss | PASS | 编码完成；响应丢失后同task查询 READY/token，重开一致。 | [日志](D1_C04_TABLET_EVIDENCE/exportReadyResponseLoss.log) |
| exportWriteFault | PASS | stage=write、hits=1、code7001、正确注入cause、abort 无 READY。 | [日志](D1_C04_TABLET_EVIDENCE/exportWriteFault.log) |
| exportFlushFault | PASS | stage=flush、hits=1、code7001；已有字节、正确注入cause、abort 无 READY。 | [日志](D1_C04_TABLET_EVIDENCE/exportFlushFault.log) |
| exportValidationFault | PASS | 编码/fsync/字节完成后 stage=validate、hits=1、OUTPUT_VALIDATION_FAILED。 | [日志](D1_C04_TABLET_EVIDENCE/exportValidationFault.log) |
| realPipelineImmediateCancel | PASS | 实际 Transformer 立即取消及输入排空；不是sample后取消。 | [日志](D1_C04_TABLET_EVIDENCE/realPipelineImmediateCancel.log) |
| writingJournalRecovery | PASS | WRITING账本恢复/abort；不是宿主实际死亡。 | [日志](D1_C04_TABLET_EVIDENCE/writingJournalRecovery.log) |
| ordinaryIsolatedCodecDenialDoesNotReady | FAIL | 预期 ISOLATED_CODEC_CAPABILITY_DENIED，实际 WORKER_DIED；不能算明确拒绝通过。 | [日志](D1_C04_TABLET_EVIDENCE/ordinaryIsolatedCodecDenialDoesNotReady.log) |
| nativeLeaseSurvivesDuplicateDescriptorClose | PASS | 锁竞争、重复FD关闭及abort原生语义。 | [日志](D1_C04_TABLET_EVIDENCE/nativeLeaseSurvivesDuplicateDescriptorClose.log) |
| isolatedActualEncodeAndReadyRecovery | PASS | companion异UID/PID、broker字节、有效真实视频sample、decode验证、死亡/源排空、READY同task恢复。 | [日志](D1_C04_TABLET_EVIDENCE/isolatedActualEncodeAndReadyRecovery.log) |
| cancelAfterActualVideoSample | PASS | 实际H264 sample后取消、死亡、租约/source释放、partial删除且无READY。 | [日志](D1_C04_TABLET_EVIDENCE/cancelAfterActualVideoSample.log) |
| workerExitDuringActualEncoding | PASS | 实际H264 sample后自身EXIT、死亡与abort/source门禁。 | [日志](D1_C04_TABLET_EVIDENCE/workerExitDuringActualEncoding.log) |
| workerSigsegvDuringActualEncoding | PASS | companion实际H264 sample后自身SIGSEGV、死亡与abort/source门禁。 | [日志](D1_C04_TABLET_EVIDENCE/workerSigsegvDuringActualEncoding.log) |
| secondCodecTaskSurvivesFirstNativeCrash | PASS | 两任务真实sample，不同PID同UID；首任务崩溃后第二任务存活、完成验证/READY。 | [日志](D1_C04_TABLET_EVIDENCE/secondCodecTaskSurvivesFirstNativeCrash.log) |
| actualHostDeathDuringEncodingAndCrossOwnerAbort | PASS | sample后helper宿主自杀；新owner租约恢复并同task abort，无READY。 | [日志](D1_C04_TABLET_EVIDENCE/actualHostDeathDuringEncodingAndCrossOwnerAbort.log) |
| actualHostDeathAfterReadyAndSameTaskQuery | PASS | durable READY后helper死亡；新owner原task/token一致且abort保留成功输出。 | [日志](D1_C04_TABLET_EVIDENCE/actualHostDeathAfterReadyAndSameTaskQuery.log) |
| playbackMp4 | PASS | 结构/5次Seek/短播放/源排空通过；静音自动用例。 | [日志](D1_C04_TABLET_EVIDENCE/playbackMp4.log) |
| playbackAviWithoutSrt | PASS | 无SRT对照结构/Seek/短播放/释放通过。 | [日志](D1_C04_TABLET_EVIDENCE/playbackAviWithoutSrt.log) |
| playbackAviSrt | PASS | 有SRT轨选择/开关/Seek/播放/释放通过；字形效果另核查。 | [日志](D1_C04_TABLET_EVIDENCE/playbackAviSrt.log) |
| playbackMkvAss | PASS | ASS轨选择/开关/Seek/播放/释放通过；自动静音不判声音。 | [日志](D1_C04_TABLET_EVIDENCE/playbackMkvAss.log) |
| offlinePlatformFaceFeasibility | FAIL | MP4 2秒非空；AVI10秒scaled和同时间点unscaled均空，FRAME_AT_REQUESTED_TIME_UNAVAILABLE。 | [日志](D1_C04_TABLET_EVIDENCE/offlinePlatformFaceFeasibility.log) |

[23入口完整结果/时间/依赖/命令](D1_C04_TABLET_EVIDENCE/tablet-batch-results.json)、[控制台](D1_C04_TABLET_EVIDENCE/tablet-batch-console.log)。每项有界180～360秒，无外部超时。日志逐方法按App/companion UID采集，可能含此前同UID记录；以当前TestRunner方法/PID与阶段确定归属。设备与电脑时间有偏差，不据跨时钟差值评价性能。

## 输出与恢复门禁证据

宿主正常输出478920字节，task f98b3704-918e-442e-873e-ead2133fdf10；READY响应丢失路径输出同478920字节、task ff115bde-a0c5-4129-8e87-1b5f9fbaa879。两条均经过冻结AndroidOutputValidator强制H264/AAC、256×144、3秒±150ms、双轨独立有效样本、严格PTS、完整视频decoder/EOS/帧数/末PTS检查；不等于画面内容人工验收。

write日志stage=write hits=1 code7001，cause包括D1_INJECTED_OUTPUT_WRITE；flush stage=flush hits=1 code7001，cause包括D1_INJECTED_OUTPUT_FLUSH；validate stage=validate hits=1 code=OUTPUT_VALIDATION_FAILED，编码/fsync后检查。T02本次设备断言通过；T01规则反例与正常输出通过，但没有制造全部恶意MP4并真机fuzz。

companion正常前置通过后六个依赖恢复方法全部执行并通过，不再沿用C03 BLOCKED。PASS仅代表冻结断言覆盖的真实sample、异UID/PID、broker、Binder death、source排空、租约、task/READY/token等；不代表完整产品单App分发、native OOM或所有隔离边界闭环。

成功输出与所有任务材料保留，测试后cache原字节备份 cache-after-batch.tar；[目录列表](D1_C04_TABLET_EVIDENCE/cache-after-batch.txt)。失败的ordinary能力探针和broker SIGSEGV没有完整最终释放断言，保留未证实排空/quarantine；App停止或Binder死亡不替代lease/source证明。取帧两次generation日志released=true。

## 平板人工观察

| 项目 | 本轮结果 |
| --- | --- |
| MP4非静音声音 | PASS（人工），用户在确认的C04 MP4页重播后反馈“听到声音” |
| MKV画面与中文显示 | PASS（当前截图），READY、视频与可读中文；仅该帧，不证明完整样式/同步 |
| MKV实际声音和字幕显示 | PASS（人工），用户在C04 MKV页反馈“声音和字幕显示  正常” |
| 音画/对白同步、完整ASS样式及开关残留 | NOT_RUN；用户未单独确认上述细项，不扩大“正常”的覆盖 |
| AVI SRT字形与同步 | NOT_RUN（人工）；自动轨道/开关/Seek通过不代替字形效果 |
| 旋转/前后台/RTL/完整产品UI | NOT_RUN |
| 人脸检测质量/实际frame PTS | NOT_RUN；AVI帧不可用，未进入检测；PTS UNKNOWN |

[MP4截图](D1_C04_TABLET_EVIDENCE/probe-mp4.png)、[MKV截图](D1_C04_TABLET_EVIDENCE/probe-mkv.png)及各自resumed记录。人工页volume=1，未调整全局设置。旧C03平板和C02手机声音反馈不移作本轮结果。

本轮人工声音日志：MP4 audio/mp4a-latm、selected=true、decoder=c2.android.aac.decoder、session889；MKV audio/ac3、6声道/48000Hz、selected=true、decoder=OMX.dolby.ac3.decoder、session897。与用户当前有声反馈相符，说明此平板本轮该路径可播放；不能推断手机的AC3能力或无声根因。[人工音频诊断](D1_C04_TABLET_EVIDENCE/manual-audio-logcat.txt)、[用户观察原文](D1_C04_TABLET_EVIDENCE/manual-observation.txt)。

## 集中剩余缺陷与根因限制

| ID / 严重度 | 本轮证据与影响 | 后续验证 |
| --- | --- | --- |
| TABLET-C04-01 / 高 | isolatedWorkerDeathAndTimeout在mode2 SIGSEGV时RPC_DONE后抛 normal bounded broker result。mode0 NORMAL、mode3 PRESSURE与mode1 EXIT已实际进入并继续；mode2进入后返回，未验证预期异常/实际死亡；HANG未执行 | 查信号发送与RPC返回/死亡时序；不得把进入模式当实际crash证明。此处与companion sample后SIGSEGV通过区分 |
| TABLET-C04-02 / 高 | ordinary能力探针返回WORKER_DIED，预期ISOLATED_CODEC_CAPABILITY_DENIED。已不再是C03 start失败，但不能作为明确codec API拒绝或完整释放证明 | 补实际隔离进程codec阶段/异常或native死亡日志，区分平台native abort、协议回传和释放未知；当前原因未定 |
| TABLET-C04-03 / 中 | MP4 2秒scaled非空，metadata320×180/8021ms；AVI10秒width/height null，duration5431488，scaled及同10秒unscaled均null，FRAME_AT_REQUESTED_TIME_UNAVAILABLE，两generation released=true；未进入人脸检测 | 排查平台AVI取帧支持/实际视频轨读取，不能换0秒或空Bitmap掩盖；取帧失败不等于ExoPlayer播放失败 |

每项.log与对应-uid日志保留cause/stack；详细探针阶段不足以解释ordinary死亡根因，未捏造错误链。宿主/companion导出1001在本轮未复现，NORMAL旧启动问题在此平板正常模式改善；不声称旧版本根因已动态证明。

AVI有/无SRT本次有界通过，没有复现旧手机180秒挂起；MKV静音自动通过仍不能关闭手机无声。手机PHONE-C02-01～04均须按修复候选另行补测。模型权利、供应链、NAS不协作、满盘/权限、native OOM、12路并发与标注质量仍未闭合。

## 批次保留

整包批次已结束，用户已确认MP4声音及MKV声音/字幕显示正常；其他人工细项保持NOT_RUN。已停止本次App播放与companion，停止不作为失败路径排空证据。保留C03/C04私有fixture、账本/lease/owner、成功输出及电脑备份。未清理或卸载。不得据20个限定PASS进入M0；下一候选及手机回归由负责人整体交接。
