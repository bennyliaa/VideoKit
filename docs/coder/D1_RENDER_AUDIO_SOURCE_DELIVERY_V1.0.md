# D1 RENDER01 呈现、PCM声音与共享源整包交付 V1.0

2026-10-20；candidateId **D1-20261020-RENDER01**；无Git commit。实施、自检和最终离线app/test构建完成，交负责人整包审查；**Android真实运行、画面、听音和焦点均NOT_RUN；D1 NOT_PASSED，M0 NOT_STARTED。** 没有设备/SDK现场命令、ADB/5037、旧handle/会话、live registry或占用查询，没有安装/启动/播放/录音/清数据/杀进程，也未读取test_media payload。

## 已实现的有限行为

有限raw来源接平台Canvas/Bitmap/Surface，保留原PTS/rotation、呈现task/sourceVersion/epoch、原CPU producer身份与surface generation；有明确生成对照和既有C14 MP4真实来源入口。PCM是本地生成的3秒低幅48kHz双声道PCM16，默认静音，只有明确Listen才申请焦点/发声。两个真实consumer打开同一只读presentation provider，原render/audio线程和平台对象归还后才分别退租；只结束一个不得释放全源。线程池终止标志、线程体结束、取消响应或30秒观察窗均不代原线程退出。

代码和技术UI在新目录；实验包com.videokit.d1present/版本1，Activity和instrumentation在:presentation，CPU服务ordinary isolated。**这是新空沙箱实验，不是旧com.videokit.app升级，不能用于绕过原手机禁用/旧任务UNKNOWN或设备占用。** 新身份及fixture准备需负责人审查后另定准确部署/测试范围，本包没有自动执行资格。旧冻结源码、制品、账目和行政false/UNKNOWN未修改。

核心、Android平台端、技术Activity分目录；本批没有Flutter、SkinKit、AAR、正式时间线/跟踪/导出。有限snapshot和生成PCM不能替代持续播放、压缩音轨或AV同步。全部原P0与M0自有Flutter Theme/完整18页PPT UI、每批1–3个完整里程碑规则保留。

## 需求完成与真实证据分栏

| ID/范围 | 实现状态 | 验证状态 | 实际代码/边界 |
|---|---|---|---|
| R1 既有raw→Canvas/Bitmap/Surface、PTS/rotation/代次 | DONE_LIMITED | NOT_RUN_ANDROID | RawSources / RawFrame / PlatformRenderer；真实C14 MP4只读入口与生成对照入口已接；当前CPU实际源为256×144。截图、实际方向/Surface效果仍未运行。 |
| R1-LIFE 暂停/seek意图、Surface销毁重建/迟到/取消 | DONE_LIMITED | PASS_CORE_ONLY; NOT_RUN_ANDROID | PlaybackGate / PlatformRenderer / WorkSession；意图与owner ACK分开，原Canvas/Surface/texture sticky UNKNOWN；有限snapshot非持续播放器。 |
| R2 合法生成PCM→AudioTrack/焦点唯一owner | DONE_LIMITED | PASS_POLICY_ONLY; NOT_RUN_ANDROID | PcmFixture / AudioFocusPolicy / PlatformAudio；48kHz双声道PCM16、3秒576000B、默认静音/明确Listen；焦点和真实听音需另验。 |
| R3-SOURCE 同provider双consumer/原归还聚合 | DONE_LIMITED | PASS_CORE_ONLY; NOT_RUN_ANDROID | PresentationSource / E13SourceGroup / WorkSession；真实bridge/registry/原线程测试成立；第一consumer不释放全源。不是全部NAS/产品consumer。 |
| R3-THREAD 原executor/producer/owner线程退出 | DONE_LIMITED | PASS_CORE_ONLY; NOT_RUN_ANDROID | AsyncReadBridge.Runtime / CpuTaskClient / WorkSession；真实executor TERMINATED时原线程仍活的旧窗口被拒，外部join原线程后才归还；原冻结不改。 |
| LIMITS 6帧/30秒、1920×1080/8294400B、队列与64MiB | DONE_LIMITED | PASS_RULES_ONLY; NOT_RUN_PEAKS | Limits / Lane / WorkSession / PlatformRenderer；真实硬限额已接；64MiB为已知自持像素预留，非总RSS/驱动/AudioServer证明。 |
| R4-AUDIO 压缩音轨合法接续 | DECISION_DELIVERED | BLOCKED | 技术决定§6；未扩FFmpeg音频；PCM不关闭AAC/AC3/MKV/AVI音轨门。 |
| R4-SINK 持续源/完整Sink/成熟编辑接续 | DECISION_DELIVERED | BLOCKED_FULL_PRODUCT | 技术决定§6；沿用Media3薄适配首选与旧E11有限Sink实证；本批无导出或旧状态恢复。 |
| R4-KIT 独立Kit可提取与公共接口 | DECISION_DELIVERED | NOT_RUN_AAR | 技术决定§6；core/平台/UI分离，JNI旧包名保留；当前application非AAR，M0/M7职责保持。 |
| R5-BUILD 集中构建、自检、APK身份/源码一致性 | DONE | PASS_OFFLINE_BUILD_ONLY | main-010 / local-006 / apk-audit-002；最终app/test构建与V2签名核验通过。源码/本机测试身份和旧冻结未变核对，非Android效果PASS。 |
| META-PROV 构建描述文件完整历史校验 | PARTIAL | OPEN_BUILD_METADATA_PROVENANCE | build-metadata-gap.json；二进制校验strict与35锁保持；部分父POM无历史hash，未伪补批准，verify-metadata=false。 |
| SAFETY J11权限/RCE/全危险链、模型、全P0 | NOT_CLOSED | BLOCKED | 技术决定§1/6；同UID进程不是权限沙箱；模型/真实标签/质量及正式发行仍未关闭，D1未过/M0未启。 |

