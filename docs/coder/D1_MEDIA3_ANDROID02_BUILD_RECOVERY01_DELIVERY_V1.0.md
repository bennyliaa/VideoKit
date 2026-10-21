# D1_MEDIA3_ANDROID02_BUILD_RECOVERY01 完整交付 V1.0

2026-10-21。**BUILT_OFFLINE_WITH_KNOWN_OBSERVATION_GAPS_PENDING_INDEPENDENT_REVIEW**。准确双APK/源-JAR-DEX/签名/strict双闭包已取得；这关闭本新恢复范围的“无产物”状态，不改旧Android02构建失败。真实Media3提取→mux→fMP4重开及所有Android方法仍NOT_RUN；当前两项已知观测缺口和fresh设备范围未闭合，**不签实机就绪/隔离格式/READY COMMIT/播放**。D1未过M0未启。

## 1. 独立恢复与两次集中构建

新目录D:/CodexProjects/VideoKit/docs/coder/d1media3-android02-recovery01；复制已封存源/准确本地mirror，独立recovery-gradle-home。原Android02/旧缓存registry/daemon35512以及48945/17257未查询/attach/终止/改写。旧日志只证明server写loopback/greeting和client无法连，本批不作唯一根因诊断。

依据负责人明确恢复及阶段A补充，purpose-built exec require_escalated通过自动审查执行固定JDK/Gradle9.5.0已有工具；不改防火墙/ACL/策略、不联网、不关闭strict。直接java -jar官方gradle-gradle-cli-main9.5.0，参数与已固定gradle.bat的默认64MiB/client agent/launcher等价，launcher/bat原hash在owner；daemon原heap2048MiB、--offline --no-daemon --max-workers2 --rerun-tasks --info --dependency-verification strict，只app:assembleDebug+app:assembleDebugAndroidTest。

第一次恢复构建001 UTC03:31:18.427016至03:32:59.039903，client28184自然exit0，stdout349760B/stderr394B；本次daemon22948/UIDcf8fac88-ff0c-4260-a786-800c078335f6，creation03:31:19.383725，同已持有Win32只读进程handle signal/exit0证明自然返回。阶段A补充于构建中到达，故先保全该真实旧源产物/源快照/原classJAR和controller在build-001/before-stage-a，再集中实现新合同，不改运行中输入。

阶段A最新要求明确允许必要源码变更在最多两次集中构建内处理。第二次最终构建002 UTC03:35:33.027334至03:36:10.047127，client36588自然exit0，stdout99992B/stderr394B；daemon39576/UID15d77138-57c5-43dc-845f-6203324b6da2，creation03:35:33.800600，同原handle signal/exit0。两次均非“无daemon”，single-use真实身份/日志/源pin保全；原Popen两流关闭、各≤16MiB、未超600秒、无kill/interrupt/--stop/第三次构建。当前新进程的自然返回不替旧UNKNOWN收尾，不证明host全空闲。

## 2. 准确最终产物与真实消费

最终app artifacts/media3-android02-recovery01-app-debug.apk，**7124541B/SHA2560998beeaa129ef3858fbe1122b80394383f96ad75196c8e4f22b4b856237f6c8**；test artifacts/media3-android02-recovery01-test-debug.apk，**466368B/SHA256f8323a1c0d82d23382baf4f776e56b26174fd5354de5e86d897cb979a467f5de**。

实际包com.videokit.d1media3.android02/.test，versionCode1/versionNameD1-MEDIA3-ANDROID02-RECOVERY01；target进程:media3/准确built-in instrumentation。apksig真实验证最终两APK和首构建保全两APK共四个，v2=true、单证书SHA2565e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。不是用Manifest声明代验签。两APK零权限/零活动服务provider receiver/零native，debug良性空实验同UID非RCE隔离；无JCodec/fork/host checks/platform-fixtures混入。最终test内准确asset8849/hash19e815a4...778a9c、qualification manifest/BBB旧观察资产/来源许可逐字节对应，无替代旧APK。

