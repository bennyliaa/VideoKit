# D1 E13C HOST_ONLY 完整冻结包独立复审报告 V1.0

日期：2026-10-18。依据：`docs/milestones/D1_E13C_TESTER_REQUIREMENTS_V1.0.md`。候选：D1-20261018-E13C-HOST-ONLY。

## 结论

**复审通过，未发现新的准入阻断项。E13AB-DEPLOY-F01/P1在实际host接线、交付JAR及有限本机CLI证据范围关闭，支持负责人另派新准确六方法平板批次。** 这不是实际部署或六方法通过：本批ADB/install/设备/媒体执行0，APK/native构建0，真实scope/release/config/once均未签发。

后续必须采用新独立scope UUID、执行目录及新once路径，fresh M1后才考虑v15→17；不得回放原失败配置或继承旧37/56及余19。设备长期授权保持，不需重问用户使用许可，但本轮不自动执行设备。

原E13A绑定P1、只读P2及E13B元数据的已审有限范围保留；原执行报告中的失败不回写。D1 NOT_PASSED / M0 NOT_STARTED，全部P0和历史FAIL/UNKNOWN保持。

## 独立核验

tester产物：`docs/tester/D1_E13C_REVIEW_EVIDENCE/`，含独立`audit_e13c.py`、`independent-audit.json`、默认/显式verify/help/pack-help原输出及manifest。**2224项字节、成员、pins、原记录和计划一致性检查通过**，不是2224个功能用例。

本批仅读取源码、JAR/ZIP与已有日志；仅实际运行已读源码确认纯读的verify/help及tester自编审计，未运行pack、构建器、javac、候选JAR/检查类、旧绑定/source/信号测试、ADB或媒体。没有修改冻结交付、旧执行根或产品。

| 对象 | 独立结果 |
|---|---|
| 外seal | `14358fdb7e7900de669e76965c4ecce5b008eb8daea216b9abaa7f7891e45762` 一致 |
| ZIP | `1365dfa17cfaab28e9f4c2c8639bf204a95a0ca4949e837b6c77d3bfb0ced4d9`；141条封印记录/140个唯一成员逐字节一致 |
| 六份旧seal | E11基础375/R1 65、E12 46、E13 367、E13A 270、E13B 118条及封印全部保持 |
| 旧失败批次 | 原execution-manifest所列39文件及报告实际hash一致；原失败目录的真实once仍不存在 |
| 新host JAR | `docs/coder/d1e13c/artifacts/e13c-host-tools.jar`，299629B，SHA `9c36d04a728a5a5b6db04ab1ffbe3f5be051b84f249d8bdf868212ed03ef774c` |
| JAR来源 | 173个精确成员；168直接复用原E13A成员，5由两份host源码重编，与原编译产物一致，无检查类/SDK port或supervisor替身混入 |
| 只读入口 | 默认、独立seal pin显式verify、help、pack-help均exit0；142份审查集合前后字节不变 |

“5重编”是生成来源，不等于5份字节都变化：独立比较发现其中2个成员仍与base字节相同，整个新JAR共有170个成员与base字节一致。两份生产源码变化仅为E11DeploymentOnce及E13HostActivationSession。

核验器初版误把生产内部类`E9HostManager$CheckedFrame`的名称当作检查类；按实际检查类名及逐成员原来源校正后通过。候选未改，该核验器匹配错误不是产品FAIL，也未重跑候选测试。

## 实际once角色接线

`tools/E11DeploymentOnce.java`现在通过私有Role区分E11/E13A：

- 原两个公开构造仍选择E11，只接受`activation-deployment.once`，原调用签名和历史规则保留。
- 固定`e13Activation`工厂选择私有E13A角色，仅接受`e13a-activation-deployment.once`，并核canonical E9 record的kind为`e13ActivationDispatchIntent`。不存在可输入任意basename/公开Role的接口。
- `tools/E13HostActivationSession.java`在原已pin配置、绝对路径/registry外/固定新名校验后，实际调用该工厂；其生成的intent仍精确绑定config/release/scope/sourceAcceptance/原pcHandle和保留状态。
- helper的角色检查不是新的授权服务；完整scope/release/registry/sourceReview门仍由原公开CLI负责。不能把单独helper的kind校验冒称人类许可或抵抗恶意同UID代码。

