# D1 RESUME02_ACTIVATION 集中复审与真实执行报告 V1.0

日期：2026-10-20。设备：HA1Q6WXR / TB138FC / API31 / user0。

结论：最终独立机械核验 PASS；M1 身份门 PASS；M1 全局占用门 **ENV_WAIT_OTHER_PROJECT_OCCUPIED**。本 scope 已停止，无自动重试和后续测试。部署、M2、ordinarySenderCannotBindCodec 均 NOT_RUN，不能据此判定 D1 通过，M0 未启动。

## 授权与冻结绑定

scopeId：`20b08d64-6fd0-4a88-8b72-c80615e58258`，scope SHA256 `662f4239e235608e2bbc39e8ca28fd0284953ee47a18df83153128f7cbe8aec3`。

负责人条件执行授权 SHA256 `04294e2f4e9dc0313b69239c9fd39572c2a449281949970b6ad1247d344c7ee3`；issued permit SHA256 `610ea25d2d38fb8d4a065da9bdccf8560eea1072828d1383e51ecdefbe20bc3f`。均为现有冻结文件，未改写状态。许可文件的静态 NOT_CONSUMED 字样不能用于重跑：实际账本已记入两次 SDK 读取。

机械核验检查 overlay33项、ZIP32成员、原 prepared95项、74生产来源/183class、真实授权与全部路径/摘要绑定、28节点前向依赖及实际 observer entered 序列化大小，全部通过。外 seal SHA256 `f5ae97ca7714472601a338786b833e497820f3776569e2a9125814f8a7cd920a`；ZIP SHA256 `28d26357a14a5c163f72e7061bb5349e4403d4788ad2dcef4cbc659482389eb4`。详细机械报告：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME02_ACTIVATION_MECHANICAL_REVIEW_REPORT_V1.0.md`，SHA256 `8c476f758754d4a41a6a78e13af438dfb97714f80c2e104891b93d9676303954`。

## 新鲜前置与真实结果

本轮本地检查确认：默认本地5037路由，无环境重定向；现有监听器对应原批准 adb.exe，准确工具摘要匹配，文件早于本次 server 创建；未启动或重启 server。原 registry13项及旧账本准确匹配，guard root 不存在、无 claim；随后仅初始化已批准 capture 输出目录。未把历史 PID 或旧现场读数当作本次事实。

| 步骤 | 真实结果 | 依据 |
|---|---|---|
| M1 identity | PASS | 完整12段原始输出及结束标记；原工具 exit0，全部原资源归还 |
| M1 global | 采集 PASS，语义占用阻断 | 完整 activity-process 原文、尾部及 EOF；LendManager 前台活动可见 |
| M1 ps | NOT_RUN | 首次占用后停止 |
| disposition 安装、部署 Java及35个SDK子操作 | NOT_RUN | 未满足无占用门 |
| M2 identity / global | NOT_RUN | 部署未进入 |
| ordinarySenderCannotBindCodec及其余用例 | NOT_RUN | 后继全部停止 |

M1 主 App版本17、fixture版本1，测试APK观察版本0；三者准确已安装APK摘要分别匹配冻结白名单 `962d903f…7483aad`、`83109c13…49f13`、`868f5815…544d8`。UID为10221/10222/10228；数据目录身份分别为10221:6972、10222:4741、10228:21515。签名依据为准确APK字节与已审签名白名单绑定，无新增签名查询。

tester 初版离线分析曾额外要求测试APK版本17，误判身份门。冻结要求只规定主 App17、fixture1及测试APK准确摘要；测试APK版本0与批准来源一致。原采集一直成功且资源归还。已保留初版分析，追加 v1.1、更正记录和真实归还后的外部证明；纠正仅复核同一份原文，增加0次SDK、0工作单元，未重采或覆写失败记录。M1 identity completion proof SHA256 `317e7d8fc6f6f3e6aeb3289cd527446e2d47138f8151b5562014d86a302bb16b`。

## 占用阻断证据

M1 global 原始输出364911 B，SHA256见 `M1-global-semantic-audit.json`。全文头、All known processes、OOM levels、最终 mForceBackgroundCheck=false及 EOF 均完整。无 instrumentation 不能代替无其他项目占用。

- 原文2393行起：`com.lendmanager.app`，UID10223、PID31712，`curProcState=2`、`cached=false`、`foregroundActivities=true`，Task256 `visible=true`；3767及4298行明确为 top-activity。
- 原文1369行起：`com.lendmanager.flexibletest.test`，UID10238、PID31396，进程仍存活，当前 cached 状态。

上述为本轮采集事实；不同于旧快照的 PID。前台 LendManager 已足以阻断。本轮没有终止其他项目、追加查询、重启server、force-stop、清数据、升级或降级，也没有生成 global 的 approvedForNext 证明。控制器35744、子进程35164为本次原采集记录，不对其追加 PID 查询。

## 按实际产物结算

| 项目 | 本轮实际 |
|---|---:|
| 已进入工作单元 / 上限 | 2 / 43 |
| M1 identity SDK 原始读取 / 保存 | 23907 / 23907 B |
| M1 global SDK 原始读取 / 保存 | 364911 / 364911 B |
| SDK 原始读取合计 / 原始文件保存合计 | 388818 / 388818 B |
| entered及receipt成功记录写入 | 5035 B |
| 原控制台输出 / 留存控制台副本 | 3055 / 3055 B |
| 外部identity completion proof | 455 B |

两次工具均真实 exit0、无遗留session；stdout/stderr读任务、EOF、pipe/file close、wait、process dispose、元数据关闭全部返回，捕获器 firstFailure=null。原始读取量与保存量分列，不把文件长度替代未知读取量。本轮两次SDK原始读取无 UNKNOWN。console转发/留存及外部证明另计，未将重复副本视为免费。

控制总类786432 B保守保留，涵盖本轮记录及本地分析/结算/报告开销；不宣称上述表格为全部控制开销的精确总和。旧已知2272 B及旧UNKNOWN8192 B继续保留，历史fixture002 UNKNOWN不结清、不退款。全局409600 B不可用额度消耗0。其余41工作单元未进入，不因此授权复跑或新增操作；未从控制余量增加SDK操作。

初始 `actual-execution-ledger.json` 是进入前0单元快照，保持原样；实际终态以 `actual-execution-ledger-final-v1.0.json` 和两次step记录、身份更正记录为准。本轮无待归还的原采集资源，capture输出目录和证据保留归档；历史 pending/UNKNOWN 保持原既定处置，不以本轮外部工具返回替代旧内部ACK。

## 交付与后续边界

证据目录：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME02_ACTIVATION_REVIEW_EVIDENCE`。原始产物：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_CAPTURE_EXECUTION/20b08d64-6fd0-4a88-8b72-c80615e58258/outputs`。关键结算文件为 `actual-execution-ledger-final-v1.0.json`、`scope-stop-record.json`、`M1-global-semantic-audit.json`；包含准确摘要和原文行号，无删改原文。

请负责人按本轮 ENV_WAIT 接收并协调平板跨项目占用，后续如再派发应使用明确新范围和现场门，不能将本轮部分执行当作未消费许可直接重跑。tester 不自动进入后续测试；D1仍未通过，M0未启动。既往原N2的ABORT及fence/账本/pending归档沿用已交付结论，本轮不重复执行ABORT。
