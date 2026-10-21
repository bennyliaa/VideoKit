# RESUME02_ACTIVATION 最终overlay交付

2026-10-20；候选 D1-20261020-RESUME02-ACTIVATION。最终机械绑定完成，实际条件执行授权已绑定、permit已发且未消费；等待tester最终独立机械PASS和新鲜现场门后按同批范围执行。coder本轮没有执行SDK/Java生产入口、设备或现场操作。D1未过/M0未启。

## 真实授权与不变基础

负责人实际派发记录源为 `docs/milestones/D1_RESUME02_ACTIVATION_EXECUTION_AUTHORIZATION_V1.0.json`，4886B，SHA256 `04294e2f4e9dc0313b69239c9fd39572c2a449281949970b6ad1247d344c7ee3`。本overlay在 `release/execution-authorization.json` 保存原字节；逐项核scope、预算、条件及13个来源pin。它是负责人依据用户持续授权作出的**条件范围派发**，不称为用户新签名或密码学签章，不再使用准备授权冒充执行权。

prepared独立报告 SHA `75380086d04cfcefa6b1ed6b67307386b3e56f0a19b16366e9be8b55aa47f582` 已核，与负责人授权相符。scopeId仍 `20b08d64-6fd0-4a88-8b72-c80615e58258`。

| 原prepared材料 | SHA256（原路径/字节不变） |
|---|---|
| 外seal / 95行 | 0b44299376d4e53f7499403e0122b1a6c21a5ecb14769989e8e810542f39cda9 |
| scope | 662f4239e235608e2bbc39e8ca28fd0284953ee47a18df83153128f7cbe8aec3 |
| release | f40bc6a0095b1627a176f13f5edfc6cb297bc31dc32a78ff997bcc8dd6bf3295 |
| config | 35ee8559baed16d80a041c30f46ac5cf4abfc2806beb11090539835833bd229d |
| base描述 | 134e031ab7c24f401db9eb2733cce13d2775bff28cd4b8861ca0a54b43edd16c |

原base内的准备态/null保留为历史基础；真实执行权在本overlay层，二者并不互相回写。产品sourceReview=0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743，captureReview=ad306682e27cdf1dec67955d9cb7f57bf99cd1451ab3b413963ee03439c6caf9分栏。原registry trust、13项准确原快照方案、行政610B及四证据原样；未读真实registry/ledger/claim或旧handle。

## overlay准确最终绑定

目录 `docs/coder/d1resume02-activation/` 仅新增机械材料：

- `release/capture-policy.json` 为 **PRODUCTION**，7614B，SHA `6d982a8341168c8d4d839a653aefbefd9e8999a9079828299bd0b4266a52f083`。相对prepared只改mode、executionAuthorization、executionPins；真实授权、capture报告、base各有且仅有一项准确digest匹配，其余实际来源pins均核字节。
- 五个metadata请求只改policySha256，保留原id/scope/root/argv/caps/15秒。文件及runtime命令的 `-File`、`-RequestPath`均指本overlay，确保读取其相邻PRODUCTION policy。
- 两个observer请求只改pins：首个null换成实际授权路径/SHA；entry/policy及全部五request的路径/摘要完整换成overlay，实际授权的其他来源pins列全。Java argv仍指原prepared scope/release/config/JAR，原observer脚本可直接接本overlay请求；没有遗留pending/null授权pin。
- `release/issued-permit.json` 为1700B canonical记录，SHA `610ea25d2d38fb8d4a065da9bdccf8560eea1072828d1383e51ecdefbe20bc3f`，kind=resume02ActivationPermit，state=ISSUED_CONDITIONAL_NOT_CONSUMED。它绑定真实授权、两类来源审查、prepared审查、scope/release/config/base/预算/入口/policy/request集合/runtime和唯一方法。不是原pending草案或旧许可重放。

`runtime-dependency-contract.json` 及两个request-set列完整路径。当前authorityGranted=true、conditionalExecutionOnly=true，但最终独立报告和fresh门仍null；currentDeviceExecutionAllowed=false表示尚不能跳过这些运行前条件，并非缺少一般真机授权。

声明DAG有28个最终节点，顺序为不可变prepared来源/报告→实际授权与原入口→PRODUCTION policy→五request→两observer请求→runtime/request-set→issued permit→manifest。prepared先于授权，base不引用本overlay，最终独立报告位于seal外，未产生哈希环。

