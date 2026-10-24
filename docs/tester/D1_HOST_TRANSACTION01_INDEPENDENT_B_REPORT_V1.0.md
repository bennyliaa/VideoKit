# HOST_TRANSACTION01 独立整包B报告

2026-10-24。**整包FAIL：F01静态确认，Binding未绑定/比较原source task，存在同源授权身份遗漏。** 唯一一次独立运行严格编译及8项真实文件集成+3项旧authority回归全部通过，原owner归还。原runner result.json的PASS不改；功能用例跑完与候选整包验收分开。D1未过/M0未启。

## 准确候选、执行与历史

正式派单`docs/tester/D1_HOST_TRANSACTION01_INDEPENDENT_B_DISPATCH_V1.0.md`。候选`docs/coder/d1-host-transaction01`，manifest `4350de4c1296c221508ea2cba23e5dc20b628d7536add1ca736462cdcc30bffe`，262项6589312B动态前后逐项核同；REPORT `4439364e2cf4d869ad2fa45bb46cb4e307535cf23b8d05ad064644a18490ec3f`、seal `3a043710d03ace21b1405763cd25179d432b5fa13a189dfbf25008e1f87e44b1`。准确runner `491ca24e787a9985d873e8583933c78e3d1b44f864a3245610949605a032ac41`。

唯一输出`docs/tester/D1_HOST_TRANSACTION01_REVIEW_EVIDENCE/b-e830d5c7`事前不存在；外部预检/事后审证只写同前缀`b-e830d5c7-preflight`与本报告。工具require_escalated自动审核允许准确原命令，tool chunk6c154d/exit0/4.915秒；未管理员提权、改ACL/防护、换目录或换源绕过。

命令为固定bundled Python `-I -X utf8 -B <冻结run_batch.py> --output <准确新leaf>`，cwd准确项目根，只review、无--attempt。先记录源码/完整argv/tuple/预算及env继承语义，再一次执行。冻结runner省略env，继承实际工具parent；预检记录的脱敏环境hash只代表预检时刻，不声称与后续tool实际env逐字节相等，不修改全局env。该候选没有env hash准入门，不能把这种继承语义冒HOST03显式环境验证。

主parent+一次编译+一次串行worker图3；编译2.578秒/exit0，worker1.235秒/exit0，原构造/wait/H及两个原流文件close记录均返回，未超300秒观察。没有第二worker、新case、开发第三attempt或修复候选。旧开发两轮失败/8+3 NOT_REACHED及原group DRAINED未证保持；本B新范围成功不补旧group归还。

## F01：source task遗漏（静态阻断）

准确文件`src/com/videokit/d1hosttx/Binding.java`：构造第10–14行从source.identity只保存instance/epoch/uid/pid及snapshot.generation；第15行key也不含source.task；第17–19行requireSource比较这些字段，**没有比较原任务task**。LocalTransaction构造与moveDrainedSource均调用该方法；RecoveryRef的binding.require亦沿遗漏task的key。

可静态复核的最小条件：源A/B uid=1、pid=1、epoch=1、instance="same_source"；两个独立新LeaseRegistry各generation=1；仅source.identity.task分别为SRC_A/SRC_B。相同事务TX/grant/outputVersion1时，Binding(A).requireSource(B)的每个现有不等条件均为false，且Binding(A)/Binding(B)的key完全相同。原SourceAdmission合同把task列为必需身份项，新绑定不能省略。

这不是把opaqueTask访问器后改值当替换：旧合同允许原捕获grant继续；F01指真正不同E13SourceGroup原任务的绑定缺失。原新case只在旧epoch场景同时改变task/epoch/instance，正常场景只改outputVersion，均不覆盖“其他身份相同、task单独不同”。

**本B未动态创建这组错误source，也未移动任何错误源；没有证明任意用户文件访问或跨进程攻击。** 缺字段及拒绝条件遗漏由冻结源确认，详细原hash/行号/纸面输入见preflight/static-defect-F01.json。建议用既有源身份权威准确保存/比较原task（或同原source authority），同步必要key/record绑定；不新建SDK身份/资源框架。修复须负责人集中派新批，不在本冻结源追加修改。

## 实际动态结果与独立后验

|本次实际范围|结果与证据|
|---|---|
|normal|真实本机临时文件写/force/close/授权重开/VKH1校验/READY/一次COMMIT；发布读取、record只读、错outputVersion拒绝、排空后源move及内容核验通过|
|validation_rejected|真实输出字节破坏被拒，未READY/COMMIT，原abort收敛、首错保持|
|cancel_before_ready|取消后不进入READY/COMMIT，临时输出处理与原返回通过|
|publish_fails|真实已有目录目标导致move拒绝；同原temp身份仍成立才CONFIRMED_NOT_APPLIED，commit1/abort0、首错保留|
|unknown_then_query|已发布但原ACK失败；UNKNOWN保管不重RPC，原可知record/原published只读核验后同原authority确认COMMITTED，首错不清|
|query_before_ack|业务QUERY见已提交时原ACK未返；ACK完成后原host尾段仍未返继续pending，放开同原尾段并join后才释放|
|dual_consumer_move|首consumer close不排空；原移源门先拒，第二consumer/read/close原返后才真实move|
|late_old_generation|原物理迟到4B实际计数但caller不覆盖；旧group实际排空后新epoch独立读及错误旧identity拒绝|
|旧authority3项|publication(false)、publication(true)、terminal原入口实际通过，原RPC1/同task-token及原query尾段/UNKNOWN首错保持|

