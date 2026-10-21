# D1 E13 完整冻结包独立架构审查 V1.0

日期：2026-10-18。tester依据：`docs/milestones/D1_E13_TESTER_REQUIREMENTS_V1.0.md`。候选：D1-20261018-E13，v16 / ACTIVATION / ABI1。

## 结论

**文件完整性通过；当前候选设备准入BLOCKED，须集中修复E13-F01/P1后整包复审。** 普通第三方UID负例在预期的绑定拒绝路径跳过原ServiceConnection解绑，却回报resourcesReturned=true，因而不能证明所有原资源已归还。另记E13-F02/P2：打包脚本没有只读verify参数模式，不应作为核验入口。

E12 F01的精确v15升级源、F02直接source持续owner/runner/PC结束门、F03同生产身份门正反对照、F04预算分配均已有可定位实现；接受其相应静态改进，不据此宣布Android测试通过。六方法Android运行全部NOT_RUN，未签发/执行真实新scope、release或once。D1 NOT_PASSED，M0 NOT_STARTED。普通项目真机长期授权有效；本次阻断来自具体候选缺陷，非重新向用户索权。

本批仅本地只读审查和tester独立字节/SDK元数据检查：无ADB、无设备/媒体payload操作、无构建、无候选代码/打包脚本执行、无候选自检或旧套件重跑。未改产品和冻结文件。接受账本214483B、7R/7S、reserved=0及旧107218B前缀均只引用E11接受报告时点，不宣称重新在线确认。

## 独立核验与唯一制品

tester证据：`docs/tester/D1_E13_REVIEW_EVIDENCE/`，包含自编`audit_e13.py`、`independent-audit.json`、独立SDK签名/Manifest输出、`three-metadata-field-plan.json`。**2247项字节、定位与记录一致性检查通过**；这不是2247个功能用例。

| 对象 | 结果 |
|---|---|
| 外seal | `3b80d430aa7f859174ffae0a4b5ca948a01aa032d15c0666fb595e6a1bba5cc0` 一致 |
| ZIP | `dbaa6f510b54ad17e020b81be0d4e26ff378c7f4de1d40da4dea2f5230af98bb`，366个唯一成员；367条封印记录逐条一致 |
| 原冻结 | E11基础375条、R1 65条、E12 46条及三seal均一致；未浮动引用 |
| 最终构建输入 | 138项及快照SHA `6eeea5bd2a5faf97cea6f7905f01ebf4f1c91a22707cd1a5d61dd1f93bccbd95` 一致 |
| 源码/本机记录 | final-003输入、源码派生baseline、真实registry自检输入/副本/接受来源一致；未重新执行这些检查 |
| host JAR | 170个production class的实际成员/字节/源码pins一致，无E13ProductionCheck/E13SourceCases检查类 |
| 依赖与native | 主锁字节与E11一致，35坐标；最终app内7个.so与继承native pins一致；没有新增native构建证据 |
| fixture | runtime锁空、实际292个DEX定义与清单一致、无Kotlin定义；其中包含Android工具链API/tool生成类，不能称只有手写代码或无任何第三方字节 |

唯一可讨论的制品均在`docs/coder/d1e13/artifacts/D1-20261018-E13/delivery/`。历史root、final目录不用于派发。

| 文件 | 字节 | SHA256 |
|---|---:|---|
| app-debug.apk | 11043409 | `6ae468ccd81fce542202af9dd9567c95722505eb795a098557da4c042a716b71` |
| app-debug-androidTest.apk | 2858614 | `fee6f07f423e6f080eb36adca14d8f1ee3b88a2bbcaed4916216c2e1a2489b13` |
| fixture-debug.apk | 2463895 | `79929c4f8c0f69f10e8b9eb2c4a10b737759195b0a8a9ae2afe16ee2c0b44640` |
| e13-host-tools.jar | 295475 | `9c57d32e61917671257fbc582eb7c7eed70ad794a7efebedb7248c0b6d7bc397` |

