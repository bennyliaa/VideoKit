# HOST_TX02_ACCEPTED_GIT01 tester整批Git检查点

2026-10-24 负责人核HOST_TRANSACTION02独立B180项999495B bad0，reportce0d5e66142ba9eecb56b6cc235564ba89bf42358a284d7a617fc9b2a5df0101/manifest717b48eeda3103dabd07dacc207c33a1d96fbce3c1a84a186850e75397603b38，限定PASS、F01本候选关闭。按docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md用户持续按需提交授权，此整批保存已审源码/文档与准确验证范围，不签D1/Android通过。

工作前read-only核当前branch/HEAD、remote/default main与未提交修改。负责人当前核branch codex/d1-qualification07-offline-20261024-a78e，HEAD e7258923f1a0f0757a8213c7b3a8bd8407940138；不得reset/force/改main，远端或HEAD变动先审准确差异。新分支codex/d1-host-transaction02-offline-20261024，以该已审当前HEAD起（不改旧PR3）；创建stacked draft PR至codex/d1-qualification07-offline-20261024-a78e，说明依赖PR3，不合并/发布。需要PR工具能力时先发现已有工具，创建后必须attach_artifact保存URL，并主动报告负责人。

准入范围先生成精确逐文件path/bytes/rawSHA白名单，核通过后只stage该清单，不git add .。本批允许：
- 已接受HOST_TRANSACTION02当前src/checks、自有run/prepare/seal脚本、README/API_MAPPING、case-plan、REPORT/manifest/seal和可安全入库小型预算/完成/来源元数据；实际源码逐hash与候选一致。lib、reference第三方/二进制、classes/JAR/APK/ZIP/原stream/work生成物排除，必要已有自有回归Java/fixture只在许可与来源核清时精确纳入，不能混入同名第三方实现。
- 对应tester01/02独立完整报告、基线A说明与oracle、正式开发/测试工作单、小型非敏感审证/覆盖/缺陷JSON；01FAIL作为准确历史，明确SOURCE_BINDING01静态F01在02才关闭，不必复制旧失败包所有源码/二进制。原报告内被排除本地依赖保持原引用，不修改冻结报告求Git自包含。
- 独立已接受HOST03自有宿主源/Schema/profile/README/REPORT及必要probe自有源码、对应独立B报告与正式单；不纳入selfchecks原日志/流/新现场证据或全部旧HOST01/02失败候选。
- 三当前协调文档及本次之前已有准确已审root协调review/工作单可筛选纳入；root现场materializer/launch/operator脚本与capture/input/raw证据默认排除（现场敏感元数据/未知历史/运行中路径不随普通代码checkpoint发布）。不能全量新增docs或夹带其他浮动新批。

明确排除：coder新d1-platform-execution-handoff02及其浮动输出；test_media、credentials/local.properties/环境原值/云密钥、运行期/本机账号或安装标识、设备raw/packet/带编码原流的JSON、compile/worker stdout、二进制/生成缓存/第三方分发包/旧活动锁PID/UNKNOWN记录。仅排Git，不删本地或改旧冻结/账本。白名单文本中扫secret/大文件/许可，发现敏感可不入库并报告，不改验收原字节。不能以SHA文件不敏感为由夹带其内嵌raw。每文件2MiB界、总新增文本16MiB内；来源检查保守读256MiB，整批30分钟首读前单调记录；不新编译/功能测试/SDK/设备/Native或Gradle。

负责人将在本单和接受状态写入三协调文档后才通知执行；Git完成回报前不再修改这三文件。先冻结白名单与基准源SHA再stage，git diff --cached核准确文件/内容/类型，commit保留PASS_LIMITED/未测/旧FAIL与依赖排除说明。commit/tree/blob逐项核原bytes/长度/hash；push前再核无范围外差异，push仅新分支。若网络/认证/工具拒绝保留本地准确commit/报告，不绕过，不把失败冒已远端。

完整报告包含新SHA/parent/branch/远端/PR URL及状态、准确白名单/排除数量/密钥许可扫描、Git blobs原hash核验和未运行范围。源生成后的报告/receipt不冒在同commit内；这些可以保留下一记录，不为一份回执循环commit。root据完整结果再独立核远端；通知失败留报告不绕过。D1未过/M0未启，主阶段/框架许可/P0/全部历史FAIL/once/UNKNOWN保持。