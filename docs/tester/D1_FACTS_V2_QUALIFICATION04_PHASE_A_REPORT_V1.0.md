# QUALIFICATION04 阶段 A：冻结 03 生产接线静态审查报告 V1.0

2026-10-24。结论：**STATIC_REVIEW_COMPLETE_WITH_BLOCKERS_AND_OBLIGATIONS**。阶段 A 静态工作完成；不签功能通过、不关闭 B02-01/B02-02。03 的固定 helper 阻断保持，生产 identity/global 与原 PS 预算实际验证仍未执行。04 浮动源码未读取，阶段 B 未启动。D1 未通过、M0 未启动。

## 1. 来源、范围和可复核产物

正式测试单 `docs/tester/D1_FACTS_V2_QUALIFICATION04_TESTER_REQUIREMENTS_V1.0.md`，SHA256 `82f4869f5d783bad35d32dd99966ce2d36113948119666c47d7a3ea31d82c797`。工作前读取三协调文档顶部；03/04 开发要求仅作为范围和契约文档读取，不审 04 候选源码。

唯一代码来源为 `docs/coder/d1android02-facts-v2-qualification03`。开发失败报告 SHA256 `dc9062532f9334b883dd38b309a86db76c455dd0e968995bfd498fefa990b7f4`；manifest `882263c06b5e9db6c23aa04165d535f8077e376cf53979e1ee79c89eb9837c33`。独立逐项静态核 **101 文件/4110981 B，bad=0**；冻结 ZIP **102 个唯一成员**逐内容/大小/hash 核验一致。完整 ZIP 摘要见 `source-audit.json`。source31 `323ff1c0b2d650f2971d8968bed9b32fbdf51ba214759d1b2a7c486e25f7ed99`，gate23 `e93a894c4518133b7944332f006713b34e7c20a56e9c283874b28766e864aa92`。

新产物仅在 `D:/CodexProjects/VideoKit/docs/tester/D1_FACTS_V2_QUALIFICATION04_PHASE_A_EVIDENCE`（下称 R）及本报告。主要证据：

- `source-audit.json`、`constants-audit.json`、`contract-extra.json`：准确字节、31 源/23 gate、54 profile pins、固定常量与运行时文件静态核对。
- `call-anchors.json`、`budget-path.json`：原函数和行号、实际调用顺序与重复读取预留推导。
- `static-findings.json`：五项静态发现/义务及补充判据 O12。
- `oracle-and-blockers.json`：62 项完整分层判据，均为 PLANNED_NOT_RUN；加 O12 共 **63 项**。
- `frozen03-original-status.json`：仅从冻结原件读取的历史结果，不是本阶段执行。
- `delivery-manifest.json`、`delivery-freeze.json`：本阶段最终文件清单和摘要。

仅使用文件字节、JSON 和 AST 分析：没有 import/dot-source 产品模块，没有调用 SourceBudget、Gate、Runner、Owner、RoleSemantic 或 PS 函数；**产品 Popen/Gate/claim/once/动态/SDK/ADB/设备/Native route/TCP/Gradle/媒体/Git 均 0**。原 once、预算、FAIL、UNKNOWN 和旧证据未写。

## 2. 原生产接线的静态可达顺序

