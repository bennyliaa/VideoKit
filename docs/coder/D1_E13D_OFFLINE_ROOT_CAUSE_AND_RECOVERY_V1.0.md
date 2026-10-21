# D1 E13D 离线根因、原任务处置与修复提案 V1.0

2026-10-18。范围：OFFLINE_ROOT_CAUSE；只读候选源码、已有冻结记录及本机已缓存的准确依赖源码。没有设备、ADB、构建、部署、测试执行或 live 对象修改；本文件是分析和待审方案，未实施修复。D1 NOT_PASSED / M0 NOT_STARTED。

## 当前结论

**尚不能唯一定位首 ordinary 方法的实际挂起点，也没有证据证明某个 Binder/主线程死锁已经发生。** 能静态证实：同步平台调用可越过局部等待时限；runner 在原资源未归还时拒绝 finish，缺少原资源后来归还后的续办入口；PC 双层缓冲使阶段输出不可见，且 55秒后的晚到 raw 可能永远不再转发。这三类机制足以产生目前观测，但不是本次已证实的唯一根因。

E13C V1.0 证明 fresh M1、唯一15→17及fixture安装、M2成功；首方法一次进入后 PENDING。已观察的原链为 exec42537 / PowerShell39560 / Java38056 / ADB49540，Android shell14763→am14765、app14779。V1.1 不重读主case，故上述身份是最后实测切片，不能写成“现在仍活”或“已结束”。没有 case terminal stdout/stderr/receipt、kernelOutcome 或原 binding 归还证据；后五方法/M3未执行。

V1.1 的 **LOST_DIAGNOSTIC_OWNER_UNKNOWN 只属于另外一次 ps 诊断**：原局部 Process/reader/pipe 不可恢复，准确诊断PID未记；58908B stdout保留，stderr/退出码/close ACK缺失。记录错误发生在读取等待之后仍不足以补造归还。不得把该诊断丢失当作主case丢失，也不能把新PID匹配为空当旧资源ACK；这项 UNKNOWN 单列保留、不退款。本批当前没有新诊断或处置授权。

## 真实线程与所有权链

| 阶段 | 源码边界与线程关系 | 已证明的等待范围 |
| --- | --- | --- |
| runner启动 | E13Instrumentation.onCreate 校验四参数；本机缓存 runner1.7.0 的 onStart 调 MonitoringInstrumentation1.8.0.onStart | monitor 在测试前 waitForIdleSync 等主队列。只能证明存在这一入口，不能证明本次停在那里 |
| @Before | E13DeviceTests:13–17 明确断言非主Looper，再做 E9Runtime.observe 和权限准入 | 文件open/read/fsync/guard/close是同步边界，30秒计时是在观察成功后才开始；没有整体原生调用截止 |
| 授权正例 | PermissionProbe:34–39 bind codec，等回调，再同步 HELLO，再解绑 | 两个5秒await只包 connected latch，不包 bindService、HELLO transact、unbindService |
| 普通发送者入口 | PermissionProbe:40–50 bind独立fixture，同步 transact(flags=0) | 该 transact 没有可取消的超时；调用未返回时 calls仍占用，finally尚未开始 |
| fixture负例 | SenderService:21–31 的自定义 Binder.onTransact；clearCallingIdentity后用自己的Context/UID bind非导出codec，finally对原connection close，再恢复身份，最后写reply | 未调用runOnMainSync或等待自己的ServiceConnection回调。bind/unbind仍可等待system_server；不能从源码称其必在main或必在Binder池某线程 |
| 共同绑定owner | BindingOwner:18–41：只在短锁内标记；port.bind/unbind和callback work都在锁外，callback finally归还计数 | 没有“持owner锁跨同步Binder再等同owner回调”的源码闭环。close可以先于callback finally，届时返回资格为false |
| Android终态 | E13Instrumentation:13–14，canFinish=false就记录pending并返回；onException返回true | 不调用平台finish是保留资源门；但没有保存待完成结果、归还事件注册或自动重新finish的接线 |
| PC边界 | 实际E13C JAR中 E13HostCase / E9PcSupervisor 字节继承E13A，case:26–31，supervisor:74–110/160–170 | 先等原ADB退出、原reader返回再decode；55秒只停止依赖并托管，不杀进程。无原owner token时不把物理子进程退出等同Android归还 |

