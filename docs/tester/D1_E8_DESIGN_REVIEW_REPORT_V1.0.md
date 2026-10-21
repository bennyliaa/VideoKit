# D1 E8 独立设计评审报告 V1.0

日期：2026-10-18。Tester。依据 `docs/milestones/D1_E8_TESTER_REQUIREMENTS_V1.0.md`，评审完整冻结四文档、需求证据矩阵和已有元数据。已从负责人窗口实际 userMessage 核实“请继续推进项目”，覆盖文件末尾旧暂停；不修改旧冻结状态或将其当成迁移执行许可。

## 结论与推荐

**方向支持，合同需修订：1项P1、1项P2。当前E8不能直接作为迁移实现的最终验收基线，不准设备迁移。** 推荐保留“精确一次性旧V1终局验收＋每host当前安全整链路”的方案；集中补齐新迁移者的跨host归还/UNKNOWN判定合同和可执行回退策略，再冻结实现边界。可继续设计修订和实现准备，无需再次批准日常设备使用；本次不请求或生成迁移批准token。

原N2已完成的恢复事实有来源绑定支持，不需要补造其从未采集的kernel birth，也不应继续反复查同一有限exit历史。合作故障模型是合理选择，但不得扩大成对主动同UID/整套自洽回滚的安全承诺，原跨UID/Binder/隔离角色校验仍保留。

本批是设计评审：22组只是测试设计，生产/Android/模型/构建/迁移执行0、ADB0、媒体及导出件读取0。E6B-OBS-F01仍OPEN，原MP4仅限定实机PASS，AVI/能力/cancel未准入；D1 NOT_PASSED/M0 NOT_STARTED、其余P0/许可保持。

## 集中需改项

### E8-F01/P1：新迁移者的持久提交与实际归还之间缺少可核验接续合同

定位：[迁移计划第17行](D:/CodexProjects/VideoKit/docs/coder/D1_E8_LEGACY_MIGRATION_PLAN_V1.0.md:17)、[两文件合同第19行](D:/CodexProjects/VideoKit/docs/coder/D1_E8_LEGACY_MIGRATION_PLAN_V1.0.md:19)、[实施阶段第31行](D:/CodexProjects/VideoKit/docs/coder/D1_E8_LEGACY_MIGRATION_PLAN_V1.0.md:31)、[部分提交第36行](D:/CodexProjects/VideoKit/docs/coder/D1_E8_LEGACY_MIGRATION_PLAN_V1.0.md:36)。

设计正确要求“最后guard close UNKNOWN仍阻断”“commit存在不证明迁移完成”，但固定验收payload/两个policy文件当前只明确旧task、旧attempt、归档/账本与批准绑定。尚未规定**本次新迁移actor**在首次写入前的不可混淆身份、受管handle/操作序号、由谁保存其在途状态，以及下个host从哪个可信、精确绑定的来源确认其已实际归还或仍UNKNOWN。

概念性反例：acceptance/commit字节已经相同且完整，迁移者释放最后guard锁后原close卡住或返回UNKNOWN。另一个host可能已经能取得同一锁、读到同一合法commit。设计虽声明要核“当前迁移owner状态”，却没有给出跨host可观测的owner索引/完成证据消费规则；“锁可得”和“commit已提交”均不能区分此状态与原owner已真实归还。此处是未实现合同缺口，不是已执行的漏洞复现，也不是指控设计已经允许绕过。

需要在实现基线前明确：

- 新迁移actor的预留身份和状态authority，至少精确绑定受管handle/attempt、任务/policy/descriptor、真实进程/参与者和操作序号；新actor可事前采样，不能以旧V1缺birth为理由省略。可以采用外部受管注册/回执或经审定的元数据方案，不强制另造硬件防回滚根。
- 一份跨host状态判定表：哪些记录只表示策略payload已提交；哪些证据才说明**该新迁移者**全部原操作返回；身份缺失、管理端失联、重复/旧回执、活owner、allocate/close UNKNOWN时一律不得激活退休例外。禁止由设备文件自行选择“已批准/已返回”的摘要。
- commit齐全但原owner尚未返回、prepare-only、损坏commit、已返回、已被可靠证明终止的恢复分支，各自允许哪些操作。特别要区分“只读识别COMMITTED”与“可进入新host观察”；同payload幂等不能把缺完成证据的情况归为安全成功。
- 专门完成政策提交的恢复owner必须新绑定、重新证明自己的实际返回；不能用重写commit去证明旧ownerclose。明确其可重验证/force/readback的对象，以及截断或不同payload哪些状态永不自动修复。
- 若补齐合同需增加意图记录、外部回执或文件，更新≤2小文件/目录/字节预算和批准范围，不暗中扩大现有两文件许可。

