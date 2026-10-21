# D1_MEDIA3_ANDROID02_FIX02 完整五项集中交付 V1.0

2026-10-21。**BUILT_OFFLINE_FIVE_FIXES_IMPLEMENTED_TYPED36_PENDING_INDEPENDENT_B**。R01-B01–B05已集中实现，实际全源类型检查、36项typed非媒体状态/顺序测试和一次离线strict app/test构建已完成，双APK真实验签及源-class-JAR-DEX/300实际消费已核。此为coder有限自检/实现交付，**不自行关闭独立五项，不签Android功能/设备就绪/隔离格式/READY COMMIT/播放**。原报告51b91814...bee8fa为五项静态P2、Android复现0的结论保持；D1未过M0未启。

## 1. 新候选与全部五项

独立目录D:/CodexProjects/VideoKit/docs/coder/d1media3-android02-fix02及fix02-gradle-home；基于冻结recovery01准确源/镜像/许可。原seal/旧cache registry/媒体/encoder/产品App不改；旧35512/48945/17257 UNKNOWN无查询/attach/处置。一次全scopeAll十case功能簇仍在同一原Job/worker运行：preopenAdmission/rejectFixture/cancelLateRead/writerPending/inspectKnown/Short3/Unknown/Seek1s/bbbObserve/muxQualified。真实捕获6→原MatureMuxer→Sink→原writer/FD/任务返回→同grant fMP4重开全链未删，Media3 1.9.3/原17版本/flags政策保持，无JCodec或新框架。

**B01**：ScopeJournal保存已编码不可变case字符串，同锁发布/快照；观察者只读immutable completed/current和同步meter/owner快照，不遍历worker正写JSONObject/parser集合。回执不依赖易变current method判断批次，始终用requested scope身份输出已有history、完成数、失败当前case/currentIOPhase/partial/firstFailure及原owner门；不重跑补历史。content196608B预留状态262144B/全scope emission1048576B，超界明确BLOCKED并保既有history；runner删除“仅最后裸JSON”降级。worker当前实际sample不完整时不编造中间parser结果。

**B02**：同ScopeMeter逐case+COPY/HASH/PARSE/SEEK/REOPEN/CONTROLLED记SDK readAt requested、native attempted/actual/EOF/unknown，copy/controlled单独；所有预留在同原调用前、全case累计。SDK+copy/control/directEOF请求门8MiB，native计量独立但由已准入请求覆盖；output SDK请求与native attempt各16MiB，无partial/unknown退款，含私有copy写及controlled写4，不换factory清零。short3预声明真实mature Reader请求上限4、原native chunk3，记录实际4/3/返回数，不从readCalls猜，库内部更上层请求长度不冒此readAt观测。原FD slot在open前登记、成功adopt和同close单独记；known registered native FD peak、asset-stream owner peak和source lease peak分开，AssetManager/全平台内部FD数API_UNPROVEN，不假称source0即nativeFD0。

**B03**：CompletionPoint把同步E13ReturnEvents.returned及其异常记录都放最后marker之前；marker/body flag后无受控资源回调。严格单调差>=0且<60000000000ns，等号/真正迟返不升级，准时完成晚观察仍准时；同原worker实际join、runner finisher owner及platform finish/外capture另列。marker不是OS退出。

