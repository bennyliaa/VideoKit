# D1 平板收尾后的恢复开发需求

日期：2026-10-20；版本：V1.0；状态：FORMALLY_DISPATCHED_OFFLINE_DEVELOPMENT。负责人已接受平板 OBSERVED_ALREADY_STOPPED，正式派发本批最小离线实现；原准备版已保存候选 reference 快照。

负责人最新顺序为：tester 完成 TABLET_CLOSEOUT_CONT → 负责人接受平板现状 → 本开发批次集中实现及主机构建 → 独立离线审查 → 等待无其他项目占用及新鲜 M1 后再正式派准确单项 T07。本批禁止设备/SDK/占用或旧任务查询，不自动启动设备阶段。

## 目标和基线

以冻结 D1-20261018-E13F（app19 / fixture3 / ABI1）为来源，完成行政收尾证据与未来执行策略的最小绑定，交付一个可独立审查的新主机策略候选。不得重做通用生命周期、重做已完成的 A/K 主机终止、复用 K 诊断入口，或以来源审查 PASS 代替真机 T07。

依据：`docs/PRODUCT_REQUIREMENTS_V1.0.md`、`docs/PROJECT_DECISIONS_AND_EXECUTION_V1.0.md`、`docs/milestones/D1_CODER_REQUIREMENTS_V1.0.md`、`docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md`，以及对应 tester 草案。当前 D1 NOT_PASSED、M0 NOT_STARTED。

正式 App 保持 Flutter（编辑及多画面），Kit 保持独立、无宿主业务和 UI 耦合；输入媒体只读，输出仅授权临时 Sink。Android12/API31+ 手机/平板为当前实施范围；其他平台保留兼容设计。全部 P0 保留：API/Fake/能力版本、单视频、静态/动态图像、HostAction、多实例/唯一音频/资源预算、排序拼接、手工马赛克、自动跟踪纠正、导出恢复、隐私许可和独立 SDK 交付。不得以当前 Spike 或 T07 代替完整 App/Kit。原开源许可限制不变，FFmpeg/LGPL 二进制仍 NOT_GRANTED；模型权重权利独立核实。

## 启动依赖

1. 已接受 `D1_TABLET_CLOSEOUT_CONT_REPORT_V1.0.md`，SHA256 `5d85e965029c8f923ad4bdffa4e5471bfa8d5e4e6c033b23de27fae40f61e354`：VideoKit stopped=true、完整 processes/ps 未见相关进程，global active instrumentation=0；强停=0，记 OBSERVED_ALREADY_STOPPED，停止原因/执行者未知。LendManager 仍有前台活动，真机阶段继续等待，不重复点击强停。
2. 固定原任务行政事实：`D1_AK_CONSOLIDATED_CLOSEOUT_REPORT_V1.0.md` SHA256 `bc4698568858a7a18b36e077c6aabe1e14915fe7e9746252928637e88ad26a26`。A/K 两原 Java 外部终止，原 Java return=false；外层 PowerShell 自然退出不构成 Java/Socket/reader/Android ACK。
3. B/H 独立保留 ADMINISTRATIVELY_QUARANTINED_UNKNOWN；旧 FAIL、缺失 ACK、原账本及 once 不改、不退款。原 launcher 的 ORIGINAL_RETURNED 标签不能覆盖上述事实。
4. 正式派发及负责人行政接受记录已在 `docs/coder/d1resume01/disposition/` 保存并绑定摘要；这里的 review 是行政接受，不是新来源独立复审。新来源审查、设备派发与新鲜 M1 仍须后续真实证据，不伪造批准摘要。

## 最小差异清单

| 项目 | 正式开发时允许的最小改动 | 不可推断的结论 |
|---|---|---|
| 行政证据 | 新建不可变聚合记录，分别指向 A/K 原始收尾、当前平板结果、B/H 隔离记录 | 强停不补正常归还 ACK；B/H 不转 PASS |
| typed disposition | 复用 E13PendingGuard 既有精确十字段 schema；保留原 scope、设备、包集合；使用 TERMINATED_WITHOUT_RETURN + originalJavaReturn=false | 不使用 ORIGINAL_RETURNED/true 粉饰终止 |
| 证据摘要 | caseEvidence 绑定 A/K 与平板聚合；diagnosticDisposition 绑定 B/H 独立隔离；review / authorization 绑定真实审查与授权记录 SHA256 | 用户授权不是执行结果；历史授权不等于新来源审查已过 |
| 策略来源 | 从冻结来源生成新工作候选，仅将 E13GuardLocation.DISPOSITION_SHA 从 ABSENT 绑定正式记录 SHA；同步新 JAR / observer / release 引用 | 不原位修改 E13F 冻结源码、JAR、binding 或旧审查 |
| 准确执行材料 | 新候选中绑定完整来源审查、单项选择、scope/release/once、预算和归档策略；全部参数机械一致 | 旧 null 字段不是有效 release，历史六项预算不能继承 |
| claim 分支 | 不预先改 schema。后续经授权的现场清点若发现独立未结 claim，停止并提交具体最小 typed administrative-claim 差异供单独审查 | 全局 disposition 不自动豁免后续 claim；不删 claim/active.pointer，不伪造 original-returned |

