# D1 四项未决任务集中处置提案 V1.0

编制日期：2026-10-18 22:04（UTC+08:00）。本文件仅依据已落盘证据编制，不构成新执行授权。

## 结论与本轮边界

四项分别为旧主任务、旧 LOST 诊断、H30384 本地探针、Kquery1；必须分账。当前没有四项实际归还完成的证明。建议由负责人选择继续保管，或接受明确损失后批准一次有边界的行政收尾；行政收尾不能改写为原任务正常返回。

本轮仅阅读已有文件、编制和发送本提案。没有设备查询、5037 查询、原会话轮询、诊断重跑、进程终止或后续测试。旧 N2 的 ABORT_ORIGINAL_N2 已另行结算，不属于本提案，不得重复执行。

下列“最后身份”均为历史截止点，不代表编制时仍存活。现有保管引用与实际可调用的清理入口分开记录：保留引用不等于可以安全关闭；没有 ACK 不得退回 UNKNOWN 预算。

## 1. 逐项身份、原对象及损失

### A. 旧主任务 E13C_MAIN_CASE_PENDING

- 原批次：`aeefe32f-816d-4c0b-aca7-16f76dbd45ff`；scope SHA-256：`116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef`。
- 原工具会话 `42537` 保留，禁止本轮轮询。主机最后独立身份切片为 2026-10-18 19:31:58.8847519：PowerShell PID 39560（父 52592，创建 16:48:05.005257）、Java PID 38056（父 39560，创建 16:48:05.688029）、ADB 客户端 PID 49540（父 38056，创建 16:48:05.953978），均为当日 UTC+08:00。
- PowerShell 可执行文件为 bundled runtime 的 `native/powershell/pwsh.exe`，参数指向原批次 `harness/run_original.ps1` 和 `inputs/case-01-request.json`。Java 为 `D:/Android/Android Studio/jbr/bin/java.exe`，类路径 `docs/coder/d1e13c/artifacts/e13c-host-tools.jar`，主类 `com.videokit.spike.e4.E13HostCase`，原 runtime-scope 路径、上述 scope SHA 及方法 `ordinarySenderCannotBindCodec`。ADB 为 `D:/Android/SDK/platform-tools/adb.exe`，完整参数指向 `-s HA1Q6WXR shell am instrument`、该测试方法及 `com.videokit.app.test/com.videokit.spike.e4.E13Instrumentation`。未来身份匹配必须使用原切片完整参数，不能只按名称或 PID。
- Android 最后历史切片约为主机 17:01：shell 14763 → am/app_process 14765，应用 14779；没有新的完整 Android 身份证明。不得用这些旧 PID 下达终止。
- 原对象：旧 PowerShell 仍持有原 .NET Process、stdout/stderr 读取任务和 MemoryStream；原 Java 保管器持有操作与 authority 对象，但 cleanup 为 null。可定位保管链，未提供经审计的主动清理入口；不能通过新 JAR、反射或重建句柄补成原对象关闭。
- 原 Java 的 androidReturned 依赖原 owner token；Android 或 ADB 死亡本身不能生成该 ACK。主入口已进入 pending 后，迟到输出也不能保证重新打印到终端。
- 已知不可追回部分：若原进程被终止，Java 私有原始输出/authority 状态及尚未落盘的 PowerShell MemoryStream 将丢失。具体字节数没有证明，不得填 0。当前没有原任务最终返回及完整 reader/pipe close ACK。

最小新确认：仅在另行批准执行后，一次主机身份快照核验上述三代进程的路径、完整参数、父链和创建时间，并在同一代验证后保留用于控制的句柄。Android 不能借旧 PID 收尾，需另行接受第 2 节的包级选择。明确停止手段：先处理经批准的 Android 包，再给原链一次有限自然退出机会；若原 Java 仍存在且同代核验通过，可执行一次外部终止。ADB 客户端、PowerShell 仅作为分别批准的条件后备项。外部终止结果必须标为 `TERMINATED_WITHOUT_RETURN`，不得替代原 owner ACK。

