# RESUME02_RELEASE 整包准备交付

2026-10-20；候选 D1-20261020-RESUME02-RELEASE。结论：准确发布基础材料已准备，执行授权待签，交独立机械复审；当前不能执行设备操作。D1未过/M0未启。

负责人已接受 CAPTURE 独立报告 SHA `ad306682e27cdf1dec67955d9cb7f57bf99cd1451ab3b413963ee03439c6caf9`，R01仅离线准备范围关闭。产品sourceReview仍为 `0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743`，二者分别绑定。原registry的历史preparePlan/authorization/review/head不被新审查覆盖。本批准备授权明确 deviceExecutionAuthorized=false，未伪签负责人执行授权。

## READY 与待定

新scopeId：`20b08d64-6fd0-4a88-8b72-c80615e58258`。

| 项目 | 当前结果 / SHA256 |
|---|---|
| 实际canonical E9 scope | READY：662f4239e235608e2bbc39e8ca28fd0284953ee47a18df83153128f7cbe8aec3 |
| 实际canonical release | READY：f40bc6a0095b1627a176f13f5edfc6cb297bc31dc32a78ff997bcc8dd6bf3295 |
| 实际canonical config | READY：35ee8559baed16d80a041c30f46ac5cf4abfc2806beb11090539835833bd229d |
| 无环基础描述 | READY：134e031ab7c24f401db9eb2733cce13d2775bff28cd4b8861ca0a54b43edd16c |
| 当前capture policy | 已准确绑定、保持PREPARATION_ONLY：f3e03619f6a95ec9a9e531fde4c85978e1df0d2057b7c4dc004e64be0db7ef5a |
| 执行授权 | WAIT：null；准备授权不能代替 |
| 两Java observer请求 | 准确argv/pins已列，首个必须执行授权pin的expected SHA为null，当前必拒绝 |
| execution-permit.pending.json | 明确UNSIGNED / NOT_ISSUED_NOT_EXECUTABLE草案，无实际许可 |
| 独立机械结果 / fresh现场门 | WAIT；未预造证明或沿用历史读数 |

全部材料位于 `docs/coder/d1resume02-release/release/`；pending文件名和状态明确，不能把READY的静态字节解释为有设备授权。

## 无环绑定与许可最终差异

`evidence/dependency-dag.json`列24个准备节点，按顺序独立检查无环：审查与准备授权→预算/产品来源→scope/release/config/原registry方案→base→policy→五请求→两observer请求→permit草案/激活差异→候选manifest。基础描述不引用后生成policy或request摘要。未解决执行授权是显式待定边，不伪装为已满足。

`release/activation-delta.json`给出可直接审查的后续差异：负责人在独立机械审查及准确派发后签发真实执行授权，绑定本prepared seal、该delta、base/scope/release/config、产品/capture审查及预算；在**新的激活目录**复制原字节采集入口和固定argv模板，把policy.mode改PRODUCTION、executionAuthorization填实际授权SHA并加真实pin，再重算五request的policySHA。两observer请求的第一个null pin换成真实执行授权路径/SHA，并更新实际overlay入口/policy/请求路径和SHA；最后生成新issued permit/manifest及外部机械结果。

实际canonical scope/release/config、JAR和base继续从本冻结目录引用，路径和摘要不变；因此新授权引用base不会因改动policy产生反向哈希环。overlay的metadata命令改指其相邻policy所在的采集器副本和新request；Java observer可复用本目录原脚本并传overlay请求。不就地改本候选或旧候选，不自签授权，也不将本草案说成“一次许可已发”。

## 复用字节与目录

74生产来源、183class/JAR与已审来源逐项相同；零host、Android、Gradle/native构建，不重复长套件。

- JAR：03a27c74061b740a879e2dfec3341b0b07172c68bf374b9231c20e42a46566c5。
- Java observer：0667bc7fe93cf2010cd337eeafaeabd94b7a795efa74059365af3fb83c8485b8。
- capture入口：fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe。
- F app19/test/fixture3及签名字节保持；行政disposition保持610B、SHA7270e5c0208d2895394bbd1cd25508b239bbe7a711a40b3e8d2b3d59a37a265d及四个证据pin。

