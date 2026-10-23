# VideoKit CONTRACT03 独立语义 A 测试报告 V1.0

2026-10-23；tester；批次 `3cce1f60-69ca-4625-99ee-e2b3c43a9034`。

## 结论与边界

**PASS_IN_SCOPE：本次有限语义 A 通过。** 366 个语义案例、34 项纯参数/静态检查全部通过，合计 400 个逻辑检查；未观察到错误 PASS。原独立 17 个条件正例全部实际通过，未以永远拒绝修掉错误放行。此次结果只属于当前准确冻结源与下述范围。

**正式整包 B、原七角色/END/once/释放、preStart13、原 collector/Gate/claim、完整目录链和现场测试均 NOT_RUN。** 开发原辅助驱动 FAIL、其内部临时 close 未证、原后续组 NOT_RUN及所有历史 FAIL/UNKNOWN/once保持原样；本次新调用通过不替旧调用补证。D1未通过，M0未启动。没有自动进入后续测试。

派单来源：负责人会话 `01a107c3-2bf9-7fa0-94a0-234258ca6774`，turn `01a1685c-fdff-72c0-a6d3-d8a1c1c045a4`，send call `exec-5506c5b6-0562-45e9-930f-f801baf253fe`。[本次完整要求](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_TESTER_REQUIREMENTS_V1.0.md) SHA-256 `2c20c94259927c2ca49f299f09062d079153cc69ccb6ff2e510efc470d189498`；[来源记录](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/dispatch-source.json)。用户已授权 tester 按测试文档执行并即时集中报告负责人。

## 准确候选、驱动与冻结

只读候选：`D:\CodexProjects\VideoKit\docs\coder\d1android02-global-idle-contract03-fix`。开发 BLOCKED 报告 `8e4e5b6f26867465852eeeee914c590b06204a7c6c7722e2dd5ffc7022cc7dba`；原全包 manifest `55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81`，98项/1245040B。原 ZIP `45fb593f8b7aa916095540275a7287bdf01e524f5a983befc3768e9c9cb4a58c`，99个唯一成员。原98项执行前后 hash 均一致；ZIP逐完整路径、长度/hash核验通过，原 ZIP 流已 Dispose。

| 对象 | SHA-256 |
|---|---|
| 17源 seal | `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93` |
| 9源 gate manifest | `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72` |
| plan | `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8` |
| 实际生产 admission 模块 | `fc09218ed9094641a7c89b69ae4d06226f758b2909bde84dbd171c4f0edcbd8a` |
| collector 源，仅选定纯守卫 | `177ae66029013463173dd78c3afa2452ac74a25ca67d3b629315a37dc3535b4a` |
| 本轮订单 | `06b3ba07057b2557513ba1c64051479fba6901868824dd1474f47f9c703bf00c` |

输出仅在 `docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE`；没有写 coder 目录或其动态输出，没有测试浮动源。原包中已冻结的失败记录只作完整性核验，不查询其原运行对象。

复用已接受 SELF 的原 Popen/原 H 身份、双 reader、单 waiter、唯一原 close 机制；原 SELF 报告 `2fd415f0bbee624abae236934514a4f9a3310e3d04ac7937d10b65cc9f3fb613` 和13源清单 `b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1` 已核验。固定14文件运行时亦在准备时逐字节核验。新 profile 没有借用不相关 Activation；本轮实际完整程序/argv/cwd/env 均在构造前纯正反例检查，来源和输入共381项预存于订单。

Windows audit 只记录原 applicationName/commandLine/cwd/env 四元组，不把字符串当 argv 数组，不在回调中执行文件IO或主动抛错。实际两个 Popen 事件均与准确显式程序 profile 相符，mismatch=0、审计抛错=0。错误程序仅在纯检查中作为值，从未实际启动。

## 逐簇结果与来源归属

| 来源 | 数量 | 通过 | 条件正例通过 |
|---|---:|---:|---:|
| 原独立175扩展，用当前源/当前合成绑定重建 | 175 | 175 | 17/17 |
| 开发98回归重放 | 98 | 98 | 10/10 |
| 开发新增73映射 | 73 | 73 | 15/15 |
| 本轮独立同类20项 | 20 | 20 | 1/1 |
| 纯参数/静态检查 | 34 | 34 | 按以下子表 |
| 合计 | 400 | 400 | 正例不跨来源去重后冒称新增 |

原45矩阵包含于独立175，不额外加45；原23规则为该矩阵的判据，不作为额外案例计数。98、175、73中存在相同语义归属，表中如实统计重放来源。20项新独立案例也不冒称全部对应新的独立需求。完整逐行输入、预期、状态、原因、stage、记录明细与 pass 字段均冻结于证据目录，见[来源映射](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/case-provenance.json)及[逐项实际结果](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/semantic-results.json)。

五项修订在阶段A中的实际证据：

