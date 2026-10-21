# INPUT_SINK03 异常边界集中修复开发要求

2026-10-21；INPUT_SINK03_FIX；依据完整独立报告c176949cf1c68978bf600ee62997e53360234835f09679ad816fd785db3db71f。原B01/B02有限修复通过，整包因B03/P2+B04/P2仍FAIL。旧INPUT_SINK02及全部既有冻结/历史失败/UNKNOWN保留，新目录新候选集中修复，纯离线不依赖真机，不SDK/ADB/5037/设备/Gradle并发，不启动M0。

1. B03：首次等待/晚结果observe准确捕获原stage直接CancellationException，稳定脱敏错误、不保留私有message/cause，原终局结果只消费一次。WRITE已真正进入但无有效ACK时登记actual下界/UNKNOWN reservation一次，晚取消不清先前timeout、不重复计账；不能因future取消推实际0B/已回滚/已提交。按WRITE/FLUSH/CLOSE/REOPEN/VALIDATE/READY/COMMIT/ABORT/QUERY所有适用原阶段审查，不只补报告六点。COMMIT未知业务状态仍保管并通过准确原QUERY/authority收敛，不伪释放/重发。SDK不主动cancel宿主原future求测试通过。
2. B04：cleanup准确区分从未准入的短暂pending与原ABORT/QUERY已进入的超时/失败，后者立即保留首次稳定错误；同原stage晚ACK、QUERY确认ABORTED及真实owner返回可以更新物理终态但不清失败历史/UNKNOWN，不推翻真实ABORTED、不新增RPC或退款。未准入不捏造失败，已进入UNKNOWN不盲重试。
3. 集中建立覆盖原阶段×正常ACK/ExecutionException/直接CancellationException/timeout后晚成功或晚取消/原线程尾段/authority未知的适用状态矩阵，说明不适用分支。复用tester23独立场景与源码/生产JAR双路径，重点十个新失败场景；补输入现有取消/错误脱敏与源释放受影响回归。保留原20组、17原尾段/19矩阵/A01/A02；不以计数取代真实状态证据。有限gate必实际join，测试异常不丢同原线程/进程，不用退出JVM伪正常释放。
4. 一次完成源码/自测再必要严格离线实际Android/Media3 ABI构建，依赖锁/metadata和许可无关范围不动；未改native/host复用。完整交差异/异常状态模型/原日志与生产JAR回归/产物hash/完整ZIP-seal，主动报告负责人后冻结，tester集中复审。任何同类漏洞本批一并列明，不逐问题交测，不造新资源/诊断框架或设备执行材料。平台FD/真实容器/业务COMMIT仍NOT_RUN，旧P0不减。
