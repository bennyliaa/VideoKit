# D1 FIXTURE SIX01 独立容器资格检查器准备报告 V1.0

2026-10-21；tester；范围 SIX01_QUALIFIER_PREPARATION。

## 结论

**PASS_PREPARATION_COMPILED_ONLY_RUNTIME_NOT_RUN**。独立 helper 已完成源码/API审查并一次编译成功，具备后续准确只读资格批的准备条件。本阶段没有启动 helper JVM、Main、生成器、编码器、decoder、demux或设备；实际媒体字段全部 NOT_RUN，输入 hash/大小/scope 保持未绑定。不能据此签容器合格、HOST_ISOLATED_FORMAT_V1、READY、COMMIT、解码等效或 Media3 资格。

本报告按既有 tester Markdown 报告惯例交付。依据 docs/milestones/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION_TESTER_REQUIREMENTS_V1.0.md；源码及全部新产物仅在 docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION。本准备批未读取或查询浮动生成媒体/生成证据内容；负责人后来派发的完整生成B证据审按顺序在本准备整包封存后另做，不计入这里的结果。

## 准确依赖与原编译返回

原 tool02 seal SHA256 5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d 的2774项及ZIP2773唯一成员均独立核验；原独立报告4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4和其36项证据保持原样。准确生产JAR1954730B SHA256 c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd；仅用其原JCodec0.2.5和既有WorkerDeadline/ReceiptJson。未修改coder、未重建库、无新依赖或网络。

固定 JDK D:/Android/Android Studio/jbr，release/java.exe/javac.exe/jar.exe/lib/modules准确身份均复核，见 compilation-summary.json。javac原PID 30664，2026-10-21T01:27:33.575245+00:00启动，2026-10-21T01:27:34.703580+00:00自然返回，实际1.14秒，exit0，原两个输出句柄关闭；stdout0B/stderr0B，sticky timeout false，强停/重试0。仅一次 -J-Xmx512m --release11 -proc:none -implicit:none 编译，空 sourcepath/processorpath、唯一准确JAR classpath、清除Java注入环境。完整argv与原返回见 compile/owner.json，未执行新class。

源码21809B SHA256 a757ecc7587c9a02ce817152f092659863ff3370e6e594bef5acbe4a08ad3544。实际产出3个class，class major55，SourceFile均为Six01ContainerQualifier.java，静态独立读取classfile核身份/方法Code hash，未加载类。准备目录在汇总前65317B，完整封存后亦小于16MiB；没有首次失败、补编译或运行验收。一次编译控制器保留原Popen、60秒观察及UNKNOWN自然等待分支，无kill或自动后继。

## API能力、观察口径与未来合同

选择成熟库 **createRawMP4Demuxer**，明确避开默认 createMP4Demuxer 的H.264包自动转换。实际file root/box/track/sample数据来自原MP4Util、MovieBox、TrakBox、SampleSizesBox和MP4DemuxerTrack API，没有自写MP4/AVC字节解析器。H264Utils.decodeMOVPacket只是成熟库AVCC→AnnexB字节表示转换，未调用解码器，而且本阶段尚未运行转换。

未来会验证一个视频零音频、无其他轨道、单avc1、entry与实际SPS均256×144、track/movie均identity matrix、self-contained data reference、允许box范围内无保护信号。root atom需精确覆盖整个文件且仅一ftyp/moov/mdat；未知root、edits、非零ctts、保护box和不支持字段直接BLOCKED，不默认成功。没有把有限元数据检查冒称密码学未加密证明。

六个样本均读取实际stsz与真实packet，预检每个<=262144B，固定复用同一buffer，文件偏移落在实际mdat，记录实际AVCC hash、NAL type/hash、容器keyflag与真实IDR，检查第七packet为null。实际avcC的SPS/PPS提供hex/hash并通过成熟库读SPS/PPS与尺寸，累计CSD64KiB。归一化AnnexB hash单列，不能与生成器含SPS/PPS的raw AU hash直接相等；生成内部观察不代文件读取结果。

**getMediaPts是composition PTS，不能当独立DTS**。DTS通过真实stts条目累计，限定无edits/零ctts后再与packet PTS/时长核对。真实stts/media/track/movie时长与真实时基分别做精确整数有理映射，非整微秒或溢出阻塞。期望六个200000us/总1200000us只作断言，不填充缺失字段。完整字段合同见 receipt-schema.json，真实结果均null/NOT_RUN。

## 预算、原owner与停批

固定唯一输入路径，不支持任意文件参数。未来须另签准确输入sha/字节/scope并先核整个helper class集合/JAR/JDK身份与只读不可变属性；本交付 future-execution-contract.json 仅含命令模板，三项尚未绑定且无执行授权。实际检查原JVM最多1/heap256MiB/原worker1/body观察60秒/所有原stdout+stderr合计1MiB，由后续准确控制器保管原Popen与两流，不以exit0或最后一条JSON替代原返回。

原InputOwner在FileChannel分配前登记；同一个只读NOFOLLOW句柄完成全文件SHA/实际EOF、root扫描、demux所有重读与seek。input<=1MiB且**累计native requested读预算1MiB包括hash与重读**，块64KiB、read4096次、seek128次，实际返回字节另记；预算不退款。接近1MiB输入可能因hash+重读耗尽预算，准确BLOCKED而非重试。控制元数据/JDK/JAR身份读取与未来外部文件hash另列，不混入媒体ledger。

原库facade close委托同一个InputOwner，guard只准一次native close，finally再次到guard不会二次native close。真实close返回、worker body最后完成点、同原worker join以及外部原进程返回分别举证。deadline/异常/不确定关后续准入且sticky UNKNOWN，保留原Job/线程/句柄，不interrupt/kill/第二close/退款/换scope重试。pending位置只报最后adopted或UNKNOWN，close后仅LAST_ADOPTED_BEFORE_ORIGINAL_CLOSE；size明确是原open实际核对过的expected值，不声称每次新OS查询。失败时先前已观察但未完整形成的字段保留未证，不用成功exit补齐。

## 能力缺口与后续门

成熟库内部metadata分配发生在部分postparse守卫前，host文件上限不证明其内部内存安全；只准准确冻结的良性合成文件，禁止恶意atom/资源注入。本批编译通过只证明API/类型和class产出，运行性能、OS权限、实际无加密/实际样本/实际时长尚未验证。readonly与外部不可变性需未来控制器pre/post身份封存；单fd不防外部并发改写。实际Android/Media3资格及HOST_ISOLATED_FORMAT_V1仍另批。

无新缺陷需coder本轮修改；需要下一准确运行批验证所有runtime门，不能将准备通过升级为实际资格通过。原48945/17257 UNKNOWN未查询、未attach、未终止；N2历史ABORT不重复。D1未过、M0未启。准备报告和证据冻结后发送负责人，随后只做已正式派发的完整生成B纯Python证据/身份审，不自动运行helper或后续测试。
