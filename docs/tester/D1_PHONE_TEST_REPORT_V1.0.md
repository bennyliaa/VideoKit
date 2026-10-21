# D1 手机测试报告

日期：2026-10-05；版本：V1.0；tester：VideoKit tester。

候选：D1-20261005-C02；本轮状态：**PHONE_BATCH_BLOCKED**；后续状态：**WAITING_FOR_FIX_CANDIDATE**。手机已实现范围的本次批次停止，仍需新候选补测；不是PHONE_BATCH_FINISHED全通过，也不是D1通过。未操作平板，不进入M0。

## 1. 依据、授权和范围

执行 [手机安排](../milestones/D1_PHONE_TEST_EXECUTION_V1.0.md) 和冻结 [设备请求](../coder/D1_DEVICE_TEST_REQUEST_V1.0.md)。用户本轮授权撤销手机延期，tester独占唯一已授权手机，只使用C02复制APK；coder本机C03不纳入本报告。延续 [C02独立核查报告](D1_C02_TEST_REPORT_D1-20261005-C02.md) 已发现的C02-T01/T02，未执行不可信的导出/故障方法来关闭安全门禁。

本轮实际安装Debug/Test、复制四项fixture、执行五个独立方法、读取本测试App UID日志和测试页截图；没有运行Gradle、修改产品源码、使用C03源码或安装其它候选。电脑test_media只读；没有共享存储中转、媒体上传、全局日志清空、其它应用终止或数据清理。截图仅在确认本测试Activity前台后获取。

证据目录：[D1_PHONE_C02_EVIDENCE](D1_PHONE_C02_EVIDENCE)。自动方法的命令、主机开始/结束时间和结果见 [phone-batch-results.json](D1_PHONE_C02_EVIDENCE/phone-batch-results.json)。主机时间与设备logcat时间分别记录，未假设两时钟同步或将差值当性能指标。

## 2. 手机与候选身份

| 项目 | 实际记录 |
| --- | --- |
| 序列号 / 型号 | U4999DLBNRR89DOR / PDYM20（OPPO，设备OP4E21） |
| 系统 / ABI | Android12 / API31；arm64-v8a、armeabi-v7a、armeabi |
| 屏幕 | 1080×2400；density480；刷新率未另测 |
| RAM / 初始可用内存 | MemTotal 7742468kB；MemAvailable 4004912kB |
| 初始空间 | /data可用104796188KiB，足够完整fixture集合 |
| 电池 / 温度 | 初始70%、USB供电；battery temperature320（32.0℃），非完整热/电量性能试验 |
| 同包数据门禁 | 安装前pm list packages com.videokit.app返回空，无已有目标/测试包；安装后UID分别10262/10263 |
| ADB | 1.0.41，37.0.1-15733141；Windows执行环境 |

设备信息见 [preflight.json](D1_PHONE_C02_EVIDENCE/preflight.json)。发现模拟器但未用于本次手机验证。

安装前再次复算四个复制产物hash，均与冻结包一致：

| 产物 | SHA-256 | 用途 |
| --- | --- | --- |
| app-debug.apk | f06b368f9ccf0b173080da6919e353577a84fdf498413fd0206b20c4499ebe88 | 已安装 |
| app-debug-androidTest.apk | 427d4285625843c7868c01d997a9522a43bf41a89da9d7968fa0fd56f8381d05 | 已安装 |
| app-release-unsigned.apk | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e | 未安装 |
| C02-source.zip | 99c713633c946f52e6ab0dcd4ef041119b4ee6042eeaa256d3f7412c327f8f56 | 冻结源码/工具读取 |

本轮复用前报告的54项证据/110项源码完整核查，无重复构建。C02原包没有修改。

## 3. 准备工具故障与fixture身份

冻结device_setup.py从ZIP执行，两APK安装Success，但首个basic.mp4仅12285字节、SHA-256 fd5a43d5a8a950a711e968cf5e6d829be7dd756a600b643a8ca43118c6253292，未通过校验。此时未运行媒体测试。进一步raw shell通道尝试仅34字节，仍不匹配；失败记录保留。ASCII/base64通道小MP4校验通过，但大文件速度偏低，主动停止该helper，未运行测试。

随后使用本机127.0.0.1 ADB已授权transport的shell v2 raw二进制通道，只将四个固定私有alias流式覆写为本任务副本。未创建共享存储中间文件。全部源hash和设备hash匹配后才运行instrumentation。工作方案见 [transfer_adb_socket.py](D1_PHONE_C02_EVIDENCE/transfer_adb_socket.py)；失败/慢速工具过程不归入产品通过证据。

