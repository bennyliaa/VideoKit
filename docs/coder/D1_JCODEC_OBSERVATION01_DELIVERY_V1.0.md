# D1_JCODEC_OBSERVATION01 完整批次报告 V1.0

2026-10-21。独立审计fork三文件补丁及一次编译打包完成，**元数据自测被本批测试辅助的factory上下文错误阻塞，未进入任何parse差分。整体VALIDATION_BLOCKED_HELPER_FACTORY_CONTEXT_FAILURE，不能交付为已验证原始字段能力或接入资格checker。** 两个fresh dref/stsd观测关闭/guard用例通过不等头字段解析通过；其余动态项NOT_RUN。完整失败证据及最小辅助修复建议冻结交负责人，当前不再编译/JVM/修改源求绿。

## 1. 实际一次构建与明确新身份

目录D:/CodexProjects/VideoKit/docs/coder/d1jcodec-observation01。原source archive1246282B/SHA2569945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db，原708Java4435752B。生产只改DataRefBox、SampleDescriptionBox、AvcCBox，705源码字节不变；新增helper在checks，不是生产改动。Receipt/encoder/产品Media3/Android/BoxFactory/DataBoxes/AliasBox/UrlBox/NodeBox/Header等均未改。原checker02/31证据和阶段A/9证据按manifest保全。

新artifact版本**0.2.5-videokit-observation01**；artifacts/jcodec-0.2.5-videokit-observation01.jar：**1930955B，SHA2561a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86**。combined patch SHA256 f5f472b6bf6422832c66db4764a1a2d431be4c296c0f33d8bc3e853c2382f23c；3文件前后hash/分别diff/组合patch均随包。Manifest列Implementation-Version、独立Automatic-Module-Name、原source及patchSHA，没有Main-Class/官方签名/沿c4ed身份声明。

原JDK21.0.10 java/javac/jar/release/modules准确hash先核；一次javac、一次jar顺序运行，-J-Xmx512m、--release11、UTF-8、-proc:none/-implicit:none和空专属classpath/sourcepath/processorpath；无Maven/Gradle/新依赖/网络/缓存。708库+1helper共709输入4460541B≤16MiB；原输出9334676B，包含原classes/生产测试副本/JAR/资源/收据，不只JAR。最终全包+ZIP再核≤64MiB。

javac历史PID19880 UTC02:11:23.879567–02:11:30.232152，jar历史PID35184 UTC02:11:41.236923–02:11:47.827076；各自然exit0/原两流关闭/未超60秒观察窗，未kill/interrupt/重试。原deprecated/unchecked/dep-ann warning保留，未为消警改上游。977生产class+3helper class均对应实际同次javac输出/副本/SourceFile/原输入hash，3helper不进JAR。新JAR中974库class字节与原c4ed相同，仅三patch class不同；无extra/native/driver class。原c4ed JAR及tool02 seal2774项复核不变。

## 2. 三文件已实现的合同（类型/静态，尚非parse动态通过）

dref/stsd同原两getInt消费处保留raw versionFlagsWord和uint32 declared count(long0..4294967295)；Version/flags getter只由同存储word提取，actualchildren仍原getBoxes().size，绝不按声明count新增循环/分配或从children反填。parse首条输入操作前只清新增观测，正常super.parse返回才置hasOriginalParseObservation=true；失败时新增getter统一拒绝ORIGINAL_PARSE_NOT_OBSERVED，不把0/上次原值作有效观察。

avcC在原skip1位置改为等量get1保configurationVersion，保留原相对4的完整flags byte、相对5的完整SPS count byte和原SPS loop后可变位置的PPS count byte；existing mask0x03/0x1f、profile/compat/level、signed getShort、NAL checkState、NIOUtils.read与SPS/PPS append均不改。reserved高6/高3可由保留raw byte计算，不规范化丢位。没有增加新的box/AVC/NAL parser、预扫、修容错或额外生产源字段。

构造/原builder/setter/write不创造parse观测；complete仅表示原例程正常返回，不等结构合法、声明count相等、全EOF或无尾部/扩展。legacy children/SPS/PPS/partial赋值保持，清的是新观察而非原状态。新增getter仅guarded primitive，无setter，不宣称并发parse/getter安全。3个doWrite及estimateSize源方法体与原版逐字相同，原输出/codec/mux/timebase不改。

**特别保留未验证项：NIOUtils.skip空输入可跳0，直接get会先抛underflow；本helper原/patch空/短输入、位置/legacy赋值差分未运行，不能仅凭源看似等价宣称已验证。** 同样count/flags/reparse/partial/readonly/write/已有getter完整差分均待下一准确范围。getter-and-byte-consumption-contract.json列全getter、原offset/可变位置、type、状态和局限，不冒已通过。

## 3. 实际单JVM失败：辅助入口选错，不改成熟factory求绿

本批只运行一个256MiB、5秒观察的元数据JVM。原PID23924，UTC02:14:04.320104–02:14:04.528075，自然exit1、未超窗、原stdout/stderr handle均关闭；原控制器随其已返回后的失败断言自然exit1。没有重复编译/补跑/强停/interrupt或故意挂起。

