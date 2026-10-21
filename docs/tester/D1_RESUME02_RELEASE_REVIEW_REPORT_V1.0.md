# D1 RESUME02_RELEASE 独立机械整包复审报告 V1.0

日期：2026-10-20。结论：**PASS_PREPARED_RELEASE_REVIEW，阻塞缺陷0；执行授权待签，当前不可执行设备批次。**

支持负责人按已审 activation-delta 准备新的授权 overlay，保留本冻结 base/scope/release/config 原路径和字节。当前准备授权false、PREPARATION_ONLY/null和UNSIGNED permit不是缺陷，也不能因本报告PASS转成执行许可。未生成实际授权、PRODUCTION policy或动态完成证明。

## 范围与完整性

依据 `D1_RESUME02_RELEASE_TESTER_REQUIREMENTS_V1.0.md` 及负责人正式交测，独立审查准确绑定、24节点DAG、原产品字节、预算、五SDK/35部署依赖、外部完成/语义证明以及授权待定边界；另运行5个代表性拒绝路径。

- 交付文档 SHA-256 `1e193e217e6571aeee88e7fab49dfeaffb27794b7336dae8a7a9be1d278995a9`。
- 外seal SHA-256 `0b44299376d4e53f7499403e0122b1a6c21a5ecb14769989e8e810542f39cda9`。
- ZIP SHA-256 `a9b5a70b9c8ef9a2365bbbe7b26e6b2b273389cc51bc7e2dbd3340184ec34828`。
- 95项不可变文件和ZIP94成员的大小、摘要、名称集合及重复成员检查全部通过；拒绝验证后95项仍未改变。
- 74生产来源和183生产class/JAR摘要匹配已审来源；Java observer和capture入口仍分别为 `0667bc7f…485b8`、`fef62cb2…e25fe`，三个F APK及不同fixture签名字节复用。本轮没有构建、修改源或扩展框架。

