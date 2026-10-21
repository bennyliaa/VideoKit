# D1 E1C 五项集中修复开发需求 V1.0

2026-10-16。负责人已全文审阅D1_E1B_REVIEW_REPORT_V1.0.md，采纳4 P1/1 P2。用户明确要求五项集中修复、自检冻结后整包复审；不派真实媒体实验。保持E1/E1B及R1–R4/C14冻结只读，在docs/coder/d1e1c续作并保留完整依赖源码。

1. T01：真实pending completion/private result cell。delegate可先完成但未开闸不得交消费者；取消或响应deadline返回具体CANCELLED/SOURCE_TIMEOUT，底层对象/结果/私有缓冲继续留账至真实排空；late H仅清理，不交付。测试观测等待future/响应和未交付/未复用，不只设置ops标志。ZERO调用实际bridge零长入口，delegate增量0，去掉0==0。
2. T02：源权威同一原子点核reservation ACTIVE/非finished、consumer/version/generation、handle精确归属；end不可逆阻断future open/read，旧已接纳只排空。补end(A)而B活时复开A、借B身份读A句柄、end/cancel与open/read竞态，断言delegate0及他消费者不变。
3. T03：去old=True快捷拒绝，ready接真实捕获的owner实例/epoch/export/handle/attempt/revision/receipt，按当前持久owner真实比较。e1请求在e2 takeover后原样提交；同时验证未takeover合法owner成功、错误epoch与receipt拒绝原因，不能由测试布尔直接决定结果。
4. T04：恢复同身份单调合并snapshot/可信q日志，预留/未知不退款；日志比snapshot少时不能降计数。持久admitted-task inventory或等价最小信用，缺失shard明确未接纳/丢失/批次UNKNOWN，不以目录不存在视0。补高snapshot低日志、已接纳shard丢失、GC跨shard max及围栏不重造raw handle。
5. T05：元数据snapshot/event/global log/receipt全部单次有界write核实际返回长度。短写不无限补写、不认完整提交，未知/失败禁止下游native/RPC，分别记请求信用/实际written。仅自建writer短返回注入，断言native0/无虚假完成；不制造磁盘故障。新增步骤若影响R4计数/事务预算须明确差异，不暗扩。

集中完成全部修复后主编译/必要修复重编、针对性合成负例及相关回归；不要逐项交测。新批合成fixture累计≤2MiB，日志证据≤4MiB，独立目录，旧失败不删除。保留原452分配/544硬控制及其他媒体/时限/资源预算，真实运行口径如实报告。无test_media读取、真实PF/媒体实验、Gradle/ADB/下载/产品M0。requiredDurability/真实版本/运行时资源限制不靠修复声明通过。

交D1_E1C_DELIVERY_V1.0.md、D1_E1C_IMPLEMENTATION_BOUNDARY_V1.0.md、D1_E1C_EXECUTION_APPENDIX_V1.0.md及完整源码ZIP/产物/manifest/只读verify/证据hash，逐缺陷→修复入口→有意义负例→结果/限制映射。完整冻结且无在途后主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；不自行派tester或真实实验。D1未通过/M0未启动，JNI仍BLOCKED，历史FAIL保持。
