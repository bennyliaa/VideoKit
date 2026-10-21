# FIXTURE_TOOL02_FIX 开发要求 V1.0

2026-10-21；负责人正式派D1_FIXTURE_TOOL02_FIX集中修复及有限非媒体自测批。

已核独立完整报告D1_FIXTURE_TOOL01_BUILD_PHASE_B_REVIEW_REPORT_V1.0.md，SHA256 57107a238dc62d11fa40b18b95bd283988388a2fcf10f8cbed08acb78eb759da；结论FAIL_SOURCE_DERIVED_WITH_RUNTIME_NOT_RUN。两项是冻结源码/产物字节可达反例推导，尚非动态复现，不夸为实际文件损坏或编码失败。原tool01身份/许可材料有限通过保留，旧FAIL/UNKNOWN不回填。

FT-B01/P2：AttemptBudgetChannel原native write/seek进入到结果采纳完成间，pending receipt可能把旧logical位置/extent冒作确定actualPhysical字段。集中统一全部适用write/seek/force等在途与已返回未采纳窗口的快照语义：实际物理位置/extent未知时明确UNKNOWN，旧已知值只作lastAcknowledged；attempt预留/已知实际下界/异常UNKNOWN/事件容量保持，不新handle/强停/二close/退款。原调用返回与原observer采纳门分别记录，快照自身一致且不遍历原worker正写列表。

FT-B02/P2：timed join到期后isAlive采样前迟到完成，可漏deadlineUnknown。采用明确单调deadline及同原worker实际完成时间/时序事实，保证deadline已过才完成不能升级；不能仅isAlive/Future done/调用者观察时间代原完成。合法到期前完成但观察者晚采样与真正迟返要按明确契约分别判定；实际同worker join仍必要，firstFailure/UNKNOWN sticky、不kill/interrupt/重试。单调计时的溢出/等号边界规则明确，记录实际完成点及原return归还边界，不因注入测试钟宣称真实编码已运行。

新目录docs/coder/d1fixture-tool02，原JCodec708源码/依赖/许可及旧候选完全不改。生产仅必要driver/channel/最小可测等待决策抽取，不造通用时间框架或诊断设施。允许一次集中javac/jar构建新工具+独立测试辅助（测试类不入工具JAR），沿固定JDK/input16MiB/output64MiB/512m及原构建owner60秒观察界；失败保留集中报告不循环构建。

本批新增明确非媒体受控自测范围：只运行driver通道包装和抽出的等待/快照逻辑，不调用SixFrameDriver.main/Job.run/H264Encoder/MP4Muxer，不初始化编码器/生成视频。允许固定内存SeekableByteChannel端口、单调时钟参数及受控worker门闩/回调尾段最小测试接缝，禁反射改生产状态/同名假成熟库。需实际原调用在内存端口进入→物理完成→采纳的各顺序，partial/header rewrite/zero/exception/capacity/16MiB先拒绝、write/seek在途与已返未采纳快照、真超时及到期前完成晚观察、到期后完成/等号边界、原worker真实join。FT01–28既有静态/计量例同步回归。

测试每原进程-J-Xmx256m/单进程串行/每组观察窗最多5秒/整批60秒；所有原门闩和同worker由finally正常放行与join，禁止故意永久挂起，观察超时停止新增准入并保管原进程/引用，不强杀/盲重放。非媒体字节总≤64KiB，预算大值用计量预留测试接缝而非实际分配16MiB。完整日志原argv/返回/对象来源/源及生产JAR优先路径、测试端口清单与NOT_RUN边界记录；若安全原返回条件不能满足则不启动该例、明确阻塞。

旧session48945/17257不读取/轮询/attach/处置，无设备/ADB/Gradle/共享缓存/联网/新依赖。这次独立范围不证明host空闲或代旧原返回。真实编码/生成/Media3资格化仍未批准，D1未过M0未启。完整新工具/测试源码/入口/来源/hash/receipt/集中矩阵/seal ZIP冻结后报告负责人，再正式独立整包复审，缺陷集中回交。

整批完成主动报告负责人01a107c3-2bf9-7fa0-94a0-234258ca6774，不逐问题交接，不自关两P2。
