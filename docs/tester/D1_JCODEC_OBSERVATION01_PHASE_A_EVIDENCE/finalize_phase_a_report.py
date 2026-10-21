from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
a=load(E/'authority-and-baseline.json');cases=load(E/'independent-oa01-oa32-oracles.json')['cases'];assert len(cases)==32 and all(x['status']=='PREPARED_NOT_RUN' and not x['floatingForkRead'] and not x['dynamicExecuted'] for x in cases)
assert a['all708SourceHashesMatched'] and a['all708SourceBytes']==4435752 and a['oldChecker02EvidenceFilesPreserved']==31 and a['newCompilerJarJvmProcesses']==a['actualMediaReads']==a['floatingForkQueriesOrReads']==0
table='\n'.join('| '+x['id']+' '+x['area']+' | '+x['oracle']+' | PREPARED_NOT_RUN |' for x in cases)
report=R/'docs/tester/D1_JCODEC_OBSERVATION01_PHASE_A_REPORT_V1.0.md'
text=f'''# D1 JCodec Observation01 阶段A独立验收准备报告 V1.0

2026-10-21；tester；仅旧冻结基线静态审查，阶段A。

## 结论

**PHASE_A_OBSERVATION_PATCH_ORACLES_PREPARED**。独立OA01–OA32验收判据已准备，全部 **PREPARED_NOT_RUN**；已核原708源码4435752B及旧checker02/31证据不变，准确定位三处原始信息丢失、消费点和失败/默认状态。未读取、列目录或查询coder浮动fork，未编译/打JAR/JVM/非媒体parse/实际MP4/设备，也未实现观测补丁。阶段A不对新fork质量、构建、原始信息保留能力或媒体资格给PASS。

依据 docs/milestones/D1_JCODEC_OBSERVATION01_TESTER_REQUIREMENTS_V1.0.md；原字节快照与hash在本证据根。coder新fork开发可并行，但tester本阶段只审旧冻结源码/原checker02及完整API矩阵，没有共改文件/构建缓存。完整fork须负责人先核冻结再另派B，有限元数据动态范围亦另准确派。

整体容器目标仍 **OPEN/BLOCKED**；原QUAL-B01实际失败不改、不判媒体损坏，checker02子条目有限语义通过不代原dref/stsd头和avcC原始信息可得。D1未过、M0未启；旧48945/17257 UNKNOWN未查询或干预。

## 原始身份与允许差异

基线原tool02 seal SHA256 5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d、生产JAR1954730B/SHA256 c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd准确匹配；本A只将原seal/JAR本身身份作anchor，**没有声称本A再次核seal全部2774项/ZIP**。708实际Java集合与原pins完全相等，全部字节/hash匹配4435752B；基线635JCodec+73内置JAAD来源保留。

旧checker02报告18bc1c596c10ffeaf3dab3af9bb4e65e5f4ce73d4a9f7e5e997d476efb08b566、manifest2a0a2f9143121a1b1be9221f6f01d2960f2f3a926884bf8841f09336098da90e及31证据逐项复核，报告/源码/4helper类/测试与完整矩阵均不变。未触原生成MP4或其路径属性，不把代码/JAR控制身份读取冒媒体IO。

新fork未来生产源码允许差异严格限三文件：org/jcodec/containers/mp4/boxes/DataRefBox.java、SampleDescriptionBox.java，以及org/jcodec/codecs/h264/mp4/AvcCBox.java。其余705个Java必须字节不变；不得改变NodeBox/Header/BoxFactory/DataBoxes/AliasBox/UrlBox/codec/muxer/driver、原产品依赖或重构另一解析链。新增测试辅助与修改通知要独立归类，不混入生产差异数。

新artifact必须明确 **0.2.5-videokit-observation01**，记录原source archive9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db、708基线hash、3文件改前后hash和patch hash及新JAR实际身份。不能冒官方未修改JCodec或沿c4ed旧身份运行，不进App/APK或替换编码工具classpath。新jar/seal/patch/getter名/class身份本阶段全null/UNBOUND，未伪造待开发接口。

## 原消费点与独立字段判据

所有offset以parse入口ByteBuffer.position为相对0，非整文件偏移。

DataRefBox与SampleDescriptionBox均在相对0..3原getInt消费version-flags word、4..7原getInt消费声明entry_count，再super.parse NodeBox。补丁只能在同两次原读取保留原raw32值；计数需准确unsigned32 long0..4294967295，version为raw高8、flags低24，只从同一个已消费word推导。声明count与实际children分列，不能改成children.size、clamp或按声明count新增分配/循环。

原DataRefBox.doWrite写0和boxes.size；stsd.doWrite写0和max(1,boxes.size)。这是新生成字节，**不能序列化parsed对象反推原version/flags/声明count**；正常构造、create方法、已有setter与doWrite都不能令原始观测状态true。

AvcCBox相对0是原NIOUtils.skip(input,1)丢配置版本；相对1/2/3的profile/compat/level原getter已保留。相对4原get flags字节随后mask0x03形成nalLengthSize，必须另保留同次消费的完整unsigned raw byte及其高6 reserved位；相对5原get SPS计数字节mask0x1f，必须保留完整raw byte/high3 reserved及low5声明SPS count。PPS声明uint8来自原SPS循环后的同次get，位置可变，不能写死相对偏移或扫第二遍；实际SPS/PPS列表数与declared count分列。

原NAL头mask/checkState、signed getShort长度和NIOUtils.read移动/异常均原样，不能新增AVC parser、纠正长度或更改SPS/NAL/codec语义。额外观测若交付，必须同样来自已消费且获准的原字段、不增加读取/生产源范围；信息仍不足准确BLOCKED，不能以更多原始字段已“可写出”为观测证据。

## 状态与失败语义：必须保持的区别

新增观测状态在每次parse可能失败的首条输入操作前清旧，在原parse正常完整返回后才标complete；构造/new/createEmpty/createAvcCBox/builder/setter默认 **NOT_OBSERVED**。complete=false时新增getter应拒绝/显式缺失或明确不可采信，不能把默认0或上次值当已观测。只读getter不能修改源/ByteBuffer，原始快照不可经外部setter或可变引用篡改；具体API名待完整fork绑定，不自造假接口。

**parse正常返回不是原始结构有效。** 原NodeBox按实际剩余字节解析children，忽略父声明count，尾部<8B可未消费；AvcC原例程也未保证消耗所有扩展/尾部。即使complete=true，后续策略仍须核原version/flags/declared与actual/count/reserved/边界；不能把完成位变成合法性、全EOF或媒体PASS。

原NodeBox/AvcC复用对象会保留已有children/SPS/PPS，失败前可能已部分写legacy字段或追加列表。为修复观测状态只能清新增观察字段，**不能顺手清legacy列表、初始化原字段、改变已有getter或异常位置**。oracle专门覆盖good→fail、good→good以及raw count与累积列表数的区别。

原NIOUtils.skip只跳min(remaining,1)，空buffer跳0再在原profile get失败；替换成等量get捕获配置版本，必须逐项保留空/短输入的实际消费位置、异常类别和legacy赋值结果，不能预扫/预校验整头而改变原执行顺序。父getInt是各4B边界的原消费；原getShort为signed、NAL checkState和NIOUtils.read切slice/position语义均保持。精确异常堆栈语句位置可因同消费点保存而不同，但不能吞异常、wrap成别类、容错修复或改变原异常时legacy状态。

本A仅由源代码识别这些判据；**未执行短输入、坏metadata或任何parse负例**，也未把静态推导当原/补丁差分运行结果。未来有限动态必须先静态排除计数驱动的资源分配等行为，再只用准确批准的≤8KiB安全最小元数据；禁资源攻击/恶意atom/媒体有效性或解码测试。SPS/PPS素材须已知获准来源，不能由测试构造NAL冒有效媒体。

## OA01–OA32验收清单

| 项目 | 独立oracle | 状态 |
| --- | --- | --- |
{table}

## 后续B准确收据与分类合同

完整新包需具备：主报告/新版本与artifact manifest，708源完整差异/3patch及before-after hash，逐字段原消费和getter状态合同，实际编译/jar/单元测试原Popen与两流/返回，class来源和测试排除，版权/修改通知/SBOM差异，以及seal/ZIP严格同成员与hash。编译成功/测试exit0均不能代字段getter正确性或原返回事实。

未来原/补丁动态差分必须证明两套真实artifact/类来源，防parent-first classpath误把原与补丁测成同一个；若单JVM限定下采用隔离loader等具体方式，需随完整冻结代码和准确另派核定，**本A没有编写/授权运行该机制**。差分只比较成熟三box parse/child语义、位置/remaining/order/既有getter和实际异常，新增观测getter只在complete真时采信，不引入额外structural parser。

coder批的输入16MiB/输出64MiB/编译512MiB/60秒串行、非媒体metadata≤8KiB/单JVM256MiB/5秒、原worker finally归还join/原进程自然返回/全原两流保留等将按真实回执审；本tester A无任何构建/JVM调用，不复用coder权限自行运行。UNKNOWN保管原句柄无kill/interrupt/二close/重试，旧UNKNOWN不得动。

许可审计只确认原按文件FreeBSD/JAAD Public Domain与FreeBSD变更/Guava Apache2/项目通知准确保留及新修改标识，不把SBOM当发行、专利、FFmpeg或产品分发清权。新fork身份必须与原工具区分，不能因同package名无条件进产品。

本A新缺陷结论 **NOT_EVALUATED_FORK_NOT_READ**；现有原始信息丢失为已知能力缺口，不声称新fork已经补齐或仍失败。32判据准备完成，后续B/有限metadata能力、checker新classpath集成与实际固定文件资格须依次准确另派；任何元数据自测都不代真实轨道/sample/CSD/PTS-DTS/1.2s/Media3/隔离/READY COMMIT/播放资格。完整A封存发送负责人后停止，D1未过M0未启。
'''
assert not report.exists();report.write_text(text,encoding='utf8')
files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='phase-a-evidence-manifest.json']
save(E/'phase-a-evidence-manifest.json',dict(frozenUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=report.relative_to(R).as_posix(),reportBytes=report.stat().st_size,reportSha256=sha(report),overall='PHASE_A_OBSERVATION_PATCH_ORACLES_PREPARED',evidenceFiles=files,preparedOracles=32,allOracleStatuses='PREPARED_NOT_RUN',floatingForkRead=False,compilerJarJvmCalls=0,actualMediaReads=0,oldSessionsTouched=False))
print(json.dumps(dict(report=str(report),reportBytes=report.stat().st_size,reportSha256=sha(report),evidenceFiles=len(files),manifestSha256=sha(E/'phase-a-evidence-manifest.json')),ensure_ascii=False))
