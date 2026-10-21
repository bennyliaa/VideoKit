# D1 E2B 别名及资源整包独立复审报告 V1.0

日期：2026-10-17。依据 D1_E2B_TESTER_REQUIREMENTS、CODER_REQUIREMENTS及负责人正式冻结交接，完成三文档、活动源码、固定诊断与唯一实际回归归档的一次独立审查。

## 1. 结论

**原 E2A-A01 可闭合；两实例/八阶段 R 对照及一次性回归门禁具证。本轮未发现新的功能性源码阻断，但实际资源准入明确失败：G369>256，原基线160的增量209>64。** 不直接安排真实媒体/PF，也不能补跑已消费的实际回归。

本轮只认可955项定向的各自范围；唯一actual full是FAIL、完整通过0，停止前77项不累计为通过。候选R诊断499、实际回归自身R501均不能覆盖G的失败；旧R519、本批对照513及本批G369分别保留。

G超限的优先静态线索是已完成PendingCell/Future/同步对象在Engine.cells中继续保留；当前代码及CPython参考实现支持将其作为下一批有限诊断假设，**尚无本机句柄类别或精确归因证据，不认定“已证实泄漏”**。建议先做小规模自有资源生命周期定位，依具体证据修正，不提高256/+64或重置PF前基线。

本轮仅只读verify、自有hash/ZIP/AST/JSON及既有槽/日志解码；未新增采样、诊断、自检、媒体/PF、编译、Gradle或ADB，未stat/open/hash真实输入。原冻结未改，审查程序全部返回，无本轮在途任务。D1未通过、M0未启动，JNI/P0/C14/历史FAIL保持。

## 2. 冻结及独立核查

| 对象 | 结果 |
| --- | --- |
| freeze-summary SHA256 | 93941847231390a5ffe4af8656cb5ce8d3120b9c07a16dcf55fcc9d802bf9ab0 |
| E2B-source.zip SHA256 | 05eef8aa55013603070fc9fd77ac2adb6ff916ab73825ef7f8e6456ad9a26c43 |
| 只读verify | PASS：63源码、27冻结文件、172自检归档文件、13基线；actualFullStatus=FAIL、actualFullAssertions=0、targeted955 |
| tester独立核验 | 清单字节/SHA、ZIP成员及内容、61入口符号/R4分配一致；诊断与reservation/claim的原文件/规范摘要、DLL/policy绑定一致 |
| 本批最终归档 | fixture135402B；日志/证据含seal1208703B，分别在2MiB/4MiB内；诊断含summary20698B≤512KiB |
| 失败前记录解码 | 11个实际admitted任务与PF inventory一致；槽SHA/schema3/身份/展开边界及usage/q日志max一致，不要求未执行的32任务全部出现 |

证据在 [D1_E2B_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E2B_EVIDENCE)，含原材料副本、archive-and-manifest-audit、alias-active-chain-review、fixed-r-diagnostic-review、single-use-admission-review和actual-partial-failure-review。上游E2A326记录/53源码、E2231/43、E1E188/33及13基线只读保持。完整性PASS不等运行时通过。

## 3. A01 修复闭合

[Ops.grant](D:/CodexProjects/VideoKit/docs/coder/d1e2b/src/gengine.py:371) 在原Q09-ALIAS/n01内取得Namespaces.input_path('C')及原绑定物理身份，不再查输出根C.bin。先add_object登记G原资源，再更新实际open/query返回的owner/object/ticket，身份未证或变更时阻断；finally执行原close。close未知保UNKNOWN/原ticket/Native.owned/信用，不把已打开对象退款为未分配。

四个活动链自有文件case、46项既有证据经过生产Flow/Ops、Namespaces、Store、G Native，输入/输出实际分离、无输出C副本：normal→INPUT_ALIAS；query-failure→BLOCKED_VERSION_NOT_PROVEN；identity-mismatch→SOURCE_VERSION_IDENTITY_CHANGED；close-unknown→GUARD_CLOSE_UNKNOWN_NO_RETRY。每case1N、0RPC、0字节delegate/新目标，原只读OPEN_EXISTING/share1；setup原C证明的额外open/query/close另列，不偷记为原控制免费动作。

合计实际open8、实际identity query7＋注入查询失败1、close8，metadata58154B/事务7（2/2/2/1）。query/mismatch/隐藏close返回是受控注入，不是真实OS故障或换版。close-unknown先保原UNKNOWN，再凭测试层独立保留的真实close成功返回退休，无第二次close；不能把这种测试收尾用于生产未知推断。最小Engine double省略helper/observer启动的范围已披露，且唯一actual full未走到Q09-ALIAS，不能写全61实际验证完成。

因此闭合原A01的具体分离布局遗漏，不扩大到真实素材版本、敌对目录替换或实际跨路径hardlink/symlink验证。既有A02/A05、authority/回调、D01、T02–T05主路径认可保持。

## 4. 固定 R 诊断与因果边界

