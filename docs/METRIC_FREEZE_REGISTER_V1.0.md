# VideoKit 指标与数值冻结安排

V1.0；2026-10-21。不是测试派发，所有新增登记状态为PROPOSED_UNFROZEN；不编造数值，不用表格完成冒指标已通过。原已签D1单批预算/once/指标不重置，发布级参数不因Spike某次通过自动冻结。项目暂停。

## 1. 冻结工作流

coder按目标设备/语料提出有来源的分布及参数→tester独立核测量与边界→负责人批准具体阈值/适用范围/失败策略，原需求明确须用户评审冻结的质量/安全指标仍由用户确认，负责人不代替；其他涉及原P0或发布安全变化亦须用户确认→分别写入开发/测试工作单并绑定candidate/version。没有数值的项不能判对应正式退出PASS；仅补文档不需要为采数开启新任务。

安全规则立即有效：源不修改、凭据不透、取消不早释放、UNKNOWN不归零/退款、不完整保护不成功、未验证不READY、最多一个声音许可。已有4/9布局和12硬上限、48dp、100/130/200%字体等不因待冻结而取消，不承诺硬件能12路解码。

## 2. 冻结登记

| ID | 指标组 | 最迟冻结点（不新增主阶段） | 提案责任 | 独立验证责任 | 测量/样本要求 | 必填数值或政策 |
| --- | --- | --- | --- | --- | --- | --- |
| MET-API | 命令/回调/事件队列和终态缓存 | M0公共契约冻结前 | API/core coder | tester契约与事件GAP | 受控单调时钟/并发上下界/队列满/订阅落后 | 队列容量、条目字节、回调时限、保留窗 |
| MET-IO | readAt块/在途/累计/断连取消 | D1原范围结论及M0契约冻结前 | 输入adapter coder | tester源/lease | 同原读/回调与buffer归还、短读/2GiB+ | block/inflight/read窗口/取消期限；D1批预算不改 |
| MET-PLAY | 启动首帧/Seek/音画同步 | M1准确候选交测前 | playback coder | tester真机图像声音 | 目标机型/样本hash/分位数/冷暖启动 | 首帧/Seek分位延迟、音画偏差与统计次数 |
| MET-SUB | 字幕同步与解析限额 | M1字幕实现准入前 | subtitle coder | tester字幕矩阵 | 有标注PTS/文本样式/坏输入/大字幕 | 同步容差、cue数量、文本/附件/字体字节 |
| MET-IMG | 图片像素/tiles/动画 | M2实现与候选交测前 | image coder | tester图片矩阵 | 大图viewport/格式/合成帧/CPU-GPU峰值 | 像素/region/缓存/帧数/异常帧delay处理 |
| MET-RES | 并发/内存/队列公平/热 | M3资源策略实现前 | core资源coder | tester1-4-9-12矩阵 | 具体SoC/RAM/温度/同时图视频/拒绝与回收 | 各池容量/等待窗/热采样/降级与恢复阈值 |
| MET-AUDIO | 声音切换/焦点回调 | M3声音策略实现前 | audio coder | tester焦点先后矩阵 | 同原静音确认→新声源授权/过期epoch | 切换等待/超时策略、焦点owner与系统事件 |
| MET-EDIT | PTS/坐标/预览导出一致 | M4计划评估器冻结前 | timeline coder | tester黄金样本 | VFR/重复源/方向/输出实际帧 | 映射舍入/图像差异容差、快照上限 |
| MET-TRACK | 检测/跟踪/覆盖质量 | D1原可行性要求保持；M5质量验收前 | tracking coder | tester独立标注集 | 授权分离语料、IoU/ID-switch/漏保护/LOST | 质量阈值、纠正策略、漏码阻断规则及范围 |
| MET-EXPORT | 编码/空间/取消/验证 | M4首链与M6完整候选交测前 | export coder | tester实际Sink与输出 | 真实flush-close/READY竞态/音画/覆盖 | 编码预设/取消窗/验证读取与字节预算 |
| MET-ISO | worker/IPC/死亡归还 | D1原隔离可行性要求保持；M3/M5/M6各风险单元前 | native coder | tester故障注入 | 独立准确任务/坏消息/原生崩溃/OOM | worker数、消息长度、共享buffer、失联观察期限 |
| MET-I18N | 语言切换/偏好/资源 | M0界面候选交测前 | Flutter coder | testerI18N-01–15 | 切换前后同session/多次快速选择/落盘失败 | 偏好大小、切换预算/超时、关键资源清单；原字体/48dp保持 |
| MET-ASR | 识别质量/实时率/资源 | EXT-ASR正式开发/候选交测前 | ASR coder | tester授权音频集 | 固定权重/语言/设备，WER-CER/PTS/静音噪声 | 模型和语言范围、RTF/延迟/漂移/内存/热限额 |
| MET-TR | 翻译质量/吞吐/上下文 | EXT-TR正式开发/候选交测前 | translation coder | tester人工双语集 | 固定模型/量化/语言对、漏译增译/取消 | 上下文token/输出/延迟/缓存/人工质量标准 |
| MET-PLAT | 平台最低系统/架构 | Android原M0前置决策；M9其他平台前 | 负责人+platform coder | tester设备矩阵 | 平台实际设备/图形驱动/页大小/构建 | 首批OS/CPU/GPU/设备清单及差异覆盖 |

## 3. 每条指标正式冻结记录

MetricDecision={metricId,revision,scope,platform/deviceProfiles,sampleSetHash,toolVersion,method,unit,distribution,threshold/comparator,budgetAggregation,firstFailurePolicy,timeoutReturnPolicy,dependency/modelHash,proposalEvidence,independentEvidence,approver,approvedAt,exceptions}。阈值须明确包含等号、采样误差与统计次数；deadline用单调计时且最后受控观察界定，不以晚到成功补绿。累计预算不能每case重领。

计划/提案/批准/验证结果分列。修改参数新revision并评估受影响回归，不重写旧原始数值和FAIL；冻结逾期登记BLOCKED及所阻阶段，不默认放宽。当前不产生任何新测量证据。
