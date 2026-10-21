# D1 FIXTURE SIX01 一次实际只读容器资格检查报告 V1.0

2026-10-21；tester；scope **D1QUAL01-CANDIDATE-001**。

## 结论

**BLOCKED_CHECKER_DREF_UNPROVEN_ORIGINALS_RETURNED**。按负责人准确新许可执行冻结helper一次，原结果 **BLOCKED_OR_FAILED_UNPROVEN_FIELD**，firstError **SELF_CONTAINED_DREF_UNPROVEN**。未授予HOST_CONTAINER_QUALIFICATION；生成媒体保持GENERATED_CANDIDATE_NOT_QUALIFIED。原文件句柄、库reader facade、检查worker和原进程均正常返回，无deadline/owner UNKNOWN。原JVM exit0只是进程自然返回，绝不代资格通过。

新增 **QUAL-B01/P2：检查器的数据引用准入与冻结生成库的既有输出不兼容**。静态源码表明helper仅接受UrlBox，而固定JCodec muxer addDref创建alis LeafBox。原失败分支未输出真实child类型/数量，故这里只把原因定为检查器实现/API准入限制的强静态证据，**不能直接声称实际文件引用类型已观察为alis，更不能判媒体损坏或要求改编码器重生成**。无检查器修改、重编译、重跑或后续测试。

## 准确许可与前后身份

依据 docs/milestones/D1_FIXTURE_SIX01_CONTAINER_QUALIFY_TESTER_REQUIREMENTS_V1.0.md（原字节另存 authorized-requirements-snapshot.md）。生成B原报告aee4808b5eab91b45dc21f3001519291ff5eb8640271c47f09bf54d6a63e8951仅证据/身份通过；检查器准备原报告0e98643827cdb7cef7841965c34bcdc6a039afe5956006bf1f979e8cf0920e73仅编译通过，历史结论未改。本次新许可才批准实际JCodec raw demux/box/SPS-PPS读与表示转换，未批准encoder/decoder/Main生成/Android/Media3。

输入仅 D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4，**8849B，SHA256 19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c**。前后生成seal ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4全部38记录实际大小/hash不变，实际readonly且路径各级无reparse/symlink。没有换文件、改字节/属性、搜索其他候选或重新生成。

检查器准备manifest6c570d2ac81c20f3bebf28d141c92edf85a153ccecfe7462e367ea8f011d412f全部13证据及原报告前后核不变。helper源码21809B SHA256 a757ecc7587c9a02ce817152f092659863ff3370e6e594bef5acbe4a08ad3544；整个classes文件集合严格等于合同3class，逐个实际hash一致、无额外class。生产JAR1954730B SHA256 c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd，固定JDK release/java/javac/jar/modules准确合同前后相同。没有调用编译器或重建库。

## 一次原进程和完整两流

唯一argv逐项吻合许可：D:/Android/Android Studio/jbr/bin/java.exe，-Xmx256m，-XX:-UsePerfData，-cp，冻结helper classes;准确tool02 JAR，com.videokit.fixturetool.Six01ContainerQualifier，--expected-sha256=19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c，--expected-bytes=8849，--scope=D1QUAL01-CANDIDATE-001。完整分项见 control-001/owner.json。全新本证据根/control-001，原owner在preflight和Popen前登记，shell=False/stdin null，清除五项Java注入环境与CLASSPATH，固定cwd/TEMP/TMP/JAVA_HOME；仅一次原Popen，无参数fallback或新路径。

原PID24020，2026-10-21T01:36:34.186953+00:00启动，2026-10-21T01:36:35.894814+00:00自然exit0，原控制器elapsed约1.719s；原stdout/stderr句柄在原进程返回后均关闭。完整原stdout **2594B**、stderr **0B**，严格UTF8总量≤1MiB；恰1条原final、0pending、0杂行，all-original-receipts与原字节重新解析相等，无tail或只取exit0。controllerTimeoutUnknownSticky/outputLimitUnknownSticky均false，kill/interrupt/terminate/attach/二close/退款/重试0。

原worker最后cleanup完成点elapsed **175346000ns**、observer175882500ns，completion-start重新核对一致，远低于60000000000ns；timelyBodyAndOriginalJoin=true、sameOriginalExternallyJoined=true、clock/deadline unknown false。此点是body最后受控语句，实际同原worker join和原JVM退出独立记录，不混为同一个事件。

