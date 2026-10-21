# INPUT_SINK05 迟到终态与原回调顺序集中修复要求

2026-10-21；INPUT_SINK05_FIX；正式集中修复。依据完整报告f527fea952e07f8ee568272170c7ad7b44ae956e2e047fb860d0d1d51796f8c5。B05/C01原修复有限通过，整包因B06/B07两个P2仍FAIL；B01–B04/A01A02既有通过保留。旧705项/此前2978冻结及原失败/UNKNOWN/测试证据保留，新目录新候选。仍纯离线，D1未过M0未启。

1. B06：所有终态来源（首次ACK、晚observe、原完成回调、QUERY、readonly authority）统一经现有状态模型的不可逆转换门，不能只在query校验。原READY响应滞后于ABORT+准确QUERY确认ABORTED时，形状合法token也不构成有效READY；保留真实ABORTED、原首错和冲突/UNKNOWN，不readyAck+abortedAck相矛盾并存或凭坏ACK归还。记录原响应实际到达和拒绝原因，不删除原宿主动作事实或新发RPC“纠正”。既有READY token确认也不可被不同token替换。用现有类的共享转换函数/状态逻辑收敛，不建新的状态平台、executor、验证ledger或协议。
2. B07：原宿主task线程已返不代表原READY响应stage/coordinator callback已返。归还与后继准入需完整覆盖原stage完成/原callback及executor/thread实际join；尚pending走稳定OUTPUT_ORIGINAL_PENDING/既有pending返回，不泄内部IllegalStateException。正常QUERY确认READY但原同一个正确READY ACK仍在途时继续持有，不cancel/重RPC；原ACK真实返回且同原callback/threadjoin后才归还。不能为避免异常直接忽略回调或靠数量自证。
3. 不只修两例：在现有逻辑上列准确同原READY ACK/ABORT ACK/QUERY终态/readonly事实与原callback物理返回的适用顺序矩阵；用有限可控gate遍历关键先后顺序（正常同token、ABORTED后矛盾晚token、QUERY先确认READY后ACK、失败/取消/超时后晚ACK/原callback尾段），每一步核业务事实/原firstFailure/响应是否消费/原keeper与线程/剩余RPC数。非法顺序应稳定失败保管，合法迟到应可收敛；不要求数学全状态证明，也不能把列举数量当完整协议证明。
4. 原两场景源码/JAR复现先留证，然后对新候选同源+实际交付JAR优先双路径回归。B01–B05/A01A02、19矩阵、既有异常/返回值套件受影响范围保持，C01文档真实入口正反例再次实跑。不以重复整套数量掩新顺序遗漏，精确记录所有原callback和有限gate真实归还。
5. 两项集中实现、自测、一次必要strict实际ABI构建，依赖锁/metadata/native/host不变；全源码差异/顺序模型/实际JAR和APK/原日志及失败/独立命令/ZIP-seal一次主动交负责人后冻结。零SDK/ADB/5037/设备/占用/旧handle查询、不引入设备发布框架、不自动M0，平台真实效果仍NOT_RUN。