**B04**：RawWrite这个unbuffered OutputStream/OriginalOwner<FileDescriptor>/计量slot均在Os.open前登记到原Job。**没有打开后FileOutputStream(fd)平台包装/别名窗口**；原FD返回后先被原holder采用，后续Os.write/flush/fsync/close一直同对象，唯一原close准入，错误/close UNKNOWN强保管并阻止resourcesReturned。包装对象本身在open前构造，无post-open平台流close所有权假设。读RAF也先注册OriginalOwner，open后未成功交桥的原对象由同keeper清理，不用替代句柄冒close。已另作官方文档网页只读核对，非构建/依赖下载联网；公开API依据见[Android Os reference](https://developer.android.com/reference/android/system/Os)及reference/android-raw-fd-api-contract.json；这里只核API类型与保守调用合同，实际Android close/内核错误行为未运行，未知不重试。

**B05**：Job.muxerBinding元数据keeper先登记，再允许原MatureMuxer构造；OriginalOwner强持有分配意图及成功返回真实对象，addTrack/sample/EMPTY_EOS/close各原调用状态/首错独立。原六payload/空EOS意图未变，仅把EOS与原close拆为可分别观测的两步；原close最多一次。错误时仍清同原对象；构造不明/close抛错或未返均保留UNKNOWN，阻止原Sink/FD被当成muxer已返，resourcesReturned/finish门明确包括muxer。无替换muxer、重导出或第二close。legacy无Job keeper的正路入口直接拒绝。

详evidence/five-fix-completion-matrix.json，类型/静态实现与Android未证分层，不以自检直接改独立结论。

## 2. 必要实际typed验证

一次javac256MiB/release11/-g对**全部真实src/android/upstream/instrumentation**和两个小helper做类型检查，固定android-36.1 SDK jar/原deps/apksig作编译输入；不是host stub替身。单typed JVM256MiB、整窗口30秒、payload<64KiB，仅实际Java政策/原keeper状态/受控future-worker-callback端口，**36项通过**：journal6、layer/budget/FD8、实际E13同步listener+受控时钟7、raw owner6、muxer owner6+阶段3。pending/失败/未知不二close、跨case预留不退款、回执快照并发和原callback尾段都有实际同原线程finally放门/join；没有故意永久挂起、反射改状态、旧未知套件或实际Os/Media3解析/mux。

typed JVM PID31592 UTC04:23:42.426171至04:23:42.908277，自然exit0/原两流关闭；编译及单JVM总窗口<30秒。typed-001源码/class/原stdout-stderr/owner保全。测试后最终复核只补两处**显示字段**：receipt currentIOPhase及小测试配置snapshot报告实际limits；没有改预算守门/owner/journal/完成算法，也未重放typed JVM。post-typed-metadata-only-differences.json明确原/末hash；最终全Android编译覆盖末源。typed-versus-final-policy-classes.json逐类给真实字节对比，不笼统冒执行过最终DEX。后置独立apksig JVM仅查签名，不再跑typed状态测试。

## 3. 一次真实集中构建与准确产物

固定官方Gradle9.5.0/JDK21 launcher/原agent、client64MiB、single-use2048MiB，--offline --no-daemon --max-workers2 strict/metadata/原锁；purpose-built require_escalated按负责人恢复成功许可经自动审查处理本地loopback，不改防火墙/ACL/网络策略、不联网。仅:app:assembleDebug+:app:assembleDebugAndroidTest，**001一次成功，无第二构建**。client13656 UTC04:25:04.476803至04:26:51.553604自然exit0，stdout345021B/stderr389B，各<16MiB且<600秒；新daemon36964 UIDd9560244-ff53-47f5-bd27-432cd30d2077 creation04:25:05.333860，原client声明准确PID+镜像/创建校核+同Win32只读handle signal/exit0/原shutdown日志。原两流关，非仅isAlive/计数推退出；新两进程返回不替旧UNKNOWN收尾。

| 最终产物 | 大小B | SHA256 |
| --- | ---: | --- |
| app APK | 7151481 | f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad |
| test APK | 478124 | b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9 |
| production class JAR | 150394 | f246fff1e4faebbc05279283f47ca264523b4bf87ff1491c198c814352b1719c |
| instrumentation JAR | 40142 | 114aa266fb60d010f07a851c4a013a35ebb15c59bbaaaa4494566d2e20390722 |

目录artifacts下media3-android02-fix02-*；实际com.videokit.d1media3.android02及.test、versionCode1/nameD1-MEDIA3-ANDROID02-FIX02、process:media3/准确built-in runner。原apksig9.3.3 SHA先准入，后置一次256MiB/30s签名JVM27040自然exit0/两流关；两APK v2true/同单cert5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。实际AXML零权限/活动服务provider receiver/native、无sharedUID；同UID只是良性实验，不签RCE隔离。JCodec/JAAD/fork/host checks/platform-fixtures未混入APK。

105真实javac class（生产94、instrumentation11）逐SourceFile/major55/源pin/class/JAR entry核对，并核各定义在所属DEX真实存在；不冒JVM/DEX逐指令等价或实际方法已跑。14处Java/Manifest相对recovery01差异及appGradle仅versionName另列，所有前后patch/source hash保留。上游E4/E13/E6成熟源不改，薄适配调整原API调用/保管与phase hook。

300实际strict artifact=123binary/37module/140POM，SHA均匹配verification及原Android01实际集合；四个独立实际closure为12/17/12/0，实际javac classpaths独立保全。锁/metadata原字节、17坐标/Media31.9.3原样，无新依赖/下载，继承source/binary/metadata许可闭包及更新SBOM；不签最终商业/专利/FFmpeg清权。

## 4. 原fixture/功能与未证边界

test APK中准确8849B/hash19e815a4...778a9c、qualification03报告a814ac8e...9e0926/manifest、BBB349102B及原来源许可逐字对应。原文件/encoder未重生成，BBB仍只bbbObserve。实际Media3 raw flags保留，KEY_FRAME与仅末LAST_SAMPLE预声明政策不变，送mux只去内部marker；AnnexB1340规范化hash不混rawAU1360，实际CSD数组不强说三项，拼接AnnexB20。独立DTS仍UNPROVEN，空EOS1200000只是意图，真实重开duration须原SeekMap/TrackOutput证明，不填golden。

当前Android方法/原生FD fsync/close/实际muxer及正路fMP4重开/平台finish全部NOT_RUN；typed端口不冒这些事实。Asset内部FD/整个OS FD峰值API_UNPROVEN，known registered FD计量不是全平台总数。原MC-B01同原Provider/一次REOPEN/暂待不耗检查、真正UNKNOWN sticky保持；无旧大套件/ContainerPendingOrderCheck重跑、无host全空闲声明。所有原seal/history/旧FAIL/UNKNOWN保留。

## 5. 准确执行准备与停止

execution-plan.json重新绑定准确双APK/签名/runner/process/version及唯一scopeAll三参数，十内部case共享SDK readAt+copy/control/directEOF输入8MiB、output请求/attempt各16MiB、块64KiB/sample262144/source2/每源1/queue0，全scope单60秒。phase/FD历史各128、immutable journal196608/每status262144/全emission1048576界明确；无case/factory退款。全48原oracle分类与五修matrix均保，不把36typed项冒48Android PASS。

future仍6个逻辑调用：准确fingerprint1、本APP/TEST存在性各1、准确双新APK各install1不-r、scopeAll instrumentation1。准确binary出站**7629605B**，命令每op4096总24576，logical outbound上界**7654181B**；preflight786432/install131072/所有pending-final两流1048576/controllerproof1048576，总logical inbound3014656B。无额外fixture push/无界logcat/其他项目操作。协议framing未观测，不冒精确wire字节，需未来capture工具合同绑定。

外wholewall观察90秒拟定，只停新准入并保管原capture/FD/worker/finisher，不强关管道/kill/二close；cleanup只在原返回后且单独准确批准处理新自有文件，不自动uninstall/clear/retry。现在scope/serial/freshIdle/captureTool仍null，先完整独立FIX02 B再负责人准确实机新范围；无自动许可或设备动作。本批设备/ADB/5037/占用/生成/编码/解码/播放0。

## 6. 封存与交接

evidence/fix02-freeze.json及外置D1-20261021-MEDIA3-ANDROID02-FIX02-source.zip覆盖全部相关源、五项typed原代码/class/流/owner、实际105class/JAR/DEX/APK/签名、准确asset/来源、300strict metadata副本/许可/SBOM、实际build原返回、五项/48矩阵/计量与API边界/准确计划/全部前后差异。大Gradle cache/mirror不是新产物；准确实际消费pin另留，原镜像不改。tools/review_materials.py仅纯Python核材料/hash/ZIP，不编译/Gradle/JVM/设备。

原recovery01 728/Android02 372/Android01 740/Container02 676/fork2738逐hash不变，独立B51b...及原QUAL03/A各manifest全保全。五项集中交负责人，不逐字段交接/自行关闭独立问题；等待整包B后统一后续。
