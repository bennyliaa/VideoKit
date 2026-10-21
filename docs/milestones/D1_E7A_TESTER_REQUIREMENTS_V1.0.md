# D1 E7A tester requirements V1.0

2026-10-17，依据负责人E7A完整派发。先独立静态复审，不设备、不部署E7或E7A、不正常测试。

重点E7-F01/P1实际任务与runner结束边界：10秒资格截止永久PENDING，迟到实际资源归还也不能改PASS；原open/read/history/proc/close在途、allocate/close UNKNOWN不能结束instrumentation，不能以static/daemon/throw/取消/进程退出替代close。核可识别原任务handle、对外状态/停止协议、实际原owner返回和结束ACK、外部进程死亡UNKNOWN，以及无需无限轮询或盲延时的明确隔离处置。

核直接执行实际Job/finish决策的有限证据，快成功/收尾失败/截止在途/迟到/close未知/分配窗口/中断/异常均覆盖。区分纯核心/平台替身与Android实测，不以旧27项gate代替新生命周期证据。

核只读owner/noFollow/257B/max8一次/no grant、原guard/fence/ledger/资源/107218与reserved0及P0保持；持久协议仍设计阻塞，长期准入OPEN，AVI/能力/cancel不解锁。整包四文档/源码diff/输入构建/签名/SBOM/native/ZIP/seal与包外只读回执一致，旧E7全195项不变。仅完成整包后集中报告；后续只读计划另行负责人正式派发。
