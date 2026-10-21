# D1 E7A 独立静态复审报告 V1.0

日期：2026-10-17。Tester。依据 `docs/milestones/D1_E7A_TESTER_REQUIREMENTS_V1.0.md` 审查完整冻结候选、四文档、来源及已有有限证据。

## 结论

**SUPPORTED_FOR_SEPARATE_FORMAL_MANAGED_READ_ONLY_DISPATCH，未发现新增问题。** E7-F01/P1 的修复在源码及已记录的实际 Job/finish 决策边界范围得到支持，静态缺口关闭；Android 自定义 runner 的进程生命周期、广播权限/可达性、实际原操作和结束流程仍 NOT_RUN，不登记为设备关闭。

支持的下一步仅为另行正式派发 E7A 受管只读诊断及有限控制协议；不是原 JUnit 单方法，也不是正常回归。E6B-OBS-F01/P1 持续 OPEN、持久协议 DESIGN_BLOCKED；原 MP4 限定 PASS 保留，AVI/能力/cancel不准入，D1 NOT_PASSED/M0 NOT_STARTED，其他P0/许可不变。

本轮 Tester 设备/ADB/安装/媒体及导出件读取/Gradle/native/模型重跑均0。仅读源码/冻结包/既有日志，并核对官方API；未部署E7或E7A，无在途设备任务。

## 原 E7-F01 与实际生命周期修复

审查路径为最终 test manifest → E7AReadOnlyInstrumentation.onCreate/onStart → 实际 E7ADiagnosticRun → 核心 acknowledgeFinish → 唯一私有 finishPlatform → unregisterReceiver → super.finish。旧 E7WriterDeathDiagnosticTests 在创建任何 Job 前失败禁用，没有旁路运行旧超时入口。

| 边界 | 静态及已有证据结论 |
|---|---|
| 启动/所有权窗口 | 原run先建立E4Owned，再beginLaunch标记窗口，然后Thread.start；尝试启动后异常不冒充“从未启动”。可证尚无原操作的prelaunch拒绝才允许EMPTY失败结束。 |
| 原操作串行/返回 | 同一实际run依次preflight/open/read/原close/afterClose/history-proc；read失败仍由原holder尝试原close一次，控制端不close/interrupt/cancel。operationsReturned仅表示上述操作链实际返回并进入内存终结记账，不声称Java线程已死亡。 |
| 未知资源 | safeToFinish同时要求操作链已返且holder EMPTY从未分配或CLOSED真实close；ALLOCATING/OPEN/CLOSING/UNKNOWN不允许finish。即使FD已关、history/proc未返，也不能结束。allocate的Exception/Error窗口、close异常没有重开或二次close接口。 |
| 10秒资格 | 从run创建起使用单调时钟；定时事件和实际完成路径都检查原截止。到界/逾期/中断/控制异常导致PENDING，之后只更新真实归还，不能变QUALIFIED。限内完成后再晚读状态不会反向误报超时。 |
| 完成确认 | 实际作业需外部先归档safe snapshot，再发送精确handle+sequence；核心锁内检查版本、实际返回和一次finish声明。错/过期/重复ACK拒绝，过早ACK保留PENDING。ACK不会触发新诊断或资源操作。 |
| Android结束出口 | 普通finish覆盖方法及onException不调用super，仅记控制故障；实际super.finish只出现一次，在原资源门之后、控制回复后排队。registered接收器必须实际unregister返回才走平台finish；队列/注销/finish异常保留PENDING，不伪报完成。finishClaimed是声明，不是平台完成或close ACK。 |
| 外部停止/意外死亡 | STOP_DEPENDENCIES仅停依赖、不终止原任务。OS死亡/重启/外部强停/控制失联明确LOST_OWNER_UNKNOWN；不能以进程不存在代替原close，也不能新host恢复同handle或自动重启。 |

