# D1 GLOBAL_IDLE_CONTRACT03_FIX 测试要求

2026-10-23；负责人保存的下一整包独立复审要求。当前仅可静态整理原失败 oracle 与本批测试计划；新的开发候选完整冻结并经负责人审核、正式派 B 前，不执行新动态、设备采集或测试浮动源码。

## 1. 接受的原结果

原完整报告 `D1_GLOBAL_IDLE_CONTRACT02_REVISION02_INDEPENDENT_B_REPORT_V1.0.md` SHA-256 `f4d16721f662a714133b7b0368a9ea50dedfe3fb1b60f653949843997c00006f`；原 manifest `3f59fd68a69a47e9016299f5c199ce86299db0bca9b2a12da65468d76edc6348`，负责人核1003项/5843549B、bad0，整包 FAIL。五项缺陷按 B-R2-01～05 集中回交，不逐问题联系 coder。

原45/45、开发98/98、17条件正例和正常原链的限定通过保留；独立175项170通过、4错误PASS、1拒绝阶段断言失败原样保留。group4 错误码断言、首版 AIDL 符号及 ZIP 核验脚本辅助失败与候选问题分列，不能删历史或给候选加假缺陷。本轮结束不是全项目暂停，历史 N2 停止仅约束原 N2。

## 2. 下轮独立整包 B 的验收点

| 检查簇 | 准确验收要求 |
| --- | --- |
| 五缺陷回归 | 独立复现三种前置畸形记录及中间/PERS等边界，完整未证拒绝；`16.5`、`1.5` 等在真实生产函数准确词法层拒绝；argv[0] 用实际守卫或准确静态模型拒绝外来程序且不真实启动它；提案所有新路径/source/gate正确且执行批准仍false；同一新tester根可走通Runner/Gate/Owner原链，越界和旧scope拒绝。 |
| 正例与完整性 | 原23规则/45矩阵、175扩展中的全部适用案例和17条件正例、开发98回归覆盖集中核；真实LIVE03归档仍68条且无新资格拒绝。不能以永久拒绝修掉错误PASS，也不能宽放OEM/system/UID或instrumentation。 |
| 原生产调用与生命周期 | 七角色/END/once/唯一释放、preStart13、有限故障、PS post/最后Start、物化变化、小追加精确OWNER_SOURCE_PIN_ENTRY整体回归。known FAIL与UNKNOWN分层；不故意实际制造无限UNKNOWN，不查询/处置旧链。 |
| 固定事实采集器 | 本批新源/新scope、固定本地producer与原Gate/claim/收尾全部绑定；完整argv/固定程序身份、字节/UTF8/顺序/时钟/错误帧、外部hash/once、真实Popen/原wait/reader/stream/H归还。无SDK/Native route/TCP。 |
| 外部交接可操作性 | 静态审查一条明确最小路径，区分负责人的执行前批准、运行时routeProof、独立authority/approval原返回、同原Gate接收与目标剩余新鲜期。proof10s/gate30s/事实至多300s不得静默扩额；同调用者合成批准不能冒真实外部往返已证。没有真实演示仍记NOT_RUN/NOT_PROVEN，不自动进入现场。 |
| 冻结与账本 | 执行前完整source/gate/plan/提案/调用图/预算和独立驱动profiles固定；执行后原冻结项及ZIP唯一成员核对。记录实际量、来源/哈希、物理归还证明与未证字段，保留旧FAIL/UNKNOWN/once/账目，不补ACK退款。 |

复用已接受SELF驱动的原身份与返回机制，新的准确可执行程序/完整argv/cwd/env profiles仍须预先纯检查并冻结，不能把不相关profile批准移作本批。优先在构造前检查，不能让真实审计拒绝造成未证临时资源后继续测试。外层/worker/读取写入/子进程/观察期预算根据实际完整候选在 B 前准确预存，受影响原生产预算保持不变。

只用全新明确的 tester 输出区；不能编辑 coder 源码、扩大白名单、换路径藏目录缺陷或测试浮动源。真实 ADB/设备/help/Gradle/媒体、旧链运行态查询和Git/index当前均不执行。原报告及证据保持冻结。

全部结果一次集中报告负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774`，缺陷集中回交；完成不自动启动后续测试或事实采集。后续提交按用户授权与GitHub规则，由负责人另定准确静止检查点/整批分支PR，保留FAIL/NOT_RUN等状态，提交不代验收。

D1未通过/M0未启动；主里程碑与原技术许可边界不变。
