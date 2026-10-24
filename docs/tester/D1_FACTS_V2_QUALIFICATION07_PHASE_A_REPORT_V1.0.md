# QUALIFICATION07 冻结06全计费与消费点静态A报告

2026-10-24。结论：静态A完成，冻结06存在已确认的子raw计费事件遗漏、共享消费者collector pin过期，以及route显式自读未纳入完整读取计划的义务。未执行产品动态测试，不签07或06功能通过。D1未过/M0未启。

## 范围与核验

依据07 tester要求（SHA256 0a72b09818fe35b45ef11881a9107a173bf52f3e3a9f80187bdcf1991a1e6185），仅读取06封存ZIP固定字节。ZIP SHA256 `250c98231da3df0ae87e9f99f733e030a15de6d25c0ec8adf4a3531e3e4e4fd5`，133唯一成员；内部manifest `68dd9820be6eeaf585cbe22793f8a4bc4a1b279acc6356ced0d6dcaa4b8d2e1d`，132项4654998B逐内容核对bad0；报告 `d7773dd5c2747bd77a720de4849c302ab0ccdb47a840a820056b54aa010aab82`、source31 `0651323122601622751a4958ae132cc33a6f8f3f5413bcacb69dd38ff4a524aa`、gate23 `fcc9c66d6be539cbcc936da51178426c9b993d24017d9fdf840f8b12268fbf45`均一致。

提取73项代码、契约及构建文本到本批sealed-code，未物化work或evidence动态输出目录。无产品import/dot-source/函数调用、Gate/Capture构造或产品进程；不读07浮动源、旧05活动输出/锁/PID/session。SDK/设备/Gradle/Git0。读取ZIP所有成员仅为封存完整性核验，不作为动态返回证据。

证据根：D1_FACTS_V2_QUALIFICATION07_PHASE_A_EVIDENCE。AST/文本枚举39处相关属性初始化/修改、180处文件/来源操作调用点、121次64位摘要字面出现及15处PS计费相关文本位置，保留原行号。此为固定源码范围枚举，不声称穷尽解释器/操作系统物理I/O。初次closure脚本因本机默认GBK读取UTF8证据失败，显式UTF8后通过；仅tester文件分析，无产品资源消费。

## A01：实际收费与事件表分离，后置检查不能代资源前覆盖检查

fact_collector.py:24直接执行gate.source_bytes+=len(raw);gate.source_reads+=1，未通过source_charge追加child-reservation事件。费用确有累计，不能报告漏收或退款。patch06.py的替换needle含两个前导空格，原行只有一个；replace没有命中断言，静默保留旧语句。语法通过、计划总数匹配与构造前总计都不足以证明事件完整。

facts_entry.py:82检查总读数、字节、事件长度；只有该检查通过才在84–86写完整事件分块和summary。故不能把静态推导的63行称为06实际完整事件落盘。若其余各步骤成功返回，原64收费对应63事件，其中child预留缺一；具体原完整ledger仍未提供。本次未重放06来补证。

完整计费修改点分类如下，明细见all-source-mutations.json与consumer-closure.json：

|位置|费用归属与记录|静态判断|
|---|---|---|
|PreparedFacts 116–127|私有原raw采用与六次preauth；sourceEvents随读追加|携入Gate seed，不能二收；初读界检查在读后，不冒所有I/O均在总计划前零进入|
|Gate 66–67|从seed事件计算初值|初始化不是消费退款；同scope种子必须完整|
|Gate 98–104、112–130|runtime16预留与普通source_read统一source_charge|cap/行scope/path/kind/index/amount读前核；普通读记录actual/close，runtime只标fixedHelperReturned，不伪造逐依赖close|
|collector 24–25|raw child永久预留，直接改两计数后检查|事实完整计划事件遗漏，修复应在统一预留入口先检查再收费与记事件|
|Gate 258–261 LIVE|已知native量走source_charge；否则直接累计known与reservedUnknown|未知/零量分支没有source_event，且处于route返回后；应明确失败保留和未知预留记录，不把它当成功完整账表|
|Runner 45、89–95、117–118|256读/512MiB，普通source及原receipt读各自先预留|有原operation/receipt返回记录；属于Runner权威，不强行塞入fact64事件图|
|SourceBudget 20–23、35–45|原Gate/Runner共同永久预扣；ticket/events与子PS delta并回|有独立既有票据，不是child漏事件的同类裸收费；不双记成新实际读取、不退款|
|SourceBudget 50–60|fixture probe先收Runner 2B/1读，Gate再source_read|有限probe单独记录；拒绝65应保持计数，不能用fact完整计划模板盲套生产probe|
|V2 host facts_qualification 15–17|_SOURCE_READS按实际读取后追加，8192/512MiB|宿主独立来源域，非原Gate64；若要求读前预算拒绝需用现有读入口预留，不能归因本批已经超限|
|PS GIV2ReadReference/Reserve/GetDelta|先票据预留，actual/read/close后增量|与原SourceBudget ticket绑定并回；观测与保守预留分别记录，source/control不可混算|

pure_budget06.py中的归零/增量是有限模型状态，不能据其文本误报产品账本被重置。本次未执行该模型。

## A02：完整读取义务及分支表

独立以提取文件长度、固定runtime声明及封存raw条目核64行逐项字节，见independent-row-byte-verification.json；未查询外部runtime或SDK文件。普通read收费L+1，preauth/adopted/runtime/child按声明或实际L，全部维持原cap。

