"""Bind final executed classes and offline APKs; write review documents, never dispatch."""
from pathlib import Path
import json,hashlib,zipfile,re,difflib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';OLD=R/'docs/coder/d1e13e';D=B/'artifacts/D1-20261018-E13F/delivery-final';C=B/'.checks/host-007'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=sha(b))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8')
assert not (E/'e13f-freeze.json').exists()
for row in json.loads((E/'final-build-inputs.json').read_text())['files']:assert pin(R/row['path'])==row
for attempt in ['host-007','public-008','join-orders-009']:assert json.loads((E/attempt/'results.json').read_text())['status'].startswith('PASS')
sources=[]
for f in ['src','upstream-c14/src','binding']:sources+=sorted((B/f).rglob('*.java'))
sources+=sorted((B/'tools').glob('*.java'));allow={}
for p in sources:
 pkg=re.search(r'package\s+([\w.]+);',p.read_text(encoding='utf-8-sig')).group(1);allow[pkg.replace('.','/')+'/'+p.stem]=p
jar=D/'e13f-host-tools.jar';rows=[];tested=[]
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z:
 for p in sorted(C.rglob('*.class')):
  n=p.relative_to(C).as_posix();top=n[:-6].split('$')[0]
  if top not in allow:continue
  raw=p.read_bytes();z.writestr(n,raw);row=dict(entry=n,bytes=len(raw),sha256=sha(raw),source=pin(allow[top]));rows.append(row)
  q=E/'tested-class-bytes/host-007'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);tested.append(dict(attempt='host-007',entry=n,sha256=sha(raw),exactFinalJarMember=True))
write(E/'host-jar-manifest.json',dict(jar=pin(jar),compileAttempt='host-007',classes=rows,testClassesIncluded=False,recompiledAfterFinalChecks=False))
write(E/'tested-final-class-equivalence.json',dict(status='PASS',members=tested,scope='All production classes of final host-007 compilation; public-008 and join-orders-009 use this directory after local policy/runtime shadows.'))
for row in json.loads((E/'host-007/inputs.json').read_text()):
 p=R/row['path'];assert pin(p)==row;q=E/'host-007/final-source-snapshots'/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
# Preserve actual test dispatch and fixture compiler provenance absent from the first harness format.
fixture=[]
for root in sorted((E/'public-008').iterdir()):
 if not root.is_dir():continue
 fixture.append(dict(group=root.name,shadowSources=[pin(root/n) for n in ['E13GuardLocation.java','E13HostRuntime.java']],testSource=pin(B/'selfchecks/FPublicChainCheck.java'),productionCompile='host-007',classPath=json.loads((root/'exit.json').read_text())['argv'][2],actualEntryProduction=True,allSdkArgumentsSubstituted=True))
write(E/'public-008/class-binding.json',dict(groups=fixture,productionSources=[pin(p) for p in sources],productionDirectory='docs/coder/d1e13f/.checks/host-007',substitutionLimit='Only fixed guard location/policy/thread daemon in finite failure test and SDK command runtime. No real ADB/Android call; synthetic child JUnit text is not product PASS.'))
audit=json.loads((E/'apk-delivery-final/apk-audit.json').read_text());assert audit['status']=='PASS_LOCAL_APK_IDENTITY_AUDIT'
assert "versionCode='3'" in (E/'apk-delivery-final/fixture-badging.txt').read_text(encoding='utf-8-sig')
dex=[]
for apk in audit['apks']:
 with zipfile.ZipFile(R/apk['path']) as z:
  raw=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
  for marker in [b'FCompletionCheck',b'FPublicChainCheck',b'FJoinOrderCheck',b'LOCAL_TEST_original_claim_custodian',b'CONTROLLED_PLATFORM_KERNEL_DENIAL']:assert marker not in raw
  if apk['kind']=='app':
   for marker in [b'E13FinishOwner',b'E13Stages',b'e13-bounded-stage-sink',b'sinkInFlight']:assert marker in raw
  dex.append(dict(apk=apk,productionMarkersVerified=True,testShadowsExcluded=True,scope='Static DEX presence/absence only, not Android execution'))
