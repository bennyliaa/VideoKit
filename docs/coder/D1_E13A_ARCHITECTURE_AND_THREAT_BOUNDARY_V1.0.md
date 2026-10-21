# D1 E13A 架构与威胁边界 V1.0

日期：2026-10-18。最小修复E13-F01/P1、E13-F02/P2。候选D1-20261018-E13A，v17/ACTIVATION/ABI1；真实已接受升级源仍是v15。旧E13 v16从未在本批安装，原冻结367项保持。

## P1：同一原连接的dispatcher生命周期

本机正式SDK Context.java 4206–4215明确false和SecurityException也需unbind；ContextImpl先getServiceDispatcher，再调用系统bind；unbind先forgetServiceDispatcher，再系统解绑。LoadedApk.doForget使后续排队连接不再交付，已开始的回调仍须实际退出。源码路径/hash和精确片段见evidence/sdk-binding-contract.json。这是SDK36.1静态契约，不冒称已实测API31。

一个小型共同E13BindingOwner用于实际SenderService和E13PermissionProbe的Context适配器，共用真实原ServiceConnection对象，非另立控制/安全/取消框架。owner在bind前进入强keeper；bindEntered、bindReturned、accepted、bindError独立，false/SE/其他已返回异常不会被当成“从未进入”。close请求可先到达，但bind仍在途时不解绑、不归还；原bind真正返回后才继续同原connection的一次unbind。

unbindEntered在实际调用前置位，unbindReturned及unbindSucceeded分别记录正常返回/抛出后的状态。无论accepted真假都执行原unbind；既已进入的解绑不再调用第二次。异常已返回不等成功ACK，资源仍未证并保同owner，调用在途也不归还。仅closeRequested、原bind实际返回、同原unbind正常返回及已进入回调全数返回同时成立，才resourcesReturned并移keeper。

回调在途计数与解绑分开：已开始回调未返时即使unbind已返也保owner；关闭后或解绑过程中的迟到回调拒绝接纳endpoint，返回记录保留。按SDKforget契约不重新bind/生成连接。主端还保留原fixture Binder及其远端resourcesReturned状态：远端解绑未证不能以本地binding已关替代，真实runner finish/onException继续拒绝结束。同scope/方法日志包含targetBinding、authorizedClient、fixtureClient的原状态，权限拒绝与资源归还分别输出。

九个有限本机分支直接执行这份生产owner：FALSE、SECURITY、OTHER_EXCEPTION、TRUE_CALLBACK、BIND_IN_FLIGHT、UNBIND_IN_FLIGHT、CALLBACK_IN_FLIGHT、LATE_CALLBACK、UNBIND_EXCEPTION。仅Context调用和平台调度用替身；异常解绑分支明确期待原keeper保留、不第二次unbind。它没有Android binding/FD，JVM自然结束不能作为Android关闭ACK；当前没有注入实际永久UNKNOWN或设备错误。

fixture仍是独立普通UID/不同签名Debug APK，只尝试固定non-exported codec组件；clearCallingIdentity后用自身身份。kernel bind拒绝不证明内部Binder鉴权，未拿到endpoint仍internalTransactAttempted=false。原授权host HELLO和source当前代真实open/read是不同正对照，原六方法/共享source keeper/聚合条件未改变。

## P2：显式写封装与默认严格只读

tools/package_delivery.py默认和verify分支只读已冻结metadata/hash/ZIP/JAR与原seal；--help及pack --help在参数解析阶段返回。只有显式pack才加载_write_package.py；后者自身也先检查明确pack参数，不能误传verify后写证据。核验不启动Gradle、JAR、候选自检、设备或媒体，不复制/改文件；结果打印stdout，外部调用者另存回执。

封印不自哈希；独立给定--seal-sha可固定外seal。核验逐不可变文件、完整ZIP成员集合与字节、host JAR类成员与字节以及旧冻结；原E13误调用的既有JAR x异常仅是打包入口误用，未登记功能FAIL。原E13 seal/367行本次再次全读核实不变，不重跑旧错误入口。

## 继承与残余

未改原AsyncReadBridge、LeaseRegistry、SourceGroup、CPU/编码/EOF/PTS、native/框架算法；不重跑未变source套件/native/历史signal。目标17、batch E13A、新e13a-activation-deployment.once是新候选的部署绑定，实际source仍精确15，原registry/账档不写。

48次PC操作/2MiB原分配不扩大。M1/M2/M3由tester既有34stat/18control pins落实为精确三个直接ADB argv/script，无Java wrapper/额外查询；仅脚本文本已准备，未执行。旧214483B/7R7S/0reserved与107218B前缀只是E11报告时点事实。

renderer/audio/source/Kit继续采用E13已审SUPPORTED_DESIGN_ONLY范围，参考冻结原文；显示/声音NOT_RUN、合法压缩音频→PCM BLOCKED，独立AAR/Fake/Flutter及全P0未完成。合作故障/受信签名代码边界不变，SHA不认证人类，同UID不等权限/RCE沙箱。D1 NOT_PASSED / M0 NOT_STARTED。
