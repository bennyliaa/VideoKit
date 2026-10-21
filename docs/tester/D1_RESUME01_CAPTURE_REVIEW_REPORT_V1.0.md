# D1 RESUME01_CAPTURE 独立离线整包复审报告 V1.0

日期：2026-10-20。结论：**PASS_OFFLINE_CAPTURE_REVIEW；R01 在离线执行准备范围关闭，阻塞缺陷0。** 支持负责人准备准确的新 release；当前 PREPARATION_ONLY policy 不放行生产，未签发或消费设备许可，M1/部署/M2/T07 仍 NOT_RUN。

本结论来自独立整包核验、控制路径审查及新隔离目录中的代表性验证，没有把 coder 的145条断言直接视为独立测试。零 SDK、5037、设备、旧PID/handle查询及产品/Android构建；未改产品源、冻结材料或旧报告。

## 来源、工件及范围

依据 `D1_RESUME01_CAPTURE_TESTER_REQUIREMENTS_V1.0.md` 和负责人本次正式派发。

- 交付文档 SHA-256：`ba0be557e61bdc72ecc271ed34ba2c5f21e6b3b033dcf4d6a3b1b2232be319e9`。
- 外 seal SHA-256：`9fd6b86f906f0ae196249e0885a83706be4692c31016bf687f6f07e322ab3b8c`；664个不可变文件和ZIP663成员逐项大小/hash及集合通过。
- ZIP 741139 B，SHA-256 `24c5e9f8c5442d17974cac7426c5d9e99bb8cb1f3a2c02e7634403c9becac263`。
- 实际受审入口 `docs/coder/d1resume01-capture/tools/capture_metadata.ps1`，SHA-256 `fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe`。
- 74生产来源、183生产JAR成员及旧发布来源保持已审字节，未因采集器加入产品类或重编。代表性验证结束后再次核664项，仍全等。