[机器完成矩阵](D:/CodexProjects/VideoKit/docs/coder/d1render01/completion-matrix.json)；[后端/权限/Sink/Kit具体决定](D:/CodexProjects/VideoKit/docs/coder/D1_RENDER_AUDIO_SOURCE_TECHNICAL_DECISIONS_V1.0.md)；[整批设备与效果入口](D:/CodexProjects/VideoKit/docs/coder/D1_RENDER_AUDIO_SOURCE_DEVICE_PLAN_V1.0.md)。

## 原生与依赖身份

Media3固定1.9.3，实际锁定35个Maven坐标与E13F逐字节一致，没有新运行时库或新codec/FFmpeg音频。Media3 muxer保持已审依赖闭包，不宣称当前已接ExoPlayer/Transformer完整产品。

七个native全部复用匹配C14来源，没有native重编。**其中6个与E13F相同；CPU JNI明确是C14字节，不是E6诊断JNI版本**，配套C14 Java只读frame协议一起复用；不把它作为旧E13F输出/恢复链的替换。五个FFmpeg/allocator库与lease库身份保持，未扩编解码白名单。补强的只是Java原input executor线程外部join，不改变native/codec实现。匹配native项目源码副本与来源pins已保留，完整上游源码及再链接/商店/EULA/专利等发行义务继续原门。

许可记录只继承既有本地Debug准入和本批差异；FFmpeg/LGPL外发、模型/人物/素材权利并未放行。source ZIP不是可发行SDK或许可证合规通过声明。

[候选SBOM](D:/CodexProjects/VideoKit/docs/coder/d1render01/render01-sbom.cdx.json)；[依赖/许可/native差异](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/dependency-license-difference.json)；[继承源差异与旧源未变](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/inherited-source-differences.json)。

## 自检、构建与实际产物

最终本机检查local-006有9组语义检查：队列/代次/布局/像素预算；真实焦点策略拒绝/失焦/静音无循环重试；生产executor TERMINATED但原线程仍活的尾部；同provider双consumer及audio最后归还；取消时在途与原线程尾部；错sourceVersion在平台前拒绝；原Future cause稳定错误/路径脱敏；同原close失败/迟到与一次显式重试；PCM精确身份与低幅。port替身明确不代表Canvas/AudioTrack、截图、听音或真实Android故障。开发早轮不累加为功能测试数。

APK集中构建最终为main-010，Gradle记录BUILD SUCCESSFUL in28s；main-009是首个通过的整包构建（38s），其APK已另存，之后仅对稳定源错误映射与取消前置作必要源码修复并重建。main-001至008的实际失败日志/receipt完整保留：缓存锁权限、离线缺失元数据/索引、严格校验缺少既有artifact/parent校验值等，不登记为设备或功能失败。没有隐藏成“首次即通过”。

实际补取了原校验值可核的公开POM/Gradle module描述文件，总2459570B/175份；没有下载二进制、SDK、模型、媒体或新版本。两个未取到的Foojay描述不在本候选/JBR固定构建路径中使用。为了绕开Gradle旧缓存索引缺失，准备了相同已核字节的标准本地Maven目录；该构建缓存不打进审查ZIP。

