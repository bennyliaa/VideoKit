# D1 E9B 交付 V1.0

候选 D1-20261018-E9B，目录 `docs/coder/d1e9b`，仅 PREPARE 静态与本机有限验证交付。负责人派单的 P1 原遍历所有权及全入口结束边界、P2 总 accept 前置额度已实现并集中验证；待独立 tester 审查。不能据此认定 D1 通过或设备准入。

## 变更和原对象

`E9Registry.Store.checkTotal` 把原 `Files.walk` 的 E4Owned 在 allocate 之前登记到同一个 Store；Store.returned 和监督者 pcClosed 都检查它。分配未返、迭代/读取失败、close 在途、Exception/Error/UNKNOWN 不会从登记中消失；只删除 CLOSED，UNKNOWN 不重关。healthy=false 仅禁止后续业务，不能充当关闭证明。

新增 `E9HostRegistry`，先把真实 Store 和 Registry 强引用交给原监督者，再初始化/打开注册表；统一 boundary 覆盖失败出口。HostManager 即使构造中失败、finally 清掉 authorityCallActive，也仍由独立 Store 引用持有资源。HostActivationSession 在配置打开、openKnownHead、approved-export、recordActivationRelease、后续 Processes 之前创建同一个监督者，后续不新建一套监督者。设备环境校验保留；本地夹具只向真实生产下层入口代入 SYNTHETIC_LOCAL，不伪造获批设备配置。

本机 accept 前保留额度，实际返回 Socket 后立即计数，已接收未处理也占额；歧义失败保守占额。总额 128 后停止调用 accept 并只尝试一次 listener close。实际 close/UNKNOWN 单独公开；原 Process、pipe、Store、remote 监督继续，不能换端口/重置扩额。达到额度后 TCP 状态与收尾入口不可用，隔离 ACK 明确标识 ACCEPT_BUDGET_EXHAUSTED；同 JVM 原非 daemon custodian 仍持有责任，不声称另有可用查询端点。

## 验证

24 组受影响有限检查全部通过，共 1294 个边界断言，另 12 个合成元数据夹具断言。真实本机目录流/Socket/Java ProcessBuilder、原生产 Store/监督者/共用入口边界参与。UNKNOWN 组在有限观察后由测试控制器终止**专用夹具 JVM**，此前确认原实际 child 均已返回；该动作不算 Java close ACK 或生产安全退出。长期不返语义只验证有限观察窗口，不冒称穷举或实际永久等待完成。

旧19/32套件、native、设备未重跑。E9A 已关闭 F01/F03/F04 的源文件及关键函数按字节继承，见 android-entry-inheritance；这不是新的 Android 运行证明。`compile-001` 是初始单组编译探测；`production-002` 为23组；`accept-failure-003` 只在枚举历史工具目录时准备失败、未编译执行；修正检查器的文件过滤后 `accept-failure-004` 单独通过新增第24组。新增只改测试，生产 class bytes 与002一致。002测试源码修改前的精确文件保存在 evidence，原日志不覆盖。

一次 `main-001` 离线 APK 构建通过（68 tasks，1m15s），无 repair、无下载、无 native 重编。最终输入快照 163 文件 SHA256 `e1e32550e4011d2d3fe0dd51c8ea19628a42010c53ccf7d9ea67e5a49b961bf0`。包含共享 Store 变更及版本13/D1-E9B-PREPARE，所以执行必要重建；测试 APK 恰与E9A按字节相同。未安装 APK。

|制品|字节|SHA256|
|---|---:|---|
|app-debug|10643006|`ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020`|
|androidTest|2749733|`2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`|
|生产 host JAR|259343|`4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707`|

两APK签名 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，生产 host JAR 158 classes，不含测试类，来源为002当前生产编译，004复核生产class字节一致。三个默认入口均 INSPECT_ONLY。SBOM 35 Maven 坐标/7 native 库继承，锁、库与 E9A 一致；FFmpeg8.0.3/Media3 1.9.3许可结论不变。源码ZIP含四文档/源码/原日志/差异/输入/制品/SBOM，ZIP外 e9b-freeze.json避免自包含哈希；冻结后只读验证回执和完整负责人报告另置docs/coder。

## 有限案例索引

|案例|断言|结束边界|
|---|---:|---|
|WALK_NORMAL|5|原资源已返|
|WALK_ALLOCATE|11|原资源已返|
|WALK_ALLOCATE_UNKNOWN|11|未证明归还；夹具有限收尾|
|WALK_READ_EXCEPTION|6|原资源已返|
|WALK_CLOSE_LATCH_EXCEPTION|12|原资源已返|
|WALK_CLOSE_LATCH_ERROR|12|原资源已返|
|WALK_CLOSE_UNKNOWN|11|未证明归还；夹具有限收尾|
|WALK_ITERATOR_UNKNOWN|11|未证明归还；夹具有限收尾|
|WALK_CLOSE_ERROR|11|未证明归还；夹具有限收尾|
|MANAGER_INIT_UNKNOWN|11|未证明归还；夹具有限收尾|
|MANAGER_OPEN_UNKNOWN|11|未证明归还；夹具有限收尾|
|ACTIVATION_OPEN_UNKNOWN|11|未证明归还；夹具有限收尾|
|ACTIVATION_FILE_UNKNOWN|11|未证明归还；夹具有限收尾|
|ACTIVATION_RELEASE_UNKNOWN|11|未证明归还；夹具有限收尾|
|EXPORT_SYNTHETIC_REJECTED|7|原资源已返|
|ACCEPT_SERIAL|139|原资源已返|
|ACCEPT_UNPROCESSED|143|原资源已返|
|ACCEPT_CONCURRENT|141|原资源已返|
|ACCEPT_LISTENER_UNKNOWN|141|未证明归还；夹具有限收尾|
|ACCEPT_LISTENER_UNKNOWN_BEFORE|141|未证明归还；夹具有限收尾|
|ACCEPT_LISTENER_UNKNOWN_PROCESS|145|未证明归还；夹具有限收尾|
|ACCEPT_PROCESS|142|原资源已返|
|ACCEPT_WALK|143|原资源已返|
|ACCEPT_EXCEPTION|7|未证明归还；夹具有限收尾|

证据入口：`evidence/targeted-check-results.json`、各 selfcheck-attempts 原 argv/stdout/stderr/平台状态、`source-derivation.json`、`host-binary-provenance.json`、`build-results.json`、`apk-audit.json`、`sbom-difference.json`、`external-readonly-verification.json`。历史E9A工具仅归档于reference/e9a-tools，不能用于本批构建或冻结。