源码中的 Binder endpoint 创建不等于“onTransact必在主线程”；具体dispatch线程需原线程证据。测试的非主断言也不证明整个系统主Looper可用。fixture Binder clearCallingIdentity 只改变后续权限身份，不把执行线程切到main。E4CodecService 的 HELLO 直接构造小Bundle，没有同步反向调用测试Binder；codec owner HandlerThread 在HELLO中不被等待。因此**当前源码不支持宣称已证实经典同线程回调死锁**。

准确依赖来源：冻结lock声明 runner1.7.0 / monitor1.8.0；读取本机对应sources.jar，无网络/下载。monitor:349–379 有初始 waitForIdleSync；finish:391–409 会post ActivityFinisher并在非主线程等待；429–445的活动等待约2秒且禁止main调用。不能把这个有界循环本身说成长时间挂起的已证根因。没有读取厂商API31线程栈，也不以本机SDK36.1旧摘录代替厂商线程实证。

E4Session在ordinary路径没有new/start；canFinish仅检查其静态retained/slot。该方法未调用source()，所以不把后五source用例、renderer/audio/native编码路径当作本次已进入阶段。E9当前观察的AndroidLease原生库加载/文件IO仍可能在@Before触发，尚无raw证明成功或异常。

## 静态已证的问题与条件轨迹

**D13-S01：finish的失去续办窗口。** PermissionProbe.onServiceConnected 在 binding.callback(work) 内 countDown，随后才由共同owner的finally减少callbackInFlight。测试线程可以先醒来；如果后续结束检查与该finally交错，canFinish可能暂时false。runner.finish一旦因此返回，后续callback实际归还、OWNERS清空并没有再驱动同一runner.finish。onException同样没有续办。此为可按源码构造的条件性活性缺口；没有原日志证明本次命中。永久UNKNOWN则应继续拒绝finish，不能用“补finish”把UNKNOWN变成功。

**D13-S02：远端瞬时未归还被压成sticky unknown。** fixture只回一个同步结果快照（bind/unbind/state/resourcesReturned）；PermissionProbe:47–49只要未收到精确resourcesReturned=true就置unknown，后续即使客户端binding归还也不移除该probe。现有fixture code1已consumed，既无原TargetBinding的scope化只读查询，也无原对象晚归还ACK通道。这保守地避免假ACK，却没有区分“原transact已返回/已知远端仍在途/不可恢复UNKNOWN”的续办路径。不构成kernel拒绝已证；正常拒绝也不当然会走此分支。

**D13-S03：局部时间限制不是调用截止。** connected.await(5s)在bind调用返回后才开始；30秒只是@After结果资格断言，且began在@Before观察成功后才设；同步transact/unbind和@Before fsync没有整体可强制结束门。PC55秒托管不是Android取消。扩大所有timeout、主线程join或另开相同case不能修复原所有权。

**D13-S04：晚到原raw的可见性缺口。** E9PcSupervisor:76只在原ADB exit0且reader归还后decode，E13HostCase:30只在runDecoded正常返回后print raw。若55秒先抛PENDING，main已进入finally；即使原ADB之后自然归还、decoder运行并确认owner，原:30仍不会重新执行。原raw可仍在Operation私有buffer中，outer harness也只有Java退出后才存完整回执（该外层行为以tester报告为依据，不把当前live脚本字节冒充执行时冻结证据）。所以外部无raw不能定位Android代码行；晚到close也不能把已超时资格改PASS。

## 合理假设与证伪需求

| 假设，均未实证 | 支持/限制 | 需要的最小证据 |
| --- | --- | --- |
| H1 runner尚在测试前main-idle等待，或@Before观察未返/失败后owner保留 | 已有ps只有app进程，没有codec/fixture进程名；这只是一个切片，不能证明从未启动过服务 | 准确scope的runner启动/测试开始、FRESH或BLOCKED观察、异常日志；若完全没有日志仍不能排除 |
| H2 正例bind、HELLO、unbind某次原平台调用未返 | 源码确有同步窗口，但无原服务/线程状态 | 原scope关联的services/processes及已有stage enter/return；当前版本缺足够阶段标记，可能仍无法唯一定位 |
| H3 fixture transact或内部bind/unbind未返 | 只有负例确已开始才成立；ps无fixture不证明未调用 | fixture PID/服务连接、原调用阶段或线程等待关系；不能从14779一个PID推内核拒绝 |
| H4 test已返回但finish门被暂时/永久owner卡住 | D13-S01/S02静态成立；缺pending日志 | E13_MANAGED的PENDING_ORIGINAL_OWNERS_NO_FINISH或PENDING_EXCEPTION，scope必须完全匹配 |
| H5 Android已有完整终态，PC在等原pipe/解码/authority | 结构上存在；报告切片仍有原ADB，不能只据主Java活判断 | 原ADB真实返回/管道EOF/同handle状态/原终态token，当前没有。新外部进程不能替代这些ACK |

