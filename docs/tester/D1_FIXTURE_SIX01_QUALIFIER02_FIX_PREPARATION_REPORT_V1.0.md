# D1 FIXTURE SIX01 QUALIFIER02 修复准备与有限语义自测报告 V1.0

2026-10-21；tester；QUALIFIER02_FIX_PREPARATION。

## 结论

**PASS_LIMITED_CHILD_SEMANTICS_WHOLE_DREF_METADATA_BLOCKED**。原QUAL-B01中UrlBox-only子条目准入问题已在新helper中有限修复，一次编译和一个非媒体语义JVM的26用例全部通过；不以此关闭原容器资格目标。原DataRefBox API丢弃必须的容器version/flags/声明entry_count，**整体HOST_CONTAINER资格继续OPEN/BLOCKED**。原唯一资格运行a9eb9630...的BLOCKED结果不改，不判媒体损坏；新资格helper实际运行0，媒体读0、实际六sample/CSD/时间线仍未证。

本批依据 docs/milestones/D1_FIXTURE_SIX01_QUALIFIER02_FIX_TESTER_REQUIREMENTS_V1.0.md及末尾负责人明确API能力边界决定，原字节快照见authorized-requirements-snapshot.md。所有新源码/编译/测试/报告证据在新tester目录，不改原媒体、coder工具/成熟库、旧helper/class/seal；不重用D1QUAL01-CANDIDATE-001，不自动重跑或另起解析链。D1未过、M0未启，旧48945/17257未查询干预。

## 新实现与准确合同

新Six01ContainerQualifier02来自旧源码21809B/SHA a757ecc7587c9a02ce817152f092659863ff3370e6e594bef5acbe4a08ad3544。完整diff/source-derivation证明仅新类/收据/线程名、替换dref门、mandatory整体阻塞与同原线程join后的partial child observation，原轨道/保护/sample/CSD/时基/EOF/读预算/owner/close/deadline门未削弱。新DataReferencePolicy只调用成熟typed box/Header/FullBox/AliasBox/UrlBox语义，无MP4/AVC/alias字节解析，无成熟factory/library改动，无反射改状态。

受限child门同时要求：实际DataRefBox存在/fourcc=dref、实际children恰1、sampleEntry dref index恰1；child fourcc/class严格对应alis/AliasBox或url /UrlBox，拒绝LeafBox/其他fourcc即使字符串看似alis也不放行；child FullBox version0/flags**恰1**，不接受仅flags&1而未知位存在；child原Header普通8B/body**恰4B**，dref原Header普通8B/body严格等于8+child完整size，排尾部/信息不足。AliasBox必须isSelfRef、fileName/extras为空且recordSize0，URL必须getUrl=null。记录真实fourcc、类型、实际count/index、version/flags/body及判据来源，不能从生成器receipt填golden。

**这些只证明child受限语义，不证明dref原容器header。** 原DataRefBox.parse直接丢弃两int，actual children不可代声明count，重新序列化会写新0/实际size而失去原值。负责人要求其必须原值未证则整体阻塞，新requireOriginalContainerMetadata无绕过参数、始终抛DREF_CONTAINER_ORIGINAL_HEADER_METADATA_UNPROVEN；不把预期BLOCKED写成媒体失败或HOST_CONTAINER成功。没有调用任何原MP4，原实际child类型尚未重新读取。

## 一次编译、class划分与原返回

前置核原tool02 seal2774记录不变、唯一生产JAR1954730B/SHA c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd、固定JDK release/java/javac/jar/modules合同身份；旧准备13证据、旧失败14证据及报告hash均核不变。读取的是冻结代码/工具/控制证据，未打开或查询实际媒体文件。

固定javac原PID41720，2026-10-21T01:45:48.554594+00:00至2026-10-21T01:45:49.601552+00:00，自然exit0/约1.047s，原stdout/stderr句柄关闭，unknown false。只有一次 -J-Xmx512m --release11 -proc:none -implicit:none、空source/processorpath、唯一准确JAR classpath，清除Java注入环境，无首次失败或补编译。完整原argv/原流见compile-001。

实际5个class major55，静态读取SourceFile和方法Code SHA核来源。4个helper class（Qualifier02/其Job/InputOwner/DataReferencePolicy）复制到helper-classes；1个DataReferenceSemanticCheck只放test-only-classes，不进未来helper classpath，复制与原javac输出逐字节一致。来源/源码与class准确SHA逐项见compile-class-identities.json，未来类集合合同明确，不靠文件名声称编译对应。

