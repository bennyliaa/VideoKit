# D1 CONTRACT03 COVERAGE_CHECKPOINT01 测试与版本检查点要求

2026-10-23；负责人已审完整CONTRACT03 B后正式派发。本批在原冻结源上集中裁定剩余覆盖、最多一次新物化过期目标尝试，并按用户既有授权保存本批WIP评审检查点；不是实际设备或新PREAUTH候选测试。

## 1. 已审完整结果与准确来源

报告 `D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_REPORT_V1.0.md` SHA `f67cdf23cf0132fe6ae1d9ef50976ef91de06035e5e729cf2a77278c1f96925b`；manifest `19cf9a1e3d8f01c08ed8d8727ca2495bc9b836eb72bc1a7da939a7bd49824bb2`，负责人核744项/2668183B、bad0。接受10组PASS/有限故障9准确命中，原整包FAIL_TARGET_COVERAGE_GAPS和两原场景不改；无新确认产品源码缺陷或资源UNKNOWN。

继续只读原CONTRACT03源17 `4881f18167ab3cdb2d7d376152f5bf1672358b99af9e285dd0ae828533d25e93`、gate9 `9cff279ddb9e60632b1422dca16af0dac4ab1922fb6b0b27c5a232055e439d72`、plan `b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8`；原98/开发484/A408/B744、两ZIP及全部原FAIL/UNKNOWN/once不改。coder在另一个全新PREAUTH目录开发，禁止测试该浮动源。

## 2. 覆盖集中裁定与一次新过期范围

- **source目标**：负责人接受原B中预先算账、真实追加1字节且准确命中OWNER_SOURCE_PIN_ENTRY/原归还的补充层，作为source门已覆盖。WRONG_OUTPUT_SOURCE原大输入仍因cap未命中，不重写原场景PASS，不为刷绿重复它；在总映射中明确替代覆盖依据。
- **物化内过期**：原9s许可在前置阶段过期、home/Gate/物化未进入的原失败保留。只为缺失阶段新建准确scope，最多一次动态尝试；不续跑f-7或任何原scope。
- 先用既存冻结B的真实阶段计时与源调用图，静态算一个有余量的合法deadline区间：许可须在构造/原Gate.prepare/实际materializer-proof-read完成时仍有效，随后原EXPIRE_DURING_MATERIALIZE等待应跨permit expiry，且早于原proof10s和gate30s门。没有有余量可行区间时动态前完整交静态阻断，不猜9s、暖机或循环换TTL。
- 不改候选、系统/虚拟时钟、原permit绑定或原guard排序。TTL与一次输入/approval/完整argv/profile/阶段判据先固定；观察实际源中原物化proof读已返回、expiry前后时刻、无activation/控制器、原线程归还与claim唯一释放。PERMIT_EXPIRED_OR_FUTURE同码但阶段未到仍不算通过。
- 可增加不启动进程的阶段/词法/期限判据纯模型，原B正常链/其余9故障及A400按同源已验收证据引用，不机械重跑整包。

新证据放 `docs/tester/D1_CONTRACT03_COVERAGE_CHECKPOINT01_EVIDENCE`，原完整入口实际输出只能用旧候选统一允许根 `D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures` 下新子scope。本批动态总180s、150s停新增、并发1/retry0，最多4个自有辅助、读取256MiB/2048次、产物16MiB/512项、单流1MiB；原生产600/30/20/10/120及字节/source门不改。驱动采用已验收B的准确成熟机制，新增profile构造前纯验证，audit只观察；不制造真实未知。遇未知即停新增且停止后续Git写入，原件保全；已知目标未到如实报告，不追加第二次尝试。

## 3. 同批静止检查点：准确分支/提交/私人仓库草稿PR

上述范围结束且本轮原件全部返回、报告及材料完整冻结后，负责人依据用户“更新私人仓库、tester后续按需提交、默认整批分支/PR”的既有授权，**明确授权本次准确WIP分支提交、push到 `https://github.com/bennyliaa/VideoKit` 并创建草稿PR供负责人审阅**。不合并main、不force push、不打stable/release标签，不以提交代验收。

先读 `docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md`。核origin准确仓库、当前HEAD/分支/remote差异、status/diff和已有index；保留他人暂存/改动，不重置/清理，不夹带其他批。选择唯一分支如 `review/d1-contract03-offline-20261023-<本批短号>`；仅从当前准确HEAD新建，不能切到不同内容的旧分支、覆盖或移动工作树。coder同时只写新PREAUTH目录，git branch创建不得改变其文件。

先落盘**逐文件精确白名单与排除理由**、hash、报告验证状态和diff检查：

- 可纳入本次CONTRACT03五修订原98中自有源码/脚本/小型文本元数据、SELFCHECK02自有驱动/差异/报告、已冻结A/B与本次覆盖报告和小型证据、对应root工作单/协调三文档及AGENTS恢复说明。
- 原revision02诊断/失败报告如需追踪引用，可纳入准确小型报告和现有元数据，不为此抓取或打包整个旧依赖链。
- 不纳入正在开发的 `docs/coder/d1android02-readonly-facts-preauth01/**` 或其他浮动源；新的PREAUTH工作单本身如入库必须明确PLANNED/NOT_RUN，不代表实现通过。
- 排除test_media、zip/媒体/大型或原始采集binary、构建缓存、第三方运行时/分发包、local.properties、密钥/凭据/真实秘密环境值。检查每个文件大小和许可来源；发现敏感原件只从Git清单排除并说明，不改旧证据/manifest脱敏后冒原hash。原完整manifest仍引用本地排除材料，另给Git检查点清单，不能声称远端能独立重现全部历史二进制。

只stage该准确清单，禁止git add .。新提交message/PR说明注明CONTRACT03离线评审范围、A及B实际状态、原时限失败/两原覆盖缺口与本补充结果、真实SDK/设备NOT_RUN和D1未通过/M0未启。push前复核stage/diff、精确冻结文件未变及secret/许可/大文件；远端有新内容先审差异，不盲目覆盖。

创建PR后必须调用attach_artifact附到本任务。记录commit SHA/分支/远端URL/草稿PR及未纳入项。如果认证、权限或工具不允许，保留已完成的准确本地提交/分支和具体阻塞，不读取/打印token、不用其他账号或绕过审核；完整报告负责人，不为PR无限折腾。

## 4. 交付与后续边界

一次集中回交：准确source及引用的A/B、source替代覆盖裁定、过期目标实际命中或未覆盖、原返回/预算/NOT_RUN、本批manifest/回执、精确Git白名单/排除/检查、commit/分支/PR或具体未完成项。两个原失败与新补充层分开，不改历史。

本批无SDK/ADB/Native route/TCP/help/设备/Gradle/媒体、新依赖或旧对象运行态查询/二close/kill/补ACK退款。新PREAUTH功能等coder整包冻结回负责人后另派独立B；不自动测试浮动源或进入现场。D1未通过/M0未启，主里程碑与全P0/技术许可边界保持。
