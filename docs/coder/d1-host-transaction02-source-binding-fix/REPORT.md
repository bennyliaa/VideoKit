# D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX 整批交付

2026-10-24。**源码task/同原authority集中修复完成；开发一次编译+串行worker取得有限PASS，待独立整包B。** 实际原8个文件集成、3个受影响authority回归、4个新增矩阵组通过；最终SDK/host/source owner均0且原返回门成立。不代Android/D1通过，M0未启。

## 正式来源与历史保持

按D1_HOST_TRANSACTION02_SOURCE_BINDING_FIX_CODER_REQUIREMENTS_V1.0.md新批执行，工作前核最新设计/协调顶部。第一次正式单读取之前，同一工具调用已测monotonic **390109.781**，UTC **2026-10-24T04:02:31.945958+00:00**，45分钟截止counter392809.781/UTC04:47:31.945958；first-read-clock.json保留原值，不前移猜测、不从prepare重启时限。

旧01完整候选manifest4350de4c1296c221508ea2cba23e5dc20b628d7536add1ca736462cdcc30bffe，262项冻结保持。原独立B报告08781fabff3344242280f82050e46cb6e92a0abff5fb87e66111b672d0610380/manifest96f7c3939ea434a87b4503bd1e48019a010b85c602448509afd9f6d90202b5ad整包静态F01 FAIL保持；该B的8+3正常环境有限PASS不补旧两开发FAIL。原F01未动态注入错源/错误移动，不能将本新证据回写成旧批实际越权。

新目录仅docs/coder/d1-host-transaction02-source-binding-fix。复用01真实FIX02生产JAR、原SDK/SourceLease/Media3 API及原依赖，没有修改旧01、FIX02、Sink05、SDK核心或旧事务/UNKNOWN。没有新身份注册表、资源权威、SDK Identity接口或通用事务框架。

## 四处生产/测试变化

1. **Binding**：增加不可变sourceTask快照、private原E13SourceGroup和原Identity引用；保留原uid/pid/instance/epoch/generation及事务/grant/outputVersion。requireSource先核准确字段，再核原group/Identity引用；require同样逐字段+原引用，不能让新registry generation1或相同字段新authority充当原源。
2. **私有key/LocalFormat**：HTB2按版本、长度前缀、精确UTF16 code units和固定整数编码后Base64，包含sourceTask，不以分隔符字符串拼接或损失性编码授权；本私有key上限2048字符，超界Binding构造时拒绝，以守原4096B record有限界，不改变SDK公共SourceIdentity。VKH2帧包含HTB2 key，旧VKH1拒绝。
3. **LocalTransaction record/消费门**：HTX2头与旧HTX1拒绝，不迁移/读取旧原事务；constructor原requireSource在目录/host注册/原writer前，move原require和source authority门在实际源IO前，RecoveryRef原require在业务query/record读接纳前。增加sourceMoveIoAdmissions仅为分支诊断，不取代原source状态或资源归还。
4. **有限自检矩阵**：SRC_A/B只变task、同字段不同authority、编码/旧版本、原opaqueTask快照四组；原8+3入口保留。准确逐文件前后hash和patch在evidence/preparation.json/diffs，实际编译输入及源ZIP在attempt01，不以旧源码编译结果冒末源码。

authority引用不会序列化成伪造权限token。不同原authority可拥有同一字段编码，但live typed require/构造/移动/RecoveryRef均拒绝，key只作数据身份。合法同原group新Binding wrapper仍允许，防止把“同原authority”误收紧成“必须同一个Binding包装对象”。

## 实际新增矩阵

|组|准确实际调用/观察|
|---|---|
|source_task_matrix|原group A.task=SRC_A、B.task=SRC_B；uid/pid/epoch/instance/generation1其余相同。Binding key不同，requireSource及实际LocalTransaction构造拒绝；错误输出root不存在、host owner不增。A/B实际排空后，错Binding移动与readonly RecoveryRef拒绝，source/target及record不变、产品IO/query接纳计数不增；同原authority wrapper/正确QUERY和真实move通过。|
|source_authority_matrix|task及所有身份字段同值、两个原group/Identity引用不同，字段编码相同不授信。requireSource/require、实际构造、排空后移动/恢复都拒绝；generation1不能替代原authority。|
|private_encoding_matrix|task="SRC\|A"/instance="B"与task="SRC"/instance="A\|B"不能拼接别名；正确格式通过、错key实际LocalFormat拒绝。VKH1头拒绝；共享production requireRecordVersion拒HTX1，正确HTX2通过。旧record部分是纯header输入，并非读旧事务或复活旧Capture。|
|original_task_snapshot|实际委托HostOutput访问器改label，SDK仍持构造时准确原task/grant；新sourceTask/key快照不改，真实写/close/reopen校验/READY/COMMIT/QUERY完成，未改SDK字段或从访问器重定向授权。|

