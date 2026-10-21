# D1 E9 集中实现交付 V1.0

2026-10-18。本包为静态审查候选 `D1-20261018-E9`，versionCode 11、versionName D1-E9-PREPARE。集中实现 E8A 接受的共享phase、外部registry/catalog、受管双phase actor、有限恢复、当前host观察和精确部署门。本包尚未获得tester静态接受，不是D1通过或项目正式交付。

源码工程：`D:/CodexProjects/VideoKit/docs/coder/d1e9`。四文档位于 `D:/CodexProjects/VideoKit/docs/coder/D1_E9_*_V1.0.md`。最终ZIP和外置seal由 `tools/e9_package.py freeze` 产生；seal不放入自身ZIP，不在本文预填自身hash。原始E7A 200项、E8A 42项冻结对象全部只读核对一致。

## 实现与可核证据

`src/.../E9Record` 是app与PC共用严格、排序、逐字节规范JSON；`E9Actor/E9Evidence/E9Catalog` 共用身份和证据解释。`E9MigrationRun` 在入队前保留操作，identity和commit各独立10秒，任何PENDING不可恢复成成功。`E9OwnedFiles/E9MigrationTransaction` 持有原资源，CREATE_NEW仅写新控制命名空间；锁释放不作为close回执。

`E9Registry` 为实际外部规范writer/reader/sealer。head只链接先前已落盘的证据记录；catalog/checkpoint/seal/未来activation-release不反向进入head。重新打开必须提供已知精确head，活跃/不连续/未锚定记录/错误授权引用/未知文件隔离。实际安全失败返回允许归档与正常结束，但不获得final，也不自动获得actor2。恢复只接受原actor真实晚返且正常finish，或精确代次终止且不伪造旧Java返回。actor2自身也UNKNOWN即停止。

`E9CurrentObservation` 在每host重新持原guards、核当前fence/档案/完整账本和已接受前缀/无pending/控制清单，并在本host真实返回后授liveproof。`E9Phase/E9BuildPolicy` 在prepare固定ROLE=PREPARE、CATALOG_SHA/BASE64=ABSENT；全部产品入口拒绝。旧reader/recovery入口禁用，旧debug instrumentation也封闭。

实际PC工具 `E9HostDeployment/E9HostManager/E9HostActivationSession` 共用生产registry和dispatch gate。无参数只inspect；本批只执行了默认inspect、编译和synthetic拒绝。未来受审配置及执行许可必须由负责人另派。未来policy导出先绑定真实final catalog，再构建APK、再登记实际APK SHA；没有要求未来APK hash先进入catalog的循环。

## 构建与APK

一次离线主构建main-001因公开SDK无O_DIRECTORY常量失败；仅移除不可用标志，保留lstat/fstat目录角色校验，repair-001离线通过。原输入与失败日志保留，无无关旧测试、native重编或依赖下载。双APK签名校验、服务manifest、DEX入口及16KiB原生库对齐校验通过。

|APK|bytes|SHA-256|
|---|---:|---|
|app-debug|10643010|`4c09d1abed854555f16e277dbcda605c37c47c11cb4d55b9712676cc5bc6a287`|
|androidTest|2749765|`9f693e30babead370ff2f632242b4ebc033de58b867b3e2e6887ec5776ca3ca8`|

证书SHA-256：`5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。最终构建输入SHA-256：`8f3ebeadcc73cbbcc297dbfcb5d86fec1c698cd8512443c382f5df377c40003d`。APK位于 `docs/coder/d1e9/artifacts/D1-20261018-E9/final/`，以实际工程绝对根目录解析。7个native库与冻结E7A逐字节一致，锁定35项依赖无变化；FFmpeg 8.0.3、Media3 1.9.3及许可状态继承，未作商业清权声明。

## 本地验证结论与范围

32组映射，36个最终映射JVM进程、D05针对性修复另2次，最终映射断言 **2027**。它们直接调用生产对象；不是另写状态模型求PASS。全部失败尝试、自检输入、stdout/stderr、平台切点轨迹保留。D05在最终检查发现PC端再hash允许集合过宽，收紧为本次候选app/test，增加“检查后替换成已知旧包”用例通过；仅host工具变化，未触发APK重复构建。6个实际最终Gradle编译Android公共入口在SDK桩上先于平台调用拒绝；未来host工具实际编译/default/synthetic-release拒绝通过。

真实JVM文件、FileChannel锁、原E4Owned holder、原事务及registry均执行。Android UID/inode/目录fsync、boot/proc来源、ActivityManager正常finish日志为替身；受控时钟不冒称真实10秒。Windows锁读取适配复用同一guard channel。用于模拟确切进程终止或最终清理的native facsimile释放不修改原UNKNOWN holder，不提供旧Java ACK。具体有限范围和未跑子例见剩余门文档与test-mapping.csv。

本批设备/ADB/真实迁移/真实媒体读写或导出/真实H_actor与approval token/activation构建均NOT_RUN或NOT_CREATED。没有新ABORT、清账或换budget。原N2 S0=ABORTED 0B，消费107218、三R三S、reserved0、原fence与oldCloseACK=false保持为被继承事实；未重读实际设备导出件冒称新验证。

D1未过，M0未启动，E6B-OBS-F01长期准入仍OPEN。请tester依据整包源码、输入和原日志独立静态审查，再由负责人决定后续设备与最终scope。
