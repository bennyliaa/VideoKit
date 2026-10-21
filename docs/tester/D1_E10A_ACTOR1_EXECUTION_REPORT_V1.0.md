# D1 E10A actor1 单次平板迁移执行报告 V1.0

日期：2026-10-18。执行设备 HA1Q6WXR / TB138FC / API31 / user0。

**结论：MIGRATION_QUALIFIED_FINAL_REVIEW_INCOMPLETE_TESTER_ERROR。** 本次唯一迁移已实际提交并取得合格原始归还、正常系统结束及旧账档守恒证据，生产端也已生成外部封存文件。最终独立审证脚本存在测试侧事件名称错误，未完成后半段 catalog/checkpoint/seal DAG 核验；因此本报告不宣布外部终局独立验收通过，不赋予产品激活资格。原 PC 自然关闭，全部原资源归还，无保留的未知客户端。执行后停止，无后续测试。

## 授权与输入

真实人类批准来自负责人窗口 VideoKit项目助理（01a107c3-2bf9-7fa0-94a0-234258ca6774）的消息 01a14cd3-0192-7072-afc2-c6052e9c15e7：批准 E10A 一次迁移、新增三记录目录、保留原视频/账本/107218B消费/全部历史证据，不删或重置，完成集中报告且暂不激活或继续播放。已通过 read_thread 核实原消息及同轮正式派发，原返回保存于 docs/tester/D1_E10A_AUTHORITY_20261018.json；未用旧被拒派单替代授权。本次执行未再被自动审批拒绝。

需求：docs/milestones/D1_E10A_ACTOR1_EXECUTION_TESTER_REQUIREMENTS_V1.0.md。接受的 E10A 包复审报告原 SHA256：e8fb76cfac6da5993c7c20638027529188be19e40fe8aae221671cb811ea99f0。

新身份各生成一次，未复用历史只读 actor：

| 身份 | 值 |
| --- | --- |
| registry | bbf71f7f-ab67-4bf8-af8f-731a38963e49 |
| migration | 4f21f71a-bf66-4a44-a287-320f0ae25fde |
| attempt | cc55fa47-5dbf-42f3-8c61-1825de5491ef |
| actor handle | 43ef4e56-072a-409f-ab73-11930d2b78a2 |
| 新原 actor | PID22086 / UID10221 / SYSTEM_BOOT_COUNT2 / start17030020 |
| actor SHA256 | aa35cc47f8408f5a78bc2f322372d79a7c36c5fa5010453729f5759148223ad22 |
| 原 PC | PID29504 / handle6f2a57b3-315f-4939-ad2b-09c73f4af347 / port1330 |

输入位于 docs/tester/D1_E10A_EXECUTION/4f21f71a-bf66-4a44-a287-320f0ae25fde/inputs。scope 为 ISSUED_FOR_EXACT_ACTOR1，scope→plan→config→index 单向绑定。scope SHA b54e51203519f11891bcf44f466d019ac447bf48a8a862a698ebd27fc5ac62be；config SHA312520a8870dbc471eadf81b7b35889b7b5f9db6fe79bd24447bf60a43d3c02e。授权的只读 --bound-dir 校验一次通过，未将其模板 readiness 文字当作现场许可。

## 实际执行与结果

1. 当前预检核实精确 E9B13 来源 app SHA ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020 / test SHA2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b，UID10221/10222、原数据目录、无相关进程、旧guard及fence、13metadata、完整ledger及无pending、新M与registry缺席。日志预检748202B。
2. 生产 DEPLOY_PREPARE 仅 app/test install-r 各一次，13→14；生产门核固定 E10A14 app SHA611672a9f2a7eab3f08a495832d513e79ee446cb1a9f99001fe323e944f2af54 / test同上 / signer5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f / PREPARE / ABI1。执行原冻结 JAR SHA8f5cbce3461d61fecf4c9bc1c026e66ddc4ed3ee1f9ab705ecdebaa594f800a0，无重新构建。
3. 唯一 REGISTERED_MIGRATION actor1：STATUS1 原 identity 为 IDENTITY_QUALIFIED，34705365ns，owned2/unreturned0。独立 ps/boot_count/proc start 匹配新原身份，随后才 RESERVE。外部原 identify/reserve 与 BOUND 同 actor、同 plan、同 scope 精确绑定。
4. 唯一 EXECUTE_COMMIT2，随后 STATUS3 得原 COMMIT：QUALIFIED_MIGRATION / ACTUAL_ALL_RETURNED / executeDone=true / safe=true / owned34 / unreturned0；executeNanos109746615，identity和commit各小于10秒。没有第三次STATUS、EXEC重放或STOP。
5. ARCHIVE_RETURN 精确保存原 COMMIT 字节；原 returned SHA dee972492b705bc3ac6801caaa786567d30ce711f9be01d77268675f7b51e668。唯一 ACK_FINISH4 与已归档原证明一致。生产 CAPTURE_FINISH 取得唯一 E9_FINAL_FINISH 原锚及其后的系统正常 finished inst / Killing PID22086。独立再次核原PID及所有相关app进程缺席；原系统日志754909B，未清日志或截尾替代。
6. 独立读取三份小型控制记录、核旧metadata/完整账本/文件身份和产物stat；检查通过后才发送唯一 SEAL_FINAL。新增目录恰好 legacy-acceptance、新M、actors 共3个，无其他控制目录；三文件如下。

