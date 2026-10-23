# D1 GLOBAL_IDLE_CONTRACT03_SELFCHECK02 开发自测安排

2026-10-23；负责人审核完整BLOCKED交付后正式派发的独立新范围。原批不续跑、不重试旧scope。项目恢复授权继续有效；当前阻塞只限失败驱动及其原临时资源证据，不是全项目暂停或要求强制收尾。

## 1. 原结果与冻结输入

报告 `D1_GLOBAL_IDLE_CONTRACT03_FIX_BLOCKED_DELIVERY_V1.0.md` SHA-256 `8e4e5b6f26867465852eeeee914c590b06204a7c6c7722e2dd5ffc7022cc7dba`；原目录 `docs/coder/d1android02-global-idle-contract03-fix`；manifest `55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81`。负责人核98项/1245040B、bad0，ZIP `45fb593f8b7aa916095540275a7287bdf01e524f5a983befc3768e9c9cb4a58c`、99个唯一成员。

接受原BLOCKED事实：第1组纯参数PASS，第2组自有审计驱动在CreateProcess前抛错；原工具已返回，但Popen内部临时资源逐项原close未证。该未知保留，不因进程退出补绿，不查询/枚举/二close原临时对象。后11组及346计划语义NOT_RUN；不把源码实现写成行为通过，也不请求据此正式独立B。

产品工具源保持上述17源seal `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93`、gate9 `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72`、plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8` 冻结。tester同时仅对这份准确冻结源做有限独立语义阶段A；双方不同输出范围，无共享可变cache、Gradle或Git/index操作。

## 2. 本批任务

只在全新 `docs/coder/d1android02-global-idle-contract03-selfcheck02` 形成准确辅助驱动/测试helper派生、profile和记录，不改原98文件/原失败驱动/旧输入。实际候选输出使用本候选已经允许的全新 `selfchecks/work` 子范围，绝不复用 `batch-c45d128d3721`。新驱动明确引用上述固定候选路径和源seal；若测试helper需要派生，只改新helper并保留原hash/diff，不把辅助变化写成产品源码已修复。

优先复用已接受SELF采集返回机制：`docs/tester/D1_DRIVER_CAPTURE_FIX01_PACKAGE/source-manifest.json` hash `b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1`；SELF报告 `2fd415f0bbee624abae236934514a4f9a3310e3d04ac7937d10b65cc9f3fb613`。复用不代表新调用元组自动获准，准确新profile仍需构造前纯校验/固定。

必须消除这次驱动根因：在调用原Popen构造**之前**校验准确程序/完整argv/cwd/env和允许数量；Windows `subprocess.Popen` audit事件中的applicationName允许为None、commandLine是完整字符串，不能把它当原argv数组。audit仅观察并记录，不在已可能分配临时pipe/DEVNULL之后用主动抛错测试参数拒绝。若发现未声明事件，保留观察、停止后继新准入，当前已进入的自有有限调用按原机制等真实归还，不改已进入结果。错误程序/参数的拒绝只做构造前纯反例，禁止实际启动错误程序或故意触发构造后审计异常。

先完成一个有限驱动资格组：完整元组/Windows audit映射纯正反例；固定自有Python正常退出、已知非零退出、固定PS正常退出三次原调用，各自自然运行至多5s、单次原wait/readers/streams/H归还可观察，按实际exit分列，正常非零不能转成永久UNKNOWN。不得实际注入CreateProcess结果未知或关闭未知。沿用已有成熟捕获实现，不新建通用进程/诊断框架。

该资格组准确通过、全部原对象返回且无新UNKNOWN后，才在**同一预冻结新批计划**继续一次受影响整包开发自测：原346计划语义（98/175/73分别归属）、五缺陷准确反例和全部条件正例、原collector/七角色END/once/唯一释放、preStart13、有限故障、PS post/最后Start、物化变化、新tester根完整链、小追加准确OWNER_SOURCE_PIN_ENTRY。无条件PASS/任意拒绝不能替准确原因；原WRONG_OUTPUT_SOURCE先cap缺口保留。

动态整批总上限仍360s、320s停止新增、并发1/retry0；驱动资格也计本批预算。先固定新源/profile/调用图与所有时间、字节、文件、进程预算，沿用原1GiB读取/16MiB归档/96辅助进程上限，不扩原生产预算。静态预计不适配即在动态前完整交准确估算，不执行后加额；遇新不确定原返回停止新增动态并完整报告，不能无限衍生自测。

如果有限自测发现候选源码问题，只集中记录全部可安全完成的结果，不在本批改冻结产品源或逐问题交tester。完整结果后由负责人统一选择集中修复或正式B。

## 3. 不扩范围与交付

无SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/新依赖；不查旧临时对象、session55065/001a或其他旧未返链，不强停、二close、补ACK退款。产品FIX02、Native/runtime、17源、gate9、七角色及原预算不改。

外部交接方案本轮继续仅静态待审。现有签名/公钥/密钥托管/IPC扩展未获实施批准，本批不开发这些设施、不签authority，也不将同调用者合成issuer冒外部批准；后续选择最小可操作方案由负责人在完整复审后统一决定。

交一份完整SELFCHECK02报告、新驱动/profile与差异、驱动资格和整包实际结果/未到达项、原返回证据、原98冻结前后核验、source/gate/plan身份及新测试材料manifest/唯一ZIP/独立回执。新整包封存应明确原BLOCKED原件与新验证层的归属，不覆写原状态、不制造hash循环。完成主动整批通知负责人；通知失败保留报告，不绕过。

tester当前语义A不是正式整包B。负责人收到双方完整结果后再准确派下一整批。D1未通过/M0未启；Git/index暂不操作，后续tester整批分支PR规范保持。
