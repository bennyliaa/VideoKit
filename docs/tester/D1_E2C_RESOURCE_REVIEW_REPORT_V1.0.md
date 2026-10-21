# D1 E2C G 生命周期独立复审报告 V1.0

日期：2026-10-17。依据 D1_E2C_TESTER_REQUIREMENTS、CODER_REQUIREMENTS及负责人完整冻结交接，完成三文档、修正前后源码、唯一原G六点和1,125项既有定向证据的独立静态/只读审查。

## 1. 结论

**历史重对象引用修正在已声明的原owner串行、调用者已用完边界下可静态闭合，本轮未发现新增阻断。可建议负责人另派绑定本次冻结身份的固定六点修后OS对照。** 本报告不自动授权执行，也不把逻辑闭合等同于OS资源门槛通过。

本批六点在修正前执行，末点工具history已清空但9个cell/Future及18闭包仍活，支持断开不必要引用；具体C同步后端/句柄类型因果仍UNKNOWN。修后OS及actual full均NOT_RUN，原E2B G369>256、delta209>64和旧R519 FAIL保持。D1未通过、M0未启动，JNI/P0/C14不变。

本轮仅运行已读源码的只读verify，以及tester独立hash/ZIP/AST/配置与既有JSON核对；未新采样、运行诊断/定向/完整回归、媒体/PF、编译、Gradle或ADB，未stat/open/hash真实输入。原冻结未改，所有审查程序已返回，无本轮在途helper/worker/IO。

## 2. 身份及独立归档核验

| 对象 | 结果 |
| --- | --- |
| freeze-summary SHA256 | bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179 |
| E2C-source.zip SHA256 | 035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934 |
| 只读verify | PASS：70源码、41冻结文件、62自检归档文件、13基线；actualFull NOT_RUN/通过0、修后OS=false |
| tester独立核验 | 清单字节/SHA、ZIP成员及内容、61入口符号及原R4分配一致；六stage/entered与汇总、前四源码hash、outer-exit、change-map和本地runtime/header hash一致 |
| 新批最终额度 | fixture117B；日志/证据含seal592495B；原G诊断含outer-exit61597B，均在各自原界内 |

证据与原字节副本在 [D1_E2C_EVIDENCE](D:/CodexProjects/VideoKit/docs/tester/D1_E2C_EVIDENCE)，含six-point-before-fix-review、lifecycle-logical-evidence-review、change-and-scope-review及静态审查记录。旧E2B199记录/63源码、E2A326/53、E2231/43、E1E188/33及13基线保持，旧失败和partial77不累计为本批通过。

## 3. 六点观察：支持引用修正，不证明修后OS效果

唯一原G26368、creation134366465678168526、owner E2C-G-1792172968097380400贯穿六点。ZERO在两个原Hub worker启动后固定；该基线不是E2B PF前基线，不与完整Engine/J/R/IO场景直接相减归因。

| 修正前固定点 | 句柄 | 工具history | 外部Future | 弱cell/Future/闭包存活 |
| --- | ---: | ---: | ---: | --- |
| ZERO_CELLS | 160 | 0 | 0 | 0/0/0 |
| ONE_LIVE | 164 | 1 | 1 | 1/1/2 |
| ONE_DRAINED | 164 | 1 | 1 | 1/1/2 |
| EIGHT_LIVE | 196 | 9 | 1 | 9/9/18 |
| EIGHT_DRAINED | 196 | 9 | 1 | 9/9/18 |
| TOOL_HISTORY_RELEASED | 196 | 0 | 1 | 9/9/18 |

前1个实际drain后再建8活，累计9、同时峰8。使用生产PendingCell/Hub/Future/callback/SourceAuthority及有限history复现，未构造Engine/Native/Channel，不声称完整Engine实测。真实release/drain/callback各9次，Future结果保持；自动GC启用且未强collect，history0不推断引用全部销毁，也不把所有存活都归因于外部首Future。

六周期＋原identity1，observer13开13关、峰1/信用0；两原Hub worker实际join、账本0，G原调用exit0。约0.047s/60s内，0.0采样耗时为记录粒度，不称零成本。无第七个关闭后OS样本。

