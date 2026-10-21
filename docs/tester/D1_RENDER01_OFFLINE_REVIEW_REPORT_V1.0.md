# RENDER01 独立整包离线复审报告 V1.0

日期：2026-10-20。候选：D1-20261020-RENDER01。依据本批OFFLINE_REVIEW及原RENDER_AUDIO_SOURCE TESTER要求。

**结论：FAIL_OFFLINE_ACCEPTANCE / BLOCKED_DEVICE_ADMISSION。** 冻结身份、APK静态身份/签名、有限core与精确复用检查PASS；确认1项P1供应链准入缺口、1项P2可复现计数缺陷、1项P2人工验证入口缺口，集中交负责人统一派修复。Android效果、安装、真实画面/听音/焦点均NOT_RUN。D1未通过，M0未启动。

本轮执行0次ADB/SDK/5037/设备/安装/占用查询、0次Gradle或Android构建、0次unsafe探针；未读取test_media payload、旧在途对象或修改旧账本。仅静态读取、独立JVM检查及官方缓存apksig离线验证。新证据位于 `D:/CodexProjects/VideoKit/docs/tester/D1_RENDER01_OFFLINE_REVIEW_EVIDENCE`。

## 1. 身份、产物与有限PASS

独立核477个磁盘冻结项、ZIP476成员、完整集合及每项长度/hash，全部准确；1066项最终构建输入、50项旧来源、18项本机测试输入匹配。检查后再次核477项未变。没有重跑coder打包器或Android构建。

| 冻结对象 | SHA256 |
|---|---|
| 主交付报告 | 91414039f6f123f88a132c88c08c2bb3516644524ba960a9305caedd920a0f2a |
| 外seal | 995e7b5e9bc2bcdbbbbd600aa0a058f259b93ea56ac172fea90796c586f4e12e |
| ZIP | 6a5507548fc89eca9e62f6b62b78e32661e7368a863844125aa471ded00c462b |
| app-debug.apk，10566683 B | be7d4cc54b24d6a7955404834b18b1cf319ae745e2b4b928416e6a9ea796b236 |
| androidTest APK，2704490 B | b36a883dc542c43acad4316c0f4b550d7af80d0f0ab0beb4988e566fbedf1126 |

直接解析两APK内二进制manifest及DEX class定义/方法codeOffset，未仅在DEX字符串中搜索名字。App实际定义4299类，test2661类；WorkSession/平台实现及四个实际测试方法有定义，LocalSelfCheck不在App。实际manifest为com.videokit.d1present、版本1、min31/target36，Activity exported=false、:presentation；CPU service exported=false、ordinary isolated :d1_cpu_worker。test runner为RenderInstrumentation，targetPackage与targetProcesses准确。App有ACCESS_NETWORK_STATE，无INTERNET；test有REORDER_TASKS及测试框架组件，不能把Debug测试包称为零权限产品。

使用准确既有apksig JAR和独立输出目录重新编译核验器，两APK V2实际验证成功，单证书均为 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。未读取私钥。签名和当前字节准确不等于完整可信构建或发行准入。

实际APK七个native成员与候选native逐字节相同，arm64-v8a/ELF64、ZIP未压缩且数据偏移16KiB对齐、PT_LOAD布局通过。七项与C14准确相同，其中六项与E13F相同；CPU JNI候选为 `ed02feb238b26ea2ac53b6ae2eafca3d3131d74ebfdfd52c39ff3a925648e9a7`，E13F为 `2547b07d7d4b298e8b455c5f24d0d1fbcdf7068b016527edbf5f80f31d16191a`，明确不同，不能替换旧诊断/输出链回填结果。

C14 NativeCpu的decode/quotaProbe/decodePipelineFrame/verifyOutput名称、匹配C14 Java回调与原native源码一起保留。此次准确复用与Java改动仅限原input线程等待接口、bridge原线程join及有限read/seek接入；真实ABI运行仍NOT_RUN。RA-02静态路径为MP4_H264→PIPELINE_FRAME，只读固定fixture，不准调用继承诊断/故障探针。

PCM独立按整数溢出/截断规则重新生成，与asset逐字节相同：seed1447764006、576000 B、48kHz双声道PCM16、样本峰257、双声道一致，SHA `268d0e111f05ef5ad7ba405df6b78e5e8f6b3a43ebd926c48429d139a27da4ff`。APK没有打包真实媒体/模型/私钥。35坐标锁与E13F逐字节相同，13项补入hash在冻结E13F SBOM中存在；没有将这些二进制/历史记录扩大成完整元数据批准。

