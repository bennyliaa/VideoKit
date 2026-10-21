from pathlib import Path
import datetime,hashlib,json
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready01';E=Path(__file__).resolve().parent;A=R/'docs/tester/D1_ANDROID02_CAPTURE_READY01_PHASE_A_EVIDENCE';REPORT=R/'docs/tester/D1_ANDROID02_CAPTURE_READY01_PHASE_B_REVIEW_REPORT_V1.0.md';assert not REPORT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
suite=read(E/'independent-suite-results-final.json');assert suite['status']=='COMPLETE_INDEPENDENT_LOCAL_SUITE' and suite['within30Seconds'] and suite['outerControllers']==14
entry=B/'tools/capture_android02.ps1';lines=entry.read_text().splitlines()
def anchor(fragment,path=entry):
 hits=[k+1 for k,l in enumerate(path.read_text().splitlines()) if fragment in l];assert hits,(fragment,path);return {**pin(path),'line':hits[0],'match':fragment}
findings=[
 {'id':'CR-B01','priority':'P2','title':'后继账强制等于早console，不能计入之后真实outer/proof开销','evidenceType':'SOURCE_PLUS_INDEPENDENT_LOCAL_CHAIN_REJECTION','trigger':'首controller自然返回/两流关闭后，真实写outer-return与completion-proof，再将已知外层写入成本加到下一步control和总前账','facts':'入口要求proof.batchTextChargedBytesKnown及所有batchGroups与早期console完全相等；可信外层若加新增真实成本，会在OUTER_CONSOLE_ORIGINAL_BINDING拒绝；照旧console才能走通。下一步proof/native文件read计量不是此前原writer/outer记录/转发已完成开销全部计量。','independentResult':'完整本地七角色机制链走通，但明确只用co-equal账。第一步console前账11830B；之后outer-return写1404B、proof写974B共新增2378B，实际flush/close后把control/总额各加2378，原入口child前拒绝。本反例不是上限耗尽或实际超量，否定的是完整实际累计账可接续能力。','fix':'同一原返回链显式区分原console计量与可信外层新增已知/未知delta；真实outer/proof/转发/记录按合同计入下一前账/组界，强绑定原controller/receipt/request/source且拒重置或伪造，不能直接放松相等而无来源，也不能把writer实际开销称零。','sourceEvidence':[anchor('$co.batchTextChargedBytesKnown -ne $batchTextBefore'),anchor('GROUP_RESET_OR_FORGED_ACCOUNTING'),anchor('$console.batchGroups.control=[long]$groups.control+$c.recordBytes+2*$console.consoleBytes+$proofReadBytes'),anchor("'batchTextChargedBytesKnown':co['batchTextChargedBytesKnown']",B/'selfchecks/run_checks.py')]},
 {'id':'CR-B02','priority':'P2','title':'outer/proof wall仅字段准入，准确生产外层owner落实仍缺','evidenceType':'STATIC_READINESS_CAPABILITY_GAP_NOT_TIMEOUT_REPRO','trigger':'未来activation填写outerSeconds/localProofSeconds后执行原外层Popen/reader/proof writer，特别外层尾段或proof原write迟返','facts':'outerSeconds只有范围检查，不传入/检查原外Popen或外reader/handle/proofwriter；localAdmissionTimer只检查入口部分prestart，不涵盖稍后独立proof形成/原writer归还。wholeWall与child窗口在入口内有真实门，不能代outer/proof门。包没有准确可供B独立审的生产外层执行合同/实现；仅本地fixture驱动wait/join/写proof，自身也不落实activation outer/proof界。报告已诚实写未来外层还须落实，故不是伪称已测，但当前不能通过完整能力就绪。','independentResult':'本审不伪造生产activation/不SDK，未注入真实外层永久卡死；14本地控制器19.437秒自然返仅证明本次有限返回，不证明未实现字段的期限门。','fix':'最小绑定现有受审原外层owner/证明writer观察合同或实现，准确传递并记录同scope outer/proof起点/末点、严格限额和UNKNOWN sticky；超界保同原引用/流且停后继，无kill/interrupt/重试。保whole/child/proof/outer四层分列，不新造通用平台/多层release。','sourceEvidence':[anchor('$activation.outerSeconds -lt 1'),anchor('$localAdmissionTimer.Elapsed.TotalSeconds -ge $activation.localProofSeconds'),anchor('WHOLE_SCOPE_OBSERVATION_UNKNOWN_NO_TERMINATION'),anchor('code=p.wait()',B/'selfchecks/run_checks.py'),anchor('save(p,d)',B/'selfchecks/run_checks.py')]},
 {'id':'CR-B03','priority':'P2','title':'App回执语义可接受负计量和非空首错的矛盾成功','evidenceType':'SOURCE_PLUS_PURE_LOCAL_FUNCTION_COUNTEREXAMPLE_NOT_ANDROID','trigger':'RoleSemantic scope_all非fixture分支收到其他门看似满足、但scopeInputReserved/outputRequested/outputAttempted均-1且firstFailure非空的有限本地政策样本','facts':'累计三项只做>上界比较，无类型/非负下界；成功语义未检查firstFailure为空。该矛盾回执仍返回PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN，而非UNPROVEN/FAIL。','independentResult':'自有semantic host仅加载冻结同字节RoleSemantic函数，未进入capture/SDK/Android；组合反例返回有限PASS，global未知与包已存在对照均正确拒绝。此次是组合反例，不声称两单项各自独立动态覆盖，也不声称实际FIX02已发出坏回执。','fix':'对接受成功所需实际字段作严格存在/类型/整数/非负且<=界及firstFailure null门，保完整history/owner与UNPROVEN分层；矛盾/缺字段/错类型不可用有限PASS蒙混。补有限正反纯语义与原capture调用链覆盖，不修改已固定产品求绿。','sourceEvidence':[anchor('$p.meter.scopeInputReserved -gt 8388608'),anchor("$p.status -cne 'OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY'"),anchor("return 'PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN'")]}
]
save('concentrated-independent-findings.json',{'overall':'BLOCKED_CAPTURE_READINESS_THREE_P2','findings':findings,'actualSdkOrAndroidReproductions':0,'priorFiveProductFixesNotReopened':True})
roles=read(A/'seven-role-independent-oracles.json')['roles'];cross=read(A/'cross-role-admission-capture-budget-oracles.json')['oracles'];assert len(roles)+len(cross)==32
coverage=[]
for r in roles:coverage.append({'id':r['id'],'oracle':r,'independentStatus':'STATIC_EXACT_PLAN_AND_LOCAL_CAPTURE_FIXTURE_REPRESENTATIVE_PASS','actualProduction':'NOT_RUN','limitations':'Own seven-step local fixture chain; real APK installs/current idle/actual media/finish not executed. Complete whole accounting blocked CR-B01; external wall blocked CR-B02; scope receipt guard CR-B03.'})
dynamic={'AC01','AC02','AC03','AC05','AC07','AC09','AC10','AC11','AC19','AC20','AC21','AC22'}
blocked={'AC12':'CR-B01 external cumulative accounting/proof-writer lifecycle gap','AC13':'CR-B03 contradictory receipt semantic accepted','AC16':'CR-B01 full outer control/proof cost cannot be admitted','AC18':'CR-B02 outer/proof wall not implemented'}
for c in cross:
 status='SOURCE_REVIEWED_PLATFORM_OR_NEW_BINDING_NOT_RUN';note='Static contract only; no production activation/current route/SDK/device.'
 if c['id'] in dynamic:status='SOURCE_PLUS_LIMITED_INDEPENDENT_LOCAL_COVERAGE';note='Refer seven fixture-group details; not complete branch/real permanent fault coverage.'
 if c['id'] in blocked:status='BLOCKED';note=blocked[c['id']]
 if c['id']=='AC04':note='Entry/plan/product/schema hash binds source; accepted JSON from trusted external owner is not malicious-host authentication; complete external budgets/wall still blocked.'
 if c['id']=='AC06':note='Fixed route/claim contract and HISTORICAL_NOT_FRESH retained; actual fresh checker/claim/device routing not queried and not supplied as execution-ready.'
 coverage.append({'id':c['id'],'oracle':c['oracle'],'independentStatus':status,'notes':note,'actualProduction':'NOT_RUN'})
