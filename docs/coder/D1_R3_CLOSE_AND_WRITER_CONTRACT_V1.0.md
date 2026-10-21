# D1 R3 close disposition与writer交付契约 V1.0

2026-10-16。回应R2-R01/R02；仅设计，待独立评审。依据[R3正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_R3_CODER_REQUIREMENTS_V1.0.md)、[R2独立报告§4](D:/CodexProjects/VideoKit/docs/tester/D1_R2_REVIEW_REPORT_V1.0.md)。不改R2五份原件、R1或C14，不实现/实验/构建/ADB，D1未通过、M0未启动。

覆盖关系：本文件§1–3**替代R2源契约§3的统一close重试规则及S07、provider P10的未展开部分**；§4–6**替代R2输出§3/O06/错误表“缓存结果”中可能重送可写对象的解释，以及Q09重放部分**。R2的源身份/seal、Sink能力、READY/abort/COMMIT、历史FAIL及宿主JNI BLOCKED其余约束保持。新协议尚未冻结公共API。

## 1. 稳定对象与关闭ticket

不能把裸fd/HANDLE整数或wrapper.closed布尔当作对象身份/释放证明。每次真实资源分配先登记`resourceObjectId`（allocation nonce＋owner进程实例/代次），每份descriptor另有descriptorId；dup共享backing object，但有不同descriptorId/resourceObjectId。所有拥有权的wrapper只能指向一个受控能力单元，禁止两份wrapper独立拥有同一个裸数值。

`closeTicketId`固定绑定该resourceObjectId、唯一关闭权威和baseCloseId，保存revision、attemptId/operationId、delegate是否进入/返回的事实、disposition、实际释放证明、首错和独立cleanup。强引用保留到有证明的终态；数字复用或缓存淘汰不生成新关闭资格。每层adapter只证明其拥有的那份资源，stream关闭不替代其他dup/同步FD/transport引用。

| disposition | 需要的证据 | 允许下一步 |
|---|---|---|
| OWNED_OPEN_RETRYABLE | 确定delegate未执行，或backend明确保证失败无关闭副作用；原稳定对象仍由该ticket独占、无其他close在途且可安全再执行。普通“fd仍valid”探测/closed=false不够 | 显式新attempt，仍受次数/revision门禁；不是收到任意异常就可重试 |
| CLOSED_PROVEN | exact对象的底层关闭实际成功事实已在可信owner处记录，或等价独立释放证明；上层ACK/日志投递可失败 | 仅query/确认原完成结果，绝不再close。原错误保留，不将ACK补齐说成第二次底层close成功 |
| CLOSE_IN_FLIGHT | 已获权关闭操作尚未实际完成，包括delegate返回后必要的资源交接尚未可核 | PENDING；相同请求附着原ticket，不启动第二次close |
| CLOSE_UNKNOWN | delegate可能执行/部分执行、返回错误不能判断对象是否归还，或分层记录冲突 | PENDING/quarantine；禁止新attempt、禁止以新opId绕过。只能接受精确ticket的后续完成证据，或原owner进程死亡后逐引用核对 |
| RELEASED_BY_OWNER_EXIT | 原owner实例确证死亡，且该descriptor只归它持有，其他dup/host/transport引用另外清空 | 可回收该引用；原close结果仍可UNKNOWN，不改写成close调用成功。不能用PID重用/线程结束替代进程实例死亡 |

底层已关闭但应答丢失时，调用方可暂见UNKNOWN；backend若保有匹配ticket的完成记录，查询可升级为CLOSED_PROVEN。若只有一个先置closed布尔，不能升级。UNKNOWN也不能靠盲目再次调用可能已复用的整数“探测”归还。

## 2. 安全重试、并发与分层责任

`retryClose(ticketId, requestId, expectedRevision)`在关闭权威的串行点判断：disposition=OWNED_OPEN_RETRYABLE、owner仍有同一对象、无in-flight、attempts<3、revision匹配；成功先登记新attempt/operationId，再锁外调用delegate。首次算attempt1，即使故障在delegate前；最多再两次获权安全尝试，不能借“未执行”无限重排。

同requestId重放只返回原ticket/结果元数据；不同requestId并发仅一个能从该revision获权，另一个返回IN_FLIGHT或STALE_REVISION状态，不能排队在前一attempt结束后偷偷开始下一次。再次尝试必须基于新查询和新expectedRevision。达到3次仍失败为EXHAUSTED/PENDING，若对象仍拥有也不授第四次；最终处置另审。

