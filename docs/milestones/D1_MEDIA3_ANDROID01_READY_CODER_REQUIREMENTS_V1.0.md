# MEDIA3_ANDROID01_READY 开发要求 V1.0

2026-10-21；负责人正式派D1_MEDIA3_ANDROID01_READY完整开发/离线审查功能簇，不是设备执行令。

已核独立报告docs/tester/D1_MEDIA3_CONTAINER02_FIX_REVIEW_REPORT_V1.0.md，SHA256 e857e11a919475562587ff300223472076e8c190388f838e61a8417fecd46649；接受PASS_LIMITED_FIX_WITH_FUNCTIONAL_SCOPE_OPEN，MC-B01仅在实际检查开始前准入/原返回范围关闭，原FAIL不回写。真实容器/fixture/平台仍OPEN/NOT_RUN，D1未过M0未启。冻结02为本批实现来源。

本批目的：准备在真实Android运行实际Media3提取链的完整可审候选，绕开JDK缺平台类的环境限制，不再靠增加JVM替身。继续原成熟库1.9.3及全部strict锁/来源许可、8MiB累计输入/16MiB输出/64KiB块/两源单源1queue0/恰六样本AVC写入界。

1. 新目录docs/coder/d1media3-android01；以独立空数据无权限测试包实现有限instrumentation入口，接02原hostreadAt→真实DataSource→Mp4/FragmentedMp4Extractor→有界轨道样本观察；测试sample只有批准349102B/hash720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9私有只读副本。原320x180+AAC/8秒仅作为读取/提取观察，不能送256x144六样本muxer门，不播放不解码。仅已批准良性精确hash输入，不做恶意atom/OOM/崩溃/卡死注入。
2. 准备同真实Android环境执行的muxer→临时Sink→只读真实提取/结构比较入口；必须资格化fixture才允许运行正例。先有限核现有批准材料是否存在匹配单AVC256x144、rotation0、无音频加密、六帧PTS0..1000000/EOS1200000及权属/CSD/NAL/hash清单的样本。没有则准确FIXTURE_BLOCKED，实际写入0；交一个完整可审的生成方案，列准确工具/版本/来源许可/参数/输入权属/预算/退出清理，负责人后续审定才执行。当前不新增编码器/转码工具/MediaCodec生成执行、不扩FFmpeg、不伪NAL。
3. 包及进程身份与既有旧包完全分离，不安装升级或操作com.videokit.app/其他项目；仅空数据良性测试沙箱，同UID进程不冒RCE隔离，不能代生产J11/P0。若既定权限/资源边界不能满足，准确阻塞，不拆旧门换UID冒归还。解析与平台调用须有限owner/真实原线程回收，超时仅停止准入并保留UNKNOWN，不能强停/二close/退款补ACK。禁止已知不可用ordinary isolated codec/GPU探针。
4. 不给主机结构结果签隔离验证或产品READY/COMMIT，不播放音视频、不改音量、不碰旧账/once/历史UNKNOWN。明确实际Android正例、主机有限自测、未来NOT_RUN三栏，实际执行前提/精确方法参数/资源预算/错误停点与证据出口一次性完整列出，复用现有采集能力不新造通用release/诊断框架。

当前零设备/SDK现场/ADB/占用检查；仅开发及必要一次集中app/test strict构建，源码/产物/清单/依赖/方法/fixture门冻结后负责人审、tester独立离线审，再由负责人另签准确新实机批次及fresh空闲门。其他项目占用不操作不持续轮询，旧停止scope不重用。

整批交付：实际Android测试实现、离线自检/必要构建、app/test准确签名身份、可重放入口、来源许可strict及原冻结差异、fixture资格或完整生成方案、设备用例/预算/退出条件、seal/ZIP与完整报告。完整冻结主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774，不自行设备或宣布容器PASS，不逐问题交接。

## 2026-10-21 阶段A完整准备审阅补充

负责人已核docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_A_REPORT_V1.0.md，SHA256 36c5d4fecfe13b955a96e9194a4f59024df115d85ab3a6292db1794ab205a4cf，接受准备完成且fixture/执行缺口保留。24项oracle全部PREPARED_NOT_RUN，不登记新实现通过。将其证据目录的independent-oracles.json、evidence-contract.json、fixture及generation-plan-review-checklist.json集中纳入本批最终映射，不逐条打断开发。

原片是BBB节选重编码派生物，署名/CC BY3.0/修改记录完整继承；320x180+AAC/8秒只提取观察。已有8视频manifest无合格六样本声明，不扩大媒体输入或自动选encoder。fixture生成完整准确方案仍待本批交付后审定，不执行新编码。真实方法/runner/进程/期限/receipt与后续设备全预算须由新包准确绑定，不照搬旧scope。

全EOF/hash、parser EOF、真实轨道样本/CSD/NAL/PTS、预算与原Provider/worker/observer/FD归还分别留证。普通观察cap=true/seek=-1/capture=false；seek1秒仅真实SeekMap准入才执行，不预填golden。app/test来源许可strict闭包分别核，不以02 app17坐标代AndroidTest依赖。新包完整冻结后另派B，仍离线；D1未过M0未启。
