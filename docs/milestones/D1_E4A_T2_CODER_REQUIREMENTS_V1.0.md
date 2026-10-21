# D1 E4A-T2 远端传输定位开发需求 V1.0

2026-10-17。T1P已fail-stop：残件归档成功；producer提交349102B/exit0但独立temp ABSENT，AVI未读。先定位，不再真实媒体补传。阅读完整D1_E4A_T1P_PRELOAD_REPORT及原backend argv/结果，重点区别ADB exec-in/exec-out对远端shell参数、run-as sh -c整体脚本引用、redirection/noclobber、工作目录/路径和stdin实际接收。不要把静态quote或exit0推断远端执行。

新目录d1e4at2，旧工具/产品/残件只读。以原证据及本机复现ADB参数拼接/远端argv解析为主，可查本地SDK对应adb源码/官方说明；缺证标UNKNOWN。提出最小修正和可审可直接执行有限诊断工具/计划，生产返回必须含独立原UID/pwd/准确路径/接收计数或明确执行标记，仍要外部独立stat/SHA。不能改用无限重试或仅加新一层quote猜修好。

本批coder仅本机自有合成数据/假子进程，不ADB/设备/真实媒体/stat/hash/Gradle。完整集中交付源码/外seal/只读verify/根因已证与未知分栏/有意义有限本机证据。下一设备诊断计划仅平板HA1Q6WXR：最多一个256B全字节合成payload、独立新诊断目录和一次attempt；最多20个metadata命令/日志1MiB/每命令15s/接收15s，原媒体路径只允许准确lstat不读内容、不改名覆盖删除；不递归扫描app/设备，不手机/安装/产品方法。准入确认现有原UID/目录及是否有前次接收仍在途的可得证据，不将ps空等同全部归还。失败保诊断产物，无补跑/换路。诊断只提案，负责人审查后另派tester。

目标是实际媒体功能可继续，而非扩大通用工具。仅解决远端命令执行/二进制落盘证据，保留T1实际close强owner/一次attempt/独立hash，不新增依赖。完整无在途后主动报告。D1未通过/M0未启动/P0历史FAIL保持。