可复用V2已提出的“新actor事前登记”原则和E7A实际快路径经验；不能只写“采用E7A原则”就视为跨host完成证据协议已经确定。无需永远反复证明一个已真正退休发布者的exit，但必须先有具体、非自证的退休依据。

### E8-F02/P2：不认识新记录的旧版本自动阻断，缺少可执行约束

定位：[迁移计划第21行](D:/CodexProjects/VideoKit/docs/coder/D1_E8_LEGACY_MIGRATION_PLAN_V1.0.md:21)及测试设计L11。提案声称回退到不认识新记录的旧版本“只能安全阻断”。冻结旧 `E5AFinalObservation` 实际只执行原writer history及旧档/guard/账本检查，不读取legacy-acceptance、policy撤销或新schema；它无法因一个自己从未检查的新文件而自动拒绝。

当前history空使旧链路拒绝，只是当前事实，不能当成未来兼容门。原E6B MP4在旧链路有合格history时已能通过，也说明不能依赖它永远拒绝。此项是设计保证缺证，不声称已实际降级或绕过。

应选择并明确一种可执行策略：迁移后禁止不具新门的二进制回退并在部署/受信版本流程执行；或者仅允许已实现显式policy/schema/revocation门的兼容版本。说明旧不兼容版本不在支持范围，而非声称它能识别新状态。APK版本号能限制普通降级的一部分路径，不能单独当作全部数据恢复/代码回退安全证明。

L11应对**真实旧reader或实际部署约束**验证：存在有效新policy/撤销/未知schema时不会被旧路径忽略；不能用一个本来认识policy的新模拟器证明旧代码阻断。继续禁止删记录、重开WRITING、逆向消费或换budget。

## 有据支持的一次性旧V1终局验收

独立核验从已归档HEX解码原1011B账本、重算每条hash链，而非信任设计分析的汇总值：

| 原输出任务 | 唯一终局 | 已消费 |
|---|---|---:|
| 86cafdb3-0fc4-447d-920b-b19c884bf494（原N2） | ABORTED，S0 | 0 |
| 0ee15550-8952-4639-91ac-83ab9d14d36c | ABORTED，原失败产物 | 53651 |
| fbe4330b-111b-4b05-a93c-467413eb8d34 | READY，E6B MP4 | 53567 |

三R/三S唯一有序，消费107218/reserved0，账本SHA256 `f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba`。不得把后续53651B归成原N2的ABORT产物；终局验收不添加媒体R/S、不释放信用或重置记录数。

原ABORTED_SETTLED来源及冻结执行顺序支持原holder/目录实际返回；并非仅complete文件自述。已有后续host实际取得writer4869的exit1792224193337/reason10/status0/proc absent，再完成旧观察；旧writer104B记录确无birth字段，oldCloseACK=false保留，旧无帧根因UNKNOWN不改。

guard.identity82B核对精确原N2任务，owner dev64522/inode20304/UID10221、lease dev64522/inode20385/UID10221，新fence662e9ecd-bede-42e6-bb58-ce81d668ff44；原pending同inode20492归档、beforeimages/原输出0B及后续两个产物均保全。原dev/inode只是既有证据，正式执行时不符应停，不能改pin求通过。

E7A_MANAGED实测只证明那次history AVAILABLE/returned0/matches0、proc NOT_REQUESTED及其诊断快路径结束；不能反证早先历史成功，也不能回溯解释旧AVI。接受已真实完成的历史操作与要求每host重新取得有限历史，是不同问题。在可信冻结实现和合作协议下，原ABORTED/新fence/唯一S0及归档使同一旧恢复的合法再执行前提失效，推荐永久退役该**精确旧操作**，不是通用ignoreWriterDeath开关。

