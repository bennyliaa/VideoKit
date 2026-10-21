from pathlib import Path
import json,hashlib,zipfile,difflib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';OLD=R/'docs/coder/d1e13f';A=B/'artifacts'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
assert not (E/'e13h-freeze.json').exists()
for row in json.loads((E/'host-001/inputs.json').read_text()):assert pin(R/row['path'])==row
for mode in ['SUCCESS','TIMEOUT','POLICY','WRITE_FAILURE']:assert json.loads((E/'host-001'/(mode+'.exit.json')).read_text())['exitCode']==0
assert json.loads((E/'final-002/results.json').read_text())['status']=='PASS_LIMITED_OFFLINE_PREPARE_PRODUCTION_DISABLED'
base=json.loads((E/'host-001/base-inputs.json').read_text());classes=[];jar=A/'e13h-host-tools.jar';C=B/'.checks/host-001'
oldManifest=json.loads((OLD/'evidence/host-jar-manifest.json').read_text());mapping={x['entry']:x for x in oldManifest['classes']}
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as out,zipfile.ZipFile(A/'e13f-reviewed-base.jar') as z:
 for n in z.namelist():
  raw=z.read(n);row=mapping[n];assert hashlib.sha256(raw).hexdigest()==row['sha256'];out.writestr(n,raw);classes.append(dict(entry=n,bytes=len(raw),sha256=row['sha256'],source=row['source'],origin='BYTE_IDENTICAL_REVIEWED_E13F'))
 for p in sorted(C.rglob('E13GReadOnly*.class')):
  n=p.relative_to(C).as_posix();raw=p.read_bytes();out.writestr(n,raw);q=E/'actual-tested-class-bytes'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);classes.append(dict(entry=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),source=pin(B/'tools/E13GReadOnly.java'),origin='ACTUAL_HOST_001_TESTED_BYTES'))
write(E/'host-jar-manifest.json',dict(jar=pin(jar),classes=classes,baseClassCount=183,newClassCount=len(classes)-183,oldClassesRecompiled=False,hostCompileAttempts=1,testClassesIncluded=False))
for p in C.rglob('HCheck*.class'):
 q=E/'actual-fixture-class-bytes'/p.relative_to(C);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
