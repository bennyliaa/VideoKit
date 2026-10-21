# D1 架构准入评审 V1.0

日期：2026-10-05；作者：VideoKit coder。状态：供负责人审定，D1 BLOCKED / NOT_READY，不进入 M0。本轮只读既有需求、冻结源码与 tester 报告，新增本文；未操作设备、ADB、Gradle，未改 C01–C06 冻结件。本文不是候选补丁，不归入 C06 原冻结清单，也不改变其身份。

## 1. 可审定结论与依据

建议停止对同一 ordinary trace 缺失条件继续修复/编译/重跑。保留 C06 唯一方法 FAIL；把下一批资源用于产品隔离路线和手机差异，而非以增加日志寻求 UNKNOWN 变 PASS。负责人尚未批准负探针退出变更，本文不实施变更。

两项条件必须分别裁定：一是是否保留“App 自主取得准确 native cause”作为 D1 额外退出条件；二是能否证明符合单 App、独立 Kit 的真实高风险流水线隔离。调整第一项，即使以后正式批准，也不能关闭第二项或任何原始 P0。当前没有同时满足格式、性能、完整处理、分发和隔离约束的已验证产品方案。

主要本机依据：

- [原始用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)，下文以“原文 §”引用具体节。31 节仍有效。
- [最新执行基线](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md) §1–3、5：Flutter App、原生 Kit、Android 先行、全部 P0 保留，D1 后才冻结 M0；Apple/Windows 当前只分析。
- [D1 开发要求](../milestones/D1_CODER_REQUIREMENTS_V1.0.md)“目标与完整开发范围”1–7及“退出与交付条件”；[C03 要求](../milestones/D1_C03_CODER_REQUIREMENTS_V1.0.md)“完整任务批次”1、5、6明确 D1 证明关键可行性，不提前做完后续产品阶段。
- [C04 要求](../milestones/D1_C04_CODER_REQUIREMENTS_V1.0.md)末段单 App/独立 Kit 约束；[C05 要求](../milestones/D1_C05_CODER_REQUIREMENTS_V1.0.md)2；[C06 要求](../milestones/D1_C06_CODER_REQUIREMENTS_V1.0.md)1–2。负探针严格结果保持有效。
- [C06 集中报告](../tester/D1_C06_TEST_REPORT_V1.0.md)、[手机 C02 报告](../tester/D1_PHONE_TEST_REPORT_V1.0.md) §4–6，均按各自候选和设备解释。

## 2. 原始 P0 与追加探针逐项映射

