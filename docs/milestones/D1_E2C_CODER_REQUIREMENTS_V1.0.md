# D1 E2C G生命周期定位与有据修正开发需求 V1.0

2026-10-17。负责人全文读E2B独立报告，A01及主路径认可保留，实际G369>256/+209>64与旧失败不改。新docs/coder/d1e2c，先一个G、无J/R/媒体的有限生命周期定位，再按证据修正；本批不授权actual full补跑。

批准诊断固定一个原G/实际运行时：预定0、1活cell、该cell实际drain、8活cell、8实际drain、释放工具侧已完成历史强引用后共6观察点，各1样本；若8活超过既定容量则按8上限安排，不另扩。使用生产PendingCell/CompletionHub及真实Future/callback，不构造Engine/Native/Channel，不媒体IO/不J/R；固定2Hub线程按原事实启动退出。基线及PID/creation不重置，不强GC、不重采择低，不任意close运行时句柄。明确保留外部Future时工具能/不能回收的区别，最终观察后实际join并留关闭证据。指标临时句柄最多1，信用先留后开/实际关；诊断控制独立计，日志≤512KiB且纳入批4MiB，≤60秒决策/清理，未知PENDING不强杀。

先查实际Python版本/构建与可得同步后端证据，若不可得明确UNKNOWN；总数/对象引用与句柄类型因果分开，不编每cell几句柄。检查Engine.cells历史表、Future.cell/异常traceback/release/on_drain闭包、IO Future与wait临时对象以及可归因自有开关账；FFM在J不直接归到G。只根据具体证据修正不必要强引用/缓存，不能改协议/提前释放。

若确认历史重对象保留，活动对象表保持有界；native/gate/callback/notifier真正排空、既有调用者不再依赖后，以有界不可变审计快照替代完成重对象，断开工具不必要闭包/Future反向引用。外部持有Future/值的行为不得被擅自撤销或伪回收，不能删除活对象/未知owner换低资源。保留64总cell历史计数与审计事实，不能通过删证据减少日志/重置峰。改动后针对性有界合成检查验证容量/通知竞态/外部持有/晚完成/取消/回调/UNKNOWN不提前释放，保留C01/C02/D01/T02–T05回归。

允许必要工具编译/合成逻辑验证（fixture累计≤2MiB/日志证据≤4MiB）；不启动另一个诊断G、不实际完整61回归/真实PF或媒体/设备/Gradle/ADB/下载。若修复需第二次独立OS对照，先交具体变更与采样计划由负责人另派，不在本批无限实验。保持G256/+64等全部门槛及原baseline，不能将修正假设当actual通过。

交D1_E2C_DELIVERY/RESOURCE_LIFECYCLE/EXECUTION_APPENDIX_V1.0.md、完整源码/产物/manifest/六观察点与引用证据/修正差异/只读verify/hash，旧E2B保留。完整自检冻结无在途后主动报告负责人，待审后另派新actual自有回归，不能复用E2B已消费许可。真实启动授权层仍未批准，JNI/C14/P0/历史FAIL保持，D1未通过/M0未启动。
