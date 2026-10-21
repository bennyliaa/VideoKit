# D1 E12 需求与门禁独立审查报告 V1.0

日期：2026-10-18。身份：VideoKit tester。依据：`docs/milestones/D1_E12_TESTER_REQUIREMENTS_V1.0.md`。

## 结论

**E12文件完整性及需求追溯审查通过；E13提案方向可采纳，但正式执行需求须先补齐F01–F04。** 这些是下一批提案的可执行性缺口，不是本批运行测试失败，也不撤销E11已接受结果。D1仍为NOT_PASSED，M0仍为NOT_STARTED。本报告不构成E13实现、构建或设备测试派单。

本批仅读取本地文件并执行tester自编字节/映射核验；未操作设备、未读媒体payload、未构建、未执行或导入候选自检/旧测试、未修改冻结交付或产品。设备账本只引用接受报告时点：214483B、7R/7S、reserved=0、旧107218B前缀保留；没有宣称本批在线复核这些状态。

## 文件与追溯核验

独立脚本：`docs/tester/D1_E12_EVIDENCE/audit_e12.py`；结果：同目录`independent-audit.json`，**806项检查全部通过**。检查项包含逐文件哈希和逐行定位，不能解释为806个功能测试。

| 对象 | 独立结果 |
|---|---|
| E12外置seal | SHA256 `6cfaa9291b10bbc5a0f4410ef7d35b2cc59672368998a64d699e6dfe21bd9640` 一致 |
| ZIP | SHA256 `678f9029dc34435d60f68ae0ee708f0c02474a88986852acf2de4c4f8c2395ca`；45个成员，集合/字节/哈希一致，无重名 |
| 不可变清单 | 46条一致；45成员加ZIP，不要求seal自含哈希 |
| 输入 | 31份原文件pins及31份reference副本一致 |
| E11历史封印 | 两份seal及375/65条不可变记录逐字节核验通过 |
| 原需求§26–31 | 99条原文、行号、唯一ID及矩阵存在性一致：58+11+12+8+10 |
| 独立表 | 13项P0、J01–J11、§28里程碑/API冻结并行前提、§30十份设计文件名均已映射 |

99条计数不含§28里程碑表与§30设计文件清单，这两部分另查。审阅同时保留§27正式发布禁止条件、§29决策需备选/风险/许可/测试方案、§30大规模编码前设计评审和§31整体成功条件；文件存在不等于设计已批准或功能已完成。脚本最初对§30名称保留`docs/`前缀而矩阵使用文件名，造成一项核验器匹配失败；改为按文件名匹配后通过，未修改候选。

## 需求、阶段与历史裁定

1. 13项P0未删减。完整播放/图片/混排、编辑与跟踪、HostAction/快照、独立AAR/Browser集成仍在；E11六帧输出不替代这些产品验收。D1应完成关键后端、输入/Sink/释放与合法路线的可行性和设计决定；M0–M7承担完整公共契约、UI和产品实现，不应把所有后续产品工作提前作为本批D1运行项。
2. E6B-OBS-F01仅接受`CLOSED_LIMITED_E11_CROSS_HOST`：HA1Q6WXR/API31、准确14→15部署和四个独立host，两个normal各6帧及能力/指定取消。E11报告SHA256 `60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635`已独立核验。其他设备、重启、长期、未触发UNKNOWN仍OPEN，旧失败记录不回写。
3. C13 self系统signal=0严格FAIL、外部raw11与另一方法OS11、C14两项NOT_RUN均保留各自范围；不能互相覆盖。旧N2 fence/oldCloseACK=false及历史UNKNOWN不因正常方法通过而改写。
4. J03–J05当前codec在`:e4_codec`独立地址空间，但与宿主同UID，非权限隔离；J06宿主仍有lease/file/fsync JNI。ByteBuffer正常编码不证明Image/Plane分支；J07仅限定视频输出验证。J08字幕、J09当前图片能力、J10跟踪/GL、J11真实Surface/AudioTrack/Flutter链均未被E11关闭。
5. 实际集成为Media3 muxer、平台MediaCodec及有限isolated FFmpeg取帧/验证；不能称已接入成熟ExoPlayer/Transformer完整播放器/编辑器或Coil/OpenCV/ONNX产品链。模型/权重/样本与许可缺口继续OPEN/BLOCKED；本批未联网作新版本或法律判断。

## 正式派单前集中修订项

### F01 / P1：把升级源绑定到已接受v15，不能直接复用14→15入口

依据：`docs/coder/d1e11/src/com/videokit/spike/e4/E9DeploymentGate.java:32`起，`deployActivationDetached`仍以`registry.trust.plan`中的旧PREPARE pair构造expected source；R1工具`revision-r1/tools/E9HostActivationSession.java`同样如此。E11已完成v14 PREPARE→v15 ACTIVATION，新提案只写“审过的pair升级各一次”，没有给出v15→新候选的具体接线。

正式需求应绑定E11已接受的v15 ACTIVATION app/test pair、signer、UID、原数据基线，要求对现有部署门作最小且可审的适配，并锁定新版本及本批一次性派发记录。不能改写原registry/prepare历史、重用已消费E11 once记录、降级/重装14或绕过源身份校验。不得借此新增authority/迁移框架。这是下一批升级适配需求，不是E11原14→15部署缺陷。

