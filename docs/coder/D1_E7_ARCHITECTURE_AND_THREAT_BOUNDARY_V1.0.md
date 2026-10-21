# D1 E7 架构与威胁边界 V1.0

2026-10-17。结论：生产诊断已实现；持久死亡事实协议 DESIGN_BLOCKED_MISSING_TRUSTED_WRITER_GENERATION，没有可用持久准入实现。E6B-OBS-F01/P1未关闭。

现有证据精确区分三道门：首先原 App/独立空闲 host 身份，再 system exit history 的 PID/realUID/process/timestamp 匹配及正 reason，最后 /proc/PID 的 lstat。E6B AVI 的 E5A_RECOVERY_WRITER_DEATH_UNPROVEN 在第二道门，尚未到 proc；错误可以是非唯一匹配或非正 reason，旧日志无法区分。不能据此认定 API 淘汰或 PID 复用。

Android 官方说明此 API 是有限最近记录的环形历史，pid与maxNum为查询条件，不提供永久保存保证；本批没有设备证据证明这次条目被淘汰。[ActivityManager官方API](https://developer.android.com/reference/android/app/ActivityManager#getHistoricalProcessExitReasons(java.lang.String,int,int))。[ApplicationExitInfo官方API](https://developer.android.com/reference/android/app/ApplicationExitInfo) 的 UNKNOWN reason 为0，不能作为已证原因。setProcessStateSummary 针对调用进程，不能回写旧 writer 身份。

实际代码边界：E5N2RecoveryAndroid 只把 Android 行映射为最多8条纯字段，超过上限直接 OVER_BUDGET，不遍历更多条。E7WriterDeathGate 是唯一新生产谓词，直接用于原 requireRecoveryWriterDead；Report 不是 E5AAdmission.Proof，没有授予准入的方法或持久状态。一次查询，不自动重试，不改 maxNum，不读上次报告。查询前固定 now 较原逐行取 now 更保守；其余身份/时间包含边界、重复判断、reason>0、仅 ENOENT 允许等条件保持。原较早 N2 host/codec death()、同步目录 barrier、existingGuard 逐字节业务体保持。

结构诊断 schema1：history=NOT_REQUESTED/AVAILABLE/UNAVAILABLE/MALFORMED/OVER_BUDGET；returned 是真实API返回条数，只有已取得列表才有值；matches 是 PID/UID/process/时间全部满足的条数。rejectPid/rejectUid/rejectProcess/rejectBeforeOwner/rejectFuture 可重叠；reasonNonPositive 仅在身份/时间全匹配行计数，先算匹配数再考虑 reason。唯一匹配才输出其 timestamp/reason/status。没有无关行明细或异常正文。proc=NOT_REQUESTED/ABSENT/EXISTS/UNAVAILABLE，EXISTS只表示仍可见或可能复用，报告始终 pidReuse=NOT_PROVEN/reboot=NOT_PROVEN。报告最长按有限固定字段 <1400字符；旧证据最多2048字符，加固定expected owner字段总量低于4096。不可用/尚未查询的计数 NOT_COLLECTED，不能当0。未知 old owner 解析失败仍停在原WRITER_DEATH，不制造后续证据。

专用 E7WriterDeathDiagnosticTests 是单独测试类，不继承原 @Before 观察。固定只读 recovery.owner，逐级 lstat 目录、O_RDONLY/O_NOFOLLOW/O_NONBLOCK、fstat原文件UID/角色/大小/dev+inode、最多257B拒超256、精确固定owner原始字节、打开前后元数据比较，原 E4Owned 在 open 前保留。实际 close 返回才报 returned；原Job静态强保留，10秒只停止等待，不取消/重开/强制清理，在途保持PENDING并停止批次。只读会有操作系统读取访问时间等常规读副作用，不写业务状态。然后仅调用同一 requireRecoveryWriterDead：拒绝也可成为成功收集的诊断，但不是观察或产品成功。没有 observe、guard/账本改写、force、sync、媒体、CPU、service、READY或授权授予操作。

长期协议所缺的依据：旧 owner=attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f/PID4869/UID10221/com.videokit.app/began1792224193301，旧exit1792224193337/reason10/status0仅是已有历史观察。旧V1没有bootID/kernel start ticks/可验证创建代次；墙钟和PID可重复，nonce也没有绑定内核代次。当前/proc缺席不能补证此前未复用，记录不存在不能区分淘汰、重启或查询不可用。旧成功日志、receipt SHA、同UID签名、应用内自签/HMAC或本地标记本身都不是额外可信死亡来源，不能解决同UID篡改/回滚或旧记录缺失代次。

未来V2仅为设计约束，未实现任何可被读取的格式：必须在未来writer开始任何恢复写前，以受支持、实测可用且能验证的来源，将boot epoch、内核start代次、UID/process、attempt nonce精确绑定；同时绑定不可变task/epoch/generation/service/budget/guard的dev+inode和旧fence/账本原始承诺。证据获取者必须证明是这个启动代次的实际死亡，持久化的授权与完整性/单调防回滚信任边界须独立审定。只有原持久owner真正写入/force/close/目录屏障返回且读回一致才可能记录已提交事实，在途、缺ACK、部分写和不确定提交一律不能声称完成；事实只描述旧writer死亡，不代替新host资源归还。

若未来协议获准，每新host仍必须重新核当前原guard角色与精确dev/inode、独占lease实际获得、旧新fence、完整账本及文件绑定、预算无pending、所有相关原持有者实际close/同步返回；不得从持久事实推导旧sync或closeACK。当前V1 writer缺失代次的迁移需要独立可信外部证据或正式安全处置方案，不能在读取日志后补造V2。新设备只读诊断也未必能补足此缺口，因此不能承诺诊断后自动解锁。

风险与本批真实覆盖：

|风险|实际生产 gate / 测试结果或明确缺口|
|---|---|
|历史缺失/重复|0条/2条匹配均拒绝，重复中一条UNKNOWN仍拒绝；直接生产测试|
|UNKNOWN/负reason|唯一匹配reason<=0拒绝，不进入proc；直接生产测试|
|错PID/UID/进程/前于owner/未来时间|分别计数拒绝，无无关行泄露；直接生产测试|
|API不可用/null/损坏/超8|未取得计数NOT_COLLECTED，空列表与未知分开，拒绝且不查proc；直接生产测试|
|proc可见、不可用、异常、null|只有ABSENT通过；可见不能断言PID复用；直接生产port测试，非Android实测|
|PID复用后又死亡/跨重启|V1无法证明启动代次，报告NOT_PROVEN；未伪造Android复用/重启实验，持久准入禁用|
|旧成功在新host重放|上一Report不会被读取替代当前查询，下一次缺历史仍拒绝；直接生产测试|
|持久记录损坏/重复/过期/缺失/伪签/回滚|本批没有持久死亡事实读写入口，均不能触发任何grant；没有虚构解析器测试。未来须定长严格编码/唯一记录/完整性/精确代次及绑定/单调新鲜度策略全部验证，任何未知拒绝|
|持久提交或资源close在途|不实现/不消费该记录。未来PREPARED/部分写/无原owner实际返回不等于COMMITTED。原观察资源边界字节保持，专用只读FD在途保留；Android在途注入未执行|
|旧live proof/旧closeACK替代当前资源|E5AFinalObservation/E5AAdmission/Guard/Budget等保持原字节，只有其原当前host整链路可能准入；本批diagnostic没有grant|

本地27场景316断言只覆盖生产纯gate及端口返回值；不是对Android真实API、跨重启、持久协议、专用FD在途或设备资源归还的实测。原E6B/E6A已接受边界为继承未重跑，精确来源和输入可复核。所有native/许可/历史signal/原预算安全性质保持。