## 2. 独立源码及故障验证

核心预算与实际接线：6帧、30秒新准入窗、单帧1920×1080/8294400 B、raw等待描述符2/在途1、PCM等待4/在途1、块3840 B、总提交576000 B；默认静音，明确Listen才请求焦点。64MiB是已知像素预留门，包含source原帧、复制、读出、ARGB/Bitmap；平台对象头、桥临时buffer、Binder/驱动/BufferQueue/AudioServer等不构成实测总峰值。实际来源固定256×144，通用上限不代表1080p已验证。source持有最多六张有限snapshot，队列2只指工作描述符，不是持续解码buffer峰值证明。

WorkSession确实让两个consumer打开同一个PresentationSource，使用真实E13SourceGroup/LeaseRegistry和独立handle/读位置。第一consumer关闭不释放全代；平台owner线程join后才退consumer，最终还等待原loader及bridge executor原线程，再释放帧引用。外部join coordinator后才声明WorkSession返回。factory/平台返回不明时强持有且不以30秒强finish。

Surface的View借用、销毁转交及原Surface→转交texture释放路径分开，unlock/close异常保留sticky UNKNOWN。AudioTrack集中在原audio线程，唯一许可、默认mute、焦点策略拒绝/丢失不逐块重试，focus abandon后join原callback线程才归还；同UID :presentation仅是地址空间边界。未发现以新UID清旧UNKNOWN的源码路径，但不据此关闭J11。

独立JVM编译只使用冻结源与tester有界替身，全部本机进程正常退出，无本轮pending。结果分列：

| 检查 | 结果及范围 |
|---|---|
| 冻结core九组原检查独立运行 | PASS_CORE_ONLY；队列/布局、焦点策略、真实executor TERMINATED但原线程仍活的尾部、双consumer、取消、错version、Future错误脱敏、late close及PCM |
| tester新增跨raw→PCM边界读 | PASS；跨段字节正确，错PID拒绝；未关闭handle时dispose拒绝；第一关闭后第二仍可读，最终真实线程/数组归还 |
| tester新增实际PlatformRenderer取消竞态 | FAIL_PRODUCT_COUNTER，已复现R02；控制Canvas为替身，生产renderer/WorkSession/source/registry为原代码 |
| 两APK官方库签名独立重验 | PASS_SIGNATURE_ONLY |
| 真实Canvas/TextureView/AudioTrack、截图/听音/焦点 | NOT_RUN；不以JVM端口或编译代替 |

## 3. 集中缺陷与最小修复

### RENDER01-META-PROV-01 / P1 / CONFIRMED_OPEN

构建可信元数据准入未通过。`gradle/verification-metadata.xml:4` 实际为verify-metadata=false；main-008日志16行曾在debugRuntimeClasspath明确因guava-parent-33.3.1-android.pom校验失败，main-010成功不能替代该门。二进制strict/35坐标锁、签名和本次新hash均不能覆盖POM对依赖/约束/插件解析的影响。本报告不认定已发生篡改，但不能准入可信构建或自动放行安装。

tester独立遍历候选标准本地Maven库及其父POM/import BOM闭包：326份POM、131条父/BOM边，0个未解析属性表达式。与原root及候选verification XML批准hash比较，静态闭包只发现以下1项准确缺口；这不是最终构建实际消费描述文件的完备审计，现有receipt未记录完整cache/descriptor消费闭包，其他未经过此闭包的构建插件解析仍待证明。

| 对象 | 当前证据 | 判定 |
|---|---|---|
| com.google.guava:guava-parent:33.3.1-android，guava-parent-33.3.1-android.pom | 20632 B；SHA `6e11986ea7250b51f847157e2dc937f32a306804dfce0007a5e81ddb9b95c579`；历史pin不存在 | OPEN，仅观察hash，不新批批准 |
| org.gradle.toolchains:foojay-resolver:1.0.0 的.module | 未恢复、候选固定JBR路径未用；历史预期SHA `6190cf0e42e664c11e1ac0a785699ab02b549cea34392c679f36d8a2c550fcb9` | NOT_USED_NOT_RESTORED，不能填作当前已取得hash |
| org.gradle.toolchains.foojay-resolver-convention:org.gradle.toolchains.foojay-resolver-convention.gradle.plugin:1.0.0 的.pom | 未恢复、候选路径未用；历史预期SHA `f133249a18754ae6a1d2701d00d849b1afba7b0683ddb5fc1b18a70071cec2fa` | NOT_USED_NOT_RESTORED，无需为本批引入该插件 |

