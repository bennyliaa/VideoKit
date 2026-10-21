# D1 E13D OFFLINE_ROOT_CAUSE 完整交接 V1.0

2026-10-18。已保存正式需求 docs/milestones/D1_E13D_CODER_REQUIREMENTS_V1.0.md / D1_E13D_TESTER_REQUIREMENTS_V1.0.md。完整分析与处置/修复/验证提案：docs/coder/D1_E13D_OFFLINE_ROOT_CAUSE_AND_RECOVERY_V1.0.md。当前仅离线文档交付，生产实现改动0、构建0、测试0、设备/ADB/部署0，不联系其他项目、不修改live对象/ledger，不继续追浮动输出。

结论：本次实际挂起点 NOT_UNIQUELY_DETERMINED，不能宣称已证实Binder/主Looper死锁或kernel拒绝。E13C V1.0（5880B SHA9cdc913d8a6c98e1aad4c4acddb0ab3ed3adc66dd39c2ee5d053139b678ace74）及V1.1（2733B SHA77a21b4beeb77e11ce065af97e0548bdcebb86f6f0c3d0be2e7061ab950e2008）准确引用。主case exec42537/PS39560/Java38056/ADB49540、Android14763/14765/14779只作最后实测切片，不宣称本轮仍活或已归还。无case terminal raw/绑定结果；后五法/M3 NOT_RUN。LOST_DIAGNOSTIC_OWNER_UNKNOWN严格只属失败ps诊断，原诊断PID未记/局部对象不可恢复，不混同主case，不补stderr0、closeACK或退未知预留。

已沿真实源码核：测试@Before非主Looper断言→E9当前观察→codec正例bind/HELLO/unbind→fixture同步Binder→普通UID目标bind/unbind→共享BindingOwner→runner finish/onException→原PC process/reader/decoder/custodian。fixture clearCallingIdentity不切线程，源码无runOnMainSync/等待自己服务回调；共同owner不持锁跨port.bind/unbind或callback work。codec HELLO无同步回调测试Binder。因此无可静态证明的经典同线程回调死锁闭环。

另读本机已缓存准确lock版本 runner1.7.0/monitor1.8.0源码，无网络或下载：测试前monitor.onStart有waitForIdleSync，故app进程存在不证明已进入绑定；monitor.finish等待activity约2秒且禁止main线程，不能把该有界循环直接断言为本次长挂根因。来源及准确行摘录已封存，未用SDK36.1冒API31厂商线程证据。

四个静态已证的条件窗口，均未冒称当前实测根因：
- D13-S01：callback work内countDown先唤醒测试，finally才归还callback计数；runner第一次canFinish=false即返回，之后同一原owner真返没有自动重新finish接线。onException同样缺保存/续办。永久UNKNOWN应继续pending，不能补finish假归还。
- D13-S02：fixture只有单次资源快照，resourcesReturned未精确成立则probe sticky unknown；现有code1已consumed，无同scope原TargetBinding查询/晚返ACK。保守门保持，但无法区分已知在途与永久UNKNOWN的后续处置。
- D13-S03：5秒await在bind返回之后、30秒计时在@Before观察成功之后，均不限制同步bind/transact/unbind/观察fsync；PC55秒只托管不取消，不可扩大timeout或重发充修复。
- D13-S04：PC先等原ADB退出和reader再decode，只有runDecoded正常返回才print raw。55秒先抛后即使晚到decoder确认原归还，main的print不会再执行，原raw可能留Operation私有buffer；外层也按tester报告在Java返回后才落完整回执。无raw不能定位Android行，晚close不能改超时资格PASS。

假设矩阵区分：测试前mainidle/@Before未返；正例平台调用；fixture内部原调用；finish门失去续办；PC pipe/authority等待。58908B原ps切片仅见app、未见codec/fixture进程名，不等于它们从未启动。需要原scope阶段日志或原线程关系，缺材料时继续NEEDS_DIAGNOSTIC。

