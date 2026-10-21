# RENDER02_DEVICE_V2 集中实机测试报告 V1.0

日期：2026-10-20。目标HA1Q6WXR。新planId：`7aebea43-88e7-40cb-8794-cd3c6216cbe0`。

**结论：ENV_WAIT_OTHER_PROJECT_INSTRUMENTATION，已停止本批。** 独立快照机械核验、新鲜本地/tool/default路由/claim门及平板身份均PASS；第二项完整global发现LendManager活跃instrumentation。实际进入2个SDK子操作，均原资源及外层工具正常归还。未进入ps、新包absence、安装、fixture或四静音用例；不自动重试、后续测试或M0。

这是本轮新鲜占用事实，不沿用旧ENV读数，也不是产品FAIL。RENDER02三项有限离线PASS和采集准备PASS保持，D1未通过，M0未启动。

## 1. 真实授权与独立机械核验

范围文件SHA256：`8698220f3ef9bfb6c2aa0d8b4a330cc37d2e66b2605cc460fcb54fcd61e202e4`；四个runner的renderScope准确绑定此值。负责人实际ACTIVATION文件SHA256：`f27f35f3492acb56136c66080c8806e74ba6dfe3409d6a53c74c8306591c76f4`，approvedForExecution=true。

新独立快照位于 `D:/CodexProjects/VideoKit/docs/tester/D1_RENDER02_DEVICE_V2_EVIDENCE/snapshot`。只复制原字节entry/reference和正式activation，纯数据设置PRODUCTION policy及25准确请求；四处runner仅改renderScope，原argv/资格/caps未扩。三个截图和人工第五项不准入，无新框架或产品重建。

| 绑定对象 | SHA256 |
|---|---|
| 原有限entry | b836b50403b4914a4afe762de5e327e2d97ac38bcc66beebafc1d097ab81f17e |
| 原28计划 | 1db733cd14d51b47d41df3670a5d9d84b1f68f599aeb3d02b8d1d814236810d1 |
| 采集独立review | c87e3c900e78e95a204189a796cedeb52ac9774b0bbf0b0a37384452617fe886 |
| 产品seal | a226b5fe0703d31c486ec2deaad1c2f2241169f4c8257701331cd5d9c1a83581 |
| 执行快照policy | d8d8b0e4270d9b5769678c87ec6fc9fe96297fdeb9ced3441e2db78a2e5e156d |

原capture818项及产品404项在执行前逐项核准未变。mechanical-audit.json在首SDK前外存，列全部25请求及快照文件准确hash，不改冻结候选补字段。

## 2. 新鲜本地门与真实身份

本批一次本地检查：无路由环境覆盖、guard不存在/claim0，新capture root及父目录未先存在，无reparse。一次现有127.0.0.1:5037监听器/所属进程来源核查，准确adb.exe SHA `b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f`，文件早于server创建；没有额外ADB版本查询、server启动或重启。

上述原host工具实际exit0/无未返session后，另作只读本地闭合记录，记录该闭合工具实际PID；闭合工具自然返回后，后续独立调用才形成pre_sdk_local_gate proof。其receipt摘要字段绑定host本地闭合事实，不冒充尚未启动的SDK receipt。没有重复listener/claim查询、预造SDK ACK或自称权限签发。

identity原准确脚本完整BEGIN/COMPLETE及中间四行通过：TB138FC/API31/user0，ABI含arm64-v8a，原read88 B。原Process、stdout/stderr reader/pipe、文件、metadata、stdin及锁实际归还；原外层工具exit0后独立语义核验，再形成identity→initial_global证明。两个proof的写入及读入、额外工具结果/语义记录均进入累计已知前账。

## 3. 最新global占用证据

完整activity processes原文366415 B，SHA256 `8c95a4fbd50df66627a40ced6f3eaf5932e5334f6ab3faf0379c1830f425c5a2`。头、All known processes、OOM levels、最终mForceBackgroundCheck及EOF均完整，非截断或仅查某个包。

| 原文位置 | 当前事实 |
|---|---|
| 2356行起 | com.lendmanager.app，UID10223、PID19377，curProcState=4、cached=false |
| 2363行 | mInstr=ActiveInstrumentation，组件com.lendmanager.app.test/androidx.test.runner.AndroidJUnitRunner，1 procs |
| 3612–3613行 | Active instrumentation列表明确有同一原记录 |
| 3804及4328行 | PID19377的进程条目明确标注instrumentation |

