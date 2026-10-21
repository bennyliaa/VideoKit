# D1_FIXTURE_TOOL02_FIX 集中修复完整交付 V1.0

2026-10-21。新目录D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool02已完成两项P2的集中修复、一次编译打包和获准的非媒体源码/新生产JAR优先实际自测。**两条路径各29组通过、原进程自然exit0、所有已启动受控worker正常放门并join；这是coder有限自测，不自行关闭FT-B01/B02，等待tester独立完整复审。** Main/Job.run/编码器/MP4Muxer/媒体生成/Media3资格化均0；D1未过M0未启。原48945/17257 UNKNOWN不读取、不诊断、不处置，不由本批证明host空闲。

## 1. 原报告、来源与集中差异

正式要求及原独立报告57107a238dc62d11fa40b18b95bd283988388a2fcf10f8cbed08acb78eb759da完整保留。原结论FAIL_SOURCE_DERIVED_WITH_RUNTIME_NOT_RUN是源码推导，不回写为旧动态失败或旧PASS；原tool01身份/许可有限通过继续继承。新候选仅改原driver的AttemptBudgetChannel/SixFrameDriver，新增一个针对同原worker的WorkerDeadline和单独FixtureToolFixCheck辅助源；ReceiptJson、708成熟JCodec/JAAD源码逐字不变，无新依赖/同名假类/反射修改状态/通用诊断或时间框架。

固定source archive1246282B、SHA2569945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db，708Java4435752B，635org.jcodec+73bundled JAAD。旧tool01/Android01/更早共8725冻结文件逐hash不变；原独立B manifest/报告/证据全部保持。许可继承FreeBSD原版权免责声明、JAAD Public Domain/JCodec FreeBSD、Guava Preconditions2007 Apache2.0和全文/逐源原头，SBOM02逐项列明，不扩大专利/发行/FFmpeg许可。

## 2. FT-B01：原调用、物理事实与采纳分层

通道以同一个原NativePort接口接原FileOwner；Production Job.nativePort只返回既有final writer，不重开/替换handle。最小Owner.afterNativeReturn接缝生产默认no-op，测试用真实门闩停同原回调尾段，不反射改状态。

同锁内把每个write/seek/position/size/force/close的进入、返回已观察与采纳分开：进入时inFlight=1、adoptionPending=1；原端口调用返后inFlight=0而pending仍1；计数、buffer位置、lastAck、结果事件采纳在同一个临界区完成，最后才清pending。**原调用在途或已返未采纳时，actualPhysicalPosition/Extent一律UNKNOWN；旧值仅lastAcknowledged/下界。** 原native/observer异常仍sticky物理UNKNOWN，不新开查询handle，不退款/重发。字段是该原端口/采纳边界事实，不把受控内存端口回执冒作OS原FD/fsync证据。已adopt的close后scope明确LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE，不称当前仍有打开FD的测量值。

每次native写前按requested≤64KiB预留、positive partial按actual返回前移原buffer并对下一剩余请求重新计attempt，header rewrite不退款，native非空0/负值/>request拒绝不spin。16MiB/offset减法界和512非终态operation事件满前拒绝保留；close不能被事件满卡住，仅一个单独终态close record、同原native close至多一次。pending不遍历活列表；已完成事件逐map复制，外部修改snapshot不能修改原事件。

受控WRITE/SEEK/FORCE/POSITION/SIZE/CLOSE分别真实经过“端口内部已改变内存物理事实但未返回”与“端口已返、同原回调未返/未采纳”的两个门，验证UNKNOWN与lastAck分层；finally开所有原门、join同原worker后再验最终采纳。不是只把布尔变量预设成期望值。

## 3. FT-B02：单调完成点与同原实际join

WorkerDeadline只为这个工具原worker服务，生产用System.nanoTime，测试仅传LongSupplier/AtomicLong参数。启动前登记同原Thread与单调start；Job finally在全部原cleanup/状态采纳后，以同原worker最后一个受控语句记录completion。**这是body/cleanup完成点，不是OS线程退出时间戳；实际同原外部Thread.join仍为独立必需事实，marker本身不能给成功。** 完整契约见generation-plan02.json，未用observer时间伪造worker完成时间。

duration60000000000ns。signed(now-start)按nanoTime模回绕在非负半区间解释，duration须0<d≤Long.MAX/4；等号elapsed==duration算迟返。负差/观察倒退/不可判半区间保守UNKNOWN。记录的同原完成点在期限前，可在观察者晚采样时仍判及时；真正到期后才完成、未完成时已观察到期限、显式UNKNOWN或无有效完成点都sticky，晚返不能升级。join超时返回或isAlive都不再作为成功/期限判断依据，Main最后一定经joinSameOriginal实际join同一worker，并重新采纳期限状态，未知时不清ORIGINAL。

实际自测包含timedjoin已返回而原worker仍待门、随后在clock101/期限100完成再由clock102观察的原时序；原clock90及时完成、clock200晚观察；等号、真实System.nanoTime20ms等待到期再原返回、模回绕、clock倒退、已经UNKNOWN后原返回、以及marker后真实线程仍在受控尾段不能冒join。单调测试钟不是生成/编码实际运行证据。生成body60秒配置只做类型/静态核对，未跑60秒编码作业。

## 4. 一次集中编译打包与准确来源

