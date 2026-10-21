from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';scope=json.loads((B/'release/execution-scope.json').read_text());release=B/'release/read-only-release.json';sha=hashlib.sha256(release.read_bytes()).hexdigest();budget=json.loads((E/'final-static-002/outer-budget.stdout.txt').read_text(encoding='utf-8-sig'));members=json.loads((E/'jar-member-difference.json').read_text());assert budget['totalUpperBound']==8157 and members['unchangedMembers']==192
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def text(p,s):p.write_text(s,encoding='utf-8')
launch=B/'release/launch_once.ps1';observer=B/'policy/observe_e13k.ps1';request=B/'release/observer-request.json'
record=dict(status='SELF_VERIFIED_AWAITING_INDEPENDENT_MECHANICAL_CHECK',functionalReview=scope['review'],mechanicalReview=None,batch=scope['batch'],originalScope=scope['originalScope'],runtimeScopeSha256=scope['runtimeScopeSha256'],release=pin(release),scope=pin(B/'release/execution-scope.json'),executionCommandRequest=pin(B/'release/execution-command.json'),observerRequest=pin(request),jar=members['jar'],observer=pin(observer),launch=pin(launch),budgetUpperBound=8157,outerAllocation=8192,remainingOuter=35,totalAllocation=262144,ownerBodyByteIdentical=True,memberComparisons=193,unchangedClassMembers=192,changedClassMembers=members['changedMembers'],strategyCompileAttempts=1,sourcePolicy=pin(B/'policy/E13JReadOnly.java'),actualExecution=False,actual5037Connections=0,SDKStarts=0,oldHandleReads=0,noReviewCycle=True)
(E/'final-binding-receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
common='本轮仅发布绑定准备和机械自检，未运行launch、有效--g-readonly或observer原owner，不真实5037/设备/SDK/旧handle/PID/处置。三历史UNKNOWN独立不补ACK，D1未过/M0未启、T07未派、P0/许可与原v17边界保持。功能review沿已通过R1，本次机械验核另存，不自循环。'
text(R/'docs/coder/D1_E13K_RELEASE_BINDING_DELIVERY_V1.0.md',f'''# D1 E13K 一次只读发布绑定交付 V1.0

2026-10-18；功能基线E13J-R1 review SHA {scope['review']}。唯一新执行批次{scope['batch']}，originalScope={scope['originalScope']}，typed release.scope仍原runtime SHA{scope['runtimeScopeSha256']}，三种身份分栏，非新产品instrumentation scope。

typed e13jFixedReadOnlyRelease精确6字段、258B，SHA{sha}；review指完整R1功能复审，不引用未来K验核。一次必要host编译只编准确策略与纯检查类；最终JAR193成员中192原字节不变，只有E13JReadOnly外class的批准SHA/describe策略常量改变。反汇编仅归一准确SHA、CP索引和水平对齐空格后，所有指令/偏移/分支/成员完全相同，Socket/archive/identity/限额和nested业务class原样；检查类不进JAR。

新observer只绑定release SHA、准确JAR路径、固定observer-request路径/SHA，原owner主体字节不变。固定最小request只有一个JAR pin，新executionBatch/originalScope记录进原intent。scope文件、release、request、最终JAR/observer由固定launch哈希检查准确绑定；无任意参数入口。launch只收取一次原observer console，返回≤128B状态/摘要，不再次全量echo；此调用层机械输出控制不修改原Process/reader/文件custody。

外层全部输入与原记录/副本保守上界8157B，原8192内余35，总262144不增。准确source及PS序列化/25错误码并集/4metadata记录/固定运行时80字type名保留与早期gate错误路径在原回执，非任意pins/任意用户异常保证。

最终JAR {members['jar']['bytes']}B SHA{members['jar']['sha256']}。四文档、准确输入/argv、机械回执、193成员差异、脚本diff、原始编译/核验记录、外seal/ZIP及只读verify完整交tester机械核验。tester PASS后依负责人已明确的这一次只读授权交执行窗口，不再转功能实现循环；coder本轮不执行。{common}
''')
text(R/'docs/coder/D1_E13K_BINDING_CONTRACT_V1.0.md',f'''# D1 E13K 精确绑定与外层额度契约 V1.0

2026-10-18。唯一执行batch {scope['batch']}，originalScope aeefe32f-816d-4c0b-aca7-16f76dbd45ff，typed scope原runtime SHA116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef。release.kind=e13jFixedReadOnlyRelease、serial HA1Q6WXR、review={scope['review']}、budget262144、requests2，真实E9Record.parse/canonical字节及实际最终JAR反射常量自检通过。

依赖无环：功能review→release SHA→Java策略/JAR→scope及observer request→observer精确request gate→launch固定各文件hash→外置机械receipt。release不含未来机械回执SHA，scope与request记录唯一batch，但不改变受审typed6字段/目标scope。正向observer preflight只执行到owner标记之前，不调用进程/Socket。

原R1 root D:/CodexProjects/VideoKit/docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE、once e13j-r1-g-readonly.once、wrapper E13J-R1-SUPPLEMENT-ONCE保持。任何已有/未知once或记录/第一查询失败、其他instrumentation、预算UNKNOWN均停止，不换目录/id重发，不强关。角色只固定transport HA1Q6WXR＋两既定shell-v2；无SDK/host:kill/start/version/feature/fallback，业务192class不变。

外层8192份额：release258＋scope407＋request831＋原intent951＋PID152＋pending150＋receipt2006＋原facts console2942＋外层准确command request204＋framing/marker/≤128B摘要预留256=8157，余35。25固定错误码保守并集（含互斥项）、4metadata记录、uint64宽度、固定PS/.NET异常家族80字typename保留；不是允许注入任意异常类型/任意长pins。早期gate无原owner/文件时，全部输入加2048错误console上界3748，不能与不可能同时生成的完整receipt路径混加后要求扩大额度。

原完整console在同一PS调用栈收取，不再次echo/复制原文；launch摘要r=原allOriginalResourcesReturned，m=原metadataRecordFilesReturnedAtConsole，h=收取console SHA256。它只转述原观察器结果，不合成close；receipt文件仍不自证自身close。若原observer未返，其全局原custody继续持有，launch亦不返回摘要，不取消/强关。不得改成直接工具全量echo或另加原文副本；必须用固定launch入口。

网络/原exec/Java/Batch/query其他份额原样，总262144无增。原exec42537一次空读≤10秒/65536B由执行窗口判断接口保证；不能保证仍BLOCKED，不借其额度。{common}
''')
text(R/'docs/coder/D1_E13K_MECHANICAL_CHECK_REPORT_V1.0.md',f'''# D1 E13K 机械自检 V1.0

2026-10-18；一次策略javac exit0，R1业务源未重编。实际193成员逐个核，192完全相同，仅E13JReadOnly.class变化；包括新编出的nested3类也逐字节相同。真实javap -p -c -constants只消去准确SHA/CP数字索引/水平对齐空格后完全一致，保留所有指令偏移和分支目标，不把字节比较不等隐写成等。

最初文本断言未归一javap CP数字宽度引起的两处对齐空格，曾报NON_POLICY_DISASSEMBLY_DIFFERENCE；原javap输出/原build工具保留。后续仅完善文本归一证明，没有再编译或改业务。真实E9Record精确解析/重序列化及实际最终JAR反射批准常量通过；describe安全执行，不运行有效dispatch。

脚本完整AST、真正生产policy前缀（owner分配标记之前）精确RequestPath/hash/JAR pin/批准字段通过；仅摘要代码对明确合成JSON验证≤128B，没执行launch或Process owner。原observer owner主体同R1实际字节相同。outer-budget真实PS序列化保守上界8157、余35，原始stdout/stderr/exit、机械绑定receipt保存。

没有Socket peer测试、APK/Gradle/native、SDK或长套件；不拿已过功能再循环。这里只是coder机械自检，等待tester独立机械PASS；无新执行结果或UNKNOWN。{common}
''')
text(R/'docs/coder/D1_E13K_EXECUTION_PLAN_V1.0.md',f'''# D1 E13K 唯一一次G补充精确入口与停止门 V1.0

2026-10-18；准备完成，待独立机械核验PASS后执行窗口承接负责人明确的一次授权，coder本轮不执行，不再功能循环。

新batch {scope['batch']}；originalScope={scope['originalScope']}，runtime SHA={scope['runtimeScopeSha256']}；typed release SHA={sha}，功能review={scope['review']}。准确最终JAR SHA={members['jar']['sha256']}，完整文件hash由evidence/final-binding-receipt.json及外seal固定，非任何旧I/J入口。

唯一外层调用（必须先比对完整包与launch SHA，不旁路helper）：C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe -NoProfile -File D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/launch_once.ps1。launch无用户参数，先核release/scope/request/JAR/observer5个准确hash，再调用准确policy/observe_e13k.ps1 -RequestPath release/observer-request.json，原完整console只收一次并输出≤128B转述摘要，禁止再echo原文以免重复计账。

内部准确argv：D:/Android/Android Studio/jbr/bin/java.exe、-cp、D:/CodexProjects/VideoKit/docs/coder/d1e13k/artifacts/e13k-host-tools.jar、com.videokit.spike.e4.E13JReadOnly、--g-readonly、D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/read-only-release.json、{sha}。root/once/id保持R1值，不改名/换目录；输入pins只能准确这一项JAR，request路径/SHA在observer头硬绑定。

两query固定127.0.0.1:5037/serialHA1Q6WXR，各同一原Socket transport→shell-v2，第一完整/无其他instrumentation/实际原资源join后才派生第二，不能输入示例PID。每query实际应用RX＋保守TX70656、通道合65536、metadata2048、帧256/10秒资格。预算耗尽不探EOF/drain/强关，保原UNKNOWN；第一任何失败/占用/UNKNOWN不第二，未花第二或原exec额度不能借。全部profile262144，外层输入/输出8157≤8192含重复receipt/console，明细见契约。

原exec42537仍独立最多一次空输入，接口无法保证≤10秒/≤65536则BLOCKED，不能取消Promise/循环/非空/Ctrl-C/重建session或借额；空返回不等原owner ACK。已采host19:31:58仍历史，不加CIM。两个只读结果只用于当前状态/收尾方案，不处置/安装/部署/续产品/T07。三历史UNKNOWN独立，所有未知额度不退款。

派单前/机械PASS后校验准确新输入、最终Jar/script/launch SHA、root/once/id、所有预留与原保管交接；任一变化/未知即停止。新的机械核验报告另存，不反写release.review形成循环。{common}
''')
latest='> 2026-10-18 E13K最新安排：R1限定离线通过后，只做唯一一次G补充的准确release/新batch/JAR/observer/launch机械绑定。193成员中192原字节不变，外层输入/记录/console合8157≤8192，总262144不扩，原R1 root/once/id保持。当前准备整包交独立机械核验，coder无真实5037/设备/旧handle；tester PASS后按负责人明确的一次只读授权承接执行，不再功能循环。第一失败/占用/UNKNOWN不第二；原exec保证不足仍BLOCKED，不借额/强关。三UNKNOWN及D1未过/M0未启/P0许可保持。\n\n'
for rel in ['docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 p=R/rel;t=p.read_text(encoding='utf-8');i=t.index('\n')+1;text(p,t[:i]+'\n'+latest+t[i:].lstrip('\n'));shutil.copyfile(p,B/'reference'/p.name)
print('Prepared K documents and final mechanical receipt; launch not executed')