## 一个有限非媒体语义JVM：实际26用例

固定java/heap256MiB/单JVM串行，原PID26084，2026-10-21T01:45:49.864552+00:00至2026-10-21T01:45:50.069044+00:00，自然exit0约0.203s。原唯一非daemon语义worker在finally标body返回，同原worker实际join=true；内部elapsed51763100ns<5秒、外部原process观察5秒未超时，原两流完整关闭、sticky unknown false、kill/interrupt/二close/重试0。没有人为挂起门或未归还线程。

26个case：**4 child接受、20拒绝、2 mandatory整体阻塞**。接受包含selfref Alias/URL最小对象和通过原BoxFactory/DataBoxes解析自有序列化最小对象；这是自测内存对象，不是原文件重序列化或原媒体证据。拒绝missing/empty/duplicate entry、index0/2/-1、nonselfref alias、外部URL/矛盾selfref+URL、未知alias/url version、未知flags、alias/url/dref尾部、缺body信息、untyped alis Leaf、unknown cios、type/fourcc错配；最后2个确认child成立也必须因原容器header未证而整体BLOCKED。外部alias用非selfref flags的最小对象验证前置拒绝，**没有声称解析过完整外部alias路径记录**，完整路径API/格式覆盖未运行。

显式非媒体payload分配**132B**（两64B最小对象buffer+一个4B拒绝Leaf），成熟Header四字符临时数组按固定源码保守另界≤64B，总受限4KiB内；不把metadata对象/JVM全部内存冒成132B，堆256MiB与对象分配仍是独立口径。原测试stdout 14189B/stderr0，27条严格UTF8 JSON（26case+summary），完整原日志保留；日志和classload审计是控制证据，不混成4KiB非媒体payload量。

class-load日志确认实际AliasBox/UrlBox/DataReferencePolicy和原factory加载，**资格helper/原SixFrameDriver、MP4Demuxer/MP4Muxer、H264Encoder/Decoder均未加载**。factory映射带来的其他metadata box类加载不冒媒体处理；本批无实际MP4/demux/codec/设备调用。所有非媒体语义用例的实际接受/拒绝理由和字段逐条见semantic-results.json。

## 后续整体静态兼容与成熟API能力矩阵

完整核后续门，一次集中交付，没有逐字段边运行边修改。表中的STATIC_COMPATIBLE只是冻结API/源行为与保留门兼容，不代真实文件运行或解除原始信息缺口。

