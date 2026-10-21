# D1 呈现、PCM声音和源接续集中开发要求

2026-10-20；D1_RENDER_AUDIO_SOURCE_FEASIBILITY，正式集中功能簇，仍属D1，不启动M0。依据退出核查6d1214b7f96943359b4fab379ac5ace1a80063db14777366ebb05f9754e7d29a及其§6。E11的MP4/AVI六帧READY、能力源零打开与指定取消仅对应报告限定真机PASS；旧Before FAIL与其余NOT_RUN/UNKNOWN保留，不再把已完成项误记为全部未测。ENV03仍占用，不能以此批派发操作设备。

本批硬边界仅为可行性候选，不是公共产品阈值：有限视频最多6帧、最长30秒呈现观察；单帧不超过1920×1080、RGBA不超过8294400B，raw队列最多2、在途最多1，呈现自持有像素/中间副本合计不超过64MiB。来源超界明确拒绝，不静默缩放或扩内存，平台自身无法计量部分标明实际测量缺口。PCM为本地生成、可复现seed/hash、来源说明的PCM16/48kHz/双声道，最多3秒576000B，块≤20ms/3840B、排队4/在途1，低幅度fixture、默认静音并明确听音入口；不得自动向未知设备播音。无下载真实私人媒体/权重，现有test_media只读不打包。预算实际超界停止新准入，原owner未返保管，不以超时冒归还。

1. 新隔离开发目录/候选，保留E13F/RESUME等旧冻结原字节。复用已有raw来源/source/lease及Android成熟Canvas/Bitmap/Surface最小呈现，不造GL/codec框架。携带PTS/rotation/task/epoch/sourceVersion/Surface generation，处理暂停seek旧代拒绝、Surface销毁重建、失败取消、消费者失联及最后producer detach原引用归还；不把有限呈现称持续播放器。
2. 同包实现平台AudioTrack有限PCM输出和单audio owner/音频焦点/全静音及唯一声音；epoch切换、在途write、stop/flush/release与source聚合接回。两消费者须真实共用既有源聚合，一个结束不得提前SourceReleased；UI不持锁等待IPC。使用平台已定接口，不扩受限FFmpeg音频或加未经准入后端/依赖。
3. 同包交既有Media3/平台压缩音频与持续源接续、完整Sink顺序/随机/reopen能力及独立Kit可提取性的具体决定和接口差距。只依据冻结依赖/许可与源码，不把平台PCM成功当压缩音轨支持，不把原生闭包示例称Flutter完整App/AAR。权限隔离/同UID残余JNI危险链如无法安全承接，集中明确BLOCKED设计缺口，禁止known-unsafe设备探针；跟踪权重权利/标签仍未解决，不用本批绕过。
4. 有限自测覆盖owner/epoch/背压/取消/Surface销毁/焦点与双consumer归还，实际Android接口在一次必要集中app/test构建检查。不改fixture/native/host则复用不重编；必要失败与修复重建如实保留。自测不靠断言数代替关键路径，不测试浮动源码。
5. 一次整包交付源码/依赖锁/SBOM及许可差异/原新边界、功能完成矩阵、有限自测与构建日志、APK hash、render/PCM/source实际运行可验证入口及tester整批用例、危险链/停止归还方案。当前不SDK/ADB/5037/设备/旧handle或真实registry，设备观察留给后续正式整包派发。完整冻结后主动报告负责人，不按单问题频繁交接。
