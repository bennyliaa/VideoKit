# D1 E7A 交付 V1.0

2026-10-17，D1-20261017-E7A / versionCode10 / D1-E7A。修复E7-F01/P1的实际诊断任务与instrumentation结束边界；本地有限证据支持新边界，Android进程生命周期及控制权限尚未实测，须独立静态复审后再正式派发。旧E7全195项保持冻结，未部署E7或E7A。

旧入口的问题成立：await10s后assert/throw可让JUnit结束，runner.finish实际会退出目标进程，static Job不能保住在途/UNKNOWN owner。新E7AReadOnlyInstrumentation直接继承Instrumentation，不用JUnit；onStart异步返回后没有自动finish，实际E7ADiagnosticRun拥有原E4Owned和全部原操作。旧JUnit入口在创建任何Job前明确禁用。正常/故障类不运行，本批不是普通JUnit单方法执行。

10秒仍为原诊断资格截止，单调时钟从run创建起计。截止仍在途、分配/close未知、中断/异常控制状态等永久PENDING，不因迟到返回改PASS。原任务只运行一次，open前已登记原holder，read失败仍由原holder尝试一次原close；UNKNOWN不重开、不重试close。history/proc未返时即使FD已close，也不能结束。外部用预存handle经权限保护的控制接口读状态、停止依赖或归档确认；实际作业的finish需精确handle/sequence归档ACK且全部原操作真实返回、holderEMPTY未分配或CLOSED实际归还。启动前可证明任何原操作尚未发起的拒绝，允许在同一门下直接失败结束，无作业假close。

本地最终28场景/338断言PASS，直接运行实际Job/run/deadline/finish-ACK和原E4Owned，并经过同一E7WriterDeathGate；只替换clock和平台操作、平台finish计数。覆盖快成功/收尾失败/七处在途/迟到/close UNKNOWN/Exception或Error分配窗口/InterruptedException/实际线程中断标记/错或过期ACK/提前结束/异常finish/重复任务。初次27/327后补真实线程中断标记用例，最终28/338；两次日志及旧测试源精确SHA保留，不累计成55项。旧死亡门27/316为继承未重跑。

main-001一次离线双APK构建成功（38秒，无修复/下载），最终输入SHA `09e62035889c5b37b6acb480711e464c091f7f1074362d90b211b6479548038a` 与build记录绑定。app/test DEX及test manifest确认新实际边界/custom runner，非AndroidJUnitRunner。125个生产/native/upstream文件逐字节继承E7，max8只读死亡门、guard/fence/账本/每host原观察/实际close/六帧EOF/1000us等均未动。七native相同，35Maven锁坐标无delta，原FFmpeg8.0.3/Media3 1.9.3/全部许可P0保持。zipalign-P16静态PASS，不作设备16KiB实测。

- app-debug：10544590 B，SHA256 `78ec2d3b057b91736ea0bf273ab6bf1b1028dae97916052b5ddb235087d84baf`，`docs/coder/d1e7a/artifacts/D1-20261017-E7A/final/app-debug.apk`。
- androidTest：2738285 B，SHA256 `5a97f705813dfbe6f1476d9409c6448a7de981ea77420f2733890691a2248646`，`docs/coder/d1e7a/artifacts/D1-20261017-E7A/final/app-debug-androidTest.apk`。

双APK证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。没有新增app权限或service；控制广播接收器仅诊断存活期间动态注册，要求发送者持有现有signature/privileged DUMP权限，普通app不能发送。Android shell是否具备并能正确调用该入口需设备复审验证，尚无实测保证。

精确构建输入变化：

- `docs/coder/d1e7a/app/build.gradle.kts`
- `docs/coder/d1e7a/app/src/androidTest/java/com/videokit/spike/e4/E7ADiagnosticRun.java`
- `docs/coder/d1e7a/app/src/androidTest/java/com/videokit/spike/e4/E7AReadOnlyInstrumentation.java`
- `docs/coder/d1e7a/app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java`
- `docs/coder/d1e7a/settings.gradle.kts`

四文档、全源码/diff/输入/日志/SBOM/原native完整对应源及来源入完整ZIP。最终seal=evidence/e7a-freeze.json、完整ZIP=artifacts/D1-20261017-E7A，身份由包外 docs/coder/D1_E7A_READONLY_VERIFICATION_V1.0.json 给出，无自指；ZIP无私钥/local.properties/classes/cache/真实媒体。tools/e7a_package.py verify只读，冻结后不重跑检查或构建。

E6B-OBS-F01长期准入继续OPEN，旧writer缺boot/start代次与可信防回滚依据，持久事实协议仍DESIGN_BLOCKED，无格式/读写/迁移/fallback/no grant。原平板MP4限定PASS保留；AVI/能力/cancel不准入。最后tester预算累计107218/reserved0及全部旧输出/N2归档保持，非本批实时重测。无ADB/设备/真实媒体源或导出件/下载/新恢复写，E3已耗许可不复用。D1未过/M0未启，历史signal门及既定P0不变。
