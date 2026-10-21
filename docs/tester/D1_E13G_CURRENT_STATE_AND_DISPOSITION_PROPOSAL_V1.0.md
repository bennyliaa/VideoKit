# D1 E13G 当前状态与原任务收尾待审方案 V1.0

2026-10-18；tester。正式需求及本派单预算已在任何fresh核查前保存。

**结论：取得一次fresh本机原身份；设备现状与原会话读取BLOCKED/NOT_RUN。** 19:31:58的准确本机切片确认原PowerShell39560→Java38056→ADB49540均真实存在，创建时间、路径、父子和完整argv与原记录完全一致。本轮没有原资源自然归还、Android终态或内核结果证据。旧主case继续PENDING/UNKNOWN；失败诊断独立LOST_DIAGNOSTIC_OWNER_UNKNOWN。

本轮原exec42537空读0次、ADB0次、STATUS/Binder连接0、处置/kill/force-stop/SIGQUIT/外部finish/部署/安装/重测0。未读live ledger、大媒体、内存或其他设备；没有查询后再重试。已知可用正式设备授权保持，以下BLOCKED来自本批具体保管入口及响应边界，不是缺少设备使用授权。

## 1. 派单与预算

需求：`docs/milestones/D1_E13G_TESTER_REQUIREMENTS_V1.0.md`；保存的派单及预算：`docs/tester/D1_E13G_CURRENT_STATE_EVIDENCE/authority-and-budget.json`。原scope `aeefe32f-816d-4c0b-aca7-16f76dbd45ff`，runtime SHA256 `116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef`，serial HA1Q6WXR。

| 操作 | 本批上限 | 本次实际 |
| --- | --- | --- |
| 原exec42537空输入只读 | 最多1次，响应≤1秒 | 0；≤1秒接口保证未成立，不试探 |
| 本机相关进程完整身份 | 1次，≤64KiB | 1次；0.749秒，完整相关身份3047B |
| 串行直ADB只读 | 最多2条；各≤64KiB/10秒资格 | 0；没有已审且可直接用于本批的原owner入口 |
| 总原输出 | ≤256KiB | 本机payload3047B；连同父工具重复console/回执保守预留8192B，未声称逐字节完整父console结算 |

本批预算与旧41/55等分栏，未继承旧余额；未发ADB不计实际消耗，也不将未消费额度转供处置或其他测试。没有在途新诊断client，不新增第二个未知诊断对象。

## 2. Fresh本机身份事实

原生本机CIM只采一次全局切片，在内存中选取原scope/原runtime SHA、历史PID提示及其直接子对象、该serial的ADB client；只落相关完整路径/启动时间/父子/argv，不输出其他项目命令行。历史PID只用于选择候选，随后逐字段核原身份，没有凭数字单独认领。

准确切片时间：**2026-10-18 19:31:58.8847519（UTC11:31:58.8847519）**。

| 对象 | fresh PID / parent | 创建时间 | 准确路径与命令角色 |
| --- | --- | --- | --- |
| 原工具宿主 | 39560 / 52592 | 16:48:05.005257 | Codex runtime native powershell/pwsh.exe；执行原批run_original.ps1及原case-01-request.json |
| 原Java | 38056 / 39560 | 16:48:05.688029 | D:/Android/Android Studio/jbr/bin/java.exe；原E13C JAR、E13HostCase、准确runtime路径/SHA、ordinarySenderCannotBindCodec |
| 原instrument客户端 | 49540 / 38056 | 16:48:05.953978 | D:/Android/SDK/platform-tools/adb.exe；-s HA1Q6WXR、am instrument -w -r、准确类/方法/e13Batch/e13ScopeSha256及原E13Instrumentation |
| 控制台辅助对象 | 25244 / 39560；29948 / 38056；44928 / 49540 | 各自记录于完整raw | conhost.exe；仅身份记录，未将其列作自动清理目标 |

三主对象的ParentProcessId、CreationDate、ExecutablePath、CommandLine与原冻结身份逐字段相同，未见PID复用。完整原raw保存 `host-identity-snapshot.json`，SHA256 `6c13732be473f3614a0489382cac3ea72082f205811d8cbd5a098db5ddbd3e22`；独立比较见 `host-identity-independent-audit.json`。

“仍存在”只在该时间切片有效，不代表对象健康、Android已到哪一步、reader任务状态或将来仍活。未读原buffer、未连接custodian STATUS、未读取原exec，本轮不能断言原pipe是否已有增量、是否EOF或有何逻辑closeACK。原宿主/原Java真实存在支持继续原保管，不构成归还证明。

## 3. 两项未启动的明确原因

### 3.1 原exec空读的≤1秒响应尚不可保证

