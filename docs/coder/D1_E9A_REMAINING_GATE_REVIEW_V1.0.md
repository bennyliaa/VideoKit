# D1 E9A 剩余门与定向证据 V1.0

2026-10-18。19组最终映射/21次最终调用、279断言（边界205，共享夹具不变量74）。原始已执行argv在每attempt/commands.json，输入摘要和stdout/stderr、原进程状态/主退出边界文件保留。final-pc-007支持原生命周期各组；frame-validation-008仅补最后纯PC语义帧校验，两组替换映射，旧3份源版本保留。最终生产JAR中共享/生命周期字节与007对照，避免把主机收尾改动掩盖为重复APK构建。

下面PASS仅限已执行列，不是全部排列或Android资格。复用旧Fixture构造合成元数据和调用实际生产对象，未执行旧32组main、未复跑native，不累计其历史PASS。

|组|实际生产对象|已执行有限范围|NOT_RUN/限制|
|---|---|---|---|
|TRANSPORT|E9HostManager.nonWaitingLaunch/broadcastFrame/checkTransport|真实生产非等待命令构造、广播帧解码及实际checkTransport；actor/request/handle/seq/模式/重放校验|Android广播交付/权限/启动实际可达性NOT_RUN；本地只代入shell响应格式|
|STATUS_GAP|E9MigrationRun.observeStatus/status|关闭写入口后仍可STATUS；缺失序号保守扣请求和STATUS额度；非法整数拒绝；第4次STATUS拒绝|真实Android冷启动/丢包未做，不保证一定取得资格|
|IDENTITY_CLEANUP|E9Registry.captureIdentityForFinish/E9Evidence/E9PcSupervisor.Remote|无reserve/无device写，原身份回执归档、精确ACK、正常finish、PC原remote责任归还；不能final或actor2|OS正常finish来源为SYNTHETIC替身；不生成真实catalog|
|NO_REPLAY|E9Registry.commandIntent|已写EXECUTE/ACK intent即使换新seq也不得重发|真实ADB失联NOT_RUN|
|DECODE_DEADLINE|E9HostDeployment.Processes/E9PcSupervisor.runDecoded|真实本机client已退出但原解码任务延迟5.5秒，5秒时PENDING、原任务仍持有；晚返不改成功|受控平台Hook延迟；不是Android响应延迟实测|
|GRANT|E9CurrentObservation/E5AAdmission|实际共享观察成功→重复BLOCKED→requireCurrent拒绝|UID/inode/目录fsync为平台替身；无设备|
|CONCURRENT_GRANT|E9CurrentObservation/E5AAdmission|旧观察close切点在途，新调用先撤销/换epoch；旧调用不能随后发布grant；新调用成功后再重复也撤销|有限本机线程交错；未穷举所有调度|
|CUSTODY_PIN|E9PcSupervisor/E9PcClient|原主管理者隔离后仍可查；错原配置pin不调用收尾回调，正确pin只调用原对象|收尾回调仅本地INSPECT；实际Android收尾NOT_RUN|
|REMOTE|E9PcSupervisor.Remote/E9Registry|真实短生命周期client退出和原共享资源已归还都不代替actor正常finish；remote责任保持直到类型化finish|actor及正常系统日志为合成元数据夹具，无Android启动|
|EARLY_EOF|真实ProcessBuilder/reader/E9HostManager.console|真实pipe reader已EOF/close但child仍活，console EOF后main返回隔离ACK而JVM仍活；child实际退出后才结束|本机Java子进程，非adb.exe|
|READER_ERROR|E9PcSupervisor.Operation/E9HostManager.console|原reader平台异常、原pipe实际close，但child活；原管理者及状态authority保留|Exception为平台Hook；实际Win32内核错误未注入|
|OUTPUT_BOUND|E9PcSupervisor.Operation|真实输出超界后停止依赖，reader结束不能代替活child退出|只测有限超界，不做无限数据压力|
|CONSOLE_EOF|E9HostManager.console/E9PcSupervisor|stdin EOF仍有原child时原监督者接管，状态可查，原实际退出/pipe返回后JVM才结束|真实本机manager JVM和child；无设备|
|CONSOLE_TRUNCATED|E9HostManager.console|截断控制台JSON失败经过同一结束边界，不丢原child/pipe|本机输入截断，不冒称ADB网络断连|
|CONSOLE_OVERFLOW|E9PcSupervisor.consoleLine/E9HostManager.console|16KiB输入界在逐字节读取时执行，错误出口仍实际接管原对象|不穷举全部字符/内存故障|
|CONTROL5|E9HostDeployment.Processes/E9PcSupervisor|实际Processes.runControl固定5秒绝对期限，超时不kill/retry，原client仍活且可识别|观察包含调度/交接尾段，非5秒资格扩成6.5秒|
|LATE_VERDICT|E9PcSupervisor.Operation|5秒后原client真正晚返，物理资源全返但原PENDING不变，不再派依赖|本机真实正常exit；无Android|
|CLOSE_LATCH|E9PcSupervisor/E4Owned|实际child退出后原stdout close在途CLOSING，JVM仍活；允许原close真正返回后才自然结束|close平台Hook有限latch，不是内核永久卡住|
|CLOSE_UNKNOWN|E9PcSupervisor/E4Owned/真实manager JVM|native close已发生但平台抛UNKNOWN，原holder不变，原管理者不退出；有限观察结束的夹具清理不产close ACK|测试controller最后清理仅合成夹具；无E9_PC_CLOSED，不能当生产安全退出|

