# D1 E6A 独立测试需求 V1.0

2026-10-17。等待完整冻结，仅静态/已有证据独立复审，不设备/ADB/安装/媒体源或导出件读取/Gradle/native或模型重跑。逐一核E6-F01/F02/F03：

1. F01实际native snapshot已收到后，Java digest/receipt/content/thumbnail、stop/close失败仍保完整实际快照作为背景；准确原Java首错与cleanup分开，native OK不作整体成功，不补零。必须有直接执行生产验证边界的有限后置/cleanup失败证据，helper单测不足。
2. F02 source与validator准确task/mode/phase，validator未启动NOT_STARTED；源错误不得写validator拒绝/字段；正常validator成功及失败链保持。核直接生产源错误边界负例。
3. F03生产接收边界先完成原PID/UID/task/epoch/size/stage/frame/字段/尾数据验证，再原子一次发布；第一份合格保留、重复/并发拒绝不覆盖、非法首份不抢槽。核直接接收边界有限并发负例，不用仅CAS helper自测代替。

逐一追源码、实际执行边界、原始结果及输入hash；有限替身只可替代平台/传输，不得冒Android/JNI/Binder系统实证。核完整四文档、精确diff、同签名新版本双APK/最终输入/日志、SBOM/7native来源差异、源码ZIP/外seal/只读verify及下一准确保数据部署MP4→AVI→能力→本批正常receipt条件cancel计划。

E6及全部旧冻结/现场不变，不先部署E6。六帧/完整EOF/1000us/画面、guard/recovery/每host观察/原deadline/稳定budget及53651消费、原P0/框架许可保持；native无必要不重编，变更需精确证据。D1未通过/M0未启动，任何本机证据不作Android通过。集中报告负责人，设备另行正式派。