| 设备alias（App files/d1_c02_fixtures） | 字节 | 源与设备SHA-256 | 结果 |
| --- | ---: | --- | --- |
| basic.mp4 | 349102 | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 | PASS（副本身份） |
| subtitle.avi | 736454656 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f | PASS（副本身份） |
| subtitle.srt | 93550 | d3a44be0636d9ec4d5a2782d1a5d6ceb7141d7bf4f8df2f693d9850f867144bd | PASS（副本身份） |
| large.mkv | 3212959911 | 28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26 | PASS（副本身份） |

详 [fixture-hash-check.json](D1_PHONE_C02_EVIDENCE/fixture-hash-check.json)。电脑源hash是在只读传输中计算并与候选预期比对；未改名、覆盖或删除电脑媒体。设备副本总计3949857219字节，不意味着任何播放需要全量下载远程源。

## 4. 自动方法：3 PASS、1 FAIL、1 BLOCKED

| 方法 / 主机执行时间 | 预期与实际 | 结果与证据 |
| --- | --- | --- |
| playbackMp4 / 11:04:12–11:04:25 | READY、0/25/50/90/99%位置、3s播放无error、输入消费者排空；JUnit Time5.386s、OK(1 test) | PASS（方法断言）；[日志](D1_PHONE_C02_EVIDENCE/playbackMp4.log) |
| playbackAviSrt / 11:04:25–11:07:25 | 应有界完成READY/字幕选择开关/Seek/排空；180s未返回，无JUnit终态，只初始化日志，最后WavHeaderReader Unsupported form type；不足以确定根因 | BLOCKED（超时）；[日志](D1_PHONE_C02_EVIDENCE/playbackAviSrt.log)、[App日志](D1_PHONE_C02_EVIDENCE/avi-timeout-logcat.txt) |
| playbackMkvAss / 11:07:54–11:08:20 | 大MKV READY、5位置Seek、支持text轨选择/关闭/开启、3s播放无error、消费者排空；JUnit Time19.098s、OK(1 test) | PASS（方法断言）；[日志](D1_PHONE_C02_EVIDENCE/playbackMkvAss.log) |
| isolatedWorkerDeathAndTimeout / 11:08:20–11:08:27 | NORMAL应返回64再进入压力/退出/SIGSEGV/HANG；首个NORMAL即进入IOException分支，断言injected termination only失败；JUnit Time0.043s、1failure | FAIL；[日志](D1_PHONE_C02_EVIDENCE/isolatedWorkerDeathAndTimeout.log) |
| offlinePlatformFaceFeasibility / 11:08:27–11:08:35 | 授权AVI帧retriever解码、平台FaceDetector调用不抛错；OK(1 test)，App日志候选数0 | PASS（执行可行性）；[日志](D1_PHONE_C02_EVIDENCE/offlinePlatformFaceFeasibility.log)；质量NOT_RUN |

方法的PASS不证明首正确帧、长期稳定播放、完整codec/图片矩阵、字幕字形/对白同步、热性能或完整资源统计。App日志MP4 PSS81589kB、MKV PSS79994kB、thermal0，仅各一次快照，非CPU/GPU峰值/设备预算冻结值。两播放方法cue_events均0，字幕轨开关断言通过不等于实际字幕显示通过。

AVI超时后只force-stop本轮新安装的com.videokit.app以终止挂起测试，保留日志与fixture；从新进程执行剩余三个不同方法，没有反复重跑AVI。未断言系统ANR/native崩溃或源损坏；根因待新候选补证。普通方法进程退出码0不视为通过，worker依据FAILURES文本正确记FAIL。

worker因NORMAL首项失败，PRESSURE/EXIT/SIGSEGV/HANG均NOT_RUN；不同UID/PID、death、故障后的lease排空/另一槽存活断言没有被完整执行。没有进行实际SIGSEGV注入或系统OOM，不得在报告中标隔离通过。设备日志仅限目标App UID10262，未清全局logcat。

## 5. 图像、字幕与人工观察

| 观察项 | 实际证据 | 结果 |
| --- | --- | --- |
| MP4测试页显示画面 | [probe-mp4.png](D1_PHONE_C02_EVIDENCE/probe-mp4.png)可见READY、8秒终点及视频图像；有系统音量浮层，未由tester调整系统音量 | PASS（该截图有画面）；持续播放/声音/Seek正确帧不能据此通过 |
| MKV测试页显示画面 | [probe-mkv.png](D1_PHONE_C02_EVIDENCE/probe-mkv.png)可见READY和片头视频图像 | PASS（该截图有画面）；此帧未见媒体字幕，不能推断字幕坏或正常 |
| AVI中文SRT字形/开关/同步 | 自动方法超时，未人工重跑AVI | BLOCKED / NOT_RUN（效果） |
| MKV ASS字形、样式、开关后无残留、对白同步 | 已请求用户观察当前测试页；报告出具前无可靠人工确认则仍待测 | NOT_RUN，不能用轨道选择或cue计数代替 |
| MKV实际声音 | 用户在MKV测试页反馈“没有声音”；只读audio状态为媒体未静音、扬声器音量16/16。未改音量；不据此确定AC3解码或文件本身的根因 | FAIL（人工观察）；[音量状态](D1_PHONE_C02_EVIDENCE/music-volume-readonly.txt) |
| MP4声音对照 | 用户明确反馈“MP4 有声音”，与MKV无声构成同手机/同测试页的对照；不是对所有样本音轨的验证 | PASS（人工观察） |
| 音画/字幕时间同步 | 未收到可支持实际对白与帧/字幕同步的人工观察 | NOT_RUN |
| 旋转、前后台、字体/中英/RTL | 未改变设备全局设置或执行完整人工矩阵 | NOT_RUN；技术UI也不是Flutter产品验收 |
| 平台人脸质量 | 候选数0，无该帧人工标注 | NOT_RUN；不是零漏检或检测率PASS |

