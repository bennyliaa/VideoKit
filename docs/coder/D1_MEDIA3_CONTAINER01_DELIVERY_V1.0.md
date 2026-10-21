# D1 MEDIA3 CONTAINER01 开发交付 V1.0

2026-10-21。候选 D1-20261021-MEDIA3-CONTAINER01，交负责人审阅后决定阶段B。

**结论：完成有限读取进展和容器薄适配交付，真实容器写入与结构重开尚未成功执行。** 已执行真实 Media3 DefaultExtractorInput 经原 DataSource/readAt 的读取、短读、未知长度、截断和取消迟返；已批准原 sample.mp4 的349102字节全EOF/hash按已知与未知长度分别核对。实际 MP4 提取器、muxer 构造受 JDK 缺 Android 类限制，且原视频参数不符合六样本写入要求。不能将本批标作容器链路 PASS、Android 效果 PASS 或完整项目交付。

## 交付内容

- [候选源码及证据](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/completion-matrix.json)：阶段A MC01–MC32逐项状态、原始用例、实际证据与 NOT_RUN。
- [接口和比较规则](D:/CodexProjects/VideoKit/docs/coder/D1_MEDIA3_CONTAINER01_INTERFACE_DECISIONS_V1.0.md)：EOF/hash与结构分层、绝对seek、NAL/CSD/时间基规则、EOS及原归还。
- [生产源码变更](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/evidence/source-differences.json)：新增 HostMp4Inspection、MatureContainerRemux，TemporaryOutput 新增独立主机检查及其取消/失败门；原输入适配器、muxer binding和全部上游保持原样。
- [封存清单](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/evidence/media3-container01-freeze.json) 与 [源代码 ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-MEDIA3-CONTAINER01-source.zip)。原 sample.mp4、Gradle镜像/缓存、JDK/SDK和编译目录不进入ZIP。

## 实际运行与缺口

| 范围 | 实际结果 |
|---|---|
| 真实 DefaultExtractorInput→DataSource→原readAt | 七组新边界检查（含8MiB耗尽后读取前拒绝）：短读3+3+1、已知EOF、未知长度截断、绝对位置重开、取消迟返及原返回、能力先拒绝和检查失败不READY |
| 已批准 sample.mp4 只读读取 | known/unknown各一次349102字节，SHA256 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9；原handle/runtime返回，读取不代表MP4解析或解码 |
| 完整源码/生产JAR优先回归 | 最终文档入口56条顶层进程回执exit0；其中含两个明确NOT_RUN平台probe，不能将56当作独立功能PASS数量；嵌套编译/20组core另有原回执 |
| 05既有边界 | 20core、17原返回、tester23、63异常矩阵、5输入异常、88宿主返回值、33状态转换、原response2、30因果顺序、7coordinator顺序、8额外宿主返回等原套件在新源码和生产JAR优先环境回放；计数重叠，不相加 |
| Mp4Extractor | 实际构造首遇 android/content/pm/PackageManager$NameNotFoundException；轨道/样本/SeekMap/畸形解析 NOT_RUN |
| FragmentedMp4Extractor | 实际构造首遇 android/os/Parcelable；fragmented结构解析 NOT_RUN |
| FragmentedMp4Muxer | 实际构造首遇 android/util/SparseArray；真实编码payload写入及重提取 NOT_RUN |
| 合规fixture | 原sample为320×180、含AAC、8秒，与单AVC256×144/六样本不符；拒绝写入资格，无新编码器/转码/伪NAL |
| 最终严格构建 | 离线strict metadata、LockMode.STRICT，最终004成功；002曾完整执行33任务，003及004因判据和精确预算修订各执行4/复用29；001仅Gradle通信启动失败，日志保留 |
| 平台FD/fsync、真实codec、隔离内容、业务COMMIT/播放 | 全部NOT_RUN；APK只作未安装编译探针，无设备、SDK现场命令、ADB、占用或旧handle查询 |

最小JDK仅沿用原 URI、errno、WorkerRule 明确端口，未添加其他平台替身；真实Media3字节码未改。平台probe输出成功退出只说明准确记录了失败，绝不说明容器功能通过。新主机检查的 kind 为 HOST_MEDIA3_MP4_STRUCTURE_V1，失败不会签发 HOST_ISOLATED_FORMAT_V1 或进入 READY/COMMIT。既有受控validator回归只检查协议边界，不是产品验证。

新读取/结构适配保持输入8MiB累计（包括hash与重读）、输出16MiB、块64KiB、源2/每源在途1/排队0；仅有限轨道/样本记录。**尚未证明真实提取器面对恶意atom声明时的内部内存分配上限，也未验证完整尾部语义、NAL归一化及最终duration。** 这些项目在32项映射内保留NOT_RUN，不能由静态源码或原始字节截断测试替代。

