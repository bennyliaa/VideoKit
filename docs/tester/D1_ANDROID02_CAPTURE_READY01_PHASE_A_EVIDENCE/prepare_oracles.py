from pathlib import Path
import datetime,hashlib,json
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;C=R/'docs/coder/d1render02-capture';P=R/'docs/coder/d1media3-android02-fix02';REPORT=R/'docs/tester/D1_ANDROID02_CAPTURE_READY01_PHASE_A_REPORT_V1.0.md';assert not REPORT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=R/'docs/milestones/D1_ANDROID02_CAPTURE_READY01_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-snapshot.md').write_bytes(req.read_bytes())
oldSeal=C/'evidence/capture-adapt-freeze.json';assert sha(oldSeal)=='65e8413b3e90dd571c22fea7049778b29c0d94221cd490560cdcd5c3cc00ae5a';oldMap={x['path'].replace('\\','/'):x for x in read(oldSeal)['files']}
selected=[C/x for x in ['tools/capture_render02.ps1','tools/admission.ps1.txt','tools/stdin-owner.ps1.txt','release/capture-policy.json','release/activation-required.template.json','release/exact-28-role-mapping.json','reference/exact-operation-and-accounting-plan.json','reference/capture-capability-audit.json','evidence/source-provenance.json','selfchecks/capture_fixture.py']]
for p in selected:
 rel=p.relative_to(R).as_posix();x=oldMap[rel];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert sha(selected[0])=='b836b50403b4914a4afe762de5e327e2d97ac38bcc66beebafc1d097ab81f17e'
oldReport=R/'docs/tester/D1_RENDER02_CAPTURE_ADAPT_REVIEW_REPORT_V1.0.md';oldBind=R/'docs/tester/D1_RENDER02_CAPTURE_ADAPT_REVIEW_EVIDENCE/final-review-binding.json';bind=read(oldBind);assert sha(oldReport)==bind['reportSha256']=='c87e3c900e78e95a204189a796cedeb52ac9774b0bbf0b0a37384452617fe886'
oldEvidence=R/'docs/tester/D1_RENDER02_CAPTURE_ADAPT_REVIEW_EVIDENCE';oldEvidencePaths=[oldEvidence/x for x in ['independent-external-accounting-chain.json','independent-chain-audit.json','independent-actual-accounting.json','independent-static-audit.json','independent-suite-results.json','gate-pending-external-observation.json','file-close-pending-external-observation.json']];oldPins={x['path'].replace('\\','/'):x for x in bind['evidence']}
for p in oldEvidencePaths:
 key=str(p).replace('\\','/');x=oldPins[key];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
fixSeal=P/'evidence/fix02-freeze.json';assert sha(fixSeal)=='39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad';fixMap={x['path']:x for x in read(fixSeal)['files']}
product=[P/x for x in ['evidence/execution-plan.json','src/com/videokit/d1android/ExperimentContract.java','instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java','instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java','artifacts/media3-android02-fix02-app-debug.apk','artifacts/media3-android02-fix02-test-debug.apk']]
for p in product:
 x=fixMap[p.relative_to(R).as_posix()];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
