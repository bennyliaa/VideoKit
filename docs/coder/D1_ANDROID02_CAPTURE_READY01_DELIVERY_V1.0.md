# D1_ANDROID02_CAPTURE_READY01 完整交付 V1.0

状态：PREPARATION_ONLY；开发侧最小绑定适配及离线自检完成，等待本候选完整独立 B 审查。实际 Android / FD / Media3 / 平台 finish 均 NOT_RUN；D1 未过、M0 未启动。本文件和 ZIP 均不构成执行许可。

## 交付边界和准确来源

在 docs/coder/d1android02-capture-ready01 独立目录交付。旧 RENDER02 入口、原 Python fixture、原文件/锁/Process/异步 stdout+stderr 泵/读取锁定 payload/UNKNOWN 持有及外层 return proof 机制保全；原目录未编辑。适配只增加七角色静态计划、source/policy/activation/前驱绑定、语义门和分组累计及 90 秒/1 MiB instrument 能力，没有新 native helper、端口查询器、通用 dispatcher 或产品修改。

产品 FIX02 seal 39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad；874 个冻结文件全部字节核对一致。旧 capture seal 65e8413b3e90dd571c22fea7049778b29c0d94221cd490560cdcd5c3cc00ae5a 的 818 个文件亦全部一致，包括原 ZIP。旧入口 b836b50403b4914a4afe762de5e327e2d97ac38bcc66beebafc1d097ab81f17e，原 producer 76a0200544f0a0e24e9a29d5fd5114144148810a584054252dd823a92a1975fe。

FIX02 独立 B 报告 4421c264ab6c45a78979aaa9339a3bc1c19e7c3a9b2bf5c6442c0c68dedce1f3 仅有限接受五项源码/真实纯 Java 门，不能用于本工具 B 或设备 READY。阶段 A 报告 bc78ec7ad16ccf239b2005f3eb7b3560a10fb69f5c838a86e7654bb13cb34438 及 7+25 项 oracle 原样引用，仍非设备结果。

准确产品：app 7151481 B / f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad；test 478124 B / b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9；证书 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。版本 D1-MEDIA3-ANDROID02-FIX02；app com.videokit.d1media3.android02；test .test；runner com.videokit.d1media3.android02.test.Media3Instrumentation；唯一 case=scopeAll，fixture SHA19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c，新 D1MA02 runId 待实际激活。

## 七角色与先序门

|顺序|唯一角色|两流上限 B|观察窗 s|必须满足的语义|
|---|---|---:|---:|---|
|1|identity|65536|15|HA1Q6WXR / TB138FC / API31，user0、arm64 和 fresh fingerprint|
|2|global_idle|851968|15|同次完整全局 processes+activities；其他项目前台/instrumentation 占用立即 ENV_WAIT；格式不明或缺失不当 idle|
|3|app_absence|65536|15|准确包查询完整标记内空结果|
|4|test_absence|65536|15|准确 test 查询完整标记内空结果|
|5|install_app|65536|45|同原 read-locked app pin，固定 install -t --no-streaming，无 -r，Success|
|6|install_test|65536|45|同原 read-locked test pin，固定无 -r 安装，Success|
|7|scope_all|1048576|90|一次固定 instrument，保存全部 pending/partial/final；准确新 runId、十项顺序历史、原返回/预算和 mux 观察|

任一原包存在即停，不能升级覆盖、清数据、卸载、换包或转其他设备。不能用包 absence、旧 ENV_WAIT、旧 source/server 事实代替当前全局门。global 固定一条有界复合 shell 查询，内部仅 dumpsys activity processes 和 activities，不另开 SDK 子进程、不改变前台。实际格式未验证，未来有歧义应停。

