# D1 C12 注册握手与未知绑定撤销集中测试需求

日期：2026-10-16；状态：2026-10-16 11:01正式交接。C11报告已完成，C12完整冻结且负责人独立核验通过；按冻结计划执行，不测试浮动工作源码。

重点验证实际registrar同步flags及认证/固定ACK形状，正常MP4/AVI必须先完成注册、真实帧、STOP/逐代次死亡/Source/slot门禁；oneway即使带其他标志仍拒绝，框架metadata不得错误拒绝同步事务。各注册错误应有稳定code/阶段，主异常与cleanup分栏，不能用超时猜唯一根因。

验证绑定已接受但未注册时cancel可独立撤销绑定、停止自动重建；迟到bind/HELLO/注册、旧death、新端点及解绑失败均不能伪释放。unbind只证撤销，不证死亡；未知/在途quarantine和两槽实际预算必须可查询。第二任务继续真实解码，额外端点无START/source。保留C11代次、停止、源预算和取证30项覆盖，新增实际握手/撤销反例按冻结计划整包执行；host7和legacy8按共享影响回归，不任意缩为容易通过项。

手机和平板已有授权，现场核验serial/API/ABI/页大小、实际hash/签名/用途、enabled/Service/空间。手机仍禁用则环境阻断并推进平板，不索重复授权、不绕过。先备份旧身份/可读数据，同签名明确用途保留数据更新；不清数据、不改旧capture/证据，素材只读核hash。每设备日志32MiB、legacy新输出32项/8MiB，采集中限额。

一次一个明确设备/方法，无Gradle、不改冻结件。失败先停调度核在途/实际资源，再继续独立项，不重复同条件求通过。注册失败退出的SIGKILL不算目标SIGSEGV；原OS status与trace另列，status0仍UNKNOWN/FAIL，外部raw不回填产品App结论。每项PASS/FAIL/BLOCKED/UNKNOWN/NOT_RUN如实分类。交docs/tester/D1_C12_TEST_REPORT_V1.0.md，包含完整集中缺陷、预算/素材及最终无在途状态；D1与发行仍未通过。
