# D1 E9B 完整交付报告 V1.0

负责人「VideoKit项目助理」：E9B 已按正式派单完成集中实现、24组受影响有限检查、一次必要离线双APK构建、四文档、原日志/最终输入/差异/host JAR来源/SBOM、源码ZIP及ZIP外seal和冻结后只读验证。现在一次性交接独立 tester 审查。P1/P2 为 CODER_IMPLEMENTED_PENDING_INDEPENDENT_REVIEW；不自行关闭独立审查门。

交付根目录：D:/CodexProjects/VideoKit/docs/coder/d1e9b
完整报告：D:/CodexProjects/VideoKit/docs/coder/D1_E9B_HANDOFF_REPORT_V1.0.md
四文档：
- docs/coder/D1_E9B_DELIVERY_V1.0.md
- docs/coder/D1_E9B_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md
- docs/coder/D1_E9B_REMAINING_GATE_REVIEW_V1.0.md
- docs/coder/D1_E9B_DEVICE_EXECUTION_APPENDIX_V1.0.md
正式需求已先落 docs/milestones/D1_E9B_CODER_REQUIREMENTS_V1.0.md、D1_E9B_TESTER_REQUIREMENTS_V1.0.md，并收入reference；未启用子代理。

一、P1 原注册表资源和入口边界
Store.checkTotal 的实际 Files.walk E4Owned 在 allocate 前登记进同一长期 Store，returned/pcClosed 覆盖原walk。分配未返、迭代/read异常、close在途、Exception/Error/UNKNOWN均保留原holder；只有实际CLOSED才退休，不用healthy=false代替归还，不二次close未知对象。
新增E9HostRegistry先把真实Store和Registry强引用交给原LIVE监督者，再调用注册表IO；同一个boundary覆盖主入口异常出口。HostManager初始化失败和authorityCallActive finally释放也不能丢Store。HostActivationSession在openKnownHead/approved-export/recordActivationRelease前创建同一监督者，后续Processes复用它。
本地测试使用真实生产Store、manager/activation下层入口和双方实际使用的共同boundary，代入SYNTHETIC_LOCAL元数据；没有绕过CLI设备环境门或伪造DEVICE获批配置。实际获批设备CLI NOT_RUN。

二、P2 原端口实际accept总上限
原accepted holder与名额先登记再accept，实际Socket返回立即占额，早于处理；已接受未处理也计入128。明确SocketTimeout未接入可释放在途保留，歧义失败保守占一额并停止继续接入。累计不清零、不换端口。
128后停止实际accept，listener只尝试一次真实close，CLOSED/UNKNOWN单独公开并参与pcClosed；原Process/pipe/Store/remote继续由原non-daemon custodian持有。
明确限制：额度耗尽后原TCP状态/CLEANUP通道不可用，隔离ACK标ACCEPT_BUDGET_EXHAUSTED；同JVM原custodian保留不代表另有可用端口，不声称无限查询/收尾能力。监听器close未知也不accept129+。TCP握手/排队不当作实际accept。

