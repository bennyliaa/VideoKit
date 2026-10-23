"""Static post-return freeze, no candidate import/call/process or old-object query."""
from pathlib import Path
import json,hashlib,zipfile,ast,difflib
H=Path(__file__).resolve().parent;C=H.parent/'d1android02-readonly-facts-preauth01'
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(p):return sha(p.read_bytes())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
r=json.loads((H/'evidence/result.json').read_bytes());profile=json.loads((H/'reference/profile.json').read_bytes());plan=json.loads((H/'reference/batch-plan.json').read_bytes());pre=json.loads((H/'evidence/pure-preflight.json').read_bytes());recovery=json.loads((H/'evidence/artifact-destination-recovery.json').read_bytes())
assert r['allPassed'] and len(r['results'])==7 and all(x['status']=='PASS' for x in r['results'])
assert r['auxOriginalsReturned'] and r['auxCustody']==r['gateCustody']==r['factCustody']==0 and not r['stopNew'] and not r['sourcePinsChanged'] and len(r['calls'])==len(r['audit'])==10 and all(x['matches'] for x in r['audit'])
old=json.loads((C/'reference/full-manifest.json').read_bytes());oldbad=[x['path'] for x in old['files'] if digest(C/x['path'])!=x['sha256']];assert not oldbad and len(old['files'])==56
seal=json.loads((C/'reference/runner-source-seal.json').read_bytes());gate=json.loads((C/'reference/gate-sources.json').read_bytes())
for rel,h in seal['sources'].items():assert digest(C/rel)==h
for row in gate['files']:assert digest(C/row['path'])==row['sha256']
for key,h in profile['scriptPins'].items():
 ns,rel=key.split('/',1);assert digest((C if ns=='candidate' else H)/rel)==h
W=Path(plan['driverOutput']);owned=Path(plan['candidateOwnedOutput']);assert owned.is_relative_to(C/'selfchecks/work') and owned.name=='selfcheck02-'+plan['batch'][:12]
observations=[json.loads((p/'observation.json').read_bytes()) for p in sorted(W.glob('aux-*'))];assert len(observations)==6 and all(x['returned'] and x['failure'] is None and x['facts']['handleCloseReturned'] and x['facts']['streamsClosed'] and x['facts']['readersJoined'] and x['facts']['originalWaitReturned'] for x in observations)
assert all(x['elapsed']<5 for x in observations[:3])
cli=r['results'][6]['detail'];assert len(cli['fixtureConstructorCalls'])==2 and all(x['matches'] for x in cli['fixtureAudit']) and cli['qualificationIssued'] is False
snap=[]
for p in sorted(owned.rglob('*')):
 if not p.is_file():continue
 raw=p.read_bytes();dest=H/'evidence/returned-candidate-scope'/p.relative_to(owned);dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(raw);assert dest.read_bytes()==raw
 snap.append(dict(original=str(p),snapshot=dest.relative_to(H).as_posix(),bytes=len(raw),sha256=sha(raw)))
