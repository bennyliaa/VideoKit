# D1 E1C 五项集中修复独立复审报告 V1.0

日期：2026-10-16。依据E1C正式测试/开发需求及冻结整包交接，完成源码、归档、机器manifest和已保存合成证据的独立静态复审。

## 1. 结论

**T02–T05的原缺陷在本轮静态范围内可闭合；T01已有实质修复，但完成交付边界仍有2项P1残余，暂不建议另派真实本机实验。** 两项分别为seal后晚open仍可能成功交付，以及Future完成在源权威/cell锁内同步执行消费者回调。

E1C不再是事后设置pending标记：真实Future、Timer错误、private cell/buffer租用、零长入口、finished/精确绑定、真实owner/epoch、inventory/max恢复和exact_write均有活动代码及针对性检查。认可这些修复，不重开已解决的E1B问题；不能因158+260=418项合成检查通过而忽略尚缺的完成竞态反例。

本轮未重跑SelfCheck、Targeted、PF、Recover、媒体、构建、Gradle、ADB或设备任务。仅运行已检查过的只读verify及tester自有hash/ZIP/AST/既有记录解码；没有启动harness/J/R。冻结件未修改，审查工具均已返回，无本轮在途任务。D1未通过、M0未启动；宿主JNI/C14/原P0和历史FAIL保持。

## 2. 输入身份与独立核验

| 对象 | 实际身份/核验 |
| --- | --- |
| freeze-summary SHA256 | 41858f8ad1ad7c99fa37f7f52a3182c8e0bd5c625fb7ca0d8969365942caf2e9 |
| E1C-source.zip SHA256 | b4ebc5a92a80c32eee30902fc6df85980da8b20ca1c7249d3a446501bfa4d9b4 |
| 只读verify | PASS：30源码、16冻结文件、430合成记录、13既有基线 |
| tester独立归档校验 | 清单字节/SHA、ZIP成员及内容一致，61入口符号存在，N/query/时间逐行与已审R4一致 |

三份交付文档、30份源码/工具/manifest原字节副本、归档审查记录、既有回执与针对性检查、引用锚点保存在[D1_E1C_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E1C_EVIDENCE)。原E1B关系和失败证据只读保留，不用新目录中的历史E1B.dll替代有效E1C.dll。静态审查不证明编译产物在所有路径的实际行为，本轮未重编。

另只读核对当前Python运行时Future实现：set_result/set_exception在调用线程直接执行已注册done callbacks。此事实用于判定锁内完成路径，非运行反例。没有读取test_media原样本；校验中的合成.bin/.out只是已冻结归档记录。

## 3. 原T01–T05闭合情况

| 原缺陷 | 本轮判定 | 源码与证据依据 |
| --- | --- | --- |
| T01 pending/取消超时/ZERO | 部分闭合，仍阻断 | PendingCell.response是真Future，Timer产生SOURCE_TIMEOUT；held完成不交付，cancel后私有结果/租用保持至gate；普通路径也走complete_source_response。ZERO调用SourceBridge并观察J读取计数。两项剩余问题见C01/C02 |
| T02 end及handle绑定 | 静态闭合 | SourceAuthority与Engine共用RLock；validate核finished/cancelled/sealed/fence、task/version/consumer/generation及handle disposition，admit在同锁登记。负例覆盖A结束/B活、借B读A、错绑定及end/cancel两确定顺序；逻辑delegate资格不冒称OS调用 |
| T03 old布尔ready | 静态闭合 | old=True入口移除；捕获并深复制ownerInstance/epoch/export/handle/attempt/revision/receipt，提交时同锁比较当前owner，Q07 e1原请求在e2后实送。未接管合法请求与错epoch/receipt分开检查 |
| T04 恢复降计数/缺shard | 静态闭合原反例 | 两槽、PF inventory最低信用及可信q日志逐维max；较少/残缺/错身份q日志不降计数并标UNKNOWN。缺失已接纳shard显式unknownShard；inventory不可信不认“从未接纳”，无raw handle重造、无新writer |
| T05 元数据短写 | 静态闭合 | snapshot/event/global header/log/receipt统一exact_write，单次返回须等请求长度；短/None/非法/异常毒化Store，后续transaction/query/remote停止，不补写。请求/实际written/未知请求分列，Flow负例核action0/未授权RPC |

