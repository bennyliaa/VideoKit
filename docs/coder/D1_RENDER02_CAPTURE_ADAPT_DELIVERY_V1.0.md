# RENDER02 有限采集入口适配交付

2026-10-20；候选 `D1-20261020-RENDER02-CAPTURE-ADAPT`。**PREPARATION_ONLY，等待集中独立复审，未授权生产执行。SDK/Android/ADB/5037/设备/占用操作0，产品修改和Gradle/native/fixture/host构建0。** 这是首SDK前采集能力适配，不是产品回归结果；原RENDER02三项有限Debug独立PASS保持，D1未通过、M0未启动。

依据 [coder要求](D:/CodexProjects/VideoKit/docs/milestones/D1_RENDER02_CAPTURE_ADAPT_CODER_REQUIREMENTS_V1.0.md)、[tester要求](D:/CodexProjects/VideoKit/docs/milestones/D1_RENDER02_CAPTURE_ADAPT_TESTER_REQUIREMENTS_V1.0.md) 及 tester 完整报告 `b66840906fce4aa00fa435b6a94f58d5c74aad3985662a496bdf39b90b412dde`。原批在首SDK前因能力不足BLOCKED，没有新占用读数，不能写成ENV_WAIT或产品FAIL。

## 本批完成

从已审 `d1resume02-activation/tools/capture_metadata.ps1`（SHA256 `fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe`）派生一个有限入口，保留同一原Process、异步原pipe读/文件写、固定小队列、原文件/锁和强保管循环。只增加本次准确角色准入、精确原stdin源/写入归还、二进制分类和计费字段；没有通用命令执行器、并发调度器、keeper服务或额外发布许可平台。

[新入口](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/tools/capture_render02.ps1) SHA256 `b836b50403b4914a4afe762de5e327e2d97ac38bcc66beebafc1d097ab81f17e`；[完整来源与复制pin](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/source-provenance.json)、[逐行差异](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/source-diff.patch)。旧五槽及旧Java观察器原件未改；RENDER01的477个、RENDER02的404个封存文件含APK/旧ZIP均逐项核对不变，见 [保护核对](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/original-preservation.json)。

## 准确28项及有限能力

[完整逐项映射](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/release/exact-28-role-mapping.json) 绑定 tester 原计划 SHA256 `1db733cd14d51b47d41df3670a5d9d84b1f68f599aeb3d02b8d1d814236810d1`，保留全部28角色/argv/依赖/预算及有限remote子命令说明。**25项串行角色入口已实现但未激活；16/19/24三个截图项明确NOT_RUN。**

| 原序号 | 对应入口及限制 |
|---|---|
| 1–4 | 精确identity、全局进程、ps、新包absence；初项须新鲜本地工具/路由/claim门外部证明，其后须准确语义依赖接受 |
| 5–6 | 只安装原RENDER02两份精确APK；锁持有原只读输入并核长度/hash；不重装、clear、卸载或换包 |
| 7–12 | 两包身份/安装SHA/数据UID及inode；不改旧包、不借旧数据 |
| 13–14 | 原私有fixture准确stdin写入349102B，再按固定stat/hash核验；不另造socket传输 |
| 15/18/21/23 | 四个原静音准确runner，各一次；不传manual，不整类批跑、不重试 |
| 17/20/22、25–28 | 原准确全局门和最终fixture/数据身份；只在前一原控制器/outer tool真实归还且语义门通过后进入 |
| 16/19/24 | 原机制是串行、独占保管，不能证明同一原instrumentation活跃且目标安全可见时并发截屏。因此生产入口在Process/lock前拒绝截图，效果NOT_RUN；不在方法结束后截桌面冒充效果，不新增并发平台或UI查询 |

生产argv只从该固定计划派生：四处 `renderScopeSha256` 必须换成负责人**新准确批准scope**，其余参数字节准确；不接受任意command/shell/template或隐藏查询。旧scope `78df082b-ed71-4c34-b032-448c061a299b` 及旧renderScope `641b93e27365df9b3a3bcb9373d0e2dd34d99956f96a4ea771fdd3fb020db01f` 不续用。INSTALL/CASE采集资格窗固定45秒，其他15秒；这是采集资格，不是强制终止期限或产品30秒硬窗变更。

默认 [policy](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/release/capture-policy.json) 为PREPARATION_ONLY，在读取request或初始化capture context前拒绝。生产需要新准确activation记录与独立报告hash；仅有文件/哈希不是本工具自行发许可。OFFLINE_FIXTURE硬限固定本地Python和固定fixture脚本/模式/根目录，SDK路径在工具pin读取及子进程前被拒绝；不能冒充E13/OFFLINE_FIXTURE执行SDK。

## 原输入、二进制及未知保管