当前工具网关的空读在此前请求yield_time_ms=1000时曾实际等待约5秒。本批明确上限≤1秒，没有已确认的非阻塞/≤1秒网关契约；本轮未再发一次空读以探测其最小等待，也未用超时取消、并行Promise或丢弃返回来伪装1秒完成。该项记NOT_RUN_RESPONSE_BOUND_UNPROVEN；不推断session失踪、EOF或原owner丢失。

需先明确一次可保证该响应资格的原session读取方式，或由负责人正式调整这一次收取的等待预算。不能借此循环轮询、重建会话或发送Ctrl-C/非空输入。

### 3.2 已审owner存在，但缺本批直ADB受审入口

E13F已审 `tools/observe_original.ps1:8–10`只接受固定Java可执行文件及E13HostCase/E13HostActivationSession两个生产角色，文本cap仅32768/81920。两角色都会走产品case/deploy，本批明确禁止。`E9PcSupervisor`确有安全原Process/唯一reader归档机制，但作为库API需一个新的调用适配入口，当前交付CLI没有准确G只读模式。E9HostManager是被禁用的PREPARE manager，E9PcClient仅STATUS/OP/CLEANUP；均不适用。

本轮未删除观察器角色门、未换参数绕过，未启动产品入口来获取只读结果，也未临时另造未审Process包装器。按正式需求“无可用保管方式不启动，记BLOCKED”，两个ADB均在启动前阻断。预检来源hash及准确门行保存在 `safe-entry-preflight.json`；E13F冻结字节未改。

最小补齐不是新生命周期框架：将已审原Process/readers/文件keeper代码保持不变，单独审一个G专用直ADB入口或最小角色适配，固定exe+HA1Q6WXR+两条准确只读argv、64KiB/10秒资格、总256KiB及本批唯一intent；记录错误和超资格时同一宿主保原对象，不抛弃局部owner/二reader/强关。先审实际入口、差异、空输出/记录失败保管和超资格停止，再派这两条调用；当前不执行。

## 4. 各层状态分栏

| 层 | 本轮fresh证据 | 当前可登记状态 |
| --- | --- | --- |
| 原PowerShell/Java/ADB身份 | 三者真实存在且完整身份与原记录相同 | LIVE_AT_SNAPSHOT；原任务仍在途，未证明自然归还 |
| 原exec42537及其stdout/stderr/readers/pipe | 本轮0次收取，无内部状态观察 | UNKNOWN_CURRENT_RETURN_STATE；保原对象，不补EOF/close |
| Android instrumentation/应用/fixture/codec | 本轮ADB0；14763/14765/14779及17/fixture1/UID/data仅历史 | UNKNOWN_CURRENT_DEVICE_STATE；不得凭历史PID处置 |
| 内核拒绝、绑定阶段、runner完成门 | 无新增stage/终态raw | NOT_UNIQUELY_DETERMINED；不判kernel PASS/FAIL或确定死锁 |
| 其他项目设备占用 | 本轮未获全局active instrumentation | UNKNOWN，不能声明设备空闲；后续只读若发现占用则停止等待，不联系他们 |
| 失败ps诊断 | 原PID/局部owner不可恢复，无新证据 | 独立LOST_DIAGNOSTIC_OWNER_UNKNOWN；不补stderr0/exit/closeACK |
| 历史账本/产物 | 本轮未读live ledger/媒体 | 保历史切片，不把214483/7R7S或N2旧结算当当前E13C归还 |

## 5. 最小准确收尾方案——本轮不执行

本轮fresh证据只足够确定原PC对象身份，**不足以定稿任何Android终止动作**。当前能安全继续的是原隔离保管；不得用缺Android证据作为先结束宿主的理由。以下为负责人可审的最小单次动作及停止门，没有控制命令、没有处置执行授权。

### A. 自然归还路径

先解决原exec一次读取的响应资格，接收同原handle自然输出；有原实际回执才分别登记Android终态/原ADB exit/原reader/pipe/decoder/authority/custodian/外层宿主归还。迟到资料另出补充报告，不回写旧切片。旧E13C HostCase在55秒抛后不会再print内层raw，最多64KiB原instrument数据可能仍仅在旧Operation内存；不能保证自然退出会完整导出，不能attach/dump/新JVM认领。

若自然归还没有发生，维持PENDING，不自动重发、安装修复版、补finish或推进后五法/M3。

### B. 外部行政终止路径的前置与准确范围

