# D1 E13 架构与威胁边界 V1.0

日期：2026-10-18。唯一交付候选D1-20261018-E13，v16/ACTIVATION/ABI1。沿用合作故障/已审签名代码/受信本机执行者边界；SHA绑定字节，不认证人类、不引入新authority或远端撤销服务。同UID不等权限/RCE沙箱。

## F01：从真实已接受v15升版

新增E9DeploymentGate.deployE13Detached，复用原private deploy和E9HostDeployment原Process/pipe监督，源固定为E11接受报告SHA60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635中的v15 ACTIVATION精确pair，不再从registry.trust.plan的v14 PREPARE取升级源。目标必须v16/ACTIVATION/ABI1、原signer/UID10221/10222及无相关在途；源和目标app/test实际字节、包、签名、角色、ABI、版本都走原门。

新E13HostActivationSession只接受精确--approved-e13-deploy入口；原registry/catalog/head只读，配置绑定独立reviewed scope及新固定路径e13-activation-deployment.once，原E11已消费once不可当本批路径。仍用E11DeploymentOnce的CREATE_NEW/write/force/readback/原close门，失败/部分安装/UNKNOWN消费派发不重试。源/目标数据目录分别run-as stat，必须保持10221:6972和10222:4741；fixture只在精确包名确认不存在后按已审字节/不同signer安装一次，非产品companion。

scope明确绑定真实源接受报告、源pair、目标pair、fixture hash/signer、六方法、预算和独立sourceReview。模板不生成批准，当前未签发实际新scope、release或once；代码里的synthetic测试记录不用于设备授权。

## F02：实际source原owner与runner/PC结束

E13SourceGroup在runtime/bridge/open之前登记到静态强keeper，持同一AsyncReadBridge.Runtime、LeaseRegistry/generation、实际bridge与其原CloseTicket、consumer、原调用线程。没有镜像released计数。每consumer在同一生产source门校验身份后才可open/read；共享generation第一个consumer close只退其消费，最后一个close才retire整代。

只有原retired && consumers==0 && operations==0 && !closeFailed、原调用线程实际终止后，才可对原runtime做graceful shutdown；两原executor实际terminated后才移出keeper。新finishReturned不调用shutdownNow，不在仍在途时中断provider。原CPU调用原Runtime.close路径未被替换；E13直接source只用安全排空分支。原AsyncReadBridge.close本身只撤接纳/发取消，不能据它返回宣布全部资源关闭。

E13Instrumentation真正finish/onException同时检查E11既有生命周期、E13原source keeper和两份permission binding owner，PENDING/UNKNOWN拒绝super.finish并保留原对象。scope/case及原task/epoch/instance/generation/consumer/operation/failed-close身份进入原状态日志；取消响应与全部原返回有不同monotonic时间。30秒仅结果资格窗，原bridge每次await仍5000ms；不变成强制结束、kill或close证明。

E13HostCase复用E9PcSupervisor/OriginalAuthority：原Android runner的同scope/方法all-owner门通过、原am instrument自然返回、原stdout/pipe与原Process实际归还，才可能让原custodian退出。JUnit PASS另验；若JUnit失败但原资源已真返，可以自然关闭PC并保留FAIL，不故意把已知失败变永久未知。无合法原finish token或进程/资源未知，原PC authority不归还，不destroy/换进程/补finish。scope SHA是受信批次绑定，不将普通日志字符串当抵抗被攻陷同UID的认证。

本批仅可返回错误和可控fixture延迟，不主动制造永久UNKNOWN。若调度/系统异常使原操作未返，代码只能保管并拒结束，设备批次停止交负责人；没有新增Android强制恢复/撤FD/cleanup控制框架，也不宣称永久UNKNOWN设备恢复已实现。

## F03：同生产门的正反对照

SourceAdmission提取原CpuTaskClient的UID/PID/task/epoch等值检查，CpuTaskClient实际broker接线调用此共同谓词，保持原CPU_BROKER_IDENTITY错误。E13SourceGroup的实际consumer open/read同样调用它，并校验原实例。oldGeneration方法先真实当前代open/read成功，再分别旧task、epoch、instance在同门拒绝，原provider open/read增量0。它不是用无session全拒或HELLO冒充source正对照，也不宣称执行CPU解码。PID只是原端点一致性项，UID/原任务/代次共同约束；不是仅凭PID授权限。

普通UID负例是单独签名/包/UID的Debug SenderService：自身清除入站Binder调用身份后，以自己的普通UID绑定固定non-exported codec服务，报告实际SecurityException或bind false。授权host对同目标真实HELLO证明目标存在可访问；main独立核fixture包UID与不同签名。未取得codec Binder，明确internalTransactAttempted=false，不称内部onTransact跨UID实测。fixture只暴露固定只读负探针，无任意目标、路径、凭据、source或输出能力。原绑定连接在尝试前保管，远端/本地unbind未知均保原keeper并拒runner结束。

## 资源、框架与残余门

原Media3 1.9.3/受限FFmpeg8.0.3、7native和35Maven不扩；CPU/Sink/6帧/EOF/PTS规则不变。SourceGroup只是D1两个真实consumer/同源生命周期机制，不是全产品播放+显示+跟踪+编辑的source聚合已验收。host lease/file/fsync JNI、同UID数据权限、系统/vendor/全局OOM、J08–J11/真实声音显示、模型/样本权利及独立Kit仍OPEN/BLOCKED。普通绑定拒绝不关闭恶意FD持有/RCE模型。当前无设备、真实媒体、新输出或R/S。D1 NOT_PASSED / M0 NOT_STARTED。
