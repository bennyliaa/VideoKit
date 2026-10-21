# D1 A/K 一次集中收尾报告 V1.0

报告时间：2026-10-18 22:28（UTC+08:00）。结论：**主机侧集中收尾完成，平板包级强停未执行；不能判定全部资源归还，不恢复测试。**

## 授权与执行范围

负责人窗口转达的用户明确授权已保存：批准按方案对 A/K 一次集中收尾，包括必要条件后备进程和强停 HA1Q6WXR、user 0 的 `com.videokit.app`，接受未落盘信息损失及同包任务中断；保留全部证据，B/H 继续 UNKNOWN，完成后集中报告，暂不恢复测试。

依据 `D1_UNRESOLVED_TASKS_CONSOLIDATED_DISPOSITION_V1.0.md` §2，SHA-256 `f242eef9a91921af0e5c7a4f19b10c6b84c0815874f3d85ca6016eb86c3e745c`。执行前保存授权、有限预算和五份小型原记录副本。没有新增诊断入口、编译、测试或部署；仅使用现有系统和 Android 工具进行本次操作，保留本次主机控制命令供审计。

证据目录：`D:/CodexProjects/VideoKit/docs/tester/D1_AK_CLOSEOUT_EVIDENCE`。

## 一次身份核验与主机结果

2026-10-18 22:23:48.1981299 仅查询一次主机进程快照。选中身份记录 4164 B，含路径、完整命令行、创建时间和父链。为四个匹配角色打开并保留控制句柄，再次以该句柄 StartTime 对齐同次快照的创建时间；后续没有按裸 PID 重找或换 PID。

| 角色 | 同次快照身份 | 本次操作与 OS 结果 | 原业务/内部 ACK |
| --- | --- | --- | --- |
| K Java | PID 51664；父 6648；创建 UTC 13:48:53.161057；完整固定 release 命令匹配 | 22:25:35 一次外部终止；WaitForExit 返回，exit -1；`TERMINATED_WITHOUT_RETURN` | `originalJavaReturn=false`；Socket/keeper 原关闭 ACK 未证明 |
| K 原 launcher | PID 6648；父 18904；创建 UTC 13:48:52.246914；完整四参数 launch_once 命令匹配 | 一次最多 10 秒等待内自行退出，exit 0；终止调用 0 | 外层 OS 结束，不代表内部 Java 正常归还 |
| A Java | PID 38056；父 39560；创建 UTC 08:48:05.688029；原批次完整命令匹配 | 给一次 10 秒自然退出机会后仍在；22:25:46 一次外部终止，OS wait 返回，exit -1；`TERMINATED_WITHOUT_RETURN` | `originalJavaReturn=false`；原 authority/Android owner ACK 未证明 |
| A 原 ADB 客户端 | 历史 PID 49540 在唯一快照中未出现，未取得句柄 | 不操作、不找替代 PID；终止调用 0 | 当前未出现不能补回原客户端退出/关闭 ACK |
| A 原 PowerShell | PID 39560；父 52592；创建 UTC 08:48:05.005257；原路径和完整命令匹配 | 一次最多 10 秒等待内自行退出，exit 0；终止调用 0 | 后述原启动器记录证明外层进程/管道层；内部 ACK 仍缺失 |

以上 UTC 创建时间来自 CIM，句柄 StartTime 保留更高精度的原记录；差异小于 2 微秒。四个行政控制句柄均已 Dispose。本次控制会话 64804 于 UTC 14:25:46.4911914 保存 final 后返回，工具 exit 0。只读取了本次控制会话的输出，旧会话 42537、49433 均 0 次读取。

## 平板强停未执行及原因

仅执行一次 Android 身份/占用确认命令，显式连接现有 `127.0.0.1:5037` 并指定 HA1Q6WXR。已匹配：序列号 HA1Q6WXR、型号 TB138FC、当前用户 0、包 `com.videokit.app`、UID 10221、versionCode 17、versionName `D1-E13A-ACTIVATION`，安装目录及 User 0 状态已保存。

**本次选用的 `dumpsys activity instrumentation` 子命令不被该平板支持**，返回 `Unknown command: instrumentation`。因此只能确认项目包身份，不能据此确认没有其他项目占用。整条 shell 命令的 exit 0 来自末尾截断管道，不能把它当作占用确认通过。这是本次确认命令的适配问题，不是已经证明存在其他项目占用，也不是审批拒绝。

按方案 §2 第 4 步，无法确认占用则停止 Android 分支。本轮未重试或切换诊断路线，未打开/点击设置强停，包级 force-stop 次数为 0，状态 `NOT_RUN_OCCUPANCY_PRECONDITION_UNPROVEN`。未使用旧 Android PID，未扩大至 test、fixture 或其他包。随后仅完成仍在授权范围内、身份已核验的主机收尾。

**平板当前 instrumentation、服务及包进程是否仍有活动保持 UNKNOWN。** 本轮结束后不追加查询、不自动补做强停。

## 外层实际归还与原始 ACK 的区分

两条原 PowerShell 启动链退出前自行生成了以下小型记录；本轮只读取并保全这些已落盘元数据，没有读取原会话或私有缓冲内容。

