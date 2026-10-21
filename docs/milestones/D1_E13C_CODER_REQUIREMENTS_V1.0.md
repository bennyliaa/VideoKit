# D1 E13C coder 正式需求 V1.0

2026-10-18，负责人正式派发 HOST_ONLY 集中修复 E13AB-DEPLOY-F01/P1。真实失败报告 docs/tester/D1_E13A_E13B_TABLET_EXECUTION_REPORT_V1.0.md，SHA256 7c7e4174fff072ed8a45dd9260137eaf4a50dcb30a5db8d7df33702e8d0a934a。

修复 E13HostActivationSession 的 e13a-activation-deployment.once 与 E11DeploymentOnce 固定 activation-deployment.once 冲突；只采用精确角色/受审配置的固定名称显式接线，不接受任意文件名、不改历史 E11 角色、不改测试 scope 文件名绕过。CREATE_NEW、重复/部分文件拒绝、force/readback/原 close 真返才构造 SDKport/安装、UNKNOWN 原 holder 与 custodian 保留。

有限本机证据须执行实际 helper 和公开入口接线：准确 E13A config/once 到预期 SDK 前门；旧 E11 名仍支持；错 role/name 在 SDK child 前拒绝；跨 JVM 重复、部分文件、close UNKNOWN 不派发。可使用明确受控测试端口止于首 SDK 调用，不执行 ADB/install、不伪造或绕过 DEVICE 授权门，不以 synthetic DeploymentGate 单独充证。

仅 host JAR 重编；新 docs/coder/d1e13c 保存源码、来源 pins/JAR 成员、原输入日志、差异、交付说明、新执行计划/sourceReview/scope 草案及固定 once 路径。精确复用 E13A v17 三 APK 与 E13B metadata；不构建 APK/native、不重跑旧绑定/source 套件。旧封印及失败报告不变。ZIP 外 seal，默认/显式 verify/help 实际只读核验。

提交独立新批预算：重新 fresh M1，source 仍已接受 v15、17 尚未安装；成功路径48、占用余量单列、文本2MiB不扩，旧37/56余19不得继承。无设备/ADB/真实 once 写入/实际scope；完整交付后独立复审再派。D1 NOT_PASSED / M0 NOT_STARTED，214483/7R7S/全部P0与历史结果保持。
