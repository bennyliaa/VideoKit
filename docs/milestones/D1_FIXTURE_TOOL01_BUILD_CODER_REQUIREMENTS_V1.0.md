# FIXTURE_TOOL01_BUILD 开发要求 V1.0

2026-10-21；用户最新明确继续推进项目。负责人正式派D1_FIXTURE_TOOL01_BUILD独立完整开发/离线审查批。原Android01候选/本地原session48945与17257保持冻结/UNKNOWN，强制收尾仍待用户明确批准；本批不能操作它们或证明host空闲，不阻断可隔离的工具开发。

依据Android01独立B报告845cd5920251c44beed2497d66d6843e5e6531e209d503cc93eb598f45fe2829的静态来源/API/提案审查，JCodec0.2.5 source1246282B SHA9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db，仅现有封存官方source/POM/FreeBSD记录及准确已有JDK21.0.10编译器。现由负责人批准本批一次独立离线工具构建，目的为取得准确编译产物hash及可审driver，不批准编码/fixture生成/产品运行。保留版权免责声明，专利/发布/旧FFmpeg许可不据此关闭。

新目录docs/coder/d1fixture-tool01，绝不改Android01及旧来源。实现真实六帧driver和明确构建源列表/全输入pin/固定javac与jar参数，无Maven/Gradle/联网/测试JUnit/annotation processor/构建插件或动态依赖。不升级或引入新binary/native。不使用PATH fallback，不执行Main/编码类初始化，不加载运行JCodec编码器；javac静态编译及打包不等编码器运行准入。若实际main源码有未获准依赖则记录阻塞，不造同名假接口/下载绕过。构建产物不进App/APK或产品依赖。

驱动沿原完整提案：原创确定YUV420J六帧256x144/5fps/无音频加密/rotation0、PTS0..1000000步200000、EOS1200000，H264Encoder keyInterval1/motionSearch0/DumbRateControl初QP20不得声称constantQP。明确AnnexB→AVCC一次转换、时基和每AU/CSD/hash实际采集字段，不伪造未生成golden。输出CREATE_NEW新私有固定文件，输入原创无原媒体读取。

必须实际实现计入attempt预算的Writable/Seekable通道薄包装，包括partial write、position/seek、MP4 header rewrite每次尝试累加，不用最终file size替代累计写入；单块64KiB/输出attempt16MiB/单sample262144B/六sample总1572864B/CSD64KiB。不能自写容器/codec或把预算包装当隔离。先登记原owner/句柄再分配；真实muxer finish/可选force/close和原worker外部join各自留证，deadline60秒仅关准入保留首错/UNKNOWN/强引用，绝不kill/interrupt/二close或删除未归还目录。该收尾实现本批仅编译/静态检查，生成行为NOT_RUN。

本批工具构建原进程单次并发1，使用已有固定JDK、新专属classes/工作目录，无共享缓存；-J-Xmx512m，main source/driver输入≤16MiB、全部构建输出≤64MiB，观察窗60秒只停止准入/保管原compiler不强杀/盲重试。构建前源清单全hash，构建后JAR逐class来源与准确hash、manifest主类及无额外文件；外部静态工具均一次有界调用。若构建失败保留原证据，集中报告不反复修构建循环。原挂起scene/62入口/新attach/设备/ADB/占用/Android/生成均0。

冻结完整source/driver/build recipe/compiler/input pin/JAR hash/许可证/SBOM/差异/预计生成命令及预算/准确NOT_RUN和原返回收据/seal ZIP。生成准入仍需负责人审准确已构建工具与driver，tester独立整包复审后另派；本批不产生.mp4，不进行JCodec运行/编码或Media3资格化。D1未过M0未启，P0/原UNKNOWN不变。

整批实现、自核与一次构建后完整冻结主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；不要逐问题交接，完整报告后再决定集中修复或交B。

## 2026-10-21 阶段A完整oracle集中补充

负责人已核D1_FIXTURE_TOOL01_BUILD_PHASE_A_REPORT_V1.0.md SHA256 1c823c521003c3384cc60a4396c559e5bb98eb5398a60a2d7979508f9c41a330，接受准备完成；FT01–FT28及6组计量数据均PREPARED_NOT_RUN，不是新driver缺陷或运行PASS。完整原source证据及机读oracle见tester阶段A证据目录。纳入当前整批，不逐项交接。

- 原MP4Muxer header、sample chunk及NIOUtils.writeLong8B回写可能单次write；driver通道要消费全部buffer，分块<=64KiB，每一次native尝试分别预留，short write后剩余请求继续时再次累计attempt。native非空0返回拒绝且不spin；异常后物理/位置UNKNOWN不重发/退款，空write0不调用native。10请求返3再7返7是attempt17/returned10；seek0回写8后attempt25/returned18而extent10/position8，勿混同。
- 封存source archive807条目、708Java/4435752B（635 org.jcodec+73 bundled JAAD）；闭包内JAAD不是缺外部依赖。保留Guava Preconditions Apache2.0、JAAD Public Domain/JCodec FreeBSD及免责声明的适用来源归属，不能以POM FreeBSD概括全树，不引新依赖或宣称商业清权。实际本批编译源列表依需要准确冻结，不无谓运行测试或新增下载。
- 固定MP4Muxer movieHeader使用当前Date；原创像素/PTS确定不能推出整文件每次hash确定。保持原成熟库不为伪造golden改时间戳，未来真实生成一次再冻结该文件实际hash；当前不预填媒体hash。

CREATE_NEW/reparse拒绝、原owner登记先于构造、finish/force/单close/同worker外部join与60秒保管按完整oracle落实；JCodec六Packet+finish不与未来Media3空EOS混同。当前仅一次javac/jar构建授权，原挂起进程UNKNOWN保留；不运行工具Main/编码初始化/生成媒体/设备。最终完成矩阵逐项区分静态实现/编译/未运行，完整冻结后另派B。
