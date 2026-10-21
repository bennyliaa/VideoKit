# 单 App / 独立 AAR 隔离方案 V1.0

日期：2026-10-05；C07研究交付，方案未选定、未准入、未实现产品CPU流水线。最多两条方案，均不需额外APK；本轮只修复已有Media3采帧源格式验证，不集成以下原生组件、不付费、不下载权重。D1仍BLOCKED，不进入M0。依据原文§2.2、§10.4–10.7、§11、§14、§16.2、§21–27及 [架构准入评审](D1_ARCHITECTURE_GATE_REVIEW_V1.0.md)；ordinary历史UNKNOWN=FAIL保持，不同条件未获准前不重跑。

## 1. 精确候选、许可事实及准入差距

| 组件/版本 | 官方事实与本轮用途 | 具体准入条件 |
| --- | --- | --- |
| FFmpeg n8.0：libavformat/libavcodec/libavutil/libswscale/libswresample | [该tag LICENSE](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/LICENSE.md)基线LGPL-2.1-or-later，选用GPL部分会改变组合许可；启用version3或某些外部依赖会影响版本。[AVI demux](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavformat/avidec.c)、[MPEG4视频decoder](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavcodec/mpeg4videodec.c)提供当前AVI/MPEG4-part2 CPU路径候选；不是只支持H264的decoder替代 | 自编译白名单、禁GPL/nonfree/version3及未审外部库，保存全部源/patch/config/ELF依赖/许可/SBOM/hash。tag和单文件头部不是完整构建合规证明。n8.0是明确研究基线，不声称当前无漏洞或已适合发布；实际准入前核查精确版本漏洞及必要补丁 |
| OpenH264 v2.6.0（仅方案B的H264软件编码） | [精确版本LICENSE](https://raw.githubusercontent.com/cisco/openh264/v2.6.0/LICENSE)的两项BSD条件允许源码/二进制分发并要求保留相应版权、条件及免责；[README](https://raw.githubusercontent.com/cisco/openh264/v2.6.0/README.md)记录Android/arm64和构建说明。FFmpeg n8.0有 [libopenh264 encoder适配](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavcodec/libopenh264enc.c) | 必须审源码与实际native依赖/构建。源代码许可与Cisco预编译二进制的专利安排不同；[binary license](https://www.openh264.org/BINARY_LICENSE.txt)有独立条件，不能把它的专利安排移用于自编译AAR。未下载Cisco二进制，未承诺H264专利已清算。质量/吞吐/帧跳过、码率和设备最低条件需实测 |
| AndroidX Media3 1.9.3，既有审核锁定版本 | Apache-2.0既有依赖，仅C07已有host Debug源验证/控制与实验回归；不会成为CPU decoder | Android平台codec不因Media3调用而在ordinary isolated中自动可用；C06反例保持。CPU路线若重用Java字幕/解析器，只能部署在isolated并另外验证预算/复杂字幕，不能把host解析残留当隔离完成 |
| 项目JNI与broker/域模型 | 独立自有实现，已有有限task/epoch/lease协议可复用概念 | 生产AAR去掉实验包名硬编码与测试压力入口；复用协议证据不表示完整新CPU管线安全通过 |

FFmpeg不是全部GPL，也不是LGPL一律不能用于闭源。官方 [许可清单](https://ffmpeg.org/legal.html)说明无GPL/nonfree的动态库路径和对应源码、修改/构建资料、通知/EULA等义务；它没有提供付费购买专有许可以取消开源义务的路径。动态链接只是合规路线一部分，独立进程不消除义务，静态链接也不能默认免除可重新链接/替换材料。具体AAR、APK、闭源宿主及商店发行条款需一并审定，不能仅凭“不启用gpl”宣称批准。

Android商店准入待审事项：随AAR交付匹配源码/修改/许可证/NOTICE和链接材料，确保消费方可遵守替换或重新链接及相关调试权利；EULA不得笼统禁止许可允许的修改调试。APK签名、ABI、库名/加载方式、宿主自身发行和商店规则需要具体方案，不能依赖远程下载可执行库作为未经验证的合规捷径。H264/AAC/MPEG4/AC3等专利或地域发行条件独立于代码版权许可；需负责人安排法务/发行审查，当前没有商店合规承诺或收费授权。

## 2. 可实施构建提案（未运行）

两方案均以源码n8.0、Android API31、arm64-v8a为最小验证目标，NDK30.0.16248370是本机已装候选工具，是否兼容仍须选定后构建证明。[n8.0 configure](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/configure)有按decoder/demuxer/parser等白名单及禁网络/自动探测选项。以下为可审定的命令形状，不是已成功构建配置：

```text
--target-os=android --arch=aarch64 --enable-cross-compile
--enable-shared --disable-static --disable-programs --disable-doc
--disable-autodetect --disable-network --disable-protocols
--disable-gpl --disable-nonfree --disable-version3 --disable-hwaccels
--disable-avdevice --disable-avfilter --disable-everything
--enable-avformat --enable-avcodec --enable-avutil
--enable-swscale --enable-swresample --enable-pthreads
--enable-demuxer=avi,mov,matroska
--enable-decoder=mpeg4,h264,aac,mp3,ac3
--enable-parser=mpeg4video,h264,aac,mpegaudio,ac3
```

方案A不启用外部库/encoder/muxer；方案B在此基础上增加 `--enable-libopenh264 --enable-encoder=libopenh264,aac --enable-muxer=mp4`，只链接单独固定v2.6.0的OpenH264动态库。OpenH264构建提案是官方Makefile的 `OS=android ARCH=arm64 NDKLEVEL=31` 共享库路径，工具链/sysroot/pkg-config必须隔离指向该ABI版本。实际configure可能自动选择内部依赖，必须检查生成config_components、最终license/version报告、每个ELF NEEDED及源码清单，不把这些参数当完整许可审计。

严禁libx264/libx265/libxvid/GPL滤镜、nonfree库、未审FDK/SSL/网络协议自动混入；当前方案不需要宿主凭据或NAS协议实现。最小白名单只验证现有AVI MPEG4/MP3与MP4、MKV/AC3等代表路径，不代表已覆盖原文所有格式。后续补webm/ts/图片/复杂字幕或其他codec时逐组件再审和测试，不能静默删去正式格式矩阵。

使用自有AVIO适配而非ffmpeg命令行/文件URL：[n8.0 avio.h](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavformat/avio.h)支持自定义读写/seek回调及中断回调。只把宿主opaque token/broker授权的短读、64位偏移和长度映射到回调；不传文件路径，不启用file/网络protocol。中断回调不是任意CPU/native调用都能强制停止的保证，超时后须走真实worker死亡/资源账本。

## 3. 两条进程及数据路线

### A：CPU解封装/解码/分析隔离，宿主只接收裸帧/PCM并用系统编码

```text
Host普通UID：只读SourceBroker、调度/租约/临时Sink、Flutter或原生UI
  -> 同APK ordinary isolated任务UID：FFmpeg CPU探测/解封装/解码/色彩归一
     -> 后续已准入检测/跟踪/遮罩（同一任务边界）
  -> 有界、复制并校验的裸YUV/RGBA/PCM + 实际PTS/格式/方向
  -> Host渲染/音频，OS MediaCodec系统编码（输入只含验证的裸数据）
  -> 宿主临时Sink -> 独立ordinary isolated输出验证 -> 宿主READY/事务
```

FFmpeg decode API使用send/receive处理EAGAIN和drain/EOS，不用忙轮询等待：[n8.0 avcodec.h](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavcodec/avcodec.h)。Host不能重新解封装源文件、把不可信压缩流交回host内native decoder，或无界分配worker声明的图像尺寸。输出验证也不能直接沿用host内MediaExtractor解码当作隔离已完成；建议另一个ordinary isolated验证任务用CPU FFmpeg重新探测/完整解码，给宿主有界验证汇总，正式双轨/PTS/覆盖规则保持。

优点：不依赖ordinary isolated硬件codec，最小CPU构建只有FFmpeg库，OS编码可望降低编码开销。未证明项：Host的JNI/渲染/音频和系统codec客户端仍可能有native风险；裸数据校验减少压缩解析攻击面但不是绝对崩溃保证。必须故障注入验证这些宿主环节，若不能满足§27，不准入而非降低隔离。1080p多帧复制/转换、同步、热/电量和硬件输入格式需实测。

### B：CPU全编辑导出在ordinary isolated，FFmpeg + OpenH264软件H264/AAC

```text
Host普通UID：只读broker/任务预算/句柄与UI，不解析压缩媒体
  -> 同APK ordinary isolated任务UID：CPU探测/解码/分析/遮罩
     -> OpenH264软件H264 + FFmpeg原生AAC -> FFmpeg MP4 muxer
  -> 宿主授权临时写Sink/broker（无源路径）
  -> 独立ordinary isolated CPU全解码/双轨/PTS/覆盖验证任务
  -> Host只核对认证任务/租约/验证汇总及物理输出状态 -> READY
```

软件AAC候选为n8.0 [aacenc.c](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/libavcodec/aacenc.c)，不是FDK AAC。控制面、preview仍用方案A同样的有界裸数据出口；CPU编码不赋予worker网络/GPU权限。输出AVIO回调须支持muxer要求的受控seek/write/flush，能力不足预先拒绝。真实writer FD/lease若由host授予也只限本task；若走写broker，必须保持实际写消费者、epoch、close/fsync/死亡门禁。

优点：高风险编辑、编码与解析可放同一个低权限任务进程，避开该平板ordinary硬件创建失败；独立验证不在Host解码输出。未证明项：CPU性能/内存/发热、H264 profile/码率/帧跳过和正确时长、独立软件验证的共模风险、OpenH264专利/分发、isolated动态库加载与NDK线程权限实际行为。纯CPU不是天然安全，也不保证所有设备实时或12路活跃。若最低设备不能满足合理预算，有限实验后退出，不能无限放宽性能或删除自动跟踪P0。

两路线中的检测/跟踪/图片/字幕模块尚未选定或实现；当前只指定数据/进程边界，不能宣称危险链已经完整。复杂ASS若需libass/font等组件，必须另审精确版本/依赖/字体/排版和预算，本文没有把未经核查组件默认引入。无权重自有对照可用于最小数据流验证，但不替代最终人脸/物体P0。

## 4. Kit接入、权限、TOCTOU和资源协议

Kit以api/core/android-worker可选AAR分发，SDK可独立无Flutter调用。Service随AAR Manifest合并到宿主APK，非exported/isolatedProcess、组件名和兼容版本明确；用公开bindIsolatedService实例名约束和预算建task进程，不能硬编码D1 host包名/companion签名权限。不同宿主各自在自己的APK/UID内运行自身broker；从App实际UID、会话登记的isolated UID/PID、Binder对象及task/owner/epoch认证每条回调，不允许请求方自报UID通过验证。Manifest冲突、R8、ABI和minSdk31、服务实例可用性须最小宿主AAR测试证明。[Android Context API](https://developer.android.com/reference/android/content/Context#bindIsolatedService(android.content.Intent,%20int,%20java.lang.String,%20java.util.concurrent.Executor,%20android.content.ServiceConnection))只是公开接口依据，不是实际CPU管线成功证据。

数据面优先有界复制：worker可写共享区先复制到Host自己的不可变缓冲再校验和消费，不能校验后继续直接读仍可被worker修改的区。尺寸/plane offset/stride/总长计算用检查溢出的64位算术；拒负值、超预算、重叠越界、错误格式、非法PTS/音频通道、超大字幕与消息。每个任务独立序列/generation、最多固定在途帧和固定字节额度，Host不信任worker声明内存。只读封装共享内存须证明写权限撤销/无残留可写mapping，未证明之前保留复制路径。

研究初始预算提案：单task 2在途帧、16MiB共享传输总额、PCM单块64KiB、输入单读64KiB；验证先用原256×144/3秒与AVI原10秒，逐级升分辨率。它们只约束跨进程出口，不等于decoder内部峰值限制或正式设备阈值。CPU内部max_pixels、线程数、包/解码队列、内存占用和超大声明必须独立控制并测量；不能先解码4K再以出口限额宣称峰值已安全。

取消分两级：合作式停止读取/推理/编码，超预算则经已认证task进程自停或受控死亡路径；普通第三方Host能否可靠终止isolated hung进程及Binder death/PID核验必须真机证明，不假定同UID kill适用于isolated UID。等待超时只结束调用；未证死亡/实际I/O排空/FD关闭则quarantine、预算不回收、不READY、不删仍有writer的文件。task死亡不能释放另一个task/槽；全局系统OOM/用户停止App不承诺绝对存活，但源安全/未提交恢复仍必须成立。

验证worker也可能被恶意输出触发，故它独立有界、只读输出、不可得最终提交权限。宿主除汇总还核对真实输出长度/lease/任务认证，失败只abort；READY≠COMMITTED、同task查询未知READY、跨owner恢复仍保留。验证两个相同decoder路径有共模风险，不能以第二进程消除效果验证；正式遮罩覆盖依实际PTS和真实标注。

## 5. 最小验证清单、停止条件与负责人选择

当前倾向先选A做有限最小验证，因为少一个软件encoder及其额外许可/性能门禁；若其Host系统codec客户端的安全边界无法成立，再评审B。方案尚未选定，本轮没有实现CPU原型或配置这两种构建，不把这段倾向当准入。现有缓存只有已审核Media3可用，不具备已审核FFmpeg/OpenH264 Android CPU产物；不借此下载未准入二进制。

负责人选定并完成组件构建准入后，一整批最小验证：

1. 源码来源/版本/许可与完整构建白名单、可重复ARM64 API31 ELF、无网络协议及实际license/NEEDED/hash；最小宿主只消费AAR，不另装APK，两个不同宿主各自授权，Manifest/R8/API不暴露第三方类型。
2. 普通isolated真实FFmpeg AVI/MPEG4/MP3、MP4/H264/AAC及MKV/AC3读/seek/解码；原10秒actual frame PTS、短读/未知长/2GiB偏移/断连/错格式/损坏输入；无Host压缩解析回退。有效控制与真实格式错误均要证据。
3. 真帧/PCM复制、溢出/长度/stride/PTS反例与共享区修改竞态；不同task串包、过期epoch/伪UID/PID被拒；2帧/字节/队列额度和CPU内部峰值实测。
4. 实际sample后cancel、native SIGSEGV、hang、进程死亡与真正OOM分开；另一槽/Host存活、SourceReleased真实账本、输出FD/writer/lease和保留未知quarantine。普通压力模式不能充当OOM证明，不重跑既有ordinary codec负探针求PASS。
5. A验证系统裸数据编码/渲染客户端边界，B验证软件H264/AAC完整输出；两者独立输出CPU解码、T01/T02、READY丢响应/恢复、跨owner、无成功partial、源hash不变。保持预设两轨，与采帧1视频0音频契约分开。
6. 手机/平板各一次最低可用资源/耗时/热预算；方案选择后评审合理阈值再升载，最终1/4/9/12混排和M5/M6效果质量仍按原需求阶段执行。

失败退出：任何GPL/nonfree/许可不明依赖混入、无法满足SDK/商店义务或专利权利不清，停止该构建准入；ordinary无法加载CPU库/回调/合法终止hung task、宿主危险解析残留、实际资源不可收束或另一槽被拖垮，停止该路线并提交具体证据；最低设备CPU处理持续超可接受资源预算，则以真实测量报告比较另一方案，不循环调大上限。未取得模型权利/标注质量不能发布跟踪模块。路线都不满足时D1继续BLOCKED，必须负责人另作实现或需求决策，不能自动采用companion产品化。

本轮网上核查仅官方tag源码、许可证和公开API文本；未对FFmpeg/OpenH264源码包完整取hash、构建或新漏洞扫描，也未声称已获商店/法律批准。源核查入口和失败获取记录在C07证据目录保存；新CPU组件不是当前APK/SBOM的一部分。
