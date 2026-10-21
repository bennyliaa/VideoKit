# D1 E1E Hub启动失败集中修复开发需求 V1.0

2026-10-16。负责人全文审阅D1_E1D_REVIEW_REPORT，保留C01/C02和T02–T05静态闭合，仅修E1D-D01 P1。新docs/coder/d1e1e续作，旧包只读，集中修复/有意义负例/相关回归/冻结后一次交测。

1. Hub分未开始/启动中/完整运行/失败/关闭状态，只有全部worker实际启动才接纳。逐worker记录信用预留、Thread实例、start进入/返回、实际存活/退出/join与未知事实；第二信用预留失败同样围栏，不能预设两个已存在。
2. 第一/第二启动或预留失败立即封闭cell、transaction/query/RPC，停止已启动worker并有限join；未启动线程不join、不伪THREAD_JOIN_PROVEN，信用仅按未分配/确证未启动/实际退出事实分别归还；未知PENDING不清零、不重启碰运气。
3. close可重复且不对未启动/缺对象二次抛错；controller/PF失败兜底含worker生命周期/剩余信用，不仅cells队列。尚无J/R也安全收尾；原返回通道给失败/PENDING、原G/已启worker/未启helper及log关闭证据，非零结果不得当整批PASS。join超时保留原owner，不强杀线程。
4. 自有Thread工厂/启动接口确定性注入第一启动失败、第二启动失败、第二信用失败、重复close；核ensure_accepting稳定拒绝、未启不join、已启实际退出、返回通道不假0。补实际启动后异常/状态未知的保守判据（若无法证明未启动，不能归还信用）。受控线程最后实际join，不制造系统线程耗尽/永久挂线程。

保持原通知/交付修复和受限Future兼容边界，不重写已认可方案。保持452/544控制、101query及IO/资源/180秒等硬限，新增内部步骤明确映射PF/n01/GC，不能暗扩。合成fixture累计≤2MiB/证据日志≤4MiB；工具编译/必要修复重编允许，相关自检集中执行。无test_media/真实PF媒体实验/设备/Gradle/ADB/下载/产品M0。

交D1_E1E_DELIVERY/IMPLEMENTATION_BOUNDARY/EXECUTION_APPENDIX_V1.0.md、全依赖源码ZIP/产物/manifest/只读verify/针对性与相关回归证据及hash，逐D01路径映射。无在途后主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774，不自行派tester或真实实验。真实配置/版本/durability/总资源口径未放行，JNI BLOCKED/D1未通过/M0未启动。