| 顺序 | 冻结 03 中的实际接线 | 静态判断与尚未执行部分 |
| --- | --- | --- |
| 1 | 原 facts preauth 验输入/来源，登记 USED，再进入 PreparedFacts.prepare / Gate 构造 | 03 helper 检查在 claim/route 前拒绝；USED 不能退回或按纯准备重跑 |
| 2 | 若后续新批 facts 成功，原 Capture 全返回→FactsBundle→未批准候选→独立有限 OFFLINE reviewer→wire | 03 本链未到；不能挪用 02 成功当 03 实际事实 |
| 3 | ProductionRunner 验 permit/approval/31 源/准确 scope；prepare_home→原目标 Gate→materialize policy/activation | facts scope 与未来目标 scope 分开；不能把两次 Gate 计数拼成一个原对象 |
| 4 | Owner 构造核原 Runner、runtime、policy/plan；原 Gate.receive 将 sdk_owner 设为本 Owner；Runner.consume 接收 | Runner.run 的 Owner 构造返回后才把 runner.owner 赋为该对象；之后 run_one 才建 SourceBudget，不把 RHS 构造中尚未赋值误判成坏接线 |
| 5 | run_one 创建 SourceBudget 一次→Gate.before_role→Runner.before_role→runtime→请求原写返回→reserve→admission 原写返回 | reserve 在 Popen 前永久计入同一 Gate/Runner。请求可能已写而 reserve 拒绝，不能称“完全无 IO”，只能称“未新增控制器” |
| 6 | runtime 再核→Gate.before_role→Runner.before_role（另读 permit/approval/entry）→唯一原 PS Popen | 后三次来源读取必须计入；不能把 reservation 快照当作之后 Runner 不再变化 |
| 7 | 原 PS 顶层验 request/policy/activation/owner admission→InitializeGIV2SourceBudget→初始 Gate/Runner 或前驱原 proof/receipt/outer/raw 验证 | 初始化发生在前驱语义之前，故前驱 identity/global 解引用确实使用本控制器 ticket |
| 8 | 前驱 RoleSemantic→本轮原 .NET 捕获/等待/EOF/流及输入归还→本轮 RoleSemantic→receipt/console | 前驱失败可在新 .NET 子进程前抛出；此时不保证有正常 console/delta，不得伪造 merge 成功 |
| 9 | 原 Owner wait/readers/原流/H/console 写入返回→解析原 console→SourceBudget.merge→已知失败/后继 proof | merge 处理来源记账不等于功能验收；失败时完整预留不退款。没有 console 时 pending 仍应保留，不强行造 delta |
| 10 | 成功 prefix 两角色或默认七角色→原 terminal writer/同 proof 时窗→原 claim release | 当前 03 均未实测；prefix 完成也不代表全部七角色或 D1 |

对应源：`production_runner.py:243–295`、`outer_owner.py:101–199`、`capture_android02.ps1:192–240/395/410`、`source_budget.py:3–39`；准确单行锚点在 R/call-anchors.json。

## 3. 重复读取、预算归属与永久预留

记固定 body 原字节为 n（1..8388608），事实 packet 原字节为 m（至多 262144）。每次 GIV2LoadReference 读 body 一次、packet 一次，仍校固定路径、非链接、单硬链接、volume/fileId、大小/hash、前后原句柄身份和原 close。review/candidate/bundle/outer/preauth/policy/窄政策文本在 body 内解码，本函数不把它们再逐个开文件。

| 控制器角色 | 前驱/当前导致的资格解引用 | 预留读取次数 | 父原预留字节 |
| --- | --- | ---: | --- |
| identity | 当前 identity 1 组 | 2 | n+262144 |
| global_idle | 前驱 identity + 当前 global 共 2 组 | 4 | 2×(n+262144) |
| app_absence | 前驱 global 1 组；当前 app 不读资格 | 2 | n+262144 |
| 后四角色 | 没有 identity/global 前驱或当前 | 0 | 0 |

所以 OFFLINE prefix2 是 **3 组/6 次**；完整七角色是 **4 组/8 次**。body 达 8 MiB 时分别永久预留 **25952256 B / 34603008 B**。实际使用是相应组数×(n+m)，小于预留的余量也不退款。该推导是静态算术和调用图，未实际读取生产文件或证明真实当前 scope 额度足够。

原目标 Gate 上限仍为 268435456 B/64 次，原 Runner 为 536870912 B/256 次；reserve 同时向两者保守计费。facts 的原 Gate 独立存在，不能用“未来目标预算”抹掉 facts 已用额度；全批读取还受外层 1 GiB 限制。既有 runtime/helper/source-integrity 读取与新资格引用要逐项归属，不把解释器/OS 隐式 IO 或 console 数字等同于完整原账本。

在原 Parent：构造检查实际类型及双向 owner 联系，Gate 只绑定一次；reserve 要求原 holder/pid/thread、顺序、无 pending，并检查 Gate unknown reserve 与两层额度。ticket 含准确 scope/generation/owner/thread/role/ticketId/version/baseGate/baseRunner/reserved。父预留永久增加四个原计数，version 递增，pending 等待原 delta。

在原 PS：没有 authority 就不能读取；ticket 精确字段，scope/role/owner/generation 与 admission 绑定，数值类型/上限检查；global 原对象保存 ticket/used/reads/events，模块复载不重新创建它，重复初始化拒绝。每次真正 open 前 ReserveGIV2Reference 先占字节/次数；hash 失败仍计实际读，身份失败占次/全额子预留，短读保留全额并在 finally 原 close；read/close 真 UNKNOWN 保留原对象并停止前进，阶段 A 不人为制造挂死。