1. **先补只读身份，不先终止。** 在G专用owner入口审定后，一条serial固定的直接只读采集取得完整global active instrumentation及完整相关进程列表/退出边界，另一条只读取第一份已确认、准确scope/包/UID/父子关系的PID启动身份；每条64KiB/10秒资格，不追加探针或把其他日志命令并入身份预算。若信息不足、输出不完整、调用未知或其他项目占用，停在UNKNOWN/BLOCKED，不发任何终止命令。
2. **Android动作须另定具体目标。** 只有fresh确认当前原scope的instrumentation/app及包级影响没有其他任务后，才能选择一个准确package/进程角色的一次外部终止。app候选范围为com.videokit.app，test为com.videokit.app.test；fixture com.videokit.e13.sender及codec是否有原owner在场须单独证实、单独决定。历史14763/14765/14779、UID10221/10228不得直接作为执行参数；本报告不把未知PID填0或假定fixture已结束。包级操作影响该包所有进程，必须明确接受范围。
3. **先让原ADB自然返。** 对Android动作的响应不当作Java ACK；保原ADB49540/pipe/Java继续自然返回。若它仍未返，是否单独外部结束这一准确ADB client要另列单次动作，并在执行时重新验证其16:48:05.953978创建时间、完整scope argv和父Java38056。共享ADB server、5037监听者、device adbd、system_server均不在范围。
4. **旧Java必要时单独处置。** 若原Android资源已终止但无原终态token，旧Java38056的androidReturned仍可能false，旧custodian无cleanup入口。若负责人接受外部行政终止，目标只能是执行时再次核准准确启动身份的原Java38056（路径/16:48:05.688029/parent39560/准确scope），一次动作；不能要求旧监督器伪写pcClosed或反射清零。Java退出后优先由同原PowerShell39560自然wait/read/close并保存原外层输出。
5. **PowerShell仅作最后独立选择。** 若该宿主仍未知/不返，是否外部结束原PS39560须另批一次动作并核16:48:05.005257/准确原请求路径。必须先保存能得到的原证据，明确原reader/MemoryStream/pipe不可恢复损失。三个conhost不加入笼统树清理，其他项目/宿主/共享服务一律排除。

不应把上述步骤打包成“清理所有VideoKit进程”。每一新动作只针对一个已审角色，前一步的真实结果决定下一步是否必要；未知结果不能自动升级范围或重试。外部终止记录为TERMINATED_WITHOUT_RETURN、originalJavaReturn=false、originalOwnerReturnUnproven=true，不合成原finish/kernel拒绝/closeACK，也不把本批产品改PASS。

### 提议预算及必须补齐的证据

未来处置批次须单独签发，**不使用本批未花的两个ADB余额**。建议先审两条只读，之后逐项选择每个必要角色最多一次外部动作；每动作响应资格10秒、原输出32KiB，无重试。Android角色若需超过单一范围须单独列数与总额；本报告尚无fresh设备身份，因此不预批动作总数或可执行argv。原session收取的工具响应预算也需先定稿，不能沿用无法保证的1秒。

证据包至少包括：处置批次/人类与负责人授权引用、fresh完整scope/启动身份、准确单次argv及作用范围、动作前已落盘raw/manifest及不可导出字节清单、每原客户端真实return/UNKNOWN、原PS/Java/ADB分层后果、原预算不退款规则、独立审查及行政处置记录。处置记录位于旧监督器之外；新APK/JAR不能反控旧v17。

潜在不可恢复损失：旧Java Operation内层原raw/decoder状态、原PS MemoryStream及原pipe/reader状态、未落盘stage/错误上下文。现在未读内存，不能写准确损失字节，也不能声称buffer为空。即使磁盘产物/进程消失，原Java逻辑归还仍未证。

## 6. 诊断LOST的独立行政隔离建议

原失败ps诊断没有准确PID或可恢复原.NET对象，无安全目标可“替它结束”；不为其重建Process或选新匹配PID。建议负责人另审ADMINISTRATIVELY_QUARANTINED_UNKNOWN记录，固定原58908B stdout、缺stderr/exit/close清单及原审证digest，originalReturn=false、未知资源/文本预留继续保留；不因主case将来结算抵消或退款。本轮只建议，不生成可放行的正式disposition pin。

原主任务处置记录、独立诊断隔离记录和fresh完整M1均审清后，才可考虑固定未来reviewed disposition源码SHA、重新复审精确主机候选、定稿v17/fixture1→19/3 metadata及独立单一T07。E13F当前pin ABSENT、actualScope/release/once null；离线PASS和51/53全六法草案不能放行部署。

## 7. 保全与提交

本轮只保存新目录 `D:/CodexProjects/VideoKit/docs/tester/D1_E13G_CURRENT_STATE_EVIDENCE`，历史报告/原manifest/live ledger/原宿主均未修改。一次fresh host身份及其独立历史连续性核验通过，设备和原session两项明确未执行，不将部分完成写成完整现状核查通过。

报告集中主动发送负责人；后续需要补齐具体受审入口及响应资格，再另行派发缺失只读核查或具体处置。当前原保管保持，不循环查询、不执行本文建议。D1 NOT_PASSED / M0 NOT_STARTED及P0/历史FAIL/UNKNOWN、许可门不变。
