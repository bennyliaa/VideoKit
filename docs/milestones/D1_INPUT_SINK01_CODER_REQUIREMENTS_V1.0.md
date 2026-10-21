# D1_INPUT_SINK01 集中离线开发要求

2026-10-20；正式批次D1_INPUT_SINK01，属于原D1第3/4项可行性缺口，不启动M0。目标是实际宿主readAt→既定Media3 DataSource薄适配、授权临时OutputSink能力/事务与重新打开验证接线，不是新播放器/编辑器/资源框架或最终公共API冻结。旧RENDER02产品/capture/已停止设备scope和UNKNOWN保持原字节。

按项目已定Media31.9.3及原平台接口，复用已有AsyncReadBridge/LeaseRegistry/sourceVersion/epoch和成熟muxer，禁止自造codec/容器/网络/NAS/凭据层或扩FFmpeg音频。若所需Media3 DataSource模块尚不在当前缓存，允许仅同精确版本必要官方artifact/POM/传递依赖来源、许可和校验准入；不能偷偷升级/关闭metadata校验或先用同名假接口宣称接入。新依赖身份/许可与既有差异完整交独立review，无法合法取得则对应集成BLOCKED，但继续可独立完成的真实薄适配。

有限离线数据固定生成seed/hash；最大8MiB样本，逻辑偏移用稀疏/受控provider验证2GiB以上和溢出，不分配巨大文件；单块≤64KiB、每源读在途1/队列≤4、总同时源≤2、输出≤16MiB，不把这些候选预算冻结为产品阈值。超时仅停止新准入并保管原资源，原close/worker真实返回前不发布SourceReleased，不退款UNKNOWN。

在新目录集中完成：

1. 实现实际Media3 DataSource/Factory适配宿主只读随机readAt：DataSpec position/length、未知长度、短读、EOF、range/整数溢出、重复open/close、取消/断线、seek新代拒旧返回及TransferListener语义。opaque标识不能泄漏真实路径/URL/凭据；同步调用只在工作线程，UI禁止等待。原桥接口匹配源码，不复制为第二资源权威。
2. 临时OutputSink具体能力协商（顺序/随机/flush/close/reopen），后端不支持的能力在写前拒绝，不以缓存整文件/路径直写绕宿主Sink。复用既有FragmentedMp4Muxer/受审宿主输出桥，对实际可支持路径给可执行适配/本地验证，无法离线运行的平台路径保留编译证据及NOT_RUN。
3. 原写入完成、flush/close返回、隔离验证或受控重新打开、markReady与宿主COMMIT分层；abort幂等、取消/写失败/迟到/空间或权限失败的稳定错误映射和路径脱敏，不凭close完成冒格式验证/提交成功。不得修改真实历史账本、宿主文件或输出授权。
4. 实现有意义有限本机测试：真实适配器与实际Media3接口编译/可运行部分、短读/未知EOF/大offset/取消迟到/双consumer和首consumer关闭、顺序/随机不支持、partial write/flush-close失败/reopen失败/abort不回填成功。Fake仅宿主受控provider/Sink或明确平台端口，不模拟Media3接口冒框架集成。
5. 一次集中必要编译/构建核实际依赖/平台接口，严格锁和metadata；未改native/host/fixture复用。完整源码/依赖许可差异/候选产物hash/自测原日志、矩阵、M0接口可冻结与未决决定、独立测试入口和ZIP/seal一次交负责人。无SDK现场/ADB/5037/设备/旧handle查询，不造设备release或诊断平台；不为等待设备停止离线开发。全批完整后主动报告，不部分交测。


## 阶段A集中基线补充（2026-10-20）

负责人核报告db797e0a7714982b85dc474eabc70273c9ea49fc97c88fdf98a54ea0874379a1，旧冻结来源测试非新候选验收。A01：同Provider/generation两个consumer基线实测read峰2，per-consumer门不等新per-source1；必须真实共享源门/队列4/全局源2。A02：partial流写7后抛错而旧bytes/position32只为attempt/reservation；新Sink需actual已知前缀/UNKNOWN分栏、首错sticky，不自动重绕重发/READY/COMMIT，原flush-close-reopen/外层真实返回分别留证。复用阶段A的19项独立回归清单，但不冒全部已PASS。两项作为本批集中范围完成后一次自测冻结，非要求小项交测；原有限PASS/UNKNOWN不改。