reference/exact-seven-role-plan.json 给出每一条准确 argv；七角色以外、额外参数、任意 URI/shell/method 均不准入。每步后继必须经过已返回的原 controller、两流原 reader/file/锁/元数据、实际外层 Popen/reader join/stream close/Windows handle close，以及后来单独写完并关闭的 completion proof。前驱绑定 controllerPid、entry/plan/product/request/原 console+raw hashes、nextId、semantic、累计组预算和计时起点；receipt 不自证自身 writer close，console 不自证外层退出。JSON 证据依赖受信任的现有外层 owner，hash 绑定不等同对恶意本地主机的认证。

## 预算和时间

SDK 最多7、串行1、无 retry。APK 二进制出站承诺 7629605 B；command 以实际 argv JSON UTF-8 表示计费，每步最多4096、全最多28672，逻辑 outbound 上界7658277。四 preflight 两流共享1048576、两 install 共享131072、instrument 包括所有 pending/final 两流共享1048576、controller/proof/转发共享1048576，总逻辑 inbound3276800。分配上限已逐组求和，没有每 case 重新领取整组预算。

成功原 read 在排队/资格/写文件前累计，console 带不可重置的六组计数，后继核原 console 相同累计。安装前同一原文件只读锁定并校验长度/SHA，直到原 SDK/输入返回才关闭；pin 读取、fixture stdin 读取、payload commitment、stdout archive 分列。真实 SDK 内部再次读 APK 和 ADB framing 不可见，保留 UNOBSERVED/NOT_MEASURED；本候选不宣称精确 wire 数。若实际授权要求超出可观察能力，应在 child 前 BLOCKED。

4×15+2×45+90=240 秒仅为分项观察窗之和，不是已授权整批 wall 或强停许可。未来 activation 必须另外绑定 wholeWallSeconds（1..600）、localProofSeconds（1..30）及 outerSeconds（1..600）；当前全未赋值。入口负责原启动前本地检查/分项/累计观察门；实际外层 owner 还须按独立 B 审过的 contract 落实 outer/proof wall 和原返回，不能只凭字段把它当作已观察事实。超窗/超量/异常冻结新准入并保管同原对象/两流，不 kill、interrupt、取消 task、重读、二次 close 或另一次 SDK retry。

过量场景不是完整保存成功：测试实际收到192 B、只写入64 B，明确失败/停后继，原读继续归还；未保存部分不能冒充完整 raw，也不把它截到上限补绿。只有合格捕获才可形成后继 PASS。

最终 instrument 的最高本工具分类为 PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN。SDK shell 退出、原 watcher 返回和 app 报告的 worker/lease/mux 返回，均不能证明 app finisher 自身平台/Binder 返回尾部；无 READY/COMMIT/播放/隔离/DTS 能力升级。

## 完整有限本地自检

最终整套 selfchecks/run_checks.py：18.453 秒，13 个原外层 controller 串行、11 个本地 Python producer；7 个测试组全部通过，其中一组含6项启动前拒绝检查。外层原 wait、两流同原 reader join、stream close、Windows 原 handle close 后才写 return JSON，原 proof writer flush/close 后才计算后继 hash。controller/producer/source/argv 记录均冻结。

正常完整七步假流程、同原 stdin 4096+2048 B 安装模拟载荷、pending+final 原 bytes、分组累计与原返通过。六项启动前拒绝为入口 pin、PREPARATION（缺失 request 也拒）、SDK 路径混入 fixture、重复 JSON 字段、第8角色、前驱预算归零。忙碌语义重放的是此前同本候选本地假 producer 原 bytes，明确是 PURE_LOCAL_SEMANTIC_ONLY，不是 fresh 设备观察；此前完整原 capture 忙碌停后继/伪 true proof 拒绝另在保留的历史自检记录中。

过量、stderr、超时迟返、文件 close gate 待返均明确失败并停准入，后两项在本地 gate 释放前观察同原 controller 仍在，最终自然返回；timeout 不能升级 PASS。当前整套外层文本44156 B，模拟输入6144 B；所有冻结测试文件另由 seal 计数。SDK/设备/server/占用查询/旧 UNKNOWN 操作/kill/产品构建均0。

