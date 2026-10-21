# MEDIA3 CONTAINER02 检查准入和原返回顺序 V1.0

2026-10-21。对应独立问题MC-B01/P2；仅本次有限修复，非M0公共API或容器功能通过。

原问题发生在真实检查开始前：第一次REOPEN已正常给出Provider，但原任务线程尾段仍活着，requirePrevious返回OUTPUT_ORIGINAL_PENDING。旧入口却提前设置hostInspectionAttempted，并把这个等待写成首错。原任务后来实际返回，也无法开始尚未执行的检查。

## 准入和真实失败

只修改TemporaryOutput。新inspectionReadProvider供主机结构检查和既有verifyAndValidate共用；它保留原reopenAttempted、同一个应答及Provider。第一次实际REOPEN失败/超时仍由原call/consumeOriginal记首错，不清除任何既有失败。重入只观察既有结果，不第二次reopen、替换任务或重发RPC。

主机检查先核能力、writer及原返回。只有拿到同一Provider、前序原任务/observer真实返回且HostInputFactory成功获得原源资格后，才设置hostInspectionAttempted。前置等待或尚未分配源的额度拒绝不会耗掉实际检查资格；实际平台构造、解析、摘要或检查失败继续保留首错，不能重新执行。

| 阶段 | 暂待和继续规则 |
|---|---|
| 原REOPEN尚未被调用 | 原准入条件不足则拒绝，不产生新RPC |
| ACK已到、同原线程或真实whenComplete observer未返 | 稳定OUTPUT_ORIGINAL_PENDING，firstFailure不因该等待改变；保留同一Provider |
| 原线程先返、ACK后到 | 原同步调用在既有期限内等同一ACK；真实超时仍OUTPUT_TIMEOUT_PENDING |
| 同原任务及observer都返 | 复用原Provider继续第一次尚未开始的检查，REOPEN仍恰1次 |
| 同Provider尚被原源能力占用 | 既有HostInputFactory拒绝；未open，不创建替代Provider，不消耗检查资格；原能力归还后可继续 |
| 真正超时、取消、权限、坏应答或invocation UNKNOWN | 保留原失败/取消/UNKNOWN，不因迟到正常ACK或线程归还而恢复 |
| 实际检查已开始并失败 | 单次策略；保留首错，后续检查/验证拒绝，不换库或循环解析 |
| 实际检查成功、只待原归还 | 私有缓存只保留同次结果；原返回及取消门仍须通过，只允许读取同容器种类的同一结果，不再次解析。真实成功/缓存路径目前NOT_RUN |

共享入口还核对原scoped observer及coordinator实际response observer返回，不以isDone、计数0或ACK替代原返回。原registry、原worker和最终owner归还模型未改变；没有新增执行器、资源账本或平台替身。

## 集中实际顺序证据

ContainerPendingOrderCheck以真实线程、门闩、CompletableFuture与真实whenComplete返回阶段构造22项检查：3种正常顺序×2个初次入口×2个继续入口=12项；再加2个真实超时、cancel、abort、原应答cancel、权限拒绝、调用UNKNOWN、null stage、坏值、null Provider共10项。每项最终join同一原caller/worker，核同一observer返回和source/output keeper0。

正常继续前没有cancel/abort。等待阶段跨两个入口再次调用仍暂待、首错null且REOPEN1次。原任务归还后，仅用一个额外、未打开的源能力登记**同一个Provider对象**，且全局第二个源槽仍空闲；再次检查被原HostInputFactory的重复Provider规则拒绝。该证据证明复用确切授权对象，而非只是RPC次数相同。这个源能力实际归还后，继续主机入口只执行一次检查，抵达真实Media3的平台缺类失败边界；继续既有验证入口则真实读取4B全EOF/hash并抵达明确拒绝的受控validator。4B刻意不是媒体，未签发隔离验证结果。

原独立输入另原样保存在reference/IndependentContainerBoundaryCheck-original.java；ContainerB01Regression只更换类名、归属文字及修复后的预期，保留原未cancel/abort干扰复现和真实超时对照等输入。两条路径各8个边界用例通过；这是coder重放，非新独立结论。

实际已证明的是准入恢复、相同授权对象和失败边界，没有证明真实MP4结构正例。普通/fMP4提取、合法六样本、实际mux/remux、坏atom内部内存界、NAL/时基/EOS结束时间，以及真实结构成功/缓存结果、平台解析过程中的权限变化均仍OPEN/NOT_RUN。已有结构类型不会因本修复设置validated、READY或COMMIT。
