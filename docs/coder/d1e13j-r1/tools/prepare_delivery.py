from pathlib import Path
import json,hashlib,zipfile,difflib,shutil,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';I=R/'docs/coder/d1e13i';F=R/'docs/coder/d1e13f';A=B/'artifacts';C=B/'.checks/host-001'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8')
assert not (E/'e13j-r1-freeze.json').exists()
for row in json.loads((E/'host-001/inputs.json').read_text()):assert pin(R/row['path'])==row
parent=json.loads((E/'parent-faults-002/results.json').read_text());assert parent['status']=='PASS_ACTUAL_PARENT_LOG_FAULT_CUSTODY' and pin(B/'tools/check_host.py')['sha256']==parent['sourceSha256']
shutil.copytree(I/'baseline-source',B/'baseline-source');base=json.loads((I/'evidence/base-jar-source-manifest.json').read_text());base['copiedJar']=pin(A/'e13f-reviewed-base.jar');write(E/'base-jar-source-manifest.json',base)
oldManifest=json.loads((F/'evidence/host-jar-manifest.json').read_text());oldRows={r['entry']:r for r in oldManifest['classes']};production=['E13JIdentity','E13JArchive','E13JSocket','E13JReadOnly'];jar=A/'e13j-host-tools.jar';rows=[]
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z,zipfile.ZipFile(A/'e13f-reviewed-base.jar') as old:
 for n in old.namelist():
  raw=old.read(n);r=oldRows[n];assert hashlib.sha256(raw).hexdigest()==r['sha256'];z.writestr(n,raw);rows.append(dict(entry=n,bytes=len(raw),sha256=r['sha256'],source=r['source'],origin='UNCHANGED_REVIEWED_E13F'))
 for p in sorted(C.rglob('*.class')):
  top=p.stem.split('$')[0];n=p.relative_to(C).as_posix()
  if top not in production:target=E/'actual-fixture-class-bytes'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());continue
  raw=p.read_bytes();z.writestr(n,raw);target=E/'actual-tested-production-class-bytes'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);rows.append(dict(entry=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),source=pin(B/'tools'/(top+'.java')),origin='ACTUAL_HOST_001_TESTED_BYTES'))
write(E/'host-jar-manifest.json',dict(jar=pin(jar),classes=rows,unchangedFClassCount=183,newProductionClassCount=len(rows)-183,productionCompileAttempts=1,testProbeCompiles=0,productionRecompiledAfterChecks=False))
diffs=[]
for name,oldName in [('E13JIdentity.java','E13IIdentity.java'),('E13JSocket.java','E13ISocket.java'),('E13JArchive.java','E13IArchive.java'),('E13JReadOnly.java','E13IReadOnly.java'),('check_host.py','check_host.py'),('observe_j_only.ps1','observe_i_only.ps1')]:
 p=B/'tools'/name;old=I/'tools'/oldName;q=E/'diffs'/(name+'.diff');text(q,''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),p.read_text(encoding='utf-8-sig').splitlines(True),fromfile=old.relative_to(R).as_posix(),tofile=p.relative_to(R).as_posix())));diffs.append(dict(source=pin(p),baseline=pin(old),diff=pin(q)))
write(E/'source-derivation.json',dict(files=diffs,base='FROZEN_E13I',scope='F01/F02/F03 only'))
for name in ['protocol-source-manifest.json','protocol-excerpt-manifest.json','dependency-difference.json']:
 t=(I/'evidence'/name).read_text().replace('docs/coder/d1e13i/','docs/coder/d1e13j-r1/');text(E/name,t)