证据：`D1_E13G_CURRENT_STATE_EVIDENCE/host-identity-snapshot.json`（3047 B，SHA-256 `6c13732be473f3614a0489382cac3ea72082f205811d8cbd5a098db5ddbd3e22`）、同目录 `host-identity-independent-audit.json`、`D1_E13G_CURRENT_STATE_AND_DISPOSITION_PROPOSAL_V1.0.md`。

### B. 旧 LOST 诊断 E13C_PS_DIAGNOSTIC_LOST

- 最后可追溯事件：2026-10-18 约 17:01:39 的一次只读 ps 诊断。已落盘 stdout 58908 B，SHA-256 `4f96c93f1b4d68782a8a3e64e54eeda675d54edadb9177ead277762f526debc4`。
- 保存空 stderr 时出现 `WriteAllBytes(null)`，早于最终 receipt/显式关闭记录；不能从该异常推定 exit、reader 或 pipe 已归还。
- 未保存原诊断 PID、创建时间、可复用工具会话；原 .NET Process/reader/pipe 对象已不可访问。17:06:26.574 的一次记录修复检查没有匹配项，只支持当次检查结果，不是原对象归还证明。
- 已知损失：原控制对象和原关闭链无法追回；stderr 字节数、原 exit 和 reader close 状态保持 UNKNOWN。已落盘 stdout 可保留，不补造 stderr 空文件或返回码。

最小新确认：本轮无需新查询；负责人确认接受证据链损失即可选择行政隔离。以后即便一次主机快照发现疑似项，没有可核验的原代身份也不得据此终止。明确停止手段：当前无可安全指定的原对象停止入口；本提案只允许将其记为 `ADMINISTRATIVELY_QUARANTINED_UNKNOWN`、`originalReturn=false`，保留 UNKNOWN 和预算，不宣称进程已停止。找不到匹配进程不能补回原 ACK。

证据：原批次 `pending-observation/01-processes-stdout.txt`、`pending-observation/record-repair-owner-check.json`，状态 `LOST_DIAGNOSTIC_OWNER_UNKNOWN`。

### C. H30384 本地探针

- 记录 ID：`E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN`。历史 Java PID 30384，创建时间、临时端口、当前存活状态均未记录。
- 冻结参数：`D:/Android/Android Studio/jbr/bin/java.exe`；类路径由 `docs/coder/d1e13h/.checks/host-001` 与 `docs/coder/d1e13h/artifacts/e13f-reviewed-base.jar` 组成；主类 `com.videokit.spike.e4.HCheck`，参数 `VERSION_OK` 与 `docs/coder/d1e13h/evidence/host-001/VERSION_OK`。
- 父 Python 等待 15 秒超时后记录 pending；原 exit/reader close 无 ACK。冻结 stdout/stderr 各 0 B 不证明归还。“jcmd no such process”只有开发交接陈述，没有独立原始输出，不能据此认定结束。
- 若原 JVM 尚在，可能持有临时 ServerSocket、peer、Version socket、reader/custodian；若已退出，原内存对象不可追回。当前没有可调用的原控制句柄。静态 peer.join 假设尚未唯一确认为实际原因。后续同字节探针通过不能回补这一次。

最小新确认：如日后选择定向停止，只可在一次获批的主机身份快照中重新识别完整路径/参数/父链及当前创建时间，并取得明确属于本项目该探针的归属证据；这只能建立当前行政控制身份，不能证明原 30384 的代际连续性。仅 PID 30384 或相同类名不够。明确停止手段：归属证据不足则不终止，行政隔离为 UNKNOWN；若归属充分且负责人单独选中该当前实例，才可另行批准一次外部停止。本轮不将 H 加入默认停止清单。

证据：`D1_E13H_REVIEW_EVIDENCE/local-probe-unresolved.json`、`D1_E13H_READONLY_ENTRY_REVIEW_REPORT_V1.0.md`。

