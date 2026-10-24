# REAL_FACTS_HOST03 必需pin修复完整交付报告

2026-10-24。**静态F03必需host pin缺口已修复并取得开发限定PASS：原admit的18项缺失/非法值拒绝、合法格式错hash的原读取关闭后拒绝，以及五例真正包装器均通过。** 未取得独立B或真实LIVE验收；D1未过/M0未启。

## 来源、范围与实际差异

正式单SHA256 `81289bc20cdc19b62fb49acbc839f9fd312c5e7dd0b85ebc49367d2d556335b7`，已核当前设计/里程碑顶部。HOST02独立B原报告 `66d9fd3d87de2ca1d775f356d6a4311ca7a023e4c0ca163904fb0fb8cafc3951` / manifest `6a0ea56ab283e8c805838e94bee6bb3a31f1e0a8d105bd264b049c07561aec33` 整包FAIL保持。F01五原包装器独立根/F02纯scope在该B限定关闭；F03原为静态发现，旧B未动态注入null，不能称旧B已证明实际越权/LIVE接受。N2历史ABORT已完成，不重放，不视作本新批暂停。

仅新目录 `D:\CodexProjects\VideoKit\docs\coder\d1-real-facts-host03`。准确源差异见host-changes.diff；无冻结HOST01/HOST02/Q07改动。新增require_pin强制exact str、非null/非零、lowercase64hex；static_config明确验证hostSourceSha256，缺失仍由闭字段schema拒绝。新增Budget.read_pinned无默认digest、open前校验必需pin，之后仍由原Budget.read执行原有界读取/fstat/close及实际SHA比较。不能把必需None变普通无期望摘要读取，也不自动填当前文件hash。

普通Budget.read(digest=None)合法bootstrap用途保留。approved ref增加open前必需pin检查，原身份/长度/无条件SHA比较保持；后者原来已经无条件比较，不冒另一个null省略漏洞。sourceSeal/probe已有固定值相等门，保留且统一明确read_pinned消费。原load_pins seal回调精确path+固定SEAL，不改原采集核心。Schema同步非零摘要与准确新host const，运行时实际使用新门，非只改JSON Schema。

## 必需pin消费表

|输入/消费|实际门|说明|
|---|---|---|
|外部配置原bytes批准SHA|外部严格形状/非零→read_pinned|原外部必需门保留并明确通道|
|hostSourceSha256|static_config.require_pin→verify_inputs.read_pinned|F03本次修复；实际读后SHA比较仍必需|
|sourceSealSha256/SEAL与source30|固定SEAL相等→原seal/hash→逐read_pinned|原固定值门有效，不称另发现漏洞|
|原load_pins seal回调|准确原seal路径→read_pinned(SEAL)|重复来源读也不走optional省略|
|probeSha256|既有固定PROBE_SHA相等→read_pinned(PROBE_SHA)|原probe门已有效，继续固定源/程序|
|三批准ref摘要|闭字段/严格pin→read_ref原H身份/长度/无条件SHA|无可选None分支；新增早类型门|
|未来SDK_SHA|固定常量→read_pinned|本次没有SDK文件读取|
|runtime/Python/child/Gate及FactsBundle原来源|冻结原显式pin/来源/原对象契约|保留原实现，不无证扩报同类漏洞|

pin-consumption.json另列准确本候选host SHA及AST实际读取行号。并非所有摘要都承担文件读取：envSha比较继承快照、scope是原五字段公式等既有逻辑保持，不误套可选读取语义。固定Q07 source30/gate22、runtime helper、Capture/origin/Journal/immutable_evidence/FactsBundle不改；未新造框架/release/审批/签名/IPC。

## 一次集中实际验证

