"""Complete E9B four-document delivery and explicit inherited/static scope, from recorded evidence."""
import json,pathlib,hashlib
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e9a'
def raw(p):return p.read_bytes()
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def row(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def read(n):return json.loads(raw(B/'evidence'/n))
def new(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
def write(n,d):new(B/'evidence'/n,json.dumps(d,ensure_ascii=False,indent=2))
def doc(n,s):new(R/f'docs/coder/D1_E9B_{n}_V1.0.md',s)

inherited=[]
for name in ['E9MigrationRun.java','E9CurrentObservation.java','E5AAdmission.java','E9Phase.java','E9BuildPolicy.java','E4Owned.java']:
 p=B/'src/com/videokit/spike/e4'/name;old=OLD/p.relative_to(B);assert raw(p)==raw(old);inherited.append(dict(current=row(p),baseline=row(old)))
for name in ['E9HostDeployment.java','E9PcClient.java']:
 p=B/'tools'/name;old=OLD/p.relative_to(B);assert raw(p)==raw(old);inherited.append(dict(current=row(p),baseline=row(old)))
for p in sorted((B/'android').rglob('*.java'))+sorted((B/'app/src').rglob('*.java')):
 if p.name=='E9AndroidIdentity.java':continue
 old=OLD/p.relative_to(B);assert raw(p)==raw(old);inherited.append(dict(current=row(p),baseline=row(old)))
def segment(p,start,end):return p.read_text().split(start,1)[1].split(end,1)[0]
same_sections=[]
for name,start,end in [('E9PcSupervisor.java','    public final class Operation {','    private synchronized boolean originalsReturned()'),('E9HostManager.java','    public static CheckedFrame checkTransport(','    private static byte[] bounded('),('E9HostManager.java','    public static List<String> nonWaitingLaunch(','    private void launch('),('E9HostManager.java','    private void control(','    private byte[] evidenceCommand(')]:
 a=segment(B/'tools'/name,start,end);b=segment(OLD/'tools'/name,start,end);assert a==b;same_sections.append(dict(file=name,start=start,end=end,sha256=hashlib.sha256(a.encode()).hexdigest()))
prior=OLD/'evidence/public-android-entry-check.json';assert json.loads(raw(prior))['status']=='PASS'
write('android-entry-inheritance.json',dict(schema=1,status='PASS',mode='INHERITED_E9A_FINITE_LOCAL_SCOPE_NO_RERUN',priorEvidence=row(prior),exactUnchanged=inherited,unchangedProductionSections=same_sections,publicEntries=6,priorRuntimeGrantInvalidationSequence=1,currentAndroidExecution='NOT_RUN',qualification='No fresh runtime claim; affected Store/entry/accept paths checked separately in E9B'))
c=read('targeted-check-results.json');a=read('apk-audit.json');h=read('host-binary-provenance.json');build=read('build-results.json');assert c['groups']==24 and a['status']==h['status']==build['status']=='PASS'
assert len(build['attempts'])==1 and build['attempts'][0]['exitCode']==0
write('final-static-review.json',dict(schema=1,status='PASS',reviewer='coder self-review; independent tester verdict remains pending',requirements=row(B/'reference/D1_E9B_CODER_REQUIREMENTS_V1.0.md'),targetedEvidence=row(B/'evidence/targeted-check-results.json'),androidInheritance=row(B/'evidence/android-entry-inheritance.json'),checks=['Store walk holder registered before allocation; same Store retained by LIVE supervisor before registry IO','Exception and Error leave original resource retained until known Java close; no second UNKNOWN close','Manager initialization failure retains Store independently of busy flag','Activation open/export/release all inside same pre-created supervisor boundary','Reservation before accept; charge actual accepted socket before processing; ambiguous failure consumes one slot','At 128 close listener once; stop accept even if close remains UNKNOWN; no port replacement/reset','Original Process wait/reader/pipe and 5s decoder bodies byte-identical to E9A','pcClosed requires original Store plus Process/pipe/remote/accepted clients plus actual listener return','One offline prepare build and original certificate/7 native libraries/35 coordinates','No device/media/actual migration/activation execution'],limitations=['Static coder review and finite local cuts only, not independent acceptance','Production IO that never returns remains held indefinitely; no kill/cancel/false close ACK','After accept budget exhaustion original custodian remains in same JVM but TCP status/cleanup channel is unavailable','UNKNOWN fixture test-controller teardown is never a resource return or safe production exit proof']))

apks='\n'.join(f"|{x['role']}|{x['bytes']}|`{x['sha256']}`|" for x in a['apks'])
cases='\n'.join(f"|{x['case']}|{x['assertions']}|{'未证明归还；夹具有限收尾' if not x['productionExitAllowed'] else '原资源已返'}|" for x in c['results'])
doc('DELIVERY',f'''# D1 E9B 交付 V1.0

候选 D1-20261018-E9B，目录 `docs/coder/d1e9b`，仅 PREPARE 静态与本机有限验证交付。负责人派单的 P1 原遍历所有权及全入口结束边界、P2 总 accept 前置额度已实现并集中验证；待独立 tester 审查。不能据此认定 D1 通过或设备准入。

## 变更和原对象

`E9Registry.Store.checkTotal` 把原 `Files.walk` 的 E4Owned 在 allocate 之前登记到同一个 Store；Store.returned 和监督者 pcClosed 都检查它。分配未返、迭代/读取失败、close 在途、Exception/Error/UNKNOWN 不会从登记中消失；只删除 CLOSED，UNKNOWN 不重关。healthy=false 仅禁止后续业务，不能充当关闭证明。

新增 `E9HostRegistry`，先把真实 Store 和 Registry 强引用交给原监督者，再初始化/打开注册表；统一 boundary 覆盖失败出口。HostManager 即使构造中失败、finally 清掉 authorityCallActive，也仍由独立 Store 引用持有资源。HostActivationSession 在配置打开、openKnownHead、approved-export、recordActivationRelease、后续 Processes 之前创建同一个监督者，后续不新建一套监督者。设备环境校验保留；本地夹具只向真实生产下层入口代入 SYNTHETIC_LOCAL，不伪造获批设备配置。

本机 accept 前保留额度，实际返回 Socket 后立即计数，已接收未处理也占额；歧义失败保守占额。总额 128 后停止调用 accept 并只尝试一次 listener close。实际 close/UNKNOWN 单独公开；原 Process、pipe、Store、remote 监督继续，不能换端口/重置扩额。达到额度后 TCP 状态与收尾入口不可用，隔离 ACK 明确标识 ACCEPT_BUDGET_EXHAUSTED；同 JVM 原非 daemon custodian 仍持有责任，不声称另有可用查询端点。

## 验证

24 组受影响有限检查全部通过，共 {c['assertions']} 个边界断言，另 {c['sharedFixtureAssertions']} 个合成元数据夹具断言。真实本机目录流/Socket/Java ProcessBuilder、原生产 Store/监督者/共用入口边界参与。UNKNOWN 组在有限观察后由测试控制器终止**专用夹具 JVM**，此前确认原实际 child 均已返回；该动作不算 Java close ACK 或生产安全退出。长期不返语义只验证有限观察窗口，不冒称穷举或实际永久等待完成。

旧19/32套件、native、设备未重跑。E9A 已关闭 F01/F03/F04 的源文件及关键函数按字节继承，见 android-entry-inheritance；这不是新的 Android 运行证明。`compile-001` 是初始单组编译探测；`production-002` 为23组；`accept-failure-003` 只在枚举历史工具目录时准备失败、未编译执行；修正检查器的文件过滤后 `accept-failure-004` 单独通过新增第24组。新增只改测试，生产 class bytes 与002一致。002测试源码修改前的精确文件保存在 evidence，原日志不覆盖。

一次 `main-001` 离线 APK 构建通过（68 tasks，1m15s），无 repair、无下载、无 native 重编。最终输入快照 {len(read('final-build-inputs.json')['files'])} 文件 SHA256 `{sha(B/'evidence/final-build-inputs.json')}`。包含共享 Store 变更及版本13/D1-E9B-PREPARE，所以执行必要重建；测试 APK 恰与E9A按字节相同。未安装 APK。

|制品|字节|SHA256|
|---|---:|---|
{apks}
|生产 host JAR|{h['artifact']['bytes']}|`{h['artifact']['sha256']}`|

两APK签名 `{a['apks'][0]['signerCertificateSha256']}`，生产 host JAR {len(h['productionClasses'])} classes，不含测试类，来源为002当前生产编译，004复核生产class字节一致。三个默认入口均 INSPECT_ONLY。SBOM 35 Maven 坐标/7 native 库继承，锁、库与 E9A 一致；FFmpeg8.0.3/Media3 1.9.3许可结论不变。源码ZIP含四文档/源码/原日志/差异/输入/制品/SBOM，ZIP外 e9b-freeze.json避免自包含哈希；冻结后只读验证回执和完整负责人报告另置docs/coder。

## 有限案例索引

|案例|断言|结束边界|
|---|---:|---|
{cases}

证据入口：`evidence/targeted-check-results.json`、各 selfcheck-attempts 原 argv/stdout/stderr/平台状态、`source-derivation.json`、`host-binary-provenance.json`、`build-results.json`、`apk-audit.json`、`sbom-difference.json`、`external-readonly-verification.json`。历史E9A工具仅归档于reference/e9a-tools，不能用于本批构建或冻结。
''')
doc('ARCHITECTURE_AND_THREAT_BOUNDARY','''# D1 E9B 架构与威胁边界 V1.0

本批仍为合作式有限执行及已批准配置的威胁边界，不扩展为同机恶意进程防护或通用守护框架。保留原非等待 launcher、独立五秒广播响应任务及解码、96原Process操作上限、48资源/6帧/full EOF/1000us等框架门。没有新增device/root/kill/retry/cancel/reset能力。

## 原对象链

LIVE[原handle] → 原non-daemon custodian → 原Store → 已登记walk或file E4Owned → 原Stream/FileChannel。Store 在首个注册表IO前交由监督者持有，Registry也保留。HostManager额外持有原manager+busy callback，不能替代Store原资源检查。HostActivationSession从open前进入相同寿命域，导出路径也适用。所有业务调用结束/失败finally只关闭业务入口并等待真实pcClosed或真实同JVM隔离ACK；UNKNOWN不能转为returned。

walk在register后才allocate；allocate异常可能UNKNOWN，Error可停在ALLOCATING；close异常UNKNOWN，Error可停在CLOSING。全部returned=false。迭代或read失败但原close真实返回时，业务仍失败、资源却可合法归还，允许pcClosed；不能把所有业务失败一律永久保留，也不能把healthy=false误当归还。Store持有原walk直到实际CLOSED，不另建假流补close，不对UNKNOWN第二次close。

## 接入与监听器

同一监督者只使用原IPv4 loopback端口。短锁内先保留总accept名额，原accepted holder先登记，实际accept返回前后均有原对象；实际返回立即计额早于处理请求。SocketTimeout明确未接受时释放在途保留；歧义失败保守消费名额且持有未知原对象，停止后续接入。accepted+reservations不超过128，累计不清零；并发客户端排队不增加额度，TCP握手成功不等于应用实际accept。

128时先标记耗尽，停止accept，原listener close只尝试一次。第128个已接受Socket仍由原holder收尾。listener的CLOSED/UNKNOWN/CLOSING单独参与闭合判定；close未知时即使已实际native close也不得认定Java已返，已native关闭不是证据。达到额度后的监听器即使无法关闭，也不再accept129+。原进程wait/reader/解码/管道及Registry监督继续；没有新端口、预算续期或重启承接。

额度耗尽后状态通道为ACCEPT_BUDGET_EXHAUSTED，原JVM可持续占有未知责任，无法再经该TCP口查询或发CLEANUP；不得声称有限额度支持无限收尾。未来设备批必须事先规划有限查询预算。UNKNOWN以及永久未返可能让JVM长期保持；本批不通过外部强退代替归还。

## 证明范围

有限故障Hooks只切真实生产Store/walk/原listener/Process/共用boundary，元数据环境合成，不替换原业务判定。manager与activation下层入口测试不冒称执行获批设备CLI；CLI仍拒绝Synthetic环境。测试控制器结束专用未知夹具是清理动作，originalCloseAck=false、productionExitAllowed=false。真实Windows内核永久卡死、Android进程/广播/ADB可达性、全调度穷举均未验证。独立tester仍需审查。
''')
doc('REMAINING_GATE_REVIEW','''# D1 E9B 剩余门审查 V1.0

E9A独立审查已关闭 E9-F01/F03/F04 的 STATIC_LOCAL 范围。本批保留其代码和证据，不重新宣称全系统通过。原 E9-F02 P1（遗漏walk及入口前序原资源）与新增P2（accept总次数）已实现和本机有限验证，状态为 CODER_IMPLEMENTED_PENDING_INDEPENDENT_REVIEW，等待 tester 决定是否 CLOSED_STATIC_LOCAL。

D1 NOT_PASSED；M0 NOT_STARTED；E6B-OBS-F01 长期准入 OPEN。本交付不是设备执行许可，E3一次性许可已消耗不能重用，不生成新token、真实catalog或H_actor；没有activation构建或部署。

既有账本3R/3S、107218 consumed/0reserved、4MiB预算、2MiB单项、128任务与原budget/fence不变。原recovery writer PID4869、UID10221、attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f、oldCloseACK=false不回填。N2S0原输出0B/ABORTED及档案不改。账本允许合法settled后缀，不锁死整文件长度；这里只继承旧证据，不声称本批重新读取真实设备。

Framework发布、严格6帧/full EOF/1000us、独立Kit/Flutter、FFmpeg许可P0等门保持既有状态。7库/35坐标没有新增，不能由SBOM无差异推导许可已获批。本机资源关闭证明不替代设备侧actor正常finish、真实进程身份、所有者/lease/fence/预算验证。

下一步只进行独立tester审查和负责人决策。任何设备只读批、实际迁移、重试、ABORT、token/catalog、activation均需其各自明确派单与许可，当前不自动执行。
''')
doc('DEVICE_EXECUTION_APPENDIX','''# D1 E9B 设备执行附录 V1.0

本附录为未来独立审查使用的步骤和预算约束，当前 NOT_AUTHORIZED / NOT_RUN。没有设备实测、没有任何ADB调用；本文不提供可直接执行的一次性许可。

候选应用版本13 / D1-E9B-PREPARE，包com.videokit.app与com.videokit.app.test，签名必须与交付审计一致。仅PREPARE，BuildPolicy.CATALOG_SHA=ABSENT，产品/旧恢复/长期观察仍拒绝。测试runner及非等待命令保留精确批标签 `D1-E9A-PREPARE-TABLET-20261018`，这是继承的协议常量，不能将CLI默认INSPECT_ONLY中的旧批文字当成设备资格或新版版本号。E9B版本号由真实APK审计给出。

未来若负责人独立批准只读批，应先复核ZIP外seal、原输入、签名、版本/role/ABI和设备原身份；配置/命令文件各自按原SHA pin，禁止Synthetic环境代入Device CLI。原HostManager为--approved-session三参入口，启动不等待instrumentation结束，以独立五秒广播取状态；只读identity模式不能RESERVE/EXECUTE_COMMIT，后续类型化归档/精确ACK/正常finish不能用launcher退出代替。未批准的激活导出/发布CLI不得调用。

tester建议未来小批最多16次本机查询、8条Android控制请求（其中STATUS≤3）仍仅设计建议，不是本批执行预算授权。实际本机supervisor总accept硬上限128，含已接受未处理以及歧义失败保守计额；readonly查询与获批收尾共用该额度。提前为收尾留额，不能到128后要求端口继续服务。达到128监听器关闭或UNKNOWN、状态通道耗尽，原custodian继续持有Process/Store责任；不换端口、不重启扩额、不把TCP断开当原资源已返。

实际registry库存最多20文件155648B（另保留196608总门）、40遍历项，独立系统日志总1MiB；本机输入/状态行16KiB、原控制回包32768B、原Process总96均保持。每条独立响应含原解码仍在同一5秒绝对期限内，超期PENDING，不重放EXECUTE或ACK。永久未返/UNKNOWN没有第二次close与安全退出ACK；原non-daemon同JVM监督者继续保留责任，需负责人另行审查，不用新root/catalog/预算/force-stop假恢复。

本批禁止项：ADB/安装/真实媒体读写/实际迁移/ABORT或预算重置/token或真实catalog/H_actor/activation。D1未过，M0未启，长期准入OPEN。
''')
new(B/'E9B_PROGRESS_FINAL.md',f'''# E9B 完成记录

P1/P2实现；24组{c['assertions']}边界断言通过，合成元数据断言{c['sharedFixtureAssertions']}；一次必要离线双APK构建、签名/7native/35坐标审计完成。四文档和原证据齐备；冻结及交接状态以包外seal、只读验证回执和完整交接报告为准。无设备或真实执行；独立tester验收待定，D1 NOT_PASSED/M0 NOT_STARTED/长期准入OPEN。
''')
print('PASS four E9B documents, inherited-scope proof and coder static review')