三、受影响验证
24组PASS_FINITE_LOCAL_SCOPE，1294边界断言，另12合成元数据夹具断言：
WALK_NORMAL / WALK_ALLOCATE / WALK_ALLOCATE_UNKNOWN / WALK_READ_EXCEPTION / WALK_CLOSE_LATCH_EXCEPTION / WALK_CLOSE_LATCH_ERROR / WALK_CLOSE_UNKNOWN / WALK_ITERATOR_UNKNOWN / WALK_CLOSE_ERROR；
MANAGER_INIT_UNKNOWN / MANAGER_OPEN_UNKNOWN / ACTIVATION_OPEN_UNKNOWN / ACTIVATION_FILE_UNKNOWN / ACTIVATION_RELEASE_UNKNOWN / EXPORT_SYNTHETIC_REJECTED；
ACCEPT_SERIAL / ACCEPT_UNPROCESSED / ACCEPT_CONCURRENT / ACCEPT_LISTENER_UNKNOWN / ACCEPT_LISTENER_UNKNOWN_BEFORE / ACCEPT_LISTENER_UNKNOWN_PROCESS / ACCEPT_PROCESS / ACCEPT_WALK / ACCEPT_EXCEPTION。
原真实目录流、回环Socket、Java ProcessBuilder以及原production对象参与；实际child退出/管道归还与walk原close返回后才允许结束，listener未知即便child已返也不能pcClosed。
UNKNOWN组仅有限观察：原监督者拒绝生产安全退出，originalCloseAck=false/productionExitAllowed=false；测试控制器确认无仍活原child后只收尾专用夹具JVM，此动作不计关闭证明。永久不返只验证有限窗口持有语义，不冒称无限时间实测。
evidence/targeted-check-results.json、selfcheck-attempts各原argv/stdout/stderr/platform状态和fixture-teardown收据完整。
compile-001初始单组探测；production-002为23组；accept-failure-003在枚举新增历史工具目录时准备失败，未编译执行；过滤为文件后accept-failure-004单组通过第24组。增加只改测试，004与002所有生产class字节一致；002修改前测试源码精确保留。
旧19/32/native未机械重跑；E9A F01/F03/F04关键源及函数按字节继承，原5秒decoder/Process/wait/reader/pipe体、E9HostDeployment、E9PcClient、grant撤销逻辑均保留。android-entry-inheritance.json明确是继承既有有限本机证据，不是新Android运行证明。已签新测试APK与E9A字节相同。

四、构建/制品/来源
163最终Android构建输入，final-build-inputs.json SHA256 e1e32550e4011d2d3fe0dd51c8ea19628a42010c53ccf7d9ea67e5a49b961bf0。
共享Store输入变化及版本13/D1-E9B-PREPARE使一次必要离线构建成立；main-001通过，68 tasks，1m15s；无repair/下载/native重编。原完整gradle.log与输入pin保留。
制品目录 docs/coder/d1e9b/artifacts/D1-20261018-E9B/final：
- app-debug.apk 10643006B SHA256 ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020
- app-debug-androidTest.apk 2749733B SHA256 2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b
- e9b-host-tools.jar 259343B SHA256 4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707
两APK原证书SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f，包名/role/ABI/manifest/16KiB对齐/7库审计PASS，未安装。
host JAR 158生产classes，不含测试类，来源为002已测编译，004逐class复核；三个默认入口实际运行均INSPECT_ONLY。
35 Maven坐标及7 native库/锁与E9A一致，SBOM差异为空；FFmpeg8.0.3/Media3 1.9.3，许可P0不变。
继承runner/非等待命令协议批标签仍为D1-E9A-PREPARE-TABLET-20261018，默认inspect旧批文字不是APK版本，附录已明确。APK真实版本以签名审计为准。

五、冻结/只读验证
源码ZIP docs/coder/D1-20261018-E9B-source.zip：
24208160B，SHA256 8c5952d929aa40edd17fd7c37dbdba69c6c49e4212da12103c6175506aa075ae。
ZIP外seal docs/coder/d1e9b/evidence/e9b-freeze.json：
83970B，SHA256 6f8c1ffffa6bff17da48b7067594d33980c443ff03a7c547e917f0814add2c92。
本批402 immutable（401 ZIP项+外部ZIP本身），独立重新运行只读verify，ZIP逐项/磁盘/大小/SHA均PASS。
包外回执 docs/coder/D1_E9B_READONLY_VERIFICATION_V1.0.json。
再次只读核验旧E9A733/E91045/E7A200/E8A42均不变；旧seal精确pin也不变。冻结后未修改本批封存文件。

六、未授权执行和剩余门
本批零ADB/设备/真实媒体读写/实际迁移/ABORT或预算重置/真实token/catalog/H_actor/activation；无activation构建。E3许可已消耗不复用。
原3R/3S、107218 consumed/0reserved、预算/fence/0B输出/档案、writer attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f、PID4869、UID10221、oldCloseACK=false均不变且不回填；此处是继承旧证据，没有新设备读取。
合作式威胁边界、Framework/独立Kit/Flutter、48资源/严格6帧/full EOF/1000us、FFmpeg许可P0保持。D1 NOT_PASSED，M0 NOT_STARTED，E6B-OBS-F01长期准入OPEN。
请组织本批独立静态/本机证据审查；本次交接不触发设备或真实执行，也不自行关闭P1/P2正式审查。
