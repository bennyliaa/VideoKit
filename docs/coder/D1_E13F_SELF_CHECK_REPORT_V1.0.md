# D1 E13F 有限自检报告 V1.0

2026-10-18；仅本批P1直接回归与必要构建，不机械重复旧套件。所有命令/真实stdout/stderr/自然exit见evidence。

| 最终证据 | 结果与范围 |
| --- | --- |
| host-007 | compile exit0；BLOCKED/THROWS两独立JVM直接调用生产request及fail：sink不持FinishOwner实例/class或Stages锁，sink未返时调用者和唯一完成worker均可返回；异常不丢首结果/失败；ring有界 |
| public-008 | CASE/DEPLOY/LEGACY各NORMAL、FAIL_MARKER共6组exit0。真实公开claim→100ms短超时isolation→主调用栈退出→同原child自然返；原writer尾通知有限扣住时resourcesReturned=false、pcClosed无、claim marker无；释放并join同原线程后准确唯一marker，另一scope从同公开入口准入；失败持久化保同guard/原PC/责任线程且下scope在PC创建前拒绝。无手工true，原超时不改PASS |
| join-orders-009 | 真supervisor零child，follow在close之前、实际终止后、并发三序列，唯一marker/重复follow拒绝/下一scope准入 |
| build main-001 | 一次离线Gradle集中构建三APK exit0，无成功后重复构建；最后host-only线程屏障不在APK源码中，无需重建APK |
| apk-delivery-final | 官方签名/清单/ZIP对齐、DEX线索、准确142输入、版本19/3、35坐标、7 native逐字节不变；静态对齐不冒16KiB实机验证 |
| final class provenance | 183生产class全部从实际host-007输出装入JAR且保留逐字节比较。public-008 / join-orders-009使用该目录，只隔离明确本地shadow；检查类不混入JAR/APK |

保留开发失败：public-002本地record路径反斜杠语法被生产parser拒绝；public-003 case/newdeploy四组通过、legacy因本地dummy文件缺失失败，public-004补本地文件后legacy两组通过。host-006编译将依赖shadow runtime的public harness误纳入生产编译而失败，未运行该轮测试；host-007只编译生产及直接FCompletionCheck，public harness分别在影子classpath编译。host-001旧版日志测试成功，其原harness快照单列；随后为harness补finally释放latch，最终host-007重测。所有旧失败证据保留，不涂成PASS；最终生产代码包括starter/reader线程实返屏障，最终public-008已全部重测。

本地每子进程有有限fixture释放，不通过kill补exit；失败marker生产keeper的无限保管分支仅在有限本地daemon测试中观察，不声称其生产线程已终止。未再测长55秒，未重跑历史Android JVM适配/全套模块/媒体。旧E13E测试仅历史来源，不能用作新Android动态验证。

D1 NOT_PASSED / M0 NOT_STARTED；原实际卡点 NOT_UNIQUELY_DETERMINED。原v17主任务仅最后观测PENDING/UNKNOWN，本轮未查询；丢失诊断独立LOST_DIAGNOSTIC_OWNER_UNKNOWN。候选app19/fixture3未安装，真实Android/Binder/UID/Looper/monitor、kernel行为和T07均NOT_RUN。源码处置pin ABSENT，scope/release/once/sourceReview均未签发；旧资格/预算不继承。用户持续测试授权已具备，当前无设备操作源于原任务未决。
