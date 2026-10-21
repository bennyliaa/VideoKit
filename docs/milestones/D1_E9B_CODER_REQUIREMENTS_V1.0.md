# D1 E9B coder requirements V1.0

2026-10-18。负责人依据docs/tester/D1_E9A_ARCHITECTURE_REVIEW_REPORT_V1.0.md正式集中派单。E9-F01/F03/F04 CLOSED_STATIC_LOCAL保持；E9-F02原登记资源P1仍OPEN，另本机端点总accept门P2。先集中实现/有限自检/完整冻结，再一次交tester。

P1：Registry.Store.checkTotal的原Files.walk E4Owned在调用前登记并长期由authority持有；allocate/迭代/read/close/Exception/Error/永久未返全部纳入returned/pcClosed。不能healthy=false但漏原walk并returned=true。HostManager/HostActivationSession（openKnownHead和recordActivationRelease之前）/approved-export从首个原registry IO前统一监督；初始化异常、无Remote、authorityCallActive释放都不能遗失Store或让main自行退出。unknown不二次close、不假完成。实际生产Store/walk与原custodian直接有限故障：close UNKNOWN、分配窗、iterate异常+close在途、activation/export前序失败，以及已真返正常失败安全退出，不写判定副本。

P2：本机总accept≤128，含已接受未处理；额度前置保留，耗尽停止accept并处理listener真实关闭/UNKNOWN，原Process/authority继续监督；不能129+继续accept后拒处理。并发/失败/close未知保守计额不重置，不换port扩额。真实128/129+和listener UNKNOWN切点，维持现有合作威胁边界。

新docs/coder/d1e9b，旧E9A733 immutable不改。保留已支持非等待/原Process/pipe/5秒/grant失效；只受影响自检/工具编译，不机械重跑19/32/native。若共享Android输入变，才一次必要集中APK；最终输入/差异/原日志/host JAR来源/同签名APK继承或构建/SBOM7native35依赖/四文档/ZIP外seal和只读verify齐全，完整一次主动报告。

无ADB/设备/真实媒体/迁移写/实际token/catalog/activation。PREPARE无authority，原107218/档案/预算/fence/oldCloseACKfalse及独立Kit/Flutter/框架/许可P0保持。D1未过，M0未启，长期准入OPEN。未授权子代理。
