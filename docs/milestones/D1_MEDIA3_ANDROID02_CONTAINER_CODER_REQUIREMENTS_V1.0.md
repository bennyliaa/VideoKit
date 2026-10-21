# MEDIA3_ANDROID02_CONTAINER 开发要求 V1.0

2026-10-21；负责人正式派D1_MEDIA3_ANDROID02_CONTAINER完整功能批，开发/离线验收准备，不是设备执行令。

已核独立实际报告a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926，接受此8849B/hash19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c文件有限HOST_CONTAINER资格；单AVC256x144/无音频/identity matrices/6样本/PTS0..1000000每200000/总1.2秒真实文件证据可用于本批良性固定fixture准入。不是全AVC语法安全/Media3/隔离内容/READY COMMIT/播放PASS；原QUAL01BLOCKED/所有历史FAIL不改。

新目录docs/coder/d1media3-android02，以完整已静态审Android01及Container02源为基线，不改旧冻结；集中完成：
1. 在独立无权限空数据Android实验app/test中嵌入上述准确合成只读fixture及来源/qualification manifest，原BBB片只保留原授权提取观察，不改参数送mux门。实际asset/私有副本每次完整EOF/hash及CREATE_NEW/原同步close/只读授予，固定路径不任意URI，固定fixtureSha/runId/case入参。新version明确，不升级com.videokit.app/不操作其他项目。
2. 接通真实Media3 1.9.3 DataSource/readAt→Mp4Extractor，资格化fixture真实轨道/6样本/CSD/AnnexB规范化/PTS/DTS能力边界/seek/短读/未知length；actualMedia3结果与主机JCodec已证事实独立比对，不拷manifest充观测。原sample未知数仍取实际，不硬填golden。
3. 实现此前muxQualified正路：真实capture6→现有MatureMuxerBinding/FragmentedMp4Muxer→原临时OutputSink→原writer/flush/close/任务真实返回→同授予只读Provider→真实FragmentedMp4Extractor重开。实际样本hash/CSD/PTS/时长/EOS规则先声明，容器变化不比较wholefilehash相同，原6payload+空EOS非第7帧。Android原FD/force/fsync/close能力与成功事实分列，原hostSink错误/partial UNKNOWN不重发退款。
4. 准备完整有限Android方法覆盖正常单轨链、known/short/unknown、seek1秒按真实SeekMap准入、capability-before-open、取消迟返及writer未归还不重开/不提前释放、不符fixture先拒绝；继承原MC-B01/FT修复不重引。尽量同一集中app/test构建，不拆成按钮级交接。不得转码/解码/编码/播放/Surface/音频/MediaCodec/ordinary-isolated GPU探针。

Media3原固定成熟框架1.9.3/strict locks和metadata许可保持，无JCodec或审计fork加入APK/产品，host qualification仅data来源证明，不把JCodec替Media3后端。原source2/每源1queue0/输入8MiB累计含copy/hash/parse/seek/重开、输出16MiBattempt/块64KiB/每sample262144/恰6单AVC256x144及原时序不扩；同一scope各phase预算预先统一说明，不通过换factory重置。deadline60秒只关准入、原Job/FD/thread保管UNKNOWN，无强停/二close/重试/删旧文件。

同UID新测试进程仅良性实验/地址空间，不冒RCE/J11/P0；真实恶意atom内部资源隔离/权限等门仍OPEN。不得凭host格式检查设置validated/产品READY/COMMIT或签HOST_ISOLATED_FORMAT_V1；本批要证明实际容器结构链，不替产品最终隔离格式/业务发布。

当前设备操作0；允许必要一次集中app/test离线strict构建及有界非媒体自检、准确app/test身份/签名/DEX/source/JAR消费与fixture来源/原返回审计。冻结完整主报告/范围完成矩阵/产物/许可/精确case runner及方法/全操作文本二进制出站控制预算/停止条件/证据出口/seal ZIP，主动报负责人。设备使用已有用户持续授权，但负责人核完整包及tester独立离线审后另派准确fresh空闲新scope；其他项目占用不操作不轮询，不复用停止scope。原48945/17257 UNKNOWN保持，不触原进程/attach，不把新本地通过当host全空闲。D1未过M0未启。

完整批次开发自测冻结后交负责人，不自行设备或分片交付；有集中阻塞如实报告，不换框架/放门求绿。

## 2026-10-21 Android02完整阶段A矩阵补充

负责人核82a2f7942023d16a7cf98a4e5c24be052e2d8ebf946b401ab63742bd2724a02c，接受M2A01–48准备完成/全部PREPARED_NOT_RUN；非候选源码缺陷结论。完整合同见tester D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_EVIDENCE。当前恢复构建/集中源码修复纳入以下口径，旧冻结不改。

host SPS7/PPS3与单AnnexB20并非Media3 initializationData固定三项；原raw AU1360不是实际container AVCC/normalized1340。Media3 raw flags按实际返回记录，不从JCodec keyboolean预填1，预声明规范化后再同框架输入输出比较。实际独立DTS在TrackOutput timeUs API不可得时保持UNPROVEN，不用PTS假造；EOS1200000意图不代真实fMP4 duration/SeekMap。不可证明字段保留明确缺口，不改golden求通过。

原worker单调last-body点+实际同workerjoin与platform finish外部返回分开，join+isAlive不代FT-B02时间门；MC-B01 pending不消耗检查/记首错，同原Provider REOPEN1；FDsync能力与实际返回、source0和runnerfinalizer owner1分别留证，不宣称receipt时finalizer已退出。

准确批scope输入8MiB全copy/hash/parse/seek/reopen及各case累计，输出attempt16MiB同样全口径，不因factory/case重置；单case界与wholebatch账分列，原native/SDK requested/actual短读及控制字节分层。固定全部case/两APK实际hash与实际出站bytes/状态receipt/控制开销重算，不复用旧14ops/设备scope。若当前恢复需要源码变更按已授集中最多2构建范围处理，日志差异全留；交通问题不盲重试。
