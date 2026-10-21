# D1 E1 有限本机harness实现开发需求 V1.0

2026-10-16。负责人全文审阅D1_R4_REVIEW_REPORT_V1.0.md，采纳18项材料认可及R3-R01闭合意见，正式批准有限本机工具实现/本机编译自检，未批准真实媒体实验、设备测试、产品实现或M0。依据R2源/Sink方案、R3 close/writer契约与61分支、R4操作清单；以其明确覆盖关系解释冲突。

## 整批范围

在docs/coder/d1e1独立目录实现G/S/O controller与J Java helper、R .NET helper，复用已定真实HostFixtures/ReadHandle思路但不可编辑C14。独立模块实现源reservation/seal/版本/operation/ticket、close disposition/安全retry、grant/delivery/take/claim/逐descriptor及READY/abort仲裁、有限journal/query恢复；公共API候选只在工具adapter，不修改正式Kit API。实现61行manifest与PF16/GC32的机器可读冻结清单、逐层预算、有限事件/计数、原进程实例与退出证明、独立reference/Windows guard/真实DuplicateHandle绑定及只读恢复路径。不能用memory provider/mock dup/noop sync冒充真实backend。

仅已有运行时和仓库依赖，先查实际JDK/.NET/编译器可用性；不下载新SDK/组件/模型或联网补环境。所需工具不可用时明确缺口并实现可完成部分，不用替代平台假PASS。可以编译这些工具；先集中实现多项，再一次主编译/自检，必要修复重编不禁止。不得Gradle/ADB、读取test_media媒体字节、启动PF或完整实验、创建正式run目录。已有测试fixture可用自建有界合成字节在独立自检目录，标明只证明逻辑/绑定，不能记真实媒体/61分支通过；合成临时产物总≤2MiB，日志≤4MiB，禁止真实native crash或全局压力。

## 实现门禁

所有副作用前先预留行/任务/全局额度，保持452已分配控制（总544）、101query、媒体请求1573522B/59调用（硬4MiB/256）、10目标/32记录、写655360B/验证262144B、文件峰值3178496B（硬4MiB）、180秒与既有句柄/缓冲上限。未分配余量不授权增加步骤；元数据累计写入与文件峰值分开。真实需要额外操作/工具绑定不兼容须报告差异，不隐藏RPC或减断言。

close UNKNOWN不重试、已关闭只确认、最多三次具安全资格attempt；不得用closed布尔/裸整数证明资源。writer首次grant及重放不可写、唯一delivery/owning cell，确认未知abort-only，逐份A/B/transport归还。预检失败不启动后续；S17最后未知由原helper实际退出及父引用另证，不伪造close成功；GC/n32最终记录后关闭通过原返回通道见证。时间到停止接纳/等待，不声称强行中断内核IO。

最小有价值自检：状态机并发/重放/迟到、close三disposition与retry耗尽、唯一writer交付/epoch仲裁、预算先预留/停止、journal损坏/回复丢失及版本隔离。用合成数据验证实际平台绑定时明确事实范围；不能仅断言日志字符串。自检不启动授权媒体实验。

## 整包交付

交docs/coder/D1_E1_DELIVERY_V1.0.md，docs/coder/D1_E1_IMPLEMENTATION_BOUNDARY_V1.0.md、D1_E1_EXECUTION_APPENDIX_V1.0.md，以及d1e1源码/编译命令/版本/机器manifest/自检证据/源码与产物SHA清单、只读完整性校验脚本。给61分支→实际代码入口及未实现/平台不支持映射；源ZIP与产物冻结，所有执行入口默认不自动运行。附真实版本保证、dup、持久性与时限仍待实验的限制和最小启动命令/停止处理。自检全部结束、无helper/构建任务在途后一次主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774，不自行派tester或运行实验。

C14/R1–R4及原样本只读不变；正式Flutter/独立Kit/框架许可/全P0与历史FAIL保持，宿主JNI仍BLOCKED。工具不构成Windows Kit产品开发、NAS或Android验证。D1未通过/M0未启动。

## 部分交付续作安排（2026-10-16）

负责人已审阅D1_E1_DELIVERY与IMPLEMENTATION_BOUNDARY，部分包不满足完整交接，暂不派tester。coder继续同一E1全部范围，集中完成边界§2五项代码缺口，不以映射/NOT_RUN替代实现。已冻结d1e1只读，续作d1e1b与D1_E1B_*三文档，最终完整包包含全部依赖源码/原包关系；续批合成fixture/日志仍2MiB/4MiB并单列实耗。其他授权及真实媒体禁行不变。五项完成自检冻结后一次整包交测。
