# D1 E2A 适配整包独立复审报告 V1.0

日期：2026-10-17。依据 D1_E2A_TESTER_REQUIREMENTS、负责人已明确裁定的 E2A 策略及正式冻结交接，完成源码、三文档和既有归档证据审查。

## 1. 结论

**A02/A05/observer 主路径在限定自有文件工具范围内可静态认可；发现 1 项 P2 命名空间适配遗漏。实际运行时准入仍被 R519>512 阻断，不允许直接进入真实媒体/PF。** 原 C01/C02、D01、T02–T05 静态认可保持，无依据重开已闭合设计。

E2A-A01：Q09-ALIAS 仍直接打开输出根下的 C.bin，没有使用已分离的输入别名；自有合成输入与输出同根掩盖了该遗漏。独立输入/输出根下通常会得到 GUARD_OPEN_FAILED，无法验证预定 INPUT_ALIAS。需在下一集中批次修正并以分离命名空间的自有文件验证。

原实际 OS 轮 PF/n05 R 句柄基线/峰值519，超过已批准512，首源字节前停止；原 FAIL、STOP_PENDING 和清理事实均保留。1003 项 driver 自有/合成断言及另87项 Java 桥检查分别认可其限定范围，不能覆盖该资源失败。

本轮只运行已审源码的只读 verify、自有 hash/ZIP/AST/JSON 算术和既有记录解码；没有新采样、重跑自检、PF、媒体、编译、Gradle 或 ADB，也未访问真实输入的 stat/read/hash。原冻结件未修改，全部只读审查程序已结束，无本轮在途 helper/worker/IO。D1未通过、M0未启动，宿主JNI、P0、C14及历史FAIL保持。

## 2. 冻结与独立核验

| 对象 | 结果 |
| --- | --- |
| freeze-summary SHA256 | a74cceea70b94354f328cb348ef5c0dd126ce50ca1125b3d7f8fcf401c3ff37e |
| E2A-source.zip SHA256 | 9ea9be9c6a2e734e364bcc22e5946e91eab9c359474ada2870107e56d5526a50 |
| 只读 verify | PASS：53源码、25冻结文件、301自检归档文件、13历史基线；旧E2 231冻结/自检及43源码、旧E1E 188及33源码保持 |
| tester 独立核验 | 清单字节/SHA、ZIP成员/内容一致；61入口符号、逐行控制/query/时间与R4一致，全部原分配/操作与E2一致 |
| 既有32任务解码 | 8KiB槽SHA、schema3/身份、展开上界与PF inventory一致；两槽usage及可信q日志max与原完整回执一致 |
| 累计归档预算 | fixture409861B；日志/证据含seal1802211B，分别在2MiB/4MiB内，失败证据保留 |

独立审查程序、原材料副本和结果在 [D1_E2A_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E2A_EVIDENCE)。身份/归档一致不等于 tester 重新执行或真实媒体通过。

## 3. A02、A05 实现与验证限界

| 审查点 | 判定及依据 |
| --- | --- |
| 输入/输出根和别名 | 主路径静态认可。G/Java/R 精确L/C/Z映射；输入只读OPEN_EXISTING、输出CREATE_NEW、单层安全名称和祖先reparse预检；候选根不生成执行能力。Q09-ALIAS例外见第4节 |
| 输出输入物理身份拒绝 | 主路径静态认可。CREATE_A原帧携带已证明输入身份registry，原输出handle查询后拒绝重合；查询失败前保留原对象/ticket和信用，不伪称未分配 |
| opened-object版本 | G guard持有且可用，J与已分配R比对identity/length/100ns mtime；首字节前失败阻断。未分配R的分支不加r+；path/hash/样本相等不能代实际FD身份 |
| J原FD桥 | 固定Windows x64/JetBrains21.0.10，窄preview/native-access/java.io flags；借原RAF.getFD/handle，52B align4结构，unsigned字段组合，无另open/dup/close借用句柄、无read/seek |
| 原对象与close竞争 | RAF/FD强引用、reachabilityFence、inspect/close同一Handle监视器；查询失败仍返回原分配和ticket，按原close清理；不把bridge错误变成OPEN未分配 |
| owner关联 | HELLO PID核原Popen，借原hProcess核creationTime，固定Channel.owner；原私有stdout管道、request id与OPEN object/ticket一起绑定。11字段回执没有inline owner，不能脱离原Channel当独立身份凭证 |

主要源码：[Namespaces](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/namespaces.py)、[Java桥与Handle](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/JavaHelper.java)、[G opened证明及原对象登记](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/gengine.py:279)、[R原分配后证明](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/RHost.cs)。

请求HMAC和原私有管道/request id是当前可信helper合同，回执本身没有新增签名；不扩大为防敌对helper证明。J每原OPEN最多66次祖先属性查询及一次原HANDLE身份查询，位于原h+，不增加控制、RPC或媒体请求；这些元数据成本仍占原时限。

