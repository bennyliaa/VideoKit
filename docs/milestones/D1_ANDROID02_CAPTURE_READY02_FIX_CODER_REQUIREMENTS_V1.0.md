# CAPTURE_READY02_FIX 开发要求 V1.0

2026-10-21；正式新批 D1_ANDROID02_CAPTURE_READY02_FIX。依据完整独立B报告 docs/tester/D1_ANDROID02_CAPTURE_READY01_PHASE_B_REVIEW_REPORT_V1.0.md，16084B/SHA606205d01c6db42c357ca72f403c6b676ed78b0f7a229f5a210e2c9be8efcfaa；223证据manifest41b423cff5020f65f8c26361ce9491edc2d30b1ca477be8a9e3bd58d68899a5d。结论三P2集中阻断，不重开已有限关闭的产品五项。

三项一次整批修复：CR-B01区分原console基账与同原可信外层新增delta，真实outer-return/proofwriter/转发/记录成本计入后继control及总账；绑定原controller/request/source/raw/console/外层原返回和已关闭writer，拒负数/重置/重复计费/无来源delta。不能仅放松相等校验或把未知成本记零。CR-B02最小复用既有外层owner，完整交准确生产外层Popen/reader/handle/proofwriter观察与原返回合同和实现，outerSeconds/localProofSeconds真实覆盖对应期间；超时只停新准入并保管原对象，不能kill/interrupt/取消/重复close。不能用入口prestart timer或字段值代真实外层观察，不新造通用dispatcher/诊断/release链。CR-B03严格验证App回执必需字段、类型、整数非负及上界、firstFailure必须null，完整history/原owner语义保持；不得误接受负账和有首错回执。

保持七角色准确argv及FIX02产品pins、7op/并发1/无retry，所有原分组预算和输出/时间上限不扩。仅独立新目录docs/coder/d1android02-capture-ready02-fix；旧候选/报告/证据/产品冻结不改。PREPARATION_ONLY仍SDK前拒绝，无设备执行许可。SDK/ADB/5037/占用查询/Gradle/JVM/媒体/共享缓存/旧UNKNOWN操作0。开发自检与独立测试分别在新输出目录，完整本地集≤30秒、串行1、文本≤4MiB、fixture载荷≤64KiB；仅固定受审Python producer/采集host，有限可释放自身门。未知原返回停止新增调用，不强停或重试。不能借离线动态通过冒真实Android/FD/平台finish/D1退出；M0未启。

开发将三项同批实现，必要关键顺序/边界自检集中覆盖：正确带外层新增开销链可接续、超限/伪delta/重复delta拒绝；outer与proof各自超时及原返回前后，迟返不能补绿；字段缺失/错误类型/bool冒整数/负数/等界/超界及非空firstFailure正反。保留正常七角色、busy实际采集停止、pending+final、stdin及超量部分保存回归。完整交最小diff、准确source/producer/owner合同/预算、所有失败和最终自检、清单ZIP与报告后主动通知负责人，再整包交tester；不逐问题交接。
