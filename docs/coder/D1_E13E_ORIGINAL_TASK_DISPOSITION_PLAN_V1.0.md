# D1 E13E 原任务处置待审方案 V1.0

2026-10-18。依据tester E13D复审§4及E13C V1.0/V1.1。**本文件不执行处置，也不构成处置授权。** 用户已有持续真机测试授权；当前不操作设备是原任务/资源未决，不是缺少测试授权。E13E新包只离线候选，不能反向控制旧v17 bytecode。D1未过/M0未启。

## 原身份与证据切片

| 对象 | 最后已交接身份 | 不得推定的事实 |
| --- | --- | --- |
| 原批次 | UUID aeefe32f-816d-4c0b-aca7-16f76dbd45ff；runtime scope SHA116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef；ordinarySenderCannotBindCodec | UUID/SHA不是新执行许可，不能重发 |
| 原PC链 | exec42537；PowerShell39560；Java38056（16:48:05.688）；其原子ADB49540（16:48:05.953） | 仅最后实测切片，本轮没有查询当前存活/退出；新Process对象不能补原pipe/readers ACK |
| Android链 | shell14763→am app_process14765，命令绑定上述scope/方法；app14779/com.videokit.app，ps显示16:48:35，设备/host时钟不同 | 不能凭历史PID直接终止，也不把时钟差当耗时；未观测fixture/codec PID不等于从未启动 |
| 已安装 | 当时app/test v17，UID10221/10222、data inode6972/4741；fixture v1 UID10228；精确APK pins见E13C报告 | 不是当前在线事实；ordinary结果/原owner归还未证 |
| 失败诊断 | ps stdout58908B；原PID未记、局部Process/reader/pipe不可恢复；V1.1 LOST_DIAGNOSTIC_OWNER_UNKNOWN | 不是主case丢失；匹配为空不补stderr0/exit/closeACK，不退款 |

先保全原35文件pending manifest、6文件repair manifest、两份报告及通知；live ledger、活harness、将来自然新增raw继续由原owner保管，不把它们冻结成停止增长。当前未采新信息、未读取原session/STATUS或其他项目窗口。

## 两分支共同前置

负责人先固定一个处置批次与负责人/保管交接人，保持serial HA1Q6WXR + app/test/fixture + 原scope/case封锁，停止所有新deploy/case/复测/安装。新UUID、once缺席或PID消失不能解除。所有相关窗口仍用同一封锁；不联系或操作其他项目。

如未来另派fresh只读确认，必须采准确本机exe路径/启动时间/父子关系/完整scope argv与原工具handle，Android采准确包名/UID/进程名/父子关系/启动身份及active instrumentation scope；允许时以/proc启动ticks等解决PID复用，若权限/完整性不足则BLOCKED。只按旧PID或仅同名进程都不足。为每个对象单列响应/字节/操作预算及实际原句柄；已有41/55及未知诊断额度不自动续用，不用观察成功充原归还。

明确排除共享host ADB server/5037 listener、device adbd、system_server、其他Android app、其他项目、其他serial及无scope关系的PowerShell/Java。原ADB49540是该instrument客户端，不等于共享daemon；Android14765是该am客户端，不等于系统所有app_process。codec/fixture若后来出现，必须由同scope实际服务连接和UID/启动身份逐个纳入；不能按videokit通配符、整棵宿主树或相似名字清理。

## A 自然原归还

仅保管并接收**同一原handle**自然输出；本方案不新增轮询。若Android原owners真实归还，同runner必须给精确scope/method的终态；再核原ADB自然exit、原reader/pipe真返、同decoder的原authority、原custodian及外层句柄真返。每层分别记录；任一缺失保留UNKNOWN。超过55秒的资格不恢复PASS，后五方法/M3不能自动续跑。

晚raw可保存部分：原外层PowerShell自然等待完成后新生stdout/stderr/receipt、同原context实际返回事实、另经授权只读获取的现存日志及预算。不可保证部分：旧E13HostCase在55秒抛后不再print内层raw，最多64KiB原instrument字节可能只留旧Operation内存；不能承诺自然返一定导出，不能启新reader/新JVM、dump/attach或新包来认领。外层MemoryStream当前长度本轮未观察，不猜它为空。新增晚证据另出补充报告，不回写V1.0/V1.1切片。

若原finish早已被拒且无续办、同步调用不返或UNKNOWN永久，旧代码没有受审自然恢复控制入口。原E13C HostCase retainAuthority(owner,null,owner)没有custodial cleanup处理器；新E13E的stage/ACK/finalizer只属于新bytecode，不能修复旧对象。这一分支可能无限保管，方案不保证自行收尾。

## B 外部终止（仅待审，当前不执行）

