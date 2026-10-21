# D1 E4A-T4 二进制传输路线集中修正需求 V1.0

2026-10-17。T3L准确合成文件26B/SHA等0..25前缀，首个缺失预期字节0x1A；Windows/ADB文本stdin处理是待核假设，不能直接改写为已证根因。阅读T3R/T3L原证据，集中查本地SDK/官方ADB源码Windows stdin setmode及shell输入路径，区分精确SDK映射未知。

停止继续给shell stdin链叠协议。优先采用ADB标准sync/push二进制文件协议，评估指定app可访问的安全staging（例如app专属external files）与run-as内部复制：准确路径/权限/SELinux/Android12 scoped storage仅设计未知，不能默认可用。不能广泛放开应用目录/全局可写、root、改产品manifest/存储权限或向媒体库发布；若选更合适受控路线，说明依据。尽可能复用现有adb push及已定工具，避免另造通用传输框架。

完整实现/计划及有限本机生产调用证据，新d1e4at4冻结。标准push源参数只读明确合成256B；push命令exit0仍须独立staging长度SHA及内部最终长度SHA，接收/复制原返回和owner界分开。固定唯一路径/一次push/一次内部copy，拒覆盖冲突，失败保原产物不重试/换路；staging和internal各256B新增，原26B残件不动。需要临时创建app外部专属目录仅准确子目录，不能改现有文件权限或清理历史。

下一平板诊断计划先一次只读准入staging可访问性/权限和工具支持，满足才一次256B，不得实际媒体补传。metadata<=20/每15s/日志1MiB/push15s/复制15s/清理2s，仅合成host读预算和设备两处hash明确。失败停止，旧远端UNKNOWN不清，T1 close强owner不回退。媒体后续计划可复用同路线，但本批不执行、不读取/stat/hash真实媒体。

coder仅本机源码/原证据/自有合成验证，不ADB/设备/媒体/Gradle/依赖下载。不要仅改批次复制全部历史源码证据放大包，保必要来源引用即可。交D1_E4A_T4_DELIVERY及BINARY_TRANSFER_PLAN_V1.0.md、完整可审小工具/冻结hash/只读核验，集中一次完成并主动报告。目标迅速恢复产品播放验证，当前D1未通过/M0未启动/P0历史FAIL保持。
