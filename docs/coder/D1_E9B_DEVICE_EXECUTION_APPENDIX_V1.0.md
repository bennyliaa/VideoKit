# D1 E9B 设备执行附录 V1.0

本附录为未来独立审查使用的步骤和预算约束，当前 NOT_AUTHORIZED / NOT_RUN。没有设备实测、没有任何ADB调用；本文不提供可直接执行的一次性许可。

候选应用版本13 / D1-E9B-PREPARE，包com.videokit.app与com.videokit.app.test，签名必须与交付审计一致。仅PREPARE，BuildPolicy.CATALOG_SHA=ABSENT，产品/旧恢复/长期观察仍拒绝。测试runner及非等待命令保留精确批标签 `D1-E9A-PREPARE-TABLET-20261018`，这是继承的协议常量，不能将CLI默认INSPECT_ONLY中的旧批文字当成设备资格或新版版本号。E9B版本号由真实APK审计给出。

未来若负责人独立批准只读批，应先复核ZIP外seal、原输入、签名、版本/role/ABI和设备原身份；配置/命令文件各自按原SHA pin，禁止Synthetic环境代入Device CLI。原HostManager为--approved-session三参入口，启动不等待instrumentation结束，以独立五秒广播取状态；只读identity模式不能RESERVE/EXECUTE_COMMIT，后续类型化归档/精确ACK/正常finish不能用launcher退出代替。未批准的激活导出/发布CLI不得调用。

tester建议未来小批最多16次本机查询、8条Android控制请求（其中STATUS≤3）仍仅设计建议，不是本批执行预算授权。实际本机supervisor总accept硬上限128，含已接受未处理以及歧义失败保守计额；readonly查询与获批收尾共用该额度。提前为收尾留额，不能到128后要求端口继续服务。达到128监听器关闭或UNKNOWN、状态通道耗尽，原custodian继续持有Process/Store责任；不换端口、不重启扩额、不把TCP断开当原资源已返。

实际registry库存最多20文件155648B（另保留196608总门）、40遍历项，独立系统日志总1MiB；本机输入/状态行16KiB、原控制回包32768B、原Process总96均保持。每条独立响应含原解码仍在同一5秒绝对期限内，超期PENDING，不重放EXECUTE或ACK。永久未返/UNKNOWN没有第二次close与安全退出ACK；原non-daemon同JVM监督者继续保留责任，需负责人另行审查，不用新root/catalog/预算/force-stop假恢复。

本批禁止项：ADB/安装/真实媒体读写/实际迁移/ABORT或预算重置/token或真实catalog/H_actor/activation。D1未过，M0未启，长期准入OPEN。