预定reservation在首进程前CREATE_NEW；固定Add-Type与LoadFrom各一个原R实例，同pwsh7.6.5/.NET10.0.11、同E2B.dll SHA06befb5eee245e4d90ca5c91b35b50093cde9cd30bb639a242295f613fc01ac8。四阶段有真实同步暂停；INIT_COMPLETE共用RHost初始化，HELLO_SERIALIZED在实际序列化、Wire.Pack及缓存登记后暂停，不伪造阶段值。

| 方法/原PID | MINIMAL | LOAD | INIT | HELLO句柄 |
| --- | ---: | ---: | ---: | ---: |
| ADD_TYPE/14880 | 498 | 511 | 511 | **513** |
| LOAD_FROM/39424 | 497 | 497 | 497 | **499** |

各阶段PID/creationTime/owner一致，并由reader核原创建时间。首超限Add-Type/HELLO/513>512保留。两方法各自增量+15/+2及HELLO相差14只是本轮总数差异；最小启动本身不同，未枚举类型或随机化/重复因果实验，不宣称LoadFrom稳定节省14个句柄、彻底解决所有宿主资源问题或消除历史519。

生产R候选只改绝对DLL的LoadFrom和自有启动路径计算/存在检查，不换runtime/flags/owner，不强GC、任意关闭CLR句柄或放宽阈值。候选诊断HELLO499符合R绝对门槛，因此满足负责人已限定的一次自有actual回归启动条件；诊断MINIMAL不是实际运行的baseline。

独立成本：2进程、8metric样本、2借原hProcess身份查询、4 HELLO/EXIT请求、8 ACK，诊断native worker1、每实例transport reader2，单列而不藏原452。observer16开16关、峰1、信用0；ledger峰11/最终0，两个原实例exit0、reader及native worker已join、unknowns空。总约1.203s，阶段/实例/总5/30/90秒内；计时0.0不等零成本，不可返回OS仍只能PENDING。本轮诊断未重复或增第三实例。

## 5. 一次性 reservation/claim 与原失败

[synthetic_admission](D:/CodexProjects/VideoKit/docs/coder/d1e2b/src/synthetic_admission.py) 与外层run-selfcheck先校验原诊断文件/规范摘要、DLL及policy，启动G前CREATE_NEW reservation；原G再核原父PID/runId/身份并CREATE_NEW claim，先于fixture/Native。真实profile先拒绝，不消耗或绕用此许可。原launcher26784/controller36192与witness claim一致，reservation/claim原文件hash绑定及第二次拒绝证据一致。

失败不退还额度。归档只有一次run-selfcheck，无本批mock full；第二reservation拒绝且原记录不变，无新helper。纯JSON门禁65项是逻辑验证，不代实际OS阶段事实；该一次性机制限本次自有SYNTHETIC，不构成真实批次授权器或产品安全能力。

唯一actual full：原G36192/J13856/R31884，各有本轮独立creation/owner；mode ACTUAL_OS_OBSERVER、mock=false、exit1、witness FAIL。完成PF＋19分支共20行，P09-TIMEOUT进行中在seal控制后的安全采样点触发：

| 原角色 | 基线句柄 | 已采样峰 | 判定 |
| --- | ---: | ---: | --- |
| G | 160 | **369** | 绝对超256，增量209超64，STOP_PENDING |
| J | 268 | 268 | 本轮该部分范围未超限 |
| R | 501 | 501 | 本轮原HELLO门槛满足，不借诊断499作baseline |

第4周期的两条G失败原因和原峰保留，未用清理后的低值覆盖。正常日志3条metrics＋header396B，触限周期在原observation/preclose/failure保留；不是少采到第4周期。gap约1.687s；reader4周期、14开14关、峰1、信用0/无pending；fresh内存2454781952B≥2GiB，但不能覆盖句柄失败。采样峰不等绝对内核峰。

原J/R实际wait0，44 private cells排空、Hub CLOSED/worker join、信用0，global.log flush/fsync/close已证、最终账本0、外层noInFlight=true。清理通过只证明原资源收尾，不把业务UNKNOWN或本次执行FAIL改PASS。

部分usage为127N/23新q/1重放、输入1573188B/44、validation0、目标0/记录11、output信用0。partial77不加955；未运行分支保持未完成。metadata累计requested=written2593620B、unknown0/HEALTHY，最终元数据文件sum/峰234324B；日志36951=events36555+metrics396，n32前events36481＋末事件74吻合。原关闭见证关联SHA623bc77602fdb668336b1955f54db74cf57724e0846a5573e831963f14664f02。磁盘关闭意图不单独当close成功。

## 6. G超限：优先静态线索与有限下一步

当前证据只证明原G计数从160上升至369并触限，不能确定泄漏类型。正常metrics在0/1000/2000ms分别是G160/192/192，随后失败峰369；线程峰仅11，受管峰21/24。两栏差距要求定位G内非媒体资源，而不能用ledger0或把J内FFM原生句柄算到G来解释。

