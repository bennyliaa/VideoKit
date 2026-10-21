# D1 E8A 旧V1迁移与管理接续计划 V1.0

2026-10-18。DESIGN_ONLY/NOT_EXECUTED/NO_APPROVAL_TOKEN。此文取代E8的两文件scope和“旧reader自动拒绝”说法，不改变旧冻结文件。

## 精确保全与批准对象

HA1Q6WXR/user0/App UID10221/test10222/原签名；budget730a73e1-50e1-4198-a515-047104f00e31；旧task86cafdb3-0fc4-447d-920b-b19c884bf494、attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f。原guard owner64522:20304/lease64522:20385/UID10221；新fence662e9ecd-bede-42e6-bb58-ce81d668ff44。原N2-e5-recovery归档/0B输出、pending归档及后续53651/53567产物、全部三R三S与107218消费保持。所有值是既有证据，正式执行不符就停，不改pin求通过。

拟policyID=D1-E8A-LEGACY-N2-TERMINAL-ACCEPTANCE-V2，批准scope必须包括新迁移/恢复actor登记、全部下表文件、有限控制、prepare与activation版本支持集合及不可逆退休语义，不能沿用E8“仅两文件”清单。descriptor先冻结不含未来approval自身hash，approval引用descriptor，最终受信manifest绑定二者及实际actor catalog，避免循环。E8A不分配实际migrationUUID/actorUUID/handle、不生成许可；下文<M>/<A>都是未实例化占位符。实现可评审后由负责人判断现有授权，当前不询用户。

## 新增文件和字节上界

设备路径前缀files/e4a_output_budget/legacy-acceptance/<M>/。只能CREATE_NEW，无覆盖旧应用数据；原S/消费/guard/fence不改。新元数据不是媒体R/S；单独计控制磁盘成本。

|路径/数量|单个上界|读写者与语义|
|---|---:|---|
|actors/0001.intent，必要时0002.intent；最多2|2048B|对应已事前绑定actor写，记录attempt/handle/birth/scope/sequence/registry reserveSHA，绝不记录已close|
|n2-v2.acceptance；1|4096B|actor1写批准payload；恢复actor只能识别/对同一完整内容重验证，绝不覆盖不同字节|
|n2-v2.commit；1|256B|引用policy/descriptor/acceptanceSHA；只表示内容提交，不表示actor已返回|
|legacy-acceptance/、<M>/、actors/；最多3新目录|—|仅在registry BOUND后、原guard保护下创建；已有意外目录或不同migrationID阻断|

最多4个设备文件、8448B内容；路径目录项/文件系统空间另计，不声称8448B就是全部磁盘开销。没有device returned.receipt或可由文件自选的approved=true。activation包资源里嵌入最终外部验收≤16384B及部署/摘要manifest≤8192B，不向device私有目录另写该receipt。

外部authority位于未来D:/CodexProjects/VideoKit/docs/tester/D1_E8A_LEGACY_MIGRATION_REGISTRY/<M>/，由受信tester管理器创建，负责人独立审定，Android app UID不可直接修改本机该目录。当前E8A不创建或执行此registry；设计证据只写docs/coder/d1e8a。

|外部registry相对路径/数量|单个上界|职责|
|---|---:|---|
|descriptor.json；1|8192B|批准前精确动作/对象/成本与旧证据|
|authorization-reference.json；1|4096B|复用或后续取得的具体授权来源引用，不凭空生成批准|
|prepare-deployment.json；1|8192B|批准的prepare app/test SHA/版本/签名/源gate审核|
|activation-release.json；1|8192B|实际最终head后才可登记的activation双APK/compat集合|
|registry.events.jsonl；1|32768B|最多32条、每条≤1024B，序号/父hash/actor/state/证据摘要，追加后真实flush-close与校验|
|registry.checkpoint.json；1|4096B|独立确认的最终head；不是根据最大文件名猜状态|
|final.acceptance.json；1|16384B|actor全集/真实返回或明确终止恢复处分/实际device文件摘要/批准和head绑定|
|final.seal.json；1|8192B|独立审定最终包，不自充源证据|
|actors/<0001或0002>/reserve.json；最多2|4096B|首次device写前可靠绑定完成，含初始资源阶段已返回证据|
|actors/<A>/identify.json；最多2|4096B|实际身份/boot-start/代码与受管handle快照|
|actors/<A>/returned.json；最多2|8192B|实际全部原操作返回的原始快照及sequence；没有就不得造此文件|
|actors/<A>/finish.json；最多2|4096B|准确归档ACK、真实finished-inst/原代次结束，不只声明finishClaimed|
|actors/<A>/termination.json；最多2|4096B|若需要，原代次可信终止及参与者清单，保留oldReturn UNKNOWN，不回填CLOSED|
|actors/<A>/commands.jsonl；最多2|8192B|每actor最多8请求，意图/响应/未知计数，不重置额度|

