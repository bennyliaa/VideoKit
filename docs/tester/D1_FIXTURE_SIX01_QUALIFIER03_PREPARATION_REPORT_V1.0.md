# D1 FIXTURE SIX01 Qualifier03 观测后端接入准备报告 V1.0

2026-10-21；tester；QUALIFIER03_PREPARATION。

## 结论

**PASS_PREPARATION_LIMITED34_POLICY_MEDIA_NOT_RUN**。基于冻结checker02接入已独立审定的观测fork，必须的dref/stsd原VF/unsigned声明count及avcC原版本/reserved/count、actual对照与完成来源全部接入；原typed-child严格门及其他track/sample/timeline/hash/预算/原返回门未削弱。一次新helper编译与单个非媒体政策JVM成功，**34case=4接受+30拒绝**，实际原worker/loader/Popen两流归还。

本阶段**actual qualifier调用0、实际MP4读/查询/hash0、demux/生成/encoder/decoder/设备0**，未来input hash/bytes/scope保持UNBOUND；未取得HOST_CONTAINER资格，不接Android/Media3/隔离READY COMMIT/播放。原QUAL01实际BLOCKED及coder旧辅助FAIL不回写，不因准备通过称旧原媒体已合格。整体容器目标仍待新准确实际批，D1未过M0未启，旧48945/17257不碰。

依据 docs/milestones/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION_TESTER_REQUIREMENTS_V1.0.md；原要求快照随证据，所有新产物仅新tester目录。没有改fork/原支持类/原工具或产品依赖，没有自写MP4/AVC parser。

## 唯一JCodec来源与精确支持集

准确fork JAR **1930955B/SHA2561a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86**，版本0.2.5-videokit-observation01；前置核其原seal8a62ef8e...全部2738记录、已独立B报告6b71997ce6ad6136cdea7f7908e102bc460e6933b7c288e78657c6fb5cbbf59b与25证据不变。checker02报告18bc...及31证据准备时亦核不变。没有把原c4ed全JAR放进编译或运行classpath。

原工具仅静态读取准确JAR c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd，提取已审现有支持class，不重新编译：

| 支持class | 大小B | 原class SHA256 |
| --- | --- | --- |
| ReceiptJson.class | 3663 | 9fa908207d31315d8473feb9fcbe92b5b1e5eed4e80f0237e53cd629634f798a |
| WorkerDeadline.class | 3897 | 37abef9af2a2dce0d3b58196d23d8cce3a6069d8e67491fd734753b5f0604796 |

support目录**严格只有这2class**，SourceFile/major55/方法Code SHA与原JAR、原class-origin02、原源hash/seal绑定一致；无嵌套支持class需要附带、无org.jcodec/JAAD/encoder/Main/Job。原WorkerDeadline/ReceiptJson语义和字节均不改，来源与项目通知单列，不用源码重编译产生“看似同名”类。

未来runtime唯一classpath为**helper-classes6 + support2 + 准确fork JAR**，不含测试/launcher/原全工具JAR。OriginFence03核fork Implementation-Version和actualCodeSource：本非媒体JVM实际核10个成熟metadata/interface类、2支持、3checker policy/origin类共15个；未来helper main另核MP4Demuxer/Track、MP4Util/H264Utils/NALUnit来源，**该媒体来源分支本阶段未执行**。全部JCodec类的唯一来源还依赖准确classpath及无额外org类的冻结类集合/外部classload审计，不用一小部分class断言冒977类逐个runtime执行。

## 原始字段准入合同

dref/stsd必须hasOriginalParseObservation=true，再读真实原raw VF word/version/flags/unsigned declared count，要求VF0/version0/flags0、declared1且等actual children1。声明与actual分列，不从children或doWrite反填。实际普通8B parent Header的body必须恰为原prefix8+实际child完整size总和，拒绝parse正常返回但未消费的tail；完整模式还保留stsd实际VideoSampleEntry avc1/256×144/dref1原检查。

dref child保留原checker02严格门：唯一实际entry/index1，fourcc与真实class对应AliasBox/alis或UrlBox/url，child原FullBoxversion0/flags**恰1**、普通8B header/body**恰4**，无aliasfileName/extras/record或externalURL。没有LeafBox白名单、只看alis名字、flags仅&1、builder default或序列化parsed对象造原值。

avcC必须原parse observation真；原configurationVersion1；完整rawLengthSizeByte reserved高6全1、low2+1等actual NalLengthSize4；原SPS count byte高3全1、low5声明SPS与实际list count相等；原PPSuint8与actuallist count相等，SPS/PPS各1..16。原Header body精确 **7+Σ(每SPS/PPS实际payload bytes+3)**，不接额外extension/tail；原payload总量受64KiB约束，原CSD/SPS尺寸/PPS解析、normalized CSD与6sample数据/NAL/时基门仍继续核。

完成位只表示原parse正常返回，**不是合法性或全EOF**；这些version/flags/reserved/count/body政策独立在complete后拒绝。失败时partial原观测保留到joined receipt，默认/未完成不填0冒观测；不能由生成内部receipt复制golden。完整字段/API限制与未来schema分别见all-field-policy-and-api-contract.json、future-receipt-schema03.json。

