# D1 R2 源聚合租约契约方案 V1.0

2026-10-16。回应R1-R01。**负责人已定**：宿主权威归并物理源/版本，seal后不接纳新消费者或future open，实际归零才可物理事务，终态通知不计入产生该通知的资源条件。**本文件为待独立评审的协议细化**，未实现、未冻结公共API、未改C14；D1未通过，M0未启动。

依据：[负责人决定§3](D:/CodexProjects/VideoKit/docs/D1_R1_COORDINATOR_DECISIONS_V1.0.md)、[R1评审R01](D:/CodexProjects/VideoKit/docs/tester/D1_R1_REVIEW_REPORT_V1.0.md)、[原文§14.1–14.4/26.7](D:/CodexProjects/VideoKit/docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md:476)、[公共API§3/6](D:/CodexProjects/VideoKit/docs/PUBLIC_API_CONTRACT_V1.0.md)、[集成设计§2](D:/CodexProjects/VideoKit/docs/LOCALVIDEOBROWSER_INTEGRATION_V1.0.md:11)。现有[LeaseRegistry](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/LeaseRegistry.java)只给单任务资源计账；[RealFramePipeline.produce/sourceReleased](D:/CodexProjects/VideoKit/docs/coder/d1c14/android/com/videokit/spike/c14/RealFramePipeline.java)说明“目前句柄0”和“任务再也不open”不同，不宣称已有产品聚合实现。

## 1. 身份与权威

| 字段 | 精确定义/作用域/不可替代的身份 |
|---|---|
| authorityId / authorityEpoch | 宿主租约管理域及该域获权的恢复代次。权限来自宿主注入/broker认证，不来自知道字符串；重启不能用新epoch抹除旧未归还资源 |
| sourceLeaseId | 宿主对同一物理源访问组分配的不透明稳定标识，作用域authorityId；不是路径、URI、Browser数据库ID，也不是内容hash |
| sourceVersion | 宿主分配的不透明授权/源实例版本；内容变化、移动/重绑定、权限撤销后重新授权均产生新版本，即使字节相同。内容指纹另存，不能用同hash认定同物理文件 |
| mediaToken | 宿主供某会话/用途解析的opaque别名。宿主可将多个token映射同lease/version；Kit不猜文件等价、不比较路径。复制出的另一物理文件不因同内容自动共用租约 |
| consumerId | 对“可能再次open的整个任务/会话”分配的唯一预留身份，携purpose=probe/playback/edit/tracking/export，不等于当前句柄。任务开始前reserve，最后一次可能open被永久禁止且关联资源真实归还后结束 |
| bindingGeneration | consumer内单调递增的绑定代次；更换源或重新授权须新代，旧结果不能写入新代。旧代预留和资源独立保留至清空 |
| reservation | 宿主原子接纳的future-open额度/义务，绑定lease/version/consumer/generation及owner。即使handles=0仍计1；首轮每绑定最多1个整任务预留，可拥有多个受预算限制的短句柄 |
| operationId / handleId | operationId是owner在该绑定下唯一的open/read/close/数据回调操作键，重试同键不再调用provider；handleId是一次成功open的对象身份。它们均不代表新授权 |
| stateSequence / releaseSequence | authority对该lease/version串行状态变更的单调序号；releaseSequence是资源归零终态对应序号。单调指同一身份域，不比较不同版本的大小；溢出前退休身份，禁止回绕 |

完整请求键为`authorityId + sourceLeaseId + sourceVersion + consumerId + bindingGeneration + operationId`，另带owner认证。字段均opaque/有界；日志只记录随机ID、计数、阶段和稳定原因，不能借此传真实路径/凭据。宿主别名表先归并再reserve；已发出两个leaseId却后来发现同物理源，必须暂停两组授权并合并资源账本/排空，不能只合并字符串后漏掉旧引用。此异常由宿主resolver处理，不要求SDK扫描文件或读Browser数据库。

authorityEpoch写入认证头与每操作的originOwner记录，逻辑幂等键保持稳定；恢复owner可查旧操作，但旧owner不能用相同operationId重获授权。同键携不同参数/句柄/用途是协议冲突，拒绝而不重做provider副作用。终态记录若已安全归档，旧key至少仍返回退休/不可授权；信息不足返回UNKNOWN，不能以缓存过期声称当前源可移动。

## 2. 状态与并发线性化

每个lease/version有一个宿主权威串行器或等价事务。**所有授权接纳/拒绝在该点落账；provider/IPC/close和用户回调在锁外调用。** 接纳时先登记操作，调用返回后再确认实际完成；发送取消或返回超时不扣操作数。

