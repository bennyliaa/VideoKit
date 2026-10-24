# HOST_TRANSACTION02_SOURCE_BINDING_FIX 独立整包B报告

2026-10-24。**PASS_LIMITED：F01在本候选实际task/同原authority构造、移动与RecoveryRef门限定关闭；未发现新增阻断缺陷。** 一次严格编译、一个串行worker实际8项原文件集成+4项新增矩阵，另3项旧authority回归通过，共15个有限组。不是21 oracle全通过、Android或D1通过；M0未启。旧01静态FAIL及此前开发失败/未证保留。

## 准确来源与唯一执行

正式单`docs/tester/D1_HOST_TRANSACTION02_INDEPENDENT_B_DISPATCH_V1.0.md`与其中合并的独立要求。候选`docs/coder/d1-host-transaction02-source-binding-fix`，manifest `9c97568ec615e0d1528701355540eb99a5315aaaaa21f85c44896ba5ab4603b0`，227项6249370B动态前后逐项核同；REPORT `7d7b3e18129f42540f0c4e6cf710d412f91fb172839568cbc6e6427732981c53`、seal `ceb664e215fe8566815d1ad865b5aa0f90e0b8efdf1585765a0065b066a5fc26`，runner `077654df91d2027cabff925c95362073614f5631c1faab696b34f71db4fe0681`核同。

运行前记录准确源/完整命令/cwd/环境语义/三流/预算；`b-f924a731` leaf事前不存在。唯一固定bundled Python `-I -X utf8 -B <准确run_batch.py> --output <正式新root>`经工具require_escalated自动审核允许，tool f85c50/exit0/9.929秒。未使用--attempt、旧scope、额外探针、管理员/ACL/防护改动。

原图parent+compiler+worker=3、串行1/retry0；编译5.047秒/exit0，worker2.172秒/exit0，未超各300秒观察。原Popen/wait/H及两个流文件close分别记录返回；parent工具终局另记。未重编译、第二worker、补新case或改冻结源。

## F01实际关闭及同原authority

Binding不可变捕获sourceTask、private原E13SourceGroup与原Identity引用，保留uid/pid/instance/epoch/generation、事务/grant/outputVersion。requireSource逐字段核task及全部原字段，再核原group/Identity引用；require对Binding也逐字段+原引用，不靠key相等授信。

|实际新增矩阵|原消费者与有限证据|
|---|---|
|source_task_matrix|SRC_A/B仅task不同、其他源字段与generation1相同。直接调用LocalTransaction构造取得SOURCE_IDENTITY_REJECTED，错root不存在/host owner不增；原A排空后错Binding实际move和原RecoveryRef.queryReadOnly取得OUTPUT_GRANT_INVALID，产品IO/query接纳不增、原source/record不变。|
|source_authority_matrix|两个原group/Identity所有字段同值、序列化key相同，实际requireSource/require、构造、move与queryPublication均拒绝；后者直接进入原RecoveryRef门。generation1/同值key不代原authority。|
|private_encoding_matrix|task/instance分隔符碰撞样本不能别名；生成/正确解析VKH2通过，错误Binding key与VKH1帧输入拒绝；共用生产requireRecordVersion实际拒HTX1头，HTX2头通过。|
|original_task_snapshot|实际HostOutput包装访问器改label，SDK原task/grant快照不重定向；仍真实完成写闭重开/校验/READY/COMMIT/QUERY，sourceTask/key快照不变。|

独立核测试源：分立的直接requireSource断言后仍另外实际调用产品构造、move、RecoveryRef，不是驱动先拒后省略消费者。产品构造首部requireSource位于目录/host注册/原writer前；move的require/requireSource在sourceMoveIoAdmissions与文件IO前；RecoveryRef.require在businessQueries和record读前。原接纳计数、实际文件/record快照与源码顺序共同支持有限“读写前拒绝”，不冒全OS拦截。

合法同原source的新Binding wrapper实际通过正确QUERY与move；并不要求同一个Binding包装对象。旧opaqueTask后改标签正例保持，修复没有把所有字段标签变化一概拒绝。新同值authority负例补到旧01未动态执行的边界，但不回写旧01为曾实际注入错源。

## 编码及所有记录消费者

HTB2：版本magic、字符串int32长度前缀、逐Java UTF16 code unit、固定宽整数，再Base64；包括sourceTask，无分隔符拼接别名。私有encodedKey≤2048字符门保持。机制静态可核，实际跑的是有限分隔符样本，不冒NUL/孤立surrogate或全长度边界穷尽测试。

key只表示数据身份，authority原引用没有被序列化成权限token。LocalFormat生成/验证使用VKH2及完整key；LocalTransaction.saveRecord写HTX2，RecoveryRef解析使用同一版本门并核key/token/bytes/hash/文件身份。独立纯文件后验核10份实际record的HTX2/HTB2、长度与源绑定；另核10份已发布或移动后原文件：完整SHA/长度、VKH2、key、body长度/hash与全EOF一致，未调用产品或启动新fixture。

旧HTX1负例是共用生产版本函数的纯头输入，不是重开旧历史事务文件；没有记录迁移、重新COMMIT或复活旧原对象。当前恢复仅原已知RecoveryRef/Binding的同原可知记录只读，不能由Base64或磁盘记录重建同原source authority、不能冒真正跨进程/崩溃持久恢复。

