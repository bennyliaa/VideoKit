# RENDER02_FIX 三项修复独立整包复审报告 V1.0

2026-10-20；候选D1-20261020-RENDER02。依据D1_RENDER02_FIX_TESTER_REQUIREMENTS_V1.0.md及负责人本次正式离线派发。

**结论：PASS_OFFLINE_FIX_REVIEW_WITH_LIMITS。原三项问题均在本批有限离线范围通过复审，无新增阻断缺陷。** 可提交负责人制定准确新设备批次；本结论不批准自动安装/运行，不代替新鲜占用、准确身份/范围/预算及原资源门。D1未通过，M0未启动。Android图像、听音、焦点、平台故障与峰值仍NOT_RUN。

本轮0次SDK/ADB/5037/设备/安装/占用查询、0次Android构建、0次unsafe探针。执行了独立JVM检查、官方缓存apksig验证和两次纯POM Gradle resolveProbe；后者无Android插件/编译任务、严格离线，仅在tester目录生成受控副本。未访问远程网络、未读取私钥/test_media payload或改动旧账本/UNKNOWN。

## 1. 冻结与实际产物

独立核404项磁盘冻结文件、ZIP403成员及准确字节/集合；1068项构建输入与新包一致。RENDER01原477项及旧ZIP全部保持原hash，原FAIL报告和证据未改。

| 对象 | SHA256 |
|---|---|
| 本批主交付报告 | 6417dcab0a33b42e4e70aa3cccc493ad71056451b3510db73eb6c557ef80e2e0 |
| seal | a226b5fe0703d31c486ec2deaad1c2f2241169f4c8257701331cd5d9c1a83581 |
| ZIP | 1b595b74f7fd02982806e251edbaf5261674a87e7de2599f3346fa21b7ea215b |
| App APK，10480388 B | 2f6e1cf02d85d8b0bd32ca0c475aea9e182a8b3b55e17a6da066a6ddfc5e2d94 |
| test APK，2695613 B | 88241afd1cfe50fee41be95d788d76948bdee24cec14a26329040f69970e63cb |