## 信任、当前安全门和批准绑定

合作故障范围与现有 `E4OutputBudget` 的cooperative契约一致。该范围可以接受来源绑定的管理验收、冻结代码及摘要承诺，不必为所有本地合作恢复强加新远端/硬件单调根。对主动同UID/改造代码/root、整套自洽回滚未外锚定后缀不承诺检测；hash/HMAC同UID密钥和inode都不是新的信任根。此限定不删除原Caller UID/PID、Binder角色、隔离参与者或资源门。

推荐的非循环批准链方向成立：先冻结descriptor，不含其未来approval自身hash；approval引用descriptor和精确scope；最终受信manifest绑定descriptorSHA＋approvalSHA。设备自身任意“approved=true”或自选hash不得成为authority。实现还须确保最终源码/策略差异与获批descriptor一致，补齐E8-F01中的新actor运行绑定，不能把可修改的runtime文件当批准来源。

| 可不再每host重做 | 仍必须每host实际取得 |
|---|---|
| 精确退休writer4869的有限history查询、旧S0重复结算、同范围重复行政验收 | 正确受信policy/有效提交及归还依据、旧档绑定、当前guard精确角色/dev+inode/独占性、fence、完整账本和已接受前缀/合法追加、无活动pending/未知actor/在途CONTROL、相关参与者归属、当前原holder/锁/目录操作实际返回 |

旧closeACK不补true；历史终局记录不序列化成本hostlive grant，新的host仍必须完成自己的观察。现有guard先unlock再close，锁可再获取不等于close已返；这也是E8-F01必须有实际接续证据的原因。后续合法账本追加必须允许，不能把1011B写成永久“只接受相同整个文件”。

## 未来V2契约评价

支持V2面向**未来新writer**在业务写/FD转交前绑定bootSource/PID/starttime、attempt/角色/task/epoch/generation/service/budget/guard/fence，并对全部持FD参与者单列记录。boot/source双采样、stat健壮解析、权限/格式失败在资源创建前关闭，均是可实现候选方向，不能补造旧V1采样。

