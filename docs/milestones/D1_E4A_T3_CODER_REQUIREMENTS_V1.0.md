# D1 E4A-T3 features解析集中修复需求 V1.0

2026-10-17。采纳T2P实证E4AT2P-F01/P2：真实220B CRLF features含shell_v2却误拒。仅最小工具兼容修复，新d1e4at3候选，不改旧冻结/报告。解析完整成功原响应，明确支持CRLF/LF与逗号token分隔，精确匹配shell_v2，拒绝shell_v20/noshell_v2/无效编码或不完整响应，不降级通道。保原exit/stderr/完整长度SHA/资源返回门。

以tester保存features-original-stdout.txt原220B/SHA05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce作离线真实回归，加LF/逗号/缺失/相似token/混合分隔/截留或错误原响应的有意义有限检查，直接生产解析器，不重复历史全部假进程。批内检查诊断剩余真实命令格式兼容性，能从同类已知输出格式修正者集中处理；未证不可预判通过。

完整工具源码/精确新批次诊断计划/有限证据/外seal ZIP及只读核验一次交付。新拟定T3P唯一入口/证据目录/诊断目录和nonce，不复用已消费T2P attempt；原T2P无producer/无新文件事实保留。下一计划仍一次256B/metadata20/15s2s/1MiB，其余UID/pwd/标记/独立SHA/旧路径仅lstat/原未知保留不弱化。coder不ADB/设备/媒体/Gradle/下载；诊断另派。D1未通过/M0未启动/P0历史FAIL保持，完整主动报告。