实际解释器CPython3.12.14/MSC1944/64位、built-in lock/RLock和本地Condition.wait源码具证；python312.dll及配套头文件hash已核对。配套头/类型不证明DLL编译宏或内核句柄类别，exactCBackend及handleTypeCausality均保持UNKNOWN。支持的结论是重对象/反向边/闭包被保留，需要断开工具不必要边；不宣称每cell固定4句柄或某个OS泄漏类别已定位。

## 4. 修正闭合与原调用者审查

| 审查点 | 判定与具体限界 |
| --- | --- |
| native/gate/callback/资源完成 | archive同时核native_done、gated、notification_done、全部callback实际返回、release_claimed/released、drained、注册关闭、Future完成及源op nativeReturned/done/已注销；任一单项不足 |
| notifier/monitor真正返回 | Hub逐cell cells/deadlines/queue/active/monitor_inflight均空才静默。notifier实际发布调用返回后del局部；monitor原cancel返回后清due槽/局部再退inflight，不提前宣称静默 |
| 原caller边界 | Engine只在creator线程的明确串行安全边界compact，不在on_drain中移表。完整action及finish_source读取原Future结果后才compact；此API不是任意异步调用者的自动GC |
| 外部行为 | 原Future对象/值/异常/traceback不改；只解绑Future.cell及工具release/on_drain/state/authority/hub/outcome边。late add_done_callback在解绑后仍稳定拒绝，不AttributeError；外部持有的值/traceback不承诺即时回收 |
| 计数及纯审计 | 活动重对象≤8，累计cell_total≤64，历史tuple≤64，total=active+history，peak不重置；归档不退款总配额，第65个仍拒绝。冻结CellAudit仅有界标量/tuple，as_dict独立拷贝，不含Future/值/异常/锁/闭包/Engine |
| 错误/未知 | submit/publication/release UNKNOWN不归档；callback已返回的已知错误可记不可变审计，但Hub.blocked保持。未返回native/未知owner不因Future.done、清理意图或归档而释放 |

主要源码：[PendingCell.archive](D:/CodexProjects/VideoKit/docs/coder/d1e2c/src/authority.py)、[Engine.compact_cells](D:/CodexProjects/VideoKit/docs/coder/d1e2c/src/gengine.py:154)、[Hub逐cell静默](D:/CodexProjects/VideoKit/docs/coder/d1e2c/src/notifications.py)、[Cleanup与终态统计](D:/CodexProjects/VideoKit/docs/coder/d1e2c/src/phases.py)。

针对调用者逐项追踪未发现改表破坏路径：

- 普通open/read由complete_source_response先complete/gate并消费原Future.result；Flow保存原action结果后compact，返回给调用者的值不被清除。
- held open/read在gate前gated=false，不会归档；Ops经原pending key取活动cell，gate动作返回后才compact。场景仍持有的cell标量/原response结果保持；不是刚Future.done就删表。
- 零长bridge不新增cell；短返回、zero-progress、EOF/Refused走原完成或错误路径，未返回native继续持有，正常错误消费后才到安全边界。没有为了归档添加补读、native completion或控制。
- Cleanup.release_gate只处理活动表，已归档项在归档前已证明source drain；owner_notice未把活private cell当原helper退出而释放。n32前再compact并要求活动表空，同时报告total/active/history及有界历史，保原handle关闭、worker和外部返回见证分层。

静态保证限既定有界工具调用合同。自定义并发直接调用cell方法者，也必须在原调用实际返回后才由owner compact；不能把archive作为任意外部方法还在执行时的撤销接口。新增专项的跨线程gate、notifier、monitor屏障均等原调用实际返回/join后再归档。

没有要求外部Future释放、强制清traceback或强GC来制造资源下降，也未改变原C01/C02的交付裁定、D01启动未知及原T02–T05/A01范围。

## 5. 170 lifecycle及1,125定向证据的范围

最终1,125=E2C105＋alias46＋diagnostic逻辑65＋lifecycle170＋namespace32＋observer87＋startup205＋completion153＋authority139＋recovery33＋metadata70＋unit20；一轮选定，不加旧包/六OS点/入口拒绝数。此轮tester只读审，不标为独立重跑通过。

