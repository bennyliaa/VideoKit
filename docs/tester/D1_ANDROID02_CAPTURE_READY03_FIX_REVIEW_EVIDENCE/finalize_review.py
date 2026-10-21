from pathlib import Path
import datetime,hashlib,json
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready03-fix';E=Path(__file__).resolve().parent;REPORT=R/'docs/tester/D1_ANDROID02_CAPTURE_READY03_FIX_PHASE_B_REVIEW_REPORT_V1.0.md';assert not REPORT.exists()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def anchor(path,fragment):
 p=B/path;lines=p.read_text().splitlines();hits=[n+1 for n,l in enumerate(lines) if fragment in l];assert hits;return {**pin(p),'line':hits[0],'match':fragment}
suite=read(E/'independent-suite-results.json');assert suite['seconds']==27.75 and len(suite['results'])==6 and sum(x['pass'] for x in suite['results'])==5 and suite['results'][-1]['detail']=="AssertionError('SUITE_STOP_NEW_OWNER_26S')"
reads=read(E/'independent-seven-read-accounting.json');assert len(reads)==7 and all(x['logicalReadTotal']==x['request']+x['admission']+x['previousProofNative'] for x in reads)
coder=read(B/'evidence/local-selfchecks.json');assert coder['allPassed'] and len(coder['results'])==9
tailfacts=[]
for o in coder['originalOwnerFacts']:
 for r in o['records']:
  g=r.get('tailGate')
  if g:
   assert o['failure']=='PROOF_WALL_TIMEOUT_STICKY' and g['writerReturnedAt']<=g['writerJoinObservedBy']<g['deadline']<=g['tailGateReturnedAt']<=r['lastControlledObservationAboutToStartAt'];assert r['sharedProofWindowStart']+1==g['deadline'];assert o['timeoutObservations'][-1]['pendingOriginalThreads']==0
   tailfacts.append({'role':r['id'],'nextId':r['proof']['nextId'],'tailGate':g,'sharedProofWindowStart':r['sharedProofWindowStart'],'lastControlledObservationAboutToStartAt':r['lastControlledObservationAboutToStartAt'],'finalOwnerFailure':o['failure'],'candidateProofNotWriterCloseProof':r['proof']['candidateOnlyWriterCloseNotProven'],'evidenceClassification':'CODER_ORIGINAL_RECEIPT_STATIC_AUDIT_NOT_TESTER_DYNAMIC'})
assert len(tailfacts)==2
save('independent-two-fix-evidence-mapping.json',{'CR2-B01':{'source':'Fixed same ReadAllBytes raw.Length+call count; actual new request/admission/predecessor sums independently verified all7','verdict':'LIMITED_SOURCE_AND_INDEPENDENT_LOCAL_ACCOUNTING_VERIFIED','anchors':[anchor('tools/capture_android02.ps1','$script:requestBodyReadBytes+=[long]$raw.Length'),anchor('tools/capture_android02.ps1','$ownerCurrentReadCost=[long]$ad.admissionWriteBytes+[long]$requestBodyReadBytes')],'independentReads':reads},'CR2-B02':{'source':'Last observe outside fixture gate and after events/digest/next/records, common successful/END path; fixture-only bounded absolute deadline gate separated','verdict':'SOURCE_FIX_AND_CODER_EVIDENCE_VERIFIED_TESTER_DYNAMIC_NOT_RUN','anchors':[anchor('tools/outer_owner.py','self.events.add(event);self.last_proof=digest(pp);self.next+=1'),anchor('tools/outer_owner.py','lastControlledObservationAboutToStartAt'),anchor('tools/outer_owner.py',"self.observe(proof_start,self.proof,'PROOF_WALL_TIMEOUT_STICKY')")],'coderTailFacts':tailfacts},'priorCR_B03':{'verdict':'INDEPENDENT_15_STRICT_POLICY_CASES_PASS','schemaCases':suite['results'][0]['detail']},'priorCR_B01_delta':{'verdict':'INDEPENDENT_THREE_ACTUAL_ENTRY_REJECTIONS_PASS','guards':suite['results'][3]['detail']},'newConfirmedSourceBlockers':[]})
coverage=read(R/'docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE/independent-phase-a32-results.json')['cases'];assert len(coverage)==32
for c in coverage:
 c['priorReady02BStatus']=c.pop('independentStatus');c['independentStatus']='READY03_STATIC_FULL_PACKAGE_REVIEW_WITH_LIMITED_INDEPENDENT_RUNS';c['actualProduction']='NOT_RUN'
 if c['id'] in ['AC12','AC16']:c['independentStatus']='INDEPENDENT_SEVEN_REQUEST_READ_BASE_PLUS_DELTA_END_AND_THREE_REJECTIONS_PASS'
 if c['id']=='AC13':c['independentStatus']='INDEPENDENT_15_STRICT_SCHEMA_CASES_PASS'
 if c['id']=='AC18':c['independentStatus']='SOURCE_FIX_CODER_TAIL_RECORDS_REVIEWED_INDEPENDENT_TIMEOUT_AND_TAIL_NOT_RUN'
 if c['id']=='AC21':c['independentStatus']='SINGLE_SUITE_27_75_SECONDS_STOPPED_NEW_ADMISSION_FIVE_GROUPS_PASS_FIVE_NOT_RUN'