原InputOwner登记于native open前，同一只读descriptor完成SHA/EOF、root扫描与demux；终态CLOSE_RETURNED，originalCloseEntered/sameOriginalCloseReturned=true，uncertainSticky=false、nativeInFlight0/operationNONE。库demux facade close通过同一个owner guard归还，finally到guard不二次native close；原receipt originalInputAndLibraryReaderReturn=true、sameOriginalCheckerThreadJoined=true。guard/同原线程顺序的依据为冻结源码，实际原close返回与原join由本次收据独立确认。

## 实际预算和停止点

原累计mediaReadRequested **9747B** ≤1MiB，实际returned **9746B**，read **12次** ≤4096、seek **14次** ≤128、实际native EOF **1次**。其中完整文件hash请求8849+EOF预留1=**8850B**、returned8849B；后续root/demux重复读请求/返回均**897B**，不能只按文件大小结算。分项8850/897由冻结控制流和最终计量差推导，原收据没有逐read trace，不能冒称逐调用独立事件日志；总量与原seek trace完整保留。

单次read上限64KiB由冻结InputOwner代码执行；heap256MiB/worker1/60秒/receipt1MiB沿原合同。实际到失败点尚未进入样本/CSD分支，没有样本buffer/转换的运行覆盖；6sample单262144/CSD64KiB/NAL64/root16/box512/depth16等是守卫，不将未到达分支写作实际媒体验证通过。成熟库内部metadata内存界仍未证，未做坏atom或资源探针。

原seek trace可见root两次扫描与moov读取，最后adopted position **8849**；close后receipt仍准确LAST_ADOPTED_BEFORE_ORIGINAL_CLOSE，非关闭后重新测量。完整SHA及实际EOF为已运行事实，原文件hash与准确许可相等。输出媒体0，仅本报告/控制证据。

外部身份审计媒体读：前38封存hash8849B、原返回后38封存hash8849B，总**17698B**；本批不解压ZIP媒体成员，归档只作控制文件整体hash。JDK/JAR/helper/控制文件身份读另类，以上不倒灌原helper9747预算、不退款，也不冒物理磁盘IO。原生成账本不改。

## QUAL-B01/P2 与字段缺口

冻结helper inspect的条件为：真实mdia.minf.dinf.dref存在、children恰1且children[0] instanceof **UrlBox**，否则抛SELF_CONTAINED_DREF_UNPROVEN；下一步才核UrlBox.getUrl/null与flags self-contained。本次准确停在第一条件，不能断言是哪一个disjunct失败，也没有达到下一步flags读取。

冻结成熟库 AbstractMP4MuxerTrack.addDref实际创建DataInfoBox/DataRefBox，并添加 **LeafBox Header("alis")，body{0,0,0,1}**；DataRefBox.parse经NodeBox，LeafBox.getData可取原body但不是helper当前要求的UrlBox语义API。这里仅静态读取既有源码定位接口不兼容，**没有手写MP4/alis字节解析器、没有额外运行探针或再次demux**。详细带行号/源码SHA片段保存在 qual-b01-source-derived-finding.json。

检查器在失败前的控制流经过raw demux、root完整性、单轨/尺寸/matrix/保护box等前置断言，但没有发出它们的结构化实际观测；receipt.actualContainerObservation为null。不能把“前面未抛异常”或固定期望值填成完整实际轨道报告。真实root列表、轨道数/codec/尺寸/rotation/保护信号、dref类型，均准确null/未完整举证。

后续avcC/SPS-PPS/CSD、stsz六样本大小/字节hash、AVCC/AnnexB/NAL/IDR/keyflag、stts/ctts与PTS-DTS、各层真实duration1200000us、第七packet EOF全部 **NOT_REACHED/NOT_PROVEN**。没有运行decoder或真实Media3，原raw AU含PS的内部hash仍不能代文件AVCC或归一AnnexB hash。

本轮是checker实现/API准入限制阻塞，文件缺陷**NOT_PROVEN**；没有观察到identity、JVM启动、捕获流或原返回的环境错误，但未到达的API/环境分支仍不能算已验。QUAL-B01不会回写已发送准备报告，编译成功原事实保留，首次实际失败另报告。

## 集中建议与停批

需负责人另签检查器修复准备范围，先确认成熟库真实语义API能否验证其既有alis/self-contained表示，再独立审查；若API能力不足则继续准确BLOCKED。不能删data-reference门、白名单接受任意引用、套expected golden、自写parser、修改编码器/原MP4或重复本scope求绿。本轮仅提出修复要求，没有修改或编译新helper，准确失败报告与所有原返回先冻结交负责人。

本范围已结束，不启动后继资格/Android/Media3/解码/隔离格式/READY COMMIT/播放。原48945/17257 UNKNOWN未poll/attach/查询/终止，不以本次原资源归还声称host全空闲；历史N2不重复ABORT。D1未过、M0未启。
