# C14 有限编码协商设计 V1.0

2026-10-16，先确定约束再实现。C13-T01两正例实际在OMX.qcom.video.encoder.avc configure失败，原始-38/0x80001001不唯一指向颜色、profile、权限或硬件损坏；C13 received/input/sample/verified均0。旧host双轨PASS不是此ByteBuffer管线成功证据。C13-T02 App系统signal0严格FAIL、trace缺失/ordinary UNKNOWN保持OPEN；退出采集不变，两项同条件CPU SIGSEGV不在C14重新调度。

## 确定策略与硬限额

固定256×144、5fps提示、600000bps、I-frame interval1，6个真实RGBA snapshot，actual relative PTS、无音频fMP4/AVC。不能改变≤1ms、luma≤24、源差异≥4/输出≥2、六帧完整EOF或白名单求通过。CPU2/encoder-output1、queue2/consumer1、保守8份可达RGBA1179648B＋YUV55296B保持；不是整个RSS/ART垃圾回收上限。

枚举公开REGULAR_CODECS≤128，单codec类型≤32，AVC能力记录≤16，name/canonical≤128且只接受系统标识字符，color/profile各≤64。超限拒绝，不遍历无界metadata；返回数组由framework分配不冒充事前控制framework内存。按canonical去别名并排序，优先第一个non-software（硬件属性另记，不把unknown称硬件），其次第一个software；若某类没有则最多选同类两个不同codec。

每codec至多两个格式，按轮次交错顺序A1、B1、A2、B2（不存在者跳过），总提案/原生创建均≤4，协商整体deadline12秒并受管线总60秒限制。variant1为首选21→19→Flexible的最小公开格式，不写可选profile/level/maxB/color-standard/range/transfer；variant2优先不同的标准颜色或Flexible，只有声明Baseline时才加Baseline。没有不同颜色但声明Baseline可尝试同色＋Baseline；完全重复格式不入计划。不推断是某个被移除key的根因。

保存width/height/rate/bitrate范围、alignment、颜色/profile/level列表、hardware/software/vendor属性和实际required-format isFormatSupported结果；先检查尺寸/帧率/码率/对齐，逐提案isFormatSupported真才create。能力否定为未创建；能力声称真但configure/start拒绝为真实失败尝试。候选都无可支持格式为CAPABILITY_BLOCKED；有实际调用拒绝则ABORTED/具体失败，不能换成能力跳过。

configure/start失败只允许在producer和writer尚未创建时协商下一项。每个原生调用在同一owner线程执行并记in-flight；异常并不等于释放。create返回对象后configure失败，须release正常返回、Image为空、creating=false/nativePending=false才下一；release失败/取消/deadline立即停止并保留引用和单许可，不跨线程强制关闭。create抛异常但未返回对象，公开API无法证明底层完全未创建，保守quarantine且不重选。native调用挂住即PENDING，deadline不能中断JNI并伪释放。

start成功即选中，随后才打开writer并生产源帧；任何INPUT/OUTPUT/MUX/VALIDATION运行期失败不进入配置回退、不再开第二输出。默认profile不承诺无B-frame；输出原有严格递增实际PTS及完整解码/内容门槛拒绝不兼容结果。不是Surface/GPU回退、不是宿主源压缩解码，不新增codec/库。

## 诊断和首因

阶段ENUMERATE/CAPABILITY/CREATE/CONFIGURE/START/INPUT/OUTPUT/MUX/VALIDATION/CLOSE分别记录。仅输出固定数值format键、系统codec标识、attempt/variant、能力事实、CodecException公开errorCode/diagnosticInfo/recoverable/transient；diagnostic只接受Android固定诊断标识模式，不输出任意exception message、路径/凭据或媒体字节。原通用StageLog保持其他路径行为，新增专用诊断不靠REDACTED隐藏必要错误码。

第一次协商错误独立留在firstAttemptError和有界4项历史；后续成功只表示选中下一候选，不能抹去先失败记录。最终pipeline first error与cleanup另列；CLOSE错误不能覆盖CONFIGURE首因或把未释放标成ABORTED。无成功READY前仍须实际Source/codec/Image/FD/租约/帧/回调归还，READY丢响应仅同ID reconcile。

## 验证范围

共享纯协商状态机反例覆盖能力否定/声称后拒绝/实际关闭后下一/全部拒绝/取消/预算/关闭失败/在途/metadata限额；纯fake不能证明设备可用。Android增加实际能力快照与真实codec configure故障注入、关闭归还/有限选择验证；关闭不确定测试可用真实release后保守扣住“未证”账本，明确区别真实硬件release故障，不泄露设备资源或假称该故障已实测。原17 pipeline包含14个被BLOCKED反例全部保留，正常MP4/AVI成功后依赖执行。

官方API参考：[isFormatSupported](https://developer.android.com/reference/android/media/MediaCodecInfo.CodecCapabilities#isFormatSupported(android.media.MediaFormat))、[CodecException](https://developer.android.com/reference/android/media/MediaCodec.CodecException)；锁定Media3 [DefaultEncoderFactory 1.9.3](https://raw.githubusercontent.com/androidx/media/1.9.3/libraries/transformer/src/main/java/androidx/media3/transformer/DefaultEncoderFactory.java)。参考其能力选择思路，未复刻Surface编码器或引新依赖；复用既有fMP4封装，ByteBuffer小探针必须自行记录实际支持/配置结果。官方文档/本机SDK源码不是设备能力结果。精确本机SDK引用与hash随evidence归档。

正式内部Maven group com.videokit、SDK namespace com.videokit.<module>、App com.videokit.app已由PROJECT_DECISIONS决定；只把正式artifact/version兼容待验保留OPEN，不撤销内部命名。Flutter＋独立Kit/AAR/C ABI、全P0、跟踪权利/真实标签及§29/M0–M8门禁保持。D1未通过，不进入M0。
