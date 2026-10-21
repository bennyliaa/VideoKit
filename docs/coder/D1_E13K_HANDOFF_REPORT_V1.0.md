# D1 E13K 一次G补充发布绑定完整交付 V1.0

2026-10-18；coder交VideoKit项目助理。依据负责人E13K正式派单与R1独立功能复审§4，完成唯一准确release/scope/JAR/脚本/argv/预算机械绑定及冻结自检。**状态SELF_VERIFIED_AWAITING_INDEPENDENT_MECHANICAL_CHECK / NOT_EXECUTED。** 请整包交tester机械核验；PASS后依负责人已明确的一次G只读授权承接执行，不再进入功能实现循环。本轮coder未执行有效dispatch、launch或原observer owner。

## 1. 准确冻结身份

- ZIP：D:/CodexProjects/VideoKit/docs/coder/D1-20261018-E13K-source.zip，778490B，SHA256 `51e5c9374d0e908995e107758f99ef01398661beb75be97cb3e5721d126743be`。
- 外seal：D:/CodexProjects/VideoKit/docs/coder/d1e13k/evidence/e13k-freeze.json，17237B，SHA256 `bb3e6511dcb62146d6ed87686ebdb5818338b0cb22ddc0fbdc65ceaa028c0916`。
- 69个准确ZIP成员/70条唯一冻结记录；默认verify、准确seal SHA显式verify、help、pack-help实际均exit0，71份文件前后字节一致、writes0。校验不运行任何launch/有效角色，不编译、不网络。
- 最终只读回执：D:/CodexProjects/VideoKit/docs/coder/D1_E13K_FINAL_READONLY_VERIFICATION_V1.0.json，在ZIP外避免自引用。本完整报告与通知回执也在ZIP外。
- 十四组旧seal及准确成员保持，含最终R1、初版J及I/H/F等全部已冻来源；不覆盖R1，不把重叠manifest行数相加冒唯一文件数。

## 2. 唯一scope与typed release

新执行batch：`d7b4ca4f-36a3-49c9-9b61-cdc7ebdcb5b6`；originalScope：`aeefe32f-816d-4c0b-aca7-16f76dbd45ff`；typed release.scope仍原runtime SHA `116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef`。新批次身份、原任务UUID、原目标runtime SHA分栏，未新建产品instrumentation scope或重发旧case。

功能review准确SHA：`f9e5a63acf2aea2fc51c9c71ec50ceba5ed080cdded46676cd7fd9cec6374583`。typed e13jFixedReadOnlyRelease精确6字段：kind、上述scope、serial HA1Q6WXR、review该SHA、budget262144、requests2，真实E9Record.parse/准确canonical重序列化及最终class反射常量核验通过。仅生成这一个scope/release，反复机械计算未重生成UUID。

| 精确文件（均在d1e13k） | 字节 | SHA256 |
| --- | ---: | --- |
| typed release | 258 | `a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03` |
| 唯一执行scope | 407 | `ea8a82cb947420197e42f62539ec327147117580e83ada5598981a7dfa8a6a5e` |
| 外层准确command request | 204 | `4b50549986a01fb5475c9633f4d8557696c4524693f4a104587bba8eecb4a8b0` |
| observer request | 831 | `a2040964fbcbae5e070d84472a7e4d73454e6f1488441466cc96ec8723e5bf5d` |
| 最终JAR | 347716 | `09aec958873b2f4cf6fcb562e608d0143f7f865c742170bd30fd49432b5f9797` |
| observer脚本 | 9965 | `b6ab0aec0df4ec62a2b317d7abcf21a8c7d0c63e5b2b9605c0a12e9bb506078d` |
| 唯一launch脚本 | 1953 | `5b995d151de6b0d3aa84e9c013e2dcb44440417fdee3a29341e47ce000124511` |

文件精确相对路径及全绝对路径在evidence/final-binding-receipt.json、release/execution-command.json、外seal，机械review字段当前null，不假称tester已通过。功能review→release SHA→Java策略/JAR→scope/request→observer request固定SHA→launch固定各文件hash→外置机械回执，无循环；release不自含未来K验核报告SHA。

## 3. 一次必要策略编译与193成员差异

一次javac只编准确策略E13JReadOnly及纯KBindingCheck检查类，对准确R1 JAR编译；未重编Socket/archive/identity或其他业务。最终JAR193成员中**192逐字节不变**，包括新编出的nested三个class也相同；唯一不同E13JReadOnly.class只含APPROVED_REQUEST_SHA及describe批准常量变化，检查类不进JAR。

真实javap -p -c -constants对照，只归一准确批准SHA→ABSENT、CP索引数字、水平对齐空格，所有指令、偏移、分支目标、成员/其他文字完全一致。原始javap及源diff保留。初次文本断言未消去CP数字宽度造成的两处空格，曾报NON_POLICY_DISASSEMBLY_DIFFERENCE；后续完善归一证明，无源码功能修正、无再次编译。没有把不等字节宣称完全相同。

最终JAR的真实反射常量与typed release SHA匹配，checker class独立目录仅存检查class，确保实际加载最终JAR；describe安全执行，未调用--g-readonly。无APK/Gradle/native、长套件或新框架，不重复已通过R1功能peer测试。旧F APK及许可门原样。