## 生产字节与有限离线检查

74生产来源/183class及原JAR不改，零host/Android/Gradle/native构建。JAR仍03a27c74061b740a879e2dfec3341b0b07172c68bf374b9231c20e42a46566c5，原Java observer仍0667bc7fe93cf2010cd337eeafaeabd94b7a795efa74059365af3fb83c8485b8；新目录capture入口逐字节等于已审fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe。三个F APK及signer完全复用。prepared95行逐项核未变。

有限核验实际授权语义/全部pins、PRODUCTION精确差异、五请求/两observer/schema、原路径/新runtime入口、外部证明依赖、canonical permit、预算及原class字节。另对校验器在内存做8个漂移负例：缺授权、错base、旧模式、重复授权proof、旧policy、错scope、抬cap、错root，均被拒绝。它们是**离线校验器负例**，没有运行任何PRODUCTION采集/Java入口，也没有借验证授权态查询现场或启动SDK；不把结构PASS说成设备通过。

首次自校验报告包装器在输出摘要时使用相对路径导致序列化失败，修正为绝对路径后保存完整结果；不涉及产品、授权、现场或执行重试。没有新增诊断/keeper框架、后台任务或动态证明。

## 准确范围、账目和运行门

实际派发范围保持43工作单元：M1三请求、部署入口及35子调用、M2两请求、唯一case及instrumentation。五SDK argv/caps=65536/524288/65536/65536/524288和15秒资格不变；35个部署响应依赖不加调用，原archive记录同包pm path解析后的真实argv。方法仅ordinarySenderCannotBindCodec，其余五方法不进入。

预算3145728B文本/4194304B归档：1949696 raw及重复 +735456控制承诺 +50976控制余量 +409600全局未分配。控制735456含589824原预留、135168五capture、2272旧已知和8192旧UNKNOWN；409600不可花，50976不是新操作授权。实际超额、未证read/部分write和控制量继续按真实量或UNKNOWN留账，不以保存界充当物理硬界，不退款。新绑定/静态准备证据另列，旧账本/once/UNKNOWN不动。

执行依授权严格依次：

1. tester最终独立机械PASS，之后新鲜同源工具/default routing、真实registry/ledger/claim门。未结claim不豁免，不凭历史值推现场；不能满足原owner保管及计费则child前BLOCKED集中报告。
2. 只创建准确批准的capture root：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_CAPTURE_EXECUTION/20b08d64-6fd0-4a88-8b72-c80615e58258/outputs`。coder未创建/查询该路径，也未写once/disposition/claim。
3. M1三项逐请求真实结束及语义审核；准确v17/fixture1、hash/签名来源/UID/data、全局无其他项目活任务或instrumentation才部署35子调用。captureQualified/exit0/无instrumentation不自动等于approvedForNext。
4. 只有原部署真实成功且物理归还后，trusted tester另次调用写scope/base匹配的deployment proof，M2两项通过再唯一case。completion-proof同样只能在同原工具自然结束/流归还后的另次调用形成，物理归还与语义批准分开；本包没有预造true或动态证明文件。
5. 首失败/UNKNOWN/占用停止全部后继，原调用未返同上下文保管；无自动重试、kill/强停/server重启/清数据/降级或其他方法。完整结果集中报告，不自动M0。

部署once仍同批父目录的e13f-lifecycle-deployment.once；case仍固定root同scope+method不可重入claim。它们未创建或消费。原A/K行政false、B/H及K UNKNOWN、fixture002外层UNKNOWN均保留，不补ACK，不以新条件许可清旧账。

## 冻结与交接

ZIP `docs/coder/D1-20261020-RESUME02-ACTIVATION-source.zip`，seal `d1resume02-activation/evidence/activation-freeze.json`。overlay引用既有prepared原绝对路径与摘要，需和已冻prepared包共同使用；不是迁移/重建base的独立产品包。默认verify/help/pack-help只读，显式pack一次生成；最终只读回执及tester独立报告在ZIP外，避免自引用。

真实条件授权和issued permit随完整报告交负责人保管并安排tester最终机械核验。coder不执行现场。正式Flutter自有Theme、SkinKit待Flutter支持、独立媒体Kit/Browser、后续1–3里程碑整批规则、既定开源框架/许可与全P0保持。
