# D1 JCodec Observation01 阶段B完整独立复审报告 V1.0

2026-10-21；tester；冻结审计fork与一次独立有限元数据验证。

## 结论

**PASS_LIMITED_METADATA_OBSERVABILITY_WITH_MEDIA_NOT_RUN**。独立冻结材料/三补丁/705不变/真实class及许可审通过；tester一次javac和单个双隔离loader JVM的**79个有限元数据用例通过**，原word/uint32声明count、avcC原字节、默认与失败观测guard、异常位置及legacy append/partial均在该子集有真实差分证据。未发现本范围新增生产缺陷。

原coder helper的factory上下文错误及exit1/parse差分0完整保留，未覆盖、修写或重跑。独立tester辅助副本使用两边真实AvcCBox(Header)构造并扩独立判据，代为完成本次另批有限验收；不把原coder两fresh通过升级为其parse已运行。

新fork可观测性结论仅限静态和这些元数据用例，**未运行实际MP4/容器/Media3/解码/隔离格式/READY COMMIT/播放**，未接入checker02或移除其mandatory BLOCKED。整体容器目标继续OPEN，D1未过M0未启，原48945/17257 UNKNOWN未查询/poll/attach/干预。

## 准确范围、原冻结及材料入口

依据 docs/milestones/D1_JCODEC_OBSERVATION01_TESTER_REQUIREMENTS_V1.0.md末尾正式B与辅助一次许可，原字节另存。本批先执行纯Python tools/review_materials.py到独立materials-001，原返回报告与独立Python再审均仅静态，不启动JVM或解析媒体。本人没有运行coder旧失败控制器/辅助或任何候选媒体文件。

原交付报告 docs/coder/D1_JCODEC_OBSERVATION01_DELIVERY_V1.0.md，9605B，SHA256 **4cb2aa84ff19eefb2c85a68c3c81210fb70286d3eb17c32d0cdba78ef8e06856**；seal SHA256 **8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725**。独立逐项核**2738唯一文件**、外置ZIP**2738唯一成员**集合/大小/解压hash完全相等，ZIP SHA2560f6042bc2b10b7e6f256d30185c48b6a3f93676406576662ad5dbffbce367df7。ZIP在seal外，与封存文件数量严格区分，不混自己seal进其成员。

新JAR artifacts/jcodec-0.2.5-videokit-observation01.jar，**1930955B，SHA2561a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86**；combined patch f5f472b6bf6422832c66db4764a1a2d431be4c296c0f33d8bc3e853c2382f23c。manifest准确Implementation-Version0.2.5-videokit-observation01与原source/patch来源、独立module，无Main-Class/官方未修改身份或c4ed替代声明。原c4ed JAR仍为基线，仅通过各自独立loader加载成熟metadata类，未改原生产/App/APK/classpath。

材料入口还核原tool02 seal2774项、checker02/31证据及阶段A/9证据原样。tester独立审另完整核705/3与977/3、原失败、源许可，不拿coder自报代实际文件检查。执行后再次核2738全部hash/两JAR及测试源码不变；原媒体不为“保全”额外读，也不查询其路径。

## 三文件允许差异、真实编译与许可

708源集合与冻结原source严格相等：705字节不变，仅DataRefBox、SampleDescriptionBox、AvcCBox变化。三份doWrite和estimateSize方法体逐字完全相同；移除仅新增观测赋值并把同消费点保存投影回原读法后，三份legacy parse方法去空白完全相同。BoxFactory/DefaultBoxes/DataBoxes/NodeBox/Header/AliasBox/UrlBox/encoder/decoder/muxer/timebase不改，无新增生产解析器/策略容错/全头预扫。

dref/stsd保存同原两getInt的raw word和unsigned32声明count，完成位首读前false/reset、super.parse正常返回后true。avcC仅在原skip位置存unsigned配置版本、原get flags/SPS count完整byte与原PPS count；原signed长度/checkState/列表追加和既有getter保留。观测getter为guarded primitive、无新setter。metadata parse不校正unknown值或声明count不一致，验证策略仍属后续checker。

独立读取实际javac输出classfile/SourceFile/major及source hash，与复制和JAR逐项相等：coder实际980class，**977生产+3测试排除**；974生产class与原c4ed字节相同，仅3目标class变化。JAR不含fixturetool/metadata helper/native扩展，未假装只编了三份源；原708全库编译产生其他未调用类，存在不授执行权限。