Linux内核文档把start_time定义为进程相对boot的启动时刻；与同boot身份结合可帮助区分启动代次，但文档不证明API31/OEM的实际访问权限。[Linux proc官方文档](https://docs.kernel.org/filesystems/proc.html)。BOOT_COUNT是API24起公开的系统计数，SDK符号存在不等于本设备可读/恢复语义已验证；不同sourceKind不得混比或运行中切换，域不明保持UNKNOWN。[Settings.Global官方API](https://developer.android.com/reference/android/provider/Settings.Global#BOOT_COUNT)。

事前绑定实际远端Binder/nonce/角色并保留DeathRecipient，是对isolated proc视图受限的合理适配候选；回调描述承载该Binder的进程退出，不等于所有其他参与者或转交FD已处置。普通断连/ping失败/超时不替代系统死亡通知；需处理并发回调、丢失与重连，API31使用已有binderDied()，不能依赖API34才加入的who重载。[IBinder.DeathRecipient官方API](https://developer.android.com/reference/android/os/IBinder.DeathRecipient)。

业务TERMINAL_STATE、原资源RETURNED、历史RETIRED及元数据发布者事务分开是正确方向。文件不能自证其最后close/force返回；新恢复owner可在可靠原代次终止及全参与者安全后建立自己的fresh操作证明，不回填旧ACK。canonical唯一编码、父状态/重放/部分提交、16参与者/控制metadata初始上界和资格时限须落实真实生产边界；目前均只是设计约束。

不要求现在额外诊断旧PID或启用V2平台采样；平台能力验证应在独立正式有界计划中进行，失败即停，不成为已退休旧V1日常流程的无限前置门。

## 测试与实现准入

14条矩阵、22组L/V/S/C场景分类完整，明确旧框架/P0/许可保留、无模型复制与设计不冒充执行结果。离线hash链和文档完整性检查通过不等于接收器、迁移或V2生产测试通过。

需将两项修改回填矩阵/状态表及测试设计后，才冻结实现验收合同。补充直接生产边界用例应包含：完全相同commit但最后unlock后close UNKNOWN、错/缺/旧actor完成回执、外部handle丢失、原actor活与已可靠终止的两类恢复、prepare-only和截断commit分别处置、真实旧reader忽略新marker或部署禁止、合法账本后缀可继续追加。测试应调用实际receiver/guard/ledger/owner，不能复制设计逻辑自证。

之后的整批实现可集中包含：精确legacy策略接收器/状态authority、受管迁移owner、每host当前观察分支、兼容与拒绝门、canonical及故障切点自检。未修订基线前可做准备，不建议按现版歧义直接冻结为已获准完整实现。实现自检和整包静态审查后才考虑新APK与准确设备派发；不因本设计方向支持而迁移或自动接正常测试。

## 将来一次性批准是否需要、准确范围

设计修订、实现及静态自检本身无需新增批准。写两个CREATE_NEW小文件也不是一条自动要求人工批准的技术定律；真正需明确的是**是否接受针对这个旧task永久改变历史验收规则及受支持回退范围**。

本提案明确选择永久终局登记，并把实际策略激活放在后续实施。因此建议负责人在完整实现/风险和验证材料可审后，对现有授权是否已覆盖此精确语义作一次核实；如未覆盖，取得一次明确批准即可。原“永久平板使用”及此前一次ABORT授权不能直接当作新策略已获采纳；若后续已取得相同具体范围的授权应复用，不重复索取。**当前不向用户请批，不启动执行。**

未来批准包至少限定：

1. HA1Q6WXR/user0/原UID/原签名；policy D1-E8-LEGACY-N2-TERMINAL-ACCEPTANCE-V1、budget730a73e1-50e1-4198-a515-047104f00e31、旧task86cafdb3-0fc4-447d-920b-b19c884bf494及recovery attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f；精确descriptor/approval/实现包绑定。
2. 只将上述历史操作登记终局、免除其将来重复history查询；原oldCloseACK=false、旧birth缺失、当前真实资源门均不改变，不再ABORT、不新增R/S、不回写旧消费。
3. 原提案两文件acceptance≤4096B/commit≤256B与目录；E8-F01补齐后若路径/文件/外部registry/成本改变，审批清单同步定稿，不暗写额外记录。全部旧目录/档案/输出和107218消费保留。
4. 合作故障假设、精确不可逆语义、兼容版本/撤销策略、部分提交/UNKNOWN失败隔离及成功核验；准许写入不代表任何FD/锁已归还。无杀进程/清数据/删产物/清账/换budget或自动正常测试许可。

如未来仍缺历史来源或当前安全条件，只在原账户外部登记隔离并保留现场，另审外证/处置；不能靠批准消除真实UNKNOWN，也不能把“旧birth不可能补”当成无限拖延已证终局验收的理由。

## 完整包与证据核验

独立证据 `docs/tester/D1_E8_EVIDENCE/audit.py`、`identity-and-design-review.json`。只读核验及已有账本重构，不运行coder的analyze/freeze、不执行迁移模型或产品。

| 项目 | 结果 |
|---|---|
| seal | bba077cd93cdaf1e6b2c172c213f236834ce218e0ea7b0447dd361b020b30b4f |
| 设计ZIP | 74867B；SHA2566fe41be747491c1fed68782d98fa6f2dab013e77fa2d694d233e8164259347bd；28个有序唯一成员逐项大小/hash一致 |
| 不可变文件 | 30项一致；来源副本/原报告/回执逐字节及hash相符 |
| 原E7A | seal及200项冻结文件仍一致，原生产guard/观察/账本来源hash保持 |
| 已有元数据 | ledger1011B/六事件/三唯一R/S/107218和reserved0；guard82B/owner104B/fence/oldCloseACK分离核实 |
| 新运行 | 生产/Android测试0、ADB0、构建0、新APK0、迁移0、媒体及导出件读取0 |

旧冻结中的PAUSED/WAIT_HUMAN是交付当时记录，当前实际用户恢复消息另存 `verified-human-resume.json`，不为恢复而改旧包。报告集中发负责人，等待下一明确整批派发；本次不自动实现、迁移或测试。
