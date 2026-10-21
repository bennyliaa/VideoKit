# D1 E13E 实现、原身份与有限边界 V1.0

2026-10-18。新目录docs/coder/d1e13e；旧E13A/C/D/B不改。R/T均对应实际源码，不另造通用取消/诊断框架。

| 需求 | 实际接线及不变量 |
| --- | --- |
| R01 | binding/E13Stages：单进程48事件、单条500 ASCII字符、总24576B含换行/结尾预留；满额只增dropped，不改资源。scope/method/原ownerID/UID/PID/thread/单调seq+时间；Android Log在owner锁外。test@Before先记录，再分E9观察各阶段；原bind/HELLO/fixture RPC、callback及unbind入返、完成门均记录。事件不是ACK。 |
| R02 | binding/E13FinishOwner先在onCreate订阅，再接同runner请求；首code/深拷贝Bundle固定，结果16KiB上限，FD原结果保原引用/UNKNOWN，不复制grant。原失败保留；最终非主线程核30秒资格、最多一次super.finish。订阅注册前/检查中/检查后/worker退出前通知不丢。实例与worker由静态OWNERS强持有；Android finalizer为daemon，不把它当PC custodian或JVM保活证明，真实Android main/instrumentation保持及T07另审。永久UNKNOWN不发finish，不调用super.onException提前终结。 |
| R02组成门 | BindingOwner callback/unbind实际返通知；Probe只在本地binding/原远端均确返后退；E9CurrentObservation退ACTIVE通知；source finalizer直接等待原registry notify、原caller.join、原runtime graceful awaitTermination，避免Future结束早于原线程返时漏通知。没有shutdownNow/中断释放。E13完成后封新增Probe/source/E4Session，保留原return。E11其他legacy keeper在E13六方法路径不创建，原初始非零会阻断；没有把旧owner转成新owner。 |
| R03 | fixture强持唯一TargetBinding及scope；caller UID10221、scope/ownerID/PID/fixtureUID及kernel结果精确匹配。code1一次；code2即时同原snapshot；必要code3等待同原callback最终归还，wait释放owner monitor，Binder原调用仍占用。永久unbind异常直接UNKNOWN快照，不二close；最多2附加读、请求1024B/响应4096B。不是2次早快照后遗忘：原code3可跨响应资格仍在途，超时不取消/不假ACK，实际晚返仍保持原失败资格。 |
| R04 | E13OperationArchive在原Operation注册后、Process启动前保存intent；唯一原reader offer，8×4096B队列/每operation原raw cap，独立原writer持有每个E4Owned文件（intent/raw/PID/facts）。2秒只判写入或intent资格；原IO未返仍保管、不取消。读流继续有界drain；EOF和readerDone不同，原exit/PID独立记录。固定记录≤4096B，不写媒体。archive-facts在原writer/自身文件最终close前序列化，不能单凭该文件证明它自己的close；最终真实supervisor/检查回执才证明writer及原文件真返。磁盘错误即记录不完整/失败，实际已返和UNKNOWN分栏。 |
| R04外层 | observe_original.ps1强持同一Process、两原ReadAsync流、bounded writes和metadata FileStreams。原raw每流8块队列、总cap32768或81920B，metadata单条8192B、单次创建；记录故障继续原drain，close仅一次，UNKNOWN继续同宿主custody。receipt不能自己证明其文件close，console补实际metadata文件归还字段；旧诊断不会被它回溯修复。 |
| R05 | E13GuardLocation固定serial及canonical root，不接受CLI/env换根；当前DISPOSITION_SHA=ABSENT。E13PendingGuard非阻塞FileLock原子判定/登记、CREATE_NEW claim/force、atomic pointer；扫描所有claim（含未成为pointer的部分条目），仅准确同claim SHA的原返marker可继续。新UUID/PID消失无放行代码。typed外部处置只由未来审定源码pin接受，external outcome要求originalJavaReturn=false，且诊断需独立disposition digest。现版本零实际处置pin。 |
| R06 | app18/fixture2，来源与旧已装17严格分开。E13E_SOURCE_DEPLOYMENT引用E13C部署报告，仅精确安装byte前身，不声称首case/source全面验收。固定新batch D1-E13E-LIFECYCLE-20261018/once e13e-lifecycle-deployment.once；旧E11/E13A角色仍固定，旧冻结未改。所有实际scope/release/once及处置pin未签发。 |

R05是被审新入口的共享操作封锁，不是OS安全沙箱；不能回溯改写旧JAR、拦截手工ADB或控制旧JVM。所有窗口后续必须采用同一受审入口/协调封锁，禁止绕用旧工具；原旧任务的保管继续由原owner负责。当前source pin ABSENT确保即使新scope也没有任何设备派发。

T01直接实际Probe ServiceConnection停在countDown之后/owner finally之前，并接实际runner，成功/原失败都验证；T02四交错、重复请求/异常/FD未知、非主调用；T03实际Sender端点和Probe解包，早snapshot→同原ACK、错UID/scope/replay、UNKNOWN；T04实际同步adapter/观察原边界；T05实际HostCase/Supervisor晚raw与archive/外层记录失败；T06真实公开新旧deploy/case入口并发新scope拒SDK；T07仅未来设备门。平台替身的UID/调度/descriptor flag不冒真实内核/FD/Looper证据。

限制：底层同步Binder/文件调用没有被“超时取消”。永久原调用或UNKNOWN仍会持有原任务，需审定处置；本修复承诺原对象可见和正确续办，不承诺所有原IO都可强制结束。没有修改renderer/audio/Kit或媒体native模块。
