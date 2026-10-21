# D1 MEDIA3 CONTAINER01 接口与验证决定 V1.0

2026-10-21。D1 实验接口，非 M0 公共 API。实际范围为真实读取组件进展、容器薄适配源码和准确的运行缺口。

## 来源和范围

Media3 固定 1.9.3，Guava 固定 33.3.1-android。新增使用 extractor/decoder 的官方 POM、module、Apache 2.0 许可与缓存 AAR 哈希在运行前核对。无二进制下载、升级或旧 pin 改写；新增两条官方 POM pin，不将其冒称为已经实际消费的 POM。最终 Gradle 实际验证 300 项：123 binary、37 module、140 POM。

原 INPUT_SINK05 的 HostInputFactory、HostDataSource、MatureMuxerBinding、E6Muxer、原 registry/bridge/coordinator 实现保持原样。TemporaryOutput 新增独立主机检查入口；取消在该入口活动期间关闭其同一原 read factory，归还仍依赖原 registry 和 worker。

## 真实提取器接线

HostMp4Inspection 只接受显式 MP4 或 FRAGMENTED_MP4 范围。能力、seek 时间界先于 DataSource 创建/open 和提取器构造拒绝；具体随机读取能力仍由原授予的 readAt 执行结果决定，不猜测底层存储能力。

路径为原 Provider/readAt → HostDataSource → 真实 DefaultExtractorInput → 真实 Mp4Extractor 或 FragmentedMp4Extractor → TrackOutput。没有自写 box、AVC 或解码解析器。接受至多两轨 AVC/AAC、每轨至多 512 样本、每样本至多 262144B；不接加密样本。可选捕获仅接受单路 AVC256×144、rotation0、恰六样本，PTS 严格递增且位于既有界内。

每次检查的实际读取累计至多 8MiB，包含完整 hash 扫描、解析和 seek 重读，单块至多 64KiB。完整原流 EOF/hash 与 extractor END_OF_INPUT 分开记录；不把 sniff 或 parser 停止视为全流证明。轨道摘要与每样本大小、PTS、flags、hash 有界保存；只在明确 capture 模式保留最多六个编码样本，不缓存整容器文件。原源总数2、每源在途1/排队0保持。

seek 使用真实 SeekMap/PositionHolder 的绝对字节位置，至多16次实际重开、总4096次 read 调用；手动 seek 时间至多2秒，仅在已知、可 seek 的真实图内执行。open 返回 remaining；DefaultExtractorInput 的已知绝对 streamLength 为 position+remaining，未知保持 -1。旧 range 的原返回仍由原 factory 负责。该 SeekMap 路径尚未运行；实际验证的是绝对5+remaining2=streamLength7的真实读取组件重开。

这些界限制 SDK 转发和记录，**没有证明 Media3 内部根据恶意 atom 大小分配内存的上限**。畸形 MP4、错误尾部、复杂 edit list 和时间基行为尚未执行。当前代码不能据此升级为生产隔离验证器；后续须在既有隔离资源门内执行，不能仅加大堆来取得通过结果。

## 写入与主机重开

MatureContainerRemux 仅消费真实检查产生的六样本 capture；检查 AVC 参数、非加密、初始化数据总量≤64KiB、首样本 keyframe 及全部样本预算后才创建现有 MatureMuxerBinding。不生成 NAL、不转码、不将不匹配原视频改造成可接受输入。

E6 的语义保持：恰6个 payload；最后单独写 0B、flags4 的 EOS，时间为 lastPTS+200000us；EOS 不是第7帧。payload PTS≤2000000us 不证明最终 duration≤2秒：last=2000000 时 EOS=2200000。建议未来资格化正例为 0..1000000us、步长200000，EOS1200000us。

预先声明比较规则：输入与重开提取器输出均按同版本 Media3 的 Annex B 表示比较，muxer 走其原 AnnexBToAvccConverter；比较相同表示下的每 access unit 大小/hash、整数微秒 PTS、单轨参数及逐项有序 CSD 字节。容器整体 hash 不要求与输入相等，不暗中接受前缀变化或任意时间容差。该保守规则尚需真实 fixture 运行确认；不将编码字节相等称为解码等效。当前未完成实际 EOS 容器结束时间及 timescale/rounding oracle 的运行验证。

TemporaryOutput.inspectHostMp4Structure 先要求 flush/close 成功及原 writer/任务真实返回，再用同一授予 Provider 建立只读 factory；检查完整 EOF/extent/hash（顺序输出还比对原写入摘要），关闭后等待原 read registry/worker。失败保留首错和原归还门。新结果 kind 为 HOST_MEDIA3_MP4_STRUCTURE_V1；不会设置 validated、签发 HOST_ISOLATED_FORMAT_V1 或调用 READY/COMMIT。重开轨道、CSD、样本比较失败也会阻断后续 READY。

该真实写入/结构重开正例仍 NOT_RUN：最小 JDK 缺 Android 类，且无资格化编码 fixture。源码接线和严格编译不是此链路效果通过。

## 主机端口与后续最小条件

只沿用冻结05的 URI、errno、WorkerRule 三类明确 JVM 端口；新增 Android 平台端口0，同名 Media3 替身0。JVM 不加载 SDK stub android.jar 来冒充 Android runtime。生产 JAR/APK 不包含测试或这些平台端口。

真实构造首遇：Mp4Extractor 缺 PackageManager.NameNotFoundException，FragmentedMp4Extractor 缺 Parcelable，FragmentedMp4Muxer 缺 SparseArray。它们是各次尝试的首个链接失败，不是完整依赖清单，也不表示补一类就能运行。

后续至少需要：负责人另行批准的准确 Android 执行环境及设备/隔离资源；权属/工具准入完整且符合参数的六样本 fixture；真实 FD/flush/fsync/close/read-only grant 证据；原 CPU/slot/death/source/timeline/内容门及独立测试。不得据本包启动设备、原 E3 许可或 M0。真实解码、平台效果、隔离验证、业务提交和播放全部保留 NOT_RUN。
