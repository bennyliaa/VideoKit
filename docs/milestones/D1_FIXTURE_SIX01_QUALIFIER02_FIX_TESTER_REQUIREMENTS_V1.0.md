# SIX01 QUALIFIER02_FIX 准备及有限语义自测要求 V1.0

2026-10-21；负责人核完整报告a9eb9630a356e7dbd0414b917dbbdd66f19eae15a634f40f973cfe057d262b61，接受BLOCKED_CHECKER_DREF_UNPROVEN_ORIGINALS_RETURNED。QUAL-B01/P2是checker准入兼容性限制，原实际失败不改、不称媒体损坏，六sample/CSD/时间仍NOT_REACHED。

正式派tester在新docs/tester/D1_FIXTURE_SIX01_QUALIFIER02_FIX_PREPARATION目录集中修复独立测试helper，不改任何coder媒体/tool/JCodec或原helper/class/seal。负责人读取冻结成熟AliasBox.parse确认其使用FullBox flags&1标self ref，原AbstractMP4MuxerTrack.addDref生成alis LeafBox四字节00000001；这仅源码语义，不代真实文件观察。应利用原成熟AliasBox/UrlBox/FullBox/原Box factory等语义API严格验证实际dref：entry唯一、数据引用索引准确、self-contained flags及版本/未知flag/尾部/外部URL/alias路径按明确受限合同处理，记录真实fourcc/实际类型/entry数量/判据来源。

不能只加alis字符串白名单、无条件放行LeafBox或删掉self-contained门；禁止自写MP4/AVC字节解析器/修改成熟factory。若原API无法给足版本/flags/外部引用等安全事实，保持BLOCKED并交准确缺口，不取生成receipt内部信息当真实文件golden。其余轨道/样本/保护/时基/全EOF/预算/原返回检查不削弱。静态复核后续所有同类自家库表示差异，一次整包说明，不逐字段边跑边改。

允许一次固定JDK javac编译新helper及独立语义检查辅助、生产引用仍唯一已冻结tool02 JAR c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd；无新依赖/网络/Gradle/缓存/旧helper改动。允许一个有限非媒体语义检查JVM，只用原AliasBox/UrlBox/FullBox/明确最小dref对象构造验证接受/拒绝边界（self-ref url/alis、external/unknown/重复entry/索引错误/未知标志/信息不足拒绝）；非媒体字节≤4KiB，无实际MP4读取或demux/encoder/decoder/Main生成。仅真实成熟API，不反射改状态。若API问题首次编译失败保留集中报告，不循环引库重构建。

编译512m观察60秒/输出16MiB，语义自测256m/单JVM串行/总5秒/所有原线程finally放门join及原进程自然返回，异常超窗保管原句柄UNKNOWN，不kill/interrupt/二close/重试。当前不实际执行新资格helper或再读原媒体，不重用D1QUAL01-CANDIDATE-001。

完整新源码/class集合hash、来源/编译原回执、语义自测实际日志、受限dref合同、后续整体检查静态兼容审计、准确未来一次argv和预算/原返回条件整包冻结主动报告负责人。核完整新checker后负责人另派准确新scope一次真实资格，不在本批自动重跑。coder保持生成media/tool冻结；旧48945/17257不触，D1未过M0未启。

## 2026-10-21 原DataRefBox API能力边界决定

tester确认成熟DataRefBox.parse丢弃原容器version/flags与声明entry_count，只暴露实际children/header；这是原始字段无法独立证明的API缺口，不是已发现媒体字段错误。负责人决定：不以实际children1代声明entry_count1，不重序列化造golden，不删门/改factory/自写parser。原容器version-flags/声明count为整体原始结构资格的必须未证字段，无法获得时保持整体BLOCKED。可以分别记录child AliasBox/UrlBox的真实FullBox version0 flags1/body4/外部引用拒绝及实际entry/索引等有限结果，但不得签完整HOST_CONTAINER资格。

继续本批原已授权一次编译及非媒体语义自测，完整新helper/实际测试证据/API能力矩阵集中交付，明确原QUAL-B01有限修复与新原始信息不可得限制，真实文件不读取/不重试。不要为全绿增加另一解析链或连续询问字段放宽。负责人将依据完整报告另安排成熟后端实际可行性和缺口处理，原容器功能目标继续OPEN，不将部分观察替代目标。
