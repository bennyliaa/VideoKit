# D1 E8A 独立设计复审报告 V1.0

日期：2026-10-18。Tester。依据 `docs/milestones/D1_E8A_TESTER_REQUIREMENTS_V1.0.md`，复审完整四文档、状态合同、actor绑定、成本清单、真实旧源码和已有部署证据。

## 结论

**SUPPORTED_FOR_CONSOLIDATED_IMPLEMENTATION：E8-F01/P1、E8-F02/P2在修订设计范围关闭，未发现新增阻塞项。** 支持负责人派下一整批实现及直接生产边界自检；不需要再开启一轮纯设计以追求对合作模型之外威胁的绝对保证。

该结论不表示迁移/V2/部署门已实现或实测。32组为设计场景，生产/Android执行0；本轮ADB/构建/模型/媒体及导出件读取/迁移写0，无批准token。E6B-OBS-F01长期仍OPEN；原MP4限定PASS、AVI/能力/cancel未准入，D1 NOT_PASSED/M0 NOT_STARTED、全部P0与框架许可保持。

## 两项原问题的关闭范围

| 原问题 | 修订后的具体闭合依据 | 关闭限制 |
|---|---|---|
| E8-F01：commit相同但原迁移者未归还，跨host无法判定 | 首次应用写前ActorKey/原身份phase返回/外部reserve落盘；外部registry是当前authority；prepare代码不允许产品例外；COMMITTED_UNRETURNED及RETURN_OBSERVED等状态均不能激活；实际原返回＋准确归档ACK＋normal finish后独立封存；activation包固定完整actor catalog，下一host不从device文件猜成功 | 仅设计闭合。新runner、registry、receiver、FD真实返回与故障切点均须实现后直接验证，不能继承E7A快路径为全部通过 |
| E8-F02：旧reader不认识新marker却声称会自动拒绝 | 承认真实旧类不读新记录；明确不支持回退至无新门版本；受管部署核完整app/test SHA对/签名/源审计/角色/descriptor与final head，安装前后核实际包；高version旧代码/伪ABI声明也不能进允许集合；人为绕过不作Android绝对阻止承诺 | 仅设计闭合。新部署gate及真实旧reader负面能力用例尚未执行；旧部署脚本只是可行先例 |

旧E8和E7A冻结不修改；原评审结论作为历史记录保留，不回写成当时已通过。

## F01：actor、归还与authority

ActorKey明确绑定registry/migration/ordinal/attempt/handle、command/state sequence、旧task/policy/descriptor、prepare app/test SHA、实际UID/PID/process、boot来源/start和参与者。新迁移限定单进程、不转交FD；身份采样本身的FD真实返回后，外部BOUND保存并验证成功，才可一次EXECUTE。新actor不能借旧V1未采birth省略身份，采样权限不符应在业务写前停止。

EXECUTE接受即预留队列/原操作，未出队且FD EMPTY也不等于safeToFinish。identity和commit各自10秒资格，之间必须无业务资源持有；不能通过切phase给原在途操作续时。超时保持PENDING，晚返只更新真实资源状态。最多8个请求/3次STATUS，不重发未知EXECUTE、不重置额度，控制与进程损失保持UNKNOWN。

16个状态中，COMMITTED_UNRETURNED、RETURN_OBSERVED、NORMAL_FINISH_CONFIRMED、FINAL_ACCEPTED、QUARANTINED、REGISTRY_UNCERTAIN均不能独自产生产品激活；只有ACTIVATION_PACKAGE_APPROVED结合本host当前证明才可能grant。guard先unlock再close的既有反例已直接绑定真实源码；锁可得不替代raw/dup/目录/ledger/guard原返回。

外部returned文件不能由设备传入bool填充，需精确ActorKey/操作sequence的原快照、冻结生产调用绑定及外部实际存储。normal finish另有系统结束证据，finishClaimed或PID不存在不是close。跨host缺/旧/错回执或未核实head、未处置actor、管理失联都阻断；最终catalog由受信activation包持有后，管理器离线不再造成永久在线依赖。

这消除了“完整commit可被误当完成”的设计歧义，也没有退回应用私有文件自选批准hash。可信本机管理者和独立审定是已明确的合作边界，不声称抵抗root或本机管理员全套改写；无需再为此加入新的远端服务、硬件密钥或同UID反回滚根。

## 有限恢复与失败关闭

原actor活或UNKNOWN时不能另开actor抢锁。晚返保持原非合格；确证原代次终止且无FD转交/无其他参与者时，也只接受TERMINATED_WITHOUT_RETURN处分，不伪造Java CLOSED。随后最多一个新actor2，必须新绑定、独立资格、全部原资源实际返回和正常finish，最终catalog保留前后两actor及处分关系。actor2再未知则停，没有无限继任。

