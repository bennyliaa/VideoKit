# D1 E8 架构决策 V1.0

2026-10-17。状态：PROPOSED_FOR_INDEPENDENT_DESIGN_REVIEW。只做设计，不修改冻结E7A、生产代码或设备。用户要求本批交付后暂停；不自动实施。

建议采用精确限定的一次性“旧V1终局验收”，把已经实际完成且不可再次执行的旧恢复操作登记为RETIRED_LEGACY_TERMINAL。后续新host继续证明当前完整状态及自己的资源返回，但不再每host查询PID4869的有限exit历史。不是放弃死亡门的通用开关，也不是把旧报告变成新host liveproof。E6B-OBS-F01目前仍OPEN，只有后续实现/独立复审/正式迁移及新host实证后才能限定关闭。

## 证据与更正

原N2 task86cafdb3-0fc4-447d-920b-b19c884bf494 的狭义ABORT实际终局为0B，不是53651B。E5C_N2_ABORT_V1.1记录ABORTED_SETTLED、原holder及目录barrier真实返回、唯一S0、原guard身份、pending同inode归档，原closeACK=false保持。恢复writer=attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f/PID4869/UID10221/process com.videokit.app/began1792224193301。E5C观察及E6B MP4新host曾实际查询到exit1792224193337/reason10/status0/proc absent并完成原观察，不是仅有一个完成文件。

另有task0ee15550-8952-4639-91ac-83ab9d14d36c 的ABORTED53651B，随后taskfbe4330b-111b-4b05-a93c-467413eb8d34 的READY53567B。共享账本消费0+53651+53567=107218，reserved0，三笔原R和各自唯一S都保留。最新已记录ledger1011B/SHAf32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba；这是E6B已取证元数据，不声称E8实时检查。

E7A_MANAGED实测history AVAILABLE returned0/matches0、proc NOT_REQUESTED；只能证明这一次没有返回条目，不能证明旧AVI当时原因或具体淘汰/PID复用。原诊断操作CLOSED、精确seq9归档ACK、实际finish与PID13876消失，只支持本次快完成路径。旧writer没有boot/start字段，不能回填成已采集。

## 信任与安全目标

主模型是当前原代码已经明写的“Persistent cooperative execution budget”：同一可信签名构建、同UID各参与者遵守原guard/fence/串行规则；故障来自退出、掉电、IO异常、超时、淘汰、重复调用、损坏或误恢复。负责人/tester的来源绑定报告与批准记录作为管理验收证据；应用沙箱、安装签名及审核固定的代码/接受摘要是信任边界。不是任意用户可输入的bool。

同UID主动攻击者可读写应用私有档案、伪造普通hash链、回滚一套自洽文件、持有/转交FD或运行改造代码；root也可改变系统事实。本批不承诺在这种攻击能力下本地预算全寿命防回滚或不可伪造close。SHA/原inode/代码内固定摘要可发现具体被改对象，但不是新的信任根；仅把HMAC密钥放同UID也不解决该攻击。若产品另需对抗该威胁，应独立立项硬件/远端单调锚与设备迁移策略，不把它默认加为合作播放器恢复的无限前置门。明显摘要/账本/身份不符即拒绝；不能声称检测了所有主动自洽回滚。

## 为何旧终局可不再反复查死

需要一次性接受的是“这一次原操作已经完成，已被原机制终局封存且不再具有修改该旧task的合法路径”，不是新造kernel birth证明。来源绑定的ABORTED_SETTLED发生在原metadata/ledger/guard/目录实际返回后；冻结execute的used与ACTIVE限制、ABORTED journal/替代fence/已存在archive/已追加S使旧originals前提不再成立。再次合法执行同一ABORT必须先遇到非原WRITING/非原ledger/已有archive，不可能再结算一次。已完成的操作不会因系统淘汰exit记录或后来PID复用而重新执行；既有exit正证进一步支持其终止，但不需要每host重新取得同一有限记录。

该论证以实际回执、可信冻结控制流与合作协议为前提。仅有complete文件、文件内声称close=true、只有排他锁可得、或负责人说“同意”均不足。尤其排他锁不等于原FD close：现有E5BGuard先unlock再close，UNKNOWN close可能锁已释放，因此必须保留原返回证据与当前原owner状态核验，不能把flock当作全部资源回收证明。

## 方案比较与选择

|方案|结论与原因|
|---|---|
|继续每host查PID4869/加limit/重试|拒绝。有限历史已实际空，不提供持续性，只制造诊断循环|
|直接删除WRITER_DEATH或信任complete文件|拒绝。没有精确迁移身份和终局依据，可能放过部分恢复|
|要求补旧boot/start或强制外部防回滚根|不选。未采集字段不可补造；同UID对抗不属于既定合作模型|
|精确一次性终局验收+后续当前整链路|推荐。基于已实际终局证据，保留原账本与档案，替换的只有这个旧writer的历史查询前置条件|
|证据不符时隔离原任务并停止新业务|备选。保留账户及全消费、不删档、不重做ABORT；需独立外证/正式处置后另审，不通过换budget继续|

验收记录采用构建审核固定的policyID/原task/原恢复attempt/原archive清单摘要/原S0/guard dev-inode/新fence/完整已接受ledger前缀及107218消费下界/批准证据摘要。具体编码和不可逆审批见迁移计划。安装新实现是明确的策略版本升级，不能悄悄把旧被冻结代码解释成已有此能力。

## 每host仍须证明什么

新host创建任何产品源/CPU/codec之前，核受信policy和已提交的精确迁移记录、旧档完整hash与角色/精确guard身份、当前实际独占guard与ledger锁、原ABORTED fence和完整合法账本、已接受前缀不丢失/消费不倒退、无活动pending/未知操作、当前相关进程/服务/句柄归属，以及本host所有新打开FD/锁/目录屏障真实返回。输出存在/角色/长度/已登记内容承诺及需要的当前验证保持；不将保留老输出的内容重新全读作为每host永久成本，若原既定观察仍要求hash则须明确实现审查变更及验证计划，不在E8擅改。

新host最终grant仅是该host实际观察对象，不能序列化或跨host复用。旧originalCloseACK=false、旧恢复当时状态和历史UNKNOWN不回写。当前发现活原任务、待收尾资源、未知关闭或不完整提交必须阻断；管理验收没有能力关闭FD或杀进程。

不再每host重做的是旧4869历史退出查询、旧0B的再次结算/再次R/S、旧已接受终局事实的重新行政审批；需要重新核的是其不可变档案绑定未变及所有当前安全条件。未来V2区分终局历史事实、当前活操作和本host liveproof，避免把每个已退休writer永久留在history依赖里。