save('independent-phase-a32-results.json',{'cases':coverage,'phaseAReportUnchanged':True,'originalAStatus':'PREPARED_NOT_RUN','candidateCannotClaim32RuntimePass':True,'sdkDeviceActions':0})
baseline=[]
for path,expected in [(R/'docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json','65e8413b3e90dd571c22fea7049778b29c0d94221cd490560cdcd5c3cc00ae5a'),(R/'docs/coder/d1media3-android02-fix02/evidence/fix02-freeze.json','39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad')]:
 assert sha(path)==expected;d=read(path)
 for x in d['files']:
  p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
 baseline.append({'seal':pin(path),'rows':len(d['files'])})
am=A/'phase-a-evidence-manifest.json';av=read(am)
for x in av['evidenceFiles']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
save('independent-baseline-post-audit.json',{'baselines':baseline,'stageA':pin(am),'oldUnknownActions':0,'actualSdkFilesRead':False})
seal=B/'evidence/capture-ready01-freeze.json';rows=read(seal)['files']
for x in rows:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
first=read(E/'fixtures/independent-001/whole-seven/proof-writer-identity.json');assert first['proofWriteBytes']==974 and first['outerReturnRecordWriteBytes']==1404
save('read-and-test-process-ledger.json',{'firstSetupOnlyFailure':'sha(PY) received str when helper expected Path. Before any host/producer/process launched; retained failed setup script/summary and6KiB prepared but not injected input. Fixed path conversion in new independent output snapshot; no unknown invocation retried.','actualCompleteSuite':pin(E/'independent-suite-results-final.json'),'actualSuiteSeconds':suite['elapsedSeconds'],'outerControllers':14,'completeGroups':7,'totalOuterTextBytes':48166,'producerStdinPayloadBytes':6144,'extraSemanticCounterexampleBytes':(E/'fixtures/independent-001/semantic-owner/outputs/production-like-receipt.txt').stat().st_size,'fixturePayloadLimit':65536,'selfcheckTextLimit':4194304,'failedSetupAndFinalPreparedFixtureBytesTotal':12288,'allActualOriginalPopenWaitReaderStreamHandleReturns':True,'killInterruptRetry':0,'newSdkDevice5037OccupancyGradleJvmMediaCalls':0,'oldUnknownActions':0,'identityReadScope':'All frozen756hash/ZIP757 bytes and explicit prior818/874 seal rows, including opaque assets/APKs in baseline hashes; no media parser, not zero payload reads or physical disk IO ledger','frozenCandidateUnchangedAfter':True})
ftext='\n\n'.join('### '+f['id']+' / '+f['priority']+' — '+f['title']+'\n\n类型：'+f['evidenceType']+'；真实SDK/Android复现0。\n\n触发：'+f['trigger']+'。\n\n证据：'+f['facts']+'\n\n独立结果：'+f['independentResult']+'\n\n集中修复：'+f['fix']+'\n\n准确冻结来源：'+'；'.join(a['path']+':'+str(a['line'])+'（SHA '+a['sha256']+'）' for a in f['sourceEvidence'])+'。' for f in findings)
text='''# D1 ANDROID02_CAPTURE_READY01 独立完整离线阶段B复审 V1.0

2026-10-21；tester；新完整冻结采集工具，非设备activation。

## 结论

**BLOCKED_CAPTURE_READINESS_THREE_P2**。756文件/ZIP757唯一成员及源计划/策略/产品身份核通过；独立本地完整集**19.437秒、14原控制器串行、7检查组完成**，包括完整七步假采集、实际本地busy capture停止、负例与迟返/关闭在途。三项P2集中回交：**CR-B01 完整真实outer/proof开销不能接续前账；CR-B02 outer/proof wall字段缺准确原外层实现/合同；CR-B03 矛盾App回执负账与非空首错仍获有限PASS**。

本地套件“检查完成”不等候选通过；其中两组用预期反例明确复现政策缺口。CR-B01是原入口本地链拒绝复现，CR-B03是纯函数本地政策反例，CR-B02是静态就绪能力缺口；真实SDK/Android复现均0。当前不签完整capture准备PASS/执行READY，更无实际Android/FD/Media3/平台finish/DTS/播放/隔离/COMMIT/D1通过，M0未启。已接受的FIX02五项产品源码有限关闭保持，不把新工具问题倒写产品或原报告。

## 准确来源、字节与最小差异

完整coder报告11004B/SHA95a1f12c3b076252e6e091d5439e436bb4b1c6b9f684821e4a8652693c88adb7；seal3ff8b42d7bd5c31f578bcfdec8bba7286dd32ba90289fcc6556dc338368fa51d，独立核**756磁盘清单项**；ZIP1498268B/SHAfff52949e2af361321cc80820d4fce38d67ab8cf6559a42301959abbd369663e，**757唯一成员=756清单+seal**，逐集合/大小/hash/实际解压CRC核。不是把756/757差异当漏文件，亦不是只采负责人计数。

冻结纯Python verify_frozen入口只读核bad=[]；自有独立材料/源/历史/全ZIP审再核及结束清单hash均相符。入口fce2d454eb036c6278f71b77393656473af3b35dfe16516cb8358bb6e933bc13；planf0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199；默认policy4158e2065ee89fc54d795ae5b03a262926137c48fd5ee5d21601cce96c70e13a；固定producerb281c18e3873fa1c9ba139a581659212e0708fd9006776cd33838a35dfd433ed。本审只写独立tester目录，不运行冻结derive/freeze/selfcheck写入脚本。

独立原RENDER入口→新入口完整diff已存，原Process/async双流/原输入FileStream/raw文件/metadata writer/独占锁/UNKNOWN持有结构保持；新增精确七角色/新产品pins/语义/前驱组账/90秒1MiB，未见产品改动、native helper/通用dispatcher或多层release实现。声明保留机制不等新增外层wall/计量已经闭合，详三问题。独立重核旧capture818/FIX02874各原seal全部列项和阶段A7份证据不变；没有旧UNKNOWN动作、旧进程/handle/SDK/5037查询。

产品seal39acf773...fbe0ad、app7151481B/f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad、test478124B/b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9、原同证书/版本FIX02/准确runner/三参数/十case源身份一致；未重新编译/验签JVM或运行产品。许可与来源仅沿既有受审工具/产品固定链，不声明新清权；引用historical route/claim显式NOT_FRESH不冒当前事实。

## 七角色与预算静态核

精确argv固定HA1Q6WXR，identity→global_idle→app_absence→test_absence→install_app→install_test→scope_all；global同一有界复合shell只dumpsys activity processes+activities，非额外SDK。presence仅准确包查询，install固定-t --no-streaming且无-r，实际包存在则停。scope_all一次instrument/固定scopeAll+fixture19e815...778a9c+新runId，不能拆十次或任意shell/URI/方法。

四preflight角色上界65536+851968+65536+65536=1048576；两install各65536合131072；instrument所有pending-final双流1048576；controllerproof1048576，总logical inbound3276800。SDK最大7/并发1/无retry；binary出站7629605、command每op4096总28672、logical outbound7658277。所有组静态求和正确，先序cap检查确实存在；**完整实际outer/proof成本可计接续仍因CR-B01阻断**，不能用静态算术或假producer7步内部账掩盖。

固定read-locked产品APK在child前length/hash准入与出站承诺，源pin读取、stdin、SDK内部file读和wire framing分列。实际SDK按路径二次读/ADB协议字节不可见，只能NOT_MEASURED/UNPROVEN；本地6144B输入模拟不是7629605B真实安装。不能证明必需捕获能力则首SDK前BLOCKED。

默认PREPARATION_ONLY在request/原context前拒，activation模板approved=false和真实scope/runId/toolCandidate/B/freshRoute/initialproof/wall均未赋值。源码确有entry/plan/product/request/前驱原PID/raw/console/proof哈希与语义绑定，旧scope及重放/halting拒绝；它依赖可信外层真实owner，不宣称防恶意本地主机伪造。现有fresh route/claim checker未在本包运行或作为当前事实提供，不据历史资料启动；仍须后续准确范围单独绑定。

## 开发自检历史准确分层

独立核四原summary，前三轮26.156/26.843/26.906秒allPassed=false，不能并成通过；它们缺完整原脚手架源快照，只能保留历史失败/局部返回。最终18.453秒、13原controller/11producer、7组、outer文本44156/模拟stdin6144B，完整当前脚手架与源pins一致。默认工具/producer从这些轮次hash未变不意味着历史脚手架全等。

最终busy组是**PURE_LOCAL_SEMANTIC_ONLY的既有本地raw重放**，不是当前最终整集端到端忙碌拒后继，更不是设备fresh idle。本审额外在自己的新scope用原producer→实际采集host完整identity+global_busy，观察到ENV_WAIT、halt和全部原返回；没有为假授权再消费后继SDK/真实设备，下一角色未进入。历史伪true proof拒绝与本审未执行分支分别保持，不把它算成当前完整动态。

## 自有有限独立本地执行

一次实际完整集**19.437秒**<30秒、串行14个原PowerShell控制器（7正常链+2busy链+1合并六guard+1纯语义+3超额/门）、12次固定producer开始；原14个Popen wait/两原reader join/pipe close/Windows handle close自然返回。总外层stdout+stderr **48166B**<4MiB；实际模拟producer stdin **6144B**，另自有小纯语义回执样本长度单列读量账，均远小于64KiB。未执行原349102B stdin，无SDK/设备/5037/占用查询/Gradle/JVM/共享缓存/媒体/native/旧UNKNOWN或kill/interrupt/未知重试。

| 独立组 | 原观察与边界 |
| --- | --- |
| 完整七角色本地链 | 各原captureQualified/原return通过，模拟安装4096+2048B同源pin/read/stdin返回，instrument保存STATUS与RESULT完整raw。末组内部counter preflight593/install250/instrument634/control98677/payload6144/command2651；仅内部co-equal机制链，不是全部outer实际开销已闭。 |
| 本地完整busy capture | 同原identity后global_busy，ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED/exit2/halt；下一app_absence未进入。非纯重放，非设备空闲。 |
| 六child前guard | PREPARE且request缺失、入口pin、fixture伪SDK、duplicate JSON、第8角色均拒；加入真实outer/proof2378B的正确累计被OUTER_CONSOLE_ORIGINAL_BINDING拒，构成CR-B01。 |
| 纯语义正反 | GLOBAL未知/包已存在正确拒绝；非fixture风格回执含三项-1和非空firstFailure却有限PASS，构成CR-B03，不冒真实App数据。 |
| 80B文本超额 | 原read192B、saved64B，明确失败/停后继；是部分保存，不假称完整raw或裁为80B合格。 |
| 有限late原返 | 资格0.3秒后halt时同原controller仍在；只释放自身fixture门、原返回28B，超时首错保持/exit2不升级。 |
| raw文件close在途 | 0.3秒过界同原controller仍持有；只放自身gate后105B原read/save/close归还，仍保持超时失败。 |

7组均完成指测试自身断言成立，**不代表缺陷反例返回值是正确功能**。异常/超额/raw保存prefix与实际读/unknown分列，未制造永久系统I/O故障；未覆盖的branch由源码/NOT_RUN标明，不扩大真实producer/reader永久unknown已测。外层+proof writer成本的自有receipt和负例已存，下一原前账不得仅抄console。

## 集中三项问题

'''+ftext+'''

## 32oracle结果与未证能力

independent-phase-a32-results.json逐七角色和AC01–25给静态、有限独立动态、BLOCKED或新绑定未运行。AC12/16因完整outer/control账阻断，AC18因outer/proofwall缺能力，AC13因成功回执语义弱门阻断；其他静态哈希/计划/拒绝或有限门通过不合并成32 runtime PASS，也不回写原阶段A PREPARED_NOT_RUN。

四15+两45+90=240秒仍分项和；入口wholeWall/child观测有真实检查，localAdmission只覆盖自己的前置部分，outer/proof界仍需CR-B02。限额不能变kill许可，超窗只能关闭新准入并保同原引用/流、未知量/返回sticky，不能二reader/二close/强关流/force-stop/重启server/另SDKretry。

本工具最终最高有限分类内部finish仍UNPROVEN；App自报source/worker/mux零数和SDK壳exit并不证明finisher平台/Binder尾段。真实Android安装、占用格式、nativeFD/fsync、Media3/重开duration/独立DTS/外finish均未跑。持续平板授权保持，无需再问一般许可；当前工具B不能自动activation或连续ADB等空闲。

## 过程、保全与交接

首次自有driver准备阶段把Python路径字符串传给仅接Path的sha函数，**0控制器/0producer**即退出；失败setup源码/summary及准备但未注入6KiB文件保留。改为Path(p)并在独立新输出快照开始唯一实际完整集；没有对任何UNKNOWN/已启动调用重试。所有本审原调用都已自然返回，无遗留同原controller需要处置，不据此宣称全host idle。

原冻结目录/756/sealZIP、旧818/FIX02874/阶段A报告证据结束再核不变。有限hash/ZIP/baseline APK与资产opaque读含媒体字节，不声称payload零读或物理IO精确，也不倒灌旧资格/设备8MiB账。本报告/完整三缺陷/32覆盖/独立本地所有原源、请求、raw、流、owner、proof及实际读量、全部历史分层冻结后一次交负责人；发送receipt目录外，发送后不修改。不逐问题派修、不自动后续测试，由负责人整批组织修复/完整新包再审。
'''
REPORT.write_text(text,encoding='utf-8');manifest={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'BLOCKED_CAPTURE_READINESS_THREE_P2','report':REPORT.relative_to(R).as_posix(),'reportBytes':REPORT.stat().st_size,'reportSha256':sha(REPORT),'evidenceFiles':[pin(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json'],'independentCompleteSuiteSeconds':suite['elapsedSeconds'],'independentGroups':7,'outerControllers':14,'findings':[f['id'] for f in findings],'sdkDeviceJvmMediaCalls':0,'oldUnknownActions':0};save('review-evidence-manifest.json',manifest);print(json.dumps({'reportBytes':manifest['reportBytes'],'reportSha256':manifest['reportSha256'],'manifestSha256':sha(E/'review-evidence-manifest.json'),'evidenceFiles':len(manifest['evidenceFiles']),'overall':manifest['overall']}))
