# D1 C06 集中设备追加说明 V1.0

candidateId：D1-20261005-C06；17+9=26入口准备完成，C06全部NOT_RUN。负责人选定整包后tester执行；本轮coder无ADB/设备操作。保留C04/C05包、fixture、账本/lease/owner、成功输出、失败采帧账本与电脑恢复备份；先核对设备/API/ABI/serial、实际安装APK hash、三包签名、现有数据用途与空间，未知数据不覆盖。禁止Gradle connected/UTP/managed路径。ARM64/API31+；unsigned release不安装，额外不同UID companion仅D1实验。

| 冻结文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| app-debug.apk | 40623273 | a01b2b088dc9e8284d308b3bec774d33609870000f634ade228579646a27e969 |
| app-debug-androidTest.apk | 2308821 | de25e0fe50eb5e0c30e554b67b06a91cd6f5a42f543a4edd756cd935b09e6687 |
| app-release-unsigned.apk | 21607782 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | 17045480 | 616769985e150841743007379ec456d9e5e00a01792981424778d5c751026e16 |

仅取冻结复制件，不取可变build输出。实际签名、manifest、ABI见apk-audit.json和各signing日志。更新/回退/清理按负责人授权和保留要求执行，不自动卸载或清数据。

## Fixture

C06读取files/d1_c06_fixtures的basic.mp4、subtitle.avi、subtitle.srt、large.mkv；精确源/hash见transfer_fixtures.py/FIXTURES与media-inventory.json。SRT1445 cues、GB18030兼容GBK，仅有界转UTF8不改源。可由tester在审查后重新验证已有C05副本，再复制到全新C06私有目录并核验长度/hash，不改C05目录；私有cp不证明Windows跨机传输工具通过。

若测Windows工具，默认PLAN_ONLY；实际需--execute、显式serial、--device-and-installed-c06-reviewed、--overwrite-c06-fixtures-reviewed、docs/tester内--result-file及固定aliases；空间至少请求总量+最大文件+256MiB，未知目录或身份不符即停止。32KiB shell-v2 raw流先.c06-part再校验提交，不用exec-in/tee，不管理ADB server/安装/卸载/清理。>2GiB电脑协议证据复用，不代替实际设备复制。

## 依赖、覆盖与判定

1. 正常宿主realEncoderOutput与companion isolatedActualEncodeAndReadyRecovery先PASS，再跑全部T01/T02和真实sample恢复。正式导出仍H264256×144/AAC，双轨各自非零样本、3秒±150ms、严格PTS、完整视频decode/EOS/帧数/末PTS。T02 write/flush指定stage/hits=1/精确cause，flush已有编码字节；validate编码/fsync后非零字节与OUTPUT_VALIDATION_FAILED。普通codec/source先失败不算注入命中。READY丢响应仍同task/token收敛，abort保留READY。
2. 普通NORMAL/PRESSURE/EXIT与独立SIGSEGV/HANG完整复验。指定模式同步ENTERED+ARMED/WAIT_BEGIN、hits=1；SIGSEGV必须没有正常RPC结果、实际Binder death及PID/isolated UID/启动时间匹配OS signal11，cleanup SIGKILL或单条mode不够。HANG精确WORKER_TIMEOUT、有界等待、实际死亡和Source计数排空。两个独立方法均执行，不能互相遮蔽。普通broker源账本不等于真实输出Writer lease。
3. ordinaryIsolatedCodecOutcomeDoesNotReady保持严格App分类与finally释放断言。记录task/epoch/UID/PID、LEASE_ACQUIRED/CREATE_BEGIN及traceStatus：APP_TRACE_ABSENT、READ_OR_PARSE_FAILED、IDENTITY_OR_SIGNAL_MISMATCH、MATCHED_PROTO等。App原因未知仍FAIL，不用SIGABRT或外部文字强造App通过；available/release未知/bind/ACK失败同样不算预期原因。即使分类失败，实际death/source_released/lease_clear/无token分别记录并复验。未知FD/lease quarantine，不删材料。
4. 另由tester有界保存对应本轮C06 PID/UID/时间/进程/阶段的原始native crash，分类为“外部死因事实”独立栏目。不能引入旧PID5588/C05 tombstone作为C06证据；不能把宿主UID-only日志当isolated栈。不把Hardware service manager错误文字推断为全局停机/权限拒绝。App trace可缺失，既定分类FAIL保留，负责人另审退出准则，不扩大allowlist或静默改判。
5. 新videoFrameCaptureMp4Control先跑：同一视频采帧管线对MP4原2秒请求（1～4秒片段内1秒），独立validator确认1视频0音频、H264256×144、3秒、有效样本/严格PTS、全视频decode/EOS/帧数/fsync和非空取帧。只有该控制PASS，再评估offlinePlatformFaceFeasibility的AVI回退；控制失败，依赖项另列BLOCKED，不把MP4结果当AVI成功。
6. face方法仍先直接MP4 2秒控制，再原AVI10秒scaled/unscaled。只有稳定FRAME_AT_REQUESTED_TIME_UNAVAILABLE触发原AVI视频-only回退，typed AviExtractor仍需实际sniff匹配，不fallback成原MP4。原AVI9～12秒转换片段内1秒OPTION_CLOSEST；源/clip请求映射留证，actual_source_frame_pts=UNKNOWN、quality=NOT_RUN。视频-only是采帧专用契约，不要求音频，也不能拿它满足正式双轨输出。decoder、轨道、muxer和sample实际阶段均保存，无有效片段/非空帧不得检测通过。
7. 保持默认10秒无sample watchdog，不延长掩盖无进展。按sniff/init/seek、track/endTracks/input sample、video decoder begin/created、muxer track/output sample/fsync/完整validate定位；SOURCE_READ_FAILED CANCELLED是取消现象，不直接作根因。90秒外层、5秒main等待、20秒retriever、10秒Source排空保持；单次native不可硬停如实保留quarantine。Transformer cancel返回不表示全部graphics资源释放。
8. C06保留d1_c06_capture_*.capture和对应片段，最多两条预算；MP4控制和AVI各占一条，不自动清理或反复重跑。达到预算FRAME_CLIP_CACHE_BUDGET_REVIEW_REQUIRED交负责人审查。output_descriptors_closed与source_released分别记录；不把capture_validated叫产品READY/token。AVI或控制失败材料保留，不修改旧C05 frame账本。
9. 真实companion sample后cancel/EXIT/SIGSEGV、第二槽存活、实际helper宿主死亡/跨owner恢复、native dup-close全部复验：真实sample后故障、确定死亡/Writer lease清除后才删未READY、第二输出完整验证/READY、同task/token恢复，未知lease保留。手机播放/声音和人工完整字幕/同步/旋转等未证据仍NOT_RUN，平板播放不移作手机通过。

## 26入口

### C06DeviceTests.java

| 方法 | C06执行 |
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
| videoFrameCaptureMp4Control | NOT_RUN |
| offlinePlatformFaceFeasibility | NOT_RUN |

### C06IsolatedDeviceTests.java

| 方法 | C06执行 |
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

逐项记录候选hash、serial/API、fixture hash、时间、实际stage/hits/cause、source/FD/lease最终状态和PASS/FAIL/BLOCKED/NOT_RUN，写docs/tester自身证据目录。原25入口全部保留并增加采帧MP4控制；依赖失败单列BLOCKED，其余独立方法继续。整批统一报告，不据部分PASS进入M0。退出准则提案尚待负责人评审，当前App内UNKNOWN仍FAIL。
