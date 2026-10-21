# D1 E13D 离线整包独立复审报告 V1.0

2026-10-18；tester。依据 `docs/milestones/D1_E13D_TESTER_REQUIREMENTS_V1.0.md`。本轮只读取冻结记录、生产源码、准确缓存依赖源码及归档成员；没有构建、候选自检、测试执行、网络、ADB、STATUS连接、本机原进程/handle查询或待审两项诊断。原主case/宿主/reader继续按既定范围保管，不轮询、不处置。

**结论：PASS_OFFLINE_REVIEW，接受 E13D 作为根因边界分析和待实现方案交付；当前实际根因仍为 NOT_UNIQUELY_DETERMINED。** 四个条件性静态缺口独立核实，但没有本次命中证据。不是产品修复验收、原任务归还或设备通过。D1 NOT_PASSED / M0 NOT_STARTED，历史 P0/FAIL/UNKNOWN 保持。

## 1. 整包身份与独立证据

| 对象 | 独立核验结果 |
| --- | --- |
| E13D 外seal | SHA256 `acc83e5aff9288099c1f324fb24394316dedfd83272cce66cd8299a215b66365` |
| ZIP | 40299B；SHA256 `dbe40dc80a4962b53f677fdc55d034b0d1b282529d6fb9a37109e25fd04d6385`；9个不可变记录、8个准确成员，成员集合/字节/SHA/CRC一致 |
| 主文档 | 17548B；SHA256 `4594b06bd42b32c44b8e1394ba251034fd3791554353c552ee2a3d1a841ef925` |
| 历史输入 | 原35文件 pending、6文件 repair，以及 E13A270/E13B118/E13C141 行逐条核字节/SHA；不把重复行相加冒唯一文件数 |
| 源码 | 18份准确文件及逐行摘录重算一致；E13HostCase/E9PcSupervisor及其嵌套类的实际E13C JAR字节与已审E13A JAR一致 |
| 准确依赖 | lock为runner1.7.0/monitor1.8.0；缓存sources.jar及entry SHA、摘录逐行核验，无下载，无SDK版本替代厂商线程证据 |

tester自有 `independent_review.py` 共 **1282项检查通过**，独立读取586份唯一文件，审查前后SHA保持。未调用候选 `analysis_bundle.py verify/collect/help` 或其自检；候选交付中的成功回执只作被审资料，不替代本次独立核验。审证范围与计数见 `docs/tester/D1_E13D_REVIEW_EVIDENCE/independent-audit.json`；586份输入切片另存，最终出报告前再核一次不变。

E13C V1.0/V1.1准确报告SHA分别为 `9cdc913d8a6c98e1aad4c4acddb0ab3ed3adc66dd39c2ee5d053139b678ace74` / `77a21b4beeb77e11ce065af97e0548bdcebb86f6f0c3d0be2e7061ab950e2008`。主case exec42537/PS39560/Java38056/ADB49540、Android14763/14765/14779仅为最后实测切片，本轮未验证它们当前存活或退出。失败ps诊断的 LOST_DIAGNOSTIC_OWNER_UNKNOWN 单列，不混同主case；不造stderr0、exit/closeACK或退未知预留。

## 2. 四项静态结论的独立复核

