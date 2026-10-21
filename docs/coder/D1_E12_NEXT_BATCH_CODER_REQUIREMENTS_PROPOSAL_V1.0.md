# D1 下一完整批次 coder需求提案 V1.0

来源：E12审计建议；暂称E13，PROPOSAL_ONLY，未正式派发。不能凭本文启动实现、构建或设备测试。

目标：一次可审候选补齐普通发送者与授权输入实际生命周期的紧邻缺口，复用E11真实catalog/当前观察、原监督器与资源owner机制，不再建设许可/迁移诊断框架。

1. 在新目录/新候选保留E11完整冻结，新增精确白名单方法；权限负例覆盖无权第三方普通UID绑定exported=false服务的实际系统拒绝，同已授权host进行零媒体或最小授权source正对照。跨UID拒绝与同UID旧task/epoch/instance拒绝分栏；不同签名负例fixture仅Debug实验，不是产品必须另装companion。普通外部无法取得Binder时如实报告绑定边界，禁止冒称已执行内部onTransact。对直接Binder身份校验的单元/受控替身检查独立标注，不能伪作跨UID真机调用。
2. 以现有Provider/ReadHandle接口实现最小双消费者、迟到open/read/cancel/close可返回路径；证明源聚合释放的必要条件及引用归还，不提前造全部公共API/TestKit。未完成聚合不得发SourceReleased；凭据/完整路径与Browser业务类型不得进入接口，输入只读，输出只宿主临时Sink。
3. 沿SESSION/CPU/LIFE既有门做受控、可返回的错误与资源保留验证，精确记录原owner、调用进入/返回、引用、callback和permit。源码/本机检查与Android实际分栏。永久卡住/close-unproven仍UNKNOWN，不能用恢复替身的成功覆盖原资源。没有已有可审持续保管/观察/停止方案时，永久UNKNOWN实机项BLOCKED，不启动、不通过、不force-stop、不补close；将缺口作为完整交付的一部分交负责人裁定。
4. 同一交付给出source→raw frame→renderer/PCM→audio owner的具体接口差距图及Kit可提取依赖清单：真实Surface/AudioTrack未执行标NOT_RUN，合法PCM解码缺口标BLOCKED；列宿主残余JNI/权限、source消费者聚合、服务命名/host包依赖和Manifest。禁止扩FFmpeg音频/新模型/新后端，禁止声称同UID沙箱或独立AAR已完成。决定具体可复用的Media3/平台薄适配后，显示/声音功能另交完整批次建议。
5. 只集中一次Android构建，确因失败修正才记录必要补构建；不重建native、不下载依赖。新runner只选正式批准方法，旧E11编码normal作为已接受来源，若改动其共有实现才提出精确必要回归，不整类重跑。候选只交一次源码/pins/依赖锁/APK/ZIP/外置seal及完整结果/缺陷矩阵。

资源/真机：正式派单前给方法数、来源/字节、process/log/时间/输出上限及UNKNOWN保管出口；此提案不伪造已批准数值。原budget730a73e1-50e1-4198-a515-047104f00e31保持214483B/7R7S/0reserved接受基线，旧前缀/产物/fence/oldCloseACKfalse不动；默认权限/源实验不新建媒体输出，不重做迁移或清账。确需新输出的具体预算由正式派单列出，现有总4MiB/单2MiB/128任务不扩大。用户已有项目常规真机授权，其他项目占用时等待，不抢占。

完成标准：完整新增功能与本机/设备证据按正式派单交付，明确所有NOT_RUN/BLOCKED；源拒绝/取消/归还无虚报，历史FAIL不覆盖，E11封印逐字节保持。提案完成不自动关闭Android永久UNKNOWN、renderer/audio、独立Kit或全部D1门；tester独立审查后由负责人决定下一步。


## 建议正式派单的六个精确入口与预算

以下为待负责人采纳的具体上限，不是已批准执行许可；方法名是新候选提案，不声称当前已有。

| 提议方法 | 最小完整行为 | 数据与结果 |
|---|---|---|
| ordinarySenderCannotBindCodec | 单个独立普通UID Debug负例fixture发起一次服务绑定，并核实际系统拒绝；授权host HELLO正对照 | 不取得源/FD、不触发编码；实际绑定返回与目标无任务分栏 |
| authorizedHostSourceReadAndClose | 原Provider接口授权本地实验source，正常open/read/close | 4096B独立生成非媒体字节；不读test_media或旧device媒体；不是NAS/解码证据 |
| oldGenerationNeverOpensSource | 同授权host旧task/epoch/instance由生产校验拒绝 | 原provider opens/reads/bytes均0，不以规则替身当真实跨UID证据 |
| twoConsumersHoldSourceUntilLastReturn | 同一只读实验source两个实际consumer，先返一个后另一个 | 两份原句柄与consumer身份；第一个关闭后另一个仍可读；最终才释放聚合源 |
| cancelLateOpenRetainsOriginalOwner | 受控Provider的原open迟到，取消先响应，原open确返后关闭其原句柄 | 进入/返回/原句柄close分别记；全程不把取消响应当SourceReleased |
| lateReadAndCloseFailureDoNotReleaseEarly | 原read在取消后返回被拒采纳；一次明确可返回close失败按既有允许规则处理 | 只验证可返回错误的实际账本/保留，原资源未返则保留UNKNOWN；不作永久native挂起 |

建议一次集中Gradle调用生成app/test及负例fixture；新候选精确版本/身份由正式派单锁定，不在本提案伪造已签发版本。必要安装只允许正式审过的pair升级各一次和独立fixture一次，未成功或身份不符停止；不重装/降级/clear。实验source总大小≤4096B，总读取≤64KiB，open≤8、close尝试≤16且不得超过原实现允许次数，无编码/validator任务、新输出/READY/R/S均0。每入口总观察窗≤30秒，其中取消响应/回收分别计时，不把30秒当强制终止保证；所有原资源未知即停止后继，不自动续下一项。

全批六入口各一次，宿主/负例fixture均由既有受管PC监督，不新增控制协议。process操作建议总≤48，日志/文本累计≤2MiB；只能采证明这些方法必需的metadata与原输出，不扫设备/媒体或全量重hash。达到预算或实际UNKNOWN停止并保留，不补次数/延时/换UUID。永久UNKNOWN/quarantine、native故障、真实OOM、重启与长期观察方法数量0。若实现发现此预算或原机制不足，集中交具体差距给负责人修订派单，不能自行扩范围。