| 要求 | 原文具体节与含义 | C06 证据及不足 | 准入判定 |
| --- | --- | --- | --- |
| 故障不拖垮宿主 | §2.2 故障隔离；§10.7 跟踪失败不影响普通播放/手动编辑；§16.2 单槽与共享资源隔离；§26.7、§27 宿主启动/浏览与崩溃阻断 | companion 实际编码 sample 后 SIGSEGV、第二任务存活通过；ordinary broker SIGSEGV/HANG独立通过。是限定实验路径，非完整播放器/图片/跟踪/遮罩产品管线 | 真正 P0，未完成；不得以 try/catch、编译或负探针失败代替产品证明 |
| 稳定错误而非裸异常 | §5.1–5.2 实际能力探测、不支持编码稳定反馈；§19.3 稳定 code/阶段/建议/脱敏诊断，含 INTERNAL_ERROR_REDACTED | ordinary 已识别匹配 native death 和阶段，但原因 UNKNOWN；不能称权限拒绝 | 原文要求稳定安全错误，未要求精确所有 native 根因；实际产品错误协议仍须实现和验证 |
| App 自动读到 native 死因 | 原文没有此明确条款；不能从 §19.3 推导为每次都须读取 tombstone | C05 要求2禁止无原因死亡当权限拒绝；C06 要求1要求证据分类/UNKNOWN及退出评审。C06严格方法 ORDINARY_CODEC_OUTCOME_UNPROVEN FAIL | D1 追加门禁仍有效，未获准退出；其 FAIL 不等价于资源释放 FAIL，也不单独证明产品隔离已成功或失败 |
| 输入、取消和真实释放 | §11.3 有界停止；§13.1 幂等句柄；§14.2、14.4 实际输入释放后才能动源；§17.4 报告全部输入/输出资源；§21 资源上限 | C06 ordinary death/source_released/lease_clear全 true、无 token；sample后取消/死亡、租约dup-close及跨owner恢复通过 | 限定路径已有证据；SourceReleased不代表Surface/GPU/输出全部释放，非协作provider/NAS及完整资源账本仍缺 |
| 新输出和宿主事务 | §11.1–11.3、§12、§17.2–17.3 输出只入临时Sink、READY不等于提交、失败不成功；§26.5、§27 源不变/部分输出阻断 | 正式H264/AAC双轨、严格PTS/full decode、T01/T02与READY恢复重新通过 | 保留现有门禁；仅短片预设，不外推无音频输入/异参数拼接/所有输出能力/系统失电 |
| ABI、宿主边界与独立分发 | §1、§3.2、§13.1、§22、§24–25、§26.7、§27 独立AAR/API、无宿主业务/凭据、仅授权输入Sink、可移除回退 | companion为另一个APK/UID，仅获D1实验授权；单App不另装约束由C04明确，尚无产品准入 | Kit/分发是原文要求；“不得另装companion”是当前明确实施约束，不能用实验APK擅自替换 |
| 资源与多实例 | §8.2–8.4、§16、§21、§26.4、§27 预算、唯一声音、有界降级、单槽隔离 | 两个worker槽特定native crash通过；无真实native OOM、1/4/9/12混排、热/Surface全面证据 | P0未完成；12为硬上限和降级测试，不是任意设备12路硬解承诺 |
| 真实人脸/物体跟踪及保护 | §4、§10.4–10.7、§26.6、§27、§31.7 完整跟踪/纠正/漏码阻断/预览导出一致 | AVI回退取得非空帧，FaceDetector候选0；actual source PTS UNKNOWN，质量NOT_RUN | 不构成跟踪/保护验收；手动回退不能取代自动跟踪P0 |
| 隐私、许可和供应链 | §22–23、§25、§27 无上传/永久人脸资料、权重独立权利、SBOM/NOTICE/漏洞 | C06无新增依赖或权重，包静态审计通过；工具既有漏洞受限使用，不是已修补；动态离线与真实模型权利未闭合 | 硬性门禁继续有效；原生、进程、FFI包装不消除许可义务 |
| 播放/字幕/图片/UI与适配 | §4–9、§15、§18、§20、§26.1–26.3、26.8 | 平板MP4/AVI/SRT/MKV/ASS结构/Seek通过；本轮静音，不证明声音/字幕效果；手机旧缺陷与产品Flutter/UI均未验收 | 不能将后续完整产品功能全部塞入D1；影响后端可行性的手机差异仍须处理 |

“权限隔离”不是原文逐字要求 Android isolatedProcess 或某种 UID 实现；原文明确的是宿主边界、授权访问及故障安全。C04进一步要求同UID多进程不得宣称权限隔离。当前实施约束仍需遵守，不能因为原文未指定机制就将同UID方案标为满足已有准入要求。

## 3. C06 事实与未证部分

C06仅平板TB138FC/API31/arm64-v8a：26入口25 PASS/1 FAIL。AVI直接10秒 scaled/unscaled仍为空；视频专用回退取原9–12秒、片段内1秒非空，90有效样本/full decode/fsync/输出FD和源释放通过，默认10秒无样本 watchdog 未延长。正式双轨预设与全部既有输出恢复断言重新通过。可关闭的是该候选、该平板、该素材的回退可行性失败；不能外推所有AVI、手机、精确源PTS或检测质量。

新增 TABLET-C06-02：MP4/AVI采帧没有EXTRACTOR_SNIFF_BEGIN/END，实际sniff门禁未证明。冻结源码 MediaEngine typed factory只提供一个Extractor，TracingExtractors有sniff日志实现，但当前证据未确认缺失原因。原方法PASS保持，需求覆盖未闭合；不能沿用开发文档“仍实际sniff”的设计意图当运行事实。若路线继续采用，应在后续完整候选中明确执行并断言实际源格式验证，覆盖“AVI路由给MP4/损坏源”等反例；可信fixture hash只能证明当前源身份。

TABLET-C06-01：本次task3fc4f602-80ef-4c85-a27c-c13741363103、PID8974、isolated UID99020，CREATE_BEGIN后 reason5/signal6、trace_status=APP_TRACE_ABSENT、cause UNKNOWN、permission_denial_proven=false；外部匹配codec2枚举native abort单独成立。finally death/source/lease均true且无token。C05旧PID5588不作本轮死因证据。不得把外部cause注入App，也不得把已有释放重写为未知。

