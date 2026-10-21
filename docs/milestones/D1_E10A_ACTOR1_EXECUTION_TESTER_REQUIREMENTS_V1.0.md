# D1 E10A actor1 单次迁移测试要求 V1.0

授权依据：负责人窗口 VideoKit项目助理（01a107c3-2bf9-7fa0-94a0-234258ca6774）真实用户消息 01a14cd3-0192-7072-afc2-c6052e9c15e7，及同轮正式派发，已由 read_thread 核实并完整保存在 docs/tester/D1_E10A_AUTHORITY_20261018.json。用户明确批准 E10A 单次迁移、新增三记录与目录，保留全部原视频、账本、107218B消费与历史证据，不删、不重置，完成集中报告，暂不激活或播放。

接受的独立 E10A 复审报告 SHA256：e8fb76cfac6da5993c7c20638027529188be19e40fe8aae221671cb811ea99f0。严格使用 docs/coder/d1e10a 冻结执行包及 D1_E10A_EXECUTION_RUNBOOK_V1.0.md，不修改候选源码或重新构建。

只限 HA1Q6WXR/user0、UID10221/10222、原签名；新 registry/migration/attempt/handle 各生成一次，绑定真实授权、scope→plan→config→index，禁止复用历史只读身份。当前来源必须为精确 E9B13 pair；一次生产受管 app/test install-r 各一次升级14，目标 app611672a9f2a7eab3f08a495832d513e79ee446cb1a9f99001fe323e944f2af54、test2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b、JAR8f5cbce3461d61fecf4c9bc1c026e66ddc4ed3ee1f9ab705ecdebaa594f800a0。任何来源不符停止，不盲重装。

预检当前版本、签名、UID、包状态、guard原dev/inode/UID/role、fence662e9ecd-bede-42e6-bb58-ce81d668ff44、13不可变metadata、完整ledger/1011B接受前缀及合法结算后缀、reserved0/原107218消费、无pending/相关进程/未归档在途、新M及外部registry缺席、日志余量。非零媒体只stat不读payload。原task86cafdb3-0fc4-447d-920b-b19c884bf494、budget730a73e1-50e1-4198-a515-047104f00e31、oldCloseACK=false和历史UNKNOWN均保留。

唯一允许写入：新M下actors/0001.intent≤2048B、n2-v2.acceptance725B、n2-v2.commit244B，CREATE_NEW，最多3目录/内容3017B/文件分配上限6400B。原guard/13metadata/0B/ledger只验与force，不改字节、不新增R/S；不得ABORT、清账、换budget、删档、卸载、清数据、人工force-stop或播放。

严格逐门：LAUNCH REGISTERED_MIGRATION actor1→STATUS1真实出生/identity<10s真返→RESERVE/BOUND→唯一EXEC2→STATUS3/必要最后STATUS4→COMMIT<10s QUALIFIED及全部原holder归还→精确ARCHIVE_RETURN→唯一ACK→CAPTURE_FINISH独立系统正常finished inst/原PID缺席/唯一锚→独立三文件与旧账档守恒→全资格通过才SEAL_FINAL并独立DAG核验→INSPECT/原PC自然pcClosed/Process、两reader、Store、listener和remote归还。不得自动actor2/3或产品激活。

BOUND未EXEC需取消仅严格STOP→当前取消归档→ACK/finish，不final；归档或safe COMMIT后禁止STOP。已发EXEC/ACK未知不重放。PC失败仍失败，只许同scope CLEANUP白名单，不SEAL。任何FAIL/PENDING/UNKNOWN停止后继并保留原handle/custodian，无kill/restart/换port/实际task清理。自动审批再次拒绝则保留原因报告，不绕过。

上限Android控制8/STATUS3/EXEC及ACK各1；原响应5s/identity及commit各10s；PC查询16/原accept128/生产process96/独立metadata20/registry20文件155648B与总196608B门/原log1MiB/新holder48。无循环轮询、无扩额。主机无副作用只读兼容错误最多2次，保留原错误并复用成功结果；不得用于有副作用或UNKNOWN重试。

交付 docs/tester/D1_E10A_ACTOR1_EXECUTION_REPORT_V1.0.md、原始证据、资源账本和独立final审证，立即发负责人。D1 NOT_PASSED、M0 NOT_STARTED及全部P0/历史FAIL保持，完成停止等待。