coder原一次javac19880/一次jar35184自然exit0及两流归还，unknown false；709输入实际总**4460541B**≤16MiB，原build outputFiles逐项大小/hash及总**9334676B**≤64MiB重算一致。全包/ZIP预算沿原冻结审计，不能只拿JAR大小作全输出。tester没有重建fork或再打包库。

Apache2/FreeBSD全文逐字相同；708逐源通知文本及三源原版权头保留，SOURCE_NOTICES准确换三份新source hash、排除不在本JAR的旧driver清单并列新helper。PROJECT-CODE-NOTICE相应改为审计fork说明，新MODIFICATION-NOTICE/SBOM明确来源与差异。这些是正确的清单更新，非强求fork通知文件全字节等于编码工具项目通知。仍不授产品分发/专利/FFmpeg许可。

## 原coder失败与本次自有辅助：不混淆来源

coder原JVM23924自然exit1，stdout425B/stderr393B，仅origin+两个fresh dref/stsd guard，parse差分0、无最终summary。真实NoSuchMethodException目标Box$LeafBox.hasOriginalParseObservation：DefaultBoxes不映射avcC，测试辅助取错上下文；不是生产AvcCBox无getter。原source/class/两未应用提案/失败日志不改。原后置泛Encoder/Decoder过滤还会误报JDK charset，源码缺陷定位与原实际执行覆盖分开。

tester自有IndependentObservationCheck基于冻结辅助副本做明确独立修正：换tester包/类名；每个隔离loader内avcC调用其成熟public AvcCBox(Header)，dref/stsd仍正确原factory；两loader在分配前登记，原worker guard仅一次实际close，真实关闭回执和失败时最终summary也保留；逐parse日志额外列fork raw观测；三类均核原/新class实际来源，新增两uint32边界与三readonly getter case。完整派生hash/diff有证据，反射只调用public ctor/method，不setAccessible或读写字段。没有修改任何生产factory或模拟getter。

本批保留两次**Java启动前**的tester Python核验适配记录：第一静态脚本误要求全部许可目录文件字节不变，读取真实notice差异后改按上游全文/708逐源文本与新清单身份分别核；运行控制器前置误把本批compiler-identity顶层array当旧files对象，TypeError时javac/JVM均0，修正原收据格式读取。详static-verifier-correction.json/preflight-shape-correction.json。它们不是产品缺陷、不是隐藏的第二次编译或JVM；未调整测试helper源码/79判据或生产结果后重跑。

## 唯一实际编译和元数据JVM原返回

tester固定javac PID21556，2026-10-21T02:36:56.217773+00:00至2026-10-21T02:36:57.249166+00:00自然exit0，约1.016s；-J-Xmx512m/--release11/UTF8/-proc:none/-implicit:none/空classpath-sourcepath-processorpath，仅编自有helper，实际3class major55及SourceFile/方法Code SHA全部记录。两流返回、unknown false，无失败后的第二次编译。

唯一test JVM PID33048，2026-10-21T02:36:57.346264+00:00至2026-10-21T02:36:57.628122+00:00自然exit0，外部约0.281s<5秒；heap256MiB、单原worker，body清理后elapsed **151725500ns**。sameOriginalWorkerJoined/bodyComplete=true，两个原URLClassLoader各openReturned/closeEntered/sameOriginalCloseReturned=true，close由同原worker执行且guard不二次native close。原Popen/两流自然返回与worker/loader返回分别有真实字段，非源码推测。

完整stdout **57624B**/stderr0，严格UTF8且合计≤1MiB，79唯一PASS case+三种真实class origin+原origin+最终summary均保全，没有tail或缺失结束记录。显式metadata byte payload **1036B**，另保守Header/fourcc scratch **2048B**，合**3084B≤8192B**；不把对象/JVM整个内存称1036B。所有输入是自有有限metadata记录（23B avcC借用已冻结批准CSD payload作来源），不声明它们是MP4原字节或有效AVC视频。

父loader明确platform，两个file-only URLClassLoader相互独立，dref/stsd/avcC每类原/新真实CodeSource和ClassLoader都核不同。实际classload日志完整保全，禁止类过滤限org.jcodec/net.sourceforge.jaad成熟媒体encoder/decoder与demux/mux/Main；JDKCharsetEncoder/Decoder属于文本转换，明确不误报。本次无成熟媒体编码/解码、MP4Demuxer/MP4Muxer或SixFrameDriver加载，无实际媒体/设备调用。

