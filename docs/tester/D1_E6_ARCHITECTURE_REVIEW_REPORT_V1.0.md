# D1 E6 输出验证整包独立静态复审报告 V1.0

2026-10-17；tester。依据 `docs/milestones/D1_E6_TESTER_REQUIREMENTS_V1.0.md`，审四文档、完整冻结源码、已有容器/Media3回放/有限检查记录、native构建、最终双APK和设备计划。

**结论：SUPPORTED_FOR_FORMAL_NORMAL_REGRESSION_WITH_P2_NOTES。新增P1阻断0项，新增3项P2诊断覆盖/并发问题。** 封装修复与严格验证门在静态和既有本机证据中获得支持，可另行正式派发准确正常回归；三个P2需集中修齐，不能宣称异常诊断链已全面验收。它们不构成本次已证明的六帧/EOF/内容/资源门放宽，不作为缺失证据或失败的豁免。

原 E5C-REG-F01/P1 **尚未以Android实测关闭**；本轮不安装、不ADB、不读原媒体或导出/回放件、不运行Java/C/Gradle/模型或桌面解码。D1 NOT_PASSED、M0 NOT_STARTED、全P0/JNI/历史signal FAIL/C14待测保持。

## 1. 冻结与最终产物

| 项目 | 独立核验 |
| --- | --- |
| 候选 | docs/coder/d1e6；D1-20261017-E6 |
| 外seal SHA256 | 362429a40889e84df49228c684feaec93faca036eeb26a5fd535147329d32265 |
| 源ZIP | 19494096B；c67a0ffbd7bddbb885575c071400df15a709d1eddc5586db0e81632eeecff801 |
| 清单 | 246源/254不可变，全部大小/SHA及ZIP精确成员/字节PASS，无媒体文件成员 |
| 最终build输入 | 3ac4722ad91be6e06572a1c30c31849753b5425cd36da208c4819627783523c9 |
| 最终构建 | repair-002，offline exit0，绑定最终输入 |
| app APK | 10701454B；931e4354be56779d6e039e752471934a339d1046bc13f5187a4cc9ec962453eb |
| test APK | 2757550B；5920174005cd6ee15d65d05f755b252d837a97d07a0ced84e2a76fa12d2b8036 |

两包既有签名日志及封存字节身份通过，证书均 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；没有重跑签名工具。原appId及两个非导出服务、原权限保持，版本6/D1-E6。原E5C一次性夹具入口未带入当前候选，不重跑已消费根。

main-001、repair-001、repair-002三轮均编译成功，但前两轮诊断发布静态审核不足：先补独立完整host字段以避开160字trace，再补仪器显式字段名单。原APK/输入/理由/日志保留，最终仅采用repair-002。独立确认最终app和test DEX均含validatorNativeDiagnostic字符串，结合源与构建绑定核其发布；不是实际Binder运行证明。

独立逐源比较确认 E5BGuard/E5N2Recovery/E5AFinalObservation/E5AAdmission/E5ALifecycle/E4OutputBudget 等相关核心与E5B字节一致，原callback/生命周期/每host观察/稳定预算不回退。E4Session仅增加诊断记录及安全cause提取等已审变更；后续实际资格仍需当前host运行取得。

## 2. 原失败的时间缺陷证据及生产修复

本轮只读取已封存export-analysis和回放记录，没有重新打开53651B导出件。该原文件身份沿先前导出报告：SHA `20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd`。

记录显示旧容器为5+1样本分段、90000Hz，首段5个duration均18750、尾段duration0，无tfdt/ctts。对照记录中的原FFmpeg MOV track_end回退，首段末间隔被重复：18750×5/90000秒使末样本PTS约1041667µs；原输入末PTS1000000，偏41667，超过原1000µs门。这与旧实机只有前5帧验证日志相容。**它证明可触发原严格拒绝的容器缺陷，不能回填旧设备未采集的具体native branch。** 本轮未独立重读容器或运行FFmpeg解码。

已有实际缓存Media3 1.9.3回放使用原六样本和生产E6Muxer，仅替代SparseArray/TextUtils基础API。旧200ms分段策略重现5+1和末41667偏差；新结果单段6样本durations为18750/18750/18750/18750/15000/18000，累加的六PTS为0/208333/416667/625000/833333/1000000，最大偏差0。tester对记录独立重算时间表，未运行回放或读取派生媒体。