本轮不是先前PID31712前台快照：现在有明确活跃测试链，已经满足停批条件。没有继续ps、查当前新包或操作LendManager。

初版离线提取器曾将其他ProcessRecord正文中的交叉引用计入候选列表；已仅匹配每条记录首行，追加initial-global-semantic-audit-v1.1.json，初版保留。准确LendManager记录及活跃instrumentation结论不变，无新增SDK或重采。

global采集本身captureQualified=true、firstFailure=null；占用是独立语义ENV_WAIT。未创建initial_global completion proof，所有后继不准入。不能把采集成功当设备空闲。

## 4. 实际用量与原归还

| 项目 | 实际已知量 |
|---|---:|
| SDK子操作 / 授权上限 | 2 / 32 |
| 25串行中未进入 | 23 |
| identity原始读取 / 保存 | 88 / 88 B |
| global原始读取 / 保存 | 366415 / 366415 B |
| SDK文本read合计 / raw保存合计 | 366503 / 366503 B |
| SDK二进制读取/归档、APK出站、fixture出站 | 均0 B |
| 两次entered/receipt成功control写入 | 5727 B |
| 原console / 一次console副本 | 5389 / 5389 B |
| 两次完成proof实际写入 / 后项读入 | 1273 / 1273 B |
| global返回时controller累计文本counter | 405489 B |

两次原工具均真实exit0、无未返session；所有原读任务/EOF、pipe/file close、wait/dispose、stdin、metadata/锁已返。原始读取与保存分列，实际无raw/saved/batch UNKNOWN。未用cap或文件长度冒充未知量，未借外围进程消失推内部ACK。

405489 B是global控制器返回时已含已知本地前账/前项外层记录及proof的累计值；其后本次语义分析/更正/结算/报告控制量另计，不称这个数为最终全部开销。完整393216 B控制预留保守保留；以原SDK文本366503 B加整类控制预留计759719 B，低于4MiB，不用未指派部分增加操作。所有本地记录和报告实际字节清单另存，不能把原计划资格界登记为消耗。

二进制归档0，三个截图未进入，16MiB未花；4余量不授权重试或人工第五项。历史UNKNOWN及旧消费不冲销、不退款，不继承原scope余额。本轮无新增待保管原SDK owner；原始文件/receipt/proof和快照原样保留，不清除旧记录。

## 5. 全批状态

| 范围 | 结论 |
|---|---|
| 机械核验、新鲜本地门、准确identity | PASS |
| initial_global物理采集/归还 | PASS_CAPTURE_ONLY |
| global语义 | ENV_WAIT_OTHER_PROJECT_INSTRUMENTATION |
| ps、新实验包absence、两APK安装/安装后身份 | NOT_RUN |
| 349102 B私有fixture准备/校验 | NOT_RUN |
| generatedMutedDualConsumers | NOT_RUN |
| existingMp4RawMutedDualConsumers | NOT_RUN |
| cancelRejectsLateGeneration | NOT_RUN |
| pausedSeekAndSurfaceRecreation | NOT_RUN |
| 3截图、人工第五项/听音、真实视觉/焦点/峰值 | NOT_RUN_NOT_ADMITTED |
| D1 / M0 | NOT_PASSED / NOT_STARTED |

本轮不改变旧com.videokit.app、其他项目或设备音量；未安装/卸载/clear-data/force-stop、kill、server重启、强finish、二close或重试。没有生成后继准入证明；范围即使仍有预算也保持停止。

## 6. 归档与负责人移交

控制/审查证据：`D:/CodexProjects/VideoKit/docs/tester/D1_RENDER02_DEVICE_V2_EVIDENCE`。原SDK产物：`D:/CodexProjects/VideoKit/docs/tester/D1_RENDER02_CAPTURE_EXECUTION/7aebea43-88e7-40cb-8794-cd3c6216cbe0/outputs`。关键结算为actual-execution-ledger-final.json，语义终态以initial-global-semantic-audit-v1.1.json为准，初版分析不覆盖；两原工具结果/console及scope/activation均保留。

请负责人接收本次新鲜ENV_WAIT并协调跨项目设备窗口。此scope已经实际消费2项，不因静态文件或未安装状态当作未消费重跑；后续须明确范围和新鲜门，不由tester自行再查。既有一般真机授权继续有效，无需用户重复授权。

报告主动交负责人。本轮停止，无自动后续测试；有限采集/产品离线PASS保持，真实效果不得回填，全部旧FAIL/UNKNOWN及许可/P0边界保持。