因此原“10秒断言结束JUnit→runner拆进程”的主动结束路径已移除。控制层在失败时可能保持受管实例，且明确不保证未知原操作能在有限时刻安全结束；这是已标识、已归档并停止依赖的隔离状态，不能记成成功或盲等求PASS。对系统可杀进程的限制没有作绝对保活承诺。

## Android API、权限和计划可执行性

官方接口允许异步 instrumentation；start启动调用onStart的线程，finish会终止被测进程。上述自定义入口不继承AndroidJUnitRunner，返回onStart与主动调用finish分开，语义方向成立。[Instrumentation官方API](https://developer.android.com/reference/android/app/Instrumentation)。

AOSP am源码在非wait且无proto reporter时不创建watcher/UiAutomationConnection，只有watcher存在才等待结束。这支持本计划非等待启动设计，但所核为AOSP主线，不能冒充本平板API31/OEM实现已测。[AOSP Instrument.java](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/cmds/am/src/com/android/commands/am/Instrument.java)。

registerReceiver的broadcastPermission约束发送者必须持有权限，符合本入口要求DUMP的用法；不是要求app新增DUMP。API33以上显式EXPORTED，API31使用既有带permission/handler重载，注册在targetContext下，action+package+user+handle提供准确路由。AOSP Shell manifest声明DUMP，使shell控制方案有源码依据；平板实际资格/送达/有序响应仍需新设备批次核验，不承诺OEM必然可达。[Context官方API](https://developer.android.com/reference/android/content/Context#registerReceiver(android.content.BroadcastReceiver,android.content.IntentFilter,java.lang.String,android.os.Handler))、[AOSP Shell manifest](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/packages/Shell/AndroidManifest.xml)。

权限只保护发送者边界；handle是派发标识，不是抵抗DUMP/root持有者的凭证。无新增app权限/service或业务持久作业文件。广播resultCode1仅表示命令被处理，未证明ACK接受、原close、unregister或平台退出；实际结束还应核核心返回字段、真实结束记录。异步排队后的平台异常不能根据先前finishClaimed当成成功。

计划可具体执行，但仅允许有限控制：启动前归档handle/设备/组件/APK/PID_UID核对；精确非等待启动，最多6个控制请求、单次响应预算5秒/日志1MiB，不带-w/proto/class/UiAutomation。约1秒和截止后取状态；只有operationsReturned/safeToFinish及EMPTY/CLOSED齐备才归档精确sequence后ACK一次。若仍PENDING/UNKNOWN，有限STOP_DEPENDENCIES并保存状态、停止批次交负责人，不轮询至PASS。响应超时/失联也不授权杀进程或开启新instrumentation；原客户端/任务不明应保留UNKNOWN。

6次是外部执行预算，runner没有计数限流器；正式tester脚本必须单独记录并执行该上限，不能误认为服务端已拒绝第7次。后续自然归还后的同handle状态/ACK须负责人另派；不会借“新派发”重置本批已用请求记录或重新运行作业。close/allocate UNKNOWN可能不能安全完成，继续隔离并另审安全处置，不把该限制隐藏成无限无标识等待。

## 28场景/338断言证据

已核local-check-results的精确输入大小/hash、javac/java原命令、退出码和lifecycle-compile-002/lifecycle-run-002原日志：**28场景/338断言**。首轮27/327及追加实际线程中断标记后的最终结果都保存，旧源码精确SHA由test-expansion-provenance绑定；不累计55项。旧死亡gate27/316仅继承未重跑。

有限检查直接执行实际 E7ADiagnosticRun.run/deadline/acknowledgeFinish、原E4Owned及同一E7WriterDeathGate；不是复制模型。覆盖快完成、preflight/read/afterClose失败、七处原平台操作在途、资格截止及迟到、close UNKNOWN、open Exception/Error、ALLOCATING窗口、InterruptedException/真实线程中断标记、错/旧/重复ACK、过早结束、launch窗口、finish callback异常、重复Job。七处在途均没有提前finish，迟到后仍PENDING才可在实际归还后ACK。

clock是可控单调值，平台操作用有限latch，finish是计数callback。没有直接执行Android runner的Handler排队/广播注册注销/权限/系统super.finish；这些仅源码/API/manifest/DEX和构建支持。不能用338断言宣称实际Android生命周期或FD归还已通过。原OS意外死亡、持久协议和控制通信丢失也没有伪装成设备实测。

## 冻结、来源与继承

独立核验 `docs/tester/D1_E7A_EVIDENCE/audit.py` 及 `identity-and-recorded-static-audit.json`：PASS；不执行候选代码、媒体或构建。

| 项目 | 结果 |
|---|---|
| 外seal | 1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76 |
| 完整源ZIP | 18524366B；SHA2569f615382bf299aa2795688357ef084f6ae383745ef3101c6c8d59f1f0a8ca851；196个有序唯一成员逐项大小/hash一致 |
| 不可变项 | 新200项一致；旧E7 seal及195项保持 |
| 最终输入 | 09e62035889c5b37b6acb480711e464c091f7f1074362d90b211b6479548038a，逐项大小/hash及唯一offline main-001/exit0/BUILD SUCCESSFUL绑定，无repair |
| version10 app | 10544590B；SHA25678ec2d3b057b91736ea0bf273ab6bf1b1028dae97916052b5ddb235087d84baf |
| test | 2738285B；SHA2565a97f705813dfbe6f1476d9409c6448a7de981ea77420f2733890691a2248646 |
| 签名/集成 | 双原签名记录通过，证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；test manifest为准确自定义runner/targetPackage，test DEX含实际run/runner，selfcheck未入包 |
| 原生/依赖 | 七native与E7 APK及来源逐字节相同；35 Maven锁无delta，FFmpeg8.0.3/Media3 1.9.3保持，无本批native重建 |
| 静态16KiB | 独立解析七ELF PT_LOAD及APK native偏移通过；不作Android16KiB实测结论 |

四文档、reference原需求/报告/收据、精确diff、测试扩展来源、签名/manifest/SBOM/完整对应源及包外只读回执齐备。逐文件来源中的继承关系复核通过；另直接遍历src/android/native/upstream源码与native-libs的107文件与E7相同。变化只在新test run/runner、旧JUnit禁用和版本/runner/项目元数据，未改生产gate/guard/原观察/资源/预算/严格六帧EOF/1000us/画面与deadline。

只读AndroidOperations仍只读固定recovery.owner：逐级目录及文件角色/UID、NOFOLLOW/NONBLOCK/O_RDONLY、257字节哨兵、精确原字节、dev+inode/大小/mtime/ctime和原close；无observe/force/sync/ledger/fence写、无媒体/CPU/codec或grant。原107218消费/reserved0及全部旧产物/归档沿最后tester实证保持，本轮不声称实时重测。许可/安全与其余P0不以本报告关闭。

## 正式只读派发准入

仅支持负责人另行派：HA1Q6WXR/user0，原UID10221/test10222，version10同签名final双APK保数据更新，先核无未归档旧在途，唯一组件 `com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation`。

精确参数 e7aCase=originalRecoveryWriterReadOnly；e7aBatch=D1-E7A-WRITER-DIAG-TABLET-20261017；e7aScope=READ_ONLY_MANAGED_NO_ADMISSION；handle=9f19bfb5-60e0-4bcc-9666-852409cfe3b4。control action=com.videokit.app.E7A_DIAGNOSTIC_CONTROL、package=com.videokit.app、user0、DUMP发送资格及STATUS/STOP_DEPENDENCIES/ACK_FINISH按上述归档门执行。正式启动命令返回0不是作业完成。

原启动代次/可信死亡与防回滚根仍缺，持久协议没有实现的格式/读写/迁移/fallback。只读收集即使QUALIFIED_DIAGNOSTIC或当前gate通过，也不是原观察或正常准入；完成或隔离后集中报告，不能串AVI/能力/cancel、重跑MP4或进入M0。本轮仅出具此静态准入结论，未执行设备。