## 79用例中的实证与边界

dref/stsd正常空/一child、raw word0xaabbccdd/0xff123456、声明0/1/0x80000000/0xffffffff、actualchildren不一致均同原消费/legacy；raw version/flags/count记录实际getter结果，uint32最大4294967295及高位2147483648不变。静态确认count不驱动分配，再做最多20B父metadata，非资源攻击。

三fresh+四builder/createEmpty均NOT_OBSERVED且全部新getter抛ORIGINAL_PARSE_NOT_OBSERVED，三own-empty write/estimate字节与原相同且不产生观测。正常/unknown配置avcC保存cfg1/7、lengthByte255/19、SPSbyte225/33、PPSbyte1，mask解释仍同原。它们可观测不等合法，后续checker仍应拒绝不合要求字段。

两父0..7截断各8条、avcC0..22截断23条，以及有界原NAL checkState/signed-short两点/缺factory/partial alias等：原与补丁异常类别、position/limit/remaining/byteOrder及既有getter视图逐项相等；good→fail重置观测且新getters不泄上次值。重复good→good保持legacy children/SPS/PPS append与第二次raw声明分离，profile partial及成功child先追加再后child失败仍保留同原结果。readonly offset与LITTLE_ENDIAN也核原语义未被强制改变，三新getter重复读不改legacy或inputposition。

**完成位不是完整结构合法性**：parent尾3B/avcC尾2B原例程正常返回而remaining仍在，观测true只证这些原消费值。有限测试不证明所有畸形输入、并发安全、完整MP4/AVC语法、成熟库内部分配安全或媒体资格；没有用正常返回替原raw约束验证。

## OA01–OA32逐项结算

阶段A原PREPARED_NOT_RUN不回写。下表严格区分静态/有限元数据/未运行文件范围；不是32项实际MP4通过。