证据目录：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME02_RELEASE_REVIEW_EVIDENCE`。没有SDK/5037/设备、现场registry/claim/ledger、旧PID/handle或原会话查询；未用现场目录存在检查来验证拒绝结果，依据实际入口拒绝码和其发生位置判定未进入现场控制路径。

## 准确身份与审查分栏：PASS

新scopeId：`20b08d64-6fd0-4a88-8b72-c80615e58258`。

| 材料 | SHA-256 |
| --- | --- |
| runtime-scope | 662f4239e235608e2bbc39e8ca28fd0284953ee47a18df83153128f7cbe8aec3 |
| activation-release | f40bc6a0095b1627a176f13f5edfc6cb297bc31dc32a78ff997bcc8dd6bf3295 |
| activation-trust-deploy | 35ee8559baed16d80a041c30f46ac5cf4abfc2806beb11090539835833bd229d |
| base-release-descriptor | 134e031ab7c24f401db9eb2733cce13d2775bff28cd4b8861ca0a54b43edd16c |
| 当前准备capture-policy | f3e03619f6a95ec9a9e531fde4c85978e1df0d2057b7c4dc004e64be0db7ef5a |

canonical scope/release/config分别为既有13/13/10字段，排序、编码、末尾换行及8192B界一致。scope/sourceApp/sourceTest/sourceAcceptance保持准确v17前置，目标app19/test/fixture3及signer pin匹配；fixture与app/test不同签名。唯一方法为ordinarySenderCannotBindCodec，budget字符串仍process43/text3145728/output0。

产品sourceReview为 `0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743`；captureReview为 `ad306682e27cdf1dec67955d9cb7f57bf99cd1451ab3b413963ee03439c6caf9`。两个真实报告的复制字节及引用分别核对，没有混用或覆盖。

原registry preparePlan/authorization/review/head保持原信任链；只读取coder封存的13项快照并核expectedActual声明与快照摘要，没有打开真实registry。base、policy、五请求、两observer和once/root路径在字符串层一致；未来真实准入不能用此静态快照替代。

行政disposition及四证据仍准确：A/K TERMINATED_WITHOUT_RETURN/false、B/H分别UNKNOWN、K预算UNKNOWN及fixture002外层UNKNOWN不被新包正常化，不补ACK、不退款。

## 24节点依赖图与overlay方案：PASS_PREPARATION

独立检查声明DAG的全部24节点和前置集合；另从这些JSON材料中的实际已知节点摘要构建120条引用边并拓扑排序，两者均无环。JAR及脚本作为已审固定字节源单独核定，不把DAG自述作为唯一依据。

顺序为两review/准备授权及固定产品材料 → scope/release/config/registry/预算 → base → policy → 五request → 两observer请求 → permit草案/activation-delta → manifest。base没有引用后生成policy/request摘要；当前未决执行授权明确为null。

对未来overlay另做19个符号节点的依赖检查，没有创建真实授权或生产policy。方案在保留以下条件时可行：

1. 负责人真实执行授权绑定本prepared seal、该delta、base/scope/release/config、两个review和预算，并明确实际执行范围；不能用当前准备记录的实际hash冒充执行权。
2. base/scope/release/config及原JAR继续引用本冻结目录原路径/摘要。base中的准备状态不改写，新的有效执行授权放在overlay层。
3. 新目录复制同字节capture入口和固定argv参考；相邻policy改PRODUCTION并绑定真实授权path/SHA、原base摘要、capture审查及全部真实execution pins。
4. 五request重算policySha256并改指overlay请求路径；SDK argv/caps、真实E9 scope和输出root不变。元数据captureCommand的-File/-RequestPath须一同更新。
5. 两Java observer的首个null pin换成实际执行授权path/SHA；capture入口、policy和全部五request的path/SHA也完整替换，生产Java argv仍指原prepared canonical材料和JAR。
6. 最后形成新的issued permit、manifest及overlay seal，独立最终机械报告在外；不得就地覆盖本候选，或把动态返回证明纳入静态预造材料。

prepared seal/delta在新授权之前已固定，policy及新请求在新授权之后生成，因此不要求反向修改base；原trust身份也不受新overlay替换影响。最终overlay的真实文件、授权语义及全量pin仍须另审，本报告未把符号无环检查说成已发布可执行overlay。

## 准备授权与真实拒绝门：PASS

准备记录 deviceExecutionAuthorized=false；base.deviceExecutionAuthority、candidate.executionAuthorization及policy.executionAuthorization为null；policy.mode=PREPARATION_ONLY。permit的kind明确UNSIGNED，state=NOT_ISSUED_NOT_EXECUTABLE。

本轮对包内实际已声明入口及准确请求运行5个独立代表性负例，原控制器均自然exit1、没有运行session或新增待收尾owner：

| 请求 | 实际拒绝码/原因 | 子进程/现场阶段 |
| --- | --- | --- |
| 首M1 metadata | PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION | 工具hash/SDK/现场root前拒绝 |
| 首M2 metadata | 同上 | 不跳过准备门进入部署/前项证明阶段 |
| deployment observer | Reviewed input pin changed | 首个执行授权expected SHA=null，Java/registry/claim前拒绝 |
| case observer | 同上 | 不把准备授权实际hash当执行授权 |
| UNSIGNED草案作为capture请求 | EXACT_SCHEMA_REQUIRED | 不是准确八字段请求，不能解释成采集许可 |

全部stdout文件0 B，原stderr共1544 B及各工具结果已保留。非0退出是预期拒绝通过，不是产品FAIL。验证只做准备态的拒绝，不生成或试运行授权态policy，不消耗旧许可、不触碰现场来“证明没改”。

## 五请求、35部署依赖及运行证明：PASS_CONTRACT

五条请求的八字段schema、scope/policySHA、65536/524288/65536/65536/524288 B及15秒资格准确，逐项等于冻结SDK argv。没有额外version、占用重试或新命令。35部署图的序号、APK参数及pm path的同包前一响应依赖保持准确，没有脚本化fake路径；唯一instrumentation的scopeSHA改为本批、方法不扩展，Android batch常量保持原APK值。

runtime contract的五个captureCommand路径、请求pin、前项固定completion-proof路径及阶段一致。首M2还绑定准确scope、原部署物理归还及本base摘要的部署完成证明。

外部完成证明必须由可信tester在同原控制器/工具自然结束、console/receipt对应资源实际返回后的另一次调用生成，再核完整metadata语义才批准后项。captureQualified、exit0、文件存在或无instrumentation都不自动等于身份/版本/data/全局无其他项目活任务成立。M1全门必须先于部署；M2全门必须先于唯一case。

本包的两个proof contract保留false/null，controllerPid及captureReceiptSHA未填，部署结果/归还false；封包中没有实际固定路径的completion-proof或deployment-completion-proof。该contract不是运行证明，也不能用离线拒绝结果补真实部署ACK。

本次没有重跑已在CAPTURE中独立验证且字节未变的读写故障、晚返/关闭gate套件；其外部真实形成证明、原owner保管、实际量/未知保留结论按准确入口摘要复用，不扩大为SDK或永久原生IO故障已验证。

## 预算与历史UNKNOWN：PASS_STATIC

43工作单元=3个M1+1部署入口+35部署子调用+2个M2+1case入口+1instrumentation。原始及重复输出1949696 B保持。控制786432 B内：589824原预留+135168五capture+2272旧已知+8192旧UNKNOWN=735456 B，余50976 B不授予新操作。另409600 B全局未分配不可用；总1949696+735456+50976+409600=3145728 B，归档4194304 B。

原旧控制台UNKNOWN/8192、A/K/B/H/K及fixture002未知不退款、不清账。真实读取超限和写入未知仍按实际或对应整栏保留，不以保存上限伪报实际读量。当前5个拒绝验证是独立离线准备证据，没有SDK原始输出或设备预算消费；没有把旧余额当本轮重试权。

## 缺陷、待定边界及交付

阻塞/非阻塞实现缺陷本轮均未发现；**授权待签是候选明确阶段，不计为实现缺陷，也不等于可继续执行。** 支持负责人在本prepared基础上按delta一次形成准确授权overlay，随后整包最终机械核验；无须重复产品或Android构建。

当前没有有效执行授权或issued permit，未创建PRODUCTION policy、动态证明、现场root/once/disposition/claim；没有现场、SDK、5037、设备、旧handle或媒体操作。未来派发仍须新鲜同源工具/default routing、真实registry/ledger/claim、准确v17/fixture1/签名来源/UID/data及全局无其他项目活任务，不能用本报告或历史读数代替。首失败/UNKNOWN/占用即停，不豁免claim、不降级重装、不追加其他五方法。

本地静态分析曾将canonical字段数量手写错误，随后按既有字段集合对同一原文件核定为13/13/10；已留在本地审查记录，不涉及改候选、重跑拒绝路径或候选失败。所有95项冻结文件最终仍匹配。

D1 NOT_PASSED、M0 NOT_STARTED及其他全部P0/许可余门保持；自有Flutter Theme、SkinKit延期和每批1–3里程碑集中协作的后续规划不改变本次范围。完整报告主动交负责人后停止，不自动激活或执行。

主要证据：`independent-binding-dag-audit.json`、`independent-guards-overlay-audit.json`、`exact-schema-phase-path-audit.json`、`proof-boundary-and-postcheck.json`、独立命令清单和5组原stdout/stderr/tool-result，均在上述tester目录。报告摘要发送前固定，通知回执另存，发送后正文不改。