lifecycle170使用生产Engine方法绑定的轻量probe、真实Python Future/Hub/受控线程，无Engine/Native/Channel构造或OS counter读取。核8活拒第9、累计64拒65、冻结纯审计、外部值/异常身份及既有traceback、notifier返回屏障、monitor在途、native/gate顺序、callback未返/已知错误、晚决定/取消及submit UNKNOWN。全部受控线程join、实际worker/lease关闭具证。

submit UNKNOWN专项先验证原未发表/持buffer/停止，再测试层受控排空物理资源，仍保1个未归档逻辑记录与NOTIFICATION_SUBMIT_UNKNOWN，未洗失败。已知callback错误归档后仍CALLBACK_FAILED。publication/release UNKNOWN本批是生产archive的静态拒绝条件，未冒称另做两类实际故障注入。外部Future/value保留测试是行为证明，不是OS降幅证明。

1125不代表全61 actual、修后G阈值或真实媒体通过。C#/Java只编译一次/无修复重编，未启动J/R；七CLI、两个actual API及已有G预约拒绝另列，构造守卫未进入Engine/Native/Hub/observer/Popen，不创造第2个诊断G。真实/actual/full mock/旧R入口均拒绝。

## 6. 下一批固定六点修后OS对照条件

当前静态修正和证据足以建议结束本轮引用修复审查，由负责人**另行授权**以下有限对照；本报告未启动或直接放行：

1. 绑定本次freeze/source及修后四文件身份，固定同CPython3.12.14/64位及原阈值；仅一个新原G、两个原生产Hub worker，无J/R、Engine/Native/Channel构造、媒体或full。轻量probe须调用实际Engine.private_cell/compact_cells，不能只手工clear history冒充修后生产路径。
2. 固定六点：0→1活→1实际drain且原caller用完后compact→8活→8实际drain且compact→工具审计/history持有释放；每点一次、累计9/同时峰8、外部首Future保留。ZERO固定于该新实例Hub启动后，不借旧160或后移baseline；完整保PID/creation/owner、active/archive/total/weak refs及外部原值。
3. 先等逐cell notifier/monitor静默，再归档；观察临时引用不得意外强持所有历史cell。保原有release/drain/callback证据、总数不退款及外部Future/异常语义；无强collect、重启择低或任意关运行时句柄。
4. 六样本/一个identity、单临时observer信用/峰1、实际close/原workerjoin、≤60秒决策清理、诊断日志≤512KiB且计新批4MiB/fixture2MiB。不得增加第7样本填关闭后峰；未返回保原entered/PID/PENDING，超限保原FAIL，不追加样本修饰。
5. 评价相对本实例ZERO的轨迹、修后重引用是否按合同断开及采样限界。外部Future仍持其Condition/值/traceback可以合法残留，不预设归档后OS必须等于ZERO，也不把小9cell范围未超256/+64当完整Engine资源门槛已过。修后若计数无改善，保留事实并区分引用/GC/后端未知，不自动推导某类泄漏已排除。

对照结束先冻结交负责人/测试复审，再决定是否另授新的actual自有文件全61。E2B一次full额度已消费，本批没有新actual许可；即使六点支持改进，也不能自动运行full或真实素材。完整Engine仍须原PF前G基线、G256/+64及其余全部G/J/R门槛、新鲜2GiB/日志/IO/时间/原实例退出规则。

## 7. 继承状态与交接

原61配置、452/544控制、101query、IO/32记录/24资源/6媒体/8槽、metadata/时间不扩；runtime-policy与E2B逐字节一致。未授真实启动层/唯一批次与CREATE_NEW root，历史stat/hash不当现场源版本，祖先预检不当原子防敌对替换，实际hardlink/symlink限制保留。

五产品namespace/READY变体仍NOT_RUN_DURABILITY_UNPROVEN；本机OS_DATA_SYNC_ACK工具目的不生成产品OutputToken/业务COMMIT，不宣称掉电或真实G崩溃重启。旧G369/+209和R519 FAIL不改，D1未通过/M0未启动，JNI/P0/C14不变。

报告及独立证据已保存。按用户即时发送测试报告的直接授权，完成后主动交VideoKit项目助理；通知送达另存证据。