“静态闭合”只针对报告中的原路径与修复代码，不等真实媒体、异常OS、持久性或平台性能通过。源码未发现需要重新提出T02–T05原问题的证据；本轮残余集中在T01的交付时序。

## 4. 残余问题与可执行修订建议

### E1C-C01｜P1｜seal后的晚open仍可能以成功Future交付

来源：[complete_source_response:86](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/authority.py:86)、[seal:226](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/gengine.py:226)、[held gate:311](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/gengine.py:311)、[原源契约open线性化](D:/CodexProjects/VideoKit/docs/coder/D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md:32)。

新admit确实检查sealed/globalFence等；完成路径却只检查consumer.finished或cancelled。Ops.seal只置sealed=True，不取消对应cell；普通complete_source_response随即自动gate，held Ops.gate也直接调用cell.gate而不重新核源生命周期。

可判定静态反例：open先获权并建立cell→seal在同一源锁内先完成→native晚返回→complete_source_response看到consumer尚未finished/cancelled→自动gate给response.set_result。该H不再符合原S03“seal后晚H只进入关闭路径，不交已撤销消费者”。held路径是native已返回但Future未交付→seal→gate，同样可得到成功H。当前P08同时执行seal和cancel，因此cancel掩盖了只seal的反例；普通权威检查也只覆盖end/cancel。

这是静态可达路径，本轮未运行或观察到实际误交付/移动源。对于已经在seal之前线性化交付的结果不要求倒退成功；问题是seal先赢、交付尚未发生的晚open。

建议把“完成可交付”的原子裁定纳入SourceAuthority，核精确binding及当前源围栏；seal或全局源围栏先赢时晚H仅保留清理所有权，不能再完成为消费者成功。held手动gate也必须走同一裁定，不能绕过。对已经接纳的read，按既定版本/取消规则明确何种结果可交付、何种只能丢弃，不把重新admit当排空前提。

补普通open、held open的两个确定顺序：交付先/seal先，以及全局围栏先的受控反例。断言实际Future结果、deliveries、私有cell/句柄留账和唯一清理，不仅检查sealed标志；不需要真实媒体或新增平台故障活动。

### E1C-C02｜P1｜Future完成在权威/cell锁内同步运行外部回调

来源：[PendingCell.cancel:60](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/authority.py:60)、[_drain:72](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/authority.py:72)、[普通完成:86](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/authority.py:86)、[end/cancel:231](D:/CodexProjects/VideoKit/docs/coder/d1e1c/src/gengine.py:231)。

_drain在cell.lock内调用response.set_result；cancel在该锁内调用set_exception。普通complete_source_response又在authority.lock内调用cell.complete/cancel/gate，Ops.end/cancel_source也持同一源锁取消cell。当前Python运行时concurrent.futures.Future._invoke_callbacks直接在set_result/set_exception的调用线程调用已注册回调，不会自动转到另一执行器。

静态反例：消费者在该Future注册done callback；回调提交/等待另一个线程执行SourceAuthority.end/query等需要同一源锁的动作。普通完成线程持源锁进入回调并等待，另一线程等待源锁，形成等待环。即使回调只慢处理，当前完成/释放被回调同步阻塞，绕过了“外部回调锁外、有限执行”的资源收尾要求。RLock只解决同线程重入，不能解决跨线程等待；Future自身condition已释放也不代表应用的源锁/cell锁已释放。

本轮未运行该反例，不能写成实际死锁。现有测试以response.result和计数为主，没有done callback重新进入权威的有界对照，418项成功不能排除此路径。

建议在锁内只做交付资格/取消和一次性状态转换决定，消费者Future完成及其可能调用的外部回调在源锁、cell锁之外执行，使用明确有界的执行/排空规则。保留结果/callback的真实引用直到必要收尾完成；不能为避锁而提前释放或允许seal后重复交付。新增真实add_done_callback的有界检查：回调能够让另一线程访问同一权威，不依赖sleep概率，不遗留线程，不把超时强记释放。与C01一起集中修复，避免两个完成入口各走一套规则。

## 5. 针对性检查与完整回归的独立意见