## 原8项与3项回归

原实际normal提交后可读/只读record/错version拒绝/源move、实际坏内容不READY、取消前置、已有目录目标发布失败、UNKNOWN后原readonly query、业务已提交但ACK与尾段未返、双consumer移动门、旧epoch迟到4B不覆盖caller均通过。每适用case写者close1、COMMIT≤1，原首错/UNKNOWN保管/物理归还分层。

publishOnce特定FileAlreadyExists且sameTemp身份仍成立才NOT_APPLIED；其他Throwable UNKNOWN，未因异常类泛推无副作用。该原异常处理源码与01相同，本B真实已存在目录拒绝及同原authority回归有限通过。原QUERY确认提交不等ACK/worker返，未重发COMMIT、取消成ABORTED或退款。

旧IndependentAuthorityCheck.main仅publication(false)、publication(true)、terminal三项实际执行，受控host authority与新真实文件case分栏；18份旧check编译不计18项运行。summary.passed12=8+4，另authority3，内部断言与A21 oracle不累加。原SDK/host/source owner最终均0；原group排空与线程返回由同原SDK门和原断言/日志证明，非JVM退出或数量替身。

## 产物、依赖与环境

39项实际源/库/runner输入与27源码ZIP成员独立核同，原candidate227项前后无变。生成生产JAR9成员，SHA `99e7fc785b1e276072dd5af0733e9b443087d76806446b7b8100e98e8b33fb45`；测试JAR85成员，SHA `295be2c9e4ab16e3e88b40b41bc8ca20815b16aa16745966757506a37bf2ae83`。原SDK/Media3 shadow边界核验与实际class origin明确：TemporaryOutput仍来自固定FIX02生产JAR f246fff1…1719c，DataSource来自真实Media3库；所有11个库与01逐hash相同，无依赖升级/新许可或SDK核心改写。

JBR一次--release11严格编译，未Gradle/Android构建。真实本地硬链接见证/文件I/O为本准确审核范围，不笼统声称OS Native0。该成功不证明所有Windows/JDK均支持身份/硬链接，也不解除R03。

order.json在任何Popen前保存完整39源pin、argv/executable/cwd/三流/shellFalse/close_fdsTrue及显式private env copy摘要。两进程本批env SHA均为`c8066178ecb68c2f21d41e5236410dc03450ffaed79b0dccec29b2e451aed256`，回执exactSpec与冻结order逐项核同；这是父进程实际传入copy及其摘要，不冒child自报OS环境块逐字节拦截。敏感原值未入档，无全局环境修改，也不挪用开发另一tool的env摘要。

## 21 oracle与未测边界

preflight/oracle-coverage.json逐ID映射：N01/N02/N03、U01/U02/U03/L01、S01/S02有限实际覆盖；R04新增task/同原authority/合法wrapper/原标签快照补齐F01，其他grant/uid/pid等字段并非全部新增孤立负例。R01/R02/R05/R07非法能力/当前不支持身份/硬链接及替换validator未新增动态例；R06实际坏bytes及错key/旧帧输入不等所有媒体坏格式；R08/L02/L03保留当前实际取消/host尾段/旧authority query尾段与未重测的完整READY冲突/SDK零counter尾段边界。

**R03同字节物理替换、TOCTOU、原FD竞态和隔离攻击仍NOT_RUN/不关闭。** FileIdentity/OwnedFileProvider与01逐文件hash相同，不把task/引用修复冒物理身份攻击防护。VKH2是固定生成文档，非MP4；HOST_ISOLATED_FORMAT_V1是旧受控能力tag，非Android隔离格式/RCE或真实AV同步。P01平台效果NOT_RUN，P02仅本机已知原reference记录读取；压缩音轨/应用持久恢复/跨平台不扩。

## 原费用与本批保全

runner读预留22295242B；最终永久写4514058B，等于原result截点加准确result文件长度，未回写截点或退两子双流4MiB预留。原输出树956990B，result之前947226B，差9764B为原result。静态/事后读预留32MiB、编译已声明输入保守64MiB另域，合并业务读取上界122958538B<512MiB；不冒OS/JVM隐式页读全计量。class/样本/见证等按实际树另加保守写域，连静态报告/封存<32MiB，完整计量见delivery-receipt与manifest。

首读工作单前同工具调用已记录实际Stopwatch tick/frequency与UTC，timing-end核1200秒界，不从runner或prepare另起计时。动态单样本≤8MiB/源2/读块64KiB/payload16MiB原限制不变；原创建/wait/流/H close从准确原回执核，不虚构未采的creation FILETIME/API拦截。

一条事后纯文件分析命令误用只读HOME变量，写出审证文件前停止，改为taskCaseHome后完成；未修改任何原测试源/结果或产品文件，未启动第二worker，记录在independent-payload-audit。此分析修正不计新增产品case或动态修复。

完整证据在`docs/tester/D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX_REVIEW_EVIDENCE/b-f924a731`及同前缀preflight，manifest含原stream/返回、源码ZIP/JAR/class、真实样本/见证、静态审阅与本报告。F01本批限定关闭；旧01及所有历史FAIL/未证/once/UNKNOWN不改。本B完成停止，完整回负责人，不自动设备测试或新修复。D1未过/M0未启，主阶段/Flutter/独立Kit/既定许可/P0保持。
