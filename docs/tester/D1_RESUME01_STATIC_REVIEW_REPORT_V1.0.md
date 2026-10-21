# D1 RESUME01 整包独立静态复审报告 V1.0

日期：2026-10-20。候选：`D1-20261020-RESUME01`。结论：**PASS_STATIC_CANDIDATE_ONLY，阻塞源码缺陷 0；DEVICE_HOLD，T07 NOT_RUN。**

支持负责人接受本次最小离线实现，并准备下一整批准确准入材料。此结论不消费一次许可、不批准设备预算、不表示部署或 Android 生命周期已通过。sourceReview/actualScope/actualRelease/actualOnce 在冻结候选内仍为 null，本报告不会回写冻结材料。

## 范围和来源

依据 `D1_RESUME_AFTER_TABLET_CLOSEOUT_TESTER_REQUIREMENTS_V1.0.md` 及负责人本次整包派单，独立核四处生产差异、行政 false/UNKNOWN、claim 阻断、同 scope 单方法 once、生产 JAR 与自检记录、精确 43 操作和新文本/归档预算。本轮只读取本地冻结文件并生成 tester 证据，没有运行候选打包/构建脚本、Java 自检或 SDK，没有设备/占用、真实 custody root、旧会话/handle 查询或操作。

交付文档 SHA-256：`68a74c4571ecde9562f142a68d5a62939e09f5c1c641331430d87deed84798ab`。

外 seal：`docs/coder/d1resume01/evidence/resume01-freeze.json`，SHA-256 `1673bca8580d7cba82cc3a518e5a9f888d25e52fb42f83beb2dec2c5b519f661`。

tester 证据：`D:/CodexProjects/VideoKit/docs/tester/D1_RESUME01_STATIC_REVIEW_EVIDENCE`。

## 工件与来源：PASS

- 独立逐字节摘要核对 497 项不可变记录；ZIP 的 496 个成员名称无重复、集合完整，成员大小/hash 与外 seal 一致，没有只信任候选自带 verify 输出。
- 来源 ZIP 6442689 B，SHA-256 `bd4ad4548ac9ac1db6b8085fd0bccdfb2d769f854b606dc6087727c3d3c003a7`。
- 旧 F 的外 seal、来源 ZIP 和全部 1179 项冻结记录仍匹配。74 个派生生产来源中，独立重算只有列明的四文件差异；旧源码、observer、生命周期相关实现未被原位改写。
- 新主机 JAR 323124 B，SHA-256 `03a27c74061b740a879e2dfec3341b0b07172c68bf374b9231c20e42a46566c5`。183 个生产 class 的名称集合、摘要及原实际测试 class 字节逐项相同，source pin 一致，无 ResumeCheck 测试类入包。
- 三个 APK 与 F 的已冻字节一致：app `938d70fb…27908e`、test `4227751b…a9dd7`、fixture `a8c86650…d1867`。完整摘要在 candidate-binding 和独立核验记录中。复用字节也保留原已审签名字节；本轮没有调用签名 SDK、重新构建或重新宣称实机安装身份。

## 四处生产差异：PASS

| 文件 | 独立判断 |
| --- | --- |
| E13GuardLocation | 仅将 DISPOSITION_SHA 从 ABSENT 绑定真实 canonical 行政记录摘要；固定 ROOT 与原 return custodian 规则保留 |
| E13HostActivationSession | scope 校验收窄为唯一 ordinarySenderCannotBindCodec，并准确限定 process43/text3145728/output0；其余 trust、release、部署 once、原 supervisor 和 35 子调用限制不变 |
| E13HostCase | 请求方法必须等于已通过 scope 校验的唯一方法；其余五项在真实 custody/子进程入口之前拒绝；原 owner、结果和物理归还门不变 |
| E13PendingGuard | 已有 claim 的 scope+method 相同即拒绝；判断在接受归还 marker 前，所以正常归还也不能重入同项；其他 claim 的原 marker/hash/pc identity/thread join 检查未绕过 |

全局 disposition 不替代后续 claim 的实际归还证明；缺 marker、错误 marker、未结其他 scope 仍阻断。没有删除 claim/active.pointer 的新路径，也没有新行政豁免分支。DEPLOY 保留原独立 once；本次单方法 once 不冒充其替代品。

本轮没有检查真实 custody root，不声明现场不存在未结 claim。未来若现场确有具体 claim 无原返回，必须按正式需求停止报告具体差异，不能借本次静态 PASS 行政清除它。

## 行政证据和 UNKNOWN：PASS

canonical 文件 610 B，小于 8192 B；e9 外层和排序、字符串编码、末尾换行逐字节匹配既有规范。十字段集合准确，原 scope、HA1Q6WXR 和三个原策略包集合不变；该集合不表示三个包都被强停。

DISPOSITION_SHA 为 `7270e5c0208d2895394bbd1cd25508b239bbe7a711a40b3e8d2b3d59a37a265d`。四个证据字段分别指向 case-evidence、diagnostic-disposition、administrative-review、authorization 的实际摘要，引用报告/账本快照的字节摘要均核对。

A/K 仍为 TERMINATED_WITHOUT_RETURN、originalJavaReturn=false；外层 PowerShell 返回和原 launcher 的 ORIGINAL_RETURNED 标签没有升级为 Java、Socket、reader 或 Android owner ACK。平板为 OBSERVED_ALREADY_STOPPED、强停 0，停止者/时间未知；另一项目前台状态不当作空闲。

