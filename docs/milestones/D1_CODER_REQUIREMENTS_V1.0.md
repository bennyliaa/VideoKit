# D1 技术开发需求：Android 高风险技术验证

版本：V1.0；日期：2026-10-05；阶段：D1；原始需求关联：5、10、11、13、14、19、21、23、26、27、29。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：当前派发准备。下游文档由前阶段证据补充精确版本/阈值，任何P0变化必须记录，不能自行减项。

## 目标与完整开发范围

1. 读取现有工程、依赖版本和测试媒体 manifest；核实可构建环境，生成样本清单（相对路径、长度、hash、真实容器/编码、轨道、动画类型、来源说明），源目录只读。

2. 锁定首轮 Media3/图像/跟踪候选精确版本并记录许可、传递依赖和模型权利；未获批的 FFmpeg/GPL/许可不明模型不集成。不能仅凭仓库许可证认定权重可商用。

3. 在局部 Spike 中贯通宿主 readAt→探测/Media3 DataSource→播放 Seek；验证短读、未知长度、2GiB+ offset、断线、取消与释放；同步媒体调用在工作线程，不等待 UI 线程。

4. 验证 Media3 编辑输入与宿主临时 OutputSink：顺序/随机写要求、flush/close、abort、markReady 及输出重新打开验证。API 仅收路径时提出受控方案，不绕过 Sink。

5. 评估 OpenCV/YuNet/ViTTrack（或合法替代）离线推理、跟踪纠正与丢失标记；质量不足如实列出，不能把模型执行完成作为跟踪成功。

6. 验证资源预算和原生崩溃隔离方案；普通异常隔离不等于 SIGSEGV/OOM 隔离。列出 Android 当前方案证据及仍需修改事项。

7. Apple/Windows 只分析接口、依赖和后端兼容性，不编写其实现、不启动平台构建；缺这些设备不阻断 Android，能力不得标 PASS。提交 API/Sink/资源/质量阈值建议后停止，等待整包验收。

## 通用实施约束

Android12/API31+、手机与平板、多语言中英资源及RTL/大字体机制；App Flutter并含编辑/多画面。Kit全部P0保留，输入只读、输出仅授权临时Sink，凭据/宿主业务/路径不穿透。当前只开发Android，Apple/Windows仅设计兼容性分析。测试样本 `D:\\CodexProjects\\VideoKit\\test_media` 只读、不打包或上传。

每个里程碑的全部内容完成后再一次性交给tester，禁止按单按钮/小功能反复交接。coder阶段可自检和必要自动测试，这不算正式交接。按完整功能簇集中编译，尽量复用已有构建结果，不每改一个文件就编译；首次构建/依赖与接口变更/原生绑定、集成失败等必须及时检查，不能为了减少编译而长期累积不兼容代码。

只交付一个可辨识候选candidateId，列源码/构建配置/依赖版本、APK/AAR路径与SHA-256、构建与自检结果、范围完成矩阵、已知风险和环境缺口。无Git时用源码快照清单与hash标识，禁止声称有不存在的commit。tester验收期间冻结该候选；发现缺陷先汇总成修复批次，修复后统一新候选和针对性回归。紧急安全问题可立即阻断并修复。

coder写docs/coder/<ID>_DELIVERY_<candidateId>.md，tester报告写docs/tester/<ID>_TEST_REPORT_<candidateId>.md。源码由coder负责，tester仅写测试计划/报告/证据，未授权不得改产品源码；双方共用工作区，不并发占用Gradle或设备。需要真机调试由负责人通知用户，不绕过设备授权。

## 退出与交付条件

D1 完整实验包与独立测试报告齐全；输入/Sink/API 的 M0 关键设计无悬而未决阻断。没有设备或有效权利证据的测试不伪造通过；关键阻断由负责人处理后再进入 M0。

功能范围逐项DONE/NOT_DONE；实际自检采用PASS/FAIL/NOT_RUN/BLOCKED，不以已编译代替效果验证。没有资源的项列清阻断，不向tester交付假完成里程碑。

## 设计依据

- [SYSTEM_ARCHITECTURE](../SYSTEM_ARCHITECTURE_V1.0.md)
- [PUBLIC_API_CONTRACT](../PUBLIC_API_CONTRACT_V1.0.md)
- [EDIT_TIMELINE_AND_EXPORT_DESIGN](../EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md)
- [TRACKING_TECHNICAL_SPIKE](../TRACKING_TECHNICAL_SPIKE_V1.0.md)
- [OPEN_SOURCE_AND_LICENSE_PLAN](../OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)

