# MEDIA3 CONTAINER02 集中修复交付 V1.0

2026-10-21。候选D1-20261021-MEDIA3-CONTAINER02-FIX；提交负责人核整包后决定独立交测。

**MC-B01的暂待错误已在新候选修复并完成源码/生产JAR优先自检，等待独立复审。** 原REOPEN正常应答但原线程/observer尚未返回时，检查保持暂待、不记首错、不消耗尚未执行的检查资格；同一原任务实际返回后复用同一Provider继续，REOPEN始终1次。真实超时、取消、权限、坏应答及UNKNOWN保持原失败。真实容器目标继续OPEN/NOT_RUN，D1未通过、M0未启动。

## 具体变更与边界

生产源码仅TemporaryOutput变化：主机检查与既有verifyAndValidate复用同一重开准入函数；实际源资格成功前不标记检查已开始，去掉将所有前置暂待笼统记首错的外层catch。真正调用/检查失败仍由原失败处理保留。已完成结构结果只可在原归还门通过后读取同次缓存，不二次解析；该真实成功路径尚未运行。

[顺序决定](D:/CodexProjects/VideoKit/docs/coder/D1_MEDIA3_CONTAINER02_FIX_ADMISSION_ORDER_V1.0.md) 说明等待、实际开始、真实失败及缓存结果的区别；[源差异](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/evidence/source-differences.json) 与patch保全准确变化。HostMp4Inspection、MatureContainerRemux、输入适配器、原muxer binding及所有上游实现不变。无新平台替身、编码器、依赖版本或通用诊断框架。

输入累计8MiB、输出16MiB、块64KiB、总源2/每源在途1/queue0保持。原回调、observer、registry、worker和owner真实返回门保持；没有清真超时、改UNKNOWN为成功、重开替代任务或提前释放。主机结构检查仍不签发HOST_ISOLATED_FORMAT_V1，不设置validated/READY/COMMIT。原05受控validator协议回归不代表真实内容验证。

## 实际自测

| 检查 | 结果和准确范围 |
|---|---|
| 原独立复现输入重放 | ContainerB01Regression源码/生产JAR优先各8项；无cancel/abort干扰继续，REOPEN1次，真超时对照首错不清 |
| 集中顺序矩阵 | [22项](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/inspection-order-matrix.json)，源码/生产JAR优先各执行：12种入口/先后顺序及10项真实失败/取消对照 |
| 同Provider身份 | 只占一个现有源能力、保留第二槽空闲，重复同Provider被原工厂拒绝；该原能力归还后继续至真实边界，非反射修改产品状态 |
| 实际继续到的边界 | 主机入口抵达真实Media3缺Android类的失败；既有验证入口真实读4B全EOF/hash后由明确false的受控validator拒绝。两者不算容器通过 |
| 原返回 | 全部新顺序项join同一caller/worker，核同一whenComplete observer真实完成；最终source/output keeper0，无早释 |
| 完整文档入口 | 60条顶层进程回执exit0；包括两个明确NOT_RUN的平台probe，不是60项容器功能PASS。其余继承检查和新检查计数重叠，不求和 |
| 旧01/05边界 | 七组真实输入边界、原片known/unknown全EOF/hash、原返回/observer/响应/取消、partial UNKNOWN、63异常、88宿主返回、33转换、30因果顺序与7coordinator顺序等原套件均源码与生产JAR优先回放 |
| 输出路径门 | local_check、review_all各8项拒绝：旧01、旧05、候选内、伪前缀、越界、相对路径、根本身、复用子目录；拒绝不修改目标 |
| 必要严格构建 | 本批001集中离线strict成功，33任务全部执行；不联网、共享缓存写、SDK现场/ADB/设备/占用操作 |

最后源码pin为local002，生产产物为build001。[完整回执](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/evidence/documented-review-prefreeze/summary.json) 保留原argv、时间、原进程返回、class origin及JAR优先身份。初次local001仅新测试中lambda捕获可变循环变量导致javac退出1；未运行产品测试。原错误日志、pin和经原pin验证的准确测试源码已保留；只修测试循环，未弱化产品门。

## 来源 许可与产物

继承原阶段B报告[4d8853e56b18de0605309a6ba627b674c222d8b846a670d4cb59754bc71a4e87](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/reference/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md) 对extractor/decoder1.9.3固定来源、许可及strict证据的有限离线准入。原报告整体FAIL及功能OPEN保留，不将其解释为本修复已独立通过。

本批17个运行坐标不变，app/settings两锁及verification-metadata与01逐字节一致；新增依赖/pin/二进制下载/版本变化均0。实际严格消费仍300项：123 binary、37 module、140 POM；每项坐标/文件/hash与01的消费闭包一致。见 [差异和准入范围](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/evidence/dependency-license-difference.json)、[继承准入](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/evidence/inherited-admission.json) 及更新SBOM。

生产JAR108666B，SHA256 757e53a49d92a9b2148417e0b37ed9680162a7709b1493029759e58ce08dfd8f。编译探针APK7094375B，SHA256 51d163ae79e4b3f92ca9417267806290b3924f66aba3f5871442a0c1d081c871。包com.videokit.d1input，versionCode7，D1-MEDIA3-CONTAINER02-FIX，min31/target36。无权限/新增组件/native/测试与平台端口，固定apksig验签证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；未安装或启动。[产物审计](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/evidence/artifact-audit.json) 和新测试排除审计保全实际身份。

## 冻结与重放

[seal](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/evidence/media3-container02-freeze.json) 与 [源码ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261021-MEDIA3-CONTAINER02-FIX-source.zip) 封存本批源码、实际JVM库、官方来源/许可、生产产物及原始自检证据。原视频、镜像/Gradle缓存、JDK/SDK和classes目录不入ZIP。

使用已有JDK/Python、该新候选专属根下尚不存在的绝对子目录：

```powershell
& 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/tools/review_all.py --output D:/CodexProjects/VideoKit/docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/reviewer-001
```

入口只在新外部目录编译和执行，生产JAR优先；冻结后先核全部seal/源pin，无Gradle/网络/共享缓存操作。已批准原片仍是独立只读输入，大小349102B、SHA256 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9；前后不变，缺片或hash不符不从网络补下。

## 保留的缺口与交接

[MC01–MC32及MC-B01映射](D:/CodexProjects/VideoKit/docs/coder/d1media3-container02/completion-matrix.json) 区分本修复证据和原功能限制：真实MP4/fMP4提取、合格单AVC256×144六样本、真实mux/remux→Sink→格式重开、坏atom内部内存界、真实SeekMap、NAL/CSD/时基/EOS最终duration均OPEN/NOT_RUN。实际结构正例/缓存继续、解析过程中的权限变化也未运行；22项前解析顺序通过不能替代它们。Android FD/fsync/codec、隔离内容/死亡/时序、业务提交和播放仍NOT_RUN。

原9批冻结共5556项hash保持一致，含01的1045及05的828；原独立报告和封存证据逐项保全，原P2/FAIL不回写。P0/J11、独立Kit/Flutter、历史FAIL/UNKNOWN及FFmpeg/release/model/media许可问题不因本包关闭。D1 NOT_PASSED，M0 NOT_STARTED。

请负责人先核完整新冻结，再统一安排独立复审；本批仅给出coder修复自检结论，不自行关闭MC-B01或启动阶段B、设备及原E3许可。
