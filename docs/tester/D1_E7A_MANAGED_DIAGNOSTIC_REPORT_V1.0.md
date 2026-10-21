# D1 E7A 受管只读诊断报告 V1.0

2026-10-17，Tester。正式派发：`docs/milestones/D1_E7A_MANAGED_DIAGNOSTIC_TESTER_REQUIREMENTS_V1.0.md`。冻结计划未改，执行唯一E7A custom instrumentation，没有执行JUnit/正常产品方法。

## 结论

**诊断收集完成：QUALIFIED_DIAGNOSTIC；当前死亡门仍BLOCKED；原只读句柄实际归还，平台正常结束，无在途任务。** 实际请求的历史API返回0条、匹配0条，因此proc未查询；不能将本结果说成旧AVI当时记录淘汰或PID复用的证明。

E6B-OBS-F01/P1持续OPEN、持久协议DESIGN_BLOCKED。E7-F01的静态修复取得本次真实快完成路径、异步保留及受控结束的支持；在途超时/allocate-close UNKNOWN等故障路径未注入，不登记为全部实机关闭。原MP4限定PASS保留，不解锁AVI/能力/cancel，D1 NOT_PASSED/M0 NOT_STARTED，其他P0/许可不变。

| 分项 | 实际结果 |
|---|---|
| 诊断收集 | QUALIFIED_DIAGNOSTIC，ACTUAL_RETURNED，原10秒资格未放宽 |
| 当前writer死亡门 | BLOCKED_CURRENT_GATE；NO_UNIQUE_MATCH_MISSING；history AVAILABLE/returned0/matches0 |
| 原操作/句柄 | originalOperationsReturned=true；holder=CLOSED；safeToFinish=true，完整快照已归档后才ACK |
| 受管平台结束 | 精确ACK后出现系统finished inst及Killing原PID，最终进程不存在 |
| 控制账 | STATUS1次、ACK_FINISH1次，共2/6，剩余4；无STOP、无控制重试 |
| 正常测试/恢复 | 全部未执行，无observe/force/恢复写/媒体/CPU/codec/grant |

## 身份、部署与单次启动

仅HA1Q6WXR/Lenovo TB138FC/API31/ARM64/user0，原app UID10221/test10222。安装前原E6B双APK身份与原无在途记录/进程清单相符，没有目标app或相关worker进程。安装后版本10/D1-E7A、UID与最终base.apk指纹核实；app→test各install-r一次且Success，无重装/清数据/卸载/降级。

- app：10544590B，SHA25678ec2d3b057b91736ea0bf273ab6bf1b1028dae97916052b5ddb235087d84baf。
- test：2738285B，SHA2565a97f705813dfbe6f1476d9409c6448a7de981ea77420f2733890691a2248646。
- 原同签名证书沿冻结核验，外seal1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76；未重复签名工具。

`pm list instrumentation`实际确认组件：com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation。不是AndroidJUnitRunner；旧不安全JUnit未执行。

启动前保存 `managed-task-handle.json`：handle9f19bfb5-60e0-4bcc-9666-852409cfe3b4、serial/user/原UID/精确组件及双APK身份/命令。四参数为原plan的e7aCase=originalRecoveryWriterReadOnly、e7aBatch=D1-E7A-WRITER-DIAG-TABLET-20261017、e7aScope=READ_ONLY_MANAGED_NO_ADMISSION、上述handle。

单次非等待am instrument，不含-w/proto/class/UiAutomation；客户端返回0/空stdout仅记“已返回”，没有当作作业完成。实际系统创建PID13876/UID10221，随后从该PID取得同handle状态和日志。未再启动任何instrumentation。

## 当前结构诊断：已知与未知

完整外部原快照 `control-01-snapshot.json`，SHA256339ad43ef17b3ae2d2624b50bb1e2de3ad5157c23b1c268e2721db66208968dd，sequence9/RETURNED。诊断原writer：attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f/PID4869/UID10221/com.videokit.app/ownerRecordedAt1792224193301。

实际生产gate输出schema1/historyAVAILABLE/limit8/callsMax1/returned0/matches0；rejectPid、rejectUid、rejectProcess、rejectBeforeOwner、rejectFuture、reasonNonPositive均0，因为此次列表为空，不代表检查了某条记录并通过。matchedTimestamp/reason/status均NOT_COLLECTED；proc=NOT_REQUESTED，错误不是proc可见/复用，也不是一个已返回reason0的匹配。

结论只能是**此次按原PID条件的有限历史查询没有返回记录**。API有限环形历史的一般性质不证明本次具体淘汰；重启、PID复用、旧AVI当时实际列表及reason仍未证。不扩大max8、不重查历史、不以旧成功proof替代当前结果。birthGenerationNOT_RECORDED、persistentFactDISABLED、grantNONE、observationNOT_CALLED保持。

## 真实归还、归档ACK及平台结束

实际run读取并通过固定owner字节/身份校验，完成原close与后置检查、一次history；因历史缺失没有proc调用。快照CLOSED由冻结原E4Owned/Os.close实际返回路径产生，operationsReturned覆盖原操作链；不是单凭进程消失或控制resultCode推断。未额外导出FD号/系统调用trace，因此句柄关闭的证据等级是实际生产状态加冻结绑定，不冒充独立逐FD跟踪。