在 Parent merge：精确 delta 字段、ticket/scope/version/generation/owner/role、Gate 快照和计数/事件合计受检，只清 pending，不退最初永久 charge。Runner 在 reserve 后有合法的新来源读取，因此不能粗暴要求 Runner 最终值恰好等于 base+reference reserve；应保留这些额外成本并检查原权威/最终边界。merge 的类型与权威不足见 A04-03。

## 4. 集中静态发现与必要义务

### A04-01：固定 helper 字节阻断，独立静态确认

03 runtime_binding.py 实际 **2036 B、0 个 CRLF**，SHA256 `1c0682fa7409fffdbdeed293c7b7766d49a1db6f8080cc06d8a64ab43236aa14`；02 原固定文件 **2056 B、20 个 CRLF**，SHA256 `47f9d48af2d3106c6b04f67e079bd6b48b3befb4b0c25061f3a6508426e3c982`。独立字节比较确认只做 CRLF→LF 就得到 03 文件。build03 的全源 read_text/write_text 派生破坏固定字节，Gate 仍要求原 47f9。

这是已知 03 原失败的静态复核，不是本阶段又执行一次 GATE_RUNTIME_HELPER。不得通过改 Gate 期望摘要、全局换行标准化或重放 USED scope 绕过；04 开发单已要求恢复原 bytes，阶段 A 不判断其是否已修。

### A04-02：临界额度下，预留后的既有 Runner 复读仍是读后检查

Owner reserve 后还调用 Runner.before_role，后者读 permit、approval、entry。Runner.read_file 的顺序为原 open/read/close→累计→检查预算，没有在该次物理读之前检查余量。

条件边界模型：若合法 baseRunnerReads=254，identity 预留 2 次后计数到 256；下一次 integrity 读先发生，再加到 257 后才抛 RUNNER_SOURCE_BUDGET。字节恰到 512 MiB 同理。**本阶段没有执行超读，也没有证明本固定七角色图能实际达到 254 次/该字节边界**；因此将其列为 P2 条件契约风险，不能报成当前正常路径必现或实际超额。

需要补完整可达图及合法来源大小的总量证明（包括 reserve 后三次复读），证明永远有余量，或在原预算内补读前准入。保持原门，不增加数值上限，不把同一原 Runner 的额外成本丢失。补充判据 O12 与主矩阵合计 63 项，不能通过真实改旧计数或重置账本试验。

### A04-03：merge 的受控类型与原权威复核有静态缺口

merge 未重复 reserve 中的原 holder/thread、Gate.sdk_owner/Runner.owner/qualification_budget 原联系检查；只核 Gate 数值快照，没有明确核原 Runner 的同一性及合法新增成本后的最终界。当前原调用点按顺序持有原对象，**不据此声称存在外部越权实测**，但需说明是由哪一层保证这些义务，并在必要处最小补检。

event 循环直接 set(e)/下标访问，未先要求每项是 dict；非 dict 可以走 TypeError。path/opened 类型没有明确检查；opened=false 可以表示原 open 根本未成功，不应伪称发生过 close，但仍必须是准确布尔值，不能任意异型。现有 PS 正常生成的事件形状不等于所有坏 delta 都会稳定受控拒绝。

需按 D06/D09 明确受控拒绝原因，缺/异型计数及事件不能靠 KeyError/TypeError 算 gate 通过；拒绝后原永久预留/pending 保持。可信同进程任意私有内存修改不作为本项目要抵御的外部攻击。

### A04-04：OFFLINE prefix 参数类型边缘遗漏

`fixture_prefix!=2` 在 Python 中会接受 float 2.0，然后在 prepare/materialize/consumed=True 之后的 range(fixture_prefix) 才发生 TypeError。固定实际调用者传 int 2；这不是已观察到执行额外角色，而是固定 API 边界可在纯准备前补齐的精确类型义务。True/其他值与 LIVE prefix 已被当前条件拒绝。建议 int2 在进入产品 once 前准确检查。

### A04-05：新增 delta 必须先证明适配原固定 console/admission 大小