| 操作 | 原子接纳条件/线性化点 | 锁外动作与最终处理 |
|---|---|---|
| reserve | 版本ACTIVE、别名解析仍指同版本、owner授权、预算足够；持久/可恢复账本写入reservation后才返回成功 | 若回复丢失，同请求键query取同一reservation，不再预留第二份 |
| open | ACTIVE且该reservation仍ACTIVE；先登记`OPEN_ADMITTED`与operationId，再调用factory | seal发生在接纳后仍须保留在途；晚返回句柄立刻纳入ledger并关闭，不交付给已撤销消费者。接纳前seal则根本不调用factory |
| read / 数据回调 | reservation未停止且版本ACTIVE，目标handle/generation匹配；先登记在途及缓冲所有权 | seal/取消后旧操作可物理返回，但不发布为新代成功；私有缓冲待真实完成才复用。保留实际读取量和关闭事实 |
| seal | ACTIVE→SEALED_DRAINING，与reserve/open/read接纳共用同一原子点；记录sealSequence和该版本全部已接纳reservation/操作 | 阻止其后新增数据操作/消费者，通知所有已接纳owner停止future-open并取消；close、query、资源完成回报始终允许，不能因seal拒绝清理 |
| finish consumer | 先停止该reservation新数据接纳，owner确认不再future-open；其所有已接纳操作、handle、source依赖回调、相关native资源实际归零 | 记录CONSUMER_RELEASED并结束reservation。消费者不能靠“目前没句柄”完成；输出任务需先完成源依赖/输出清理与验证收尾，终态通知发送不成为资源条件 |
| 全源归零 | SEALED_DRAINING且下述R向量全零、无未知owner/失败close | 原子转DRAINED，记releaseSequence。宿主内部排队物理事务在同一权威下独占该版本；这不是Kit文件移动API |

R向量为`reservations + openInFlight + readInFlight + closeInFlight + liveHandles + sourceDataCallbacks + retainedSourceNativeRefs + failedCloses + unknownOwners`，各项分别报告，不能相互抵销。复制完成且已脱离源访问的独立裸帧有自己的帧账本，不能借它“释放”仍会future-open的源预留。首轮导出在全部输入/输出收尾的READY_ELIGIBLE点结束源预留，然后请求READY，避免“等READY才能归还、READY又等归还”的循环；全源DRAINED不作为导出READY必要条件，因为其他独立播放消费者可能仍在读。

版本状态：`ACTIVE → SEALED_DRAINING → DRAINED → HOST_TRANSACTION → RETIRED`。有未证资源时附带PENDING/RECOVERY_UNCERTAIN，不自动前进。seal不可撤销为ACTIVE；宿主放弃移动但想重新使用，也须新授权版本/代次。只有宿主内部事务能执行移动/改名/索引，Kit只交资源证明。旧版的DRAINED快照不能直接授权现版本事务；宿主须原子核对lease/version/releaseSequence并占有HOST_TRANSACTION，且该版本不能再reserve。

consumer状态为`RESERVED_ACTIVE → QUIESCING → RELEASED`；是否已经open由handle计数描述，不另开一个可漏账身份。QUIESCING含PENDING/close失败子状态，不可重新ACTIVE；换绑定建立新代，旧代仍独立排空。预留落账或seal持久结果未知时query同键并保持围栏，不能按“没收到成功”认定未接纳。

## 3. 查询、通知、失败与恢复

| 情况 | 唯一允许的协议行为 |
|---|---|
| Session SourceReleased | 携带lease/version/consumer/generation/releaseSequence，仅证明该消费者已清空。宿主不能据一个事件就移动；其他consumer与整任务预留由宿主聚合 |
| 最终释放通知本身 | 是终态控制事件，不是R中的数据回调。持久终态先成立，再发通知；通知超时/丢失不倒退终态，也不重开输入。队列仍有独立有界投递预算 |
| query | 按完整身份认证返回状态、seq、sealSequence、R各计数、失败close/owner摘要和是否终态；返回同版本快照。旧版本返回其墓碑/终态，不把它解释为现版本；无法恢复返回UNKNOWN/PENDING，绝不猜“0引用” |
| 已接纳open回复丢失 | 同operationId查询PENDING/原handle；不能发新operationId绕过未知结果。取消后晚句柄进入close账本，消费者未获句柄不代表它未创建 |
| close失败 | 保留handle/失败计数，显式恢复：首次＋至多2次重试、不可重叠。每次获权重试有新operationId/closeAttempt，关联同handle/baseCloseId；同attempt命令重放只查原操作，不再次调用close。再失败标EXHAUSTED/PENDING，不无限新建池或复用资源 |
| 源换版/别名改绑 | 旧版先seal，已有资源不转记新版本；新版本只能由宿主明确授权。旧token/Provider/回调不能自动解析新路径、清空新代计数或发当前版本可移动许可 |
| consumer/worker死亡 | 仅匹配原owner实例/task/generation的真实死亡能关闭其进程私有引用；宿主broker句柄、未返回provider调用和其他进程dup仍须分别归还。PID重用、unbind/超时/进程名近似不算死亡证明 |
| authority宿主重启 | 先获恢复所有权，载入seal/预留/操作/源版本日志；新epoch只围栏旧命令，不销毁旧资源事实。核对存活worker与broker资源；无法重建的引用计UNKNOWN，版本保持不可移动。没有旧数据≠证明从未创建 |
| 恢复日志不可用/身份不全 | 不自动沿路径重开，不宣称DRAINED；由宿主恢复流程/人工处置保留BLOCKED。SDK不获得删除/移动权限 |