before=(OLD/'tools/observe_original.ps1').read_text(encoding='utf-8-sig');after=(B/'tools/observe_g_only.ps1').read_text();marker='# Same original local context';assert before[before.index(marker):]==after[after.index(marker):]
text(E/'observe-g-only.ps1.diff',''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='FROZEN_E13F/observe_original.ps1',tofile='E13H/observe_g_only.ps1')))
write(E/'script-binding.json',dict(script=pin(B/'tools/observe_g_only.ps1'),reviewedOriginal=pin(OLD/'tools/observe_original.ps1'),ownerBodyByteIdentical=True,actualTests='final-002',publicRole='G_ONLY_REFUSES_BEFORE_PROCESS',sameSourceAsTested=True))
write(E/'local-probe-environment-history.json',dict(status='FIRST_LOCAL_VERSION_PROBE_UNQUALIFIED_RETAIN_UNKNOWN',initial='host-001/VERSION_OK.pending.json',pid=30384,pythonWaitSeconds=15,killedByCoder=False,followup='One jcmd30384 Thread.print returned no such process; not original product PID and no original product handle accessed',naturalExitAck='UNPROVEN',readerCloseAck='UNPROVEN',cause='NOT_UNIQUELY_DETERMINED; same compiled bytes passed ephemeral-loopback test with approved sandbox escalation',laterTests='final-002 real captured natural exit0; earlier missing exit not retroactively filled',notOldLostDiagnostic=True))
write(E/'protocol-source-and-binary-binding.json',dict(sdkBinary=dict(path='D:/Android/SDK/platform-tools/adb.exe',bytes=8273560,sha256='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f'),sdkExecuted=False,officialHeader='https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/adb.h',officialCandidateProtocolConstant=41,wireHex='0029',candidateSource='AOSP ADB_SERVER_VERSION constant, not Pkg.Revision37.0.1 or 1.0.41 version-string inference',exactSdkBuildToOfficialSourceMapping='UNPROVEN',clientKillStartSource='https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/android15-qpr2-s8-release/client/adb_client.cpp',socketLocalitySource='https://android.googlesource.com/platform/packages/modules/adb/+/refs/tags/android-mainline-11.0.0_r31/socket_spec.cpp',androidDumpSource='https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android12-release/services/core/java/com/android/server/am/ActivityManagerService.java',sourceReadMethod='Official web source search results; direct source download failed DNS, no copied source claimed',remainingServerReplacementRace=True,productionEnabled=False))
write(B/'release-plan.json',dict(status='PREPARE_ONLY_DIRECT_ADB_DISABLED',actualExecution='NOT_RUN',adbStarts=0,actual5037Connections=0,originalExecReads=0,termination=0,scope=E13Scope if False else 'aeefe32f-816d-4c0b-aca7-16f76dbd45ff',runtimeSha='116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef',twoDeviceCommands='First fixed full activity-processes dump + full ps; second only same scope verified app/am PID proc stat/status/cmdline',futureOriginalExec42537=dict(emptyReadsMax=1,responseQualificationSeconds=10,retries=0,notReturnAck=True,outputReservation=65536),budget=dict(totalBytes=262144,previousHostAndReceiptReservation=8192,deviceClients=2,deviceEachBytes=65536,deviceEachQualificationSeconds=10,versionQueries=1,versionBytes=1024,versionQualificationSeconds=2,outerJavaStdoutStderrReservation=32768,observerFactsConsoleReservation=8192,originalSessionReservation=65536,allocatedBytes=246784,unallocatedBytes=15360),sourceReview=None,actualScope=None,actualRelease=None,actualOnce=None,independentReview='PENDING',D1='NOT_PASSED',M0='NOT_STARTED'))
common='本轮ADB/实际5037/原exec42537读取/设备/处置/安装/部署/方法重测均0。旧主任务最后PENDING/UNKNOWN，独立诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN未解除，实际根因NOT_UNIQUELY_DETERMINED。E13F及历史冻结不改；用户持续设备授权已存在，当前限制来自准确范围与原任务未决。D1 NOT_PASSED / M0 NOT_STARTED，T07未派、P0/许可保持。'
text(R/'docs/coder/D1_E13H_READONLY_ENTRY_DELIVERY_V1.0.md',f'''# D1 E13H 最小只读入口准备交付 V1.0

2026-10-18；依据负责人E13H正式派单及server补充。本包是离线准备候选：固定两组argv/证据身份门、现有原owner组合链、本地版本前置原型与拒绝门有限自检通过，**生产直ADB入口保持禁用**。不得把此包作为E13G补充执行许可或可立即执行的设备核查方案。

新增E13GReadOnly Java角色；旧183生产class逐字节复用E13F，不重编。一次必要javac仅编新增Java及HCheck；最终JAR共{len(classes)}成员，其中{len(classes)-183}新增生产成员与实际测试class字节相同。observer_g_only.ps1仅收窄固定G角色/根/范围，并在Process/网络前强制拒绝；其原Process/readers/archive/异常custody主体与既审E13F逐字节相同，无新通用框架。未编APK/Gradle/native，无Maven或native依赖变化，E13F app19/fixture3保持原样。

SDK仅静态pin b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f，未执行。官方AOSP ADB_SERVER_VERSION=41是协议候选来源，不从37.0.1软件版本猜测；准确SDK编译源码/协议映射仍UNPROVEN。AOSP客户端在server版本不匹配时含kill/start路径，-H127.0.0.1也不能排除版本替换窗口。新增固定host:version预检仅信息前置，不能绝对保证随后adb.exe无重启。因此Java及PowerShell正确角色也在任何owner/Process/网络前拒绝。另审替代方案见准确执行方案，尚未实现、尚未批准，未扩大为通用ADB客户端。

两固定设备命令、总预算及原exec一次≤10秒收取仅未来草案；生产current actualScope/release/once/sourceReview均null。全文原始回执、单次编译、有限测试、183旧class来源及新class实测字节、脚本diff/版本来源局限、失败历史/四文档/正式需求均封包，外seal及最终只读回执另附。最终JAR {pin(jar)['bytes']}B SHA{pin(jar)['sha256']}。

{common}
''')
text(R/'docs/coder/D1_E13H_IMPLEMENTATION_CONTRACT_V1.0.md',f'''# D1 E13H 固定只读角色契约 V1.0

2026-10-18。公开main只接受--describe或--g-readonly；后者无参数可传exe/serial/PID/shell，因无法排除server替换重启路径在创建owner/网络前硬拒绝。PowerShell也只接受准确Java/JAR/G角色/固定根/原scope、32768B host cap并硬拒绝，旧case/deploy角色拒绝。所有下面的组合链和前置目前仅包内离线原型，不能从公开CLI绕入；不是新可用产品入口。

固定argv1：SDK adb.exe -H127.0.0.1 -P5037 -sHA1Q6WXR shell -T，最后单一固定脚本完整dumpsys activity processes及ps -A -w -o UID,PID,PPID,NAME,ARGS，显式AM/PS begin/end和exit码。无截取/grep/部分行充完整；超过64KiB/10秒、非零/格式不识别/权限拒绝/其他active instrumentation即停止。大设备完整AM输出可能超64KiB，这种情形只拒绝，不追加命令或提高cap。实际API31格式与/proc权限未验证。

第二argv不能输入PID，由完整第一raw推导：唯一全局active instrumentation组件、mFinished=false、准确原runtime SHA/原batch D1-E13A-SOURCE-20261018/class/method；对应原mRunningProcesses中的com.videokit.app/u0a221必须与全局ps中UID10221/准确name/args/存在父进程一致。原am客户端须UID2000及准确完整scope argv、有效shell父UID。仅选择这两个明确角色PID；不能因未选择fixture/codec断言它们不存在或已归还。重复/缺失/异UID或其他instrumentation拒绝。

argv2只拼接已验证正整数PID到固定/proc路径，读取boot_id及这两个PID的stat/status/cmdline，逐项shell失败退出；检查完整边界、同PID/PPID/全四UID/准确argv/正start ticks。新start ticks与boot_id是第二切片身份，不证明两次间绝无复用，更不构成终止授权。未知/proc拒绝不fallback，不任意shell注入。

组合Chain先持有原supervisor并retainAuthority(同Chain)再启动child，沿用既审E9PcSupervisor Process/唯一reader、8×4096 archive、E4Owned close/actual原线程join。第一命令或解析失败/超资格，不第二命令，finally closeIngressAndSupervise可交isolation，非daemon原custodian继续保管同原对象。生产没有接出可执行once/审批入口，不会绕过旧pending gate；旧DISPOSITION_SHA ABSENT保持。

版本原型仅host:version、生产默认127.0.0.1:5037，单次≤1KiB/2秒资格；按固定OKAY+0004+4hex解析候选0029，不接受任意服务。E4Owned原Socket与唯一reader/非daemon keeper在allocate前登记；调用者超时不关在途socket，keeperjoin实际reader后才退责任，close未知继续保管，不二close。测试仅显式包内临时端口影子，生产CLI拒绝所以原型未连实际server。其输出与request共≤28B远低1KiB，未知/不完整/版本不匹配拒绝。未把预检插入生产dispatch，也未把候选41冒确切SDK构建证明。

无新产品安全ACK、无OS沙箱承诺、无行政终止记录。{common}
''')
text(R/'docs/coder/D1_E13H_SELF_CHECK_REPORT_V1.0.md',f'''# D1 E13H 有限离线自检 V1.0

2026-10-18。单次host-001 javac exit0；现有183class全沿用准确E13F JAR，未重编旧源。新增生产class来自同一次编译的实测字节，HCheck替身class另存、不进最终JAR。

host-001 SUCCESS/TIMEOUT/POLICY/WRITE_FAILURE四组自然exit0：实际包内Chain用原监督器/唯一reader/archive，命令唯一替成有限本地JVM，不运行SDK。成功两child原返；50ms短超时后同原PC继续保管、第二0，释放本地fixture后原自然返仍不改首次资格。拒exe/serial/argv/scope/UID/截断/其他instrumentation/启动ticks/父身份错误，正确生产CLI也拒绝。写失败直接注入原archive IO，实际原文件close一次、失败不改成功；这是archive直接测试，不冒完整公开链磁盘故障动态证明。

host-001的首VERSION_OK等待15秒未完成，记录pending(pid30384,killed=false)，Python自然抛TimeoutExpired；后一次仅对这个本地测试PID作jcmd Thread.print返回no such process，未读任何旧产品PID/handle。该probe原exit/readers close缺失仍UNPROVEN，原因NOT_UNIQUELY_DETERMINED，不因进程不在而补自然exit/closeACK，不混入旧诊断LOST。受限环境内没有通过证据；同一字节获临时本地端口权限后检查成功支持环境相关性，但不声称已唯一定位。初始失败未被涂成PASS。

final-002在明确仅自身临时127.0.0.1端口的权限下完成VERSION_OK/BAD/TIMEOUT三组原始stdout/stderr/自然exit0，不重编。实际一服务包、错协议拒绝；50ms未返时同socket/reader/keeper强持且不close，释放测试peer后同线程/socket自然结束。无5037连接、无ADB启动；协议候选响应不是确切SDK协议证明。另有describe/public拒绝、完整PowerShell AST parse、正确角色禁用/错exe/旧产品角色拒绝三组实际回执，生产body未执行；脚本原owner主体与E13F逐字节比较通过。

初次官方源码直接下载DNS失败，未冒下载成功/完整源码pin；协议及隐式kill/start仅引用官方web源码及确切SDK文件pin，二者编译对应未证，所以生产硬拒绝。未做Android/Gradle/native编译或旧长套件。{common}
''')
text(R/'docs/coder/D1_E13H_E13G_SUPPLEMENT_PLAN_V1.0.md',f'''# D1 E13H 准确E13G补充方案待审 V1.0

2026-10-18；本包准备入口而非执行批准。当前方案BLOCKED_DIRECT_ADB_SERVER_REPLACEMENT_RACE_AND_SDK_PROTOCOL_MAPPING。不能发本包--g-readonly然后期待设备查询；Java与脚本都会在Process/网络前拒绝。E13G已fresh证实原host身份切片，不重复CIM、不循环观察，不据旧PID实施终止。

## 两条准确设备argv

第一固定数组及完整最后shell脚本见E13GReadOnly.INVENTORY和--describe原回执（host-001编译、final-002 describe）；无外部参数扩展。第二只允许第一完整证据匹配的app及am PID，生成的准确数组在host-001/SUCCESS/approved-argv-2.txt，仅本地fixture示例不能用于真实PID。实际两设备数组应在未来单一准入批次先固定第一，校验第一实际raw SHA/完整性/同scope身份后据模板定稿第二；不提供任意PID CLI，不从旧14763/14765/14779填参。

完整global活动instrumentation/进程来自dumpsys activity processes及ps，不能将filtered/截断当完整；64KiB不够或10秒资格失败则停止保管，不重试/追加第三条。第二包含boot_id/stat启动ticks/status UID/PPID/原cmdline，缺权限/变化则UNKNOWN停止。只读证据不等于旧owner返回，不能将PID消失当归还。fixture/codec等未精确匹配角色仍未知。

## server限制与待批替代

官方adb_client.cpp的协议不匹配分支会kill/start；版本检查与随后SDK新连接之间仍有可替换窗口，固定-H不能绝对排除。官方头ADB_SERVER_VERSION41只是候选协议来源，SDK准确构建映射未证，不能据软件版本37.0.1放行。本地host:version前置原型已有限验证，但生产未启用，也不能消除此竞态。官方证据链接及SDK byte pin见evidence/protocol-source-and-binary-binding.json。

建议负责人另审的最小替代范围：固定127.0.0.1:5037的一次host:version仅信息前置；后续每条采用已存在server的一条原socket，固定serial transport再固定shell-v2服务，完整处理同一原连接上的stdout/stderr/exit framing并复用原有有界归档/真实线程归还。该路径不调用adb.exe的version-mismatch kill/start分支，但与“必须由SDK adb.exe执行”的原要求不同，须明确变更并独立审查，当前未实现。不得变成任意ADB host service/serial/shell客户端，也不发host:kill或启动server；server缺席/不兼容/替换后未知均拒绝。不把协议内部transport握手冒额外设备shell，仍最多两条固定设备命令。需要审清同连接生命周期、失败保管、shell-v2界限和预算后才能实施；本文件不自行扩范围。

## 单次收取与预算

原exec42537未来最多一次空输入收取，响应资格改为≤10秒，不循环、不发Ctrl-C/非空输入、不重建session。本轮0次。原工具实际响应超资格仍记未决，不靠取消Promise或抛弃原handle制造截止；即使空输出/工具返回，也不是原Java/ADB/reader/pipe/Android ACK。原返回资格及case失败不改，若接口不能限制文本则不启动，记BLOCKED。

总256KiB独立批次草案：已采host及原父工具保守8192B；两设备原raw各65536B（共131072）；一次server前置1024B/2秒；原exec收取预留65536B；外层Java stdout/stderr预留32768B（不重复echo设备raw，只输出摘要和保管facts）；observer facts console8192B。共246784B，保留15360B。重复console实际输出也计入相应预留；不得将同raw复印无限排除计账。若原session工具无法保证65536B以内或其他wrapper实际将超过剩余，停止、不提额、不将未消费余额转供处置。

每设备命令64KiB/10秒是资格，不是同步调用强制终止；原Socket前置1KiB/2秒亦同。一次intent/准确review/pins、预算账和执行批次尚未签发，当前actualScope/release/once均null。未来替代实现受审前，原exec单次收取也必须负责人另派，不能由本文件自动开始。A/B收尾选择和所有终止动作仍另审；无Androidfresh启动身份时不可定稿终止。

{common}
''')
latest='> 2026-10-18 E13H最新安排：仅离线准备G-only固定只读入口，新增server协议前置原型及有限回归完成，生产直ADB入口因server替换重启竞态和准确SDK协议映射未证而硬拒绝，完整冻结交审；不是设备执行许可。原exec42537最多一次空读≤10秒仅待另派，本轮未读取。E13F限定离线通过及历史候选保持冻结；旧主PENDING/诊断LOST未解除，T07未派。用户已有持续测试授权，当前限制源于原任务未决和本阶段范围；D1未过/M0未启。\n\n'
for rel in ['docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 p=R/rel;t=p.read_text(encoding='utf-8');at=t.index('\n')+1;text(p,t[:at]+'\n'+latest+t[at:].lstrip('\n'));shutil.copyfile(p,B/'reference'/p.name)
print(json.dumps(dict(status='PREPARED_DISABLED_E13H',jar=pin(jar),classes=len(classes),old183ByteIdentical=True,deviceCalls=0),ensure_ascii=False))