固定现有JetBrains JDK21.0.10，java/javac/jar/release/modules hash与原许可保留；无Gradle/Maven/联网/共享缓存/新二进制下载/注解processor/插件，-proc:none/-implicit:none及空专属classpath/sourcepath/processorpath。一次javac把708原source+4driver+1checks共713源一次类型检查，4492852B≤16MiB，-J-Xmx512m；一次jar顺序打包，两个原Popen句柄均自然exit0、原输出handle关一次，未超时/kill/interrupt/重试。

工具artifacts/videokit-fixture-tool02.jar，**1954730B，SHA256 c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd**；Main-Class仍com.videokit.fixturetool.SixFrameDriver，仅身份声明没有执行。985个生产class和5个测试class全部匹配实际本次原javac输出/复制及SourceFile/明确输入hash。工具JAR只含985生产class及准确manifest/许可证资源，5个测试class不入JAR。source路径用原classes，production路径仅工具JAR优先+test-classes，无raw production fallback；类加载/真实CodeSource证据保留。构建返回实际输出9578896B，含原classes、production/test复制、JAR、资源副本、argfile/日志/收据，不去重冒实际占用；最终全包+ZIP仍核≤64MiB。

原javac历史PID34216 UTC00:41:12.750665–00:41:19.345274；jar历史PID29200 UTC00:41:35.490619–00:41:41.870093。它们是当次原调用回执，不作未来PID身份凭据。编译上游warning保留。编译观察窗60秒仅关后续准入/保管同原Popen而非强杀；本次未触发，编译器与测试/未来生成期限分别记账。

## 5. 实际受控非媒体自测与原返回

tools/run_checks.py为本次实际执行的原控制器，完整argv/cwd/stdout/stderr/class-load log/owner/起止/PID/生产JAR hash在evidence/nonmedia-001。源码和production JAR优先各29组，58组总计，两个原JVM均自然exit0，实际整批约0.485s≤60秒，每组观察≤5秒。运行参数-Xmx256m（Java启动器，编译器才用-J前缀）、串行每进程一个；无反射/动态case选择/强停/盲重放。类加载记录仅加载JCodec真实SeekableByteChannel接口，未加载SixFrameDriver/Job、任何codec或muxer。

29组涵盖：EX01/02 partial10返3+剩7返7、header8计attempt25/returned18/extent10/position8；EX03原额外写1后抛异常的known3/物理UNKNOWN/no retry；0/负/>request/空write；16MiB-8虚拟已有预算+8再+1在native前拒绝；负/overflow/range、512事件满仍能单close；错worker/read/truncate拒绝；六操作双窗口snapshot；事件map脱离原列表；原close抛异常不二close；上述单调时序/真实workerjoin各边界。

预算大数通过构造器明示prior meter reservation测试缝，仅保守占用attempt，receipt明确initialMeterOnlyReservation且不冒物理I/O；production永远传0。两路径合计byte数组36928B、native请求1248B、受控实际写入1148B，均≤64KiB，不分配/写16MiB。JDK/JAR/class-load及文字收据是另列的构建/控制元数据，全原日志保留且总体64MiB界内。原门闩均2秒有界等候，finally正常countDown放门并join同原worker，无故意永久等待；观察超窗停新准入并保留同原process，不kill。

每路径有1个刻意close-throw的纯内存对象UNKNOWN，保留引用并断言不二close；它没有OS FD/异步资源，不伪报平台closed。所有实际已启动测试worker和JVM均正常归还，不把“预期内存UNKNOWN被识别”写作真实FileChannel原close已证。

FT01–28同步映射及6算术例回归在completion-matrix02.json；只计通道/时钟/内存门/真实受控join的实际范围。CREATE_NEW/reparse/真实FileChannel/force/fsync、Job.run、真实六AU/CSD/NAL/MP4/媒体生成/Media3仍NOT_RUN，不把58组绿升格为这些功能PASS。FT-B01/B02独立关闭仍PENDING。

## 6. 冻结、入口与交接边界

完整source/4driver/1checks、990真实编译class及复制、工具985class JAR、许可/SBOM、原构建与两路径日志/字节来源/差异patch/集中矩阵均冻结。seal evidence/fixture-tool02-freeze.json，ZIP D:/CodexProjects/VideoKit/docs/coder/D1-20261021-FIXTURE-TOOL02-FIX-source.zip；准确行数/hash/全口径bytes由seal列出，不含JDK/cache/key/native/媒体。

只读材料入口tools/review_materials02.py --output 新D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE绝对子目录，只核字节/JAR/原旧seal，不JVM。受控动态复审仅在负责人另签B范围后使用tools/review_checks.py --output 另一个新独立子目录：核seal后执行同一固定非媒体check两路径，无编译/生成，不写候选。REVIEW_ENTRY.txt明确许可/参数/次数/门；原run_checks.py保持当次原字节不重跑，build_one冻结后拒绝重建。继承tools/audit_build.py仅作为原01纯class parser代码字节来源，当前仅AST提取函数，未执行其不适用top-level；本批记录脚本为audit02.py，冻结后不要运行任何写候选脚本。

原旧12套共8725身份及tool01独立FAIL证据保持；原会话/一次许可/历史UNKNOWN/账目不碰。当前只提交集中修复与有限自测、等待完整独立复审；不自关两P2，不自动接生成。下一步仍要负责人准确新生成tool/scope/预算与原owner批准、实际媒体immutable manifest，再独立真实Media3资格化和新Android mux候选。原成熟库Date不改，未来整文件hash只有实际生成后才取得，媒体/AU/CSD golden均null。D1未过、M0未启，P0/J11/C13/发布专利旧门不借此关闭。