query是无数据授权副作用的控制观察：每次新观察有queryRequestId并携同一租约身份/lastStateSequence；同queryRequestId可重放同快照，获取新状态用新queryRequestId，不是新consumer/新open。迟到的较小seq不能倒退本地状态；任何查询快照都不能代替宿主内部物理事务的原子获权。

读失败/取消的公共码候选使用原文现有码：拒绝已退休绑定为`SESSION_RELEASED`（stage=SOURCE_ADMISSION，reason=LEASE_SEALED/STALE_GENERATION）；无授权为`SOURCE_PERMISSION_DENIED`；超时为`SOURCE_TIMEOUT`且资源状态可仍PENDING；非零读0进展/提前EOF见provider方案。可靠宿主换版证据才提出新增`SOURCE_CHANGED`，它是待评审码；没有版本证据不能凭短读宣称改变。控制命令seal/query成功返回状态，不用“0引用”或新的错误码代替状态机。

## 4. 至少八个可复核反例（设计，均未运行）

| ID / 初态 | 并发顺序 | 唯一允许终态/必须保留的证据 |
|---|---|---|
| S01 两token A/B→同L/v，P播放与E编辑各预留，E句柄0 | P关闭→收到P释放；E将来才open | L仍ACTIVE、E预留1、不得全源移动。E的open可在未seal前接纳；不能因handles0给移动许可 |
| S02 S01后宿主seal，E未open | seal落账→E尝试open→E处理取消并结束预留 | 新open为SESSION_RELEASED且factory调用0；E真实结束前PENDING，结束后DRAINED；不同token没有独立漏账 |
| S03 open已接纳但factory晚返回 | 登记OPEN_ADMITTED→seal→caller取消→factory返回H | seal后H只进入关闭路径；H实际close/在途回报清空前不可DRAINED。无句柄交付不等未创建 |
| S04 seal与reserve竞争 | 分支a reserve先落账；分支b seal先落账 | a：预留必须进入seal快照并排空；b：reserve拒绝且不调用provider。只能由原子顺序二选一，不出现成功预留漏在seal之外 |
| S05 v1已DRAINED/事务完成，v2 ACTIVE | v1终态通知丢失后迟到；随后v1旧open | v1通知只更新v1查询记录；v2保持原状态/计数，旧open拒绝，不得到v2可移动许可、不沿新位置重连 |
| S06 read取消但provider仍写私有缓冲 | read接纳→取消响应→close尝试成功→read才返回 | close成功不扣未完成read；缓冲不复用，SourceReleased只能在read真正返回及数据回调排空后成立 |
| S07 close失败/重复恢复 | 初次close失败→两次同时retry请求→实际第二次close成功 | 同一时刻仅一个close attempt，重复请求附着/返回IN_FLIGHT控制状态；成功证据清除失败项，最多3次，未成功不可归零 |
| S08 worker死亡但宿主provider在途 | 真实worker death→owner恢复→provider尚未返回 | worker引用可归还，provider项仍PENDING；新authorityEpoch不能清账。返回并清理后才DRAINED |
| S09 SourceReleased通知永不到达 | 持久CONSUMER_RELEASED→丢通知→宿主query同身份 | query得到同releaseSequence与真实终态；不会重新open，不因等通知造成资源释放死锁 |
| S10 宿主发现两个leaseId指同源 | 两组都有引用→归并请求 | 两组先围栏新授权、联合排空；缺任一旧组即不可移动。不能只在别名表重指向新L就忘旧ledger |

后续实现前须独立评审上述原子点、可恢复日志及错误码，受控本机case使用[provider计划](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md)。这些是通用宿主资源语义，未引Browser类型、实际源路径或SDK物理移动方法，也未把现有单任务账本改称全源聚合。