Guava parent本地准确位置、引用边和全部闭包在metadata-parent-bom-closure-audit.json；原缓存为 `C:/Users/benny/.gradle/caches/modules-2/files-2.1/com.google.guava/guava-parent/33.3.1-android/d4598d14da6c708054bc42f2be7e6245ac715be4/guava-parent-33.3.1-android.pom`，冻结副本在coder evidence/observed-build-metadata。父来源应补官方Maven坐标及取证/校验链；本次未联网取证。可复用原root verification XML、175份准确旧pin恢复回执、offline-repository-004、13项SBOM merge和main-008失败原文。不能把缓存SHA1目录名或新算SHA256当历史批准。

最小修复：只为缺失父描述补独立来源证据，由负责人记录本批新增准入；收齐实际消费的父/BOM/.module/plugin描述闭包和准确字节，恢复verify-metadata=true，在原35坐标/二进制/锁不变条件下由coder进行一次必要的离线严格验证/构建并整包重新冻结。若同类缺口追加出现须一并列齐，不能再整体关闭metadata验证。本轮tester没有执行此构建或批准未知来源，不要求无关功能重写。

### RENDER01-R02 / P2 / REPRODUCED

实际生产renderer在lockCanvas晚返后若已取消，会跳过64行的drawBitmap分支，但72行清理unlockCanvasAndPost后无条件return true。WorkSession123–124行因此drawn++并生成frame receipt，即使没有位图绘制。

独立复现：有界Surface替身让原lockCanvas等待；tester在确认已进入后调用真实session.cancel，确认source/owner尚未归还；只放开同一个等待，原coordinator/source/threads随后正常归还。实测 `WorkSession drawn=1 / Canvas bitmapDraws=0 / cleanup posts=1 / originalsReturned=true`。未在Android制造卡死/崩溃，此结果证明原Java分支计数错误，不能声称Android真实图像已测。

影响：取消/Surface/代次竞态的呈现计数与帧回执可能把仅为资源归还的post算作画面提交。未发现此次复现资源泄漏，也不声称旧像素被显示。

最小修复：保留准确原Canvas的unlock/return；分别记录本次是否确实执行drawBitmap、是否完成post、post后代次状态，按真实draw结果返回和计数，不能因当前gate已变便抹掉实际发生的旧提交，也不能将空清理post算帧。加入本复现回归。证据：independent-faults.stdout、checks及独立编译来源pins。

### RENDER01-R03 / P2 / CONFIRMED_TEST_ENTRY_GAP

设备计划RA-SOUND要求从未启动状态明确点击Listen。实际App无launcher且PresentationActivity exported=false；当前四个冻结方法都会在启动Activity后立即调用startProbe（RenderDeviceTests31行），没有保留闲置等待操作者的准确入口。RA-01/02还要求全程默认静音。故现有方案不能直接完成文档所述“闲置→完整3秒听音”流程，临时点已运行的静音测试不能充当同一前置。

这不等于断言Activity在系统中永远无法启动；这是冻结交付缺少可准确派发的同包人工setup路线。最小修复：补一个有界、保持默认静音、只启动闲置技术Activity的同包人工入口，或提交实际可行且经批准的同UID启动途径及证据；不把Activity随意exported或添加后台自动发声。四个自动方法保持准确选择和原静音语义，人工入口单列授权/观察/原归还；无人观察则NOT_RUN。

## 4. 四个必须保留的边界裁定

