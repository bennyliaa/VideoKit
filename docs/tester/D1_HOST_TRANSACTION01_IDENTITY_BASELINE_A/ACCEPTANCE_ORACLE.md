# 后续独立B有限oracle（全部PLANNED_NOT_RUN）

仅在完整候选冻结、负责人正式派B并绑定其准确端口/产物后执行。这里不引用HOST_TRANSACTION01浮动实现，也不创建新测试框架。每例均须记录准确旧/新源hash、原grant/task/事务/版本、真实原对象和读写/发布/返回事实；字段名以届时冻结API为准，不能把本表概念强加成旧SDK新字段。

|ID/类别|有限输入与动作|验收重点|
|---|---|---|
|N01 正常|自己临时输出，真实write→flush/close→原grant授权reopen→validator→READY|内容/结构与同grant分别证明；READY token不代COMMIT，全部原writer/read/validator返回|
|N02 正常COMMIT|N01后唯一显式同task/token COMMIT，实际发布并重开读、同事务只读结果|实际内容与发布对象可核；CONFIRMED_COMMITTED及原响应/worker归还分栏，RPC/物理发布各1|
|N03 源代次|原两个consumer/read/close/原worker全返，退休原generation后新range|新epoch合法、旧身份拒绝；新open不能清旧pending或假复用原H|
|R01 grant准入|opaqueTask缺/非法或能力不满足|旧构造OUTPUT_GRANT_INVALID或OUTPUT_CAPABILITY_UNSUPPORTED，错误来源按实际门；owner未准入/不产生不明副作用|
|R02 fileKey缺失|候选JDK适配端口报告无法提供其所需物理身份|稳定拒绝/能力不足，无READY/COMMIT；不以path/hash/mtime补身份。确切候选code待正式源，不发明IDENTITY_*公共码|
|R03 替换物理对象|相同path、相同bytes/hash/length/mtime，换成不同原物理对象|宿主同grant权威在reopen/validate/commit边界拒绝；内容hash相同不能假同文件；若端口无可观察身份即BLOCKED而非PASS|
|R04 grant/版本替换|物理内容相同，但实际绑定的task/事务/token/generation/lease之一被替换（仅opaqueTask访问器后改值不重定向原快照）|按原边界拒绝旧响应/错误authority；SDK旧接口无的字段由已批准宿主broker内部原记录证明，不补造SDK字段|
|R05 硬链接不支持|需要硬链接的适配器明确无法支持发布能力|发布前拒绝或同原任务明确NOT_APPLIED证据；不静默退化copy覆盖/换目标。异常类本身不证明无副作用|
|R06 结构校验失败|同grant读回byte/hash合格，但真实格式验证失败|OUTPUT_VALIDATION_FAILED/不READY；摘要相等不代容器、内容、AV同步或遮罩合格|
|R07 validator替换|已进入原validator后换另一个对象继续|旧OUTPUT_VALIDATOR_IDENTITY；原validator尚未归还继续保管，不用新future顶替|
|R08 token/终态冲突|QUERY/原READY晚ACK给不同token、READY↔ABORTED或终态回退|保留原终态、raw收到与accepted分开；OUTPUT_INVALID_HOST_RESULT/协议UNKNOWN不清，不能“修正”第二RPC|
|U01 提交响应在途|实际发布，原COMMIT stage仍pending；宿主只读QUERY先见已提交|宿主真实结果可记录COMMITTED，但旧SDK不能仅凭SinkCoordinator.READY或零计数释放；pending/原observer/worker未返继续持有|
|U02 COMMIT未知|调用进入后抛异常/响应取消/超时，副作用不明|OUTPUT_COMMIT_UNKNOWN与firstFailure保留，无重放、退款、abort删除；仅同原Commit.originalOutcome(task,token)可消歧|
|U03 明确未应用|原COMMIT实际返回、同authority确认NOT_APPLIED|旧CONFIRMED_NOT_APPLIED可归还但不committed；不是把失败变成功，也不自动重试|
|L01 晚回|原COMMIT晚返回成功/失败，或readonly原结果确认COMMITTED|同原任务采用允许事实但首错保留；必须原响应、observer、原worker真返，不能只改业务counter|
|L02 READY/取消|取消先赢、READY原响应后到，或READY先赢再取消|按Sink05不可逆门；ABORTED不能接纳矛盾READY，READY不能取消成ABORTED或删除输出|
|L03 callback尾段|response/view done、计数0，同observer/SDK worker尾段仍活|OUTPUT_ORIGINAL_PENDING，keeper未释放；只在同原尾段实际返回/join后归还|
|S01 多consumer|第一consumer已close、另一consumer/read/close仍pending|租约整体未released；宿主不得安全移动源。FS偶然允许rename不代租约门通过|
|S02 旧代晚读|源换代后旧read晚返|原缓冲/票据照原返；不写新caller、不重新准入旧generation，不清旧UNKNOWN|
|P01 平台效果|Android FD/真实fsync/codec/muxer、隔离安全、格式/AV同步|本机端口测试不可签这些PASS；无准确平台证据保持NOT_RUN|
|P02 恢复|本批宿主记录重建+同事务只读QUERY|仅有限本机记录恢复；不得冒真实应用崩溃持久性、跨进程原任务已返，或重放COMMIT/扫目录猜身份|

建议独立证据分栏：A原身份/同grant链；B真实写读与内容/结构；C逻辑结果/原firstFailure/UNKNOWN；D原stage/observer/线程/句柄归还；E调用次数及保留预算。缺任一必要栏即FAIL/BLOCKED/NOT_RUN按准确原因，不以“测试跑完”代候选通过。

旧原接口没有独立physicalFileId/transactionVersion公开字段，不能让旧受控端口编造这些字段求绿。必须先核新冻结宿主实现到底提供何种可替换平台能力以及本机实际可测范围，再把表绑定到真实入口；不穷举无限排列，不机械重跑已接受Sink05所有旧套件。
