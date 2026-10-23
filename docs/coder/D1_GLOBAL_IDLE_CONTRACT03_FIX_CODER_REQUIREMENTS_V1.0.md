# D1 GLOBAL_IDLE_CONTRACT03_FIX 开发要求

2026-10-23；负责人正式集中修复派单。用户恢复开发与整批交付授权继续有效。范围仅为 GLOBAL_IDLE_CONTRACT02 revision02 独立 B 的五项集中缺陷、对应回归，以及准确未来事实采集提案和最小外部交接方案；不是 M0 或新实机批。

## 1. 准确输入与结论

- 独立报告：`docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVISION02_INDEPENDENT_B_REPORT_V1.0.md`，SHA-256 `f4d16721f662a714133b7b0368a9ea50dedfe3fb1b60f653949843997c00006f`。
- 证据清单：`docs/tester/D1_GLOBAL_IDLE_CONTRACT02_REVISION02_REVIEW_MANIFEST_V1.0.json`，SHA-256 `3f59fd68a69a47e9016299f5c199ce86299db0bca9b2a12da65468d76edc6348`。负责人独立核验 1003 项、5843549B，bad=0；完整报告结论 FAIL 接受为本批修复依据。
- 原冻结候选：`docs/coder/d1android02-global-idle-contract02-revision02`；source 17 项 seal `e0ad5adf1e0ae3a48d397ac0d8205a72394b54dffd9e85a3693e18ab831601db`、gate 9 项 `297bd1ef7189e46831bbab4cfd2b541cf325a6d4adb2c532111e87ee7faa8140`。原 1140 文件/ZIP 1141 成员不修改。
- 原独立 45/45、开发回归 98/98、17 个独立条件正例及有限正常原链通过有明确范围；补充语义 175 项中 170 通过、4 次错误 PASS 和 1 次拒绝阶段断言失败均保留。不能将局部通过改成整包通过。

## 2. 本批必须集中完成

| 缺陷 | 实现与开发自测要求 |
| --- | --- |
| B-R2-01 / P1 未识别前置进程记录被跳过 | 先完整盘点疑似顶层进程记录，再逐条验证支持语法。首条受支持记录之前、记录之间及尾段的未识别进程形内容不能静默遗漏；覆盖 `*APP* UID10065`、`*APP* uid 10065`、`*APP*UID 10065`，以及相同 APP/PERS、前置/中间顺序边界。真实 68 记录样本仍完整解释，缺资格仍拒绝。 |
| B-R2-02 / P1 状态数字前缀被接受 | own `curProcState` 按完整词法与完整整数校验，不接受 `16.5`、`1.5` 或其他不支持值的整数前缀。重复、缺失、负数、非存在状态、超界和明确支持值分别测试；cached 错误 PASS 必须在准确解析层被挡下，HOME 后继拒绝不能冒充词法验证通过。 |
| B-R2-03 / P1 fixture 未约束 argv[0] | 固定本地 producer 的可执行程序及身份与完整参数共同在构造/Popen 前验证，复用已冻结精确运行时身份。真实 adb、其他 Python、仅同名程序、额外参数等用纯参数反例证明准确拒绝；不得实际启动错误程序验证防线，不把这一静态问题夸为 LIVE authority 已被绕过。 |
| B-R2-04 / P2 当前未来提案绑定旧包 | 新版提案绑定本批实际 source/gate/collector/factPlan 内容与准确新路径；逐字段区分内容 hash 未变化与路径/source 变化。旧提案保留为明确历史原案，新版仍为 approvedForExecution=false，不能以提案生成执行许可。按 source/gate → 提案 → 完整 manifest/ZIP 的无循环顺序封存。 |
| B-R2-05 / P2 三入口 fixture 白名单不一致 | 在生产 Runner、Gate、Owner 中统一准确、有限的本批 tester 输出根和候选自有测试根，保留 LIVE 原共享 claim 路径。指定本批全新 tester 根须能进入原完整链；越界根、别名绕过、旧 scope 不得放行。不能靠改 tester 驱动路径掩盖三入口分歧。 |

补一份简短、可操作的外部交接方案，准确列出原 Gate.prepare 后 routeProof 才出现、外部 authority/approval 双 hash 接收受 proof10s/gate30s、事实至目标资格与 global_idle 剩余新鲜期至多300s的先后顺序。选一个最小可执行路径，明确谁在何时持有什么原对象、负责人批准边界、失败/超时的原返回和拒绝；若需要预先批准固定的一次性签发入口或调整信任契约，逐项列为待负责人审定，不用同调用者合成 issuer 字符串冒充外部批准。此项当前只做静态方案，不新造通用诊断/调度框架，不执行跨会话现场交接，也不擅自扩原时窗或自动自签 LIVE 许可。

## 3. 实施、自测和冻结

在全新 `docs/coder/d1android02-global-idle-contract03-fix` 目录形成新候选，保留原报告、旧修订、旧失败输入及所有原预算/once/UNKNOWN。先保存准确源、调用图、预算和本批 scope，再执行直接有限函数/纯参数检查，随后一次受影响整包自测。开发动态整批最多360s、停止新增案例后只收已有原返回；并发1/retry0。用例、读取/写入量、子进程/流/句柄和外层预算必须执行前固定；如完整预计不适配该预算，先交静态实际估算，不在执行后扩额或连续派生自检。

保留原23规则/45矩阵、开发98案例、全部条件正例；加入五缺陷的准确反例和同类边界，不只复制原断言。原七角色/END/once/唯一释放、preStart13、生产 PS post/最后 Start、物化变化及小追加字节准确 `OWNER_SOURCE_PIN_ENTRY` 必须集中回归。原 WRONG_OUTPUT_SOURCE 先撞 cap 的缺口继续按原结果保留，不能以任意拒绝冒精确 source 覆盖。未知创建/Start/close 只做纯状态模型，不故意制造无限未返回；当前全新自有已知失败路径由同原 owner 按实际资源唯一归还。

无需 Gradle、产品 APK 重建、新依赖、许可升级或缓存变更。不得 SDK/ADB/Native route/TCP/help/设备/媒体调用；不得查询、attach、轮询、kill 或二次 close 旧对象，尤其旧001a scope/session55065。旧未知链隔离不是本批推进前提。产品 FIX02、Native/runtime、七角色和原生产预算均不扩。

完整交付包含：新目录/精确 diff、五项逐条映射、真实开发回归与原返回结果、调用图、当前未来提案、外部交接方案、新 source/gate/plan/full manifest、ZIP 唯一成员、独立冻结回执和各项 NOT_RUN。原开发自测失败及辅助失败也保留，不重写全绿。

开发自测完整冻结后主动整批报告负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774`；通知失败只保留，不绕过。负责人核验后才正式交 tester 独立整包 B，不逐问题交接、不测浮动源。

## 4. 版本与里程碑

本批开发期间不切共享 Git 分支或操作 index。用户要求 tester 后续按需整批提交继续有效；本批独立复审后由负责人选定静止检查点，按 `docs/GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md` 安排准确分支/PR，不以提交代验收。

D1未通过、M0未启动，主里程碑和 Flutter/独立 Kit/成熟框架版本许可/全P0边界不变。
