# D1 E8 coder requirements V1.0

2026-10-17。负责人正式派发：E7A_MANAGED当前history AVAILABLE/returned0/matches0/proc未查/gate BLOCKED；实际原操作holder CLOSED，seq9归档ACK一次，PID13876正常finish消失，无遗留任务。只支持快完成/保留到ACK，不把超时UNKNOWN算实机通过。

E8为设计整批，不新APK/设备/实现：交D1_E8_ARCHITECTURE_DECISION/LEGACY_MIGRATION_PLAN/WRITER_V2_CONTRACT/TEST_DESIGN_V1.0.md及需求证据矩阵。基于旧V1已完成结算/档案、多次既有真实死亡正向证据及当前历史缺失，提出可落地旧V1安全迁移/隔离与未来V2生命周期方案，避免不断加诊断。

明确合作故障恢复与同UID主动篡改的不同威胁模型，不凭空增加防回滚根永久阻塞播放器；不补造启动代次，不放弃真实资源归还。比较不可变旧终局档案/全部消费与产物、当前独占guard/精确fence/完整账本/无pending/现存进程与资源，是否可由明确一次性负责人审定的终局验收记录终止重复查询旧writer。若不足，列独立可信外证或具体安全隔离/不可逆动作，保留原账户和107218消费，不换budget/清账/删除/隐含重置。

V2事前可实现boot/start身份，哪些历史事实可持久、哪些每host重证，不能拿旧报告作liveproof，也不能无意义每host重证永恒事实。覆盖原host/跨进程/重启/淘汰/PID复用/部分提交/close unknown/回滚篡改/幂等重放/成本测试。仅本机设计和已有日志引用，无ADB/构建/媒体/恢复写/迁移执行。不可逆审批如需要，先做准确对象/变化/保留/风险/验证方案，由负责人最终处理。整包完成主动报告，tester独立设计审查后再实现；原E7A冻结、P0许可和独立Kit框架不变，D1未过/M0未启。

后续明确指令：只完成当前E8整批，保存完整结果并报告，然后暂停；不得开始实现/构建/设备/迁移/下一批，不因旧heartbeat恢复。
