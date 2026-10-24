# REAL_FACTS_HOST03 独立离线B测试报告

2026-10-24。**限定PASS：F03在本批原公开准入、必需读取通道及格式合法错摘要的实际run中关闭。** 五例完整包装器、根与纯scope回归通过，未发现新增缺陷。结论只适用于本次冻结HOST03离线范围；不构成LIVE批准或D1通过，M0未启。HOST02静态FAIL及原结果保持。

## 来源与一次执行

正式派单SHA256 `c7c27d2ec24c3ef4b7ca4eb3e62a44abe095505306cbc7a84d0683c7339dcac2`。候选`docs/coder/d1-real-facts-host03`，manifest `5994bf8fb81b81d37901a78dcfc8a35721f218d67e56217f86adf351dcfe026f`；126项1194624B前后逐项核验一致。REPORT `7e9ad8575dac4143bbf51c4b2c6da74911e604d2715ba156aca380d9a1b92e51`；host `d2fe383774f87a24f510173b2fb2801281be9e1781e2ca72eeabf42cc2c870eb`；profile `3cf173ddd59554a5651006fc208e1b8810424a682ee64f9bed6f3403a5db964a`。Q07REV2 source30 `0db36468464dcfb92c2da87de8d6bff678b09af173bb21b41ed9e3d4d58157de`、gate22 `ba8fbd645e4c8403525c111ba2943cb81f3fbf6fbfc11a9f6d7c7c5a49026f81`保持。

独立新根为`D1_REAL_FACTS_HOST03_INDEPENDENT_B_EVIDENCE`。完整201项源/程序/输入/runtime、环境及tuple在动态前冻结，order SHA `6927636e0f23f686f6b3a85a9e6944098279002da7530ec2226f2a5b5cf6c9f7`；事后201项全部核同。环境固定SYSTEMROOT/WINDIR/TEMP/TMP，实际子调用env=None继承准确环境。源未复制或改BASE，未运行开发selfcheck。

实际输出为新`fixtures\6c25f391d5\<ok/fail/empty/bad/over>`，五个leaf事前不存在。probe固定为候选selfchecks/probe.py，SHA `d49ee2f675263186de11a3825b530a5612ed2f3cc09cd3969b765da7647efb7a`。五主链都是原`admit_config_file→host.run(OFFLINE_HOST_PROBE)`，父侧原Capture只观察本批worker，不替代主链。worker1+probe5共6辅助，串行1/retry0；worker1.265秒、原父侧1.781秒，全部原返回，无第二worker或补跑case。

## F03关闭证据

18份缺失/非法hostSourceSha256配置均以冻结原bytes及其独立外部期望SHA直接送入产品原admit_config_file。没有由测试驱动预先筛掉配置：缺字段由CONFIG_EXACT_SCHEMA拒绝；null、bool、false、int、float、list、dict、空串、63/65长度、大写/混合大小写、非hex、全零、首尾空白和Unicode字符由REQUIRED_PIN:hostSourceSha256拒绝。每份原配置实际读闭，费用保留；无输出leaf、新registry/capture或archive费用。

第19份配置使用格式合法的错误摘要`1`×64。原admit实际接受后，继续原run：读取已封存核心并实际读取本候选host.py，原fstat/close返回后以ORIGINAL_INPUT_HASH拒绝；最后读费绑定host.py，原关闭已证。未创建该负例输出leaf，未到Journal/Capture/子程序工厂。这不是仅校验摘要形状，也不是用测试驱动拒绝冒产品门。

required reader的10种非法值各直接调用原read_pinned及read_ref，合计20项均在路径检查/预留/open前拒绝；使用的是自己根下未创建文件，预算和原文件事件不变。另1项证明read_pinned省略digest实参即TypeError，签名无默认；1项实际普通Budget.read(None)及正确read_pinned读取同一自有文件并关闭成功，共22项。保留普通bootstrap用途，没有把所有输入拒绝当修复。

源码核`read_pinned`先require_pin再调用原read；static_config强制host pin，verify_inputs消费同一字段。ordinary read/write/reserve原方法AST与HOST02一致；approved ref除新增首行必需pin门外，原身份/长度/无条件SHA方法体AST一致。旧approved ref原本已经无条件比较SHA，不另冒null省略漏洞。旧HOST02未实际注入null的事实不改。

## 必需摘要消费闭合

独立消费表与原调用行号保存在post-audit.json；全宿主只有read_pinned内部一处self.read，未剩余必需消费者直接落入optional digest=None。

|输入|准入与实际消费|本批证据边界|
|---|---|---|
|外部config SHA|原公开外部exact str/nonzero lower64；read_pinned|实际正确/缺失/错误外部摘要及19份配置|
|hostSourceSha256|static_config require_pin；verify_inputs read_pinned|18非法、1错内容、五正确run均实际|
|sourceSealSha256/SEAL|原固定相等；load_core及pinned_seal_read固定SEAL|实际load_core；LIVE回调静态|
|source30各摘要|原SEAL绑定manifest；逐项read_pinned|实际加载及最终逐项hash|
|probeSha256|原固定PROBE_SHA相等；固定摘要读取|实际五包装器与错值拒绝|
|三个批准ref|原LIVE闭字段/类型/准确path/require_pin；原身份与无条件SHA|自有ref正负实际；LIVE三输入正链未运行|
|SDK_SHA|固定常量read_pinned|仅静态，未读SDK文件|
|runtime/Python与child/core来源|原冻结helper/核心具名pin|原runtime返回及冻结核验；不冒逐OS隐式读插桩|
|FactsBundle源/packet|原origin/decode_entry不可变绑定及额外预留|静态/引用已审Q07；新LIVE归档未执行|

