# D1 C04 设备追加批次 V1.0

candidateId：D1-20261005-C04；14+9=23项准备完成，手机/平板全部NOT_RUN。Coder未连接设备。旧C02手机、C03平板包/fixture/账本保留。负责人选定C04、tester核对设备/API/ABI/serial、现有包与数据用途、签名后才切换；未知数据不覆盖。禁止Gradle connected/UTP/managed路径。ARM64/API31+；unsigned release不安装；worker为不同普通UID的D1实验APK。

| 冻结文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| app-debug.apk | 40623273 | f2d3a9473f27f5281a0214e04a821bca7a6fc579a5f9a1d9ffb50c539e62e937 |
| app-debug-androidTest.apk | 2308821 | c70362b629030f4a27e66a51a50e69b5e4834f7e54718d23682ab2b6969a8c13 |
| app-release-unsigned.apk | 21607782 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | 17081128 | ad1f9785218bb996c5b25c8f24eeb7e1080101c7690b0ec857f5a51a4d90fdc5 |

仅使用冻结复制件，不取可变build输出。签名见apk-audit.json与三份signing日志；按负责人批准方式安装，不擅自卸载或install-r，不混用旧测试结果。

## Fixture门禁

固定别名basic.mp4、subtitle.avi、subtitle.srt、large.mkv；精确源文件/hash在tools/transfer_fixtures.py的FIXTURES及media-inventory.json。SRT1445 cues、GB18030兼容GBK，源不重写，仅有界转UTF8。目的仅files/d1_c04_fixtures，不改旧候选目录。

transfer_fixtures.py默认PLAN_ONLY。未来实际复制需要--execute、--serial、--device-and-installed-c04-reviewed、--overwrite-c04-fixtures-reviewed、位于docs/tester的--result-file；这些参数必须对应tester已完成审查。--aliases仅固定别名。实际空间须至少请求文件总量+最大文件+256MiB；未知目录、空间不足、长度/SHA不符停止。32KiB shell-v2 raw帧传二进制，不用exec-in/tee；先.c04-part，源/stream/目标长度与SHA一致才提交，再验最终别名。工具不安装/卸载/管理ADB server/清理设备。实际2GiB+设备复制另留字节/hash证据，桌面6断言不替代。

## 顺序及通过条件

1. ordinary NORMAL先PASS，再pressure和故障。记录SOURCE_OPEN/BIND/CONNECTED/HELLO/RPC/BROKER、实际非宿主UID/PID、原cause；NORMAL/PRESSURE IOException均FAIL。fault模式必须实际进入且hits=1，并对应死亡/超时后实际排空；绑定失败不算命中。
2. normal host realEncoderOutput与companion isolatedActualEncodeAndReadyRecovery分别先PASS。失败保存完整ExportException cause/stack、muxer阶段、样本/字节；依赖项BLOCKED。T01 H264256×144/AAC，两轨独立非零样本、时长±150ms、严格PTS、全视频decoder/EOS/帧数/末PTS。规则反例不算真机恶意MP4 fuzz。
3. T02 write/flush指定stage、hits=1、ExportException精确D1_INJECTED_OUTPUT_WRITE/FLUSH；flush已有编码字节。validate须编码/fsync完成、非零字节且OUTPUT_VALIDATION_FAILED。错阶段、未命中、普通source/codec先失败均不PASS。READY响应丢失以同task QUERY收敛，abort不删READY。
4. 普通isolated负探针仅实际Hello/身份/租约后createEncoderByType失败、返回ISOLATED_CODEC_CAPABILITY_DENIED才通过；AVAILABLE、RELEASE_UNKNOWN或bind失败不算拒绝。保留cause。API探针不是GPU或产品隔离闭环；完整边界还需companion正常控制。
5. sample后cancel/crash/host death、另一task存活、dup-close、跨owner恢复保留C03门禁：真实样本后故障、确定死亡/Writer租约释放后才删未READY；未知lease隔离，不清除；另一task输出完整验真，不能假定同UID processgroup行为。
6. MP4对照AVI有/无SRT，prepare/post/enter/return、Extractor类sniff/read/offset、字幕decode/playerstate逐阶段记录。5秒主线程等待、30秒准备预算、五次seek及cue证据。WAV sniff不是根因。超时先独立撤销Source，再尝试main release；实际operations/consumers/failedClose和graphics未知分别记录，不能伪称全释放。
7. 自动播放静音，仅验结构/轨道/字幕。手动ProbeActivity volume=1，同机先MP4再MKV，人工记录听到/未听到；mime尤其AC3、supported/selected、decoder/session/sink/focus留证。不改系统音量，仅READY/音轨存在不算声音PASS；平板人工有声不替代手机。
8. 帧提取先MP4 2秒控制，再AVI10秒scaled；空帧回退同10秒原尺寸再有界缩放。metadata、耗时、异常与实际资源账本留证；两次空为FRAME_AT_REQUESTED_TIME_UNAVAILABLE。native超时不能硬中断就保留单槽与未释放事实。非空后才检测，不换0秒/空Bitmap；实际frame PTS UNKNOWN、质量NOT_RUN。

## 准备入口

### C04DeviceTests.java

| 方法 | C04执行 |
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
| offlinePlatformFaceFeasibility | NOT_RUN |

### C04IsolatedDeviceTests.java

| 方法 | C04执行 |
| --- | --- |
| ordinaryIsolatedCodecDenialDoesNotReady | NOT_RUN |
| nativeLeaseSurvivesDuplicateDescriptorClose | NOT_RUN |
| isolatedActualEncodeAndReadyRecovery | NOT_RUN |
| cancelAfterActualVideoSample | NOT_RUN |
| workerExitDuringActualEncoding | NOT_RUN |
| workerSigsegvDuringActualEncoding | NOT_RUN |
| secondCodecTaskSurvivesFirstNativeCrash | NOT_RUN |
| actualHostDeathDuringEncodingAndCrossOwnerAbort | NOT_RUN |
| actualHostDeathAfterReadyAndSameTaskQuery | NOT_RUN |

每项记录候选hash、serial/API、fixture hash、阶段/cause、时间与PASS/FAIL/BLOCKED/NOT_RUN，写docs/tester自身目录。保留旧包/数据/输出，故障不自动清理；旧平板7/5/10不推导C04通过。
