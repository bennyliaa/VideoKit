"""Generate the four E9 delivery documents and exact finite-case mapping from recorded local facts."""
import csv,hashlib,json,pathlib,re,shutil
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2]
def read(name):return json.loads((B/'evidence'/name).read_bytes())
checks=read('local-check-results.json');audit=read('apk-audit.json');build=read('build-results.json');inherit=read('external-readonly-verification.json');source=read('source-derivation.json')
def put(p,text):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text.strip()+'\n')
def doc(name,text):put(R/f'docs/coder/D1_E9_{name}_V1.0.md',text)
apks='\n'.join(f"|{x['role']}|{x['bytes']}|`{x['sha256']}`|" for x in audit['apks'])
scopes=[
('A01','实际身份读取异常、未BIND、execute无许可，业务open/write为0','E9MigrationRun/E9MigrationTransaction/E9Phase','身份FD close UNKNOWN专门注入未做；Android身份所有失败切点NOT_RUN'),
('A02','UID/PID/start/descriptor/bootKind/task拒绝、错误reserve、含括号proc解析','E9Actor/E9ProcessIdentity/E9Registry','全部字段笛卡尔组合及Android权限失败NOT_RUN'),
('A03','初始外部授权引用force失败；reserve WRITE/FORCE/CLOSE_AFTER/READ失败无写许可','E9Registry.Store/reserve','磁盘掉电及进程崩溃NOT_RUN'),
('A04','已预留但尚未执行时FD计数0仍不safe；早ACK令PENDING；失败返回可归档收尾不可final/actor2','E9MigrationRun/E9Registry','真实Android线程调度NOT_RUN'),
('A05','intent open前/后、write/force/read/close前/后Exception和Error；mkdir/dirsync异常','E9MigrationTransaction/E9OwnedFiles/E4Owned','mkdir/dirsync每个Error/永久阻塞排列NOT_RUN'),
('A06','payload和commit七个切点各Exception/Error，不能final','E9MigrationTransaction/E9Registry','任意中间字节截断组合NOT_RUN'),
('A07','同一完整commit，lease unlock后close等待；另一真实JVM锁可取得，finish仍0；10秒后真实晚返仅PENDING','E9MigrationRun/E5BGuard/E9Registry','Android raw/dup close及真正10秒墙钟NOT_RUN；本地时钟受控'),
('A08','所有数据close后最后owner guard native close已发生但抛UNKNOWN，原holder不归还、不产return proof/finish','E9OwnedFiles/E4Owned/E9MigrationRun','Android内核close UNKNOWN NOT_RUN'),
('A09','队列到界执行前不写；身份到界前不打开资源；永久PENDING','E9MigrationRun','真设备超时与调度NOT_RUN'),
('A10','伪造/错actor/非0未返原回执拒绝','E9Evidence/E9Registry','真实管理链路断连NOT_RUN'),
('A11','finishClaimed及假的系统finish证据不足以final','E9MigrationRun/E9Registry.captureNormalFinish','真实ActivityManager日志和原PID缺席NOT_RUN'),
('A12','returned/checkpoint/seal各WRITE/FORCE/CLOSE_AFTER/READ失败，不发布final authority','E9Registry.Store/sealFinal','真实PC崩溃/掉电NOT_RUN'),
('A13','错head/活actor重开拒绝；重复控制seq消耗后不得重复写','E9Registry.openKnownHead/commandIntent','真实管理进程失联NOT_RUN'),
('A14','完整device commit及合格synthetic catalog仍无法使PREPARE产品/观察激活','E9Phase/E9Registry/E9Catalog','实际activation包尚未构建'),
('A15','旧actor活着、无终局证据时actor2拒绝；同代proc仍活拒绝','E9Registry/E9ProcessIdentity','真实boot/PID复用NOT_RUN'),
('A16','旧close UNKNOWN后以合成OS确切终止处分启actor2；actor2实际各holder返回，catalog旧return保持ABSENT','E9Registry/E9MigrationTransaction/E9Catalog','终止证据平台来源为替身；Android死亡NOT_RUN'),
('A17','旧actor10秒晚返+正常finish，actor2新身份新资格，保留旧PENDING','E9MigrationRun/E9Registry/E9Catalog','Android正常finish来源替身'),
('A18','payload完整commit缺席时actor2只补建缺失项；0B torn commit隔离、不覆盖','E9MigrationTransaction/E9Catalog','全缺席、torn intent、所有部分长度组合未逐一执行'),
('A19','actor2 close UNKNOWN后无actor3；原3R/3S、107218、档案和fence不变','E9Registry/E9OwnedFiles/E9LegacyState','原设备全部导出件当前hash未重读'),
('A20','事件head固定不含未来APK/catalog自指；另存release不改head；错auth/未知外部文件拒绝；合成catalog禁止导出发布policy','E9Registry/E9Catalog/E9ActivationPolicyExport','实际DEVICE catalog/H_actor/activation均NOT_CREATED'),
('A21','错误信任pin/environment/registry/actor清单/schema/device commit；当前payload/pending/guard/ledger/close失败分别无grant','E9Catalog/E9CurrentObservation/E5AAdmission','4个当前失败子例分独立JVM；真实activation/设备NOT_RUN'),
('A22','合法完整追加R/S消费7B被接受；真实本地新观察持guard/账本并实际close，仅本进程grant；prepare仍拒绝产品','E9CurrentObservation/E9LegacyState','UID/inode/目录fsync替身；不同真实Android host NOT_RUN'),
('A23','身份真实返回、无execute预留，关闭写入口后精确ACK可结束；晚到EXEC拒绝','E9MigrationRun','实际Android广播竞争NOT_RUN'),
('D01','新鲜编译冻结E7A真实旧reader，未知marker仍FRESH；旧字节在新dispatch gate install前拒绝','真实旧E5AFinalObservation/E9DeploymentGate','旧Platform的死亡/guard/目录fsync为替身；不是设备旧码重装'),
('D02','高version/相同证书/伪ABI的未知完整字节，inspect及install均0','E9DeploymentGate','未实际重签/安装旧APK'),
('D03','候选phase不符拒绝','E9DeploymentGate','所有错签名/UID/package组合未逐一枚举'),
('D04','已安装有相关进程时拒绝','E9DeploymentGate/E9Registry','实际base.apk/进程观察NOT_RUN'),
('D05','实际PC端port解析、候选再hash、固定install-r双命令；任意uninstall拒绝；检查后替换成已知旧字节也install0','E9HostDeployment/E9DeploymentGate','Commands为OS替身，无adb.exe或真实安装调用'),
('D06','安装后实际Port返回SHA不符，结果拒绝','E9DeploymentGate','实际安装和组件验证NOT_RUN'),
('D07','prepare共享phase/预算/初始化/旧reader/旧恢复直接拒绝；另6个实际新编译Android公共入口先于平台拒绝','E9Phase/E4FencedTask/E4OutputBudget/6 Android entry methods','SDK桩非Android设备；Binder/服务事务仅源码/DEX核查'),
('D08','外部revoked json/未登记activation release不构成代码撤销或激活','E9Registry/E9DeploymentGate','实际撤销release未派发'),
('D09','同历史head的后续合成compatible release可以精确deploy gate；prepare仍拒绝产品','E9Registry/E9DeploymentGate','部署OS替身；真实activation未构建/安装')]
assert len(scopes)==32
counts={x['case']:int(re.search(r'assertions=(\d+)',x['stdout']).group(1)) for x in checks['results']}
with (B/'evidence/test-mapping.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['group','localStatus','assertions','actualProductionObjects','executedScope','notRunOrPlatformBoundary'])
 for case,scope,objects,gap in scopes:w.writerow([case,'PASS_FINITE_LOCAL_SCOPE',sum(v for k,v in counts.items() if k==case or k.startswith(case+'-')),objects,scope,gap])
mapping='\n'.join(f'|{case}|{objects}|{scope}|{gap}|' for case,scope,objects,gap in scopes)
doc('DELIVERY',f'''
# D1 E9 集中实现交付 V1.0

2026-10-18。本包为静态审查候选 `D1-20261018-E9`，versionCode 11、versionName D1-E9-PREPARE。集中实现 E8A 接受的共享phase、外部registry/catalog、受管双phase actor、有限恢复、当前host观察和精确部署门。本包尚未获得tester静态接受，不是D1通过或项目正式交付。

源码工程：`D:/CodexProjects/VideoKit/docs/coder/d1e9`。四文档位于 `D:/CodexProjects/VideoKit/docs/coder/D1_E9_*_V1.0.md`。最终ZIP和外置seal由 `tools/e9_package.py freeze` 产生；seal不放入自身ZIP，不在本文预填自身hash。原始E7A 200项、E8A 42项冻结对象全部只读核对一致。

## 实现与可核证据

`src/.../E9Record` 是app与PC共用严格、排序、逐字节规范JSON；`E9Actor/E9Evidence/E9Catalog` 共用身份和证据解释。`E9MigrationRun` 在入队前保留操作，identity和commit各独立10秒，任何PENDING不可恢复成成功。`E9OwnedFiles/E9MigrationTransaction` 持有原资源，CREATE_NEW仅写新控制命名空间；锁释放不作为close回执。

`E9Registry` 为实际外部规范writer/reader/sealer。head只链接先前已落盘的证据记录；catalog/checkpoint/seal/未来activation-release不反向进入head。重新打开必须提供已知精确head，活跃/不连续/未锚定记录/错误授权引用/未知文件隔离。实际安全失败返回允许归档与正常结束，但不获得final，也不自动获得actor2。恢复只接受原actor真实晚返且正常finish，或精确代次终止且不伪造旧Java返回。actor2自身也UNKNOWN即停止。

`E9CurrentObservation` 在每host重新持原guards、核当前fence/档案/完整账本和已接受前缀/无pending/控制清单，并在本host真实返回后授liveproof。`E9Phase/E9BuildPolicy` 在prepare固定ROLE=PREPARE、CATALOG_SHA/BASE64=ABSENT；全部产品入口拒绝。旧reader/recovery入口禁用，旧debug instrumentation也封闭。

实际PC工具 `E9HostDeployment/E9HostManager/E9HostActivationSession` 共用生产registry和dispatch gate。无参数只inspect；本批只执行了默认inspect、编译和synthetic拒绝。未来受审配置及执行许可必须由负责人另派。未来policy导出先绑定真实final catalog，再构建APK、再登记实际APK SHA；没有要求未来APK hash先进入catalog的循环。

## 构建与APK

一次离线主构建main-001因公开SDK无O_DIRECTORY常量失败；仅移除不可用标志，保留lstat/fstat目录角色校验，repair-001离线通过。原输入与失败日志保留，无无关旧测试、native重编或依赖下载。双APK签名校验、服务manifest、DEX入口及16KiB原生库对齐校验通过。

|APK|bytes|SHA-256|
|---|---:|---|
{apks}

证书SHA-256：`{audit['apks'][0]['signerCertificateSha256']}`。最终构建输入SHA-256：`{build['attempts'][-1]['inputSnapshotSha256']}`。APK位于 `docs/coder/d1e9/artifacts/D1-20261018-E9/final/`，以实际工程绝对根目录解析。7个native库与冻结E7A逐字节一致，锁定35项依赖无变化；FFmpeg 8.0.3、Media3 1.9.3及许可状态继承，未作商业清权声明。

## 本地验证结论与范围

32组映射，36个最终映射JVM进程、D05针对性修复另2次，最终映射断言 **{checks['assertions']}**。它们直接调用生产对象；不是另写状态模型求PASS。全部失败尝试、自检输入、stdout/stderr、平台切点轨迹保留。D05在最终检查发现PC端再hash允许集合过宽，收紧为本次候选app/test，增加“检查后替换成已知旧包”用例通过；仅host工具变化，未触发APK重复构建。6个实际最终Gradle编译Android公共入口在SDK桩上先于平台调用拒绝；未来host工具实际编译/default/synthetic-release拒绝通过。

真实JVM文件、FileChannel锁、原E4Owned holder、原事务及registry均执行。Android UID/inode/目录fsync、boot/proc来源、ActivityManager正常finish日志为替身；受控时钟不冒称真实10秒。Windows锁读取适配复用同一guard channel。用于模拟确切进程终止或最终清理的native facsimile释放不修改原UNKNOWN holder，不提供旧Java ACK。具体有限范围和未跑子例见剩余门文档与test-mapping.csv。

本批设备/ADB/真实迁移/真实媒体读写或导出/真实H_actor与approval token/activation构建均NOT_RUN或NOT_CREATED。没有新ABORT、清账或换budget。原N2 S0=ABORTED 0B，消费107218、三R三S、reserved0、原fence与oldCloseACK=false保持为被继承事实；未重读实际设备导出件冒称新验证。

D1未过，M0未启动，E6B-OBS-F01长期准入仍OPEN。请tester依据整包源码、输入和原日志独立静态审查，再由负责人决定后续设备与最终scope。
''')
doc('ARCHITECTURE_AND_THREAT_BOUNDARY','''
# D1 E9 架构与威胁边界 V1.0

2026-10-18。基线为冻结E7A，设计依据为E8A四文档和独立静态接受报告。本实现不改变原资源框架计数、时限或native协议；48仅是新增owner集合上界。主要变更及逐文件来源见evidence/source-derivation.json和diffs。

## 权威与无环顺序

受信本机操作员保管的批准plan/pin/授权引用/独立审查引用 → prepare双APK完整SHA+原签名+sourceReview → actor预写身份实际返回 → 外部BOUND reserve实际force/close/readback → actor commit实际操作与原返回 → 精确回执外部归档 → ACK_FINISH → 原instrumentation正常finish与OS事实 → 最多一次恢复actor重验证 → 最终events head H_actor → final catalog → checkpoint → seal → 未来activation包固定同catalog/head → 单独activation-release记录实际APK SHA。

events仅引用已有较早证据，不引用catalog/checkpoint/seal/未来APK。seal本身及ZIP seal都不对自己求hash。本批真实链未执行；SYNTHETIC_LOCAL测试链不能成为DEVICE_HA1Q6WXR的发布输入。E9Phase只读取编译固定release authority，不接受device hash、instrumentation参数或外部BOOL作为激活开关。prepare无论文件/回执多完整都不激活。

## 资源与收尾

E9MigrationRun构造即开始identity资格钟；bindAndReserve接受时即保留commit和资格钟，worker启动不会重置。FD尚EMPTY但操作已保留依然未返。核心状态、seq、8控制/STATUS3、ACK hash及finish仅一次由同一对象管理。10秒到界、控制异常或原资源UNKNOWN形成永久PENDING；晚返仅更新资源已返回状态。没有Future.cancel、强杀或把锁重获当资源归还。

E9OwnedFiles在open之前登记IO-free mutable handle；Android raw/dup/stream/lock均保留原对象，逐一unlock/close，不重试未知close。数据holder先返回，最后guards返回。错误保留首因与cleanup suppressed。身份FD也属原identity集合。受管Instrumentation用DUMP权限动态广播入口，限定case/batch/mode/handle/seq/state，不接FD；onStart返回不会触发JUnit自动结束，平台finish仅经过精确ACK与真实safe边界。失败发生在任何自身IO之前的拒绝可安全终止，但不形成迁移成功authority。

迁移只写三层新控制目录：legacy-acceptance/M/actors，以及0001.intent、可选0002.intent、n2-v2.acceptance、n2-v2.commit。单文件上界2048/2048/4096/256，总8448B；只CREATE_NEW，已有完整对象逐一精确重验，截断/错内容/额外项隔离，不覆盖或删除。每个原目录/文件/完整账本保持检查，未追加业务R/S。

actor2只有两种前序处分：真实晚返非合格且正常finish，或精确原boot/PID/start代次终止且SELF_NO_FD_TRANSFER。前者保留旧PENDING；后者旧Java返回继续ABSENT，不能写成CLOSED。actor2使用新attempt/handle、真实身份和独立资格，逐一返回自身原资源。缺外部旧身份/回执不重建authority，actor2未知没有actor3。

## 每host与产品边界

当前host使用固定release catalog，仅退休legacy V1 PID4869的历史查询例外；不豁免当前host、当前actor或当前资源。实际持原owner/lease guards，匹配UID/dev/inode/fence，核13项原档案元数据、N2 0B输出、完整合法链及固定1011B已接受前缀、合法后续R/S与预算、无active pending，再核精确控制inventory和摘要。只有本host原force/fsync/close全部返回才创建liveproof；失败先失效旧grant并保留未知owner，不复用旧host证明。

prepare入口在Session/CpuTaskClient构造之前、CPU source/验证、任务initialize、预算reserve、codec BEGIN/debug、CPU START/debug及encoder create上应用共享phase。原低层guard/close primitive仍供迁移及cleanup，不把“通用primitive存在”当公开产品绕过入口。旧E5观察/恢复及E7A debug入口明确禁用。activation的可写迁移入口在requireMigrationPair第一步拒绝；源码共用，不需要第二套迁移模型。

## PC工具与成本

外部registry固定20种文件、155648B元数据cap，同时不超过192KiB；原日志额外合计1MiB。catalog实现上限16KiB，比合同24KiB更窄。固定2actor，各8控制/STATUS3。任何PC原open/force/close不确定导致store不可继续。日志/进程超时保留原对象，不自动kill/retry。PC实际dispatch只发目标HA1Q6WXR的install-r app/test，核完整候选SHA/审核角色ABI/原证书/已装精确pair/UID/版本/无相关进程，并在dispatch前再次仅比对本次候选SHA，安装后复核。CLI默认inspect，activation CLI与原迁移阶段分开，使用同一registry/catalog/gate，既有release不重试。

本机批准配置和hash由受信操作员/负责人保管，本工具不是远端签名服务器，也没有新密钥或新硬件根。拥有同签名重打包、adb/管理员权限或可任意改本机registry/编译固定常量的人可以绕过合作部署流程；不宣称Android绝对阻止高version旧码。真实旧E7A reader会忽略新marker的限制已由真实旧类证明。外部撤销json也不能追溯修改旧程序，必须部署源审查兼容版本。

同UID主动并发替换父目录、恶意native/内核、root或恶意operator不在当前静态合作模型保证内；NOFOLLOW、lstat/fstat及当前guards仍用于正常竞态/误配失败关闭。设备fsync/锁/boot source/日志来源的真实有效性未通过本地替身证明。Kit独立于Flutter、帧不经Dart、六帧/full EOF/1000us、原预算身份和全部许可P0均保持；当前仍非正式交付。
''')
doc('REMAINING_GATE_REVIEW',f'''
# D1 E9 剩余门与有限自检映射 V1.0

2026-10-18。下面PASS仅指表内已执行的有限本地范围，不代表每个设计子排列、Android实测、D1通过或正式准入。32设计组按实际生产对象映射，36最终映射JVM调用、D05针对性修复另2次，共{checks['assertions']}个最终映射断言。A21四个当前状态失败追加子例使用独立JVM，未清空生产静态保留集合来制造恢复。

完整日志入口：evidence/local-check-results.json、selfcheck-attempts/final-production-009、replacement-cut-011；test-mapping.csv含断言计数。001至008所有失败/诊断/扩展尝试保留。主修复原因为Windows锁读取适配和实际资源检查；失败返回归档与host端dispatch检查也有明确测试。旧reader由冻结E7A源码新鲜编译、独立classloader加载，平台替身仅提供其允许继续的条件，未复制旧判断模型。

|组|实际对象|已执行有限范围|未执行或平台边界|
|---|---|---|---|
{mapping}

## 仍开放的验收门

1. tester整包独立静态代码/证据审查尚未完成。当前包不自动获得设备、迁移、activation或正式交付许可。
2. Android真实boot/proc/UID权限、目录stream/fsync、FileChannel锁、原raw/dup close、广播seq竞争、真正10秒资格及正常instrumentation finish证据均NOT_RUN。本地替身不替代这些事实。
3. 负责人另派最终device scope、registryID/migrationID、精确prepare plan SHA/授权引用/独立最终review后，才可能运行真实actor。当前没有真实H_actor、catalog、approval token或新执行许可。
4. 实际actor最多2；未知对象/管理断链/恢复资格不足/部分torn内容均隔离，不能用第三actor、补旧ACK、删目录或新ABORT解决。未覆盖子例须由tester决定是否补充本地验证，不能预填PASS。
5. 真实final事实到齐、独立封存接受后才可另派activation发布。须固定精确同catalog/head、同原证书、必要role/入口差异及更高版本；本批没有构建它。
6. E6B-OBS-F01只有实际新host核当前原guards/完整账本/无pending并真实返回后才能关闭；静态代码和合成catalog不能关闭。D1未过，M0未启，长期准入OPEN。

原N2旧V1没有boot/start，不能补造；原close ACK=false保持。原消费107218、reserved0、三R三S和输出/档案hash来自冻结证据，当前没有重新读取真实媒体作新声明。稳定性、独立Kit/Flutter、许可与全部其他P0继承未变。
''')
doc('DEVICE_EXECUTION_APPENDIX',f'''
# D1 E9 精确设备执行附录 V1.0

2026-10-18。本文是静态可审的后续边界，不是执行许可。当前设备/ADB/真实媒体/真实迁移/activation均未执行。负责人必须在tester整包静态接受后另行确定device与最终scope；本批不生成真实批准配置、token、registryID/migrationID或H_actor，也不复用已消费E3许可。

## 唯一候选与入口

目标只允许未来正式范围中的HA1Q6WXR，包名com.videokit.app与com.videokit.app.test，原应用UID10221，合同test UID10222必须在实际部署前核实一致。候选version11/D1-E9-PREPARE，原签名证书 `{audit['apks'][0]['signerCertificateSha256']}`。

|APK|bytes|SHA-256|
|---|---:|---|
{apks}

实际构建instrumentation组件为 `com.videokit.app.test/com.videokit.spike.e4.E9MigrationInstrumentation`，不含默认AndroidJUnitRunner入口。精确选择参数：e9Case=legacyN2Migration，e9Batch=D1-E9-PREPARE-TABLET-20261018，e9Mode只能READ_ONLY_IDENTITY或REGISTERED_MIGRATION，e9Request为严格canonical identityRequest的URL-safe无padding Base64；禁止class及FD参数。

READ_ONLY_IDENTITY只采身份并在真实返回后互斥关闭写入口；即使再收到EXECUTE也拒绝。负责人如先派该只读诊断，须独立限定非迁移scope、采集transport、真实原返回及精确失败/只读finish；本包HostManager专用于正式REGISTERED_MIGRATION，不把只读结果写成commit authority。请求含bootKind明确选择KERNEL_BOOT_ID或SYSTEM_BOOT_COUNT；权限不可核验失败关闭，不回退V1或墙钟。当前没有可直接执行的真实request。

## 外部管理与正式迁移顺序

未来受信配置必须严格含kind=managerTrust、完整规范preparePlan及其精确SHA、授权引用、独立review引用、外部registry绝对路径、NEW或明确已知head、原已装完整app/test SHA/版本/role/ABI。plan包含原descriptor SHA、实际候选完整pair SHA、证书、UID、sourceReview及DEVICE_HA1Q6WXR。仅存在64位hex字符串不证明其被批准；负责人须保管实际批准输入及pin。

HostManager无参数只inspect。未来受管会话入口为 `--approved-session <实际受审配置文件> <实际配置SHA>`；这些是明确未填值，不是本轮命令。进入后只接canonical managerCommand：DEPLOY_PREPARE、LAUNCH、POLL、RESERVE、CONTROL、ARCHIVE_RETURN、CAPTURE_FINISH、CAPTURE_TERMINATION、SEAL_FINAL、INSPECT。LAUNCH带ordinal/attempt/handle/bootKind；RESERVE带predecessorIntent；CONTROL仅STATUS/EXECUTE_COMMIT/ACK_FINISH/STOP_DEPENDENCIES，并从原transport派生当前seq/state/handle。所有控制先记外部intent，未知回复不自动重发；每actor8请求、STATUS最多3。PC进程及reader必须保持至原命令真实返回，stdin丢失也不强杀设备原actor。

正式顺序：核已装精确pair/原签名/版本/UID/无相关活进程与未知owner → 经真实dispatch门install-r候选并复核 → 外部CREATE_NEW launch登记 → 原identity实际返回 → 外部identity/reserve force-close-readback BOUND → EXECUTE先预留commit → 等原操作和所有holder返回 → 精确returned外部归档 → ACK_FINISH匹配同hash和seq/state → 确认原instrumentation命令正常结束、原PID不在、唯一E9_FINAL_FINISH锚点及其后ActivityManager Force stopping/Killing finished inst → 独立最终审查。

正常失败已真实返回可归档并finish，但不得final。永久PENDING晚返只非合格；恢复actor2必须有原late-return+normal-finish或经审查的确切原代次termination证据。CAPTURE_TERMINATION读取独立平台采集并归档的规范probe，本包没有执行该采集；actor2 Android identity仍重新核旧代次确已不活。任何原UNKNOWN不因重新取锁、PID不存在、当前文件完整或管理器bool变成Java CLOSED。

新设备控制只允许M/actors下0001.intent、可选0002.intent、n2-v2.acceptance、n2-v2.commit，合计最多8448B/3目录；不覆盖/删除任何原文件，不动原107218、预算身份或R/S。外部20文件155648B/192KiB元数据+1MiB原日志，catalog实现cap16KiB（合同24KiB以内）。任何超界、额外文件、断head、torn内容或缺旧身份/回执立即隔离并报告负责人，不自动换scope/补请求/第三actor。

## 未来activation阶段

只有真实final接受并封存后，由负责人另派受审activationTrust配置（plan/pin/授权/review/registryPath/精确head）。`E9HostActivationSession`默认也只inspect；未来 `--approved-export` 只导出同final catalog固定policy源码，随后构建必要role/catalog/版本/入口差异的双APK，再由新的实际release文件绑定APK SHA、sourceReview、原签名和同head/catalog。未来 `--approved-deploy` 经同一实际dispatch gate部署，CREATE_NEW release先消耗该部署流程，未知安装不自动重试。当前不调用这两条路径；本地已验证SYNTHETIC_LOCAL输入在任何导出/设备调用之前被拒绝。

新host的产品测试还须走E9Runtime.observe，退休4869历史查询0仅适用于该固定catalog中的legacy例外；当前host必须真实持guard、核完整合法账本后缀、无pending、force/fsync/close全返。prepare即使完成迁移也不能运行正常四例；activation也不能写迁移。本批没有新正常四例、媒体导出、native fault、D1验收或M0启动。

不支持-d、卸载/clear/data restore、force-stop原未知actor、清账、换budget或手工绕过SHA门；拥有管理员权的人仍可绕过合作流程，本附录不宣称Android绝对阻止。旧runner/旧reader不会因device marker或外部撤销json自动懂新政策，必须经源审核兼容代码与完整SHA部署。
''')
# Preserve exact compiler response files, and explicitly identify command reconstruction (no rerun).
work=B/'.selfcheck/final-production-009';target=B/'evidence/selfcheck-attempts/final-production-009'
for name in ['compile.args','compile-frozen-reader.args']:shutil.copyfile(work/name,target/(name+'.txt'))
manifest=dict(scope='Exact argv reconstructed from the preserved runner and original response files; not a new execution',invocation='python -X utf8 -B docs/coder/d1e9/tools/run_selfcheck.py --attempt final-production-009',java='D:/Android/Android Studio/jbr/bin/java.exe',javac='D:/Android/Android Studio/jbr/bin/javac.exe',cases=[x['case'] for x in checks['results']],targetedRepair='python -X utf8 -B docs/coder/d1e9/tools/run_selfcheck.py --attempt replacement-cut-011 --cases D05',inputSnapshots=['selfcheck-attempts/final-production-009/inputs.json','selfcheck-attempts/replacement-cut-011/inputs.json'])
put(B/'evidence/selfcheck-execution-command-index.json',json.dumps(manifest,ensure_ascii=False,indent=2))
put(B/'E9_PROGRESS_FINAL.md',f'''# E9 work completed for static handoff
2026-10-18. Supersedes early E9_PROGRESS.md planning details. Strict canonical JSON and all current implementation/tool sources present. Final local mapping32 groups,36 mapped JVM invocations+1 targeted dispatch fix,{checks['assertions']} final mapped assertions; six actual Android host public methods rejected before SDK platform. Main offline dualAPK build1 failed for unavailable public SDK constant; repair1 passed, both rawlogs/input snapshots preserved. Seven native/35 dependencies identical; no native rebuild, ADB, real media, actual migration/catalog/H_actor/approval/activation. Four delivery docs, source diff/provenance, SBOM, final APK audit, freeze tool ready. Static reviewer decides next step; D1 not passed/M0 not started/E6B-OBS-F01 OPEN. No subagents. Final seal and read-only receipt are generated after these docs.
''')
print('four delivery documents and finite-case mapping written')
