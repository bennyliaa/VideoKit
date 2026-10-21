# INPUT_SINK03 异常、终态与原归还模型 V1.0

候选 D1-20261021-INPUT-SINK03；临时契约，M0未启。

## 四条事实分别保留

| 事实 | 证据 | 不能推导的结论 |
|---|---|---|
| 原动作准入 | 同一次真实host方法进入后的一次进入标记 | 不能把准入前pending变成已发生失败；已进入UNKNOWN不能改回未调用。 |
| ACK终局结果 | 同一原stage的值/失败/直接取消；只消费一次 | 失败/取消不证明实际0B、未发生副作用、原线程已返或可重试。 |
| 原任务真实返回 | 同原host/validator/commit authority、原registry/worker/coordinator线程 | 线程返回不证明COMMIT业务结果；ACK或新线程不能替代原返回。 |
| 业务终态 | 实际READY token/COMMIT ACK/准确原QUERY或相同任务原authority | 不覆盖先前firstFailure、UNKNOWN预算，不伪回滚READY/COMMIT。 |

firstFailure取第一次已观察的稳定失败，正常晚ACK和终态成功不清空它。取消意图是本地元数据；宿主ACK以CancellationException失败是另一条实际终局事实。SDK不对原宿主future调用cancel。

## 消费与映射

直接阶段首次get与晚observe均处理ExecutionException、CancellationException。进入consumeOriginal后，失败转为ACK_FAILED、登记首错、WRITE登记UNKNOWN、清除该原pending与不再需要的原私有块。重复observe不会再消费该终局、重复加reservation或重发调用。timeout保留同一原future和私有块；原未完成期间仍ACK_PENDING，不把timeout当终局失败强行消费。调用本身抛异常则INVOCATION_UNKNOWN，保留一次进入事实和未知副作用，不盲重试。

| 阶段 | 未获安全白名单错误时的稳定映射 | 特殊事实 |
|---|---|---|
| WRITE/FLUSH/CLOSE | OUTPUT_IO_FAILED | WRITE无有效ACK登记原请求UNKNOWN一次；CLOSE失败ACK与同原writer物理返回分列。 |
| REOPEN | OUTPUT_REOPEN_FAILED | 不重复原reopen，原读回registry仍决定源真实释放。 |
| VALIDATE | OUTPUT_VALIDATION_FAILED | 原receipt失败不能补READY；独立validator原证明仍参与保管。 |
| READY | OUTPUT_READY_UNKNOWN | 原真实READY ACK/token即使晚到也保留；取消ACK不能推断未READY。 |
| COMMIT | OUTPUT_COMMIT_UNKNOWN | 原ACK未知继续保管，不能把cancel/线程已返当未执行或已提交。 |
| ABORT/QUERY | OUTPUT_ABORT_UNKNOWN | 已进入失败先登记，后续准确ABORTED与owner返回不得擦除历史。 |
| 原等待超时 | OUTPUT_TIMEOUT_PENDING（READY保留其现有READY_UNKNOWN入口code） | 既往首错优先；晚成功/失败/取消不覆盖它。 |

既有明确权限/无空间/断开等白名单语义沿用；对外新建稳定IOException，宿主原私有message/cause不透传。输入现有SOURCE错误映射未修改，仅补受影响检查。

READY/ABORT/QUERY view只转发同一次宿主原stage，完成失败时先记录脱敏首错再完成view。缓存view不会成为物理返回证明，不用于重新执行原动作。

## cleanup准入与deadline

原ABORT未准入，或ABORT ACK已到但原尾段仍活、QUERY根本未准入时，保持pending/retained，不登记虚构RPC失败。ABORT/QUERY已经进入后的失败或timeout立即sticky。若timeout抛出后、catch登记前晚ACK已到，用已发生的等待超时和对应准入事实记录，不能仅看view现在done就漏掉历史。

原ABORT失败但实际宿主已经ABORTED时，后续准确原QUERY可确认ABORTED；返回资格仍等原host/原coordinator实际线程，firstFailure继续非空，ABORT/QUERY RPC各仅一次。QUERY自身失败/取消且无准确终态证明时继续保留，不能推测ABORTED；同原task权威事实可在真实归还后收敛。

## COMMIT和终态authority

`Commit.originalOutcome(task, token)`仅允许读取准确同原COMMIT和原宿主查询已建立的事实，不能启动/重试RPC，不得根据取消、READY或writer已返推断。默认UNKNOWN。`commitAcknowledged`表示原ACK，`commitOutcome`表示准确业务事实，`committed()`仅在CONFIRMED_COMMITTED时为true；CONFIRMED_NOT_APPLIED允许在全部原归还且已有READY终态后结束资源保管，但不称为ABORTED或SDK回滚。首错不清。

`HostOutput.originalTerminalStatus(task)`及Android authority的相同方法只读同原任务的原仲裁/原查询事实；默认UNKNOWN。SDK仅在QUERY确已进入、无待消费直接stage且所有同原任务已返时接纳READY/ABORTED。没有可靠权威事实则保管持续，不为keeper归0造证据。

这些accessor不拥有额外资源，没有新增释放计数或executor。宿主必须遵守相同task/token、无副作用、非阻塞、来源准确的临时契约；其真实性需后续真实集成验证。实际业务发布和平台路径仍NOT_RUN。

## 本批状态矩阵

九阶段×七结果共63项；详见 [结构化矩阵](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/phase-exception-matrix.json)。七列：ACK、EXEC、CANCEL、LATE_ACK、LATE_EXEC、LATE_CANCEL、THROW_CANCEL。每项分别验证原进入一次、稳定首错、原ACK、同原尾段与unknown authority门、最终准确归还。正常ACK及未准入pending首错为空；已进入失败/超时首错非空。WRITE的actual4/ACK下界/callerPos/UNKNOWN分别核对。

不适用项：仅WRITE有字节UNKNOWN reservation和callerPos，不给其他阶段伪造字节账；仅COMMIT有发布业务确认，其他阶段不伪造commit；REOPEN的读回子任务归还另由原registry检查覆盖；THROW_CANCEL没有异步stage，因此没有晚ACK或独立host异步尾段，保留准确原调用内抛错/UNKNOWN；真实Android FD/容器错误均NOT_RUN。

测试的Actual/Original就是执行该受控宿主动作的原线程，先真实执行body，再完成ACK并阻塞同一线程尾段，最终join该线程；authority查询也使用它所持同一原查询线程，没有替代worker证明。所有测试正常或异常清理路径均保留原对象并实际join，不能用JVM退出冒充资源归还。[生产原日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/evidence/suites-005/matrix.stdout)。