现有公开AOSP机制解释来自冻结的 [primary-source-review.json](d1c06/evidence/primary-source-review.json)，vendor_match=NOT_PROVEN；本轮不联网或核查固件策略。只能认定该平板/C06普通公开API路径当前没有App trace证据，不能证明所有Android设备永远不可能取得，也不能承诺改几行即可强制系统提供。此处的不可满足项是“用当前证据通过当前严格App自动原因分类”，而非抽象宣称整个Android API不可能。

## 4. 不另装 APK 的隔离选项与可证实路径

下表是方案评审，不是能力已实现。沿用 [系统架构 §6](../SYSTEM_ARCHITECTURE_V1.0.md)、[C04隔离研究](D1_C04_ISOLATION_AND_AC3_OPTIONS_V1.0.md)及当前源码/Manifest；没有新增组件、许可准入或平台权限结论。

| 选项 | 单App/独立Kit适配 | 能力与风险边界 | 必须取得的证明 / 当前结论 |
| --- | --- | --- | --- |
| 同APK普通UID独立进程 | AAR附Service、宿主Manifest合并；无需另装APK | 有进程崩溃边界候选，但与宿主同UID，不隔离私有数据/权限；同UID多任务及系统OOM行为不能凭第二槽SIGSEGV外推 | 真实媒体/Surface/编码崩溃、宿主及另一槽存活、OOM/取消/预算和宿主数据边界必须验证。当前不能满足C04权限隔离要求；若负责人要采纳需明确约束变更，本文不推荐直接准入 |
| 同APKordinary isolated，CPU高风险处理 | AAR可携带Service和经审查CPU组件；宿主合并Manifest，Kit不依赖额外安装 | 当前可优先研究的产品候选：不可信容器/压缩流/图片/跟踪/遮罩留在isolated，宿主只接受验证的有界数据。CPU decoder/格式覆盖/模型权利/性能未解决；不能假定获得codec/GPU权限 | 先证明合法最小CPU解封装/解码和真实PTS，再证明帧/PCM格式、长度、步幅、溢出、预算、取消/崩溃/第二槽、显示/音频/编码接续。若宿主普通UID使用OS编码/显示，必须验证其输入为受控裸数据且风险可接受。当前BLOCKED，未实现完整方案 |
| 同APKordinary isolated直接MediaCodec/GPU | 打包形态可符合单APK，但API可用性未成立 | 本平板真实codec创建native abort，原因不是已证权限拒绝；不得将isolated_compute/平台特权当普通第三方Kit可用能力 | 只有具体目标设备真实编码/解码/显示及生命周期成功才能准入。当前不可用路径，不重复同条件探针，不能承诺跨设备通用 |
| 系统媒体服务承担高风险，App薄适配 | 可保持单App/AAR；既有Media3为薄适配方向 | 系统服务存在不等于整个App内Extractor、图片库、跟踪和验证器都隔离。必须逐环节分清App/系统进程，不以“系统API”自动证明 | 画出真实调用/权限/数据面；检查App内native及解析残留，做真实故障/恶意输入/死锁/资源证据。当前只可作组合路线研究，不能替代未隔离环节 |
| 不同UID实验companion | 需另一APK，当前不符合产品分发约束 | C06真实编码、故障、恢复、第二任务存活提供协议实验价值；两个槽仍同companion UID。signature permission不等于彻底防RCE/全局OOM | 可复用broker、task/epoch/FD租约与恢复语义的证据；不能宣布单App或Kit产品隔离通过，也不能继续扩展为默认产品 |

优先提交负责人选择的是“同APKordinary isolated的CPU处理 + 经验证的系统编码/显示边界”最小可行性研究。先确认格式/CPU组件权利与合理资源预算，若无合法组件或性能无法满足，立即形成不可行结论和替代准入决策，不进入无目标实现循环。不是从零承诺实现所有解码器，也不是授权引入FFmpeg/LGPL或购买商业授权。

必须覆盖整个危险链：探测/解封装/字幕/解码/图片、检测/跟踪/遮罩、编码和输出验证。当前host Debug AVI采帧、平台FaceDetector和AndroidOutputValidator的MediaExtractor/MediaCodec调用仍在相关宿主路径；即使编码worker隔离，也不能把输出视为无条件可信后在宿主无限制解析。独立输出验证必须保留，但其风险边界需单独设计，例如受控验证worker与数据汇总；不能删除验证来解决隔离。