plan=json.loads((I/'release-plan.json').read_text());plan.update(status='DRAFT_NO_EXECUTION_DISPATCH',root='D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE',fixedOnce='e13j-r1-g-readonly.once',wireSemantics='Exact application RX+conservative TX intent; each IO prechecked, length<=remaining; zero means UNKNOWN/no more IO or drain, no socket force close. No OS/NIC total traffic claim.',auditSchema='Two <=512B P/T snapshots in one <=1024B original facts.txt plus <=1024B intent. Snapshot not own-close/final caller ACK. Production Batch emits bounded final caller/return summary.',firstScriptSha=pin(B/'tools/E13JIdentity.java')['sha256']);plan['budget']['wireOverrun']='Impossible for new application read/TX admission: at remaining0 no IO/drain/EOF probe, same original owner held UNKNOWN; no refund or borrowing unused reservation';write(B/'release-plan.json',plan)
old=(F/'tools/observe_original.ps1').read_bytes();new=(B/'tools/observe_j_only.ps1').read_bytes();marker=b'# Same original local context';assert old[old.index(marker):]==new[new.index(marker):];write(E/'script-binding.json',dict(script=pin(B/'tools/observe_j_only.ps1'),old=pin(F/'tools/observe_original.ps1'),ownerBodyActualBytesIdentical=True,approvedRequestSha='ABSENT'))
# Exact source script gates, no Process/Socket role started by the wrapper.
ps=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe');P=E/'script-003';P.mkdir();parser=R/'docs/coder/d1e13h/tools/check_observer.ps1'
tests=[('parse',[ps,'-NoProfile','-File',parser,'-ScriptPath',B/'tools/observe_j_only.ps1'],0)]
request=dict(evidenceRoot='D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE',pins=[],argv=['D:/Android/Android Studio/jbr/bin/java.exe','-cp','D:/CodexProjects/VideoKit/docs/coder/d1e13j-r1/artifacts/e13j-host-tools.jar','com.videokit.spike.e4.E13JReadOnly','--g-readonly','UNISSUED','a'*64],maxTextBytes=32768,id='E13J-R1-SUPPLEMENT-ONCE',scope='116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef');write(P/'request.json',request);tests.append(('unissued',[ps,'-NoProfile','-File',B/'tools/observe_j_only.ps1','-RequestPath',P/'request.json'],1))
for name,cmd,expected in tests:
 with (P/(name+'.stdout.txt')).open('xb') as so,(P/(name+'.stderr.txt')).open('xb') as se:
  child=subprocess.Popen([str(v) for v in cmd],stdout=so,stderr=se)
  try:code=child.wait(timeout=20)
  except subprocess.TimeoutExpired:write(P/(name+'.pending.json'),dict(pid=child.pid,parentRetainsSameProcess=True,killed=False));code=child.wait()
 write(P/(name+'.exit.json'),dict(argv=[str(v) for v in cmd],pid=child.pid,exitCode=code,naturalReturn=True));assert code==expected