优先级是先区分“测试尚未进入 / 已进入平台调用 / 已到finish门 / PC等待归还”，不先改Binder线程或解绑语义。若后续只读材料仍不够，结论继续NEEDS_DIAGNOSTIC，而非选概率最高的一项当确定根因。

## 最小只读观测提案（当前不执行）

负责人已要求在诊断owner丢失后停止新设备诊断。下列只是待独立审查的需求，不消费余量、不自动复用原两次额度。

1. 首先接收tester已落盘、明确交接的补充raw及manifest；不轮询浮动目录，不在本窗口读原session或live ledger。对原case与丢失诊断分别记账、分别保管。
2. 若负责人未来另派，最多两个直接原ADB客户端，每次最长10秒、完整输出各≤64KiB，合计≤128KiB，全部另计原批补充范围。先固定原scope/组件/已知PID启动身份，禁止仅按旧PID采信；第一客户端只取system_server的完整active instrumentation及两个固定服务的连接/进程切片，保留头尾和原exit，不用client-side dump、不新建绑定。完整性/身份/输出超限即BLOCKED且停止，不追加探针。
3. 仅第一份仍需分支判断且预算/所有权准入成立，第二客户端读取已存在、固定scope/PID对应的有限logcat窗口，关注E13_MANAGED、AndroidJUnitRunner/MonitoringInstrumentation、AndroidRuntime的既有日志。固定最多200条/64KiB，保留截取边界；日志缺失/覆盖不证明未执行。原版本没有逐调用stage，报告允许最终仍无法定位；不以SIGQUIT、debugger attach、kill -3、ANR触发、heapdump或新测试补栈。
4. 观察器本身须在进入前强持原Process/readers/pipes，先保存身份和intent，字节数组非null，落盘失败仍由同一原宿主持有，回执在finally逐项写实际事实；预留至完整自然归还，不能再发生“脚本错误即丢局部owner”。若此观察器门尚未审清，连这两个只读客户端也不启动。

不建议现在新增PC STATUS/OP连接：会消费原custodian accept预算，且现有状态接口没有raw/Android调用栈，不能直接回答根因。若后续确需，应单列准确同handle/操作ID、一次连接/4KiB/5秒的授权与预算，不能暗加在两次设备观测外。查询仅能观察原authority，不能成为close命令或归还替身。

## 当前原任务安全收尾与防并发

**现版本能无新增控制动作实现的收尾只有同一原任务自然归还。** 原Android owners实际归还并由同一runner发终态token、原ADB自然退出/reader&pipe真返，原decoder确认同scope，再等真实custodian/外层原句柄自然返，才能保存补充回执。已经跨55秒的结果仍是超时/失败资格，不恢复为PASS；若晚到raw被S04拦在内层，须明确证据缺口，不能凭进程消失补齐。

若原任务因S01已失去finish续办，或永久原调用/UNKNOWN不返回，现有已安装bytecode没有受审的恢复入口。不能通过新APK部署、重装fixture、外部调用finish、清空静态集合、二次unbind、重发code1、换UUID或结束宿主修复原对象。必须继续隔离/保管，等待负责人另行明确原任务处置；本分析不能承诺一定可无干预结束，也不提出立即强停。若以后需要外部进程处置，须另审“外部终止证据/非Java归还”状态，绝不能写成原closeACK或普通方法PASS；本批不执行该动作。

丢失诊断的局部owner不能恢复；将来新诊断成功、PID不见或关闭另一个新Process，均不修复其旧UNKNOWN。保持它的资源/文本预留和独立处置记录，不能拿其未知是否归还来推首case已失管。

当前禁止所有候选安装/升级和同设备新case。执行层应以设备serial＋app/test/fixture＋原scope/case建立共享pending封锁，所有入口（包括新UUID、其他窗口、修复版部署）都必须核负责人原任务处置状态及fresh完整M1，既有once只防同配置重放，不能代表跨scope准入。PID检查不能释放封锁。新构建即使获批也仅离线生成候选，不能替换在途v17。

## 后续集中修复提案（未实现）