原existing-parent/no-symlink、CREATE_NEW、完整/部分既有文件拒绝、write/force/readback及原close真返要求未被移除。attempted后同对象重入拒绝；异常不返回record成功，不进入后继SDK。原holder在首次文件IO前注册真实监督器，未知不通过第二次close补ACK。

实际交付JAR对应成员和编译输入已核，原E13A `E9HostDeployment`、`E9PcSupervisor`等168份直接继承成员逐字节一致，生产JAR没有替换其run或custodian。

裁定：**CLOSED_HOST_FIX_STATIC_AND_FINITE_CLI_EVIDENCE**。实际安装和设备SDK调用仍未执行，不能将此关闭写为部署PASS。

## 原记录与替身边界

已读核8个helper分支的原argv/stdout/stderr/退出与实际实现：E13_OK、E11_OK、E13_OLD_NAME、E11_NEW_NAME、ARBITRARY、WRONG_INTENT、FORCE_FAIL、CLOSE_IN_FLIGHT。8个检查JVM均自然exit0，含预期拒绝分支。

正常helper记录核实际intent文件、WRITE→FORCE→CLOSE_BEFORE→CLOSE_AFTER与readback。force受控失败无后继dispatch。在途close分支使用实际交付helper和真实E9监督器：原state=CLOSING、returned=false、SDK后继0，实际pcIsolationAck保持原custodian；只放行该原close调度后原worker自然返回、原监督器物理CLOSED，不以替身对象关闭代替。

8次公开CLI记录均是自然exit1的预期边界/拒绝，不是8次真实部署成功：

| 场景 | 实际有限证据 |
|---|---|
| 精确E13A新角色 | 实际公开main/helper从交付JAR加载；本机配置经历史DEVICE trust/registry门，写入本机local-test once后到首SDK前受控边界 |
| 第二JVM同配置 | 既存once拒绝，文件保持，不再进SDK边界 |
| 旧名/任意名 | 外层固定新角色校验拒绝，无SDK标记 |
| 错config role | 精确schema拒绝 |
| SYNTHETIC_LOCAL environment | 原真实DEVICE环境门拒绝，未伪造DEVICE环境绕过 |
| 部分文件/空文件 | 既有一次性文件拒绝，保持原字节，无SDK标记 |

精确正例只将测试classpath中的`E9HostDeployment.private run`换为：先记录准确首argv，再抛`E13C_LOCAL_FIRST_SDK_BOUNDARY_NO_CHILD`，未调用commands.run、未创建SDK进程。其首argv为原`adb.exe -s HA1Q6WXR shell run-as com.videokit.app stat -c %u:%i .`。授权/registry/main/helper没有替身，sourceReview/DEVICE材料只是已pin历史本机夹具，不是新设备许可。该port替身不在交付JAR中。

各CLI原stderr均包含真实监督器pcClosed/allOriginalsReturned=true。所有once写入只在明确的本机helper/cli-fixtures目录，不能将这些local-test文件当真实执行目录的once。

## UNKNOWN证据的精确范围

补强`unknown-jar-002`原记录确认4条helper class来源均为实际交付JAR，未在该检查阶段重新编译helper。受控CLOSE_AFTER异常时，原holder=UNKNOWN、returned=false、dispatch0、closeAttempts1，原对象重入被拒，未第二次close。

但其supervisor为**有限引用保留替身**：只证明实际helper保留同一原authority/未知状态，不证明永久UNKNOWN下真实非daemon custodian持续在线或最终物理归还。检查JVM退出0不能作为原closeACK。真实监督器的在途保管只由上一节CLOSE_IN_FLIGHT有限可返回场景及继承源码支持；永久UNKNOWN实际门继续未关闭。

