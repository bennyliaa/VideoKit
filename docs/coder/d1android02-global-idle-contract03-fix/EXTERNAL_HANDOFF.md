# 最小外部交接静态方案（当前 NOT_RUN / NOT_PROVEN）

选择一条路径：执行前由负责人批准一个**专用、独立、单次的本地签发进程**，在 Gate.prepare 之前已就绪；它只签本次只读 facts authority/approval，不签服务例外、不签后续七角色许可。原 Gate/claim 对象一直留在原采集 Owner 内，不跨进程搬运。此方案尚未实现，不是现有程序已获授权的功能。

目前 collect API 已能接收准确 authority/approval 及两个外部 hash，但 routeProofSha256 在 Gate.prepare 后才存在；接收仍受原 proof10s/gate30s。人工通过聊天在此窗口内来回批准不能作为可靠流程，同调用者生成 issuer 字符串、JSON 和 hash 也不能充当独立批准。当前本地 fixture 只证明对象所有权与归还，不证明真实外部批准往返。

## 执行前，时钟尚未开始

负责人审核并冻结：本候选 source/gate/plan/collector、精确单次只读 argv、scope/planId/nonce、宿主身份与七个 ENV 覆盖项缺席、SDK/预算、独立签发者程序/来源/配置/公钥、IPC 输入输出上限及原返回机制。facts 的 authority/approval schemas 不变；签发者返回一个额外的 detached signed envelope，覆盖这两份原始字节的 SHA、nonce、scope、source/gate/plan、route/proof hash、有效期及专用用途。

采集调用者不能访问签发私钥；签发者必须由独立身份/ACL 托管，不能只在同调用者可写文件里放 issuer 名字或密钥。签发者及其原管理者在 Gate.prepare **之前**启动/校验/进入一次性等待，不能把启动和人工确认挤进 proof10s。固定采集 Owner 仅在验证预批准公钥签名、用途、scope/nonce/source/time 后，将原 authority/approval 的准确外部双 hash 交给现有 collector；不能自算两个值便代替验证外部来源。

## Gate.prepare 之后的一个有界交接

1. 原 Owner 持有同一 GateSession/claim，原 checker、writer/reader/wait/handle 已实际返回；取得该次准确 route proof 和初 proof，不发布为通用授权。
2. 通过预先建立的固定 IPC 发送 <=8192B 的本次原 proof/route 摘要及必要原回执；独立签发者只处理这个预批准 nonce 一次，核预批准来源、用途、scope 和原回执关系，产生 <=8192B 的 authority/approval 原字节与 detached signature，不增查设备或 Native route。
3. 原 Owner 收原响应，核来源签名与严格双 hash，在原 proof 起点+10s 及 gate 起点+30s之前调用同原 Gate.receive/collect；为本地核验/接收保留至少1s。任一时钟、数据、签名、原返回或 ENV 不符即拒，绝不切备用签发者、改 route、补查或重试原 nonce。
4. 若 IPC 的原读写尚未返回，保留其准确原对象及 Gate，停止后继，不 kill/二close/补ACK。已知拒绝且所有原 IO 已归还，原 Owner 唯一关闭自身资源、唯一释放同 claim；过期响应不能恢复资格。签名仅是独立授权来源证明，不代替原 checker/collector/外部 Owner 的实际返回。

## facts 到 target：最多300秒，不承诺在原最大值之和内必然成功

收集时刻 Tc 在七项查询之前。采集成功仍须 SDK<=15s、原 proof<=10s、outer<=30s/whole<=90s；实际外部 Owner 返回并保存原 raw/receipt/return 证据后，负责人核系统来源、HOME/component/UID/user/固件及**精确非竞争用途策略**，再批准一个明确 targetScope/runId/source/plan/review 的资格与七角色许可。系统清单或签发 facts 不自动批准服务；新事实不自动复用于别的 target。

可操作安排：身份/来源/政策证据和目标 scope/源/plan 在采集前已准备审阅；原 facts 归还后只核实际观察与这些准确条件及原返回，建议 Tc+150s 前完成审阅并启动 target。每次交接使用原始 Tc/expiry，打印实际剩余时间。target 原 gate<=30s，但每个控制器原 outer 上限120s，因此不能把“150+30+15+15”误写成保证；实际启动/返回延迟也会消耗新鲜期。

固定未来执行入口应再施加更紧的**剩余资格**截止（不扩大任何原预算）：事实过期或剩余不足保守预留时，不启动 target/下一SDK；global_idle 的实际语义接收及其后继重核也必须在 Tc+300s前。未能在有效期内取得完整原结果，保持未证并等原返回，不补签、不回填旧 scope。若之后另需新事实，只能由负责人另批全新 scope/once，不是自动 retry。

## 必须由负责人审定的信任契约变化

- 是否批准独立一次性签发入口、公钥/独立密钥托管、固定 IPC、唯一 nonce 及所有原返回/预算；其签名验证入口必须先实现、独立审测，现有 issuer 字符串不等效。
- 是否批准一个固定专用调用入口作为上述签名验证及“剩余新鲜期”附加准入的可信执行者；只服务该次只读 facts 和准确 target，不是通用调度框架。
- facts→target 的人工审阅或预审条件边界，以及无法在300s内完成时拒绝的流程；本批不提前批准任何真实系统服务策略。

本批只交静态方案。没有实现/运行签发者、密钥、IPC、外部跨会话交接或现场采集；没有生成 LIVE authority/approval；proof10s/gate30s/300s不扩。完成本候选独立B后仍须负责人明确选择是否批准并派发上述最小入口实现/验证，不能把本方案当作执行许可。
