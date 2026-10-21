# D1 E6A 开发需求 V1.0

2026-10-17。负责人原始技术派发完整保存：

E6完整复审后正式派下一完整批次E6A，集中修齐E6-F01/F02/F03三个P2再整包交测，不先部署E6。
请首先将本消息完整技术需求保存 docs/milestones/D1_E6A_CODER_REQUIREMENTS_V1.0.md，并单独保存对应测试需求 docs/milestones/D1_E6A_TESTER_REQUIREMENTS_V1.0.md（内容按下列验收，tester只独立复审不设备）。保留E6全部冻结不可变，新目录docs/coder/d1e6a。
1 F01：实际native snapshot已收到后，Java digest/receipt/content/thumbnail或stop/close失败仍保完整快照作为背景，准确原Java首错与cleanup分开，不把native OK当整体成功，不凭空补零；补实际生产边界有限后置失败及cleanup失败证据，不能仅helper自测。
2 F02：准确区分source阶段native诊断与validator task/mode/phase，validator未启动明确NOT_STARTED，源错误不能写validator拒绝/字段；正常validator成功和失败链保持，补真实生产边界源错误负例。
3 F03：接收边界合格snapshot原子一次发布，第一份保留，重复/并发拒绝不覆盖；校验先于成功发布，非法首份不能抢占合法槽，原PID/UID/epoch/task/大小/stage/帧一致门保持，补直接生产接收边界有限并发负例。
集中实现/意义明确自检后双APK一次主构建，必要修复保留证据，避免小功能交接。无设备/ADB/媒体源/导出件/下载；无必要不重建native，若变必须精确源及差异。E6Muxer六帧EOF/1000us/画面、原guard/recovery/每host观察/deadline/53651预算保持；既定框架许可/P0不变。完整四文档、精确diff/测试证据/新版本双APK同签名/输入日志/SBOM/ZIP外seal及只读verify/后续部署正常MP4→AVI→能力→条件cancel准确计划一次交付后主动报告负责人。
tester验收要求：三项问题逐一追到实际边界证据，异常语义/原子性/未启动归属，完整冻结及计划/许可原门；不得把本机证据当Android通过，设备另派。D1未过/M0未启。
