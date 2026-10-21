# D1 E1D 完成交付独立复审报告 V1.0

日期：2026-10-16。按D1_E1D_TESTER_REQUIREMENTS及负责人正式整包交接，完成C01/C02源码、冻结归档、既有合成证据与异常退出路径的一次独立静态审查。

## 1. 结论

**原C01/C02的完成决定、锁外通知和实际回调排空主路径可静态闭合；新增1项P1启动异常阻断，暂不建议直接另派真实本机实验。** E1D-D01：CompletionHub部分启动失败后仍标记started、接纳未封闭，清理假定两线程均已启动，可能二次抛错而缺少可判定的启动失败回收/未证状态。

该问题不是“所有未测异常都要补测”：当前代码给出了具体的两线程非事务启动、错误接纳状态及无条件join路径。正常573项合成检查与主动披露未覆盖这条路径。建议只集中补该安全出口及针对性负例，保留原交付/回调和T02–T05已认可修复，不重新扩展设计范围。

本轮没有重跑Targeted、SelfCheck、Recover、PF、媒体、编译、Gradle或ADB，没有新建harness/helper/worker。只运行已读过的只读verify、tester独立hash/ZIP/AST/既有记录解码；全部返回，无本轮在途任务。原冻结件未改。D1未通过、M0未启动，JNI/C14/P0/历史FAIL保持。

## 2. 身份与独立核查

| 对象 | 实际身份/结果 |
| --- | --- |
| freeze-summary SHA256 | 53feba0c78fac9a27f4b1c045f925d5db432b46ed8d1ebbbccdc89333f638186 |
| E1D-source.zip SHA256 | d5123e6527b6fbd613e7df565319bf14e8c8d6eeaba028e4474c35480c54ca9a |
| 只读verify | PASS：32源码、12冻结文件、216合成记录、13既有基线 |
| tester独立归档校验 | 清单全部字节/SHA、ZIP成员和内容一致，61入口存在，N/query/时间逐行与已审R4一致 |

报告依据包括三份E1D文档、活动SourceAuthority/PendingCell/CompletionHub/DeliveryFuture、Engine/Flow、PF/GC/controller、completion检查、既有回执及上游静态认可。当前Python Thread.join对未启动线程的RuntimeError也已只读核实；没有调用Thread.start/join做反例。

原字节副本、32份源码/工具/manifest、archive-and-manifest-audit.json、archived-evidence-review.json、source-anchors及启动反例静态记录保存在[D1_E1D_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E1D_EVIDENCE)。原E1C关系和失败证据只读保留，不读取test_media。产物身份一致不等独立重编或运行通过。

## 3. 原C01/C02及回归意见

| 审查点 | 判定 | 静态依据与限界 |
| --- | --- | --- |
| 普通/held统一交付决定 | 静态闭合 | SourceAuthority.complete/gate共用_delivery_locked和_decide_delivery_locked；原operation绑定、reservation、sealed/fence/finished/cancelled/recovered、handle身份/disposition均复核，不重新admit |
| seal/fence先赢与交付先赢 | 静态闭合 | cell.outcome只决定一次；seal先则晚H错误/仅清理，成功决定先则后seal不倒退，即使通知仍排队。普通/held open/read有各确定顺序检查 |
| Future与done callbacks锁外 | 静态闭合 | 源/cell锁只决定，_post在退出这些锁后入队；notifier退出Hub condition后调用_publish_outside_locks，标准Future完成和同步callbacks不持应用锁。end/cancel的活动Ops也不在外层源锁中等待通知 |
| native/gate/callback排空分离 | 静态闭合 | notification_done须注册callbacks实际返回；release还须native_done和gated，release_claimed防重入；Future.done和原J/R退出都不能代替G私有cell回收 |
| 容量与active归还窗口 | 静态闭合 | 8注册cell提前持一次通知信用，排队+active≤8；active私有资源释放后仍占容量，notifier最终在同一Hub锁归还。固定2worker/每cell4callback，无逐cell Timer |
| 慢/异常callback与submit异常 | 有限定支持 | 慢callback保留引用、drain/gate/close期限到Stop、封新transaction/query/RPC；受控回调实际返回才join。submit异常保留未提交及原错误，原submit仅在测试finally排空，不伪成功 |
| n31及n32正常收尾 | 有限定支持 | n31有界close/join固定Hub线程；n32前核cell/workers=0，n32实际close经原返回通道证明。正常证据不覆盖D01部分启动失败 |
| 原T02–T05 | 保留静态认可 | 精确consumer/version/generation、真实owner/epoch ready、inventory/恢复max/缺shard UNKNOWN、exact_write均保持，139/33/69/20组相关检查未被573总数替代 |

## 4. 唯一新增阻断

### E1D-D01｜P1｜Hub部分启动失败未封闭接纳，close不能安全处理未启动worker

来源：[start:35](D:/CodexProjects/VideoKit/docs/coder/d1e1d/src/notifications.py:35)、[ensure_accepting:45](D:/CodexProjects/VideoKit/docs/coder/d1e1d/src/notifications.py:45)、[close:114](D:/CodexProjects/VideoKit/docs/coder/d1e1d/src/notifications.py:114)、[controller异常收尾:43](D:/CodexProjects/VideoKit/docs/coder/d1e1d/src/controller.py:43)。

start在两线程实际启动前设置started=True并预占两个worker信用，然后连续notifier.start(); monitor.start()，没有逐worker启动结果、失败围栏或回滚。具体静态序列为：notifier已成功启动、monitor.start抛RuntimeError。此时started=true、closing/closed=false、blocked=null，ensure_accepting的现有条件仍可通过；但deadline worker并不存在，Hub不能再被视为完整可用。

