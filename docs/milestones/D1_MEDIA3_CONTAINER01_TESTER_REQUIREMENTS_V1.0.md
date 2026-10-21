# D1_MEDIA3_CONTAINER01 测试要求 V1.0

2026-10-21；负责人正式派发。D1功能簇，非M0启动。

基线：INPUT_SINK05独立报告6cd4621901dddcc9ad7d11ddca4248eaac2a1ae7e45513ca257a35055f1b6973有限离线PASS；B06/B07指定修复关闭，旧FAIL/UNKNOWN保留。冻结来源docs/coder/d1input-sink05，主报告25503fe0f72310db4b22eeb23875fbdc17f782092ebd4e0bf132baf2fb3f82a7。

目标：从真实Media3 DataSource/readAt走到成熟提取器，再从现有FragmentedMp4Muxer薄适配走到临时Sink及只读重开，推进实际容器链路，避免继续停在编译绑定。真实解码、平台FD/fsync、隔离内容验证、业务COMMIT和播放效果不由主机结构检查替代。

保持既定成熟框架精确版本及许可、strict锁和metadata验证，不造同名假Media3接口。预算沿用输入8MiB、输出16MiB、块64KiB、源2/每源在途1/排队0；muxer单AVC256x144、最多6样本/2秒、每样本262144B。不自动扩范围。全P0/独立Kit/Flutter边界保持，D1未过M0未启。当前纯离线，无设备/ADB/占用检查，无并发Gradle/共享缓存写；历史N2停止不约束新批。

## 阶段A：立即并行离线基线与用例准备
只使用已冻结INPUT_SINK05及其封存真实Media3库/上游E6Muxer，核对真实接口可执行范围、fixture许可与参数、实际提取/重开结构判据、畸形/短读/seek/取消/partial UNKNOWN及资源归还用例。外置已有JDK/独立目录，不Gradle、不修改共享缓存、不读新浮动源码。可做准确冻结基线实际边界验证，不重复无变化整套自检。产出一份完整阶段A报告/用例与缺口，不以准备代替新实现验收。

## 阶段B：负责人核完整冻结后另行正式交测
当前不提前启动B。届时独立核seal/ZIP/原冻结及许可严格实际消费，运行文档入口和生产JAR，并自行构造有界独立样例核真实Media3调用、实际readAt→提取与muxer→Sink→重开结构路径；不只信coder计数。核AVC参数/PTS/样本边界、短读/EOF/seek/损坏/取消和输出故障，原observer/worker返回后才释放。结构重开不得冒充隔离内容验证、业务READY/COMMIT或真实播放。真实平台路径仍单列NOT_RUN，不为好看引入假接口或弱化P0。

阶段A和之后正式B各自整批报告给负责人01a107c3-2bf9-7fa0-94a0-234258ca6774；独立发现集中报告，由负责人统一回交coder修复回归。不逐问题来回调试，通知失败保留不绕过。

## 2026-10-21 阶段A完整审阅补充（当前批次适用）

负责人已核阶段A报告edb4cd48b9bd1c04f0d1f9ddff5f80a6a16257e0055a7aa4c3eb000a303870d7，接受BASELINE_REVIEW_COMPLETE_WITH_GAPS；不是新实现FAIL，32项用例为待执行。继续当前整批，不逐项交接。

- A-G01真实muxer在最小JDK构造首遇android.util.SparseArray链接限制。须明确实际执行环境与所有主机测试端口，不假定补一类即可完整运行。真实Media3代码与主机平台替身分别留证，替身环境结果不冒Android实机效果。
- A-G02封存extractor/decoder1.9.3身份可核，但本批新增运行闭包来源许可尚缺；按本单既有授权补固定官方POM/module/适用许可及strict实际消费后才运行，不升级/关校验或伪造同名Media3。
- A-G03当前尚无资格化六样本AVCfixture。先核已批准只读sample参数与权属；不符则记录具体阻塞，允许采用已有准入工具/已有授权合法合成内容，不自动新增编码器或扩大FFmpeg范围。fixture须来源/工具版本参数许可/hash/初始化数据/每样本NAL表示及hash/keyframe/PTS/时基。不得4B或伪NAL充有效样本。
- A-G04原E6 finish恰6个payload，0B flags4 EOS非第7帧，EOS=last+200000；payload PTS上限不等总duration，正例建议PTS0..1000000步长200000、EOS1200000。提取器END_OF_INPUT/sniff不等全底层EOF/hash；seek绝对位置/stream终点不等open返回remaining长度。事先声明NAL与时基比较规则。

完整判据与MC01–MC32见docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_REPORT_V1.0.md及其PHASE_A_EVIDENCE/independent-cases.json。coder集中实现/自测并在最终报告逐项映射可运行证据和准确NOT_RUN；tester只在负责人审新冻结后执行B。原预算/保管归还/P0及D1未过M0未启不变。

## 2026-10-21 正式派发阶段B：完整冻结有限实现独立审查

负责人已核主报告18137c21ad6806b13d1a8d0a8b818b5be1b0db20ba7b07067900cda6018dfca7，seal6d08e618dd1b98852830468a69b5048f65b55f4bc0a9117360c7bd414423c4ed全部1045项含ZIP身份及ZIP1044唯一成员计数。当前交付有限读取/薄接线，容器正例仍NOT_RUN；不是全部开发目标完成或准入PASS。

现在正式启动B，整包审查已实现部分、新使用准入和准确缺口。先独立审extractor/decoder同版本官方POM/module/许可证、AAR/classes及strict实际消费差异；不合格的新使用不运行。对新绝对输出目录运行冻结文档入口，源码/生产JAR优先路径实际来源核验，独立故障与MC01–MC32逐项映射。尤其审HostMp4Inspection、MatureContainerRemux、TemporaryOutput新检查/取消/失败/原返回门；8MiB包含hash及重读、绝对stream end、short/unknown/截断/latecancel、两源预算；新host结构结果不得validated/READY/COMMIT，不能因NOT_RUN校验跳过出现放行。

主机缺Android类的probe退出0只代表记录阻塞，不能算功能PASS。sample.mp4只读全EOF/hash不等提取成功；不符六样本fixture、恶意atom内部内存、seek真实图、NAL/时间基/EOS duration及真实mux/remux不得静态代过。允许输出有限已实现PASS_WITH_GAPS或集中FAIL，但原功能簇未执行目标始终列OPEN/NOT_RUN，不以有限复审PASS关闭容器链。

只离线已有JDK/新独立证据目录，零设备/ADB/占用/Gradle/共享缓存修改，无新fixture/编码器/平台替身或旧E3许可。核旧封存和原05回归；汇总独立发现和后续准确Android/fixture条件为一份完整报告通知负责人，集中回交修复或下一批。coder保持候选冻结；D1未过M0未启。