| 编号 | 生产证据及判定 | 与当前在途任务的关系 |
| --- | --- | --- |
| D13-S01 | `E13PermissionProbe.java:15`在callback work中countDown；`E13BindingOwner.java:27`之后才finally减少计数。`E13Instrumentation.java:13–14`首次canFinish=false直接返回/吞异常，既不保存待完成请求也不订阅原归还。原owner晚返后没有驱动同runner完成的接线。**条件性活性缺口成立，P1待实现。** | 测试线程可在callback finally前醒来，若整条结束检查仍与该finally交错，首次finish可被拒绝；不证明本次实际出现这种调度。canFinish重新被外部调用时可能清理已返probe，不等于有自动续办。异常分支同样没有保存结果及晚返完成路径。 |
| D13-S02 | `SenderService.java:24–31` code1只准一次，原TargetBinding只给单次同步快照；probe:47–49缺精确原归还就设置sticky unknown；tryReturn:29有!unknown门，未见同原远端对象的晚返查询/ACK。**保守安全门存在，活性/可观测性缺口成立，P1待实现。** | 正常拒绝不必走unknown；异常、身份错误和非预期接受不能因后来owner归还变成kernel拒绝成功。未来远端ACK只能补同原对象归还证据，不能洗掉原失败。 |
| D13-S03 | probe:25先同步bind后才await5s；codec HELLO及fixture transact(flags0)、unbind为同步平台调用。test:17在E9 observe成功后才设began；:20是@After30s资格断言。PC55s只停止依赖并保管。**局部超时不等于调用截止，P1待实现可观测性。** | @Before的open/read/fsync/锁/close可未返，30s并未覆盖它；不能用扩大timeout、重发或杀线程补归还。没有实测stage，不能确定卡在bind。 |
| D13-S04 | `E9PcSupervisor.java:74–79`原进程和reader返回后才decode，:89–95先达55s就抛；`E13HostCase.java:29–31`仅runDecoded正常返回才print raw，抛后进入finally。晚到decoder可确认owner但不能让已退出的print语句再执行。**晚raw可见性缺口成立，P1待实现。** | 原raw可能留内层Operation缓冲，外层报告还存在等待Java退出才落盘的第二层缓冲。没有raw不能反推Android阶段；不能把当前未冻结live脚本当执行时冻结源码。晚归还不恢复超时PASS。 |

以上P1属于既有生产门和观察链需集中修复的风险，不是E13D已完成实现。E13D文档没有把它们冒称本次已实证的死锁或产品修复结果，离线交付可接受。

## 3. Binder、Looper与准确runner边界

测试@Before首先断言非主Looper，随后E9观察；runner1.7.0 onStart:451先进入monitor1.8.0 onStart，后者:372 waitForIdleSync发生在测试执行之前。因此app进程存在不证明测试已到@Before或bind，非主测试断言也不能证明主队列当时可用。

fixture clearCallingIdentity改变权限身份，不切换线程。自定义onTransact并未runOnMainSync或等待自己的ServiceConnection latch；共享owner的port.bind/port.unbind/callback work位于短锁外，未发现同一owner锁跨同步Binder再等同锁回调的闭环。codec HELLO直接构造Bundle，不在该分支同步回调测试Binder或等待owner HandlerThread。由此只能否定“源码已经证明经典主线程回调死锁”的说法，不能证明厂商API31的Binder/Looper没有阻塞。未采线程栈、不猜实际dispatch线程。

monitor1.8.0 finish:391–409有自身finished标志、post ActivityFinisher后等待；:429–445明确禁止main，循环约2秒。这个局部循环有界不能保证整次finish所有调用都有总截止，更不能把它定为当前长挂根因。tester额外读取runner onException:638–648的完整尾部，确认仍向super.onException传播；不能在新方案中盲调super.onException越过原归还门。新增归还回调即便发生在main，也不能在main直接调用monitor.finish。

普通方法没有调用后五方法的source()，也没有创建正常编码E4Session；E4Session静态retained/slot仅作为finish门检查。renderer/audio/JNI正常编码没有已进入证据，E9观察中的AndroidLease加载/原生IO仍只是潜在@Before边界。ps只见app而未见fixture/codec，不能推出它们从未启动。

## 4. 当前原任务的收尾与待审外部处置

无新增控制动作时，完整自然归还链必须是：同一原Android owner真实归还→同runner准确scope/method终态→原ADB自然退出→原reader/pipe实际返→同decoder确认原authority→原custodian及外层原句柄真实返回→真实raw落盘。任何一层缺证都单列UNKNOWN；超55s资格仍不通过。若S01已失续办或同步调用永久不返，已安装v17没有受审恢复入口，E13HostCase retainAuthority(owner,null,owner)也没有可直接调用的当前任务恢复处理器。新APK、新scope、新Process、外部finish或二unbind不能接管旧对象。

E13D只提出隔离保管和未来另审外部处置，未给可立即执行的恢复流程。负责人若需要收尾，可审以下两个具体分支；**它们均为待批需求，本轮不执行**：

