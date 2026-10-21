# D1 E2C G 资源生命周期与证据边界 V1.0

2026-10-17。包根 `D:\CodexProjects\VideoKit\docs\coder\d1e2c`。本批只执行正式批准的一次原 G、六点生命周期观察及必要的有界合成逻辑验证；不启动 J/R、真实媒体或 actual full。**观察与静态代码证实完成重对象及引用环被工具保留，支持做生命周期修正；具体同步 C 后端、句柄类型因果及修正后的 OS 效果仍 UNKNOWN。旧 E2B 的 G369>256、原增量209>64 FAIL 没有被撤销。**

依据 [E2C 正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_E2C_CODER_REQUIREMENTS_V1.0.md)。原诊断 [g-lifecycle-1792172968097380400.json](D:/CodexProjects/VideoKit/docs/coder/d1e2c/evidence/g-lifecycle-1792172968097380400.json) 与六份 stage、六份 entered marker、预约、原 caller 退出回执随包保留。

## 实际 Python 与同步证据

唯一原 G 的 Python 为 **CPython3.12.14**，构建 `main, Aug 25 2026, 14:01:42`、`MSC v.1944 64 bit (AMD64)`，cache tag `cpython-312`，指针64位。`sys._is_gil_enabled` 在此解释器不可用，`Py_GIL_DISABLED` 配置查询为 null，不把缺字段写成另一个运行时或已证构建选项。

观察前读取的真实类型是 `_thread.lock`、`_thread.RLock`，模块来源built-in；本地 `threading.Condition.wait` 源码包含 `_allocate_lock()`。同一原回执保存 threading.py 与 concurrent/futures/_base.py 的原文件SHA。另 [synchronization-backend.json](D:/CodexProjects/VideoKit/docs/coder/d1e2c/evidence/synchronization-backend.json) 仅作静态文件读取，记录已安装 python312.dll 版本3.12.14、SHA `2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1` 及包内头文件hash。

本地配套 pyconfig.h 声明 NT_THREADS/WITH_THREAD，但配套头文件不等于已证明 DLL 的具体编译原语；本地没有 thread_nt.h 实现源码。没有符号/内核句柄类型追踪将某个 Python 对象绑定到某一类实际句柄。因此 `exactCBackend=UNKNOWN`、`handleTypeCausality=UNKNOWN`，不编造“每 cell 四个句柄”、固定 semaphore/mutex 类型或每对象释放会使 OS 必然下降的结论。Java FFM 在原 J 中执行，不直接归入 G 的增量原因。

## 唯一原 G 与六个固定点

原 G PID26368、creationTime100ns `134366465678168526`、owner `E2C-G-1792172968097380400`。原身份捕获一次；ZERO baseline 固定于生产 CompletionHub 两 worker 启动后、0 cell 时，其后不重置。全部采样均核同一原creation，不重启、不强制GC、不重采择低、不任意close运行时句柄。

| 固定点 | 线程 | 句柄 | 较原ZERO句柄差 | workingSetBytes | privateBytes | 工具历史重对象 / 外部Future / 弱cell存活 |
|---|---:|---:|---:|---:|---:|---|
| ZERO_CELLS | 6 | 160 | 0 | 24,637,440 | 14,954,496 | 0 / 0 / 0 |
| ONE_LIVE | 6 | 164 | +4 | 24,653,824 | 14,954,496 | 1 / 1 / 1 |
| ONE_DRAINED | 6 | 164 | +4 | 24,678,400 | 14,954,496 | 1 / 1 / 1 |
| EIGHT_LIVE | 6 | 196 | +36 | 24,682,496 | 14,954,496 | 9 / 1 / 9 |
| EIGHT_DRAINED | 6 | 196 | +36 | 24,686,592 | 14,954,496 | 9 / 1 / 9 |
| TOOL_HISTORY_RELEASED | 6 | 196 | +36 | 24,686,592 | 14,954,496 | 0 / 1 / 9 |