|RAW_FILE阶段|次数|字节|归属|
|---|---:|---:|---|
|caller-raw|1|139264|entry原读采用|
|preauth|6|53955|私有seed|
|gate-constructor|26|364884|manifest+23pin+helper+metadata|
|fixed-runtime|16|7952341|原Gate为固定helper永久预留|
|route-preconstructor|2|5061|seal/script|
|route-validation|2|5774|script/contract|
|facts-receive|5|50695|seal/binder/collector/CLI/plan|
|fixture-raw|1|139265|父raw|
|fixture-child-reservation|1|139264|子raw已收、漏事件|
|fixture-runtime|2|112761|metadata/exe|
|facts-preconstructor|2|4404|seal/script|
|冻结实现计划合计|64|8967668|不是本次动态ledger|

route_fixture.py:13显式读取自身脚本1819B；父pin/guard/返回校验读同文件不能抵消子自读。这一义务不在上表，若纳入完整显式费用则RAW65读及8969487B，超过原64门。它在06冻结后上一份A才交达；不倒改06原64账面，也不把新静态义务伪作当时漏收的动态观测。

COMPLETE分支没有entry raw采用、父raw、子raw三读，账面61读8549875B；加route自读为62。LIVE无fixture guard/三项raw/runtime fixture分支；当前源码计划为6 preauth+26 Gate+16 runtime+1 auth+1 native+2 route+5 receive+1 SDK=58读，另有win32_route.py:489显式读取自身，完整显式义务为59。LIVE字节依实际授权长度与最终固定源/runtime重新算，不移用RAW字节；本次无LIVE运行或native返回结论。

route上下文、CLI template/policy、proof/receipt及写账分块属于控制域；运行时14依赖加metadata两次已预留，不把它们当新增未计16读。fact_fixture.py:9只有RAW_FILE显式raw读，已对应child预留；route_model没有额外显式文件读。解释器导入与OS元数据另属未测范围。

## A03：具名来源闭包与共享消费点

source31逐hash、gate23逐hash均一致；Runner SOURCE_FILES与PS srcKeys完整31集合一致，gate23是其子集。release policy七项入口/owner/gate/runner/runtime metadata/runtime helper/七角色plan摘要均匹配。29处可准确关联当前来源的产品字面摘要消费点，仅collector过期；121次全范围字面出现均留档，SDK、ABI、产品及历史proof等非来源摘要不能盲替换。

|具名消费者|生产者|结果|
|---|---|---|
|GICollectorSha256，admission_checks:158、182|fact_collector.py|旧9c7654af…1ffe；实际2ec849ba…f595，不一致|
|GIFactPlanSha256|reference/fact-plan.json|一致|
|GIV2AdapterSha256|facts_qualification.py|一致|
|GIV2CaptureSha256|outer_capture.py|一致|
|GIV2OriginSha256|capture_origin.py|一致|

影响不应只标V1：GIQualification在V2时先GIV2LoadReference，随后V1/V2都进入GIQualificationExpanded02，182的collector/factPlan/SDK校验共用。静态上，合法带当前collector的V2在前置全部成功后也会触该旧pin拒绝；不能冒充06已实际跑到V2失败。构建patch末尾只同步Runner/adapter/origin/capture，漏collector正是闭包不完整。

来源链包括collector原receipt sourceSha256→facts_contract按封存seal/load_pins校验→FactsBundle与适配器输出→PS V2 reference展开与共享GI producer pin；另有Runner sourceSeal/permit sources→Gate manifest→Owner与PS入口/owner/gate pin。动态scope、review、receipt、product授权摘要还须在最终候选原数据上核，静态集合一致不替代其验收。

qualification_reference.ps1的11个具名函数与admission_checks中的内联函数段（去尾空白/换行差异）逐段一致，包含GIV2LoadReference与SourceBudget三个函数；不只检查独立参考文件。详named-pins-and-inline-copies.json。容量已合并到source_budget.py，最终pin/数据值也需随来源闭包冻结；本次未执行其函数或将声明consolidation报告当功能证明。

## 最小资源前预检与后续

使用现有构建与source_charge/票据机制：每次patch先断言准确匹配次数，写后AST核目标收费不再绕过记录器，不能只compile或查目标字符串存在。逐入口携入、runtime预留、两guard、子raw、两种route自读建立完整有序义务表；在USED、claim及产品构造前核完整费用。记录已预留、实际返回、actualBytes与unknown各自含义，原64/256MiB及其他caps不扩。

对每个具名生产者建立消费点映射，最终字节算hash后更新全部消费者和内联副本，再按依赖顺序重算gate/seal/policy等摘要；替换0次/多次、残余旧pin、遗漏消费点或副本差异应在产品资源前失败。保留参数/来源/环境/文件身份等必要校验，不全局替换任意64位文本。不新增诊断、IPC或账本服务。

新增oracle.json为最小分支判据，全PLANNED_NOT_RUN，沿用05驱动A及此前规划但不重复执行全部组合。后续正式B必须重新绑定07最终API、路径、hash、预算与状态分类，覆盖真实完整账表、V1/V2 producer pin、原receipt同fileId身份、控制容量、生产正负链及18辅助。开发最多两版新scope授权不构成本tester动态许可。A交负责人后停止，不自动B；旧FAIL/UNKNOWN/once/custody与原05RETURN_UNPROVEN不读改、不强停收尾。