另：实际新Gradle输出的6个Android公共入口使用SDK桩在平台前拒绝；Runtime成功共享观察→Runtime拒绝→requireCurrent失败序列通过。不是Android系统执行。实际生产host JAR三个默认入口只inspect通过，JAR不含夹具/清理测试类。

## 失败尝试和夹具收尾口径

main-001的Socket.connect被沙箱拒绝，原非daemoncustodian保持存活，后续只对精确新建合成夹具保存无ACK清理记录；不作PASS。pc-local-002在正常本机权限通过真实IPC。关闭UNKNOWN的早期夹具把Windows conhost.exe算作业务child，断言失败且生产监督正确保持；修正夹具只允许原Java任务已退出、剩余仅OS控制台宿主后，才清理该合成manager。004/005失败和006修复证据未覆盖抹去。

最终CLOSE_UNKNOWN的通过点是原holder=UNKNOWN、allReturned=false、原JVM仍活且状态可查、child已真正退出；随后controller终止有限观察夹具是测试清理，不是生产退出路径、没有E9_PC_CLOSED、不生成close ACK。生产JAR没有destroy/cancel/kill；此分界必须随报告转交，不能简写为“UNKNOWN后关闭成功”。其他正常原返回场景自然退出，无此强制收尾。

## 仍开放的门

1. tester对E9A整包独立复审尚未完成，E9原NEEDS_FIX/NOT_SUPPORTED_FOR_DEVICE_MIGRATION未自动解除。
2. 非等待真实Android启动、receiver可达/DUMP权限、完整registered/readonly会话、原raw/dup/dirsync、实际5秒链路调度、boot/start来源及系统normal finish仍NOT_RUN。永久PC start/close/监听UNKNOWN和全部内核异常未穷举。
3. 负责人另派device/最终scope与有效实际授权；本包不填造registry/migration/actor/H_actor/catalog/approval token，也不复用旧E3许可。只有合成SYNTHETIC_LOCAL夹具，不可导出真实release。
4. 缺完整V2身份/原回执、未知管理head、恢复资格不足或torn内容仍隔离，不补boot/start/旧JavaACK，不新ABORT/清账/换budget或启actor3。PC custodian须保留，不能手动kill充close。
5. 真实final facts独立接受后才能另派activation，同一实现、精确同catalog/head及实际APK release绑定；本批没有activation。
6. E6B-OBS-F01须实际新host持原guards、核当前完整合法账本/无pending并真正返回才能关闭。本地/SDK桩无此资格。D1未过/M0未启/长期准入OPEN，其余P0及历史FAIL保持。