| 待审分支 | 必须先固定的证据与动作边界 | 可记录的结果与限制 |
| --- | --- | --- |
| A. 继续自然保管 | 原scope/方法/准确启动身份和既有handle清单；仅接收原handle自然输出，保留原缓冲与原reader，不另起观察器替代 | 可补真实晚返raw和原资源事实；没有晚返就继续PENDING，不能承诺自行结束 |
| B. 负责人明确选择外部终止 | 另发准确serial、app/fixture组件、要处置的每个Android/PC原对象及当前启动身份、单次操作/响应/字节预算、原始证据保存顺序和保管转交人；先保存可获得的原raw/日志/已用预算，明确不可恢复内存损失及诊断丢失历史。分别审Android侧终止与PC侧终止，不能合并为笼统“清理”或按历史PID直接执行 | Android被外部结束后，即使ADB和管道自然返，也只能记录外部终止/无Java归还；无同scope终态token则androidReturned仍false，原PCcustodian可能继续保管，不能伪造ACK让其退出。若进一步选择结束PC宿主，须另批承认原内存/handle不可恢复的行政终止状态；保留ORIGINAL_RETURN_UNPROVEN/LOST_OWNER，不能登记正常close或产品PASS |

外部终止如何解除跨scope封锁，也须负责人给出独立处置记录、保留历史UNKNOWN的预算处理及fresh完整M1准入；单凭PID消失或新once不能放行。本报告不提供或执行终止命令，不凭离线文档解除原pending。丢失ps诊断也须独立处置，不由主case将来归还抵消。

## 5. 最小完整下一实现需求

建议负责人集中派一批E13E或其指定版本，保持现有adapter/owner/runner/PC门，不新增通用框架。下表是实现前必须落到准确接口、状态、预算和证据的验收要求；不是批准部署。

| 项目 | 最小实现与不可缺的边界 |
| --- | --- |
| R01 有限原stage证据 | 沿@Before入观察前、E9观察入返、每次原bind/transact/unbind、callback入/最终计数返、完成请求/阻断原因记录scope/method/原ownerID/PID/UID/thread和单调序号。固定事件数/单条/总字节/落盘上限写入需求；锁外记录，不引入同步回调等待。日志失败不改变资源状态，事件不是ACK；准备计时与结果30s资格分别呈现。 |
| R02 同runner完成请求续办 | 深拷贝固定scope/method/code/result及有限异常，保留最早失败/超时；先注册原归还订阅再检查，同步覆盖“注册前、注册中、检查后、finalizer退出前”四种交错。完成请求后封住新增依赖，只准原return继续；所有canFinish组成门（E11 lifetime、source、probe/binding）都须有真实事件或可证明不再变化。最多一个强持有的非主finalizer，反复通知合并；锁内决定唯一状态，锁外调用super.finish最多一次。永久UNKNOWN不finish；异常和晚返不能翻PASS，也不能用super.onException提前结束。finalizer本身/订阅注销纳入原保管及证据。 |
| R03 原fixture晚返ACK | 原TargetBinding保留准确scope/单次request/原owner身份、真实端点UID和一次consumed负例；只读查询/有界订阅不得重新bind、二unbind或重做code1。区分物理transact返、kernel结果和owner真返；已知晚返与不可恢复UNKNOWN不能共用可任意清零标志。错scope/UID/请求/旧owner拒绝；身份损坏或原失败保留，迟到ACK仅补原资源事实。协议字段、尺寸、次数、超时、强持有对象和异常处理均先审。 |
| R04 原PC唯一reader增量落盘 | 修改实际E9PcSupervisor/E13HostCase路径，进入前注册原operation/process/reader/pipes及archive身份，先保存intent/PID。唯一原reader同时有界归档，不为“补日志”另开reader；55s前后连续原字节、顺序、EOF、exit与各pipe关闭事实独立保存。总量/文件/块/写入等待和失败保管有明确上限；磁盘失败仍保原owner与未归还状态，避免阻塞唯一drain无限积压或关pipe伪返。不能从新对象追溯认领当前私有buffer。外层观察器也须先强持有、finally记录实际事实，空数组写入修复只是其中一项，不能再由记录错误丢失原owner。 |
| R05 跨UUID设备封锁 | 在实际公开deploy/case入口、其他窗口和新UUID共同生效，按serial+app/test/fixture及原scope登记未决归还/外部处置。进入第一个child/install前检查；未决时新UUID、once文件缺席或历史PID消失都不能放行。写明并发登记/检查原子性与失败后保守封锁，不以新框架替代既有生产准入。 |
| R06 集中交付 | 固定源码/APK/JAR/依赖锁/manifest与原提案逐项映射，明确实现变更、已执行本机证据和仍需Android证据；先离线复审。原任务处置通过前不安装、不启动修复版；后续设备仅负责人新派准确单方法，按真实代码影响决定一次集中构建，不机械重跑旧套件。 |

