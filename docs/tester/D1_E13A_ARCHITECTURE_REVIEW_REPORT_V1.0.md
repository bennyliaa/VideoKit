# D1 E13A 完整冻结包独立复审报告 V1.0

日期：2026-10-18。依据：`docs/milestones/D1_E13A_TESTER_REQUIREMENTS_V1.0.md`。候选D1-20261018-E13A，v17 / ACTIVATION / ABI1。

## 结论

**原E13-F01/P1绑定归还遗漏已在静态实现及直接生产owner的平台替身证据范围关闭；原E13-F02/P2已通过独立只读执行与前后字节快照关闭。冻结完整性通过。当前设备准入仍BLOCKED：新增E13A-F01/P1，三份metadata脚本采用的instrumentation查询入口不符合AOSP API31命令契约。**

该问题限于设备计划/证据入口，不撤销绑定修复，也不是新的产品功能FAIL或设备复现。请集中修正三份metadata脚本、完整argv、记录期待及相关pins/封印后复核；不需要为此重建APK/JAR/native、重跑绑定九组、source旧套件或升级产品版本。当前不执行M1、部署或六方法。

本批无ADB/设备、无媒体payload、无构建、无候选测试重跑、无remote脚本执行。独立执行的候选工具仅为已读源码确认纯读的默认verify、显式verify、help、pack-help；没有执行pack或写封装器。其余执行为tester自编字节审计和SDK签名/Manifest读取。产品和冻结交付未改。

D1 NOT_PASSED，M0 NOT_STARTED；六方法Android全部NOT_RUN。原214483B、7R/7S、reserved=0和旧107218B前缀/产物/fence/oldCloseACK=false只引用E11接受报告时点，本批没有在线重新确认或变更账档。

## 完整性与唯一制品

独立产物：`docs/tester/D1_E13A_REVIEW_EVIDENCE/`，包括`audit_e13a.py`、`independent-audit.json`、四份只读入口输出、三APK签名/Manifest、`metadata-command-review.json`。**2251项文件、成员、pins、预算和原记录一致性检查全部通过**，不是2251个功能测试。

| 项目 | 独立结果 |
|---|---|
| 外seal | `24d9fd0b3fa00afe0d37768cfd7eafd7bf1349810f641c7c03814937ace8acb6` 一致 |
| ZIP | `45765142b21ca193d1b5ca26feb2e1023e5151e95303fd9ba5b167c1cc37e48e`；269个唯一成员、270条封印记录一致 |
| 旧封印 | E11基础375/R1 65、E12 46、E13 367条及四seal字节全部保持 |
| 最终构建输入 | 139项一致；快照SHA `2c71c4e24e28abff2c6cd03ad30e8a638e7a39b95c8b3eb91348c213df4b939c` |
| JAR | 172个production class实际集合/字节/源码pins一致，不含绑定检查、source检查或部署自检类 |
| 主依赖/native | 35项锁与E13一致；app内7个native库与继承源pins一致 |
| fixture | 空Maven runtime锁、不同签名；独立解析实际300个DEX定义，含共同BindingOwner与平台工具生成类，无Kotlin定义。空runtime不等于APK只有手写代码 |
| 只读入口 | 默认、verify独立seal pin、help、pack-help均exit0；272份候选/交付文件前后字节相同 |

最终仅使用`docs/coder/d1e13a/artifacts/D1-20261018-E13A/delivery/`：

| 文件 | 字节 | SHA256 |
|---|---:|---|
| app-debug.apk | 10692238 | `962d903ff4dbe2ccf767a6adb9bd7845c4cbfd025ebee249caad4d0517483aad` |
| app-debug-androidTest.apk | 2770225 | `83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13` |
| fixture-debug.apk | 65609 | `868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8` |
| e13a-host-tools.jar | 298510 | `a0ff822bb9097106322bfccfc6a9c95d2bc1c701928da1be3feef5f01122614f` |