## 已审框架保持及实际编译

checker02→03完整diff封存，静态逐区核InputOwner整个class、us整数映射、preflight、hashOriginal、rootAtoms、walk、identityMatrix、csd、原Job.run cleanup正文完全一致并记录区域SHA。只变新类/收据名称、新metadata政策/source proof接入与输出；只在新fork getter可实际观察且政策通过时移除旧“API永远不可得”的硬阻塞，不删必须字段门。

固定JDK原身份精确核；一次javac PID33448，2026-10-21T02:52:36.927762+00:00至2026-10-21T02:52:38.033633+00:00自然exit0/约1.110s，原stdout/stderr及两捕获handle归还、unknown false。-J-Xmx512m/--release11/UTF8/-proc:none/-implicit:none/空source/processorpath，classpath仅support+准确fork，未隐式补源/重建成熟库/打JAR或联网。

实际9个新class major55，source/class/方法Code hash与原javac输出/复制一致：**6 helper +2 test-only +1纯JDK launcher**。运行测试时主classpath仅launcher，原worker分配前登记自有URLClassLoader，子classpath为test/helper/support/fork，parent=platform；不存在旧JCodec fallback。后续实际helper runtime只用6+2+fork，不用测试loader/launcher。

## 唯一非媒体政策JVM及34项结果

原policy JVM PID32736，2026-10-21T02:52:38.370977+00:00至2026-10-21T02:52:38.664886+00:00自然exit0/约0.297s；heap256MiB/总5秒、原worker清理后elapsed **151925400ns**。holder-before-loader、allocation returned、同原worker单次loader close returned、body returned和实际join全有真实receipt；同原Popen自然退出/原两流关闭分别有回执，unknown false，无kill/interrupt/二close/重试。没有以源代码推测不存在的返回字段。

显式metadata payload **3133B**+成熟Header/fourcc等保守scratch **2048B**=**5181B≤8192B**；原stdout19887B/stderr0、strictUTF8全量≤1MiB，正反case的实际partial观测/拒绝理由、CodeSource与最终原返回日志均完整保留。实际classload确认所有已加载JCodec来自fork，支持来自support，原videokit-fixture-tool02.jar未加载；无资格helper/SixFrameDriver/demux/mux/编码器解码器类加载，JDK charset不误报。

测试只构造自有有限metadata、调用成熟parse和真实getter。stsd正例只验original-header/唯一实际entry政策，使用有限free child；**不冒真实VideoSampleEntry/完整轨道正例**，全checker原VideoSampleEntry门仍在。avcC自有23B metadata源于之前批准冻结CSD payload，仅元数据测试不冒有效媒体。count不一致用真实原头，实际list差异通过公开既有可变API构造拒绝对象，不反射改私有状态。full external alias路径未在此解析，未知/外引用门不放宽。