错误调用直接进入本候选原方法，由产品Binding门抛既有SOURCE_IDENTITY_REJECTED/OUTPUT_GRANT_INVALID，测试驱动没有预先拒绝以代产品。移动/恢复“前IO”依据原门顺序、产品接纳计数0和实际文件前后快照，不冒独立拦截全部OS读写。无反射改原状态或伪造资源归零。

## 原功能与回归

原8个real-file case：正常原内容→READY→一次COMMIT、原record只读/发布可读及源move；真实坏数据不READY；cancel-before-ready；目标已存在真实move失败NOT_APPLIED；原ACK失败UNKNOWN保管后同原readonly query；业务已提交/ACK与线程尾段分层；双consumer未排空不move；旧epoch晚到4B不覆盖caller。均通过。每case writer原close1、COMMIT≤1，源/host原任务/相关observer与callback原线程归还由同原SDK门核；UNKNOWN/首错不清、不补ACK/退款或二COMMIT。

另调用原IndependentAuthorityCheck.main的publication(false)、publication(true)、terminal三场景，全通过。其明确controlled host port不是新真实文件case；18份旧check源码只是为引用完整编译，并非18项已运行。summary的passed12=8原real-file+4新增矩阵，另affectedFrozenAuthorityScenarios3；合计15有限组，不能把内部断言或旧A oracle再相加冒更多独立场景。

最终SDKOwners/hostOwners/sourceOwners均0。TemporaryOutput实际来源lib/fix02-production.jar（原SHA f246fff1e4faebbc05279283f47ca264523b4bf87ff1491c198c814352b1719c），DataSource来源真实lib/media3-datasource.jar；生产JAR只含com/videokit/d1hosttx，不造同名Media3/SourceLease接口。原三个Android平台fixture只作JVM端口。

## 准确运行与预算

一次准确固定本地命令经工具require_escalated自动审核执行（tool chunk56c105 exit0，外层9.7397117秒）；未在受限/外部间来回探针，无管理员、ACL/防护修改或换目录绕审核。compile3.984秒/exit0，单worker2.016秒/exit0；两子进程constructor/wait/原H及stdout/stderr文件close均返回，无超300秒/未知原对象/强杀。没有第二编译/worker或使用修复轮。

order.json在任何Popen前冻结完整src/lib hash、准确argv/cwd/executable/三流/shellFalse/close_fdsTrue及显式冻结env。两进程相同env hash **2bf2e17ca1ed8feafae09d893bdf4e920d74c5fff4abd169bc137173cb2206ed**；实际Popen使用该私有copy，环境原值不入档、不改全局环境。父进程/tool外层返回与子回执分开，未伪造创建FILETIME或API拦截。

prepare具名读预留13,669,395B（含前置具名console8MiB保守预留、实际console长度不冒精确值），复制5,129,724B；runner读15,999,600B。runner result快照写预留4,504,112B在最后result之前，工具终局4,513,778B包含9666B result，无退款。编译class、真实样本/见证和静态seal/hash另按文件树分账，最终账及32MiB界见batch-ledger/receipt；不冒全OS/JVM隐式页读全计量。

正式45分钟截止沿首读前原counter；读512MiB、永久输出32MiB，样本8MiB/源2/块64KiB/输出payload16MiB及每子观察300秒未扩。源/输出/见证只为本批新scratch文件，未碰test_media或真实业务数据；原sample/hash/身份前后由当前有限case观察，不签任意攻击者的路径环境。

## 明确未测/不关闭

VKH2是生成的有限本地文档，不是MP4；HOST_ISOLATED_FORMAT_V1为原受控validator tag，不签Android隔离进程格式/RCE。只读record恢复限当前已知事务的原reference/Binding，不是真正应用崩溃、数据库/跨进程恢复，未补旧COMMIT。原API/格式字段及错误版本约束见API_MAPPING。

R03同字节物理对象替换、TOCTOU/原FD竞态/隔离攻击未运行，task修复不宣布关闭这些边界；旧文件读取不变/正常见证通过不升级race-free身份。SDK/ADB/TCP/设备/媒体回归、网络、Gradle/Android构建、Git及旧PID/锁/once/UNKNOWN查询改写0。压缩音轨/AV同步、M0、完整产品持久化和发行清权不扩。

## 完整冻结与交接

源码/API/编码差异、原库/许可SBOM、真实JDK JAR/class/源ZIP、完整case与原进程流/返回及预算一次冻结。manifest列准确文件/长度/hash，seal与delivery/notification收据外置防循环；静态后验复核当前输入与实际compiled inputs相同，旧01源/库固定摘要保持。未以本开发PASS自行关闭原独立F01或自动进入B/设备。完整包主动报负责人，待一次独立整包B；D1未过/M0未启，主阶段/Flutter/独立Kit/原许可/P0及历史FAIL/UNKNOWN保持。