必须另发**准确对象/动作次序/单次次数/响应/字节预算**，分别审批Android对象与PC对象；不能笼统批准“清理”，也不能自动升级权限/root或扩大package作用域。未取得fresh准确启动身份或scope关系、涉及共享daemon/他项目即停止。此处不提供可直接执行的kill/force-stop/SIGQUIT/外部finish命令。

1. **证据先行**：保存当前已可取得的原落盘输入、预算与原raw/有限日志；记录不可导出的旧内存/句柄损失。若原内层buffer最多64KiB无法受审导出，明确接受不可恢复损失，不造空文件或后补摘要。禁止先结束保管宿主再试着找旧reader。
2. **Android侧单独处置**：仅对fresh确认的原instrumentation/app角色和明确选择的package/UID/进程范围；包级处置会影响该package所有进程，必须审清范围，不能误伤其他任务。原fixture/codec若需处置逐项审，不从过去未见PID推定已关闭。保留实际外部动作、对象身份、结果及响应；结果只能是外部终止/状态未证，永不补Java owner.close ACK、kernel拒绝或普通方法PASS。
3. **原ADB及管道**：Android被外部结束后优先让同一原ADB/原pipe自然返回，原Java可能得到异常/非零退出。记录真实物理exit/EOF/每个原pipe归还，不能把ADB退出当Android安全终态。不得kill-server/restart-server；若原客户端仍不返，是否对这一准确客户端采取外部动作必须另列，不能用它制造正常EOF/Java ACK。
4. **旧PCcustodian**：没有同scope owner token时androidReturned仍false，即使ADB/pipe已返，旧Java/custodian仍可能保管。不能调用新包代码、反射清零authority、第二close或新Process来令旧custodian“承认归还”。当前没有安全的同scope恢复入口。如果进一步选外部结束Java/PowerShell，须分别批准并明确原在内存owner/handle丢失；先保可得证据、精确区分原Java与原PS，不结束共享JDK服务/其他窗口。原PS若因Java外部死亡而自然wait/read/close，可记这一层物理返回，但仍不是旧Java逻辑归还。若PS自身先被外部结束，其原reader/pipe不可恢复事实必须单列。
5. **行政记录而非伪ACK**：由负责人/独立审查在旧监督器之外保存同原scope的TERMINATED_WITHOUT_RETURN处置记录，originalJavaReturn=false、originalOwnerReturnUnproven=true、实际外部死亡证据/不可恢复损失/仍未知对象/预算与审查引用。**不能要求旧custodian在不具备入口时自行写该新状态**；旧内存status保持PENDING或随外部死亡丢失。外部行政记录不改旧pcClosed字段、不宣称LIVE Map自然退、不合成原finish token。

若只完成B中的一部分，尚活/未知的同原对象继续隔离；没有所有必要处置证据不能解除跨scope封锁。此分支不是自动故障恢复或测试重试。

## 丢失诊断独立处理

无准确原PID、无原.NET对象、无最终close回执，不能选择一个新匹配进程“替它结束”。原记录继续LOST_DIAGNOSTIC_OWNER_UNKNOWN；若负责人决定行政隔离结算，单独给ADMINISTRATIVELY_QUARANTINED_UNKNOWN记录、originalReturn=false及原58908B/缺stderr/exit/close的清单，保未知资源/文本预留，不用主case后来归还抵消。若没有可确定目标，不执行终止动作。E13E新observer修复只防未来再次丢失，不追溯补旧事实。

## 解除隔离与新候选准入

须同时具备：同原主任务的完整自然原返证据，或经明确选择的外部处置记录（仍保原UNKNOWN/非Java归还）；所有相关原活对象/作用范围的fresh精确证据；独立诊断unknown处置；预算保留/未知不退款方案；负责人和独立审查引用。PID消失、新文件、新UUID单独均不足。

新Guard当前源码pin ABSENT，所以任何文件不能自行解除。未来如采纳处置，reviewed-original-disposition.json固定serial/packages/originalScope、typed outcome、originalJavaReturn、caseEvidence/diagnosticDisposition/review/authorization精确digest；经独立审定后才把该记录SHA写入主机来源策略并重审准确新JAR。ORIGINAL_RETURNED只可配true；TERMINATED_WITHOUT_RETURN只可配false。新策略承认行政隔离选择，不把旧UNKNOWN抹成Java归还。

此后另派fresh完整M1确认精确已装v17 pair/fixture v1、UID/data、全局active无其他任务、原账本及产物守恒、无新在途；214483/7R7S仅历史，不预写为当前终态。重新定稿metadata、准确new scope/once/release和新预算后才考虑单一T07方法。候选18/2升级代码不会反向控制旧17；原task处置未通过时，连修复版部署也禁止。

本轮没有选择A/B，没有fresh进程查询、ADB、SIGQUIT/kill/force-stop、外部finish、重装、原session读或STATUS连接。交负责人统一审查，再决定是否及如何实际处置。
