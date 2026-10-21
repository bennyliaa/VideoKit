# D1 E13E 生命周期整包独立离线复审报告 V1.0

2026-10-18；tester。依据正式tester需求及E13D R01–R06/T01–T07。**结论：NOT_PASSED，3项P1需集中修复；封包/制品身份核验通过，原任务处置方案可继续审议，但不构成执行授权。** 原实际挂起根因仍NOT_UNIQUELY_DETERMINED，D1 NOT_PASSED / M0 NOT_STARTED。

本轮无设备/ADB、原handle/进程查询、STATUS连接、处置、安装/部署、正常方法或原剩余两诊断；旧主任务未操作。未运行候选全套自检、候选打包verify或长55s子进程；仅编译tester自身小探针并对未改最终JAR执行两个秒级有限验证，以及官方静态APK签名/清单工具。没有重编候选Java、Gradle或native。

## 1. 制品身份与独立核验

外seal `a07b56f55733ecc775a21a8c5622b3cdd5b99480386b7ba627520e71e2c6f978`；ZIP为 `docs/coder/D1-20261018-E13E-source.zip`，24662899B，SHA256 `633540d0d5ceea6c5e69e4ad41b3f9daa4bfc706276b479fedb207a71467fb3e`。1001条唯一记录、1000个准确ZIP成员，长度/SHA/成员集合/CRC独立通过。

tester自有审计7555项检查通过，读取2400份唯一冻结文件；八组旧manifest行数375/65/46/367/270/118/141/9全部保持，不把行数相加称唯一文件数。最终167项构建输入中未分发的fixture私钥按交付声明单列缺席，不读取/补造其内容；其余源码/锁等输入字节核实。131条来源映射、182个准确host JAR成员及各自生产source pin、16条既有测试class与最终JAR逐字节等价核实，无平台替身或检查类混入host JAR。

| 最终制品 | 字节 / SHA256 |
| --- | --- |
| e13e-host-tools.jar | 318828 / `8d17b39c999d8b2e135af69927f1a2614672995ed5e39575d99e1bfcb5ab9223` |
| app-debug.apk | 10708622 / `5a196bb225ad5f3811fd8daa06769ebdfa41b1da410c1487c7b3a91f954e0045` |
| app-debug-androidTest.apk | 2774237 / `49808fb23aabb8e01b2b0a18f89b5d6aa5767b4365d9c5ee8e2fcafaafca8c97` |
| fixture-debug.apk | 78841 / `454f50865f6393c03d4b914aece10289cd1ae2f7c60b1c2512e860e089eb8eb5` |

