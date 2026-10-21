# D1 E4A 集中修复开发需求 V1.0

2026-10-17。依据 tester D1_E4_ARCHITECTURE_REVIEW_REPORT_V1.0.md，REQUEST_CHANGES。一次完成 E4-F01/P1、F02/P1、F03/P2，集中本机验证与必要构建，完整冻结后一次交审。不改 E4/C14 冻结；新候选 D1-20261017-E4A，独立目录 docs/coder/d1e4a，允许复用可追溯原源码。

## 实现要求

1. F01：分离 ABORT 撤权/持久终态与失败产物保留，保留原身份和实际长度/hash或明确UNKNOWN。实现正式批次跨方法及必要跨host的单调累计输出消费账本；删除文件、进程重建、新实例不能退款。明确预留与实际消费/未知保留规则，4MiB累计/2MiB单输出/128记录保持，预算不足拒绝而不扩大。元数据自身开销单列有界；初始化或持久化未知时保守拒绝，不能仅目录存量推导累计。旧C14只读；衍生适配保来源关系。
2. F02：在实际FD/guard分配前外部可达holder已登记，拆分allocate/register/initialize或等效显式交接。覆盖AndroidLease open/acquire失败+close失败，以及FencedTask persist/directory-sync失败+guard close未证。原对象/参数/异常与强引用留在原owner账本，UNKNOWN不重试、不释放许可、不依赖GC；空Sink/opening标志不是持有实际资源。
3. F03：统一取消收尾，仍按原调用实际返回扣controlInFlight；通过同原身份和原时限的query或唯一终态发布，观察CONTROL最后返回后真实归还。未知保持PENDING，不提前扣账，不延长既定时限或依靠重跑求稳定。

## 验证与交付

有界离线证据至少包括部分输出→失败→产物仍在→后续预算仍消费，跨holder/host恢复不退款、累计账持久化异常拒绝；初始化失败+close成功/未返回/异常的原owner可达；CONTROL返回前/后屏障和合法PENDING→已证归还。测试实际关键交接，不以镜像断言替代。使用自有小文件/假故障，不读取真实媒体、不启动Android/native fault。

先完成三项及相关计划调整，再集中JVM与一次Android本机offline构建，必要修复重建保留全部日志。无需重复历史检查；不ADB/设备/真实媒体/PF/依赖或模型下载。Media3 1.9.3、原FFmpeg闭包、正式Flutter/独立Kit边界及许可要求保持；新增依赖须说明必要性，默认不扩。

提交E4A交付/架构威胁边界/剩余门禁/设备附录四文档、完整源码ZIP/双APK/签名/精确SBOM差异/只读外freeze核验工具和证据，三缺陷逐条映射真实代码及有限结果。更新8项设备计划，三quarantine各独立最后，不能重建host洗未知许可；累计输出与源hash读取预算明确。全部Android仍NOT_RUN，D1未通过/M0未启动，原P0/JNI/历史FAIL保持。完整冻结无在途后主动报告负责人；不自行交tester/设备或提前小项交接。