选定既有证据为完整合成158项及针对性260项，共418；针对性组为逻辑权威/响应138、恢复33、短写69、通用20。未重复累计早期185/249/258、旧E1/E1B或前轮完整回归。逻辑组调用活动SourceAuthority/PendingCell/Engine.private_cell、真实Future和Ledger，不再仅比自设字符串；其“delegate资格”仍是逻辑计数，非Windows/JVM实际IO。

短写组自有writer包装分别返回0/7/8191/None/非法/异常，核Store UNKNOWN、无repair/sync、下游action0与RPC未授权；没有制造真实磁盘满。恢复组覆盖高快照低日志、部分/错batch日志、缺失已admitted shard、缺inventory、GC跨shard max及raw字段剥离；不能据这些有限负例外推断电或任意损坏都可精确恢复。

tester独立解码既有8KiB槽，核SHA、64KiB展开限额和schema3/batch/task；正常32任务与PF inventory集合相等。两槽usage和现存身份绑定q日志取max后，与外层usage一致。未调用候选recover函数或重新运行负例。这支持正常既有证据，不补C01/C02缺失的交付竞态。

正常回归为351N/83新q/18重放=452控制，输入1,573,492B/59请求、写信用655,360B、目标10/记录32、验证请求128B。452分配/544硬界、输入分配1,573,522B/59、输出/验证/180秒等未放大；未用30B不转移。新增ZERO是原零delegate数据入口，不增加媒体读取请求。

privateCells总64、峰1、retained0；受管OS峰21、媒体5、64KiB媒体槽1，两个原helper实际wait code0。S17.D attempts3/native0、C原UNKNOWN/native1在owner退出后仍保留。n32前磁盘仍为待外部见证，关闭成功来自原返回通道；不能把关闭意图当结果。均为该次正常合成记录，不保证挂起或所有异常出口也已释放。

## 6. inventory事务、元数据与预算差异

新task第一次请求的admission写PF inventory，替代该task admission写，完成再写task。inventory含batch/task/admitted、首命令与minimumUsage，PF自己首次完成包含自身inventory；因此没有新增顶层记录、控制token或RPC。通常仍为最多两次8KiB authority事务；纯元数据首请求由一事务变两事务的累计写量已披露。held先写ADMITTED、gate负责已接纳cell排空，不能在held中再加隐含第三次snapshot来声称全部完成。

这个替代解决“已接纳task记录整个丢失时无法区分未接纳”的原反例。缺shard只得已知最小信用/UNKNOWN，usageExact=false，不能将差额当新额度；活动J恢复回调也先合并G现存预留和可信q日志，再重建预算，未重造raw handle。

exact_write核type(returned)为int且等请求，bool/None/非法不当实际写事实；短写和异常均停后续effect，不补写。正常元数据requested=written=6,396,167B、unknown请求0、HEALTHY；文件峰628,999B，两者分开，不用累计写大于4MiB误报峰值超限。query仍有有界append/fsync证据/cache成本，非字面零磁盘IO；单行/100ms/文件峰/native计数需继续计入。

资源统计仍只覆盖工具受管对象；JVM/.NET基线及内部句柄不是全内核测量。requiredDurability/namespace ACK、真实源版本/guard共享、实际2GiB位置等仍未证，不能由修复或合成READY改PASS。

## 7. 下一批准入与交付状态

建议集中修复C01/C02并补针对性合成检查，在新授权批次冻结后整包复审。T02–T05已认可的修复及证据保留，无需逐小项重交或重写设计；不要原地改E1C、删除失败日志或重跑已冻结检查重置额度。

当前真实实验入口仍禁用，不能直接把SelfCheck切成真实样本。即使残余完成边界修复，仍需负责人另行审定真实样本配置、源版本证据、durability所需层级和资源口径后才能派真实实验。本报告不新增设备/媒体授权、不运行实验，不使宿主JNI/P0、正式Kit/Flutter/AAR、NAS/Android/许可和历史FAIL通过。

报告、原字节副本和审查证据已保存；无本轮自检、媒体、构建、设备或helper任务在途。E1C、E1B、C14原件未改。D1未通过，M0未启动。按用户明确授权，完整报告保存后主动发送负责人，送达状态以本窗口最终回复为准。
