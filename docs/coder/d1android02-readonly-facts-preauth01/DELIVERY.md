# D1_READONLY_FACTS_PREAUTH01 完整源码及开发自测阻塞交付

2026-10-23；coder集中交负责人。**BLOCKED：源码已实现，开发自测资格失败，不能派正式独立B或LIVE。** 本批仅一次集中动态调用，没有补跑或替换失败profile。D1未通过/M0未启。

## 准确输入与冻结身份

正式工作单：D1_READONLY_FACTS_PREAUTH01_CODER_REQUIREMENTS_V1.0.md；负责人完整派发来源01a107c3-2bf9-7fa0-94a0-234258ca6774，原用户恢复及项目沟通授权有效。已读当前设计基线、里程碑协调和D1执行安排最新PREAUTH01块。原CONTRACT03 source17 `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93`及gate9/plan保持；本批静态复核原17源bad0。原98/SELFCHECK02/A/B和全部旧FAIL/UNKNOWN/once未改。

全新目录 `D:\CodexProjects\VideoKit\docs\coder\d1android02-readonly-facts-preauth01`。新source20 `02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df`；gate12 `bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192`；七角色plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`（内容未改）；预冻结失败profile `f0ea99f8f8839a662ebae3f45288da5f8ddc6e8f0ea9c253526ec057b02cdb9b`。三个新增条目tools/fact_preauth.py、tools/facts_entry.py、reference/fact-preauth-schema.json均纳入source及gate。精确修改映射与完整diff在reference/source-delta.json/.patch。旧seal不冒作新候选。

## 已实现源码及批准边界

新GLOBAL_IDLE_FACT_PREAUTH_V1绑定准确source/gate/collector/binder/facts-entry/runtime/SDK/factPlan/policy、scope/plan/run/nonce、输出位置、模式、设备、原七query、负责人来源与不超过90秒UTC有效区间。外部已批准template SHA是明确入口参数，无默认自计算批准；缺失/错误hash、封闭字段/type/整数/重复/预算/时间/身份不合均在Gate/Popen构造前拒绝。模板可以供审阅，其生成本身不授权。

PreparedFacts持有原pid/thread，唯一构造原Gate，Gate.prepare返回后由该同原ticket、同未消费Gate生成GLOBAL_IDLE_FACT_RUNTIME_BINDING_V1，绑定实际route/proof/receipt/generation/holder/file-id/ticks。接收器复核同原对象及原字节，在原proof10/gate30内进入共同私有capture体，无人工或跨窗口实时补hash步骤。新路径没有生成legacy authority/approval。原V1双hash验证分支保留，共同body的Popen/reader/wait/pipe/H与claim释放保持原算法。

新facts回执GLOBAL_IDLE_FACT_CAPTURE_V2明确authorizationKind/externalPreauthSha256/runtimeBindingSha256，不塞旧authoritySha256/approvalSha256；旧V1回执字段保留。原SDK一次、固定model/api/firmware/user/system/role/home、stdout139264/stderr8192/合147456、qualification15/outer30/proof10/whole90、并发1/retry0不扩；LIVE仍固定原共享claim及原SDK/env校验。事实入口不运行目标七角色、不安装或处理媒体、不批服务/资格。

本批选择不做qualification V2适配，因而无V2资格或模拟目标链接回，相关项明确NOT_IMPLEMENTED/NOT_RUN。旧V1资格接收器只更新准确collector源码常量，不更改其资格语义。未来适配仍须独立真实facts/HOME窄政策review、目标source/scope/plan与原返回、至多300秒新鲜期；本预授权不代该review。

外部hash属于受信启动输入。无签名/公钥/密钥/IPC，所以程序不能仅凭hash证明批准人的真实来源；不把caller自算hash或issuer字符串视为批准证明。离线正例只设计合成fixture输入，本轮根本未运行，不能声称真实外部往返、设备资格或新路径原返回已证。源码字段表与时序/信任边界见CONTRACT.md及Schema；调用与原对象所有权见CALL_GRAPH.md。

## 实际动态结果与停止原因

一次工具exec `e104ab`于原工具返回，观察exit_code=1；worker结果约0.015秒。源码末尾请求SystemExit(2)，本记录不把它冒作单独观察到的native exit_code=2。

第一组driver-qualification在第一次正确命令的纯Registry.check阶段即FAIL：`ValueError('PROFILE_SOURCE')`。prepare_driver用Windows str(relative_to)存键（如driver\reuse\owned_child.py），driver_guard却用as_posix查driver/reuse/owned_child.py。错误出在我新建的辅助profile，不是候选Gate或collector已确认失败。

此时还未进入Capture构造、Journal写入或原Popen构造：calls=[]、audit=[]、Gate/FACT/AUX custody均0，没有新建Popen临时pipe/原进程/claim。三次资格调用全部NOT_RUN；auxOriginalsReturned=true仅空集合布尔结果，**不代表三次资格实际通过或有原返回证据**。本批无新增资源UNKNOWN；旧UNKNOWN原样保留。

| 组 | 本批实际结果 |
|---|---|
| driver qualification | FAIL：纯构造前profile路径键不一致，实际资格调用0 |
| strict template models | NOT_RUN；逐字段/时间/hash/模式/重放等设计在selfcheck.py |
| original 346 semantic regression | NOT_RUN；原45/17及其他条件正例不继承为本批PASS |
| original preStart13 | NOT_RUN |
| original preauth Gate→binding→fixed producer→return/release | NOT_RUN |
| legacy V1 exact positive/negative | NOT_RUN |
| explicit V2 facts CLI original outer return | NOT_RUN |

原evidence/result.json、group-1.json和预冻结profile/driver31项均保持，不修正后覆盖原错误。本报告附reference/profile-normalized-static-draft.json，仅把键规范化后静态核31项内容bad0；**该草案未替换失败profile、未安装、未执行**，不当作驱动资格修复已证。没有追加第二动态scope、暖机、扩额或重试未知对象。

## 静态验证、预算与未证项

源码20/gate12所有hash与预冻结31项helper/profile源码静态复核bad0；Python AST/compile静态检查通过，不代功能测试。Schema初次静态组装曾抽错AST节点导致缺schema文件，随后静态纠正并封源；原失败保留reference/static-preparation-failure.json，没有因此运行候选或子进程。

整批计划在运行前固定：360秒、320停止新增、并发1/retry0、读取1GiB、产物16MiB、辅助96以内；实际图上界12、预计90秒。三套原Gate source cap预留805306368B、解释器/PS导入控制67108864B、驱动源/控制33554432B，共905969664B（864MiB），未事后扩额。实际没有到达原Gate/source读或子进程；这项静态预留不是全部物理IO实测值，不用逻辑量冒充物理计量。

新增template/policy载荷、binding创建/receiver按原Gate control账，当前源重读按source_read；CLI嵌套fixture构造前固定两条完整argv与顺序、cwd/env/source/stream，不在Windows audit内抛异常。驱动复用已接受SELFCHECK02原Capture算法和SELF Journal/native原handle身份函数，来源hash与零算法更改见reference/driver-lineage.json；**复用来源不代本轮新profile资格**。

原旧完整B接受范围及原FAIL_TARGET_COVERAGE_GAPS、旧9s前置失败/旧cap不改绿；未查询/操作旧001a/55065、31884/30010、40119或其他未知进程、会话、锁、预算、once。未kill/二close/补ACK退款。没有SDK/ADB/Native route/TCP/help/设备/Gradle/媒体、新依赖或Git/index操作；tester独立Git检查点不属于本窗口。

## 完整交接与后续依赖

未来执行提案reference/future-execution-proposal.json绑定本批准确20源/12gate/collector/binder/entry/Schema/runtime/factPlan/plan，approvedForExecution=false，scope/plan/run/nonce/外部批准hash未签发。当前状态BLOCKED_DEVELOPER_QUALIFICATION_NOT_PASSED，不是authority或执行许可。

本目录源码/diff/Schema/调用图/信任边界/原失败/全部NOT_RUN/静态审计/未来提案一次整包冻结。manifest逐项hash与ZIP唯一成员校验、含ZIP全部材料小于16MiB；独立freeze-receipt.json位于manifest/ZIP外以避免自包含hash循环，但仍在本次新目录内。负责人审完整包后选择新的准确profile/资格与整批验证安排；本窗口当前不追加动态，也不自动派独立B或现场。
