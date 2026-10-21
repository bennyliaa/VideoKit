# D1 E2F 包装判定与封存证据重评独立复审报告 V1.0

日期：2026-10-17。角色：VideoKit tester。依据：E2F 正式测试/开发需求及负责人冻结交接。

**结论：E2F 离线判定修复及本次只读重评复审通过，新增阻断项0。E2E-F01在新离线判定范围内闭合；建议负责人有限采信原E2E完整场景、采样资源、输出和原收尾事实。** 原E2E最终FAIL、G exit2、工具exit1、160条原执行断言及已消费许可均保持；本结论不追认原批PASS，不增加actual尝试或通过数，也不提供新执行入口授权。

## 1. 冻结、只读复核与活动范围

| 项目 | 核验结果 |
|---|---|
| E2F freeze SHA256 | `1a73391a12f9473f661a5e62204218d5a875031f064bb12af262529c4e866dee` |
| E2F-source.zip SHA256 | `a7c09e34a5ccf6a3c980299a6fb0484792ca6496bc52b3bc08f73160ed72c4a5` |
| 集合 | 79源码/98不可变条目，逐长度/hash、ZIP精确成员及成员hash一致 |
| 原生产绑定 | E2C修后32源码＋5配置、10原产物、原r-helper字节一致；未编译 |
| 离线证据 | 452条开发离线断言、175个负例，核源码及原记录，不重跑负例 |
| tester执行 | 已审只读verify一次、reevaluate只读重算一次、自有静态归档审计 |
| 新actual/OS/G/J/R/媒体/构建/ADB | 全部0；无新预约、fixture或执行许可，无在途任务 |

只读verify在外部expected seal约束下PASS；其SOURCE合并读取260,535,062 B/277次≤256MiB/8192次。只读重算结果与开发封存重评JSON完全一致，completion/resources均accepted，scope=EVIDENCE_REEVALUATION、decision=SUPPORTED_ORIGINAL_TOOL_FACTS。重算原结果读取851,746 B/148文件≤16MiB/1024，原源码完整性读取52,989,816 B/91次≤256MiB/8192；64KiB块、路径/reparse限制保持。

新包fixture0，日志/证据含seal143,649 B≤4MiB；没有把原输出复制成新运行fixture。tester证据见 [独立封存审计](D:/CodexProjects/VideoKit/docs/tester/D1_E2F_EVIDENCE/independent-package-audit.json) 和 [只读重算结果](D:/CodexProjects/VideoKit/docs/tester/D1_E2F_EVIDENCE/readonly-recomputed.json)。

## 2. F01修复核验

旧E2E driver及其错误计数分支作为历史冻结保留。新 [e2f_wrapper.evaluate_bound_bundle](D:/CodexProjects/VideoKit/docs/coder/d1e2f/tools/e2f_wrapper.py:7) 是可实际执行的离线判定入口，AND聚合原封存身份、完成证据、资源/输出/退出及历史FAIL保留门槛；不是示意补丁，也不是单独把61改为62。

完成模块分别检查：

- PF恰有一次且首条，原16个control、2个data、query/时间/完成字段符合批准记录。
- 61场景精确ID集合、唯一性及批准顺序，P10-D/P10-C末尾；逐行control/data/query/时限及原160断言跨回执一致，原usage与PF/场景/GC总账一致。
- 原global每N/D槽的ADMITTED/终结阶段、kind、resultDigest与批准预期拒绝一致；并发重试竞态允许原批准的结果组合，不把错误DONE无条件当成功。
- P08/P09的WAITING_COMPLETION不视为实际返回；另查原cell归档的native_done/gated/released/notification_done/notifier_quiescent、discarded且未交付、callback实际返回和对应拒绝结果。资源模块进一步查原source operation done/nativeReturned。
- GC/n01..n31按原顺序实际DONE，n32必须同时有原短回执的flush/fsync/close已返回、remainingResources=0。盘上READY_TO_CLOSE及preclose的PENDING_RETURN_CHANNEL只能证明意图。

具体见 [完成判定](D:/CodexProjects/VideoKit/docs/coder/d1e2f/tools/completion_evaluation.py:246)、[WAITING返回核验](D:/CodexProjects/VideoKit/docs/coder/d1e2f/tools/completion_evaluation.py:162) 和 [GC分层](D:/CodexProjects/VideoKit/docs/coder/d1e2f/tools/completion_evaluation.py:225)。

负例覆盖缺行、相同62条中的重复/乱序/替换/额外、PF缺失/未完、control/query/data/time/原断言不符、GC缺DONE/错误顺序/n32仅意图、WAITING未排空、原FAIL改写、资源绝对值/原基线增量超限或UNKNOWN、worker未join、输出篡改/遗漏/越界/额外及原身份/hash变化。除封存hash拒绝外，另有语义原因断言：例如一致修改G峰至224虽低于256但超过原159+64，仍由增量门槛拒绝；worker未join/observer close UNKNOWN/metadata未知等亦检查具体原因。没有仅靠改坏hash冒称全部语义负例覆盖。

本轮只审读原452条检查记录与实现，未重新执行负例；452是离线断言数，与原452个控制预算、160条实际断言各自独立。F01闭合仅指新离线判定已正确表达本批完成语义，**未改旧实际runner，也未验证未来actual入口与新判定的集成**。