跨进程数据面仅task/owner/epoch及显式授权读/写句柄，不传凭据或完整路径。帧/PCM采用有界复制或可证明不可变协议，校验布局、大小、步幅、时间戳、采样率/通道、旋转、生命周期，处理共享内存TOCTOU。输出writer实际close/death、租约和READY门禁仍成立；flock不是撤销恶意FD的内核能力。SDK要验证Manifest合并、服务命名冲突、多宿主签名/UID授权、可移除AAR、R8与升级兼容，不能硬编码实验host包名作为最终通用契约。

原生OOM与系统整体内存压力单独验证；压力分配模式、普通SIGSEGV和二槽存活不是系统OOM隔离证明。任何路线均不能承诺抵抗系统终止整个App或失电的绝对存活；应按原文验证可控单任务风险、恢复和降级，边界不满足则BLOCKED并由负责人处置。

## 5. D1真正剩余准入项、责任与退出证据

| 准入项 | 当前状态与责任 | 有限退出条件 |
| --- | --- | --- |
| ordinary追加原因分类 | FAIL；负责人裁定，coder只提供证据 | 保持现行FAIL。负责人若决定改为“平台能力观察+实际释放独立门禁”，需另立书面变更与后续用例版本，保留UNKNOWN/外部事实/历史失败；目前未批准，不再同条件重跑 |
| 产品隔离与分发路线 | BLOCKED；负责人选路线，coder实现后整包tester验证 | 明确不另装APK、完整危险链、Kit集成和资源边界；最少真实处理/输出、故障后宿主/另一槽及释放可行性证据。不仅方案文本或companion通过 |
| 手机后端/音频/字幕差异 | NOT_RUN新候选；负责人安排tester设备 | 按第6节完整批次复验，关闭旧挂起与worker启动失败；无声必须实际音频链原因/支持反馈与兼容决定，不能以平板PASS代替 |
| 实际输入/Sink边界 | 部分可行性PASS；coder/tester | 非协作read/close保留实际账本；真实provider断线/能力不足/权限或空间错误的有界失败与不READY、源不变。NAS认证归宿主，可用符合契约的provider实验，不能冒称真实NAS上线 |
| typed采帧实际格式验证 | TABLET-C06-02未闭合；后续候选coder/tester | 若继续此路线，真实验证调用/拒绝错格式与损坏输入并有断言；保留原AVI10秒与MP4控制、输出验证/释放及精确PTS未知事实 |
| 跟踪路线权利和技术可行性 | BLOCKED；负责人组织权利/样本，coder/tester | 权重或无权重路线有合法依据、最低设备路径、真实标注可行性和纠正/丢失/多目标差距，提出可评审质量/性能阈值；不要求D1先完成正式M5全量产品 |
| 供应链与限制工具决定 | 限制使用证据存在；最终发布未准入，负责人/coder | 精确版本/锁/校验、组件和模型权利、NOTICE/SBOM范围，以及已知漏洞可达性/限制或兼容升级决定被审定；不能把受限使用写成漏洞消除 |
| M0基础设计待定 | 尚未冻结；负责人组织评审 | 原文§29的API/artifact、后端/模型、输出/质量、Sink、Schema、UI、资源算法各有决定/风险/测试安排；D1输入/Sink/API关键不可行问题处置后才派M0 |

完整1/4/9/12混排、多图片格式、Flutter产品UI、全部编辑工程/拼接/遮罩、正式跟踪全量质量、三档Android系统矩阵、最终R8/AAR/Browser真实集成与商店发行属于后续阶段交付；保留P0和发布阻断，不将未完成冒充PASS，也不把全部后续功能作为重复D1负探针的理由。关键隔离/许可/后端不可行不能仅排到后续而宣称D1已过。

## 6. 手机集中补测范围（本轮不执行）

手机现有证据仍是C02/PDYM20/API31：AVI/SRT挂起、worker NORMAL失败、MKV无声而MP4有声、旧复制工具截断。平板C06不能关闭这些同机差异。负责人选择冻结候选并授权设备后，tester独占手机；先审旧包/签名/hash/数据/空间并保留账本、副本和输出，不能自动安装覆盖或清理。

建议一个完整手机批次：

