# D1 E4A 剩余门禁评审 V1.0

2026-10-17。E4A针对 tester F01/P1、F02/P1、F03/P2提供新实现和有限离线证据，等待整包独立复审。**D1 NOT_PASSED、M0 NOT_STARTED、全部原P0不变。** 所有新Android/安装/ADB/真实媒体/native fault/硬件结果NOT_RUN。原E4/C14冻结与结果不覆盖。

## 修复的范围与限制

F01现在保留ABORT产物，累计实际消费记录在跨方法/host的固定持久账本，不从目录存量推算。每次先预留2MiB，原资源/CONTROL/metadata都返回后才结算实际长度/SHA，未知保完整预留与pending marker；删除文件、换batch/UUID、重建host不退款。F02现在在实际guard/FD/channel初始化前登记外部holder，初始化+close双失败保原对象/路径/两异常；close未返回不算归还、不重试。F03保持CONTROL真实在途，最后finally触发唯一收尾，取消设备用例沿原30s截止query同一Session的新状态。

最终68项断言是66项主要自有文件/owner/CONTROL检查+2项独立新JVM恢复读取。原65项MAIN及必要元数据持有补强后的REPAIR均保留，不相加成133条“最终测试”。没有重跑旧E4 89项。Android本机MAIN和必要REPAIR保原日志/源码快照/双APK与审计；编译通过不代表设备通过。JVM受控线程、真自有小文件和假失败不是Android/native/权限/压力实验。

全批后续设备仍需验证实际文件系统行为、PFD/guard、Binder调度、资源峰值和故障。账本是合作式协议：同UID恶意修改、完整清除app数据、存储/系统/掉电不可证明状态仍是风险；marker只在原已证结算后删除，不提供自动恢复或洗未知许可接口。三个quarantine各自可选最后分支，首个未知后的余下分支BLOCKED，不能靠新host执行。

## J01–J11位置与待证

| 项 | 当前真实位置/边界 | 未闭合门禁 |
|---|---|---|
| J01 host Source/Media3 parser | 新host只read-only broker和原始帧，旧host Media3路线在历史C14/全产品 | 旧链未因最小APK省略而解决；多容器/坏源/取消/native fault与宿主存活仍待证 |
| J02 FFmpeg demux/decode/sws | 同APK ordinary isolated CPU，原8.0.3闭包/白名单/配额/禁网不扩 | 真实六源帧及PTS、实际CPU死亡/read/close/slot、坏输入与安全边界NOT_RUN；不证明任意RCE安全 |
| J03 CodecList/能力查询 | :e4_codec owner，只收有界配置与授权空Sink | 具体Android12手机/平板/OEM硬软能力、能力拒绝Source0但实际FD关闭待证 |
| J04 codec create→release | 同UID独立进程，四提案上一个实际释放后才下一项，运行期不重选 | 六输入/六样本/真实释放，native命中/host和另一任务存活，硬件属性与驱动恢复均未证 |
| J05 Image/Plane | codec owner持Image、边界检查和YUV scratch | 实际色格式/Image分支/stride/padding/close未知待测；ByteBuffer成功不覆盖Image |
| J06 fMP4/Sink/sync/lease/预算 | service持muxer/授权FD；host持E4FencedTask、原名AndroidLease JNI、本地累计账本 | 新holder改正静态缺口，但实际FD/stream/close/fsync/lock回收、取消与跨host持久化待测。host Java FileChannel/文件同步和极小lease JNI仍可致命；同UID/RCE无权限隔离，OS ACK不等绝对掉电安全 |
| J07 输出验证 | 新产物回 ordinary isolated CPU 完整EOF/六帧/PTS/内容 | 真实产物验证/原validation source-close/退出/slot待证；旧host MediaExtractor及多轨验证仍OPEN |
| J08 字幕/字体 | E4A不接SRT或Media3字幕；原host路线不迁移 | 字幕编码/时序/坏输入/取消/字体native/绘制/资源归还未关闭 |
| J09 图片/FaceDetector | 本批不接压缩图/模型 | 维度/坏图/bitmap/native owner、实际质量/权利/最低设备与故障边界OPEN |
| J10 跟踪/遮罩/GL | 无正式model/GL owner，不下载模型、不扩GPU探针 | ROI/LOST/修正/旧revision/质量/模型权利/GL资源及隔离BLOCKED/NOT_RUN |
| J11 显示/音频/Flutter | 无Surface/Texture/AudioTrack，六帧输出无音频，帧不走Dart | 真画面/声音、audioEpoch/Surface代次/旧帧、producer/PCM/track归还及Flutter生命周期未证；无准入PCM解码，不扩FFmpeg音频 |

