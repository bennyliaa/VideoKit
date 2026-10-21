# D1 E13F 实现契约 V1.0

2026-10-18；最小范围扩展现有owner/archive/supervisor，无新增通用生命周期框架。

## F01 同claim真实原返

E13HostCase、E13HostActivationSession与E9HostActivationSession的deploy分支，在创建同一supervisor后、任何原child前follow同一E13PendingGuard。export分支无claim，不改。移除人工originalReturned(boolean)接口及同步finally结算。静态OWNERS强持guard，guard强持samePC与非daemon责任线程；join同一PC custodian，不靠可能丢失的通知/定时器。follow只能一次；在join前/后/并发close均不漏返。原PCterminated要求线程已实际停止、listener已返且LIVE已退；Operation还要求原starter/reader实际终止join、原pipe/decoder/authority及archive全部真实归还。

唯一结算attempt：CREATE_NEW临时marker，E4Owned持有原FileChannel，写全/force/同handle读回/长度比对、原close真实返回，再atomic move为claim.original-returned。内容绑定claim及其SHA、samePC UUID/PID、pcThreadJoined=true。任何失败保留同guard/PC/原marker对象和责任线程，保持跨scope拒绝，无重试/二close/补ACK。marker是原PC终止证明，不声称发布marker的责任线程在发布前自身已退出；发布后无新增IO。partialclaim及失败marker均封锁，词法close无归还语义。

## F02 日志与完成分离

request/fail只在owner monitor内保存首结果、失败及唤醒数据。唯一worker在锁外先启动；之后stage只记录有限ring并非阻塞offer。一个daemon诊断线程在所有owner/Stages monitor外调用平台sink，异常计数且不重试，sink未返只占一个在途引用；最多48引用队列，沿用48事件/500 ASCII字符/24576字节上限含footer预留。丢日志和sink UNKNOWN不是finish或原资源ACK，诊断线程不拥有完成请求。保持原第一个payload/code、失败只降资格、唯一非主finalizer、原UNKNOWN不finish。完成owner worker本来的daemon属性不改，日志worker也不是资源替代owner。

## F03 原writer返回

writer终于完成文件调用后仅写writerBodyReturned并调用原ReturnEvents；即使通知未返也仍在OWNERS。resourcesReturned拒绝原writer自己调用，并在外部观察同Thread非alive后join，写writerThreadReturned，逐个原文件returned后才退OWNERS。archive-facts是writer内提前快照，可显示线程未返；不是完整归还ACK。通知异常会记archiveFailed，物理归还与成功资格分别判断。上层pcClosed/claim都受此物理屏障限制。

## 替身与交付边界

最终public-008运行真实公开入口/guard/PC/archive类，影子仅固定本地guard根/处置pin与本地child命令runtime。测试用LOCAL child合成instrument文本不构成Android/产品PASS。失败marker子测试仅把本地责任线程改daemon以有限JVM自然退出；原失败对象/线程在断言时仍被保管，生产责任线程非daemon且无限保管。部署测试首SDK调用由一个本地JVM替代，其后metadata格式有意不模拟完整设备；证明准入及归还链，不是部署成功。没有真实ADB。FCompletionCheck直接调用生产request/fail，sink扣住/抛错均与原worker完成断言分离；不是只看E9类锁。

源码策略根固定、pin ABSENT，不提供环境变量/命令行绕过。D1 NOT_PASSED / M0 NOT_STARTED；原实际卡点 NOT_UNIQUELY_DETERMINED。原v17主任务仅最后观测PENDING/UNKNOWN，本轮未查询；丢失诊断独立LOST_DIAGNOSTIC_OWNER_UNKNOWN。候选app19/fixture3未安装，真实Android/Binder/UID/Looper/monitor、kernel行为和T07均NOT_RUN。源码处置pin ABSENT，scope/release/once/sourceReview均未签发；旧资格/预算不继承。用户持续测试授权已具备，当前无设备操作源于原任务未决。
