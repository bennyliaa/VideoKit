# D1 C03 平板集中测试需求

日期：2026-10-05；状态：已派发，等待用户切换平板。用户明确允许切换，不表示手机缺陷已关闭。

tester 独占设备；coder 仅本机 C04 修复。先有界检查连接；只操作确认是用户本次平板的设备，不能把仍连接的手机视为平板。未连接、RSA 未授权或设备不符合 API31+/arm64 条件时记录 WAITING_FOR_TABLET，不反复轮询、不操作其他设备。不得运行 Gradle。

候选固定为 D1-20261005-C03，核对 docs/coder/D1_DELIVERY_D1-20261005-C03.md、D1_C03_DEVICE_APPENDIX_V1.0.md、冻结源码和 APK/hash。负责人批准在已确认平板安装该候选的三个同签名 debug/test/worker 包；worker 仅 D1 实验，不代表产品分发方案批准。未知既有包或数据不能覆盖，先报告；不得安装 unsigned release，不得修改冻结件。

执行 appendix 的集中批次：可信 fixture 校验后，先正常编码与输出解码，再 T01 反例、T02 精确注入与恢复；按前置条件执行普通隔离拒绝、companion 编码、实际 sample 后取消/死亡、第二槽存活、跨 owner 恢复。前置失败只阻断相关后续测试，继续独立可运行的项；所有操作限定测试 App 自身。

同时做 MP4、AVI/SRT、MKV/ASS 的播放/Seek及平板效果检查，重点复核手机四项缺陷。AVI 需有界超时与日志，不无限等；音轨自动断言与人工声音分开，截图/cue 数不代表字幕或同步通过。用户观察仅在明确准备好测试页面时提出具体动作，不自行调整全局设置。手机 C02、平板 C03 证据分开。

样本只读、不上传；fixture 仅授权 App 私有目录，二进制传输可复用本次已验证 shell-v2 工具，记录长度/hash与空间。保留手机数据，不访问或清理手机。大样本若空间不足如实 NOT_RUN。

报告 docs/tester/D1_TABLET_TEST_REPORT_V1.0.md：设备/candidate/hash、逐方法 PASS/FAIL/BLOCKED/NOT_RUN、输出门禁与注入命中、隔离/释放、人工效果、集中缺陷和证据链接。报告平板批次真实结束或阻断，不宣布 D1 通过。手机仍 WAITING_FOR_FIX_CANDIDATE，修复后须另安排手机补测。C04 待负责人整体交接，本轮不自动替换候选。
