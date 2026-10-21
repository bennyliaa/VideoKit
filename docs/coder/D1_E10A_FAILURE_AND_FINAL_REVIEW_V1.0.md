# D1 E10A 阶段化失败收尾及独立final审证 V1.0

E10确认的P1/P2本批已实现本机有限验证，待独立E10A接受；不是设备取消/写故障实测。无新取消wire，Android Run/STOP/PENDING/ACK语义未改，主机严格阶段门和registry原证据校验提供合法出口。

|阶段|允许处置|不可推论|
|---|---|---|
|启动前scope/现场失败|全部metadata原client真返后结束，迁移0写|不补随机token或重装绕过|
|身份未返/无actor/UNKNOWN|原manager/custodian/Process/Store/remote保留，剩余额度内只受审查询/收尾|不补actor/return、不开新manager/actor2|
|未BOUND合格身份要停止|一次STOP原PENDING真返→原IDENTITY归档→精确ACK→独立normalfinish|不把无actor或未返当可归档|
|BOUND但未记任何EXEC意图|严格同actor/plan/reserve/连续最后BOUND+原identity真返+原sticky停止才新出口，identify/reserve原字节不动|不覆盖qualified identify、不强EXEC换收尾、不final/actor2|
|已记EXEC意图但wire/回包未知|快捷IDENTITY取消拒；不重发EXEC，剩余STATUS核原进度/收尾或隔离|缓存旧IDENTITY、executeDone=false不能排除已预留执行|
|执行在途原资源未知|停止后继依赖，若有适用原STOP且预算/阶段允许才发，原资源须实际真返|PC stopDependencies不等于Android STOP或资源已返|
|FAILED COMMIT且全部原资源真返|returnedForArchive允许原COMMIT FAILED、device ABSENT；精确归档ACK/normalfinish，final仍拒|不能强求完整deviceRecord才准安全收尾，不能当恢复actor资格|
|晚返PENDING有真实COMMIT|不改超期判定，归档ACK/normalfinish；actor2仍须另派并过原严格门|不抹旧PENDING/UNKNOWN，不改oldCloseACKfalse|
|已知safe COMMIT终局或任意returned已归档|STOP在host写intent/发wire之前拒；原R0保持，沿唯一精确ACK/finish|不让STOP产R1，也不为拒绝先消耗唯一ACK|
|第二STOP/STOP后EXEC/第二ACK/重复归档|原host/registry前置拒；不append意图、不改原proof或identify/reserve；真正已发未知仍已消费|不以拒绝作为重放许可；重复归档不故意CREATE_NEW毒化Store|
|ACK原字节不匹配|host在ACK意图前拒；先保留原证据，不伪造proof/覆盖归档；PC失败后只能原CLEANUP受审收尾|不错误发ACK再消耗唯一机会重试|
|ACK已发响应未知|不第二ACK；只据原系统normalfinish和代次证据有限收尾，缺证隔离|finishClaimed或磁盘记录不等于正常finish|
|registry head/plan/reserve不同或IO force/close/alloc/reader未知|新取消拒，Store/原任务长期持有；REGISTRY_UNCERTAIN不恢复发布|不从最大seq/commit猜head，不第二close或kill/cancel/换budget/port|
|系统日志>1MiB或normalfinish锚点缺失|无final，保全原证据，集中报告|不clear/tail或拼造系统finish|

生产operation任何失败仍标manager.failed并停止依赖；原同JVM受审CLEANUP仅POLL/受限CONTROL（STATUS/ACK/适用STOP）/ARCHIVE_RETURN/CAPTURE_FINISH/CAPTURE_TERMINATION/INSPECT，原config+命令SHA绑定。新pre-wire阶段门同用于custodial控制。CLEANUP无RESERVE/EXEC/SEAL，不能因为Android后来合格就忽略原PC失败。测试console失败后实际经原custodian完成唯一ACK证明只限收尾，不证明重新发布资格。

## 不自动actor2

本包只actor1。取消后的IDENTITY/PENDING不是COMMIT，原sealFinal/requireRecovery仍拒，不能因为正常finish就actor2。未来最多一个actor2须实际结果另派：原COMMIT PENDING且实际超资格、完整deviceRecord及normalfinish；或独立双采boot/proc证明新原actor代次可靠终止且单进程无FD转交，登记TERMINATED_WITHOUT_RETURN。FAILED/device ABSENT/身份缺失/未终局不自动满足。新actor2有新attempt/handle/实测boot/start/10s资格，保留同migration、原actor历史、budget和descriptor。仅完整同一metadata或当前确证缺席且有序前缀可CREATE_NEW其0002.intent/缺失payload/commit；部分冲突不覆盖删改，第二次未知停。旧V1缺birth不补，oldCloseACKfalse不变。

## final独立审证门

核本批真实被接受的E10A实施+scope/原派单/plan/config/命令/部署前13及部署后14 exact pair；新actor完整身份与原资源真实返回；identity/COMMIT各独立10s和5s响应含decode，未伪造内核raw/dup trace。核原COMMIT return与归档完全相同、deviceRecord/intent/reserve/725B payload/244B commit精确、无多余M/actor2文件；旧13metadata/原guard/fence/0B/S0/ledger全部合法并保留107218与合法settled后缀，无pending或活未知参与者。唯一ACK、独立normalfinish原日志与原代次缺席、PC全部原任务自然真返；无一项用磁盘commit/锁可取/client exit代替。

只有正常COMMIT合格+原全部实际返回/normalfinish+独立当前审证接受才SEAL_FINAL；事件parent/evidence与最终head、catalog中actor/reserve/return/finish/device、checkpoint/canonical hash及seal绑定无环。生成文件本身不是独立接受。取消/FAILED/超期不合格/PC failed后CLEANUP不能final。当前没有真实catalog/H_actor，也未执行该流程。

新APK/JAR只证明本批静态/有限本机范围；真实Android写/取消故障、普通发送者DUMP负例、raw/dup内核故障未升级为通过。D1未过、M0未启、长期准入OPEN，后续activation独立。
