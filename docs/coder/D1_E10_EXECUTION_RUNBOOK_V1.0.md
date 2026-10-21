# D1 E10 条件执行手册 V1.0

本手册是未来正式actor1派单的精确操作映射，当前禁止执行。P1收尾缺口未处置前不将本包记为READY。无新的执行器、服务或后台任务；只使用冻结E9B HostManager和E9PcClient。

## 正式派发与输入落盘

负责人采纳新终局策略及独立E10审查后，签发本批ACTOR1 scope和实际执行派单。派发者/受托tester只生成一次新registry UUID、migration UUID、attempt UUID、handle UUID，四值唯一，不能复用任何旧scope/旧actor。目录布局docs/tester/D1_E10_EXECUTION/<新M>/inputs（scope/plan/config/commands/index）、同级registry（初始必须不存在）、evidence（原命令/响应/统一台账）。只在本机预存，不预先填actor PID/boot/start或创建device目录。

将scope模板转为scope.json，status=ISSUED_FOR_EXACT_ACTOR1，补issuedAt、真实executionDispatchEvidence和acceptedE10ReviewEvidence的path/bytes/sha256，acceptedE10ReviewSha256等于实际审查原文件SHA；记录authority来源。scope只绑定动作/固定制品/新UUID/限额，不能包含尚未产生的config/hash或H_actor，以免循环。正式派单可授权受托tester按已审模板一次落盘和归档，不另造用户批准。

逐个去除templateOnly外壳，仅取wireFields。所有E9 canonical规则：ASCII，顶层e9=1/fields，fields键字典序、值均字符串、紧凑JSON、仅尾部一个LF；禁止BOM/CRLF/重复字段/空白重编码，SHA取原始字节。prepare-plan填新registry/migration，authorization=实际scope原字节SHA，sourceReview=接受的E10原审查SHA；config.plan为该canonical plan的URL-safe base64去padding，planSha精确原SHA，authorization同前，review同sourceReview，head=NEW，registryPath为同级新registry绝对正斜杠路径。originalApp/Test/Version/Role/Abi固定已核E9B pair/13/PREPARE/1，现场不同即不启动。

commands依模板生成10个canonical文件，仅LAUNCH填新attempt/handle。input-index.json记录scopeSha256及scope/plan/config/preflight/全部10命令的path（相对于项目根）/bytes/sha256，index本身不列入自身files，不形成哈希循环。正式config和命令生成后原字节唯一，不在已发未知后重新生成或变seq。核验命令：Python -X utf8 -B docs/coder/d1e10/tools/validate_package.py --bound-dir <新inputs绝对路径>；校验器只读，不能签发scope或收集现场。

## 启动前实际现场预检

执行者以真实设备只读元数据客户端采集并保存原argv/起止/exit/stdout/stderr/两reader返回/字节SHA；全部在新scope派发后、启动前、同一会话内。现场值变化则重新审现场，不能用本包历史值作receipt。preflight.json格式由validator.bound明确：status=COMPLETE_CONTEXT_REVALIDATED、sessionRegistry、observedAt、serial/user/UID/版本/role/ABI、installedPair（与已核本机制品row对应的**当前设备实际摘要**）、relatedProcessPids=[]、ownerId/leaseId/fence、oldOutputBytes0、consumed/reserved、九个生产前置元数据断言和rawEvidence非空pin列表。所有true须有原始观测来源，不是照抄模板。

1. 实际设备serial HA1Q6WXR，user0、机型/API31正常，包user状态/UID10221及10222/版本13/角色PREPARE/ABI1、签名和当前pm path重新查询；按当前返回路径sha256sum两base.apk，不能用旧随机/data/app路径或只核证书/高版本。计划不安装；不同pair/相关app或worker进程仍活→停止，不force-stop。
2. 对固定13项原metadata清单（E9LegacyProfile.IMMUTABLE逐项）进行有界role/lstat/原字节SHA核对，guard owner/lease准确dev/inode/UID/size/fence、路径无symlink、原0B输出只stat/零内容；保留后续53651/53567媒体文件，不读取非零媒体payload。元数据工具若有能力/权限差异集中报告，不能临时写探针或扩大scope。
3. 完整ledger ≤131072B且1011B前缀固定，完整hash chain/R/S合法、旧三R三S未改、reserved0、总<=4MiB；禁止只核前缀便忽略后缀，合法settled后缀交本次scope审查，不删回1011B。operation.pending缺席，旧ABORTED档案及closeACKfalse不动。现场元数据预检不是持有旧guard等待外部批准；生产COMMIT仍会在实际guard/ledger排他保护下重新验证，预检不能替代它。
4. 新M目标必须不存在；legacy-acceptance不存在或为空，不能有其他M；外部新registry不存在，只有其父目录及inputs/evidence。生产transaction白名单仍是最终门，不预mkdir/device占位file。实际相关进程/既有pending/未知原资源一律不进入EXECUTE。
5. 按生产固定logcat -d -v brief -s E9_MANAGED:I ActivityManager:I *:S有界观察系统日志容量，生产CAPTURE_FINISH总1MiB。需留足新会话增长余量（建议观察≤800000B，非可保证的增长界）；过界阻断，不能logcat -c、tail剪裁后伪称生产原日志。归档系统日志和metadata内容只存本机；不导出视频。

