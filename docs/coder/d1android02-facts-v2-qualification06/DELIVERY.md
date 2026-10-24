# QUALIFICATION06 完整集中失败交付

2026-10-24。**FAIL：FACT_SOURCE_EVENT_RECORD_MISSING + V1_COLLECTOR_PIN_STALE**。唯一动态批次9.656秒，8组为1 PASS、2 FAIL、5 NOT_RUN。原外层5个Popen均返回，audit5/5匹配，新Parent custody全0；没有本批新增保留等待。全部原失败/源码/输入冻结，不在06修补或重试。D1未通过/M0未启动。

## 权威与原件保护

正式工作单SHAd61eba7f318851288d344d26af722934eee2a4fc69eec26bd5040e92fdbd64b2。仅新06目录。05来源只读封存ZIP32aadc2e6021d03f5fe780e3f2f8d0fe99a15c6cb1370223375ab8ace575e458，完整106成员/105项1062255B逐内容/hash bad0；originalCallsFinal=false/lock排除不改。**未查询05 session16942、PID、排他lock或活跃输出，旧05仍RETURN_UNPROVEN_RETAINED，不因06已知返回补绿。** 前后核04候选284、tester04独立B260、tester05静态A28项均bad0。

source31 0651323122601622751a4958ae132cc33a6f8f3f5413bcacb69dd38ff4a524aa；gate23 fcc9c66d6be539cbcc936da51178426c9b993d24017d9fdf840f8b12268fbf45；profile65 0cb910c6235faa12292e5514f3dc7d0fa4db4a696a95e0408d1b6230908d25eb；批计划 0ebebffc8772f205a2120e7369f2f1dc06dd5e05c87b1fdc4c34cbba95a24ff1；完整source计划 899d533b2b1de39023b75d1b8b79661c51d297128ca6d68070ef8d66afd8741c。runtime47f9原2056B/20CRLF、metadata2593和14依赖准确保留。源/pins/profile前后bad0，实际后未改源或驱动。

## 完整读取计划、必要pin整合与实际到达

容量函数与完整shape值按原bytes/值整合进已有source_budget.py固定pin，移除其两个分立source/gate成员；两者内容仍全部包含于现必要源，见reference/capacity-source-consolidation06.json和source-delta。不是跳过必要hash，也未复用旧报告计费或把某项真读记0。SourceBudget原正常票据/永久charge/merge逻辑保持；原Gate64/256MiB、Runner256/512MiB、control/时窗不提高。

PreparedFacts在USED之前计算全链读取计划，初始raw原读取按caller实际bytes采用入账；plan按当前封存source集合/运行时固定元数据和每个当前文件大小构建，预auth六次、Gate源码/固定helper、两次fixture真实构造前seal/script、路由、receiver、raw读取/固定child永久预留、runtime元数据/exe全部列入。明显65次或超过256MiB的模型在USED/Gate/claim/Capture/Popen前拒绝。每个Gate.source_charge在内容open前同时核原scope/path/index/kind/准确charge及原cap。

|阶段|计划次数|计划字节|原权威|
|---|---:|---:|---|
|caller-raw|1|139264|ORIGINAL_ENTRY|
|preauth|6|53955|ORIGINAL_PREAUTH|
|gate-constructor|26|364884|ORIGINAL_GATE|
|fixed-runtime|16|7952341|ORIGINAL_GATE_FOR_FIXED_HELPER|
|route-preconstructor|2|5061|ORIGINAL_GATE|
|route-validation|2|5774|ORIGINAL_GATE|
|facts-receive|5|50695|ORIGINAL_GATE|
|fixture-raw|1|139265|ORIGINAL_GATE|
|fixture-child-reservation|1|139264|ORIGINAL_GATE_FOR_FIXED_CHILD|
|fixture-runtime|2|112761|ORIGINAL_GATE|
|facts-preconstructor|2|4404|ORIGINAL_GATE|

合计**64次/8967668B**，逐操作完整表在reference/fact-source-plan06.json，区分原实际读与runtime-helper/child永久预留。固定helper16次包括两次metadata读取和14文件原helper读取义务，采用原预留计费，不冒逐文件独立close实测。原Gate receipt实写sourceHashReads=53；两个构造前持久记录分别在原constructor进入前证明已准入，其中第二个记录**64次/8967668B，与计划数量/字节相符**。该记录不证明Popen已进入，更不冒完整后置账单已落盘。

事实采集原facts_entry最终返回exit2、stdout79/stderr0，准确reason=FACT_COMPLETE_SOURCE_PLAN_ACTUAL_MISMATCH。它已通过ticket.receive到达后置对照分支，但未产生FactsBundle、review或后续生产scope。外层原wait/readers/流/H归还证据保存在children/facts/return.json及原journal；内层fact过程返回/原claim释放仅可按该冻结源已知异常路径限定推断，未有独立的完整ledger/最终release输出，不当作正常facts资格通过。

## 两处集中失败与预检缺口

**Q06-F01：一条真实child预留收费未写入新事件表。** tools/fact_collector.py第24行仍为`gate.source_bytes+=len(raw);gate.source_reads+=1`。patch06.py的替换needle前缀为两个空格，而当前原行只有一个空格，替换静默未命中且未断言。原charge没有漏收：第二个构造前持久记录64/8967668与计划相同；但事件列表按冻结代码应少一条child-reservation（推断63行），最终原对照拒绝。完整actual rows没有落盘，不把63推断伪作原观测，也不拿数量吻合冒所有事件通过。后置检查暴露了漏patch，却没有资源前验证实际各收费语句都已经走统一记录器。

