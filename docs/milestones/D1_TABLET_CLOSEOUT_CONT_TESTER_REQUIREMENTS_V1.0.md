# D1 TABLET_CLOSEOUT_CONT tester 执行要求 V1.0

2026-10-20；负责人窗口 `01a107c3-2bf9-7fa0-94a0-234258ca6774` 转达最新用户恢复指令：“请继续推进项目，先完成平板剩余收尾，再协调coder和tester恢复开发测试，完成后集中报告。”

本批仅完成平板剩余行政收尾；既有用户已接受指定包任务中断和未落盘信息损失。不重复已完成的主机终止，不自动进入 T07、部署或产品测试。

固定设备 HA1Q6WXR、user 0、包 com.videokit.app。保留所有旧 once、账本、媒体、pending 和证据；B/H 继续行政隔离 UNKNOWN，不补原 ACK、不退款。外部包停仅为行政收尾，不代表原 Java/Socket/reader/Android owner 正常返回。

执行顺序与有限预算：

1. 先保存本文件及本批证据目录。一次本机只读兼容性确认：核当前 5037 listener 的实际进程/路径/创建时间/命令行，与同源现有 ADB 文件身份及本地 version 输出。不得启动、停止或重启共享 server；同源/兼容不确定即集中报告具体阻塞。
2. 唯一一轮前置完整采集：准确设备/用户/包身份及已在 API31 实证支持的 `dumpsys activity processes`。全量原始输出有界，资格 15 秒、最多 512 KiB；完整保存 stdout/stderr、实际 exit/EOF/字节数。禁止不支持的 instrumentation 子命令，不以 head/grep 截断或管道 exit 0 作为空闲证明。可选一次既有 ps 补充，最多 128 KiB。
3. 全局 active instrumentation/项目占用若不明确、存在其他项目活任务、缺完整头尾、诊断错误、截断、超额或记录/命令异常，则本批停止并集中报告；不循环重试。其他项目占用时将下一次机会交负责人按半小时节奏安排，本批不自建监控、不抢占。
4. 若全局无其他项目活任务且目标包身份明确，使用已有系统/ADB/UI工具进入该包的应用设置，仅一次“强行停止”及其确认。只操作固定包，不扩大到 test/fixture/其他包，不使用旧 Android PID。
5. 随后一次受控只读采集 package stopped、项目进程和完整 activity processes，判断行政收尾结果。不复查或补动作。
6. 整批最多 8 个 ADB 调用（本地 version 也计入），全部原始文本总额最多 1 MiB；单次完整采集最多 512 KiB，ps 单独补充最多 128 KiB，UI/版本小结果单次最多 32 KiB。每次资格最多 15 秒；标准客户端资格失败只处理该次自建客户端，不触及共享 server/设备系统进程；任意异常停止，不创造长期 keeper 或诊断任务。

使用现有 SDK/系统工具及标准有限调用/落盘方式，不实现自定义 ADB 协议、keeper、发布绑定，不编译。新产物只写本批目录；UI dump 如需写设备，仅写本批独有 /data/local/tmp 文本路径并保留，不触及旧媒体或证据。

完整报告：`D:/CodexProjects/VideoKit/docs/tester/D1_TABLET_CLOSEOUT_CONT_REPORT_V1.0.md`；证据：`D:/CodexProjects/VideoKit/docs/tester/D1_TABLET_CLOSEOUT_CONT_EVIDENCE`。发送负责人前计算报告 hash，回执单独保存，发送后正文不改。完成主动集中通知负责人，然后停止，等待负责人整批恢复安排。
