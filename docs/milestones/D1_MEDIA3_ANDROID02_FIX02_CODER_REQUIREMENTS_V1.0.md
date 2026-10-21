# MEDIA3_ANDROID02_FIX02 开发要求 V1.0

2026-10-21；负责人正式派D1_MEDIA3_ANDROID02_FIX02完整五项集中修复批。依据独立报告51b9181446d747bc3030cb2c13ce3d8fa1f1d5c9089267418a3f40f122bee8fa，结论OFFLINE_ARTIFACTS_VERIFIED_WITH_5_SOURCE_BLOCKERS_ANDROID_NOT_RUN；双APK/86类/依赖strict/原新client-daemon退出有限证据保持，不以其代功能。五项均静态源码P2，Android复现0，不夸真实泄漏/实际超限。

新目录docs/coder/d1media3-android02-fix02，从完整冻结recovery01复制准确源；旧包/seal/失败/UNKNOWN不改。一个完整scopeAll十case功能簇及真实Media3提取capture→mux→Sink→fMP4重开不删、样本/许可/flags已修政策保持。一次整批设计实现自检后集中构建，不逐问题交接。

R01-B01 回执：用不可变requestedMethod判batch；正常、失败、中断/pending均导出已完成case快照/完成数/失败case及当前phase，保留原在途owner/首错UNKNOWN。不重执行补历史，不读取worker正写集合；快照按同锁/不可变已完成值，receipt全输出1MiB及每status262144B，超界明确阻塞，不静默丢既有历史或只lastjson冒全。
R01-B02 计量：在同原路径独立累计SDK requested/native attempted/native actual、copy/hash/parse/seek/reopen/controlled各phase及全case总账，不从actual/readCalls猜requested；native短读min3与SDK原count分列。输入scope8MiB/outputattempt16MiB/块64KiB/不退款/不换factory重置，全phase/全case预留守门一致。明确source租约峰值不等实际native FD峰值，需要FD原登记/实际分配/关闭证据或标未证，不能共用假计数。分层计量不新开读取/补做动作。
R01-B03 时间：completedNano/bodyReturned必须位于同原worker所有受控cleanup及同步E13ReturnEvents返回之后的最后受控点；同原marker仍非OS退出，外部join和finalizer/platform finish独立。真实回调尾段跨deadline不得早marker升级；准时完成晚观察与真迟返按单调合同分开，等号迟返sticky，无kill/interrupt。
R01-B04 FD：原RawDescriptor owner/holder须在Os.open调用前登记并强持有，Os.open返回后到FileOutputStream包装之间已有原FD可保管；wrapper构造/flush/sync/close每个原步骤及别名所有权明确，异常/不确定不能丢rawFD或新建句柄冒close。单原native关闭至多一次，wrapper/raw别名不能双close，构造未证/close UNKNOWN强保管并阻止resourcesReturned，不靠finally计数0推原返。真实Android关闭语义如无契约证据明确API_UNPROVEN，不运行OOM/平台崩溃注入。
R01-B05 Muxer：原成熟Media3 muxer构造前登记Job keeper/分配意图，创建成功真实对象全程由原Job/owner保管，addTrack/sample/EOS/close异常均纳入原生命周期。成功EOS/close与失败清理按原对象/同原线程/一次close准入；原close未返/抛错unknown不得再close，不以外Sink abort/FD返回替muxer原close/线程门。构造结果不明保留allocation UNKNOWN，无替换muxer/重导出。resourcesReturned/finish gate必须纳入原muxer，避免局部变量丢对象。可以调整SDK薄适配/Job/source/owner，不改Media3成熟库或引JCodec/新框架入产品。

集中必要非媒体实际自检：固定已有JDK/真实生产Java可执行子集和最小typed内存/FD模拟端口，只测试政策/ledger/原owner状态及真实future-worker-callback顺序，模拟不冒Android Os/真实muxer效果。覆盖五项正常/失败/pending/late返/unknown不二close/回执快照/跨case预算、callback尾段先后与muxer-return gate。单JVM256m/整批30秒/有限payload64KiB/原finally正常放门join/Popen自然返，禁止重放旧ContainerPendingOrderCheck/无变化大套件/反射改状态/强停或故意永久挂起。原Android/native测试仍NOT_RUN。

构建：沿恢复成功固定JDK/Gradle已有镜像、独立新Gradle home、--offline --no-daemon strict/metadata/原锁/17坐标/Media31.9.3，不改策略/ACL/防火墙/联网。一个集中app/test构建窗口，先全部五项与源码类型自检完再一次必要构建；若确定编译错误允许集中修完最多一次必要重构建（总2），传输再失败停止不盲试。预算/原client及single-use daemon自然返回合同沿recovery，不能--stop/kill旧daemon35512/48945/17257。

完整交付五项实现+实际受控证据矩阵/准确Android未证/全部scopeAll源码-编译-双APK签名DEX/实际双闭包strict与fixture/新操作预算/所有前后差异及旧seal/原构建返回/sealZIP后主动报负责人。tester独立整包复审后再准确实机新scope，当前无设备/ADB/占用/生成/编码解码播放，不签READY COMMIT/隔离验证。D1未过M0未启。
