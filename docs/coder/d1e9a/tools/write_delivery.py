"""Four E9A review documents, finite-case mapping and completed-work note, from recorded facts."""
import csv,hashlib,json,pathlib
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2]
def read(n):return json.loads((B/'evidence'/n).read_bytes())
def new(p,text):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text.strip()+'\n')
def doc(n,text):new(R/f'docs/coder/D1_E9A_{n}_V1.0.md',text)
c=read('targeted-check-results.json');a=read('apk-audit.json');h=read('host-binary-provenance.json');build=read('build-results.json');inputs=read('final-build-inputs.json');inputSha=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()
apks='\n'.join(f"|{x['role']}|{x['bytes']}|`{x['sha256']}`|" for x in a['apks'])
scopes=[
('TRANSPORT','真实生产非等待命令构造、广播帧解码及实际checkTransport；actor/request/handle/seq/模式/重放校验','E9HostManager.nonWaitingLaunch/broadcastFrame/checkTransport','Android广播交付/权限/启动实际可达性NOT_RUN；本地只代入shell响应格式'),
('STATUS_GAP','关闭写入口后仍可STATUS；缺失序号保守扣请求和STATUS额度；非法整数拒绝；第4次STATUS拒绝','E9MigrationRun.observeStatus/status','真实Android冷启动/丢包未做，不保证一定取得资格'),
('IDENTITY_CLEANUP','无reserve/无device写，原身份回执归档、精确ACK、正常finish、PC原remote责任归还；不能final或actor2','E9Registry.captureIdentityForFinish/E9Evidence/E9PcSupervisor.Remote','OS正常finish来源为SYNTHETIC替身；不生成真实catalog'),
('NO_REPLAY','已写EXECUTE/ACK intent即使换新seq也不得重发','E9Registry.commandIntent','真实ADB失联NOT_RUN'),
('DECODE_DEADLINE','真实本机client已退出但原解码任务延迟5.5秒，5秒时PENDING、原任务仍持有；晚返不改成功','E9HostDeployment.Processes/E9PcSupervisor.runDecoded','受控平台Hook延迟；不是Android响应延迟实测'),
('GRANT','实际共享观察成功→重复BLOCKED→requireCurrent拒绝','E9CurrentObservation/E5AAdmission','UID/inode/目录fsync为平台替身；无设备'),
('CONCURRENT_GRANT','旧观察close切点在途，新调用先撤销/换epoch；旧调用不能随后发布grant；新调用成功后再重复也撤销','E9CurrentObservation/E5AAdmission','有限本机线程交错；未穷举所有调度'),
('CUSTODY_PIN','原主管理者隔离后仍可查；错原配置pin不调用收尾回调，正确pin只调用原对象','E9PcSupervisor/E9PcClient','收尾回调仅本地INSPECT；实际Android收尾NOT_RUN'),
('REMOTE','真实短生命周期client退出和原共享资源已归还都不代替actor正常finish；remote责任保持直到类型化finish','E9PcSupervisor.Remote/E9Registry','actor及正常系统日志为合成元数据夹具，无Android启动'),
('EARLY_EOF','真实pipe reader已EOF/close但child仍活，console EOF后main返回隔离ACK而JVM仍活；child实际退出后才结束','真实ProcessBuilder/reader/E9HostManager.console','本机Java子进程，非adb.exe'),
('READER_ERROR','原reader平台异常、原pipe实际close，但child活；原管理者及状态authority保留','E9PcSupervisor.Operation/E9HostManager.console','Exception为平台Hook；实际Win32内核错误未注入'),
('OUTPUT_BOUND','真实输出超界后停止依赖，reader结束不能代替活child退出','E9PcSupervisor.Operation','只测有限超界，不做无限数据压力'),
('CONSOLE_EOF','stdin EOF仍有原child时原监督者接管，状态可查，原实际退出/pipe返回后JVM才结束','E9HostManager.console/E9PcSupervisor','真实本机manager JVM和child；无设备'),
('CONSOLE_TRUNCATED','截断控制台JSON失败经过同一结束边界，不丢原child/pipe','E9HostManager.console','本机输入截断，不冒称ADB网络断连'),
('CONSOLE_OVERFLOW','16KiB输入界在逐字节读取时执行，错误出口仍实际接管原对象','E9PcSupervisor.consoleLine/E9HostManager.console','不穷举全部字符/内存故障'),
('CONTROL5','实际Processes.runControl固定5秒绝对期限，超时不kill/retry，原client仍活且可识别','E9HostDeployment.Processes/E9PcSupervisor','观察包含调度/交接尾段，非5秒资格扩成6.5秒'),
('LATE_VERDICT','5秒后原client真正晚返，物理资源全返但原PENDING不变，不再派依赖','E9PcSupervisor.Operation','本机真实正常exit；无Android'),
('CLOSE_LATCH','实际child退出后原stdout close在途CLOSING，JVM仍活；允许原close真正返回后才自然结束','E9PcSupervisor/E4Owned','close平台Hook有限latch，不是内核永久卡住'),
('CLOSE_UNKNOWN','native close已发生但平台抛UNKNOWN，原holder不变，原管理者不退出；有限观察结束的夹具清理不产close ACK','E9PcSupervisor/E4Owned/真实manager JVM','测试controller最后清理仅合成夹具；无E9_PC_CLOSED，不能当生产安全退出')]
assert len(scopes)==19
lookup={x['case']:x for x in c['results']}
with (B/'evidence/test-mapping.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['case','status','assertions','productionObjects','executedFiniteScope','notRunBoundary','actualPCProcess'])
 for name,scope,objects,gap in scopes:w.writerow([name,'PASS_FINITE_LOCAL_SCOPE',lookup[name]['assertions'],objects,scope,gap,lookup[name]['realPCProcess']])
table='\n'.join(f'|{n}|{o}|{s}|{g}|' for n,s,o,g in scopes)
doc('DELIVERY',f'''
# D1 E9A 集中修复交付 V1.0

2026-10-18。依据E9独立复审2项P1、2项P2的集中派单，E9A已实现四项修复并形成静态复审候选。E9的NEEDS_FIX/NOT_SUPPORTED_FOR_DEVICE_MIGRATION结论尚未被tester复核解除；本报告不自行授设备、迁移或activation许可。

工程 `D:/CodexProjects/VideoKit/docs/coder/d1e9a`，versionCode12 / D1-E9A-PREPARE。旧E9全部1045项、E7A200项和E8A42项只读核对，未改旧冻结文件。四文档位于 `D:/CodexProjects/VideoKit/docs/coder/D1_E9A_*_V1.0.md`；最终ZIP与外置seal由e9a_package.py生成，seal不放入自身ZIP，不预填自身摘要。

## 四项对应修复

|缺陷|实现|直接证据|
|---|---|---|
|F01/P1|真实am instrument -r非等待；启动client归还不代表actor归还。完整状态通过DUMP保护的独立有界ordered broadcast，POLL实际消耗STATUS；不依赖watcher/sendStatus。首次状态不用猜stateSeq；缺失STATUS保守扣额度；只读模式可查询并安全收尾|TRANSPORT/STATUS_GAP/IDENTITY_CLEANUP/REMOTE，最终runner源码/DEX|
|F02/P1|实际ProcessBuilder、3条pipe、reader、wait/解码和主程序所有出口有统一原owner；静态强持有及非daemon原custodian。EOF/错误时原对象和registry authority仍在原JVM，给出可识别handle/PID/本机端口与实际隔离ACK。原资源未返不能JVM自动退出|真实manager JVM+child、EOF/reader异常/输出界/console错误/close在途/UNKNOWN；只读查询实际可用|
|F03/P2|每控制原响应任务独立5秒绝对资格，包含启动、原client/pipe/等待及帧解码和身份校验，不共用55秒、不加1秒join、不重置；晚返永久PENDING，intent已发即消耗且EXECUTE/ACK不重发|CONTROL5/DECODE_DEADLINE/LATE_VERDICT/NO_REPLAY|
|F04/P2|每次observe在类锁前先撤销旧grant并领新epoch；used等早拒也撤销。旧在途调用不能晚发grant；准入检查与发布同步；Runtime失败也先撤销|GRANT/CONCURRENT_GRANT；最终新APK类的runtime失败后置断言|

## 构建、身份与来源

一次集中offline主双APK构建main-001通过，无APK repair、设备任务、依赖下载或native重编。Android源确有状态入口/phase校验变化，故没有拿旧E9 APK冒充新包；最后语义帧验证为纯PC工具差异，单独定向自检及主机JAR重新封存，APK输入保持不变。

|APK|bytes|SHA-256|
|---|---:|---|
{apks}

证书SHA-256 `{a['apks'][0]['signerCertificateSha256']}`。最终构建输入 `{inputSha}`，共{len(inputs['files'])}项。签名、manifest、实际默认runner、DEX及16KiB对齐审计通过。7个native与35个锁定依赖继承E9，FFmpeg8.0.3/Media3 1.9.3及许可状态不变。原预算/严格六帧/完整EOF/1000us、独立Kit/Flutter与其他P0不改。

实际可用PC工具JAR：`D:/CodexProjects/VideoKit/{h['artifact']['path']}`，{h['artifact']['bytes']}B，SHA-256 `{h['artifact']['sha256']}`。从已经定向编译验证的生产class打包，没有重编native/新依赖/新签名根；{len(h['productionClasses'])}个生产class，不含测试类。相对final-pc-007，{len(h['unchangedLifetimeAndSharedClassBytes'])}个共享/原生命周期class字节核对一致；最终帧验证差异有frame-validation-008输入和直接断言。默认三个入口均只inspect，无设备调用。

## 验证与明确未执行范围

19组最终映射，21次最终验证调用（19组集中验证+2组纯PC帧验证补测），{c['assertions']}断言，其中新增边界{c['boundaryAssertions']}、共享实际夹具不变量{c['sharedFixtureAssertions']}。直接运行生产ProcessBuilder/原pipe/reader/console/监督者和真实本机Java子进程；元数据部分调用共享生产registry/run/observer。未机械重跑旧32组或native套件。最终新Gradle Android类另有6个SDK桩公共入口和1个Runtime失败撤销旧grant序列通过，不冒称Android运行。

全部原始argv、输入、stdout/stderr、真实子进程边界文件/状态和失败尝试保留。首次沙箱阻止Socket.connect，原监督者按设计存活；仅失败合成夹具另存无close ACK的清理记录。随后正常本机权限下验证。Windows conhost.exe被早期夹具误计为未退出任务子进程，修正夹具识别后复验；不改生产原返回门。CLOSE_UNKNOWN有限验证证明生产JVM不会退出，最后测试controller清理仅该合成夹具，UNKNOWN未变CLOSED、无E9_PC_CLOSED、无生产close ACK；不把清理求PASS。

实际ADB/安装/设备广播、原Android raw/dup、真实媒体读写/导出、迁移、实际approval token/H_actor/catalog和activation均NOT_RUN或NOT_CREATED。没有新ABORT/清账/换budget。原N2 ABORTED0B、107218/三R三S/reserved0、原fence/档案/oldCloseACKfalse为继承事实，没有重读实际设备导出件作新声明。

D1未过、M0未启、E6B-OBS-F01长期准入OPEN。请tester整包集中复审后，由负责人决定后续有限设备身份/控制批次和最终scope。
''')
doc('ARCHITECTURE_AND_THREAT_BOUNDARY','''
# D1 E9A 架构与威胁边界 V1.0

2026-10-18。保留E8A/E9已审查的共享phase、固定catalog无环DAG、2actor有限恢复和真实原holder门；集中修PC管理链路与当前grant失效，不新增远端根、密钥或第三次APK发布。

## 非等待actor与独立状态

HostManager真正构造am instrument -r，不带-w。该client的Process/pipe归还只结算PC启动请求，绝不结算Android actor。LAUNCH前外部intent与原remote责任登记，随后即使client已退出、管道已EOF、甚至actor所有IO已归还，remote责任仍需精确正常finish或类型化原代次终止才完成。

custom runner保持异步受管生命周期；完整actor/returned/snapshot transport仅由DUMP保护的ordered broadcast返回，publish只记snapshot日志。PC每个POLL实际发送STATUS（handle/新seq/state=-1），原Run在同锁内采当前state并扣请求；写/ACK仍绑定精确state。后台原任务可推进，缺actor/returned资格信息不授写。请求未达、截断、拒绝、未知响应均不视为完成，不自动重发EXECUTE/ACK；缺失STATUS序号保守作为已消费请求/STATUS处理，不能扩大8/STATUS3。READ_ONLY_IDENTITY真实身份返回后关闭写入口，STATUS和精确失败/只读finish仍可用，晚到EXEC拒绝。

只读或未提交身份的回执可在原外部identify/returned/finish槽归档收尾，没有reserve、device业务写或COMMIT资格。最终catalog仍严格要求COMMIT phase合格返回；identity-only不能final或凭此续actor2。没有完整V2身份/有效原回执的未知路径不补造boot/start或CLOSED，保持可识别隔离，等待独立处置。

## 原PC生命周期与隔离

E9PcSupervisor在ProcessBuilder.start之前登记原Operation及原starter线程。实际start、stdin/stdout/stderr、原reader、wait、response decoder均保留原对象，线程非daemon；子进程仍活、read先EOF/失败、pipe close在途或UNKNOWN都不能算allReturned。UNKNOWN不重关求成功，生产代码没有destroy/cancel/kill。实际原等待/管道归还后仅更新资源状态，资格PENDING不回成功。

所有HostManager console出口（正常EOF、截断、超界、异常）和Deployment.Processes使用同一个原监督者。主入口停止依赖并等待两种真实结果：all originals归还且本机监听关闭的pcClosed，或由已运行原custodian实际给出的pcIsolationAck。后者只让main方法交接，不让JVM结束：同一个非daemon原线程、静态LIVE强根、原registry/manager/remote/Process/pipe仍在原JVM。测试实际证明main返回后JVM仍活且状态可读，直至原资源真返。不是把对象放在即将退出JVM的局部列表，也不是只join一个已经退出的reader。

本机127.0.0.1状态端点用session handle、PC PID、port、operation UUID和实际child PID识别原对象。STATUS/OP只读不消费Android控制额；CLEANUP仅在原输入关闭后、匹配原已审配置pin时调用原manager，允许POLL/STATUS、STOP、精确归档ACK、归档原回执、独立finish/termination和INSPECT。禁止LAUNCH/RESERVE/EXECUTE/DEPLOY/SEAL_FINAL；已发EXECUTE或ACK在registry命令账中只允许一次。pin复用原受审配置的SHA，不生成新密钥或替代approval。E9PcClient只是该原端点客户端，不接替authority或授新权限。

状态服务的Socket/accept对象同样有原holder，已知无accept的超时与UNKNOWN分开；未知accept/close停后继并保留可识别原监督，不循环新accept掩盖未知。PC最多96个原client记录、128个本机状态连接，属新增PC原对象有限管理，不改Android48 owner、8/STATUS3、10秒或文件/日志界。状态通道本身内核故障的永久UNKNOWN、本机进程被管理员终止等没有通过运行验证，不宣称故障后仍必有可用网络；已有原对象和handle不被变造为close成功。

本模型继续信任本机操作员、受审配置和同签名源码。配置pin是原scope绑定，不宣称对有配置/签名/管理员权限的主动攻击者提供绝对隔离。本机IPC不是新远端信任根，数据文件或查询BOOL不能自行成为真实原返回。手动杀原manager、改registry、重打包旧码或绕过部署门仍不受支持。

## 独立绝对期限

控制响应Operation从接受到结束的原任务只有5秒，包含实际ProcessBuilder启动、原Process/wait、pipe/reader及帧语法/身份/模式/seq验证；decoder在同一个原starter中，未返也保留。到界立即PENDING并停止依赖，不等55秒、不另join1秒、不重置，也不把随后decoder或client返回改成PASS。一般安装/本机工具保留原55秒期限；Android身份/提交仍各独立10秒且入队先保留。

观察测试中的5.0至6.5秒只是父进程计时含调度/隔离交接的有限检测范围，不是将5秒资格扩到6.5秒。原deadline比较始终5秒；受控5.5秒decoder用例在到界仍未返，真实晚返后仍PENDING。

## 当前grant的线性化

每次E9CurrentObservation.observe先调用beginCurrentObservation：清grant并取单调epoch，再进入类串行锁。used/ACTIVE/历史未知早拒也不能沿用旧grant。只有当前最新epoch、实际本host已归还的观察可发布；已有另一调用进入时，旧在途调用即使后来IO全部完成也返回SUPERSEDED_NO_GRANT。requireCurrent/require与发布/撤销同步，Runtime.observe也在authority/context失败之前撤销。

线性化的是新准入与观察尝试，不以取消别的原任务实现撤销；已开始资源仍由原owner负责。旧的物理返回历史可以保持，新的准入grant不能复用。并发定向测试实际持原guard/元数据FileChannel并卡原close，证实旧调用不晚发grant、新调用再成功及重复拒绝均按epoch处理。SDK桩进一步验证实际新APK Runtime拒绝后旧共享grant不可用。

## 保持与未证边界

PREPARE仍固定CATALOG_SHA/BASE64=ABSENT，无文件/回执能激活产品；activation的写迁移入口仍禁用。原accepted prefix1011B与完整合法后缀、107218消费/三R三S、fence/所有历史输出档案、oldCloseACKfalse、严格六帧/EOF/1000us及独立Kit/Flutter/许可P0保持。设备4文件8448B/3目录、外部20文件155648B且≤192KiB+1MiB日志、catalog实现16KiB≤24KiB、2actor/各8控制STATUS3、两phase各10秒、48仅新增Android owner均不扩。

原Android调用/广播权限/原raw或dup关闭/真正boot与start/正常finished inst和当前host实机观察均NOT_RUN。本机Java真实进程不冒称ADB或Android；UID/inode/目录fsync及合成OS日志仍为元数据平台替身。原始失败与合成夹具清理均留痕，清理不授Java ACK。E9A静态自检不自动关闭D1、M0或长期准入。
''')
doc('REMAINING_GATE_REVIEW',f'''
# D1 E9A 剩余门与定向证据 V1.0

2026-10-18。19组最终映射/21次最终调用、{c['assertions']}断言（边界{c['boundaryAssertions']}，共享夹具不变量{c['sharedFixtureAssertions']}）。原始已执行argv在每attempt/commands.json，输入摘要和stdout/stderr、原进程状态/主退出边界文件保留。final-pc-007支持原生命周期各组；frame-validation-008仅补最后纯PC语义帧校验，两组替换映射，旧3份源版本保留。最终生产JAR中共享/生命周期字节与007对照，避免把主机收尾改动掩盖为重复APK构建。

下面PASS仅限已执行列，不是全部排列或Android资格。复用旧Fixture构造合成元数据和调用实际生产对象，未执行旧32组main、未复跑native，不累计其历史PASS。

|组|实际生产对象|已执行有限范围|NOT_RUN/限制|
|---|---|---|---|
{table}

另：实际新Gradle输出的6个Android公共入口使用SDK桩在平台前拒绝；Runtime成功共享观察→Runtime拒绝→requireCurrent失败序列通过。不是Android系统执行。实际生产host JAR三个默认入口只inspect通过，JAR不含夹具/清理测试类。

## 失败尝试和夹具收尾口径

main-001的Socket.connect被沙箱拒绝，原非daemoncustodian保持存活，后续只对精确新建合成夹具保存无ACK清理记录；不作PASS。pc-local-002在正常本机权限通过真实IPC。关闭UNKNOWN的早期夹具把Windows conhost.exe算作业务child，断言失败且生产监督正确保持；修正夹具只允许原Java任务已退出、剩余仅OS控制台宿主后，才清理该合成manager。004/005失败和006修复证据未覆盖抹去。

最终CLOSE_UNKNOWN的通过点是原holder=UNKNOWN、allReturned=false、原JVM仍活且状态可查、child已真正退出；随后controller终止有限观察夹具是测试清理，不是生产退出路径、没有E9_PC_CLOSED、不生成close ACK。生产JAR没有destroy/cancel/kill；此分界必须随报告转交，不能简写为“UNKNOWN后关闭成功”。其他正常原返回场景自然退出，无此强制收尾。

## 仍开放的门

1. tester对E9A整包独立复审尚未完成，E9原NEEDS_FIX/NOT_SUPPORTED_FOR_DEVICE_MIGRATION未自动解除。
2. 非等待真实Android启动、receiver可达/DUMP权限、完整registered/readonly会话、原raw/dup/dirsync、实际5秒链路调度、boot/start来源及系统normal finish仍NOT_RUN。永久PC start/close/监听UNKNOWN和全部内核异常未穷举。
3. 负责人另派device/最终scope与有效实际授权；本包不填造registry/migration/actor/H_actor/catalog/approval token，也不复用旧E3许可。只有合成SYNTHETIC_LOCAL夹具，不可导出真实release。
4. 缺完整V2身份/原回执、未知管理head、恢复资格不足或torn内容仍隔离，不补boot/start/旧JavaACK，不新ABORT/清账/换budget或启actor3。PC custodian须保留，不能手动kill充close。
5. 真实final facts独立接受后才能另派activation，同一实现、精确同catalog/head及实际APK release绑定；本批没有activation。
6. E6B-OBS-F01须实际新host持原guards、核当前完整合法账本/无pending并真正返回才能关闭。本地/SDK桩无此资格。D1未过/M0未启/长期准入OPEN，其余P0及历史FAIL保持。
''')
doc('DEVICE_EXECUTION_APPENDIX',f'''
# D1 E9A 精确后续设备附录 V1.0

2026-10-18。本附录供静态审查，不是执行许可。当前无ADB/设备/媒体/真实迁移/activation；tester集中复审后负责人再定有限身份/控制批次与最终scope。旧E3许可已消费，不复用；本包没有真实配置、token、迁移UUID或H_actor。

## 唯一prepare候选

version12/D1-E9A-PREPARE；com.videokit.app / com.videokit.app.test；原证书 `{a['apks'][0]['signerCertificateSha256']}`。合同app UID10221、test UID10222须在后续实际部署前核实；没有本轮设备观测可代替。

|APK|bytes|SHA-256|
|---|---:|---|
{apks}

APK目录 `D:/CodexProjects/VideoKit/docs/coder/d1e9a/artifacts/D1-20261018-E9A/final/`。同目录生产host JAR {h['artifact']['bytes']}B，SHA `{h['artifact']['sha256']}`，用已验证的Android Studio自带JBR启动；不含测试类。源码/class来源见host-binary-provenance.json。所有下述参数都是未填的受审输入，不是本轮可执行指令。

## 非等待、模式和状态

实际组件 `com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation`。e9Case=legacyN2Migration；e9Batch=D1-E9A-PREPARE-TABLET-20261018；e9Mode仅READ_ONLY_IDENTITY或REGISTERED_MIGRATION；e9Request是严格canonical identityRequest的URL-safe无padding Base64。无class/FD参数，实际launcher为am instrument -r，无-w。client命令退出不意味着Android actor、IO、正常finish或迁移完成；不从空stdout推断成功。

未来 `E9HostManager --approved-session <实际受审配置> <实际配置SHA>` 才开会话，默认无参数只inspect。配置沿E9 managerTrust字段，精确plan/app-test SHA/原签名/UID/版本/sourceReview/授权和评审引用/registryPath/NEW或已知head均须负责人提供，不以任意64hex本身当批准。

LAUNCH必须明确mode（文档要求显式填）；实现兼容缺mode时REGISTERED_MIGRATION，但任何模式都不自动RESERVE/EXECUTE。先外部登记，再非等待启动并保留remote责任。POLL实际发一个STATUS，seq消费，state=-1由原Run原锁取当前state；完整transport来自DUMP保护的ordered broadcast。其他控制仍用当前原stateSeq。初次缺receiver、无有效帧、actor/returned尚缺资格资料或超时均不得授写，停止依赖并保留原管理者；不通过等待client stdout求首帧，不循环STATUS。缺失序号保守扣额；actor总8请求、STATUS最多3。

READ_ONLY_IDENTITY身份返回后关闭写入口，STATUS仍可查询，所有晚到EXEC拒绝。已验证的有V2身份且原IO真返的identity-only回执可以ARCHIVE_RETURN、精确ACK_FINISH和独立正常finish，只有PC原责任结束，没有reserve/COMMIT/final/actor2资格。只读诊断与未来正式迁移应由负责人另派各自scope；不自动把已结束只读scope复用成写scope，也不自行生成新scope绕成本。

## 原执行与5秒控制

正式REGISTERED_MIGRATION只有身份原归还、外部BOUND reserve force/close/readback后才允许EXECUTE。接受写时先保留原队列/资格；身份和提交各10秒独立，不能重置未返原操作。每个STATUS/EXECUTE/ACK/STOP响应有同一个原5秒绝对任务，覆盖start/process/pipe/wait/语义解码，超时永久PENDING；一般安装和独立PS/logcat查询仍有原55秒界。已发EXECUTE或ACK intent只允许一次，即使未知回复也不换seq重发。

原返回必须精确actor/handle/seq/资格和全部原holder；外部真实归档相同return bytes后ACK同hash。正常finish独立核原PID不在、唯一E9_FINAL_FINISH锚点、其后ActivityManager Force stopping/Killing finished inst，不再以等待式instrument client结束当finish。只有符合实际最终scope的最后合格commit与全部前序处分才能审final；正常身份/失败收尾不激活。

actor2仅在原确切代次终止且SELF_NO_FD_TRANSFER，或原真实晚返非合格+正常finish后有限恢复。旧Java ACK不补写。原身份或返回不可验证就保留未知，不杀陌生PID，不启actor3，不删除torn对象或重新ABORT。

## PC输入丢失后的原管理者

实际管理者先打印E9_PC_SUPERVISOR_READY（handle、PC PID、本机127.0.0.1 port）。EOF/错误后pcIsolationAck只表示同JVM非daemon原custodian实际接管，不表示JVM/actor/pipe已结束。保留该JVM，禁止手动终止它冒close。真正全返且监听关闭才有E9_PC_CLOSED。

同JAR的 `E9PcClient --status <port> <原handle>` / `--operation <port> <原handle> <operationUUID>` 查询原对象，不碰设备、不耗Android STATUS。收尾 `--cleanup <port> <原handle> <原配置SHA> <canonical命令文件> <该命令SHA>` 只面向原受审配置和原manager；允许有限POLL/STATUS/STOP/精确归档ACK/原回执/独立finish或termination/INSPECT，拒绝新LAUNCH/RESERVE/EXECUTE/DEPLOY/SEAL_FINAL。不能以查询结果另造authority，也不能重启另一manager自动续未知head。状态通道本身UNKNOWN需原隔离处置，不能以杀JVM排除。

PC客户端只是查询/收尾桥，不是新根；仍是受信本机操作员合作模型，不宣称阻止有原配置/签名/管理员权限的人绕流程。禁止-d、uninstall/clear/restore/force-stop未知actor、换budget或手工装未批准高version旧码。

设备4文件/8448B/3目录、外部20文件155648B且≤192KiB+原日志1MiB、catalog实现16KiB≤24KiB、2actor/各8控制STATUS3、两phase10秒、48新增Android owner及原框架界不变。PC原对象96/本机查询128只界定新本机监督记录，不扩大Android请求或owner。

## 后续activation和当前结论

真实final facts独立接受后另派E9HostActivationSession阶段，同原实现、精确同head/catalog、同原签名和必要role/入口/版本差异；先固定实际catalog build input，再登记实际APK SHA，不能产生自指。当前PREPARE/catalogABSENT，无activation包、实际H_actor或approval token。之后每个新host仍要E9Runtime.observe实际核原guards/fence/完整合法后缀/无pending并原返回；旧4869退休历史例外不豁免当前原资源，也不复用旧livegrant。

当前D1未过、M0未启、长期准入OPEN；不启动正常四例、真实媒体导出或native fault测试。独立Kit/Flutter、严格六帧/完整EOF/1000us、原107218/三R三S/档案/fence/oldCloseACKfalse及许可P0保持。
''')
new(B/'E9A_PROGRESS_FINAL.md',f'''# E9A completed static candidate
2026-10-18. Four dispatched findings implemented; independent review pending. Final19 groups/21 targeted invocations/{c['assertions']} assertions, actual local ProcessBuilder/pipe/console/custody boundaries and shared metadata grant checks. SDK six public entries + one Runtime invalidation sequence. One offline prepare dualAPK main001 passed, no repair/native/old32/ADB/media/actualscope/catalog/approval/activation. Final host-only frame validation008, production155-class JAR with exact lineage. Historical denied-socket/fixture-conhost failures and explicitly no-ACK fixture teardowns preserved; UNKNOWN hold tests do not claim close success. E9 all1045 immutable must remain unchanged. Four docs/evidence/SBOM/source diff/freeze tools provided. D1 not passed/M0 not started/E6B-OBS-F01 OPEN. No subagents. Supersedes working E9A_PROGRESS.md.
''')
print('E9A four documents and19-case mapping written; assertions',c['assertions'])
