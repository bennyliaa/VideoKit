"""Post-return packaging only. Never invokes candidate functions/processes."""
from pathlib import Path
import json,hashlib,zipfile
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
d=json.loads((H/'evidence/result.json').read_text());plan=json.loads((H/'reference/plan.json').read_text());B=Path(plan['candidate']);g={x['name']:x for x in d['results']}
assert d['ownAuxOriginalsReturned'] and d['auxCustody']==0 and not d['stopNew']
assert len(d['results'])==14 and sum(x['status']=='PASS' for x in d['results'])==13
assert all(x['matches'] for x in d['audit']) and all(x['constructorReturned'] for x in d['calls'])
orig=json.loads((B/'reference/freeze-manifest.json').read_text())
for r in orig['files']:assert sha(B/r['path'])==r['sha256']
sem=g['original98-independent175-new73-semantics']['detail'];app=g['exact-small-append-source-pin']['detail'];q=g['finite-three-call-driver-qualification']['detail'];root=g['new-tester-root-original-seven']['detail'];seven=g['original-seven-END-once']['detail'];prop=g['proposal-static-pins']['detail']
assert sem['total']==346 and sem['positive']==42 and app['exactReason']=='OWNER_SOURCE_PIN_ENTRY'
profile=json.loads((H/'reference/profile.json').read_text())
for rel,h in profile['helperCodePins'].items():assert sha(H/rel)==h
report=f'''# GLOBAL_IDLE_CONTRACT03_SELFCHECK02 完整开发验证报告 V1.0

2026-10-23；coder；一次集中回交负责人。**本批驱动资格通过；14组中13 PASS、1已知时限FAIL，不能写成整包全绿。** 346语义、原collector、完整七角色/END/once、新tester根、preStart13、PS守卫及精确小追加source门已实际验证；有限故障簇没有完整到达11项。没有重跑、扩额、修改冻结产品源或新增资源返回UNKNOWN。D1未通过/M0未启动，是否正式B或继续集中补验由负责人统一决定。

## 准确授权、源与隔离

执行范围为 D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_CODER_REQUIREMENTS_V1.0.md，当前设计/里程碑/D1_PHONE顶部安排均已读取。新辅助目录 `{H}`；batch `{plan['batch']}`。不续跑原 batch-c45d128d3721，不读取、枚举或二close其临时对象，不操作旧001a/session55065或其他旧链。

产品目录 `{B}` 的17源seal `{plan['sourceSealSha256']}`、gate9 `{plan['gateSourcesSha256']}`、plan `{plan['rolePlanSha256']}`保持不动。原manifest98项/1245040B在执行前、执行后及本次封存前逐行hash核验bad0；原BLOCKED/FAIL/UNKNOWN/once不改。独立tester阶段A另由负责人接收，本报告不混入其400/400作为开发自测，不签正式B或现场。

## 辅助驱动修正与成熟机制复用

复用已接受SELF包的13源manifest SHA `b3cdd53b3527e39aac726d1014473e69f2c1a552fa7243a6be434adc5901c2e1`，与已接受SELF报告 `2fd415f0bbee624abae236934514a4f9a3310e3d04ac7937d10b65cc9f3fb613`分清。reuse/保留原源逐字节preimage，native_identity.py及Journal未改；owned_capture.py派生原Capture的drain、wait、stream/H close及disposition。唯一返回流程仍针对同原Popen/H，不OpenProcess查PID、不夺取产品owner、不二close；未知状态不故意实际制造。差异与原/新SHA在reference/lineage.json、receiver-diff.patch和各helper.diff。

guard.py把准确程序、完整argv、cwd/env、shell/继承/流、固定脚本来源、OFFLINE context/permit及新输出范围的检查放到**原Popen构造前**。profile固定所有调用族、生成者source、程序和script pins；每次物化完整tuple/Windows commandLine在构造前核并留记录。candidate生产Popen包装只作此前置检查，原对象仍归原Gate/Owner/collector，不读取/关闭其流。

audit回调只作内存观察，明确applicationName可以None、commandLine是序列化字符串；不写文件、不主动抛参数拒绝。未知观察只停止后续新准入，当前有限原件等真实归还。18次父宿主观察全部匹配，18次被记录构造均返回；不宣称父Python audit能观察CLI/.NET内部每个事件，后者由固定源码/调用图与原回执核。继承env=None保持不清洗，只存其摘要；三次资格用预存四项非秘密env。所有新profiles不自动继承旧许可。

## 先行有限驱动资格

纯前置程序/额外参数/cwd/env反例与Windows None/string audit纯映射先通过，错误程序没有真的启动。三次原调用自然完成：

| 调用 | exit | 语义 | 实际时长 | 原归还 |
|---|---:|---|---:|---|
| 自有Python正常 | {q['actualThree'][0]['exitCode']} | PASS | {q['actualThree'][0]['seconds']:.3f}s | 原H身份、wait/readers/streams/H及journal均返回 |
| 自有Python已知非零 | {q['actualThree'][1]['exitCode']} | 原语义FAIL，资格接受已知归还 | {q['actualThree'][1]['seconds']:.3f}s | 非零不转永久UNKNOWN |
| 自有PS正常 | {q['actualThree'][2]['exitCode']} | PASS | {q['actualThree'][2]['seconds']:.3f}s | 同原对象归还，无重开或PID查找 |

均小于5s，资格通过后才加载/构造后续产品链。资格和其余组共用一个预冻结360s计划，没有追加第二轮资格或复用旧scope。

## 完整实际结果与边界

| 组 | 结果/准确范围 |
|---|---|
| 五缺陷纯参数 | PASS。错误argv[0]等准确拒绝，固定程序身份/metadata/exe变异拒绝；有限根谓词正反通过 |
| preStart13 | PASS。0/1/2 raw与输入source唯一关闭、原Process Dispose、真实自有已启动子进程原归还；未知只纯模型 |
| 语义346 | PASS：原98、独立原175重放、补充73；原45/17条件正例保留，合计42合成条件PASS，所有指定reason准确。原归档两次均68记录且无资格拒绝，不回填LIVE03 |
| 当前提案 | PASS静态。当前source/gate/collector/factPlan/plan及路径、false批准均匹配；外部方案仍待审未实现 |
| 原collector/wire | PASS。准确新原Gate与固定本地producer、程序身份、外部hash反例、原Popen/reader/wait/H/claim返回；合成fixture不证明外部真实授权 |
| 默认/批准/source/预算 | PASS。默认/live缺准许、schema/type/hash/source/scope/backend/product/role等准确反例无真实SDK |
| 原候选自有根完整链 | PASS。真实固定PS七角色到END，once拒重入，初proof不变，terminal writer和原claim唯一释放 |
| 十一有限故障簇 | FAIL / 部分未到达。详见下节，不以任意拒绝覆盖目标 |
| PS post/最后Start | PASS。原消费/reset/重复/类型/source/event/时钟/过期等守卫精确回归 |
| 物化变化 | PASS。准确MATERIALIZATION_ORIGINAL_PENDING_OR_BYTES，原返回/释放已知 |
| 新tester根完整链 | PASS。同一根实际通过Runner/Gate/Owner及PS七角色、END/once/唯一释放，未改根白名单隐藏问题 |
| 单字节source guard | PASS。实际仅给本次自有PS副本追加1字节，准确OWNER_SOURCE_PIN_ENTRY；不是先碰cap |

14组实际13 PASS/1 FAIL。evidence/result.json为原结果，不能用本节局部通过改其allPassed=false。

### 有限故障簇的失败与NOT_RUN

原计划MATERIALIZE_KNOWN_REJECT首例实际先因GATE_STICKY停止，未到受控物化拒绝目标；其checkpoint已证原gateReleased=true、pendingOriginalThreads=0。原helper对首例接受任意已知失败的宽断言不能据此签该目标PASS，本报告保留准确错位。

下一NO_SDK_ABORT例在构造/准备预算中以RUNNER_GATE_STICKY返回，未物化actual-home、未到受控no-SDK-abort目标；整簇因此退出。剩余9项WRONG_HOLDER、WRONG_OUTPUT_SOURCE、MATERIALIZE_LATE、RECEIVER_LATE、TAIL_LATE、EXPIRE_DURING_MATERIALIZE、BUSY、PRESTART_KNOWN_REJECT、OWNER_END_TAIL本批NOT_RUN。未重跑、暖机、扩gate30或proof10，也未改冻结产品源码以绕过时限。

这是实际已知预算拒绝/目标未覆盖，不是新资源返回UNKNOWN。原collector/Runner/Gate与13个自有Capture均已归还，最后custody检查未发现新保留对象，所有捕获原调用自然返回。后续可安全组继续按同一计划完成。细分证据evidence/finite-fault-adjudication.json及原checkpoint，旧WRONG_OUTPUT_SOURCE先cap覆盖缺口继续保留。

## 原链、根与准确小追加计量

自有根scope `{seven['terminal']['scope']}`；新tester根 `{root['home']}`，scope `{root['scope']}`。两者terminal角色数7，nextId END、初proof未改、唯一unlock/close返回且临时线程已join；重复原home均拒FRESH_ONCE_EXACT_HOME。原candidateOnlyTerminalWriterCloseNotProven字段保留，不以自写marker替自身尾返回。

自有根完整control {seven['terminal']['batchControlBytesKnown']}B，logical inbound {seven['terminal']['totalLogicalInboundBytesKnown']}B；新tester根control {root['terminal']['batchControlBytesKnown']}B，logical inbound {root['terminal']['totalLogicalInboundBytesKnown']}B，均在原生产门内。

小追加在构造前预计算局部control上界 {app['budget']['runnerControlBound']}B、gate上界 {app['budget']['gateControlBound']}B，均<262144。实际control {app['control']}B/gate {app['gateControl']}B；追加write/flush/close全部原返回，pending0、控制器进入0，原初proof不变，精确 `{app['exactReason']}`，原holder唯一释放。修补的是原先只碰cap而未到source门的**覆盖缺口**，不改原cap结果。

## 时间、来源与材料

预计245s，实际 {d['seconds']:.3f}s，360s内结束、320s前停止新增，资格也计本批；并发1/retry0。预存1GiB读/16MiB产物/96辅助进程，固定调用图保守78，观察宿主18构造（CLI/.NET内层按固定图而非冒作全局hook计数）；本批未扩任何原生产window/byte/source界。16MiB材料界另按全部新输出/快照/封存文件复核。读取为预存静态额度与原scope各自source界，未对全部Python/.NET物理IO作全局测量，不把logical统计称物理总量。

原SELF接收器针对三个简单程序的观察期在本派生profile为资格5s、有限辅助CLI80s，明确属于新辅助profile；不改变产品600/30/20/10/120、SDK7/metadata4、262144/1048576/3276800等门。新辅助代码27个pre-profile pins前后均匹配，产品原98项前后bad0。

source/gate/plan始终原4881…5e93/9cff…9d72/b280…26c8；源码、helperdiff、完整profile、原返回、语义输入输出和原输出scope的返回后快照都进入本材料manifest/ZIP；新材料不覆盖原BLOCKED原件、旧失败scope或其UNKNOWN。此次没有修改五项修订，没有签authority/LIVE、签名密钥/IPC实现、SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/Git/index。

本批只证明以上准确开发范围。有限故障簇剩余目标由负责人据完整结果统一选择，不自动补跑或签正式B/现场。独立冻结回执与报告同级，不进入自身manifest形成hash循环。
'''
delivery=P/'D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_REPORT_V1.0.md';delivery.write_text(report,encoding='utf-8',newline='\n');(H/'DELIVERY.md').write_text(report,encoding='utf-8',newline='\n')
manifest=H/'reference/material-manifest.json';assert not manifest.exists()
files=sorted(p for p in H.rglob('*') if p.is_file());rows=[dict(path=p.relative_to(H).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files];save(manifest,dict(schema='SELFCHECK02_MATERIAL_MANIFEST_V1',status='13_PASS_1_KNOWN_TIME_FAIL_NO_NEW_RESOURCE_UNKNOWN',candidateSourceSealSha256=plan['sourceSealSha256'],files=rows))
archive=P/'d1android02-global-idle-contract03-selfcheck02-frozen.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(p for p in H.rglob('*') if p.is_file()):z.write(p,p.relative_to(H).as_posix())
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(rows)+1 and len(set(z.namelist()))==len(z.namelist())
 for r in rows:assert sha(H/r['path'])==r['sha256'] and hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
 assert z.read('reference/material-manifest.json')==manifest.read_bytes()
materialBytes=sum(p.stat().st_size for r in (H,Path(plan['candidateOwnOutput']),Path(plan['testerRoot'])/('dev03-'+plan['batch'][:8])) for p in r.rglob('*') if p.is_file())+archive.stat().st_size+delivery.stat().st_size
assert materialBytes<=plan['savedBytes']
receipt=dict(schema='SELFCHECK02_FREEZE_RECEIPT_V1',deliveryPath=str(delivery),deliverySha256=sha(delivery),helper=str(H),candidate=str(B),candidateSourceSealSha256=plan['sourceSealSha256'],candidateGateSha256=plan['gateSourcesSha256'],candidatePlanSha256=plan['rolePlanSha256'],candidateFrozen98BeforeAfterBad=0,helperPreProfilePinsBad=0,qualification='PASS_3_ACTUAL_ORIGINAL_RETURNS',groups=14,passGroups=13,knownTimeFailGroups=1,semanticCases=346,syntheticConditionalPass=42,finiteFaultTargetsIncomplete=True,newResourceUnknown=False,actualWorkerSeconds=d['seconds'],materialManifestSha256=sha(manifest),materialRows=len(rows),archivePath=str(archive),archiveBytes=archive.stat().st_size,archiveSha256=sha(archive),archiveMembers=len(rows)+1,allUniqueMembersAndRowsVerified=True,allNewMaterialBytesIncludingOriginalScopesAndArchive=materialBytes,capBytes=plan['savedBytes'],actualSDK=0,actualNativeRoute=0,oldQueries=0,externalIssuer='NOT_IMPLEMENTED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
save(P/'D1_GLOBAL_IDLE_CONTRACT03_SELFCHECK02_FREEZE_RECEIPT_V1.0.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
