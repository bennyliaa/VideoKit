# 测试与验收计划

## 2026-10-21 国际化详细设计补充（当前有效）

依据[《VideoKit 国际化详细设计》](INTERNATIONALIZATION_DETAILED_DESIGN_V1.0.md)及[国际化数据模型](INTERNATIONALIZATION_DATA_MODEL_V1.0.md)，首轮界面支持en/zh-Hans，SYSTEM/EXPLICIT切换与确定性script回退，资源离线完整；界面、字幕、识别、翻译四类语言分别设置，不隐式互改。UI localeGeneration不改变媒体generation/epoch，不重建播放或取消模型任务。

新增I18N-01–15验收：解析真值、切换/系统/手选、存储失败与迁移、四域隔离与媒体不中断、完整资源/ICU/参数、错误映射、格式、RTL/长文/100-130-200%字体/读屏、离线/原生宿主/发布测试locale隔离。按静态/Fake/真实UI/真实媒体/扩展及NOT_RUN分层，禁止编译/Fake代真实验收。

仅文档更新，主阶段/原P0/冻结证据保持，项目PAUSED_WAITING_USER，D1未过/M0未启。

## 2026-10-21 最新播放子系统设计基线

新增播放验收索引采用[《VideoKit 播放子系统详细设计》](PLAYBACK_SUBSYSTEM_DETAILED_DESIGN_V1.0.md)第13节PB-01–08、ASR-01–02、TR-01–02；数据边界见[播放模型](PLAYBACK_DATA_MODEL_V1.0.md)。设计覆盖不等已有实测，旧D1局部PASS/FAIL/UNKNOWN原样保留。ASR/翻译为单列扩展，派发前冻结目标语言/模型/设备和质量/时延/内存阈值；静态与回执不能代图像声音/原资源归还。子任务验收集中整包测试，不逐功能反复交测。

本节为当前设计；被撤销指令已从执行正文移出，修改前原文见history/design/2026-10-21-consolidation/。历史证据保持，项目继续暂停。

## 最新有效决定：Flutter 自有 Theme，SkinKit 延后（2026-10-20）

先使用 Flutter 开发自有 VideoKit Theme 和完整 App UI，按既有 PPT 样式实现；等 SkinKit 正式支持 Flutter 后再评估并安排集成。当前不做 SkinKit Android 原生桥接，也不以其真实接入作为 M0/M8 的既定退出门。旧SkinKit实接与禁止自有Theme要求已归档，不作为当前任务；未来仅在正式Flutter支持和新批准范围下评估。完整现行范围见 [Flutter Theme 与延后集成决定](FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md)。完整 UI 优先、演示数据隔离、后续功能接回以及每批 1–3 个里程碑的集中开发测试规则不变；D1未通过、M0未启动；当前项目暂停。


## M0 起交付批次规则（2026-10-20）

负责人每批选择 1–3 个完整里程碑并向用户汇报范围与理由；coder 整批开发、自测、冻结后统一交 tester，tester 整批测试并集中报告，缺陷集中回交修复及回归。阶段需求与验收分栏保留，禁止逐问题反复交接，不以合批冒充阶段通过。详见 [协调规则](MILESTONE_COORDINATION_V1.0.md)。此规则覆盖下文单里程碑立即交测的冲突表述，当前 D1 及 M0 未启动状态不变。


## 1. 验收原则

原文第 26 节完整测试矩阵及第 27 节全部阻断条件有效。Fake PASS 不代替真实后端 PASS；编译通过不代替播放、跟踪质量或输出正确。每条子需求映射 requirementId → caseId → 平台/设备/样本 → 结果证据。结果仅 PASS/FAIL/NOT_RUN/BLOCKED，不以缺设备当作通过。

## 2. 契约与故障注入

API 版本、主版本拒绝、旧 schema、新可选字段、命令重复/过期 generation、Seek 合并、幂等 release、回调超时、取消、SourceReleased 顺序与多消费者租约归零。ReadHandle 覆盖短读/EOF/长度未知/2GiB+ offset/溢出/并发/取消；OutputSink 覆盖顺序写、随机写、空间未知、磁盘不足、写失败、flush/close 失败及 markReady 结果未知。

Fake 与每个平台真实实现共用语义用例。高频事件采样不得吞掉终态；状态保存失败不能阻止资源释放。宿主 adapter 往返映射逐字段比较。

## 3. 播放、图片和多实例

保留原文全部视频/图片后缀矩阵，并附具体容器编码、轨道、方向、样本 hash 和样本授权。测试 Seek 0/25/50/90/末尾及快速 Seek、结束重播、倍速、轨道、缩放、旋转、全屏、字体和后台/锁定。

