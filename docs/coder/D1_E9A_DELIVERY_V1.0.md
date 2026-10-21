# D1 E9A 集中修复交付 V1.0

2026-10-18。依据E9独立复审2项P1、2项P2的集中派单，E9A已实现四项修复并形成静态复审候选。E9的NEEDS_FIX/NOT_SUPPORTED_FOR_DEVICE_MIGRATION结论尚未被tester复核解除；本报告不自行授设备、迁移或activation许可。

工程 `D:/CodexProjects/VideoKit/docs/coder/d1e9a`，versionCode12 / D1-E9A-PREPARE。旧E9全部1045项、E7A200项和E8A42项只读核对，未改旧冻结文件。四文档位于 `D:/CodexProjects/VideoKit/docs/coder/D1_E9A_*_V1.0.md`；最终ZIP与外置seal由e9a_package.py生成，seal不放入自身ZIP，不预填自身摘要。

## 四项对应修复

|缺陷|实现|直接证据|
|---|---|---|
|F01/P1|真实am instrument -r非等待；启动client归还不代表actor归还。完整状态通过DUMP保护的独立有界ordered broadcast，POLL实际消耗STATUS；不依赖watcher/sendStatus。首次状态不用猜stateSeq；缺失STATUS保守扣额度；只读模式可查询并安全收尾|TRANSPORT/STATUS_GAP/IDENTITY_CLEANUP/REMOTE，最终runner源码/DEX|
|F02/P1|实际ProcessBuilder、3条pipe、reader、wait/解码和主程序所有出口有统一原owner；静态强持有及非daemon原custodian。EOF/错误时原对象和registry authority仍在原JVM，给出可识别handle/PID/本机端口与实际隔离ACK。原资源未返不能JVM自动退出|真实manager JVM+child、EOF/reader异常/输出界/console错误/close在途/UNKNOWN；只读查询实际可用|
|F03/P2|每控制原响应任务独立5秒绝对资格，包含启动、原client/pipe/等待及帧解码和身份校验，不共用55秒、不加1秒join、不重置；晚返永久PENDING，intent已发即消耗且EXECUTE/ACK不重发|CONTROL5/DECODE_DEADLINE/LATE_VERDICT/NO_REPLAY|
|F04/P2|每次observe在类锁前先撤销旧grant并领新epoch；used等早拒也撤销。旧在途调用不能晚发grant；准入检查与发布同步；Runtime失败也先撤销|GRANT/CONCURRENT_GRANT；最终新APK类的runtime失败后置断言|

## 构建、身份与来源

一次集中offline主双APK构建main-001通过，无APK repair、设备任务、依赖下载或native重编。Android源确有状态入口/phase校验变化，故没有拿旧E9 APK冒充新包；最后语义帧验证为纯PC工具差异，单独定向自检及主机JAR重新封存，APK输入保持不变。

|APK|bytes|SHA-256|
|---|---:|---|
|app-debug|10643010|`1edb820faea79cf87d261555adbd397f32c6796447ace127bd39cb756e10c841`|
|androidTest|2749733|`2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b`|

证书SHA-256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。最终构建输入 `06fc16bd7e27f766d30fc2b57810c0952df56aaf59011c4d93b0f3b0aee87d0b`，共163项。签名、manifest、实际默认runner、DEX及16KiB对齐审计通过。7个native与35个锁定依赖继承E9，FFmpeg8.0.3/Media3 1.9.3及许可状态不变。原预算/严格六帧/完整EOF/1000us、独立Kit/Flutter与其他P0不改。

实际可用PC工具JAR：`D:/CodexProjects/VideoKit/docs/coder/d1e9a/artifacts/D1-20261018-E9A/final/e9a-host-tools.jar`，255014B，SHA-256 `709fa796ed59ce6394b25f75bc69391099f7a4d398cafbd79cef91ef257d17e4`。从已经定向编译验证的生产class打包，没有重编native/新依赖/新签名根；155个生产class，不含测试类。相对final-pc-007，148个共享/原生命周期class字节核对一致；最终帧验证差异有frame-validation-008输入和直接断言。默认三个入口均只inspect，无设备调用。

## 验证与明确未执行范围

19组最终映射，21次最终验证调用（19组集中验证+2组纯PC帧验证补测），279断言，其中新增边界205、共享实际夹具不变量74。直接运行生产ProcessBuilder/原pipe/reader/console/监督者和真实本机Java子进程；元数据部分调用共享生产registry/run/observer。未机械重跑旧32组或native套件。最终新Gradle Android类另有6个SDK桩公共入口和1个Runtime失败撤销旧grant序列通过，不冒称Android运行。

全部原始argv、输入、stdout/stderr、真实子进程边界文件/状态和失败尝试保留。首次沙箱阻止Socket.connect，原监督者按设计存活；仅失败合成夹具另存无close ACK的清理记录。随后正常本机权限下验证。Windows conhost.exe被早期夹具误计为未退出任务子进程，修正夹具识别后复验；不改生产原返回门。CLOSE_UNKNOWN有限验证证明生产JVM不会退出，最后测试controller清理仅该合成夹具，UNKNOWN未变CLOSED、无E9_PC_CLOSED、无生产close ACK；不把清理求PASS。

实际ADB/安装/设备广播、原Android raw/dup、真实媒体读写/导出、迁移、实际approval token/H_actor/catalog和activation均NOT_RUN或NOT_CREATED。没有新ABORT/清账/换budget。原N2 ABORTED0B、107218/三R三S/reserved0、原fence/档案/oldCloseACKfalse为继承事实，没有重读实际设备导出件作新声明。

D1未过、M0未启、E6B-OBS-F01长期准入OPEN。请tester整包集中复审后，由负责人决定后续有限设备身份/控制批次和最终scope。
