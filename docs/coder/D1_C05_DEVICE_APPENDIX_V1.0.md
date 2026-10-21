# D1 C05 设备追加批次 V1.0

candidateId：D1-20261005-C05；16+9=25入口准备完成，全部C05设备NOT_RUN。由负责人整体选定候选后tester集中执行。Coder本轮不接触ADB/设备。保留C03/C04已有包、fixture、账本、lease、输出及电脑恢复备份；先确认实际安装候选、同签名、设备/API/ABI/serial、可用空间和现有数据用途，未知数据不覆盖。不自动卸载/清数据/恢复旧版本，不用Gradle connected/UTP/managed设备路径。ARM64/API31+。

| 冻结文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| app-debug.apk | 40623273 | 4639989459c9c9ec5491e71ebe0d52ae35f705c3dbe6f24b5262a1cab9258fd9 |
| app-debug-androidTest.apk | 2308821 | abc7c2cd56ecab256567dfbe6c22f45b9780f5466d9c90c146c2627ae04b790d |
| app-release-unsigned.apk | 21607782 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | 17100536 | 591f8de03b48121e68d4a13d2d3b3a152b4b6a3044fc78e81c915cc86d0ea5b6 |

只用冻结复制件，三份debug APK同签名；unsigned release不安装。worker是额外不同普通UID的D1实验，不是单App产品方案。签名/manifest/ABI见apk-audit.json及各APK证据。

## 源与复制

C05读取files/d1_c05_fixtures的固定别名basic.mp4、subtitle.avi、subtitle.srt、large.mkv。电脑源45项保持hash，FIXTURES在transfer_fixtures.py和media-inventory.json；SRT为1445 cues/GB18030兼容GBK，源不重写。

可由tester在数据审查后复用已有C04副本：先重新核验可信源长度/SHA，再复制到新C05私有目录并核验目标，不修改C04目录；此路径不能算Windows传输工具设备通过。若测试Windows路径，transfer_fixtures.py默认PLAN_ONLY；实际执行需显式serial、--execute、--device-and-installed-c05-reviewed、--overwrite-c05-fixtures-reviewed、docs/tester内--result-file；仅固定aliases。未知目录、空间不足（请求总量+最大单文件+256MiB）、长度/hash不符均停止。32KiB shell-v2 raw流先.c05-part再核验提交，不用exec-in/tee；工具不管理server/安装/清理。电脑>2GiB协议证据为复用，不代替实际设备复制。

## 批次顺序与证据

