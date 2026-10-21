# D1 平板收尾后恢复批次测试需求草案

日期：2026-10-20；版本：V1.0；状态：正式离线复审需求 / DEVICE_HOLD。对应同目录 CODER_REQUIREMENTS；本轮来源候选完成冻结后整包交审，当前不构成设备测试、部署或许可消费授权。

TABLET_CLOSEOUT_CONT 已由负责人接受为 OBSERVED_ALREADY_STOPPED（本次强停0），正式启动 coder 离线批次；LendManager 前台活动仍阻断设备阶段。tester 仅审查冻结候选，不测浮动源码、不改产品源、不与 coder 并发使用设备/Gradle。

## 第一阶段：整包独立离线审查

1. 核对新来源快照、最小 diff、构建记录和准确工件摘要；三个 Android APK 复用时必须保持 E13F app19/fixture3 字节和签名。旧 E13F 来源审查 PASS 只适用于其冻结来源，新策略需独立审查。
2. 校验行政记录 canonical 十字段、8192B 上限、原 scope/serial/packages 与四个证据摘要。TERMINATED_WITHOUT_RETURN/false 必须保留，不接受外层 ORIGINAL_RETURNED 覆盖原 Java 状态。
3. 分别追溯 A/K、平板、B/H，检查旧 FAIL/UNKNOWN/ACK/预算及 once 没有被重写。平板一次包级处置不证明 test/fixture 包或原 Android 内部 ACK 正常返回。
4. 新 source pin、JAR、observer、scope、release、once、来源审查指针必须互相绑定；原 ABSENT/null 不可当作正式材料。不得重用 K 诊断来源或已消费的历史许可。
5. 确认全局 disposition 没有旁路后续 pending claim。若实际未结 claim 需新增行政分支，必须具体另审，不删标记/active.pointer、不补原归还。
6. 有限本地自检应覆盖错误摘要、错误身份、终止/false、正常返回/true 的类型配对与 claim 阻断等本次差异；不新造诊断框架、不重跑与改动无关的全部历史检查。
7. 检查准确单方法选择、argv、逐操作及文本/归档预算。新提案43操作=1部署入口+35部署子调用+1case入口+1instrumentation+3 M1+2 M2，零占用重试；总3MiB文本/4MiB归档。相对旧2MiB的明确差异为两次完整512KiB采集及归档元数据/重复输出，不隐含已获新额度。核算详见新候选 exact-budget.json 与脚本化真实端口35项轨迹；实际设备准入仍需负责人另派。未闭合或依赖旧六项总额则 BLOCKED。

完整离线报告一次性交负责人，列 PASS/FAIL/BLOCKED 和具体缺陷。离线 PASS 不自动触发设备执行。

## 第二阶段：负责人正式派发后的准确单项 T07

前提：平板报告已接受；新来源独立 PASS；明确单次范围/预算/许可；新鲜完整 M1 确认准确设备 HA1Q6WXR、API/user/包身份、签名/UID/数据及全局无其他项目占用。历史 v17/fixture1 不当作新鲜读数。是否部署由该身份决定；部署后 M2 绑定 app19/fixture3 与原工件，不能跳过检查。

唯一推荐首项 `ordinarySenderCannotBindCodec`，完整类为 `com.videokit.spike.e4.E13DeviceTests`。只接受准确单方法选择；不因选择成功就运行余下五项。首个超时、占用、UNKNOWN、解绑异常或失败即停止，保留同代原 owner 与全部原始有界输出，不循环、不强杀换 PASS、不借旧预算。

验证真实不同签名 fixture、Android UID/Binder 内核拒绝、正确 case/scope/token、单方法 JUnit/最终 instrumentation 状态与 PC/runner/线程/资源物理归还。逐项区分阶段日志、内核拒绝、内部方法执行、最终结果及归还证据；任何缺失不得推测 PASS。

集中报告至少包含：候选和每个实际工件摘要、精确执行材料/一次许可消费、M1/M2、占用判定、原始输出引用、逐项结果、原 owner 与资源账目、失败首因、剩余阻断。一次 T07 PASS 不代表全部生命周期、D1、Flutter App、独立 Kit 或全部 P0 通过，不自动进入 M0/其他五方法。

未涉及的 readAt/格式轨道/渲染音频/Sink/跟踪/资源隔离/许可及 API 阈值余门沿用原 D1 测试矩阵，不能以本单项覆盖。正式开发完成后由负责人确定后续整批，当前只提交草案。