既有 schema 的精确键：kind、originalScope、serial、packages、outcome、originalJavaReturn、caseEvidence、diagnosticDisposition、review、authorization。kind=e13ReviewedOriginalDisposition；originalScope=aeefe32f-816d-4c0b-aca7-16f76dbd45ff；serial=HA1Q6WXR；packages=com.videokit.app,com.videokit.app.test,com.videokit.e13.sender。包集合是旧策略目标身份，不证明三个包均被强停。记录须遵守原 canonical 编码及 8192B 限制。

现有 enter 仍逐一检查实际 guard root 的 *.claim 及准确归还标记。当前准备不查询该目录、不假设为空。保留原 custodian、同代 owner、强引用、物理归还与失败保留语义，不为通过准入绕过检查。

## 预计一次构建与整包交付

预计正式批次集中一次主机工具构建。Android 产品/测试/fixture 源码不变则复用已冻三个 APK，Android 构建为零；不得仅为改行政策略重编 APK。若独立审查发现必须修改 Android 的实质缺陷，先向负责人汇总扩展范围与新版本，再集中一次必要 Android 构建，不能悄悄覆盖 app19/fixture3。

交付包包含：准确最小差异、不可变行政记录及摘要、来源快照/清单、新 JAR 与观察入口摘要、原 APK 身份引用、有限本地自检结果、逐项准入矩阵、完整预算和一次执行材料草案。先集中自检、冻结一个新候选，再整包交 tester；不得逐小项反复编译/交接。准备文档本身不生成可执行许可或消耗 once。

## 单项 T07 的后续准入

限定推荐首项 `com.videokit.spike.e4.E13DeviceTests#ordinarySenderCannotBindCodec`，只运行一次准确选择，不隐含批准另外五项。既有选择键 class/e13Case/e13Batch/e13ScopeSha256 必须与来源规则一致；批次常量 D1-E13F-LIFECYCLE-20261018 不是新 scope 的替代品。采用新的执行 scope / release / once 身份绑定，不重用已消耗许可。

正式执行须另行取得：平板收尾接受、行政策略独立 PASS、经授权的新鲜完整 M1、准确安装前身份与全局占用、部署后 M2、来源与方法选择匹配、准确命令/文本/归档预算及负责人派发。历史安装 v17/fixture1 仅历史，不能作为当前设备事实。M1/M2 要包含设备型号/API/user、包版本、签名/UID/数据身份、fixture 及其他项目占用，无未归还 owner/未知输出账目后才可进入产品调用。

历史六项方案 51/53 操作、2MiB 文本不是本单项预算。当前新方案明确为 43 次操作（部署入口1+SDK子进程35+单case入口1+instrumentation1+M1采集3+M2采集2），不含占用重试。完整预算见 `docs/coder/d1resume01/release/exact-budget.json`：原始/重复输出1949696B，元数据控制文本786432B，未分配不可使用409600B，总3MiB文本/4MiB归档。相比旧2MiB，明确增加的理由是两次完整512KiB占用采集与原归档记录的重复计费；这是待独立审查和未来正式设备派发的新提案，不沿用旧余额或已获额度。现有旧预算不能授权新计划，复审/准入不足仍不得派发。

PASS 必须同时具备准确单方法 JUnit/作用域/令牌/退出证据、真实 Android Looper/Binder/UID/不同签名 fixture 的内核访问拒绝证据，以及原 PC/runner/线程/资源物理归还。内核拒绝不证明内部 Binder 方法已执行，阶段日志不等于最终通过。首个失败、超时、占用、UNKNOWN、解绑异常即停，保存原 owner，不重试、不追加其他五项、不强杀换取 PASS。

## D1 余门与退出边界

| 余门 | 本批作用及后续依赖 |
|---|---|
| 来源/权限/真实生命周期 T07 | 当前只准备行政绑定及单项准入；单项 PASS 只关闭其矩阵单元，其他五项待负责人下一整批决定 |
| 宿主随机读取与 Media3 | readAt 短读、未知长度、2GiB+、断线、取消、释放、seek 仍按原 D1 证据矩阵独立验证 |
| 格式/轨道及真实渲染/音频 | 真容器/编码探测、轨道选择、显示/声音及状态恢复不能由编译、样本读取或方案分析代替 |
| Sink/导出恢复 | 顺序/随机写、flush/close/abort/markReady、重开验证及取消/进程终止仍需完整证据 |
| 跟踪/质量/权利 | 合法权重、离线质量、纠正、LOST/AMBIGUOUS 与漏遮保护仍独立收口 |
| 资源/原生隔离 | 多实例预算、唯一音频、真实原生崩溃隔离不能用普通异常代替 |
| 设计交付与独立 Kit | API/Sink/资源/质量阈值、SBOM/NOTICE 和独立接入证据完成后，由负责人审查 D1；不得自动进入 M0 |

上述为保留余门，不宣称本恢复批次同时完成全部 P0。正式报告逐项使用 DONE/NOT_DONE 与 PASS/FAIL/NOT_RUN/BLOCKED，历史结论保持可追溯。