同锁当前ENOENT只证明当前缺席，不回填旧CREATE未执行。原actor已安全终局且外部绑定齐全时，payload/commit均无、或完整payload而commit缺席，可在专门scope下CREATE_NEW相同内容；完整commit只重验证。截断intent/payload/commit、不同内容、多份记录、旧intent缺失却已有提交、外部身份缺失等均隔离，不覆盖/删档/改名清障。每一恢复分支仍不新增媒体R/S、不抵消消费、不改原fence或oldCloseACK。

在实现中须保持“只读COMMITTED_IDENTIFIED”“合格原归还”“最终历史接受”和“当前host grant”的类型/入口区分；这属于已经闭合合同的落实，不是新增安全范围。

## hash依赖与最后close

修订已将actor-final head H_actor、独立验收catalog/checkpoint/seal与后来的activation-release分层。未来APK SHA不回填已冻结actor events，APK不含自身SHA，approval不含自己未来hash；没有要求Android actor再写一份returned.receipt证明自身最后close。

实现canonical布局时应把依赖顺序落成可检查的数据图：既有descriptor/授权/prepare身份与actor原始证据 → 封存actor事件前缀H_actor → 引用该head的final catalog/checkpoint → 不含自身digest的seal → activation资源/实际APK → 外部activation-release。final catalog/seal和release不能再作为同一H_actor前缀的自指输入。此为避免实现偏离现有非循环设计的具体验收约束，不再增加第三次“证明最后发布者close”的行政或构建链。

外部registry存储/校验/独立封存失败时没有FINAL包，不激活。它不是Android业务actor；其外部可信验收是明确的管理边界，不递归要求设备自身为每次报告写入生成新的自证文件。

## F02：可执行部署与回退边界

直接核真实冻结 `E5AFinalObservation` / `E5AAdmission`：不读取legacy-acceptance/schema/revocation，当前history0不是版本门。新设计已不再作相反保证。后续D01必须调用真实旧reader，在合格旧Platform/本机有界夹具旁放新marker，记录旧代码实际不识别，而不是让一个新模拟器假装旧reader拒绝；本轮没有运行该用例。

选定的强制点是受管部署入口：独立批准完整app/test SHA对、签名/package/UID、phase、经源码审查的GateABI和descriptor/head，安装后核实际base.apk/组件。version只是附加条件；高version同签名旧代码、复制ABI文本、改文件名或错test配对仍不在允许集合。旧不兼容版本从支持集合排除，不承诺拦住拥有签名/adb权限的管理员绕开入口。

prepare必须在所有恢复/debug/public资源路径执行phase gate，不只改一个@Test；activation不得保留可变迁移路由，旧prepare test在新app下首写前也因pair/phase拒绝。撤销需新compatible release实际生效，不能仅外部写revoked.json就声称旧代码已停；安装和升级也不能用来终止未知actor。上述真实入口和部署边界是下一实现批次必查点，不需要引入Android平台外的新绝对防降级能力。

## 两阶段和构建成本评价

**在本设计选择“最终事实固定进入受信APK、产品不依赖常在线管理器”的前提下，准备→最终接受→激活两次受信发布合理且有限。** catalog在真实迁移结束前尚不存在，所以不能把同一个固定最终catalog提前装进prepare包。仅改一个device completed或activate标记会重新引入已关闭的authority问题。

这不意味着逻辑上必须重新实现两套代码，或两次全量Java/native重编、全部旧套件重跑、重复索取相同策略批准。建议下一整批实现一次性完成共享phase控制器、registry/actor协议、只读激活reader、部署gate及全部直接切点测试；prepare和activation用同一已审实现，只改变必要phase/可达入口和最终catalog资源。

若现有工具链能分开公共编译与资源/manifest打包，第二阶段可复用已验证编译输入，仅进行必要的catalog/角色打包、签名、对齐和精确差异核验。是否真正复用要以实际构建输入/产物证明，不能把随意编辑zip当合格已签APK，也不假称当前已实现该优化。若工具链仍需一次正常主构建，按现有“两阶段各一次主构建”即可；无需为省这一调用引入新的签名协议、密钥、插件或远端authority。

第二阶段只重复与变化有关的验收及真实activation集成门；原未变native/框架来源不重编，旧全部测试不机械重跑。新系统事实若缺失应按原停止条件处理，不为找PASS增加第三个actor、第三轮修饰发布或无限行政确认。因此建议接受两阶段上限，并优化重复工作，不因发布次数本身继续阻断实现。

