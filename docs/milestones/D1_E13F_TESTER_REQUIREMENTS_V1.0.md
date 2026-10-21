# D1 E13F 集中复审测试需求 V1.0

2026-10-18。待完整冻结交付后，依据 E13E 三项 P1 与 D1_E13F_CODER_REQUIREMENTS_V1.0.md 独立整包离线复审。

重点核实际公开入口同原 claim 超时后的自然归还续办、订阅竞态、唯一 marker 和磁盘失败保管；锁外日志及日志未返/异常不丢完成请求；实际原 archive writer 线程终止屏障，尾通知未返时禁止提前 pcClosed/claim 结算。不得用手工 originalReturned(true)、线程内布尔值或仅镜像 gate 证明完整组合链。原失败超时不能改 PASS，不自动续方法。

核最终生产 classes 与直接有限证据字节绑定、完整 APK/JAR 身份及签名/来源、必要构建理由、旧冻结不变和外 seal/ZIP。避免机械重跑长测试或重编候选。输出集中报告 docs/tester/D1_E13F_LIFECYCLE_REVIEW_REPORT_V1.0.md；未通过给准确位置、触发、证据及最小修复要求。

本轮无设备/ADB/原 handle 查询/STATUS/处置/部署/重测。原 case PENDING/UNKNOWN、诊断 LOST 分开保留，处置方案仍只可审，不冒执行授权或资源归还。D1未过/M0未启，P0、许可和历史FAIL不变。完成主动通知负责人。