该观察使用实际生产 PendingCell/CompletionHub、真实 Future/callback 和 SourceAuthority，但**没有构造 Engine、Native 或 Channel**。工具history是为观察静态已确认的 Engine.cells 保留模式所设的有限字典，不能将它描述为已启动完整 Engine。累计建立9个cell：先1个实际drain，再8个并发活cell后实际drain；同时峰8，没有9活或放大容量。这里的native完成是生产cell的受控逻辑完成回调，不执行文件native IO。

ONE_DRAINED 时该cell的native_done/gated/notification_done/released均为真，SourceAuthority已注销；工具history仍强持有cell，response.cell反向边、release/on_drain闭包各仍存在。EIGHT_DRAINED 时9个cell均实际drain；弱cell9、弱Future9、弱闭包18仍活，Future完成callback列表已清空。TOOL_HISTORY_RELEASED明确清空工具history，但保留第一个外部Future；9个cell/Future和18闭包仍活，总数未降。第一个外部Future.done为真，原返回值仍稳定可读。

此结果支持“仅清字典不保证切断对象图”的事实，不证明9个cell分别占有固定句柄数，也不证明末点全部存活都由那个外部Future造成。生产对象的自引用/闭包、notifier局部、GC时机和外部所有权均需区分。原自动GC保持启用、阈值700/10/10，正常计数如实保存；未禁用GC来保高，也未强制collect来求低。计时粒度下每个sampleDuration0.0不等于零成本。

## 具体引用链与原调用者依赖

观察前四份源码完整保留于 `artifacts/diagnostic-source-before`，SHA由原诊断sourceEvidence绑定。修正后的源文件另有冻结hash，不能修改原样本假装它已经运行修正版本。

| 原引用 / 生命周期点 | 已得证据与修正理由 |
|---|---|
| Engine.cells→所有历史PendingCell | 原 Engine.private_cell 只新增，从不删除完成重对象；容量检查只数released为false，故历史表可保留64个完整重对象。需要保64审计事实，同时移除已安全排空且调用者已用完的重对象 |
| cell→response→cell | DeliveryFuture.cell是直接强反向边，真实Future自身含Condition；完成不自动解除该边。晚callback注册已由cell的decision关闭，解绑后仍须稳定拒绝而不是AttributeError |
| release/on_drain闭包 | 原Engine闭包捕获Engine/ledger/state，on_drain还捕获cell；单清_value不切断这些链。只有真实release/on_drain成功、源操作drain完成以后才可断开 |
| Future/outcome异常traceback | 真实异常及调用result的traceback可继续引用Future、cell、调用者或状态；外部持有这些对象是其合法所有权。不得修改外部Future结果、异常、traceback来声称全部回收 |
| Hub notifier/monitor局部 | 原notifier在空闲等待时保留最后局部cell；monitor due列表/循环变量也可能短暂保留已处理对象。清理只放在实际调用返回之后，不能提前还通知容量 |
| IO Future / wait临时对象 | 原 Engine.io_call 将已完成Future从pending移除；未返回的Future仍必须保留。此次无Engine/真实IO，未将IO Future纳入实际六点归因；仅检查代码，不声称其已证明为OS根因 |

`Future.done()`、`cell.released`、`cell.drained` 任一单项均不能证明notifier已退出该次发布。原_release_ready在_publish内部就置released/drained，而Hub.active/容量信用要等_notify finally。因此归档需要Hub层的逐cell静默证明，还要覆盖monitor已拿出的due处理；不能在on_drain中直接删Engine活动表。

调用者边界同样是必要条件：complete_source_response在gate后仍读取原Future.result，held open/read及Ops.gate要使用原cell，场景可能立即检查其状态，Cleanup也需检查未返回的owner。归档只在这些调用者已用完的串行安全边界或显式compact调用执行，不在任意异步完成瞬间撤销对象。

## 有据修正合同与验证范围

生产实现将活动重对象与最多64条不可变审计分开，`cell_total`单调、`cell_peak`不重置；保 `total=活动数+历史审计数`。活动重对象上限8，累计上限64，不能归档后重新获得第65个总cell配额。审计保binding、kind、native/gate/通知/回调/丢弃及private资源release事实和有界错误摘要，不保私有值、Future、异常对象、lock、闭包或Engine；它不是原文件句柄CloseTicket或关闭证明的替代。