## 6. 下一批必须给出的直接生产证据

| 证据组 | 必须覆盖的有限交错与原回执 |
| --- | --- |
| T01 adapter→owner→runner | 实际PermissionProbe ServiceConnection在countDown后、callback finally前受有限latch暂停，首次finish被阻断；同一callback自然返后唯一完成。测试通过与@After已失败两分支都要保原结果。只测BindingOwner九组或镜像gate不足。 |
| T02 不丢唤醒/非主完成 | 对实际runner分别在订阅前、订阅中、canFinish检查后和finalizer退出时归还；重复finish/异常请求和多次通知合并；monitor1.8.0实际约束证明super.finish运行在非主。永久UNKNOWN保持无平台finish，无新增测试/owner。 |
| T03 同远端端点 | 实际SenderService入口和PermissionProbe解析，平台替身只控制原bind/unbind的有限晚返；一次code1、同scope只读ACK、错误UID/scope/replay拒绝、UNKNOWN不清零、原unbind仅一次。不同UID/签名/kernel行为另留Android实证，不能由本机替身充数。 |
| T04 原同步调用 | 分别扣住实际adapter的bind、HELLO/fixture transact、unbind和@Before观察，跨5s/30s/55s仍不假close，释放后仅原对象续办。有限替身不声称验证厂商Binder调度。 |
| T05 PC晚raw/磁盘失败 | 实际E13HostCase/E9PcSupervisor/归档器使用有限本机原子进程产生55s前后raw、分块与空stderr、自然EOF/exit；全raw字节/SHA及每个原pipe归还可核。权限拒绝/中途写失败/容量上限时仍保同owner，记录失败不丢局部对象，不二reader/二close。超时/原失败不升级PASS。 |
| T06 跨scope准入 | 同一实际公开部署/方法入口以另一UUID、新once、并发请求及旧PID消失状态尝试，均在原pending未处置时拒绝，实际child/install=0；不能只测另写的布尔函数。 |
| T07 后续设备门 | 上述实现离线通过、旧原任务与诊断未知处置审清、fresh完整M1后才可新派。真实API31主Looper/Binder、独立fixture UID/签名、false/SE的原一次unbind、准确runner终态及PC原归还分栏。当前六方法不因此获得补跑许可。 |

## 7. 待审只读观测提案与停止

E13D“至多两个原ADB、各10s/64KiB、合计128KiB”的计划是待审提案，不是恢复原剩余两次额度。第一份须准确身份与system_server完整active结构、固定服务切片，超限/不全即BLOCKED停止；第二份仅在需要且准入成立时读有限日志，明确最多200条/64KiB的窗口边界，缺失/覆盖不当作未执行。先审观察器原对象强持有及磁盘失败路线，失败诊断UNKNOWN未处置不能直接新增并发client。PC STATUS/OP不暗加，若另派须准确同handle、一次连接/4KiB/5s及accept预算，无控制权限。本轮这些全部0。

本轮集中复审到此完成；没有选择某个假设作为当前唯一根因，没有替原活对象实施任何修复或处置。报告及独立证据交负责人统一安排下一批实现和原任务处理；报告SHA及发送回执另存，不回写已发版本。