前三次测试脚手架方案分别26.156、26.843、26.906秒，在26秒新准入阈值处主动停止、整套未完成，均 allPassed=false，原记录完整保留，未汇总成通过。调整仅把无需建 context 的拒绝断言合并到一个原 host，减少启动开销，采集入口和 producer 从首轮到最终 hash 均未变。旧脚手架版本不是完整可重放源快照；它们仅作为历史失败/局部原返证据，最终脚手架及整套18.453秒记录为当前验证依据。各次均≤30秒、单 child 串行、6 KiB 载荷；此前运行不当作 SDK retry，也不构成设备或宿主空闲证明。

原 fixture stdin349102 B 未执行；新限定 producer hash b281c18e3873fa1c9ba139a581659212e0708fd9006776cd33838a35dfd433ed。仅固定 Python -I -X utf8 -B +准确 fixture路径/模式/gate 的8项 argv，模式及路径硬绑定，无 SDK/network/媒体行为。故障只允许本地可释放 gate，不加入永久卡死模式。

## 准备态、许可与复核

默认 release/capture-policy.json=PREPARATION_ONLY，在请求读取/锁/context/SDK child 前拒绝。release/activation-required.template.json 的 approvedForExecution=false，scope、planId、runId、独立 B、toolCandidateSeal、fresh route、初始原 proof 和全部 wall 实值为空；不含一次性执行许可。

未来只接受完整独立新工具 B 后，由负责人另签与本入口/计划/产品/工具/新 scope/runId/准确输出目录/B/本候选 seal/freshRouteProof/initialPredecessorProof 匹配的 activation。旧 Render scope 78df082b-ed71-4c34-b032-448c061a299b 和7aebea43-88e7-40cb-8794-cd3c6216cbe0 禁止。工具/server route 与 exclusive claim 复用现有受审外层 checker；本批没有实现/调用新检查器，旧 reference 文件显式 HISTORICAL_NOT_FRESH，不能激活。若负责人无法取得独立 B 已审过的准确 fresh proof，第一 SDK child 前 BLOCKED。本包不自动轮询或串接设备执行。

evidence/static-audit.json 含32项静态映射和7条完整 argv、全部静态 pins/先前完整 seal 校验、四轮自检索引；它不是独立32项 runtime PASS。evidence/minimal-entry-diff.patch 与 source-and-adaptation.json 供整包 B 审计。tools/verify_frozen.py 只读核验本包全部清单，不启动任何子进程；不要直接在冻结目录重跑会写文件的 selfcheck/derive/freeze。独立测试应按自己的受限输出目录和阶段 A oracle 运行。

旧35512/48945/17257未查询、未接管、未终止；无 host idle/清理结论。用户既有平板授权继续保留；本批完成交付后等本候选完整独立 B 和准确新 activation，不重复索取一般设备许可。

## 本候选字节身份

入口 SHA256: fce2d454eb036c6278f71b77393656473af3b35dfe16516cb8358bb6e933bc13

计划 SHA256: f0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199

默认策略 SHA256: 4158e2065ee89fc54d795ae5b03a262926137c48fd5ee5d21601cce96c70e13a

最终完整自检记录 SHA256: 42542f881e02d84ef4f4ea0d015b43bc869af814bf67018834284c9faed9c826

seal 为 evidence/capture-ready01-freeze.json；ZIP 为 docs/coder/D1_ANDROID02_CAPTURE_READY01-source.zip。seal 清单覆盖报告及候选所有其他文件，排除自身和 ZIP 以避免循环；ZIP 包含清单全部文件加 seal。报告、seal、ZIP 的实际长度/hash/member数由外置 D1_ANDROID02_CAPTURE_READY01_HANDOFF.json 绑定，交接通知记录另存，冻结后不改本包。
