# D1 E7A coder requirements V1.0

2026-10-17，负责人正式派发，关联 docs/tester/D1_E7_ARCHITECTURE_REVIEW_REPORT_V1.0.md。

E7完整复审NOT_SUPPORTED_FOR_READ_ONLY_DEVICE_DISPATCH，接受E7-F01/P1：await10s后PENDING再assert完成JUnit会触发runner结束杀进程，static Job无法保在途/UNKNOWN owner。新候选 docs/coder/d1e7a，旧E7冻结不改。正式集中修复实际诊断任务/结束边界。

10秒是既定诊断资格截止，超时永久PENDING/非PASS/停依赖，迟到不能改为限内成功。实际原open/read/history/proc/close未返或allocate/close UNKNOWN时，不准靠assert/throw/正常JUnit完成/daemon/静态引用声称保留。明确可执行结束协议：原操作真实返回/资源已证归还才允许正常结束；无法证则保原任务和可识别handle并输出PENDING给外部协调，不取消future/用进程退出充当close。若引入独立受管组件，须说明权限/生命周期/真实ACK/进程死亡和不确定状态/外部停止如何保留恢复，不盲加deadline或无限无证等待。

直接执行实际Job/runner结束决策边界的有限证据，覆盖快成功、原失败已收尾、10秒仍在途、迟到真实返回、close UNKNOWN、分配窗口、中断及异常，证明PENDING不可变、结束不得早于真实归还。平台替身限制明示，不能仅重跑27项死亡gate。

死亡诊断生产门max8/只读owner/no grant/持久设计blocked保持，原guard/预算107218/每host安全/P0许可不变。必要一次主双APK构建，四文档、精确diff/来源/输入/日志/SBOM/ZIP/外seal/只读verify/准确下一只读设备计划，整包完成主动报告。无ADB/设备/媒体/下载，不部署E7、不继续normal或恢复写。长期准入仍OPEN，D1未过/M0未启。