[E6Muxer](/D:/CodexProjects/VideoKit/docs/coder/d1e6/android/com/videokit/spike/c14/E6Muxer.java:9) 以3000ms分段阈值覆盖合法≤2s输入窗和末200ms结束元数据；该值是容器分段设置，不是延长执行时限。finish要求track合法、count=6、last≤2000000，发送size0/flag4 EOS且PTS=last+200000，再关闭muxer。空EOS只提供最后时长，未增加第七帧。E4CodecSink仍严格6个非空≤256KiB样本、原单调/相对PTS/轨道及2MiB输出门，addTrack增加一次限制；源与编码输入PTS没有重写。

回放记录包含早期与最终锁定runtime两组派生文件SHA，均与原导出SHA不同，不能当原文件逐字节复现或Android解码成功。两次初始SDK Stub失败保留，补基础shim后才完成封装；本机没有实际桌面解码。

## 3. 严格native/Java验收门及诊断主链

native抽出的e6_verify.h仍要求256×144、accepted范围0…5后才索引timeline、PTS原窗及1000µs包含边界；超六帧、缺PTS、少帧、非完整demux/decoder EOF均拒绝。逐帧像素/PTS合格且原Java frame ACK返回后才增加accepted；原send/receive/EAGAIN/drain循环不为通过而放宽。原PipelineRules时间/内容/映射、thumbnail与完整输出验证保持。

新诊断为10个int+3个long：reason/site/stage/AVERROR、packets/decoded/accepted、demuxEOF/decoderEOF/drain、lastPTS、JNI readAt实际调用与返回压缩字节。reason1…9映射命名谓词，reason0/site>0映射冻结cpu.c精确site；原异常pending时不发送cleanup后的替代JNI回调，早期返回可NOT_COLLECTED，不能补零。

CpuTaskClient在原PID/UID/task/epoch/revoked鉴权和1024B上限后解析，检查字段范围、stage及verify accepted与实际frame列表一致、无尾数据；DONE保留原六帧/orientation并新增本次site0/accepted6/双EOF资格。ERROR将原精确诊断挂入CpuDiagnostics.Failure，经Future cause传到E6FailureCodes，最多8层，不读取suppressed cleanup替换首错。

成功Verification及明确native失败路径可进入E4Session专用validatorNativeDiagnostic，并由仪器HOST_DIAGNOSTICS显式发布完整字段；原trace只保短码。字段文本本身由固定数值与本地安全码生成，低于仪器单字段1400和总4096界。broker实际readAt请求/返回字节另记，不以缺日志为0。**主链获支持，但异常覆盖和原子发布仍有以下三个P2。**

## 4. E6-F01 / P2：native已成功，后续Java验证/cleanup失败时完整快照丢出主报告

位置：[E4CpuAdapter.validate](/D:/CodexProjects/VideoKit/docs/coder/d1e6/android/com/videokit/spike/c14/E4CpuAdapter.java:71)、[E4Session.catch](/D:/CodexProjects/VideoKit/docs/coder/d1e6/android/com/videokit/spike/e4/E4Session.java:163)。静态路径推导，未设备或模型复现。

verifier.awaitVerification已成功且nativeDiagnostic已实际收集后，若stopAndAwait/源关闭资格失败，或随后digestAfter、PipelineValidationReceipt.prove中的内容/thumbnail检查抛普通IOException，validate不会构造Verification，也不把已有snapshot挂入该异常。E4Session成功赋值未发生，catch又只能从CpuDiagnostics.Failure取snapshot，专用字段仍NOT_COLLECTED。此时不能准确解释为“native未采集”；logcat可能仍有实际快照，但交付承诺的主报告完整失败诊断没有贯通。

建议在validator边界分别保留native snapshot与原Java/cleanup首错，将已收集的E6_NATIVE_OK也作为背景证据传出；不能把native成功改成整体成功，不能用它覆盖实际内容/关闭失败。补生产Java后置验证失败及native成功但cleanup失败的定点证据；现有preserving工具检查不是这条实际整合路径的运行证明。

## 5. E6-F02 / P2：源帧native失败被归属为validator失败

位置：[E4Session.run/catch](/D:/CodexProjects/VideoKit/docs/coder/d1e6/android/com/videokit/spike/e4/E4Session.java:163)。同一外层try覆盖source.next及之后的output validate；catch不区分阶段，只要任一错误带nativeDiagnostic就赋给validatorNativeDiagnostic，并记录E6_VALIDATOR_REJECTED。

若源PIPELINE_FRAME native失败且带精确snapshot，此时输出validator尚未启动，仍会被报告为validator诊断，造成错误归属。安全短码被保留有益，但不能借此声称输出验证器已经运行。建议分开source/validator字段或附准确task/mode/phase，validator未启动时明确NOT_STARTED；补源native失败→不得填validator结果的生产边界证据。未设备/模型复现。

## 6. E6-F03 / P2：“一次snapshot”检查和发布非原子

