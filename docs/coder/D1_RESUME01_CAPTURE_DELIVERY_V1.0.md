# RESUME01_CAPTURE 整包交付

2026-10-20；候选 D1-20261020-RESUME01-CAPTURE。最小采集入口已实现并完成最终145条有限离线断言，交独立审查；本批未签发/消费新设备许可。D1未过、M0未启。

依据执行准备阻塞报告 SHA `d86433cb2b1421ae8e0c8c583fb3a7693b48ff18c5d5d0adb08dfb0c22c98d6d`。原SDK/部署/T07仍NOT_RUN，R01不是媒体产品FAIL。旧授权/候选/once/预算/registry/claim/账本/UNKNOWN原样保留。

## 可运行入口及准确契约

入口 `docs/coder/d1resume01-capture/tools/capture_metadata.ps1` 由已审Java observer的前台原Process、异步pipe读取、原FileStream与任务保管结构收窄派生，未引入通用keeper、网络协议、服务或产品class。`observer-derivation.diff`列出差异，历史杀进程采集参考只作拒绝复用的证据，从不执行。

入口固定读取相邻 `release/capture-policy.json`，唯一必填参数 `-RequestPath`。后续请求必须由可信tester在同一个原控制器/工具调用自然结束后，另存固定路径的 completion-proof，传 `-PredecessorProofSha`；第4项M2还要准确部署完成证明的SHA。证明必须匹配前项id、scope、receipt摘要及controllerPid，且实际控制器退出、工具流归还、console物理归还和语义允许继续的布尔值均为true。入口不自造这些外部证明，也不能靠文件存在或阶段日志宣称外层已结束。

request精确八字段：schema、id、policySha256、scope、evidenceRoot、argv、maxTextBytes、qualificationSeconds；严格值类型、重复键、id/范围/根目录/policy及entry摘要检查。生产模式只接受原冻结的五组SDK argv及65536/524288/65536/65536/524288上限、15秒资格、M1/M2固定顺序。原 `-s HA1Q6WXR` argv逐项不变，不迁就历史maxBytes或-H/-P脚本。

本交付policy为 PREPARATION_ONLY，五请求采用新准备plan及独立新根，运行必在工具hash/SDK启动前拒绝。其scope是离线准备计划摘要，不是新E9执行scope或许可。未创建对应现场目录。未来PRODUCTION需新的执行授权、独立capture审查和基础release绑定摘要，全部有真实文件pin；当前这些字段null，不以文字承诺放行。

## 原对象与物理归还

每请求只有一个前台PowerShell控制器、一个原Process、两组固定reader对象/pipe、原始输出文件及其异步任务。global custody在原IO前强持上下文；同批`.capture.lock`保持独占。持久entered记录在child前写入关闭，重复id、halt、无前项真实返回证明都拒绝；词法退出和Process消失不等于完整归还。

所有成功read返回的长度先计费，再检查quota/入队/写文件；raw读计数与保存计数分开。未结束read只报已知前缀和总量未定；read fault保留UNKNOWN。写任务失败可能已部分写入，savedBytes仅为已知完整写入前缀，savedAmountUnknown/recordWriteAmountUnknown分别保留归档/控制分栏，不能以0伪称未发生写入。

超时、越界、stderr、写失败、非0退出等保留第一个失败，停止后续准入；同一原控制器继续原读取/落盘/归还，不kill、强关、替换reader或重启server。失败后迟到正常返回只补当前物理事实，不抹失败/halt、不退额度。read/write启动本身未证时不关闭可能仍在途的原对象；wait/dispose/pipe/file close均有一次进入屏障，未知不二次关闭。若原调用永久未返，原前台上下文、对象和lock持续保管，不保证15秒内退出，也不假装完成。

receipt自身明确不能证明自己的关闭；console只在已登记原资源、metadata文件与lock实际关闭后输出。外部同一原控制器退出及工具流完成证明仍须可信tester提供。controller/token、reader/stream token、EOF、wait/close、metadata逐项状态及实际计数分栏可追溯；保管不等于正常ACK。

## 有限离线验证与保留失败

最终 `evidence/fixture-004/results.json`：145断言通过；当前原入口字节、fixture、实际测试控制器输入摘要和完整命令/自然exit/stdout/stderr均保存。覆盖正常采集及前项真实返回后继续、stderr、分块越界、资格超时、faulted writer task、faulted reader task/UNKNOWN、子进程退出7、晚返、文件关闭未证窗口、原id重复、无前项证明、旧根/旧schema/错误argv/cap/类型/pin/重复JSON键拒绝。

