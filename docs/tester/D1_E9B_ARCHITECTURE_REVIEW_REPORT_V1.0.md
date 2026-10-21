# D1 E9B 整包独立静态复审报告 V1.0

2026-10-18；tester；依据 `docs/milestones/D1_E9B_TESTER_REQUIREMENTS_V1.0.md`。候选 `docs/coder/d1e9b`，version13 / D1-E9B-PREPARE。复用E9/E9A已成立范围，审查本次实际生产Store、入口监督、accept门及最终完整冻结。

**结论：完整性 PASS；E9A-F02 / 原E9-F02残留P1、E9A-F01连接硬界P2均 CLOSED_STATIC_LOCAL。本轮无新增阻断缺陷。SUPPORTED_FOR_FINITE_READ_ONLY_IDENTITY_CONTROL_BATCH，可由负责人另派有限READ_ONLY_IDENTITY真机批次；本报告本身不执行或批准设备动作，不授写迁移/activation准入。**

关闭范围仅为静态实现与已有有限本机证据。真实Android启动/权限/身份/原FD/normal finish仍NOT_RUN。D1 NOT_PASSED、M0 NOT_STARTED、E6B-OBS-F01长期准入OPEN；其他P0、许可和历史FAIL保持。本轮tester设备/ADB/安装/构建/候选自检重跑/媒体/迁移/ABORT均0，未生成实际配置许可、token、H_actor、catalog或activation。

## 1. 独立完整性、来源和必要构建

独立审计：[independent-metadata-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E9B_EVIDENCE/independent-metadata-audit.json)。审计只读/hash/解析文件及ZIP/JAR/ELF，不执行候选脚本或生产程序。

| 对象 | 独立核验 |
| --- | --- |
| 外seal | SHA256 `6f8c1ffffa6bff17da48b7067594d33980c443ff03a7c547e917f0814add2c92`；402项 immutable 全匹配 |
| 清单/ZIP | manifest400项全匹配；ZIP401文件逐项与原文件比较无差异，包含源清单；402 immutable另计ZIP，计数一致 |
| ZIP | 24208160B；SHA256 `8c5952d929aa40edd17fd7c37dbdba69c6c49e4212da12103c6175506aa075ae` |
| version13 app | 10643006B；SHA256 `ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020` |
| androidTest | 2749733B；SHA256 `2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`，与E9A逐字节相同 |
| 最终Android输入 | 163项全匹配；快照SHA256 `e1e32550e4011d2d3fe0dd51c8ea19628a42010c53ccf7d9ea67e5a49b961bf0` |
| 生产host JAR | 259343B；SHA256 `4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707`；158个生产class逐项匹配源码摘要、002编译class与004编译class，无测试类 |
| 继承 | 146个JAR类与E9A按字节相同；130项严格逻辑/原生继承输入、59项Android入口继承输入均匹配，4段关键生产函数与E9A相同且按原区段取值规则重算摘要匹配 |
| 历史冻结 | E9A733/E91045/E7A200/E8A42项及各原seal全匹配，无历史文件被本轮修改 |
| SBOM/native | 35坐标/7原生库差集为空，全部SBOM组件与E9A一致；APK内7个so摘要及ELF LOAD 16KiB alignment通过元数据核验 |

