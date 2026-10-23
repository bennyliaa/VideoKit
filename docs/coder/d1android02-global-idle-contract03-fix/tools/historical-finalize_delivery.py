"""Freeze exact reviewed artifacts once, retaining all prior local rounds."""
from pathlib import Path
import hashlib,json,zipfile,sys
B=Path(__file__).resolve().parents[1];P=B.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
contract=json.loads((B/'evidence/contract-result.json').read_text());affected=json.loads((B/'evidence/selfcheck-result.json').read_text())
assert contract['allPassed'] and len(contract['results'])==4 and all(x['pass'] for x in affected['results']) and len(affected['results'])==6
assert not affected['retainedRunnerCustody'] and not affected['retainedGateCustody']
seal=sha(B/'reference/runner-source-seal.json');sources=json.loads((B/'reference/runner-source-seal.json').read_text())['sources'];gate=sha(B/'reference/gate-sources.json');plan=sha(B/'reference/exact-seven-role-plan.json')
assert contract['results'][0]['detail']['seal']==seal
for case in affected['cases']:
 p=Path(case['home']).parent/'permit.json'
 if p.exists():
  try:d=json.loads(p.read_text())
  except ValueError:continue
  assert d.get('sourceSeal',{}).get('sha256')==seal
from datetime import datetime,timezone
sys.path.insert(0,str(B/'selfchecks'))
from fixture_inputs import qualification
save(B/'reference/synthetic-qualification-example.json',qualification())
sem=contract['results'][1]['detail'];full=affected['results'][2]['detail'];t=full['terminal'];route=json.loads((B/'reference/fact-plan.json').read_text())
report=f'''# GLOBAL_IDLE_CONTRACT02 完整开发交付 V1.0

2026-10-23；coder；GLOBAL_IDLE_CONTRACT02独立revision02整批交负责人。**已实现可达条件性 PASS 的生产解析与资格接收，开发离线自检通过；独立 B、真实事实采集和现场均 NOT_RUN。D1 未通过，M0 未启动。**

## 生产改动与默认行为

候选目录 `D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02-revision02`。原 COMPAT03与上一001a候选源码均不改写；上一次OWNER_END_TAIL未返回链单独隔离，缺失证据见下文。原14源扩为17：新增专用事实 collector、固定事实 plan、独立本地事实 producer；gate由6扩9，均进入 source/gate/module/loader/许可接收 pins。原14中7项逐字节不变，10项总变化详见 reference/source-delta.json 与 source-delta.patch。Native、runtime、FIX02 APK和产品逻辑不变。

原 RoleSemantic 的 global_idle 分支现在调用被同一 admission module 哈希固定的真正资格解析函数；没有另一套只供测试的放行实现。source seal `{seal}`；gate seal `{gate}`；plan `{plan}`；PS `{sources['tools/capture_android02.ps1']}`；runner `{sources['tools/production_runner.py']}`；Owner `{sources['tools/outer_owner.py']}`。

默认 release/capture-policy.json 仍 PREPARATION_ONLY，globalIdleQualification=null；默认 CLI/缺授权/旧 V2 缺新字段均在启动 SDK 前拒。V2许可标识保留，但精确 schema 增加 globalIdleQualification，旧许可不能复用。Runner先校验准确scope/runId/source seal/plan/review和fixture模式；PS再将policy资格与原批准permit中的完整对象比较，防止物化时替换。新 scope 仍按原公式、独立 planId/runId；无有效 LIVE 许可或现场执行产生。

## 全量语义与可达正例

完整保留 APP/PERS、ProcessRecord token、正有界PID、全部冒号的processName、数字UID和原user token；按100000分解user/appId，绑定各记录自身四空格user/UID/packageList/curProcState。所有顶层头都计数；未知类别、重复PID/token、缺/重复/非法状态、isolated/shared/跨user及归属冲突均阻断。末PERS在Process OOM control等准确分节结束，后续六空格UID-summary不能成为它的状态。

原三类active instrumentation先于所有HOME/系统例外；不合法mInstr/null后缀/未知instrumentation编号拒为未证。唯一resumed与focus必须user/组件/token/task一致，显示分节唯一0；无包名去重。HOME详情Hist与resumed完整身份相同，app=ProcessRecord再与完整进程token/PID/name/user token绑定，自身package/process/component、RESUMED/非finishing/可见状态全部互证。它不批准同包其他弹窗/服务/后缀。

TOP和BOUND_TOP竞争不得由service策略豁免；其他活动服务/重要前台须匹配本次精确已审非竞争系统服务条目。core UID、PERS、OEM前缀、目录、FLAG_SYSTEM或HOME身份不单独授予非竞争许可。普通背景/cache记录本身不等于占用；BACKUP/RECEIVER/TOP_SLEEPING等仍阻断。API31状态20 NONEXISTENT不能作为现存记录的合法当前态。

最终98个开发语义案例全部符合准确预期，其中10个PASS都是明确 OFFLINE_FIXTURE 合成资格（不是新设备事实），包括HOME、精确服务、数字core token和普通cached进程；另有88个拒绝或身份边界案例。tester原45项逐项映射，另53项专门变异，23规则映射 reference/criteria-map.json。它们是开发执行，**不把独立判据文件中的PLANNED_NOT_RUN改成独立验收PASS**。历史388784B原文精确解析68条，缺新资格仍拒；原LIVE03 BLOCKED、proof UNKNOWN、batchAmountUnknown/candidateOnlyWriterCloseNotProven和once均保留。

## 固定官方来源已闭合

tag android-12.0.0_r1 → frameworks/base commit `cebf5c06997b64f4e47a1611edb5f97044509d76`；Permission commit `c11239c07afab2d6093c8efb3fa59328b7389df7`。Gitiles提交JSON与原文/字节/哈希均保留 reference/upstream，最终索引 upstream-source-closure.json。

固定 ProcessStateEnum.aidl SHA `343c60effa4ce83ce42296527bae8bd4341a9da982a670a83b1c86a7ef307881`，实际核0 PERSISTENT、1 PERSISTENT_UI、2 TOP、3 BOUND_TOP、4 FOREGROUND_SERVICE、5 BOUND_FOREGROUND_SERVICE、6 IMPORTANT_FOREGROUND、7 IMPORTANT_BACKGROUND、8 TRANSIENT_BACKGROUND、9 BACKUP、10 SERVICE、11 RECEIVER、12 TOP_SLEEPING、13 HEAVY_WEIGHT、14 HOME、15 LAST_ACTIVITY、16–19四类cache、20 NONEXISTENT；-1 UNKNOWN不准入。不使用main分支推值。

Permission的正确路径是 service/java/com/android/role/RoleShellCommand.java；SHA `6a090980982249b6c1345576354a66d8236f57e39c19b1cba6e1acadc6600cae`。其完整onCommand只有三个变更角色子命令，**没有get-role-holders**。原提案这一项撤销；固定替换为只读 `dumpsys role`。RoleService.dump、RoleUserState.dump与DualDumpOutputStream已取同提交，确定ROLE STATE标题、user_states/roles/holders的单值与数组文法。PackageManagerShellCommand固定提交确认 -s/-U/--user 和 resolve-activity --brief --components 的组件单行输出。DUMP权限拒绝、缺user0、多个HOME holder或角色/组件/UID失配均拒，不查设备help，不fallback。

起初沙箱DNS失败、网页cache失败和错误路径404均是取得方式/定位问题；只读提升后直接取得官方固定提交。完整URL/失败/成功保留fetch-round01–05.json，没有把一次打不开当永久依赖。

## 事实 collector 与信任边界

tools/fact_collector.py 是实际可调用的原进程collector，不是仅有提案：只能由原Owner在已准备、未消费的同进程精确 GateSession 上调用；原gate读取/接收/原Native route及共享claim必须成立。LIVE共享claim仍是 production-runner01/release/cooperative-default-route.lock，不派生新LIVE锁。它验证准确执行authority和批准记录的外部双hash、scope/plan/source/route/时窗；继承宿主环境，七个ADB覆盖项任一存在即拒；不清洗环境、不UAC、不换route。fixture只允许固定本地producer，LIVE不能选择fixture argv。

精确 argv 在 reference/fact-plan.json（SDK绝对路径、-s HA1Q6WXR、shell、完整固定脚本）。内部7个事实查询依次为 model、API、fingerprint、current-user、system packages+UID、dumpsys role、HOME intent component。外围只读date/printf/字符串字节计数负责时标与帧，无临时设备文件、无动态命令/包名插值、无替代查询。

协议GI_FACTS_V1/END；每项GI_ITEM头带id、原status、开始/结束epoch秒、精确UTF8字节数，再按长度取原输出；保留命令末尾换行。每项stderr并入本项输出以保留原status/错误；transport stderr单独计量且必须空。接收器核顺序/字节/严格UTF8/控制字符/status/单项与全项时窗/唯一结束，输出逐项SHA和原内容。设备date精度为秒，另有host monotonic实际耗时，不伪称高精度/原子快照。

实际持有原Popen、两reader线程/原流、wait和原HANDLE，原结果未知时保留所有对象；不kill、不二close、不退款。资格15s；外层30s、归还proof10s、整scope90s；超时只失去资格，仍等待原返回并唯一释放已知资源。collect本身与finish返回都明确 outerControllerReturnStillRequired，不能把函数内marker当控制器自身返回证明。开发fixture已实际执行该collector的固定本地子进程、双流/等待/唯一handle close、原claim释放；没有执行SDK。

资格输入是**负责人据原事实与外部实际返回证明审定的不可变归一化输入**，进入原审批permit哈希。它包含原事实scope、source/plan、原始字节/SHA、route、采集authority/approval、capture receipt和外部return证明hash，及严格原返回字段/时窗；接收器核结构/来源pins/外部review关联，不自行发查询，也不把这些hash当成重新证明旧未知返回的能力。原归档/自写true/自写hash不能替代负责人对原产物的审查。合成示例中的1/2/3/4等hash仅为OFFLINE_FIXTURE测试占位。

完整资格绑定本机HA1Q6WXR/TB138FC/API31/user0、精确fingerprint，identity角色必须与事实指纹一致；HOME为准确package/component/process/user/UID/systemFlag；services每项精确packages/process/user/UID/APP或PERS/state/NONCONTENDING_SYSTEM_SERVICE/firmware/证据hash/factScope/起止有效期/EXACT_SNAPSHOT，缺一或漂移即拒。系统清单仅用于核具体条目的来源，不整表放行；没有默认已批准service。

事实scope与后续七角色scope明确不同，必须由负责人在审查后针对**一个准确targetScope/runId/source seal/plan/review**批准绑定；不自动跨scope复用。采集时刻至有效期最多300s，未来/过期拒，服务条目有效期必须与快照完全一致。七项不是原子快照，角色/组件/UID/user/指纹矛盾不得动态补查或猜通。真正LIVE事实目前没有采集，因而当前真实资格仍未证。

## 执行次序与预算

本交付后的完整次序一次收束：负责人审本包 → 独立整包B → 负责人另派一次准确只读事实scope/authority/approval和原gate/route/claim → 原SDK采集/reader/wait/handle/原Owner返回及原scope完整账本证明 → 负责人据具体包/组件/进程/状态审窄策略 → 生成准确target新scope与资格绑定、重新核时效/source/identity → 原七角色。没有把collector插成第八角色、没有复用LIVE03 once、没有在本包执行现场，也不需要为每个空字段再增加诊断批。

事实独立scope：SDK<=1，并发1/retry0，stdout139264/stderr8192/合计147456B；15/30/10/90s如上。新目标生产scope仍whole600/gate30/checker20/proof10/outer120，4 metadata/7 SDK，并发1/retry0，control1048576、localControl262144、text3276800、payload7629605、command28672。source读取仍原536870912/256，gate source268435456/64；不扩门。资格对象<=16384、permit<=32768，精确角色文本global_idle<=851968。

新资格随原permit/policy物化和原读回累计原control收费，不开免费旁路；17源冷读取与9源gate校验计入既有source账。最终真实PS fixture正链初始control {full['initialControl']}B，post {t['postControlBytes']}B，receiver {t['receiverControlBytes']}B，局部总量 {full['initialControl']+t['postControlBytes']+t['receiverControlBytes']}B <262144；完整END control {t['batchControlBytesKnown']}B <1048576，总logical inbound {t['totalLogicalInboundBytesKnown']}B <3276800。这里只证明本精确完整fixture输入适配；更大合法schema对象仍必须满足同一总预算，超限拒绝，不能扩额。

## 验证、保全与集中交接

最终source seal上的四组collector/语义/源一致性自检全通过（{contract['seconds']:.3f}s），98语义/10合成正例；真实生产RoleSemantic定义的无效UTF8专项拒绝；原入口六组回归全通过（{affected['seconds']:.3f}s）：默认拒、批准/源/scope/schema/预算反例、实体PS七角色/END/once、十一类有限故障（新增精确preStart拒绝）、post-delta生产守卫、物化字节变化拒绝。本修订最终套件自身的原测试工具均已返回，无新保留Runner/Gate custody；这不包含也不关闭上一次001a未返回链。独立B未执行。

有限故障中WRONG_OUTPUT_SOURCE在本次输入下先触发RUNNER_CONTROL_CAP，不冒称已经到达其后source guard；原source/loader/permit篡改另有准确校验。OWNER_END_TAIL仍在7角色后因原proof时窗失去资格，旧candidateOnlyWriterCloseNotProven字段继续保留。

原父候选的早期轮次保留在 `D:/CodexProjects/VideoKit/docs/coder/d1android02-global-idle-contract02`：变量名冲突正例误拒、PID测试同时改两侧造成错误预期、各已通过阶段的源与结果均保留。它们不能代替最终修订的检查。其最终001a套件98语义/collector四组已通过，affected前三组含实体七角色/END通过，故障组在identity阶段未返回；后两组NOT_RUN。该轮不是整包PASS。
+
+### 原未返回链与准确缺失
+
+上一17源/gate9 seal `001a0089ddd9140b7b46cd21c1822579703a1d789062b9bb3b8bed962a226039`，scope `a7036abcb551c826b1367d19eb74dd4ec83a97881f08015868c007a8026a37da`；suite `suite-4effb013d3544d1b94c9c8face11752e` / scenario-OWNER_END_TAIL / actual-home；工具session55065未返回。最后已观察identity capture-halted为ORIGINAL_INITIALIZATION_OR_ADMISSION_FAILED、childPid=null、unknownOrPending=true。没有其receipt/console/外部原controller返回/claim唯一释放完整证明；不能用null PID推定从未Start或已经归还。最后源码顺序揭示一个可导致等待尚未创建pipe的启动前出口，但未取得原调用实际返回，不能据新修复替它补证。
+
+已在负责人允许的本批修订范围将旧源/原once/旧工具记录保留隔离；不再查询该链，不kill、二close、补ACK、退款、改写其文件或运行源。该链不是本次独立新scope验证的前置收尾目标；原隔离记录见reference/isolated-prior-scope.json。
+
+### 本修订的准确未来路径修复
+
+完整调用图见CALL_GRAPH.md。仍是现有原PS控制器和原Owner，不新增捕获框架或进程调度层。原Process构造移入已登记原context；Process构造进入/返回、Start进入/返回/值/成功、Dispose进入/返回/次数分开，raw文件Open进入/返回/未知与Close进入/返回均登记。原输入source与pin hash创建/Dispose也纳入归还判定。
+
+同一个Get-CaptureStartDisposition/Close-KnownPrestartResources被生产PS与固定函数夹具调用。已证Start从未进入且所有相应创建均明确时，同原owner唯一Close自己已打开的raw/source并Dispose原Process，`pipeNeverCreated`/`stdinNeverCreated`明确未创建，不伪造EOF、pipeClose或Wait。`fileCloseCalls`是新增preStart收尾分支的计数；正常已启动路径仍使用原fileCloseEntered/fileClosed一次保护，不把其增量计数0解释为未关闭。Start进入但未建立成功、打开/Close/Dispose未知仍保留原对象，不能因空集合/异常便放行或再次Close。
+
+已静态审所有初始化/准入/runtime/最终启动门/Start异常出口：未拥有context前的批准或格式拒绝不启动SDK；拥有原Process后、0/1/2 raw文件已明确打开的已知拒绝均进入同一收尾；原锁busy/重放准入拒绝关闭自己明确拥有的对象一次；原创建、pin hash或Close未知不归入已知集合；成功Start只走原reader/waiter/pipe路径，不调用preStart收尾。原异步metadata writer仍由原PumpRecords观察/关闭后才出console，不用新marker代替其原返回。
+
+先在无SDK/Native-claim的固定函数/真实原Process与本地文件夹具核0/1/2 raw、输入source、Dispose/Close唯一性，再用固定自有本地子进程证明成功Start分支不会被preStart helper关闭；九类未知状态只做纯状态分类，不真正制造无限UNKNOWN。evidence/prestart-lifetimes.json为实际PS工具返回结果。
+
+本修订第一轮seal5435…ab98的完整affected测试前三组PASS，新增PRESTART_KNOWN_REJECT已真实观察原文件/Process/控制器归还；但END夹具误配10秒，触发原FINITE_TAIL_GATE_TWO_SECONDS_MAX，SDK未进入、原gate唯一释放且pending线程0。该轮故障组FAIL、后两组NOT_RUN，源和报告保留evidence/known-tail-config-failure，不改判。仅将该夹具参数改为原允许的2秒（生产仍原10秒），冻结新源后重跑当前完整套件；并非放大生产预算。最终source seal和全部结果以上文为准。旧scope未重用，动态中不修改已启动的源。

原COMPAT03 source-only seal仍2595222c…0c69；原LIVE03 raw仍388784B / 6eab0a91…96b0，未改原FAIL/UNKNOWN/once，不读/干预旧PID/session/锁。无Git/index/force push、设备ADB/TCP/UI/Gradle/产品APK构建或test_media写入。

完整核验与ZIP回执在同级 `D1_GLOBAL_IDLE_CONTRACT02_FREEZE_RECEIPT_V1.0.json`。本包仅交负责人一次集中审测，不逐问题交tester，不声明设备idle/READY/COMMIT或D1验收通过。
'''
assert sem['total']==98 and sem['positive']==10
(B/'DELIVERY.md').write_text(report,encoding='utf-8',newline='\n');delivery=P/'D1_GLOBAL_IDLE_CONTRACT02_DELIVERY_V1.0.md';delivery.write_text(report,encoding='utf-8',newline='\n')
manifest=B/'reference/freeze-manifest.json';assert not manifest.exists(),'ALREADY_FROZEN'
files=sorted(p for p in B.rglob('*') if p.is_file());rows=[dict(path=p.relative_to(B).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
save(manifest,dict(schema='GLOBAL_IDLE_CONTRACT02_FULL_FREEZE_V1',sourceSealSha256=seal,files=rows))
archive=P/'d1android02-global-idle-contract02-revision02-frozen.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(p for p in B.rglob('*') if p.is_file()):z.write(p,p.relative_to(B).as_posix())
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(rows)+1
 for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'] and sha(B/row['path'])==row['sha256']
 assert z.read('reference/freeze-manifest.json')==manifest.read_bytes()
receipt=dict(schema='GLOBAL_IDLE_CONTRACT02_FREEZE_RECEIPT_V1',deliveryPath=str(delivery),deliverySha256=sha(delivery),candidate=str(B),sourceSealSha256=seal,sourceCount=17,gateSourcesSha256=gate,gateCount=9,planSha256=plan,manifestSha256=sha(manifest),manifestRows=len(rows),archivePath=str(archive),archiveBytes=archive.stat().st_size,archiveSha256=sha(archive),archiveMembers=len(rows)+1,allRowsAndArchiveMembersVerified=True,semanticCases=98,syntheticConditionalPassCases=10,contractGroups=4,affectedRealPSOwnerGroups=6,priorIsolatedScope='a7036abcb551c826b1367d19eb74dd4ec83a97881f08015868c007a8026a37da',priorToolOriginalReturn='UNPROVEN_PRESERVED_NO_QUERY',independentB='NOT_RUN',actualSDKCalls=0,deviceQueries=0,candidateNativeRouteCalls=0,oldRuntimeStateQueries=0,D1='NOT_PASSED',M0='NOT_STARTED')
save(P/'D1_GLOBAL_IDLE_CONTRACT02_FREEZE_RECEIPT_V1.0.json',receipt)
print(json.dumps(receipt,ensure_ascii=False))
