# D1 FACTS_V2_QUALIFICATION01 开发要求

2026-10-23；负责人正式派下一完整离线功能簇。PREAUTH01完整独立B已接受：报告 `309a56d23173a04327af4b80da5b21332f845436ea1f4cf10887bb44755e66cd`，manifest `fd3b676a69da58aa52d1c86ae3073e8b627bf5e3559f46242a976aeb0b230cbc`，184项/4096286B bad0、9组PASS、原资源全返。旧失败/辅助恢复/未证及原物化过期缺口保留，不因此签D1。

准确输入仍为PREAUTH01 source20 `02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df`、gate12 `bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192`；原plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。新目录 `docs/coder/d1android02-facts-v2-qualification01`，原20源/全部证据不修改。

## 功能簇

1. 实现facts V2回执到严格 `GLOBAL_IDLE_QUALIFICATION_V2` 的薄适配、只读候选导出及原target资格接收。明确新的authorizationKind/externalPreauthSha256/runtimeBindingSha256，不塞进V1 authority/approval字段冒旧语义；原V1闭字段/原行为兼容。最终字段表/Schema/调用图只有一套权威版本并纳入source/gate/plan pins。
2. 验证同一facts scope/plan/run/nonce/source的原raw字节/大小/hash、固定七query解析、V2 capture receipt、preauth/runtimeBinding、原outer-return证据的精确对应。不能由自写controllerReturned或空custody推导原资源归还；所有未知/原返回未证保留阻断，不补ACK/退款。
3. 默认仅导出明确标识 `REQUIRES_REVIEW / approved=false` 的候选，不能由systemFlag/OEM名/UID或HOME角色自动批准服务。签发资格须额外明确输入负责人外部已批准的review字节hash，review绑定这批原事实/外层返回/窄HOME及服务证据与准确目标source/scope/run/plan。无外批、错源/模式/跨scope/旧证据/未证服务均拒绝；不自生成review就当批准。
4. 新V2保留原全部仪器/竞争TOP优先、APP/PERS全记录/own字段、唯一HOME和窄服务匹配。采集到发资格/target global_idle的有效期最多300s，未来、过期、负数/浮点/布尔时钟与错目标拒绝，expiry不得延长事实新鲜期。全局拒绝或UNKNOWN不重arm；资格不是安装/媒体许可。
5. 实现一个明确标记的OFFLINE端到端：已返回V2 facts→合成独立review→V2资格→原target模拟入口；实际global_idle函数消费V2，V1回归保持。合成数据/外批/target全部fixture，不能声称真实资格或现场已测。

## 集中自测和交付

先固定新源/Schema/profile/全Python-PS-.NET图/写入根/预算，再一次集中自测：V2完整正例、闭字段删改/类型/重复、raw/receipt/binding/outer错配、未外批/未知原返回、HOME服务/仪器与目标/时间矩阵、V1原45和17条件正例、原capture/唯一返回不回退。复用成熟SELF/ENV02驱动，Windows raw与child环境分层、构造前检查、audit只观察，禁止旧worker输出路由错误。

动态整批360s/320s停新增、并发1/产品retry0；读取1GiB、产物16MiB、辅助≤96，原生产与facts90/30/15/10/SDK1和target字节门不扩。纯准备且无原资源/once进入的问题可保留版本后批内修正，不逐错回交；真正未知停新增。实际不适配先交整体静态估算，不事后扩额。

真实SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/新依赖/Git/index0，不读取test_media或查询旧对象。tester并行只读已冻结20源准备oracle并提交已通过PREAUTH快照；你只写新目录，不改其旧输入/三协调文档，按固定hash而非共享HEAD判断来源。

完整源码/Schema/映射/合成标记/自测与原返回/NOT_RUN/source-gate-plan-full manifest/唯一ZIP/独立回执一次主动交负责人；审核完整新包后才派tester整包B，不自动现场。D1未通过/M0未启，主里程碑、Flutter/独立Kit/成熟框架许可及全P0保持。