直接解析APK内二进制manifest、DEX类定义及五个方法codeOffset，不只搜索字符串：实际包com.videokit.d1present、versionCode2、min31/target36；App4300类，test2664类。Activity仍non-exported、:presentation，无launcher；CPU ordinary isolated :d1_cpu_worker；runner及targetProcesses准确。两APK使用既有准确apksig JAR在tester输出目录独立验证V2和单证书，证书SHA `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。

七native与RENDER01/C14准确字节相同，PCM asset不变，35坐标锁仍与E13F相同；ZIP/ELF arm64及16KiB静态布局通过。CPU JNI仍为C14 `ed02feb238b26ea2ac53b6ae2eafca3d3131d74ebfdfd52c39ff3a925648e9a7`，不冒充E13F的E6诊断JNI。新SBOM标签纠正不修改旧SBOM或旧事实。16KiB静态核验不是设备页大小测试。

## 2. META-PROV-01：PASS_CURRENT_OFFLINE_CANDIDATE

独立核原HTTP/POM/校验材料：固定Maven Central坐标com.google.guava:guava-parent:33.3.1-android，四份HTTP回执请求/最终URL相同、状态200，保存原件长度/hash匹配；20632 B POM SHA256 `6e11986ea7250b51f847157e2dc937f32a306804dfce0007a5e81ddb9b95c579`。SHA1/MD5与原件相符，asc原字节留存。

**这是本批新增来源证据，经此次独立离线核证接受为有限Debug候选的新元数据pin，不能称为历史批准。** SHA1/MD5来自同源，不能算独立发布者认证；asc未做PGP身份/信任验证，不登记签名身份PASS。本轮没有向远程重新取证。此有限准入不升级为上游发布者全链认证或发行合规通过。

候选实际verify-metadata=true，新增校验值准确仅上述1项；其余旧pins不变。源码构建命令明确--offline、--dependency-verification strict；settings只有本地镜像，显式POM/module来源，无google/Maven Central/插件门户fallback。最终005原日志/receipt成功，tester未重复构建Android。

### 实际消费闭包

独立从Gradle原始Dependency verification事件重新提取并核对327个唯一产物，而非枚举缓存冒充实际消费。每个坐标/文件/事件id、镜像字节及记录hash相同；135 binary、38 module、154 POM，192份实际描述副本全部核对，全部符合既有RENDER01 pins。新Guava parent和Foojay均未被最终005消费。

独立复核71条POM parent/import-BOM声明：记录中的70条直接对应实际验证坐标；另1条protobuf-parent:3.25.5声明protobuf-bom:${project.version}，原审计保留表达式而非臆造坐标。tester按该POM明确project.version=3.25.5解析，确认实际protobuf-bom:3.25.5.pom已被事件216验证，SHA `080e2984173238b50e064c226afffbb1b0233520295c790a7fd3d6ae4593f063`。因此不是缺失父/BOM；补充证据为protobuf-expression-resolution.json。module、插件marker和父/BOM分别有实际记录，不将未消费的新父POM算成最终构建证据。

### 独立正负校验

在tester全新隔离目录/Gradle home创建纯POM probe，使用准确新verification XML和只读镜像；强制Maven POM、忽略module重定向，关闭无关传递解析，不加载Android插件。

- 正向原POM：resolveProbe退出0，准确解析guava-33.3.1-android.jar。
- 负向只改parent副本：退出1，原HTML报告明确目标guava-parent POM的期望SHA为6e11986e…c579，实际为tester独立改动的 `91f9afe227c4c7ccad7394930839751f8ea317d7575fc31f5c8134e84574ad26`。
- 失败不是variant选择、checker-qual缺失或无关传递依赖；canonical镜像保持原字节。coder原负例的另一tampered hash是另一份控制副本，未混用。

原Gradle客户端正常返回，两次probe均有原日志/回执。本机客户端退出不额外冒称后台daemon的内部ACK；本轮未建立设备owner或SDK pending。该正负校验仅证明准确POM校验机制，不替代官方来源判断。结合最终真实192份旧可信描述闭包、metadata恢复与新增来源材料，原P1在当前有限候选范围关闭。

## 3. R02：PASS_INDEPENDENT_RACE_REGRESSION

修复准确区分bitmapDraw、post、cleanupPost。真实drawBitmap且原unlockCanvasAndPost返回后才增加画面提交；未绘制的清理post返回false。已实际绘制后才取消，不因gate变化抹掉旧事件，回执保留旧epoch及currentAfterPost=false。

tester使用此前独立有界Surface替身、原生产PlatformRenderer/WorkSession/source/registry，重新编译并执行：

| 独立场景 | bitmapDraw / post / WorkSession drawn / receipt | 原归还 |
|---|---|---|
| 原lockCanvas等待期间取消，后仅释放同一等待 | 0 / 1 / 0 / 0 | source/原线程真实返回，像素held0 |
| 已drawBitmap，在原post等待期间取消 | 1 / 1 / 1 / 1，旧事件currentAfterPost=false | 同原资源真实返回 |
| 正常六帧，实际生产renderer | 6 / 6 / 6 / 6，PCM提交576000 B、默认静音 | 原资源真实返回 |

两竞态均先确认原调用已进入，取消后原source/owner仍未返回，再放开同一有界等待。未kill/二close/换对象制造ACK。源码与回执计数一致，原误报复现现为0帧；不是Android实际Surface效果PASS。

同时独立跑冻结core九组，以及跨raw→PCM边界、错PID拒绝、未关闭handle时dispose拒绝、首consumer关闭后第二可读及最终原线程/数组归还；均PASS_CORE_ONLY。coder的seek/Surface五类回归及源码作为补充检查，不冒充tester独立实机结果。

## 4. R03：PASS_FROZEN_MANUAL_ENTRY_AND_POLICY

第五准确方法为 `com.videokit.d1present.RenderDeviceTests#manualIdleListenThreeSeconds`，runner仍 `com.videokit.d1present.test/com.videokit.d1present.RenderInstrumentation`。除准确class/renderCase/renderScopeSha256外，必须有 `renderManual=IDLE_LISTEN_3S_V1`；原四自动方法禁止此参数。

真实同包instrumentation通过startActivitySync启动non-exported Activity并传renderManualIdle=true，先确认session为空/Surface可用，再arm；不是依赖外部shell启动未导出Activity。准备窗5秒、点击窗15秒、随后原归还观察30秒分开。arm没有建立WorkSession、开启声音或请求焦点。只有明确Listen监听器claim一次点击，才在session.start前设置audible意图，使用完整576000 B原生成PCM；不再把已运行静音session当听音起点。

独立JVM策略校验：未arm拒绝、arm不启动、claim本身不等启动、一次点击、准确deadline拒绝、关闭窗口后晚点拒绝、无click调用started拒绝，均通过。源码核对UI只在明确Listen路径传initiallyAudible=true，其余四入口仍false/默认静音；DEX已定义第五方法实际代码。

无点击不是听音PASS；窗口结束会关入口并使测试失败。若已有session，@After仅cancel且原returned后才finish；原API/线程/source未返时，仍由原WorkSession/runner finalizer保管，不以观察超时finish。本轮没有实际启动这个Android入口，故同包真实启动、完整三秒听感、焦点授予/丢失和设备生命周期均NOT_RUN。