真实app class JAR **130790B/SHA25695a6068c5719cc4400d2e10d8dd4262a40d7fe4463166b7889975c4b02f62e6b**；instrumentation JAR **32695B/SHA2565742a92cb8910689db7e464a7992093848162e00a47147924c6a79e3de9d6940**。共86真实javac class（生产78/instrumentation8）逐SourceFile/major55/源hash/实际class/打包JAR核对，再确认对应全部类实际出现在各自DEX中；platform fixture定义不入APK。源码差异7处Java/Manifest及app Gradle仅版本名差异单列，首/末源pin与patch完整。

实际strict消费300artifact=123binary+37module+140POM，全部匹配verification SHA256并与Android01原真实300身份集合完全相同；configurations独立实际closures为appCompile12/appRuntime17/testCompile12/testRuntime0。两次真实编译classpath单列，非从主包17坐标推断测试闭包。锁/app/settings verification字节原样，Media3固定1.9.3、无新依赖/下载/版本/许可边界放宽。继承已准入source/binary/metadata/Apache2闭包、更新本候选SBOM、实际metadata审查副本一并封存；不作专利/商业最终清权声明。

## 3. 阶段A集中修改与完整功能源码

阶段A82a2f794...724a02c/完整M2A01–48合同已复制reference并保原PREPARED_NOT_RUN，不反写独立结论。本恢复batch仅scopeAll可由外部参数准入，内部十case按preopenAdmission/rejectFixture/cancelLateRead/writerPending/inspectKnown/inspectShort3/inspectUnknown/inspectSeek1s/bbbObserve/muxQualified顺序，在**同一个Job、同一个原worker**中运行。内部每case结束先查同原资源返回，所有source/native attempt/copy/hash/parse/seek/reopen与output attempt累计计数不重置；不能逐case各获得8MiB/16MiB。全scope同一60秒deadline，非10个60秒。

原CREATE_NEW O_EXCL|O_NOFOLLOW0600、实际copy全EOF/hash、同FD flush/sync/close及只读后交源保持，每子case新runId+case私有root，不覆盖或删旧文件。资格化六帧真实capture→原MatureMuxerBinding/FragmentedMp4Muxer/E6空EOS→原临时Sink→同writer/FD/任务返回→一次只读grant→真实FragmentedMp4Extractor正路保留；BBB仅观察，不送mux。MC-B01暂待不耗检查/不sticky、同原Provider/REOPEN1不变，不添加账本/新框架。

实际Media3 raw flags原样记录；预声明KEY_FRAME必须、只许末sample带LAST_SAMPLE内部marker，其他bit拒绝。送原mux前仅去LAST_SAMPLE，保key语义，输出按实际flag政策及同框架key/PTS/size/hash核对，绝不从JCodec keybool造raw1。实际AnnexB4六sample1340B与独立规范化hash比较，旧rawAU1360不混；CSD实际数组按真实顺序拼接AnnexB20比hash，不强说三initData，不注入SPS/PPS。独立DTS API无→UNPROVEN，不用PTS填DTS。原空EOS1200000仅意图，重开SeekMap/TrackOutput实际duration必须1200000，TIME_UNSET不补绿。

## 4. 有界必要自检与证据缺口

无变化host旧20父组（含MC-B01内部8）仅继承原证据，不重跑旧未知套件。改动处单独一次512MiB helper javac、一次256MiB/30秒JVM，实际production JAR在classpath前，public policy+apksig原返回均自然exit0/两流关闭。JVM40380 UTC03:39:23.977541至03:39:24.357180；**17项**含唯一scopeAll准入、十单case拒绝、实际rawflags/末marker/EOS/保护bit规则及四真APK签名；不加载Android job/媒体或伪造native对象验证功能。

预算源码同scope输入8MiB/native attempt与EOF/copy、output16MiBattempt含short/UNKNOWN无退款；controlled取消read预留1、writer预留4并计同scope。native实际返回、provider physicalBytes、parser Reader返回字节与scope inputReserved分列。控制输入/整批receipt/平台原返回和最终封存见计划，但以下是**当前明确已知缺口**，不派设备求证后才补：