1. 先realEncoderOutput和isolatedActualEncodeAndReadyRecovery正常前置，再完整T01/T02及全部实际sample恢复批次；不能用普通探针失败跳过已通过实际管线复验。T01 H264256×144/AAC、各轨独立非零样本、3秒±150ms、严格PTS、完整视频decoder/EOS/帧数/末PTS。T02 write/flush指定stage、hits=1、ExportException精确D1_INJECTED_OUTPUT_WRITE/FLUSH，flush已有字节；validate编码/fsync后非零字节与精确OUTPUT_VALIDATION_FAILED。无关codec/source失败不算注入PASS。READY丢响应同task/token查询；abort保留READY。
2. 普通isolatedWorkerDeathAndTimeout本轮只测NORMAL/PRESSURE/EXIT。isolatedBrokerSigsegvIndependently和isolatedBrokerHangIndependently各自先NORMAL，再独立目标模式；即使一项失败也继续执行另一项并单列结果。ENTERED hits=1加对应SIGSEGV_ARMED/HANG_WAIT_BEGIN/EXIT_ARMED同步ACK，非宿主UID/PID。SIGSEGV不能返回普通RPC，必须实际Binder death及匹配OS退出signal11；cleanup SIGKILL、无历史记录或错误PID/UID均不PASS。HANG必须实际WAIT_BEGIN、精确WORKER_TIMEOUT、有界等待和实际死亡/Source账本排空。记录finally实际状态；普通broker不证明真实媒体输出lease。
3. ordinaryIsolatedCodecOutcomeDoesNotReady替代旧Denial方法。记录实际task/epoch、HELLO UID/PID、LEASE_ACQUIRED/CREATE_BEGIN/END、typed Java cause或native死亡、RELEASE_BEGIN/END/FAILED。仅Java codec调用异常且对应同步阶段，或CREATE_BEGIN后具体匹配tombstone cause的SIGABRT，才能记“调用失败/native abort事实”；不能称已证codec权限拒绝。AVAILABLE、RELEASE_UNKNOWN、ACK/bind失败和未解释WORKER_DIED均FAIL。即使断言失败仍执行finally：death、Source实际released、FencedTask独占lease可取后abort、无token；释放未知quarantine，不清除材料。
4. 系统退出记录在App内查询；若trace缺失/超256KiB/不匹配/无allowlist原因，保持UNKNOWN失败。不得用宿主UID-only日志解释isolated native死因。tester按当前方法、PID、isolated UID及阶段有界保存所需crash/协议日志，排除旧同UID记录。OS循环历史记录可能丢失，不能捏造权限原因或用其他进程tombstone。原native trace含路径，App只保留SHA与固定cause；需更广原因分析由tester保留原始证据，下一整批审查，不扩大当前allowlist。
5. offlinePlatformFaceFeasibility先MP4 2秒控制，再原AVI10秒scaled/unscaled；仅FRAME_AT_REQUESTED_TIME_UNAVAILABLE允许转现有Media3 AVI 9～12秒片段，经T01完整双轨/decode/fsync/READY门禁后请求转换MP4的1秒OPTION_CLOSEST。不能换原片0秒、空Bitmap或仅MP4结果。记录source AVI、clip_start/end、requested_source=10000000、requested_clip=1000000、actual_source_frame_pts=UNKNOWN；非空才检测，quality=NOT_RUN。转码可能有损，不代表精确源帧/检测质量验收。若转换或取帧失败保留完整cause/账本，记FAIL/BLOCKED。
6. 取帧/转换分别20秒/90秒、主线程5秒、输入排空10秒；单次native无法硬停时保留资源事实。frame片段输出和.task均保留证据，不自动删除；最多两份缓存记录，达到预算FRAME_CLIP_CACHE_BUDGET_REVIEW_REQUIRED，由负责人审查后处理，不清未知文件。graphics释放未知或Source未排空均不算通过。原AVI源不得修改；新cache输出不是额外fixture替代。
7. companion sample后cancel/EXIT/SIGSEGV、第二槽存活、实际host死亡与跨owner恢复、native dup-close均保留：实际H264 sample后故障、确定死亡/Writer lease释放后才删未READY、第二输出完整验证/READY、同task/token恢复，未知lease隔离。普通broker与companion SIGSEGV单列，不相互代替。
8. 完整MP4/AVI无SRT/AVI SRT/MKV ASS播放及手机追加保留C04门禁：prepare/Extractor/字幕/main/seek有界诊断，Source真实排空，5次seek/字幕开关。自动静音只验结构；同一手机MP4/MKV手动volume=1、轨道支持/选择/renderer/session/focus及人工听音才判声音；平板有声不关闭手机。字形/同步/ASS全样式、实际frame PTS和检测质量未证据则NOT_RUN。

## 全部入口

### C05DeviceTests.java

| 方法 | C05执行 |
| --- | --- |
| playbackMp4 | NOT_RUN |
| playbackAviWithoutSrt | NOT_RUN |
| playbackAviSrt | NOT_RUN |
| playbackMkvAss | NOT_RUN |
| realEncoderOutput | NOT_RUN |
| outputValidationCounterexamples | NOT_RUN |
| exportReadyResponseLoss | NOT_RUN |
| exportWriteFault | NOT_RUN |
| exportFlushFault | NOT_RUN |
| exportValidationFault | NOT_RUN |
| realPipelineImmediateCancel | NOT_RUN |
| writingJournalRecovery | NOT_RUN |
| isolatedWorkerDeathAndTimeout | NOT_RUN |
| isolatedBrokerSigsegvIndependently | NOT_RUN |
| isolatedBrokerHangIndependently | NOT_RUN |
| offlinePlatformFaceFeasibility | NOT_RUN |

### C05IsolatedDeviceTests.java

| 方法 | C05执行 |
| --- | --- |
| ordinaryIsolatedCodecOutcomeDoesNotReady | NOT_RUN |
| nativeLeaseSurvivesDuplicateDescriptorClose | NOT_RUN |
| isolatedActualEncodeAndReadyRecovery | NOT_RUN |
| cancelAfterActualVideoSample | NOT_RUN |
| workerExitDuringActualEncoding | NOT_RUN |
| workerSigsegvDuringActualEncoding | NOT_RUN |
| secondCodecTaskSurvivesFirstNativeCrash | NOT_RUN |
| actualHostDeathDuringEncodingAndCrossOwnerAbort | NOT_RUN |
| actualHostDeathAfterReadyAndSameTaskQuery | NOT_RUN |

记录候选hash、serial/API、fixture hash、时间、实际stage/hits/cause、Source/FD/lease最终状态与逐项PASS/FAIL/BLOCKED/NOT_RUN，写docs/tester自身目录。不得据C04的20PASS移作C05成功，不自动停止后续独立方法；依赖前置失败单列BLOCKED。整批结束统一报告，保留失败材料，无M0验收。
