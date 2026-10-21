# D1 平板收尾后恢复批次交付

2026-10-20；候选 D1-20261020-RESUME01。结果：离线实现及有限自检完成，提交整包独立静态复审；设备阶段仍等待其他项目释放及新鲜准入。D1 NOT_PASSED / M0 NOT_STARTED。

本批准确引用平板报告 SHA256 5d85e965029c8f923ad4bdffa4e5471bfa8d5e4e6c033b23de27fae40f61e354：VideoKit OBSERVED_ALREADY_STOPPED，stopped=true、完整 processes/ps 未见相关进程，global instrumentation=0，本次强停0；不推定是谁或何时停止。负责人接受该事实结束补强停需求。LendManager 前台活动保持设备等待，不以本次观察替代未来 M1。

## 改动与行政证据

生产 Java 相对 E13F 仅四文件差异：

- E13GuardLocation：DISPOSITION_SHA 从 ABSENT 绑定 `7270e5c0208d2895394bbd1cd25508b239bbe7a711a40b3e8d2b3d59a37a265d`。
- E13HostActivationSession：scope 方法仅 ordinarySenderCannotBindCodec，预算字符串限定 process43/text3145728/output0。
- E13HostCase：请求方法必须等于经过 scope 校验的唯一方法，不能挑选其余五项。
- E13PendingGuard：现有持久 claim 在同 scope+method 下成为不可重入的单项 once；即使已有正常归还 marker，也拒绝重复进入。其他 claim 的原归还检查完整保留，不删除、修改或行政豁免任何现有 claim。

使用现有 canonical 十字段 typed disposition，TERMINATED_WITHOUT_RETURN / originalJavaReturn=false。A/K 两原 Java 外部终止、外层 PowerShell 自然返回分栏；B/H 独立 ADMINISTRATIVELY_QUARANTINED_UNKNOWN，K 原 Socket/reader ACK、预算 UNKNOWN 不退。caseEvidence / diagnosticDisposition / review / authorization 分别指向真实报告聚合、隔离记录、负责人的行政接受及本批派发记录。review 的含义是原行政收尾接受，新源码独立审查仍 PENDING，不混用。

原同代 custodian、原 authority、join、writer/reader/Socket 物理归还规则不改，未新增生命周期框架。disposition 仅保存在交付目录，尚未放入真实 custody root；本批从未读取该 root，不声称没有独立未结 claim。以后若命中具体未结 claim，停止并集中报具体差异，不自动行政结算。

## 工件与构建

新主机 JAR：`docs/coder/d1resume01/artifacts/resume01-host-tools.jar`，323124 B，SHA256 `03a27c74061b740a879e2dfec3341b0b07172c68bf374b9231c20e42a46566c5`。183 个生产 class，逐项绑定源码及实际测试过的 class 字节，无测试类入包；生产源码只编译一次，之后未重编。

零 Android/Gradle/native 构建，复用已冻 app19/test/fixture3：

| 文件 | SHA256 |
|---|---|
| app-debug.apk | 938d70fbc70fd9bfdbef4ac37d2d83a66d7260e88e8c3c62bb2d022ea427908e |
| app-debug-androidTest.apk | 4227751bf659fca9efc8a8d2d32d5ce754bcbef9033e15a0c92ab7537dca9dd7 |
| fixture-debug.apk | a8c86650ae756f682fb2cbaaa896424974893282026525266e7b1912a8dd1867 |

observer 沿用原 F 脚本字节，新 binding 显式绑定其摘要、新 JAR、行政记录及原 APK。新依赖为零，许可范围无变化。

## 有限自检

本地直接调用真实 guard 的显式测试根重载，覆盖外部终止/false 接受、错误摘要/身份/schema/review摘要/真假配对拒绝、其他 scope 未结 claim 阻断、同 scope 在 pending 和有归还 marker 时均拒绝重入；scope 及公开 case 入口拒绝其余五方法和旧预算。没有真实 custody root 访问，也未创建 PC supervisor 或设备子进程。

真实 E9HostDeployment 方法使用明确的本地脚本化端口输出，逐条导出35项实际 argv，涵盖前后数据身份、APK探测、安装前后身份、两安装及 fixture 前后检查。它验证的是命令展开与数量，不是 Android 安装/内核/真实 metadata 正确性。原首次测试样本漏写现有 output0 后缀导致 scope 拒绝；失败与原样本均保存。修正测试样本后仅编译测试类一次，重跑有限自检通过；无生产重编或隐藏失败。详见 `d1resume01/evidence/build-001/`。

## 准确执行计划及限制

静态计划限定唯一 ordinarySenderCannotBindCodec，部署/用例入口、instrumentation 子命令、M1/M2 全量采集 argv 和观察器 pins 已列出。部署子调用轨迹中 APK 名称/摘要及输出属于明确本地替身；正式展开必须以 binding 的三个真实 APK 和批准 scope/release 为准。

43操作=1部署主机+35 SDK子调用+1case主机+1instrumentation+3 M1+2 M2，零占用复试。总3MiB文本/4MiB归档的提案逐项计入1949696B原始/重复输出、786432B记录控制文本和409600B未分配不可使用额度。相对历史六法2MiB，明确考虑两次完整512KiB占用采集和归档元数据，不冒充继承批准；必须独立复审、负责人接受新预算后才可正式派设备批次。若设备已非准确 v17/fixture1 前置，则现有部署不能照跑，必须停止报告，不允许同版重装/降级或换设备迁就计划。

未来 M1/M2 要检查完整输出、各子命令状态、精确包/版本/签名/UID/数据身份与全局占用。无 instrumentation 不等于其他项目空闲。第一异常/超时/占用/UNKNOWN 即停，不以55秒资格到期杀原进程；不自动重试，不追加其他五项。

`release/templates/` 含明确无效的 PENDING 字段，无法通过 digest/身份校验；actualScope/release/once/sourceReview 仍 null，未签发、未创建或消费任何执行许可。独立 PASS 后仍需负责人正式设备派发、新鲜 M1、完整 registry/config/scope/release/pin 绑定和部署后 M2。不得直接运行模板。

## 封包与阶段边界

源码差异、冻结来源、行政证据快照、原 APK、新 JAR、编译/自检原始结果、预算与草案整包封存；ZIP 为 `docs/coder/D1-20261020-RESUME01-source.zip`，外 seal 为 `docs/coder/d1resume01/evidence/resume01-freeze.json`。只读校验回执在 ZIP 外，避免自引用。工具默认 verify，help/verify 不写文件、不启动进程或网络；仅显式 pack 一次生成包。

本轮无设备、SDK、占用、旧会话/handle/claim 查询，无处置、部署或产品测试。旧冻结 F 全部成员、来源 ZIP 与 APK 已核未改，旧 FAIL/ACK/UNKNOWN/账本/once 保留。正式 Flutter App、独立 Kit、全部 P0 和原定开源许可不变。单项未来 PASS 也不关闭 D1 其他输入/格式/渲染音频/Sink/跟踪/资源隔离/阈值余门，不自动进入 M0。
