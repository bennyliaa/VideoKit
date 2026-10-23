# D1 PREAUTH01 独立整包 B 测试要求（待正式派发）

2026-10-23；负责人已审核开发完整结果并保存本要求。**当前只是准确B准备单：tester先完成已经开始的COVERAGE_CHECKPOINT01与Git检查点，收到负责人后续明确派发才执行本B；本文件不自动中断或追加其当前任务。**

## 1. 准确输入与已知缺陷

产品候选 `docs/coder/d1android02-readonly-facts-preauth01`，source20 `02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df`，gate12 `bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192`，plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`。原BLOCKED报告 `d170d1bffb784d78624bb753ed5fa341d17f503541f5b680ab6dbc9308bdd413` 与56项manifest `3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c`保留。

完整开发自测在 `docs/coder/d1android02-readonly-facts-preauth01-selfcheck02`：DELIVERY SHA `0a49494fc88b55050229c51e7bf918cac4fc79868c67ec1f02bcc401f3fc70d9`，manifest `2c8c69d8ecec03d7bc339ae8bdb2349bdb942258f0c050b183197f1aa960fe61`；负责人核108项/3707218B、bad0，ZIP `1a0fb5e9d424e83ed6de8668607a05b28365c401b3d527d55cfaf7f959773b3c`、109唯一成员。

限定接受开发实际7/7功能组、三次真实驱动资格、138模板反例、43绑定/once、346语义及原返回的已报告范围；独立结果仍待本B。两项辅助问题必须保留：

- 原worker的finally把新结果误写到候选旧evidence/result.json；新结果SHA `b71b9c59e36e06939a2a023846c7bd76f02916babf632b782d80b8efd8c46b8f`已逐字另存，再从原ZIP `e563573c…fed52`恢复旧文件SHA `d11659b55f31aa5bed06fbd76aff611da4b8588334f97d425dad2d052ce1fc10`。负责人复核现在原56项bad0；不能写执行期间从未改变。恢复审计必须与功能通过并存，不能再运行该错误worker main或再次覆盖/恢复原件。
- 预存图只计12个Popen，漏preStart中的1个固定.NET Python Start；实际全图13、原返回已证、低于96，但估算遗漏不抹去。本B必须预存完整Python/PS/.NET后代图。

没有新资源UNKNOWN；产品20源与gate12始终未改。qualification V2适配明确NOT_IMPLEMENTED/NOT_RUN，当前产品能力仅facts V2回执及旧V1兼容，不得误签真实资格/目标七角色或完整D1。

## 2. 本B完整独立范围

1. 封闭模板、canonical JSON/重复大小写字段、准确字段类型/整数/UTC/90秒、source/gate/collector/binder/entry/runtime/SDK/factPlan/policy/设备/唯一scope-plan-run-nonce/固定七query与预算。逐字段删改/模式/超界/expired/future/额外动作和外部hash缺失等均准确裁定。
2. **区分两层反例**：固定原外部批准hash改caller模板，应在hash层拒绝；用明确合成OFFLINE批准hash验证坏Schema/源/预算的内部语义，必须到准确内部拒绝，不能把所有hash不等统拒冒成每一细项已测。外部hash是受信启动输入，本实现无签名/来源鉴别；不把caller自算hash描述为程序已证明负责人批准，真实LIVE还需新批外部准确批准。
3. 原PreparedFacts ticket/同原Gate、真实owner/thread/generation/holder/file-id/route/proof/receipt/ticks及一次状态：构造前/prepare前/换Gate/换scope/换owner/篡改binding/重复绑定或消费后重入准确拒绝；原proof10/gate30不扩。多数纯字段矩阵与少量实际原对象边界分清，不能让source cap抢先拒绝后还称内部目标通过。
4. 真实OFFLINE原Gate→确定性binding→原receiver→固定producer→facts V2→原wait/readers/streams/H/claim/外层退出，旧V1正反和新CLI默认/缺参/固定准确正例；旧V1/newV2回执字段严格分开，不能伪造legacy authority/approval。实际SDK/ADB为0，不运行正确LIVE模板或真正Native route。
5. 对当前准确源进行独立适用语义回归，至少原45矩阵/17条件正例与新源/collector常量绑定。可重建原175或346集合，但分清原A/开发重放与本次新独立验证，不盲继承旧17源的A400为新20源已经验收。
6. preStart13、原资源唯一返回、出错前/后状态、账户/source/control新增模板及binding读写计量；固定原只读query/一次SDK槽/原90-30-15-10和字节门。错误程序/未知Start/close只纯模型，不制造真实未知。重放和跨进程同home的拒绝可作有限已知入口测试，不删除home或退款重arm。
7. 原56/108及两ZIP/20源/12gate前后核；新证据只写本B明确新根。独立预检列出启动、group、finally、异常/收尾所有预定写入目的，写前统一核新evidence/允许新fixture根，不能写候选旧evidence、DELIVERY或任何冻结原件。不要复用带输出路由缺陷的worker main；可复用已接受成熟SELF原返回算法并准确派生新profile。新产物避免Windows aux等保留名称，原已存在文件不重命名或改历史清单。

## 3. 独立执行边界

正式派发时选实际已被该候选白名单允许的全新fixture子scope；证据根独立为 `docs/tester/D1_PREAUTH01_INDEPENDENT_B_EVIDENCE`，不能为取得新目录而修改候选。准确完整argv/cwd/env/脚本与输入/输出/实际后代图、读取写入预算在Popen构造前纯校验/冻结，Windows audit仅观察。

outer360s、worker300s、240s停新增、并发1/retry0；辅助实际图最多64（含PS/.NET而非只Popen），读取最多2GiB/8192次，归档32MiB/2048项/单1MiB，单原辅助观察≤90s。原每Gate source/control及所有生产门不扩，先算真实调用组成本；预算不足在动态前完整估算，不运行后加额。普通已知失败且原件已返可继续原计划，未知即停止新增，不循环刷场景、不强停/二close/补ACK退款。

构造前纯配置错误且无资源/once进入可在本B准备阶段保留版本并修正后重新纯预检，最终实际scope/profile冻结后只执行本批一次；不为静态路径/导入问题反复交接，但也不暗改冻结产品源。

本B无SDK/ADB/Native route/TCP/help/设备/Gradle/媒体、新依赖或Git/index操作。外部authority/真实facts/服务资格/qualification V2/目标安装播放不执行。旧未知对象及所有原FAIL/UNKNOWN/once不查不改，主里程碑/技术许可/全P0保持。

## 4. 交付

一次集中完整B报告，列准确实际测试与纯替身边界、每项拒绝原因/阶段、全部实际原返回和账本/未证、辅助写入/图问题的独立防护、原包不变核验、来源/输入/驱动/profile/调用图、新manifest与独立回执。完整交负责人，缺陷集中回交，完成不自动现场或下批；D1未通过/M0未启。