| 层 | 必须负责的事实 | 不得代替的事实 |
|---|---|---|
| resource backend | 分配的稳定对象、实际native/OS close进入/结果、backend错误的副作用保证与ticket记录 | 不以异常名称或OS数值仍可访问就断定仍是原对象 |
| Java/.NET/平台wrapper | 单关闭权、强引用、wrapper到descriptor映射、返回的disposition/完成证明 | 不因wrapper.closed=true或Dispose已调用就向上报告已释放 |
| IO/IPC adapter | 请求接纳、传输/回包是否已知、同ticket查询和未证引用 | 不把“应答丢失”映射为“delegate未执行”，不复制新ticket重试 |
| 聚合租约/Sink owner | 逐ticket汇总，终态通知与真实资源向量分开，保留首错 | 不以子进程死/单FD关/新epoch清除其他层在途和dup |

冻结[HostFixtures.FileHandle.closeAsync](D:/CodexProjects/VideoKit/docs/coder/d1c14/src/com/videokit/spike/c14/HostFixtures.java)先置closed再file.close；若异常后再次调用可能跳过delegate。这里只保留静态差距，未发生过的IOException不伪装实测；C14不修改。后续有限adapter必须按上述ticket证明，不允许用该布尔作为重试成功判据。F03四次仅属于已定encoder协商，不授任何close/普通API四次重试。

## 3. close反例与唯一允许结果（设计）

| 序列 | 必须断言 |
|---|---|
| C1 delegate前故障，原对象独占仍开；两个retry同时带同revision | attempt1/delegate0；仅一个attempt2获权且实际close一次；另一个不可在attempt2结束后自动成为attempt3 |
| C2 底层实际关完并记ticket，随后ACK丢失；并发retry/query | delegate总调用1、释放证明同objectId；只有确认，不再close；新分配且恰好同裸数值的另一对象不能受影响 |
| C3 delegate进入、结果未知；不同opId/新owner请求retry | disposition UNKNOWN、attempts不增加、底层close不重入；保持PENDING；新epoch不使原对象“恢复为OPEN” |
| C4 closed布尔为true但无底层证据 | 不可报CLOSED_PROVEN；query仍UNKNOWN/PENDING，任何成功返回值不能单独抹除原失败 |
| C5 第2次安全尝试仍确定未执行，显式第3次；再来第4次 | 第3次仍须新revision门禁；第4次拒绝，即使delegate实际调用少于3也不放行 |
| C6 UNKNOWN最终由原测试owner进程退出收敛 | 观察窗口保持PENDING；仅在匹配进程实例死亡及所有其他引用归还后记RELEASED_BY_OWNER_EXIT。原close UNKNOWN/首错不改为成功 |

首轮manifest的P10-A/B/C分别对应C1、C2、C3/C4/C6；次数耗尽C5由P10-D“预delegate安全拒绝至上限”分支独立展开。不是只测delegate前失败就声称三类结果都覆盖。

## 4. writer grant、交付和认领状态

原`exportId/intentDigest/handleId/ownerEpoch/attemptGeneration`绑定保持。新增`grantId`（一次授权）、`deliveryId`（一次传递尝试）、`receiverInstanceId`（唯一进程实例＋接收端点/能力单元）及`claimId`。同owner名不等同一接收单元；第二调用者不能以同command取得第二个owning wrapper。

**候选协议改变**：首次openTemporary也只返回不可写grant/handle/状态元数据；实际writer能力经独立的一次交付驱动和受控认领取得。公共三方法/WriteHandle如何承载该内部协议仍需API评审；本文件不修改其签名。任何缓存或重放的open/claim/query响应都不含FD、stream或可重复take的对象。