## 4. 精确observer、launch与8192外层份额

observer只绑定准确release SHA、最终K JAR路径、固定observer-request路径/SHA；最小request只有一个JAR pin，任意路径/内容不能通过精确请求gate。原R1 Process/唯一reader/文件/异常custody主体**实际字节不变**；没有删owner门或添加设备能力。新批次/originalScope记录进原observer intent，与外部scope文件/launch hash绑定。

launch无用户参数，先核release、scope、request、JAR、observer五个固定hash，再调用准确observer。原完整console由同原PS调用栈仅收取一次，不再次全量echo/另复制原文；仅输出≤128B摘要：r转述allOriginalResourcesReturned，m转述metadataRecordFilesReturnedAtConsole，h为已收console SHA。它不合成原close；receipt文件仍不自证自身close。原observer未返时launch亦不返回摘要，原全局custody继续持有，不取消/强关。

脚本完整AST、真实production policy前缀在owner标记之前的正向校验，以及对明确合成JSON的摘要格式检查通过。没有执行原owner或有效dispatch，合成布尔格式测试不冒真实资源ACK。

最终合并上界：

| 输入/副本 | 上界B |
| --- | ---: |
| typed release | 258 |
| execution scope | 407 |
| observer request | 831 |
| observer intent | 951 |
| PID记录 | 152 |
| pending记录 | 150 |
| receipt文件 | 2006 |
| 原facts console一次收取 | 2942 |
| 精确外层command request | 204 |
| framing/marker/有界摘要预留 | 256 |
| 合计 | **8157** |

在原8192内余35，总262144不增、不借其他份额。真实PS原序列化核算，25固定错误码保守并集含互斥项、4个metadata记录、uint64数宽、固定可信PS/.NET异常家族80字typename预留；不是任意注入pins/类型或任意输出副本承诺。前置gate失败未创建owner/文件的路径，全部输入加2048错误console上界3748，不能与不可能同时产生的完整receipt路径混为扩额理由。

最初7953上界未含后来单独列明的外层准确command JSON；最终补计其**实际Windows CRLF文件204B**为8157。曾按内存LF字符串估203B，实际PS预算子检查已返回PASS/8157，但父预期数字8156断言失败；保留原回执/执行脚本快照，最终算术核按实际文件204修正，无编译/dispatch重试。机械自检记录中的早阶段7953不是最终预算，不覆盖原证据。

## 5. 唯一可执行入口与停止门

机械PASS后执行窗口使用release/execution-command.json的精确四项argv：

1. C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe
2. -NoProfile
3. -File
4. D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/launch_once.ps1

先核完整seal/launch SHA，不旁路调用包内helper/直接observer全量echo。内部Java argv精确为固定D:/Android/Android Studio/jbr/bin/java.exe、-cp、最终d1e13k/artifacts/e13k-host-tools.jar、com.videokit.spike.e4.E13JReadOnly、--g-readonly、release/read-only-release.json绝对路径、批准SHA `a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03`。

原R1 root保持D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE，once=e13j-r1-g-readonly.once，wrapper id=E13J-R1-SUPPLEMENT-ONCE。已有/未知/记录失败不换目录/id重发。当前只准备字节，不创建真实once，也未核查原现场新状态。

最多两query固定127.0.0.1:5037/HA1Q6WXR、同原Socket transport→两既定shell-v2；第一实际成功/完整/无其他instrumentation/原资源join后才派生第二，不能外填旧/示例PID。第一失败、占用或UNKNOWN不第二；单query实际应用RX＋保守TX70656、通道合65536、metadata2048/256帧/10秒资格，余额0不探EOF/drain/强关，不重连/SDK fallback，不借未消费额度。

原exec42537最多一次空输入、≤10秒/≤65536B保证不足则该项BLOCKED，不循环/Ctrl-C/非空/取消Promise/重建session，不能借其额度。空返回不是原owner ACK。G旧host19:31:58只作历史，不增CIM；这次只读不自动处置/部署/续产品/T07。

## 6. 文档与交接

四文档在D:/CodexProjects/VideoKit/docs/coder/且入包：D1_E13K_RELEASE_BINDING_DELIVERY_V1.0.md、D1_E13K_BINDING_CONTRACT_V1.0.md、D1_E13K_MECHANICAL_CHECK_REPORT_V1.0.md、D1_E13K_EXECUTION_PLAN_V1.0.md；coder/tester正式需求在docs/milestones分别保存。两滚动文档顶部同步最终8157及精确一次机械发布安排，历史保留，包内封副本。

本轮未运行launch、有效--g-readonly/observer原owner，真实5037/设备/SDK/旧handle/PID/处置/产品测试均0。旧v17主PENDING、旧ps诊断LOST及H本地30384 RETURN_UNPROVEN独立，不补ACK/退款。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/历史FAIL/UNKNOWN/许可不变。

现完整冻结交负责人转tester机械核验。核验PASS后按负责人本次已明确只读授权进入执行窗口，无需再回功能实现循环；coder本轮到此只交准确制品与入口，不擅自执行。
