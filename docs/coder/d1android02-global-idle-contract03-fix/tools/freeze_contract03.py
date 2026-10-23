"""Static blocked-delivery freeze only. No candidate functions or subprocesses."""
from pathlib import Path
import hashlib,json,zipfile
B=Path(__file__).resolve().parents[1];P=B.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
source=sha(B/'reference/runner-source-seal.json');gate=sha(B/'reference/gate-sources.json');plan=sha(B/'reference/exact-seven-role-plan.json');proposal=sha(B/'reference/next-readonly-facts-execution-proposal.json')
seal=json.loads((B/'reference/runner-source-seal.json').read_text());g=json.loads((B/'reference/gate-sources.json').read_text());result=json.loads((B/'evidence/batch-result.json').read_text())
assert len(seal['sources'])==17 and len(g['files'])==9
for p,h in seal['sources'].items():assert sha(B/p)==h
for r in g['files']:assert sha(B/r['path'])==r['sha256']
assert result['sourceSealSha256']==source and result['results'][0]['status']=='PASS' and result['results'][1]['status']=='FAIL' and len(result['audit'])==1
assert result['runnerCustody']==0 and result['gateCustody']==0 and not result['cases']
mapping=[
 dict(id='B-R2-01',source='tools/admission_checks.ps1 / tools/semantics.ps1.txt',implementation='Independent suspicious header inventory; broad starred and top-level ProcessRecord/UID records; orphan prefix fields; compare every admitted header and exact summary boundary',execution='NOT_RUN',planned='33 malformed/order cases plus 98/175 preserved inputs'),
 dict(id='B-R2-02',source='tools/admission_checks.ps1 / tools/semantics.ps1.txt',implementation='Whole own-state token; canonical decimal0..19; no decimal/exponent/suffix/leading-zero or duplicate token prefix promotion',execution='NOT_RUN',planned='20 lexical mutations plus all20 canonical states; exact reason checks'),
 dict(id='B-R2-03',source='tools/fact_collector.py',implementation='Exact full argv including argv[0], fixed PY; frozen runtime identity and program bytes/hash before Popen via charged Gate.source_read',execution='PURE_GUARDS_PASS_ONLY_NO_COLLECTOR_OR_POPEN_SUCCESS',planned='Owned collector whole chain NOT_RUN'),
 dict(id='B-R2-04',source='reference/next-readonly-facts-execution-proposal.json',implementation='Current source/gate/collector/factPlan/plan paths and hashes; old bytes explicitly HISTORICAL; authority false',execution='STATIC_FILE_HASH_AUDIT_PASS_ONLY',planned='No authority or live handoff'),
 dict(id='B-R2-05',source='tools/entry_gates.py + production_runner.py + outer_owner.py + PS root binding',implementation='One shared finite fixture predicate; own work and exact new tester fixtures; aliases/prefix/old/namespace roots reject; LIVE claim unchanged',execution='PURE_ROOT_PREDICATE_PASS_ONLY',planned='New tester root real seven/END/once NOT_RUN')]