优先检查下列具体生命周期：

1. **已完成cell的同步对象保留。** [Engine.private_cell](D:/CodexProjects/VideoKit/docs/coder/d1e2b/src/gengine.py:118) 将每个cell保留在self.cells，release后没有移出该历史表；[PendingCell](D:/CodexProjects/VideoKit/docs/coder/d1e2b/src/authority.py:92) 每个包含RLock、DeliveryFuture的Condition和drained/decided两个Event，release/on_drain闭包及Future.cell也有引用关系。最后44 cell均released并不等于这些Python同步对象已销毁。该累积与增长时段相符，足以优先验证，不能凭数量直接声称每cell恰好泄漏4个OS句柄。
2. **实际Python构建与等待后端。** CPython3.12.14参考源码包含Windows锁/条件变量的semaphore模拟路径及释放函数，也存在native条件变量路径；需确认本机打包构建再归因。不能把Python Event名直接当Win32 Event类型。[CPython thread_nt](https://github.com/python/cpython/blob/v3.12.14/Python/thread_nt.h)、[condvar实现](https://github.com/python/cpython/blob/v3.12.14/Python/condvar.h)、[构建条件定义](https://github.com/python/cpython/blob/v3.12.14/Include/internal/pycore_condvar.h)。
3. **Future/异常与回调引用。** 查已完成IO Future、Future异常traceback、cell.on_drain/release和旧Flow线程局部对象是否在完成后仍被历史字典/闭包保留；native/gate/callback真正完成前不得清理。检查超时轮询与notifier/deadline的wait临时对象生命周期，区分持续持有与短暂分配，不据一个快照认定未close。
4. **自有OS对象/API账目。** 当前Native.raw guard、Store文件close、observer snapshot/process query均有相应归还路径，仍可用有限包装核开/关及借用边界与G总数差。ctypes库/函数绑定、元数据path查询、对象/缓存和线程初始化列为核查点；FFM实际运行在J，G只收元数据字符串，需先证明跨进程归因链，不能直接归罪FFM。模块引用或缓存条目数量也不自动等于OS句柄数量。

建议负责人新批次先授权**一个G、无媒体/无J/R的小规模生命周期实验**，预定有限对象数量和固定观察点，例如0→1→8个自有cell/Future、全部实际drain后的检查；样本/控制/日志/时间成本独立批准，不消耗原452或复用本批full reservation。不强GC、不反复取最低值、不关闭Python/CLR任意内部句柄；无安全观察条件则如实缺证。

如果证据指向已完成历史重对象保留，可在新批次把历史审计事实改为有界不可变快照，活动对象单独受限；只有native返回、gate完成、同步callback返回、notifier归还/实际drain且既有调用者不再依赖时才断开不必要的强引用。不得复用尚被外部Future持有的cell、提前退信用或删冻结失败证据。保留旧C01/C02/D01的交付裁定和所有权证明，针对具体生命周期改动验证，而非重做协议设计。

修正假设验证后再由负责人另授明确的新actual自有文件回归批次。该次仍须满足G256/+64、R512/+128等全部硬门槛，基线不能后移；本批一次许可已消费，不自行补跑。若必要宿主开销无法满足，保持BLOCKED并给具体兼容性证据，不自动提高阈值。

## 7. 计数、继承约束与后续现场条件

955仅为最终定向：E2B105、A01 46、diagnostic65、namespace32、observer87、startup205、completion153、authority139、recovery33、metadata70、unit20。早先955不累加，旧E2A1003/Java87不算本批；8诊断样本不冒充断言通过，actual partial77和完整0分栏。

61配置原452/544控制、101query、输入1573522B/59、输出655360B、验证262144B、10目标/32记录、metadata峰3178496B/硬4MiB、24/6/8和180/200秒规则不扩。失败轮只承认11个已admit记录，未执行尾部不要求凭空出现，也不补记PASS。原G PF前baseline、G16/+12及其余阈值、1s/201/gap2.5/返回后0.1s、现场fresh≥2GiB保持。

真实授权/启动层和唯一新root仍缺。未来须另审新冻结SHA/原owner/唯一批次、CREATE_NEW独立输出、首字节前实际opened同对象/版本/共享、现场fresh内存与全程实际OS阈值/log信用后，才考虑真实执行。继承stat/hash不是现场版本，祖先预检非原子防敌对替换；hardlink/symlink实际创建限制不作已测全覆盖。31源NONE、30输出限定OS_DATA_SYNC_ACK，五产品namespace/READY变体继续NOT_RUN_DURABILITY_UNPROVEN，无产品OutputToken/业务COMMIT、断电或G死亡重启通过结论。

本轮没有新功能缺陷清单；集中保留G资源阻断及上述有限定位条件。报告及证据已保存，按用户即时发报告的直接授权完成后主动交VideoKit项目助理，送达记录另存证据。D1未通过、M0未启动，JNI/C14/P0/历史FAIL不变。