fixture源生产时仅允许原计划指定的 `test_media/imgs_and_videos/videos/sample.mp4`（349102B、SHA256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`）；**本批没有读取该媒体payload**。原源FileStream先以只读共享锁打开，同一handle核长度与分块SHA，再回到0，单个4096B原读与单个原stdin异步写串接，写返回后才复用buffer。分别记录pin读取、传输源读取、写调用/尝试/返回字节、原task、源/原stdin一次关闭；写错误不补成功字节，任务/close未返仍由该原控制器保管。

stdout/stderr始终原始字节保存；binary stdout不经UTF8/JSON转换，stderr始终独立文本，非空即首失败停止。每次read返回先按TEXT/BINARY累加，再做资格/队列/保存；记录读写调用数、raw实际字节、保存尝试/已返字节与partial/UNKNOWN。二进制fixture仅用于字节保真/分账，不是有效截图或视觉证明。

保留首失败，继续观察同一原Process/原任务直至自然返回；不kill、不第二reader、不二次close、不丢handle、不通过换scope重做。读/写fault即便后来原资源自然关闭，未知字节类别仍UNKNOWN；不以cap、文件长度或到时填造精确值。元数据intent/halt/receipt自己的原write/close单列，receipt明确不自证自己的关闭；console只在这些原对象和锁已返后输出，但console/控制器/外层tool自身返回仍需外部原观察器证明。后继必须有同原controller退出、原tool streams归还、receipt绑定、准确语义依赖和累计实际/未知分账的原完成证明。

## 预算与实际量

维持32工作单元/4MiB文本/16MiB二进制归档。原28项预留、4未指派不重试/人工；本适配3项截图NOT_RUN，最多25个串行SDK child进入。原文本资格3559424B+控制/转发/报告预留393216B=3952640B。每项控制资格14000B，28项392000B仍在该预留内；超额实际照记并停止后继，不承诺物理读取硬界。

文本累计为外部已知前账+本项原文本read+已返控制文件写+console+一次console归档副本+前驱证明读入。原文本保存属于同份入站payload，其物理写字节另列，不伪装成新的入站内容；额外外层转发/控制/报告开销须由tester如实并入后继proof，未知则拒绝。policy/代码/批准文档是钉住的输入来源，另列，不冒充SDK输出；不声称控制OS/解释器的全部物理I/O。

二进制read与实际archive写、保存未知分列；原16MiB是archive界，不是SDK协议总流量。两份APK出站源payload承诺13176001B，原fixture349102B单列；原只读源pin读取与fixture传输读取也分别记账。SDK内部wire/内部read量NOT_MEASURED，未填造、未当stdout免费或新增归档。三截图12582912B和可能一次fixture归档349102B预留未消费。详见 [计费契约](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/accounting-contract.json) 与 [最终离线fixture逐项实际/未知账](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/offline-actual-accounting.json)。这些本机fixture账不冲抵、退款或重置任何历史scope/UNKNOWN。

## 有限验证与历史失败

最终005 **17组通过、21个原外层观察器自然归还**：[摘要](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/selfcheck-005/summary.json)、[测试源码pin](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/selfcheck-005/tested-source-pins.json)、[原观察器总表](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/selfcheck-005/original-owner-audit.json)。覆盖成功、准确生成349102B输入、二进制保真/独立stderr、文本与binary超额、原read/write故障、stdin写故障、迟到、stdin未关闭/文件未关闭时持续保管与后继拒绝、PREPARATION_ONLY拒绝、缺新授权拒绝、fixture拒绝SDK、pin不符在child前拒绝，以及原外层返回后第二请求的准确前驱/累计分账。

测试只使用本地生成字节，stdin源hash为 `7632338ac076378ca130a602ebcf61ba98f1c62aca5a376395e20ccd1cdc5b2b`，不是媒体fixture原件。外层使用同一Popen、两个原有界reader，超时不终止、不停止排空；fixture异常finally只释放受控gate，保留同一Popen直至自然wait、原reader join、原Windows process handle关闭。没有实际制造永久UNKNOWN；有限gate关闭未证期间保持原对象，释放后自然归还。

历史001两秒测试资格过小，准确stdin自然完成但超时，保留原失败；002基础13组通过；003扩充准入测试发现生成policy以LF字符串而非Windows落盘CRLF字节计算entry pin，按真实文件字节修正；未启动SDK或生产context。004完整17组通过；005最终metadata/console计费与独立tester输出路径版本再次17组通过。详见 [历史](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/attempt-history.json)，不覆盖旧结果。

## 交接及未执行边界

[准确待激活说明](D:/CodexProjects/VideoKit/docs/coder/D1_RENDER02_CAPTURE_ADAPT_ACTIVATION_PLAN_V1.0.md)、[机器完成矩阵](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/completion-matrix.json)、[ZIP](D:/CodexProjects/VideoKit/docs/coder/D1-20261020-RENDER02-CAPTURE-ADAPT-source.zip)、[seal](D:/CodexProjects/VideoKit/docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json)。ZIP包含新源码/模板、原来源差异、准确28映射、代表性本机成功/失败原证据、实际/未知账及原资源归还；产品APK引用冻结原件，不重复归档。冻结后只读，独立review证据写外部。

真实生产入口、安装、fixture写入、四Android方法和截图仍NOT_RUN；没有新scope/许可、设备前置或现场读数。现机制无法安全表达的三张截图完整保留限制和替代方案：后续只有负责人另批已审明确可证明同次目标时机的方式才可处理，不为本批扩框架。其余语义门依tester原始输出审证，不以capture成功代产品PASS。所有旧危险链/UNKNOWN/许可OPEN保持；等待独立集中复审及负责人另派新准确批次，不自动M0。
