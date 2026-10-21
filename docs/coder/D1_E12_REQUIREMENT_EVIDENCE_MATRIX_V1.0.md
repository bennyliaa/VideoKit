# D1 E12 需求—实现—证据矩阵 V1.0

日期：2026-10-18。READ_ONLY_AUDIT。D1 **NOT_PASSED**；M0 **NOT_STARTED**。所有“OPEN”表示当前证据不足或未完成，不捏造新测试FAIL。原始需求为U，当前源码为E11 final R1；源码存在只证明实现位置。证据引用ID与原字节pins见 [docs/coder/d1e12/SOURCE_INDEX_V1.0.md](D:/CodexProjects/VideoKit/docs/coder/d1e12/SOURCE_INDEX_V1.0.md)。本批未联网核新版本/法律结论，沿用冻结项目记录，不作新的发行许可判定。

## 1. 已接受的有限增量与历史基线

E11报告“唯一部署”“四项实际结果”“最终账本”“限定关闭范围”接受一次14→15保数据部署、四个独立host的实时观察、MP4/AVI各6帧READY、能力源opens/bytes/reads=0、条件取消及全部原资源和五个PC会话自然归还。批次a129ad0a-9d93-49c6-8289-9087afd419ff，平板HA1Q6WXR/API31；非声音、字幕、长期或UNKNOWN实测。

最新接受账本214483B、7R/7S、reserved0，完整2271B SHA e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649；旧107218B/1011B前缀保持。这里只转述报告时点，不是本批在线重读。旧oldCloseACK=false、未知出生/信号均保持。

E6B-OBS-F01/P1（OBS，2026-10-17）原AVI Before失败保留；E11通过catalog来源与每新host实际观察解决该历史问题在本批独立host连续执行中的阻断，记 **CLOSED_LIMITED_E11_CROSS_HOST**。长期运行、系统重启、旧历史退出记录再缺失/新UNKNOWN均OPEN，不将旧报告FAIL改PASS。

C13报告（2026-10-16）self系统signal0严格FAIL、外部raw11与独立双槽系统11分别保留；C14ENV（2026-10-16 12:40）两项NOT_RUN_UNCHANGED_PLATFORM_LIMIT，不存在本批C14新signal PASS。E11正常退出不能覆盖这条历史失败或证明native死因可观测。

## 2. 原文§26–31逐条矩阵

每条原文均保留行号。第28节里程碑另见下表；第30节十个设计交付名称另列。以下OPEN均只限制其自己的最终要求，不表示把全部后续M阶段实现强塞D1。