write(E/'final-dex-wiring-audit.json',dict(status='PASS',rows=dex,fixtureVersion=3,deviceCalls=0))
derived=[]
for folder in ['src','android','upstream-c14/src','upstream-c14/android','binding','checks/com','app/src','fixture/src','tools']:
 for p in sorted((B/folder).rglob('*')):
  if not p.is_file() or p.suffix not in ['.java','.py','.ps1','.xml']:continue
  old=OLD/p.relative_to(B);before=pin(old) if old.is_file() else None;after=pin(p);same=before and before['sha256']==after['sha256'];derived.append(dict(current=after,baseline=before,relationship='BYTE_IDENTICAL' if same else 'MODIFIED' if before else 'NEW_E13F'))
  if not same:
   q=(E/'diffs'/p.relative_to(B)).with_suffix(p.suffix+'.diff');text(q,''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True) if old.is_file() else [],p.read_text(encoding='utf-8-sig').splitlines(True),fromfile=before['path'] if before else '/dev/null',tofile=after['path'])))
write(E/'source-derivation.json',dict(files=derived,baseline='FROZEN_E13E',nativeBuilds=0))
plan=json.loads((OLD/'release/candidate-binding.json').read_text())
plan.update(candidate='D1-20261018-E13F',appVersion=19,fixtureVersion=3,hostJar=pin(jar),targetApks=audit['apks'],fixedOnceBasename='e13f-lifecycle-deployment.once',batch='D1-E13F-LIFECYCLE-20261018',metadataArgv='NOT_YET_AUTHORIZED; fresh exact installed v17/fixture1 to candidate19/3 metadata required after original disposition',independentReview='PENDING_E13F_REVIEW',rootCause='NOT_UNIQUELY_DETERMINED')
write(B/'release/candidate-binding.json',plan);write(B/'release/device-plan-draft.json',plan)
latest='> 2026-10-18 E13F最新安排：E13E独立复审NOT_PASSED（3项P1，报告SHA3193a7728e84d860d03b14447214901f0641ccf135ffd655cfc69fc0938f9d6d）；E13F已集中修复同claim晚返续办、日志锁外异步记录、原writer实际线程归还判定，有限离线自检及一次必要APK构建成功，完整冻结后交独立复审。候选app19/fixture3未安装。原E13C主case最后PENDING/UNKNOWN，LOST_DIAGNOSTIC_OWNER_UNKNOWN独立；实际根因NOT_UNIQUELY_DETERMINED。用户已有持续真机测试授权，当前不操作设备源于原任务未决，禁止新部署/重测/查询原句柄/处置；源码pin ABSENT、scope/release/once未签发。D1未过/M0未启，P0/许可和旧冻结证据保持。\n\n'
refs=B/'reference';refs.mkdir(exist_ok=True)
for rel in ['docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 p=R/rel;t=p.read_text(encoding='utf-8');pos=t.index('\n')+1;text(p,t[:pos]+'\n'+latest+t[pos:].lstrip('\n'));shutil.copyfile(p,refs/p.name)
for rel in ['docs/tester/D1_E13E_LIFECYCLE_REVIEW_REPORT_V1.0.md','docs/tester/D1_E13D_OFFLINE_REVIEW_REPORT_V1.0.md','docs/tester/D1_E13C_TABLET_EXECUTION_REPORT_V1.0.md','docs/tester/D1_E13C_TABLET_EXECUTION_REPORT_V1.1.md','docs/coder/d1e13d/evidence/cached-dependency-source-excerpts.json']:
 p=R/rel;shutil.copyfile(p,refs/p.name)
assert pin(refs/'D1_E13E_LIFECYCLE_REVIEW_REPORT_V1.0.md')['sha256']=='3193a7728e84d860d03b14447214901f0641ccf135ffd655cfc69fc0938f9d6d'
ident='\n'.join('| '+x['kind']+' | '+str(x['bytes'])+' | `'+x['sha256']+'` |' for x in audit['apks'])
common='D1 NOT_PASSED / M0 NOT_STARTED；原实际卡点 NOT_UNIQUELY_DETERMINED。原v17主任务仅最后观测PENDING/UNKNOWN，本轮未查询；丢失诊断独立LOST_DIAGNOSTIC_OWNER_UNKNOWN。候选app19/fixture3未安装，真实Android/Binder/UID/Looper/monitor、kernel行为和T07均NOT_RUN。源码处置pin ABSENT，scope/release/once/sourceReview均未签发；旧资格/预算不继承。用户持续测试授权已具备，当前无设备操作源于原任务未决。'
text(R/'docs/coder/D1_E13F_LIFECYCLE_DELIVERY_V1.0.md',f'''# D1 E13F 生命周期集中修复交付 V1.0

2026-10-18。依据正式E13F coder/tester需求和E13E独立报告SHA3193a7728e84d860d03b14447214901f0641ccf135ffd655cfc69fc0938f9d6d。本候选完成三P1修复及指定有限离线自检，提交独立审查，未自批产品通过。

F01：公开case、新旧deploy在启动原child前把同一claim绑定同一supervisor；责任线程跨main超时isolation继续保管，join同一实际custodian后一次写准确marker。原超时继续失败，禁止自动下一方法。F02：request/fail锁内决定状态，锁外启动唯一worker与记录；平台日志通过48项有界异步队列，异常/未返不阻断请求及原归还。F03：writer体结束标志与线程真实结束分栏，原writer外检查并join同一线程后才退keeper；同样加强原PC starter/reader线程尾部屏障。

`evidence/host-007`实际两组日志测试、`public-008`六组完整公开入口链和`join-orders-009`三时序通过。全部生产class来自最终host-007编译，准确字节装入JAR，{len(rows)}个成员；所有成员保存原测试class字节并逐字节核对。未重跑长55秒/历史全套/媒体。

一次必要离线Gradle集中构建main-001 exit0；APK输入142项逐字节核对；app/test同签，fixture独立签。7 native与既审基线逐字节相同、35 Maven坐标及锁不变，fixture零第三方runtime，license NOT_GRANTED不变，无native重建/下载。DEX是静态接线核验，不能代替Android行为证据。

| 制品 | 字节 | SHA256 |
| --- | --- | --- |
{ident}
| host JAR | {pin(jar)['bytes']} | `{pin(jar)['sha256']}` |

app/test签名SHA5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f；fixture签名SHA45b462a82be4e90ceb60e26ffa5819272947c05d7274801043c1fd57a68114e9。fixture私钥不分发，构建输入单列其pin。

包路径`D1-20261018-E13F-source.zip`；外seal `d1e13f/evidence/e13f-freeze.json`；最终只读回执`D1_E13F_FINAL_READONLY_VERIFICATION_V1.0.json`在ZIP外提供实际SHA，避免自引用。默认verify/带seal SHA verify/help/pack-help只读；仅显式pack生成一次新包。旧E11–E13E九组seal和准确成员保持原样，两份滚动协调文件只新增顶部安排，封包采用副本。

{common}

未来预算51成功/53含两次占用复查、2MiB文本仅全六法上限草案，非许可。须原任务及独立诊断处置审定、fresh完整M1、准确候选metadata、独立复审后重新派单一T07准确scope/budget；不得按此草案自动六法执行。P0、renderer/audio/Kit及历史FAIL/UNKNOWN保持。
''')
text(R/'docs/coder/D1_E13F_IMPLEMENTATION_CONTRACT_V1.0.md',f'''# D1 E13F 实现契约 V1.0

2026-10-18；最小范围扩展现有owner/archive/supervisor，无新增通用生命周期框架。

## F01 同claim真实原返

E13HostCase、E13HostActivationSession与E9HostActivationSession的deploy分支，在创建同一supervisor后、任何原child前follow同一E13PendingGuard。export分支无claim，不改。移除人工originalReturned(boolean)接口及同步finally结算。静态OWNERS强持guard，guard强持samePC与非daemon责任线程；join同一PC custodian，不靠可能丢失的通知/定时器。follow只能一次；在join前/后/并发close均不漏返。原PCterminated要求线程已实际停止、listener已返且LIVE已退；Operation还要求原starter/reader实际终止join、原pipe/decoder/authority及archive全部真实归还。

唯一结算attempt：CREATE_NEW临时marker，E4Owned持有原FileChannel，写全/force/同handle读回/长度比对、原close真实返回，再atomic move为claim.original-returned。内容绑定claim及其SHA、samePC UUID/PID、pcThreadJoined=true。任何失败保留同guard/PC/原marker对象和责任线程，保持跨scope拒绝，无重试/二close/补ACK。marker是原PC终止证明，不声称发布marker的责任线程在发布前自身已退出；发布后无新增IO。partialclaim及失败marker均封锁，词法close无归还语义。

## F02 日志与完成分离

request/fail只在owner monitor内保存首结果、失败及唤醒数据。唯一worker在锁外先启动；之后stage只记录有限ring并非阻塞offer。一个daemon诊断线程在所有owner/Stages monitor外调用平台sink，异常计数且不重试，sink未返只占一个在途引用；最多48引用队列，沿用48事件/500 ASCII字符/24576字节上限含footer预留。丢日志和sink UNKNOWN不是finish或原资源ACK，诊断线程不拥有完成请求。保持原第一个payload/code、失败只降资格、唯一非主finalizer、原UNKNOWN不finish。完成owner worker本来的daemon属性不改，日志worker也不是资源替代owner。

## F03 原writer返回

writer终于完成文件调用后仅写writerBodyReturned并调用原ReturnEvents；即使通知未返也仍在OWNERS。resourcesReturned拒绝原writer自己调用，并在外部观察同Thread非alive后join，写writerThreadReturned，逐个原文件returned后才退OWNERS。archive-facts是writer内提前快照，可显示线程未返；不是完整归还ACK。通知异常会记archiveFailed，物理归还与成功资格分别判断。上层pcClosed/claim都受此物理屏障限制。

## 替身与交付边界

最终public-008运行真实公开入口/guard/PC/archive类，影子仅固定本地guard根/处置pin与本地child命令runtime。测试用LOCAL child合成instrument文本不构成Android/产品PASS。失败marker子测试仅把本地责任线程改daemon以有限JVM自然退出；原失败对象/线程在断言时仍被保管，生产责任线程非daemon且无限保管。部署测试首SDK调用由一个本地JVM替代，其后metadata格式有意不模拟完整设备；证明准入及归还链，不是部署成功。没有真实ADB。FCompletionCheck直接调用生产request/fail，sink扣住/抛错均与原worker完成断言分离；不是只看E9类锁。

源码策略根固定、pin ABSENT，不提供环境变量/命令行绕过。{common}
''')
text(R/'docs/coder/D1_E13F_SELF_CHECK_REPORT_V1.0.md',f'''# D1 E13F 有限自检报告 V1.0

2026-10-18；仅本批P1直接回归与必要构建，不机械重复旧套件。所有命令/真实stdout/stderr/自然exit见evidence。

| 最终证据 | 结果与范围 |
| --- | --- |
| host-007 | compile exit0；BLOCKED/THROWS两独立JVM直接调用生产request及fail：sink不持FinishOwner实例/class或Stages锁，sink未返时调用者和唯一完成worker均可返回；异常不丢首结果/失败；ring有界 |
| public-008 | CASE/DEPLOY/LEGACY各NORMAL、FAIL_MARKER共6组exit0。真实公开claim→100ms短超时isolation→主调用栈退出→同原child自然返；原writer尾通知有限扣住时resourcesReturned=false、pcClosed无、claim marker无；释放并join同原线程后准确唯一marker，另一scope从同公开入口准入；失败持久化保同guard/原PC/责任线程且下scope在PC创建前拒绝。无手工true，原超时不改PASS |
| join-orders-009 | 真supervisor零child，follow在close之前、实际终止后、并发三序列，唯一marker/重复follow拒绝/下一scope准入 |
| build main-001 | 一次离线Gradle集中构建三APK exit0，无成功后重复构建；最后host-only线程屏障不在APK源码中，无需重建APK |
| apk-delivery-final | 官方签名/清单/ZIP对齐、DEX线索、准确142输入、版本19/3、35坐标、7 native逐字节不变；静态对齐不冒16KiB实机验证 |
| final class provenance | {len(rows)}生产class全部从实际host-007输出装入JAR且保留逐字节比较。public-008 / join-orders-009使用该目录，只隔离明确本地shadow；检查类不混入JAR/APK |

保留开发失败：public-002本地record路径反斜杠语法被生产parser拒绝；public-003 case/newdeploy四组通过、legacy因本地dummy文件缺失失败，public-004补本地文件后legacy两组通过。host-006编译将依赖shadow runtime的public harness误纳入生产编译而失败，未运行该轮测试；host-007只编译生产及直接FCompletionCheck，public harness分别在影子classpath编译。host-001旧版日志测试成功，其原harness快照单列；随后为harness补finally释放latch，最终host-007重测。所有旧失败证据保留，不涂成PASS；最终生产代码包括starter/reader线程实返屏障，最终public-008已全部重测。

本地每子进程有有限fixture释放，不通过kill补exit；失败marker生产keeper的无限保管分支仅在有限本地daemon测试中观察，不声称其生产线程已终止。未再测长55秒，未重跑历史Android JVM适配/全套模块/媒体。旧E13E测试仅历史来源，不能用作新Android动态验证。

{common}
''')
old=(R/'docs/coder/D1_E13E_ORIGINAL_TASK_DISPOSITION_PLAN_V1.0.md').read_text(encoding='utf-8')
old=old.replace('# D1 E13E 原任务处置待审方案 V1.0','# D1 E13F 原任务处置待审方案 V1.0').replace('E13E新包只离线候选','E13F新包只离线候选').replace('新E13E的stage/ACK/finalizer','新E13F的stage/ACK/finalizer').replace('E13E新observer','E13F新observer').replace('候选18/2升级代码','候选19/3升级代码')
pos=old.index('\n\n')+2;old=old[:pos]+'E13F增补：三项P1修复仅影响新字节码中的claim真实晚返续办、日志无阻塞和writer物理join。旧v17没有该续办接线，新包不能补旧marker、接管旧handle或把外部处置改成Java正常ACK；自然/外部两分支原条件保持。当前pin仍ABSENT，未选择/执行A或B。历史已装v17/fixture1是最后切片，后续候选为19/3（不是18/2）。\n\n'+old[pos:]
text(R/'docs/coder/D1_E13F_ORIGINAL_TASK_DISPOSITION_PLAN_V1.0.md',old)
write(E/'final-summary.json',dict(status='READY_FOR_INDEPENDENT_REVIEW',hostFinalCompile='host-007',finishGroups=2,publicCombinedGroups=6,joinOrders=3,jarClasses=len(rows),exactProductionClassComparisons=len(tested),apkBuildAttempts=1,passingApkBuilds=1,productionBuildInputCount=142,deviceCalls=0,oldSuitesRerun=0,T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED'))
print(json.dumps(dict(status='PREPARED_E13F',jar=pin(jar),classes=len(rows),apks=audit['apks']),ensure_ascii=False))
