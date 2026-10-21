# D1 E10A coder requirements V1.0

2026-10-18，负责人依据D1_E10_EXECUTION_PACKAGE_REVIEW_REPORT_V1.0.md集中派发最小实现及执行包同步。先落需求，不修改E9B/E10冻结，不启用子代理。

P1 BOUND未EXEC：严格核同actor/plan/reserve/连续head，无任何EXEC意图或预留/在途执行，当前identity原资源真返，写入口永久停止；复用既有identify/reserve原字节，不覆盖原合格identify为取消后PENDING，不再CREATE_NEW冲突；归档当前取消原return，唯一精确ACK和独立normalfinish。该身份收尾不能final/actor2，不为收尾强行EXEC、不改历史记录。

P2 POSTARCHIVE STOP：在原host写intent/发送wire前按阶段拒不适用STOP，或经审终局原receipt稳定语义；原已归档COMMIT R0不能因STOP成为R1破坏唯一ACK。拒绝不应消耗唯一ACK或重放已发未知。无通用取消框架。

直接生产公开控制/registry/run/实际管理边界有限自检：BOUND未EXEC取消正常收尾且原identify/reserve hash不变；已有EXEC意图/错误actor/head拒；归档前后STOP/ACK seq/重复；FAILED真返可收尾但不可final；UNKNOWN不伪归还。仅受影响检查，不重跑19/32/24/native。证明PC-only且ABI/Android输入不变才可继承E9B APK，否则一次必要集中构建，记录真实host JAR/版本/签名/输入/SBOM并同步机器计划/scope/失败表；本BLOCKED报告不当执行准入。

新docs/coder/d1e10a，四文档、执行包、原输入日志、ZIP外seal/只读verify，一次完整主动报告负责人。0ADB/设备/媒体/真实UUID或scope签发/迁移写/token/catalog/activation。原107218、oldCloseACKfalse、所有P0/框架许可及D1未过/M0未启/长期准入OPEN保持。
