# D1 R2 源与输出契约、原生故障判据整批设计需求 V1.0

日期：2026-10-16；状态：正式派发，仅设计文档与只读证据审查，不产品编码/构建/ADB/新APK。

完整读取docs/D1_R1_COORDINATOR_DECISIONS_V1.0.md、D1_R1_REVIEW_REPORT、R1两主体与原需求/公共API/集成/输出/系统设计。按负责人决定集中关闭R1-R01至R04材料缺口，并引用R05固定快照勘误；保留R1已审核hash，不改旧候选。

## 整批交付内容

1. D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md：给sourceLeaseId/sourceVersion/mediaToken/consumerId/bindingGeneration/operationId/预留/seq精确定义，身份、别名合并、seal/reserve/open线性化、会话释放/全源可移动区别、迟到/丢通知/query/失败close/进程死亡恢复状态表。至少六条有初始状态→并发顺序→唯一允许终态的反例，包含异token同物理源＋未来open、seal与迟到open、换版后的旧通知。不能引Browser数据库/路径/移动API；源聚合的宿主责任与Kit实际资源证明明确。
2. D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md：能力与FD所有权矩阵、稳定exportId/handleId/ownerEpoch/attempt/plan/source版本关系、临时writer与只读验证lease生命周期、写前拒绝、close/flush/durability/空间未知、READY/abort/query/COMMIT的仲裁和幂等。至少覆盖READY回包丢失、旧owner ready对新owner abort、writer未关闭/验证不可读、能力冲突、重复openTemporary和取消未知。所有错误映射现有码或明确提出新增码及兼容影响，不自行冻结公共API。
3. D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md：以现有真实本机文件provider为首个有限离线候选，写出实际路径/输入hash来源/真实ReadHandle调用与版本保证、注入与真实故障区别、2GiB边界小块和独立对照、未知/空/短读/提前EOF/0进展、迟到open/read/close失败恢复、双消费者与未来open、纯顺序/可seek/FD Sink及未知READY等具体case输入/预期码/资源/终态。只读源/有限buffer及累计IO预算、输出独立目录/预算、超时保留PENDING与停止条件写清。不运行实验、不实现M0；Windows小块IO不能外推Android/SMB/完整播放。
4. D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md：逐调用列真实进程/UID/输入权威/资源owner/触发/独立观察/宿主与另一任务结果/实际回收证明。native/Java异常/OOM/全局压力/系统强杀分列。负责人允许分栏原则不等原P0通过；原精确signal用例/历史FAIL→新功能隔离用例与独立observability能力映射明确，unknown实际字段不捏造。宿主JNI不能仅记风险就准入，如无机制证明给具体BLOCKED与待评审替代，R2不自行改权限形态/新增组件。
5. D1_R2_DELIVERY_V1.0.md：按R1-R01–R05逐项关闭材料缺口/剩余真实实现缺证，列主体文件hash、原P0及§29影响、明确可执行下一批、需要设备和仍可离线完成事项；少量有结论的图表即可，禁止复制旧报告堆页。所有建议/已决/未验证分开，原文P0、既定架构、C14冻结和历史统计保持。

全部一次完成交负责人，先独立评审再任何实现。不开Gradle/设备、不下载模型/媒体或改开源依赖。Media3薄适配、受限FFmpeg仅Debug、Flutter/独立Kit/C ABI、Android先行不变。通过任务完成事件交付，不反复跨窗口通知，不自派tester/下一阶段。D1未通过，不进入M0。