最小只读观测只是待审需求，当前不执行/不复用剩余额度：
先接收tester明确交接已落盘raw；若负责人以后另派，最多2直接原ADB，各10秒/64KiB、总128KiB，身份/完整性/过限即停。第一只system_server完整active及两个固定服务切片，第二按必要条件取最多200条准确scope/PID已存在日志；无clientdump/新绑定、SIGQUIT/debugger/ANR/heapdump/重测。现版本缺stage可能仍不能唯一定位。观察器须进入前原Process/readers/pipes强持有、先保存身份、空数组非null、落盘故障仍同宿主保管，未审清前不得发。当前不建议新增PC STATUS/OP；如确需必须另审同handle的一次连接/4KiB/5秒和accept预算，不能暗加且不产生close授权。

原任务安全处置：
仅同一原Android owners自然真返→同runner终态token→原ADB/reader/pipe真返→原decoder同scope确认→原custodian/外层句柄自然返，才出补充回执；超55秒仍不升级PASS。若S01失续办/永久原调用/UNKNOWN，现已装bytecode没有受审恢复入口，不能以新APK、重装、外部finish、清空集合、二次unbind、重发code1/换UUID结束旧对象。继续隔离保管，原诊断UNKNOWN独立不能恢复。未来若需外部处置应另审“非Java归还/外部终止证据”，本轮无动作且不写原closeACK。
当前所有新安装/升级/同设备case继续禁止。防并发必须按serial+app/test/fixture+原scope/case pending封锁；新UUID/once不绕过，PID检查不能放行，新候选仅离线，待原处置结论及freshM1再谈部署。

集中修复提案（全部未实现）：
1) 实际adapter逐stage/原owner/scope/thread/UID/PID有限元数据、异常摘要；锁外记录，不用日志充ACK。
2) 同一runner不可变完成请求+先订阅归还事件避免丢唤醒，最多一个强持有非主finalizer，实际canFinish后一次super.finish；不能post到main调用monitor的等待；保原超时/失败，永久UNKNOWN不finish。
3) fixture同scope原TargetBinding只读快照/有界晚返ACK协议，单次consumed不重做负例，不用新owner接管。
4) 原PC唯一reader有界增量归档、55秒前后同operation raw/EOF/自然exit/pipe事实分栏，持久化故障也保原owner。不能追溯导出现存内存或修复丢失诊断。

直接生产边界验证计划已具体列出：实际PermissionProbe callback countDown/finally交错+共同owner+runner；各原平台调用未返；SenderService端点/原身份晚返和UNKNOWN；实际runner onException/finish及monitor非主约束；实际E13HostCase/E9PcSupervisor晚到raw和磁盘失败；准确公开deploy/case入口跨UUID pending拒绝child/install0。旧9组或synthetic gate不能单独充验收；平台替身明确有限，实际不同UID/Looper/Binder/unbind必须旧任务处置后新派Android单方法验证。无renderer/audio/Kit扩展或旧source/信号重跑。

封存：
docs/coder/D1-20261018-E13D-offline-analysis.zip，40299B，SHAdbe40dc80a4962b53f677fdc55d034b0d1b282529d6fb9a37109e25fd04d6385；
外seal docs/coder/d1e13d/evidence/e13d-freeze.json，2102B，SHAacc83e5aff9288099c1f324fb24394316dedfd83272cce66cd8299a215b66365。
8 ZIP条目/9不可变记录，18源码文件行摘录。原35文件pending manifest、6文件repair manifest、E13A270/E13B118/E13C141不可变行全核保持，不加总冒唯一文件数。默认/显式verify/help实际只读通过，7文件前后一致；回执 docs/coder/D1_E13D_FINAL_READONLY_VERIFICATION_V1.0.json。live ledger、活harness和将来raw不封印；只按交接报告解释外层缓存，不把当前harness源码冒执行时冻结版本。

请统一审查根因边界、当前原任务处置和下一实现批，不在当前活对象上实施提案。D1 NOT_PASSED/M0 NOT_STARTED、P0/历史FAIL/UNKNOWN全部保持；214483/7R7S等只作历史准入，未读case后账本。

