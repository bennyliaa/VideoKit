# D1 E13H 最小只读入口离线适配需求 V1.0

2026-10-18；负责人正式派单及后续server协议前置补充。先读E13G报告`docs/tester/D1_E13G_CURRENT_STATE_AND_DISPOSITION_PROPOSAL_V1.0.md`，SHA02d60005562af95b4257befb623ff00911f956615ffbaa66ee955397809000fb。E13F与所有历史冻结保持；本批只离线准备入口和补充方案，不启动ADB、不连实际server/设备、不读取原exec/handle，不外部处置。

仅新增G-only固定只读角色，复用既有Process/唯一reader/有界archive/实际线程归还/异常custody和pending机制，不新增通用框架、不编Android APK/Gradle/native。固定SDK adb.exe及serial HA1Q6WXR，最多两组准确设备argv：第一组完整global active instrumentation与完整进程；第二组只能从第一完整证据严格校验同原scope/包/UID/父子关系推导PID后生成固定/proc启动身份读取，禁止任意PID/任意shell/外部argv注入。每条64KiB、10秒资格，总输出256KiB包含host/原输出；不启动/重启server，不重试、不部署、不执行产品角色。原owner先登记，未知/超时继续保原对象，不kill/二close。

补充允许一个最小现有server协议只读前置：仅固定127.0.0.1:5037，唯一host:version，最多1KiB/2秒资格，计入原256KiB总预算。不接受任意host service、host:kill、启动ADB/server；缺席/不完整/未知/版本不匹配拒绝。版本来源要区别官方源码常量与准确SDK二进制对应，不能凭37.0.1等软件版本猜协议值。

预检与随后adb.exe存在server替换竞态；预检不能自称绝对不重启保证。若最小方案不能排除此路径，生产入口保持拒绝，完整提交受审替代方案（可建议同现有server协议连接固定transport/shell，未经另审不得自行实现扩大为通用ADB客户端）。必须写明可执行边界、剩余限制与严格拒绝条件。

集中实现后仅必要一次host编译，有限成功/短超时/写失败/错exe/serial/argv拒绝自检，准确最终JAR/脚本字节绑定、差异/来源、外seal/ZIP及实际只读verify冻结，主动整包报告。原exec42537建议未来最多一次空输入读取，响应资格≤10秒，不循环、不发非空输入，不把空输出/工具读取返回当原资源ACK；本批不实际读取。待独立复审后由负责人另派准确补充执行批次，T07未派、原主PENDING/诊断LOST未解除，用户持续授权已存在。
