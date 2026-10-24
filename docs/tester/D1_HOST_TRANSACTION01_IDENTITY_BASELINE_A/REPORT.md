# HOST_TRANSACTION01_IDENTITY_BASELINE_A 静态报告

2026-10-24。**STATIC_BASELINE_MAPPED / ORACLES_PLANNED_NOT_RUN。** 旧冻结SDK是可替换宿主能力端口，不是强制JDK fileKey或硬链接实现；同grant、真实物理对象、内容/结构与COMMIT权威是四个不同义务，均不能互相替代。本A不审新候选、不签产品PASS。

## 来源与静态保全

Sink05 accepted seal `ec7e5e9a8f38d2d1fe531592117f5db0a6d3481cd3ff89536d985f9dae173d96`核同；只对本A选定13份原源码/既有check逐项核seal内准确path/bytes/SHA，均一致，不重读828项或产物/依赖。连同设计、原独立报告、当前单和补充环境证据共24项356654B小副本，来源完整hash见source-inventory.json。未读取`docs/coder/d1-host-transaction01`新冻结或此前浮动代码，也未检视其新失败包。

旧INPUT_SINK05独立报告仅有限离线PASS，真实宿主COMMIT/平台FD/codec/muxer当时NOT_RUN，不能按现在的实现目标回写历史。设计文件内旧暂停按原日期范围解释，当前准确新派单有效；设计建议不冒已有方法/ABI或实现证明。

## 身份层与端口边界

|层次|旧实际入口/门|能证明与不能证明|
|---|---|---|
|逻辑grant|HostOutput.opaqueTask/capabilities；TemporaryOutput构造捕获同task|task形式/能力与单原授权快照；不是物理FD标识|
|源身份/代次|HostInputFactory→E13SourceGroup.Identity(uid,pid,task,epoch,instance)→SourceAdmission/LeaseRegistry|原身份tuple/实例/generation及consumer/operation归还；不自动证明磁盘文件未被路径替换|
|物理I/O|原AsyncReadBridge.Provider/Handle、HostOutput.writerOriginalsReturned/reopenReadOnly|宿主负责原endpoint/写者/描述符与授权重开关系；SDK接口不暴露JDK fileKey或通用物理fileId|
|内容/结构|TemporaryOutput.verifyAndValidate/HostOutput.Validator|原读回字节/长度/SHA及同task格式结果；同bytes不代同物理对象，SHA不代真实容器合格|
|READY/COMMIT|原SinkCoordinator不可逆终态；HostOutput.Commit.originalOutcome(task,token)|READY与同原COMMIT结果分开；原响应完成与物理归还再分开|

本A中的“SourceLease”按既定租约语义映射到旧E13SourceGroup、LeaseRegistry及HostInputFactory，选定旧接口没有名为SourceLease的公开类或physicalIdentity平台接口。不能据此断言全仓没有该类；若后续要求另一个已冻结同名SourceLease实现，应先提供准确path/seal，不能自行造接口补缺。

TemporaryOutput不接路径/凭据，不读BasicFileAttributes，不调用Files.createLink。HostOutput的Validator、Commit、reopenReadOnly原Provider与Originals属于可替换宿主端口；宿主可在既有能力的内部维持准确grant→原文件对象/版本/写者→授权只读端点映射。此处“可替换”不是运行中随意换原validator/commit任务或重开陌生文件，不能为测试新增第二资源权威。