- A 原 receipt：exit -1，`originalWaitReturned=true`，stdout/stderr reader returned、closed，以及 `bothOriginalPipesReturned=true`。保存 stdout 0 B、stderr 1285 B。这些是原启动器对其持有的 .NET Process 和两条管道的实际归还记录；不证明被终止的 Java 完成原业务、内部 authority 关闭或 Android owner 返回。
- K 原 receipt：exit -1，`allOriginalProcessAndPipesReturned=true`、两 reader EOF/pipeClosed/archiveClosed 均 true；stdout 317 B、stderr 354 B，合计 671 B。`allOriginalResourcesReturned=null` 且 `receiptOwnCloseNotProvenByThisFile=true`，不能把文件本身作为全部元数据对象的原关闭 ACK。原 launcher 的 OS 退出另由保留句柄证明。
- K 先前 `budgetUnknown=true` 的 Socket/keeper 由 Java 外部终止结束其持有进程；没有在原预算内读到 EOF，也没有原 Socket.close 成功 ACK。不能将其改记为正常读取完成或正常业务返回。

本报告的 `originalJavaReturn=false` 指原 Java 业务与内部归还证明缺失；与外层 .NET Process 已 WaitForExit/pipe 已返回属于不同层。原工具会话最终终端响应未读取，不推断工具层 EOF。

## 证据保留与账本

执行前已复制原 A live ledger、A intent/pending、K once/pending；执行后另存两份原 receipt 和 A ledger。原 intent、两个 pending 及 K once 的前后 SHA-256 相同，无删除、重置或 replay。

A 原启动器自行将 live ledger 的该事件写为 `ORIGINAL_RETURNED`，原操作计数仍为 37，文本计数由 114005 增为 180826（增加 66821 = 已落盘 stderr 1285 + nested 保留计费 65536），`nestedTextAmountProven=false`。tester 没有手改该账本；原启动器该标签仅指它的外层返回，不能直接解释为 Java 正常归还或测试通过。更新前后副本与 hash 均保留，当前独立行政账本不将该标签用作 UNKNOWN 退款依据。

K 原已分配预算 189440/262144、wire 70656 B 和预算未知结论继续保留；没有借用未进入的第二次额度，没有退款。B/H 分别记为行政隔离 UNKNOWN：没有操作历史 PID，没有补 ACK，也没有退款。B 的丢失诊断控制对象、H 缺少原代身份和返回链的事实未改变。

进程内尚未落盘的信息在外部终止后不可追回，实际损失字节数 UNKNOWN；已由原启动器保存的输出文件原地保留，本轮只记录其大小，没有为追回私有内容追加读取或查询。历史媒体、fixture、冻结证据和旧 N2 结算均未操作。

## 有限预算和排除范围

| 项目 | 预先上限 | 实际 |
| --- | --- | --- |
| 主机身份快照 | 1 次；选中记录 ≤32768 B | 1 次；4164 B |
| 同代控制角色/句柄 | 5 角色 | 4 个句柄，均已 Dispose；1 个未匹配 |
| 外部终止 | 每已核验角色最多 1 次 | A Java、K Java 各 1；其他 0 |
| OS 等待 | 每次 ≤10000 ms；每角色最多 2 次 | 未超限；无重试 |
| 控制器等待 Android 决策 | ≤600 秒 | 约 108 秒；有限返回 |
| Android 命令/文本 | ≤24 次；单次 ≤16384 B；累计 ≤131072 B | 1 次；落盘 623 B |
| Android UI/强停 | ≤6 输入；强停确认 ≤1 次 | 0/0；前置不足停止该分支 |
| 原会话/原缓冲读取 | 0 | 0 |
| 审批拒绝/绕过 | 如拒绝则停止并保存 | 拒绝 0；绕过 0 |
| 新诊断工具/编译/测试/部署 | 0 | 0 |

未操作共享 5037/ADB server、设备 adbd/system_server、其他项目/序列号、conhost 或非获选进程；没有 kill-server、root、重启、全树 kill 或通配清理。唯一主机控制命令只核验并操作获选角色，不是新的诊断服务或可重跑测试入口。

## 剩余事项与最终状态

| 项目 | 收尾后的事实与未决项 |
| --- | --- |
| A | 已核验 Java 外部终止、原 PS 退出，外层管道返回；Android 分支未执行，内部原 ACK UNKNOWN |
| K | 已核验 Java 外部终止、原 launcher 退出，外层管道返回；原 Socket/keeper 正常关闭 ACK UNKNOWN |
| B | `ADMINISTRATIVELY_QUARANTINED_UNKNOWN`，原丢失链无法补证 |
| H | `ADMINISTRATIVELY_QUARANTINED_UNKNOWN`，未对历史 30384 操作 |

本轮执行已停止，主机后备角色无需补杀；平板强停与当前占用未确认，不宣告整项收尾成功。负责人可依据本报告集中处理剩余事项。本轮不自动再次确认、补动作、部署或恢复测试，D1 测试结论不因行政终止而转为通过。

关键证据：`authorization-and-execution-requirements.json`、`pre-action-preservation.json`、`host-identity-and-handles.json`、`host-actions.json`、`controller-final.json`、`android-01-identity.txt`、`android-occupancy-assessment.json`、两份 `after-*-receipt.json`、`preserved-record-comparison.json`、`closeout-disposition-ledger.json`。文件均位于上述证据目录；报告发送回执单独保存，不回写已发送正文。
