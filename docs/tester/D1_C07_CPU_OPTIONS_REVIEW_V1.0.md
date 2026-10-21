# C07 CPU两方案独立文档审核 V1.0

日期：2026-10-05。审查对象：冻结C07交付的 D1_SINGLE_APP_ISOLATION_OPTIONS_V1.0.md；对照原始需求§2.2、§10～14、§16.2、§21～27及架构准入评审。结论：方案信息可供负责人选择有限实验，当前两方案均未准入、未实现，不能计设备PASS或产品隔离通过。未下载、构建或集成CPU库，未运行新漏洞扫描。

| 审查维度 | 文档覆盖 | 仍需证明 |
| --- | --- | --- |
| A：FFmpeg CPU解封装/解码＋宿主系统编码 | 把压缩解析放ordinary isolated，宿主只接收有界复制裸帧/PCM；建议独立CPU输出验证任务 | 宿主JNI/渲染/系统codec客户端仍有native边界，裸数据校验不保证宿主不会崩溃；须实际故障验证原始§27，失败退出 |
| B：FFmpeg＋OpenH264全CPU编码/封装 | 编辑、编码、封装和独立输出验证均规划在低权限任务；preview仍有有界裸数据出口 | CPU性能/峰值内存/热、软件H264/AAC输出质量、共模验证、库加载与hung task终止未实现；纯CPU不等于安全 |
| 高风险完整链 | 规划源解析/解码/分析/遮罩/输出验证边界，明确不允许宿主压缩解析回退 | 图片、大图、复杂字幕、检测/跟踪/模型、最终遮罩质量仍未选定或实现，不能据当前AVI路径关闭P0 |
| 单App／独立AAR | Manifest合并、nonexported isolated Service、不同宿主各自broker及去实验包名硬编码有计划 | 没有两个最小宿主、Manifest/R8/ABI/SDK独立接入的实际证据；现有companion结果不能移作此能力 |
| 源与输出验证 | opaque broker、64位偏移、源只读、临时Sink、独立CPU完整解码及正式双轨/PTS/覆盖规则规划明确 | 自定义AVIO、seek/write/fsync/真实writer lease、READY未知/跨owner恢复和恶意输出验证仍须真实管线复验 |
| TOCTOU与预算 | worker共享区先复制至宿主不可变缓冲，再检查尺寸/stride/offset/长度/PTS；在途帧和传输字节有限 | 内部decoder峰值、复制竞态、伪task/epoch/UID/PID、OOM、另一槽存活和真实死亡/source释放须验证；合作式中断不保证native硬停 |
| 许可证与发行 | 指定FFmpeg n8.0/OpenH264 v2.6.0，白名单/链接/源码/通知/EULA、专利与商店条件分开 | 未取得完整源码包身份、真实config/ELF依赖/SBOM、漏洞及商店/宿主义务审核；不能仅凭configure参数批准 |

独立核对官方文本：FFmpeg n8.0主要为LGPL-2.1-or-later，选用GPL部分或外部组件会改变许可组合；原文不是“FFmpeg全部GPL”，也不能据此忽略具体构建义务。[精确tag许可](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/LICENSE.md)。FFmpeg官方动态链接清单同时要求匹配源码等资料，并说明不存在付费专有许可替代路径；该清单只是其建议的合规路径。[官方许可说明](https://ffmpeg.org/legal.html)。

OpenH264 v2.6.0源码许可有两项保留版权/条件/免责要求。[精确版本LICENSE](https://raw.githubusercontent.com/cisco/openh264/v2.6.0/LICENSE)。Cisco提供二进制的专利安排另有条件，包括单独下载及用户控制，不能直接移用于自编译并集成的AAR。[Cisco二进制条款](https://www.openh264.org/BINARY_LICENSE.txt)。本审核确认文档区分正确，不批准实际商业分发或专利权利。

两方案对数据和进程边界有明确提案，但没有满足完整原始P0的实现证据。A的宿主native风险及B的性能/许可/终止能力是独立退出条件；检测/跟踪/图片/字幕未实现是共同缺口。不由tester选择路线、放宽原需求或新增依赖。下一步只能由负责人选定并准入后安排一整批有限实验；若无法满足真实崩溃边界、终止/资源门禁、发行义务或最低设备预算，保持BLOCKED，不能以companion产品化或扩大预算替代。

ordinary历史App UNKNOWN=FAIL不变，本次不重复派测；外部native原因事实不作为单App CPU管线通过。手机、实际源帧PTS、标注质量、NAS和最终P0仍未闭合。