| 边界 | 本次裁定 |
|---|---|
| 新com.videokit.d1present、:presentation、空数据身份 | 仅有限可行性候选；独立UID不替旧App升级/恢复，不碰旧registry/once/UNKNOWN；不能绕过手机禁用、平板占用或替代原T07。新身份/fixture仍需具体派发，不是重复索取一般设备授权 |
| C14 CPU JNI与E13F差异 | 源/字节复用准确，Java回调来源匹配；不等旧E6诊断JNI，不代旧E13F输出链。所有unsafe入口不调用，实际JNI效果仍未验 |
| 父POM与verify-metadata=false | 当前可信构建准入BLOCKED；签名/锁/strict二进制仅局部PASS，不能自动豁免R01 |
| PCM/raw与播放器/权限/发行 | 本地生成PCM不证明压缩音轨或AV同步；snapshot不证明连续NAS/任意Seek；同UID非权限沙箱，J11全危险链BLOCKED；FFmpeg/LGPL外发及模型等许可仍NOT_GRANTED/未关闭 |

成熟平台Canvas/AudioTrack被薄适配，Media3依赖存在不代表已集成完整ExoPlayer/Transformer；技术决定保留持续源、完整Sink、AAR/独立Kit及公共API差距合理。既往E11局部MP4/AVI/能力/指定取消有限真机PASS保留，C13历史FAIL及其他NOT_RUN/UNKNOWN不回填。不将本次局部离线FAIL扩大成对全部既有功能的否定。

## 5. 修复后未来四入口与证据方案

本节为后续整批派发建议，**不是本轮执行授权或可直接消费的旧scope**。先集中修复/重新冻结并复核R01–R03；负责人审定准确新包身份、fixture准备、完整新操作/文本/归档预算及有限观察计划。再按新鲜设备/无其他项目占用、准确APK与签名/UID/data、无未知原owner门执行；占用时停止，不查询/停止其他项目。绝不继承ENV/RESUME已停止许可或旧余额。

准确component：`com.videokit.d1present.test/com.videokit.d1present.RenderInstrumentation`；测试类：`com.videokit.d1present.RenderDeviceTests`。每次独立准确方法/新进程，class参数为“类名#方法”，renderCase为同一方法，renderScopeSha256必须是届时实际批准范围摘要；语法hash不是权限。不能整class连续跑以重置预算。

| ID / 方法 | 该次应取的证据与停止条件 |
|---|---|
| RA-01 / generatedMutedDualConsumers | 默认静音，准确六次实际绘制/post及576000 B提交/排空；各FrameReceipt、两consumer的同原registry快照、首关闭sourceReleased=false；同次最多一张批准截图核90°/颜色/PTS，不能把生成图当解码 |
| RA-02 / existingMp4RawMutedDualConsumers | 仅新包私有basic.mp4，349102 B、SHA720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9；准备不得读写旧App数据。最多六个原C14 CPU，前个STOP/death/source归还才下个；保存producer/PTS及呈现回执。生成PCM不是MP4音轨；同次一张批准截图 |
| RA-03 / cancelRejectsLateGeneration | 预暂停，先确认实际raw在途、无setup失败、source未释放，再取消；旧代拒绝，准确原线程/FD/callback归还。此入口是在平台调用前的队列取消，不能代替真实Canvas/write在途故障；后者仍NOT_RUN，本机受控race归入R02回归 |
| RA-04 / pausedSeekAndSurfaceRecreation | 预暂停、真实TextureView移除/转交/新可用、seek后意图ACK=false；恢复至少1且≤6次真实新代绘制/post，原代未被重新当新代生效。保存新旧generation/原对象归还，同次一张批准截图核方向 |

每方法沿用6帧/30秒准入、raw queue2/在途1、PCM queue4/在途1、64MiB已知像素与3秒PCM，不以await30秒或JUnit退出代原归还；首错误/未知停止后继并强持有同原对象，不能kill、二close、清数据、强finish或换scope求绿。每个原instrumentation客户端及stderr/stdout/归档也须真实归还，操作次数/字节由正式派发准确限定，本报告不虚构可用SDK余额。

真实听音另经R03修正后的准确人工入口，只在明确Listen后发声；不改系统音量、不录音，逐项记录操作者/时间/声音/静音/暂停/取消。焦点失去只在合法可控条件下验证，不操作其他项目造失焦；无人听或无批准回环则NOT_RUN。四自动入口不能充当听音PASS。截图不是方向/音画同步全矩阵，Bitmap reservation不是RSS/平台峰值。

完成后对同一修复冻结候选集中出四方法/人工项/回归/首失败与真实归还报告。保留全部旧证据及UNKNOWN，继续D1未过/M0未启，不自动进入下一阶段。