bp=R/'docs/tester/D1_MEDIA3_ANDROID02_FIX02_PHASE_B_REVIEW_REPORT_V1.0.md';bm=R/'docs/tester/D1_MEDIA3_ANDROID02_FIX02_REVIEW_EVIDENCE/review-evidence-manifest.json';assert sha(bp)==read(bm)['reportSha256']=='4421c264ab6c45a78979aaa9339a3bc1c19e7c3a9b2bf5c6442c0c68dedce1f3'
allSelected=selected+oldEvidencePaths+product+[oldSeal,oldReport,oldBind,fixSeal,bp,bm,req]
save('authority-and-frozen-baseline.json',{'stage':'A_OLD_FROZEN_MECHANISM_AND_FINAL_FIX02_ONLY','selectedPins':[pin(p) for p in allSelected],'oldSealVerifiedSelectedRowsOnly':len(selected),'oldComplete818SuiteNotReplayedOrRehashed':True,'newFloatingToolFilesRead':0,'sdkFilesOrProcessesReadOrExecuted':0,'deviceActions':0,'actualOccupancy':'NOT_OBSERVED','productApkOpaqueHashBytes':sum(p.stat().st_size for p in product if p.suffix=='.apk'),'oldLimitedReview':'25 prepared serial/3 screenshot not admitted, exact old capture review preserved; no new capture PASS inferred'})
newplan=read(P/'evidence/execution-plan.json');assert newplan['futureOperationBudget']['logicalPlatformInvocations']==6
apks=[pin(p) for p in product if p.suffix=='.apk'];assert sum(x['bytes'] for x in apks)==7629605
base={'status':'PREPARED_NOT_RUN','argv':'UNBOUND_UNTIL_NEW_COMPLETE_FROZEN_TOOL_B','newScope':'UNASSIGNED_NO_EXECUTION_AUTHORIZATION','originalReturnRequired':'same original child Process/PID, stdin/stdout/stderr Tasks/files/lock/metadata + outer controller natural return + separately returned proof writer; independent semantic PASS before next role','retry':False,'concurrentSdkChildren':1,'stderr':'raw TEXT separately preserved; nonempty follows reviewed stop policy, never discarded','rawStreams':'full original stdout+stderr including partial/pending/final; overflow records actual observed prefix/unknown and stops, never truncates to cap for PASS'}
spec=[
 ('CR01','IDENTITY','批准HA1Q6WXR/TB138FC/API31与fresh fingerprint身份；当前未读取设备。',15,'PRE_SDK_LOCAL_CAPTURE_TOOL_ROUTE_CLAIM_PROOF','exact serial/model/API/fingerprint/runtime identity matches reviewed future contract; mismatch/unknown stops before later roles','PREFLIGHT_SHARED_1048576'),
 ('CR02','GLOBAL_FRESH_IDLE','同次fresh全局其他项目前台/instrumentation/测试占用，只读有界查询。',15,'CR01_SAME_SCOPE_IDENTITY_PASS','Other project busy => ENV_WAIT entire scope stop; partial/ambiguous/unknown not idle. No stop/kill/foreground change, no continuous poll or second global child','PREFLIGHT_SHARED_1048576'),
 ('CR03','APP_ABSENCE','准确com.videokit.d1media3.android02当前存在性一次。',15,'CR02_FRESH_GLOBAL_IDLE_PASS','Only explicit absence accepted; presence stops, query failure is not absence; no upgrade/clear/uninstall/rename','PREFLIGHT_SHARED_1048576'),
 ('CR04','TEST_ABSENCE','准确com.videokit.d1media3.android02.test当前存在性一次。',15,'CR03_APP_ABSENT_PASS','Only explicit absence accepted with original successful query response; same restrictions as APP','PREFLIGHT_SHARED_1048576'),
 ('CR05','INSTALL_EXACT_NEW_APP','同read-locked/pinned app7151481B/SHAf67edf...ac04ad无-r安装一次。',45,'CR04_BOTH_PACKAGES_ABSENT_AND_GLOBAL_GATE_PASS','Original APK exact hash/length + binary outbound commitment before child; raw install response explicit success + full capture and outer return','INSTALL_SHARED_131072'),
 ('CR06','INSTALL_EXACT_NEW_TEST','同read-locked/pinned test478124B/SHAb034ce...dc37d9无-r安装一次。',45,'CR05_APP_INSTALL_SEMANTIC_AND_ORIGINAL_RETURN_PASS','Exact test package/version/signer/target bound to frozen product; no path/param replacement/extra push','INSTALL_SHARED_131072'),
 ('CR07','INSTRUMENT_SCOPE_ALL','准确runner一次，case=scopeAll/fixturehash19e815...778a9c/新D1MA02-runId；十case同Job，非十次am instrument。',90,'CR06_TEST_INSTALL_SEMANTIC_AND_ORIGINAL_RETURN_PASS','All partial/status/final preserved; requested method identity and history/counts/firstFailure/layered budget/original owner gates assessed. ADB client exit alone is not internal platform finish/native/media PASS','INSTRUMENT_ALL_PENDING_FINAL_1048576')]
roles=[]
for n,(rid,role,purpose,seconds,dep,semantic,budget) in enumerate(spec,1):
 d=dict(base);d.update(id=rid,ordinal=n,role=role,purpose=purpose,qualificationSeconds=seconds,semanticDependency=dep,passOracle=semantic,textBudgetGroup=budget,sdkChildCost=1,commandPayloadUpperBound=4096);roles.append(d)
