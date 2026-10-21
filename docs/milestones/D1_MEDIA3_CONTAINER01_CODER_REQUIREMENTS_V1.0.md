# D1_MEDIA3_CONTAINER01 开发要求 V1.0

2026-10-21；负责人正式派发。D1功能簇，非M0启动。

基线：INPUT_SINK05独立报告6cd4621901dddcc9ad7d11ddca4248eaac2a1ae7e45513ca257a35055f1b6973有限离线PASS；B06/B07指定修复关闭，旧FAIL/UNKNOWN保留。冻结来源docs/coder/d1input-sink05，主报告25503fe0f72310db4b22eeb23875fbdc17f782092ebd4e0bf132baf2fb3f82a7。

目标：从真实Media3 DataSource/readAt走到成熟提取器，再从现有FragmentedMp4Muxer薄适配走到临时Sink及只读重开，推进实际容器链路，避免继续停在编译绑定。真实解码、平台FD/fsync、隔离内容验证、业务COMMIT和播放效果不由主机结构检查替代。

保持既定成熟框架精确版本及许可、strict锁和metadata验证，不造同名假Media3接口。预算沿用输入8MiB、输出16MiB、块64KiB、源2/每源在途1/排队0；muxer单AVC256x144、最多6样本/2秒、每样本262144B。不自动扩范围。全P0/独立Kit/Flutter边界保持，D1未过M0未启。当前纯离线，无设备/ADB/占用检查，无并发Gradle/共享缓存写；历史N2停止不约束新批。

## 一次完整开发范围
1. 新目录docs/coder/d1media3-container01开发，旧冻结完全不改。实际Media3 1.9.3提取器经已通过DataSource读取，记录轨道、样本边界、PTS及有限seek/EOF/unknown-length；能力拒绝必须先于打开。只支持本批明确MP4范围，不自造容器或解码器。
2. 将现有MatureMuxerBinding与TemporaryOutput真实库运行链路接通：合法带来源和hash的编码fixture/原已批准只读sample.mp4，在既有AVC界内写入，writer真实返回、flush/close、只读重开由实际成熟提取器校验轨道/样本/时间信息并记录全EOF/hash。原sample.mp4保持只读不入源码交付；不适配其不符参数或未获证明的样本，不伪造有效NAL。先核fixture匹配，不能满足时明确具体阻塞及合法生成方法。
3. 主机结构重开证据独立命名，不签发HOST_ISOLATED_FORMAT_V1，不凭主机解析调用产品READY/COMMIT。真实平台API不能离线运行时保留NOT_RUN，交付实际已运行部分与准确平台缺口，不用替身冒充真库。不得扩建通用诊断/发布系统。
4. 集中覆盖短读/截断/畸形有界输入、seek边界、取消迟返、写入partial UNKNOWN、flush/close故障、结构校验失败不能READY，以及原线程/observer真实返回。保留05全部既有边界，复用已核工具而不重建整套框架。
5. 必需同版本提取器新依赖可收集官方来源/许可证并严格验证实际消费；未经来源准入的artifact不运行，不升级、不关闭校验。允许必要一次集中严格构建；tester阶段A只外置已有JDK，不用Gradle或共享缓存。

## 整包交付
完成实现、自测和必要构建后冻结：主报告、接口决定、实际执行/NOT_RUN矩阵、来源许可、可重放入口、源/JAR实际来源证据、预算资源归还、hash seal及ZIP。对无法主机执行路径给出具体受限原因及后续最小实机条件，不把静态检查计作效果通过。整批完成主动通知负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；报告发送失败保留，不绕过。负责人审阅后才正式交tester阶段B，缺陷集中修复。

## 2026-10-21 阶段A完整审阅补充（当前批次适用）

负责人已核阶段A报告edb4cd48b9bd1c04f0d1f9ddff5f80a6a16257e0055a7aa4c3eb000a303870d7，接受BASELINE_REVIEW_COMPLETE_WITH_GAPS；不是新实现FAIL，32项用例为待执行。继续当前整批，不逐项交接。

- A-G01真实muxer在最小JDK构造首遇android.util.SparseArray链接限制。须明确实际执行环境与所有主机测试端口，不假定补一类即可完整运行。真实Media3代码与主机平台替身分别留证，替身环境结果不冒Android实机效果。
- A-G02封存extractor/decoder1.9.3身份可核，但本批新增运行闭包来源许可尚缺；按本单既有授权补固定官方POM/module/适用许可及strict实际消费后才运行，不升级/关校验或伪造同名Media3。
- A-G03当前尚无资格化六样本AVCfixture。先核已批准只读sample参数与权属；不符则记录具体阻塞，允许采用已有准入工具/已有授权合法合成内容，不自动新增编码器或扩大FFmpeg范围。fixture须来源/工具版本参数许可/hash/初始化数据/每样本NAL表示及hash/keyframe/PTS/时基。不得4B或伪NAL充有效样本。
- A-G04原E6 finish恰6个payload，0B flags4 EOS非第7帧，EOS=last+200000；payload PTS上限不等总duration，正例建议PTS0..1000000步长200000、EOS1200000。提取器END_OF_INPUT/sniff不等全底层EOF/hash；seek绝对位置/stream终点不等open返回remaining长度。事先声明NAL与时基比较规则。

完整判据与MC01–MC32见docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_REPORT_V1.0.md及其PHASE_A_EVIDENCE/independent-cases.json。coder集中实现/自测并在最终报告逐项映射可运行证据和准确NOT_RUN；tester只在负责人审新冻结后执行B。原预算/保管归还/P0及D1未过M0未启不变。
