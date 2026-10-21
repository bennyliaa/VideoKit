# D1 R3 close、writer与分支预算独立复审报告 V1.0

日期：2026-10-16。任务：按D1_R3_TESTER_REQUIREMENTS及负责人正式整包交接，集中复审R2三问题。方式：离线全文、原始字节身份及表格解析核对；不运行harness、JVM/.NET预检、媒体IO、构建、Gradle、ADB或故障实验。

## 1. 结论

**R2-R01与R2-R02的本轮设计缺口已补齐；R2-R03的分支及数值预算已补齐，但逐行控制操作可执行性仍缺证，整包需一次集中补充后审定。** 16项审阅记录：15 SUPPORTED、0 CONTRADICTED、1 MISSING。此为材料判定，不是16项功能测试或61分支运行结果。

R3-R01（P1）要求明确每行控制步骤及计数粒度，尤其Q07-TAKEFIRST。当前“最多6次，所需步骤不够就停止”可安全拒绝超额操作，却尚不能证明该必测分支具备在预算内到达目标检查点的路径。不能将该设计不足交给实现时任意合并/隐藏控制操作解决，也不建议直接派完整实验执行。

S17未知close的尾部处置、按原helper实例退出与父进程逐引用归还的证明边界，设计文字可接受；实际是否退出、实际底层关闭及持久性均仍未验证。宿主JNI仍BLOCKED，C14冻结计划/历史FAIL不变，D1未通过、M0未启动。无本批功能/设备/构建任务在途。

## 2. 交付身份与范围

| 材料 | 实际SHA256 | 核对 |
| --- | --- | --- |
| D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md | c91743c74bab78ea854c4e5f6dbe7bd2c09da6e3428641f3b31db158323ebb44 | 与交接一致 |
| D1_R3_BRANCH_MANIFEST_V1.0.md | 6b5cb83a9e67fc7de69cac0817f53e29e6ee82b69e9defc781504e0a148e569b | 与交接一致 |
| D1_R3_DELIVERY_V1.0.md | ee8086792298abd31a99bd4ed627ce2adcabddf3b0dec94372b38a9101a6a605 | 与交接一致 |

三份原字节副本、输入/链接核对、行号锚点及独立分支解析结果存于[D1_R3_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_R3_EVIDENCE)。11处本地链接、6个唯一目标均可访问。R2五份原件SHA与已评审值逐项相同；没有修改R2/R3交付主体、C14、产品、原需求或门槛。

复审另读取R3开发/测试需求、R2独立报告及其已留证的源/Sink/预算语义。输入路径/历史hash继续沿既有清单，不打开媒体重新验真。R2中的源身份、seal原子点、Sink能力、READY/abort/COMMIT、全P0及原生故障判据未由R3无说明地覆盖；覆盖段落有明确声明。Windows同进程mailbox和helper收尾仍只是工具计划，不代表Windows Kit、Android Binder或故障隔离已实证。

## 3. 逐项复审

| ID | 对象 | 判定 | 理由与边界 |
| --- | --- | --- | --- |
| R01 | 三份输入身份/完整包及原件保留 | SUPPORTED | 三SHA与正式交接一致，R2五原件未变，原字节副本留存 |
| R02 | R3覆盖R2的段落/兼容与阶段 | SUPPORTED | 契约首段、回执§2明确覆盖统一close重试、可写缓存解释及旧分支/时限；公共API承载仍待审，未宣称冻结或实现 |
| R03 | close disposition及稳定对象/ticket | SUPPORTED | OWNED_OPEN_RETRYABLE/CLOSED_PROVEN/IN_FLIGHT/UNKNOWN/OWNER_EXIT分列；闭合R2-R01的任意异常可重关、布尔可证明释放歧义 |
| R04 | 安全重试资格/并发/耗尽 | SUPPORTED | 同ticket/revision串行获权，最多首次加两次，不同并发请求不自动排队偷获下一attempt；已关只确认、未知不重试，C1–C5有反例 |
| R05 | S17尾部UNKNOWN及全局退出证明 | SUPPORTED | 两对象/关闭操作先登记、D→C最后执行，不在未证之后开新任务；原helper实际退出只证明其独有descriptor消失，父guard/reference/pipe等另证；原close仍UNKNOWN。见§6 |
| R06 | writer授权/交付/认领/关闭状态 | SUPPORTED | 首次open也不可写；grant/delivery/receiver/claim分开，SEND_STARTED先耗唯一资格，takeOnce单owning cell。闭合R2-R02“一个grant却重复交FD”的解释缺口 |
| R07 | 同command并发/重放及确认丢失 | SUPPORTED | open/claim/query缓存均不含FD/stream；确认未知首轮abort-only，query曾CLAIMED不恢复写；已正常确认的原owner可继续，第二receiver不能再take |
| R08 | descriptor账本及W0–W7限制 | SUPPORTED | A/B各ticket，dup/send/install/take/claim/close分别计；同进程mailbox峰值2有profile限制，不外推Binder；模型退休不得替代OS死亡 |
| R09 | 22族展开为61行及共享任务 | SUPPORTED | 独立解析31P/30Q、17S/14T；T01 READY、T02/T03/T04 ABORTED、能力拒绝分开；S01四窗→EOF→ZERO后才结束，S17在全部Q后 |
| R10 | 合法短读/预算出口与P05补齐 | SUPPORTED | N行只有满读才窗口成功，S行实际4B前缀+ref后预算停止，不是provider错误/整窗成功；P05五次≤7B补齐32另有对照 |
| R11 | 输入/验证/输出/目标/记录数值 | SUPPORTED | 全部表格求和匹配回执，详见§4；不将预留当实耗或资源实际归还 |
| R12 | query及非query总分配算术 | SUPPORTED | Qr18/Qn83；非query分配414，合计515≤544，P10-D8/C4与普通两行12相同；分配求和不证明必需步骤数 |
| R13 | 每行控制额度与真实必需步骤相容 | MISSING | Q07-TAKEFIRST等未给完整操作清单/组合命令粒度，无法独立证明≤6，见R3-R01 |
| R14 | 时间/日志/资源分区及停止语义 | SUPPORTED | 20+52+55+5+20+10+18=180，日志3,178,496B；明确为controller决策期限，未保证内核调用结束。H/B为行同时上限，控制OS资源另限24；不能将未证写成0 |
| R15 | guard/Java/helper的前置与退出后资源 | SUPPORTED | PF包含兼容/身份/独立reference与启动，失败不重启碰运气；清理计时独立且在180内，helper没退出则PENDING。当前兼容、无写映射及稳定版本仍未实证 |
| R16 | F03范围、宿主JNI、P0/历史/C14边界 | SUPPORTED | 四次仅encoder，close仍三次安全资格；历史signal0 FAIL、trace缺失和C14两项NOT_RUN不追认通过。未用工具IO代正式媒体/Flutter/Kit/许可/原生隔离 |

