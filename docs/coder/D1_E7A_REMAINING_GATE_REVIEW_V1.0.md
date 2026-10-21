# D1 E7A 剩余门槛复审 V1.0

2026-10-17。请求tester先完整独立静态复审，不直接设备部署。本批不提供一次性执行许可。

|项目|当前状态|
|---|---|
|E7-F01/P1|本地实际Job/finish边界28/338支持；Android异步runner/控制权限与真实操作返回尚未实测，交独立复审，不自行登记设备关闭|
|E6B-OBS-F01/P1持续准入|OPEN，旧writer启动代次与可信持久根缺失，持久方案设计阻塞|
|原E6B_NORMAL MP4|原平板限定真实6/6/6/6 READY/PTS0/双EOF/画面/全部资源/S53567 PASS保留|
|AVI/能力/cancel|不准入，不能因只读诊断QUALIFIED解锁|
|原预算与产物|最后tester107218/reserved0及全部旧输出/N2归档保留，非本轮重测|
|构建/来源|一次38秒离线双APK、原证书/version10，125生产文件不变、七native/35依赖无delta、旧E7全195只读核验|
|D1/M0/signal/许可及其余P0|D1未过/M0未启，原门与未决P0保持|

复审应从新test manifest的custom Instrumentation到onStart、原Job、唯一super.finish出口逐段核对，而非只数纯gate用例。确认旧JUnit入口禁用；onStart返回不触发AndroidJUnitRunner；预留启动窗口后才启动；核心返回标记包含全部真实平台调用，关闭未知/分配未知不能被失败报告绕过；10s PENDING不可变；ACK严格handle/sequence/资源返回且只调用一次；初始化例外确实没有发起作业；最后receiver实际unregister异常也不以正常退出掩盖。

核权限：不新增app uses-permission/service，动态receiver要求发送方现有DUMP，STATUS/STOP不取消、不重查、不写业务状态；外部协议仅非等待am instrument（无-w/proto/UiAutomation），避免启动命令结束牵连目标。核有实际可识别handle和有限状态查询、外部隔离记录、迟到/UNKNOWN/进程死亡不可恢复资源的真实限制，不接受静态引用、线程非daemon或无穷等待本身当证据。

本地平台替身只支持实际核心决策；Android进程生命周期、DUMP shell权限/广播递达/无watcher启动、原FD与系统调用仍需新正式设备派发实证。若静态协议仍有缺口，继续阻断设备；不得为通过而延长资格时间、结束未知原任务、丢UNKNOWN或取消原future。

完整材料：source-derivation逐输入精确diff、local-check-results最终28/338原日志、001追加测试来源、integration-static-check生产目录字节比较、输入SHA绑定main-001、signer/aapt/testmanifest/DEX/zipalign、SBOM/native对应源、四文档和device_plan、ZIP/freeze/包外只读receipt。旧E7不再构建或部署，旧27项死亡gate仅继承。持久损坏/重复/过期/在途均无准入消费入口，未虚构解析器或Android重启/PID复用测试。