cell归档同时要求native真正返回、gate已开、decision及注册窗口已关闭、发布完成、所有callback返回、release/on_drain成功、源authority已注销；Hub证明该cell无cells/deadlines/queue/active和monitor处理，其他cell可仍在途。提交/发布/release未知或回调尚未返回不因外层测试收尾而假恢复为可归档；已知回调错误在实际返回后仍须保留错误审计和Hub停止事实，不能改成成功。活对象、未知owner、notifier仍在调用的对象继续保留原信用和停止事实。

归档断开工具不必要release/on_drain/state/authority/hub与Future.cell边；外部Future仍保持原对象与结果/异常可观察行为，迟到callback继续CALLBACK_REGISTRATION_CLOSED。外部仍持有cell、Future、值或traceback时，并不承诺全部Python/OS对象被即时释放；本批没有第二次独立OS对照证明修正后的句柄峰。

有界合成检查使用生产方法、真实Future/callback/Hub，覆盖8活/总64、不可变历史、通知返回前不能归档、外部持有结果/异常、晚完成/取消/回调竞态、UNKNOWN保留与真实排空。原C01/C02/D01/T02–T05、A01及其它定向组保持。最终选定断言数与具体证据以交付报告及audit.json为准，不加旧E2B955、partial77或旧E2A1003/87。

## 诊断独立成本、关闭与未授予事项

六点实际原reader共6周期，外加1次原G identity查询；observer13开13关、同时峰1，信用先留后开/实际关才返，最终无UNKNOWN或pending。独立账本峰3（两Hub worker＋最多1临时observer），buffer峰8最终0。9个cell各完成一次release、source drain和callback；原Hub两线程实际join、THREAD_JOIN_PROVEN，最终CLOSED、剩余资源0。

原诊断约0.047s，六点完成后才实际关闭Hub；没有第七次OS采样。日志回执内60,966B为当时含reservation/entered/stage/report快照；最终全部g-lifecycle*.json含outer-exit为61,597B≤512KiB。backend/build/change-map/targeted等另计整批4MiB；日志/证据含seal及fixture最终精确值由freeze-summary给出，保持4MiB/2MiB。原exec调用实际exit0另存outer-exit，仅记录已观察的退出，不启动新G补证。≤60秒是停止等待与决策界；不可中断OS调用若不返回仍PENDING，不强杀/替换。本轮原返回和关闭完整。

继承的R诊断、actual/full mock wrapper、controller full及actual预约/claim入口均明确拒绝E2C范围外执行；唯一G CREATE_NEW预约不被覆盖。现有E2B许可已消费，不可转让到本批。

建议的后续有限对照方案（**本批未执行，需负责人另派新批次**）：绑定本次freeze/source hash，保同CPython3.12.14/64位和原阈值；仅一个新原G、两个生产Hub worker，不构造Engine/Native/Channel、不J/R/媒体。以轻量probe调用实际Engine私有cell/compact方法，在原调用者读取Future且Hub逐cell静默后归档；仍固定0→1活→1 drain及compact→8活→8 drain及compact→工具审计/history释放共六点，每点一次，累计9/同时峰8、外部首Future明确保留。该新实例的ZERO在Hub启动后固定，不借用旧160、不重base；同时保active/archived/total/weak refs与外部原值，逐点比较归档后的有界引用事实及OS总数，不预称固定降幅/句柄类型因果。observer临时峰1、原identity/credit/actual close具证，总决策/清理≤60秒、日志≤512KiB且计新批4MiB、fixture≤2MiB；不强GC、不重采择低，超限或未返回保原FAIL/PENDING，不追加样本。随后先交负责人审查，是否另授新的actual自有回归由负责人裁定，不自动转入full。此方案不会在本批启动。

没有test_media字节/stat/hash、真实PF/61、J/R helper、真实runs/root、NAS/Gradle/ADB、设备或下载。JNI仍BLOCKED，P0/C14及历史FAIL保持；真实授权层和唯一批次/root未批准，D1 NOT_PASSED，M0 NOT_STARTED。