## 来源 许可与产物

[新增使用准入材料](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/evidence/extractor-source-admission.json) 保全运行前取得的 [Google官方extractor POM](https://dl.google.com/dl/android/maven2/androidx/media3/media3-extractor/1.9.3/media3-extractor-1.9.3.pom)、[decoder POM](https://dl.google.com/dl/android/maven2/androidx/media3/media3-decoder/1.9.3/media3-decoder-1.9.3.pom)、同版本module及 [AndroidX许可](https://github.com/androidx/media/blob/1.9.3/LICENSE)。AAR与module原pin一致，classes.jar逐字节来自该AAR。两条新官方POM pin明确记录，旧pin逐条不变；未下载新二进制、升级或关闭校验。

最终实际验证300项：123 binary/37 module/140 POM；相对05新增两份binary和两份module消费，POM两条是来源材料及精确pin，不能冒称新增实际POM消费。运行坐标17，相比原15只增加同版本extractor/decoder。原新增使用许可独立审阅和SBOM继承保全，本批独立准入仍PENDING；自检不签发独立结论。

生产JAR108476B，SHA256 57f07b9f841487a5e76750ed0380656f72862e60caeef78a4ae9cb40d42e527e；实际生产JAR优先class origin见回执。编译探针APK7208106B，SHA256 0979fc8fc8428f5ee8ada6fb4859450aa8a39f5acd67bba0d7872310bb7ea3aa；包com.videokit.d1input，versionCode6，D1-MEDIA3-CONTAINER01。无权限/组件/native/test/platform端口，JDK+固定apksig验签通过，证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。见 [产物审计](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/evidence/artifact-audit.json)。

[原视频资格记录](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/reference/approved-sample-scope.json) 保全 Blender Foundation 署名、CC BY3.0、原来源及hash。未将原媒体入源码ZIP。记录了未来合法生成方法：另外准入合适编码工具后，从有权内容创建新文件，单AVC256×144、无音频、6帧5fps、无B帧、首keyframe、PTS0..1000000us及EOS1200000us，保全工具版本/参数/许可、SPS/PPS、NAL表示和每样本hash。该方法尚未执行，未自动扩大FFmpeg或原视频处理范围。

## 重放和原返回

在本工作区现有JDK/Python下，使用新的绝对输出子目录；不需要Gradle、网络或共享缓存写入：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/tools/review_all.py --output D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/reviewer-001
```

输出必须位于该候选专属review根下的新子目录；旧候选、候选自身、前缀相邻目录、越界、相对路径、根本身等均拒绝。两个入口各七项负例已实际执行；封存后入口先核全部seal和源pin，再在外部编译，并以生产JAR优先重放。原sample.mp4为单独的已批准只读输入；缺少或hash不符时不能执行对应正例，也不从网络补下。

最终完整自检原回执在 [documented-review-prefreeze](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/evidence/documented-review-prefreeze/summary.json)，标注CODER_SELF_CHECK，非tester阶段B。所有进程、原read/close/coordinator线程及observer实际返回条件均由原套件检查；caller结束、ACK或counter0不替代它们。平台probe没有建立有效muxer，不能声明其writer真实完成。既有受控异常/取消场景结束时source/output keepers均0。

复核入口首次迁移漏改动态JAR路径，父入口exit1；子入口编译和20组core已退出，记录与出错脚本保留。只修复工具路径，随后完整入口重新运行；不把早期失败抹成通过。source/suites早期运行亦保留，最终源码为local007；产品JAR来源最终build004。

## 后续条件与状态

[32项集中映射](D:/CodexProjects/VideoKit/docs/coder/d1media3-container01/completion-matrix.json) 是自检说明；源码存在不等于实际运行。进入真实正例至少还需准确Android运行环境及负责人另行派发的资源/隔离条件、资格化六样本fixture、原FD/fsync/close与只读授予证据、完整轨道/样本/时间基/EOS与坏输入验证。现阶段没有成功的编码容器或隔离验证收据供业务使用。

原8批冻结共4511项hash一致，包括05的828项；05独立有限PASS不变。阶段A完整报告edb4cd48b9bd1c04f0d1f9ddff5f80a6a16257e0055a7aa4c3eb000a303870d7及32用例已原样引用。原P0/J11、独立Kit/Flutter、历史FAIL/UNKNOWN、有限真机结论及FFmpeg/release/model/media许可问题不因本包关闭。D1 NOT_PASSED，M0 NOT_STARTED。负责人审阅本整包后决定阶段B或下一批条件；本包不新增执行许可。