close无条件join两Thread对象。本机Python Thread.join明确对未started的Thread抛“cannot join thread before it is started”。在上例中close可先请求notifier退出并join，随后join未启动monitor再次异常，跳过worker信用归还和closed设置。controller的兜底分支只据cells/queued/active判断PENDING，不包含部分worker状态；最后直接调用completions.close，该二次异常没有在此分支再转换为有界失败/未证回执。PF此时可能尚无J/R，而常规GC还会尝试缺失helper的操作，更容易进入该兜底。

**范围限制：** 当前controller在PF报错后会停止正常61行，不是说本轮观察到继续媒体、必然遗留线程或错误PASS。notifier在某些路径可能实际退出，外层也可能取得非零退出/超时证据；但这些不补Hub自身错误可接纳状态、不可重入close和缺少逐owner启动/释放事实。问题在具体安全出口，不在“未注入验证”这几个字本身。

建议将启动状态至少分为未开始/启动中/运行/启动失败，只有两worker实际启动后才允许接纳。逐worker记录已预留、Thread对象、start已返回、实际存活/退出/join证明；部分失败立刻围栏新cell/transaction/query/RPC，仅对实际启动的worker发停止并有界join，未启动/未知分开处理。信用按真实事实归还，不能给没启动的线程伪造THREAD_JOIN_PROVEN；未知仍保留PENDING。

close和controller启动失败收尾应可重复调用且不因缺属性或未启动Thread再次失控；回执明确原G/已启动worker/尚无helper、剩余信用和log关闭是否有证明。若join到期，保留PENDING与原owner，不强杀任意线程，不重新start碰运气。

补有限的第一/第二worker启动失败、第二信用预留失败及重复close负例；可注入自有Thread工厂/启动接口，不制造真实系统线程耗尽。核失败后ensure_accepting拒绝、未启动worker不join、已启动worker真实退出、无错误零资源声明、controller原返回通道保留失败/未证；所有受控测试线程最终join。集中补这一项，不重跑真实媒体或扩控制/资源硬限额。

## 5. 573项证据的范围与独立核对

选定证据159项完整合成+414项定向=573，定向分组153 completion、139源/owner、33恢复、69短写、20通用。早期393与上游检查不重复累计。completion检查使用生产权威/Hub/PendingCell和真实add_done_callback；跨线程Event屏障核同一源/cell锁可访问，超时不算PASS，测试finally受控放行后实际join。并未包含部分worker启动失败反例。

独立归档解码核8KiB槽SHA、schema3/身份/64KiB展开、32任务与PF inventory；两槽usage及可信q日志取max后与原回执一致。正常使用351N/83新q/18重放=452，输入1,573,492B/59，目标10/记录32，写信用655,360B，验证128B；R4各行分配保持，未用30B留原行。62结果行是PF+61，不是62媒体用例。

正常privateCells64/峰1/retained0，Hub notices64/cells0/queued0/active0/workersAlive0/blocked=null；两个原J/R实际wait code0。S17.D attempts3/native0、C原UNKNOWN/native1保持，owner退出不把原close改成功。原n32外层见证关联关闭前SHA6ac2133b118394394b9a2dd0562ebb33a8f6ffb04e8fa8a8da19a4894291a498；关闭前磁盘意图不是close结果。

正常元数据requested=written=6,396,288B、unknown0/HEALTHY，文件峰629,120B，累计写与文件峰分开。受管峰23含新增两worker信用，媒体5、64KiB槽1，不是完整系统OS句柄/内存测量；JVM/.NET基线、既有native pool/pipe线程和内部资源仍需真实口径。不能因账本23/24宣称整个运行时≤24。

PF/n01内新增本地worker、GC/n31内join映射明确，没有新控制token/RPC/journal事务。原452分配/544硬限、101query、IO/文件/32记录/180秒不放大；晚callback/系统IO不返时180秒只约束接纳/等待，不强制证明进程已退出。

## 6. 受限Future兼容性

DeliveryFuture明确将callback注册收窄为决定前最多4个，决定后包括callback内再注册均拒绝；外部cancel/set_result/set_exception也拒绝。它保持真实Future的result/done和已注册同步callback行为，但不是普通Future的完全可替换实现，不能让调用者默认“完成后add_done_callback立即执行”。

当前工具的回调检查均在决定前注册，场景普通路径取得值、held路径观察result而没有依赖晚注册，静态上与这些既定调用兼容。因此**不将此收窄本身列为新增阻断，也不要求立即实现产品通用Future适配**。后续真实实验配置/任何消费者若需要晚注册，应先明确适配或稳定拒绝，不能不经审定替换为通用Future宣传兼容。

## 7. 下一批条件与状态

建议保留C01/C02及T02–T05静态认可，集中修复D01并补针对性有界检查，在新批次冻结后复审安全出口。修复不是要求抵抗任意永久挂线程，而是部分启动这种可识别、可在本工具范围内处理的失败必须有明确围栏/清理/未证结果。

当前不直接准入真实实验；真实配置/样本绑定/2GiB窗口、source version/共享模式、requiredDurability/namespace确认和运行时资源口径仍需负责人另行审定。573是合成范围，不代真实媒体、产品Kit/Flutter/AAR/Android/NAS、许可或宿主JNI隔离。D1未通过、M0未启动。

报告与证据已保存，冻结E1D/E1C及旧报告未修改。本轮无Targeted/SelfCheck/PF/媒体/编译/设备/helper/通知worker任务在途；仅只读审查程序已结束。按用户授权保存后主动发送负责人集中处置，送达以最终回复为准。