## 3. 原证据锚点与可有限采信的事实

三项原输入及tester原报告hash均未改变：

| 原输入 | SHA256 |
|---|---|
| E2E seal | `aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a` |
| 原result-manifest | `baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea` |
| 原preclose | `702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032` |
| tester E2E报告 | `bb1042940d9c6376bf019c73d95c7001a6887feddc998fe834cffd968c65a2d3` |

原90项不可变文件及146输出逐hash绑定。原父PID39108/creation134366511032212370、G PID40980/creation134366511035829924、J40896/R31648与原creation/owner串联，预约/launch/claim/preclose/短回执/原工具回执一致。重评使用原实际输出为输入，未用tester摘要替代底层事实；tester独立审计与原工具回执仅作交叉佐证。

建议负责人采信的限定事实：

1. 原PF＋全部61场景的完成checkpoint和原GC32槽事实，62为checkpoint数、61为场景数；160条原执行断言、原preclose PASS和最终wrapper FAIL同时保留。
2. 原G PF前、J/R原HELLO基线未重置；五个实际采样周期资源未超原界：G句柄159→峰204、线程5→峰12；J句柄266→峰266，R503→峰505；WS/private均在各原绝对/增量界内。托管峰23/媒体5/buffer1，cell累计64/归档64/active0/retained0/峰1；没有新采样替代旧数据。
3. 原146输出精确集合、10个输出的独立预期字节及L/C/Z自有模式一致；32任务/61个实际snapshot shard经header/digest、有界解压、最高有效seq选取，原任务/批次/角色和预算交叉一致。
4. 原N351＋query83新/18重放=452，input请求1,573,492 B/59次、validation128 B、32记录、10目标、output信用655360 B。存量metadata峰664,677 B与累计覆盖写6,431,845 B分列；准备＋执行metadata812,811 B、fixture135,244 B符合原界。
5. 原global最终93,440 B=event92,902＋metrics538。原回执event92,828是在n32最终意图事件前取值，差74 B保留原时点，不篡改计数使其表面相等。
6. 原J/R实际exit0、两Hub worker实际join、source/private结果实际排空、observer18开18关且无UNKNOWN、原GC/n32日志关闭返回、原G exit2及父process handle实际关闭，支持原无在途结论。不能只靠G退出推断其余资源释放。

以上与tester此前E2E独立字节/资源审计一致。本次不是第二次运行；原完整批次通过0、新actual尝试0/通过0。

## 4. 证据能力边界

- **逐query时长缺失。** 原.q没有每次duration。可采信的是原冻结Flow.query内0.1秒guard、Flow.finish与行时限全部返回支持“该guard未触发”；不能补造每query实测耗时。
- **逐周期duration/PID未单独落盘。** compact metric只有相对毫秒与数值，内存列为ceilKiB。结合原身份链、原冻结observer的身份检查、永久STOP锁存、最终OBSERVED/reasons空/finished、原raw-byte基线/峰及最大gap/末次duration，可采信原采样guard未触发；不能从这些行重构每周期精确byte/duration/PID，也不能声称连续OS峰。
- **IO pool未单独序列化join布尔。** 原Cleanup.finish在pending Future检查通过后实际执行原IO shutdown(wait=True)，随后才返回GC/n32关闭见证。结合原源码完整性、原资源与owner退出事实支持收尾已返回；不能凭空增加独立IO线程join回执。
- **时长口径分开。** checkpoint elapsed总和约4.984秒不是完整运行耗时；原工具调用约8.53秒支持外200秒界未触发。新完成模块明确不单独证明full runtime duration。
- 固定身份、原160断言和原hash约束适用于这一次封存证据；新模块并非已验证的任意未来批次通用判定器。对未来入口接入、授权和运行能力不能从离线通过推断。

代码及新文档均如实标明这些边界。未发现依靠补造字段、把UNKNOWN算成功或删除旧FAIL取得结论的问题。

## 5. 后续准入与最终状态

本次可提交负责人裁定上述有限工具事实采信；无需为修正历史计数自行补跑。若后续派发新actual批次，应先冻结并复审新入口、判定集成、批次身份/一次性许可及其适用ID，保持fresh≥2GiB、G原PF前/JR原HELLO基线、全部资源/IO/日志/时限与UNKNOWN保留规则；原E2E许可不退款不复用。

若转真实媒体，必须另有明确任务/输入与输出根授权，证明当前内容/版本及原打开对象身份，执行对应完整准入核验。当前只用小型自有文件，没有验证实际>2GiB媒体窗口、产品持久化/namespace、真实设备或端到端业务。五产品变体仍NOT_RUN_DURABILITY_UNPROVEN；tool READY/OS_DATA_SYNC_ACK不能代替产品OutputToken/COMMIT。

本轮新增阻断0，F01在新离线判定范围内闭合，建议有限采信，最终裁定交负责人。原E2E整批FAIL/exit/许可与旧G369/+209、R519 FAIL保持。host JNI BLOCKED、Kit/Flutter/AAR/Android/licensing P0、C14原限制及平板功能执行0保持，**D1 NOT_PASSED、M0 NOT_STARTED**。本轮无在途任务，不自行派发下一批；报告及回执主动提交负责人。