覆盖静态/动态 WebP、GIF、HEIC/HEIF/AVIF、大图/长图/透明/EXIF/坏图；图片不得显示无意义视频控件。大图测试峰值内存和帧缓存，不能仅看是否打开。

1/4/9/12 槽视频/静态/动态图混排，唯一音频、零音频、声音槽移除、离屏恢复、单槽资源不足和错误，反复切换/旋转/释放后句柄/Surface/解码器归零。12 是硬上限和降级测试，不保证设备实际支持 12 路活跃解码。

## 4. 编辑、安全输出与跟踪

片段增删重排/边界、相同与不同参数拼接、VFR/无音频/不同音频/横竖屏、非关键帧裁切、轨迹重排、遮罩坐标黄金图、预览/导出效果与 PTS 对齐。

取消、源断线、编码失败、满盘、权限变更、markReady/取消竞态、进程终止。每次失败验证源 hash/路径不变、未 ready、abort 幂等、资源归零；成功输出重新解封装/解码并验证时长、方向、音画同步及覆盖。

跟踪使用人工标注集量化检测、ID switch、丢失/歧义、漏码、纠正、重入、内存/热/电量；临界区间必须可见。遮罩存在并不等于目标覆盖，不能仅比较程序轨迹。无网络上传和永久人脸资料需通过网络阻断及文件观察验收。

## 5. 宿主集成与故障隔离

执行原文第 26.7 节，重点多消费者 SourceReleased、scope 隔离、HostAction、不暴露地址凭据、Sink 与业务提交分离、可移除 AAR 和启动回退。

对 worker 异常退出、原生崩溃、OOM、死锁和取消失效单独注入；普通异常测试不能代替原生崩溃测试。Android/Windows 验证任务进程边界，Apple 验证系统服务与嵌入依赖。平台无法满足隔离条件需列 BLOCKED 并重做方案，不自动放宽 P0。

## 6. 设备及平台

Android 保留 API31、中间主流版本、测试时当前稳定版本、ARM64 实体手机和 10 英寸级平板；记录 SoC、RAM、系统和温度。模拟器只辅助契约，不能代替硬解/热/电量真机。

iOS/iPadOS 评估最低系统版本与实体手机/平板；macOS 覆盖 Apple Silicon，是否 Intel 支持待冻结；Windows 覆盖 x64 及真实 GPU，ARM64 是否首期正式支持待冻结。四平台商店是既定目标，具体 OS/架构矩阵待用户评审。

跨平台测试同一媒体语料、工程与快照；比较时间/坐标与状态语义，不要求不同 GPU 输出位级完全相等。字体 100/130/200%、中英、伪本地化、RTL、触摸/鼠标/键盘和窗口变化必须覆盖。

## 7. 指标冻结与证据

启动、Seek 延迟、取消时限、音画偏差、跟踪质量、峰值内存、热和输出速度目前无实测阈值。Spike 产出数据分布与建议，评审冻结每类设备可接受值；未冻结不得标正式验收通过。安全约束立即生效：源不改变、凭据不穿透、未完成不 ready、无静默漏码成功声明。

报告包含 SDK/依赖/模型版本和 hash、设备、输入 hash、执行条件、测量方法、阈值、实际值、失败复现、NOT_RUN/BLOCKED。正式交付附 Debug/Release hash、R8/ProGuard、SBOM/NOTICE/漏洞、独立构建/接入文档及回退证据。

## 集中整理后的执行依据（2026-10-21）

[REQUIREMENT_ACCEPTANCE_TRACEABILITY](REQUIREMENT_ACCEPTANCE_TRACEABILITY_V1.0.md)；[METRIC_FREEZE_REGISTER](METRIC_FREEZE_REGISTER_V1.0.md)。

以上补充现有职责、接口和验收追踪，不新增主阶段或删除原P0。历史设计原文已归档，不再作为并行指令；当前项目暂停，不能以本文触发开发测试。

## Git提交交付补充（2026-10-21）

用户要求tester在后续开发测试过程中按需提交代码。仅在用户恢复并获得准确整批范围后，tester按[GitHub同步与提交规则](GITHUB_SYNC_AND_TESTER_COMMIT_POLICY_V1.0.md)核对冻结候选/diff和产物来源，提交相应代码、文档、报告，记录commit SHA/分支/URL与实际验证/未运行项；不夹带浮动源码或以提交冒验收。默认整批分支/PR审核，不自动force push/发布。当前暂停不执行新测试或让tester补提交历史任务。