**576000 B提交及生命周期断言不等于三秒真实听到声音。** 焦点拒绝/失焦、用户提前静音/暂停/取消可能改变听感，必须独立记录人工结果；没人听或无批准回环就NOT_RUN，不能以方法成功或初始audible=true登记听音PASS。

## 5. 准入与残余边界

| 范围 | 判定 |
|---|---|
| 三项修复及受影响离线回归 | PASS_LIMITED，旧三项在本批范围关闭；RENDER01历史FAIL保留 |
| 当前来源/构建描述可信度 | PASS_CURRENT_OFFLINE_CANDIDATE，新pin接受依据和未验PGP身份明确；未称历史批准 |
| APK/签名/native/PCM/锁身份 | PASS_STATIC_ONLY |
| 新独立空包与权限 | 仍只是有限实验；同UID :presentation不是权限/RCE沙箱，J11全危险链未关；不代旧App升级/原T07或清旧UNKNOWN |
| 真机/声音/图像/焦点/峰值 | NOT_RUN，需新批准确派发及新鲜设备门 |
| 压缩音轨/持续NAS/AV同步/完整Sink与Kit/发行许可 | 原BLOCKED/NOT_GRANTED保持；本地PCM/raw不覆盖 |
| D1 / M0 | NOT_PASSED / NOT_STARTED |

仍保持6帧/30秒新准入、raw等待2/在途1、PCM等待4/在途1、64MiB已知像素、3秒PCM及原owner保管。64MiB预留不是RSS/BufferQueue/AudioServer或系统总峰值。没有新增FFmpeg音频白名单/codec，LGPL外发、模型/样本及全部P0继续原门。E11已有局部MP4/AVI/能力/指定取消有限真机PASS、C13 FAIL和其他NOT_RUN/UNKNOWN原样保留。

## 6. 后续整包设备方案

本报告主动交负责人，可据此制定准确新设备批次，tester不自动执行。先接受此次新包version2、准确APK/hash/签名及新pin有限准入；明确两APK安装、独立fixture只读准备、每方法原客户端和观测/文本/归档上限。不得继承已停止ENV/RESUME许可或余额，不操作其他项目/旧账本。

新鲜设备空闲、原owner/claim归还、准确工具/路由/身份通过后，同冻结候选按以下五个准确选择分别派发；每方法独立新进程，不能整class连跑重置预算。`class=完整类名#方法`，`renderCase=同方法`，`renderScopeSha256=届时真实批准范围hash`。第五项另加上述renderManual参数；语法hash不是执行权限。

| 入口 | 观察与界限 |
|---|---|
| generatedMutedDualConsumers | 全程静音、6次真实draw/post及PCM完整提交/排空；同原consumer/registry归还；同次批准截图核90°/颜色/PTS |
| existingMp4RawMutedDualConsumers | 新包私有basic.mp4仅349102 B、SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9；六个C14 CPU逐个原STOP/death/source返回；逐帧producer/PTS与截图；生成PCM不是MP4音轨 |
| cancelRejectsLateGeneration | 预暂停、实际raw在途且source未释放后取消；旧代拒绝与原线程/FD/callback归还；不扩大为永久Canvas/native卡死测试 |
| pausedSeekAndSurfaceRecreation | View原texture转交/新Surface可用、seek意图不冒ACK；恢复后新代实际帧、原对象归还与批准截图 |
| manualIdleListenThreeSeconds | 事先协调操作者已准备，避免15秒窗内临时等待答复；看到READY后一次明确Listen，从闲置完整源起点听音，记录操作者/时间/实际听感。5/15/30秒分栏，晚点无重试；无人观察NOT_RUN |

人工静音/焦点/暂停/取消按届时准确观察方案另列，不能破坏默认静音自动入口或用其他项目制造失焦。任何失败/未知停止依赖，保管同原对象/线程/源及SDK客户端，不能kill、强finish、二close、清数据或换scope求绿。既有一般真机授权沿用，无需重问；精确新批派发与现场门仍须成立。

## 7. 证据索引与移交

目录：`D:/CodexProjects/VideoKit/docs/tester/D1_RENDER02_OFFLINE_REVIEW_EVIDENCE`。

- independent-artifact-audit.json、两APK实际manifest解析、signer-verify.stdout：冻结/DEX/签名/native身份。
- independent-metadata-consumption-audit.json、independent-pom-rejection-audit.json、independent-pom-probe原日志/报告/输入绑定：新来源和真实校验拒绝。
- independent-source-boundary-audit.json、protobuf-expression-resolution.json：71声明边、精确复用及人工入口接线。
- independent-faults.stdout、independent-normal-renderer-audit.json、baseline-core.stdout、checks及source-pins/原进程回执：独立竞态/正常与策略回归。

报告冻结后发送负责人；本轮保持设备停止，无自动实机或M0推进。