关键设备日志时间（epoch秒）：

| 事件 | 原始时间/状态 |
|---|---|
| 创建诊断进程 | 1792233991.300，PID13876/UID10221 |
| 首次RESERVED | 1792233991.457，sequence1/EMPTY/未返回 |
| 原操作RETURNED | 1792233991.470，sequence9/QUALIFIED/CLOSED/safe |
| 截止事件后仍保持已完成结果 | 1792234001.462，sequence9，未提前finish |
| 唯一ACK后的声明 | 1792234058.820，sequence10/finishClaimed=true |
| 平台实际结束 | 1792234058.824，ActivityManager finished inst |
| 系统结束原进程 | 1792234058.825，Killing13876 due to finished inst |

RESERVED到RETURNED的日志间隔约13ms，只是两个日志点，不是精确全部系统调用耗时；10秒资格由实际run的单调时钟判定。原任务早已完成后，自定义instrumentation持续存活超过10秒，直到外部归档确认才结束，支持onStart返回不自动完成以及受控finish的真实快路径。

先完整保存sequence9快照及独立准入 `finish-admission.json`，再以相同handle/archivedSequence9发送ACK_FINISH一次。响应sequence10/finishClaimed=true仅记声明；另以系统finished inst/Killing13876和最终进程清单无该PID/相关app进程证明平台确实结束，不将声明本身当完成ACK。

receiver实际unregister返回由“冻结唯一super.finish之前必须unregister成功”的控制流与真实finished-inst事件联合支持，没有单独导出unregister系统调用trace。最终 `dumpsys activity instrumentation` 在该OEM不支持，不能用其文本空缺证明结束；这里采用的是上述实际系统日志和进程清单。无遗留受管作业/未归还原owner，本批结束后停止。

## 控制与外部账本

预检从shell包的既有权限记录取得android.permission.DUMP:granted=true；没有授予、更改任何权限。第1次STATUS实际送达该PID并返回精确handle状态，证明本平板上此发送资格/路由/正向响应可用；未测试无DUMP发送方拒绝、系统异常或失联注入。

| 线上的实际控制请求 | 证据与耗时 | 剩余额度 |
|---|---|---:|
| 1 STATUS | control-01-response及snapshot；约0.110s | 5 |
| 2 ACK_FINISH，archivedSequence9 | control-02-response及direct-tool receipt；工具总耗时0.319s，低于5s | 4 |

总请求2/6，从未清零；不因响应采集的intent文件或主机失败把它误计成再次广播。控制账见 `control-budget-final.json`。无第二次STATUS或凑>=10秒再查：第1次已经证实安全完成；设备自身截止事件有日志，保持已完成结果。无STOP，因为本次不处于PENDING/UNKNOWN资源隔离。

17次实际ADB客户端（含一次已知无副作用的只读命令不支持）：安装2、启动1、控制2、其他只读12；原始输出180050B，低于1MiB。全部客户端已返回，无客户端超时或在途。未kill/force-stop/interrupt/restart；系统因实际finish而退出进程的记录不是Tester主动终止未知任务。

## 主机工具问题与证据保留

两次被派发允许的只读兼容修正均留痕：pm不支持check-permission，改读既有shell权限记录；package dump不列组件，改专用组件列表。成功身份/安装/指纹证据复用，没有重复安装或成功设备检查。

ACK包装器在ADB前因intent文件glob误含response采集intent、无command键而停止；此时没有写入ACK控制意图或发出ACK。原包装器保留、不修改、不重跑，审查已归档安全快照后直接发送原派发已批准的唯一精确命令，并单独留control-02意图与原工具回执。该主机错误不是产品方法或已发/UNKNOWN控制重试；实际上线ACK只有1次，既有两次只读兼容修正没有追加为第三次。

最终自动审证脚本已验证快照、顺序、实际finish和控制门后，在主机回执数量的硬编码期望15处停止；原脚本保留未修改/未重跑。最终数量由现存清单人工核对：16份采集回执加1份直接ACK回执，共17次；未为对账新增设备检查。最终审证采用原始记录独立审查和人工计账，不宣称该脚本整段PASS。

## 范围、产物与后续

本批只打开固定原owner元数据（最大257B哨兵），没有视频源/导出件、额外预算内容/hash、恢复写、observe/force/sync/ledger/fence/grant、CPU或正常产品操作。原107218累计消费/reserved0和全部旧输出/N2归档沿最后设备证据保持，本轮未读账本重新证明，也未清账或变更预算身份。

本次验证快完成、有效DUMP控制、精确归档ACK和实际平台结束；超时/UNKNOWN/无权限/系统杀进程分支没有故障注入，既有有限替身证据不升级为本批实测。持久协议没有实现，诊断收集完成不替代当前死亡门或原最终观察，更不产生任何正常测试准入。

原始证据及原失败脚本/回执位于 `docs/tester/D1_E7A_MANAGED_EVIDENCE/`，总汇 `final-independent-review.json`。日志SHA2569864464c5251584f945120be4cdd70a3d867dcb31a2c4e5e9ab06c3fa3f577a8；最终进程清单SHA256bafc46bb1a3e1649f5ac929fb5d39c0fd2e00805c2a6c875a094ba73db2cf601。完成集中报负责人，等待长期协议/旧V1安全处置的正式安排，不自动任何后续测试。