tester证据目录：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_CAPTURE_REVIEW_EVIDENCE`。只在新的 `selfchecks/work/tester-29d7cb11-369c-49a2-83d0-9dc497f3e9d2` 隔离目录运行固定本地fixture；该目录不属于封包不可变源。全部本轮控制器返回后，另存60文件快照及索引，没有读取旧fixture002原在途对象。

## R01准确入口与策略门：PASS

入口不再使用旧 TABLET_CLOSEOUT_CONT 的固定目录/旧schema/kill采集器。请求准确八字段，检查schema、重复键、值类型、policySHA、entrySHA、root/scope、slot、逐项argv、cap及资格；生产模式只允许原五条SDK argv、65536/524288/65536/65536/524288 B、15秒及M1→M2固定阶段，未增加SDK请求。

准备policy保留 PREPARATION_ONLY，授权、独立capture审查及基础release绑定字段为null。在任何工具hash/子进程启动前拒绝生产；本轮对真实准备请求独立运行该拒绝路径，实际工具返回1、stderr包含准确拒绝码，没有SDK或现场目录初始化。

OFFLINE_FIXTURE 仅允许固定本地Python和既有capture_fixture.py的准确路径及摘要，root限于隔离fixture前缀。故障注入受该模式限定，不作为生产任意子进程/任意故障接口。

持久entered在child前写入并关闭；同请求重放、halt、未证前项返回、输出已存在均拒绝。同一原控制器持有独占`.capture.lock`和global强引用；未新增网络协议、后台服务或独立通用keeper。既有前台控制器在原对象未证时持续保管，不承诺15秒退出。

## 计数与原对象归还：PASS，适用范围明确

控制路径将每次成功read的n先加入原始计数，再判断quota/队列/写文件，保存计数独立。未结束读取只能报已知前缀，faulted read保留总量UNKNOWN；faulted write可能部分写入，不能把已知成功前缀0解释为实际写入0。原始归档和控制写入未知分别保留对应预算。

首次超时、越界、stderr、读写错误或非0退出停止后续准入并保留第一失败。迟到返回仅补当前物理事实，不清halt、不转资格PASS、不退款。原Process、reader/pipe、FileStream和原任务没有替换或kill；wait/dispose/close均有一次进入屏障。调用启动或关闭未知时不会再发第二次调用强行制造归还。

原receipt明确不能证明自身关闭；只有原读取/文件/metadata和lock确实返回后才生成console结果。console写入/返回和原控制器工具退出仍由外部可信tester独立证明，不能仅凭进程消失、文件存在或阶段日志进入后项。

永久未返回、同步IO启动未知和真实原生close永久挂起未被本轮实际制造。静态检查相应路径保留原上下文和锁/原对象、不重复关闭、不生成合格证明，依赖保持阻断；不将受控task/gate验证扩大为真实操作系统永久IO故障已测或可自动恢复。

## 独立代表性验证

本轮7个实际采集控制器及2个前置拒绝控制器均通过各自原工具调用自然结束，无kill、无新增待收尾owner。所有数据为固定本地Python fixture，不调用真实SDK或网络。

| 用例 | 独立观察 | 判定 |
| --- | --- | --- |
| 正常链第1项 | 实读/保存17 B、资格true、原资源关闭、工具exit0 | PASS |
| 缺前项证明 | 下一项工具exit1，没有创建该项entered或child | PASS，正确拒绝 |
| 外部证明后第2项 | 第1项工具实际结束后，在另一次调用中写证明；第2项实读17 B、exit0 | PASS |
| 分块越界 | 资格96 B，实际已读192 B、保存64 B；资格false、halt保留、自然exit2 | PASS，未截断实际账目 |
| faulted writer task | 实读17 B；saved成功前缀0、savedAmountUnknown=true；资格false、自然exit2 | PASS |
| faulted reader task | rawBytesKnown=0但rawAmountUnknown=true；原任务/pipe/file返回，资格false、自然exit2 | PASS，0仅为已知前缀 |
| 资格超时后晚返 | 后来实读19 B并完成原关闭，仍保留超时首因与资格false，exit2 | PASS |
| 文件关闭gate | 子进程wait已返回，但原文件未进入关闭时没有console或最终receipt；释放测试gate后同一owner/reader完成，仍资格false、exit2 | PASS |
| 真实准备policy | 准确拒绝 PREPARATION_ONLY，工具exit1，不发SDK | PASS |

文件关闭gate的初次工具响应为本轮会话82582仍在运行。已保存窗口证据：waitReturned=true、两个reader的fileCloseEntered/fileCloseReturned均false、console0 B、最终receipt不存在；仅释放明确的本地测试gate后，工具自然exit2。前后owner GUID、controllerPid、processToken、readerToken、streamToken全部一致。这不是用旧PID查询或外部终止换来的结果。

本轮7份原console合计11214 B。正常与非正常结果均保存原console、stderr及工具最终结果；faulted-read的原始总量仍UNKNOWN，不用其他六项已知数量补齐它。

## 外层completion-proof可形成且非采集器自证：PASS

独立正常链采用以下真实先后顺序：第一条采集器原工具调用完整返回exit0、无运行session → 下一次工具调用读取该原console和receipt、核原资源及资格、取得controllerPid与receiptSHA → tester在固定completion-proof路径写入证明并计算SHA → 再启动第二条请求。该证明不是采集器生成，也不是仍在同一调用中根据“将来会退出”先填true。

`external-proof-formation.json` 绑定原工具结果、controllerPid和receiptSHA，实际第二项接受该SHA；没有证明的负例在child前拒绝。receipt自己的captureQualified不等价于外层console关闭或工具EOF，本轮均有另外的实际工具结果。

接口中的approvedForNext仍要求可信tester先做语义审查。未来生产必须先核每段身份/版本/数据/完整性和占用，不能只因采集exit0或captureQualified就填true。首M2还需准确scope/releaseBindingDigest及真实部署结果/归还的独立证明，代码检查保留；本轮未模拟成真实部署已完成。

## 历史失败和UNKNOWN：保持

coder最终fixture004的145断言有其输入摘要、原始输出和自然退出记录；本报告只把它作为候选证据，并以上述独立验证补充。fixture001/002/003/004的先后修正未被合并成无失败历史。

特别保留fixture002：测试观察器曾在异步halt文件尚未成为完整JSON时退出1，原局部控制器的外层wait/工具返回为UNKNOWN。封包仅冻结该轮快照，排除可能仍变化的原路径。后轮145 PASS和本轮9个新控制器自然返回均不能回补其ACK；本轮没有查询其旧PID、轮询旧会话、释放其gate或终止它。

旧执行本地控制台UNKNOWN/8192槽、A/K TERMINATED_WITHOUT_RETURN/false、B/H分别UNKNOWN、K原预算UNKNOWN及旧账本/once均不变，不退款。新fixture及准备控制证据单列，不能消费或重置旧余额。

## 预算和新release无环绑定：PASS_OFFLINE_FEASIBILITY

不扩大43操作/3145728 B文本/4194304 B归档。原始/重复输出1949696 B不变；控制预算786432 B内重算：

| 控制部分 | B |
| --- | ---: |
| 其他原控制预留 | 589824 |
| 五capture：每项entered8192+receipt8192+console4096+副本4096+外部proof2048，另halt一次2048 | 135168 |
| 旧已知前置记录 | 2272 |
| 旧控制台UNKNOWN槽保留 | 8192 |
| 保守承诺合计 | **735456** |
| 控制余量，非新操作许可 | **50976** |

1949696+735456+50976+409600=3145728。409600 B全局未分配额度不可花。运行时未知/超额继续如实保留，不把名义cap当物理硬读界；额外转发raw须另外计重复文本。这是新release可行性核算，不是本轮实际设备预算消费或授权。

无环绑定顺序可行：新授权及基础release描述先固定新E9 scope/release/config/once、原registry/预算及entry摘要，不引用后生成policy/request；policy再引用基础描述、授权及本capture报告；五请求引用policySHA；最终manifest/permit/Java observer pins列全前层材料；独立机械报告在seal外，运行时完成证明只在真实工具完成后产生。

产品sourceReview和capture独立报告分开绑定，原registry历史trust不改。新evidenceRoot须在新机械PASS和本地准入后、首M1前按准确授权创建；不先写部署once/disposition/claim。M1全门后再部署，M2再唯一case，不复用旧许可或就地覆盖旧release。

## 集中结论及阶段边界

本次R01的准确采集入口、目录/schema/argv、超额/UNKNOWN计费、同原owner保管及可实际形成的外部完成链已在离线范围闭合；没有新增阻塞缺陷。支持交负责人准备下一准确新release，之后仍需独立机械审查、明确派发、同源工具及真实registry/ledger/claim、新鲜v17/fixture1/data和全局占用门。当前生产policy仍拒绝执行，M1/部署/M2/T07全部NOT_RUN。

本轮不启动M0，不改当前D1产品范围；现行UI方向为自有Flutter Theme，SkinKit待正式支持Flutter后再安排，旧报告中的历史UI要求不改写。D1 NOT_PASSED、M0 NOT_STARTED及所有其他媒体/P0/许可余门保持。

完整报告主动发送负责人后停止，不新增监控、设备查询或重试。主要证据为 `identity-and-fixture-plan.json`、`independent-fixture-results.json`、`external-proof-formation.json`、`file-close-gate-before-release.json`、`contract-accounting-and-history-review.json`、原console/tool结果与60文件独立fixture快照。发送回执另存，不回写已发送报告。