| 字段/门 | 级别 | 分析与边界 |
| --- | --- | --- |
| DREF_CHILD | PASS_LIMITED_26_NONMEDIA_CASES | Typed aliases/url version0/flags exactly1/body4, parent exact body and actual unique child/index1; no pathname/URL/extras permitted；No actual MP4 child parsed this batch |
| DREF_ORIGINAL_HEADER | MANDATORY_BLOCKED_API_INFORMATION_LOSS | parse discards original version/flags and declared entry_count; no getters; doWrite emits regenerated0/actual-size；Cannot prove by actual children or serializing parsed objects; helper hard-blocks whole qualification |
| STSD_ORIGINAL_HEADER | UNPROVEN_SAME_KIND_OF_API_INFORMATION_LOSS | parse also discards original version/flags and declared entry count; children retained, doWrite generates values；No actual original-header proof; no additional parse chain or new success claim |
| ROOT_LAYOUT | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | getRootAtoms/Atom/Header expose true root offset/type/size/header; existing contiguous one-ftyp/moov/mdat and accepted root set unchanged；Mature Header reader behavior is not adversarial full-conformance validation |
| TRACK_AND_MATRICES | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | Mature muxer identity track/movie matrices and one AVC track are compatible with existing checks; API values remain actual getters；Source behavior never substitutes actual file getters |
| VIDEO_ENTRY_FACTORY | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | avc1 VideoSampleEntry and avcC mapping supported by original video factory; width/height/drefInd real getters；No full raw reserved-byte proof |
| AVCC_CONFIG | STATIC_COMPATIBLE_WITH_INFORMATION_GAPS | SPS/PPS parsed lists exclude NAL header; create/read/store and getPicSize compatible; parseAVCC can use real typed box；AvcC parse skips original configurationVersion and masks reserved bits without exposed getters; not full original AVC configuration syntax proof |
| CSD_NORMALIZATION | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | readSPS/readPPS accept payload without NAL header; saveCodecPrivate adds mature start/header representation; original limits untouched；No decoder invocation and no independent actual CSD here |
| STSZ | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | Mux createSampleSizesBox2 emits per-size table/default0, count6 available; getNextFrame fixed bounded buffer compatible；Table arrays may be allocated by mature parser before guard; malicious input excluded |
| STTS_CTTS_EDITS | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | Sequential Packet i/duration1 produces stts count6 duration1; no offsets/edits expected source-wise; existing nonzero-ctts/edit block preserved；DTS must derive from actual stts; no source expectation substituted into receipts |
| REAL_PTS_DTS | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | getMediaPts is composition PTS; DTS independent stts with zero ctts/no edit. Existing integer BigInteger conversion unchanged；Original packet alias cannot independently prove DTS |
| LAYERED_DURATION | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | movie/track/media scaling source matches actual duration getters and existing1200000us check；No date overwrite, no real duration observation this batch |
| KEY_AND_IDR | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | allI can omit stss; demux absent stss marks key. Existing NAL IDR check independent; stps false required；Key flag alone not proof of complete AVC conformance |
| RAW_AVCC_ANNEXB | STATIC_COMPATIBLE_RUNTIME_NOT_RUN | raw demux preserves AVCC; mux removes SPS/PPS; decodeMOVPacket only length-prefix conversion on copy; separate hashes unchanged；Not raw encoder AU equality, no decoded equivalence |
| PROTECTION_AND_DREF | LIMITED_SCOPE_ONLY_RUNTIME_NOT_RUN | Existing parsed protection-box rejects and strict unknown reference rejection unchanged; finite admitted scope；Not cryptographic no-encryption, global MP4 compliance, hostile input proof or RCE safety |
| ORIGINAL_RETURN_BUDGET | STATIC_PRESERVED_RUNTIME_NOT_RUN | One original readonly fd, hash+all rereads requested1MiB, block64K/read4096/seek128, once close, body-last-point and original join; unchanged；External Popen/two streams/post identity remain future separate evidence; no input read |
| PARTIAL_RECEIPT | COMPILED_ONLY_RUNTIME_NOT_RUN | Emit partial actualDataReferenceChildObservation only after same original worker joins, even when full container observation null；Cannot fill actual fields from generator or expected constants |
| WHOLE_GATE | PASS_TWO_IN_MEMORY_MANDATORY_BLOCK_CASES | No bypass/flag/alternate scope path: missing mandatory raw dref original fields always throws DREF_CONTAINER_ORIGINAL_HEADER_METADATA_UNPROVEN；Whole HOST_CONTAINER goal OPEN/BLOCKED; backend feasibility must be separately dispatched |

其中额外发现同类信息损失：SampleDescriptionBox.parse也丢弃stsd原version/flags/声明entry_count；AvcCBox.parse跳过原configurationVersion并mask reserved位而无原值getter。它们是成熟API能力缺口，**不是媒体坏字段或新运行复现**。原保护/box守卫仍为有限parsed scope，不冒全MP4/AVC合法性、无加密密码学证明或恶意内容隔离。带源码SHA/行号证据与整体18项矩阵已交，不加备用parser求绿。

## 冻结合同和下一步

future-execution-contract02.json保全准确4class集合/3源码/唯一JAR/JDK hash、未来argv模板、固定输入路径和原预算；未来input hash/bytes/scope保持**UNBOUND**，旧D1QUAL01 scope明确不可复用。模板不授执行权；当前helper即使child成立也会因原始dref header缺口准确BLOCKED，**不建议原样重跑期待整体PASS**。需负责人依据完整矩阵统一安排成熟后端可行性/必须字段取得方案，新实际范围另签。

未来合同仍是同一只读原fd/hash+全部重读requested1MiB、块64KiB/read4096/seek128、六sample单262144/CSD64KiB/NAL64/root16/box512/depth16、worker1/heap256MiB/body观察60秒/所有stdout+stderr1MiB。原holder在分配前登记、native close一次、facade/cleanup body最后点/同原worker join/原Popen两流自然返回与前后identity分别判；异常/超窗保留sticky UNKNOWN和原Job/句柄，无强停/退款/二close/重试；外部hash另账。原成熟库内部allocation界仍未证。

本轮只对QUAL-B01的child语义作有限修复证据，不关闭整体问题/容器目标，不回写原准备成功或原实际失败报告。**整体资格OPEN/BLOCKED，实际媒体不读、不重跑**。完整报告/源码class/原两进程与语义日志/合同/全部API缺口冻结发负责人，停止后继；coder媒体/tool保持冻结，旧UNKNOWN未触，D1未过M0未启。