越界实际read192B而保存资格96B，明确不截断实际账目；晚返前后owner/Process/pipe/reader身份相同。关闭gate用例证明进程已退出也不提前归还原文件。read/write fault仅在固定本地Python fixture模式经受控任务注入，生产模式不存在任意child/故障开关；不宣称真实SDK、永久原生IO故障或Android行为已验证。

初轮fixture-001通过130断言；封包前补严类型/metadata状态后fixture-002的测试观察器误把刚创建的异步halt文件当成完整JSON，测试观察器退出1。该轮失败、原始输出、缺失外层wait证明保留：其局部PowerShell控制器外层返回为UNKNOWN，不凭后来文件/推测补ACK，不查PID或终止。原采集器继续持有受控本地child，fixture自身有限gate后备不是SDK终止。

观察器随后等待完整JSON，并在自身异常时保管同一Popen、只释放明确的本地fixture gate后自然等待；fixture-003通过145断言。最终再补严未知写入计数、未知IO启动保留、wait/dispose不重入后，fixture-004整批通过145断言。历史失败/UNKNOWN不被最终PASS覆盖；最终轮所有原测试控制器均有自然返回/原文件关闭证明。未知的历史测试根只封存一次内容快照，不把可能仍变化的原路径列为不可变源，不另造收尾工具。

## 预算与后续绑定

不改43操作/3MiB文本/4MiB归档，不动409600B不可分配额。`release/accounting-feasibility.json`为等待新release授权的可行性清单：原始/重复输出1949696B不变；控制786432B内，其他原记录589824B、新五capture保守135168B、旧已知2272B和旧控制台UNKNOWN槽8192B分别保留，合计735456B，控制余量50976B不授予新操作。新capture计入intent/receipt、console及其副本、外部证明和一次halt记录。未知/超额照记，不把保存界当物理硬界。

新准备/fixture证据独立列账，不动旧执行余额；准备工具控制台没有原始字节归档的部分仍记UNKNOWN，不能伪报0或转成SDK许可。原旧8192槽不退款，原SDK调用0也不产生自动重试权。原始保存文件计归档，若再转发其内容须另计重复文本；当前console仅摘要，不再打印raw payload。

下一新release必须：

1. 取得本capture独立报告和负责人新整批派发；不能重放已冻RELEASE的许可/旧前置。
2. 保留已审74来源/183class/JAR/三个APK、行政disposition及四证据原字节。产品sourceReview与capture独立报告分别绑定，原registry历史trust保持。
3. 先生成无环基础release描述（新E9 scope/release/config/once及原registry/预算/授权/本entry摘要，不含后生成policy摘要）；capture-policy引用该基础描述、授权及capture审查摘要，再生成五个准确request/policySHA，最终manifest/许可在后层列全pins，避免互相自引用。
4. policy改为经审PRODUCTION，planId/实际E9 scopeSHA/新输出根一致，工具pin及五个argv/cap保持；更新外层Java observer pins、schema/入口/前项和部署证明依赖。机械PASS和本地门通过后、首M1之前，只创建获批的新evidenceRoot用于采集，不预写部署once/disposition/claim；采集入口拒绝不存在的父目录，不自行初始化现场。M1全过才进行后续获批部署准备。不需要改媒体class或Android构建。新scope/evidence/once和许可必须重做准确机械绑定，不能就地改旧文件。
5. 独立机械PASS后仍需新鲜工具来源/default routing、原registry/ledger/claim及准确v17/fixture1/data/全局占用门，M1→部署→M2→唯一case；本批不自动进入此阶段。

完整替换清单见 `release/rebind-plan.json`。若原IO永久未证或可信外层完成证明无法提供，保持BLOCKED并集中报告确切对象/缺口，不能靠新增框架、kill或补marker恢复资格。

## 封包与范围

ZIP `docs/coder/D1-20261020-RESUME01-CAPTURE-source.zip`，外seal `docs/coder/d1resume01-capture/evidence/capture-freeze.json`，只读回执在ZIP外。生产不变清单、精确入口/五请求/预算/类型schema、fixture快照及原失败均封存。默认verify/help/pack-help只读，显式pack一次生成新包。测试scratch不作为不可变原路径，包内使用准确快照。

本批无SDK/5037/设备/旧handle或现场registry/claim查询，无Android/产品构建、媒体读取或设备许可。Flutter自有集中Theme当前要求、SkinKit等待正式Flutter支持、独立媒体Kit/Browser、既定开源框架及全P0保持，不开始M0。
