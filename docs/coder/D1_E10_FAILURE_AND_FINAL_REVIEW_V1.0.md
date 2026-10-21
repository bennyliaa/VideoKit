# D1 E10 失败隔离与独立终局审证 V1.0

本批只准备，以下条件分支不得被当作设备试验通过。源码静态发现E10-PREEXEC-BOUND-CLEANUP为P1：RESERVE已持久化identify/reserve/BOUND，未发EXEC时原return仍IDENTITY。HostManager ARCHIVE_RETURN按phase调用captureIdentityForFinish；后者明确拒绝reserve.json已存在。STOP_DEPENDENCIES不能把未执行的IDENTITY变为COMMIT；直接ACK又要求已归档returned.json。故原冻结公开CLI不能为该分支完成正常归档ACK。保持原actor与custodian隔离，不手写returned或造COMMIT，不为收尾勉强发送EXEC、不force-stop或偷偷改E9B。证据见static-blockers.json及其三源码精确pin；这是静态链路发现，未声称实测复现。需tester独立确认、负责人集中决定后续最小修复批或范围处置；当前不得标记执行包已闭合。

## 分支处置

|分支|允许动作与证据|禁止推论|
|---|---|---|
|scope/现场预检失败，尚未启动|留原采集及阻断，设备迁移0写；全部metadata client真返后结束本批|不得补用户批准文本、重装/清账绕过|
|LAUNCH结果未知或原身份FD UNKNOWN|停止依赖，原Process/pipe/remote/Store由同custodian保留；在有限预算内仅查询/已审收尾|不得新actor/manager接管，不用进程客户端exit等于Android已死|
|已获安全identity、尚无reserve，需要取消|原控制STOP_DEPENDENCIES使PENDING且无业务原资源在途后，可按原archiveComplete保存IDENTITY→精确ACK→正常finish；只在原真实frame及生产门允许时；控制与STATUS合计<=8/3|不造没有actor的回执；若identity/actor缺失按UNKNOWN隔离|
|BOUND已落而EXEC未发|上述P1隔离，公开CLI正常收尾受阻，集中报告|不发送原本不该发的EXEC当清理，不编辑registry|
|EXEC意图已记/已发但回执未知|不重放、不换seq重发；最多剩余STATUS核实，依赖停止|原磁盘commit完整/锁能取不能代表原操作已返|
|部分intent/payload/commit或内容不符|保全原目录/原原对象，FAILED/PENDING真实返回若符合COMMIT归档门可精确归档ACK及独立finish；终局仍不合格|不覆盖截断对象、不unlink重建、不ABORT旧N2|
|COMMIT真正FAILED但全部原操作已返|原returnedForArchive可允许非资格COMMIT收尾，必须原字节与normalfinish；本次不得final|FAILED不自动成为actor2资格|
|晚返PENDING有完整deviceRecord|保留原超期PENDING，归档/精确ACK/正常finish，原时钟不改；另派可能的actor2仅见下门|晚返不改QUALIFIED，不把新actor当旧closeACK|
|ACK回执未知|禁止第二ACK；原OS日志/原代次缺席可按原生产门收尾，缺证即隔离|finishClaimed/磁盘回执/单PID缺席不够|
|任何原close/Error/alloc/reader/Store未知或永久未返|原same-JVM非daemon custodian继续持有；本机有限STATUS/OP与白名单CLEANUP仅原config pin绑定；查询耗尽后通道关闭/UNKNOWN仍保留原责任|不第二close、不kill/cancel、不换port补额，不controller terminate当CLOSED|
|finish日志超1MiB或原正常系统证据缺失|不能CAPTURE_FINISH/final，保全已有证据并报告；即使原PID缺席仍不伪造normalfinish|不logcat clear/tail拼证，不把容量问题当正常finish已证|
|registry写/force/close未知、head连续性不明|REGISTRY_UNCERTAIN，原Store所有权保留，结束业务入口，原监督链持续|不从最大文件名/commit/最大seq或新registry恢复成功|

PC业务入口失败后只走原custodian已支持的CLEANUP白名单（POLL/受限CONTROL/ARCHIVE_RETURN/CAPTURE_FINISH/CAPTURE_TERMINATION/INSPECT），原config SHA与canonical命令SHA双pin；禁止CLEANUP执行RESERVE/EXECUTE/SEAL_FINAL。调用前确认剩余额度，不在未知后自动重放。这不是对上述P1缺口的修复。

## 本次不准actor2

只发actor1；任何失败结果均先集中报告，不能自动恢复。未来最多一个actor2须有独立派单，并保持相同migration/descriptor/budget和原actor1事实。生产requireRecovery只接受：原COMMIT返回PENDING且实际资格超时、完整deviceRecord并已有normalfinish（RETURNED_LATE_NONQUALIFIED）；或实际独立双采boot/proc证明原actor代次终止、单进程无FD转交，登记TERMINATED_WITHOUT_RETURN。已FAILED/无deviceRecord/身份未知/缺原normalfinish/缺原连续registry均不自动满足门。PID重用/boot变化需原boot/start，不拿旧V1缺birth推断新actor死亡。

actor2需新attempt/handle及新实际boot/start/FD返回/独立10秒资格，仍仅CREATE_NEW自己的0002.intent，原payload/commit必须完整精确或当前确证缺席且符合有序前缀。部分/冲突/原intent缺席但payload已存不自动修复。最多一次恢复；第二次未知停，绝不回填actor1 Java RETURNED，也不改旧N2 closeACKfalse。本包没有actor2命令/许可，6400B单actor最大分配门不能当8448B两actor授权。

## final前独立审证

核实际签发scope/审查/plan/config/命令原SHA，确保新actor与原只读scope隔离；准确身份/真实SYSTEM_BOOT_COUNT与start/UID/无FD转交；identity、COMMIT各原10秒资格及全部原raw/dup/stream/目录/guard最后close真实返回，STATUS快路径不能补写缺失内核trace。确认returned是原完整COMMIT字节并正确deviceRecord；intent绑定同actor/BOUND hash，acceptance725B/commit244B逐字节和hash精确；无其他M/0002/未知控制文件。原档案、0B output、guard/lease/fence及完整ledger合法、原0+53651+53567消费未改、不新媒体、不追加R/S。最后原return精确归档、唯一ACK、唯一系统E9_FINAL_FINISH与对应原PID正常finished inst、真实缺席；任何步骤无证不造。

上述当前证据接受后才发SEAL_FINAL；生产追加FINAL_ACCEPTED事件，catalog含actor1/reserve/returned/finish/device与最终head；checkpoint指catalog+head，seal指catalog/checkpoint/descriptor/preparePlan/review。独立重算所有事件parent/evidence及canonical原字节、无循环，final H_actor此时才实际存在。生产生成文件不自动等于独立审查通过；审查者另存明确结论及原输入seal，不能把catalog当旧资源close证据。原PC自然pcClosed/exit/reader全部返、独立无残留后结束该批。

写迁移终局审查通过仍不激活产品。PREPARE role及CATALOG_SHA=ABSENT保持，不授E5A grant；当前D1未过/M0未启/长期准入OPEN。后续activation与本次写scope分开。