| 项目 | 独立B级别 | 依据与限制 |
| --- | --- | --- |
| OA01 authority | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | 准确新B许可/身份与一次编译+一JVM，原scope不重放 |
| OA02 source identities | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | 独立2738/ZIP2738，708源705不变/3允许补丁 |
| OA03 raw parents | PASS_STATIC_AND_FINITE_METADATA_ONLY | 原两getInt投影一致；真实rawVersionFlagsWord/uintcount日志独立核 |
| OA04 uint count | PASS_STATIC_AND_FINITE_METADATA_ONLY | 实际0/1/0x80000000/0xffffffff uint32按long保留，无count驱动分配 |
| OA05 actual-versus-declared | PASS_STATIC_AND_FINITE_METADATA_ONLY | 声明0/高uint与actualchild不相等仍保留原值；parser未擅自校正 |
| OA06 unknown parents | PASS_STATIC_AND_FINITE_METADATA_ONLY | unknown parent raw0xaabbccdd/0xff123456保留，未规范化 |
| OA07 raw config | PASS_STATIC_AND_FINITE_METADATA_ONLY | avcC空/短输入与正常config byte同原异常位置/legacy结果，rawconfig有实际记录 |
| OA08 raw reserved | PASS_STATIC_AND_FINITE_METADATA_ONLY | actual rawLength19/255、rawSpsCount33/225保留；原mask含义不改 |
| OA09 PPS count | PASS_STATIC_AND_FINITE_METADATA_ONLY | PPS实际原uint8和截断前未完成guard，非由列表反推 |
| OA10 fresh and builder | PASS_STATIC_AND_FINITE_METADATA_ONLY | fresh3+builder4均false且所有新增getter实际抛guard |
| OA11 write not observation | PASS_STATIC_AND_FINITE_METADATA_ONLY | 三own-empty builder write/estimate原字节相同且不产生parse观察 |
| OA12 completion meaning | PASS_STATIC_AND_FINITE_METADATA_ONLY | parent尾3B/avcC尾2B正常返回observed true且remaining保留；不是全结构通过 |
| OA13 failure reset | PASS_STATIC_AND_FINITE_METADATA_ONLY | good→truncated parents16/avcC23，失败新观察false且getters拒绝旧值 |
| OA14 legacy partial state | PASS_STATIC_AND_FINITE_METADATA_ONLY | 原SPS/PPS/children append和profile partial不变；partial child2保留 |
| OA15 read sequence | PASS_STATIC_AND_FINITE_METADATA_ONLY | 真实exception/position/limit/remaining/order/legacy视图逐case相等，offset readonly/LITTLE_ENDIAN覆盖 |
| OA16 truncated parents | PASS_STATIC_AND_FINITE_METADATA_ONLY | parent0..7 safe短输入每类8条差分通过 |
| OA17 short avcC | PASS_STATIC_AND_FINITE_METADATA_ONLY | avcC0..22安全截断/checkState/signed-short两界例同原异常与legacy |
| OA18 successful metadata | PASS_STATIC_AND_FINITE_METADATA_ONLY | 冻结CSD来源自有23B最小metadata构造，只用于成熟parse非有效媒体声明 |
| OA19 repeated objects | PASS_STATIC_AND_FINITE_METADATA_ONLY | 第二次parse新raw值与原legacy累积list区别真实记录 |
| OA20 readonly getters | PASS_STATIC_AND_FINITE_METADATA_ONLY | 三readonly getter重复调用不改inputposition/legacy；primitive guarded无新setter；不声称并发安全 |
| OA21 factory/children | PASS_STATIC_AND_FINITE_METADATA_ONLY | 原factory705源不变；avcC各自真实public ctor；typed alias/url记录真实 |
| OA22 algorithm preservation | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | 独立doWrite/estimate完全相同、legacyparse投影完全同源；有限差分非全输入形式证明 |
| OA23 artifact identity | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | 新0.2.5-videokit-observation01/JAR SHA/manifest/sourcepatch一致，非原官方身份 |
| OA24 source-to-class | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | 真实980coder classes=977production+3excluded tests，974库字节同原/3改；tester仅3新测试class |
| OA25 licensing | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | Apache/FreeBSD原文及708逐源版权保留，新project/modification/SBOM及sourcehash清单正确更新 |
| OA26 build limits | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | coder一次javac/jar原返回与输入4460541/输出9334676B独立核；tester编译一次原返回 |
| OA27 finite unit limits | PASS_STATIC_AND_FINITE_METADATA_ONLY | 自有单JVM79cases、payload1036+scratch2048≤8192、5秒内、原worker2loader/Popen两流归还 |
| OA28 differential origins | PASS_STATIC_AND_FINITE_METADATA_ONLY | 真实两URLClassLoader/platform父隔离，三种原/新类来源URL不同，公开API反射无字段编辑 |
| OA29 raw receipt completeness | PASS_STATIC_AND_FINITE_METADATA_ONLY | 完整stdout57624/stderr0、最终summary/结束/loaderclose/workerjoin都有实际证据；coder原失败无summary不补造 |
| OA30 later checker integration | PASS_SCOPE_BOUNDARY_ACTUAL_FILE_NOT_RUN | 未集成checker02/未撤其blocker，后续准确新批 |
| OA31 immutability | PASS_STATIC_MATERIALS_AND_RECORDED_RETURNS_ONLY | 原失败helper/fork2738前后不变、旧tool2774/checker31/阶段A9材料入口核保持，实际媒体不读 |
| OA32 classification | PASS_SCOPE_BOUNDARY_ACTUAL_FILE_NOT_RUN | 仅有限元数据可观测性审定通过，容器/Media3/隔离READY COMMIT等均NOT_RUN |

## 集中交接与停止点

本范围新增生产缺陷0；原coder测试辅助factory入口与过滤错误明确保留，不要求改生产库求绿。独立新辅助一次79case已覆盖本有限验收目标，但不能据此补造原失败结束/loaderclose记录、改原报告或称它已重跑通过。当前fork三类消费信息可在受限合同下真实保留，完整getter/unsigned/失败状态由此另批有实证，不再仅凭补丁源码推测。

报告及证据冻结后发送负责人。后续是否接入新checker、怎样固定新JAR/classpath/原始字段拒绝策略、绑定新scope真实文件等，仍须负责人整包审后准确派；本轮未撤checker02硬阻塞、未运行实际MP4，不签HOST_CONTAINER/Media3/隔离READY COMMIT/播放。与本tester无关的coder-postfreeze-001只读复核子目录保留未改、不纳本次独立报告证据集合。旧UNKNOWN不碰，D1未过M0未启，停止后继。