后验核source-input-pins全部源/依赖/runner仍同；source ZIP每个条目与冻结准确源码匹配。生成两个JAR由新classes构建：生产9成员/SHA a6bdc3e6a0e112e41ece49ddc5f5dece11d8dcc57ffe9b60a862356659c097ae，测试84成员/SHA cb704aa7ccbd365377fe9d70e276cdb8812384973a8b2678179c9c052ef6b006；39项源/依赖输入及27源码ZIP成员独立核同，原SDK/Media3类来源和shadow边界核验见post-audit。实际TemporaryOutput ORIGIN为固定`lib/fix02-production.jar`（SHA f246fff1e4faebbc05279283f47ca264523b4bf87ff1491c198c814352b1719c），DataSource来自真实media3-datasource.jar；没有同名Media3替身。

runtime/依赖/JDK按冻结源与原runner读取pin复用，一次JBR严格--release11；未新下载/升级、Gradle或Android构建。VKH1只生成文档，不是MP4；HOST_ISOLATED_FORMAT_V1沿旧受控能力tag，不签隔离进程/RCE/Android媒体/真实AV同步。

正常与各失败分支summary最终hostOwners/SDKOwners/sourceOwners均0，逐例原host任务返回、写者close1、COMMIT≤1；case cleanup只放开已声明原gate并等同原线程，不因JVM退出假归还。本机新样本/见证文件保留，不操作test_media或真实宿主数据。实际保留16份`.hosttx-identity-*`见证，结合冻结分支说明本范围已走fileKey为空后的硬链接见证路径；不把它推广为所有Windows/JDK环境可用。

## 静态权威与21项oracle覆盖

A的21项与本B8+3不能相加当32项通过；准确逐ID映射见preflight/oracle-coverage.json。正常/COMMIT、有限未知/晚回、多consumer与旧代覆盖来自本次原运行；异常输入/身份替换等未跑者保留。

|oracle|本B裁定|
|---|---|
|N01/N02|ACTUAL有限正常与提交/发布/QUERY通过|
|N03|ACTUAL旧代排空及新epoch，非全身份字段独立负例|
|R01/R02/R05/R07|仅静态/NOT_RUN：非法grant、当前不支持能力、硬链接不支持及替换validator未新增动态例|
|R03|NOT_RUN：同字节物理对象替换/路径竞争；不能仅凭正常身份见证签攻击防护|
|R04|PARTIAL：错outputVersion/旧epoch实际拒绝；source task单独变化为F01静态缺口|
|R06|PARTIAL：字节破坏确拒；“授权hash正确但格式坏”独立负例未跑，格式门源码可核|
|R08/L02|PARTIAL/引用旧门：当前cancel-before-ready与提交后取消覆盖，不冒新测完整READY晚ACK冲突排列|
|U01/U02/U03/L01|ACTUAL有限原COMMIT未知/未应用/迟到/QUERY与首错、返回层次|
|L03|PARTIAL：原host尾段/旧authority query尾段实测；SDK零counter但worker尾段的独立A例本轮未另跑|
|S01/S02|ACTUAL有限全租约排空门/旧代迟到|
|P01/P02|平台NOT_RUN；P02仅当前可知RecoveryRef原记录只读，不是真应用崩溃或跨进程恢复|

原publishOnce只在特定FileAlreadyExistsException且sameTemp真实身份仍成立时记录NOT_APPLIED；其他Throwable为UNKNOWN。当前目标目录失败确覆盖这条有限分支，不能泛化所有FS异常必无副作用。原记录COMMIT_ENTERED+实际published/绑定/格式/身份成立可只读确认提交；没有再发COMMIT、改record或清首错。

FileIdentity的JDK属性/私有硬链接见证不降级为hash/path/mtime；但它围绕路径检查，并不暴露同一原FileChannel的H/FD元数据。当前是可信私有本地宿主，未做同字节替换/TOCTOU负例，**不声称race-free FD身份或任意攻击者文件系统隔离**。该项作为未证边界，不另冒第二确认源码漏洞或未授权实跑。

## 预算与证据边界

原runner读预留17503951B。result.json记录永久预留4473220B在最后导出前；加原result4127B得4477347B，与原工具终局输出一致。两子进程双流各1MiB，合计4194304B预留不退款；实际compile流0/0、worker4097/0。静态/事后读预留32MiB，编译已声明输入独立保守64MiB，合并业务读取上界118167247B<512MiB；不冒JVM/OS隐式页读全测量。

原输出树最终约827209B；准确全文件及生成JAR/源码ZIP/class/原样本/见证长度hash见最终manifest。runner预留不覆盖的编译class/样本等采用本次实际树整体另加的保守上界，连静态证据/报告也低32MiB；不因内容硬链接就按物理簇去重或退款。

首次派单读取未同时取tick，随后在候选核对前单调锚点保守前移60秒覆盖前置间隔；timing-end按该更早预算起点核20分钟，**不冒精确首次读取瞬间已测**。此流程记录缺口保留，保守时限核算另列。原创建/wait/close来自准确原runner回执，parent工具exit0另有6c154d，不虚构未采集的创建FILETIME/API拦截。

## 集中回交与停止

本B动态有限通过但静态F01阻断，完整集中交负责人安排修复；coder原两轮失败与所有旧状态不改，不追加第三开发attempt。本批无第二编译/worker/新动态case、SDK/设备/网络/Gradle/Git或权限/防护修改；真实JDK本地文件/硬链接I/O是本单准确允许的范围，不笼统称全OS Native为0。

原FAIL/once/UNKNOWN、旧05/capture1/N2及主阶段/许可保持；报告/manifest一次回交，不自动修复或进入设备测试。D1未过/M0未启。