save(H/'evidence/returned-scope-manifest.json',dict(schema='SELFCHECK02_RETURNED_SCOPE_SNAPSHOT_V1',scopeRoot=str(owned),onlyCurrentNewKnownReturnedScopes=True,files=snap))
save(H/'evidence/post-audit.json',dict(old56BadBeforeDynamic=[],old56BadAtFinalArtifactWrite=['evidence/result.json'],old56BadAfterExactZipRecovery=oldbad,source20Bad=0,gate12Bad=0,preFrozen41PinsBad=0,parentPopen=10,parentAuditMatches=10,nestedCliPopen=2,nestedCliAuditMatches=2,additionalPinnedPSPrestartDotNetChild=1,actualProcessGraphTotal=13,plannedPopenTuples=12,graphEstimateOmittedDotNetChild=True,cap96NotExceeded=True,allSixAuxOriginalsReturned=True,qualificationElapsedSeconds=[x['elapsed'] for x in observations[:3]],actualSDK=0,actualNativeRoute=0,oldQueries=0))
worker=(H/'worker.py').read_text();draft=worker.replace("B/'evidence/","H/'evidence/")
assert draft!=worker and "B/'evidence/" not in draft and "B/'evidence'" not in draft
compile(draft,'STATIC_DRAFT_NOT_EXECUTED','exec')
(H/'reference/worker-output-routing-static-draft.py.txt').write_text(draft,encoding='utf-8',newline='\n')
(H/'reference/worker-output-routing-static-draft.patch').write_text(''.join(difflib.unified_diff(worker.splitlines(True),draft.splitlines(True),fromfile='frozen-runtime-worker.py',tofile='UNEXECUTED-output-routing-draft.py')),encoding='utf-8')
source=digest(C/'reference/runner-source-seal.json');gs=digest(C/'reference/gate-sources.json');ph=digest(H/'reference/profile.json');rawsha=digest(H/'evidence/result.json')
groups='\n'.join('| '+x['name']+' | '+x['status']+' | '+format(x['seconds'],'.3f')+' |' for x in r['results'])
report=f'''# PREAUTH01_SELFCHECK02 完整集中验证交付

2026-10-23；coder集中交负责人。**功能执行七组PASS；整包保留辅助证据写入缺陷，不报完全无缺陷的开发全绿。** 本批一次实际资格及功能执行已原工具返回，没有补跑。D1未通过/M0未启。

## 准确范围与身份

工作单docs/coder/D1_PREAUTH01_SELFCHECK02_CODER_REQUIREMENTS_V1.0.md；负责人01a107c3-2bf9-7fa0-94a0-234258ca6774正式派发，允许无Popen/Capture/Gate/claim/once时自行纯预检修正。共享协调三文档保持原快照，未改Git/index或tester材料。

候选原目录`{C}`，source20 `{source}`，gate12 `{gs}`，plan仍b2802b659ef1b7d1f99938b36248373da41dc0e0faffffc9da001d45a4de26c8。原20源码与12gate条目始终未修改。新driverRoot `{H}`；最终profile `{ph}`；实际原结果SHA `{rawsha}`。

候选自身Gate只接受其既定selfchecks/work子根，故本轮三个全新已固定scope的原输出位于`{owned}`；未通过改源放宽根。新helper/profile/驱动输出位于`{W}`。这些是新对象、新scope，不是旧失败scope续跑。原新scope已归还后逐字快照{len(snap)}文件至evidence/returned-candidate-scope，原路径/bytes/hash映射独立保存，不读旧未知锁或进程。

## 驱动纯一致性与最终冻结

source_key/relative_key/resolve_key/pin_map由profile生产和Registry消费共同使用，内部唯一相对POSIX键带candidate或driver命名空间；实际程序/脚本/参数/cwd/env/stream守卫仍准确匹配，不接受任意路径。

原31个helper/source项完整生成→读取→反解路径→内容hash往返全部通过；新profile共41项。12次预定Popen调用（10种唯一完整元组）在实际资格之前全部纯正例通过，错误程序/额外参数/错误cwd/env逐调用拒绝，重复/大小写碰撞、绝对/点/双点/空段/反斜杠/越界和错误内容hash拒绝。None applicationName及完整Windows命令行字符串的纯审计模型通过，实际审计只观察，无回调拒绝/IO。

纯revision01也保留：当时12tuple已通过，后静态发现group evidence目的根还指候选，尚无任何实际Popen/Capture/Gate/claim/once，按本工作单授权自行修正并重新生成新scope/输入/profile；revisions/pure-01含原helper/profile/输入及说明。最终实际执行前41源、scope/plan/run/nonce、合成template/policy和准确完整tuple重新固定；不得把纯修正计成SDK/once重试。

## 一次实际执行结果

工具exec `28fef9`启动本次最终prepare+worker，session33811仅本次自有调用；原wait `7badee`返回exit_code=0。worker {r['seconds']:.3f}s，无320秒后新增或360秒越界，无第二次调用/暖机/旧scope重放。

| 组 | 原执行结果 | 秒 |
|---|---|---|
{groups}

三次实际资格Python0、Python7、PS0：{observations[0]['elapsed']:.3f}/{observations[1]['elapsed']:.3f}/{observations[2]['elapsed']:.3f}秒，均自然小于5秒。0/7/0原exit已见；非零7为KNOWN_NONZERO_FAIL，资源仍正常原返回。原H身份来自该Popen原handle，原wait/readers/streams/H唯一归还；不是空集合或进程退出推定。

模板组138反例、1纯正例通过：全字段删除/null、额外/大小写重复、外部hash缺失/错误、caller修改模板沿用原批准hash、源/policy/预算整数布尔浮点/SDK设备/query顺序与内容、过期/未来/超90秒/逆序、模式/来源/nonce/plan/run/home及非原Gate/owner模型/同scope-plan-run-nonce重放拒绝。负例未实际启动错误程序或制造未知Start/close。

346语义原98+独立175+新73，全部符合expected及有定义的准确reason；原45矩阵与17独立条件正例通过，总42条件PASS，历史68记录保留不放行。preStart13包括三个真实创建未Start的唯一收尾、纯未知状态模型及一个固定Python的实际Start/原返回；真实未知0。

新预授权原Gate→binding→固定producer：scope `4cd144e4f73898f805dcb5901b5da6a4cd69b68d80f7f773a6690bf30bf55e67`，真实同原Gate/claim/receiver，事实stdout532/stderr0，七项解析成功。43个binding字段删改/重复绑定/消费后接收/唯一release检查通过。receipt为GLOBAL_IDLE_FACT_CAPTURE_V2，准确authorizationKind/externalPreauthSha256/runtimeBindingSha256，无legacy authority/approval字段；proof、source、owner与原capture/释放均及时。

旧V1原正例scope `f0aeffb9020c302f027c44023f052cc255ce8b467ce5031dac35c6e018ac035d`，外部authority/approval双hash错配和同capture重放准确拒绝；V1回执仍使用原字段。新CLI scope `b1b0d113f7c08d098b2ef286c69c7e13802cdfb47f1abbe5fdd8560b2881492a`，fixture两次子构造及两次audit准确，通过原外层Capture wait/readers/streams/H观察其真实返回，不自证外层退出。三条facts原collector均1个fixture逻辑槽、真实SDK0，原唯一unlock/close与临时线程归还全true。

所有外部批准输入均明确合成OFFLINE_FIXTURE；没有真实负责人LIVE签发或跨窗口外批往返。新路线不等待人在proof10/gate30内补实时hash，确定性绑定实际Gate。qualification V2适配未实现/NOT_RUN，没有真实资格、服务政策、目标七角色或安装媒体授权。原V1语义回归不能代现场。

## 原返回、资源与预算

父宿主10个Popen构造及10个audit全部匹配且构造返回；CLI内2个固定构造/2个audit亦匹配。外层6个Capture全部原wait/readers/stream/H返回，AUX/Gate/FACT custody均0，stopNew=false，无新增资源UNKNOWN。原调用资源未二close/kill/ACK退款。

预算360秒/320停新增、1GiB读取、16MiB产物、辅助96、并发1/retry0原样。预冻结12 Popen图遗漏了原preStart13 PS中固定Python `-I -X utf8 -B -c print(...)` 的1个.NET Start，因此准确整个辅助图为13个进程而非12；原13用例给出了该固定子进程原wait/readers/dispose证据，未新造不受限程序。实际13仍低于96，但此静态估算缺项明确保留，不能称预存调用图无遗漏。

原Gate source账：新路径8303441B/45读，旧V1 8248145B，CLI 8310239B/49读；均在原256MiB/64界内。新CLIcontrol20506B；其他原scope原账在快照。1GiB预算采用预存三套Gate cap+64MiB导入/控制+32MiB驱动保守预留905969664B（864MiB），不是全部物理IO实测，不能以这些source逻辑量冒称总物理IO。新增模板/policy/binding/source重读沿原账计，不扩90/30/15/10秒或SDK1/输出字节。

## 辅助报告路径缺陷、准确恢复与整包状态

最终派生worker已修group输出根，但漏了另一个字符串形式`B/'evidence/result.json'`，原finally把本批七组结果写入了候选旧evidence/result.json。后续封存读取新目录结果不存在时立即发现。该错误发生在全部原测试/资源返回之后，不是候选产品20源修改或资源UNKNOWN。

本批新原结果先逐字保全到本目录evidence/result.json（SHA `{rawsha}`），随后从原冻结ZIP e563573ca4d51c428ae7c56d79f4b5b7e03bd6e106157f95286c849a91afed52恢复原单项字节，核原manifest SHA d11659b55f31aa5bed06fbd76aff611da4b8588334f97d425dad2d052ce1fc10。恢复前原56坏1项，恢复后56项bad0；不能写“原56整个执行期间从未被改写”。evidence/artifact-destination-recovery.json保留准确前后状态、原ZIP来源和新结果SHA，无隐去覆盖事实。

本次执行用worker/41pins均未事后修改；附reference/worker-output-routing-static-draft.py.txt及diff只是静态把剩余输出根改为driverRoot的草案，未安装、未执行、不混为已测驱动。新模板/运行时绑定/原capture七组PASS保留，但整包状态为LIMITED_FUNCTIONAL_PASS_WITH_AUXILIARY_ARTIFACT_ROUTING_FAILURE（并保留图估算遗漏），不自动判正式B可派或交付全绿。没有借修报告补跑动态。

## 完整冻结与交接

原56前审bad0；最终写报告时坏1；按原ZIP恢复后复审bad0；原source20/gate12和本次41预冻结runtime pins均bad0。原旧PROFILE_SOURCE失败/未执行草案及所有CONTRACT03/旧FAIL/UNKNOWN/once/预算不改，旧对象未查询干预。实际SDK/ADB/Native route/TCP/help/设备/Gradle/媒体/新依赖/Git/index均0，共享三文档与tester目录未改。

本目录完整源码派生/diff/纯修订历史/最终profile与固定输入/七组原结果/原返回/新scope快照/恢复记录/静态草案统一manifest和唯一ZIP核验，独立freeze-receipt.json在manifest/ZIP外避免自包含循环。原new scope保留，冻结后不继续动态。负责人审完整包后决定限定接受、辅助修订或独立B准确范围；D1仍未通过/M0未启。
'''
(H/'DELIVERY.md').write_text(report,encoding='utf-8',newline='\n')
manifest=H/'reference/full-manifest.json';archive=H/'preauth01-selfcheck02-frozen.zip';receipt=H/'freeze-receipt.json'
assert not manifest.exists() and not archive.exists() and not receipt.exists()
files=sorted(p for p in H.rglob('*') if p.is_file());rows=[dict(path=p.relative_to(H).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in files]
save(manifest,dict(schema='PREAUTH01_SELFCHECK02_FULL_MANIFEST_V1',status='LIMITED_FUNCTIONAL_PASS_WITH_AUXILIARY_ARTIFACT_ROUTING_FAILURE',candidateSourceSha256=source,files=rows))
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files+[manifest]:z.write(p,p.relative_to(H).as_posix())
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(rows)+1 and len(set(z.namelist()))==len(z.namelist())
 for row in rows:assert sha(z.read(row['path']))==row['sha256'] and digest(H/row['path'])==row['sha256']
 assert z.read('reference/full-manifest.json')==manifest.read_bytes()
total=sum(p.stat().st_size for p in H.rglob('*') if p.is_file())+sum(p.stat().st_size for p in owned.rglob('*') if p.is_file());assert total+65536<16777216
save(receipt,dict(schema='PREAUTH01_SELFCHECK02_FREEZE_RECEIPT_V1',status='LIMITED_FUNCTIONAL_PASS_WITH_AUXILIARY_ARTIFACT_ROUTING_FAILURE',reportPath=str(H/'DELIVERY.md'),reportSha256=digest(H/'DELIVERY.md'),candidateSourceSealSha256=source,candidateGateSha256=gs,profileSha256=ph,originalDynamicResultSha256=rawsha,groups=7,functionalPassGroups=7,templateNegative=138,bindingAndOnceNegative=43,semanticCases=346,semanticConditionalPass=42,qualificationActualOriginalReturns=3,allSixAuxOriginalsReturned=True,parentPopen=10,nestedCliPopen=2,additionalDotNetProcess=1,wholeProcessCount=13,preplannedPopenTuples=12,graphEstimateOmissionRetained=True,wholeSeconds=r['seconds'],newResourceUnknown=False,old56BeforeBad=0,old56DuringFinalReportBad=1,old56AfterExactRecoveryBad=0,source20Bad=0,gate12Bad=0,runtime41PinsBad=0,manifestSha256=digest(manifest),manifestRows=len(rows),manifestBytes=sum(x['bytes'] for x in rows),archivePath=str(archive),archiveSha256=digest(archive),archiveBytes=archive.stat().st_size,archiveMembers=len(rows)+1,allUniqueMembersAndRowsVerified=True,currentScopeSnapshotFiles=len(snap),allNewMaterialBytesIncludingOriginalScopesAndArchiveBeforeReceipt=total,capBytes=16777216,noDynamicRerun=True,qualificationV2='NOT_IMPLEMENTED_NOT_RUN',actualSDK=0,actualNativeRoute=0,actualDevice=0,actualGit=0,D1='NOT_PASSED',M0='NOT_STARTED'))
print(receipt.read_text())