官方apksigner对三APK独立验证exit0、v2签名成立：app/test证书SHA256均 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`，fixture为 `45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9`。aapt2直接解析app v18/D1-E13E-ACTIVATION、fixture v2；test自身版本字段为空，按准确byte pair核，不强求等于18。APK DEX生产类/协议marker与无JVM检查类独立核，七native字节与原已审基线一致、35 Maven锁不变、fixture零第三方runtime。DEX marker是存在性及接线线索，不冒称逐条机器码动态执行证明；Android行为仍未实测。

四次集中离线构建日志/输入/结果与宣称一致：main-001缓存锁权限在Gradle/compiler前失败；env-002 Kotlin sourceSet DSL配置错误在APK编译前失败；fixed-003修正生产源目录及原ACK接线后首次成功；r01-004因真实E9CurrentObservation锁范围源码变化再成功。后两次输入SHA不同，旧成功版/两次失败保留，不是相同源码机械重复构建。未把开发期host-001指针匹配、android-003日志总长、android-004旧汇总误计、outer-008输出杂讯改写为通过；最终证据适用范围单列。

## 2. 集中缺陷

### E13E-F01 / P1：超时后自然归还不能完成同claim结算，永久封住后续scope

位置：`tools/E13HostCase.java:26–32`、`tools/E9PcSupervisor.java:118–121,166–177`、`tools/E13PendingGuard.java:20,26–28`；部署入口也仅在同步boundary返回后检查terminated。

准确触发轨迹：首case超过55s→runOriginal抛PENDING→finally调用closeIngressAndSupervise→原资源未返时返回transferAck→当时terminated=false，因此不调用custody.originalReturned→main退出原调用栈；原custodian继续保管。若原子进程/reader/归档器后来全部自然归还，custodian仅写自己的pcClosed/LIVE.remove并返回，**没有保存或通知同一custody去写原claim marker的接线**。下一scope扫描旧`.claim`，因缺`.original-returned`必拒绝。

这是晚返链的确定静态缺口，不是旧E13C实际卡点判断。host-004 PC_LATE验证了原custodian晚返，但直接调用runOriginal而没有经过公开入口claim生命期；GUARD用手动`first.originalReturned(true)`证明扫描门，不能覆盖这条组合路径。

要求：同一原claim在启动前接入同一监督器实际归还续办，main收到isolation后仍强持有；只在真实完整归还后一次写marker，不依靠再次调用main/finally或人工传true。marker持久化失败继续保管并封锁。所有公开deploy/case入口同样接线。新增有限离线回归必须贯通原claim→超时isolation→同原自然归还→准确marker→另一scope准入；原方法超时资格仍失败，禁止自动继续后续方法。

### E13E-F02 / P1：完成owner锁内仍执行日志sink，R01锁外记录未闭合

位置：`binding/.../E13FinishOwner.java:16–17`两个synchronized方法，内部直接调用`E13Stages.at`；`E13Stages.java:15`在离开其自有ring锁后同步调用sink；Android实际sink为`E13Instrumentation.java:19`的Log.i。

tester对**最终JAR**有限探针实测：FINISH_REQUEST和ORIGINAL_FAILURE的sink调用中，`Thread.holdsLock(originalFinishOwner)==true`。因此虽已修E9类锁，仍有真实owner锁跨日志平台调用。若日志sink未返，request尚不能启动worker/释放owner锁，其他fail/状态/worker接线也可能等待它；不应把诊断调用引入完成所有权临界区。本报告不声称已发生Android日志死锁。

要求：锁内只决定不可变状态和有限待记录数据，锁外记录/调用平台sink；worker启动与唯一请求的发布顺序单独审清，日志异常/未返不能使完成请求丢失。直接验证实际request/fail各stage sink不持任何相关owner monitor，而不只测E9CurrentObservation.class。

### E13E-F03 / P1：archive资源归还使用线程内提前标志，可在原writer仍活时放行

位置：`tools/E13OperationArchive.java:23–29`，writer在自己的finally中先设writerReturned=true、可能移除OWNERS，随后调用`E13ReturnEvents.returned()`，然后才真正退出；resourcesReturned只读该标志和文件状态，不检查原writer Thread真返。`E9PcSupervisor.java:94,113,171–172`据此可认定全部原资源返回并关闭custodian。

tester用最终JAR的原归档器及有限通知listener，在原通知阶段暂停不到2秒，实测 **archive.resourcesReturned=true、原writer.isAlive=true**；随后释放并join同writer确认真实结束。该验证没有Android进程或SDK子调用，started/exit为明确的归档输入替身，不冒真实进程回执。它证明归还判定窗口，不证明当前旧任务命中。

要求：由writer之外的原保管方观察实际线程终止/join后才认定writer资源归还和退keeper，不能在线程自己尚执行通知时当作已返；通知自身未知时仍保原对象。不要在writer自己join自己。增加同原writer尾部通知/返回交错的有限证据，验证supervisor不会提前pcClosed/解除claim；保持文件自身close与facts文件快照分栏。

三个问题均未修复，本轮不修改候选。最小修复集中在已有完成owner、archive、supervisor/custody接线；无需新增通用生命周期框架、重做媒体模块或重跑全部长用例。

## 3. R01–R06与T01–T07核对

| 项目 | 当前已证范围 | 复审判定 |
| --- | --- | --- |
| R01 / T04 | 固定48事件/500 ASCII字符/24576B总量，包含换行预留；实际@Before/E9及原bind/transact/unbind stage接线，E9日志/平台IO已离开类锁；有限平台未返证据 | 部分关闭；F02仍阻断。5s/30s/55s均不当作同步调用强制截止 |
| R02 / T01–T02 | onCreate先订阅；原Semaphore通知在检查期间不丢请求；首code/Bundle深拷贝，16KiB/FD未知保原引用并拒finish；最多一个非主worker，错误/30s资格只降低结果；source原registry等待、caller.join和runtime实际终止接线 | 核心接线成立；实际callback countDown→finally及@After/TestWatcher原失败有分离证据，不能称真实Android monitor执行。F02仍需修，永久UNKNOWN不finish保持 |
| R03 / T03 | 原Sender TargetBinding被强持、caller UID10221、scope/owner/PID/fixtureUID/kernel结果核验；code1 consumed一次，code2快照/code3原对象等待；最多两附加读、1024/4096B；原unbind失败UNKNOWN不二close | 原晚ACK协议静态与有限JVM适配证据通过；无新owner接管。原异常/非预期kernel结果仍由精确响应门拒绝，超过资格期的晚返保失败；真实UID/系统dispatcher/内核拒绝仍NOT_RUN |
| R04 / T05 | 原Operation注册后进程启动前intent，唯一reader offer、8×4096队列/原cap；独立writer实际文件keeper、自然EOF/exit分栏；已有56s子进程原证据对应最终JAR成员；磁盘拒绝/写失败/在途/close UNKNOWN与外层故障证据 | 晚raw落盘已有实证，但F03阻断完整归还验收；未重跑长case。outer-009持久receipt不自证自身close，console实际metadata close另证，不能用这些新证据修复旧丢失诊断 |
| R05 / T06 | 固定serial/root/源码ABSENT；原FileLock下扫描所有claim（含部分登记），CREATE_NEW/force/atomic pointer；公开两个case并发＋新旧deploy入口拒绝、child/install0，位置shadow明示 | 未决准入拒绝通过；F01阻断晚返后正常解除。门是新受审入口协调封锁，不能反向拦截旧JAR或手工ADB，不声称OS安全沙箱 |
| R06 / T07 | 四文档、完整源码/差异/构建/APK/JAR/SBOM/签名/冻结身份可核；app18/fixture2未安装；准确旧source仅部署byte前身，不是测试PASS | 整包来源通过；产品复审因3 P1不通过；T07 NOT_RUN，不能据草案部署或执行六法 |

核现有原命令/退出记录32组，另含public-004四个准确公开入口的自然返回/child0记录、actual-after-007实际JUnit4.13.2 TestName/TestWatcher及实际@After、outer-009/R01-lock-010等接线证据。JVM Android SDK/UID/Binder/Looper/base runner均为明确有限替身；准确monitor1.8.0来源沿用已封E13D，仅验证非主约束与调用线程，不把替身说成真实monitor平台finish。

真实不同UID/签名的kernel行为、API31实际Looper/Binder、系统false/SE unbind和真实平台终态都未运行。本轮两个新增探针只验证最终host JAR的锁和线程窗口；原生产classes未重编，两个探针进程均自然exit0；归档探针的有限latch在finally释放并join同原writer，未留下持续运行的探针进程。

## 4. 旧任务处置方案可审性

`D1_E13E_ORIGINAL_TASK_DISPOSITION_PLAN_V1.0.md`准确区分原主链与LOST诊断，所有PID/版本/data/UID仅最后切片；没有查新状态，也没有凭旧PID提供终止命令。自然分支要求同原handle/owner/终态/原ADB/pipe/decoder/custodian真实链，不保证旧晚raw可以导出。旧Java `retainAuthority(owner,null,owner)`无cleanup入口，新v18/fixture2不能反控旧v17，判断正确。

外部分支具体区分：证据先行→经fresh完整启动身份审定的Android范围→优先原ADB/pipe自然返回→如仍需，另批准确PC对象→监督器之外的行政记录。排除共享ADB server/adbd/system_server/其他项目/serial，包级影响须单列，不通配整树。缺原token则androidReturned仍false，不能让旧custodian伪写新状态；外部终止只能TERMINATED_WITHOUT_RETURN/originalJavaReturn=false，不能写正常Java closeACK、kernel PASS或正常pcClosed。原PS若自身被结束，其reader丢失另记。

诊断独立行政隔离仍为LOST_DIAGNOSTIC_OWNER_UNKNOWN，原58908B及缺stderr/exit/close保留、未知预留不退款，不拿主case将来归还冲销。方案可作为负责人选择和独立审批的基础；**当前未选择A/B、未给fresh身份/准确操作与预算，仍不可执行**。新pending gate接受typed disposition的前提是未来独立审定并固定源码pin再审，文件本身不授权。F01/F03也须先修复，不能把部署后的新claim误当旧对象处置完成。

## 5. 草案、预算与停止门

`candidate-binding.json` / `device-plan-draft.json` status=DRAFT_NO_DISPATCH，actualScope/actualRelease/actualOnce均null，sourceReview=null，dispositionSourcePin=ABSENT。固定once为e13e-lifecycle-deployment.once、新batch D1-E13E-LIFECYCLE-20261018，当前源码在SDK前拒绝，未签发派单。

51成功/53含两次占用复查，是全六法草案：deployment entry1＋35 SDK child＋6Java＋6instrument＋3metadata；fixture旧v1在场的3个额外身份操作计入35。2MiB文本上限/另提3MiB archive磁盘不是当前许可，旧48/50或41/55不继承。每instrument内最多两fixture读RPC不冒新PC操作，真正同步未返仍保管。将来若只派T07准确单方法，应重新定稿更小scope/预算、v17/fixture1→18/2的完整metadata及fresh M1，不按六法草案自动执行。

当前原主case/宿主/reader按原安排隔离保管，本轮未观察其最新状态；不循环轮询、不补ACK。三项P1集中交负责人安排修复，整包重交后独立复审，再由负责人另选原任务处置和T07。历史D1/M0/P0/FAIL/UNKNOWN、许可NOT_GRANTED及renderer/audio/Kit未完门保持。

独立证据目录：`D:/CodexProjects/VideoKit/docs/tester/D1_E13E_REVIEW_EVIDENCE`，包括审计/输入快照、两个最终JAR探针源和原stdout/stderr/退出回执、官方静态APK工具原回执、最终不变核验和manifest。报告发送负责人并保存单独通知回执；不反写已发送报告。