初轮同源码另编helper及补强交付JAR检查两类记录均保留，最终以补强来源为准。原日志审计曾误将运行时生成的lambda也要求有JAR来源；修正只过滤现存日志中的生成类，没有重跑该JVM，不能将其登记产品FAIL。tester本轮只读这些记录，没有执行检查。

## 精确复用与新批派单条件

产品仍为E13A v17 / ACTIVATION / ABI1，source仍接受v15；三APK字节/签名与已审结果一致，无APK/native重建或升版：

| 制品 | SHA256 |
|---|---|
| E13A delivery/app-debug.apk | `962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad` |
| E13A delivery/app-debug-androidTest.apk | `83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13` |
| E13A delivery/fixture-debug.apk | `868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8` |

主signer仍`5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，fixture不同signer仍`45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9`。这些是按相同实际APK hash继承的已审签名事实，非本批Android UID实测。

三份M1/M2/M3完整argv原字节复用E13B，manifest SHA `223e0d42a045fce01df8c4564945221276fbe78120fa7dad60641a10a2985af5`，原34stat/18control、70/18/71记录、单64KiB/55秒及完整活动列表语义不变。16:06前旧批没有安装；15:59旧M1只是历史实测来源，本批没有重新确认平板或账档。

新派单必须：

1. 绑定本报告、新host JAR/seal/ZIP、原三APK及E13B完整metadata pins；sourceReview使用本次独立完整E13C报告，不能只沿E13B报告授权新JAR。
2. 新独立scope UUID/执行根，固定新目录内`e13a-activation-deployment.once`，例如草案`docs/tester/D1_E13C_TABLET_EXECUTION/<NEW_SCOPE_UUID>/deployment/`。不改原失败批config、不复用旧scope/once或原失败entry。
3. 保持原运行batch `D1-E13A-SOURCE-20261018`、实际runner精确四字段和原生产schema；M1必须fresh，核当前exactv15/UID/data、fixture不存在及设备/账档/占用后才部署。M2/六方法/M3沿已审完整门，不用历史M1或静态报告当实时grant。
4. 成功路径48=部署entry1+内部32+六Java6+六instrument6+metadata3；仅部署前ACTIVE占用可另至多2次M1，至少间隔30分钟，总上限50。文本1638400+131072=1769472B，余327680B，总2MiB。旧37/56、余19、ENV_RECOVERY额外host操作均不继承。
5. 新批额外STATUS/OP/CLEANUP查询0、隐含恢复/安装或方法重试0。环境失败停交负责人，不能自动start-server/kill-server、强杀、补close或以未发预留回充重试；占用不明/其他项目活动先等待。

source/取消/聚合仍原5000ms接口、30秒方法资格、4096B非媒体、计划6open/4224B read/7close（上限8/64KiB/16、每ticket更紧约束），媒体输出/READY/新R/S=0。正式六方法顺序仍ordinarySenderCannotBindCodec→authorizedHostSourceReadAndClose→oldGenerationNeverOpensSource→twoConsumersHoldSourceUntilLastReturn→cancelLateOpenRetainsOriginalOwner→lateReadAndCloseFailureDoNotReleaseEarly，每项一次/独立host，任一FAIL/BLOCKED/PENDING/UNKNOWN停依赖保原对象。

当前candidate-binding、device-plan、new-scope-draft的sourceReview/actualScope/release/config/once均为未签发草案，符合本批范围。此报告支持负责人采纳新批，不自动创建真实许可或执行。

## 剩余结论与停止

原214483B/7R7S/0reserved、旧107218B前缀/产物/fence/oldCloseACK=false只引用接受及旧M1时点，未在线读写。原E13AB部署失败报告/原raw保持，不能由此次修复回写PASS；新v17和六方法仍未实际安装/执行。

E11限定实机PASS、C13系统signal0严格FAIL/外部raw11/另方法OS11、C14 NOT_RUN、ordinary UNKNOWN及许可、renderer/audio、独立Kit/Flutter/全部P0仍保留；D1 NOT_PASSED/M0 NOT_STARTED。

报告主动发送负责人。当前停止设备/实现工作，等待新的准确正式设备批次，不自动续用旧批。发送后报告字节保持，通知回执另存。