- P1 可观测性先行：在现有生产adapter实际调用前后记录固定stage/原ownerID/scope/thread/UID/PID、bind返回类型、callback入返、unbind入返、原transact入返、runner完成请求/阻断原因；有限事件环、限长错误摘要，元数据不含媒体。记录在锁外，不增加同步回调/平台等待，不以日志当归还证明。@Before进入观察前就记录开始，30秒资格时钟与准备阶段分别呈现。
- P2 原runner一次完成请求续办：保存同一scope/method/code/result的不可变待完成请求，在首次资格检查前订阅原owner真实归还事件以避免丢唤醒；只由这些事件驱动、最多一个被强持有的非主线程finalizer，重复finish请求不能改写结果或重跑测试。实际canFinish全部成立后最多一次调用super.finish。monitor明确禁止在main等待activities，故不能把finalizer简单post到main执行super.finish。永久UNKNOWN继续pending；超时/原异常结果不得翻成PASS。若原异常发生，先保留有限错误事实，不调用可能终结进程的super.onException越过原门。
- P3 同scope原远端归还协议：fixture保留原TargetBinding身份及单次请求状态；区分原transact物理返回、原kernel拒绝与远端owner归还。若需新增查询，仅固定原handle/scope的只读快照或有界归还ACK，不再bind或重做负例。晚返只确认同一原owner；失败/UNKNOWN不允许通过新对象认领。此改动涉及fixture/app协议和预算，必须先独立审查，不能注入当前已运行对象。
- P4 原PC流归档：由唯一原reader把有限原raw增量归档，保留55秒前后同operation/handle、EOF、自然exit和每个原pipe的实际返；response资格与原资源归还分离，超时后raw仍归档但不升级结论。避免再把完整raw仅放私有内存等runDecoded正常返回。持久化故障本身要保原owner并有诊断状态，不杀/重启原进程或换reader。该提案不能追溯导出现存私有内存，也不修复诊断丢失。

不建议无证据把全部bind移到main或另开无限线程；先验证已有真实线程边界。E13A必要的false/SecurityException原unbind规则保持，不能为让finish通过而跳过、吞并原资源失败。renderer/audio/Kit、旧source/信号套件不扩。

## 直接生产边界验证计划（未执行）

| 验证 | 必须直接执行的生产边界 | 判据/替身限制 |
| --- | --- | --- |
| 真实callback countDown→finally交错 | PermissionProbe实际ServiceConnection＋BindingOwner＋runner完成门；用有限latch停在callback work与finally之间 | 首finish pending；同一callback自然返后一次原finish，无新test/owner。只跑owner九组不足以覆盖adapter/runner接线 |
| 平台调用未返 | 原bind/transact/unbind各阶段，有限平台替身扣住同一调用 | 5s/30s/55s不形成假close；返回后沿原身份续办；不另造超时原语取消Binder |
| fixture已知晚归还/永久UNKNOWN | SenderService实际端点与原owner协议、PermissionProbe响应解析 | 单次consumed不重放；晚返原ACK可更新；异常UNKNOWN绝不清零、不二次unbind |
| runner异常/迟到/重复请求 | 实际E13Instrumentation finish/onException及相同版本monitor约束 | 非主finalizer、最多一平台finish、错误/超时保原结论，永久UNKNOWN不会finish；不能仅测镜像gate |
| 主机55s前后raw及磁盘失败 | 原E13HostCase＋E9PcSupervisor原Process/reader/decoder＋真实归档器 | 有限本机子进程替身输出、自然晚退出；同raw完整落盘、原归还证明分栏；磁盘失败不丢owner。替身不是Android归还证据 |
| 防部署并发 | 准确公开deploy/case入口＋pending准入 | 原scope unresolved时新UUID也拒绝，child/install0；新once名不绕过封锁 |
| 后续Android验证 | 仅旧原任务处置完成、复审和freshM1后，由负责人新派准确单方法 | 实际主Looper/Binder/不同UID/平台unbind及runner终态验证；本机替身不能充设备PASS。按最终代码影响决定一次集中app/test/fixture或host构建，不机械重跑旧套件 |

本分析没有执行上述测试或编译，也没有断言其中任一未来实现已存在。证据索引/源码行摘录/依赖来源及旧封印核验另存 docs/coder/d1e13d；只读封存本轮文档，不封印live ledger、活对象或将来可能新增的case raw。完整报告交负责人统一选择下一批实现和必要原任务处置。