assert 'J_EXECUTION_NOT_DISPATCHED_BEFORE_PROCESS' in (P/'unissued.stderr.txt').read_text(encoding='utf-8',errors='replace')
common='无真实5037/SDK/设备/旧handle/PID查询/处置/部署或产品重测；审批ABSENT、actualScope/release/once/sourceReview未签发。旧v17主PENDING、旧诊断LOST与H本地30384 RETURN_UNPROVEN三栏独立，未补ACK/退款。用户持续授权已存在，D1未过/M0未启、T07未派、P0/许可/历史FAIL保持。'
text(R/'docs/coder/D1_E13J_R1_FIXED_SOCKET_DELIVERY_V1.0.md',f'''# D1 E13J 三P1集中修复交付 V1.0

2026-10-18；依据E13I独立复审SHA250083aed28e914bd5d7eb67394fe3bdd69b87f48ec4f6a1f2fe75ed7fa330e7。完成应用IO前额度守卫、生产审账落盘与父诊断失败保管修复及有限验证，完整冻结交独立复审，不自批执行许可。

每query70656B实际应用RX＋保守TX意图、全batch262144B预算不变；每次read/write之前核剩余，read长度≤剩余，0余额连EOF也不偷读，不继续drain/强关/二reader/重试。同原Socket/keeper预算UNKNOWN持有，未用其他额度不借用。只限制应用层smart-socket/shell数据消费/意图，不声称限制OS缓冲/TCP头/网卡总流量。

生产原archive在原facts.txt有界保存P/T两切片各≤512B，总≤1024，原intent≤1024，query元数据仍2048B；计费/写进入返/late/资格/归还状态不依赖ICheck。audit失败强keeper保原对象，未知不二close；切片不自证自身close或最终caller PASS。生产Batch另在已有Java摘要额度中输出实际caller/物理返快照。

父pending write/console都受保护，无论其异常都进同原Popen wait；两原记录文件分别唯一close，UNKNOWN保父holder，不以诊断成功为条件。三组实际待日志故障探针同原child自然exit0/files close，资格仍失败。

一次生产host编译、9个直接有限组及三父故障组通过；未重跑I31全套或长测试。JAR {len(rows)}class=F183原字节＋{len(rows)-183}本批实测class，{pin(jar)['bytes']}B SHA{pin(jar)['sha256']}，检查类不混入。脚本AST/未派拒绝实测，observer原owner主体与F实际字节相同，无APK/Gradle/native或依赖变更。官方协议10份字节沿I固定commit复用，未重下载/宣称新SDK映射。

四文档/源码diff/原证据/JAR/脚本/完整ZIP/外seal及实际只读回执交审；原I和十二组历史seal成员保持不变。{common}
''')
text(R/'docs/coder/D1_E13J_R1_IMPLEMENTATION_CONTRACT_V1.0.md',f'''# D1 E13J IO与审账契约 V1.0

2026-10-18；最小修已有固定Socket/archive/父run，不增加通用框架。

F01 allowance在实际InputStream.read与OutputStream.write前执行。唯一reader下chargedWire=incomingWire+intendedTx；read传入min(wanted,remaining)，returned n才加实际RX；完整TX意图在写前扣费并入归档，writesEntered/Returned分栏。额度不足不执行该次read/write、不退款、不借第二条/其他预留。parse错误后的drain也同门控，余额0停止全部新IO、未知Socket不关闭，archive有限终止并审账，同原non-daemon keeper继续持有budgetUnknown；不会将未消费EOF当返回。最多两query串行，各wire70656+metadata2048，加base116736正好262144。原脚本/serial/白名单/同连接及第一真实归还后第二派生不变。

F02原writer在连接前建立intent和原facts文件。facts只有可选P（caller请求后首次可写切片）与T（reader结束/原writer尾通知返回后的切片），每条≤512，合≤1024；写入意图先计auditBytes，不按部分失败退款或重试。记录cw/in/tx/we/wr/rt/off/disk/rawQuota/frames/eof/exitSeen/exit/failed/late/qualification/budgetUnknown/readerBody/readerAlive/socketReturned/writerAlive/physical/why及auditOwnClose=UNPROVEN。cw是实际应用RX＋保守TX，rawQuota是帧长度预扣，不冒实际完整payload；off/disk是原queue/成功write事实，不冒power-loss耐久保证。

P/T是执行时点快照，P不保证恰在超时瞬间（writer可能先有原IO），T仍在原writer内，不能写自身join/close已证。无失败时qualification=SNAPSHOT_NOT_FINAL，失败/已超资格时FAILED；最终caller资格/各原线程真实join由生产Batch的有界J_PRODUCTION_RETURN_SNAPSHOT补充，落入既有外层Java32768B预留，不另分配query元数据。若迟到只发生在审账文件关闭后的caller调度阶段，不能回写旧切片冒当时已迟到，以该后续生产摘要登记。审账open/write/close失败保同原Op/keeper和计费内存，不以缺facts充成功；永不二close。

F03父holder在Popen/记录文件前登记；pending写入与print的任何BaseException只降资格并留有界诊断码，不越过finally内同原wait。wait本身未知继续原holder等待，不换Process；stdout/stderr分别尝试唯一close，任一未知则父仍持有而不再次close。只有同wait及两个文件close均已返，才可释放活动custody；最后诊断失败不改变这些已证事实或补资格。日志文件自身记录不自证其关闭。

审批pin ABSENT，正确角色在网络前拒绝；预算到限后可能永久UNKNOWN，不能承诺本批内自然收尾，也不通过kill/扩额处理。{common}
''')
text(R/'docs/coder/D1_E13J_R1_SELF_CHECK_REPORT_V1.0.md',f'''# D1 E13J 有限自检 V1.0

2026-10-18；host-001单次javac exit0。9组：OK、EXIT_NO_EOF、WRITE_FAIL、CHAIN_OK、CLOSE_PENDING、TAIL_PENDING、BUDGET_BOUNDARY、BUDGET_TX、PRODUCTION_AUDIT，另describe/未派拒绝和脚本AST/正确角色拒绝原回执。无生产修正后重编、无I31长回归、APK/Gradle/native。ICheck仅用peer helper及列出的6有限回归；其未选旧模式不是J验证结论，尤其不得手动运行旧I越限活Socket再kill求退出。

BUDGET_BOUNDARY直接调用真实生产readSome/drain，非网络计数InputStream实际读70656，最后read长度1024，随后read/EOF/drain次数增量0；同holder budgetUnknown、不标原返。没有allocate真实Socket或启动keeper，因此未制造永久未知活网络对象。BUDGET_TX以明确预置已收费前缀测剩2字节，实际write2后多写0；另剩1读1、多读0。该TX前缀是单位夹具预置，不冒已真实发送70654网络字节。生产方法/最终class与socket链测试同源字节，不是镜像预算门。

PRODUCTION_AUDIT真实生产Batch/Op/Archive两条本地peer，第一归还后严格派生第二；直接读取生产intent/facts/original.wire，未创建ICheck final-owner-facts。核cw=in+tx=wire文件长度、we/wr、quota/EOF/EXIT、actual pending/terminal切片和自身close未证、各metadata≤1024及batch总262144。归还后生产Batch摘要在原stdout显示physical/callerQualified，文件切片仍SNAPSHOT_NOT_FINAL，两个层不混同。

EXIT_NO_EOF/CLOSE_PENDING/TAIL_PENDING原扣住时不提前归还，释放后同原线程/Socket实际join并保首次失败；生产facts的late/FAILED可读。WRITE_FAIL仍实际socket＋archive组合，审账记录失败资格，不用测试额外facts充生产账。永久audit异常强keeper路径静态保留，不为自检制造永久未知活连接；原close永久异常非IO契约范围沿用I，不扩其证据结论。

parent-faults-002直接导入实际父run，唯一适配将wait资格改20ms，有限Python child睡350ms。PENDING_WRITE/CONSOLE/BOTH分别抛OSError，函数只在同原Popen自然wait/两文件close后以AssertionError报告资格失败；没有先逸出原日志异常、kill、daemon或换Popen，三组新UNKNOWN0。source原SHA及真实stdout/stderr/exit/diagnosticFailures原回执可核。

实际5037/SDK/旧handle/PID/设备0，仅本地临时peer；OS网络流量本身不属应用read硬门保证。{common}
''')
text(R/'docs/coder/D1_E13J_R1_E13G_SUPPLEMENT_PLAN_V1.0.md',f'''# D1 E13J 准确一次补充待派方案 V1.0

2026-10-18。三P1修复先独立整包复审，再由负责人另派准确一次G补充，不实际执行。APPROVED_REQUEST_SHA=ABSENT、scope/release/once/sourceReview均未签发；不得修改已冻结常量或从包内helper旁路执行。

未来固定Java/JAR/角色七项argv：D:/Android/Android Studio/jbr/bin/java.exe、-cp、D:/CodexProjects/VideoKit/docs/coder/d1e13j-r1/artifacts/e13j-host-tools.jar、com.videokit.spike.e4.E13JReadOnly、--g-readonly、准确typed release路径、其SHA。typed kind=e13jFixedReadOnlyRelease，原runtime SHA/serial HA1Q6WXR、独立review SHA、budget262144/requests2均准确绑定至新来源策略版本并再审。固定root D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE，once e13j-r1-g-readonly.once、wrapper id E13J-R1-SUPPLEMENT-ONCE、Java摘要cap32768，脚本/JAR/输入pins必须一致；现无可执行release。

固定127.0.0.1:5037、每条同原Socket先host:transport:HA1Q6WXR再shell,v2,raw:两既定模板，无SDK/kill/start/version/feature/fallback。首完整global activity processes＋ps，准确scope/batch/component/method、app UID10221及am UID2000/父/argv合格且原实际资源join后，才严格派生第二boot_id/stat/status/cmdline；无外填示例/旧PID。真实设备格式/权限未知、其他instrumentation、全量超64KiB即停止，不grep/追加查询。

总262144B保持：host8192+原exec65536+Java32768+observer8192+batch intent2048+两query各(wire70656+metadata2048)。每query stdout+stderr65536、帧256、service2048、FAIL256；wire应用实际RX＋保守TX前置核余额。0余额不再读EOF/drain，不强关原Socket；保预算UNKNOWN，不能借未发第二条/其他预留继续收尾、扩额或退款。TCP/IP头、OS缓冲和远端网卡流量不在硬控承诺。

生产facts每query P/T最多512各、总1024，intent1024，记录计费/写进返/late/资格与归还切片；快照不自证自身close/最终PASS，实际caller摘要用既有Java预留，原observer逐层持有。任何审账记录未知继续保原对象，不用ICheck丰富文件代替。预算UNKNOWN可能永久保管，需要未来另审处置，不能在本次profile强行收尾。

原exec42537未来另派最多一次空输入收取、≤10秒响应资格/≤65536B文本；接口若不能保证先BLOCKED，不循环/非空/Ctrl-C/重建session。空输出/工具返回不是原owner ACK；已采host19:31:58仍历史，不新增CIM预算。所有终止、部署、产品方法/T07另审，两个只读query不解除三旧UNKNOWN。{common}
''')
latest='> 2026-10-18 E13J最新安排：依据E13I复审3P1集中修应用IO前预算、生产有界审账及父诊断故障保管，有限自检通过后完整冻结交审。query70656/批262144约束实际应用RX＋保守TX，余额0不继续read/drain/强关，原owner预算UNKNOWN保管；不宣称控制OS/网卡总流量。审批ABSENT，真实5037/SDK/设备/旧handle/PID/处置0；三历史UNKNOWN独立，I及所有旧候选冻结，用户持续授权已存在，T07未派，D1未过/M0未启。\n\n'
for rel in ['docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 p=R/rel;t=p.read_text(encoding='utf-8');pos=t.index('\n')+1;text(p,t[:pos]+'\n'+latest+t[pos:].lstrip('\n'));shutil.copyfile(p,B/'reference'/p.name)
print(json.dumps(dict(status='PREPARED_J_REVIEW',jar=pin(jar),classes=len(rows),newClasses=len(rows)-183,compileAttempts=1,parentFaultGroups=3),ensure_ascii=False))
