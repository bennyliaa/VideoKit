# D1 C14 编码能力协商与真实帧管线集中修复开发需求 V1.0

日期：2026-10-16；状态：正式派发，仅本机整批开发，无ADB。D1未通过，不进入M0。

## 输入事实与范围

完整读取D1_C13_TEST_REPORT_V1.0.md、C13交付/边界/剩余门禁/许可/框架映射及原始需求、既有系统/API/输出设计。C13平板52 PASS/3 FAIL/14 BLOCKED，手机69环境阻断，无在途。C13-T01两个pipeline正例在OMX.qcom.video.encoder.avc的MediaCodec.configure失败（-38/0x80001001），received/input/sample/verified均0；旧host双轨通过。C13-T02 self SIGSEGV App原始signal0且trace缺失，外部raw11；另一独立任务系统11。没有证据唯一认定颜色/profile/权限等根因，不能把旧host成功当本管线支持或将实际断言失败重分类为PASS。

本批目标是让真实帧接续获得可靠、可诊断且有限的编码能力协商，并完成未进入的实际PTS/内容/EOF及生命周期反例；不扩散为产品编码或默认CPU后端。C01–C13、素材只读，独立C14候选与完整归档。Flutter/独立Kit、Media3薄适配与所有P0保持，VideoKit不依赖Browser业务。

## 集中实现

1. 明确当前固定256×144/5fps/600kbps/无音频短片实验的格式约束和已证错误。审查现有PipelineEncoder选择第一个支持size/rate和颜色的codec、固定profile/颜色标准/maxB配置等路径，按已锁Android公开API与Media3可复用能力做最小适配；查询并保存候选codec名、硬件/软件属性、所需尺寸/帧率/码率/对齐/颜色/profile范围和isFormatSupported事实。文档能力不等实际configure成功，不凭错误数字猜唯一原因；查阅官方源码/文档需存精确引用。
2. 先形成有界确定的配置策略：能力过滤、明确的有限标准颜色/必要profile参数组合、顺序与最大尝试数（建议总计不超过4次，实际需求写清）、整体deadline和单encoder许可。允许使用设备公开提供且满足原像素/PTS/输出限制的系统编码器候选；硬件/软件结果分列，不宣称任意设备硬编保证。不得增加新的FFmpeg encoder/商业库/Surface-GPU回退、宿主源压缩解码、自制codec或改变颜色/PTS/EOF通过阈值来求通过。
3. 失败候选每次实际codec/Image/callback归还且无creating/pending之后才下一配置；close不确定、native调用仍在途、取消或整体预算到期时停止尝试并quarantine，不能以异常/超时等同释放。配置阶段不创建Source producer/输出writer或泄露槽位，能力不支持与已选configure失败分别保留。允许有限能力选择不能成为tester无限重跑或隐藏首失败；每次尝试日志与最终选中理由全部保存。
4. 分阶段诊断ENUMERATE/CAPABILITY/CREATE/CONFIGURE/START/INPUT/OUTPUT/MUX/VALIDATION/CLOSE，记录有限脱敏MediaFormat键、codec/颜色/选项、CodecException errorCode/diagnosticInfo/recoverable/transient等公开事实和首次错误；不泄露路径/凭据/媒体内容。修复PIPE_ENCODER_OR_VALIDATION_FAILED过度合并，不用通用REDACTED抹去必要诊断；cleanup独立，不将运行期致命错误自动恢复成成功或失败后虚假READY。
5. 复用C13六真实源snapshot→有界不可变RGBA→系统AVC/Media3 fMP4→隔离CPU完整EOF验证、Source/PTS/内容及两CPU槽/单encoder限制。新增测试覆盖能力否定/能力声称但configure拒绝/失败候选释放后有限下一候选/全部拒绝/取消/关闭失败不许重选/尝试上限/metadata限额，不以纯mock等同真实codec可用。真实设备正例必须六源/六输入/六样本/六验证、实际PTS对应≤1ms、原画面差异及luma门槛不改、无音频明确标记；不绕过验证或换合成帧。
6. C13十四个未进入反例全部保留并整批完成；至少覆盖实际writer/flush/截断隔离验证、READY丢响应、取消帧租约/队列、另一真实CPU继续、第二encoder拒绝。原host双轨/legacy实际共享影响回归，身份/注册/解绑/代次、源预算与受影响CPU方法按范围保留。统一最终保守8份RGBA预算1179648B+YUV55296B，修正新文档初稿5份表述，不能只改文档掩盖数组峰值；实际引用/队列/codec/FD计数及终态对应。
7. C13-T02保留FAIL、App trace缺失和ordinary UNKNOWN为OPEN。不修改signal0判定，不外部raw回填、不引crash handler、不声称系统必给signal。当前未改变退出采集路径则不为新包身份重复同条件SIGSEGV两项；计划明确NOT_RUN_UNCHANGED_PLATFORM_LIMIT并引用C13原失败/独立释放事实，不算C14 PASS或关闭门禁。若有具体真实采集代码缺陷需另提供证据、设计及必要一次验证，由负责人审阅后正式交接，不悄然增加崩溃campaign。
8. 新剩余门禁矩阵保留原文§29十二项与M0–M8划分，内部Maven命名以PROJECT_DECISIONS既定决定为准，不再说全部未定。跟踪权利与真实标签缺口不伪造；不新增下载权重/媒体/依赖。FFmpeg8.0.3 Debug-only、Media3 1.9.3锁/许可/NOTICE/SBOM/完整源对象映射不扩，release无实验与原hash独立核验；Apple/Windows只设计不实现。

## 冻结交付

多小功能集中完成再必要编译、自检、审计，保留首次失败，不无理由clean、不逐项交测。交docs/coder/D1_DELIVERY_D1-20261016-C14.md、D1_C14_ENCODER_NEGOTIATION_DESIGN_V1.0.md、集中缺陷矩阵/框架与许可/设备附录、具体方法依赖计划（实际计数，保留未运行历史signal门禁）及可独立校验实际ZIP/源/证据/产物的工具和身份回执。全部本机设备NOT_RUN，coder不ADB、不自行交tester。最终交付说明完整与未完成范围，负责人通过任务完成事件收取；不重复跨窗口发送尝试。D1未通过、不进入M0。