| 用例 | 实际结果 | 接受范围或拒绝原因 |
| --- | --- | --- |
| dref_alias_original_and_child | PASS_POLICY_ACCEPT | 有限metadata政策接受，非完整文件资格 |
| dref_url_original_and_child | PASS_POLICY_ACCEPT | 有限metadata政策接受，非完整文件资格 |
| stsd_original_header_only_one_actual_entry | PASS_POLICY_ACCEPT | 有限metadata政策接受，非完整文件资格 |
| avcc_original_raw_and_actual_counts | PASS_POLICY_ACCEPT | 有限metadata政策接受，非完整文件资格 |
| dref_unparsed_builder | PASS_POLICY_REJECT | DREF_HEADER_NOT_OBSERVED |
| stsd_unparsed_builder | PASS_POLICY_REJECT | STSD_HEADER_NOT_OBSERVED |
| avcc_unparsed_builder | PASS_POLICY_REJECT | AVCC_HEADER_NOT_OBSERVED |
| dref_unknown_original_version | PASS_POLICY_REJECT | DREF_ORIGINAL_VERSION_FLAGS_REJECTED |
| dref_unknown_original_flags | PASS_POLICY_REJECT | DREF_ORIGINAL_VERSION_FLAGS_REJECTED |
| dref_raw_declared_zero_actual_one | PASS_POLICY_REJECT | DREF_ORIGINAL_COUNT_REJECTED |
| dref_uint32_max_actual_one | PASS_POLICY_REJECT | DREF_ORIGINAL_COUNT_REJECTED |
| dref_duplicate_actual_entries | PASS_POLICY_REJECT | DREF_ORIGINAL_COUNT_REJECTED |
| dref_original_unconsumed_tail | PASS_POLICY_REJECT | DREF_BODY_OR_TAIL_REJECTED |
| dref_index_zero | PASS_POLICY_REJECT | DREF_UNIQUE_ENTRY_AND_INDEX_UNPROVEN |
| dref_external_url | PASS_POLICY_REJECT | DREF_VERSION_OR_FLAGS_NOT_ADMITTED |
| dref_selfref_url_with_ignored_tail | PASS_POLICY_REJECT | DREF_BODY_OR_TRAILING_DATA_UNPROVEN |
| dref_child_unknown_version | PASS_POLICY_REJECT | DREF_VERSION_OR_FLAGS_NOT_ADMITTED |
| dref_child_unknown_flags | PASS_POLICY_REJECT | DREF_VERSION_OR_FLAGS_NOT_ADMITTED |
| dref_unknown_child_type | PASS_POLICY_REJECT | DREF_TYPED_SEMANTIC_API_UNPROVEN |
| dref_untyped_alis_leaf | PASS_POLICY_REJECT | DREF_TYPED_SEMANTIC_API_UNPROVEN |
| dref_failed_reparse_not_observed | PASS_POLICY_REJECT | DREF_HEADER_NOT_OBSERVED |
| stsd_unknown_original_version | PASS_POLICY_REJECT | STSD_ORIGINAL_VERSION_FLAGS_REJECTED |
| stsd_unknown_original_flags | PASS_POLICY_REJECT | STSD_ORIGINAL_VERSION_FLAGS_REJECTED |
| stsd_raw_declared_zero_actual_one | PASS_POLICY_REJECT | STSD_ORIGINAL_COUNT_REJECTED |
| stsd_duplicate_actual_entries | PASS_POLICY_REJECT | STSD_ORIGINAL_COUNT_REJECTED |
| stsd_unconsumed_tail | PASS_POLICY_REJECT | STSD_BODY_OR_TAIL_REJECTED |
| stsd_failed_reparse_not_observed | PASS_POLICY_REJECT | STSD_HEADER_NOT_OBSERVED |
| avcc_unknown_configuration_version | PASS_POLICY_REJECT | AVCC_CONFIG_VERSION_REJECTED |
| avcc_bad_length_reserved | PASS_POLICY_REJECT | AVCC_LENGTH_OR_RESERVED_REJECTED |
| avcc_bad_sps_reserved | PASS_POLICY_REJECT | AVCC_SPS_RESERVED_REJECTED |
| avcc_unconsumed_extension_tail | PASS_POLICY_REJECT | AVCC_BODY_OR_TAIL_REJECTED |
| avcc_declared_vs_actual_sps | PASS_POLICY_REJECT | AVCC_ORIGINAL_COUNTS_REJECTED |
| avcc_declared_vs_actual_pps | PASS_POLICY_REJECT | AVCC_ORIGINAL_COUNTS_REJECTED |
| avcc_failed_reparse_not_observed | PASS_POLICY_REJECT | AVCC_HEADER_NOT_OBSERVED |

## 未来准确命令、原预算与限制

future-execution-contract03.json列完整6helper+2support集合/hash、6源码/JDK/fork唯一身份、排除test/launcher、固定输入路径、未来argv模板；**expectedSha256/expectedBytes/scope全null/UNBOUND**，不读取或查询媒体来填它们。只有负责人另派准确D1QUAL03才能绑定执行，不重用D1QUAL01或任何旧失败scope。

未来仅一个原JVM/worker，heap256MiB/body观察60秒；同一只读NOFOLLOW原fd先核完整SHA及实际EOF再raw demux，累计native requested **1MiB包括hash+全部重读**，块64KiB/read4096/seek128。原sample6/每个262144/CSD64KiB/NAL64/root16/boxes512/depth16不变，原sample key/实际IDR/AVCC与独立AnnexB hash/精确stts DTS及ctts PTS/timebase/layered1200000us/第七EOF/identity矩阵/有限保护box门不减。

原holder在分配前、同原close一次、facade return、body最后完成点、原worker join、同原Popen/全两流自然返回和前后immutable身份分别举证。60秒超窗或异常关准入、sticky UNKNOWN保管原Job/句柄/流，不kill/interrupt/二close/退款/重试，不以exit0/后迟返或最后JSON补绿。所有pending+final/stdout+stderr UTF8合计1MiB，不tail；外部hash/工具身份/control/classload读另列，不能倒灌原1MiB或冒物理磁盘流量。

本合同所需新增观测字段已有真实API与有限政策接入证据，**这不等所有原MP4/AVC字节信息完整保留**；PS头其他bit/保留字段、全语法/RCE、密码学无加密、并发可变对象与成熟库内部metadata allocation边界、解码等效仍有限或未证。可信准确良性文件范围之外不推断安全，不添加坏atom/资源探针或另parser。未知/不支持、edit/nonzeroctts/不完整字段继续BLOCKED。

fork原版权/FreeBSD/JAAD PublicDomain+FreeBSD/GuavaApache2、新修改通知/SBOM与原support项目说明均保留在licenses；不冒官方未修改身份、产品发行/专利/FFmpeg许可。原工具、fork、旧helper、产品依赖均未改。

本准备新增缺陷0，实际文件资格尚未运行。完整源码/class/support/CodeSource/编译与政策原返回/字段schema/未来合同冻结发负责人，等待准确实际D1QUAL03另派，不自动读MP4或做后续测试；D1未过M0未启，旧UNKNOWN保持。