## 4. 独立重算

解析原始Markdown每一P/Q行，无运行harness。证据：[branch-and-budget-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_R3_EVIDENCE/branch-and-budget-audit.json)。

| 项 | 独立计算 | 与交付对比/限界 |
| --- | ---:| --- |
| 分支 | 31P+30Q=61，ID无重复 | 一致；22族均保留，不是61次已执行 |
| 原始输入请求 | 1,573,426(P)+64(Q)+32(PF)=1,573,522B | 一致，≤4MiB；含失败/未知预留，不退还 |
| 原始输入调用 | 55+2+2=59 | 一致，≤256；包装计费与实际delegate数仍需实现分别留证 |
| 输出验证读取 | 4×65,536=262,144B | 一致，≤4MiB |
| 目标/输出写 | 10目标、10×65,536=655,360B | 一致，≤12目标/2MiB；不是实际写量 |
| 顶层记录 | S17+T14+PF1=32 | 一致；ticket/事件嵌入且受文件字节限额，不另开无限旁路 |
| 查询 | P:7/42，Q:11/41；Qr18/Qn83=101 | 一致；重放与新观察区分，单行≤1/3 |
| 非query/全控制分配 | 61×6+PF16+清理32=414；+101=515 | 一致，≤544；P10-D8/C4已含在61×6，不重复加。尚缺R3-R01的必要操作映射 |
| 时间 | P57秒（尾5）+Q55+PF20+清理20+记账10+停止18=180秒 | 一致；尾5未重复，接纳/等待期限不等完成保证 |
| 日志 | 61×32,768+131,072+32×16,384+524,288=3,178,496B | 一致；余1,015,808B仅停止证据 |
| 表内同时峰值 | H最大5，B最大2 | 均在媒体6/缓冲8内；文中另预留缓冲峰值4不是逐行表的实际最大值，但更保守，不是超限。真实运行时、管道/进程/log句柄仍另受24限额 |

短读S1–S4：65536+65535+65534+65533+reference4=262,142B，每行预算262,144，下一请求65,532不能预留，5次请求后仅4B前缀对照成立。P05按外层剩余32/25/18/11/4及ref32计122B，行给128B是保守上界，不是算术错误。所有预算尚为控制器需要实现的前置门禁；真实磁盘阻塞、helper退出或数据同步仍不能由表格证明。

## 5. 集中问题

### R3-R01｜MISSING｜P1：控制命令分配未绑定可复核的操作步骤

来源：[manifest:26](D:/CodexProjects/VideoKit/docs/coder/D1_R3_BRANCH_MANIFEST_V1.0.md:26)、[Q07-TAKEFIRST:111](D:/CodexProjects/VideoKit/docs/coder/D1_R3_BRANCH_MANIFEST_V1.0.md:111)、[writer协议:55](D:/CodexProjects/VideoKit/docs/coder/D1_R3_CLOSE_AND_WRITER_CONTRACT_V1.0.md:55)、[验证租约生命周期](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md:83)。R2-R03此部分尚未闭合；这是协议/计划完整性问题，不是已发生的实验超限。