**构建元数据例外必须单列：**最终二进制校验仍strict，35坐标锁未变；补入的13项checksum全部来自已独立审查的E13F SBOM及相同缓存字节，没有自造批准。部分父POM（已发现Guava parent实例）没有历史批准hash，未把本次新算hash当旧许可，因此verify-metadata=false，记RENDER01-META-PROV-01 OPEN_BUILD_METADATA_PROVENANCE。镜像中已核元数据有单独pins，但不宣称所有间接父元数据完整通过；完整发行/供应链门继续OPEN。F旧独立工程本来未包含这个额外root verification XML，本批没有修改旧F设置。

[最终本机结果](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/local-006/core.stdout)；[最终构建日志](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/build-main-010/gradle.log)；[元数据缺口](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/build-metadata-gap.json)；[13项旧批准hash来源](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/runtime-pin-merge.json)。

| 最终制品 | 字节 | SHA256 |
|---|---:|---|
| [app-debug.apk](D:/CodexProjects/VideoKit/docs/coder/d1render01/artifacts/app-debug.apk) | 10566683 | `be7d4cc54b24d6a7955404834b18b1cf319ae745e2b4b928416e6a9ea796b236` |
| [app-debug-androidTest.apk](D:/CodexProjects/VideoKit/docs/coder/d1render01/artifacts/app-debug-androidTest.apk) | 2704490 | `b36a883dc542c43acad4316c0f4b550d7af80d0f0ab0beb4988e566fbedf1126` |

已用已有、核hash的官方apksig Java库在JDK中验证两APK V2签名，公共证书均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；没有读取/分发私钥或调用SDK现场命令。静态核7个APK native成员与来源完全一致、ZIP/ELF 16KiB布局，实际DEX含四个入口和平台实现、不含本机check harness；生成PCM asset精确，APK无真实媒体/权重/私钥。16KiB布局不代16KiB页设备运行。

产物审计初轮只接受merged_manifests，遗漏AGP test的merged_manifest路径而停止；已保留失败checker和原因，仅修正checker，未改APK/产品或为它重建。成功审计后又只读核canonical packaged manifest。静态/签名核验不是Android方法执行或图像/声音效果。

[最终制品/源码一致性审计](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/apk-audit-002/artifact-audit.json)；[官方库签名核验](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/apk-audit-002/signer-verification.json)；[实际packaged manifest核对](D:/CodexProjects/VideoKit/docs/coder/d1render01/evidence/apk-audit-002/packaged-manifest-crosscheck.json)。

## 硬边界、未测与交接

最多6帧/30秒准入窗，单帧≤1920×1080/8294400B，raw queue2/inflight1；自持已知像素/中间副本reservation≤64MiB，原CPU host frame也计入。PCM 3秒576000B、20ms3840B块、queue4/inflight1，默认静音。Bitmap实际allocation读回核对；peak是预留峰，非RSS。平台图形/BufferQueue/AudioServer/内核分配、热/最低设备/长时均未实测。

30秒后不再准入，原调用未返则保管原对象、原线程和预算；不强finish、kill、二close或退款。UI只有意图/状态，不锁等媒体IPC。技术决定详细区分View借用texture、转交texture、producer detach和owner ACK，不能把窗口销毁/进程缺席当原ACK。

同UID进程依旧不是权限/RCE沙箱，J11全链安全BLOCKED；当前空沙箱实验不证明Browser宿主安全。压缩音频、连续NAS播放、正式Sink/Transformer、全部consumer聚合/HostAction、独立Kit/Fake/公共版本、模型权利/真实标注/质量以及完整P0继续原矩阵。旧E11四方法有限PASS不撤销、不扩成当前候选效果；C13历史FAIL/C14未跑、手机差异、旧行政false与UNKNOWN不回填。

审查ZIP及外置render01-freeze.json固定本批源码、文档、native复用、生成PCM、依赖锁/SBOM、原本机/构建记录与最终制品，不包含约417MB本地Maven缓存、Gradle/JDK/SDK、私钥或test_media。完整构建输入与镜像pins另存，未声称离开现有环境就通过独立SDK构建。冻结后不改产品；完整一次交负责人审查，tester待新身份/范围/环境/预算正式派发后整批验证，不自行启动任何设备步骤或M0。
