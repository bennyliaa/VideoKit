from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];REPORT=R/'docs/coder/D1_ANDROID02_CAPTURE_READY03_FIX_DELIVERY_V1.0.md';SEAL=B/'evidence/ready03-fix-freeze.json';ZIP=R/'docs/coder/D1_ANDROID02_CAPTURE_READY03_FIX-source.zip';INDEX=R/'docs/coder/D1_ANDROID02_CAPTURE_READY03_FIX_HANDOFF.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not SEAL.exists() and not ZIP.exists()
t=read(B/'evidence/local-selfchecks.json');a=read(B/'evidence/static-audit.json');assert t['allPassed'] and a['allPassed']
report='''# D1_ANDROID02_CAPTURE_READY03_FIX 完整集中交付 V1.0

2026-10-21；PREPARATION_ONLY。两项源码修复及原缺失验证同批完成，唯一完整开发本地集22.891秒、9组通过，等待本候选完整独立B。SDK/设备执行许可未产生，真实Android/FD/Media3/平台finish仍NOT_RUN/UNPROVEN；D1未过，M0未启。

## 本批依据与保全

依据独立B cffd1476883fcf9a6ebfa924888d16e74c1a0c8633dcedf5b48c8848d36b66bb 与本批完整要求，新目录docs/coder/d1android02-capture-ready03-fix最小修改既有PS入口与同原outer_owner.py。完整B原文和READY02入口/owner原字节引用随包；两个最小diff在evidence/ready02-to-ready03-entry.patch及ready02-to-ready03-owner.patch。

旧READY02 seal364、READY01 seal756、FIX02产品seal874、原RENDER capture seal818全部原文件size/hash结束再核一致，无原候选/旧报告/产品改写，不重开已有限关闭的五项产品源码。没有新dispatcher/native helper/诊断/release框架。SDK/ADB/5037/server/占用查询/Gradle/JVM/媒体/共享cache/旧35512/48945/17257动作均0。

上轮tester尾段反例尝试在预定目标前先遇正常proof timeout，动态未证成且其schema/delta组NOT_RUN；本报告不回写或把那次尝试改称复现。本批使用新范围与明确可达时序验证修复，开发结果也不代替下一独立B。

## CR2-B01：同源request正文原读成本

PS同一个ReadJsonExact调用在实际ReadAllBytes返回后，对精确本次RequestPath记录raw.Length和调用次数。该值加到ownerCurrentReadCost/proofReadBytes/control/总账，首步没有前驱也入账。不是用request写成本抵读，不是另外GetItem估计原读，也不扩成源码、policy、hash校验等所有物理磁盘I/O审计。

console.logicalControlReads逐项公开requestBodyBytes、requestBodyReadCalls、ownerAdmissionBytes、predecessorProofAndNativeBytes；三项字节数之和等于proofReadBytes，次数不是字节。正常七步每个请求正文各读一次，actual原请求文件长度逐项一致：

|角色|request正文B|admission读B|前驱proof/native读B|合计读B|
|---|---:|---:|---:|---:|
|identity|799|582|0|1381|
|global_idle|805|643|2806|4254|
|app_absence|805|643|2876|4324|
|test_absence|807|644|2877|4328|
|install_app|805|643|2881|4329|
|install_test|807|644|2884|4335|
|scope_all|802|641|2884|4327|

request/admission写仍是本次启动前独立写成本；前驱原console base+真实唯一outer delta沿原机制分列，后继对读/写/组和/实际source/PID/request/receipt/console/event核验不放松，不重复加入请求读。每组/全域上限不变，增加明确读量只会占用原control额度。

## CR2-B02：同一proof窗覆盖必要受控尾段

原proof writer join/close后，events.add、实际digest(pp)、last_proof/next状态和records.append仍以原共享proof_start计时；全部必要工作完成、失败或成功return分支前再执行最后一次observe，END也经过相同点。没有等下一角色重开proof_start掩盖前次迟返。

最后受控观察之后，只余失败条件/return和解释器调度尾部，这一尾部不能由同一调用自证；报告不声称解释器真正return尾部或平台finisher已被证明，也不增加无限日志/hash/自身return证据链。受控点时刻、同窗start和owner最终failure与候选proof/原writer事实分层记录。

新有限fixture门CROSS_SAME_DEADLINE_AFTER_TIMELY_WRITER仅在OFFLINE_FIXTURE生效、窗口最多2秒。测试选1秒，源码先确认同原writer实际及时close/join、failure仍空，再记录deadline并以有限Event.wait等到同一绝对单调deadline+0.005，然后执行必要digest/交接和最终observe。没有反射改failure/改冻结状态/relative sleep竞争；生产不执行该门。前置writer若不及时，测试就不能声称命中尾段，本批断言会失败并停追加。

两个目标均实际达到，数字为同次monotonic秒，非日期/系统磁盘故障：

|目标|原writer返回/已join|同窗deadline|尾门返回|最后受控点|最终|
|---|---:|---:|---:|---:|---|
|下一角色前尾段|140029.812|140030.750|140030.765|140030.781|PROOF_WALL_TIMEOUT_STICKY，global_idle未进入|
|END尾段|140032.109|140033.030|140033.046|140033.078|PROOF_WALL_TIMEOUT_STICKY，END不能成功交接|

两项都满足writer及时返回≤join观察<deadline≤尾门返回≤最后受控点。原writer已无pending、尾段最后observe时pending原线程0，区别于原proofwriter timeout的pending1；后续run_one再次拒绝，next计数不增加，不改写候选文件补绿。候选proof依然明确不能自证自身writer归还或最终及时性，真实owner源码控制流才决定下一admission；JSON/hash不是恶意本地主机认证。

## 完整本地自检及缺失目标

唯一实际整套selfchecks/run_checks.py：22.891秒<30，9组全部完成通过，没有失败/中间不完整套件被重跑补绿。本批保留最终entry/owner/driver快照和所有原请求/raw/console/native/proof/writer/时点。14个原本地capture控制器串行，另1个纯政策PS host；当前scope实际SDK child仍0。

|组|实际覆盖|
|---|---|
|PREPARATION|默认Owner在Popen前拒|
|完整七步|正确原base+真实outer delta接续，首base15299+delta2806；每角色request读逐项核，末control146416/total147913，末END新增开销亦计|
|严格政策及delta|完整13样本+三类实际entry拒绝+一项纯预算超限门，安排在所有迟返用例之前，全部已执行|
|busy实际capture|新scope的identity后global_busy原producer→原capture ENV_WAIT，app_absence不进入；不是历史流重放|
|超量|read192B/save64B，失败sticky；不称完整raw或裁到cap合格|
|outer原窗口|0.1秒在3原线程pending时观察超界，原自然返回后仍拒后继|
|proof原writer窗口|0.03秒、有限close延迟0.12秒时1原writer pending，归还后仍sticky|
|及时writer后尾段/后继|达到上表目标、最终同窗observe拒绝后继|
|及时writer后尾段/END|达到上表目标、最终同窗observe拒绝END成功|

13个严格schema纯政策样本准确为：zero/upper-equal两正例有限PASS；negative/bool冒整数/string/fraction/over/null/missing/firstFailure非空/missing-firstFailure/flag-int/history-type十一负例均APP_REQUIRED_TYPES_BOUNDS_OR_FIRST_FAILURE。保持必需字段存在、准确bool/string/int-long、非负与上界、firstFailure存在且null和完整history/原owner约束。不是实际Android坏回执/真机复现。

三delta原入口负例reset→OUTER_DELTA_RESET_OR_DUPLICATE、fake→ORIGINAL_OUTER_DELTA_SOURCE_BYTES、duplicate→OUTER_DELTA_RESET_OR_DUPLICATE。它们只在开发新fixture副本造负例并恢复原字节，不改任何冻结候选/生产scope。额外纯预算策略样本WHOLE_SEVEN_ROLE_BUDGET_BEFORE_CHILD，未假称真实SDK超限。

正常安装模拟同原stdin4096+2048=6144B，pending+final完整原bytes保留；实际PS/producer/外层wait/readers/Windows handle/原proofwriter自然返回，无kill/interrupt/cancel/二close/未知重试。文本观察/写入177974B；整套目录201文件共911835B（含源码/所有记录/6144B载荷），亦<4MiB，非精确物理I/O量。永久unknown分支只静态保持原对象/引用，不制造永久故障、无全host idle结论。

## 原范围/预算/许可不扩

计划f0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199字节不变；准确七角色identity/global_idle/app_absence/test_absence/install_app/install_test/scope_all，固定HA1Q6WXR/TB138FC/API31及future fresh fingerprint/global门。两个自身包任一存在即停；无-r新装，无覆盖/清理/卸载/换包/设备替代。唯一scopeAll、fixture19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c、新runId待独立B后另签。

FIX02产品seal39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad；app7151481B/f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad；test478124B/b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9，原同cert/版本/包/runner不变。

七SDK max、并发1无retry；preflight两流1048576（65536/851968/65536/65536）、install131072、instrument所有pending+final1048576、controllerproof1048576，总logical inbound3276800；APK outbound7629605+command每步4096/全28672=logical上界7658277。源read-locked pin、读取/写入/承诺/SDK内部再读/ADBframing未知分列。四15+两45+90=240仅分项和，App60，outer/localproof/whole600/30/600实值仍空，不扩窗口不作强停许可。

默认PS/Python均PREPARATION_ONLY，activation approved=false，新scope/runId/B/toolseal/freshroute/初始proof/实际wall均待另签。原受审tool/server/exclusive claim能力未在本批查询或重建，历史gate不当当前事实。独立完整B前无自动设备activation，不重复索用户通用平板许可。最高仍PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN，非平台/Binder finisher尾段/FD/播放/DTS/隔离/COMMIT/D1通过；32oracle不冒全runtime PASS。

## 准确身份与集中交接

入口 @ENTRY@

准确owner @OWNER@

producer @PRODUCER@（与READY02同字节）

最终完整自检 @TEST@

reference/original-outer-owner-contract.md头部明确本批读账及最后受控点边界，其余原合同保留。evidence/static-audit.json含旧四套seal逐行核、计划/源pins、唯一测试历史/全目录字节数。tools/verify_frozen.py只读核全清单，不启动子进程；不要在冻结目录重跑会写入的build/audit/selfcheck/freeze。

本报告及候选全部文件纳seal，seal排除自身/外置ZIP避免循环；ZIP为清单全部+seal，逐成员大小/hash/CRC校验。外置D1_ANDROID02_CAPTURE_READY03_FIX_HANDOFF.json记录报告/seal/ZIP准确字节/hash/member数，发送回执在冻结外。集中交负责人后等待新完整独立B；未证能力、旧失败/UNKNOWN及tester上轮INCONCLUSIVE/NOT_RUN原层级不回写。
'''
report=report.replace('@ENTRY@',t['entrySha256']).replace('@OWNER@',t['ownerSha256']).replace('@PRODUCER@',t['producerSha256']).replace('@TEST@',sha(B/'evidence/local-selfchecks.json'));REPORT.write_text(report,encoding='utf-8')
paths=sorted([p for p in B.rglob('*') if p.is_file() and p!=SEAL]+[REPORT],key=str)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
save(SEAL,{'schema':'READY03_FIX_FROZEN_V1','createdUtc':datetime.now(timezone.utc).isoformat(),'status':'PREPARATION_ONLY_TWO_IMPLEMENTED_PENDING_INDEPENDENT_B','files':rows,'archiveMembersExpected':len(rows)+1,'sdkActions':0,'newPermit':None})
with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in paths+[SEAL]:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(ZIP) as z:
 assert len(z.namelist())==len(set(z.namelist()))==len(rows)+1 and z.testzip() is None
 for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
 assert hashlib.sha256(z.read(SEAL.relative_to(R).as_posix())).hexdigest()==sha(SEAL)
index={'schema':'READY03_FIX_HANDOFF_V1','status':'FROZEN_PREPARATION_PENDING_B','files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [REPORT,SEAL,ZIP]],'sealFileRows':len(rows),'archiveMembers':len(rows)+1,'localSuiteSeconds':t['elapsedSeconds'],'sdkActions':0,'deviceActions':0}
save(INDEX,index);print(json.dumps(index,ensure_ascii=False))
