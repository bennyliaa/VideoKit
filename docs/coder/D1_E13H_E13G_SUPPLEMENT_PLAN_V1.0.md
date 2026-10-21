# D1 E13H 准确E13G补充方案待审 V1.0

2026-10-18；本包准备入口而非执行批准。当前方案BLOCKED_DIRECT_ADB_SERVER_REPLACEMENT_RACE_AND_SDK_PROTOCOL_MAPPING。不能发本包--g-readonly然后期待设备查询；Java与脚本都会在Process/网络前拒绝。E13G已fresh证实原host身份切片，不重复CIM、不循环观察，不据旧PID实施终止。

## 两条准确设备argv

第一固定数组及完整最后shell脚本见E13GReadOnly.INVENTORY和--describe原回执（host-001编译、final-002 describe）；无外部参数扩展。第二只允许第一完整证据匹配的app及am PID，生成的准确数组在host-001/SUCCESS/approved-argv-2.txt，仅本地fixture示例不能用于真实PID。实际两设备数组应在未来单一准入批次先固定第一，校验第一实际raw SHA/完整性/同scope身份后据模板定稿第二；不提供任意PID CLI，不从旧14763/14765/14779填参。

完整global活动instrumentation/进程来自dumpsys activity processes及ps，不能将filtered/截断当完整；64KiB不够或10秒资格失败则停止保管，不重试/追加第三条。第二包含boot_id/stat启动ticks/status UID/PPID/原cmdline，缺权限/变化则UNKNOWN停止。只读证据不等于旧owner返回，不能将PID消失当归还。fixture/codec等未精确匹配角色仍未知。

## server限制与待批替代

官方adb_client.cpp的协议不匹配分支会kill/start；版本检查与随后SDK新连接之间仍有可替换窗口，固定-H不能绝对排除。官方头ADB_SERVER_VERSION41只是候选协议来源，SDK准确构建映射未证，不能据软件版本37.0.1放行。本地host:version前置原型已有限验证，但生产未启用，也不能消除此竞态。官方证据链接及SDK byte pin见evidence/protocol-source-and-binary-binding.json。

建议负责人另审的最小替代范围：固定127.0.0.1:5037的一次host:version仅信息前置；后续每条采用已存在server的一条原socket，固定serial transport再固定shell-v2服务，完整处理同一原连接上的stdout/stderr/exit framing并复用原有有界归档/真实线程归还。该路径不调用adb.exe的version-mismatch kill/start分支，但与“必须由SDK adb.exe执行”的原要求不同，须明确变更并独立审查，当前未实现。不得变成任意ADB host service/serial/shell客户端，也不发host:kill或启动server；server缺席/不兼容/替换后未知均拒绝。不把协议内部transport握手冒额外设备shell，仍最多两条固定设备命令。需要审清同连接生命周期、失败保管、shell-v2界限和预算后才能实施；本文件不自行扩范围。

## 单次收取与预算

原exec42537未来最多一次空输入收取，响应资格改为≤10秒，不循环、不发Ctrl-C/非空输入、不重建session。本轮0次。原工具实际响应超资格仍记未决，不靠取消Promise或抛弃原handle制造截止；即使空输出/工具返回，也不是原Java/ADB/reader/pipe/Android ACK。原返回资格及case失败不改，若接口不能限制文本则不启动，记BLOCKED。

总256KiB独立批次草案：已采host及原父工具保守8192B；两设备原raw各65536B（共131072）；一次server前置1024B/2秒；原exec收取预留65536B；外层Java stdout/stderr预留32768B（不重复echo设备raw，只输出摘要和保管facts）；observer facts console8192B。共246784B，保留15360B。重复console实际输出也计入相应预留；不得将同raw复印无限排除计账。若原session工具无法保证65536B以内或其他wrapper实际将超过剩余，停止、不提额、不将未消费余额转供处置。

每设备命令64KiB/10秒是资格，不是同步调用强制终止；原Socket前置1KiB/2秒亦同。一次intent/准确review/pins、预算账和执行批次尚未签发，当前actualScope/release/once均null。未来替代实现受审前，原exec单次收取也必须负责人另派，不能由本文件自动开始。A/B收尾选择和所有终止动作仍另审；无Androidfresh启动身份时不可定稿终止。

本轮ADB/实际5037/原exec42537读取/设备/处置/安装/部署/方法重测均0。旧主任务最后PENDING/UNKNOWN，独立诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN未解除，实际根因NOT_UNIQUELY_DETERMINED。E13F及历史冻结不改；用户持续设备授权已存在，当前限制来自准确范围与原任务未决。D1 NOT_PASSED / M0 NOT_STARTED，T07未派、P0/许可保持。
