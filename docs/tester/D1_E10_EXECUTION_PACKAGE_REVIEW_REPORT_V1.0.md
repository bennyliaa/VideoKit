# D1 E10 精确执行包独立复审报告 V1.0

2026-10-18；tester；依据 `docs/milestones/D1_E10_TESTER_REQUIREMENTS_V1.0.md`。审查四文档、HANDOFF、机器计划、模板、只读校验器、已有验证记录及实际冻结生产源码。没有运行候选脚本或生产测试。

**结论：包完整性与准备材料 PASS；执行准入 BLOCKED / NEEDS_MINIMAL_CONSOLIDATED_FIX。确认 coder 的 E10-PREEXEC-BOUND-CLEANUP / P1；新增 E10-POSTARCHIVE-STOP / P2，需同时补阶段化收尾规则。当前不能派设备写迁移。** 正常提交链在静态上可由现有CLI表达，失败/停止出口尚未完整闭合，不能把准备校验PASS当成READY。

本轮设备/ADB/构建/候选工具或测试重跑/媒体/迁移写均0；未生成实际新UUID、签发scope/token、H_actor/catalog或activation。E9B只读真机限定PASS保持原范围，D1 NOT_PASSED、M0 NOT_STARTED、长期准入OPEN及其余P0/许可/历史FAIL保持。

## 1. 独立完整性与证据范围

独立审计：[independent-package-audit.json](D:/CodexProjects/VideoKit/docs/tester/D1_E10_EVIDENCE/independent-package-audit.json)。仅自编元数据/源码审计，没有运行validate_package.py、package_delivery.py或其他候选程序。

| 对象 | 结果 |
| --- | --- |
| E10外seal | `d9b684b1d5946533738139c170b95aae1c4cc4743ccc9c14fae07ad46e8f81c1`；67项immutable全匹配 |
| 清单与ZIP | manifest65项全匹配；ZIP66文件逐项与原文件一致（含清单）；67 immutable另计ZIP，口径一致 |
| ZIP | 144956B；SHA256 `564feb09a56b6ef7bd1e19512e93a8da1e39dafe7d45e9a8fd4a2bda27910c7e` |
| 外部来源 | 47项external-input-pins全匹配；原E9B402项及seal全匹配，无旧冻结修改 |
| 历史只读实机证据 | 原manifest的127项逐项核验匹配；只是历史已接受快路径证据，不是新现场采集 |
| 校验输入/记录 | 最终47项输入匹配；原两条命令/日志保留：准备校验PASS且公开BLOCKED；12个离线拒绝性检查PASS |
| 复用制品 | 原app/test/JAR大小与SHA全匹配；未复制或重编二进制 |

复用app version13 E9B PREPARE SHA256 `ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020`；test `2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`；host JAR `4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707`。原证书、7native/35依赖和许可范围继承E9B审计，不据此解除许可P0。执行计划安装0次，现场pair不符应停止另审，不能盲目重装。

## 2. 准确写范围、旧事实与授权DAG

descriptor为725B，SHA256 `4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb`，与原生产实际descriptor字节相同。expected-commit为244B，SHA256 `f0fc5dd5cac41d6d702b26d809f28ef52536633f04058a2dfe42e18f3cd7c542`，kind/descriptor/payload/policy与E9MigrationTransaction.commitRecord一致。这只是期望字节，不是已提交对象。

未来单actor1只允许在 `files/e4a_output_budget/legacy-acceptance/<新M>/` 新建：

| 文件 | 本次内容与生产单项界 |
| --- | --- |
| actors/0001.intent | 原新actor与实际BOUND hash产生后才能确定长度；≤2048B |
| n2-v2.acceptance | 精确725B；生产单项≤4096B |
| n2-v2.commit | 精确244B；生产单项≤256B |