独立读取 Java 10进程/87项回执：全部实际观察退出，noInFlight=true、pending=null；缺preview为启动非零拒绝，其余原对象实际close一次、read/seek=0。close-race有真实BLOCKED监视器及线程join事实；该分支 positionUnchanged=false 是未执行常规position对比的初始值，不当成位置已改变或已证明不变。path-separation是已打开4096B对象与17B decoy路径属性对照，**没有实际rename/replace**。

namespace32项为自有文件及受控接口范围：hardlink创建WinError5、symlink创建不可用均明确保留。两个实际自有FD/fstat相同身份支持物理ID拒绝逻辑，但不等于成功创建跨路径hardlink，也不代Java/Win32 ABI证据。reparse位注入不算实际symlink/junction全覆盖。祖先预检与open之间的TOCTOU限界已披露，认可范围限本机受控目录，不声称原子锁定目录链或抵御敌对替换。

## 4. 集中缺陷清单

### E2A-A01｜P2｜Q09-ALIAS 遗留输出根/C.bin，绕过实际输入别名解析

依据：[Ops.grant(alias=True)](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/gengine.py:377)、[Q09-ALIAS场景](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/scenarios.py)、[候选命名空间](D:/CodexProjects/VideoKit/docs/coder/d1e2a/src/namespaces.py)。

Q09-ALIAS调用grant(alias=True)，当前代码仍以`self.e.root/'C.bin'`调用Native.open，再close并与PF原C身份比较。正常guard/ref/Java输入已经走Namespaces，但该分支没有使用namespace.input_path。严格分离输入与输出根后，C来自输入别名，输出根不会生成C.bin；因此该分支通常会提前报GUARD_OPEN_FAILED，而非预定INPUT_ALIAS。即使输出根有同名文件，也测试了错误对象。

现有完整回归将L/C/Z自有fixture放在同一root，因而159项不能覆盖此分离布局遗漏。namespace32验证了解析器本身，没有经过Ops.grant的这条真实调用链。本轮是静态路径反例，未运行该分支或读取媒体；真实入口仍关闭，没有声称已经发生真实源写入或产品安全事故。

建议在**原grant控制内部**经精确C输入别名解析并保留原只读open/身份/close账目，使用已证明的原输入物理身份判断。缺证明或身份变化如实阻断，不回退输出根、path/hash或构造C.bin。补自有文件的inputs/outputs不同根到Q09-ALIAS调用链检查，核拒绝原因、原对象清理及无额外N/RPC/字节请求。此项须在宣称完整61真实路径适配就绪前修正；无需重开原authority/回调设计或扩大材料请求。

## 5. observer 接线及 Store 优化

G PF/n01前建立原baseline，J/R原HELLO后注册一次，register不重置G，retire只接受原PID/owner实际退出证明并保留历史baseline/峰。已按负责人裁定固定G16/+12、J/R64/+32，其余句柄/WS/private及2GiB规则保持；旧E2-C01策略冲突已由正式裁定和接线消除。

RuntimeSampler仅creator线程、不持Engine锁、非重入的安全边界调用；原IO池观察请求observe=False，worker不会同步提交等待自己。Engine等待原Future时有界轮询并调用安全采样；0.1s到期保留原pending、停止新接纳，不重发query、不借晚返回撤销原停止。单周期snapshot先关，再逐process查询；最多一个observer自有句柄/信用，满24拒绝，close UNKNOWN保原对象/信用。J/R身份捕获借原hProcess，不关闭借用句柄。

global.log原131072B内events≤104320与metrics≤26752分别门禁，header≤1024、最多201行/每行≤128，锁内检查和exact_write；短写污染Store并在下次采集前阻断，不能追加repair。早期G行有界缓存到原log打开，n32前finish，关闭后不再采写。受控observer87项是dict/kernel/BytesIO/Future接口证据，不把mock UNKNOWN计成实际OS泄漏或已证回收。

原IO wait与observer查询/日志均占原行及整批180秒；安全边界暂不能采样、OS不返回或gap超限时只能停止/保PENDING，不保证绝对峰或180秒进程退出。正常helper顺序退出期间暂停采样，后续仍须受gap规则判断；不将暂停当持续测量。

Store增量峰优化在单G写者范围内可静态认可：真实close后stat该path，其余已关闭文件沿用已证明大小；仍开的原global FileIO取max(已证大小、有效write返回量、当前位置)，最终close计入大小。全量observe入口及自有文件最终sum对照保留，未少写/sync/事务，也未延长P12原1秒。原Store锁串行global event/metric写与计数；不宣称缓存可检测外部敌对元数据修改。第一轮mock P12时间FAIL及namespace权限FAIL均保留，不因最终PASS重写历史。

## 6. 实际 R519 阻断与下一步定位建议

原OS轮G38592/J4120/R38684（各有原creationTime及owner）采3周期，R首基线和峰均519，理由仅METRIC_THRESHOLD_EXCEEDED:R:handles。外层exit1、原witness FAIL、原观测STOP_PENDING；input ib/ic=0/0。实际J/R最终code0、Hub CLOSED、账本0；observer10开10关、同时峰1、信用0。停止路径有效不等运行时通过。