| ID / 原文定位与逐条要求 | 当前实现和实际证据范围 | 缺证及能否关闭 | 阶段/出口 |
|---|---|---|---|
| U26.1-01 / U:941 API版本与能力协商。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.1-02 / U:942 旧状态快照读取和新增可选字段兼容。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.1-03 / U:943 未知未来主版本安全拒绝。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.1-04 / U:944 正常、取消、超时、重复调用和release幂等。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.1-05 / U:945 HostAction超时/失败不影响播放。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.1-06 / U:946 输入句柄和输出Sink故障映射。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.1-07 / U:947 Fake与真实实现执行同一套契约测试。 | TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝 | OPEN：缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收 | D1界定输入/释放语义；M0公共契约 |
| U26.2-01 / U:951 0%、25%、50%、90%和接近结尾Seek。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.2-02 / U:952 连续快速Seek。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.2-03 / U:953 暂停、恢复、播放结束和重新播放。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.2-04 / U:954 字幕、音轨、倍速、方向、缩放和状态恢复。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.2-05 / U:955 小视频、2GiB以上视频、长视频、损坏视频、0字节和播放中断线。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.2-06 / U:956 每种正式容器至少测试一个真实有效样本；缺少样本标NOT_RUN。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.2-07 / U:957 输入释放后SMB/文件句柄归零。 | CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证 | OPEN：缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放 | D1后端差异可行性；M1播放 |
| U26.3-01 / U:961 JPG/JPEG、PNG、WebP、HEIC/HEIF、AVIF、BMP、GIF。 | C14/J09：旧平台Bitmap/FaceDetector对照；当前E11未含图片产品 | OPEN：缺本条真实图片格式、交互和生命周期证据 | D1选型和危险解析路线；M2图片 |
| U26.3-02 / U:962 静态WebP、动态WebP和动态GIF。 | C14/J09：旧平台Bitmap/FaceDetector对照；当前E11未含图片产品 | OPEN：缺本条真实图片格式、交互和生命周期证据 | D1选型和危险解析路线；M2图片 |
| U26.3-03 / U:963 小图、大图、长图、透明图、旋转元数据图和损坏图。 | C14/J09：旧平台Bitmap/FaceDetector对照；当前E11未含图片产品 | OPEN：缺本条真实图片格式、交互和生命周期证据 | D1选型和危险解析路线；M2图片 |
| U26.3-04 / U:964 左右导航请求、缩放、平移、旋转、窗口变化和资源释放。 | C14/J09：旧平台Bitmap/FaceDetector对照；当前E11未含图片产品 | OPEN：缺本条真实图片格式、交互和生命周期证据 | D1选型和危险解析路线；M2图片 |
| U26.3-05 / U:965 图片界面不显示视频专属控件。 | C14/J09：旧平台Bitmap/FaceDetector对照；当前E11未含图片产品 | OPEN：缺本条真实图片格式、交互和生命周期证据 | D1选型和危险解析路线；M2图片 |
| U26.4-01 / U:969 1、4、9、12个槽位。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.4-02 / U:970 视频/静态图/动态图混排。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.4-03 / U:971 每格状态独立。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.4-04 / U:972 唯一音频源及全静音。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.4-05 / U:973 离屏暂停/释放和重新绑定。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.4-06 / U:974 解码器不足、内存压力和温度升高时稳定降级。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.4-07 / U:975 一个槽位故障不影响其他槽位。 | SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法 | OPEN：缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵 | D1预算与两任务边界；M3多实例 |
| U26.5-01 / U:979 单视频多个片段的添加、裁剪、删除和重排。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-02 / U:980 多个同参数和不同参数视频拼接。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-03 / U:981 横竖屏、可变帧率、不同音频参数和无音频输入。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-04 / U:982 手动马赛克/模糊与坐标映射。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-05 / U:983 导出取消、空间不足、权限失败、输入断线、编码器失败和进程被杀。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-06 / U:984 任意失败时源媒体字节和路径保持不变。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-07 / U:985 不完整输出不被markReady。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.5-08 / U:986 宿主验证失败后VideoKit不自行提交或删除源。 | SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消 | OPEN：缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN | D1输入/Sink关键边界；M4/M6完整编辑导出 |
| U26.6-01 / U:990 单人、多脸、侧脸、遮挡、离开/进入画面。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.6-02 / U:991 单物体、多物体、快速运动、低对比和相似目标。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.6-03 / U:992 关键帧纠正和从纠正点继续。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.6-04 / U:993 跟踪丢失区间提示。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.6-05 / U:994 预览与导出遮罩一致性。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.6-06 / U:995 取消、模型缺失、内存不足和热降级。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.6-07 / U:996 不产生网络上传或永久人脸资料。 | C14及G.P08：候选/设计与历史对照，E11无跟踪执行 | OPEN：缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据 | D1合法路线与最小可行性；M5/M6完整质量 |
| U26.7-01 / U:1000 BrowserMediaSource可映射为VideoKitMediaSource且不暴露凭据。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-02 / U:1001 MediaPlayHobby往返不丢字段，SINGLE/VIDEO_BOX作用域由宿主隔离。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-03 / U:1002 标签/收藏HostAction只回传ID。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-04 / U:1003 播放中标签操作等待SourceReleased。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-05 / U:1004 controlsVisible可驱动邻近媒体条同步显示。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-06 / U:1005 多会话音频和资源限制由Browser协调。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-07 / U:1006 输出只进入宿主Sink。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-08 / U:1007 移除AAR后LocalVideoBrowser临时播放器仍可构建运行。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.7-09 / U:1008 VideoKit崩溃或加载失败不阻止LocalVideoBrowser启动和浏览。 | CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配 | OPEN：缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现 | D1接口不阻断可行性；M0/M7真实契约/集成 |
| U26.8-01 / U:1012 Android 12/API31最低版本。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-02 / U:1013 一个中间主流Android版本。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-03 / U:1014 当前稳定Android版本。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-04 / U:1015 ARM64实体手机。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-05 / U:1016 10英寸级实体平板或明确记录的等价设备。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-06 / U:1017 竖屏、横屏、分屏和窗口变化。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-07 / U:1018 字体100%、130%、200%。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U26.8-08 / U:1019 简体中文、英文、伪本地化和RTL冒烟。 | E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史 | OPEN：缺本条其他版本/设备/窗口/语言字体的实际证据 | D1最低设备差异；M1/M3/M6/M8矩阵 |
| U27-01 / U:1025 VideoKit可能覆盖、移动或删除输入源。 | CPU只读授权输入；E11四方法的原样本与历史产物身份保持 | OPEN：未证全部编辑/取消/断线/进程终止产品组合；源不变仍发布硬门 | D1机制先处置；正式发布前全部硬门 |
| U27-02 / U:1026 输出绕过宿主Sink或绕过宿主验证直接成为正式文件。 | SESSION临时Sink/隔离验证/结算；两normal READY | OPEN：宿主业务COMMIT没有由Kit替代；全Sink能力/宿主拒绝组合仍缺 | D1机制先处置；正式发布前全部硬门 |
| U27-03 / U:1027 NAS凭据、完整路径或宿主数据库类型进入公共API。 | CPU broker只收opaque token/字节，SERVICE只接任务/FD | OPEN：正式公共API/多宿主resolver未建立；不能据Debug不传凭据关闭全API门 | D1机制先处置；正式发布前全部硬门 |
| U27-04 / U:1028 一个会话故障导致整个宿主崩溃或其他会话被错误释放。 | codec迁出host，压缩解析isolated；C13限定故障他槽历史 | OPEN：本候选故障/UNKNOWN/宿主lease JNI以及显示声音图片链未闭合 | D1机制先处置；正式发布前全部硬门 |
| U27-05 / U:1029 多实例无法限制音频或资源不足时循环创建解码器。 | CPU2/encoder1限制，E11无音频 | OPEN：唯一发声与资源不足反复创建/1–12降级无产品证据 | D1机制先处置；正式发布前全部硬门 |
| U27-06 / U:1030 人脸/物体跟踪丢失时仍把结果宣称为完整打码。 | C14/G跟踪尚无完整合法质量链 | OPEN：LOST不能宣称完整保护；不得用手动回退删自动P0 | D1机制先处置；正式发布前全部硬门 |
| U27-07 / U:1031 编辑失败后留下被标记为成功的部分输出。 | E11能力/取消两项0B ABORTED，无假READY | OPEN：永久UNKNOWN、全部IO失败/损坏输出与工程编辑链未证 | D1机制先处置；正式发布前全部硬门 |
| U27-08 / U:1032 稳定复现ANR、OOM、Surface/句柄泄漏或无法取消的任务。 | E11四方法有界正常归还；SESSION保留未证资源 | OPEN：无长期/真实OOM/Surface/永久挂住取消完成保证；UNKNOWN不归零 | D1机制先处置；正式发布前全部硬门 |
| U27-09 / U:1033 GPL/AGPL/SSPL或许可证不明代码进入计划闭源的产品模块。 | FM/STATIC仅受限Debug精确版本与7库/35依赖 | OPEN：闭源正式分发许可/模型权利未准入，不是本批新法律审查 | D1机制先处置；正式发布前全部硬门 |
| U27-10 / U:1034 Release包含测试凭据、真实NAS资料、压力入口或永久调试日志。 | BUILD debug sourceSet含故障入口；非正式Release交付 | OPEN：最终Release移除压力/永久日志/凭据需独立发行审计，不能将Debug可交实验当可发行 | D1机制先处置；正式发布前全部硬门 |
| U27-11 / U:1035 AAR无法独立构建，或LocalVideoBrowser必须直接依赖VideoKit源码才能运行。 | SET仅app，BUILD application | OPEN：无独立AAR/无源码宿主构建/替换证明，M0/M7硬门 | D1机制先处置；正式发布前全部硬门 |
| U29-01 / U:1056 1. Maven group、artifact、Android namespace和版本策略。 | D§3内部com.videokit/App命名已定；BUILD仍Debug v15 | OPEN：正式artifact/SemVer/兼容迁移未冻结；M0/M7 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-02 / U:1057 2. 公共API是否拆分播放artifact与编辑artifact。 | D§3 api/core/playback等分包计划；SET仅app | OPEN：实际播放/编辑依赖分离与发布产物未有；M0/M7 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-03 / U:1058 3. Media3、图像库、编码器、FFmpeg替代方案及许可证结论。 | BUILD只接Media3 muxer；FM/STATIC保留1.9.3与受限FFmpeg8.0.3 | OPEN：ExoPlayer/Transformer/图片与产品发行许可未闭合，不复刻媒体框架；D1/M1/M2/M6 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-04 / U:1059 4. 人脸和移动物体跟踪技术、模型许可证和最低设备要求。 | C14/G跟踪候选固定但非已准入权重 | OPEN：模型/训练/样本再分发权利、真实标注/最低设备未证；D1阻断及M5 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-05 / U:1060 5. 首版输出容器、编码器和质量预设。 | E11实测无音频6帧AVC/fMP4；旧host双轨为历史 | OPEN：不能代替首轮MP4/H264/AAC/SDR正式预设；M6参数/音频矩阵 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-06 / U:1061 6. 快速无重编码拼接的兼容条件。 | E11六帧是重编码，无无损拼接路径 | OPEN：remux需参数/关键帧/PTS/旋转/音轨兼容与fallback；D1设计/M4/M6 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-07 / U:1062 7. 跟踪效果、导出速度、内存和温度验收阈值。 | E11有限64MiB/8192reads/6帧/2MiB门与耗时记录 | OPEN：非正式导出速度/质量/全进程RSS/热阈值；D1测法与M3/M5/M6审定 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-08 / U:1063 8. Compose UI、Android View及纯引擎模式的对外组合方式。 | D§3无UI原生Kit+可选View/Compose+Flutter已定 | OPEN：E11无Surface/Flutter生命周期实证；D1边界、M0接口/M1/M8 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-09 / U:1064 9. OutputSink需要顺序写、随机写还是文件描述符能力。 | SESSION本地临时Sink+有界顺序mux channel；E11写后关闭验证 | OPEN：不证明任意FD/非seekable宿主Sink能力；D1须决定必要能力与失败语义，M0/M6 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-10 / U:1065 10. 编辑工程Schema、版本迁移和进程恢复范围。 | 现有journal/epoch/终局迁移是实验任务记录 | OPEN：不是工程schema/undo/revision/跨进程恢复产品契约；M0/M4/M6 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-11 / U:1066 11. 默认控件布局、主题扩展和宿主叠加层API。 | U§20/D设计有方向，E11无正式控件/overlay接口 | OPEN：主题/宿主叠加/坐标/无障碍未定可用API；M0/M1/M2/M5/M8 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U29-12 / U:1067 12. 多实例共享资源池及硬件解码器预算算法。 | CPU进程内2槽/SESSION encoder1及账本，E11正常资源返回 | OPEN：不是宿主全局1–12公平/音频/硬解预算算法；D1权威与M0/M3 | D1解决有关可行性；M0设计冻结/相应阶段实证 |
| U30-01 / U:1090 如何让LocalVideoBrowser提供SMB随机读取而VideoKit不知道账号和路径。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-02 / U:1091 如何保证播放资源释放后标签工作队列才移动/复制媒体。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-03 / U:1092 如何让普通播放和不同VideoBox的PlayHobby互不覆盖。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-04 / U:1093 如何由宿主统一控制多会话音频、数量和降级。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-05 / U:1094 如何把标签/收藏设计为通用HostAction而不引入宿主业务依赖。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-06 / U:1095 如何确保编辑输出只写宿主临时Sink且永不覆盖源。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-07 / U:1096 如何让自动跟踪失败区间对用户可见并可人工修正。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U30-08 / U:1097 如何独立发布AAR、运行契约测试，并在缺失或故障时由LocalVideoBrowser安全回退。 | D及既有十份V1.0设计文档/G差距分析；E11仅局部实现 | OPEN：设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证 | D1报告可供决定；M0契约与M7集成 |
| U31-01 / U:1103 1. LocalVideoBrowser无需把NAS、标签、收藏、VideoBox或数据库交给VideoKit。 | CPU/SERVICE无Browser数据库参数 | OPEN：正式API/Browser adapter仍未证；M0/M7 | D1给可行路线；M0–M8实现并整体验收 |
| U31-02 / U:1104 2. VideoKit可以通过宿主随机读取接口稳定播放本地及NAS大视频。 | E11仅MP4/AVI取帧，无持续播放/NAS | OPEN：随机读取大视频与NAS正式稳定播放待M1 | D1给可行路线；M0–M8实现并整体验收 |
| U31-03 / U:1105 3. 视频和图片共享统一会话边界，图片隐藏无关控件。 | 当前候选没有统一图片产品会话 | OPEN：统一图片/视频会话及控件隐藏待M0/M2 | D1给可行路线；M0–M8实现并整体验收 |
| U31-04 / U:1106 4. 单媒体和多画面使用同一种可多实例架构。 | 现有task/epoch/CPU2是实验机制 | OPEN：正式单媒体/多画面同架构和实例独立待M0/M3 | D1给可行路线；M0–M8实现并整体验收 |
| U31-05 / U:1107 5. 每个媒体的播放偏好可完整交还宿主，并按作用域隔离。 | G/公共契约设计有MediaPlayHobby作用域要求 | OPEN：产品偏好往返全字段/作用域隔离待M0/M1/M7 | D1给可行路线；M0–M8实现并整体验收 |
| U31-06 / U:1108 6. 标签、收藏、邻近媒体和导航全部通过宿主接口完成。 | E11不实现HostAction/导航UI | OPEN：通用宿主动作与邻近媒体同步待M0/M2/M7 | D1给可行路线；M0–M8实现并整体验收 |
| U31-07 / U:1109 7. 单视频片段重排、多视频拼接、手动打码及自动人脸/物体跟踪可生成新视频。 | 六帧新输出有限通过，无编辑器/跟踪产品 | OPEN：重排/拼接/手动及自动目标跟踪完整新视频待M4/M5/M6 | D1给可行路线；M0–M8实现并整体验收 |
| U31-08 / U:1110 8. 任意编辑失败、取消、断线或进程终止都不改变源媒体。 | 正常/指定取消源保持，UNKNOWN不伪称释放 | OPEN：全部失败/终止/断线源不变产品链待M6/M7 | D1给可行路线；M0–M8实现并整体验收 |
| U31-09 / U:1111 9. VideoKit可作为版本化AAR独立构建、测试和替换。 | SET/BUILD是Debug app，不是独立版本化AAR | OPEN：独立构建/契约测试/替换待M0/M7 | D1给可行路线；M0–M8实现并整体验收 |
| U31-10 / U:1112 10. 缺少VideoKit或单个功能模块失败时，LocalVideoBrowser仍可启动、浏览并回退到临时播放器。 | E11候选无真实Browser缺失模块回退集成 | OPEN：宿主启动浏览和临时播放器回退待M0/M7 | D1给可行路线；M0–M8实现并整体验收 |