save(B/'reference/five-defect-map.json',dict(schema='CONTRACT03_FIX_FIVE_DEFECT_MAP_V1',status='SOURCE_IMPLEMENTED_DYNAMIC_REGRESSION_BLOCKED',items=mapping))
report=f'''# GLOBAL_IDLE_CONTRACT03_FIX 源码交付与开发自测阻塞报告 V1.0

2026-10-23；coder；集中交负责人。**本包 BLOCKED / 开发自测未完成，不是可正式派独立B的开发PASS包。** 五项源码修订、新版提案和外部交接静态方案已准备；第一组纯参数检查PASS，第二组因我编写的辅助审计驱动错误FAIL，后续全部NOT_RUN。依据本批原资源规则已停止新增动态，不重试、不补造原返回。D1未通过/M0未启动。

## 派发与准确来源

工作单 D1_GLOBAL_IDLE_CONTRACT03_FIX_CODER_REQUIREMENTS_V1.0.md / SHA `a9f5acbbc24a6d5238be46161471208031c107fa15c8429e0b4ed42d04db54b3`；已读设计/里程碑顶部CONTRACT03块及tester要求。父revision02独立报告SHA `f4d16721f662a714133b7b0368a9ea50dedfe3fb1b60f653949843997c00006f` 的整包FAIL保持，原175项170通过/4错误PASS/1阶段断言失败与所有辅助错误不改；原45/98/17条件正例仅保留原批适用范围。

新目录 `{B}`。原revision02的1140项/ZIP、原001a/session55065及其他旧链均不改写、不查询运行态、不attach/kill/二close/补ACK。冻结旧源只作源码及差异只读输入，不测试浮动源、不操作共享Git/index、test_media或产品。

## 当前源、五项实现及尚未获得的验证

source17 seal `{source}`；gate9 `{gate}`；plan `{plan}`。相对revision02共8项源变化，精确old/new SHA与diff在reference/source-delta.json/.patch。Native/runtime、产品FIX02、既有七角色/预算/once及preStart生命周期函数不扩大或替换；新入口模块全部进入原loader/gate/source/许可pins。

| 缺陷 | 已实现源码 | 本次实际验证边界 |
|---|---|---|
| B-R2-01 | 不再用两套同样窄的header匹配证明完整性。先盘点所有疑似带星记录、顶层ProcessRecord/UID形记录、前置孤立own字段，再逐条与支持头比较；前置/中间/尾段或summary后的不支持形态均未证。支持头固定两空格，记录仍按APP/PERS与准确summary结束 | 当前PS函数未执行。33个新边界及原68样本回归均NOT_RUN；只作静态归档文本盘点68条，不冒称生产解析通过 |
| B-R2-02 | own curProcState取完整非空白token，再核完整规范十进制0..19；不接受16.5/1.5、指数/后缀/前导零/同一行重复字段。非法数字在state解析阶段拒，不以HOME后继拒代替 | 当前PS函数未执行。20个词法变异与20个合法态策略检查NOT_RUN |
| B-R2-03 | validate_fixture_argv严格约束列表类型、七个字符串、完整参数及准确PY程序；verify_fixture_runtime复用已冻结14文件身份，前置核metadata/当前解释器版本架构与程序实际bytes/hash，额外两次source_read计原Gate source界 | 第一组直接候选纯守卫PASS：正确tuple/身份；adb/其他Python/同名/别名/额外/缺失/类型8反例；meta及exe内容变异2反例。错误程序没有实际启动。实际原Gate/collector尚未执行 |
| B-R2-04 | 当前提案绑定本批准确source/gate/collector/factPlan/plan和全部新路径；旧提案原字节改为明确HISTORICAL文件，当前approvedForExecution=false | 六项路径/hash静态复核匹配。factPlan内容与父批相同但路径改变；collector内容已改变，不能沿用父hash。没有生成authority |
| B-R2-05 | 三个Python入口统一调用entry_gates.fixture_root_allowed；PS固定根同步。只允许本候选selfchecks/work的子范围和 D:/CodexProjects/VideoKit/docs/tester/D1_GLOBAL_IDLE_CONTRACT03_FIX_REVIEW_EVIDENCE/fixtures 的新子范围。拒绝越界、相似prefix、点/双点、旧候选、其他drive/命名空间；LIVE原共享claim路径保持 | 纯谓词own/tester正例与6负例PASS；三入口完整构造/新tester根7角色/END/once未执行。不能把谓词通过写成目录整链通过 |

机器可读映射reference/five-defect-map.json。原98与独立175源码oracle保留，新增73项，合计计划346项；包含原独立45与17条件正例，不能以永拒修错PASS。selfchecks/review_semantics.ps1新增准确expectedReason断言。**本次这些语义全部未运行，当前criteria-map统一NOT_RUN，不复制父批PASS。**

## 辅助驱动FAIL、临时资源归还未证及停止边界

批次 `{result['batch']}`，source在启动前已固定。第一组0.016s PASS；第二组请求运行prestart_lifetimes.ps1时，辅助sys.audit钩子把Windows的applicationName=None当成非法程序，又把commandLine字符串当argv数组逐字符读取，抛出 `BATCH_UNAPPROVED_PROGRAM_BEFORE_CREATE`。这是本窗口辅助驱动错误，不是候选argv[0]缺陷回归失败，更不是LIVE绕过。

原工具exec `4e701b`已返回，观察exit_code=1；driver源码请求SystemExit(2)，本回执没有单独观察native driver exit code。原batch结果、audit原样保留，组1 PASS/组2 FAIL/后11组NOT_RUN。实际候选PS/SDK/原Gate/原Owner均未开始，runner/gate custody为0只说明这些候选对象未构造，**不能证明Popen内部临时对象已全部归还**。

固定CPython Lib/subprocess.py SHA `85d29b2bf0249f5436838298c9a60ee93508b1102e9ac43b001f8a7e7ae8f375`显示：1004–1027附近先创建父端流对象；1534 audit在1538 CreateProcess之前；1038–1063异常清理会抑制OSError。因此可以说明此处未进入CreateProcess，但此前管道、DEVNULL/继承句柄可能已经创建，逐项原Close没有本驱动观察证据。保留 `AUXILIARY_TEMPORARY_RESOURCE_RETURN_UNPROVEN`；不因driver退出或空children列表补签临时资源Close，不重开/枚举/二close它们。

原证据evidence/batch-result.json和原scope `selfchecks/work/batch-c45d128d3721` 不改；准确边界补充在evidence/auxiliary-failure-boundary.json，固定runtime源码片段另存reference/runtime-subprocess-audit-closure-excerpt.txt。识别此边界后没有继续candidate函数、Gate/claim、Popen/PS或动态重试，仅做文件/AST/差异/提案与文档静态封存。

selfchecks/profile_guard_v2_static.py只交**未执行草案**：在原Popen构造前校验有限准确argv/profile，Windows audit只记录原applicationName/commandLine，不在已有临时管道后充当参数拒绝层。没有将该草案安装进本次错误驱动，没有生成第二个动态scope或把它写成已验证修复。后续是否选取新准确driver/profile/scope由负责人集中审定。

## 原调用图和所有未到达项

CALL_GRAPH.md区分本次实际参数→辅助构造→停止与未执行的原生产链。原Runner同对象、Gate原checker/claim/reader/wait/handle、原Owner/PS、七角色、END/once、preStart三态/唯一Dispose、原writer/释放路径均保持。此次仅第一组守卫函数执行；preStart13、346语义、原collector、默认/批准/预算反例、完整七角色、11有限故障、PS post/最后Start、物化变化、新tester根全链、精确单字节OWNER_SOURCE_PIN_ENTRY全部NOT_RUN。

单字节追加函数来自原冻结独立exact_append回归，来源preimage/function SHA保留reference/independent-regression-sources.json。它将执行前算局部control界、只给新自有PS副本加1字节，必须精确OWNER_SOURCE_PIN_ENTRY，不接受cap先拒。但本次未到达，原WRONG_OUTPUT_SOURCE先撞cap的覆盖缺口不改绿。

## 当前提案和外部交接静态方案

当前提案SHA `{proposal}`，内容审计evidence/proposal-static-audit.json。无循环顺序为source/gate先定→提案绑定→本full manifest/ZIP最后；独立外部回执不进入本manifest，避免自包含hash循环。历史错误提案、映射、合成示例及旧组装脚本明确标注HISTORICAL，不作为当前执行入口。

EXTERNAL_HANDOFF.md选取一条最小路径：负责人执行前批准专用独立一次性签发者/公钥/隔离密钥托管/固定IPC与scope/nonce，签发者在原Gate.prepare前就绪；prepare后原Owner持有同原对象/claim，送本次原route/proof摘要；独立签发原authority/approval字节和detached signature，固定调用入口核原签名与外部双hash，再在原proof10s/gate30s内接收。不是同调用者写issuer字符串自批；超时/返回未知不走SDK、不换签发者、不retry或ACK，仍保留原对象至原返回。

事实至target最多300s，原target控制器outer120s意味着不能把各局部较短预算相加当作保证。预先准备身份/来源/窄政策证据和target绑定，采集后只核实际事实及原返回，争取Tc+150s前完成审阅并入target；仍须用真实剩余时长附加拒绝新SDK/global_idle或后继重核，过期不补签。独立签发/签名验证/剩余新鲜期附加准入属于待负责人审定的信任入口变化，当前**未实现、未运行、未批准**，没有现场外部往返演示。该方案不扩窗，不创建通用调度框架，不自动放行任何系统服务。

静态封存首轮也保留一项辅助FAIL：复制的revision02原full manifest占用了当前文件名，封存断言在创建ZIP前停止。核原SHA后将原字节明确改名HISTORICAL，再单独生成当前manifest；记录evidence/static-freeze-failure.json。这只是静态包装修正，没有重跑任何动态。

## 预算、保全与集中交接

执行前batch-plan/profile固定：whole360s、320s停止新增case、并发1/retry0，预计235s（父受影响套件175s+collector/语义/纯检查+新根完整链+单字节guard），保守子进程图界75/上限96、source/read总界1GiB、保存16MiB、aux stream1MiB。实际约0.047s即停止，原预算不扩额；原始profile/错误驱动保持，不借第二轮掩盖辅助FAIL。

生产仍17源/gate9；whole600/gate30/checker20/proof10/outer120、metadata4/SDK7，并发1/retry0、localControl262144/control1048576/text3276800/payload7629605/command28672。Gate源268435456/64和Runner源536870912/256保持；fixture程序新增metadata+exe校验112759逻辑字节/2源读属于现有source界，不新增现场查询或控制侧免费通道；整链真实计量尚NOT_RUN。

原revision02报告/manifest/原001a与session55065/所有旧FAIL/UNKNOWN/once原样保全，不读旧动态对象。没有ADB/SDK/Native route/TCP/help/设备/Gradle/媒体或共享Git/index；未签idle/READY/COMMIT。当前不能提交正式B验收或现场，也不以代码提交代验收。按既有授权主动交负责人一份完整源码/五项映射/原返回边界/提案/静态外部方案/独立冻结回执；负责人选择下一准确自测安排，当前不继续动态。
'''
delivery=P/'D1_GLOBAL_IDLE_CONTRACT03_FIX_BLOCKED_DELIVERY_V1.0.md';delivery.write_text(report,encoding='utf-8',newline='\n');(B/'DELIVERY.md').write_text(report,encoding='utf-8',newline='\n')
manifest=B/'reference/freeze-manifest.json';assert not manifest.exists()
files=sorted(p for p in B.rglob('*') if p.is_file());r=[dict(path=p.relative_to(B).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files];save(manifest,dict(schema='CONTRACT03_FIX_BLOCKED_FULL_FREEZE_V1',sourceSealSha256=source,status='BLOCKED_AUXILIARY_RETURN_EVIDENCE_UNPROVEN',files=r))
archive=P/'d1android02-global-idle-contract03-fix-blocked-frozen.zip';assert not archive.exists()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(p for p in B.rglob('*') if p.is_file()):z.write(p,p.relative_to(B).as_posix())
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(r)+1 and len(set(z.namelist()))==len(z.namelist())
 for row in r:assert sha(B/row['path'])==row['sha256'] and hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
 assert z.read('reference/freeze-manifest.json')==manifest.read_bytes()
receipt=dict(schema='CONTRACT03_FIX_BLOCKED_FREEZE_RECEIPT_V1',status='BLOCKED_AUXILIARY_TEMPORARY_RETURN_UNPROVEN',deliveryPath=str(delivery),deliverySha256=sha(delivery),candidate=str(B),sourceSealSha256=source,sourceCount=17,gateSourcesSha256=gate,gateCount=9,planSha256=plan,proposalSha256=proposal,manifestSha256=sha(manifest),manifestRows=len(r),archivePath=str(archive),archiveBytes=archive.stat().st_size,archiveSha256=sha(archive),archiveMembers=len(r)+1,allRowsAndUniqueArchiveMembersVerified=True,sourceChanges=8,pureParameterGroup='PASS',prestartGroup='FAIL_OWN_AUDIT_BEFORE_CREATE_PROCESS',remainingGroupsNotRun=11,plannedSemanticCasesNotRun=346,candidateChildProcessesCreated=0,temporaryPopenResourcesOriginalClose='UNPROVEN_NO_SECOND_CLOSE',newDynamicStopped=True,actualSDK=0,actualNativeRoute=0,oldQueries=0,independentB='NOT_DISPATCHABLE_AS_DEVELOPER_PASS',D1='NOT_PASSED',M0='NOT_STARTED')
save(P/'D1_GLOBAL_IDLE_CONTRACT03_FIX_BLOCKED_FREEZE_RECEIPT_V1.0.json',receipt);print(json.dumps(receipt,ensure_ascii=False))