该轮fresh内存3,004,215,296B达2GiB，也不能覆盖R句柄超限。首源字节前尚未分配媒体对象，现有证据不支持把519称媒体FD泄漏；当前只有总数，**不能确定其中哪些是多余或具体根因**。阈值512和+128保持，不用mock或反复新实例采到低值洗去原失败。

建议负责人下一批先安排有限、无媒体的R启动根因定位，与A01修复合并处理：

1. 对固定pwsh7.6.5/.NET10.0.11、同一原R实例，预先约定有限阶段：最小无profile启动、加载既有E2A程序集、初始化RHost/Sandbox、首HELLO序列化返回。对照原PID/creation/owner，保留第一超限和阶段差异，不做无上限重试、强制GC后再取最低值或重置基线。诊断观察自身成本/额外metadata操作和输出额度另列，不藏入原452控制或新增身份RPC。
2. 优先检查启动加载带来的文件/事件/线程/管道资源、重复加载或未Dispose的自有对象。当前r-helper已使用-NoProfile/-NonInteractive，不能把“加NoProfile”当新修复。其脚本仍用Add-Type -Path加载预编译DLL；可将“直接按已冻结绝对路径LoadFrom加载同一程序集，避免不必要cmdlet加载路径”作为**待验证假设**，而非已确认能少7个句柄的修复。[Add-Type说明](https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/add-type?view=powershell-7.6)、[Assembly.LoadFrom](https://learn.microsoft.com/dotnet/api/system.reflection.assembly.loadfrom)。
3. 仅减少明确不需要的启动/加载和自有诊断资源；不关闭CLR/PowerShell内部任意句柄、不缩减协议证明、不改文件共享或运行时版本、不通过提升512解决。若最小必要宿主仍超限，如实继续阻断并交负责人处理策略兼容性，不能自动换产品路线或声称通过。
4. 根据已定位原因作一个明确候选修改，在新批次/目录按预定有限对照验证，原失败保留。R启动门槛满足后，才另行安排自有文件的实际OS observer完整回归，验证全程绝对量/增量/gap/日志/退出；这仍不是本报告授权真实素材。

本轮未启动该诊断、未采新指标或修改宿主。新的观察布局/启动修改和预算须由负责人明确安排。

## 7. 分栏证据与原硬界

| 证据 | 本轮复核结论 |
| --- | --- |
| 原实际OS完整尝试 | FAIL/资源阻断保留，首字节0，实际清理完成；不加入通过总数 |
| 选定mock full159 | 只替换counter值，原JFD桥/G/R自有文件IO/进程身份与退出仍实际；5线程/100句柄/32MiB为mock，不算OS峰 |
| 最终targeted844 | E2A105、namespace32、observer87、startup205、completion153、authority139、recovery33、metadata70、unit20；限定各自接口范围 |
| 独立Java87/10进程 | 单列实际自有FD探针与退出，不累加为driver1003或媒体用例 |

选定mock full runtime real reader cycles0，仅OS identityQueries3（J/R借原hProcess2、自有G句柄1开1关）。实际final global.log93462B=events92902+metrics560；回执n32前events92828，末n32事件74B仍经过cap，不能误报漏账。正常64cell排空、原J/R wait0、Hub CLOSED、账本0；受管23/24、媒体5/6、槽1/8仅工具账本，不是OS总量。

原控制351N/83新q/18重放=452/544、101query；输入1,573,492B/59，30B余量仍留原行；验证128B、目标10/记录32、输出信用655360，原时间/IO/metadata峰硬界不扩。selected metadata requested=written=6,401,375B、unknown0/HEALTHY，文件峰634207B，累计写/文件峰分开。原n32实际关闭见证关联摘要961bcd4949299644861580ca1aab4d468bd105d8c876a2e529c249b3044aafc2；磁盘READY_TO_CLOSE本身不证明关闭。

## 8. 下一批与现场硬条件

集中下一批应修正A01并定位/减少R不必要启动句柄，再以新冻结整包交tester复审；不追加无新反例的旧设计修复。没有支持直接真实执行的结论。

后续仍须另受审的唯一批次/全新根/冻结SHA授权层，现场原opened-object/共享/版本与新鲜≥2GiB，以及实际G/J/R全程资源门槛、原日志/时间/退出未证规则满足后，才考虑真实首字节。当前包REAL_IO入口固定关闭，不根据approved JSON或mock解锁。

31源NONE、30输出限定OS_DATA_SYNC_ACK目的保持；五产品namespace/READY变体继续NOT_RUN_DURABILITY_UNPROVEN，无产品OutputToken/业务COMMIT。Q06不冒称G死亡重启/断电；历史stat/hash不作当前源版本。JNI/C14/P0/历史FAIL不变，D1未通过、M0未启动。

报告与独立证据已保存；按用户即时发送测试报告的直接授权，完成后主动交VideoKit项目助理集中处理，通知送达记录另存证据。
