# D1 QUALIFICATION03 独立测试要求（等待完整候选正式派B）

2026-10-24；对应 docs/coder/D1_FACTS_V2_QUALIFICATION03_FIX_CODER_REQUIREMENTS_V1.0.md。当前02独立B完整报告FAIL已审，停止本scope后续动态；原报告ec65e690341848b104e155eeecece03fbb8f33b7ce9e3eb03e15c0c00170633f及259项原件冻结，不逐缺陷回交、不改产品、不审03浮动源、不Git/设备。完整03包经负责人审核后另正式派独立整包B。

独立验收重点：B02-01原生产identity到global_idle在实际新V2 wire/完整证明下兼容，所有生产调用方旧字段访问已经核查；裸fingerprint/错源/改值仍拒绝，V1原路由保持。B02-02原Gate/runner/outer权威账本在读前准入base/reservation、返回delta原并回、准确scope/owner/单调状态与异常不退款；缺base不能默认0，模块重载/多次消费/失败不能清零。分清facts和目标scope、Gate256MiB/64、Runner512MiB/256及全批1GiB各自归属，不能把不同账本局部PASS当全批集成。

新根 docs/tester/D1_FACTS_V2_QUALIFICATION03_INDEPENDENT_B_EVIDENCE/fixtures 下唯一scope，以真实离线原入口覆盖原facts→原Capture归还→独立有限review→生产前置identity→global_idle；固定SDK夹具不代真实设备。容量、43/15字段、V1/V2、时钟、TOP/仪器、来源和原返回按受影响面集中回归；未改02已验收限定层可以准确同源引用并核差异。必要覆盖缺口分层保留，不为160计数造真实未知。

正式B动态预算360秒/320秒停新增、读取1GiB、产物16MiB、辅助96、并发1、产品retry0，SDK/ADB/设备/Gradle/Git0；全部来源/图/预算预冻结，仅写新测试根和同名前缀报告。旧once/账本/UNKNOWN/FAIL不查不改、不二close/kill/补ACK退款。整批完整缺陷和manifest主动回负责人，通知失败保存报告。D1未过/M0未启；既定框架许可/Flutter/独立Kit/P0保持。