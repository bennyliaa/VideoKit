# INPUT_SINK02 原操作状态与资源归还模型 V1.0

候选 D1-20261021-INPUT-SINK02。以下是临时离线候选约束，不是 M0 API 定版。

## 三条独立事实

1. 准入/调用事实：是否真正进入宿主原操作，决定一次性标记能否改变。
2. 业务 ACK：原 stage 的结果，例如 write ACK 字节、validation receipt、READY token、COMMIT ACK，必须按实际收到的事实保留。
3. 原任务真实返回：同一 host authority、validator/commit authority、reopen registry/workers、原 SinkCoordinator callback/thread 的归还资格，决定后继动作及 owner 释放。

ACK 早完成而同一原线程仍活着时，第2条成立、第3条不成立。write/read 的私有块、UNKNOWN 和预算不会因此退款。

## 直接原操作状态

| 状态 | 一次进入标记 | 允许行为 |
|---|---|---|
| NOT_ADMITTED | false | 等前序准确同原任务返回后，可以首次准入；不登记 firstFailure。 |
| INVOKING | true | 持有 owner；不能并发后继动作。 |
| ACK_PENDING | true | 保留同一原 future 和私有块；超时记录 firstFailure，不取消原任务、不重发。 |
| ACKED | true | 保存 ACK；仍必须等待同原 authority 证明物理返回。 |
| ACK_FAILED | true | 保存首错和 partial/UNKNOWN；不盲重试。 |
| INVOCATION_UNKNOWN | true | 调用抛错/返回非法 stage，不能断言未发生；保留首错、一次进入事实和原 authority，禁止盲重试。 |

FLUSH/CLOSE/REOPEN/VALIDATE/COMMIT 标记都在 requirePrevious 通过后、实际调用前改变。B01 write 尾段挡住 flush 时保持 NOT_ADMITTED；尾段 join 后 flush1、close1，不存在“flush0/close1且永久无错pending”。FLUSH已执行但尾段未返时 CLOSE 仍未准入；CLOSE早ACK未返时不二次 close。

firstFailure 只记录第一次业务失败/超时；瞬时前序原任务未归还拒绝不污染首错。取消是意图，不能抹掉 ACK 或伪造回滚。WRITE UNKNOWN reservation 每个实际原调用只登记一次，重复 observe 不加账；已知 ACK 下界、caller position、实际宿主写入、attempt/reservation分别表示。

## 阶段门与原证明

| 阶段 | 本候选保留的同原对象/证明 | 下一步/释放条件 |
|---|---|---|
| WRITE/FLUSH/CLOSE | host、原 pending stage、原 block；writerOriginalsReturned 和 host.originalOperationsReturned | 前序 pending 已观察、同原 writer/host任务真实返回；flush/close结果另验。 |
| REOPEN | 同一次 host stage、同一个 Provider；原 HostInputFactory/registry/workers | host尾段返回才读回；读回关闭并 originalsReturned 才进验证或释放。 |
| VALIDATE | 同一个 Validator 对象、原 receipt、Validator.originalOperationsReturned | receipt正确且全部原任务已返才 READY；独立 validator 不依赖 writer 的已返布尔值。 |
| READY | 同次原宿主 stage/token；缓存view仅转发原ACK；host原任务、coordinator原线程 | early/lateACK可成为业务READY；未返时无COMMIT、无完整owner返回。 |
| COMMIT | 显式同一 Commit 对象、原stage/ACK、Commit.originalOperationsReturned | 实际ACK保留为committed；原任务未返继续retained；ACK未知不释放且不伪回滚。 |
| ABORT/QUERY | 同次原host stage/view/query结果；host原任务、coordinator原callback线程 | ABORT尾段未返不进入QUERY；QUERY早ACK可确认业务终态但不返owner；已进入RPC不重复。 |
| 最终owner | 上述全部authority、读回原registry和实际coordinator线程join | writer已返、READY或ABORTED业务终态成立、已尝试COMMIT则必须ACK、所有原任务真返，再移除原OWNERS。 |

读取 proof 抛错、未知或false均保持未返。`HostOutput.Validator`、`HostOutput.Commit` 及 AndroidGrantedStream.Authority 必须实现非阻塞的同原任务证明，不能用“future完成”、新计数器或代替线程冒充。宿主诚实履行该契约仍需后续真实集成独立验证。

候选只复用既有 OWNERS、read registry、SinkCoordinator。缓存结果避免重新执行宿主副作用；公共修改调用的 CAS 防止两个调用并发穿过门，不作为归还证据。显式 COMMIT 前先 join 准备阶段原 coordinator callback/executor/thread；最终释放再核对并 join。join 前不再把 outstanding ACK 计数的瞬时减账当作真实返回或永久失败。

## 晚 ACK 与历史

超时后的同原 stage 继续保留；observeOriginal 可收回晚 ACK，firstFailure不清除。READY晚ACK保留 token；COMMIT晚ACK保留 committed=true，资源仍等同原尾段退出。调用发生 UNKNOWN 不被改写成 NOT_ADMITTED，不重复 flush/close/reopen/validate/COMMIT。已执行的 READY/ABORT/QUERY 只复用同次结果；某 QUERY 在 ABORT尾段未返前根本未发出，后续真实归还后才允许首次发出。

返回资格测试见 [逐阶段原始日志](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/return-003/run.stdout) 与 [结构化观察](D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/evidence/original-phase-observations.json)。测试里的 Job 是执行该实际受控宿主动作的原线程，完成ACK后在同一线程保留尾段；join 的也是该线程，没有另起替代线程证明归还。实际宿主业务和 Android 媒体效果仍 NOT_RUN。
