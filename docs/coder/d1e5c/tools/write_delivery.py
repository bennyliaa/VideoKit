"""Write the reviewable E5C delivery/plan after final APK audit; no device execution."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
audit=load(B/'evidence/apk-audit.json');app,test=audit['apks'];inputs=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest();prov=load(B/'evidence/source-provenance.json')
fixture_args={'class':'com.videokit.spike.e4.E5CGuardFixtureTests#isolatedOriginalInodeSymlinks','e5cCase':'isolatedOriginalInodeSymlinks','e5cBatch':'D1-E5C-GUARD-LINK-TABLET-20261017','e5cRun':'FORMAL_DEBUG_FIXTURE_ONLY'}
query_args={'class':'com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort','e5N2Task':'86cafdb3-0fc4-447d-920b-b19c884bf494','e5N2Budget':'730a73e1-50e1-4198-a515-047104f00e31','e5RecoveryBatch':'D1-E5B-N2-RECOVERY-20261017','e5N2Action':'QUERY'}
def instrument(args):
 v=['shell','am','instrument','-w','-r']
 for k,value in args.items():v+=['-e',k,value]
 return v+['com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner']
plan={'schema':1,'candidate':'D1-20261017-E5C','state':'DRAFT_FOR_INDEPENDENT_REVIEW_NOT_EXECUTION_PERMISSION','deviceExecution':'NOT_RUN','deviceBinding':'Only original approved N2 tablet, app UID 10221; tester dispatch must bind its existing serial. No auto device selection or fallback.','artifactIdentity':audit['apks'],'signerCertificateSha256':app['signerCertificateSha256'],'steps':[{'order':1,'name':'same_signer_preserve_data_update_app','argvAfterBoundAdbSerial':['install','-r',app['path']],'gate':'Verify exact hash/signer/versionCode5 and existing same-signer package. No uninstall/clear/downgrade/new UID.'},{'order':2,'name':'same_signer_update_instrumentation','argvAfterBoundAdbSerial':['install','-r',test['path']],'gate':'Only if step1 succeeded; no product methods automatically.'},{'order':3,'name':'isolated_fixture_production_observation_lock_boundary','argvAfterBoundAdbSerial':instrument(fixture_args),'fixedRoot':'files/e5c_guard_fixture_20261017_once','methodDeadlineSeconds':60,'gate':'All original operations returned and exact PASS required; prior root, FAIL, BLOCKED, PENDING, UNKNOWN, runner exit without result, deadline or transport failure stops batch. Keep root and original resources. QUERY then NOT_RUN.'},{'order':4,'name':'fixed_original_readonly_QUERY','argvAfterBoundAdbSerial':instrument(query_args),'gate':'Only after fixture PASS and all actual closes proven in same explicitly dispatched batch. Separate new instrumentation host. Exact QUERY_ELIGIBLE plus originalCloseACK=false and retainedOperations=0; do not infer ABORT or observation approval.'}],'resultIndependence':'Report deployment, fixture, original QUERY separately; fixture PASS does not prove original writer death, full observe, N2 recovery, or product encoding. QUERY failure does not erase fixture evidence. Failure never invokes ABORT/observe/normal.','limits':{'fixtureNodesIncludingDirectoriesAndSymlinks':64,'fixtureRegularAndLinkDataBytes':262144,'individualRegularFileBytes':65536,'fixtureLogBytes':4194304,'actualImplementationEvents':64,'actualImplementationEventChars':4096,'fixtureMethodSeconds':60,'registeredFixtureIOHolders':128,'cases':3,'fixtureAttempts':1},'stopRules':['No retry/reset/delete/alternate root or batch after any attempt; existing root blocks before scan.','No killing owner, forced cancellation, replacement closer, or force-stop to obtain pass. Timeout reports PENDING/UNKNOWN; retain original worker/root.','No Windows privilege/Developer Mode attempts, environment install, root, external storage, native fault, media, budget cleanup, metadata repair or arbitrary paths.','No QUERY on fixture failure/PENDING/UNKNOWN. QUERY is NOT_RUN and needs separate review if fixture does not fully return.','No ABORT_ORIGINAL_N2/OBSERVE_SETTLED_N2/product methods in this batch. Separately reviewed later dispatch required.'],'scope':'Production observation private lock -> same E5N2RecoveryAndroid -> E5BGuard -> actual lstat/open/fstat/dup/flock/close. Metadata and writer death are NOT EXECUTED synthetic premises; full observe NOT_RUN.','runner':'com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner','fixtureArguments':fixture_args,'queryArguments':query_args,'recoveryBatchPreserved':True,'deviceCalls':0,'realMediaReads':0}
put(B/'tools/device_plan.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
artifact_table='\n'.join('| '+a['role']+' | '+str(a['bytes'])+' | `'+a['sha256']+'` |' for a in audit['apks'])
base='D:/CodexProjects/VideoKit/docs/coder/d1e5c/'
delivery=f'''# D1 E5C 完整交付 V1.0

2026-10-17。候选 D1-20261017-E5C，版本5 / D1-E5C。已完成Debug隔离夹具入口、有限本机逻辑检查、集中离线构建及签名/清单/原生库核验。真实Android补验、原QUERY、完整观察和恢复均NOT_RUN。G01待实机证据及独立复审，D1 NOT_PASSED、M0 NOT_STARTED、全P0和历史signal FAIL不变。

## 最终双APK

| 角色 | 字节 | SHA-256 |
|---|---:|---|
{artifact_table}

最终文件在 `{base}artifacts/D1-20261017-E5C/final/`。双APK签名证书均 `{app['signerCertificateSha256']}`，与原候选一致。App为com.videokit.app，测试包com.videokit.app.test，单APK产品布局及原两个私有服务保持，7个arm64原生库字节一致。ACCESS_NETWORK_STATE是既有依赖合并权限；无新增权限/INTERNET。

## 实现与验证

新增 `app/src/androidTest/java/com/videokit/spike/e4/E5CGuardFixtureTests.java` 与 E5CFixtureBounds.java。精确方法 isolatedOriginalInodeSymlinks，只使用files/e5c_guard_fixture_20261017_once；健康两锁及owner/lease真文件链接三例。生产类未改，按相对路径直接引用冻结E5B的src/android/C14及原测试源码；main/debug清单复制字节一致。私有方法声明类、private修饰及返回/参数签名精确固定；完整源码hash由最终输入、source-provenance和freeze约束，反射失败即停。

本机10项纯JVM边界/时限用例与9项源码约束PASS，详见evidence/local-check-results.json。它们不能替代Android symlink/flock/FD验证；未重跑旧270/82项历史套件。最终输入SHA `{inputs}`，最后成功构建repair-001绑定此输入。

首轮main-001编译成功，但APK清单审核发现overlay漏带E5B的Debug服务清单，故审核失败。已补入原文件，不修改生产逻辑；一次必要repair-001离线构建通过，最终审核PASS。首轮两APK保存在artifacts/D1-20261017-E5C/pre-debug-manifest-repair，原签名/清单/输入和失败说明在evidence/pre-debug-manifest-repair；两轮构建日志及build-results-before-repair-001.json保留。没有把首轮APK交作最终候选。

来源核验对原E5B seal及1561项不可变文件只读校验PASS。source-provenance同时核直接引用的生产、Android、原测试和C14来源，原main/debug复制与原字节一致。35个Maven坐标、Media3 1.9.3、FFmpeg8.0.3、7个原生库保持，无下载。完整C14对应源容器保留，未复制E5B旧自检树；不是许可证/漏洞放行结论。

## 交付与下一步

另附架构边界、剩余门、设备附录三文档，准确计划tools/device_plan.json。source-manifest逐件绑定完整小overlay、所需E5B源/native/NOTICE/完整C14对应源容器及证据；ZIP按原相对目录装入，解压后配置自身local.properties，可离线重建；不含私钥、缓存或实际媒体。外seal evidence/e5c-freeze.json另绑定ZIP、最终及首轮保留APK，seal自身hash在交接消息/包外只读核验回执中给出。

仅交负责人整包复审；审过再正式派同签名保数据更新→隔离补验→固定原N2只读QUERY。所有执行动作未启动，新计划不是执行许可。原N2预算、R2MiB、pending及旧失败现场保持；任何失败不自动ABORT/观察/产品方法。
'''
architecture=f'''# D1 E5C 架构及威胁边界 V1.0

2026-10-17。仅验证生产观察的锁获取边界，不验证完整observe、真实writer死亡、N2恢复或产品编码。

## 同一生产路径

负责人批准Debug-only精确反射 `E5AFinalObservation.private lock(Path,E5BGuard.Role,String,E5BFileId)`。声明类/参数/返回类型/private必须匹配，不能替代方法或吞异常；source-provenance固定其原文件SHA `{prov['observationBoundary']['sha256']}`。进入同E5N2RecoveryAndroid.existingGuard→同E5BGuard→同E5BAndroidGuardIO（Os.lstat/O_NOFOLLOW open/fstat、ParcelFD.dup、真实flock、unlock及两个原FD close）。E5B生产Guard、恢复、观察、Admission、Lifecycle没有新接口或字节修改。

夹具平台只放行本case两条精确路径/role/epoch/expected实例，实际existingGuard完全委托原Android适配器。死亡、recoveryOwner、sync、metadata force/close接口直接拒绝，不能假冒成功。适配器构造不做磁盘恢复动作。完整observe从未调用，actualReturnProven必须仍false，原静态live grant先null且后相同；原恢复及观察retained计数进入前必须0，产品session/slot必须0。

## 隔离及负例

仅既有com.videokit.app主进程、UID10221、Debug可运行；固定新root创建必须CREATE_DIRECTORY成功，0700。既有root阻断，不扫描它、不重置、不换名。三子目录healthy/owner_symlink/lease_symlink；每例自有随机任务、epoch、账本ID，own-identity.txt/own-ledger.txt/own-payload.bin仅合成自有字节（R/S计数0），不含真实原N2 task/budget/ledger。死亡及metadata前提明确ASSUMED_SYNTHETIC_NOT_EXECUTED。

健康通过两次原锁获取并实际关闭。负例先无覆盖move原guard到同目录相邻.original-target，再Os.symlink用相对文件名指回原inode；lstat S_IFLNK、readlink精确目标、目标regular且原dev/inode/UID/length、跟随stat同dev/inode、目标原SHA证实真链接。owner负例仅登记第1holder后拒绝，lease负例先获取健康owner再第2holder拒绝，随后关闭原owner。错误必须是原生产E5B_EXISTING_GUARD_ROLE_LENGTH_UID，不能把任意异常作预期PASS。

附加原AndroidIO O_NOFOLLOW探针要求真实ELOOP且预登记holder的close返回；它支持系统语义，不替代观察边界拒绝。生产负例lstat先拒绝，FD未分配会明确NONE_PREOPEN_REJECTION，不能虚称其关闭了某个打开的FD。健康已分配guard反射读原descriptor，实际raw/dup closeAttempted及原FileDescriptor.valid=false后才标CLOSED；UNKNOWN单列且不PASS。

每例链接设置后、边界前后的有限NOFOLLOW清单对比路径/类型/dev/inode/UID/mode/regular length/SHA/link target，忽略访问时间。无新节点、metadata/ledger/payload字节变化、R/S计数变化、live grant。只扫自有root子树，不扫app、缓存、媒体、原预算/输出。最终自有root总限额另查。

## 所有权及时限

注册Run后才调用worker，原observer在任何反射lock前强引用登记；原类holder在factory前登记。自有write/read/原探针也先注册E4Owned，最多128个IO holder；实际物理节点最多64（含目录/链接）、regular及link target数据合计256KiB、单regular64KiB。日志总限4MiB，实际更紧64事件/每事件4096字符。限定3例1次，不能重用root。所有路径受root限制，链接不遍历。

单方法从开始算60s，host只等待剩余时间，worker各阶段/读写检查原deadline。超时不cancel、不shutdownNow、不替代close或删root；报告PENDING/actualReturn UNKNOWN并保持原Run/worker/observer/holder强引用。晚返回不升级已超时结果，worker不再开始后续case；原close可能继续真实返回。该截止不是强杀不可返回系统调用的承诺，系统调用不返回时资源仍PENDING。close仅原worker在OPEN/READY时尝试，UNKNOWN/CLOSING不重试。失败保留整个root及Run（成功也保留root及已闭合Run，进程consume门不可重跑）。仪器系统结束不是协议close证据。

## 明确未覆盖

本机仅逻辑边界与编译，Android实际链接/FD/flock均NOT_RUN。原N2死亡证据、metadata验证、force/sync、全observe/live admission、ABORT/settlement及正常媒体编码均未执行。G01是否补齐取决于将来的真实证据和独立审查，不继承WindowsJunction为真文件链接证据；原Windows1314 NOT_RUN保留。
'''
gate='''# D1 E5C 剩余门复审 V1.0

2026-10-17。E5C是已构建的补验入口交付，G01尚未取得Android真文件symlink证据。

| 项 | 当前结论 | 后续门 |
|---|---|---|
| E5B生产修复 | 原静态支持保持，生产字节相同 | 不扩成设备恢复通过 |
| E5C本机逻辑/编译 | 10纯JVM+9源码约束、最终双APK核验PASS | 不证明实际Android IO |
| G01真文件链接 | NOT_RUN，待独立入口复审 | 实际S_IFLNK/readlink/同原inode/字节、健康实际锁/FD关闭、两个负例拒绝且无修改/R/S/grant |
| 原N2只读QUERY | NOT_RUN，原batch及稳定UUID保持 | 正式整批派发、夹具实际PASS且全return后才运行；独立记录 |
| 原N2 ABORT/settlement | NOT_RUN | 单独审查QUERY与狭义恢复许可；不由新夹具或QUERY自动授权 |
| 新host最终观察/活准入 | NOT_RUN | 单独真实恢复、writer死亡及当前强制持久化/实际关闭证据 |
| 正常MP4/AVI、capability、条件cancel | NOT_RUN | 原完整真实链与收尾门，另派执行 |
| 旧signal、全P0、正式Flutter/独立Kit、框架许可 | 保持既有未通过/未完成 | 既定原验收及许可不变 |
| D1 / M0 | NOT_PASSED / NOT_STARTED | 本包不能宣称项目正式交付完成 |

本批编译首轮遗漏Debug清单已按实际APK审核失败修复，最终原两个私有服务与签名/7native验证PASS，首轮证据仍冻结保留。没有新增依赖/权限/真实媒体访问，没有系统设置、Windows特权重试、设备/ADB/QUERY。所有失败停止、保留原现场，不伪造close ACK，不清预算，不用新UUID替代原恢复。

完整source/native/C14对应源、35坐标SBOM和来源追踪已提供，但它们是构建与来源证据，不是漏洞/许可证/商用合规结论。旧E3许可已消费，不在E5C重发或复用；当前计划不是执行许可。
'''
appendix=f'''# D1 E5C 设备执行附录 V1.0

2026-10-17。供负责人复审后正式派发；本次coder设备调用0。唯一准确机器计划 `{base}tools/device_plan.json`，记录最终双APK完整SHA、证书和逐步argv；`argvAfterBoundAdbSerial`仅是待执行参数，需正式派发绑定原平板serial，不能自动选任意设备。禁止Gradle/媒体/设备并发。

## 单批顺序

1. 先独立核外freeze/ZIP/源/最终双APK/原证书和原app身份。用相同签名执行保数据更新app及test包（install -r），不用卸载、clear、降级或新UID。版本5、原UID10221不符即停。
2. 精确选一个方法 `com.videokit.spike.e4.E5CGuardFixtureTests#isolatedOriginalInodeSymlinks`，runner `com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner`。参数e5cCase=isolatedOriginalInodeSymlinks，e5cBatch=D1-E5C-GUARD-LINK-TABLET-20261017，e5cRun=FORMAL_DEBUG_FIXTURE_ONLY。固定root files/e5c_guard_fixture_20261017_once，不接受caller传路径；本方法不执行原QUERY/ABORT。
3. 必须看到健康两锁真实close、owner/lease两份真链接S_IFLNK/readlink/同原inode/长度/SHA、实际ELOOP、原生产role拒绝、无修改/R/S/grant、每个实际FD与原holder CLOSED，最后E5C_LOCK_BOUNDARY_PASS及仪器方法PASS。原生产负例在open前拒绝的FD标NONE_PREOPEN_REJECTION，不能当实际已分配FD close。所有证据需独立复核；方法PASS不等于正式G01审查通过。
4. 同一正式派发整批中，仅在第3步完全PASS且所有原调用返回时，另起instrumentation精确执行 `com.videokit.spike.e4.E5RecoveryDeviceTests#originalN2QueryOrAbort`，显式e5N2Action=QUERY、e5N2Task=86cafdb3-0fc4-447d-920b-b19c884bf494、e5N2Budget=730a73e1-50e1-4198-a515-047104f00e31、e5RecoveryBatch=D1-E5B-N2-RECOVERY-20261017。保持原恢复batch，无e5aSettlementReceiptSha256参数。只读旧狭义原路径；原QUERY入口源码字节保持。QUERY_ELIGIBLE/originalCloseACK=false/retainedOperations=0及系统证据独立归档，不把fixture合成死亡当原writer证据。

## 预算与停止

夹具最多64节点/256KiB数据/单文件64KiB，日志4MiB（实现64事件各4096字符更紧），原方法时钟60s，3例1次。已有root直接BLOCKED，不扫描既有root、不删、不重命名、不换root重跑。任何FAIL/BLOCKED/PENDING/UNKNOWN/超时/runner或传输不明确均停止，QUERY标NOT_RUN。原线程/实际调用未返回不以外部cancel/kill/force-stop/系统仪器结束冒充close；保留原现场，等待独立判断。日志限额达到也FAIL，不截断拼PASS。

部署、fixture和QUERY分别写结果，夹具PASS仅证明生产观察锁边界；QUERY失败不抹去夹具证据，亦不触发ABORT/observe/正常产品方法。恢复动作必须将本批完整证据交审后再单独派发。原媒体、预置fixture、原budget/R2MiB/pending、原N2身份/epoch/lease、原失败保持，不新建预算替代。

## 审阅入口及本机复核

先读另外三份D1_E5C文档，再核source-provenance/local-check-results/build-results/apk-audit/sbom-difference/external-readonly-verification。包外回执核外seal自身hash，`tools/e5c_package.py verify`只读复核所有immutable和ZIP成员/字节/最终输入；其检查不是设备授权。解压源码ZIP保留docs/coder/d1e5c及所需d1e5b相对布局，配置自己的SDK路径后用既有Gradle/JDK离线构建，不导入任何签名私钥/缓存；若环境无既有依赖，不自动下载。
'''
for suffix,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gate),('DEVICE_EXECUTION_APPENDIX',appendix)]:put(R/f'docs/coder/D1_E5C_{suffix}_V1.0.md',text)
print('Four E5C documents and precise review-only device plan written')
