# D1 C06 集中修复技术需求

日期：2026-10-05；依据 docs/tester/D1_C05_TEST_REPORT_V1.0.md。C05平板已结束，25方法23 PASS/2 FAIL。一次完成本轮分析、修复、自检、冻结与设备追加计划，不逐项交接。仅本机，不操作ADB/设备，不改C01-C05冻结件或媒体，不进入M0。

1. TABLET-C05-01：ordinary codec在CREATE_BEGIN后native SIGABRT，App内退出trace缺失而cause UNKNOWN；tester匹配PID5588/UID99012的tombstone记录 Hardware service manager is not running，栈为codec2服务枚举。分析App内证据获取限制与原始崩溃原因，不凭SIGABRT或此文字推断权限拒绝。若平台不向App提供原因证据，准确返回UNKNOWN；测试可分别记App内分类失败与外部匹配死因证据，不强造App通过或扩大宽松allowlist。给负责人提交此负探针的退出准则评审建议，保持产品隔离P0不变。已证最终death/source_released/lease_clear须保留复验。
2. TABLET-C05-02：AVI原10秒直接取帧空，9–12秒Media3回退转码因10秒无输出sample watchdog失败。查加载、seek/clip、视频音轨解码与muxer的实际阶段及可用证据，提出可复现修复与MP4控制。不能只延长watchdog掩盖无进展，不能改用0秒/空帧/仅MP4；若采帧路径本来不需音频，明确视频采帧与双轨编辑导出是不同输出契约，由独立验证器验视频结果，不能弱化正式双轨导出门禁。新增依赖先闭源许可证准入，不引入未经审查GPL/权重。帧PTS未知、转换有损与检测质量NOT_RUN如实保留。不能解决则明确BLOCKED及方案决策点。

保留SIGSEGV/HANG、正常导出、T01/T02、实际sample取消/死亡、第二槽与跨owner恢复门禁。手机回归、单App独立Kit产品隔离、模型权利等未决不借本轮关闭。

交付 docs/coder/D1_DELIVERY_D1-20261005-C06.md，含两项根因事实/假设/状态、源码/产物hash、集中自检与完整追加测试说明。新增诊断不等于缺陷已关闭。整包交负责人后才派tester。
