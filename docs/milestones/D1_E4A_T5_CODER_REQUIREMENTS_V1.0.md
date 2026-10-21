# D1 E4A-T5 私有目录流式封装传输需求 V1.0

2026-10-17。T4L实证app外部base与Download不可访问，无双视图staging。正式选择测试专用Base64 ASCII流→设备base64 -d→app私有文件路线，明确覆盖此前工具需求中“不做base64”的实现选择；它不是用户产品需求或许可证限制，不修改产品/权限/架构。无需新增外部存储权限、root或改manifest，不再外部staging/push方案反复试路。

新小目录d1e4at5，复用已审原process强owner/完整原响应，集中实现可复用256B诊断及后续媒体同路线参数设计。主机源分块标准Base64，正确3字节边界和末尾padding，输出仅ASCII字母数字+/=与可选LF，绝无0x1A或NUL；源读取/原字节SHA和实际编码字节/提交SHA分别记录。不可整文件缓冲/写巨大主机编码副本。设备同UID只准确新私有目录/目标，noclobber base64 -d直接解码落盘，无外部stage。标准shell_v2 -T -e none，stdin只编码流，原BEGIN/END阶段marker及解码返回/计数、独立有界原始SHA才能准入，exit0不等落盘。管道各端原返回和close未知保留，不借文本ASCII假设替独立hash。

实际设备base64命令支持尚未证明。下一诊断可先无文件写的printf固定四字符AA==经base64-d再od核一个00字节，保存每原rc（避免无pipefail吞错）；支持再一次256B编码接收。新目标/attempt不碰旧26B/归档。仅诊断max源256B/编码344B或精确有界LF数量，独立device hash256B，metadata<=20/每15s/1MiB/cleanup2s。失败保产物，不自动补传/换路/扩权限。

本机有限生产编码/进程测试覆盖0/1/2/3/256/跨64KiB边界长度、所有字节、padding、短写/close未知/解码非零/短件exit0/独立SHA拒绝，必要者集中一次，不重跑全部旧历史。无新依赖。coder不ADB/设备/媒体/stat/hash/Gradle。交D1_E4A_T5_DELIVERY/BINARY_TRANSFER_PLAN_V1.0.md、最小完整工具/外hash冻结/只读verify/有限证据。未来MP4/AVI精确源字节和4/3编码流量/流式内存/时限计划一并设计，但本批只提256B诊断，媒体执行另派。

尽快恢复真实产品测试，不扩通用工具、不嵌套复制历史大包。旧T4路线失败结果保留、不再默认外部路径可用。完整无在途主动报告，D1未通过/M0未启动/P0旧FAIL保持。