SDK apksigner独立验证三APK成功：主app/test signer `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，fixture signer `45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9`。独立Manifest确认app为v17/ACTIVATION、包名对应；签名及静态对齐不代表普通UID真机或16KiB设备通过。

## 原P1修复裁定

定位：`binding/com/videokit/spike/e4/E13BindingOwner.java`，实际`SenderService.TargetBinding`及`E13PermissionProbe`共用这份owner，app/fixture sourceSets及两APK实际DEX均有对应接线。

- bind前入静态强keeper；绑定是否进入、实际返回、accepted、异常分开。false、SecurityException、其他已返回异常均走同一原connection的一次必要unbind，不再由accepted决定是否解绑。
- close先到而bind仍在途时保留；解绑进入前置位，重入close不重复解绑。异常虽已返回仍无成功ACK，returned=false、keeper不清；没有第二次unbind填成功。
- 回调进入/返回/在途计数与解绑分开；已开始work未返仍保留。关闭后迟到callback不接endpoint。仅closeRequested、bind实际返回、原unbind成功返回及回调全部返回才returned。
- host仍单独保留远端fixture Binder及未知状态，不能用本地client解绑替代远端target归还；真实runner finish/onException经permission门和共同keeper拒绝未知结束，PC OriginalAuthority接线继承。

原SDK36.1 Context/ContextImpl/LoadedApk契约文件pins已核。九组72断言原日志/输入/退出记录已读取：FALSE、SECURITY、OTHER_EXCEPTION、TRUE_CALLBACK、BIND_IN_FLIGHT、UNBIND_IN_FLIGHT、CALLBACK_IN_FLIGHT、LATE_CALLBACK、UNBIND_EXCEPTION。最后一组明确resourcesReturned=false、原keeper保留，JVM结束不冒充Android归还；本审查没有重跑九组。

裁定：**CLOSED_STATIC_AND_PLATFORM_SUBSTITUTE_EVIDENCE**。Android API31实际dispatcher/kernel负例与归还仍NOT_RUN，不据平台替身关闭真实设备或永久UNKNOWN门。不同签名普通UID/clearCallingIdentity后的kernel拒绝与授权host HELLO仍分栏，未取得endpoint不声称内部onTransact。

## 原P2修复裁定

`tools/package_delivery.py`默认选择verify；参数帮助先返回，仅显式pack才加载`_write_package.py`，后者首段再要求明确pack。verify逐文件/hash/ZIP/JAR/旧seal读取，不复制、写证据或运行构建/设备。

独立以`-B`执行四种只读模式，并在前后对272份文件做快照，字节全部一致。交付原197份预冻结、264份最终快照及负责人真实显式verify回执属于各自范围，不将不同快照计数混为同一集合。原E13 seal/367条也由tester重新逐字节读核，未运行原误用入口，原既存JAR x异常仍是工具误调用而非产品FAIL。

裁定：**CLOSED_LOCAL_READONLY**。写打包必须显式pack，冻结后不重pack；本次没有需要授权的写操作。

## 继承、部署与预算

七份核心source生命周期文件字节继承：SourceGroup、AsyncReadBridge、LeaseRegistry、SourceAdmission、CpuTaskClient、E4Session和SourceCases。生产正对照/双consumer/迟到open-read/原ticket规则、排空后executor terminated才清source keeper及原runner/PC门继续按E13已审范围接受；继承不算E13A新功能或实机PASS。不要求重复原source/native/历史signal套件。

升级来源仍为E11真实接受v15精确pair，非未安装v16。源码目标检查、host target与Android @Before均为17；batch为`D1-E13A-SOURCE-20261018`，新固定once名`e13a-activation-deployment.once`，原registry外CREATE_NEW。主app/test各install-r一次，fixture确认不存在后首次安装一次；部分失败/未知停止，不重试/降级/clear或换once。当前真实scope/release/config/once均未签发。

一次离线main-001构建日志/输入一致，约1m7s、101任务成功，0修正构建；未下载或重建native。fixture签名私钥仍本地外置未归档，签名环境不等于发行权利；35Maven/7native/工具生成类的来源证据不关闭许可、模型/权重/样本等门。

六方法未来精确顺序与源预算如下；当前均NOT_RUN，**不得越过metadata阻断直接执行其中任一项**。

| 方法 | open | 原read | close |
|---|---:|---:|---:|
| ordinarySenderCannotBindCodec | 0 | 0 | 0，另核三份真实binding归还 |
| authorizedHostSourceReadAndClose | 1 | 4096B | 1 |
| oldGenerationNeverOpensSource | 1 | 32B | 1 |
| twoConsumersHoldSourceUntilLastReturn | 2 | 48B | 2 |
| cancelLateOpenRetainsOriginalOwner | 1 | 0 | 1 |
| lateReadAndCloseFailureDoNotReleaseEarly | 1 | 48B | 2 |

同一4096B非媒体定义，五host共20KiB准备、实际read4224B/open6/close7；仍受read64KiB/open8/close16及每ticket initial+最多2次明确失败后重试的更紧门。原await5000ms，方法30秒只资格，无强制终止保证。每个方法独立host、当前观察及真实原返回，任一FAIL/BLOCKED/PENDING/UNKNOWN停止后继，未知保原owner/Java/ADB/custodian，不新增查询、重发、强杀或第二次解绑。

PC算术与上限保持：部署entry1+内部32+六entry6+六instrument6+metadata3=48；文本已分配1638400B、余458752B，总2MiB。不得将metadata改成新Java wrapper而漏记进程，也不按阶段清零或免算重复top/child raw。长期设备授权有效，后续准确派单无需再向用户索权；其他项目占用/不明时等待。

## M1–M3核验及新增阻断项

固定34stat/18control与tester字段计划一致；完整ledger2271B/SHA `e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649`，四个新增旧产物stat准确取acceptedStat，未造inode。固定inventory保留已归档`operation.pending.N2-e5-aborted`，不把它当新在途pending或删除。非零媒体仅stat，18小型控制字节完整base64后按pins核。

三份JSON都含一个完整直接ADB argv；最后参数经shlex解引号后与对应.sh完全一致，没有PC wrapper、push或新增客户端。记录数/唯一标签/cap和总上界独立重算一致；29份既有`bash -n`记录仅证明语法。其早期MSYS同步/Windows引用错误不是Android结果。

| 客户端 | 记录/上界 | script SHA256 | argv JSON SHA256 |
|---|---|---|---|
| M1_PRE_DEPLOY | 70 / 53512B | `581c44aedd2fb6be8a71de7a2390e9c2a70703d110dcfc037c45e1c13813a89c` | `49b564546900e4bbd59bbf237052fc51d9c908927ee509c24fd1f44b76455572` |
| M2_POST_DEPLOY_PRE_CASE | 18 / 27588B | `dcfc31af8eebdf647e5adc4719c44d66abf7ed52c8def5b94759fe372cf24426` | `9fcbb8c3b4a95b3e1036f64b2f29563359cfcb868f264ec7617343604ec9cfa1` |
| M3_AFTER_SIX | 71 / 56360B | `93a948bd3e110437417e85575fb63d704854cb69fb31b36ab1d2044ffbb24080` | `b0c0824ce5952e961bf92f02d5a56a29e17380f01df9d6f83df7ec493b3606db` |

以上只是已审当前字节身份，不是设备准入pins；修正以下入口后必须更新对应pins/封印。

### E13A-F01 / P1：三份INSTRUMENTATION记录使用不支持的查询入口

定位：三份`.sh:19`及各`.argv.json`嵌入脚本，统一为`emit INSTRUMENTATION 4096 dumpsys activity instrumentation`。

AOSP API31标签的dump分派未提供该子命令；不匹配时走activity/shell回退，可输出诊断而非活动测试列表。[ActivityManagerService原文](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java)（8265–8464）。shell回退也没有此项；`instrument`是不同的执行入口，不能替代只读查询。[ActivityManagerShellCommand原文](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/services/core/java/com/android/server/am/ActivityManagerShellCommand.java)（171–319）。

因此，当前脚本不能据此取得“无活动instrumentation”的必要独立证据。emit只检查退出码和字节数；系统诊断即使小于4096B且外层返回0，也不能被当空闲。现有语法/标记/大小检查不覆盖命令语义。这个结论来自上游API31契约审查；未声称已连接厂商平板复现，厂商扩展也没有已接受证据。

修正要求：在同一个直接客户端内，改用API31受支持、可核完整性的活动instrumentation读取路线；可沿E11已有`dumpsys activity processes`来源作有限抽取，但须保存完整目标段和明确解析/缺段/错误判定，不以简单grep无命中或空字符串证明无任务。不要将查询改为启动测试。保持三客户端、每份64KiB/55秒、48操作及2MiB预算；脚本/argv/期待记录/pins集中更新。若无法保留全部必要字段则先报预算缺口，不加查询或在执行中改脚本。

**无需因本项重建或重测未变产品。** 完成元数据交付修正及只读复核后，原绑定修复和其余支持结论保留，负责人再派准确设备批次。M1以前还需既有controller独占/他项目占用证据；M2/M3继续与真实binding/source finish和原PC/pipe返回交叉审证，不能由PID消失或脚本exit0替代。

## 剩余门与交接

renderer/audio/source及Kit保持E13已审SUPPORTED_DESIGN_ONLY：显示/声音NOT_RUN，合法压缩音频→PCM BLOCKED；原owner/Surface代次/PCM焦点/全consumer退租、D1封装边界与M0/M7契约和AAR工作不减项。没有扩decoder/FFmpeg音频/模型/安全或诊断框架。

E11限定四方法PASS及E6B跨host有限关闭保持；C13 self系统signal0严格FAIL、外部raw11/另方法OS11、C14 NOT_RUN、ordinary UNKNOWN及全部P0/许可/长期门不回填。原E13误调用不作为产品FAIL，本次也没有设备pending或新输出/READY/R/S产生。

报告及集中问题交负责人后停止。等待元数据修正冻结复核，不自动进入设备、后续测试或M0。通知回执另存证据目录，发送后报告字节保持。