采集器固定根前缀仍为已审 `D1_RESUME01_CAPTURE_EXECUTION`，使用新UUID隔离，不为改名重写代码。计划root为 `D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_CAPTURE_EXECUTION/20b08d64-6fd0-4a88-8b72-c80615e58258/outputs`，部署once为同批父目录的 `e13f-lifecycle-deployment.once`；case沿用固定root的同scope+method不可重入claim。本批没有预创建这些目录/文件或安装disposition，不查询其当前存在状态。

registry方案只从旧受审coder快照重绑13项预期字节与路径；实际root仍原真实registry，当前未读现场，未来不得用快照复制品替代实际inventory/quiet门。旧R01/CAPTURE两组冻结成员在准备和最终校验中核未改，滚动协调记录只更新顶部并封存副本。

## 准确运行依赖与账目

五SDK argv逐项保留，caps=65536/524288/65536/65536/524288，资格15秒；35部署子调用图不增加操作，`pm path`后的APK参数继续由同包前一响应严格解析，原archive记录实际展开argv。唯一instrumentation的scope已换成本新scope SHA，方法仅ordinarySenderCannotBindCodec；Android batch常量仍按原APK固定值，不伪改。

`runtime-dependency-contract.json`列准确当前命令及动态证明依赖。后继completion-proof只能由可信tester在**同原工具实际自然结束且原资源返回后**的另一次调用生成，再核metadata身份/版本/data/完整性/占用语义才填approvedForNext。captureQualified不自动等于语义允许。M2额外绑定真实部署通过、原对象物理归还及本base摘要的证明。证明contract保留false/null，不预造实际证明。

预算保持本批接受的43工作单元/3145728B文本/4194304B归档：

| 内容 | 数量 / B |
|---|---:|
| M1三采集、部署入口+35子、M2两采集、单case+instrumentation | 43 |
| raw及重复输出 | 1949696 |
| 其他原控制预留 | 589824 |
| 五capture保守控制 | 135168 |
| 旧已知前置 | 2272 |
| 旧控制台UNKNOWN槽保留 | 8192 |
| 控制承诺 / 控制上限 | 735456 / 786432 |
| 控制余量，非新操作许可 | 50976 |
| 全局未分配，不可用 | 409600 |

总额1949696+735456+50976+409600=3145728。超额按实际已读/重复量计，未知保留对应整栏，保存maxTextBytes不是物理硬读界；原owner未证继续保管，不kill/二次close/重启server。旧UNKNOWN及8192不退款，新准备/测试证据另列，不把旧余额当新重试权。

## 有限离线核验

7次实际调用原受审入口均在child/root/custody创建前拒绝并自然结束：五metadata为PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION；部署和case原observer因首个执行授权expected digest=null报Reviewed input pin changed。该null是显式待定，不填假的64位摘要；它指向本地准备记录但绝不把其实际hash充作执行权。入口代码位置与准确原字节一起核定，测试没有SDK/Java child或现场root检查。

canonical编码/字段/摘要、全部已知pins、两个sourceReview分栏、原registry trust、24节点DAG、scope/root/once一致性、35动态依赖、五请求schema/caps/阶段、预算和183成员等价均通过有限自校验。测试只验证本准备态正确拒绝，**不把它说成实际授权态SDK、部署或T07通过**；真实执行需后续准确新派发。

生成器最初一个本地语法括号错误发生在执行前，修正后只生成一个scope；该留痕不涉及编译、许可或现场重试。

## 冻结与下一门

ZIP `docs/coder/D1-20261020-RESUME02-RELEASE-source.zip`；seal `d1resume02-release/evidence/resume02-freeze.json`；最终只读回执在ZIP外避免自引用。默认verify/help/pack-help只读，显式pack仅生成一次新准备包。当前独立机械报告未存在，不能在包内伪造。

独立机械PASS和负责人准确后续派发前，不创建新root/once/disposition/claim，不SDK/5037/设备。派发后也需全新同源工具/default routing、原registry/ledger/claim、准确v17/fixture1/签名来源/UID/data及全局无其他项目占用；历史值不当新鲜事实。未结claim无豁免，不同前置即停，不降级重装，不追加其他五方法。

A/K行政false、B/H及K UNKNOWN、fixture002外层返回UNKNOWN继续保持，不回补ACK。正式Flutter自有Theme/SkinKit待Flutter支持、独立Kit/Browser、每批1–3完整里程碑集中开发测试、原开源框架/许可及全P0不变；不提前M0。
