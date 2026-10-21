# D1 E9A 精确后续设备附录 V1.0

2026-10-18。本附录供静态审查，不是执行许可。当前无ADB/设备/媒体/真实迁移/activation；tester集中复审后负责人再定有限身份/控制批次与最终scope。旧E3许可已消费，不复用；本包没有真实配置、token、迁移UUID或H_actor。

## 唯一prepare候选

version12/D1-E9A-PREPARE；com.videokit.app / com.videokit.app.test；原证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。合同app UID10221、test UID10222须在后续实际部署前核实；没有本轮设备观测可代替。

|APK|bytes|SHA-256|
|---|---:|---|
|app-debug|10643010|`1edb820faea79cf87d261555adbd397f32c6796447ace127bd39cb756e10c841`|
|androidTest|2749733|`2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`|

APK目录 `D:/CodexProjects/VideoKit/docs/coder/d1e9a/artifacts/D1-20261018-E9A/final/`。同目录生产host JAR 255014B，SHA `709fa796ed59ce6394b25f75bc69391099f7a4d398cafbd79cef91ef257d17e4`，用已验证的Android Studio自带JBR启动；不含测试类。源码/class来源见host-binary-provenance.json。所有下述参数都是未填的受审输入，不是本轮可执行指令。

## 非等待、模式和状态

实际组件 `com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation`。e9Case=legacyN2Migration；e9Batch=D1-E9A-PREPARE-TABLET-20261018；e9Mode仅READ_ONLY_IDENTITY或REGISTERED_MIGRATION；e9Request是严格canonical identityRequest的URL-safe无padding Base64。无class/FD参数，实际launcher为am instrument -r，无-w。client命令退出不意味着Android actor、IO、正常finish或迁移完成；不从空stdout推断成功。

未来 `E9HostManager --approved-session <实际受审配置> <实际配置SHA>` 才开会话，默认无参数只inspect。配置沿E9 managerTrust字段，精确plan/app-test SHA/原签名/UID/版本/sourceReview/授权和评审引用/registryPath/NEW或已知head均须负责人提供，不以任意64hex本身当批准。

LAUNCH必须明确mode（文档要求显式填）；实现兼容缺mode时REGISTERED_MIGRATION，但任何模式都不自动RESERVE/EXECUTE。先外部登记，再非等待启动并保留remote责任。POLL实际发一个STATUS，seq消费，state=-1由原Run原锁取当前state；完整transport来自DUMP保护的ordered broadcast。其他控制仍用当前原stateSeq。初次缺receiver、无有效帧、actor/returned尚缺资格资料或超时均不得授写，停止依赖并保留原管理者；不通过等待client stdout求首帧，不循环STATUS。缺失序号保守扣额；actor总8请求、STATUS最多3。

READ_ONLY_IDENTITY身份返回后关闭写入口，STATUS仍可查询，所有晚到EXEC拒绝。已验证的有V2身份且原IO真返的identity-only回执可以ARCHIVE_RETURN、精确ACK_FINISH和独立正常finish，只有PC原责任结束，没有reserve/COMMIT/final/actor2资格。只读诊断与未来正式迁移应由负责人另派各自scope；不自动把已结束只读scope复用成写scope，也不自行生成新scope绕成本。

## 原执行与5秒控制

正式REGISTERED_MIGRATION只有身份原归还、外部BOUND reserve force/close/readback后才允许EXECUTE。接受写时先保留原队列/资格；身份和提交各10秒独立，不能重置未返原操作。每个STATUS/EXECUTE/ACK/STOP响应有同一个原5秒绝对任务，覆盖start/process/pipe/wait/语义解码，超时永久PENDING；一般安装和独立PS/logcat查询仍有原55秒界。已发EXECUTE或ACK intent只允许一次，即使未知回复也不换seq重发。

原返回必须精确actor/handle/seq/资格和全部原holder；外部真实归档相同return bytes后ACK同hash。正常finish独立核原PID不在、唯一E9_FINAL_FINISH锚点、其后ActivityManager Force stopping/Killing finished inst，不再以等待式instrument client结束当finish。只有符合实际最终scope的最后合格commit与全部前序处分才能审final；正常身份/失败收尾不激活。

actor2仅在原确切代次终止且SELF_NO_FD_TRANSFER，或原真实晚返非合格+正常finish后有限恢复。旧Java ACK不补写。原身份或返回不可验证就保留未知，不杀陌生PID，不启actor3，不删除torn对象或重新ABORT。

## PC输入丢失后的原管理者

实际管理者先打印E9_PC_SUPERVISOR_READY（handle、PC PID、本机127.0.0.1 port）。EOF/错误后pcIsolationAck只表示同JVM非daemon原custodian实际接管，不表示JVM/actor/pipe已结束。保留该JVM，禁止手动终止它冒close。真正全返且监听关闭才有E9_PC_CLOSED。

同JAR的 `E9PcClient --status <port> <原handle>` / `--operation <port> <原handle> <operationUUID>` 查询原对象，不碰设备、不耗Android STATUS。收尾 `--cleanup <port> <原handle> <原配置SHA> <canonical命令文件> <该命令SHA>` 只面向原受审配置和原manager；允许有限POLL/STATUS/STOP/精确归档ACK/原回执/独立finish或termination/INSPECT，拒绝新LAUNCH/RESERVE/EXECUTE/DEPLOY/SEAL_FINAL。不能以查询结果另造authority，也不能重启另一manager自动续未知head。状态通道本身UNKNOWN需原隔离处置，不能以杀JVM排除。

PC客户端只是查询/收尾桥，不是新根；仍是受信本机操作员合作模型，不宣称阻止有原配置/签名/管理员权限的人绕流程。禁止-d、uninstall/clear/restore/force-stop未知actor、换budget或手工装未批准高version旧码。

设备4文件/8448B/3目录、外部20文件155648B且≤192KiB+原日志1MiB、catalog实现16KiB≤24KiB、2actor/各8控制STATUS3、两phase10秒、48新增Android owner及原框架界不变。PC原对象96/本机查询128只界定新本机监督记录，不扩大Android请求或owner。

## 后续activation和当前结论

真实final facts独立接受后另派E9HostActivationSession阶段，同原实现、精确同head/catalog、同原签名和必要role/入口/版本差异；先固定实际catalog build input，再登记实际APK SHA，不能产生自指。当前PREPARE/catalogABSENT，无activation包、实际H_actor或approval token。之后每个新host仍要E9Runtime.observe实际核原guards/fence/完整合法后缀/无pending并原返回；旧4869退休历史例外不豁免当前原资源，也不复用旧livegrant。

当前D1未过、M0未启、长期准入OPEN；不启动正常四例、真实媒体导出或native fault测试。独立Kit/Flutter、严格六帧/完整EOF/1000us、原107218/三R三S/档案/fence/oldCloseACKfalse及许可P0保持。
