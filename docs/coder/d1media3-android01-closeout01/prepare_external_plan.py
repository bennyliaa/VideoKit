from pathlib import Path
import json,hashlib,datetime
HERE=Path(__file__).resolve().parent;R=HERE.parents[2];B=R/'docs/coder/d1media3-android01';E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=E/'media3-android01-freeze.json';assert sha(seal)=='fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a'
s=json.loads(seal.read_text());assert len(s['files'])==740 and all(sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes'] for x in s['files'])
old=0
for row in json.loads((E/'frozen-baseline-preservation.json').read_text()):
 p=R/row['sealPath'];assert sha(p)==row['sealSha256'];v=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in v['files']);old+=len(v['files'])
assert old==6232
pending=json.loads((E/'earlier-suite-pending.json').read_text());rows=[]
for row in pending['completedReceipts']:
 p=E/'earlier-suite-snapshot'/Path(row['path']).name;assert sha(p)==row['sha256'];v=json.loads(p.read_text());assert v['exitCode']==0 and v['originalProcessReturned'];rows.append({'name':p.stem,'snapshot':p.relative_to(R).as_posix(),'sha256':sha(p),'startUtc':v['startUtc'],'endUtc':v['endUtc'],'exitCode':0,'originalProcessReturned':True})
assert len(rows)==29
record={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'External supplementary plan only, no termination authority','originalSessionResults':json.loads((HERE/'one-time-existing-session-results.json').read_text(encoding='utf-8-sig')),'sealSha256':sha(seal),'newFrozenFilesVerifiedUnchanged':740,'oldFrozenFilesVerifiedUnchanged':6232,'completed29':rows,'pendingOriginalIdentities':{'suiteToolSession':48945,'parentPythonPidHistorical':35988,'parentCreationTime':'NOT_OBTAINED; first child start22:22:14.882512Z is not parent creation time','parentCommand':'fixed bundled python.exe -X utf8 -B docs/coder/d1media3-android01/tools/run_suites.py 001 002 source','javaPidHistorical':39256,'javaCreationTimeFromEarlierGetProcess':'2026-10-21T06:22:37.9542743+08:00','javaParentPidHistorical':35988,'javaMainClass':'com.videokit.d1input.ContainerPendingOrderCheck','javaClasspath':'evidence/local-002/classes;exact candidate deps as recorded original argv; no production Jar first','javaJvmArg':'-Xmx256m','diagnosticToolSession':17257,'diagnosticCommand':['D:/Android/Android Studio/jbr/bin/jcmd.exe','39256','Thread.print','-l'],'diagnosticOwnPid':'NOT_OBTAINED;39256 is target argument not jcmd PID','diagnosticCreationTime':'NOT_OBTAINED','historicalPidMayBeReused':True,'currentPidLivenessNotRequeried':True},'newDeviceOrDiagnosticProcesses':0,'newSessionResultReads':2,'terminationSuspendInterruptKillOrSecondCloseActions':0,'newTestInvocations':0,'candidateOrActiveDirectoryWrites':0,'state':'UNKNOWN_ORIGINAL_RETURN_NOT_PROVEN','postfreezeGreenDoesNotOverrideEarlierOriginal':True,'dispatchGate':'Parent contains no per-iteration frozen/stop gate; only startup assert. Current waiting subprocess return0 can dispatch final AndroidReadyCheck; never stop child first while parent may dispatch','options':['Preserve sessions/UNKNOWN and stop polling; static tester review proceeds. No stop-dispatch guarantee in this option','Future separately approved original-parent admission barrier, only if exact original process handles/creation evidence and an existing approved atomic stop-dispatch capability are available; otherwise blocked','Future separately approved diagnostic forced closeout: parent first; verify that same parent actually terminated before child action, account narrow pre-termination spawn race, separately bind each surviving exact child/diagnostic original. Not natural test return; preserve permanent test UNKNOWN and evidence-loss disclosure'],'newApprovalRequiredBeforeAnyIntervention':True,'report':'docs/coder/D1_MEDIA3_ANDROID01_READY_ORIGINAL_SESSION_CLOSEOUT_PLAN_V1.0.md'}
(HERE/'external-validation-and-identities.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
table='\n'.join('|'+v['name']+'|'+v['endUtc']+'|0 / 原始子进程已返|' for v in rows)
report=f'''# ANDROID01 原会话整体验证与收尾可审方案 V1.0

2026-10-21 06:41后形成。仅外置补充，不改Android01 seal、ZIP、原活动目录或旧候选。负责人已正式交tester阶段B先静态材料独立审；本方案不阻塞该审查，不是终止/暂停进程/新attach/设备执行授权。

**结论：两个既有会话各收取一次后均无新增输出或最终返回，保留UNKNOWN。无终止、interrupt、暂停、第二close、新诊断、测试重放或设备操作。** 会话返回的“仍运行”只证明工具尚未交付最终结果，不能作历史PID当前存活或无PID复用证明。此后不连续轮询。

## 一、已做的整体验证

在独立外置目录d1media3-android01-closeout01保存one-time-existing-session-results.json：session48945及17257各一次空输入读取；均output空、session id仍存在、无exit_code。每次requested yield1000ms，工具实际约5000ms，两次并行完成。未新开测试/attach/进程诊断；现有结果读取不是终止动作。

只读文件核验：Android01 seal SHA256 {sha(seal)}，列740身份全部长度/hash不变，旧10候选6232文件逐hash不变；原29已返receipt的冻结快照逐hash及exit0/originalProcessReturned一致。没有重新运行62、挂起场景、构建或平台探针。既有前/后封存各62绿仅证明那两次各自原返回，不能替代本早期原会话，也不能证明当前全机空闲或设备fresh门。

## 二、原会话身份及创建证据

1. suite工具session48945：原命令为固定bundled Python执行tools/run_suites.py 001 002 source；历史CIM看到父Python PID35988，原Java PID39256/ParentProcessId35988。Java实际argv为固定JDK java.exe -Xmx256m -cp candidate/evidence/local-002/classes及candidate/deps精确JAR集合，main com.videokit.d1input.ContainerPendingOrderCheck。不是Android/ADB或生产进程。
2. Java创建时间有本窗口早先Get-Process原输出：2026-10-21T06:22:37.9542743+08:00。父Python准确创建时间未取得；core receipt start2026-10-20T22:22:14.882512Z只证明首子调用开始，不可冒父创建时间。上一CIM/线程属性输出仅为历史观察，不能当今后终止时身份验证。
3. read-only诊断session17257：原命令固定JDK jcmd.exe 39256 Thread.print -l；原输出只有39256:，无栈、无退出。39256是目标Java参数，不是jcmd自身PID。jcmd自身PID、创建时间、完整原句柄均未取得，不能凭命令参数杀目标/所有jcmd。另一次默认沙箱attach access-denied已有历史输出，并不解释挂起根因。
4. 当前单次收取仍无最终结果，既不能断言进程已归还，也不把历史PID更新成当前强绑定。负责人CIM不可访问的事实保留；本次未另查CIM或启动新诊断。若将来没有原工具句柄或可靠创建时间/image/完整argv/亲子关系，则任何按PID干预保持阻塞。

本地创建/查询的原工具输出在本coder窗口历史记录；外置external-validation-and-identities.json准确注明已知值、证据来源与缺失值，未伪造完整OS审计日志。原原始测试stdout/stderr通常由父Python在subprocess.run返回后才写文件，因此未返回那一例的原stdout/stderr可能仍仅在活进程/管道内，没有伪造不存在的完成receipt。

## 三、29已返与未返资源分别保存

29条已返receipt均为原始子进程自然返回exit0，不把platform-availability的预期NOT_RUN算实际Android通过。冻结earlier-suite-snapshot保存其原argv/start/end/stdout/stderr及hash；外置JSON再列精确身份。列表如下：

|原已返回测试|原结束UTC|有限结论|
|---|---|---|
{table}

未返：当前ContainerPendingOrderCheck原Java调用无完成receipt；其进程、JVM线程、可能仍执行的受控原worker/observer、SDK source/output登记及stdout/stderr管道的实际归还均UNKNOWN。父Python在subprocess.run等子退出/pipe EOF，父本身与其pipe读取/句柄也未证返。诊断jcmd原会话无完成状态。不能从旧计数、他次通过、PID消失、Future.isDone或外部kill断言这些原callback/线程自然返回。

源码只支持风险推断，不能定位已卡在哪个case：测试有ACK_FIRST/THREAD_FIRST/OBSERVER_TAIL/TIMEOUT/cancel等真实线程顺序，确切当前case/栈未取到。它的输入是受控4字节非媒体端口，不是本批Android解析；仍不得据此伪造“没有任何FD/owner”的证明。

最后的android-ready-host尚无本早期suite的开始/结束receipt；历史父控制流显示它排在inspection-orders后。现在没新输出不是它永远未派发的强证明，未来可能因原子自然返回而派发，必须按下一节控制。

## 四、父进程派发风险与必须的屏障

冻结run_suites.py只在**启动时**assert seal不存在，for循环每轮没有stop/frozen检查；Python已将脚本载入内存。不能靠现在seal存在、改磁盘脚本、放stop文件、改输出目录权限或关闭工具显示窗来阻止原父继续运行。**先单独终止/放行Java39256不安全：若父读到return0，它将写该例receipt并继续派AndroidReadyCheck；非0通常触发assert，但不能以此作为可控准入屏障。** 原stdin已关闭，不假设能发Ctrl+C；不使用名称匹配、taskkill整树或针对其他项目进程的批量操作。

若负责人要求绝不再派新测试，今后必须先有可靠的**原父派发屏障**。可选一：经审定的现有执行设施持有准确原父进程句柄并支持原子暂停/停止派发，确认屏障已生效且维持不恢复，再处理子进程；当前没有确认这种可用能力，故不能说此方案已可执行，也不新造native helper/诊断框架。暂停不等于返回，会保留更多UNKNOWN/资源，后续解除屏障另审。

可选二：若决定强制诊断收尾，先用重新核准的**准确原父句柄**终止父Python并等待该同一原句柄真实signaled/退出记录，之后才考虑子Java/jcmd。这个次序能阻止“已确认父退出之后”再派发；**不能消除决策至父退出之间的窄窗口**。因此最小方案还须在屏障前后用获准的一次有界身份快照核对子列表/创建时间，出现新子进程就停止原计划，把新资源作为未知单列，不擅自扩大终止范围。若连这个窗口也不允许，必须先具备上一段可证的原子屏障；没有则继续阻塞。

今后任何干预需独立明确范围、具体已批准现有工具身份/参数、原进程创建证据/句柄绑定、最多次数与预算。当前本方案不提供可直接执行的Stop-Process/taskkill脚本，因父创建时间和jcmd自身身份缺失，写一个裸PID命令不可审也不安全。

## 五、可选最小处置及证据损失（均未执行）

|选项|能达成什么|风险及不能声称什么|
|---|---|---|
|A 保留UNKNOWN、不再主动收取或诊断|不改变原运行/证据，tester继续静态审|父仍可能随原子自然返回继续派最后测试；不能承诺已关闭派发/资源释放/全机idle|
|B 准确原父原子准入屏障（仅存在获审设施时）|屏障实际确认后，父不能再派余下测试；保留子原返回机会|设施/原句柄尚未确认，当前不可执行；被暂停父未返回，pipe读取可能停，子输出可能阻塞，不能作正常回收|
|C 准确原父先强制终止，确认后再逐个审定原子/诊断收尾|父退出之后无法继续派发；可回收原OS进程资源|父退出会关闭管道读端，可能使子写失败/改变执行；进程/job关联语义未证，不能假设对子无影响。可能丢失未落盘stdout/stderr/栈、Python尚未写的receipt、JVM finally/observer自然返回证明。须永久保留原测试UNKNOWN/被干预，后续绿不补。

C不能通过“先杀jcmd/Java再看”简化；jcmd独立PID未知，且终止目标39256不等于终止诊断。也不假设结束父会自动结束所有孩子。所有强制动作的返回都只证明执行器/OS干预结果，**不是原业务close/线程/observer自然返回**，不得补ACK、改exit0、退款或回写原29/旧seal。诊断收尾的状态拟记DIAGNOSTIC_FORCED_CLOSEOUT_WITH_ORIGINAL_TEST_UNKNOWN，不能记原测试PASS。

## 六、今后获准操作后的确认边界

1. 先保全已有原会话输出/29快照/原命令、创建时间、当前绑定证据和操作前原子列表；不伪造缺失栈，不修改原活动目录/冻结对象。若绑定不可得/变化/PID复用/权限拒绝，立即停，保持UNKNOWN，不尝试其他进程或新工具绕过。
2. 在准确父屏障实际确认之前，不对Java/jcmd做会解除其等待的操作。父终止若获准，只等待同一原进程handle一次；无返回继续UNKNOWN，不追加强杀。核查是否发生窄窗口新派发；发现即停并另审，不把新孩子批量带走。
3. 各获准原子/jcmd独立记录干预次数/时间/精确身份/工具返回、同一原handle终态；原会话结果如实际得到只能按原字节保全。任何非自然退出都单列，不冒JVM原finally/FD close/callback返回。
4. 只做获准的一次有界后确认：已绑定原进程终态、父无后续派发能力、原子列表差异、外置证据hash与新740/旧6232不变。只对这些准确进程下结论，不能由进程不见推出全系统idle/零句柄/所有SDK归还，更不能代设备fresh gate。
5. 若确认不足/新PID/日志损失/工具不返，保留UNKNOWN和精确缺口，交负责人统一判断；不自动删活动目录、卸载软件、重跑测试或复用原scope。后续实机授权、fixture/toolbuild准入均仍另审。

## 七、当前交接

本补充只提交整体验证与可选收尾方案；当前实际执行只有两个原会话各一次收取和只读文件核验，未选择B/C、未暂停/终止/新attach。tester静态阶段B可直接使用已封存740身份/ZIP739材料；原局部UNKNOWN独立保留，不用后续62绿替代、不要求tester复现挂起、不拖住静态审。本补充位于候选外部，原seal/报告/ZIP不改，等待负责人一次集中决定。
'''
p=R/'docs/coder/D1_MEDIA3_ANDROID01_READY_ORIGINAL_SESSION_CLOSEOUT_PLAN_V1.0.md';assert not p.exists();p.write_text(report,encoding='utf-8')
files=[p]+sorted(x for x in HERE.iterdir() if x.is_file())
manifest={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidateSealUnchanged':sha(seal),'files':[{'path':x.relative_to(R).as_posix(),'bytes':x.stat().st_size,'sha256':sha(x)} for x in files],'terminationAuthorizedOrExecuted':False,'nextDecision':'Coordinator consolidated decision; static tester review can proceed'}
(HERE/'supplement-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':p.relative_to(R).as_posix(),'reportBytes':p.stat().st_size,'reportSha256':sha(p),'manifestSha256':sha(HERE/'supplement-manifest.json'),'currentState':'UNKNOWN_ORIGINAL_SESSIONS_NOT_RETURNED','newFrozenFilesVerified':740,'oldFrozenFilesVerified':6232},ensure_ascii=False,indent=2))