B/H 各自 ADMINISTRATIVELY_QUARANTINED_UNKNOWN；K 的预算未知、189440/262144 分配和 70656 B 原 wire 事实保持，不退款、不重跑。caseEvidence 与 diagnosticDisposition 没有把这些对象合并成正常归还。

review 明确只表示负责人对原行政收尾的接受，authorization 只派离线批次；两者均没有冒充本次独立来源 PASS 或正式设备授权。行政文件只在候选交付目录，未安装到真实 custody root。

## 构建和有限自检证据：PASS，未独立重跑

记录支持一次生产 javac、零 Android/Gradle/native 构建。初次自检因测试样本漏写已有 `/output0` 后缀失败，原 stderr/exit 1 和原样本保留。最终测试源码与初始样本规范化换行后只有补该后缀的差异；修复只编译测试类，生产 class 输入和测试后入包字节一致，随后自检 exit 0。

61 条断言的范围与源代码一致：22 条 guard/schema/配对/选择及拒绝检查，35 条脚本化响应长度检查，4 条部署端口/总量检查。显式测试根重载未调用真实 custody；五个其余方法仅验证公开 case 入口前置拒绝，不运行其方法体。

独立将原 stdout 的 35 条 TRACE 解码，与 deployment-command-trace.json 每条 argv、顺序和 maxBytes 比对完全一致。真实 E9HostDeployment 方法调用的是本地 Scripted 端口：28 个 adb 路径、4 个 aapt 路径、3 个签名 Java 路径；第 15、16、32 项分别对应 app/test/fixture 的脚本化安装响应。

这些是实际生产方法的命令展开证据，**不是调用了 SDK、安装成功、Android UID/Binder 内核拒绝或真实生命周期的证据**。本轮不重跑 Java 来扩大结论，原 61 条记录的来源和范围已独立追溯。

## 新预算提案：算术与静态展开 PASS，尚未批准运行

| 分组 | 操作数 | 原始/重复输出预留 B |
| --- | --- | --- |
| 新鲜 M1 | 3 | 655360 |
| 部署主机入口 | 1 | 81920 |
| 部署子调用 | 35 | 524288 |
| 新鲜 M2 | 2 | 589824 |
| 唯一 case 主机入口 | 1 | 32768 |
| 唯一 instrumentation | 1 | 65536 |
| 合计 | **43** | **1949696** |

另有元数据/控制文本 786432 B、未分配且不可使用额度 409600 B；合计 3145728 B（3 MiB）。元数据细项重算为 712704 B，余量 73728 B，未遗漏进 operationArchives、observer/console、metadata client、release/scope、claim/pointer 的逐项预留。归档提案为 4194304 B（4 MiB），不是声称本轮实际设备归档已验证。

M1 的 identity/global/ps 分配分别 65536/524288/65536 B；M2 identity/global 为 65536/524288 B，五条元数据 argv 与分组总额相符。占用命令采用完整 processes，没有不支持的 instrumentation 子命令，没有 head/grep 截断；identity 有逐段及完成标记、set -e、包/数据/已装 APK hash 检查要求。工具兼容性明确采用已实证同源 ADB pin，字节变化阻断。全局无 instrumentation 不等于其他项目前台空闲，等待规则保留。

这是独立的新 43 操作/3 MiB/4 MiB 提案；零占用复试、不继承旧六方法 2 MiB 或 K 诊断余额。精确成功路径及记录预留已闭合，仍须负责人接受后才能派设备。

运行边界需准确解释：现有 observer 的 maxTextBytes 是保存/合格界，超界仍保留原读取/归还上下文；该字段本身不是对任意输出流的物理读取硬停止证明。正式派发的外部执行材料必须计入实际读取、必要归档/控制文本及超额状态，遵守总额和第一异常停止，不能把只保存前 N 字节写成只读 N 字节，也不能挪用 409600 B 未分配额度。本包未发布实际执行材料，本轮没有验证运行时硬限或要求重做通用生命周期框架。

## 尚未具备的设备准入材料

冻结 candidate-binding 的 sourceReview、actualScope、actualRelease、actualOnce 均保持 null；scope/release 模板含明确无效 PENDING 字段，无法通过正式 digest/身份门。本报告不将它们视为缺失却可继续的正式材料。

下一正式批次仍需负责人一次明确范围/新预算，绑定本独立报告、准确 JAR/observer/disposition/APK、新 scope/release/config/registry/once 和受控采集记录方式；新鲜 M1 确认其他项目已释放及准确前置 v17/fixture1，否则停止，不同版重装/降级或换设备迁就。部署后 M2 核 app19/fixture3 及完整身份，再只执行 ordinarySenderCannotBindCodec。

该单项 PASS 须由实机准确 JUnit、scope/token、最终 instrumentation、真实不同签名 fixture 与 UID/Binder 内核拒绝以及原 PC/runner/线程/资源归还证据共同支持；目前均 NOT_RUN。不能将内核拒绝解释为内部方法执行，也不能以单项覆盖余下五项、全部 D1/P0、Flutter App 或独立 Kit。

本轮已停止，SDK/设备/占用/安装/产品测试/构建均 0。D1 NOT_PASSED、M0 NOT_STARTED、许可限制及既有其他余门保持。报告主动发送负责人，之后等待整批安排。

证据文件：`identity-source-artifact-audit.json`、四份独立 diff、`semantics-trace-budget-review.json`。本地分析两次断言修正仅涉及 CRLF 文本比较和 argv 索引取法，没有重跑候选自检、改源、改变原证据或掩盖候选失败。报告与证据索引发送前计算摘要，回执另存，发送后正文不改。
