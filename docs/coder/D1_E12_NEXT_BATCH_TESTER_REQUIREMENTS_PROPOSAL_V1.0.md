# D1 下一完整批次 tester需求提案 V1.0

来源：E12；暂称E13，PROPOSAL_ONLY，须负责人另行正式派发后才能执行。

先审核新候选唯一身份、源码/依赖/服务Manifest/方法白名单和E11不可变封印；独立复核方法数/字节/process/log/时间预算及UNKNOWN保管出口，未定则不启动。只验证完整“普通发送者与授权source资源生命周期”簇，不做MP4/AVI/迁移整类重跑。

| 项 | 真正独立成功条件 | 不得推定 |
|---|---|---|
| 普通第三方UID拒绝 | 实际系统身份/绑定返回、目标服务未开启任务或源；同授权host正对照 | exported=false静态事实不冒充实际拒绝；无Binder endpoint不能声称内部onTransact被调用 |
| 同UID旧代/错task/instance | 精确原实现拒绝、无源读取/输出/错误permit释放 | 不当作抵御同UID恶意RCE或授权凭证来源认证 |
| 授权source双消费者 | 同源两个真实consumer身份/代次；一个结束另一个仍可用；最终都返才SourceReleased | 一个CPU死亡/取消响应不能等全源释放；不得误释放他槽 |
| 迟到open/read与取消 | UI/取消响应与原操作真实返回分别记；迟到结果不被采用，资源各自归还 | 超时不等close或允许重试；可返回错误不充native故障 |
| UNKNOWN有限门 | 按实际源码/可返回检查证明保留与不READY/不复用；原owner审证 | 本机替身不等Android未知实测；永久UNKNOWN无合法保管出口则BLOCKED，禁止启动旧quarantine再强杀收尾 |
| renderer/audio/source及Kit差距材料 | 按实际源码核每一owner/UID/JNI/依赖/Manifest、source聚合/合法PCM/回退方案 | 材料审SUPPORTED不等显示声音PASS或AAR可分发 |

只有正式派单批准的可正常收尾方法可进行设备测试。常规项目真机授权已给，无需重复索取；先确认占用，其他项目在用则稍后。源码不由tester改动；若发现功能缺陷集中反馈新修复批次。任何PENDING/UNKNOWN保持原资源/证据，不重复派发、换UUID、清账、kill/force-stop或把新对象归还当旧对象关闭。

预算与原档：默认不产生新媒体输出；保持接受的214483B/7R7S/0reserved和旧107218B前缀，fence及oldCloseACK=false不改。无实际在线重读则只说“接受报告时点”。四方法以外回归必须有共有代码变化与正式范围理由。独立报告一次整包提交，保留历史C13系统signal0 FAIL、C14 NOT_RUN和ordinary UNKNOWN。D1 NOT_PASSED / M0 NOT_STARTED，不自行启动后续阶段。


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