roles[4]['binaryOutboundPin']=apks[0];roles[5]['binaryOutboundPin']=apks[1]
roles[6]['exactProductArguments']={'case':'scopeAll','fixtureSha256':'19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c','runId':'UNBOUND_FRESH_D1MA02_[A-Z0-9_-]{1,32}','runner':'com.videokit.d1media3.android02.test.Media3Instrumentation','target':'com.videokit.d1media3.android02','test':'com.videokit.d1media3.android02.test','process':'com.videokit.d1media3.android02:media3','version':'D1-MEDIA3-ANDROID02-FIX02','versionCode':1,'certificateSha256':'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f'}
save('seven-role-independent-oracles.json',{'roles':roles,'allRolesStatus':'PREPARED_NOT_RUN','existingSixOperationPlan':'Product6 proposal retained; current accurate capture batch7 adds explicit fresh global gate, not mutation of frozen product plan','noHiddenExtraOperations':'No adb devices/version/start-server/ps/logcat/screenshot/pull/push/cleanup or extra server probe children outside frozen7; prerequisite capability itself must not spend unapproved SDK role'})
conditions=[
 ('PREPARE_ZERO_CHILD','PREPARATION_ONLY rejects before request/SDK Process/lock/context, even missing request; no production activation now.'),
 ('MODE_SEPARATION','OFFLINE_FIXTURE only fixed local approved Python producer/hash/modes/root; reject SDK path and arbitrary argv/shell before child.'),
 ('EXACT_SCHEMA','Duplicate/case-conflicting fields, extras, wrong scalar/argv types, NaN/Inf, bad path/reparse or wrong source/hash fail child-before; no arbitrary URI/path/method params.'),
 ('EXACT_NEW_CHAIN','New entry/source/plan/policy/product seal/B review/activation/tool/scope/runId/output root bind mutually; label alone not authority; old RENDER scopes/once/halt not reused.'),
 ('ONLY_SEVEN_ROLES','Exactly seven ordered SDK role ids and precise argv; no eighth child, retries, parallel SDK or undeclared per-role shell subcommands.'),
 ('LOCAL_CAPTURE_GATE','Before CR01 prove fixed tool and default server route/claim through existing reviewed capability/metadata and actual local owner returns. No SDK/5037 probe or server mutation to improvise proof; insufficient capability BLOCKED before child.'),
 ('GLOBAL_NOT_PACKAGE_ABSENCE','Fresh other-project occupancy gate is independent of own package absence, old ENV_WAIT and stale snapshots; unknown/partial fails closed without repeated polls.'),
 ('APK_BEFORE_START','Read-only same original source file length/hash locked before install, no mutable-path alias; outbound committed exact7629605 separate from pin reads/source reads/stdout archive; SDK file reads/wire internally unmeasured stay explicit.'),
 ('ORIGINAL_CONTEXT_BEFORE_START','Original Process/start intent/stream file/pipe/lock refs held before native open/start; actual PID only after original start returns, unknown start held, no substitute child or double-close.'),
 ('RAW_BOTH_STREAMS','Every successful original read accounted before queue/qualification; stdout and stderr separate bytes, no text reencode/tail, finite writer backlog/known saved prefix and partial UNKNOWN distinct.'),
 ('CHILD_VS_RETURN','Process exit code/wait, stdin, read Tasks, pipe close, original file write/close, metadata lock and controller outer return are separate gates; client exit/counter0/fileexists not all-return.'),
 ('PROOF_NOT_SELF_CERTIFY','Receipt cannot prove own writer close; console cannot prove own flush/controller exit. Form next proof in later action after actual outer/Popen streams and proof-writer natural return, bound original controllerPid/receiptHash/nextId/scope/semantic and accumulated real+UNKNOWN amounts.'),
 ('SEMANTIC_NEXT','Raw captureQualified not device idle/install success/Android PASS; require role-specific accepted semantic proof. Busy/identity mismatch/presence/nonzero/stderr/unknown stops dependents.'),
 ('OP_BUDGET','Pre-reserve SDK7 max and one active; entered uncertain charged, no refund/case reset/retry. First/predecessor cumulative exact0..6 and role id chain verified.'),
 ('OUTBOUND_BUDGET','APK app7151481+test478124=7629605; command perop4096,total28672; upper7658277. Count binary separate not input fixture/output archive.'),
 ('INBOUND_BUDGET','Four preflight combined1048576; install combined131072; all instrument pending/final two streams1048576; all controller/proof local record+forward/report overhead1048576; total3276800. Fix per-role allocations whose group sums fit; cannot allow every preflight whole group afresh.'),
 ('WIRE_CAPABILITY','Application payload commitments/known prefixes not exact ADB transport framing or SDK internal read volume. Explicit UNOBSERVED; if full required raw/installation/proof capture cannot be retained BLOCKED prechild.'),
 ('QUALIFICATION_TIMES','CR01..04 each15s, CR05..06 each45s, CR0790s vs App samebody60. Fixed old max45 cannot admit90 unmodified. Sequential child observation sum240s is not authorized single whole-batch hardwall; later accurate outer wall/overhead contract must distinguish these.'),
 ('TIMEOUT_NO_FORCE','Timeout/overrun/error closes new admission but same original references/pipes continue held; no wait timeout kill, interrupt, taskcancel, second reader/close, force-stop or server restart; later natural return cannot upgrade earlier UNKNOWN.'),
 ('PARTIAL_HISTORY','Preserve every pending and final status, existing completed case history/current snapshot/firstFailure; final-only tail or file truncation cannot pass.'),
 ('SELF_CHECK_LIMITS','Future B only fixed local finite Python fixture. Complete suite <=30sec, one child serial, text<=4MiB, injected fixture payload<=64KiB, finally release/join original, no permanent fault or old suite rerun.'),
 ('OLD_FIXTURE_LIMIT','Old stdin mode requires349102B, exceeds new64KiB fixture injection. Do not replay it as meeting this batch; minimal frozen finite variant or other bounded input test required. No new native helper/platform.'),
 ('NO_PRODUCT_REPLAY','Use exact FIX02 seals/accepted B only, no APK rebuild/Gradle/library runtime/Media3 tests in A or captureB. SDK activation separate after complete new frozen tool B.'),
 ('UNKNOWN_PRESERVATION','Old35512/48945/17257 and all consumed/stopped scopes untouched; no process/handle/port/ledger query or automatic cleanup for idle. User persistent tablet use permission kept, no repeated generic approval question.'),
 ('B_COMPLETE_HANDOFF','Review whole new minimal tool diff, sourcepins, seven exactargv/role/group budgets, precise activation template, fixture source/results and original returns only after freeze; report all findings once, then coordinator separately activates accurate fresh scope/device. No new release/dispatcher layers.')]