两份已归档APK签名报告与audit一致，原证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`；本轮未重复运行签名工具。包、角色/ABI和真实版本沿最终APK审计。E9AndroidIdentity实际检查version13；runner/launcher保留 `D1-E9A-PREPARE-TABLET-20261018` 是协议批标签，默认inspect文字也不是新版安装身份，不因此要求改名重编测试包。

共享Store源进入Android输入，故本次一次集中离线main-001重建有必要；原日志BUILD SUCCESSFUL、68任务、1m15s，无repair/native重编/下载。没有以旧APK冒充新版本。JAR直接打包已验证的002生产class，004新增测试的全部生产class仍相同；三个默认入口原运行记录exit0/INSPECT_ONLY，本轮未重跑。

## 2. P1：长期Store原owner和首次registry IO边界

### 2.1 walk在allocate前登记，未知不会消失

`E9Registry.Store.outstanding`从只容纳IO holder改为容纳E4Owned<?>，新增统一register/retireReturned。checkTotal先在同一Store登记原walk，再调用Files.walk及各平台切点；returned()遍历同一长期集合。register检查既有原资源实际返回，只退休CLOSED，不用healthy=false代替归还。

分配未返、Iterator/read/遍历异常、close在途、Exception/Error/UNKNOWN均仍能由Store与监督者追到原holder。finally只对OPEN/READY执行原close；UNKNOWN/ALLOCATING/CLOSING不二次close求成功。close抛Error时E4Owned可能保持CLOSING，仍returned=false。业务已失败但原close真正完成时允许returned=true和正常pcClosed，不把所有已知失败都永远当在途。

对应实际生产证据：WALK_ALLOCATE的真实worker卡在分配切点时，Store已登记1个ALLOCATING holder，监督者不能pcClosed；WALK_CLOSE_LATCH_EXCEPTION/ERROR在业务异常后原close尚未返回时保持CLOSING，放行原close真实完成后才自然关闭。WALK_ALLOCATE_UNKNOWN/CLOSE_UNKNOWN/ITERATOR_UNKNOWN/CLOSE_ERROR原状态UNKNOWN或CLOSING、registered=1、returned=false；重新checkTotal拒绝且walkRegistrations不增加，证明没有用新walk替代或重复关闭旧未知对象。

### 2.2 同一监督者在首个原registry IO前持有Store/Registry

`E9HostRegistry.create()`先构造IO-free Store并交给supervisor.retainRegistry，再创建/保留Registry；随后才initialize/openKnownHead。Store独立强根不依赖HostManager字段赋值或authorityCallActive标记。prepareRegistry失败而manager字段尚未赋值时，supervisor仍可直接看到Store原holder；原E9A误判registryReturned的路径已封闭。

两个真实CLI共用E9HostRegistry.boundary结束门。HostManager在prepareRegistry之前已有监督者，原console的EOF/异常结束门保留；activation在openKnownHead、approved-export、recordActivationRelease及后续部署之前创建同一个监督者，Processes复用它。activation/export不再在登记存储操作完成后才开始监督。只有原Store、Process/pipe、Remote、accepted clients与原监听器均实际返回才pcClosed。

直接验证调用真实生产prepareRegistry、openReviewedRegistry和双方共用boundary。MANAGER_INIT_UNKNOWN/OPEN_UNKNOWN、ACTIVATION_OPEN_UNKNOWN/FILE_UNKNOWN/RELEASE_UNKNOWN在没有Process/Remote的情况下仍保留同一Store原未知资源，不因入口finally退出而丢失。EXPORT_SYNTHETIC_REJECTED原业务拒绝但资源真返，允许正常关闭。测试没有绕过Device CLI环境门；原配置pin和受审环境仍是后续实际入口条件。

本项关闭的是指定原registry资源和管理入口边界，不泛化为任意JDK临时文件操作、全部内核故障或所有平台排列均已实测。实际获批Device CLI、真实activation导出/发布均NOT_RUN。

**E9A-F02及原E9-F02残留P1：CLOSED_STATIC_LOCAL。** E9A已支持的ProcessBuilder/pipe/reader/decoder/console部分继续成立。

## 3. P2：128实际accept硬总界和耗尽后的原责任

reserveAccept在实际accept之前于短锁内保留额度；原accepted holder也先登记。已实际返回的Socket立即resolveAccept(true)，早于解析/处理/额外平台调用，未处理连接同样占额。accepted+reservation不超过128，累计不清零；明确SocketTimeout无接入才退在途保留，歧义失败保守占1并保留未知accepted holder，停止后续接入。

达到128后admissionExhausted阻止后续实际accept，closeListenerOnce只尝试一次原listener close；最后一个已接受Socket仍按原holder收尾。监听器CLOSED/UNKNOWN/CLOSING参与最终资格，原Process wait/reader/pipe、Store及Remote继续监督，不能为关listener而遗失它们，也没有换端口/续额。

ACCEPT_SERIAL/UNPROCESSED/CONCURRENT使用真实本机socket：128个实际accepted Socket计数，128号在处理前已占额，额外129+请求没有新handler。TCP握手/内核队列不算应用实际accept。LISTENER_UNKNOWN/UNKNOWN_BEFORE证明native已关但无Java ACK或close之前抛错时都不accept129+，listener只尝试一次close。ACCEPT_PROCESS/WALK在额度耗尽后原Process/pipe或Store尚未返，原custodian继续持有；资源真返后才结束。UNKNOWN_PROCESS最终原Process已返但listener仍UNKNOWN，仍无pcClosed。ACCEPT_EXCEPTION原accept结果不明保守计1，未知holder保留，无后续处理，不返还已消费额度。

明确代价：额度耗尽后同一TCP状态/CLEANUP端点不可再用，隔离ACK以ACCEPT_BUDGET_EXHAUSTED公开，不假称另有可用查询入口。原non-daemon custodian仍在同JVM保留责任；这不等于无限收尾能力。未来小批须预留查询/收尾额度，不能到128后再要求换端口或新manager续接。

**E9A-F01 / P2：CLOSED_STATIC_LOCAL。** 永久内核accept/close故障和所有调度排列未穷举；硬界的源门与有限真实边界证据成立。

## 4. 24组定向记录、失败留痕与UNKNOWN口径

独立核对24组映射：1294边界断言，另12共享合成元数据夹具断言，共1306。23组来自production-002，ACCEPT_EXCEPTION来自accept-failure-004。65份原日志/输入/命令/teardown引用的大小与SHA全部匹配；各结果、断言和原状态记录一致。

| 组别 | 已执行实际生产范围 | 限制 |
| --- | --- | --- |
| WALK_NORMAL/ALLOCATE/ALLOCATE_UNKNOWN/READ_EXCEPTION | 实际Files.walk、先登记、分配在途或未知、读失败但真返 | 分配未知切点在实际Files.walk前；不冒称内核已经分配了流 |
| WALK_CLOSE_LATCH_EXCEPTION/ERROR/CLOSE_UNKNOWN/ITERATOR_UNKNOWN/CLOSE_ERROR | 原迭代、原Stream.close、Exception/Error及真实close前后Hook | 永久不返仅验证有限观察持有语义；不是无限时长运行完成 |
| MANAGER_INIT_UNKNOWN/OPEN_UNKNOWN | 实际生产prepareRegistry与共同入口boundary | 没有实例化获批Device CLI，不冒充真实设备配置 |
| ACTIVATION_OPEN_UNKNOWN/FILE_UNKNOWN/RELEASE_UNKNOWN/EXPORT_SYNTHETIC_REJECTED | 实际openReviewedRegistry、FileChannel/Store、release下层操作及合成导出拒绝 | 使用SYNTHETIC_LOCAL元数据；没有真实token/catalog/activation |
| ACCEPT_SERIAL/UNPROCESSED/CONCURRENT | 实际128/129+socket、前置保留、未处理占额与并发客户端 | 不是同机恶意用户/无限压力模型 |
| ACCEPT_LISTENER_UNKNOWN/UNKNOWN_BEFORE/UNKNOWN_PROCESS | 原listener实际关闭前后异常、只关一次、未知不结束；真实child另行真返 | 平台异常为Hook，不是Windows内核注错 |
| ACCEPT_PROCESS/WALK/EXCEPTION | 实际ProcessBuilder/管道和Store原close在途、accept异常保守计额 | 原child有有限正常退出机制；没有ADB进程或Android广播 |

24组中11组原资源真返并记录E9_PC_CLOSED；13组保持未返，originalCloseAck=false、productionExitAllowed=false且无E9_PC_CLOSED。controller只结束已完成有限断言的专用合成JVM，不能将其退出码当生产安全退出：检查器为记录断言通过会归一化测试结果，此PASS证明“原未知时拒绝退出”，不是“UNKNOWN已被成功关闭”。所有实际子进程返回条件及Store/listener状态分别核对；尤其ACCEPT_LISTENER_UNKNOWN_PROCESS原进程0在途、listener UNKNOWN仍阻止关闭，不能只看allOriginalsReturned=true漏掉listener。

ACCEPT_EXCEPTION属于原accept未知、状态通道已不可靠的路径，共同boundary线程仍阻塞，没有伪造隔离/close ACK；日志保留原handle/PC PID和原状态，controller有限清理也不构成生产处置方案。不能据此承诺未知端点始终可查。

production-002的80项输入中，只有后续增加ACCEPT_EXCEPTION的测试源码与当前路径不同，精确对应保留的E9BProductionCheck.before-accept-failure副本；004的80项输入全部匹配。002/004全部158个生产class与最终JAR逐字节一致，变化没有混入生产。compile-001为初始单组编译/探测；003只有setup-failure.json，记录过滤reference历史工具目录之前的准备失败、无编译或执行，不算缺失测试PASS；004修正文件过滤后完成新增组。没有覆盖原失败历史。

旧19/32/native未重跑，不累计历史PASS。E9A已关闭的F01非等待与独立broadcast、F03同一5秒decoder任务、F04提前撤销/epoch发布仍按源文件与关键函数继承；6个Android公共入口和Runtime撤销序列继承E9A原SDK桩有限范围。本轮没有重新运行SDK桩，也没有Android系统运行证明。

## 5. 下一准确范围：可另派有限只读身份/控制批次

本轮未发现需要继续阻断该小批的实现缺陷，建议负责人另派准确测试需求并给出实际受审配置/scope。候选范围：

1. 仅HA1Q6WXR/user0；先核真实已安装pair/版本/role/ABI、原UID10221/10222、原证书及无相关在途进程，按本报告最终APK/JAR精确摘要准入。当前设备身份未在本轮读取，不把历史安装版本当现场事实。若需更新，两包按同批部署门统一安排。
2. 一次显式READ_ONLY_IDENTITY，不能使用兼容默认REGISTERED_MIGRATION。受审配置绑定实际scope/plan/版本13精确pair和原授权/评审引用；不能用任意64hex充批准或把SYNTHETIC_LOCAL传入Device CLI。
3. Android控制总≤8、STATUS≤3；建议本机STATUS/OP/CLEANUP合计≤16，并预留收尾查询。仅验证非等待client返回与actor独立存活、DUMP保护状态入口、真实boot/start、identity原FD返回与5秒状态链路。禁止RESERVE/EXECUTE_COMMIT/SEAL_FINAL、媒体、原budget变更、actor2/3或自动重试；不得循环轮询或重发已发ACK。
4. 有效原身份和实际return bytes齐全才归档相同回执、唯一精确ACK_FINISH，再独立核原PID缺席及normal finished inst/finish锚点，最后核PC原资源与责任归还。不能以launcher退出、磁盘文件、native close已发生或finishClaimed代替。身份/receiver/原返回未知立即停止依赖并保留原custodian/handle，只有原scope内有限收尾；不kill/换端口/清理数据或重新ABORT。
5. identity-only结束不构成COMMIT/final，不可自动转写或复用为写迁移scope。设备批次需独立报告；负责人根据真实资格和最终范围再决定迁移，真实final facts/canonical catalog独立接受之后才可另派activation。同一catalog/head/实现与精确发布门继续有效。

这是可供负责人派单的有限范围建议，不是本轮执行许可。本轮不连接设备、不制作配置/token、不自动启动下阶段；平板使用已有用户授权，无需重复询问设备使用许可。

## 6. 原账目、历史与项目门保持

原budget `730a73e1-50e1-4198-a515-047104f00e31`、107218消费/三R三S/reserved0、原N2 ABORTED0B/S0、原guard/输出/前像/pending归档、fence `662e9ecd-bede-42e6-bb58-ce81d668ff44`、oldCloseACK=false和旧无帧根因UNKNOWN保留。本轮只是继承历史已接受事实，没有重读设备或改写旧FAIL。固定1011B已接受前缀后仍允许合法完整settled R/S后缀，不能永久锁死整文件长度。

设备4文件8448B/3目录、PC20种登记元数据155648B且≤192KiB+原日志1MiB、40遍历项、catalog16KiB≤24KiB、最多2actor/各8控制STATUS3、两phase各10秒、48新增Android owner；PC96原操作、128总accept，以及原4MiB预算/单项2MiB/128任务均保持。严格六帧/完整EOF/1000us、既定Framework/独立Kit/Flutter及全部许可/P0不放宽；SBOM不变不等于许可已获批。

原MP4限定实机PASS保留，AVI/能力/cancel待测；D1未过/M0未启/长期准入OPEN。旧E9/E9A报告保持原时间和结论，本报告仅记录当前新冻结的审查。报告冻结后主动发负责人并另存通知回执。