三文件内容上界3017B，生产文件分配上界6400B，最多3个新目录。目录项、块与文件系统journal成本不包含在3017B内，不能称为全部磁盘成本。源码使用CREATE_NEW/O_EXCL、写后force/readback和父目录sync；原guard、13项metadata、0B输出及完整ledger只读取、验证和force，不追加R/S或重写旧字节。只有actor1，本包没有0002.intent执行许可或actor2模板。

独立重算已接受1011B前缀的完整链，3R/3S、reserved0、0+53651+53567=107218与机器计划逐笔task/状态/摘要/输出路径一致，无链错误。原13项metadata清单、budget730a73e1-50e1-4198-a515-047104f00e31、fence662e9ecd-bede-42e6-bb58-ce81d668ff44、原0B/S0及oldCloseACK=false均保持。合法完整settled后缀允许存在，不能冻结整文件为1011B或清账恢复历史；非零媒体只作元数据保全，不为取得当前文件SHA额外读payload。

scope模板为DRAFT_NOT_EFFECTIVE，新registry/migration/attempt/handle、issuedAt、执行派单和接受审查SHA均null；currentDeviceFacts=null、preflight=NOT_COLLECTED。四个旧只读UUID及PID17434/boot2/start16410590明确标为已结束历史，不可复用或升写。当前没有有效执行scope，也没有把模板值当现场证明。

授权顺序 scope真实原字节→authorization SHA→preparePlan→config→独立index 单向无环；scope不反含未来config/hash。项目/设备授权与负责人对具体终局策略/三文件/一次actor1的正式采纳分开，模板不编其他窗口用户原话，不另造随机token/签字框架。当前准备派单不产生写权限；后续scope须绑定修复后被接受的准确审查与执行派发，不能用本份BLOCKED报告冒充执行准入已通过。

## 3. 确认P1：E10-PREEXEC-BOUND-CLEANUP

触发：合格REGISTERED_MIGRATION身份已返回，RESERVE已持久化，EXECUTE_COMMIT尚未发送，需要停止。静态见证，未运行复现：

1. [E9Registry.reserve:123](D:/CodexProjects/VideoKit/docs/coder/d1e9b/src/com/videokit/spike/e4/E9Registry.java:123)已CREATE_NEW identify.json、reserve.json并记BOUND；Android尚未bind/预留execute。
2. [E9MigrationRun:72](D:/CodexProjects/VideoKit/docs/coder/d1e9b/src/com/videokit/spike/e4/E9MigrationRun.java:72)按executeDone生成phase；没有执行的原return仍为IDENTITY。STOP只使其PENDING，不会产生COMMIT。
3. [HostManager.ARCHIVE_RETURN:81](D:/CodexProjects/VideoKit/docs/coder/d1e9b/tools/E9HostManager.java:81)按IDENTITY调用captureIdentityForFinish；[Registry:126](D:/CodexProjects/VideoKit/docs/coder/d1e9b/src/com/videokit/spike/e4/E9Registry.java:126)明确拒绝reserve.json存在。
4. 即使只移除这个拒绝条件，[Registry:128](D:/CodexProjects/VideoKit/docs/coder/d1e9b/src/com/videokit/spike/e4/E9Registry.java:128)仍再次CREATE_NEW identify.json，会与RESERVE已建文件冲突。既有identify内是原合格身份证明；取消后的原return可能已是新PENDING字节，不能把整份identify直接覆盖为它。
5. [HostManager:63](D:/CodexProjects/VideoKit/docs/coder/d1e9b/tools/E9HostManager.java:63)的ACK要求returned.json与当前原proof逐字节相同；没有合法归档便不能ACK→normalfinish。原Remote/custodian因此必须保持，不能用设备尚未写文件或锁已释放代替正常结束。

**确认P1，阻断执行。** 不能为取得收尾强行EXEC、造COMMIT return、直接编辑registry、第二close、kill或换manager。