### F02 / P1：把直接source原owner接入真实runner结束门

依据：`android/com/videokit/spike/e4/E11ActivationLifetime.java:4`只检查既有E9/E4/E5 owner，未直接统计新建的独立AsyncReadBridge/LeaseRegistry；实际runner的finish/onException仅调用该门。`upstream-c14/src/com/videokit/spike/c14/AsyncReadBridge.java:19`起使用daemon executor，Runtime.close会shutdownNow。`upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java:83`起已有特定构造失败的AbandonedSource保管，但不能自动覆盖所有新直接source方法。

正式需求应指明复用哪一现有owner，在open前登记并持续持有同一Runtime、generation、bridge、原句柄、回调和在途操作，将未归还状态接入真实finish/onException及既有PC监督结束门。取消响应或JUnit返回不能代替原操作/close归还；只有实际归还后才能关闭runtime/释放permit。

即使计划只注入可返回错误，也须定义意外UNKNOWN的保管出口：停止后继，保留原host/原对象与受管观察，不到30秒强杀/finish，不换对象或补close伪造归还。若现有机制不能承接，则相关Android错误路径BLOCKED并集中反馈，不启动永久挂起实验，也不建设新的控制框架。

### F03 / P1：旧代拒绝须有同生产门的有效正对照

依据：`android/com/videokit/spike/e4/E4CodecService.java:97`起，verify只查UID/instance；exact查实际session/task/epoch/PID。没有当前session时，新旧身份都可能被`E4_ORIGINAL_HOST_OR_OLD_GENERATION`拒绝；HELLO不经过同一session/source准入。BEGIN又要求真实Sink/lease/callback，与本提案零编码/零新R/S边界需明确协调。

正式需求须指定所测生产source身份门和调用路线：当前授权代在同一门真正open/read成功，旧task/epoch/instance在open前被拒绝且计数为0。不能拿“无session时都拒绝”证明旧代判别；若只能覆盖无任务/instance拒绝，就限定结论并保留其余缺口。不得为制造正对照擅自新增编码输出。普通UID负例仍须真实独立普通UID/不同签名，实际bind拒绝与同UID旧代分栏；未取得Binder时不声称触达内部onTransact。

### F04 / P2：将总上限分解到实际方法、对象和部署步骤

建议4096B非媒体源、64KiB累计read、8次open、16次close、每入口30秒观察、48次PC操作、累计2MiB文本可作为待核预算，现阶段没有逐方法/部署/收尾分配，不能据此断言一定足够或自行扩大。

正式需求至少补齐：

- 引用并锁定AsyncReadBridge、LeaseRegistry等实际实现。AsyncReadBridge每原ticket只允许初始close加至多两次明确失败后的重试，不能用总16次替代每对象限制；pending close不能重叠重试。其他owner继续遵守自身一次close等原约束。
- SourceReleased明确采用实际聚合条件`retired && consumers==0 && operations==0 && !closeFailed`。同源双consumer须保持共享聚合；先结束一个不能把整代retire而使另一个不可读，最后才退役并核原回调/close归还。
- 列每方法open/read/close、原操作deadline及取消/原返回时间；30秒仅为观察窗，不能覆盖原5000ms等接口语义或成为UNKNOWN强制收尾条件。
- 将pair升级、fixture安装/身份、六次启动、必要日志/进程观察与收尾计入48次实际操作表；减少重复采集或由负责人修改预算，不能实施中自行补次数。区分单操作原文本上限与全批2MiB累计上限，不以累计值放宽原单操作限制。

F01–F04可集中写入下一份正式coder/tester需求，不要求重开或修改已冻结E12包；新实现后整包交tester复审。

## renderer/audio/source与Kit设计提交时机

**接受E12“与下一完整批次同包提交具体设计差距”的方向，要求在D1内作出可行性决定，不推迟到M7，也不将完整M阶段UI作为E13交付。** 同包至少说明压缩源→demux/decode→raw frame→renderer/Surface代次与detach归还，合法PCM来源→audio owner/焦点/唯一声音，以及所有source consumer归还后HostAction才可用。

显示/声音真实运行未执行继续NOT_RUN，合法PCM路线缺证继续BLOCKED。优先明确可复用Media3/平台薄适配及残余宿主JNI/权限；不得扩FFmpeg音频、新模型或新后端冒充解决。Kit在D1先明确Browser业务/凭据隔离、硬编码宿主包和服务命名/Manifest冲突、native与依赖可提取性；M0冻结API/Fake契约，M7提供版本化AAR独立构建、两个宿主及可移除/升级回退证据。当前`:app`不是独立可分发AAR。

## 交接与停止状态

本报告和独立核验产物交负责人集中修订下一批正式需求。当前没有新运行测试、媒体产物、账本变更或设备pending产生；原接受基线和历史资源裁定不动。报告后停止，不自动实施E13或进入M0。通知结果另存`docs/tester/D1_E12_EVIDENCE/notification-receipt.json`，报告发送后保持字节不变。