最多20个有名元数据文件；内容上界155648B，registry总体metadata硬界192KiB，原始控制/系统日志另限1MiB并记录来源引用。可选文件缺失必须符合状态，不用空return文件代表已返回；原历史报告可引用其冻结SHA，不复制视频或大包。除上述清单，不暗写额外actor/receipt文件；超2actor、超界或需新路径时停止另审，不自动扩展。

## 首写前绑定与authority

1. 管理器预留<M>/actorOrdinal1/attempt/handle/初始commandSeq=1，绑定已审核descriptor和prepare双APK SHA；此时ALLOTTED_UNBOUND不能写设备目录。
2. 仅启动受管READ_ONLY_IDENTIFY。实际App UID/PID/process、bootSource/starttime、handle、nonce挑战、task/policy和参与者（此迁移限定原app单进程、不转交FD）由可信runner采样；身份读取本身的FD也须真实close返回。采样失败/UNKNOWN不进入业务写。boot/start能力需实施阶段有界平台验证，不能拿旧V1缺birth当新actor省略依据。
3. 管理器保存identify与reserve，核代码SHA、实际进程身份和该phase原操作已返回，追加BOUND状态后真实落盘/校验；控制ACK仅经已有DUMP权限保护入口、精确handle+expected sequence+reserveSHA。app只对这一个已预留actor接受一次EXECUTE_COMMIT；permission对普通app的负例将来必须实测，不把广播Binder.getCallingUid误当原shell调用者。
4. 每次状态命令的target handle/actor/command sequence精确匹配。状态命令重放不能再执行写动作；失联/已发但回执未知消耗一次额度，不重发EXECUTE。只可在同handle有限STATUS核实真实进度。管理器重启没有已独立核实的连续head即REGISTRY_UNCERTAIN，不从commit或最大seq恢复成成功。

控制采用E7A非等待instrumentation/有界STATUS/归档ACK的已证快路径原则，但这是新协议、尚未实现。身份阶段和执行阶段各有独立10秒资格，从各自原操作实际开始计；两阶段之间只允许无业务资源持有的受管等待授权，不把它用于延长在途资格。每phase超时永久PENDING；晚返只能收尾，不变原phase成功。每actor最多8控制请求/每响应5秒外部预算/STATUS最多3次；无取消future、kill或无限等待求PASS。

## 提交切点状态表

authority始终为外部registry；device字段与锁只作为被核证对象，不反向授权自己。

|切点/外部状态|device可能状态|能否激活/后续|
|---|---|---|
|ALLOTTED_UNBOUND|无新device文件|否；只有只读身份采样|
|BOUND_IDLE|无device写；原身份phase真实返回|否；一次EXECUTE后才建目录/intent|
|INTENT_CREATING / INTENT_WRITTEN|intent缺/部分/完整|否；部分保留，不清理重来；原actor继续仅在其原资格内|
|PAYLOAD_CREATING / PREPARED|acceptance缺/部分/完整|否；错或截断payload不可自动修复|
|COMMIT_CREATING|commit缺/部分|否；部分commit冻结隔离；不覆盖成看似成功|
|COMMITTED_UNRETURNED|acceptance+commit完全正确|仍否；锁可取得、unlock已返回都不是归还证据|
|RETURN_OBSERVED|真实全部metadata/目录/guard dup/raw close已返回|仍不能自动产品激活；归档精确seq再ACKfinish|
|NORMAL_FINISH_CONFIRMED|原代次实际正常finish，全部原返回证据已存|可送独立审定，尚非产品grant|
|FINAL_ACCEPTED|外部最终head/actor全集/范围独立接受|可另批产生activation包；prepare代码仍不激活|
|ACTIVATION_PACKAGE_APPROVED|精确最终catalog已嵌入受信同签名新包|每新host核完整catalog/文件与当前安全链后才可本hostgrant|
|QUARANTINED / REGISTRY_UNCERTAIN|任何组合，包括看似完整commit|否；不让device字节猜管理状态|

