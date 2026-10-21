# D1 E6 完整交付 V1.0

2026-10-17。D1-20261017-E6 / versionCode6 / D1-E6。已复现E5C-REG-F01的容器时间错误，完成生产封装修复和精确验证诊断链、本机关键证据、native及双APK离线构建。Android正常回归NOT_RUN；不宣称原设备失败已转PASS。D1 NOT_PASSED、M0 NOT_STARTED、全P0/正式Flutter/独立Kit/框架许可与历史FAIL保持。

## 有据定位与修复

唯一获准导出件failed-output-53651.mp4（SHA20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd）容器有两段5+1样本，90000Hz首段时长18750×5，尾段duration0，无tfdt/ctts。首段最后间隔被重复，使第六样本按FFmpeg8.0.3既有MOV track_end回退时间推为1041667µs；真实源及编码输入末PTS1000000µs，偏差41667µs，明确超过原native1000µs门。前五帧日志与此一致。原当时未记录具体拒绝谓词，不能把本机推导改写成旧实机branch trace，也不能排除后续其他条件。

使用实际缓存Media3 1.9.3封装库与原六样本有界回放，旧200ms策略复现5+1及41667µs偏差。新生产E6Muxer把合法<=2s六样本放同一fragment（3000ms是分段阈值，不是延长执行时限），并给空EOS元数据lastPTS+200000；新段durations=[18750,18750,18750,18750,15000,18000]，六PTS全部准确、最大偏差0。空EOS不是第七帧。实际源/编码PTS不重写，encoder/mux完整六样本/EOF/PTS/画面门均保持。最多6×262144B复制样本，2MiB输出上限未变。

新增numeric-only native诊断：命名谓词/原源码site/阶段/AVERROR原值、视频packet send次数/解码与接受帧、末PTS、demux/decoder EOF、drain、实际readAt调用/返回压缩字节。固定13数值经原鉴权Binder一次传输，校验1024B、取值、stage/帧数一致后保留；ERROR保留原精确安全码。E6FailureCodes有界解开future causes，首错不被cleanup覆盖。专用validatorNativeDiagnostic报告字段和仪器输出名单保留全结构，不依赖160字trace行。缺失诊断明确NOT_COLLECTED；pending Java原异常不会被cleanup后的JNI诊断覆盖。

## 验证与最终产物

| 角色 | 字节 | SHA-256 |
|---|---:|---|
| app-debug | 10701454 | `931e4354be56779d6e039e752471934a339d1046bc13f5187a4cc9ec962453eb` |
| androidTest | 2757550 | `5920174005cd6ee15d65d05f755b252d837a97d07a0ced84e2a76fa12d2b8036` |

最终双APK在docs/coder/d1e6/artifacts/D1-20261017-E6/final，证书均 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；原两个私有服务/无新增权限与INTERNET/原AppID保持。签名与7native对应字节核验PASS。最终输入SHA `3ac4722ad91be6e06572a1c30c31849753b5425cd36da208c4819627783523c9`，最终repair-002成功绑定。

本机生产C同一e6_verify.h真实执行17项（合法6帧/末帧、原41667偏差、1000边界、真多/少帧、缺EOF等），生产Java诊断/异常与cleanup、原画面/映射/时间表17项，合计34 PASS；实际Media3回放另单列PASS。JVM回放只替代Android SparseArray与TextUtils基础容器/文本API，未替代Media3封装算法；不是Android解码通过。最初两个JVM harness因SDK Stub方法停止，补独立基础API shim后复现；未据此变更产品门。原历史270/82未重跑。

只重建独立项目libvideokit_cpu.so：18552B/ed02feb238b26ea2ac53b6ae2eafca3d3131d74ebfdfd52c39ff3a925648e9a7 → 20104B/2547b07d7d4b298e8b455c5f24d0d1fbcdf7068b016527edbf5f80f31d16191a。另六库逐字节不变。原NDK30.0.16248370/API31/FFmpeg8.0.3及有限codec/demux/禁网络配置不变。七库ELF LOAD>=16KiB，最终APK zipalign -P16静态PASS；不是Android16KiB实测。精确源码diff、源码/header/config身份、构建命令/日志、native/Maven差异和NOTICE-E6随包；35Maven坐标锁不变，无下载。完整原C14对应源容器保留。

集中main-001及必要repair-001/002均编译成功。两次repair仅完整诊断报告及仪器输出白名单贯通（最终静态核查发现旧trace160字截断及显式字段名单遗漏）；前两轮APK、审核/输入/理由/日志及build-results-before-*全部保留，最终只取final。native包装库只编译一次，无第三方重建。

## 范围与交接

原E5C144项和E5B1561项不可变来源只读校验PASS。Guard/恢复/Observation/Admission/Lifecycle/Budget字节不改；原N2已结算、53651消费及失败产物不动。只读获准导出件两次共107302B，原test_media/设备/ADB/QUERY/ABORT/媒体传输/native fault/下载均0。私有回放派生媒体不放源码ZIP；其hash/时间表/工具和限额有记录。

四文档、tools/device_plan.json、source-manifest与完整源码ZIP/双APK/外seal一次交负责人复审。下一正式批次仅同签名保数据部署→正常MP4→AVI→能力拒绝→条件cancel，每新host原实际观察，稳定budget不变、无新ABORT；真实动作尚未启动。