只捕获明确前台测试Activity，没有截图无关应用。截图看到片头中文标识不能充当ASS中文字幕字形证据。用户后续反馈应追加操作者、具体场景与观察结果，不自动升级整组通过。

## 6. 集中缺陷与待修复回归

| ID / 严重度 | 复现、影响和预期 | 集中修复/回归建议 |
| --- | --- | --- |
| PHONE-C02-01 / 高 | 本机冻结setup用exec-in/tee，首个MP4复制截断并hash失败；电脑源正常。准备脚本不能完成fixture可信交接 | 修复跨Windows二进制stdin传输，保留固定私有范围/hash及旧包门禁；覆盖含控制字节的小文件、AVI与>2GiB副本；本轮已用任务工具绕过，不代表冻结工具修复 |
| PHONE-C02-02 / 高，播放阻断 | 在PDYM20运行playbackAviSrt，180s无终态；源/副本hash均正确。应有界成功或稳定失败，不能挂住测试并使内部30s检查无返回 | 新候选增加prepare/主Looper/Extractor/字幕分层时序与有界故障；合法支持不足给稳定错误；同AVI/SRT、无侧车AVI、小/大MP4/MKV与取消释放受影响回归。不能直接据Wav sniff日志判定codec不支持 |
| PHONE-C02-03 / 高，隔离阻断 | Worker NORMAL发生IOException，测试断言injected termination only失败，未达后续模式 | 保留脱敏原因code/cause和mode，查源open/服务bind/broker/RPC阶段；修复后先NORMAL，再各故障/UID/PID/death/排空；不把断言文本当SIGSEGV成功 |
| PHONE-C02-04 / 高，声音效果 | MKV/ASS自动方法PASS，但用户在ProbeActivity观察无声；随后同手机MP4对照用户确认有声。系统媒体未静音且speaker16/16。自动方法setVolume(0)，不能验证实际有声；MKV含AC3轨仅元数据已证明 | 记录音频轨支持/选择、renderer初始化、audio session/focus和稳定不支持反馈；补已知有声AC3区间核查，不能以READY掩盖无声。MP4对照说明手机音频输出可用，但不能单独断言MKV无声由AC3不支持造成。根因与完整音画同步待查 |
| C02-T01 / 高，未关闭 | 输出validate用全部轨道样本总数，不能要求video轨有实际样本 | C03整包修复后回归正常H264/AAC、空视频有音频反例、尺寸/PTS/解码与ready门禁 |
| C02-T02 / 高，未关闭 | 三故障方法可接受与目标注入无关的编码失败 | C03整包核实故障阶段/命中计数/稳定原因、正常前置管线，不复用C02自动PASS关闭安全门禁 |

本轮未执行realEncoderOutput/exportReadyResponseLoss/exportWriteFault/exportFlushFault/exportValidationFault/realPipelineImmediateCancel/writingJournalRecovery，均NOT_RUN（等待完整修复候选统一回归）。没有实际编码中取消、宿主kill、满盘/权限、真实媒体native隔离、OOM/12路并发、NAS断线、跟踪标注质量及模型权利闭合证据。手机接上不自动关闭这些门禁。

## 7. 批次结束、保留与平板安排

手机当前批次已结束并因上述问题标PHONE_BATCH_BLOCKED；仍需完整修复候选，后续WAITING_FOR_FIX_CANDIDATE。安装前无同包应用，测试包和四项fixture暂保留供负责人审查/回归；未卸载、清空私有目录或修改电脑源。成功导出本轮没有执行。结束时停止本轮测试页播放，避免持续占用手机；具体停止记录保存在证据目录。

tester不自动切换模拟器或平板。负责人可依据本报告通知用户切换平板并另派发；这不会消除手机C03补测需要。需继续本手机补测时由负责人重新交付候选并安排设备，禁止在当前设备混用C02/C03证据。

D1尚未全量通过：AVI、worker、导出门禁及人工效果未关闭；权重权利、完整native隔离、质量/性能、供应链风险和特殊样本仍沿用D1未决清单。不得据3个限定PASS进入M0。
