# D1 E13C 平板执行与在途保管报告 V1.0

2026-10-18；tester；设备 HA1Q6WXR。批次 `aeefe32f-816d-4c0b-aca7-16f76dbd45ff`。

**结论：PENDING / NOT_PASSED。** fresh M1、唯一部署及 M2 通过；首方法 `ordinarySenderCannotBindCodec` 原 Java/ADB 仍在途，未取得 Android 终态、原资源归还或绑定结果。后五方法及 M3 未启动。旧 N2 的 ABORTED_SETTLED 为另一任务历史结果，不代表本批归还。

## 已完成的真实执行

| 阶段 | 结果 | 证据 |
| --- | --- | --- |
| fresh M1 | PASS，179 项核验 | 原 source v15、UID/data、无活动 instrumentation、历史产物与账本符合准入 |
| 唯一部署 | PASS，原 Java 返回 | E13C JAR 调用 32 个 SDK 子操作，app/test 15→17 各 install-r 一次、fixture 首次安装一次；实际子文本 88888B |
| M2 | PASS，46 项核验 | app/test v17，UID10221/10222，fixture 独立 UID10228；data6972/4741 保持；当时无相关活动对象 |
| ordinarySenderCannotBindCodec | PENDING | 仅执行一次，原 Java/ADB 尚未归还 |
| 其余五方法、M3 | NOT_RUN | 首方法未满足停止门后的继续资格 |

部署 once 实际生成 460B，SHA256 `a0b934bce94b31674c73d345e47ac72202eb2c537ff8f342615eb2af22117766`；部署 PC handle `ac7884a2-3d72-48d4-87d3-298c25362ede` 有原实际归还回执。此处 PASS 仅证明本次部署阶段和 once 修复，不证明首 case 或项目通过。

## 原在途对象与只读观察

首 case 入口时间 16:48:05（UTC 08:48:05.6692683）。原 exec session **42537**、PowerShell **39560**、Java **38056**，原 runtime scope SHA256 `116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef`。55 秒后写入 PENDING marker；没有强制结束或重发。

本次仅一次同 session 空读，返回 running、增量 0B，无 EOF。17:01:39 的本机进程身份采集确认同一 PowerShell、同一 Java（启动时间16:48:05.688），及 Java 原子 ADB **49540**（16:48:05.953）。其完整命令为该 scope 的唯一 `am instrument` 首方法。因此当前并非仅有历史 PID 记录，原宿主和子 ADB 在观察时真实存在；不能标为 LOST_OWNER，也不能认定已 close。

原 harness 在同一 PowerShell 强持有 Process、两个 CopyToAsync reader、pipe 和 MemoryStream，等待原进程及两个 reader 自然返回后才保存完整 raw 并写最终 receipt。本次没有外部检查 reader 内部状态或内存缓冲长度；仍运行的工具会话和进程身份支持保管连续性，不能替代逐个资源归还 ACK。当前首 case 最终 stdout/stderr/receipt 尚不存在，缓冲不视为已落盘证据。

负责人补充只读诊断已记录在 `pending-observation/authority.json`。仅发出第一个直 ADB 进程列表查询，原 stdout **58908B**，首尾 `E13C_PS_BEGIN/END`、内部 `E13C_PS_EXIT=0` 齐全。可见 Android shell14763、am app_process14765（16:48:35）、应用14779，命令绑定准确首方法及 scope。设备与本机显示时钟不同，未将两者混作同一时钟或据此推断耗时。

该诊断的输出读取已经通过脚本等待条件，但保存空 stderr 时出现 tester 记录错误：PowerShell 将空字节数组经子表达式变成 null，WriteAllBytes 抛错，未执行后续 final receipt/显式 pipe close。脚本宿主退出不能补造逐资源 close ACK。本地原 stdout 已保留，原 stderr、退出码、精确时长及最终资源回执不完整；该项记 **DIAGNOSTIC_RECORDING_ERROR / UNKNOWN_FINAL_RECEIPT**。未重跑，未执行剩余 activity/services 与 logcat 两次诊断。因此只能定位为原 instrumentation 链仍在途，无法判断实际停在测试准备、普通发送者绑定还是 E9 归还阶段，也不能判定 kernel 拒绝 PASS/FAIL。

## 预算、冻结及停止

原 live ledger 保持其唯一原宿主所有，未外部改写：37 个操作分配、已结算文本114005B。其中首 Java 与原 instrument 各1已占用；本次进程身份补证了子 ADB49540的真实创建。补充成功本机身份1、实际诊断 ADB1；另将被 sandbox 拒绝的本机 CIM 尝试保守计1，合计 **40/55**。唯一原 session 读取单列，不作为新设备操作。未消费诊断额度不转供后续测试。

已保存诊断原文本58908B，原未决文本上界保留147456B，合计保守文本上界320369B，低于2MiB。缺失诊断 stderr 不伪记为空或精确结算；该诊断继续保守保留完整65536B额度时，总上界326997B仍在范围内。其余未知诊断/资源事实不退款或补造。

只冻结已落盘输入、已完成 M1/部署/M2 回执及其 raw、当前 case intent/初始 pending marker、单独资源快照与诊断文件。manifest 明确排除原 live ledger、首 case 将来自然返回后可能新生的 raw/receipt、以及运行中 harness 文件；原会话和还可能增长的产物不宣称不可变。独立审证核验三阶段六份 raw 长度及 SHA，全通过；这只是证据完整性核验。

未 kill、force-stop、二次 close、重发 case、替换 UUID、重启 ADB/server、重部署、绑定操作或启动其他方法。保留原会话及宿主等待自然返回；若将来自然返回，需要另出补充结果，不能改写本报告的时间切片。当前停止本批后续执行，未向 coder 派发设备修改。

历史账本最后核验的2271B/214483B消费/7R7S/0预留属于准入证据，本次未采集 case 后账本、最终设备状态或 M3，不能声明这些仍是当前终态。D1 NOT_PASSED、M0 NOT_STARTED、历史问题保持。

证据根目录：`D:/CodexProjects/VideoKit/docs/tester/D1_E13C_TABLET_EXECUTION/aeefe32f-816d-4c0b-aca7-16f76dbd45ff`。资源切片与独立审证见该目录 `pending-observation/`。报告单独发送负责人并保存通知回执，不将通知回执反写进已发送报告。
