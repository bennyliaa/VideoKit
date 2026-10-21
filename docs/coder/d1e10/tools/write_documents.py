"""Write the four requested execution-package documents. No runtime or device execution."""
import json,pathlib,hashlib
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2]
if (B/'evidence/e10-freeze.json').exists():raise RuntimeError('FROZEN_READ_ONLY')
def put(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
def doc(n,s):put(R/f'docs/coder/D1_E10_{n}_V1.0.md',s)
plan=json.loads((B/'plan/execution-plan.json').read_bytes());pins=json.loads((B/'plan/external-input-pins.json').read_bytes())
put(B/'reference/E10_COORDINATOR_DISPATCH_SOURCE.md','''# E10 需求来源记录

来源窗口VideoKit项目助理，thread 01a107c3-2bf9-7fa0-94a0-234258ca6774；本窗口实际收到的E10整批派单，以下为范围摘录，并非新的用户签名或真实执行许可：

> 正式派E10精确执行包准备整批，不再新增一般设计/不重复构建：复用已核E9B生产APK/JAR
> 授权引用准确区分用户全权实现过程/恢复开发/永久设备授权与新策略scope采纳，不造用户批准文本/随机64hex token
> 发现代码/计划阻断则集中列出，不悄改E9B冻结
> 当前无ADB/设备/媒体/真实迁移写/activation

用户在本coder窗口实际给出的恢复开发、项目内负责人沟通授权继续有效。用户全权实现过程及永久平板授权在负责人派单和已接受tester真机报告中被引用；本包如实注明是这些来源的记录，不伪造本窗口未见的用户原文。E10准备派单不是对新终局写策略的实际执行scope签发；正式策略采纳由负责人在独立审查后记录于具体新scope与派单中。
''')
scopepath=B/'templates/scope.template.json';scope=json.loads(scopepath.read_bytes());scope['authoritySourceReferences']=['reference/E10_COORDINATOR_DISPATCH_SOURCE.md','reference/D1_E10_CODER_REQUIREMENTS_V1.0.md','reference/D1_E9B_READ_ONLY_IDENTITY_DEVICE_REPORT_V1.0.md'];scopepath.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
finding=dict(id='E10-PREEXEC-BOUND-CLEANUP',severity='P1_LIFETIME_EXIT_GAP',status='OPEN_STATIC_SOURCE_REVIEW_NOT_RUNTIME_REPRODUCED',trigger='RESERVE has durably created identify/reserve/BOUND; EXECUTE_COMMIT has NOT been delivered; operator must stop or PC operation fails',chain=['HostManager ARCHIVE_RETURN chooses captureIdentityForFinish for phase IDENTITY','Registry.captureIdentityForFinish rejects if actors/0001/reserve.json exists','CONTROL STOP_DEPENDENCIES preserves phase IDENTITY if executeReserved=false; PENDING is not a COMMIT return','ACK requires exact archived returned.json; direct creation or fabricated COMMIT receipt forbidden','Original remote/custodian remains retained; no safe normal-finish route through the frozen public CLI for this branch'],sourcePins=[x for x in pins['files'] if x['path'].endswith(('/E9HostManager.java','/E9Registry.java','/E9MigrationRun.java'))],handling='Quarantine and retain original custodian/actor, no EXECUTE merely to obtain cleanup, no kill/new manager/direct registry write/actor2. Coordinator+tester must decide minimal later-batch repair or explicit acceptance before write execution.',normalPath='Registered identity -> BOUND -> one actual COMMIT -> original COMMIT return archive -> exact ACK -> actual normal finish -> final remains statically expressible, but this gap prevents declaring the execution package universally closed.')
put(B/'evidence/static-blockers.json',json.dumps(dict(schema=1,findings=[finding],executionReadiness='BLOCKED_PENDING_INDEPENDENT_REVIEW_AND_COORDINATOR_DISPOSITION',deviceCalls=0,productionMutation=0),ensure_ascii=False,indent=2))
doc('DELIVERY',f'''# D1 E10 精确执行包交付 V1.0

本包是唯一原N2终局验收迁移的准备交付，状态 PREPARATION_ONLY_NOT_EXECUTABLE。未产生实际新registry/migration/attempt/handle、签发scope、现场预检、H_actor/catalog、设备写或activation。复用E9B原双APK/JAR，不构建、不编译、不运行旧通过套件。发现一个生产收尾缺口，列于static-blockers.json；执行准备结论为 **BLOCKED_PENDING_INDEPENDENT_REVIEW_AND_COORDINATOR_DISPOSITION**，不能由本包直接启动迁移。

## 四文档映射及机器输入

本DELIVERY负责范围/授权/来源/成本；EXECUTION_RUNBOOK负责可实际落到原CLI的条件流程、现场采集和统一账；FAILURE_AND_FINAL_REVIEW负责失败/UNKNOWN/actor2及独立final；ACTIVATION_INPUT_DAG负责后续独立发布输入，无预建包。

plan/descriptor.json是已冻结生产proposal的精确725B，SHA256 4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb；plan/expected-commit.json是同一算法的244B固定期望字节，二者不是设备提交或授权。execution-plan.json列固定旧事实/新增白名单/额度/不生成身份状态；templates列实际managerTrust/preparePlan字段与逐条命令的未实例化模板，带templateOnly外壳，**不可直接交生产CLI**。外壳不是新协议或执行器。

## 授权来源与生效

用户原有全权项目推进、恢复开发、永久平板授权属于项目/设备层权限；具体新旧N2终局策略、指定三文件及一次写actor须由负责人在E10独立审查后正式采纳并派发。来源分别见reference/E10_COORDINATOR_DISPATCH_SOURCE.md、正式需求、已接受真机报告；对于其他窗口用户原话，本包仅引用负责人/报告的记录，不伪造签字或逐字用户批准。E10准备派单本身明确禁止设备/写迁移。

scope.template.json保持DRAFT_NOT_EFFECTIVE且实际身份、签发时间、正式派单和接受的E10审查SHA均null。正式派发时负责人签发具体scope，受托tester可按派单记录其精确文件及来源，由实际负责人派单承担策略采纳；身份只生成一次并存原字节。scope的SHA256是这些真实字节的绑定，直接供生产Trust.authorization引用，不是随机64hex token、密码、资源返回证据或产品准入。原只读scope的授权SHA不可挪用，E3已耗许可不能重用。不得因为模板尚未填充而循环询用户或另建token框架；当前缺的是集中发现的代码出口缺口处置和独立执行派单。

## 精确新增与旧事实

设备路径均在files/e4a_output_budget/legacy-acceptance/<新M>/：actors/0001.intent ≤2048B；n2-v2.acceptance精确725B；n2-v2.commit精确244B。本actor仅3文件，已知内容+intent上界3017B（各生产单文件上界2048/4096/256，总分配上界6400B）；最多3新目录legacy-acceptance、<M>、actors。目录项/块/文件系统journal开销另计，不能把3017B当总磁盘成本。新intent实际长度仅在真实actor与BOUND hash已得时由canonical actor.intent计算，当前不填造PID/boot/start/H_actor。

全部O_CREAT|O_EXCL/CREATE_NEW，0600文件/0700目录；payload/commit/intent写后force/readback，父目录sync。代码会打开/排他验证原guard、13项档案/metadata、原0B输出及ledger，force旧metadata/ledger和原目录，但不改旧字节、不追加R/S、不新媒体输出。原ledger完整≤131072B，接受固定1011B前缀及合法已settled后缀，不能锁死整文件1011B。

原task86cafdb3-0fc4-447d-920b-b19c884bf494、attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f、budget730a73e1-50e1-4198-a515-047104f00e31、fence662e9ecd-bede-42e6-bb58-ce81d668ff44、owner64522:20304:10221/0B、lease64522:20385:10221/36B及oldCloseACK=false保留。S0 ABORTED0B，后续53651+53567=107218，三R三S/无reserved为历史接受基线；现场须重新核，合法settled后缀需归入本次审查，不删除还原历史。旧writer缺boot/start根因UNKNOWN不能回填成Java close。

## 复用制品与证明范围

app version13/D1-E9B-PREPARE，SHA ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020；test SHA 2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b；host JAR SHA 4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707。精确路径/大小/签名/35坐标7库/E9B seal源均列external-input-pins.json。计划安装0次；现场pair不同则阻断另审，不盲目再次install-r。

已接受真机只读report与127项证据manifest本地逐项重算，用作历史能力证明：SYSTEM_BOOT_COUNT正常分支、原身份39.3ms与FD返回、非等待/五秒完整广播、归档精确ACK/normalfinish、PC26操作自然返。旧actor PID17434/boot2/start16410590，registry b1d2b533-2461-4a85-ad05-d64509a6b1f9、migration eed3bd1d-7f52-47a4-bd66-992f5b8937f1、attempt fa4e3689-90dc-4bef-b565-fb602863d97f、handle8419402b-16a0-45a0-92fe-d1ec7019848c均**已结束不可复用**。这些不是当前设备值，写COMMIT、guard raw/dup故障、DUMP普通发送者负例等不因该报告而通过。

## 只读校验与封存

tools/validate_package.py只读取本地文件并输出JSON；无subprocess/socket/ADB/UUID生成/文件写。默认严格检查模板状态、字节成本、47外部输入、E9B402 immutable及真机127旧证据；PASS仅PREPARATION_ONLY，不是执行通过。--bound-dir在正式派发后读取新inputs、scope/新UUID/原scope隔离、canonical plan/config/命令/index与现场receipt绑定，仍不证明其采集真实性或替代原生产guard/返回门。校验器拒绝重复key、非canonical wire、越界路径/错误hash/旧actor复用。无正向伪造现场fixture；有限负例仅校验器输入拒绝测试，不重跑生产套件。

本包保留D1 NOT_PASSED、M0 NOT_STARTED、长期准入OPEN。Framework、独立Kit/Flutter、48资源/严格6帧/full EOF/1000us、FFmpeg许可P0均不变。下一步先独立审查本包及P1出口缺口，不能自动开始设备或activation。
''')
doc('EXECUTION_RUNBOOK','''# D1 E10 条件执行手册 V1.0

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
''')
doc('FAILURE_AND_FINAL_REVIEW','''# D1 E10 失败隔离与独立终局审证 V1.0

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
''')
doc('ACTIVATION_INPUT_DAG','''# D1 E10 后续activation输入DAG V1.0

本批不导出真实H_actor/策略、不建activation、不执行安装或grant。这里只给出已存在生产工具的可复用输入关系，避免随机token或hash循环。

依赖顺序：

1. 真实负责人终局迁移scope原字节 → authorization SHA；接受的E10审查原SHA → preparePlan.sourceReview/config.review。
2. scope SHA + 固定descriptor + 实际新registry/migration + E9B固定APK SHA → canonical preparePlan SHA → packed plan/config SHA。配置只引用已经存在的输入，scope不反向包含config SHA。执行者在正式派单授权的模板内一次生成/归档这些文件及独立input-index，不生成随机token、不另起授权框架。
3. 新actor实际采样 → 外部BOUND(reserve actor hash/plan SHA) → 设备intent/payload/commit → 原COMMIT return + 独立normalfinish → 实际final event head → catalog(H_actor) → checkpoint → final seal。最终checkpoint/seal不反写旧events，避免哈希环。
4. 原写批资源全部终局且独立final审查通过后，负责人另行发activation源准备/构建scope；可信activationTrust只引用真实plan/authority/review/registryPath/已确认head。现有E9HostActivationSession --approved-export <真实activationTrust> <配置SHA> <新输出目录>，经原监督者和finalCatalog门导出E9BuildPolicy.java+final.acceptance.json。导出不要求尚未存在的activation APK SHA；没有最终catalog时不能先导出假placeholder构建。
5. 后续新候选复制E9B已冻结source/native/dependency配置，不修改E9B原目录，只替换经过审核的BuildPolicy生成源，标ROLE=ACTIVATION/真实CATALOG_BASE64及SHA/SOURCE_ENVIRONMENT=DEVICE_HA1Q6WXR/GATE_ABI1；新版本必须>13。保留已核独立Kit/Flutter/严格6帧EOF1000us及所有许可门。记录精确source/native继承、35坐标7库不变、当前最终输入snapshot；在新的正式构建派单下才一次必要离线双APK构建+签名/角色/ABI/行为门审计。这个阶段的版本/Hash/兼容pair目前未知，不填写假值。
6. 新activation APK及test实际构建审查后才生成activationRelease（head/catalog/实际app/test/signer/ACTIVATION/abi1/version>13/sourceReview/environment），CREATE_NEW登记到原final registry。release不进入catalog的源head链，catalog不要求这些未来APK SHA，所以无循环。原HostActivationSession --approved-deploy <activationTrust> <pin> <release> <pin> <app> <test> 仅在新部署派单授权时使用；它在记录release前已持有原Store/监督者，未知安装不重试。当前不填release、不调用CLI。
7. 真正部署前确认全部登记actor已终局且无未知参与者；固定双APK install-r精确pair门、UID/签名/数据保留及安装后实测，禁-d/卸载clear/以安装杀未知actor。旧prepare test面对activation app role拒绝迁移入口；新activation runner也不能开COMMIT写。
8. 后续每个新host使用受信内嵌catalog并完成实际当前原guard/fence、全部intent/payload/commit、档案/完整ledger/无pending和本host原资源返回观察，才可能该host grant；不能由catalog年龄、某个磁盘commit或上次host grant代替当前门。缺/旧scope/错actor/未知均拒绝。完整catalog来自真实终局不是“已获产品许可”。

E10仅复用E9B生产JAR/APK进行计划；上述未来构建说明不是一次新构建授权，不复制签名密钥进包，FFmpeg许可P0及Framework发布/独立Kit/Flutter门没有因SBOM无差异而解除。
''')
print('PASS four execution-package documents and explicit static blocker; no execution')
