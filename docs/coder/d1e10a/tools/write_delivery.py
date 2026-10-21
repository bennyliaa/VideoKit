"""E10A four execution documents, repaired-scope proof and exact input references. No devices."""
import hashlib,json,pathlib,shutil
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e9b';E10=R/'docs/coder/d1e10'
if (B/'evidence/e10a-freeze.json').exists():raise RuntimeError('FROZEN_READ_ONLY')
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def new(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
def js(p,d):new(p,json.dumps(d,ensure_ascii=False,indent=2))
def doc(n,s):new(R/f'docs/coder/D1_E10A_{n}_V1.0.md',s)
c=read(B/'evidence/targeted-check-results.json');a=read(B/'evidence/apk-audit.json');h=read(B/'evidence/host-binary-provenance.json');p=read(B/'plan/execution-plan.json')
new(B/'reference/E10A_COORDINATOR_DISPATCH_SOURCE.md','''# E10A 派单来源

VideoKit项目助理，thread01a107c3-2bf9-7fa0-94a0-234258ca6774，在接受E10集中BLOCKED复审后向本coder实际派发最小P1/P2实现及执行包同步。范围摘录：

> P1 BOUND未EXEC收尾：不仅删reserve拒绝，还须避免再次CREATE_NEW identify冲突、原qualified identify不能被取消后PENDING原proof覆盖
> P2 POSTARCHIVE STOP：按准确phase在host写intent/发wire前拒不适用STOP
> 无ADB/设备/媒体/真实UUID或scope签发/迁移写/token/catalog/activation

本文件记录已收到的开发派单，不是用户新批准文本、真实迁移scope或设备派发。项目/设备长期权限来源仍按原E10来源记录及被接受真机只读报告引用；新策略scope在修复包独立接受后才由负责人正式采纳派发，不用本份开发派单或旧BLOCKED报告代填。
''')
same=[]
for n in ['E9MigrationRun.java','E9Evidence.java','E9MigrationTransaction.java','E9OwnedFiles.java','E9BuildPolicy.java','E9Phase.java','E9LegacyProfile.java','E9LegacyState.java','E9CurrentObservation.java','E5AAdmission.java','E4Owned.java']:
 f=B/'src/com/videokit/spike/e4'/n;old=OLD/f.relative_to(B);assert f.read_bytes()==old.read_bytes();same.append(dict(current=row(f),baseline=row(old)))
for n in ['E9PcSupervisor.java','E9PcClient.java','E9HostDeployment.java','E9HostRegistry.java']:
 f=B/'tools'/n;old=OLD/f.relative_to(B);assert f.read_bytes()==old.read_bytes();same.append(dict(current=row(f),baseline=row(old)))
for f in sorted((B/'android').rglob('*.java'))+sorted((B/'app/src').rglob('*.java')):
 if f.name=='E9AndroidIdentity.java':continue
 old=OLD/f.relative_to(B);assert f.read_bytes()==old.read_bytes();same.append(dict(current=row(f),baseline=row(old)))
js(B/'evidence/android-entry-inheritance.json',dict(schema=1,status='PASS',exactUnchanged=same,mode='Original Android Run/transport/IO/ABI unchanged; prior public-entry evidence inherited only; actual new APK compile/signature audited',changedSharedInput='E9Registry.java; packaged by Android even though changed cleanup behavior is host authority logic',newIdentityVersion=14,gateAbi=1,oldPublicEntryEvidence=row(OLD/'evidence/public-android-entry-check.json') if (OLD/'evidence/public-android-entry-check.json').exists() else row(OLD/'evidence/android-entry-inheritance.json'),androidExecution='NOT_RUN',deviceCalls=0))
js(B/'evidence/final-static-review.json',dict(schema=1,status='PASS',reviewer='coder; independent E10A acceptance pending',findings=[dict(id='E10-PREEXEC-BOUND-CLEANUP',status='CODER_FIXED_FINITE_LOCAL_PENDING_REVIEW'),dict(id='E10-POSTARCHIVE-STOP',status='CODER_FIXED_FINITE_LOCAL_PENDING_REVIEW')],productionChanged=['E9Registry.java','E9HostManager.java'],notChanged=['E9MigrationRun Android STOP/ACK semantics and control ABI','Original Process/pipe/5s decoder/Store walk/128 accept/grant gates'],tests=row(B/'evidence/targeted-check-results.json'),limitations=['Actual full approved DEVICE CLI/ADB/system normalfinish NOT_RUN; shared public production boundary is tested with synthetic platform control','No raw/dup Android kernel fault test or new real write permission','002 preserves child argv and decoded canonical frame, not separately every raw child stdout;003 additionally captures raw merged child output','Two retained isolation fixture JVMs are controller-terminated only after finite assertions, never counted as original close or production natural exit'],scope='No new cancellation protocol/framework. Sticky original Android PENDING plus original command-intent latch prevents future execute.'))
refs=[R/'docs/milestones'/f'D1_E10A_{x}_REQUIREMENTS_V1.0.md' for x in ['CODER','TESTER']]+[R/'docs/tester/D1_E10_EXECUTION_PACKAGE_REVIEW_REPORT_V1.0.md',R/'docs/tester/D1_E9B_READ_ONLY_IDENTITY_DEVICE_REPORT_V1.0.md']
refs += [B/'tools'/n for n in ['E9HostManager.java','E9HostRegistry.java','E9PcSupervisor.java','E9HostDeployment.java','E9PcClient.java']]+[B/'src/com/videokit/spike/e4'/n for n in ['E9Registry.java','E9MigrationRun.java','E9LegacyProfile.java','E9LegacyState.java','E9Record.java','E9Actor.java','E9Evidence.java','E9Phase.java','E9BuildPolicy.java','E9MigrationTransaction.java']]
refs += [B/'evidence'/n for n in ['final-build-inputs.json','apk-audit.json','host-binary-provenance.json','targeted-check-results.json','build-results.json']]+[R/x['path'] for x in p['artifacts']]+[R/x['path'] for x in p['deployment']['sourcePair']]
d=R/'docs/tester/D1_E9B_READ_ONLY_IDENTITY_EVIDENCE';refs += [d/'evidence-manifest.json',d/'independent-device-audit.json',OLD/'reference/normalMp4SixRealFrames-post-state-stdout.txt']
js(B/'plan/external-input-pins.json.tmp',dict()) if False else None
# Replace the copied historical E10 pins with this candidate's actual source/binary pins; no self-seal cycle.
(B/'plan/external-input-pins.json').write_text(json.dumps(dict(schema=1,files=[row(f) for f in refs],oldSeals=[row(OLD/'evidence/e9b-freeze.json'),row(E10/'evidence/e10-freeze.json')],readonlyDeviceManifest=row(d/'evidence-manifest.json'),readonlyEvidenceRoot=d.relative_to(R).as_posix()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
art='\n'.join(f"|{x['role']}|{x['bytes']}|`{x['sha256']}`|" for x in a['apks'])
cases='\n'.join(f"|{x['case']}|{x['assertions']}|{'原责任保留；仅专用夹具有限收尾' if not x['productionExitAllowed'] else '原资源已返/正常结束'}|" for x in c['results'])
doc('DELIVERY',f'''# D1 E10A 最小实现与执行包交付 V1.0

P1 BOUND未EXEC取消收尾和P2终局/已归档后STOP已集中实现，12组受影响本机有限检查通过；状态 CODER_FIXED_FINITE_LOCAL_PENDING_INDEPENDENT_REVIEW。执行包仍PREPARATION_ONLY_NOT_EXECUTABLE，未来scope/实际新身份/现场值均未生成，不能使用原E10 BLOCKED报告当准入。D1未过、M0未启、长期准入OPEN。

## 实现

Registry复用并严格校验已存合格identify及reserve，不再CREATE_NEW覆盖identify；同actor（完整canonical含birth）、同plan/authorization/reserve/最后BOUND head、实际磁盘events与原内存连续链一致、命令同handle连续seq、无任何EXEC/ACK意图、确有唯一STOP、当前原回执PENDING/EXTERNAL_STOP/IDENTITY/executeDone=false/0未返且原identity时间及owned一致，才归档新取消return。原合格identify/reserve保持逐字节，追加BOUND_IDENTITY_CANCELLED_NO_COMMIT，不改旧记录。原Android STOP的PENDING本已永久sticky，不能再bindAndReserve；原registry命令门额外拒STOP后EXEC或第二STOP。没有新取消wire或通用取消框架。该IDENTITY结局永远不是final/actor2的COMMIT资格。

HostManager共用公开prepareControl在intent/seq/wire之前拒已归档return、实际已知safe COMMIT终局、此前STOP/finish后的STOP；Registry也在append前拒归档后STOP及STOP重放/后继EXEC。ACK当前proof与原已归档字节比较移到写ACK意图前。重复归档先拒，不让CREATE_NEW失败毒化Store。真正已发的EXEC/ACK意图仍单次不可重放；IO close/force UNKNOWN与PC失败规则保留，不把前置拒绝变成资格恢复。生产operation失败后仍failed，只能经原scope/CLEANUP白名单收尾，不能SEAL_FINAL。

## 验证与边界

12组通过，{c['assertions']}边界断言、{c['sharedFixtureAssertions']}共享合成夹具断言。真实生产Registry/Run、与原host CLI实际共用的prepareControl、原ProcessBuilder/5秒decoder、真实console错误退出和原custodian→精确ACK/normalfinish路径参与。平台身份/控制/System normalfinish为SYNTHETIC替身，不是获批DEVICE CLI或Android故障/内核实测。旧19/32/24/native未重跑。

targeted-001只在测试callback checked Exception处编译失败，无执行；原源码和原日志保留。targeted-002通过11组；console-003仅新增一组实际console拒绝→custodial ACK并增加raw合并子进程输出日志，未重复旧11组；两次所有生产class字节一致。002保留每次child argv、canonical frame及原测试JVM stdout/stderr，未另存每次child raw stdout；003额外原样保存它。EXEC_INTENT_ISOLATION在真实Registry先记EXEC意图、故意不投wire，然后直接原Run.stop生成真实取消proof，证明后者仍不能抹去先前意图；不声称host会合法发那条错位控制。UNKNOWN_COMMIT_CLOSE与该意图隔离两组均保留原责任，有限观察后控制器只终止专用夹具JVM且所有真实child已返，originalCloseAck=false；不算生产安全退出。正向分支经原console/entry及自然JVM退出收尾。

|组|边界断言|结束边界|
|---|---:|---|
{cases}

## 必要构建及真实制品

共享Registry源码在Android输入中，不能宣称纯PC继承旧APK。因此一次必要main-001离线构建成功（68 tasks，约1分钟），无repair/下载/native重编。163最终输入SHA `{sha(B/'evidence/final-build-inputs.json')}`。版本14/D1-E10A-PREPARE，AndroidIdentity准确版本门14；原Run/Instrumentation/IO/ABI1及框架逻辑按字节继承，仅该身份版本条件随候选更新。protocol批标签仍D1-E9A-PREPARE-TABLET-20261018，不为改文案重建。

|制品|字节|SHA256|
|---|---:|---|
{art}
|生产host JAR|{h['artifact']['bytes']}|`{h['artifact']['sha256']}`|

JAR含{len(h['productionClasses'])}生产classes，不含测试类，来源targeted-002已测编译，并与003生产class逐项相同；三个默认入口INSPECT_ONLY。两APK原签名5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f，7native/35坐标不变、16KiB对齐/角色/ABI/服务审计PASS。测试APK恰与E9B同字节；app已更新。未安装候选。

四文档：本DELIVERY含实现/证明；EXECUTION_RUNBOOK为新受管部署+actor1正常/取消条件流程；FAILURE_AND_FINAL_REVIEW为阶段化收尾/UNKNOWN/actor2门；ACTIVATION_INPUT_DAG为终局后独立发布。机器plan/scope/12个条件命令/只读校验器已同步新14候选、原13来源pair及新host JAR，review占位必须未来E10A接受审查SHA。旧E10“安装0次/复用旧host/BOUND无出口”不再适用新候选，旧文档只作冻结历史。

固定descriptor725B SHA4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb、commit244B不变；新actor1只3控制文件，intent≤2048B，总内容≤3017B/分配上界6400B、最多3新目录，目录FS开销另计。原task/attempt/budget/fence、0B/S0、53651+53567=107218、13原metadata与oldCloseACKfalse不改；固定1011B前缀与完整合法settled后缀分开。非零媒体不读写，原旧bytes不改、不追加R/S/ABORT/清账/换budget。

E9B/E10原冻结完整只读核验，新ZIP含源码/原日志/差异/输入/制品/完整执行包，外seal避免循环；冻结后独立verify及完整交接报告另存包外。当前0ADB/设备/真实UUID/scope签发/迁移写/token/catalog/activation，无H_actor。用户项目/设备权限与负责人未来具体scope采纳明确分开，不造随机批准token或额外用户授权文本。Framework/独立Kit/Flutter/48资源/严格6帧fullEOF1000us/全部许可P0保持。
''')
doc('EXECUTION_RUNBOOK','''# D1 E10A 条件执行手册 V1.0

当前只准备，必须修复包独立接受及负责人另行exact actor1派发；原E10 BLOCKED报告和本开发派单均不是执行许可。不直接运行模板或整串无条件喂命令。

## 一次新身份和canonical输入

正式派发时负责人签发具体scope，受托tester按已审模板只生成一次新registry/migration/attempt/handle四UUID并存原字节。四值唯一，不能用已结束只读actor的四UUID/PID17434/boot2/start16410590。目录docs/tester/D1_E10A_EXECUTION/<新M>/inputs、同级registry（启动前必须不存在）和evidence；不预填PID/boot/start/H_actor，不预建设备目录。

scope status=ISSUED_FOR_EXACT_ACTOR1，issuerRole=PROJECT_COORDINATOR/原负责人thread，补真实issuedAt、实际派单和接受的E10A审查原path/bytes/SHA，acceptedE10AReviewSha256等于其原SHA；具体采纳新终局策略/三文件/本次一次actor1/受管部署，受托tester可记录派单生成文件。项目全权推进/恢复/永久设备权限仅为上层来源；不虚构其他窗口用户原文，不拿旧只读scope或E3已耗许可升权，不以随机64hex当批准。

templates有templateOnly外壳，生产仅接收wireFields：ASCII e9=1/fields，fields排序紧凑JSON、值全string、尾部一个LF、无BOM/CRLF/重复键。scope原SHA→plan.authorization；新registry/migration、v14候选pair/sourceReview=未来接受E10A报告SHA→canonical plan SHA；Base64URL无padding嵌入config.plan，planSha精确，config.authorization同scope/review同报告；head NEW、registryPath同级新registry绝对正斜杠路径。originalApp/Test为原E9B13精确pair、originalVersion13/PREPARE/ABI1；candidate plan是新E10A14。scope不反向包含config hash，独立input-index列scope/plan/config/preflight/全部12条件命令的原path/bytes/SHA且不包含自身，无hash环。

只读校验：Python -X utf8 -B docs/coder/d1e10a/tools/validate_package.py --bound-dir <新inputs>。校验器不生成scope/UUID、不会执行命令/观察设备，静态绑定通过也不是权限或READY。preflight.json按validator.bound schema记录本scope真实现场及rawEvidence pin；不能用九个true或模板旧值代原始证据。

## 现场和一次受管部署

正式执行前实际采集serial HA1Q6WXR/user0/机型/API、当前pm path及两base.apk完整SHA/UID10221和10222/包状态/签名/版本/role/ABI、无相关app或worker/旧在途。**本计划来源必须为新观测的精确E9B13 pair**（app ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020，test2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b）；即使现场已经14也不盲目再装，来源不同停止另审精确分支。旧read-only报告只证当时13，当前未测。

预检固定13metadata/旧guard owner64522:20304:10221/0B、lease64522:20385:10221/36B与fence662e9ecd-bede-42e6-bb58-ce81d668ff44，role/dev/inode/UID/无symlink；完整ledger≤131072B、固定1011B前缀与全链合法settled后缀/原三R三S/107218不变、reserved0/4MiB总门，无operation.pending；原0B及53651/53567产物只metadata保全，不读非零payload。新M不存在、legacy-acceptance不存在或为空、不容其他M；新registry不存在。预检不能持guard等待批准，真实COMMIT仍重新排他验证全部原条件。元数据能力/权限异常停止，不写探针。

原系统日志生产固定logcat -d -v brief -s E9_MANAGED:I ActivityManager:I *:S，总≤1MiB，建议事前≤800000B留余量但不保证增长；超界不clear/tail假拼normalfinish。全部独立metadata客户端最多20，保存argv/exit/两reader/原stdout/stderr/hash；UNKNOWN或现场变化停止。新boot/start由新原actor实际采样并独立核，不能复制旧2/16410590。

未来原Java入口：D:/Android/Android Studio/jbr/bin/java.exe -cp <本批固定e10a-host-tools.jar> com.videokit.spike.e4.E9HostManager --approved-session <canonical config> <精确SHA>；逐项argv、保留原stdin/两reader/同custodian。00-DEPLOY_PREPARE先由生产门核原13和无actor，app/test install-r各一次到本批14，核安装后exact pair/UID/版本/role/ABI/启用状态/原数据目录保留；不能-d/卸载clear/重复安装/靠安装结束未知actor。尚未生成此部署实际回执。

## actor1正常链

1. LAUNCH显式REGISTERED_MIGRATION/ordinal1/SYSTEM_BOOT_COUNT/新attempt+handle。原am instrument -r不-w，协议标签仍D1-E9A-PREPARE-TABLET-20261018；启动client返回不等于actor结束。
2. POLL STATUS seq1/state=-1，完整transport经原五秒含decode门；验证新request/actor/UID/PID/handle/seq/pair，原identity phase真返/owned≥1/unreturned0/IDENTITY_QUALIFIED/identityNanos<10s，独立ps/双boot/proc stat对应新出生身份。无原合格身份不RESERVE。
3. RESERVE predecessorIntent NONE，生产保存原qualified identify与reserve、追加BOUND；核原Store返和同head。不写device。若需停止，走下节严格取消，不为收尾强发EXEC。
4. 唯一EXECUTE_COMMIT seq2（state用最新稳定snapshot），原host先记不可重放intent、Android先reserve再排原execute，独立10s从原reserve起算，响应含decode≤5s，未知不更seq重发。只有原guard/ledger排他门通过才CREATE_NEW三文件，force/readback/sync和原最后guard/dup/raw close均须真返。
5. POLL seq3，必要时最后一次STATUS seq4（总STATUS≤3）；不能无限poll或延长原10秒。原真实COMMIT return executeDone=true/unreturned0/safe=true、QUALIFIED_MIGRATION及identity/execute各<10s、deviceRecord绑定完整，才走正常终局。FAILED或PENDING只能按真实归还事实收尾，不能升级资格。
6. ARCHIVE_RETURN精确原COMMIT R0。之后不再STOP；也不在已知safe COMMIT终局前机械补STOP。唯一ACK_FINISH seq4或5，host先核当前原proof==已归档原字节，再记唯一ACK意图/发wire；错字节/重复/阶段不适用拒绝不消耗ACK。已发未知仍不能重发。
7. CAPTURE_FINISH由原生产端独立ps缺席+唯一原E9_FINAL_FINISH锚点及对应原PID正常finished inst/Killing系统日志，存原finish/event。系统正常Killing记录不是执行者发force-stop。finishClaimed/client exit/单个PID缺席不够。
8. 独立核新三控制文件精确intent actor/reserve hash/725B acceptance/244B commit及旧档案/ledger守恒/无在途；接受当前证据后SEAL_FINAL才实际生成final event head、catalog(H_actor)、checkpoint和seal；再独立重算DAG。当前不填H_actor。PREPARE仍无grant。
9. INSPECT、正常关闭原stdin、原custodian等全部原Process/pipe/Store/remote/accepted Socket/listener返回才pcClosed；原Java自然exit/两reader返回。当前STATUS回复allOriginalsReturned可含正在处理的Socket，不补无穷查询、不controller terminate当成功。

## BOUND未EXEC取消链（新P1出口）

仅原identity实际合格真返、外部same-actor BOUND且无任何EXEC意图/预留/在途时发一次11-STOP_DEPENDENCIES（通常seq2）。原Android sticky PENDING永久禁止再reserve；取得真实IDENTITY/PENDING/EXTERNAL_STOP/executeDone=false/unreturned0原回执。Registry核原qualified identify/time/owned、原reserve/plan/auth、完整actor、最后BOUND head及原events连续性、命令链无EXEC/ACK并确有唯一STOP，**复用**既有identify/reserve原字节，ARCHIVE_RETURN仅新建当前取消returned并追加取消event。已有EXEC意图即使回包像IDENTITY也拒此路，不靠executeDone=false判断。

再唯一ACK通常seq3→独立CAPTURE_FINISH→INSPECT→原PC自然退出。取消不发送EXEC，不生成device三文件，不SEAL_FINAL，不actor2。若STOP/ACK已发未知，只用剩余额度与原scope允许证据有限收尾，不重放；新出口不是让原UNKNOWN伪归还。

统一evidence台账不侵入registry20文件白名单。正常Android4或5控制，取消3控制；上限8/STATUS3，EXEC/ACK各1，本机STATUS/OP/CLEANUP≤16共用原128accept，原Process≤96，正常含部署预计≤29，metadata独立≤20。PC前置拒绝导致原operation失败后仍failed，只可CLEANUP白名单（原config+命令双SHA），禁止RESERVE/EXEC/SEAL，不恢复发布资格。额满监听通道关闭/UNKNOWN但原custodian继续持有，不换port/重启扩额。
''')
doc('FAILURE_AND_FINAL_REVIEW','''# D1 E10A 阶段化失败收尾及独立final审证 V1.0

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
''')
# Preserve the complete accepted DAG explanation while updating this candidate's actual minimum and trust references.
s=(R/'docs/coder/D1_E10_ACTIVATION_INPUT_DAG_V1.0.md').read_text().replace('D1 E10 ','D1 E10A ').replace('E10准备','E10A准备').replace('接受的E10审查','接受的E10A审查').replace('版本必须>13','版本必须>14').replace('E10仅复用E9B生产JAR/APK进行计划','E10A复用本批version14 PREPARE/JAR进行计划；新候选已按共享输入变化完成一次必要离线构建，未安装').replace('复制E9B已冻结source/native/dependency配置','复制E10A已冻结修复后source/native/dependency配置')
s+='\n\n本批新增取消出口不生成final catalog、不授actor2资格；P2拒绝保持原归档R0供ACK。后续activation release版本必须严格高于本批PREPARE14，原E10 BLOCKED报告不可填为sourceReview；仅未来真正接受的E10A及真实终局独立审定可进入授权DAG。当前phase/grant/许可门未开。\n';doc('ACTIVATION_INPUT_DAG',s)
new(B/'E10A_PROGRESS_FINAL.md',f'''# E10A 完成范围

P1/P2实现及12组{c['assertions']}边界断言（另{c['sharedFixtureAssertions']}共享夹具断言）通过；一次必要v14离线双APK构建、原签名/7native/35坐标审计和新host JAR来源完成；四执行文档/12条件模板/机器计划同步。冻结/交接状态以外seal与包外只读回执/完整报告为准。候选待独立审查，不设备、不签发scope/真实身份、不迁移/activation，D1未过M0未启长期准入OPEN。
''')
print('PASS four updated documents, exact inheritance and new version14 execution bindings')
