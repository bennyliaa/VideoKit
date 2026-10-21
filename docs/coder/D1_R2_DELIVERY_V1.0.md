# D1 R2 整批设计交付回执 V1.0

2026-10-16。状态：DESIGN_PACKAGE_READY_FOR_INDEPENDENT_REVIEW；D1未通过、M0未启动。依据[R2正式需求](D:/CodexProjects/VideoKit/docs/milestones/D1_R2_CODER_REQUIREMENTS_V1.0.md)、[负责人R1处置决定](D:/CodexProjects/VideoKit/docs/D1_R1_COORDINATOR_DECISIONS_V1.0.md)、[R1独立评审](D:/CodexProjects/VideoKit/docs/tester/D1_R1_REVIEW_REPORT_V1.0.md)完成四个方案及本回执，仅新增这五份文档。

## 1. 主体身份

| 文件 | SHA256 |
|---|---|
| [源聚合租约](D:/CodexProjects/VideoKit/docs/coder/D1_R2_SOURCE_LEASE_CONTRACT_V1.0.md) | `b0bae695abdb189251ca81c40a45f2a6a27dacb2a9d740fbbe5d153f3a0dea17` |
| [输出能力与恢复](D:/CodexProjects/VideoKit/docs/coder/D1_R2_OUTPUT_CAPABILITY_AND_RECOVERY_V1.0.md) | `b64ba9c1ce43cff8c353e17dff2370c7de407342c63a0130652f1ddca5d67a52` |
| [真实本机Provider计划](D:/CodexProjects/VideoKit/docs/coder/D1_R2_PROVIDER_SPIKE_PLAN_V1.0.md) | `c070320396513c5d23d31535df62297f2961b6a4a0648716fc72c93439e75bf1` |
| [原生故障门禁计划](D:/CodexProjects/VideoKit/docs/coder/D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md) | `e3adbcda852d421df0beda8c228e74de38f3e00421982da04089bbf476df07ec` |

本回执不写自身hash避免自引用；R2是设计材料，不创建APK、源码候选或freeze目录。主体hash待tester独立核验，不能以本文自查代替独立评审。

## 2. R1-R01–R05逐项回应

| R1问题 | 已补齐的可裁定材料 | 未实现/未证与审定条件 |
|---|---|---|
| R01 聚合租约 | 字段/别名权威、整任务future-open预留、seal/reserve/open/read同一线性化、R向量、会话释放/宿主全源事务区别、seq/query/通知丢失/close重试/进程恢复；10条初态→并发顺序→唯一终态反例 | 现C14单任务账本未变，不是产品聚合实现；持久日志/别名resolver/跨consumer/恢复仍需有限实现与验证。材料待审，不自判真实缺口已关闭 |
| R02 Sink及恢复 | 显式能力/FD三种所有权、首轮DUP提案、稳定export/handle/owner/attempt/plan/source版本、writer与只读验证lease、真实sync/close/durability区分、query/READY/abort/COMMIT，12组并发反例 | 两个现本地Sink不因此成为通用宿主Sink；首轮writer一次授权、恢复只清理/query是实验提案，正式重启/公共签名与码表尚需评审，不削减P0 |
| R03 真实provider判据 | 真实授权大文件/小文件/空文件路径与历史hash，既有ReadHandle实际调用、guard/版本条件、独立reference、22个case、注入分类、IO/输出/时限预算及明确停止 | 全部PLANNED_NOT_RUN；新lease/capability adapter与harness未实现。当前代码提前EOF等差异明确保留；Windows句柄dup不等Android/Binder；本机IO不外推NAS/完整播放 |
| R04 宿主JNI机制 | J01–J11逐调用进程/UID/输入/owner/触发/观察/回收/缺证，F01–F08与O01–O04功能/精确原因分栏，新旧严格方法映射 | J03–J06等宿主致命JNI没有屏障机制，明确BLOCKED_HOST_JNI_MECHANISM；提出同APK受控执行进程等可审替代但不采纳/实现。无Java catch/系统服务/小像素风险接受放行 |
| R05 引用版本勘误 | 采用固定12:38:18快照及下列hash，承接负责人附加勘误 | 原R1主体与回执保持原hash；不修改已审R1矩阵或C14。勘误只校正证据锚点，不产生设备功能结果 |

R05正确锚点：[batch-status-20261016T123818.json](D:/CodexProjects/VideoKit/docs/tester/D1_C14_EVIDENCE/batch-status-20261016T123818.json)，SHA256 `1f8fa4c6ca11c271d19fab16da06a3e490723c50251837219f6b0e3d49ca3d7a`，at=2026-10-16T12:38:18+08:00、WAITING_FOR_TABLET_CONNECTION。12:41的可变batch-status及[C14环境中间报告](D:/CodexProjects/VideoKit/docs/tester/D1_C14_ENVIRONMENT_STATUS_V1.0.md)另属后续时点，不能替代这份固定快照；两时点均不证明C14执行通过。

## 3. 已决、建议、未验证

**已决沿用**：宿主源身份/版本权威、seal与实际归零、显式Sink与同ID仲裁、READY不等业务COMMIT、功能隔离/精确原因分栏、原P0与单APK约束。**待审细化**：本批字段/状态机/原子点、query与writer策略、错误码/兼容、22个case和F/O判据。**尚未验证**：任何新聚合/通用Sink/harness行为、真实本机窗口IO、native机制、Android/SAF/NAS/完整媒体及产品能力。