save('independent-phase-a32-results.json',{'cases':coverage,'phaseAUnchanged':True,'no32RuntimePass':True,'projectAfterThisReport':'PAUSED_WAITING_USER','actualSdkDeviceCalls':0})
baseline=[]
for p,expected in [(R/'docs/coder/d1android02-capture-ready02-fix/evidence/ready02-fix-freeze.json','c5ec7bafa461bc6e99ed2790248c67edce92cf11cd4a3e33c72fed54f5b82b1e'),(R/'docs/coder/d1android02-capture-ready01/evidence/capture-ready01-freeze.json','3ff8b42d7bd5c31f578bcfdec8bba7286dd32ba90289fcc6556dc338368fa51d'),(R/'docs/coder/d1media3-android02-fix02/evidence/fix02-freeze.json','39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad'),(R/'docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json','65e8413b3e90dd571c22fea7049778b29c0d94221cd490560cdcd5c3cc00ae5a')]:
 assert sha(p)==expected;d=read(p)
 for x in d['files']:
  q=R/x['path'];assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
 baseline.append({'seal':pin(p),'rows':len(d['files'])})
seal=B/'evidence/ready03-fix-freeze.json'
for x in read(seal)['files']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
save('baseline-and-post-review-preservation.json',{'baselines':baseline,'new225Unchanged':True,'oldUnknownActions':0,'sdkToolFileQueries':0})
req=R/'docs/milestones/D1_ANDROID02_CAPTURE_READY03_FIX_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-and-pause-snapshot.md').write_bytes(req.read_bytes())
save('single-suite-stop-and-pause-record.json',{'suiteOriginalStatus':suite['status'],'elapsedSeconds':27.75,'plannedGroups':10,'completedPassGroups':5,'admissionStopCheck':'SUITE_STOP_NEW_OWNER_26S before overrun Owner/Popen creation','notRun':['partial-save-overrun','outer-live-thread-timeout-sticky','shared-proof-close-window-sticky','timely-writer-late-tail-no-successor','timely-writer-late-tail-END'],'knownProductFailureFromAdmissionStop':False,'actualCaptureControllers':sum(len(o['records']) for o in suite['ownerFacts']),'purePolicyHosts':2,'allEnteredOriginalReturns':all(r['proofWriter']['closeReturned'] and r['outer']['sameOriginalPipeReadersJoined'] and r['outer']['outerStreamsClosed'] and r['outer']['originalWindowsProcessHandleCloseReturned'] for o in suite['ownerFacts'] for r in o['records']),'textObservedAndWritten':115288,'fixtureStdinBytes':6144,'afterStopNewDynamicCalls':0,'oldUnknownActions':0,'sdkDevice5037OccupancyGradleJvmMediaCalls':0,'postReportProjectState':'PAUSED_WAITING_USER','noAutomaticNewBatchFixRegressionOrDeviceActivation':True,'staticPreparationCorrectionsOnly':'Tester static audit preparation quote syntax and old7-versus-current9 coder count adjusted before any own dynamic test; original single dynamic script unchanged after start. No runtime retry.'})
table='\n'.join('| '+x['id']+' | '+str(x['request'])+' | '+str(x['admission'])+' | '+str(x['previousProofNative'])+' | '+str(x['logicalReadTotal'])+' |' for x in reads)
text='''# D1 ANDROID02_CAPTURE_READY03_FIX 最后一次独立整包离线B报告 V1.0

2026-10-21；tester；本轮报告发送后暂停，等待用户通知。

## 结论

**SOURCE_FIXES_VERIFIED_INDEPENDENT_DYNAMIC_INCOMPLETE_PROJECT_PAUSED**。225清单/ZIP226逐内容、全部最小source diff/准确七角色/产品pins/准备态与原证据已核；request同源正文读账修复在独立正常七步验证通过，旧严格schema和delta拒绝缺失目标已补。最后同窗尾段源码修复和开发原时序收据可核，**本轮tester该动态分支NOT_RUN**，不能签完整独立B/采集就绪PASS或设备READY。

本轮唯一独立测试集实际**27.75秒**<30秒：计划10组中**5组通过、其余5组NOT_RUN**。到partial-save-overrun时触发自有26秒新owner准入停止阈值，尚未创建该Owner/Popen；动态summary原样为INCOMPLETE_OR_FAILED。此为测试窗口停止，不是发现候选产品FAIL，也没有隐去未跑项目。未延窗/重领测试集/补跑或强停在途原调用；已进入的9个capture原controller与2个纯政策host均自然返回。没有新增确定源码阻断，但完整动态覆盖缺口仍OPEN。

遵用户“完成手头开发测试后暂停”与本次最后一轮派发：完成本报告并主动发负责人后**项目暂停，等待用户通知**。无论上述有限通过或NOT_RUN，均不自动下一批、修复、回归或设备activation。已接受的产品五项有限关闭及旧FAIL/UNKNOWN不回写，D1未过/M0未启。

## 来源与独立静态全包审

开发报告10348B/SHA301a56c1d341e9d0ca1d6b9d256f9b3b2a4993222ef24e784d414805fe296db3；seal e8750063bec93dec4dcad090b3dabab637816bcb6dea8d57f98302fdf2356b11。独立核225项磁盘size/hash及ZIP bf53714ace7473a2dcb60005b7e906ee60692acb1f64a05b75d1b6dc8cf6b69f 的226唯一成员=225清单+seal，逐集合/大小/hash/解压CRC通过。只读入口bad=[]，自有结束再核225字节不变；未在冻结目录运行写入型自检/生成/冻结。

entry044fe40e340d5818b566dfee94462c7f5420886b22e5ed79f1a5fa4a28db023c；owner9e558b3f6d64d86ea7e8c4326cfb4d88cd261f95198067ff66cfb6ef7f91effb；producer4b0aea7b372f737ae6d0970374d18d491c2f537c741df3fa7166c5ef654e8d5a与READY02同字节。完整entry/owner/producer差异独立保存，仅既有PS读取计量和原owner末观察/有限fixture门等准确适配；未见产品改动、新native helper/通用dispatcher/诊断或多层release框架。

原READY02364/READY01756/FIX02874/RENDER818各seal全行结束hash保全。准确FIX02产品seal39acf773...fbe0ad、app7151481B/f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad、test478124B/b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9、原同证书/版本/runner/三参数/十case不变；不重建/重验签JVM/运行产品。旧35512/48945/17257 UNKNOWN、SDK工具文件/当前server/5037/claim/其他项目占用无查询。引用许可/来源仅沿固定既有审查链，不增加新发行清权结论。

## 两项修复与旧缺失目标裁定

### CR2-B01 同源request读账 — 源码与独立七步通过

ReadJsonExact在原ReadAllBytes返回后仅对准确RequestPath记录raw.Length/调用次数；不是另GetItem估算或新增读取。原ownerCurrentReadCost=admission读+request实际读，进入proofReadBytes/control/总账，写成本另列。独立每角色requestBodyReadCalls=1、原文件长与实际读字段一致，三层之和等proofReadBytes；首步无前驱也正确计入。

| 角色 | request读B | admission读B | 前驱proof/native读B | 同次合计B |
| --- | ---: | ---: | ---: | ---: |
'''+table+'''

数值与coder799等不同来自本审新输出路径/请求长度，不是golden变更；逐原文件/同次读校验才是判据。正常首base15200+实际outer/proof delta2790成功接续，末END仍加2854；末control145529/total147026。没有把request写抵读、每case重领组额或扩大成全OS/source/hash物理IO审计。

### CR2-B02 最后同窗尾段 — 源码修复可核，tester动态未跑

生产与fixture共有的events.add、digest(pp)、last_proof/next/records必要工作之后，在失败/成功return分支之前新增同一proof_start的最后observe，END也走同一点。该observe**在fixture门之外**，不是只让测试分支报错；不把下一role新的proof_start当旧role完成点。受控末观察后仅失败判断/return及解释器调度尾部，不能自证该尾部，保持明确能力边界而不新增无限证明链。

有限CROSS_SAME_DEADLINE_AFTER_TIMELY_WRITER只在OFFLINE_FIXTURE生效且最多2秒；先核原writer已实际及时close/join及failure为空，再使用同一绝对monotonic deadline+0.005的有限Event等待，然后回到共有digest/交接/末observe。生产不运行该延迟门。开发两收据独立静态核：writer返回/已join分别140029.812、140032.109，deadline约140030.750/140033.030，门返140030.765/140033.046，最后点140030.781/140033.078，均满足writer及时→同窗跨界→末点sticky；pending原线程0，与writer超时pending1分开。

这些是**开发原记录审查+源码位置证据**，本轮tester两个尾段目标均NOT_RUN；不以开发9组或旧上轮不确定反例代独立动态证明。该修复可记源码修复，完整独立时间门动态覆盖仍未关。

### 原CR-B03 严格schema及原delta拒绝 — 独立补齐

本轮先运行15个自有同字节RoleSemantic纯政策样本：zero及精确上界两项有限PASS；negative、bool冒整数、string、fraction、over、null、缺budget、非空firstFailure、缺firstFailure、int冒bool、history错类型均拒；另独立重验旧负账+首错组合和body等60秒边界均拒。总15项，均为有限本地政策，不冒实际App输出。

随后在已返回的本审原七步链fixture上运行三类真实entry child前拒绝：reset→OUTER_DELTA_RESET_OR_DUPLICATE，伪native来源→ORIGINAL_OUTER_DELTA_SOURCE_BYTES，重复加delta→OUTER_DELTA_RESET_OR_DUPLICATE。保留原base/native/proof/event/PID/request/raw绑定与原writer返回，负例仅改本审副本，完成恢复原字节；不修改冻结候选或生产scope。旧缺失schema/delta目标已由**自己的结果**补齐，不照抄开发13+3。

## 本轮唯一独立动态集

只在新的tester fixtures目录准备快照，加载准确冻结Owner（-B、无pycache写）并运行固定有限Python producer/受审采集host；生产policy未激活，SDK child0。原controller强引用/wait/readers/stream+Windows handle和原proofwriter事实存于ownerFacts，不拿counter0/文件存在或候选proof自证close。

| 计划组 | 本轮结果 |
| --- | --- |
| 严格schema先行15项 | PASS，纯政策边界/首错/完整history与旧组合均按预期。 |
| PREPARATION owner | PASS，Popen前拒。 |
| 正常七步读账/base+delta/END | PASS；4096+2048同原stdin pin/read/返回、pending/final保全、所有proofwriter关闭后接续、每role读账计一次。 |
| 三类delta原entry拒绝 | PASS，位于所有迟返测试之前完成。 |
| busy实际本地capture | PASS，identity后global_busy原producer→原capture ENV_WAIT；下一app_absence未进入，非历史纯语义重放。 |
| 超额部分保存 | NOT_RUN，准备副本后new Owner准入已到26秒阈值，无该Popen；不照搬旧192/64为本轮。 |
| outer原线程迟返 | NOT_RUN；旧有限通过保持历史，不作当前独立回归。 |
| proof原writer迟返 | NOT_RUN；同上。 |
| 及时writer后尾段/禁止后继 | NOT_RUN，只有本轮源码与开发原记录审查。 |
| 及时writer后尾段/END | NOT_RUN，同上。 |

实际27.75秒，观察/写入115288B<4MiB、模拟stdin6144B<64KiB。9个capture原controller+2个纯政策host均原wait/reader/pipe/handle归还，所有已进入proofwriter均closeReturned；无永久unknown注入、kill/interrupt/取消/二次close/未知retry。触及预设准入停止后没有新增动态调用、没有重跑或延长窗口。summary中第六check的AssertionError('SUITE_STOP_NEW_OWNER_26S')是**脚手架停止新任务**，不是候选超量功能失败；最终测试状态INCOMPLETE_OR_FAILED如实保留，不改allPassed。

静态准备曾修正自有审计生成器引号和旧7组/新9组计数断言，均在动态前，0采集调用；本轮实际自有动态script启动后未改/未重跑。后续读证据/核hash/出报告不属于追加动态验证。

## 七角色、预算与未证能力

计划SHAf0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199逐字不变；identity/global_idle/app_absence/test_absence/install_app/install_test/scope_all，准确HA1Q6WXR/TB138FC/API31未来fresh身份与独立global占用门。两包存在即停，无-r安装，无清数据/卸载/换包/换设备/自动轮询。sole scopeAll/fixture19e815...778a9c/新runId待真实范围另签。

原7op/并发1/无retry与分组预算不扩：preflight1048576、install131072、instrument全部pending-final1048576、controllerproof1048576，总logical inbound3276800；binary7629605+command各4096总28672=logical outbound7658277。实际ADB内部读/wire不可见，不以6144fixture模拟当真实payload传输。240只是七分项观察和，App60，生产outer/localproof/whole实值仍空，上限600/30/600不作强停许可。

proof候选candidateOnlyWriterCloseNotProven=true仍正确保留。writer归还后的尾段可能晚，早落盘approved=true不能自行证明最终timely；同原owner末observe/failure与实际外层返回才决定后继，JSON/hash不认证恶意本地主机。SDK壳exit/App自报worker/mux/source与原outer return不证明Binder/平台finisher尾段，最高有限分类INTERNAL_FINISH_UNPROVEN；真实Android/FD/fsync/Media3/重开duration/独立DTS/播放仍NOT_RUN/UNPROVEN。

全32oracle迁移矩阵保原A状态不变，明确本轮五组通过/其余未跑与开发证据边界；不把32静态映射或开发9组当32 runtime PASS。开发唯一22.891秒整套/9组/source snapshots逐身份核对保全，不能代本轮未覆盖的真实独立回归。没有新确认源码P2不等完整B已经可接受。

## 发送后暂停

本报告、原动态完整/未跑事实、225/ZIP226/最小diff/两项修复证据、全七读账/严格15样本/三拒绝、候选proof与所有原返回、32映射和旧保全一并冻结，发送receipt在证据目录外。有限hash含opaque APK/媒体字节，不冒载荷零读取/全物理IO或倒灌旧资格与设备8MiB账。

报告完成后即**PAUSED_WAITING_USER**。不自动追加未跑验证、修复回归、新批或设备activation；缺失回归与实际平台能力留待用户明确恢复后安排，不以暂停将其补绿或消除。持续平板通用授权保持，但暂停期间不使用；所有旧UNKNOWN原样保管、不强停在途原调用。
'''
REPORT.write_text(text,encoding='utf-8');manifest={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'SOURCE_FIXES_VERIFIED_INDEPENDENT_DYNAMIC_INCOMPLETE_PROJECT_PAUSED','report':REPORT.relative_to(R).as_posix(),'reportBytes':REPORT.stat().st_size,'reportSha256':sha(REPORT),'evidenceFiles':[pin(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json'],'confirmedNewSourceDefects':0,'dynamicPassGroups':5,'dynamicNotRunGroups':5,'suiteSeconds':27.75,'strictPolicyCases':15,'actualDeltaRejections':3,'sdkDeviceJvmMediaCalls':0,'oldUnknownActions':0,'postReportState':'PAUSED_WAITING_USER'};save('review-evidence-manifest.json',manifest);print(json.dumps({'reportBytes':manifest['reportBytes'],'reportSha256':manifest['reportSha256'],'manifestSha256':sha(E/'review-evidence-manifest.json'),'evidenceFiles':len(manifest['evidenceFiles']),'overall':manifest['overall']}))