JDK fileKey允许为null；硬链接createLink是可选文件系统操作，故不可从语言平台名断言本机可用或全SDK必须依赖它们。[JDK fileKey合同](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/attribute/BasicFileAttributes.html#fileKey())、[JDK createLink合同](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html#createLink(java.nio.file.Path,java.nio.file.Path))。

若具体宿主适配器只能用fileKey维持其已承诺物理身份，而当前null或获取失败，则必须稳定拒绝/能力不足，无READY/COMMIT或假发布；不能回退path/hash/size/mtime求绿。非null key仍需与准确文件系统/原打开对象及同grant关联，路径属性快照本身不消除换路径/TOCTOU风险。本A没有新增“通过任意新身份端口”的豁免：平台原生H/FD身份如需调用须已有合同能力、准确来源和后续范围批准，当前不新增Native。

同理，具体发布适配器若要求硬链接但不支持，应在准入前拒绝，或按同原已发生调用的实际结果保留已知失败/UNKNOWN。不能只看UnsupportedOperationException就推断未发布、偷换copy覆盖或换目标。硬链接也不是普遍COMMIT语义；若原宿主合法实现不用硬链接，应按其准确发布/同grant/可查询权威验收，不强加某JDK实现路径。

## 原门的准确时点

1. 构造时快照原task/能力；非法task走OUTPUT_GRANT_INVALID，能力不满足走OUTPUT_CAPABILITY_UNSUPPORTED，资源owner按原准入。fileKey缺失不是旧接口单独错误码，不能凭设计发明IDENTITY_*公共码；新候选具体稳定拒绝与错误映射留待其准确源码。
2. producer channel.close是逻辑停写，不是原Writer物理close；finishWriter须flush/close原ACK、host.writerOriginalsReturned与此前原任务归还。PENDING/UNKNOWN不再close求绿。
3. verifyAndValidate只能在原写者归还后调用原host.reopenReadOnly；原读回provider以原SourceGroup/Registry跟踪，验证读租约须关闭排空。validatorOriginal对象一旦进入不能换另一个，旧错误OUTPUT_VALIDATOR_IDENTITY。Validation实际字段只有task/bytes/sha256/kind/structurallyValid，没有强物理fileId；同grant物理锚由宿主证明，不能从字段形状单独签真实宿主成功。HostResultCheck的ORIGINAL_TASK_SNAPSHOT还明确：构造后opaqueTask访问器改值不重定向已捕获原grant，原任务应继续；不能把访问器标签变化一概当真实grant替换。
4. 顺序输出SHA和原写入摘要比较；随机输出以原读回extent/SHA交validator，不能把该hash当预先正确最终内容的证明。真实容器/格式、AV同步等须真实验证，旧HOST_ISOLATED_FORMAT_V1受控回执不冒Android效果。
5. markReady须validated、原writer/相关原任务归还、无首错/cancel，并经原仲裁门；READY token不代业务提交。commitByExplicitHost是额外显式宿主动作，绑定task/token、只调用一次并保留原Commit authority；不能因READY自动发布。
6. HostOutput.Commit.originalOutcome缺省UNKNOWN，只读、不得发新RPC；CONFIRMED_COMMITTED/CONFIRMED_NOT_APPLIED须同原task/token实际权威。SinkCoordinator.HostState没有COMMITTED，不能把其READY QUERY当提交证明。原COMMIT stage仍pending时，宿主可先记录已提交，但SDK物理归还仍等待同stage/observer/原worker；未知不重放/退费/取消成ABORTED。
7. LeaseRegistry.released须retired、consumer/operation归零且无failedClose；E13还等原caller/runtime退出。原单consumer close、单会话SourceReleased、零业务counter或取消请求都不足以安全移动。宿主真实移动仅限获准自己临时源，并在原所有consumer/read/close/generation归还后由宿主决定，SDK无删除/移动源权。

## 后续有限验收oracle

ACCEPTANCE_ORACLE.md列21个有限正常/拒绝/未知/晚回/同grant替换/多consumer/平台边界项，全部PLANNED_NOT_RUN。正常项须本机实际临时文件写闭/授权重开/验证/发布/读取；换相同bytes物理对象的负例不能仅看SHA；原API不暴露的字段由实际冻结宿主内部原记录证明，缺证BLOCKED。

本机有限宿主可测与平台效果分栏：当前能力若不支持物理身份/发布则拒绝项可验，不把正常项全拒当集成成功；替换受控端口可验证协议状态但不能冒真实文件身份或Android效果。Windows fileKey/hardlink能力、本批真实临时文件集成、编译/JVM执行均未做；真实FD/fsync/codec/muxer、隔离媒体、进程崩溃恢复均NOT_RUN。是否另做完整B由负责人核新冻结包后准确派发，不由A自动启动。

## 补充环境证据（准确引用，不是本A运行）

负责人独立新范围LIVE03_NATIVE_PERMISSION_CHECK01原probe源SHA `68cccbb80c399cab959321bae97f79172df448386132ae30d436d1e0047ace1f`已核；其原approval/once/result小副本纳reference。原结果记录一次AF2/class3/Reserved0尺寸调用return122/required972、tableAllocated0、SDK/device0、originalFunctionReturned=true。负责人消息说明工具require_escalated经自动审核允许、tool250d04 exit0；本A仅将其与原记录关联，不声称自行取得该工具执行记录或重测。

该新受审核执行边界能得到一次正常尺寸响应，不是重试LIVE03旧scope，也不识别5037/server/平板；更不证明JDK fileKey、硬链接、Java权限或真实宿主发布可用。它缩小“所有环境均不能调用”的推断范围，但不把不同调用环境的差别冒唯一根因。当前不据此新增权限或测试。

## 预算、保全与回交

首读前同调用取Stopwatch tick，timing-end准确核600秒界；具名静态资料总读预留4MiB<16MiB（含少量官方文档与重复校验），输出manifest列实际大小且≤1MiB。已核13选定旧源码，不将引用原828项验收冒本A全量复核；无新产物JAR/APK读取或执行。

本A新Native/TCP/CIM/SDK/设备/编译/Gradle/Git/辅助程序/权限变化均0；不读新coder候选、不动旧证据/once/UNKNOWN。本报告与oracle一次集中交负责人，非逐问题派修复、非候选B；D1未过/M0未启，主阶段/设计许可/P0保持。