assert len(conditions)==25
save('cross-role-admission-capture-budget-oracles.json',{'oracles':[{'id':'AC'+str(k).zfill(2),'area':area,'oracle':text,'status':'PREPARED_NOT_RUN'} for k,(area,text) in enumerate(conditions,1)],'actualRuns':0})
oldText=selected[0].read_text();anchors=[]
for token,label in [('PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION','prepare rejects first'),('FIXED_28_PLAN_PIN','old28 plan pin'),('a226b5fe0703d31c486ec2deaad1c2f2241169f4c8257701331cd5d9c1a83581','old product seal'),('bytes=10480388','old app payload'),('bytes=2695613','old test payload'),('qualificationSeconds -gt 45','old max observation45'),('maxTextBytes -gt 524288','old per role text512KiB'),('$batchSdkBefore+1 -gt 32','old global operation32'),('batchTextChargedBytesKnown=$batchTextBefore+$c.textBytes','old external text formula'),('receiptOwnCloseNotProvenByThisFile','receipt own close boundary'),('externalControllerExitProofStillRequired','external original return boundary')]:
 hits=[n+1 for n,line in enumerate(oldText.splitlines()) if token in line];assert hits,token;anchors.append({'meaning':label,'oldSource':pin(selected[0]),'line':hits[0],'match':token})