同JVM采用两个file-only URLClassLoader、parent为platform loader，原c4ed与新fork Class来源URL明确不同，实际loader身份检查通过；只反射调用public ctor/factory/parse/getter，不setAccessible/读写字段或注入生产状态。该具体机制随源完整保留；后续B需明确核机制和范围，本A准备本身不是授权来源。

完整stdout425B有3条JSON：一条两Origin和两条PASS dref_new_instance_unobserved/stsd_new_instance_unobserved；stderr393B完整保留主断言/NoSuchMethod异常。**完成2 fresh guard case、parse差分完成0、没有最终success summary。** 计划的自有≤8KiB metadata vectors（含已知来源CSD的自有avcC记录）、截断/重复/异常/写入语义等均未执行，不能作70余项PASS或原字段已观测。未得到最终payload/endNano/loader-close成功收据，不伪造它们。源表明main在最终断言前实际join同原worker、runAll try-with-resources会尝试close两个loader；原process已自然返回，不用进程消失代未输出的逐项close回执。

原异常是java.lang.NoSuchMethodException: **Box$LeafBox.hasOriginalParseObservation()**。测试Api.box对avcC误用BoxFactory.getDefault，其DefaultBoxes原本不映射avcC，mature factory按原行为返回LeafBox；avcC正常映射属于VideoBoxes/sample-entry上下文。这是本测试辅助的入口错误，不能归为新fork缺getter/parse失败，也不能为求绿改BoxFactory/DefaultBoxes或媒体。class实际含新增AvcCBox getter已静态核，但其动态正确性仍未证。

附加静态集中发现：当前控制器未到达的后置class-load过滤以Encoder/Decoder后缀泛匹配，会误认普通JDK CharsetEncoder/Decoder；这不是运行过媒体codec。静态审计已按org.jcodec命名空间区分，原实际控制器保持原字节，另附未应用修复建议。完整class-load显示无JCodec编码器/解码器、SixFrameDriver/MP4Demuxer/MP4Muxer加载，实际MP4/媒体生成/设备0。

## 4. 未应用的最小后续方案

PROPOSED_HELPER_ENTRY_FIX_NOT_APPLIED.patch仅建议两loader中对avcC使用原public AvcCBox(Header) ctor（或经审定正确VideoBoxes factory），dref/stsd仍用原成熟factory。另一个PROPOSED_CONTROLLER_CLASS_FILTER_FIX_NOT_APPLIED.patch建议媒体encoder/decoder只按JCodec空间筛选，允许JDK文本charset转换器。这两个都是文本提案，**没有应用到当前已编译helper、没有新构建/JVM或实际媒体读**。

建议负责人先审完整当前失败包，另签一次准确helper/控制器修复验证范围；可复用本冻结fork作独立验收，若另有生产问题再新批明确安排。不得修改原C4/编码工具或扩三文件来修辅助上下文，不沿当前失败scope盲重放。当前原始信息能力验证仍BLOCKED，不接checker、不改其mandatory blockers，不重跑固定MP4期待资格PASS。

## 5. OA01–32、许可、冻结与交接

阶段A c28a3285dba537cceaf3ffde80888b975e2e6393b5fb72dbb7b855f59bf7486f及9项证据/全合同纳入reference，原PREPARED_NOT_RUN不改。新oa01-oa32-completion-matrix将build/字节许可静态证据、2个fresh动态guard、失败后全部parse差分NOT_RUN逐项分开；不能把测试exit1解释成完成或把编译成功冒getter通过。

原FreeBSD版权免责声明、73 bundled JAAD Public Domain+JCodec FreeBSD变更、Guava Preconditions Apache2和全文/逐源通知均保留，新MODIFICATION-NOTICE/SBOM明确独立审计fork的3源差异、原archive/patch身份，未冒官方签名或商业/专利/FFmpeg清权。新fork不进App/APK/Media3/原encoder classpath。原checker02报告18bc...与31证据及本A/9项证据完整hash保持；原c4ed/tool02封存2774项不变。本批未读取/查询实际MP4路径，也不为“保全”额外读媒体，旧48945/17257不读取/轮询/attach或处置，不作host空闲证明。

seal evidence/observation01-freeze.json与ZIP D:/CodexProjects/VideoKit/docs/coder/D1-20261021-JCODEC-OBSERVATION01-source.zip覆盖708源/3patch/新JAR/980真实编译class及复制、helper实际失败源/原构建测试完整流/原Popen回执、getter合同/OA矩阵/未应用提案/许可。只读材料入口tools/review_materials.py不编译、不JVM、不parse媒体，不提供自动重跑失败辅助或改旧scope的入口。

本批完成到“可审静态新fork+完整失败验证证据”，**未完成动态parse验证与后端验收，整体资格仍OPEN/BLOCKED**。集中交负责人，不自行补编译/扩大权限；下一步独立完整审或准确辅助修复由负责人决定，之后才可能新checker集成/新scope真实资格。原媒体/encoder/历史失败与UNKNOWN保持，D1未过M0未启，未签HOST_CONTAINER/隔离格式/READY/COMMIT/播放。
