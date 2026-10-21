# D1 C11 进程代次与退出取证整批修复需求

> C10最终报告已落盘并审阅：docs/tester/D1_C10_TEST_REPORT_V1.0.md。C10-T01为App退出信号/trace采集缺口，C10-T02为worker重连身份/死亡账本混用，均阻断；C10-ENV01为手机系统禁用。tester明确无在途/残留，不新增设备执行。逐缺陷矩阵以这三个编号闭合，原历史FAIL保留。平板38 PASS/2 FAIL、手机40环境阻断不变。

> 正式派发：C10平板40项已完成（38 PASS/2 FAIL），手机40项环境阻断；tester正在收敛报告。负责人已查结束进程记录为空及最终预算/素材证据，批准仅本机开始本整批修复，不等待报告排版。最终报告落盘后一次对齐缺陷编号；不改C10，不设备。此段覆盖下文准备状态。

日期：2026-10-16；状态：准备，等待C10批次明确结束和负责人正式派发。当前仅允许既有只读分析，不修改C10冻结候选。

## 依据与范围

C10平板CPU25项中23 PASS/2 FAIL，host7与legacy8当前记录PASS，最终以集中报告为准。两项CPU失败为cpuSelfSigsegvSignalMustBeProven、cpuSecondSlotAndHostSurviveFirstSelfCrash。外部raw证明signal11，App退出记录signal0仍UNKNOWN。首项同task/epoch的HELLO从27146/99055变为27175/99056，而账本沿用旧frame/death；已确认实现缺陷，不能全部归为平台限制。手机系统禁用是独立环境阻断，不绕过、不重跑同条件。

## 整批实现与证据

1. 固定每个worker进程代次的Binder、PID/UID、task/epoch与状态。死亡回调必须捕获并核对所属代次，不能写入可被后续连接覆盖的公共身份。终态不可复活、首次连接完成后不可静默替换remote或接受另一个worker；迟到/重复onServiceConnected、旧death回调、HELLO在途及退出竞态均须明确拒绝或隔离处理。无需媒体重新启动时不得依赖系统自动重建服务继续同任务。
2. 对已由系统重建或迟到绑定的worker，不能仅忽略回调或unbind便声称已死亡。给出有界、严格认证的撤销/停止与实际死亡/未创建证明；未证的新进程和在途调用保留预算及quarantine。旧worker死亡不能释放新worker资源，旧帧/回调不能记到新代次。维持最多两CPU槽，第二任务独立存活并继续解码。禁止扩大权限、放宽UID/PID/task/epoch或用超时清零。
3. ExitEvidence在系统status0时不应跳过App trace采集。分别保留原始系统reason/status、trace读取状态、trace内身份/信号/来源及最终判定，不能覆盖原始status。沿用现有ExitRecordRules/TombstoneWitness及有界输入解析，不引入自制crash handler或额外高权限服务。匹配原始任务的PID/isolated UID/时间及进程身份，缺失、截断、冲突、歧义或错身份保持UNKNOWN/FAIL。外部ADB/raw仅独立测试证据，不作为产品App内数据源。
4. 先说明status0配合可信且身份匹配的App trace能证明什么、不能证明什么，并对应既有验收条款；不得擅自把status0、测试ARMED标记或预期注入信号判成成功。系统原始signal0的严格失败门禁保留，若需改变判定依据，提交具体证据和设计评审，不自行降低P0。采集失败、权限拒绝、无trace、解析失败、实际pending、信号冲突分别记录，重复采集有界且不因采集阻塞主线程或释放仍在途资源。
5. 有意义反例至少覆盖：旧death→新连接→迟到旧death、连接/HELLO与取消交错、重复连接、终态重连、未知新worker不能伪释放、另一槽不受影响；status0+trace存在/缺失/错身份/截断/冲突，以及非零系统status与trace一致/冲突。纯检查和真实Android测试分开，不能用本机模型替代实际Binder竞态。检查CPU与legacy共享退出取证代码的影响，保留host双轨输出安全门禁。
6. 沿用FFmpeg8.0.3、Media3和配额/白名单/Debug-only准入，不重写解码器、替换正式Flutter/独立Kit架构、扩展companion为产品方案或引入模型。仅必要协议/生命周期/取证适配；对应来源、许可证、依赖及框架映射一并提交。

## 一次性交付

整批实现、自审、有意义反例和集中构建后冻结D1-20261016-C11，不逐小项交测。先对齐C10最终缺陷编号与全部证据；仅本机，不ADB/设备，不改C01–C10和素材。交docs/coder/D1_DELIVERY_D1-20261016-C11.md、缺陷矩阵、设备附录、取证设计与未证限制、源码/产物/证据hash及实际归档校验。校验脚本计数须对应本批结果，不能沿用旧硬编码。若平台证据仍不可得，明确BLOCKED/FAIL与可推进范围，不重复相同条件碰运气。D1未通过，不进入M0。