save('old-capture-adaptation-boundaries.json',{'sourceAnchors':anchors,'oldPolicy':read(C/'release/capture-policy.json'),'oldActivationMustNotAuthorizeNewBatch':read(C/'release/activation-required.template.json'),'newProduct6PlanNotChanged':pin(P/'evidence/execution-plan.json'),'needMinimalExactAdaptationNotGeneralPlatform':True,'newToolEntryPlanPolicyToolHashAndActivation':'UNBOUND_NOT_READ_FROM_FLOATING_CANDIDATE','oldMechanismPreserved':['same Process and async pipes','single original raw files and metadata writers','exclusive original scope lock and once/halt files','pinned original input source','actual outer original process/streams and later proof return','known-prefix vs amountUNKNOWN and sticky fail']})
budget={'sdkRoles':7,'parallel':1,'retry':0,'binaryOutboundBytes':7629605,'commandPerRoleMax':4096,'commandTotalMax':28672,'logicalOutboundUpperBound':7658277,'preflightTwoStreamsTotal':1048576,'installTwoStreamsTotal':131072,'instrumentationAllPendingFinalTwoStreamsTotal':1048576,'controllerProofTotal':1048576,'logicalInboundUpperBound':3276800,'sequentialChildQualificationSeconds':[15,15,15,15,45,45,90],'sumChildQualificationSeconds':240,'sdkAppBodySeconds':60,'adbTransportFraming':'UNOBSERVED','newToolHashScopeDeviceFreshIdleCaptureBound':False}
assert budget['binaryOutboundBytes']+7*4096==budget['logicalOutboundUpperBound'] and 1048576*3+131072==budget['logicalInboundUpperBound'] and sum(budget['sequentialChildQualificationSeconds'])==240
save('future-b-activation-and-budget-contract.json',{'budget':budget,'A':'32 independent oracles prepared; no candidate new code reads/exec','B':'Only after complete new capture freeze; independent static/pure local <=30s suite and accurate seven role/pins/owner budget review; still no SDK','activation':'Coordinator after complete independent B, exact fresh local capability+device+global idle in seven roles; persistent tablet consent kept. No automatic A->B->device dispatch','unbound':['new entry/sourcehash/plan/policy','actual approved adb/tool/server route+claim metadata','scope/planId/newD1MA02runId/output root','activation document and independent new tool B hash','per-role cap split and full outer-controller overhead/wall contract','global bounded query exact argv and semantic complete-idle parser']})
for x in [pin(p) for p in allSelected]:assert sha(R/x['path'])==x['sha256']
roleTable='\n'.join('| '+r['id']+' | '+r['role']+' | '+str(r['qualificationSeconds'])+' | '+r['semanticDependency']+' |' for r in roles)
text='''# D1 ANDROID02_CAPTURE_READY01 阶段A独立准备报告 V1.0

2026-10-21；tester；只审旧冻结采集机制及最终FIX02身份，不读coder浮动新工具。

## 结论

**PHASE_A_SEVEN_ROLE_CAPTURE_ORACLES_PREPARED**。已准备7个准确SDK角色oracle及25项跨角色准入/双流/预算/原返回oracle，共**32项PREPARED_NOT_RUN**。这是A准备完成，不是新采集工具独立通过、生产执行许可或设备空闲结论。新工具完整冻结后负责人另派本地B，B后再单独准确activation；当前SDK/ADB/5037/占用/设备/产品与fixture执行、Gradle/JVM调用均0。

接受FIX02独立B4421c264ab6c45a78979aaa9339a3bc1c19e7c3a9b2bf5c6442c0c68dedce1f3的五项指定有限源码/最终typed门通过；其实际Android/FD/Media3/finish NOT_RUN保持，未扩大READY/D1。旧35512/48945/17257 UNKNOWN无查询或处置，M0未启。用户持续平板许可不重复询问，但本批不实机。

## 冻结依据与实际阅读范围

新TESTER要求准确快照已保存。旧capture seal65e8413b3e90dd571c22fea7049778b29c0d94221cd490560cdcd5c3cc00ae5a及选定10份原机制/政策/计划/固定fixture源逐seal hash核；入口b836b50403b4914a4afe762de5e327e2d97ac38bcc66beebafc1d097ab81f17e，旧计划1db733cd14d51b47d41df3670a5d9d84b1f68f599aeb3d02b8d1d814236810d1。旧独立报告c87e3c900e78e95a204189a796cedeb52ac9774b0bbf0b0a37384452617fe886及binding、有限7份预算链/双流/门收据摘要选定hash核对；不重跑旧24控制器、不声称本轮重新核全818或ZIP。

只读最终FIX02 seal39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad、准确源码入口参数/原6操作计划、双APK身份及接受B报告/manifest。app7151481B/f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad，test478124B/b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9；读取两APK合计7629605B为opaque hash身份读，包含媒体asset字节，不声称载荷读取0；未媒体解析或重验签/JVM，未动未来设备账。未读SDK工具文件、当前server/claim/其他项目或新候选浮动目录。

## 七角色准确顺序

| ID | 角色 | 观察秒 | 必要先序语义 |
| --- | --- | ---: | --- |
'''+roleTable+'''

每角色SDK成本1、全scope最多7、并发1、无retry，不能把十内部case拆为十个instrument。CR01仅批准HA1Q6WXR/TB138FC/API31的未来fresh事实，不自动换手机。CR02补原FIX02六操作提案缺失的全局其他项目前台/instrumentation/测试占用门：**旧ENV_WAIT、仅自身包absence、旧snapshot都不是fresh idle**。其他项目忙立即ENV_WAIT停止本scope；partial/unknown/无法判定不得作idle，不操作/强退其他项目，不持续ADB轮询。

两准确包任何一个存在就停，不-r/升级/清数据/卸载/换包名；query错误不能当absence。后继除了原capture返回，还需相应identity/global idle/absence/install成功语义独立接受。新的global只读有界查询及全部精确argv由完整新工具冻结后B审，本A不发明可执行shell或借多次查询加第八SDK；role argv均UNBOUND。

唯一产品runner com.videokit.d1media3.android02.test.Media3Instrumentation；app/test com.videokit.d1media3.android02/.test；进程:media3、versionCode1/FIX02、同cert5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；三参数只case=scopeAll/fixtureSha256=19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c/新D1MA02-runId。scope/planId/runId/outputRoot一次新绑定，不续用已耗范围或旧once/halt账。

## 旧采集可复用与必须最小适配处

可保留的是原Process/真实PID、原async stdout/stderr、原raw文件与metadata writer、同原输入FileStream、scope独占锁、先序proof和UNKNOWN强保管结构。旧review仅对准确旧25串行角色有限通过，不授新产品执行。旧入口固定28计划/RENDER产品seala226b5...、旧app10480388/test2695613、32SDK/4MiB文本/16MiBarchive和最大45秒；旧每项text上限524288B也不足本批instrument1048576B。需做**准确7白名单/新产品pin/角色各15-45-90秒/分组新预算**最小适配，不能改标签或参数伪装为旧角色。

PREPARATION_ONLY必须在request/SDK child/锁/context之前明确拒生产；OFFLINE_FIXTURE只能准确固定Python/hash/有限模式/root，不能通过fixture走SDK。精确新入口/原源diff/计划/政策/activation/产品seal/B报告/toolhash/scope/root相互绑定，不能只有自贴approved标签。现有成熟tool/server route/claim需原受审机制可证的fresh本地事实和原返回；能力不足首child前BLOCKED，不能额外运行adb version/devices/start-server/5037 probe或造新诊断/dispatcher/release链来获得能力。

旧固定Python stdin模式要求349102B，**超过本批selfcheck fixture≤64KiB**，不可直接重放并称符合；后续最小固定变体或其他已冻有限输入模式才可用于新B。旧binary8201/overrun192/late等仅已有有限非媒体端口，均非截图/播放。新本地自检整集≤30秒、单child串行、文本≤4MiB、fixture≤64KiB、finally放同原门/join，自然Popen两流归还，不运行SDK、产品或旧大套。

## 双流、原输入与三层返回

每原stdout/stderr成功read先累加再资格/队列/写，全部pending/final和stderr保原字节。超额按真实已知前缀/未知照记并停止，不裁成cap、tail或只lastJSON补绿。write partial/fault、read启动未知、source或file关闭未知各自保管原对象，不第二reader/替换Process/二close。stderr非空按已审停止政策留证，不能丢弃求成功。

安装APK是**准确同原read-locked文件length/hash与出站payload承诺**，pin读取、源传输读取、stdout入站保存、控制证明写入分别计；ADB内部按路径读和wire framing未观测，不伪报实际传输精确字节。若旧机制不能保全本批全部安装payload承诺/两流/原返，则先BLOCKED，不先花identity或global SDK再补工具。

第一层原SDK child wait/exit、stdin和两reader/task/pipe/file/write/close/lock；第二层metadata/receipt原writer与控制器console/flush/外Popen原两流及自然返回；第三层后续动作真实形成proof的原writer/辅助返回与语义审核，必须分别可证。receipt不能证明自己的close，console不能证明自己的flush/控制器退出，proof不能由自身标签证明归还。下一角色前核同controllerPid/receiptHash/nextId/scope/semantic与真实累计账，proof只在实际原外层已返后的后续动作产生；文件存在、counter0、future完成或工具显示完成不代原返回。

旧完整外层计量链已显示：首controller8378B+外return885B+实际proof631B=9894B提交前账，次controller18909B另有外return989B；本A只保留该旧证据，**新预算不能仅抄console数字**，必须包括所有原控制/转发/报告/proof写读，未知拒后继。ADB壳exit不证明平台instrumentation内部finish、nativeFD或Media3结果；在实际机制能证明的层级分别留UNPROVEN/NOT_RUN。

## 全scope准确预算与时间

四preflight两流合计1048576B；两install合计131072B；单instrument全部pending-final两流1048576B；controller/proof整体1048576B；总logical inbound **3276800B**。新冻结计划需把各角色cap分配到这些组，不能每preflight又获得整组1MiB；原外层写/读/转发/未知也计原证明预留，不复用旧4MiB总额求准入。

两APK binary出站 **7629605B**，命令每op4096/七项总28672，logical outbound上界 **7658277B**。APK出站不是stdout archive、也不是本地selfcheck fixture注入。无额外fixture push/截图/logcat/pull旧包或清理SDK。ADBframing未知，精确工具能力与不可见传输分列。

identity/global/appabsence/testabsence各15秒，install各45秒，instrument90秒；单App body仍60秒。七child顺序观察额度之和240秒只是算术，**不把instrument90秒误作全七操作wholewall，也不将240秒擅自授权为强制结束界**；完整新执行合同还需区分前置本地/proof/外层wall。任一观察超窗/超量/异常/原owner未返停止新准入、同原引用与流UNKNOWN保管，后来真实自然返回不回升成功；无kill/interrupt/任务取消/强关流/force-stop/serverrestart/自动重试。

## 完整B与未来activation门

已备7角色+25跨角色oracle，各PREPARED_NOT_RUN；正反项覆盖prepare不存在request也先拒、duplicate/schema/source/argv/hash/pins错误、旧scope/halt/缺前驱、原外层未返或budget UNKNOWN、7op/两流/安装准确载荷、有限晚返保管等。它们是**待新完整工具B实际验证**的验收条件，不拿旧17/24控制器结果冒新通过。

不读docs/coder/d1android02-capture-ready01浮动新源，不改产品/构建APK/新平台。完整工具冻结经负责人核后另派离线B，核最小准确diff/实际七argv/分角色及全scope预算/原return正反本地自检/许可sourcepin/sealZIP；不存在完整capture能力则BLOCKED。B仍不设备，随后负责人单独准确activation/fresh local capability+身份+全局占用七角色；当前这些绑定均空，不能连续等待设备空闲或自动下发SDK。

本A报告、准确旧身份/selected source anchors、七角色、25跨角色、预算/B/activation合同及要求快照冻结后一次发送负责人；发送收据目录外。原报告/局部PASS/FAIL/UNKNOWN和所有旧scope消费保持，D1/M0不自动推进。
'''
REPORT.write_text(text,encoding='utf-8');manifest={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'PHASE_A_SEVEN_ROLE_CAPTURE_ORACLES_PREPARED','report':REPORT.relative_to(R).as_posix(),'reportBytes':REPORT.stat().st_size,'reportSha256':sha(REPORT),'roleOracles':7,'crossRoleOracles':25,'allOracleStatus':'PREPARED_NOT_RUN','evidenceFiles':[pin(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='phase-a-evidence-manifest.json'],'newFloatingCandidateRead':False,'sdkDeviceJvmMediaCalls':0,'oldUnknownActions':0};save('phase-a-evidence-manifest.json',manifest);print(json.dumps({'reportBytes':manifest['reportBytes'],'reportSha256':manifest['reportSha256'],'manifestSha256':sha(E/'phase-a-evidence-manifest.json'),'evidenceFiles':len(manifest['evidenceFiles']),'oracles':32}))