| 新文件（相对新M） | 实际字节 | SHA256 |
| --- | ---: | --- |
| actors/0001.intent | 959 | 6ab15e02d848613811228f679daea25ee2ec19541ef0ae825e8a89adb47439de |
| n2-v2.acceptance | 725 | 4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb |
| n2-v2.commit | 244 | f0fc5dd5cac41d6d702b26d809f28ef52536633f04058a2dfe42e18f3cd7c542 |

总内容1928B≤3017B。intent与本次原actor、durable reserve精确绑定；725B/244B为固定canonical字节。6400B为冻结计划的文件容量上界；实际三文件 stat 块占用共12288B，按冻结计划的“FS目录项/块/journal另计”单列，不宣称实际磁盘块≤6400B。目录及journal开销未据内容字节推算。

## 旧账档守恒

原task86cafdb3-0fc4-447d-920b-b19c884bf494、budget730a73e1-50e1-4198-a515-047104f00e31、fence662e9ecd-bede-42e6-bb58-ce81d668ff44保持。owner64522:20304:10221/0B、lease64522:20385:10221/36B保持；13份不可变metadata逐字节hash一致。完整ledger仍为1011B、SHA f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba，全链验证通过，三R三S、107218B消费、0预留，未新增R/S。原0B、53651B和53567B产物stat身份/大小保持；非零媒体payload读取为0。原pending归档及全部旧恢复证据保留，未再执行ABORT。oldCloseACK=false、历史出生证据缺失及原UNKNOWN未改写。

## 外部终局审证未完成

生产端实际 head：6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5。

| 实际原文件 | 字节 | SHA256 |
| --- | ---: | --- |
| final.acceptance.json | 5853 | 27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7 |
| registry.checkpoint.json | 241 | f57af4f4ea47199dc28dfc1c6c7921aef3e66fafcf56337a09375b9c944ede7f |
| final.seal.json | 502 | c99cf4565aba45c62232d5214f779f7b514df51392bc3736e934a04fde07a6ff |

独立脚本已核原descriptor、部署plan、scope授权引用及四个事件的canonical字节/seq/parent/actor/evidence hash。原实际事件序列为 BOUND→RETURN_OBSERVED→NORMAL_FINISH_CONFIRMED→FINAL_ACCEPTED。脚本误把第二事件写成 catalog disposition 名 RETURN_VERIFIED_IN_TIME，于 NORMAL_ACTOR1_FINAL_CHAIN 断言退出1；尚未执行后续catalog嵌入原字节及checkpoint/seal完整DAG检查。因此“文件已生成”不等于“独立终局验收通过”。这是测试脚本错误，不能据此判为设备提交失败，也不能把未运行的独立检查标PASS。

此前两次允许的主机只读兼容修正已用于机型字符串误写及ADB CRLF解析，原错误和成功原回执均留存，未重复相应设备请求。此次最终断言错误后未进行第三次修正或重跑；冻结脚本与原输出，后继停止。若需完成独立审证，应由负责人另派基于现有冻结证据的只读审查，不能重发EXEC、重迁移、重安装或假造新原归还。

## 资源结算与停止状态

Android控制4/8，STATUS2/3，EXEC1、ACK1；PC查询3/16且全部真返；生产supervisor原operations28/96、最后live/nonqualified/unresolved/unreturned均0；独立metadata19/20，全部原客户端及pipe返回；新holder34/48且全部归还。registry小型metadata12文件/14383B，分别低于20文件/155648B及196608B门，原日志单独754909B≤1MiB。

收尾 INSPECT 后正常关闭原stdin。原PC输出唯一 E9_PC_CLOSED actualOriginalReturns=true，同handle的pcClosed allOriginalsReturned=true；原Java自然exit0，两reader返回。没有kill/人工force-stop/重启/换port/清数据/卸载/ABORT/账本重置/actor2/actor3/产品激活/播放。剩余额度不用于自动续跑。

D1 NOT_PASSED，M0 NOT_STARTED；全部P0、许可证与历史FAIL结论不变。本批不解除产品准入限制。

## 证据索引

根目录：docs/tester/D1_E10A_EXECUTION/4f21f71a-bf66-4a44-a287-320f0ae25fde。inputs为绑定输入，registry为原封存文件，evidence含所有原argv/stdout/stderr/实际exit和归还回执。

- evidence/independent-execution-audit.json：SHA9e2288bcbf4d7bd67b41557baf5411d1630b70d3c06033e340b8e31ad8503ee6。
- evidence/command-resource-ledger.json：SHA1dd30546a914311c7387a4bbe516eb69b64c6eaf0bf5c359ca185e9a4729e2cc。
- evidence/evidence-manifest.json：SHAe045e98bae54159c863f5ac01823cc5fc70c91591247681dc46f3cf917846726，逐文件pin，排除自身、后生成报告和通知回执。
- evidence/final-dag-audit-original-failure.json：原断言失败、已完成与未到达检查明确分列；无final-dag-independent-check PASS文件。
- evidence/device-final-independent-check.json、identity/commit/archive/ack独立检查、原受管控制台、manager-final-client-receipt.json及最终PC回执共同支持本报告已完成部分。

报告完成后立即通知负责人，并保存发送回执；不自动进入后续测试。