独立metadata客户端上限20，各有有限响应与真实退出/reader收尾账；超界/UNKNOWN停止。status=COMPLETE只是可信执行者基于原始证据的记录，Python校验静态绑定不冒充实际设备观察。boot/PID/start在新actor身份采样时取得并独立核，旧boot2/PID17434/start16410590一律不可填写为新值。

## 原生产管理器正常路径

未来命令argv为 D:/Android/Android Studio/jbr/bin/java.exe -cp <固定E9B host JAR> com.videokit.spike.e4.E9HostManager --approved-session <新canonical manager-config.json> <该文件SHA256>。当前不执行。保存原Java进程、stdin和两reader；不要shell拼接整串，逐项argv。Manager NEW创建外部descriptor/authorization-reference/prepare-deployment/events，原Store已由同一custodian持有。无DEPLOY_PREPARE命令，现场exact E9B pair是启动前独立前置门；Android自身version/UID/signer门不替代设备实际APK SHA核对。

严格按条件逐条送stdin，**不能把10条命令一次喂入**：

1. LAUNCH显式REGISTERED_MIGRATION、ordinal1、SYSTEM_BOOT_COUNT、新attempt/handle；生产am instrument -r无-w，旧批标签D1-E9A-PREPARE-TABLET-20261018保留。该模式允许未来一次EXECUTE，不得用只读旧actor升权。启动client返回不表示actor结束。
2. POLL（Android STATUS seq1/state=-1）取得完整transport/actor/returned。原五秒任务内已做语法/result/模式/UID/PID/handle/seq校验；外部核identityNanos<10s、verdict IDENTITY_QUALIFIED、phase IDENTITY、unreturned0、executeDone=false/device ABSENT/真实身份FD返回、正确新scope和exact pair；独立ps/boot_count/proc新PID stat核原boot/start/UID。无合格原actor回执，不执行RESERVE。
3. RESERVE predecessorIntent=NONE，生产归档原identify，生成唯一reserve.json并追加BOUND。核原registry真实返回、原文件原字节及事件head；此时只有外部记录，未写device三文件。此切点若必须停而EXEC尚未发，触发本包P1出口缺口；隔离，绝不为了收尾强行EXEC。
4. 唯一CONTROL EXECUTE_COMMIT（seq2，state取原最新稳定snapshot）。原manager在广播前先持久化command intent再计seq；Android先bind/reserve再排原execute，资格从该原reserve开始10s且不因排队/查询延长。主机广播响应5s内包含原解码。即使回包未知，也不得更seq重发EXEC。
5. POLL seq3；如果仍在途，最多再一次POLL seq4（STATUS总3），按原开始时间采集；永久PENDING不变成功。可提前安排有界时间点，例如EXEC回复后首次观察、距原execute开始近8秒但不超过有限观察账的最后STATUS；不靠无限poll求PASS。只有原returned phase COMMIT、executeDone=true、unreturned0、safe=true、QUALIFIED_MIGRATION且identityNanos/executeNanos均<10s、deviceRecord精确绑定的原字节可进入正常终局。
6. ARCHIVE_RETURN原COMMIT字节，验证actors/0001/returned.json精确原SHA。唯一CONTROL ACK_FINISH（无追加STATUS时seq4，否则seq5），精确同handle/state/已归档原return hash。ACK未知禁止再发，不用finishClaimed或client exit代替正常finish。
7. CAPTURE_FINISH生产独立ps排除原PID、固定原系统日志唯一E9_FINAL_FINISH锚点及finished inst/Killing对应原代次，存finish.json/event。该Killing是OS正常finish日志，执行者不得发kill/force-stop。归档日志≤1MiB。
8. 独立审计新三控制文件的精确字节/intent actor与reserve hash、原legacy/ledger守恒及无在途/未知，保存当前元数据原receipt；这才允许SEAL_FINAL。该命令产出真实catalog、checkpoint、final seal和head，当前模板不提前填任何H_actor；再独立重算DAG并冻结外部final。PREPARE仍无grant。
9. INSPECT原head。关闭原stdin，原custodian须实际pcClosed、原Java自然exit0和两reader返回；STATUS回复中的allOriginalsReturned可能包含当前accepted Socket，不能忽略它或补无限查询。所有原责任必须真返，不能用控制器terminate假结束。

统一账在evidence之外不侵入registry20文件白名单。记录每条意图原SHA/seq/handle/response/deadline/已知未知及原任务，未见响应仍计已发。计划Android控制4条（STATUS/EXEC/STATUS/ACK）或5条（加一个STATUS），<=8/STATUS<=3，EXEC/ACK各1；本机STATUS/OP/CLEANUP累计<=16共用原accept128，建议常规只2连接并为收尾保留。原Process最多96，metadata客户端<=20，系统日志1MiB；无预算重置/换端口。总预算不足、日志过界或原资源UNKNOWN即停在该分支，不能靠新manager/安装/actor2恢复。
