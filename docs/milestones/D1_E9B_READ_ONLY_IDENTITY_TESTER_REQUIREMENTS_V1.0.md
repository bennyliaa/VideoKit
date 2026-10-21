# D1 E9B READ_ONLY_IDENTITY tester requirements V1.0

2026-10-18；正式派发来源：负责人「VideoKit项目助理」01a107c3-2bf9-7fa0-94a0-234258ca6774，本批发送给tester的E9B_READ_ONLY_IDENTITY指令。设备使用授权沿用户对HA1Q6WXR永久授权及2026-10-18继续推进项目；本文件的SHA仅绑定这份真实指令范围，不是写迁移批准token。E9B独立复审报告SHA256 03cae4e6313db391ea0838bc289814b97a1319bd98ac6d08e30f2a4df1fa5fb1 支持有限只读身份/控制批次。

只允许HA1Q6WXR/user0、app UID10221/test10222。先核实际设备/当前已安装pair/证书/版本/启用身份及无原相关在途进程；设备不存在则报告，不轮询。不操作手机或其他设备。

候选version13 E9B PREPARE，app SHA256 ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020；test SHA256 2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b；生产host JAR SHA256 4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707；证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f。若需更新仅生产受管部署门两条install-r各一次，保数据，不卸载/clear/重复安装。

先存本批scope/config/canonical命令及SHA账。生产--approved-session配置/pin，不使用SYNTHETIC_LOCAL。仅一个actor，显式READ_ONLY_IDENTITY；继承协议批标签D1-E9A-PREPARE-TABLET-20261018，不改包。生成准确只读actor/registry身份和同scope外部记录属本批，不能产生COMMIT/产品authority、真实迁移批准token/H_actor/catalog。

Android控制≤8，STATUS≤3；每响应同一个原5秒绝对预算，identity资格10秒。本机STATUS/OP/CLEANUP合计≤16统一账并预留收尾；128总accept不清零。不循环轮询、不重发未知原命令/ACK。主机只读兼容错误最多2次留痕修正，不用于安装/启动/UNKNOWN重试。

验证非等待client归还与actor独立存活、DUMP保护广播完整transport、真实boot/start与身份FD实际归还；有效原identity return bytes先完整归档，再唯一精确ACK_FINISH，独立核finish锚/ActivityManager normal finished inst/原PID缺席，最后核PC原Process/pipes/Store/listener/remote全部实际返回。不以launcher exit/finishClaimed/native close替代。

未知/失败停止依赖，保留原custodian/handle/未返明细，仅同scope有限收尾；不得kill/force-stop/restart/换端口/预算/clear或用测试fixture teardown处置真实任务。主机审核门不满足就报告准确缺项，不跳gate或造授权。

禁止RESERVE/EXECUTE_COMMIT/SEAL_FINAL、写迁移、媒体、actor2/3、正常产品、旧ABORT/预算变更。原107218/3R3S/S0/fence/档案/oldCloseACKfalse保持；本批不能关闭长期准入或D1/M0。

原始证据与命令资源账保存docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE；报告docs/tester/D1_E9B_READ_ONLY_IDENTITY_DEVICE_REPORT_V1.0.md，完成主动发送负责人。没有实际Android证据的故障项为NOT_RUN，不自动后续测试。
