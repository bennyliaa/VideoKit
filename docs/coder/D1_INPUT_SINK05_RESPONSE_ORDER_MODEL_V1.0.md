# INPUT_SINK05 原响应与不可逆终态顺序模型 V1.0

候选D1-20261021-INPUT-SINK05；仅有限离线候选约束，不是M0协议定版或全状态证明。

## 事实、采纳与归还

| 层次 | 本批保留的准确原对象/事实 | 不等同于 |
|---|---|---|
| 宿主原调用 | 同一task、原host对象、原RPC进入事实、原host工作返回证明 | 原response ACK已经交付。 |
| 原response | 同一个CompletionStage及传输终局；raw received/succeeded/私下原token | 其内容合法、与已确认终态兼容或可以释放。 |
| 原响应采纳 | shared acceptTerminal下的ready/aborted/token、raw accepted/rejection | 删除被拒响应、推翻已发生动作、清除首错或UNKNOWN。 |
| 原SDK观察回调 | 原whenComplete真实返回stage，原coordinator call/result/observer引用 | 代理view完成或outstanding计数0。 |
| 原物理任务/线程 | 原host/validator/commit/readback证明，原SDK executor终止及原worker实际join | 仅future终局或线程池计数。 |
| owner返回 | 上述全部资格、正确终态及既有COMMIT结果门满足后移除原OWNERS | 原ACK到达、终态先确认或异常被catch。 |

外部完成response的线程可能是持续存活的客户端/事件循环。该线程在observer返回后继续存活并不表示SDK任务仍在途。若它还拥有原host工作尾段，原authority必须保持未返；SDK自己创建的原coordinator线程则必须真实退出/join。测试区分这两种情况，不以无关线程替代证明。

## 统一不可逆采纳

TemporaryOutput首次/晚READY原回调、等待结果、原QUERY、readonly原仲裁及派生coordinator结果都进同一个同步函数；coordinator自身也在其已有state/token中使用同一私有转换函数，禁止分支直接覆盖终态。

| 已确认 | 可采纳新事实 | 拒绝/保留 |
|---|---|---|
| 尚无终态 | 合法READY/token，准确ABORTED/null | null/type/非法组合失败，不猜终态。 |
| READY/token T | READY且同T；UNKNOWN只是不新增证明 | ABORTED、不同T、倒退WRITING拒绝；不清旧READY。 |
| ABORTED | ABORTED；UNKNOWN只是不新增证明 | READY即使token形状合法也拒绝；不把已确认ABORTED覆盖成READY。 |

原response成功传输但因冲突拒绝时，`readyResponseReceived=true`、`readyResponseSucceeded=true`、`readyResponseAccepted=false`，拒绝原因例如CONFLICT_WITH_ABORTED/TOKEN_CHANGED。readyPhase为ACK_REJECTED，原CF和私下token仍保留；原首错继续是最早错误。原失败/取消到达则记录received、succeeded=false、ORIGINAL_ACK_FAILED，不能从失败推断宿主未发生READY。

已有冲突/UNKNOWN只能由准确兼容的原QUERY或readonly原仲裁收敛。匹配的迟到ACK、等待返回或派生缓存结果都不能单独擦掉另一来源的冲突。拒绝原因保留，首错/写UNKNOWN不清，不重RPC“纠正”。readonly不发RPC，已有原READY/ABORT/QUERY仲裁可提供相同原task事实；缺证明仍保管。

两个互相矛盾的宿主声明不能同时当准确事实。有限测试覆盖谁先到及应拒的后到来源；若宿主持续不合约、无准确兼容事实，本候选必须继续持有，不能为了keeper0反射改状态或虚构业务回滚。本批不证明恶意CompletionStage/observer实现、真实持久化账本或跨进程业务。

## 原stage、observer、executor/thread返回门

1. READY/ABORT/QUERY的原stage和本次真实whenComplete返回stage分别保留。代理view用于同原结果转发，不作物理返回证明。public observe不把尚未回答的原response报告为全部已观察。
2. 原response尚pending时，完整finish返回稳定OUTPUT_ORIGINAL_PENDING；不关闭仍需原response的executor，不cancel，不发新RPC。ABORT/QUERY原仲裁可以在原READY ACK未到但host原工作已返时合法执行，业务事实与资源返回分开。
3. 结果已回答、observer仍在真实尾段时，按配置有限等待；未返继续稳定pending。正常微小时序窗口也等同一原回调，不用替代worker补证。
4. coordinator在原八项上界内保留准确call/result/observer引用，只有同原observer已完成才剪除；既有原Thread引用仍保留。outstanding用于既有容量/状态防护，不作为正向归还证据。
5. 全部结果与observer资格满足后，原executor实际终止、每个准确原worker join；join自身/未就绪为稳定pending，不抛内部unchecked异常。最终还要重新核原host/registry和全部响应资格，再移除owner。

原firstFailure与取消意图不改变这些物理门。COMMIT业务ACK/readonly三态、原任务返回及先前READY/token仍分开；首错、partial ACK、UNKNOWN reservation按原规则一次登记、不退款。

## 有限关键顺序矩阵

| 类别 | 实际安排 | 验证重点 |
|---|---|---|
| QUERY先，原READY ACK后 | 准确ABORTED或READY先确认，后同token/不同token/失败/取消 | B06拒矛盾晚READY；B07原响应未到稳定pending，合法同token后收敛。 |
| ACK先于QUERY response | 原QUERY已进入但响应在途，READY原ACK先到 | 后到坏ABORTED/不同token不覆盖已采纳READY；准确兼容authority后收敛。 |
| ABORT ACK在途 | 原ABORT已发生但ACK保留，原READY成功或失败先到 | 尚在途stage继续持有；需要时只首次进入原QUERY，不重ABORT。 |
| readonly仲裁先 | 原READY/ABORT事实准确先提供，原ACK稍后 | 业务事实可先采纳；原response/observer未返不释放；坏晚ACK不擦事实。 |
| 坏readonly先于晚ACK | 已确认终态，后到矛盾authority，再到成功/失败/取消ACK | 匹配ACK也不能抹掉已有冲突；准确原authority后才解未决。 |
| 原observer尾段 | 同一whenComplete已执行SDK动作，但其真实返回stage仍由有限gate保留 | 原response可能done、host工作可能已返，仍不能完整返回。 |
| 原coordinator worker尾段 | ACK可能早完成，但注册/observer真实方法仍在该原worker | 稳定pending；放gate后join同一原worker。 |
| host物理尾段 | ACK和SDK观察已完成，但实际host delivery任务仍未退出 | 原authority保持false，join该原线程后才返回。 |
| coordinator计数0尾段 | 原f已完成、outstanding0，但实际原observer/worker还被gate保留 | 计数0仍不合格，实际原observer与worker返回后才通过。 |

[30项owner顺序和67条状态观察](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/response-order-matrix.json)、[生产顺序原日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/suites-005/orders.stdout)、[7项coordinator原日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink05/evidence/suites-005/coordinator-orders.stdout)。源码/JAR双路径是重复加载验证，不增加场景数；其与旧套件有重叠，不相加冒充完整协议证明。

生产仍仅已有owner/registry/coordinator；无新executor、状态平台、验证ledger或宿主协议字段。Status、CommitOutcome和Provider/Handle缺失的身份/物理FD字段不凭空扩展。真实Android平台、媒体容器与宿主业务发布NOT_RUN，D1未过、M0未启。