最小修复应提供严格的BOUND但未执行取消/身份收尾：核原同actor/同plan/reserve/连续registry、没有任何EXEC意图/未预留在途execute、真实当前原identity资源已返及写入口永久停止；精确复用并验证已存identify/reserve，保留原字节与BOUND历史，再归档当前原取消return和唯一ACK/normalfinish。仅executeDone=false不够，不能用EXEC已发后缓存的旧IDENTITY帧绕过在途COMMIT。终局迁移/actor2资格仍必须COMMIT原返回，不因这个身份收尾入口放宽。

## 4. 新增P2：E10-POSTARCHIVE-STOP，归档后STOP会破坏ACK前置

E10失败说明允许原custodian白名单CONTROL STOP_DEPENDENCIES，但没有按“归档前/后”限制。现有公开入口也无相应阶段拒绝。

静态见证：原COMMIT已全部返回并ARCHIVE_RETURN保存R0；随后在ACK前发送一个合法STOP。 [Run.stop:78](D:/CodexProjects/VideoKit/docs/coder/d1e9b/src/com/videokit/spike/e4/E9MigrationRun.java:78)调用pend清旧proof、stateSeq递增并生成PENDING的R1；[HostManager:65](D:/CodexProjects/VideoKit/docs/coder/d1e9b/tools/E9HostManager.java:65)采用新frame。不可覆盖的returned.json仍是R0，下一ACK在原字节比较处被拒；再次ARCHIVE也不能覆盖CREATE_NEW的R0。即使物理资源已返，这条停止序列也没有正常结束出口。没有实测此序列，不标为已发生任务事故。

**P2，需与P1集中处理。** 最小方式可为阶段化收尾：归档后只允许精确ACK/独立finish等，不再发送会改变原terminal return的STOP；在生产host入口于写intent/发送广播前拒绝这种不适用动作，或实现经审查的原终局回执稳定语义。不能让拒绝再次触发原proof改写或消耗唯一ACK后再“重试”。不需为此另起通用取消/凭据框架。

## 5. 正常链及其他失败分支的可执行性

| 分支 | 静态结论 |
| --- | --- |
| 正常identity→RESERVE→一次EXEC→COMMIT原归还→ARCHIVE→ACK→normalfinish→审证→SEAL | 现有CLI/record schema可表达；仅静态可达，写路径真机NOT_RUN |
| 尚无reserve的合格identity需要停止 | STOP后原IDENTITY/PENDING可由archiveComplete收尾；无actor/无原有效回执则保持隔离，不能补造身份 |
| RESERVE已落、未EXEC | P1确认，不能正常归档ACK；仅改一条reserve条件不足 |
| EXEC意图已发、响应未知 | 原请求消耗且不得重发；剩余额度内仅STATUS核实/原scope收尾，不重获资格，不自动进入final |
| 部分三文件、FAILED COMMIT但原全部真返 | returnedForArchive允许FAILED或PENDING、device ABSENT的实际COMMIT归档；不能强求deviceRecord完整才准安全收尾，final仍拒绝 |
| 超期PENDING且实际晚返 | 可按原字节归档ACK/normalfinish；超期不改QUALIFIED。仅满足实际晚返+deviceRecord/normalfinish等严格门后，未来actor2才可另派 |
| 已归档后STOP | P2确认，当前不受阶段限制会改摘要并破坏ACK |
| ACK响应未知 | 唯一ACK不重发；只按已有原归档、原系统finish/代次事实有限收尾，不能只看finishClaimed |
| registry不连续、force/close/alloc/reader UNKNOWN | 保留原Store/Process/remote/custodian，有限通道不等于一定可正常结束；不改账、换port或另manager“恢复成功” |
| 日志容量过界、normalfinish证据缺失 | 无final；不clear或tail拼证。建议≤800000B预检只留余量，不能保证之后不增长 |
| PC进入failed/超期后经CLEANUP取回合格Android COMMIT | 可证真实资源归还并收尾；不能据Android结果忽略PC原失败。CLEANUP禁止SEAL_FINAL，失败manager不会自动恢复发布资格 |