## 原§29十二项

| 项 | 本批保留事实 | 未完成范围 |
|---|---|---|
| 1 坐标/版本 | 内部group com.videokit、namespace com.videokit.<module>、App com.videokit.app方向不变 | 正式artifact/版本/兼容/迁移/服务命名冲突M0/M7 |
| 2 组件拆分 | 独立最小单APK，不依赖Browser/SMB/Room | api/core/playback/image/ui/timeline/effects/tracking/export/testkit独立AAR及可移除宿主M0/M7 |
| 3 库/FFmpeg/许可 | Media3 1.9.3，35坐标较E4零差异；原7库不变，C14减少图14GA差异/新增GA0 | 完整图片路线、NOTICE/再链接/专利/商店/闭源宿主分发仍OPEN，不新增SCA通过 |
| 4 模型 | 不下载新模型，原候选身份只作历史事实 | 权重/训练/样本人权利、质量标注/最低设备和执行位置M5 |
| 5 容器/质量 | 六帧256×144/AVC/fMP4/无音频 | 正式MP4/H264/AAC/SDR/HDR/颜色/分辨率/长时与硬软各设备矩阵M6；旧configure FAIL不改 |
| 6 remux | 本批有限重编码 | 无损拼接/时戳/edit-list/旋转/多轨/兼容fallback M6 |
| 7 质量/性能 | 六帧/queue2/encoder1/CPU2/输出累计预算有界 | RSS/PSS/VMS/FD/线程/热/效果和低端分级/多轨/长期行为M3/M5/M6 |
| 8 UI/引擎 | 原生host控制进程，帧不经Flutter | Compose/View/Flutter engine/texture/Window和多宿主M0/M1/M7/M8 |
| 9 Sink公共协议 | 仅有界临时Sink、本地预算与原授权 | 顺序/随机/跨宿主FD/通用query/恢复公共API仍待评审M0/M6/M7；工具READY非业务COMMIT |
| 10 schema/恢复 | task/epoch/generation/instance围栏，未证owner持久保留 | schema/undo/revision/迁移、正式host强杀恢复/公共存储合同M0/M4/M6 |
| 11 控件/主题 | 本批无产品UI，原文动作和Browser边界不改 | 无障碍/主题/overlay/坐标/编辑和Flutter UI M0/M1/M2/M5/M8 |
| 12 共享预算 | 单host CPU2/encoder1，跨host未结算输出marker拒新编码 | 不是跨多宿主全局CPU/硬件codec池，公平/抢占/多路/音频唯一与1/4/9/12槽M0/M3/M7 |

## 历史与下一步

实际sameUID codec仅是待实测崩溃边界，无权限/RCE沙箱。ACCESS_NETWORK_STATE依然是normal网络状态权限；无INTERNET不消除同UID能力。有限binder、资源计数、源码/签名或使用系统API不能代替全链宿主存活与原资源回收证明。

C14原冻结、73可调度+2 NOT_RUN_UNCHANGED_PLATFORM_LIMIT不改；C13平板52 PASS/3 FAIL/14 BLOCKED、手机环境阻断不改。self App系统signal0严格FAIL，外部raw11/另一方法system11分别保留，不回填；trace缺失/ordinary UNKNOWN继续OPEN。E4A不运行旧CPU信号条件、不改退出采集算法或设crash handler。

Android12手机与平板分别验证，旧连接/安装/legacy companion结果不等新环境或授权。禁止卸载清数据、换包名/预算身份/目录洗未知，禁止改阈值或重跑求signal。iOS/macOS/Windows只设计，AVFoundation/MediaFoundation/平台进程token与句柄adapter未实现；不假设iOS能任意创建本型子进程。

完整冻结后仅交负责人，由负责人集中交tester复审再另派有限设备批次。正常真实六帧/原身份、另一真实任务前置、故障命中和资源证据缺一不可。所有原P0及M0/M1–M8保持，不将中间原型作为删减版正式发布。