## 成本核算与实际可执行边界

独立按清单乘数量重算：

| 项目 | 核算/判定 |
|---|---|
| device文件 | 2×2048B intent＋4096B acceptance＋256B commit＝4文件/8448B内容；3个新目录。目录项/文件系统开销另计，未混成8448B总磁盘占用 |
| 外部registry | 20个有名元数据文件最坏内容合计155648B，低于192KiB硬界；原始日志另限1MiB，不能又把完整大响应重复嵌入小记录超界 |
| 激活资源 | final acceptance≤16384B＋部署/摘要manifest≤8192B＝24576B；不是额外device私有receipt文件 |
| actor/控制 | 最多2actor；每actor最多8请求、STATUS3、单响应5秒，意图已发/响应未知也计数，不是旧E7A handle余额的重置 |
| 资格 | 每actor身份/提交各10秒，phase之间无业务资源；超时不可晚到改PASS |
| holder | 48为新迁移owner设计上界，尚非实测；不授权把原budget或其他框架类的原上限改成48 |
| 发布 | prepare双APK一阶段，最终事实独立接受后activation双APK一阶段；当前实际构建0 |

registry事件最多32条/每条≤1024B和各记录上界应以引用原日志摘要而非复制全部日志来实现；切点日志放独立有界原始证据。实现需给出真实holder/call/读写计数、关闭顺序和目录同步开销；如布局放不进上界，应先简化布局或明确修订，而非暗扩权限/文件/次数。以上是可执行的有限合同，不是已经测得的性能或容量结果。

新增scope相比E8的两文件明显增加，但现在成本和authority都可见且用于关闭真实问题；不得沿旧两文件范围直接执行。当前没有分配真实migrationID/actorUUID/handle，也没有创建实际registry或批准token。

## 下一整批实现准入

支持负责人现在派**一个集中实现批次**，包含：

1. 真实外部registry writer/reader、规范序列/哈希图和最终catalog封存；精确actor绑定、phase控制、队列预留、原holder/finish接续。
2. 限定legacy receiver、原guard/账本与新host observation集成、未知/部分提交/有限actor2恢复；不改媒体消费和旧任务事实。
3. prepare/activation全入口兼容门、精确APK对允许集合及实际部署wrapper；完整角色隔离，不只修改测试选择器。
4. A01-A23/D01-D09直接调用这些生产对象的有限切点自检、完整源/成本证据、一次prepare主构建及整包交审。激活发布的后续工作不提前填造真实catalog或head。

32组仍只是设计，旧22组作为上层需求不能相加成已执行54组。新E8A gate/registry/actor尚未实现；E7A身份/ACK快路径和旧脚本SHA核验仅是先例。实际平台boot/start权限、DUMP负例、原始FD/跨进程/进程退出、真实部署等须实现静态整包通过后另派有界设备批次，不在此复审启动。

原账本identity、三R三S/107218消费/reserved0、原档案与全部产物、oldCloseACK=false保持，历史事实不成为当前liveproof。未来真正激活仍要求完整catalog、当前guard/fence/合法账本后缀/无pending/无未处置actor及本host实际资源归还。迁移、激活、正常AVI/能力/cancel分开正式派发，不自动串行。

## 冻结与证据核验

独立只读脚本 `docs/tester/D1_E8A_EVIDENCE/audit.py`、结果 `identity-and-design-review.json`。不运行coder状态模型或迁移实现；无ADB/构建/媒体/批准。

| 身份项 | 结果 |
|---|---|
| seal | dfbb91fcc193d65b599d88e9399f66edb115e0331e85a656f1b83d0ba54d1e86 |
| 设计ZIP | 139379B；SHA2567ff0c0b4a7e918b1b5e44bf671ef3f4dd4892722f48577ae7000ef14e6a3b2e4；40个有序唯一成员逐项大小/hash一致 |
| 不可变文件 | 42项一致；四文档/diff/原始引用逐字节对应 |
| 旧冻结 | E8 seal/30项与E7A seal/200项均保持，不改旧报告和代码 |
| 设计证据 | 16条需求/16状态/32组设计；真实旧reader直接源码检查，部署先例明确不是新gate运行 |
| 当前执行 | 生产/Android测试0，模型/构建0，新APK0，设备0，迁移0，批准token0 |

本轮建议进入实现而非继续扩大设计防御范围；批准和实际迁移scope待完整可审实现及具体风险材料确定，复用已覆盖的明确授权，不因本设计支持先生成许可。长期问题仍OPEN、D1未过/M0未启；报告集中发负责人，等待下一正式整批派发。