### §28里程碑与§30设计交付

| 原文范围 | 当前裁定 |
|---|---|
| §28 VK-M0 | API/Fake/TestKit/示例宿主仍未正式实现/冻结；D1未过，不启动 |
| §28 VK-M1–M3 | 播放、图片、混排/唯一声音保留全部P0；D1仅验证关键后端与资源路线 |
| §28 VK-M4–M6 | 时间线、跟踪与安全导出需后续完整实现；六快照不等产品编辑器 |
| §28 VK-M7 | 正式AAR/兼容/可移除回退与真实Browser集成未过 |
| §28并行前提 | 公共API评审冻结是前提；当前不满足，不据建议并行擅自进入M0 |
| 后续App范围 | D已采纳Flutter，原文M0–M7建议表不取消后续执行文件中的App工作；当前无Flutter交付 |
| §30 PRODUCT_REQUIREMENTS.md | 已有版本化文件 [docs/PRODUCT_REQUIREMENTS_V1.0.md](D:/CodexProjects/VideoKit/docs/PRODUCT_REQUIREMENTS_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 SYSTEM_ARCHITECTURE.md | 已有版本化文件 [docs/SYSTEM_ARCHITECTURE_V1.0.md](D:/CodexProjects/VideoKit/docs/SYSTEM_ARCHITECTURE_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 PUBLIC_API_CONTRACT.md | 已有版本化文件 [docs/PUBLIC_API_CONTRACT_V1.0.md](D:/CodexProjects/VideoKit/docs/PUBLIC_API_CONTRACT_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 LOCALVIDEOBROWSER_INTEGRATION.md | 已有版本化文件 [docs/LOCALVIDEOBROWSER_INTEGRATION_V1.0.md](D:/CodexProjects/VideoKit/docs/LOCALVIDEOBROWSER_INTEGRATION_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 PLAYBACK_AND_IMAGE_DESIGN.md | 已有版本化文件 [docs/PLAYBACK_AND_IMAGE_DESIGN_V1.0.md](D:/CodexProjects/VideoKit/docs/PLAYBACK_AND_IMAGE_DESIGN_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 EDIT_TIMELINE_AND_EXPORT_DESIGN.md | 已有版本化文件 [docs/EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md](D:/CodexProjects/VideoKit/docs/EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 TRACKING_TECHNICAL_SPIKE.md | 已有版本化文件 [docs/TRACKING_TECHNICAL_SPIKE_V1.0.md](D:/CodexProjects/VideoKit/docs/TRACKING_TECHNICAL_SPIKE_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 OPEN_SOURCE_AND_LICENSE_PLAN.md | 已有版本化文件 [docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md](D:/CodexProjects/VideoKit/docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 TEST_AND_ACCEPTANCE_PLAN.md | 已有版本化文件 [docs/TEST_AND_ACCEPTANCE_PLAN_V1.0.md](D:/CodexProjects/VideoKit/docs/TEST_AND_ACCEPTANCE_PLAN_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |
| §30 MILESTONES.md | 已有版本化文件 [docs/MILESTONES_V1.0.md](D:/CodexProjects/VideoKit/docs/MILESTONES_V1.0.md)；文档存在可确认，评审状态/实现与验收不得据存在推定 |

## 3. 原文§4全部13项P0（无减项）

| P0原文行/内容 | 现有实现/证据 | 缺口与D1责任；最终阶段 |
|---|---|---|
| U:73 稳定公共API、Fake和示例宿主 | SET仅:app，BUILD是application；G.P10 | OPEN：正式api/Fake/示例不存在；D1确定可独立封装与释放语义，M0基础契约 |
| U:74 单视频播放 | CPU六次snapshot/E11有限正常 | OPEN：非连续播放器；D1后端/源可行性，M1 |
| U:75 静态/动态图片查看 | J09旧Bitmap对照，不在E11功能闭包 | OPEN：图片/动图危险解析与候选需D1处置；M2完整UI |
| U:76 HostAction扩展按钮 | G.P07、§30宿主业务隔离设计 | OPEN：无真实HostAction产品；D1只需定边界，M0/M2 |
| U:77 播放状态捕获与恢复 | G.P07与公共契约设计 | OPEN：无产品完整状态往返；D1列快照兼容风险，M0/M1 |
| U:78 多实例与资源报告 | CPU2/encoder1、SESSION账本；E11正常归还 | OPEN：未知未实测/唯一音频无证；D1许可/故障隔离可行性，M3 |
| U:79 单视频片段重排 | 六帧流水线不含时间线 | OPEN：D1确认输入/Sink接续，M4片段重排 |
| U:80 多视频拼接 | 六帧无音频fMP4，不是多源拼接 | OPEN：D1记录remux与格式限制，M4/M6 |
| U:81 手动打码 | J10设计，无正式遮罩GL链 | OPEN：D1原生危险边界路线，M5/M6 |
| U:82 人脸自动跟踪 | C14跟踪候选，无合法真实标签集完整证据 | OPEN：D1模型/样本权利与最小质量路线阻断，M5 |
| U:83 移动物体自动跟踪 | C14物体候选与模板对照 | OPEN：D1合法模型/LOST/纠正可行性，M5 |
| U:84 安全导出和取消 | E11两READY+两0B ABORTED/SESSION门 | OPEN：真实UNKNOWN/断线/空间权限及全产品未证；D1关键释放/Sink语义，M6 |
| U:85 LocalVideoBrowser适配器契约测试 | G.P10及设计，E11没有Browser产品适配 | OPEN：D1可移除/无业务API依赖路线，M0/M7 |

## 4. J01–J11 当前实现差分（历史R2位置不可原样当现状）

| 门 | 当前源码位置/owner/权限与证据 | 缺证、状态及出口 |
|---|---|---|
| J01 | CPU在isolated处理压缩源；旧MediaEngine宿主Media3路径属历史，不在最小E11产品闭包；E11两限定格式取帧 | PARTIAL：仅MP4/H264、AVI/MPEG4；其他容器/持续播放/真实provider及普通发送者拒绝未证 |
| J02 | CPU task/epoch+Binder实际UID/PID；FFmpeg在isolated；E11实际6源任务/normal | PARTIAL：正常读取/释放成立；C13故障限定证据保留，真实OOM/所有UNKNOWN不由正常路覆盖 |
| J03 | SERVICE独立:e4_codec承担编码能力查询；同UID，非isolated，E11实际启动 | PARTIAL：已迁出UI host地址空间；不具权限/RCE隔离，未证当前服务故障与他槽全链 |
| J04 | SERVICE编码owner；SESSION保留在途与原代；E11 AVC6in/6out | PARTIAL：正常和指定取消通过；非native crash/卡住/实际UNKNOWN结束证明 |
| J05 | SERVICE持Image/Plane或ByteBuffer；E11报告未独立声明Image分支已进入 | OPEN：不得用正常编码推定所有色格式/Image路径；按实际分支再定有限验证 |
| J06 | muxer在codec owner；SESSION宿主Sink/lease/file/fsync与AndroidLease JNI仍在 | PARTIAL：实际正常close/输出结算成立，host残留JNI及FD未知未消除，flock不撤销恶意FD |
| J07 | 输出CPU isolated validator mode11；E11两normal双EOF/drain/6decoded；旧双轨host验证历史保留 | PARTIAL：当前6帧视频输出有限通过，不外推多音轨/validator death与全容器 |
| J08 | 旧SRT/Media3字幕路径；E11无字幕显示实现 | OPEN：读取/解析/字体/Surface owner和销毁代次未证；D1设计路线，M1完整字幕 |
| J09 | 旧Bitmap/FaceDetector对照，不在当前E11能力闭包 | OPEN：图像解析/动图/正式模型和资源边界未证；D1合法候选与危险解析决定 |
| J10 | 跟踪/遮罩/GL正式链未实现；C14/G记录候选 | BLOCKED：模型/标签/质量及执行owner无证，不能把未实现写成已隔离；D1最小路线，M5完整 |
| J11 | E11无实际Surface/Texture/AudioTrack/Flutter bridge；C14只有有限显示/PCM设计 | BLOCKED：无准入PCM解码输入，禁止扩FFmpeg音频；先决定raw显示/source权威和音频合法路线再派功能实现 |

## 5. 开源选型与实际集成

OSS是2026-10-05初步估算，写明只有Flutter确定，不能把候选清单当依赖已冻结。BUILD实际只debugImplementation Media3 muxer及既有运行时约束；SET只含app。FM记录自有胶水是授权输入、队列、owner、Sink和资源门；不是自制codec。

| 原计划 | 当前事实（冻结记录/源码） | 差距与下一步 |
|---|---|---|
| Flutter/本地化 | 已确定App路线，E11为原生Debug应用 | 未实现；M0桥接契约/M8完整App，禁止用Java测试APK冒充产品 |
| ExoPlayer | 旧C14 MediaEngine实验，当前最小E11只muxer依赖 | 持续播放/字幕/音轨后端仍缺；保留薄适配首选，先解决宿主读取与危险边界 |
| Transformer/Composition | 原首选，当前六帧编码采用公开MediaCodec+Media3 fMP4 | 没有Transformer输入/Sink正式集成；后续以精确Sink能力/故障边界再决定是否适用，不继续扩自有编辑框架 |
| Coil/SDWebImage | 图片候选，未在E11实际接入 | Android图片选型待验证；Apple仅分析，不启动构建 |
| OpenCV/YuNet/ViTTrack/ONNX | 历史固定候选/对照，正式模型/权重与标签权利未闭合 | 负责人组织权利与标注；不得自制跟踪器代替未达成P0 |
| media_kit控件 | 选择性MIT控件候选，E11无Flutter控件 | 不默认引入底层libmpv/FFmpeg；后续UI按已审组件适配 |
| FFmpeg8.0.3 | 当前受限Debug CPU库真实参与，原初估算未计入 | 后续受限技术准入不等闭源外发；7native/35Maven不扩；替换/再链接/NOTICE/专利等发行门OPEN |
| 自有协议工具 | broker、资源owner、source/Sink事务承担本项目边界 | 下一批复用既有监督/观察/生命周期；禁止新authority服务/诊断平台/另套取消框架 |

结论：D1关键剩余项是权限负例、UNKNOWN真实生命周期、产品源聚合及显示/音频危险边界、合法跟踪与封装可行性；全图片UI/1–12混排/完整编辑器和最终AAR发行仍按原阶段实施。下一批提案只选择其中一个可完整核验的功能簇，其余逐项OPEN，不宣布D1通过。

