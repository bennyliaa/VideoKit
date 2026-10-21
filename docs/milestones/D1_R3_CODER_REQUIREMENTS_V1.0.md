# D1 R3 集中契约修订开发需求 V1.0

2026-10-16。负责人已全文审阅D1_R2_REVIEW_REPORT_V1.0.md，采纳R2-R01–R03；17 SUPPORTED只代表材料依据，不是功能通过。一次完成下列整包修订，仅离线设计，不产品编码/实验/构建/ADB，不修改R2原始五份交付、R1或C14。

1. R01：定义close disposition和稳定对象/关闭ticket。分别处理确定delegate未执行、确定实际关闭但应答丢失、底层结果未知；仅能证明仍拥有原对象且可安全再次close才有新attempt资格。未知保留PENDING，已关闭只补查询确认，不重关裸句柄或用closed布尔证明资源释放。明确adapter逐层责任、并发重放、首次加最多两次安全重试的适用条件，增加三类故障及并发反例；冻结HostFixtures静态差距保留，不修改其代码。
2. R02：定义writer grant/delivery/claim/close状态及唯一接收owner、deliveryId与每份descriptor账本。同command重放仅返回不可写元数据，不能缓存重送FD/stream；交付未知不再授权writer，首轮仅query/围栏清理/abort。明确创建至发送、认领应答丢失、owner死亡的每个窗口和同command并发，逐项断言真实dup/交付/引用数量，不仅writerLease=1。
3. R03：交冻结branch manifest，展开P01–P13/Q01–Q09全部明确分支，含Q05成功流式与空间失败的不同终态；不要删分支省预算。每行给前置、独立/同任务、终态、input请求字节/调用上限、验证读取、目标/记录、句柄/缓冲、时间和停止后记账。预检JDK/.NET/guard+Java+reference纳入预算；计查询重放与新观察。总和保持输入4MiB/256调用、12目标/32记录、输出2MiB、验证4MiB、日志4MiB、全批180秒；不得未经决定放大硬限额。正常满读与合法短读不能同时笼统承诺全窗口成功：先预留剩余额度，不足则明确预算停止/未收齐，不能报provider违规。总最坏时间须含预检和清理，不能每分支10秒另加全局180秒。

交docs/coder/D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md、D1_R3_BRANCH_MANIFEST_V1.0.md及D1_R3_DELIVERY_V1.0.md（主体hash、R2三问题映射、与R2冲突时明确覆盖段落、未实现/限制/下一步条件）。跨文档语义须一致，不能仅说实现时注意。保留Kit/Flutter/C ABI/框架许可/全P0与全部历史FAIL。宿主JNI依旧BLOCKED，有限IO不能放行D1/M0；F03四次仅适用已定encoder协商，不能泛化API重试。

整批自查后主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；不自行派测试。无设备/构建任务允许新增，C14继续环境等待。通知失败保留报告，不反复绕过。

负责人半小时检查记录：2026-10-16，coder当前turn已结束但最终回复仅确认字幕素材。已有两份R3主体，无规定交付回执；已要求继续原批次未完成自查与交付，不重启成果、不交浮动材料。tester仍等待完整包。