事前profile `3cf173ddd59554a5651006fc208e1b8810424a682ee64f9bed6f3403a5db964a` 冻结9项源码/配置/说明/消费表，host.py `d2fe383774f87a24f510173b2fb2801281be9e1781e2ca72eeabf42cc2c870eb`。唯一工作根selfchecks/work/**addf53b68e**。prepare仅静态核单/source seal、compile与冻结，不运行产品。worker中负例输入原bytes/hash经原admit接收，五份完整合成OFFLINE输入在任何Capture/Popen前保存原bytes/hash。所有合成hash只是离线测试绑定，不冒用户真人批准、可执行LIVE配置或设备许可。

18项实际原admit负例：缺失、null、true、false、0整数、其他整数、list、dict、空字符串、63位、65位、全大写、混大小写、非hex、全零64位、空格、换行、Unicode。缺字段准确CONFIG_EXACT_SCHEMA，其余REQUIRED_PIN:hostSourceSha256；每例只增加一次原配置读/原close，费用保留。产品原static_config拒绝，不是测试驱动预挡。

第19个负例为合法64hex但错值f×64：原admit格式准入后调用原run(OFFLINE)，经Q07原源核验，实际读取本候选host.py并完成原close，随后ORIGINAL_INPUT_HASH拒绝。原host read事件含actual字节、fstat/hash/原close，费用永久保留；无Journal/Capture/Popen/新输出目录。正确host pin另经原admit正例通过，后续五例全部在原run中实际读取并比较正确host摘要。

负例结束时原capture_origin记录0、独立只观察audit的Popen事件0、实际输出leaf不存在。Journal未构造是准确原guard顺序与无输出根的分支推断，未做额外构造器拦截，不冒独立全资源插桩。每例原返回及费用见required-pin-admit-results.json与最终readFees。普通read(None)实际正读保留；17项非法mandatory digest对不存在路径在原read_pinned门前拒绝，不新增读费用/open。sourceSeal/probe的null经原admit分别按原固定值门拒绝；自己的approved-ref null在原file open前拒绝且原file事件不增。

总109项前置/拒绝检查，包括原68项、外部全零hash1项、上述host-pin19项、mandatory reader17项、既有seal/probe null2项、seal回调错path1项和ref null1项。另保留31根predicate（20正/11负）、scope纯正golden与44负（计入109的拒绝项）、自身原ref正读/错identity/错hash（负计入109）；不把各表相加成109之外新的独立动态例，也不冒全面Q07回归。

## 五包装器与原返回

五例均实际 **admit_config_file→host.run(OFFLINE)→原Capture→原归还/归档**，不组件拼装、不fake Capture，不改H/S/BASE。每例工厂前完整tuple准入，原launch再核；固定当前候选probe原字节/hash `d49ee2f675263186de11a3825b530a5612ed2f3cc09cd3969b765da7647efb7a`。

|mode|exit|stdout读到/保存B|准确包装器结果|
|---|---:|---:|---|
|ok|0|53/53|OFFLINE_ORIGINAL_CAPTURE_PASS；COMPLETED/require成功|
|fail|7|23/23|CHILD_EXIT_FAILED_RETURNED|
|empty|0|0/0|EXPECTED_OUTPUT_MISSING_RETURNED|
|bad|0|11/11|EXPECTED_OUTPUT_BAD_RETURNED|
|over|0|270000/262144|CAPTURE_FAILED_RETURNED / PIPE_BOUND|

stderr全部0。每组唯一audit匹配、identityBound true，原wait/EOF/readers join/双流/H/Journal/control完整返回，custody/filePending均0。五原H各由原Capture正常close一次；Journal50原文件/530768B、无错误/写量未知，原close全部返回。returned或RETURNED_BOUND不代语义成功，原failure/exit/缺坏输出与截断原样失败，不授信或重试。

自身approved-ref仍正读、错fileId/错hash返回；4原file close、6次原identity完成，null摘要早拒不新增identity。早身份拒绝actual null依据原分支未到内容读，不冒API interceptor read0。普通文件fstat与跨调用正式approved ref身份契约分开，不声称普通config字节替换攻击已测。

## 预算及未运行边界

事前60秒whole/50秒停新增、8辅助含worker、并发1、读256MiB/永久输出4MiB/retry0不扩。实际worker1+五自然退出probe=6；原观察Popen总5，负例阶段0。worker1.735秒，工具完成2.4052183秒、exit0。读永久预留43,837,451B；304条费用行含299显式原读（296普通/3approved ref）及5个runtime helper16读/7,952,341B预留，metadata-only取ref身份另开原文件无内容读取。helper返回不冒逐库close监测，解释器/OS隐式页读不冒业务源读计量。

最终结果导出前永久输出预留3,347,462B，最后export203943B，最终3,551,405B；原结果ledger明确截在最后export之前，工具完整返回另记最终合计/所有显式close返回。Journal每例600000B合计3000000B不按实际530768B退款；原stream/JSON另逐open计费。整目录交付实际大小另见manifest/receipt，也须小于4MiB。事后静态来源核验和打包不是另一次产品动态测试。

自有process原identity5次完成，派生GetProcessTimes/QueryFullProcessImageNameW/GetProcessId各5；file identity6次完成，派生GetFileInformationByHandle/GetFinalPathNameByHandleW各6；GetCurrentProcess0。均来自冻结函数完整返回推导，不冒API拦截/全部OS元数据。原05/capture1/PID/session/锁/once/FAIL/UNKNOWN未查改，无OpenProcess/attach/远端句柄/kill/二close/补ACK退款。

HOST03开发根与未来 **docs/tester/D1_REAL_FACTS_HOST03_INDEPENDENT_B_EVIDENCE/fixtures/<10hex或canonicalUUID>/<mode>** 精确允许；新批mode仍ok/fail/empty/bad/over，旧根不作为输出。开发只纯谓词/字段测试tester路径，不写其根。原canonical/nonlink/dot/前缀/准确深度与新leaf规则保持。scope原五字段公式/两种entrySHA分义及SDK前位置不改，后层Gate门保持。原LIVE输入/outer命名HOST01_EXECUTION和D1_ANDROID02_CAPTURE_EXECUTION事实home规则保持。

本次LIVE verify_inputs后部/run、SDK exe/DLL读取、真实route4/8TCP/镜像127ReadFile、SDK/ADB/设备/Gradle/Git均0。三LIVE输入闭合与新FactsBundle归档正例未执行，事实层只引用已接受Q07独立B，不改其fixture白名单或写旧冻结根。实际链接/UNC/其他盘攻击和真正资源UNKNOWN未注入，原保护分支静态；不从档案重建Capture、candidate/review/q/驻留/七角色。

原LIVE58+A=25,053,680+A及Gate64/256MiB保持；宿主独立source/config/runtime/archive费用不混入58，FactsBundle额外3源读14011B/packet≤262144保留。原90whole/30Gate/20checker/15SDK/30outer/10proof与流/控制/源码各门嵌套不相加。真实执行仍需负责人准确批准新scope/时窗/原输入身份与hash、host/config、Native范围，不因本修复自动获准。

## 完整回交

准确source30 `0db36468464dcfb92c2da87de8d6bff678b09af173bb21b41ed9e3d4d58157de` / gate22 `ba8fbd645e4c8403525c111ba2943cb81f3fbf6fbfc11a9f6d7c7c5a49026f81`。package.ps1仅静态复核Q07 source30/gate22、原handoff10、HOST01原96项、HOST02原102项及本候选事前9项profile，然后逐文件清单；结果见delivery-audit.json。实际后没有改源码/profile/原结果或第二次动态运行。

完整源差异/消费表/Schema/实际原admit与包装器/原返回费用/报告一次冻结交负责人，manifest列长度/hash，delivery/notification收据清单外避循环。请求核完整包后一次独立B，开发PASS不代B/LIVE；D1未过/M0未启，主阶段/原设计框架许可/Flutter/独立Kit/P0与历史状态保持。
