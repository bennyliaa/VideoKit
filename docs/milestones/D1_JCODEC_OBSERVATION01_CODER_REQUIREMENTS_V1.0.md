# JCODEC_OBSERVATION01 开发要求 V1.0

2026-10-21；负责人正式派D1_JCODEC_OBSERVATION01一个完整审计后端开发批。依据独立报告18bc1c596c10ffeaf3dab3af9bb4e65e5f4ce73d4a9f7e5e997d476efb08b566，child self-contained有限语义通过，原dref/stsd头与avcC原始信息被库丢弃，整体资格仍BLOCKED。原媒体/编码器/失败scope和候选不改，不能缩要求冒PASS。

本批明确批准仅独立审计工具源码副本的最小可观测性补丁，不是修改产品Media3/Android依赖或自写容器/codec。新目录docs/coder/d1jcodec-observation01，准确来源仍已封存org.jcodec0.2.5的708源码。新artifact必须明确标注0.2.5-videokit-observation01及原source hash+补丁hash，绝不冒原官方JAR/签名或沿原c4ed身份运行；保留原版权/FreeBSD/JAAD/Guava许可、修改通知和SBOM差异。新审计fork不进入App/APK/编码工具或替换其classpath。

允许生产源差异仅DataRefBox、SampleDescriptionBox、AvcCBox三处：在原parse已经读取/skip/mask的同一位置保留原容器version/flags word、原declared count unsigned值；avcC configurationVersion/raw保留位字节/SPS计数字节等实际消费但被丢信息及实际parse完成状态。通过只读getter暴露，实例新建或parse失败不能显示已观测；parse前清旧观察、完成后才置observed，合法原值不从builder/default/doWrite反推。若需要其他字段/生产源更改，先在整包报告明确阻塞，不临场扩补丁范围。

原字节消耗/结构解析/box factory/真实AliasBox或UrlBox/stream bounds与异常语义保持：把skip1替等量get1可保原configurationVersion，但不能改变解析算法、容错、NAL/SPS/codec/muxer/timebase或成熟doWrite输出。禁止新增手写box/AVC parser、重序列化造golden、改文件或encoder、手写假成熟接口。getter正确性需要真实原parse输入/消费位置/字段来源证据，版本/flags/声明count的原始值与实际children计数分列。

本批一次固定JDK javac/jar构建独立审计JAR及独立helper测试（测试不入生产JAR）；输入16MiB/全输出64MiB/512m原编译工具60秒观察/串行，无新依赖/网络/Gradle/缓存/annotation processors。完整原708源码diff、3文件改前后hash/逐字段byte-consumption、真实class来源/manifest新身份/许可通知/编译原返回冻结。禁止覆盖旧源/JAR/classes/pins。

允许有界非媒体元数据parse单元自测：只原成熟三box parse及child AliasBox/UrlBox语义，最小内存payload≤8KiB、不读取MP4媒体/不demux/encoder/decoder/mux/Main。核合法头保留、实际children与declared count不一致仍原值记录、unknownversion/flags保留供策略拒绝、parse失败不泄旧值、同原消耗位置与基线一致；avcC仅已有来源允许的最小合法元数据，不以测试构造NAL冒有效媒体。比较原/补丁解析异常/位置及已有getter语义，不能修改原库求绿。单JVM256m/总5秒/原线程进程自然返回，超窗UNKNOWN保管无kill/interrupt/重试。可只测能够安全正常返回的最小输入，不做资源攻击。

完成为可审计原始信息保留能力，不是任何媒体资格通过。完整source+patch/JAR/真实编译与单测来源/全getter合同/缺口/seal ZIP后报负责人，独立整包审后再将新fork准确接入独立资格checker、另批对固定媒体只读复核。实际文件解析0/生成0/设备0，旧48945/17257不碰；D1未过M0未启。

## 2026-10-21 阶段A完整差分判据补充

负责人核c28a3285dba537cceaf3ffde80888b975e2e6393b5fb72dbb7b855f59bf7486f，接受OA01–OA32准备完成/全部PREPARED_NOT_RUN；原708集合/旧checker31证据保持。完整合同见tester阶段A报告与9项证据，不把对旧源码分析当浮动fork缺陷。

必须集中覆盖：原dref/stsd同getInt4+4保留原word/uint32声明count、actualchildren分列；avcC原skip1位置/configVersion、flags原byte/reserved高6、SPS count原byte/reserved高3/PPScount，同原消费点保存。parse首读前清新增观测、正常原返回后才complete；fresh/builder/doWrite不冒观测，complete不等合法结构或EOF。getter失败不得泄上次原值。

保留原legacy children/SPS/PPS重复parse append及失败partial行为，不能因清观测而清旧列表/修算法。NIOUtils.skip在空输入跳0，与直接get替换可能改变异常类别/position/legacy字段赋值顺序，需原/补丁同输入差分留证，若不等则调整观测实现，不修改原语义。getShort signed/checkState/NIOUtils切片消费等同样保持，禁止预扫/容错/顺便修异常。原NodeBox可能忽略count mismatch/剩尾、AvcC可能不消费扩展，观测complete不能冒全部校验通过。

这些原始信息将供后续checker严格拒绝/区分UNPROVEN，不在本批自动读取原MP4或放行整体资格。完整新fork差分/真实构建class来源/新身份许可/原返回及OA矩阵封存后再独立B。
