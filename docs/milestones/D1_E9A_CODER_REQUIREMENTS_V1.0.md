# D1 E9A coder requirements V1.0

2026-10-18。负责人依据docs/tester/D1_E9_ARCHITECTURE_REVIEW_REPORT_V1.0.md正式集中派单：E9 NEEDS_FIX / NOT_SUPPORTED_FOR_DEVICE_MIGRATION，修2P1+2P2，整批完成再交tester。

F01：HostManager真正非等待启动，不能仅移除-w而仍依赖watcher sendStatus。落实实际custom runner可达、权限及身份绑定的独立有界status/control transport，启动client返回不当actor完成。

F02：统一管理真实ProcessBuilder、原Process、管道reader/等待/close以及主管理程序全部出口。reader异常/截断/控制台超界/超时/EOF但原Process活或UNKNOWN时，不能只throw或将对象存在daemon/即将退出的JVM局部列表。保持可识别handle、原对象强持有、持续管理与状态authority，停止依赖，原资源全部真实返回或明确受管隔离接管ACK之前不退出工具进程。不得cancel/kill冒close，不无限无标识等待。Deployment.Processes同样落实。有限本机故障切点直接覆盖实际生产ProcessBuilder/reader和程序结束边界，替身限平台，不复制判定。

F03：每个控制响应独立5秒绝对期限，不能共享通用55秒+1秒join或到时重置，迟到不改成功；原identity/commit各10秒、控制8/STATUS3不变。

F04：CurrentObservation每次调用先invalidateCurrent，包含used/ACTIVE等早拒路径；实际成功→重复失败→requireCurrent拒绝。准确处理并发、异常调用与旧grant边界。

新候选docs/coder/d1e9a，旧E9全部1045项冻结不改。先PC工具有限直接验证，针对变更补测，不机械重跑32全套或native。实际Android runner transport改变时一次集中prepare双APK构建；host-only修复不必重编APK；完整输入及差异说明来源。四交付文档/原始直接边界输入与日志/准确设备附录/SBOM依赖差异/同签名最终APK来源/ZIP外seal与只读验证齐全，一次完整主动报告。

当前无ADB/设备/真实媒体/迁移写/activation/新approval或实际catalog；PREPARE无authority，原107218/档案/guards原资源、独立Kit/Flutter及框架/许可/P0保持。D1未过，M0未启，长期准入OPEN。未授权子代理。