所有实际open/read/write/force/close/sync/guard最后close切点均可UNKNOWN，外部不得越过。即使完成文件齐全，必须有精确同actor的RETURN_OBSERVED和NORMAL_FINISH证据；旧/错seq、错handle、缺身份、receipt来自另一次尝试、部分writer仍活、registry缺失或管理失联均阻断。

## 专门恢复actor

活原actor只能原任务自然收尾；不能另开actor抢锁/重写commit。原actor晚返，PENDING不改成功；可被明确登记为RETURNED_LATE_NONQUALIFIED，随后经独立授权的actor2对完整同一事务做重新验收，actor2有新身份/handle/seq/10秒资格，原失败不会被抹去。

若原actor可靠终止而返回不明，必须先有首次绑定的boot/start或已审实际Binder实例死亡证据、原单进程/无FD转交清单和当前参与者处置；原因UNKNOWN不造旧closeACK。登记TERMINATED_WITHOUT_RETURN_RECOVERY_REQUIRED，原资源状态历史仍UNKNOWN，能力已可靠终止但不把内核回收写成Java返回。独立管理接受这种终止处分后，actor2才可能开始：新绑定、原guard/ledger排他及全部当前条件、只对同一批准payload和无歧义commit重验证/force/readback；新actor自己的原holder、目录和最后guard须全部实际返回/正常finish。最终catalog显式列actor1未返回的已接受终止处分和actor2真正完成，不能只留actor2覆盖原历史。

若原actor已按上文安全终局，原registry身份完整，当前固定目录中payload和commit均确证缺席，可专门批准actor2 CREATE_NEW同一批准payload及commit；旧intent可为完整精确内容或确证缺席，最终catalog明确记录其presence，不补写旧actor intent。prepare-only且payload完全正确、commit当前确证缺席，可另行批准actor2 CREATE_NEW同一commit；commit已完整则仅重验证，不重写。当前缺席是同锁下lstat得到ENOENT并核精确目录与无冲突条目，不声称知道旧CREATE是否曾执行后掉电丢失，旧调用UNKNOWN仍保留。已有截断intent/commit/payload、不同内容/多份记录、原intent缺失但payload/commit已存在这种不合提交顺序的组合、缺失外部原actor身份或无法排除活参与者，均不在本合同自动修复范围；即使进程已死也先ISOLATED保全，另审精确处置，不覆盖/删除/清账。最多一个恢复actor，第二次未知就停，不无限继任。

## 跨host与发布/安装

prepare版本硬禁产品例外，且迁移入口核自身app/test的批准SHA与PREPARE角色。外部独立审定最终catalog后，另批activation app/test内嵌它和精确head/actor集合；此时不再启动任何迁移写actor。activation test包不保留可写迁移入口；旧prepare test即使被保留也必须因app SHA/角色不匹配在首写前拒绝。

安装只在全部登记actor已终局、原资源已实际返回或已被明确可靠终止后由合格恢复actor完成、无未知当前参与者时进行；不能用install-r结束未知actor。版本vPrepare>当前实测10，vActivation>vPrepare，具体数字/包SHA到实际交付填，不现在虚构。两阶段各双APK，部署禁-d/卸载clear/强停未知资源。

每新host的激活条件同时满足：受信兼容activation包的完整final catalog；全部actor身份/sequence唯一，最后执行者真实RETURNED+NORMAL_FINISH；前序每actor已实际返回或有明确被接受的终止恢复处分，无未处置UNKNOWN；device所有intent/payload/commit与catalog完全一致；原档案与完整合法ledger前缀/后缀、当前精确guard/fence、无pending/在途资源、本host实际原返回。缺/旧head/错scope/部分catalog一律阻断。永久终局事实不按墙钟年龄过期；“旧”指被当前受信scope/version取代或actor不匹配，而不是隔一天就重问history。最终catalog已进受信包时管理器可离线；在此之前失联没有authority，不能激活。

具体禁止回退、数据恢复和同签名高version旧代码规则见V2合同兼容章节；老observer并不读这些新文件。未实际实施/审定前不形成任何迁移批准或正常测试准入。