这里的“停止依赖”应区分PC停止后继与实际Android STOP控制；不是每个失败切点都机械补一条STOP。正常归档后有正确原终局return时，应沿精确ACK/finish收尾；原数据/资格已坏或未知则保留隔离，不造安全出口。

原两phase10秒、每控制5秒、Android≤8/STATUS≤3、EXEC/ACK各1、本机STATUS/OP/CLEANUP共≤16、原accept128不清零、Process≤96、独立元数据客户端≤20保持。计划普通链4控制或加最后STATUS共5，给失败收尾留余量；不能把额度上限当任意循环次数或把仅单actor的6400B扩为actor2的8448B授权。

## 6. 校验器与activation DAG的有效范围

validate_package.py静态AST和完整源阅读符合只读本地约束：读取/解析/hash、UUID语法检查，无网络、subprocess、写文件或UUID生成API。默认分支核准备包；--bound-dir仅核未来受控输入的结构/hash/新旧scope隔离、canonical plan/config/命令及原receipt pin。当前没有bound正向现场实例或运行，状态仍公开BLOCKED。

12个已有拒绝检查覆盖重复key、非有限JSON、canonical格式、路径/摘要、新旧身份和时间戳语法；它们不是生产取消、COMMIT或真机测试。校验器只检查原receipt可读取/摘要相符及执行者断言，不能认证采集真实性、全部现场语义或授权文件的真实派发者；这点与文档限制一致。后续实际receipt须独立核，不能只提交九个true布尔值。

activation依赖顺序合理：真实scope/审查→plan/config→原actor/BOUND/设备三文件→原COMMIT return+normalfinish→final event head→catalog/checkpoint/seal→独立接受→另派导出策略→必要新版本构建→实际APK摘要入独立release→受管部署→每个新host真实当前观察。没有要求未来APK给自己预填SHA，scope/index和final/release之间也没有哈希环。当前无真实H_actor/catalog、activation输入或构建；PREPARE的CATALOG_SHA=ABSENT不因静态计划变成grant。

## 7. 最小下一批建议

建议一次集中实现/执行包更新，再整包复审，不先上设备：

1. 补BOUND未执行取消的严格合法归档/唯一ACK出口，验证并复用既有identify，不能覆盖原合格证明；EXEC曾发/资源在途/actor或reserve不匹配必须拒绝这个入口。
2. 补归档后停止的阶段规则/生产host前置门，保留准确原return供ACK；明确PC failed后只清理、不SEAL。同步失败表、条件命令和机器计划，避免执行者误用白名单。
3. 用实际生产Run/Registry/HostManager或共享公开控制边界做有限本机定向验证：BOUND后不EXEC→停止→归档→一次ACK/finish；identify冲突与错误actor/已有EXEC拒绝；已归档后STOP禁止或终局稳定；原UNKNOWN仍不第二close。保留原字节、事件链和三文件0写/旧账守恒断言，不需要重跑19/32/24或native套件。
4. 不修改旧E9B/E10冻结。新包准确列实现差异与host JAR来源；若修复只影响PC且能证明Android ABI/行为未变，可复用已测APK。若触及Android共享门，则按实际影响一次集中构建和身份审计。不要为文案或协议批标签重复构建；必要编译不应以“保持旧hash”规避。新版本/制品发生变化时同步全部pins、现场pair门及activation最低版本。
5. 修复后更新完整执行包与接受审查引用；负责人再作准确单actor1派发和一次新身份生成。当前不生成这些值、不问额外设备使用许可，也不以假scope或已结束只读actor代填。真实终局后activation仍独立派单。

旧账、0B/S0、107218消费、原guard/fence、历史输出与oldCloseACKfalse均保留，不读非零媒体、不清账/改R/S/重新ABORT。Framework/独立Kit/Flutter、48资源/严格六帧/full EOF/1000us、全部许可/P0保持。报告冻结后主动发负责人并另存回执；当前设备保持停止。
