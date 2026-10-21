# ENV03 两项环境复查绑定交付

2026-10-20；候选 D1-20261020-ENV03。纯数据绑定与有限只读自核完成，提交tester独立核验后一次执行；coder未运行PRODUCTION入口或SDK/5037/设备、未读现场。无论占用是否解除，两项后均停止报告，不部署或恢复产品测试。D1未过/M0未启。

## 范围、授权与新隔离根

scopeId=`f0be73d2-01d2-4775-be6d-b6e55b8b77b3`。负责人实际环境复查授权原字节复制为 `release/environment-authorization.json`，2355B，SHA256 `dcc163aa7f4764a7cef146b33dadf1e5c86793be987efc95aefc1c315fcec44c`；仅2操作/1MiB文本/1MiB归档，15秒资格。该记录依据用户下一步要求和持续授权，不是新用户签名或密码学签章。

`release/environment-plan.json` 为环境观察计划，不是产品部署scope，SHA `ff23db7cdba88db95af9e9e39af8738fea4be9ec90b3cd9fb73402996051b27d`。采集器固定schema里的scope/releaseBindingDigest均绑定此环境计划摘要，不冒充E9产品release。policy为PRODUCTION、SHA `a32081b68c811497b122cac63d042816423c1776852bfda7ecfc301f3fb17ee8`，准确绑定新授权、原capture独立报告及环境计划，三类proof digest各唯一。

新root计划为 `D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_CAPTURE_EXECUTION/f0be73d2-01d2-4775-be6d-b6e55b8b77b3/outputs`，保留已审入口固定前缀，以新UUID隔离。coder未创建/查询该现场路径，没有部署once、claim、disposition初始化或新产品permit。

## 原入口不改，实际只准入两项

入口 `tools/capture_metadata.ps1` 逐字节复用 SHA `fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe`，固定SDK argv参考也复用原字节。没有源码/host/Android构建或通用keeper/协议框架。

| 槽 | policy ID | 实际请求/许可 |
|---|---|---|
| M1 identity | ENV03_M1_identity | 1项，65536B，15秒 |
| M1 global | ENV03_M1_global | 1项，524288B，15秒 |
| M1 ps | UNAUTHORIZED:ENV03_M1_ps | 仅未授权模板，无request/命令 |
| M2 identity | UNAUTHORIZED:ENV03_M2_identity | 仅未授权模板，无request/命令 |
| M2 global | UNAUTHORIZED:ENV03_M2_global | 仅未授权模板，无request/命令 |

入口要求5槽完整argv/cap/阶段与固定参考相符，所以保留后三模板；但入口还要求请求id**精确匹配槽**且符合 `^[A-Za-z0-9_]{1,80}$`。后三模板ID含冒号，任何匹配请求都被既有EXACT_REQUEST_SLOT拒绝；删冒号或使用其他合法id则无精确槽。五候选与该正则的交集严格只有前两项，不依靠“少发三份JSON”或口头承诺限权。最后三槽的cap不代表授权额度；请求文件和可运行命令均只有2个。

`evidence/admission-proof.json` 核实际原入口字节和这两个源代码谓词，记录10个有限数据检查：前两项仅在槽谓词上可准入，三个非法模板和五个其他合法名称均拒绝。**这是离线源谓词证明，不是PRODUCTION入口运行测试。** 没有为试探第三项而读现场root或启动SDK；入口其他字段、PRODUCTION五槽校验及真实pins另逐项核对。

## 命令、物理返回与语义边界

`release/two-request-dispatch.json` 列两条准确PowerShell入口/请求路径及唯一前项证明依赖。五槽SDK argv全部保留原样，不改-H/-P、参数、输出脚本或cap来迁就历史参考；实际授权/运行仅前两项。

独立PASS后tester按新授权先做fresh本地/tool/default routing、无未结当前claim门，只创建新scope采集root，再identity。原工具自然结束、stdout/stderr/文件/metadata/lock真实返回后，可信tester**另次调用**核完整身份语义并生成identity completion-proof，传真实SHA后才global。captureQualified不是语义批准；本包未预造该动态证明。

测试APK按冻结SHA `83109c13d76d635024add5575c1bf77606a05c3400b71ae3f6247acf18949f13` 和已审签名/UID/data判断，**不额外要求版本17**；旧报告观察版本0属于有效来源。主App17、fixture1及其他准确源hash/UID/data分别核，fixture新鲜数据身份只记录，不要求本批不存在的M2。任何身份/完整性失败先停，不追加请求修复。

global需完整activity processes原文头/主体/尾部/EOF，分别记录其他项目前台/测试进程和instrumentation。无instrumentation不能判无占用。global之后不形成准入第三项的proof，不论空闲/占用均集中报告后停止；无M1 ps、部署、M2、case、force-stop/kill/server重启/清数据或自动重试。

## 独立预算与旧事实保留

| 新ENV03预留 | B |
|---|---:|
| 两项原始read资格 | 589824 |
| 两capture记录/console及副本/外部proof、一次halt | 55296 |
| 本地前置记录与console | 16384 |
| 最终报告/结果控制 | 32768 |
| 合计 | 694272 |
| 未指派，非额外调用许可 | 354304 |
| 文本总上限 / 归档上限 | 1048576 / 1048576 |

原始读取、保存、转发/副本、控制及未知分栏；保存界不是物理读硬界。超限仍按实际已读/未知留账，停止依赖，同原Process/pipe/reader持续保管，不kill或二次关闭换ACK。归档在合格路径按逻辑产物预算检查，未知/超额不伪报0。

新预算不继承旧余额，不冲销旧scope20b08d64…已进入2项/388818B或旧UNKNOWN/8192；旧全局409600也不成为ENV03额度。冻结permit旧静态NOT_CONSUMED不能重跑。旧A/K行政false、B/H/K及fixture002 UNKNOWN继续保持。本批只从已交付报告SHA `0ccfb39bd348e4f77635055c7b5f64e9bef14018ee1732ed2d4cfd3b84394782` 和原overlay33项取源，不查询旧原在途对象或当前占用。

## 交付与验证

ZIP `docs/coder/D1-20261020-ENV03-source.zip`，seal `docs/coder/d1env03/evidence/env03-freeze.json`；最后只读回执在ZIP外。默认verify/help/pack-help只读，仅显式pack生成新包。新授权/pins、环境计划/policy、2请求与命令、5槽可准入域、预算/语义门和旧33项字节均已自核；tester独立核验未在本包预造。

本地生成器初次用了保留字作数据键，发生在执行前，修正后生成本唯一指定scope；不涉及源修改、现场或请求重试。未生成全产品release/新许可层，不改既有候选/账本/once。正式Flutter自有Theme/SkinKit延期、独立Kit/Browser、全部P0/开源许可和后续整批协作规则保持。