### D. Kquery1 新增保管项

- 新批次 `d7b4ca4f-36a3-49c9-9b61-cdc7ebdcb5b6`；原 scope 仍为 A 的批次。原工具会话 `49433` 保留，不轮询。
- 新 Java PID 51664，创建时间 `2026-10-18T13:48:53.1610574Z`。PowerShell PID 未记录，不得臆填。启动入口为 `docs/coder/d1e13k/release/launch_once.ps1`，Java 主类 `com.videokit.spike.e4.E13JReadOnly --g-readonly`，类路径 `docs/coder/d1e13k/artifacts/e13k-host-tools.jar`，release 路径 `docs/coder/d1e13k/release/read-only-release.json`，release SHA-256 `a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03`。
- 21:53:05.818525 的已落盘审计截止点：仅第 1 次查询进入，第 2 次 NOT_RUN；wire 70656 B（in 70367、tx 289），10 frames，rawQuota 64868；`budgetUnknown=true`、`readerAlive=false`、`eof=false`、`exitSeen=false`、`socketReturned=false`、`physical=false`、`auditOwnClose=UNPROVEN`，失败原因 `I_FRAME_LENGTH_OR_RAW_CAP`。T 片段的 writerAlive=true 是当时快照，不代表现在存活。
- 原 Socket/操作由新 Java 原保管链持有，未失去 owner；但没有经审计的主动清理入口。现实现预算耗尽后停止读取，budgetUnknown 为粘滞状态，reader finally 跳过 Socket.close，keeper 也不能宣告 physicalReturned。因此远端 FIN/EOF 到达本身不能使本地继续读取或自动解除保管。不得提出扩大预算、换过滤条件、新 reader 或重试来“自然收尾”。
- 已知落盘 wire 的 SHA-256 为 `4db90cf3bbe16197f22fdaeb1b873ef8b241d04ab1efee788c6f692fc1a350cb`。没有最终 process receipt/launch summary。截点 stdout/stderr 为空不证明管道结束，T 落盘也不证明 writer 关闭。
- 已知潜在终止损失：Java 未归还 Socket/keeper 状态与外层尚未落盘的输出/reader 状态。已经捕获的 wire 不抹除；不为追回未知内容另开查询。

最小新确认：与 A 共用一次获批主机身份快照，核验 Java 51664 创建时间、完整命令、路径和父链；同次识别其原 launcher，创建时间必须实际采得。明确停止手段：验证同代后一次外部终止该 Java，随后只给原 launcher 一次有限自然退出机会。若 launcher 不退出，仅可在同次已识别且单独选中的情况下停止。外部 OS 退出不等于原 Java Socket/reader close ACK。

预算保留：基础 116736 + 已进入查询 72704 = 189440；上限 262144。未进入第二次的 72704 不借用；原 exec 的 65536 额度未使用，不能据此开展原会话读取。未知不退款，不把新 K 项并入三个历史项后冲销。

证据：`D1_E13K_REVIEW_EVIDENCE/execution-checkpoint/actual-execution-audit.json`、`source-file-cutoff-index.json`、`D1_E13K_G_SUPPLEMENT_EXECUTION_REPORT_V1.0.md`（SHA-256 `e6f579ee906fff5d1883a67d2c1b27ca2aef0a26a76401d56d8e6a0192200a4e`）。活动产物根目录 `D1_E13J_R1_G_SUPPLEMENT_EVIDENCE` 不在本轮追加读取或封存；once 标记不重置。

## 2. 供负责人决策的一次性收尾边界

以下是待选择的执行边界，尚未实施；不是追加诊断方案或工具开发需求。