Q07-TAKEFIRST是T05唯一一行（新任务/新目标），要求从授权writer到关闭/验证、READY_ELIGIBLE，再新owner接管、旧ready拒绝和abort终态。它不能借T01/T02的writer/receipt或在另一行预做未收费步骤。

按独立控制请求的通常分解，即使把全部writer关闭合为一个请求，并且完全不计分配/dup/send/take、write、flush及query，仍有以下8步需要明确归属：

| 序号 | 必需控制步骤 | 必须保留的事实 |
| --- | --- | --- |
| 1 | openTemporary/grant | T05同export/intent的唯一授权 |
| 2 | receiver claim | 正常认领确认，才可写 |
| 3 | writer finalize/close请求 | 每份真实写引用归还 |
| 4 | validation lease授权/open | 同revision只读验证 |
| 5 | validation lease归还/close | 验证资源实际清空才能READY_ELIGIBLE |
| 6 | takeover | 新epoch先获权，不能靠字符串假接管 |
| 7 | 原owner markReady | 实际到仲裁器后被STALE_OWNER拒绝 |
| 8 | 新owner abort | 资源已归还后唯一ABORTED |

当前行限6，而总分配515是给每行额度的算术，并没有给这8步的组合语义。若某个受控协议确实用一次finalize命令完成writer停止、只读验证及归还，则外部请求可以少于8；但三份材料尚未定义该组合请求、其副作用/在途子账本和清理边界。因此本报告判MISSING，**不把“至少8个独立步骤”误写成所有实现必定超6的数学反证，也不将此记CONTRADICTED**。同理P11双consumer、P10-B旧close重放再开对象、S17预授权/关闭/拒绝及全局清理32次也应有可查的逐步计数，避免隐藏前置。

建议一次补充control-operation manifest：每行从初态到终态的requestId/commandId序列、哪些明确为外部控制请求、哪些为同一命令下的有限IO子操作、并发重放/被拒绝请求的计数及每个ticket归属；将副作用实际调用数与控制请求数分列。若采用组合命令，预先定义其准入、取消/超时后在途、验证失败及实际释放证明，不能实现时临时把多步改称“内部步骤”绕过门禁。

在不变544全控制/180秒/32记录等硬限额内，经负责人明确修订分配或审定组合语义即可；本报告不要求增加硬限额或取消分支。重新求和所有行和PF/清理，确认任何必测分支在满足环境前置时存在可执行路径，再派实现。仍需保留“真实阻塞/预算耗尽就停止”的正确出口，但不要把一个必然缺前置额度的场景全记NOT_RUN后称完整计划可执行。

## 6. S17、close与writer的剩余实施条件

S17的D对象是已达3次且确定未调用底层close的持有资源，C对象是实际close结果UNKNOWN。两者在负例前登记、seal后只有已接纳清理继续，D→C收尾不需要新源授权；C后不再开分支，避免未知资源期间继续独立分配。该次序与R3例外一致，不能套用“同S编号”在未知后偷偷登记新对象。

正常helper退出必须由外部controller匹配原启动实例实际结束，而非只收到“准备退出”、进程名消失、线程结束或新PID启动。只有其独有descriptor可据此记RELEASED_BY_OWNER_EXIT；host guard/reference/transport、其他dup和仍在父进程的调用逐项另证。父进程源reservation/unknownOwner账本也须在这些证据满足后收尾，不能只清helper的fd数就宣称全源DRAINED。文本“所有task/FD/ticket核对”与逐引用规则已要求这一点；后续实现需要给具体证据，不是本轮要求产品实现。

20秒清理或180秒总决策期到，helper未实际退出、任何父引用/数据操作未证，继续PENDING并列owner；允许控制器结束等待不等所有资源已关闭。不得因最终进程退出把原close UNKNOWN改成CLOSED_PROVEN或成功调用；也不得调用shutdown hook盲重关数值。同理本机helper退出不是SIGSEGV、Android隔离进程或宿主JNI P0证明。

writer方面，grant记录、真实descriptor安装、takeOnce、claim提交与确认送达各有独立事实；确认未知只能停止写/query/围栏清理/abort，不能把CLAIMED状态查询当补发能力/恢复写许可。正常已确认原owner的幂等重放返回元数据而不取新对象，语义与前者不冲突。W0–W5模型owner退休和真A/B关闭也不能称OS死亡；真实Android transport若自动dup须另立profile和额外账本。

## 7. 下一步与交付状态

建议负责人采纳R2-R01/R02在**材料层面**的补充，保留真实backend/公共API承载/兼容/版本/dup/durability未验证属性。R2-R03的数值和停止原则已有依据；集中补R3-R01控制步骤与分配后，再决定有限本机harness实现及一轮执行。不自动启动下一批、不向用户索取环境、不重跑历史信号。

报告及证据均已保存；无harness/媒体窗口/设备/构建/故障任务在途。C14未恢复，既有信号FAIL/两项NOT_RUN、原P0、宿主JNI BLOCKED和框架/许可约束保持。D1未通过，M0未启动。

主动通知状态以本窗口最终回复为准；此前跨窗口通知自动审批拒绝，未以更换内容或工具反复重试，负责人可按既定半小时检查收取。