`SOURCE_CAPABILITY_UNSUPPORTED`、`SOURCE_CHANGED`为公共码新增候选；WORKER_DIED语义按负责人决定保留，但若加入公开enum仍需版本/unknown fallback评审。stage/reason与状态PENDING/UNKNOWN不冒充现已冻结ABI，也不靠UNKNOWN伪造精确信号PASS。

原C13 self系统signal0严格FAIL保持；独立双槽OS11/资源事实不相互覆盖；App trace缺失与ordinary UNKNOWN继续OPEN。C14仍73项待合格环境、另2项NOT_RUN_UNCHANGED_PLATFORM_LIMIT；新F/O名称须独立评审后正式派发才可用，不能改C14调度或追认其PASS。本批不注入崩溃、不新crash handler、不轮询设备。

## 4. 原P0与§29影响

| 原文来源 | 本批具体影响与不变条件 | 正式阶段 |
|---|---|---|
| §14/17/21/22/26.1、26.5、26.7/27 | 明确源与输出授权/实际回收、未知结果与幂等；输入不写/不移动、不泄露路径凭据、不产生成功部分输出、不误释放他槽。方案未实现不能记PASS | D1有限实验→M0契约/Fake/TestKit→M1/M6/M7真实集成 |
| §27会话故障 | 功能/原因分栏不降低宿主/他槽存活与实际资源P0；宿主JNI未有机制则阻断，不只列风险后准入 | D1先处置关键路线，M3/M6完整故障与资源矩阵 |
| §29.1/2/8/11 | 既定内部命名、模块/纯引擎与Flutter控制权不变；新平台FD类型不泄入核心计划，未实施UI/overlay或M0 API | M0/M1/M2/M7/M8 |
| §29.3/4 | Media3 1.9.3薄适配、FFmpeg8.0.3仅受限Debug不变；未下载模型/媒体、改依赖/许可或新增组件；真实标签/权重权利仍缺 | D1准入与可行性，M5/M6/M7实际能力/分发 |
| §29.5/6 | IO_BYTE_PROBE的.bin/协议READY不是有效视频；不改变六真实帧/PTS/色差/EOF、正式H264/AAC/SDR候选或remux要求 | D1接续，M4/M6真实编辑输出 |
| §29.7/12 | 本机4MiB输入请求/有限缓冲/输出与时限是新实验提案，非产品性能；C14 CPU2/encoder1/8数组及设备输出/日志限制不变 | D1实验预算，M3/M5/M6正式性能/热/质量 |
| §29.9/10 | 具体补通用Sink能力、FD/验证/恢复身份、sourceVersion/ownerEpoch/query；仍待schema/兼容与持久性实证，不把noop sync或epoch变化当资源释放 | M0协议/schema，M4/M6恢复，M7多宿主 |

十二项都有对应归属；不以本批设计移除任何P0、宣布整体API冻结或将完整M5质量提前到本机IO实验。Apple/Windows仍只设计，本机Windows测试工具计划不是Windows Kit实现；Flutter＋独立Kit/AAR/C ABI、Android先行保持。

## 5. 可派的下一完整批次与验证记录

先由tester对本五份材料独立评审，负责人裁定所有权/原子点/码表/边界与实验预算。若通过，下一完整离线批次可仅实现受控本机harness并一次执行P01–P13/Q01–Q09，保留真实delegate与独立窗口对照、注入、资源/终态和IO实耗；不是先实施M0或新APK。未实现、版本无法保证、durability/实际dup不支持等按各case条件NOT_RUN/BLOCKED，不能用mock补真实PASS。

仍须设备的工作：保留冻结C14整批接续/反例计划；E3的真实显示/PCM、宿主JNI/原生机制、Android provider/多任务与后续NAS/产品矩阵由负责人在可用环境后另派。当前不要求用户重新连平板、找不存在的启用按钮、交NAS凭据或买模型。团队仍可离线完成harness实现审查、权威日志/版本/错误映射设计及现有模型/样本用途盘点；不自行下载或开启实验。

本批只读检查了固定快照hash、R1三份原件hash及四份R2主体的本地链接/行号和跨文档身份/案例/预算。只读verify_c14.py --working-tree仍PASS：342源条目、139证据、5产物；冻结摘要 `880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155`、源ZIP `69ca847d7c1947ae65eb3ed6e79d8ab50e21ac9463a1a686cdeda6cfef2d683d`。这不是重跑871断言或新增功能/设备PASS。

本轮仅为核对本机文件共享/句柄计划查阅三份官方API页，引用版本/日期在provider方案；没有下载组件、媒体或权重。无Gradle/产品编译/ADB、无本批功能/设备任务在途。R1/C14及原样本未改，新的五份文档交统一独立评审。

按最新用户明确指定接收窗口的通信授权，保存完整结果后向负责人 `01a107c3-2bf9-7fa0-94a0-234258ca6774` 报告；若自动审批拒绝只记录未送达、不反复尝试。通知结果以本任务最终回复为准，不自行派tester/下一阶段。D1未通过，不进入M0。