1. 先确认选择范围与可接受损失。A/K 是仍有原保管链的对象；B/H 缺少安全原代身份，默认只行政隔离，不据历史 PID 停止。已落盘证据保留；不为补齐内存缓冲而追加抓取。
2. 若批准行政收尾，仅做一次主机身份确认，覆盖获选的 A/K 角色。核验完整路径、参数、创建时间、父链，并保留同代控制句柄供条件操作使用；不得稍后凭裸 PID 重新寻找或重试。这些新行政句柄不是原协议对象的返回证明。无法核验的角色跳过并保持 UNKNOWN。
3. 获选 K Java 可一次外部停止；原 launcher 仅一次、最长 10 秒的退出等待。若有严格输出字节上限，可收集此次退出结果；不能保证上限则不轮询工具会话、不读取原管道。超时不自动加预算。
4. A 的 Android 收尾需单独接受包级影响：确认设备 HA1Q6WXR、user 0、包 `com.videokit.app` 当前归本项目占用后，可通过系统应用设置执行一次“强行停止”。它会中断该用户下该包的所有任务，不能表述为仅终止旧 instrumentation。若占用归属无法确认、影响其他工作或实际目标包不符，停止此分支；不自动扩展到测试 APK、fixture 或其他包。包级停止也不证明原 reader/socket 已归还。
5. A 原链仅一次、最长 10 秒自然退出机会；原 Java 若仍在且核验同代，可按批准执行一次外部停止。原 ADB 客户端、原 PowerShell 与 K launcher 是分别选中的条件后备项，每角色最多一次；不得用进程树全杀代替逐项身份核验。此选择最多覆盖 5 个主机角色（K Java/launcher、A Java/ADB 客户端/PowerShell）和 1 个 Android 包；未选角色不得动。H 不计入默认清单。
6. 收尾结果逐项记为原返回已证明、外部停止无原返回、身份不足未停止或行政隔离 UNKNOWN。OS 终止/句柄释放只能证明相应层，不能写成内部 Socket、reader、Android owner 的 ACK。没有原 ACK 的账目继续保留 UNKNOWN、不退款。输出一次收尾报告后停止，不发起下一轮检查。

共享资源排除：主机 ADB server 与 5037 监听者、设备 adbd/system_server、无关 Java/PowerShell、其他项目/序列号、conhost/控制台均不属于停止目标。不执行 kill-server、重启/root、泛化 app_process 清理或通配进程树终止。已有 fence/once/历史账本和原 pending 不改造为成功；行政结论另立记录，原始材料保留。

## 3. 必要的人为风险选择

| 选择 | 接受内容 | 结果边界 |
| --- | --- | --- |
| 继续保管 | 不采取外部停止，接受任务持续占用及验证仍受阻 | 四项实际归还仍未证明；不能预计 K 自动清空 |
| 选择性行政收尾 | 明确选中 A、K 或其子集；接受所选进程内未落盘信息损失，A 包级停止的全部同包任务影响，以及 B/H 的证据链损失 | 按第 2 节仅一次确认/条件操作；未知继续挂账，不能回填原成功或自动开始测试 |

负责人应将所选角色、Android 包级影响、条件后备角色和不可恢复损失一起交由用户决定。当前委托仅允许离线提案并明确禁止终止；此前平板测试的持续授权不能替代本次不可恢复收尾的范围选择。可用决定格式：“选择行政收尾；批准对象为……；允许的后备角色为……；接受所列缓冲损失/包级影响；B/H 维持行政隔离 UNKNOWN；完成报告后停止。”也可以只选择 K、暂不处理 A。

无论选择哪项，都不把行政隔离当作物理资源全部归还。是否解除阻塞由负责人独立复核；继续测试需另行明确安排。本轮不重新冻结全部历史、不开发工具、不启动测试。

## 4. 交付与核对

本提案四项一一对应，未增加诊断实例；没有以新 K 的保管替代旧三项，也没有将 UNKNOWN 清零。引用路径均相对本文件所在的 `D:/CodexProjects/VideoKit/docs/tester`，开发路径从项目根解析。发送前计算本文件 SHA-256；发送回执另存，不回写已发送报告。
