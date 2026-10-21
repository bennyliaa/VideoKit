# E13J-R1 收尾补充（原需求全文附后）

2026-10-18。首次J集中候选已冻结但尚未交审；收尾自核发现raw写失败可能令审账writer早于reader退出。保留J初版所有字节，在独立J-R1目录继续原三P1任务，仅修raw故障后审账writer等待原reader done，并新增生产IO故障后继续接收有限尾字节的审账回归。预算/权限/执行范围不变。由于实际生产源码变化额外一次host编译，不能说整个J批只有一次；本revision自身一次。旧I/J及三历史UNKNOWN冻结不动。

# D1 E13J 三P1最小集中修复需求 V1.0

2026-10-18；依据E13I独立复审报告SHA250083aed28e914bd5d7eb67394fe3bdd69b87f48ec4f6a1f2fe75ed7fa330e7及负责人正式派单。仅修三项，不改旧I包、不扩大预算/通用框架；无APK/Gradle/native/长套件、真实5037/SDK/设备/旧handle/PID/处置。本批集中实现、有限自检及必要host编译后完整冻结交审。

F01：query70656与batch262144为实际应用层RX＋保守TX意图的硬额度。每次IO前核剩余，read长度不超过余额；余额0停止新增IO/依赖，保同Socket/owner UNKNOWN，不继续drain、不强关/换reader/重试。EOF判定也不能在0余额时偷读。仅限制本程序应用读取/发送意图，不声称控制OS缓冲/网卡/远端总流量。

F02：在现有query两份各≤1024B元数据额度内，由生产原owner有界落盘charged/incoming/TX/writeEnteredReturned/late/资格/各原归还状态及留存区别。事实快照不能自证自身close；意图先记、发送部分未知不退款，记录失败仍原保管。不能依赖ICheck额外facts文件充生产账。

F03：父check_host.run超资格后的同原Process持续wait与记录文件保管，不能被pending写入/console异常跳过；逐个记录原文件真实close或明确原保管，不能以日志成功作前提。直接有限验证pending/print分别抛错时仍同child自然wait/close，资格保持失败。

有限验证准确70656边界/到限read0（避免制造永久活Socket再kill）、生产审账而非测试额外facts、实际父故障保管及最终class字节。审批ABSENT/生产网络前拒绝保持，三个历史UNKNOWN只档案不补ACK。交付四文档、源码/diff/原始证据/JAR/脚本/外seal/准确ZIP及实际只读verify，更新两滚动文档顶部、完整主动报告。