新 delta 最多带四个完整路径事件，现有 console 仍限 **8192 B**，超限分支为保留等待；admission 原声明限制 **4096 B**、读取上限 **8192 B**。03 未产生生产 console，因此本阶段**没有证明实际超限**，也不能拿静态“字段多”当必现缺陷。

在唯一实际调用前，应纯序列化完整 Snapshot+delta+最长合法路径/计数，核实际 UTF-8 与 console/admission 及控制转发限额。不能只量 delta，也不能以字符数代字节；不得提高原 cap，不故意向真实控制器喂超限输入触发永久等待。见 I13。

## 5. identity、prefix 和固定契约核对

03 identity 保持原 framing/model/API/user/ABI 判据，V2 经 GIQualification→GIV2LoadReference→原引用身份/原字节→外批及窄政策/目标/鲜度/展开校验后才比 fingerprint，没有给 wire 加裸值。global_idle 仍走原 Get-GlobalIdleDecision；其前驱原 identity 在 global 控制器再次解引用。这是正确的静态接线方向，**03 未实际跑到，不能因此关闭 B02-01**。

同一份事实 collectedAt 及外批 expires 在每次当前/前驱校验继续使用，不可刷新 300 秒；过期或前驱失败停止后继。OFFLINE prefix2 只运行 identity/global，terminal 标识 OFFLINE_PREFIX_IDENTITY_GLOBAL_ONLY；LIVE 有 prefix 则拒绝，默认完整七角色路径保留。前两 fixture 角色改用原 plan 既有 15 秒，后五仍 2 秒；原生产 Gate30/共享 proof10/outer120/whole600 未改。前驱与引用同步 IO、最终语义/receipt/console 仍须在原观察时窗计入，不能靠时间重置或扩大门取得通过。

本轮独立核的 10 组明确固定常量中，helper 不匹配，其余匹配：runtime metadata、Runner/Owner/admission、adapter/Capture/origin/collector、固定 producer。metadata 摘要 `2593ddab8ed0a7cee369c13a145817c4365ce1847f18e0d7167db453060e5d48` 及其列出的 **14 个依赖文件**只做字节/hash 核对一致；未调用 require_runtime，也未动态断言运行时版本。Python AST 可解析，7 份 PS AST 无语法错误；均非产品执行。

Runner SOURCE_FILES、PS srcKeys 与冻结 seal 的 31 个路径集合逐项一致；gate23、54 profile pins 全部与冻结文件一致。reference 模块与 admission 中内联副本字节一致。另给出 tools 内 **33 处 64hex 字面量**及源行，区分 source pin、SDK pin、枚举契约和 proof hash，不能把所有 hash 当文件摘要统一替换。未来新04路径、根、常量、scope 公式、实际 caller 与 profile 必须重新完整核，不能用03自身 manifest 自洽代替固定继承义务。

## 6. 完整 oracle 和后续阻断顺序

R/oracle-and-blockers.json 的 62 项按六层分组：固定纯契约 8、原 Parent 权威 11、PS ticket/复载 9、固定原文件 9、原返回与 merge 11、完整入口与固定边界 14；另 A04-02 的 O12 为第 63 项。**全部动态状态 PLANNED_NOT_RUN**，列出的原 03 原因仅为后续精确 oracle 依据，不冒本轮实际触发。

后续顺序应为：固定 helper bytes/运行时与完整常量预检→新正式 scope 的最大 facts 原返回→独立有限 OFFLINE reviewer→原 Runner/Owner/PS 完整顶层合法 identity-global 串行→错固件无后继→原权威预留/delta 并回、模块复载/失败/临界图与原 close→受影响回归。不得用 AST 提取代完整入口，不重跑旧 USED，不以合成批准代真人，不用 prefix 代全七角色。

确定阻断是冻结03 helper 不满足固定 bytes。其后真实生产链及预算实测均未到达；A04-02/03/04 需集中审定修复或给出准确的可达/权威证明，A04-05 先纯大小证明；阶段 A 不打开任何真实故障注入窗口。04 完整自测冻结且负责人核包正式派 B 之前，tester 不自动执行任何后续测试。

本报告及全部新静态产物整批发负责人，由负责人集中转 coder。未直接逐问题交接；旧证据/once/预算/FAIL/UNKNOWN 保持。本阶段没有新增产品原资源或 pending，亦没有新增产品 UNKNOWN。