**Q06-F02：V1生产者源码固定摘要未同步。** 原346项实际结果可靠落盘，214 PASS/132 FAIL；132失败均GLOBAL_FACT_PRODUCER_PIN。admission_checks.ps1的GICollectorSha256仍为9c7654af3242f7d7ba1e2598522e6ceab92f07f6fc4d193b9d023ffd1b591ffe，当前collector为2ec849ba5796bc1531996608d7411f24c075cdea0171037a351ce4263d66f595。构建只同步了Runner/adapter/origin/capture等部分具名caller pin，54项预检遗漏GICollector这一消费点。必须按具名契约完整核所有相关caller，不盲替换SDK/ABI/历史proof等其他64位摘要。本失败没有归因环境或tester。

这两项均为coder准备与完整预检遗漏；当前不补丁、不重跑。原helper输出、原exit/流、全346结果及每组状态保留。receipt原writer身份、容量与生产正常/错固件/替换验证仍未到达，不能报修复成功或沿用旧批次结果填本批PASS。

## 构造前已知拒绝与真正未知的当前实现

fixture_guard先在preflight完成完整argv/cwd/env/流选项、原seal/script读取及持久PRECONSTRUCTOR_ADMITTED，再返回绑定准确参数的唯一原构造callable。Gate与OwnedFactCapture只调用该准备好的函数；可失败guard和文件写入不再藏于原构造进入之后。collector只在即将调用保存的真正original Popen时由marker设置entered；异常分类使用该准确状态：False为KNOWN_PRECONSTRUCTOR_REJECT、True为FACT_START_UNKNOWN并保留。不是按ValueError/超时/空pid一概判安全。真实原close不返回仍保持原UNKNOWN等待，不造真实故障来测。

54项纯契约/34项原预算模型及PS解析/布尔检查通过，包含完整64计划、65/超字节模型、错误fixture source/context/options与Parent完整argv在Capture构造前拒绝，以及原构造进入前后分类的纯模型。**真实构造后UNKNOWN只做有限状态模型，没有实际注入；实际known guard拒绝夹具也未另开scope。** 纯检查未发现上面两个缺口，因此不能视为整包通过。

## 未到功能与容量边界

05原writer→console五字段receiptRef→Owner自己的原读句柄核volume/fileId/size/前后身份/hash→恢复字段→merge原delta的实现已按新根保留，前驱原receipt新读原票据8192B/1次永久预留保持。但本批未到原writer/Owner正常或替换，代码尚无该动态实证。其余旧正常资格层只可引用独立04的限定结果，不代06。

完整UTF8容量代码共享实际policy/activation构造函数，容量逻辑与shape均在已有必要source pin。纯普通模型最大局部64461B、共享249631B，7189字符独立root候选在CONTROL_ENVELOPE_CONTROLLER_65536:92503>65536资源前拒绝。该候选OS/全协议可达性未证明，未物化，不报真实溢出。生产原正常/超量构造准入未执行。

18预算辅助保留独立A可靠逐项/最终持久化及显式$false实现，并把expectedFingerprint接实际bundle解析字段；未运行，不冒18通过。V1本批214/346，不能报全通过。8/16/68服务、raw139264/128范围和原全部caps保持；正常生产identity/global、错固件、物理同字节换FileId等均NOT_RUN。

|组|准确结果|耗时|
|---|---|---:|
|qualification|PASS|1.531s|
|actual-max-facts|FAIL|1.750s|
|independent-review|NOT_RUN_DEPENDENCY|0.000s|
|production-prefix-positive|NOT_RUN_DEPENDENCY|0.000s|
|production-wrong-firmware|NOT_RUN_DEPENDENCY|0.000s|
|production-receipt-replacement|NOT_RUN_DEPENDENCY|0.000s|
|source-budget-and-reload-models|NOT_RUN_DEPENDENCY|0.000s|
|V1-regression|FAIL|6.328s|

## 一次预算、冻结与下一批

动态9.656秒<360/320，宿主实际5个原Popen均返回且audit5/5；.NET生产controller0。facts内route原Gate receipt证明原临时资源返回，fact构造返回由冻结控制路径限定推断，没有独立完整nested原audit输出，故不报全图23已执行。读取计划960MiB<1GiB，SOURCE已知数量/字节仅以原阶段持久记录为准，未冒全量物理I/O。产物≤16MiB。新Parent capture/gate/fact/file/runner custody全0；不查询旧对象，不kill/二close/补ACK退款。SDK/ADB/设备/Native route/TCP/Gradle/媒体/Git0，test_media未触及。

下一正式整批应准确修F01并断言所有变更命中、核所有手工收费节点及实际事件覆盖；同步F02所有具名生产者pin并完整静态预检，再在新scope完成目前未到的完整功能簇。本06保持FAIL冻结，不补绿、不复用已消耗scope。完整候选经负责人核后才正式独立B，当前不是可通过交测候选。D1未过/M0未启，主阶段/既定框架许可/Flutter/独立Kit/全P0保持。

manifest与ZIP在报告后生成，freeze/通知回执在hash循环外。冻结包含完整原结果及上游封存校验、计划与差异。完成主动报负责人集中裁定，不逐问题回交。