独立调用SDK apksigner验证三APK成功：app/test原signer为`5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，fixture为不同的`45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9`。独立Manifest检查确认v16、ACTIVATION、app对fixture的queries、codec非exported；APK签名验证不代替现场UID证据。16KiB静态对齐不能代替设备运行兼容验收。

核验器最初按十进制匹配versionCode，而本机aapt输出`(type 0x10)0x10`；修正tester解析后通过，未改候选。审核期间未使用候选工具生成核验结果。

## E12 F01–F04实现与证据边界

### 精确v15 ACTIVATION→16

`src/com/videokit/spike/e4/E9DeploymentGate.java:22`起的acceptedE11Source/deployE13Detached绑定接受报告SHA、v15精确pair、ACTIVATION、原signer/UID与v16目标，复用原deploy检查和install-r顺序。`tools/E13HostActivationSession.java`绑定scope/release/sourceReview、原head/catalog、独立固定名`e13-activation-deployment.once`及原registry外CREATE_NEW；`tools/E9HostDeployment.java`前后核数据inode6972/4741，fixture须实际未安装才安装一次。部分失败/未知消费本次派发，不重试、不改原registry。

静态实现接受。实际升级未执行；最终pair/fixture、独立新scope/config/release和once绝对路径仍须负责人正式设备派单绑定，不能拿synthetic自检记录作许可。已有E11 once不可改名重放。

### 原source持续owner与真实结束门

`src/com/videokit/spike/e4/E13SourceGroup.java`在runtime/bridge/open前进入强OWNERS，持真实Runtime、LeaseRegistry/generation、Consumer/bridge/原CloseTicket和调用线程。首consumer关闭不retire共享generation，最后一个才retire。tryReturn需真实`retired && consumers==0 && operations==0 && !closeFailed`及原调用线程死亡；新增`AsyncReadBridge.Runtime.finishReturned`仅在排空后graceful shutdown，且两executor实际terminated才清keeper。没有用shutdownNow替代直接source归还。

实际`E13Instrumentation.finish/onException`同时检查E11原owner、source keeper和permission owner；`tools/E13HostCase.java`的OriginalAuthority在同scope/case原finish token、实际am自然返回和原pipe归还门之间保留PC custody。缺token或原资源未知，原custodian仍持有，不强杀结束。已知JUnit FAIL但原资源有实际结束证明可自然收尾，不能改写为PASS。

直接source静态接线接受；permission部分受E13-F01阻断。JVM受控可返回错误不是Android永久UNKNOWN或native卡住实测；没有关闭历史UNKNOWN门。

### 同生产source身份门与普通UID边界

`upstream-c14/src/com/videokit/spike/c14/SourceAdmission.java`抽出原CpuTaskClient UID/PID/task/epoch等值判断，实际broker调用该谓词并保留原错误及revoked检查。E13SourceGroup实际consumer/open/read使用同谓词并另核instance。旧代方法先当前代实际open/32B read成功，再旧task/epoch/instance分支拒绝且provider计数无增量，避免HELLO/无session全拒的空正对照。

CpuTaskClient改动是等值谓词提取，原native解码、normal编码与帧/EOF/PTS门未改；本审查不要求整类重跑E11 normal或历史signal套件。共同谓词调用不等于已做Android实际broker跨UID安全测试。

fixture有独立包、不同签名、现场需普通UID；SenderService先clearCallingIdentity再以自身身份bind固定非exported codec。授权host HELLO与实际kernel拒绝分栏，未取得Binder时不声称执行内部onTransact。这个测试意图正确，但原连接归还实现不满足准入条件，见下。

### 本机记录与预算

已读取final-003七组原记录：五个生产bridge/source场景，DEPLOYMENT 45断言和BOUNDARIES 22断言，退出均0；合计实际记录6open、4224B read、7close，迟到open/read时keeper门为false，实际返回后清零。来源为生产bridge/真实受控fixture及synthetic部署port；未把这些记录当Android Binder/UID/native实测，未重跑。

| 方法 | open | read payload | 原close调用 | Android |
|---|---:|---:|---:|---|
| ordinarySenderCannotBindCodec | 0 | 0 | 0（另有控制binding） | NOT_RUN / P1阻断 |
| authorizedHostSourceReadAndClose | 1 | 4096B | 1 | NOT_RUN |
| oldGenerationNeverOpensSource | 1 | 32B | 1 | NOT_RUN |
| twoConsumersHoldSourceUntilLastReturn | 2 | 48B | 2 | NOT_RUN |
| cancelLateOpenRetainsOriginalOwner | 1 | 0 | 1 | NOT_RUN |
| lateReadAndCloseFailureDoNotReleaseEarly | 1 | 48B | 2 | NOT_RUN |

4096B是每source host同一非媒体定义，五host累计20KiB准备量与4224B实际read分栏。原bridge await/fixture协调5000ms，30秒仅方法资格；每ticket最多initial+2次明确失败后重试，pending不重叠，7/16不是允许再补close。余量不授权重跑/追加方法。

PC分配算术成立：部署Java1+内部32+六Java6+六instrument6+独立metadata3=48；文本32768+524288+491520+393216+196608=1638400B，余458752B，合计2MiB。部署32/512KiB有实际wrapper门；现场controller还需累计计入top/child/metadata原文本，不按阶段清零。socket STATUS/OP/CLEANUP计划0；未知不产生免费查询或新次数。

## 集中缺陷

### E13-F01 / P1 / 阻断设备准入：预期绑定拒绝未解绑却报告归还

定位：`fixture/src/main/java/com/videokit/e13/sender/SenderService.java:21`至25。`bindService`返回false或抛SecurityException时，代码置returned=true；finally只有accepted=true才调用unbindService，因此预期负例两条路径均跳过原连接解绑，随后从originalConnections移除并返回resourcesReturned=true。

本地正式SDK契约证据：`D:/Android/SDK/sources/android-36.1/android/content/Context.java:4206`至4215明确要求无论返回值，以及SecurityException时，都调用unbindService释放connection。`android/app/ContextImpl.java:2273`起先注册ServiceDispatcher，再进入系统bind；`:2358`起unbind调用forgetServiceDispatcher。SDK文件哈希已保存；这是静态契约/源码问题，未冒称API31设备已实际复现。

影响：目标服务拒绝成功并不等于客户端dispatcher已归还；主端`E13PermissionProbe.run`信任该resourcesReturned，可能给出全owner finish证明。它直接违反本批“原target binding真实归还”和UNKNOWN不能伪返的要求。该缺陷不否定exported=false权限拒绝本身。

相关同类路径：`android/com/videokit/spike/e4/E13PermissionProbe.java:19`至22也只在accepted时解绑；bind返回false会移除keeper但不解绑，bind抛异常则bindReturned未设而永久保留，缺乏区分“原调用已异常返回”与“原调用未返”的准确记录。

修复要求：对已经进入bind的同一原ServiceConnection明确记录调用进入/实际返回或异常返回，并完成所需的原解绑；无论false/权限异常都不能由accepted决定跳过它。解绑调用进入/实际返回与异常应独立计账，未知保留同一owner，不用新connection/第二次bind或重复unbind代替。主端只在原连接真实归还后接受resourcesReturned。只需修既有owner与fixture路径，不新增控制或安全框架。

验证：补可审的true/false/SecurityException及unbind失败/未知路径证据，尤其证明预期拒绝路径对同一connection执行一次必要解绑；随后按新整包pins复审，通过后再正式派设备六方法。本批不为证明此问题启动负例。

### E13-F02 / P2 / 工具说明：package_delivery.py不是只读verify入口

`tools/package_delivery.py`没有参数分派，直接执行写证据/复制/打包流程，并以ZipFile(...,'x')创建JAR。负责人已说明误传verify后在既存JAR处FileExistsError退出；本审查没有再次运行它。误调用可在到达该错误前写前置派生文件，不能把它称为纯只读命令。

本次独立审计确认冻结367行/ZIP/JAR及旧seal字节均未变；不登记为候选功能FAIL。请在交付说明中明确packager只用于生成，不支持verify；核验应使用真正的仅读工具或tester审计，不为此重构产品或修改旧冻结。

## 三份独立现场metadata的具体内容与准入条件

固定字段清单已落盘`three-metadata-field-plan.json`，含34个固定stat路径、18份既有小型control/ledger字节pins、原最终raw来源SHA及新四产物已有stat；没有推造缺失inode。控制数据与媒体payload分开：非零媒体仅stat，不读取或重新hash内容。

| 客户端 | 固定必要字段 | 成功条件 |
|---|---|---|
| M1 部署前 | serial/model/API/ABI/user/解锁可用；既有controller占用证据；相关PID/PPID/UID/NAME及instrumentation/service；v15 pair路径/hash/UID、data身份；fixture不存在；固定stat/18控制pins、完整2271B ledger、pending不存在与固定控制目录清单 | HA1Q6WXR/TB138FC/API31/user0，空闲；精确E11接受基线，214483/7R7S/0reserved，无相关在途 |
| M2 部署后、首方法前 | 精确v16 pair路径/hash/UID与原data；fixture路径/hash/version1/实际独立普通UID；本地已审不同签名对应；相关进程/实际instrumentation/service与user | 本次新批准制品且原data未变，无在途；不以部署前信息替代部署后确认 |
| M3 六方法后 | M1同一固定stat/control/目录清单及完整ledger；pair/fixture/data；相关进程与实际instrumentation/service，并关联六份同scope finish、原七PC自然归还证据 | ledger全字节/hash及控制pins不变，无新输出/pending；原资源真实归还。缓存进程存在本身不等于服务/任务仍在途，也不能单靠进程消失证明资源已返 |

每份一次原有受管直接ADB shell客户端、≤65536B、原GENERAL响应≤55秒，总196608B；只在正式设备批次中执行。原PID、exit、双reader/pipe实际归还与scope留证。不得将三个客户端实现成另起三个Java wrapper再把wrapper排除在48外；不全量logcat、不读媒体、不以tail或静默截断当完整证据。既有controller占用不明或其他项目在用则等待，不抢占。

当前已锁字段/路径/预算，未编写或运行设备客户端；正式修复包通过后仍须将三份精确argv/脚本文本及逐记录上限锁入设备scope。若原接口无法在3份/64KiB/48内取得必要独立证据，应集中报BLOCKED由负责人改正式预算，不能执行中加次数。P1修复前不生成真实批准scope或once。

## 构建、来源与设计裁定

已核main-001原日志为工作区外Gradle wrapper缓存锁AccessDenied，配置/编译前停止；repair-001离线构建成功，repair-002排除fixture自动Kotlin runtime并锁空，repair-003补原keeper身份/scope与取消/实际返回时间。四次尝试均留痕；不将首次缓存失败说成源码编译失败或审批拒绝。原早期fixture依赖报告含stdlib/annotations，属于修正前历史，不能用它否定最终空锁，也不能沿用早期“无第三方”过度声明。

final-003源码及repair-003输入/最终制品一致。fixture签名私钥本地外置未归档；未来重建需相应签名环境或另交新候选，不能替换当前APK。7native/35Maven继承及工具生成类清单只是来源证据，仍非闭源发行许可、模型/权重/样本权利或专利准入。

renderer/audio/source与Kit设计接受为**SUPPORTED_DESIGN_ONLY**：采用现有raw RGBA与平台Canvas/Bitmap/Surface薄适配方向，列FrameLease/PTS/layout/rotation/Surface代次及真实detach；PCM到AudioTrack/focus/唯一audioEpoch与原write/stop/flush/release分工；所有source消费者真实退租后HostAction才可执行。合法压缩音轨→PCM仍BLOCKED，显示/听音均NOT_RUN；生成PCM只能验证PCM输出，不能冒充实际音轨支持。

Kit清单明确实验包/UID/device inode不进入通用API，服务namespace/Manifest与宿主残余JNI须在D1明确可提取性，M0冻结API/Fake契约，M7提供独立版本化AAR、双宿主与可移除/升级回退。当前:app不是AAR。上述方案应在D1内继续证明关键可行性，不推迟到M7，也不提前要求完整M阶段UI或扩FFmpeg音频/decoder/模型。

全部P0、Flutter/完整播放与编辑跟踪、历史C13系统signal0严格FAIL、外部raw11/另方法OS11、C14 NOT_RUN、ordinary UNKNOWN和旧N2 fence/oldCloseACK=false继续保持。E11限定四方法PASS及E6B有限跨host关闭不撤销、不外推。本批没有新输出/READY/R/S或设备pending产生；集中报告负责人后停止，等待修复完整冻结包，不自动开始测试。
