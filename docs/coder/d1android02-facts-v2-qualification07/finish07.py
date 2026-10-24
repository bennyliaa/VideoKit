"""Freeze final REV2 plus immutable failed REV1 and the shared budget audit."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,collections
R=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
decl=load(R/'batch-declaration07.json');revs={};audit=[];logical=[];host=0
for name in ('rev1','rev2'):
 H=R/name;fr=load(R/(name+'-freeze.json'));res=load(H/'evidence/result.json');p=load(H/'reference/plan07.json');W=Path(p['work'])
 assert res['revisionReturnProof']['allOriginalsProven'] and res['auxOriginalsReturned'] and not any(res['custody'].values()) and not res['sourceChanged']
 for e in fr['files']:assert (H/e['path']).stat().st_size==e['bytes'] and sha(H/e['path'])==e['sha256']
 for e in load(H/'reference/profile07.json'):assert sha(H/e['path'])==e['sha256']
 assert all(x['matches'] for x in res['audit']) and len(res['audit'])==len(res['hostPopen'])
 assert all(e['closeReturned'] and not e['readOrWriteAmountUnknown'] for e in res['fileEvents'])
 fa=load(W/'actual-facts-complete-source-audit.json');assert fa['allMatched'] and fa['summary']['sourceReads']==64 and len(fa['rows'])==64 and fa['summary']['sourceBytes']==8998997
 assert sum(x['chargedBytes'] for x in fa['rows'])==fa['summary']['sourceBytes']
 route=[x for x in fa['rows'] if x['kind']=='route-child-reservation'];raw=[x for x in fa['rows'] if x['kind']=='child-reservation'];assert len(route)==len(raw)==1 and raw[0]['chargedBytes']==139264 and route[0]['chargedBytes']==(H/'selfchecks/route_fixture.py').stat().st_size
 products={}
 for label in ('positive','wrong-firmware','receipt-replace'):
  d=load(W/('production-'+label+'.json'));assert d['gateReleased']
  fees=d['runnerSourceFeeEvents'];tickets=[x['ticket'] for x in d['sourceEvents']];probe=d['terminal'].get('sourceBudgetProbe') if d['terminal'] else None;probe_n=len(probe['reads']) if probe else 0
  assert all(x['originalReturned'] for x in fees)
  assert d['runnerSourceReads']==len(fees)+sum(t['reservedReads'] for t in tickets)+probe_n
  assert d['runnerSourceBytes']==sum(x['chargedBytes'] for x in fees)+sum(t['reservedBytes'] for t in tickets)+2*probe_n
  logical.append(dict(revision=name,label=label,runnerSourceBytes=d['runnerSourceBytes'],runnerSourceReads=d['runnerSourceReads'],originalReadFeeEvents=len(fees),permanentTicketBytes=sum(t['reservedBytes'] for t in tickets),permanentTicketReads=sum(t['reservedReads'] for t in tickets),probePermanentRunnerBytes=2*probe_n,probePermanentRunnerReads=probe_n,matched=True,gateSourceBytes=d['gateSourcesBytes'],gateSourceReads=d['gateSourcesReads'],pendingRetained=d['pending'] is not None))
  products[label]=d
 revs[name]=dict(result=res,plan=p,work=str(W),facts=fa,products=products,freeze=fr)
 host+=len(res['hostPopen'])
 audit.append(dict(revision=name,allPassed=res['allPassed'],allOriginalsProven=True,hostPopen=len(res['hostPopen']),hostAuditMatches=len(res['audit']),parentOriginalFileEvents=len(res['fileEvents']),fileClosesReturned=len(res['fileEvents']),sourceAndProfileBad=0,rootBytes=fr['bytes'],batchElapsed=res['batchElapsed']))
assert revs['rev1']['result']['allPassed'] is False and revs['rev2']['result']['allPassed'] is True
assert len(revs['rev2']['result']['groups'])==8 and all(x['status']=='PASS' for x in revs['rev2']['result']['groups'])
assert revs['rev2']['result']['batchElapsed']<320 and decl['totalReadReservation']==1006632960 and host==30
v2=revs['rev2'];H=R/'rev2';W=Path(v2['work']);positive=v2['products']['positive'];wrong=v2['products']['wrong-firmware'];replace=v2['products']['receipt-replace']
assert [r['console']['semantic'] for r in positive['records']]==['PASS','PASS'] and positive['pending'] is None
assert wrong['records'][0]['console']['semantic']=='FACT_IDENTITY_FIRMWARE_DISAGREEMENT' and wrong['pending'] is None
assert replace['error']=='ORIGINAL_RECEIPT_FILE_IDENTITY' and replace['pending'] is not None and not replace['records']
swap=replace['replacement'];assert swap['sameBytes'] and swap['differentId'] and swap['originalRef']['bytes']==swap['replacementRef']['bytes']==4345 and swap['originalRef']['sha256']==swap['replacementRef']['sha256']
assert replace['receiptReads'][0]['readBytes']==0 and replace['receiptReads'][0]['originalCloseReturned'] and replace['receiptReads'][0]['before']['fileId']==swap['replacementRef']['fileId']
assert sha(Path(swap['retained']))==swap['originalRef']['sha256'] and sha(Path(swap['replacementRef']['path']))==swap['originalRef']['sha256']
normal=[]
for r in positive['records']:
 co=r['console'];observed=next(x for x in positive['receiptReads'] if x['role']==r['id'] and x['error'] is None)
 assert observed['expected']==co['receiptRef'] and all(observed['before'][k]==co['receiptRef'][k] for k in ('bytes','volumeId','fileId')) and observed['before']==observed['after'] and observed['originalCloseReturned']
 bound=next(x for x in positive['controlAdmission']['roles'] if x['role']==r['id']);actual=co['recordWriteBytesKnown']+2*co['consoleBytes']+co['proofReadBytes'];assert actual<=bound['localControlBytes']<=65536
 normal.append(dict(role=r['id'],writerRef=co['receiptRef'],originalReceiver=observed,actualLocalControlBytes=actual,admittedLocalControlBytes=bound['localControlBytes'],functionalReadBytes=co['proofReadBytes'],consoleBytes=co['consoleBytes']))
budget=load(W/'budget-result.json');v1=load(W/'v1-result.json');assert budget['complete'] and budget['allPassed'] and len(budget['results'])==18 and all(x['pass'] and x['reason']==x['want'] for x in budget['results']) and budget['realAuthority'] is False
assert len(v1)==346 and all(x['pass'] for x in v1)
up=[]
for row in load(H/'reference/upstream-before.json'):
 root=Path(row['root']);m=load(root/row['manifest']);es=m['files'] if type(m.get('files')) is list else m['entries']
 assert len(es)==row['count'] and sha(root/row['manifest'])==row['sha256']
 for e in es:
  p=Path(e['path']);p=p if p.is_absolute() else root/p;assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 up.append(dict(**row,postBad=0))
Z=R.parent/'d1android02-facts-v2-qualification06/QUALIFICATION06-frozen.zip';assert sha(Z)=='250c98231da3df0ae87e9f99f733e030a15de6d25c0ec8adf4a3531e3e4e4fd5'
with zipfile.ZipFile(Z) as z:
 m=load(R/'rev2/reference/upstream06-zip-audit.json');es=json.loads(z.read('reference/full-manifest.json'))['files'];assert len(es)==132
 for e in es:assert hashlib.sha256(z.read(e['path'])).hexdigest()==e['sha256'] and len(z.read(e['path']))==e['bytes']
final_audit=dict(schema='QUALIFICATION07_TWO_REVISION_POST_RETURN_AUDIT_V1',finalRevision='REV2',finalAllPassed=True,allRevisionsPassed=False,history= audit,logicalSourceCounters=logical,normalWriterToReader=normal,physicalSameBytesReplacement=swap,replacementContentReadBytes=0,replacementPermanentPendingRetained=True,helper18Passed=18,V1Passed=346,hostPopen=30,hostAuditMatches=30,actualGraph=dict(REV1=dict(host=14,factsNested=2,dotNet=0,worker=1,total=17),REV2=dict(host=16,factsNested=2,dotNet=4,worker=1,total=23),combined=40,declaredMaxWithSetup=56,cap=96),batchElapsed= v2['result']['batchElapsed'],readReservation=decl['totalReadReservation'],readCap=decl['readCap'],readInterpretation='Conservative source/control/domain reservation; not total OS/interpreter physical IO measurement',upstream=up,upstream06ZipBad=0,old05Queries=0,newObservedUNKNOWN=0,SDK=0,Git=0,D1='NOT_PASSED',M0='NOT_STARTED')
save(R/'post-return-audit07.json',final_audit)
groups='\n'.join(f"|{x['name']}|{x['status']}|{v2['result']['groups'][i]['status']}|" for i,x in enumerate(revs['rev1']['result']['groups']))
source_table='\n'.join(f"|{x['revision']}/{x['label']}|{x['gateSourceBytes']}/{x['gateSourceReads']}|{x['runnerSourceBytes']}/{x['runnerSourceReads']}|{x['permanentTicketBytes']}/{x['permanentTicketReads']}|{'保留' if x['pendingRetained'] else '无'}|" for x in logical)
normal_table='\n'.join(f"|{x['role']}|{x['writerRef']['bytes']}|{x['writerRef']['volumeId']}/{x['writerRef']['fileId']}|{x['consoleBytes']}|{x['actualLocalControlBytes']}/{x['admittedLocalControlBytes']}|" for x in normal)
report=f'''# QUALIFICATION07 完整集中交付：最终REV2离线功能簇通过

2026-10-24。**最终REV2八组开发自测PASS；REV1原FAIL完整保留，不能写成两版均通过。** 两版按事前batch-declaration07.json的独立目录/seed/新scope及共享360秒、1GiB、16MiB、96进程预算执行。REV1所有原返回证明齐后才启REV2，原scope/once没有重放；REV2通过即停止。此为有限开发候选，待负责人核包后独立整包B，**D1未过/M0未启**。

## 正式授权、吸收A与原件保护

正式单SHA405448bc78b15cd64e4fa3ee66cf8e35a13af58af0e0983168bc9ac3a88d8d0c。批声明SHA{sha(R/'batch-declaration07.json')}，REV1/REV2 UUID5种子及目标scope派生规则、完整23/条件25图和合并预算均在首次执行前声明。只新07目录；REV1源/输入/256文件2280254B在REV2前独立冻结，REV2源/输入/297文件5676697B返回后冻结。

完整静态A在07执行前收到并逐核90项2435522B bad0：报告55cebda03133f2a9669da8b2386376c55ee13c750d28e5e82ca68f8d7dfdb4ca、manifest0a9173fc3f2c654c408d1a75bb4dc239b6a8437ca1f1840f9b4ef002a0c3e48f。原06 ZIP133成员/132项4654998B在新构建和最后审计均bad0。04候选284、tester04 B260、tester05 A28前后逐核bad0。**旧05及tester capture1未查询、未处理；未查session/PID/排他锁/活动输出，不二close/kill/补ACK退款，旧RETURN_UNPROVEN与FAIL保持。**

## 三项缺陷的最终关闭证据

**F01实际收费漏事件：** child raw的原1次/139264B收费改用同一原Gate.source_charge，读前校验完整计划并同时记录phase/kind/path/scope/index/bytes；没有漏收后退款或另造账本。所有语义补丁断言准确命中数，REV2有28个已核源补丁；源码AST扫描17处计数变更，分别登记canonical source_charge、preauth seed、原双权威SourceBudget票据、Runner独立费用、有限probe、原Native unknown保留类，保持原合法预留，不把它们盲塞fact64表。完整actual rows在最终对照拒绝前先持久化分块/summary。

两版实际原facts读取表均**64行/64次/8998997B**，逐行scope/path/kind/index/准确charge与冻结计划完全匹配，实际原读close返回，runtime16是原helper永久预留并标fixedHelperReturned，child预留不假冒逐句柄close实测。既有host独立来源域和PS票据账不混入fact64。finalSource/Runner每个原read与原receipt读新增原计费事件，并与永久票据及probe费用对账，六个目标scope的Runner计数/字节均逐项相等，见post-return-audit07.json。

**route子自读额外义务：** 保留route_fixture.py真实Path(__file__).read_bytes()，在原Popen前由其同原Gate为该准确脚本长度独立永久预留1读；LIVE win32_route自读同样入计划，仅静态模型未执行。为保持原64而不跳校验，将预授权schema完整原UTF8文本并入已有fact_preauth.py必要pin，KEYS从完整required派生，additionalProperties/schema const仍核；不再单列schema Gate读。原容量逻辑/shape已整合的source_budget仍完整保留。最终source30/gate22，必要内容均在现有源hash下，旧schema副本作冻结文档，不是运行时替代校验。RAW64、COMPLETE61、LIVE58义务分别纯重算，不将LIVE静态义务冒作运行。

**F02具名producer pin闭包：** GICollectorSha256准确绑定最终collector，同时核共享V1/V2消费点、factPlan、adapter、origin、capture、Runner、Owner、admission、Gate、固定runtime/helper、Python load_pins等。最终48项具名/费用检查通过，11个PowerShell参考/内联函数逐段一致；未盲替SDK/ABI/历史proof摘要。真实V1 346/346及真实V2生产identity/global、错固件语义拒绝和18 helper展开共同证明当前collector消费点已接通，不能只用manifest自洽代证。

## REV1已知失败与REV2使用条件

REV1最大facts、独立review、18辅助通过；三个生产scope在原PS前置校验因修订目录中的混合斜杠prefix触FIXTURE_ROOT_ONLY，未启动.NET fixture子进程；V1生成器多一层revision目录导致找不到冻结legacy夹具，未构造该helper Capture。准确原状态见rev1/evidence/result.json，不改原FAIL或scope。

REV1原14宿主Popen及全部原文件/线程/claim返回证明齐，new custody全0，revisionReturnProof.allOriginalsProven=true。保留REV1原来源/结果冻结后，才在事前声明的REV2独立根和全新scope修正Windows canonical prefix与两个legacy只读夹具根；追加资源前根比较及实际346输入生成检查。REV2纯61项契约、48项pin/费用、34项模型、PS parser/11内联检查通过后执行。没有为已运行REV1改源冒同次测试，未用第三版。

## REV2原生产链、receipt原身份与反例

最大facts原collector→原Capture全部返回，raw139264B/128系统包，packet193626B；三份独立有限review helper均以新scope返回，realHumanApproval=false。真实原ProductionRunner→Gate→materialize→Owner→完整PS顶层正常identity/global均PASS。错固件scope仅identity返回FACT_IDENTITY_FIRMWARE_DISAGREEMENT，原owner已知拒绝并释放claim，无global后继。

receipt原writer在自己的SafeFileHandle关闭前取准确volume/fileId/大小/固定path，并以原WriteAsync准确bytes计算SHA；原console五字段receiptRef传原Owner。父侧原wait/readers/流/H及原console/native归档返回后，原Runner从自己的原读句柄核相同身份、前后稳定与原SHA，再恢复bindings/readers/input、merge原delta。正常两份原writer/console/reader准确一致：

|角色|原receipt B|volumeId/fileId|原console B|实际局部控制B/准入预留B|
|---|---:|---|---:|---:|
{normal_table}

正例另在同原reader API验证错path/volumeId/fileId/SHA准确拒绝，读取费用永久计入原Runner，原close返回，再接受正确原件。物理替换scope在原controller及原native归档返回后，将原receipt保存在本scope另一路径，以**相同4345B及同SHA {swap['originalRef']['sha256']}**重新创建固定原路径：原fileId {swap['originalRef']['fileId']}，新fileId {swap['replacementRef']['fileId']}，volume均{swap['originalRef']['volumeId']}。原reader返回ORIGINAL_RECEIPT_FILE_IDENTITY，**内容read0B且原close返回**；delta未merge，原永久票据pending保留，原claim已返，无global后继。不是字节已篡改或伪造原归还；pending保留是已知拒绝后的费用权威，不是新资源UNKNOWN。

## 原预算、控制容量与辅助结果

|修订/目标|Gate来源B/次|Runner来源B/次|永久资格票据B/次|pending|
|---|---:|---:|---:|---|
{source_table}

REV2正例原同owner ticket版本0→1，来源实际2+5读的delta各merge一次，新增前驱receipt计入原票据；无重载清零/退款。原Gate仍持有claim时，有限一字节probe到64，第65在内容open前SOURCE_READ_BUDGET拒绝且计数不变，下一角色永久预留亦读前拒绝。Runner256/512MiB界本批未实际到达，边界仍为纯模型。全七角色的完整14次资格来源预留仅静态，不以prefix两角色代完整七角色/设备验收。

完整控制UTF8准入在Runner.validate、consumed/Gate/claim/物化/controller前，独立evidenceRoot通过完整wire同时计入permit/policy，真实物化与准入共用policy/activation构造函数。所有重复功能读、前驱原receipt、原record及两次console都计入原65536/262144/1048576，原8192等局部cap不提高。REV2三scope共享预留251120/251804/251848B均低262144；正常实际局部控制与准入逐项相符（上表）。7189字符独立root候选由同一准入函数纯模型读前拒绝，未证OS/全资格可达、未物化，不能报真实溢出或真实生产负例。

18个辅助case ID/理由逐项可靠持久化，原exit0/stdout/stderr/return先归档再判结果；缺base、类型、scope、重复初始化、同原模块复载不清零、wrong hash/identity按已消耗预算及close返回、cap读前、拒绝后不退款等18/18。helper明确syntheticAuthority=true/realAuthority=false，不冒原生产owner；真实原生产正常票据/delta另有上述证据。V1当前原实现346/346，原输入/结果与原helper归还完整保存。

|组|REV1原结果|REV2最终结果|
|---|---|---|
{groups}

## 合并预算、返回与有限边界

共享时钟到最终返回**189.516秒**<320停新增/360；两版宿主14+16=30原Popen，audit30/30。实际产品图REV1 14宿主+facts内2+.NET0+worker1=17，REV2 16宿主+facts内2+.NET4+worker1=23，共40，低事前50/含setup56及原96；原顺序并发1。Parent原文件事件86+108=194，原close均返回；两个revisionReturnProof含原Gate操作、外层wait/流/H、原writer、源读及线程/claim检查，全部true，新custody全0、无新增观测UNKNOWN。旧05未证仍原样未查询。

两版来源预留448MiB各一份，加setup64MiB为960MiB<1GiB；Parent/Gate/host/PS原来源域按各自权威分列，不把预留冒全系统物理I/O，解释器隐式加载/OS元数据仍未全量测量。固定Owner/runtime与PS额外校验在driverAndModels保守预算内，未更改原Runner/Gate票据域。两版产物各在7MiB内，最终全树含归档≤16MiB，ZIP另核≤1.5MiB。原SourceBudget永久票据不回收未用余量，失败scope均不重放。

SDK/ADB/设备/Native route/TCP/Gradle/媒体/Git操作0；只离线原route fixture，不安装APK，test_media未触及。短读/真实构造/close UNKNOWN仅有限模型，不造真实永久未知；LIVE、设备、完整七角色、真实长路径资格、真实reparse/hardlink攻击及完整所有规划组合未执行。准确最终通过范围为**REV2所列离线完整功能簇**，不代独立B、D1或M0。

最终源权威：source30 {sha(H/'reference/runner-source-seal.json')}；gate22 {sha(H/'reference/gate-sources.json')}；profile64 {sha(H/'reference/profile07.json')}；批计划 {sha(H/'reference/plan07.json')}。runtime_binding.py原2056B/20CRLF/SHA47f9、metadata2593与14依赖保持。完整manifest与ZIP覆盖两版/声明/审计/报告；freeze与通知回执在hash循环外。完成主动完整报负责人，经核后再正式独立整包B。主阶段/指定成熟框架精确许可/Flutter/独立Kit/P0保持。
'''
(R/'DELIVERY.md').write_bytes(report.encode())
exclude={'full-manifest.json','QUALIFICATION07-frozen.zip','freeze-receipt.json','notification-receipt.json'};files=[p for p in sorted(R.rglob('*')) if p.is_file() and p.relative_to(R).as_posix() not in exclude];entries=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
mf=R/'full-manifest.json';save(mf,dict(schema='QUALIFICATION07_COMPLETE_FROZEN_MANIFEST_V1',utc=datetime.now(timezone.utc).isoformat(),files=entries,bytes=sum(e['bytes'] for e in entries),finalRevision='REV2',finalAllPassed=True,allRevisionsPassed=False))
zp=R/'QUALIFICATION07-frozen.zip';assert not zp.exists()
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files+[mf]:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(zp) as z:
 assert len(z.namelist())==len(entries)+1==len(set(z.namelist())) and z.testzip() is None
 for e in entries:assert len(z.read(e['path']))==e['bytes'] and hashlib.sha256(z.read(e['path'])).hexdigest()==e['sha256']
 assert hashlib.sha256(z.read('full-manifest.json')).hexdigest()==sha(mf)
assert zp.stat().st_size<=decl['archiveReservation']
fr=dict(schema='QUALIFICATION07_FREEZE_RECEIPT_V1',status='FINAL_REV2_EIGHT_GROUPS_PASS_REV1_FAIL_PRESERVED',finalAllPassed=True,allRevisionsPassed=False,finalRevision='REV2',reportSha256=sha(R/'DELIVERY.md'),manifestSha256=sha(mf),files=len(entries),unpackedBytes=sum(e['bytes'] for e in entries),zipSha256=sha(zp),zipBytes=zp.stat().st_size,zipMembers=len(entries)+1,zipVerified=True,sourceSealSha256=sha(H/'reference/runner-source-seal.json'),gateSha256=sha(H/'reference/gate-sources.json'),profileSha256=sha(H/'reference/profile07.json'),allNewOriginalsProvenReturned=True,old05ReturnUnprovenUnchanged=True,newObservedUNKNOWN=0,batchElapsed=189.516,hostPopen=30,actualProductGraph=40,readReservation=1006632960,SDK=0,Git=0,D1='NOT_PASSED',M0='NOT_STARTED',receiptOutsideHashCycle=True)
save(R/'freeze-receipt.json',fr);total=sum(p.stat().st_size for p in R.rglob('*') if p.is_file());assert total<16777216;fr.update(entireRootBytes=total,within16MiB=True);save(R/'freeze-receipt.json',fr);print(json.dumps(fr))