Schema host const核本候选实际host hash、必需字段保持，ref非零规则与运行时门相符。JSON Schema仍非执行批准；上下文约束以原公开准入路径为准，未把内部已校验域外任意对象夸作新增漏洞。source/probe既有固定值门保持，不冒此前有同类漏洞。Registry/Control/require_success及原run/spec_for/validate_scope AST均保持，Q07核心未改。

## 包装器与受影响回归

|mode|原exit|读到/归档stdout|原包装器结果|
|---|---:|---:|---|
|ok|0|53/53B|OFFLINE_ORIGINAL_CAPTURE_PASS；origin COMPLETED及require_success通过|
|fail|7|23/23B|CHILD_EXIT_FAILED_RETURNED；origin拒绝V2_CAPTURE_UNQUALIFIED|
|empty|0|0/0B|EXPECTED_OUTPUT_MISSING_RETURNED|
|bad|0|11/11B|EXPECTED_OUTPUT_BAD_RETURNED|
|over|0|270000/262144B|CAPTURE_FAILED_RETURNED、PIPE_BOUND，origin未COMPLETED|

原流、exit、wait/EOF/readers/流/H/Journal/control、唯一audit及registry完整tuple逐例核验。原包装器先保存原返回与流，再判结果；empty/bad的origin完成不代语义成功，returned或exit0不单独授信。归档实际文件hash和计数均核同，未用泛异常代某层通过。

17项根谓词覆盖准确开发/新tester命名空间、10hex/UUID以及相似前缀/根本身/父目录/错scope/额外层/exit7与LIVE leaf/旧HOST01根/混斜杠/dot/dotdot/相对路径。另预声明独立空leaf由原run实际FRESH_OUTER_OUTPUT_REQUIRED拒绝，未创建Capture或子程序；不是重放任何产品scope。实际reparse/UNC/其他盘攻击未运行。

45项原validate_scope纯入口覆盖独立UTF8 golden、五字段逐变及缺失/异型、四处绑定与全相等错公式、run语法与policy.entry/preauth.entry分义。前后原预算、原文件事件及custody一致。源码确认scope在SDK读取/runtime/Journal/Capture/Gate前；LIVE批准ref自有H身份接收在其前，单列该权限，不据纯公式正例授予LIVE资格或冒完整LIVE资源前置实测。

另23项预检/文件检查覆盖缺/错外部hash、draft、批准异型、源/probe/env/extraargv/modeleaf、完整tuple负例及自有ref正负。实际ref正确读取、错误SHA、错误volume、同字节不同fileId替换拒绝均沿原API；原输出保留、close返回、费用不退。身份早拒绝的actual=null，未到内容读由原分支推导，不冒API拦截计量read0。普通config是原fstat+外部SHA，不能套跨调用approved-fileId契约；普通同字节替换仅源码契约，未另做攻击实测。

## 原归还与费用

64项事后独立复核通过，候选126项和冻结201项无变化；custody、filePending及host.PENDING均0，无新增资源UNKNOWN。所有原记录读取/写入close返回。自有原process身份6次，派生GetProcessTimes/QueryFullProcessImageNameW/GetProcessId各6、GetCurrentProcess0；file identity8次，GetFileInformationByHandle/GetFinalPathNameByHandleW各8。原process H关闭6、流关闭12、approved-file关闭6。计数从冻结原函数完整返回路径派生，非API拦截或全OS资源测量，不笼统称全部Native0。

合并原读预留 **54550609B<256MiB**。worker最终导出后永久写预留3495821B，父侧160356B，合并 **3656177B<4MiB**。Journal每例600000B永久预留不按实际退还，归档流/JSON另计。原result记录截在最后导出前；post-export账界及最终合并另核。准备/事后文件与最终整树大小由封存manifest/freeze单列，均低4MiB；不冒业务预留即全系统物理I/O测量。64项是证据复核数量，不抄开发109项。

本批静态审证脚本曾修正Schema字段定位与AST复制比较写法，均只修事后分析，产品worker未重启，原动态结果/输入/once未改。

## 回交与停止

完整证据根`docs/tester/D1_REAL_FACTS_HOST03_INDEPENDENT_B_EVIDENCE`，最终manifest/freeze含准确文件长度/hash、完整报告及本批原结果。结论为F03限定关闭、HOST03独立离线B限定PASS，未测边界如上。集中回负责人审完整包，后续真实只读需另准确派单。

本B LIVE verify_inputs后部/run、真实facts_entry/FactsBundle、SDK exe/DLL读取与调用、route/TCP、设备、Gradle/Git均0；没有candidate/review/qualification、驻留/七角色或从档案重建Capture。原LIVE58+A与宿主额外费用分域及原嵌套时窗保持。

旧HOST02FAIL、旧05/capture1/锁PID/预算/once/UNKNOWN不查改。N2原17日一次ABORT及原任务后停止范围沿既有报告，不重复执行、不套全局暂停。当前本批完成后停止，不自动后续测试；D1未过/M0未启，主阶段/设计许可保持。