* **REC-OBS01：** 中途case异常时method仍为失败子case，receipt仅在method==scopeAll时放caseReceipts，故此前完成case快照保留在原Job内存却未导出到pending/final。失败本case/firstError/原任务保管仍有，不代表此前没执行；不能声称整批外部证据完整。建议下一集中批按requestedMethod导出已有partial case历史及实际completedCount，保同字节预算，不新worker或重放。
* **REC-OBS02：** inputReserved是copy/native attempt（short3按实际native请求3预留，不可叫SDK请求3），inputActual/provider physicalBytes为已返；当前没有独立SDK requested累计及完整每phase requested总量。此字段UNAVAILABLE，不能从actual/readCalls推算。建议下一集中批在同原路径补有界分层观察。当前8MiB计量层要如实标native physical attempt，不偷换SDK请求累计。

两项详evidence/known-observation-gaps.json。它们来自coder最终静态复核，不冒独立缺陷裁定；当前两次构建窗口已满，没有第三次偷偷修编译/重跑。整包交负责人统一决定后续集中修复/独立B；不是可执行READY包。

## 5. 原返回、整批计划与准确预算

原worker cleanup后单调completed-start严格<60秒+实际同worker join与timer pending分列；case快照记录sameWorkerStillExecutingScope，不能说每case各join。最终source0/output0与runnerfinalizerOwnerAtReceipt可能1、super.finish外部返回/原两流捕获仍分开要求。设备未运行，因此实际FDsync/close/原task/case/外finish均NOT_RUN，不能用此次本机helper的exit0替它们。

execution-plan.json已绑定准确双APK/证书/runner/process/version和唯一scopeAll三参数、十内部case、无case/factory退款、停止规则。当前scopeId/serial/freshIdle/captureTool仍空；先完整独立B及处理上述缺口，才可另派准确设备scope，不自动使用旧许可。

未来计划逻辑平台调用6次：准确device fingerprint1、仅本APP/TEST存在性各1、准确新双APK各install1（不-r覆盖）、scopeAll instrumentation1。准确二进制出站**7590909B**；无额外fixture push，参数/命令每op≤4096B总24576B，logical outbound上界**7615485B**。preflight两流总786432B、install两流131072B、instrumentation所有pending/final两流1048576B、controller proof log1048576B，总logical inbound文本3014656B。每status JSON≤262144B，整批只一worker/60秒，不复用旧14ops或10次新scope额度。

上述是应用层控制/二进制预算；ADB transport framing未观测，明确非假精确wire计量，future capture/tool合同仍需准确绑定。任何未知/超时/不符hash/CSD/PTS/真实时长/不支持seek停止后继case，保管同原FD/thread/任务，未返回不reopen/retry/refund/release；不kill/二close/clear/reinstall/跨项目probe/无界logcat。当前设备/ADB/5037/占用操作0，编码生成/播放/解码0。

## 6. 完整矩阵、封存与交接

M2A01–48每行原oracle、静态/已编译/Android未运行/独立待审分类完整列evidence/m2a01-m2a48-completion-matrix.json；DTS、真实duration、partial导出、SDK requested、外finish、fresh设备等未证不填PASS。原冻结Android02 372、Android01 740、Container02 676、fork2738行逐hash不变，qualification03与新阶段A各原manifest完整保全；旧source/媒体/encoder/App/UNKNOWN不触。

封存evidence/recovery01-freeze.json及外置D1-20261021-MEDIA3-ANDROID02-BUILD-RECOVERY01-source.zip覆盖最终和首构建原源/产物/全流/owner/daemon快照、86原class+JAR/DEX/APK/签名helper、300实际strict消费metadata、准确fixture/来源、许可/SBOM、集中patch/阶段A合同/全scope计划/已知缺口。大cache/mirror非运行结果不封作产物；实际消费身份/审查副本已固定，旧mirror不改。纯Python tools/review_materials.py只核材料/hash/ZIP，不编译/Gradle/JVM/设备。

当前完成新范围内离线构建恢复、实际产物身份与集中源码/政策验证；**完整Android功能与观测仍OPEN**。主动交负责人完整包，不逐字段调试或自行设备；待统一新批范围。
