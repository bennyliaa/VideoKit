# D1 E13 coder正式需求 V1.0

日期：2026-10-18。来源：负责人VideoKit项目助理正式派发，吸收D1_E12_REQUIREMENT_GATE_REVIEW_REPORT_V1.0.md F01–F04。E12提案不是执行许可，本文件记录本次新实现范围。

1. 基于已接受v15 ACTIVATION精确app/test pair实施最小升版部署适配；新候选版本16、ACTIVATION、ABI1，同签名/UID/空闲与原数据身份门，独立新scope/once，不沿用v14 PREPARE来源或已消费once，不改原registry。只实现与计划，当前不生成实际批准scope/once、不设备。
2. 复用实际生产AsyncReadBridge/LeaseRegistry，在open前登记原runtime/generation/bridge/句柄/在途/回调到持续owner，纳入实际runner finish/onException和原PC监督结束门。30s只资格与观察，不强制结束；未知保原holder并停止后继，归还后才能关闭runtime/释放。
3. 集中实现六精确方法：ordinarySenderCannotBindCodec；authorizedHostSourceReadAndClose；oldGenerationNeverOpensSource；twoConsumersHoldSourceUntilLastReturn；cancelLateOpenRetainsOriginalOwner；lateReadAndCloseFailureDoNotReleaseEarly。真实普通第三方UID Debug fixture绑定拒绝+授权正对照；kernel拒绝与内部Binder校验分栏。旧代测试须同生产source门有效当前代真实open/read，再拒旧task/epoch/instance；HELLO或新旧都拒不算正对照。
4. 共享source聚合条件是retired && consumers==0 && operations==0 && !closeFailed；第一个consumer退不能retire整代。每原ticket初始close+最多2次明确失败后的重试，pending不重叠。只可控迟到/可返回错误，不主动注入永久UNKNOWN、OOM、重启、自杀信号，不kill/第二close/换UUID填PASS。
5. 实验非媒体source4096B，累计读≤64KiB/open≤8/close≤16；原接口更紧则用更紧门。每方法资格30s、全批PC48/文本2MiB细分到方法/部署/收尾，预算不足停，不临时扩大。区分fixture准备/实际payload；媒体输出/READY/新R/S=0，旧214483B/7R7S与107218B前缀及全部旧产物/fence保持。
6. renderer/audio/source原始帧/合法PCM来源、owner/代次/归还以及Kit无Browser硬依赖/可提取性提交具体设计决定；显示/声音未测NOT_RUN、PCM未准入BLOCKED。不扩FFmpeg音频/新decoder，不造新安全/取消/诊断框架，不提前实现完整UI/AAR或M0。
7. 完整实现与有意义本机自检后一次集中主app/test及必要普通UID fixture构建，必要repair留痕；未变native不编、不机械重跑旧套件。交docs/coder/d1e13源码、四文档、精确diff、自检输入日志、部署计划、签名APK/fixture来源、SBOM/7native35依赖与许可、ZIP/外seal/只读verify，一次完整主动报告。

当前无ADB/设备/真实媒体执行。后续真机长期授权已给，正式范围内无需再问；他项目占用等待不抢占。旧冻结全部不改，历史FAIL/UNKNOWN/P0保持，D1 NOT_PASSED / M0 NOT_STARTED。