1. **B-R2-01 语义通过。** 原三种错误 PASS 已准确未证拒绝。新增73映射中的33个头部/位置边界，以及独立前/中/尾 APP/PERS、ProcessRecord 间隔、未知星形头、UID形头、孤立own字段均准确拒绝 `GLOBAL_PROCESS_HEADERS_UNPROVEN`。支持的 APP/PERS、own字段、末 UID summary 及完整68条归档仍正常解析，未为补漏而吞掉受支持记录。
2. **B-R2-02 语义通过。** `16.5`、`1.5`、小数、指数、后缀、前导零、同一行重复字段等均在状态词法层准确拒绝；原 HOME `1.5` 已不依赖后继 HOME 状态检查。`+2` 在 own-field 词法入口准确 `GLOBAL_OWN_FIELD_FORMAT_UNPROVEN`。规范0..19的20个策略案例全部符合预期，TOP/BOUND_TOP、竞争操作与批准窄服务有区别；instrumentation优先仍阻挡。
3. **B-R2-03 纯守卫通过。** 从冻结 collector 源 AST 只选 `validate_fixture_argv`、`verify_fixture_runtime` 及其纯解码/hash依赖，不实例化原采集器。12个准确argv正反例全部符合预期，adb/外来Python/tuple/类型/路径/模式/多缺参数均在参数守卫拒绝。4个身份模型包括准确身份、metadata字节变异、程序字节变异、政策hash失配，均符合准确原因。身份模型使用只提供固定已读字节的纯协议替身，不是原 Gate 的返回证明。
4. **B-R2-04 静态通过。** 当前提案 source/gate/collector/factPlan/targetPlan/externalHandoff 六组准确路径/hash均匹配本冻结包，`approvedForExecution=false`；历史提案有独立历史引用。此结论仅证明当前提案绑定，不代表批准执行。
5. **B-R2-05 纯/静态通过。** 统一根谓词8个正反例通过；Runner/Owner引用统一谓词，PS同步新tester根，3项引用检查通过。谓词模型对 `no_links` 使用纯依赖替身，真实目录/重解析门、同一新根完整构造及七角色链仍 NOT_RUN，不由本次纯模型代签。

纯/静态34项分为argv12、身份4、根8、提案绑定6、入口引用3、外部方案状态1；见[完整结果与边界标记](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/pure-static-results.json)。

原 LIVE03 样本388784B，SHA-256 `6eab0a9190438367150182a530395585066826514242dbaf5dc70bb6f49596b0`，两套来源各 H01/H02，共4次归档回归，每次实际解析68条，缺新资格继续 BLOCKED_UNPROVEN，没有回填历史现场 PASS。API31 空 instrumentation 的已知语法新增正例实际通过；活跃 instrumentation 和外部 TOP 等反例保持拒绝。

## 原返回与资源预算

| 项目 | 上限 / 实际 |
|---|---|
| 动态整阶段 / 停新增 | 300s / 240s；原外层6.453s，原 worker5.485s |
| PS函数宿主 | 最多2个、每个90s；实际1个、5.375s、exit0 |
| 辅助进程 | 最多4；受控动态树为外层Python、原worker、PS宿主共3个，Popen事件2个；文件型准备Python不创建子进程 |
| 并发 / retry | 1 / 0；仅执行一次冻结订单，无动态修源、重跑或加额 |
| 标准流 | 每路上限1MiB；沿用SELF更紧的262144B合计缓冲界。worker stdout128B/stderr0B，PS stdout0B/stderr0B |
| 读取 | 上限64MiB；明确受控读取分类和用例生成/函数宿主/封存读取的保守上界另存账本。物理IO与解释器内部IO不以逻辑小计代证 |
| 产物 | 上限16MiB /512项；实际全文件长度/hash见新manifest和独立冻结回执 |
| 新未知 | 0；wait/readers/streams/H原唯一close均真实返回；没有构造错误程序或故意制造未知 |

原 worker PID28280，creation FILETIME `134372267991500879`；原 PS PID38788，creation FILETIME `134372268001481528`。原H身份和准确创建参数均由本轮原对象观察；worker另有实际自身命令行/身份与nonce准入。原 worker/PS/外层观察及测试工具终态均 exit0。原 stream/H close 只发生一次，原 observer custody为空，所有自有证据文件 close已观察。见[原PS返回](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/PS-original/runtime/outer-original-return.json)、[原外层返回](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/outer-final.json)及[原worker结果](D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE/worker-final.json)。

生产 whole600/gate30/checker20/proof10/outer120 及原字节/角色/once上限均未改；本次不执行这些原链，不能把阶段A的更小预算写成已验证了完整生产路径。SELF自有H身份API的调用不等于真实Native路由测试。

## 全部未证与后续依赖

外部交接文档明确采用待审的独立签发、公钥/密钥托管、固定IPC与签名验证方案；当前 `implemented=false / executed=false / requiresNewTrustContractApproval=true`。本次只核静态边界，**没有实现、运行、批准或签发**。原Gate proof10s/gate30s、facts至target最多300s仍需未来准确可操作性验证；同调用者合成issuer/hash不能充当外部真实往返。真实外部owner/authority/签名/IPC/新鲜资格链仍 NOT_RUN / NOT_PROVEN。

原 collector、Runner、Owner、Gate、claim、Native route/TCP、七角色/END/once/释放、preStart13、有限故障、PS post/最后Start、物化与小追加source门、完整新tester根链，全部未在A运行。SDK/ADB/help/设备/Gradle/媒体均0。原 c45d128d37214321b75f863558ec21bd 辅助失败对象、旧001a/session55065及其他旧未返链未查询或干预；没有kill、二close、补ACK退款。没有修改旧报告/预算/once/FAIL/UNKNOWN、test_media、候选或共享Git/index。

本报告只集中发负责人，不逐问题交coder。负责人收到开发SELFCHECK02完整结果后统一决定下一批；正式整包B、外部信任入口或现场采集须另行准确派发。A通过不签整包B、执行就绪或D1。
