"""Four E11 delivery documents and finite source/type/lifetime proof. No device or approval issuance."""
import base64,difflib,hashlib,json,pathlib,zipfile
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e10a'
if (B/'evidence/e11-freeze.json').exists():raise RuntimeError('FROZEN_READ_ONLY')
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def new(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s.strip()+'\n')
def js(p,d):new(p,json.dumps(d,ensure_ascii=False,indent=2))
def doc(n,s):new(R/f'docs/coder/D1_E11_{n}_V1.0.md',s)
c=read(B/'evidence/targeted-check-results.json');a=read(B/'evidence/apk-audit.json');h=read(B/'evidence/host-binary-provenance.json');binding=read(B/'release/candidate-binding.json');cat=read(B/'source-export/original-export/final.acceptance.json')['fields'];actor=json.loads(base64.urlsafe_b64decode(cat['actor1']+'='*(-len(cat['actor1'])%4)))['fields']
same=[]
for n in ['E9MigrationRun.java','E9Evidence.java','E9Registry.java','E9OwnedFiles.java','E9MigrationTransaction.java','E9LegacyProfile.java','E9LegacyState.java','E5AAdmission.java','E4Owned.java','E4Broker.java','E4OutputBudget.java','E4FencedTask.java','E5ALifecycle.java']:
 p=B/'src/com/videokit/spike/e4'/n;old=OLD/p.relative_to(B);assert p.read_bytes()==old.read_bytes();same.append(dict(current=row(p),baseline=row(old)))
for n in ['E9PcSupervisor.java','E9PcClient.java','E9HostRegistry.java','E9HostDeployment.java']:
 p=B/'tools'/n;old=OLD/p.relative_to(B);assert p.read_bytes()==old.read_bytes();same.append(dict(current=row(p),baseline=row(old)))