位置：[CpuTaskClient NATIVE_DIAGNOSTIC](/D:/CodexProjects/VideoKit/docs/coder/d1e6/upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java:256)。nativeDiagnostic是volatile；Binder onTransact及该分支未串行化，先检查null、验证字段，随后直接nativeDiagnostic=d。

两个来自准确已鉴权worker的并发诊断调用可以都在赋值前看到null，并先后成功覆盖，不能保证承诺的“一次snapshot/拒绝重复”。volatile提供可见性但不使检查与发布原子化。正常冻结native当前单线程发送一次，因此本项不证明正常编码门被实际绕过；它是新诊断协议并发负例缺口，静态推导而非已运行攻击。

建议用原子一次发布或受控同步，保留第一份合格snapshot，后续调用明确拒绝，不能覆盖首诊断；补直接生产接收边界并发重复的有限负例。不要为修诊断改变原帧/EOF/身份或资源门。

## 7. 已有34检查与native来源边界

已有C17项直接执行生产同一header，覆盖六个合法帧、原末41667偏差、+1000/+1001边界、额外/少帧、尺寸、缺demuxEOF/decoderEOF；Java17项执行生产诊断/cause/cleanup helper及原内容/映射/时间表正负例。记录输入/exit/log身份核验通过，合计34不重复累加；不表示整个JNI/Binder/Java实际路径已执行，也没有覆盖第4—6节全部问题。旧270/82仅引用，未重跑。

仅项目libvideokit_cpu.so改变：18552B/SHA ed02feb238b26ea2ac53b6ae2eafca3d3131d74ebfdfd52c39ff3a925648e9a7 → 20104B/SHA2547b07d7d4b298e8b455c5f24d0d1fbcdf7068b016527edbf5f80f31d16191a。独立比较APK/upstream，另六库逐字节相同，不能宣称七库全未改。

包装库构建一次，NDK30.0.16248370/API31、FFmpeg8.0.3、原链接/编译参数及输入header/config SHA均有记录；source/diff/native-diagnostic-sites和NOTICE-E6对应，原完整C14源容器保留。35Maven坐标锁不变，Media3 1.9.3及codec/demux/禁网络白名单未扩；SBOM正确单列wrapper差异，不作安全或许可放行。

tester从最终ELF字节独立解析七库LOAD alignment≥16384，并核APK内未压缩库本地数据offset均16KiB对齐，与既有zipalign记录相容。只支持静态布局，不是Android16KiB实测。

## 8. 正常回归准入及后续

**明确准入：核心修复可支持另行正式派发同签名保数据部署和限定正常回归，三个P2不豁免任何实测门。** 建议负责人集中安排修齐这些诊断缺口；若先验证当前冻结包，必须保留本报告P2状态，遇实际缺证/错误归属/协议异常或产品失败按计划停止，不能将本包称为完整诊断需求已全部交付。本轮没有设备执行许可或动作。

device_plan.json绑定最终version6双APK、HA1Q6WXR/原UID，app/test各install-r保数据更新；当前53651累计消费和失败产物沿既有报告保留，本轮未新查设备状态。四方法准确顺序normalMP4→normalAVI→capability→条件cancel，batch D1-E4A-E6-NORMAL-TABLET-20261017，原稳定budget/结算SHA保持，每新host @Before实际最终观察，不复用旧host liveproof。无新QUERY/ABORT/独立OBSERVE/G01夹具重跑。

正常必须READY、真实6源/6输入/6样本、完整隔离6 accepted/EOF/PTS/原画面检查、完整专用诊断E6_NATIVE_OK/site0/双EOF/drain1以及原真实资源/owner/CONTROL/预算归还，无pending。产品60s/首次cancel30s及原12s协商/15s STARTED不扩；每输出2MiB/三次hash≤6MiB、累计4MiB与53651旧消费保持，额度或新pending阻断不能删产物/换账解决。

取消计划仍是占位符，必须替换为本次E6同设备两正常完整结果独立审证报告准确SHA；不能用旧报告、交付SHA或任意64字串。条件不成立就BLOCKED。任一FAIL/PENDING/UNKNOWN、诊断/EOF/画面/真实关闭不符停止依赖，保留现场，不临时改代码或弱化期望。

本次tester ADB/安装/媒体与导出件读取、Gradle/native构建/Java/C模型重跑均0；仅执行自有只读身份/已有记录审计。独立证据：[identity-and-recorded-static-audit.json](/D:/CodexProjects/VideoKit/docs/tester/D1_E6_EVIDENCE/identity-and-recorded-static-audit.json)。集中报告主动发负责人，后续任务另行准确安排。
