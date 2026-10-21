# D1 E6A 架构及威胁边界 V1.0

2026-10-17。Java诊断所有权/归属/一次发布集中修复；native、封装、完整六帧/EOF/1000µs/画面及原资源门不改。

## F01：实际生产后置失败边界

E4CpuAdapter公开validate(Context,...)仍执行offMain/原timeline准入、原TrackedProvider及真实CpuTaskClient创建；平台适配器封装原verificationTimeline/start/awaitVerification(15000)/stopAndAwait(5000)/close、实际source归还检查及原retained verifier。随后进入同一package-private validate(ValidationOwner,...)完整生产工作流。该入口无测试模式判断，也没有可由Binder/Intent传入的Owner；外部公开入口固定真实平台适配器。

共享工作流顺序仍native→stop→close→digest→实际receipt/content，任何原第一错误保留，再尝试原收尾；首错phase保持，后续stop/close异常单列最多两份，原异常对象与cause不替换。stop false、stop throw或close未返回资格不完整时保留原verifier，不能因native OK构造成功结果。全部错误统一携带同一实际接收snapshot或NOT_COLLECTED；不会凭空补零。成功Verification只由原receipt严格证明构造。

PipelineValidationReceipt新增内部View适配，真实生产View仅转发原CpuTaskClient；证明体仍原verificationDone/orientation/death/source/slot/pendingCalls/stopPending/unresolvedWorkers/byte界/before-after摘要，以及真实PipelineRules.content、thumbnail长度/错误/帧映射/可辨识检查。测试通过有限平台View进入这个真实证明体，不以mock prove取代。接口均内部包级、没有新跨进程授权路径或产物READY豁免。

source.next同样共享实际所有权工作流，平台适配器保原真实解码/seek/像素/timebase/哈希/方向准入。创建后取消在已登记owner内拒绝并执行原收尾；坏timeline在已拥有validator时也必须收尾。source active/retained强保留原CPU对象；失败不会用替代close或重试UNKNOWN冒充归还。创建失败的原CpuTaskClient自身清理/隔离逻辑不变。

## F02：作用域与启动事实

E6AFailure包括scope、实际task或NOT_CREATED、role mode10/11、phase、原primary/cause、单列cleanup及实际snapshot引用。公开metadata只用本地安全短码/异常类型/固定字段，不泄露路径凭据；内部Throwable原对象仍保留。background里的E6_NATIVE_OK只说明native状态，不替代Java内容/收尾和session READY。

E4Session实际catch委托E6ADiagnosticState.failure，不再把任意含native的cause记到validator；SOURCE只填sourceNativeDiagnostic。每源frame成功也登记实际source task/snapshot；validator进入前严格NOT_STARTED，进入后尚无事实时start UNKNOWN，实际成功后本task/mode11/VERIFIED。CREATE/TIMELINE/BEFORE_READ是已知未进入native调用，明确start NOT_STARTED；其他ENTERED是该调用路径已进入，不能拿它当进程start ACK。全局session.first仍原compareAndSet，取消或更早全局错误不被模块背景替换；cleanupError原独立字段保持。

两个完整字段均通过原instrumentation HOST_DIAGNOSTICS白名单，实际最终app/test DEX有键。字段由有限模式/32hex task/phase、安全code/type、最多两cleanup与原有限native数值生成；保持原单字段1400/记录4096界。没有snapshot用NOT_COLLECTED，未启动用NOT_STARTED，不转成虚假零计数。

## F03：完整接收边界与原子性

原CpuTaskClient Binder最外层保原真实caller/task/epoch/revoked/parcel上限，分支再将真实caller/context/原parcel size/数值parse及CpuProtocol.end委托E6ADiagnosticInbox.receive。该生产方法自身再校验鉴权/size，随后创建同一E6NativeDiagnostic并检尾、stage与VERIFY帧数一致，最后AtomicReference.compareAndSet(null,d)。所有验证先于发布；错误首份不能占槽；只有第一份合格对象可发布，后续失败不覆盖。DTO仍不可变，接收器无清除/重置方法，getter及DONE/ERROR统一读首份。

原协议非法回调依然可触发业务失败/收尾；CAS空槽未被非法数据抢占不是业务继续许可。新增本机并发证据只证明同生产接收方法的内存发布/协议验证，不声称真实Android Binder线程调度已实测。

## 本机证明与未覆盖

20直接边界用例/112断言。F01真实validate/receipt内容和后置/收尾分支，F02真实next失败与实际session routing组件，F03完整receive（不是仅CAS helper）。16线程同时调用同一生产receive，1发布/15重复拒绝，第一对象保持；此前错PID/UID/task/epoch/size/revoked、非法字段、尾数据、阶段和帧数均不占槽。

平台start/stop/close/lifecycle、Context/Looper/Log由自有有限shim模拟；真实Android bind方法在shim中直接抛错，不能暗中伪造系统操作。生产纯规则及每个变化边界从E6A源重新编译，未改的Android支持类型只用既有E6 classes，未运行设备/JNI/真实Binder/媒体或导出件。单个模拟receipt/death事实不能对外充当实机验收；实际每host观察、真实FD/owner/slot/CPU死亡归还仍由原生产链取得。

E6Muxer和E4CodecSink、PipelineRules、guard/recovery/Admission/Lifecycle/Budget与相关native/schema保持字节。原2MiB输出/64MiB与8192readAt/六帧/1000us/完整EOF/thumb/内容/映射、60s/首次cancel30s/真实owner终局不变。无新native构建/依赖/权限/白名单；旧E6、旧FAIL/原N2 closeACKfalse、结算R/S0/53651消费均不动。