new(B/'reference/E11_DISPATCH_SOURCE.md','''# E11 派单来源记录

VideoKit项目助理thread01a107c3-2bf9-7fa0-94a0-234258ca6774转述用户最新“请继续推进开发”，正式派本批activation候选准备/实现/本机自检/一次必要离线构建。摘录：

> 当前仅开发不设备激活或播放
> 不得改原registry/events/head或重新SEAL
> 最新恢复开发授权不当成执行安装激活许可

本记录不是新用户签名、安装/播放派单或release批准；旧N2写授权仅为历史终局DAG来源，不升格为activation执行许可。
''')
new(B/'evidence/source-export-policy.diff',''.join(difflib.unified_diff((B/'source-export/original-export/E9BuildPolicy.java').read_text().splitlines(True),(B/'src/com/videokit/spike/e4/E9BuildPolicy.java').read_text().splitlines(True),fromfile='original_frozen_export_LF_normalized',tofile='E11_reviewed_head_source_LF_normalized')))
with zipfile.ZipFile(R/a['apks'][0]['path']) as z:dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
policy=(B/'src/com/videokit/spike/e4/E9BuildPolicy.java').read_text();packed=policy.split('CATALOG_BASE64="',1)[1].split('"',1)[0];raw=base64.urlsafe_b64decode(packed+'='*(-len(packed)%4));assert len(raw)==5853 and hashlib.sha256(raw).hexdigest()=='27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7'
assert raw==(B/'source-export/original-export/final.acceptance.json').read_bytes() and packed.encode() in dex
assert all(x['sha256'] not in policy for x in a['apks'])
js(B/'evidence/final-static-review.json',dict(schema=1,status='PASS',reviewer='coder; independent E11 review pending',sourceCatalogExact=True,apkCatalogBase64Exact=True,catalogBytes=len(raw),catalogSha256=hashlib.sha256(raw).hexdigest(),head=cat['head'],typedCatalog='E9Catalog.Trusted from source digest/head/environment; E9Record or receipt bool is not live proof',legacyEntriesDisabled=True,selectionDoesNotGrant=True,currentKnownFailureReturnedCanRetireWithoutGrant=True,currentUnknownRetainsOriginal=True,runnerFinishHook='Actual new Gradle compile/static source audit and its used lifetime method checked; Android finish execution NOT_RUN',inherited=same,tests=row(B/'evidence/targeted-check-results.json'),publicEntries=row(B/'evidence/public-android-entry-check.json'),releaseBinding=row(B/'evidence/release-binding-validation.json'),noApkSelfHash=True,deviceCalls=0,deploymentAuthorized=False))
js(B/'release/device-plan.template.json',dict(schema=1,state='NOT_AUTHORIZED_NOT_EXECUTABLE',deploymentScope=None,currentPreflight=None,sourceInstalledVersion=14,targetVersion=15,targetApks=binding['actualApks'],sourcePair=binding['sourceInstalledPair'],role='ACTIVATION',gateAbi=1,head=cat['head'],catalog=hashlib.sha256(raw).hexdigest(),originalRegistryMustRemainUnchanged=True,approvedDetachedRelease=None,caseBatch='D1-E4A-E11-ACTIVATION-20261018',normalMp4Receipt=None,normalAviReceipt=None,order=['fresh exact v14/UID/signer/data-inode/idle preflight','new explicitly approved pinned detached release; one supervised app/test install-r14->15','post-install exact pair/role/ABI/data preservation/idle proof','each new test host does actual current observation before product','normalMp4SixRealFrames; independently accepted receipt1','normalAviSixRealFrames gated by receipt1; independently accepted receipt2','capabilityDenialDoesNotOpenSource gated by both same-scope normal receipts','cancelRejectsWrongEpochOversizeAndLateFrame only after independent acceptance of capability plus both normals and actual idle/original return; no quarantine/death cases'],noActualCommandsExecuted=True))
art='\n'.join(f"|{x['role']}|{x['bytes']}|`{x['sha256']}`|" for x in a['apks']);cases='\n'.join(f"|{x['case']}|{x['assertions']}|" for x in c['results'])
doc('DELIVERY',f'''# D1 E11 activation候选交付 V1.0

版本15/D1-E11-ACTIVATION，现有ABI准确role=ACTIVATION（派单ACTIVATE的实现值）。本批完成真实终局只读导出、候选实现/本机检查/一次必要离线双APK构建，状态 BUILT_NOT_DEPLOYED_PENDING_INDEPENDENT_REVIEW。不是安装激活/播放许可；0ADB/设备/真实媒体用例/新迁移/actor2/强停。未签发实际release或当前host grant，两个真实normal receipt未生成。原D1未过/M0未启/长期准入OPEN。

## 真实来源及导出

已接受终局报告原SHA a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff；688实际输入和217执行manifest行本地精确核验。冻结E10A原生产JAR的--approved-export只调用原registry读路径，输出新source-export/original-export；未调用recordActivationRelease/SEAL/deploy。原registry13文件前后清单/字节SHA一致。其副本仅存新accepted-registry-snapshot，原事件/head不改。原入口read使用READ_WRITE FileChannel但没有写/force/append调用，结论是内容/清单不变，不声称未更新文件系统访问时间。

实际catalog5853B/≤16384B，SHA27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7；head6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5。原kind catalog/version1，registry{cat['registry']}，migration{cat['migration']}，environment DEVICE_HA1Q6WXR，actorCount1/disposition1 RETURN_VERIFIED_IN_TIME、termination1 ABSENT/actor2全部ABSENT。source-provenance列全部原字段/13文件映射及审查来源。旧补审manifest声明excludes:self但含0B self占位，本批以已接受报告的真实manifest SHA绑定并仅核其余实际行，不把占位当零字节文件验证，不修改旧manifest。

原trust.authorization {cat['authorization']}、review {cat['review']}仅为原N2迁移DAG输入；补审报告a597单独绑定，本批未来安装审批又是独立阶段，不能用原写scope升权。原actor PID{actor['pid']}/UID{actor['uid']}/boot{actor['boot']}/start{actor['start']}和prepare14 pair是历史事实，非当前现场。完整catalog原样内嵌；新增source HEAD常量与digest/environment共同核，导出器同步输出该字段并通过往返检查，不重造H_actor。

## 实现与安全边界

E9Phase从source-pinned digest/head/environment产生E9Catalog.Trusted；历史catalog只提供终局authority，不授实时proof。E9CurrentObservation仍核当前原guard/fence/13原metadata/完整合法ledger/无pending/精确三控制文件及自己的raw/dup/stream/目录/最后guard真实返回。重复或失败先撤销grant；已知失败且所有holder真返时移出ACTIVE可安全结束，但不授grant；UNKNOWN/在途仍保留ACTIVE。epoch并发检查保持。

新E11测试runner只接受单个受审MP4、AVI、能力拒绝或条件cancel；旧迁移/全类/死亡/隔离故障选项拒绝。每项仍通过原E4DeviceTests @Before当前观察。AVI须本scope MP4回执，能力/cancel须两份不同当前normal报告/输出task，绑定scope、candidate pair、version15/ACTIVATION/catalog/batch及READY/六帧EOF1000us/原owners返回。它只是选择/次序校验，不能认证外部报告来源或替代当前proof；外部受信tester/负责人必须实际核其原证据。无normal receipt可由开发或旧历史回执代填。

runner结束先撤销grant，原观察/会话/encoder slot/legacy原操作未返则不调用platform finish；actual Android finish未实测。旧PREPARE E9AndroidIdentity/事务入口仍因ACTIVATION在首个身份/写IO前拒绝，新host main也在配置读取/ADB之前拒PREPARE会话。

新host批准部署使用独立pinned release的deployActivationDetached，同一原部署gate核字节/source role/ABI/签名/UID/current pair/idle/严格升版/两条install-r一次，无需往原final registry加activation-release。未知或部分安装保守消费，不重试。SHA只绑定真正被批准的文件；没有新密钥/远端根/自选approved bool或网络撤销服务。role REVOKED/未知schema/错pin拒；正式执行者必须使用当时有效的真实批准，静态hash不能认证人类身份或自行证明未撤销。

## 检查与构建

12组定向最终映射，{c['finalMappedAssertions']}断言；13次本机验证调用（初10组、增migration router、仅扩展部署组、增export roundtrip），没有机械重跑旧套件或native。使用实际生产模块及真实已接受catalog，UID/inode/目录fsync/设备安装为Windows平台替身；UNKNOWN原Java holder仍未返，测试native facsimile收尾不算close ACK或live grant。SDK桩检查实际新Gradle app公开入口、旧prepare pair拒绝及runtime失败撤销旧本机fixture grant，均无Android运行。runner结束钩子只做实际编译/静态及其所用lifetime方法验证，不冒称真机结束已证。

|组|断言|
|---|---:|
{cases}

一次必要main-001离线构建成功，166输入SHA `{sha(B/'evidence/final-build-inputs.json')}`；无repair/下载/native重编。后补exporter HEAD兼容仅PC工具编译/JAR重封，没有第二次APK构建。原签名5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；7native/35Maven坐标/锁不变，FFmpeg8.0.3/Media3 1.9.3及许可P0不变。

|制品|字节|SHA256|
|---|---:|---|
{art}
|host JAR|{h['artifact']['bytes']}|`{h['artifact']['sha256']}`|

host JAR {len(h['productionClasses'])}生产classes、无测试类，取最终activation-004已测编译；此前生产class差异仅明确host router与exporter，原快照/JAR及源码留存。APK DEX已核完整内嵌Base64和实际catalog字节，未嵌自身APK hash；构建后actual SHA进入独立candidate-binding和release模板，sourceReview/部署派单/approvedRelease/live observation/两normal receipt均null或占位，不能直接交生产CLI。工具早期仅因独立输入表字段名准备失败，未启动原Java；更正后原冻结export分支执行一次。原日志/输入/差异保留。

完整源ZIP及ZIP外seal/只读verify由包外记录给出；E10A及所有原证据冻结不改。原107218/三R三S/0B/S0/53651/53567及oldCloseACKfalse保持；独立Kit/Flutter/原框架严格六帧EOF1000us/全部许可P0不变。本交付不关闭D1或启动M0。
''')
doc('ARCHITECTURE_AND_THREAT_BOUNDARY','''# D1 E11 架构与威胁边界 V1.0

继续采用已审签名代码/受信本机执行者的合作故障边界。SHA绑定真实输入，不认证批准人的身份；同UID主动篡改、root、自洽回滚及远端撤销服务不在本批新增承诺内。不新增密钥、远端根、普通文件自证authority或取消框架。

authority单向DAG：真实迁移原身份/BOUND→原三记录→COMMIT原返回→normalfinish→四事件最终head→catalog/checkpoint/seal→独立终局接受→source-pinned ACTIVATION policy→签名APK真实SHA（构建后）→未来独立批准release。APK不含其自身hash，release不反写原event/catalog。旧authorization/review仍是原历史来源，不代表E11安装批准。

实时准入是另一条链：每新host的已审catalog类型→当前平台idle→原owner/lease准确身份与fence→13旧metadata/完整合法ledger及settled后缀/无pending→精确intent/acceptance/commit→本host全部原holder真实返回→epoch一致的进程内grant。普通E9Record、设备自选digest、磁盘commit或外部normal receipt布尔字段不能替代该链。E9Catalog.Trusted只能由reviewed digest/head/environment路径得到；旧observer/recovery公共路由仍禁用。

成功观察完成并移出ACTIVE后才可能发grant。已知失败即使holder已真返也不发grant；此时可以解除不再需要的keeper。UNKNOWN/ALLOCATING/CLOSING/在途不能移出ACTIVE或第二close，保留原对象。新runner在platform finish前调用实际lifetime门，若当前观察/原Session/slot/旧操作未返则拒结束；不为JUnit失败强行结束原资源。开始新观察和runner结束都撤销旧grant；并发epoch在等待class锁之前失效，旧观察不能晚发grant。有限本机交错验证不代表Android内核UNKNOWN测试。

测试选择和normal receipts仅约束受信批次流程：精确class#method/batch/稳定budget/独立终局报告、同scope和actual candidate pair；AVI需MP4，能力及cancel需两份不同报告/task。记录还须声称READY、6/6/6、fullEOF、PTS1000us、ownersReturned，并由外部独立核原证据。APK只核结构/绑定，无法认证这些声明；每个测试@Before仍做真实当前观察，选择通过不发grant。旧test调用写迁移时实际app role ACT拒首写；新test manifest只注册E11 runner，不声明旧managed迁移入口。

部署沿用原精确字节/source role/ABI/签名/UID/idle/升版门、原Process/pipe/55秒一般任务和5秒控制解码、同JVM非daemon custodian/128总accept/有限查询。新增detached入口读原final registry与当前独立批准release，不写原registry。partial/UNKNOWN install不重试，不能以install结束未知actor。批准尚未存在时模板不是合法release；REVOKED role/未知schema/未匹配pin都拒绝。

框架帧/资源/ABI和全部native严格六帧/完整EOF/1000us不变。没有对原V1缺birth补证、没有改oldCloseACKfalse或旧三R三S；对当前13原metadata和合法账本后缀验证不能被历史age替代。独立Kit/Flutter/许可与D1总体验收均未由本批源码或模拟测试完成。
''')
doc('REMAINING_GATE_REVIEW','''# D1 E11 剩余门与证据范围 V1.0

E10A真实actor1迁移和完整终局仅在已接受报告a597范围PASS；E11只读复用，不重迁移或重SEAL。E11候选实现/本机有限检查/一次离线构建完成，待独立tester复审；不自认设备ACTIVATION或normal PASS。D1 NOT_PASSED、M0 NOT_STARTED、E6B-OBS-F01长期准入OPEN。

NOT_RUN：v14→v15实际安装、实际当前观察、Android runner结束/UNKNOWN钩子、普通app发送者权限负例、MP4/AVI/能力/cancel、媒体/native故障/长期回归、actor2/3。SDK桩公开入口与Windows原metadata文件仅证明明确的本机代码边界，不能把UID/inode/目录fsync shim当本机实际Android平台。两个normal receipt目前不存在，不能用历史prepare报告、模拟receipt或同一报告改名填入。

下一步先独立审候选及附录，负责人再判断新的具体设备派单。用户当前恢复开发仍不解除原“不激活/不继续播放”的设备限制。候选release sourceReview/dispatch未填，不得生成随机token、伪造批准文本、重复利用原N2写scope或E3许可。真实被接受的E11审查和另行人类安装/测试范围才能形成当时有效release及scope。

原budget730a73e1-50e1-4198-a515-047104f00e31、fence662e9ecd-bede-42e6-bb58-ce81d668ff44、旧task86cafdb3-0fc4-447d-920b-b19c884bf494/attempt8c6673b7-38a5-4a24-838d-ca8466d8b75f、0B/S0与53651+53567=107218、三R三S/0reserved、原档案和全部产物均未改，oldCloseACKfalse不回填。未来若另行准许正常输出，新合法R/S只能追加保留原前缀和旧消费，不能承诺总消费仍固定107218或清账让测试通过。

Framework发布、独立Kit/Flutter、严格六帧fullEOF1000us、FFmpeg许可及其他全部P0维持既有状态。SBOM7库/35坐标无差异不是许可清除。禁止以正常流程模拟PASS、静态角色或historical catalog取消这些门。
''')
doc('DEVICE_EXECUTION_APPENDIX','''# D1 E11 未来设备附录 V1.0

当前 NOT_AUTHORIZED / NOT_RUN；本附录是下一个受审批的拟定顺序，不含执行许可或真实normal receipt。最新恢复开发不等于激活或播放授权。所有当前字段须当时真实采集。

1. 候选和完整终局独立审查接受后，先取得新的人类明确安装/当前观察/逐项测试范围；负责人记录实际派单scope原字节SHA，不发明随机token。复核E11外seal、签名、actual双APK/JAR/hash、5853B实际catalog/head及原13文件。scope历史N2授权只作来源，不能拿来授安装或媒体。preflight serial HA1Q6WXR/user0、原UID10221/10222、当前pm path+两APK完整SHA、版本14/PREPARE/ABI1/原签名、包状态/数据目录inode、无相关活进程/未知资源。历史boot/PID/start/14包状态不是当前观测。原guard/fence/账本档案/0B和已settled产物只按受审元数据核，不能预读非零媒体。
2. sourceInstalledPair严格为本次E10A v14已核pair，target本候选v15/ACTIVATION新pair。若现场不同（包括已15）停止另审，不自动再安装。将release模板在真正接受E11 source审查和新派单后填唯一实际sourceReview，生成canonical activationRelease及其实际SHA；新release位于新受控E11批目录，原activationTrust只用于读取已接受历史registry，原授权不能替代新批准。用新host --approved-deploy、原config pin/独立release pin/实际app/test逐项argv，原生产gate before/after精确pair、idle、UID/role/ABI，app/test install-r各一次。禁-d/卸载clear/强停；不向原registry追加release/event/head，不重SEAL。部分/未知安装消费原任务，不重试；原PC/pipe/custodian继续保留，不能用安装清除未知参与者。部署后真实核两包、原数据目录与旧N2数据保留，再批准下一步。
3. 每个测试都是新host，必须原E4DeviceTests @Before调用E9Runtime.observe：当前idle/精确guard/fence/13原metadata、完整ledger固定1011B前缀+合法settled后缀/无pending、实际M4f21f71a-bf66-4a44-a287-320f0ae25fde intent/725B acceptance/244B commit和本host原holders真实返。只有FRESH_E9_OBSERVATION_ADMITTED才继续；BLOCKED/UNKNOWN不拿历史catalog或旧grant绕过，不第二close。已知失败并全真返可正常结束失败，UNKNOWN/在途runner必须拒platform finish并保留原对象，不kill/cancel进程。
4. 新test runner com.videokit.spike.e4.E11ActivationInstrumentation，固定batch D1-E4A-E11-ACTIVATION-20261018，精确class com.videokit.spike.e4.E4DeviceTests#<方法>且e4Case同名；e4BudgetIdentity原730a...、e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT、e5aSettlementReceiptSha256为接受终局报告a597...。e11ScopeSha256绑定这次真正批准的设备批，e11ReleaseAppSha256/e11ReleaseTestSha256为部署后实际精确pair（由外部独立核，APK不嵌自身hash）。runner仅接收字符串/白名单args，不接受legacy e9Case/e9Request或整类/死亡/隔离故障选择。未来可用受原PC监督的am instrument -w -r单方法收集原status/exit，不能用外部超时杀client/原Android任务；每原一般客户端55秒绝对响应、输出≤1MiB，超期PENDING保留原Process/pipe并另审。实际case自身原框架clock不延长，未知不得靠重复启动求PASS。
5. 第一项normalMp4SixRealFrames，不附任何已有normal receipt。采实际当前观察、原源/编码/回调/输出metadata、READY/6 received/6 inputs/6 outputs、完整EOF/PTS1000us、原resourcesReleased/owner-return/无workerDied/回调拒绝0/原slot0、输出合法R/S/真实客户端与系统结束证据；独立审定原报告后才形成normal receipt1。没有就停，不自动AVI。
6. 第二项normalAviSixRealFrames，除同scope/pair参数还须e11Mp4Receipt。它是canonical e11NormalReceipt原字节的Base64URL无padding；字段严格为kind/batch/scope/app/test/version/role/catalog/case/report/task/status/received/inputs/outputs/fullEof/ptsUs/ownersReturned。version15/ACTIVATION、catalog27fe...、case=MP4方法，report是真实独立接受的MP4报告SHA、task为该实际outputTaskId UUID，其余必须与原证据相符。APK只核声明和绑定，不认证来源。AVI也要本host新观察和同样完整实际验证，审定后形成不同的receipt2，不能复用同一report/task或历史prepare回执。
7. capabilityDenialDoesNotOpenSource仅在两项normal都实际通过并独立接受后派发；e11Mp4Receipt和e11AviReceipt须同scope/实际pair/version/catalog/batch且分别匹配case、不同report SHA与output task。e4NormalReceiptSha256是canonical MP4 receipt原字节接AVI receipt原字节的SHA（各自尾LF保留），是双回执索引，不能冒充第三份normal报告。实际核生产source broker opens/bytes/reads0、无READY、原资源释放；fixture本身的受审asset准备和生产broker source计数分清。能力拒绝本身不是失败迁移或准入恢复。
8. cancelRejectsWrongEpochOversizeAndLateFrame只有两份本批normal receipt已接受、能力项已审定、现场无原在途且负责人明确条件允许才派；仍须自己的当前观察。核原wrong epoch/oversize/late frame拒绝、原cancel收尾与实际owners返回，不延长deadline，不以future.cancel/强停当原返回。不选择closeUnproven/self-kill/segv或扩大故障范围。本批不执行任何这些项。

每步独立原命令/输入pin/开始结束/seq/原stdout-stderr/pipe返回/来源表，未知或预算超界停止，不自动重放或换host/port补额。沿用原PC96进程、总128accept、受审查询预算≤16，控制响应5秒、一般任务55秒、日志/单命令输出1MiB、原holder48及框架严格资源门。normal可能合法新增R/S与输出，原三R三S/107218必须保留但新总消费可增加；每次必须满足4MiB总量、2MiB单任务全额预留、128任务、无pending，若新输出后余量不足下一次2MiB预留便阻断，不清账/换budget或假定两项一定能运行。未拿到两份真实normal receipt，不进入后续条件测试。

完成后集中报告，停在被批准范围。任何产品长期准入、Flutter/Kit/Framework/许可P0或D1总体验收不由本附录自动通过。当前0设备安装/激活/播放/媒体/actor2，所有scope、当前proof和normal receipts仍未创建。
''')
new(B/'E11_PROGRESS_FINAL.md',f'''# E11 完成范围

真实已接受catalog只读导出，原registry13文件不变；v15 ACTIVATION候选与12组{c['finalMappedAssertions']}断言/13本机调用、实际新Gradle SDK公开门验证完成；唯一一次必要双APK构建及签名/7库35坐标审计通过。后续host exporter字段同步仅本机工具编译/JAR更新。待独立复审，不设备安装激活播放，不签发release或真实normal receipt。冻结/交接以外seal和包外verify/完整报告为准。D1未过M0未启长期准入/P0保持。
''')
print('PASS E11 four documents, exact catalog in APK, draft release and future-only device plan')