1. Windows流式二进制传输工具真实路径：小文件控制字节、AVI/SRT及超过2GiB MKV，长度/hash一致再测媒体。平板私有cp复用不算Windows工具通过。
2. MP4正常前置、同AVI无侧车/有SRT对照、分层prepare/Extractor/字幕/取消日志与有界终态；真实字幕字形/同步/开关无残留。MKV/ASS样式/同步也独立人工验证。
3. 同手机非静音MP4与已知有声MKV区间，实际轨道支持/选择、renderer/session/focus/音频sink证据与人工听音。若AC3受限须稳定能力反馈并审定兼容路线，不静默丢音轨或以READY标有声；[C04方案](D1_C04_ISOLATION_AND_AC3_OPTIONS_V1.0.md)仅条件评估未准入。
4. 宿主正常H264/AAC与companion真实编码前置后，完整T01/T02、READY丢响应、真实sample取消/死亡、第二槽、跨owner/租约；普通broker NORMAL/PRESSURE/EXIT、独立SIGSEGV/HANG与当前ordinary严格分类。若选择C06实验包，仅验证实验路径，不能据此宣布产品方案通过；ordinary不作为重跑追求成功项，按批次要求记录一次即可。
5. 若采用C06采帧路径，同pipeline MP4控制前置再原AVI10秒/9–12秒映射，full video验证、取帧及实际释放；新手机cache额度事前审查，不能复制平板已满预算状态。实际source PTS/质量仍单独记录。
6. 受影响生命周期/旋转/前后台/取消资源冒烟和短时内存/热观测；将正式大字体/中英/RTL/完整多槽性能与产品UI安排在对应阶段，不将技术测试页当Flutter产品验收。

遇前置失败只阻断依赖项，保留独立测试；集中报告真实PASS/FAIL/NOT_RUN/BLOCKED，避免串行首FAIL遮蔽全部故障。不复用C02/App旧PID或平板日志作为新候选手机证据。若所选路线需要源代码变化，负责人另派完整候选，而不是修改C06冻结件。

## 7. 模型权利、质量与阶段边界

依据原文§10.5–10.7、§22–23、§26.6、§27以及 [跟踪设计 §2–6](../TRACKING_TECHNICAL_SPIKE_V1.0.md)、[C03样本协议](D1_C03_TRACKING_SAMPLES_AND_LABELS_V1.0.md)：FaceDetector只是可行性对照；候选0不证明无漏检。自有模板没有外部权重也不天然满足尺度/旋转/多人关联/遮挡重入。YuNet/ViTTrack目录许可不证明权重、训练来源、商用/再分发链完整；ML Kit路线仍需具体条款、离线/遥测与SDK分发审查。当前没有新权重准入。

负责人需组织10个权利明确的15–30秒clip（F01–F05、O01–O04、N01），各关键事件至少100个实际PTS帧、合计至少1000帧，独立标注与复核、冻结hash/标签版本。该数量是既有D1最少可行性方案，不是原文最终阈值，样本尚未取得且不替代正式输出逐帧覆盖。真实视频授权范围与人物/测试/标注使用依据分别留证，不能将现有可播放媒体直接视为完整质量集。

报告按场景分层precision/recall、ID switch、LOST/歧义、真实目标未覆盖、纠正及重入、FPS/首结果/峰值内存/热/电量。VFR依实际帧PTS，不按固定FPS推算。M5/M6要求预览与导出坐标/PTS一致及漏码阻断；低分辨率有损采帧仅供分析，不能据插值或矩形存在宣称保护完整。手动关键帧回退保留但不删自动跟踪P0。

## 8. 负责人可作出的具体决定

建议现阶段记录：C06限定平板25项通过作为局部证据接受；TABLET-C06-01继续FAIL，TABLET-C06-02覆盖缺口保留；D1仍BLOCKED。停止同条件可观测性修复，选择产品隔离最小可行性路线与手机整批计划，组织模型权利/标注资源。这些决定不批准额外APK产品化、不引入新依赖、不降低最终P0。

如负责人坚持App精确native原因为不可放宽条件，应明确当前平台证据无法通过该项，等待可证明的不同平台/接口条件，而非继续无改变重跑。如负责人要调整该追加门禁，须单独批准并保留历史FAIL；本文件和此前退出建议均不构成批准。无论哪种决定，未证实的产品隔离、模型权利或后端关键可行性仍必须处置，不能直接进入M0。

本文不改原需求、测试结果或冻结hash。C06冻结清单SHA-256仍为 `1fc7ef1b294c8e2dd11d3b547385bcec2875540bbc1428f939bfdbd198ae6f0d`，源码ZIP仍为 `fc0e041aa3048f9fbce301aa3d3b80b95bda8343e5dee4dc696ab159aaf77634`；新评审文档身份独立，可由负责人引用审定结论后另派下一阶段工作。
