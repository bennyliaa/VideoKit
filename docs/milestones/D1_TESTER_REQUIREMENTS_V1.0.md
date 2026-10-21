# D1 测试需求：Android 高风险技术验证

版本：V1.0；日期：2026-10-05；阶段：D1；原始需求关联：5、10、11、13、14、19、21、23、26、27、29。

基线：[用户需求](../VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md)；最新执行范围：[项目决定](../PROJECT_DECISIONS_AND_EXECUTION_V1.0.md)；统一交接：[协调规则](../MILESTONE_COORDINATION_V1.0.md)。

状态：测试准备；只有收到负责人确认的完整候选交接包才执行正式验收。M9当前不执行平台测试。可先阅读和整理用例，但不抢跑产品测试、不为准备重复构建。

## 接收条件

对应 [coder需求](D1_CODER_REQUIREMENTS_V1.0.md) 全范围完成矩阵、candidateId、产物hash、集中构建及自检证据、已知问题、样本清单和设备条件齐全。若资料或必要功能不完整，先报告拒收/阻断原因，而不是频繁测试半成品。

## 必须执行的测试

- TC-D1-01：核对样本 manifest 和真实探测结果；后缀不是能力证明，缺字幕/双音轨/动图/跟踪标注样本标 NOT_RUN。

- TC-D1-02：随机读大偏移、短读、EOF、长度未知、非法范围、断线与取消；确认无完整下载和主线程阻塞。

- TC-D1-03：播放 Seek 后正确读取；取消与 release 后无旧 generation 访问，所有输入资源归零。

- TC-D1-04：Sink 不足在导出前失败；满盘/写失败/flush失败/取消调用 abort；不完整输出不得 markReady，成功输出能验证打开。

- TC-D1-05：模型权利资料、离线网络观察、人工纠正与 LOST/AMBIGUOUS；未实测质量不宣称可靠。

- TC-D1-06：故障隔离实验、资源峰值、可取消性与阻断风险；Apple/Windows分析与未实现状态分开。

- TC-D1-07：基线项目集中构建及相关测试证据与版本一致；列出 M0 可冻结接口和禁止冻结事项。

## 执行和证据

使用测试需求→用例→实际环境/样本hash→预期→实际→证据映射。按PASS/FAIL/NOT_RUN/BLOCKED记录。缺样本/设备/模型权利/未冻结阈值不得记PASS；Fake结果不代替真实设备/引擎/效果，扩展名不代替格式探测。性能与取消阈值据正式决定执行，暂无数值则提交测量并标未冻结。

Android12手机/平板由负责人通知用户开启调试后测试；无设备阶段先做可执行契约和产物核查，真机项等待，不擅自标通过。样本只读，输出仅授权临时目标，不上传媒体，不改产品源码。

tester不重复coder已完成且candidate未变的构建；优先检查并使用其产物。需要验证独立构建/R8/发布包或证据不足时，可做必要集中构建，并避免与coder并发占用构建缓存/设备。报告全部发现后统一交回，修复候选做缺陷验证和受影响回归，只有新变更/失败/风险才扩大或重复测试。

## 报告与判定

报告保存docs/tester/D1_TEST_REPORT_<candidateId>.md，附case表、缺陷复现/严重度/预期实际/修复建议、日志或截图证据及环境。所有关键安全缺陷立即阻断，其余同批汇总；不因一次测试通过就自动派发后续开发。

退出条件：D1 完整实验包与独立测试报告齐全；输入/Sink/API 的 M0 关键设计无悬而未决阻断。没有设备或有效权利证据的测试不伪造通过；关键阻断由负责人处理后再进入 M0。

阶段全通过后负责人确认退出并派发下一阶段；未经关闭的关键NOT_RUN/BLOCKED不能用口头结论掩盖。

## 设计依据

- [SYSTEM_ARCHITECTURE](../SYSTEM_ARCHITECTURE_V1.0.md)
- [PUBLIC_API_CONTRACT](../PUBLIC_API_CONTRACT_V1.0.md)
- [EDIT_TIMELINE_AND_EXPORT_DESIGN](../EDIT_TIMELINE_AND_EXPORT_DESIGN_V1.0.md)
- [TRACKING_TECHNICAL_SPIKE](../TRACKING_TECHNICAL_SPIKE_V1.0.md)
- [OPEN_SOURCE_AND_LICENSE_PLAN](../OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md)

