# INPUT_SINK02 两项集中修复开发要求

2026-10-21；INPUT_SINK02_FIX。依据阶段B集中独立报告dc6271e9ed151e0779740c98a63e543830f5a506ea34d641d46ba8702a09c575，P1 B02和P2 B01整批修复，不单项反复交接。INPUT_SINK01旧334项/ZIP及此前1699冻结项全部保留；新目录新candidate。A01/A02与三依赖本有限离线准入通过结论保留，但不能覆盖当前输出缺陷。D1未过M0未启，仍纯离线零SDK/ADB/5037/设备/占用/旧handle查询。

正式派发：
1. B02/P1：TemporaryOutput.markReady/finishOriginalCallbacks及ownerReturned/retained资格覆盖所有同原host任务，包括writer外reopen/validate/READY/COMMIT及其原callback/thread尾段；future或ACK早完成不是原任务真实归还，不新造平行计数/替代任务冒证据。实际业务READY/COMMIT语义与源/原owner保留分开，未返/UNKNOWN时不发资源已归还、不允许后继危险动作，不抹原ACK或伪回滚已发生宿主动作。补validator早future、COMMIT早ACK等受控原尾段，以及reopen/READY对应分支。
2. B01/P2：finishWriter中flushAttempted/closeAttempted等一次进入标记仅在原动作真正准入时改变；准入前被原write尾段挡住应可在准确同原尾段归还后合法继续flush一次，再close一次，不留下永久无错pending或跳flush。已执行、执行是否发生UNKNOWN、已确定失败必须区分，不能盲重试或双close/双flush原在途动作。全链firstFailure/partial ACK/UNKNOWN账不退款。
3. 用tester阶段B独立5场景及生产JAR优先加载复现作回归，同时覆盖A01共享源/跨factory/epoch、A02 partial physical10/ACK3及callerPos/私有块、全部20原组/19项受影响裁定和原keeper/thread真实归还；不得为绿色测试放宽原门或用相同实现镜像断言。
4. 集中完成两项源码和有限自测后一次必要实际接口/严格metadata/锁编译与候选产物；依赖/native/无关功能不变。完整新源码/JAR或APK身份、自检原日志/失败/差异、状态模型及每个原阶段归还证据、ZIP/seal一次交负责人。若发现同类生命周期缺陷，在本批一并修复并列范围，不中途小项交付。不改旧候选，不引入新资源/诊断框架，不启设备或M0。
