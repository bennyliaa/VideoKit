# D1 E9 精确设备执行附录 V1.0

2026-10-18。本文是静态可审的后续边界，不是执行许可。当前设备/ADB/真实媒体/真实迁移/activation均未执行。负责人必须在tester整包静态接受后另行确定device与最终scope；本批不生成真实批准配置、token、registryID/migrationID或H_actor，也不复用已消费E3许可。

## 唯一候选与入口

目标只允许未来正式范围中的HA1Q6WXR，包名com.videokit.app与com.videokit.app.test，原应用UID10221，合同test UID10222必须在实际部署前核实一致。候选version11/D1-E9-PREPARE，原签名证书 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。

|APK|bytes|SHA-256|
|---|---:|---|
|app-debug|10643010|`4c09d1abed854555f16e277dbcda605c37c47c11cb4d55b9712676cc5bc6a287`|
|androidTest|2749765|`9f693e30babead370ff2f632242b4ebc033de58b867b3e2e6887ec5776ca3ca8`|

实际构建instrumentation组件为 `com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation`，不含默认AndroidJUnitRunner入口。精确选择参数：e9Case=legacyN2Migration，e9Batch=D1-E9-PREPARE-TABLET-20261018，e9Mode只能READ_ONLY_IDENTITY或REGISTERED_MIGRATION，e9Request为严格canonical identityRequest的URL-safe无padding Base64；禁止class及FD参数。

READ_ONLY_IDENTITY只采身份并在真实返回后互斥关闭写入口；即使再收到EXECUTE也拒绝。负责人如先派该只读诊断，须独立限定非迁移scope、采集transport、真实原返回及精确失败/只读finish；本包HostManager专用于正式REGISTERED_MIGRATION，不把只读结果写成commit authority。请求含bootKind明确选择KERNEL_BOOT_ID或SYSTEM_BOOT_COUNT；权限不可核验失败关闭，不回退V1或墙钟。当前没有可直接执行的真实request。

## 外部管理与正式迁移顺序

未来受信配置必须严格含kind=managerTrust、完整规范preparePlan及其精确SHA、授权引用、独立review引用、外部registry绝对路径、NEW或明确已知head、原已装完整app/test SHA/版本/role/ABI。plan包含原descriptor SHA、实际候选完整pair SHA、证书、UID、sourceReview及DEVICE_HA1Q6WXR。仅存在64位hex字符串不证明其被批准；负责人须保管实际批准输入及pin。

HostManager无参数只inspect。未来受管会话入口为 `--approved-session <实际受审配置文件> <实际配置SHA>`；这些是明确未填值，不是本轮命令。进入后只接canonical managerCommand：DEPLOY_PREPARE、LAUNCH、POLL、RESERVE、CONTROL、ARCHIVE_RETURN、CAPTURE_FINISH、CAPTURE_TERMINATION、SEAL_FINAL、INSPECT。LAUNCH带ordinal/attempt/handle/bootKind；RESERVE带predecessorIntent；CONTROL仅STATUS/EXECUTE_COMMIT/ACK_FINISH/STOP_DEPENDENCIES，并从原transport派生当前seq/state/handle。所有控制先记外部intent，未知回复不自动重发；每actor8请求、STATUS最多3。PC进程及reader必须保持至原命令真实返回，stdin丢失也不强杀设备原actor。

正式顺序：核已装精确pair/原签名/版本/UID/无相关活进程与未知owner → 经真实dispatch门install-r候选并复核 → 外部CREATE_NEW launch登记 → 原identity实际返回 → 外部identity/reserve force-close-readback BOUND → EXECUTE先预留commit → 等原操作和所有holder返回 → 精确returned外部归档 → ACK_FINISH匹配同hash和seq/state → 确认原instrumentation命令正常结束、原PID不在、唯一E9_FINAL_FINISH锚点及其后ActivityManager Force stopping/Killing finished inst → 独立最终审查。

正常失败已真实返回可归档并finish，但不得final。永久PENDING晚返只非合格；恢复actor2必须有原late-return+normal-finish或经审查的确切原代次termination证据。CAPTURE_TERMINATION读取独立平台采集并归档的规范probe，本包没有执行该采集；actor2 Android identity仍重新核旧代次确已不活。任何原UNKNOWN不因重新取锁、PID不存在、当前文件完整或管理器bool变成Java CLOSED。

新设备控制只允许M/actors下0001.intent、可选0002.intent、n2-v2.acceptance、n2-v2.commit，合计最多8448B/3目录；不覆盖/删除任何原文件，不动原107218、预算身份或R/S。外部20文件155648B/192KiB元数据+1MiB原日志，catalog实现cap16KiB（合同24KiB以内）。任何超界、额外文件、断head、torn内容或缺旧身份/回执立即隔离并报告负责人，不自动换scope/补请求/第三actor。

## 未来activation阶段

只有真实final接受并封存后，由负责人另派受审activationTrust配置（plan/pin/授权/review/registryPath/精确head）。`E9HostActivationSession`默认也只inspect；未来 `--approved-export` 只导出同final catalog固定policy源码，随后构建必要role/catalog/版本/入口差异的双APK，再由新的实际release文件绑定APK SHA、sourceReview、原签名和同head/catalog。未来 `--approved-deploy` 经同一实际dispatch gate部署，CREATE_NEW release先消耗该部署流程，未知安装不自动重试。当前不调用这两条路径；本地已验证SYNTHETIC_LOCAL输入在任何导出/设备调用之前被拒绝。

新host的产品测试还须走E9Runtime.observe，退休4869历史查询0仅适用于该固定catalog中的legacy例外；当前host必须真实持guard、核完整合法账本后缀、无pending、force/fsync/close全返。prepare即使完成迁移也不能运行正常四例；activation也不能写迁移。本批没有新正常四例、媒体导出、native fault、D1验收或M0启动。

不支持-d、卸载/clear/data restore、force-stop原未知actor、清账、换budget或手工绕过SHA门；拥有管理员权的人仍可绕过合作流程，本附录不宣称Android绝对阻止。旧runner/旧reader不会因device marker或外部撤销json自动懂新政策，必须经源审核兼容代码与完整SHA部署。