| 状态 | 原子记录与真实资源 | 重放/失败出口 |
|---|---|---|
| GRANT_RECORDED | 意图/receiver/delivery/attempt绑定持久化；writer预算保留，尚可无目标/FD | 同command只元数据；不同意图/receiver拒绝，不产生副作用 |
| ALLOCATING / PREPARED | descriptor分配操作先登记；真实目标原FD A、若需要则一次dup B各有ticket。分配未返回也有未知槽位 | 创建/dup结果未知不重做；已知分配要逐份清理，不能以grant=1推导ref=1 |
| SEND_STARTED | 先落账该delivery已耗用唯一send资格，再在锁外发能力；不得因回包未知重发 | 首轮send最多1；发送前失败且能证明未调用也不自动重授，按query/fence/abort处理 |
| DELIVERED_UNCLAIMED | 接收driver确认具体descriptor已安装/取得，绑定唯一receiver和一次take能力单元；尚不得写 | 同delivery重复回调只metadata或由driver关闭额外异常引用并保留账本；不能交给第二wrapper |
| CLAIMED | 已认证receiver以claimId报告同descriptor的拥有权；authority持久认领记录，返回不可写的认领确认；receiver原对象仅在确认后开始写 | 确认丢失/发送或认领不确定时，首轮转abort-only；查询即使发现曾CLAIMED也不重新发能力或恢复写入 |
| QUIESCING / CLOSE_PENDING | 围栏新写/交付/认领，排空已接纳write和每份close ticket | epoch变更只拒旧控制，不关FD；UNKNOWN仍保留预算，不能提前验证 |
| CLOSED / ABORTED | 全部写descriptor、wrapper、transport/在途已证归还，按Sink仲裁持久终态 | 原目标唯一；READY条件仍包括验证/lease/输入收尾，close不自动READY |

实际receiver driver的`takeOnce(deliveryId)`只能一次把同一对象放入单一owning capability cell；其后的同command/claim重放只拿元数据，不能重新take。write授权依据receiver已持有的原对象＋当前claim/epoch，不依据可重放字符串。authority提交CLAIMED与receiver获确认是两个事实，无需无限ACK握手：前者持久可查，后者不确定即receiver停止写并请求abort；首轮不通过“再传一次”补确认。

## 5. 每份descriptor账本与计数

账本逐项记录descriptorId/resourceObjectId、backingHandleId、创建op、parentDescriptorId（dup）、当前owner/location、inFlight、closeTicket及释放证明。已知存活数与未决传输上界分列；不能把未知槽位计0。真实dupCreated、sendInvoked、receiverInstalled、takeSucceeded、claimCommitted与每份close进入次数单独记录。

首轮Windows同进程受控mailbox profile：真实A＋一次DuplicateHandle得到B，**dupCreated≤1、sendInvoked≤1、takeSucceeded≤1、每对象owning cell=1**；mailbox交接同一B不再OS dup，已知native引用峰值2（若另有sync/guard须另外逐项计数）。owner身份退休只是模型注入，不能称进程死亡；真实A/B仍由harness ticket归还。若transport会自动再dup，必须先声明并验证额外槽位/安装/清理规则；Android Binder/跨进程profile未准入，不沿用“峰值2”当证明。

同命令并发N次的验收不是writerLease=1，而是：一个grant/目标、一次实际分配/dup/发送/认领、N−1份不可写响应、无第二owning wrapper，最终每份原/dup/异常传输引用均实际归还。未确认安装时可能引用区间而非精确数，保持PENDING，不写假精确0。

## 6. 创建至关闭各窗口的唯一出口

| 窗口/并发 | 不可写重放与清理规则 |
|---|---|
| W0 grant记录后、目标创建前owner消失 | query/fence/abort；目标/dup/send=0，不创建“补发”目标 |
| W1 A已创建、B未dup | 原A有ticket；清A后abort；同command不再create |
| W2 B已dup、send未调用 | A/B各计1，send=0；仅清理/abort，不重发或再dup |
| W3 send已调用，是否收到未知 | send=1；安装/transport引用按已知数＋未知上界保留，不能再send。首轮abort-only，直到逐引用证明归还 |
| W4 receiver已取B、尚未claim即owner消失 | 安装/一次take=1；receiver引用不能漏账；真实进程死亡只释放其独有引用，sender/transport另清；模型退休须真实close |
| W5 claim已持久但确认丢失/owner消失 | claim记录不撤成“没领过”；禁止写恢复、再claim或FD重送；query后围栏/逐ticket清理/abort |
| W6 正常claim后的同command并发/第二claim | 只返回元数据或拒绝其他receiver/claim，真实dup/send/take不增加；active原owner继续按原能力串行写 |
| W7 关闭返回丢失或owner死于close窗口 | 按§1 disposition；已关闭只补确认，UNKNOWN不重关；全部引用证明确立前不验证/READY |

R3 manifest覆盖W0–W7和并发认领；不把模型owner退休当真实OS死亡，也不把一次writer授权解释为允许无限FD重放。旧owner ready与新owner abort、READY已持久丢回复、验证不可读等R2约束仍保留。
