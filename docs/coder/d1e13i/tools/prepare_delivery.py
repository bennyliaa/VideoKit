from pathlib import Path
import json,hashlib,zipfile,difflib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';F=R/'docs/coder/d1e13f';H=R/'docs/coder/d1e13h';C=B/'.checks/host-001';A=B/'artifacts'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8')
assert not (E/'e13i-freeze.json').exists()
for row in json.loads((E/'host-001/inputs.json').read_text()):assert pin(R/row['path'])==row,row['path']
assert json.loads((E/'host-001/results.json').read_text())['status']=='PASS_FINITE_FIXED_SOCKET_OFFLINE'
assert json.loads((E/'supplement-002/results.json').read_text())['status']=='PASS_SUPPLEMENT_FINAL_PRODUCTION_BYTES_UNCHANGED'
base=json.loads((F/'evidence/host-jar-manifest.json').read_text());sourceRows={x['source']['path']:x['source'] for x in base['classes']}
for name,row in sourceRows.items():
 p=R/name;assert pin(p)==row;q=B/'baseline-source'/p.relative_to(F);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
write(E/'base-jar-source-manifest.json',dict(jar=base['jar'],copiedJar=pin(A/'e13f-reviewed-base.jar'),sources=list(sourceRows.values()),classes=183))
production=['E13IIdentity','E13IArchive','E13ISocket','E13IReadOnly'];jar=A/'e13i-host-tools.jar';rows=[];oldRows={x['entry']:x for x in base['classes']}
with zipfile.ZipFile(jar,'x',compression=zipfile.ZIP_DEFLATED) as z,zipfile.ZipFile(A/'e13f-reviewed-base.jar') as old:
 for n in old.namelist():
  raw=old.read(n);r=oldRows[n];assert hashlib.sha256(raw).hexdigest()==r['sha256'];z.writestr(n,raw);rows.append(dict(entry=n,bytes=len(raw),sha256=r['sha256'],source=r['source'],origin='UNCHANGED_REVIEWED_E13F'))
 for p in sorted(C.rglob('*.class')):
  if p.stem.split('$')[0] not in production:continue
  n=p.relative_to(C).as_posix();raw=p.read_bytes();z.writestr(n,raw);q=E/'actual-tested-production-class-bytes'/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);rows.append(dict(entry=n,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),source=pin(B/'tools'/(p.stem.split('$')[0]+'.java')),origin='ACTUAL_HOST_001_TESTED_BYTECODE'))
write(E/'host-jar-manifest.json',dict(jar=pin(jar),classes=rows,unchangedFClassCount=183,newProductionClassCount=len(rows)-183,productionCompileAttempts=1,testOnlyExtraProbeCompiles=1,productionRecompiledAfterTests=False))
for label in ['host-001','supplement-002']:
 for p in (B/'.checks'/label).rglob('*.class'):
  if p.stem.split('$')[0] in production:continue
  q=E/'actual-fixture-class-bytes'/label/p.relative_to(B/'.checks'/label);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
diffs=[]
for name,old in [('E13IIdentity.java',H/'tools/E13GReadOnly.java'),('E13IArchive.java',F/'tools/E13OperationArchive.java'),('E13ISocket.java',None),('E13IReadOnly.java',None),('observe_i_only.ps1',F/'tools/observe_original.ps1'),('check_host.py',H/'tools/check_host.py'),('ICheck.java',H/'tools/HCheck.java')]:
 p=B/'tools'/name;q=E/'diffs'/(name+'.diff');text(q,''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True) if old else [],p.read_text(encoding='utf-8-sig').splitlines(True),fromfile=old.relative_to(R).as_posix() if old else '/dev/null',tofile=p.relative_to(R).as_posix())));diffs.append(dict(source=pin(p),baseline=pin(old) if old else None,diff=pin(q)))
write(E/'source-derivation.json',dict(files=diffs,newFramework=False,oldFClassesUnchanged=True))
old=(F/'tools/observe_original.ps1').read_bytes();new=(B/'tools/observe_i_only.ps1').read_bytes();marker=b'# Same original local context';same=old[old.index(marker):]==new[new.index(marker):];assert same
write(E/'script-binding.json',dict(script=pin(B/'tools/observe_i_only.ps1'),old=pin(F/'tools/observe_original.ps1'),ownerBodyActualBytesIdentical=True,actualTests='supplement-002',releaseSha='ABSENT'))
commit='1cf2f017d312f73b3dc53bda85ef2610e35a80e9';mapping={'adb_io.cpp':'adb_io.cpp','adb.h':'adb.h','NOTICE':'NOTICE','daemon_services.cpp':'daemon/services.cpp','daemon_shell_service.cpp':'daemon/shell_service.cpp','docs_dev_protocol.md':'docs/dev/protocol.md','docs_dev_services.md':'docs/dev/services.md','shell_protocol.h':'shell_protocol.h','shell_service_protocol.cpp':'shell_service_protocol.cpp','sockets.cpp':'sockets.cpp'}
protocol=[]
for name,path in mapping.items():
 p=B/'reference/protocol'/name;assert p.stat().st_size>0;protocol.append(dict(**pin(p),commit=commit,repositoryPath=path,url='https://android.googlesource.com/platform/packages/modules/adb/+/'+commit+'/'+path+'?format=TEXT'))
write(E/'protocol-source-manifest.json',dict(status='EXACT_OFFICIAL_SOURCE_BYTES',commit=commit,metadata=pin(B/'reference/protocol/commit.json'),files=protocol,whitelist=['host:transport:HA1Q6WXR','shell,v2,raw:<fixedScript>'],versionServiceUsed=False,protocol='Client/server smart socket, not ADB aproto 24-byte daemon transport',littleEndianScope='Android API31 arm64 little-endian shell uint32 length; header/native uint32 implementation pinned',optionalFailedOverview='HTTP NOT_FOUND produced0B, not source authority'))
excerpts=[]
for name,start,end in [('adb_io.cpp',37,74),('docs_dev_services.md',44,49),('docs_dev_services.md',171,174),('shell_protocol.h',38,63),('shell_protocol.h',96,108),('shell_service_protocol.cpp',31,67),('daemon_services.cpp',86,123),('daemon_shell_service.cpp',784,792)]:
 p=B/'reference/protocol'/name;lines=p.read_bytes().splitlines(keepends=True);raw=b''.join(lines[start-1:end]);q=B/'reference/protocol-excerpts'/(name+'-'+str(start)+'-'+str(end)+'.txt');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);excerpts.append(dict(source=pin(p),firstLine=start,lastLine=end,excerpt=pin(q)))
write(E/'protocol-excerpt-manifest.json',dict(excerpts=excerpts,wholeSourcesAboveAreAuthority=True))
budget=dict(total=262144,previousHostAndConsole=8192,originalExecReservation=65536,outerJavaSummary=32768,observerFactsConsole=8192,batchIntentMetadata=2048,queryWireCapEach=70656,queryMetadataEach=2048,queries=2,versionQueries=0,allocated=262144,unallocated=0,wireIncludes='tx intended service/control bytes plus actual received handshake/status/FAIL/header/stdout/stderr/EXIT bytes; bounded single canonical archive, no duplicate channel files',unknownNotRefunded=True,wireOverrun='Same reader drains/discards with incomplete flag and full reservation held; actual unretained remote traffic may exceed cap, never qualify or dispatch second')
write(B/'release-plan.json',dict(status='DRAFT_NO_EXECUTION_DISPATCH',role='FIXED_SOCKET_G_READONLY',actualScope=None,actualRelease=None,actualOnce=None,sourceReview=None,approvedRequestSourceSha='ABSENT',root='D:/CodexProjects/VideoKit/docs/tester/D1_E13I_G_SUPPLEMENT_EVIDENCE',fixedOnce='e13i-g-readonly.once',serial='HA1Q6WXR',endpoint='127.0.0.1:5037',sdkStarts=0,versionQueries=0,budget=budget,firstScriptSha=hashlib.sha256((B/'tools/E13IIdentity.java').read_bytes()).hexdigest(),originalExec42537=dict(maxEmptyReads=1,responseQualificationSeconds=10,maxOutputBytes=65536,executed=False,notOriginalReturnAck=True),D1='NOT_PASSED',M0='NOT_STARTED'))
write(E/'dependency-difference.json',dict(runtimeDependencyAdded=0,MavenDelta=[],nativeDelta=[],SDKExecutions=0,AndroidBuilds=0,base='Reviewed E13F JAR183 exact classes',officialSourceReferencesOnly=True,NOTICEIncluded=pin(B/'reference/protocol/NOTICE'),licenseClearance='UNCHANGED_NOT_GRANTED'))
common='本轮实际5037/设备/SDK/旧handle读取/处置/安装/部署/产品重测均0。旧v17主任务最后PENDING/UNKNOWN、旧ps诊断LOST_DIAGNOSTIC_OWNER_UNKNOWN、E13H-LOCAL-VERSION-30384-RETURN_UNPROVEN三栏独立；本轮不查历史PID、不补ACK、不退款。用户持续测试授权已存在，原任务未决与本阶段范围继续限制执行。D1 NOT_PASSED / M0 NOT_STARTED，T07未派，P0/许可与旧候选不变。'
text(R/'docs/coder/D1_E13I_FIXED_SOCKET_DELIVERY_V1.0.md',f'''# D1 E13I 固定同连接只读协议交付 V1.0

2026-10-18。依据E13H独立复审SHA d74bb01bf02361fd8785bf1f215a793937ad756fb69f02eb7dfe4931256a953c及负责人E13I正式派单，完成固定角色最小离线实现并冻结交独立复审，不自批执行许可。

每条查询在自己的同一原Socket上先固定host:transport:HA1Q6WXR，再固定shell,v2,raw:既定脚本。两条串行、无SDK/no host:kill/no server启动重启/no feature探测/无任意host服务或PID CLI；可选version前置本批不使用（0次、最多两Socket）。新公开入口只接受准确角色及未来固定release pin，APPROVED_REQUEST_SHA仍ABSENT，当前Java/脚本均在Process/网络前拒绝。与H的技术阻断不同，协议角色已离线实现，执行派单仍未签发。

准确官方协议commit {commit}的10份全文及NOTICE、原始字节SHA/行段摘录封包；实际处理smart-socket长度/status/FAIL、shell-v2五字节头、1/2通道、3号单字节EXIT、一次4号零载荷close-stdin。借用流不独立close，唯一原Socket close/EOF/EXIT/原reader及archive writer实际join分栏。

一轮必要生产host编译成功、31组有限原peer测试通过；之后仅增加一个测试probe编译，生产不重编，对最终生产class执行身份/空输出/父保管/脚本验证。最终JAR共{len(rows)}class：183原F逐字节不变＋{len(rows)-183}本批实测class逐字节绑定，检查类不混入。JAR {pin(jar)['bytes']}B SHA{pin(jar)['sha256']}。无APK/Gradle/native构建、新依赖或Maven/native差异，FFmpeg等既有许可门NOT_GRANTED保持。

精确256KiB新预算覆盖wire/握手/帧/错误/元数据/原exec预留和重复console：8192+65536+32768+8192+2048+2×(70656+2048)=262144B，无未分配余额；stdout+stderr合65536B/查询、最多256帧、服务2048B、FAIL256B，10秒只是资格。单一original.wire保留请求意图与接收wire，不另写channel raw副本或echo到console；发送失败的全部意图预留不退款。超额同reader有界留存/明确丢弃，actual未留存remote traffic可越留存上限，不能冒完整raw/预算内查询成功。

本地harness connect失败路径原accept自然超时后stop并实际join；父wait超资格继续强持同Popen及记录句柄，50ms适配探针真实验证原Process随后自然exit0/文件关闭，但资格仍false，不靠raise丢owner、kill或daemon求通过。close永久异常使用准确E4Owned非IO有限fixture验证UNKNOWN不二close，真实Socket链验证close未返/CLOSING及尾通知扣住；未制造一只永久未知活Socket再强行结束以冒有限证据。

完整包/外seal/最终只读回执和四文档交审，十一个旧seal及准确成员不改；两滚动文档仅顶部新增安排、包内封副本。{common}
''')
text(R/'docs/coder/D1_E13I_IMPLEMENTATION_CONTRACT_V1.0.md',f'''# D1 E13I 原对象与协议契约 V1.0

2026-10-18；最小角色适配E4Owned与既审archive模式，不建立通用ADB客户端。E13IIdentity只保留既审准确G身份门/脚本，删除SDK命令工厂及版本原型；原183 F类准确沿用。E13IArchive仅将原process归档适配为socket wire及EOF/协议EXIT分栏，不伪造Process PID/exit。

## 先登记、单一关闭与实际线程返

Batch静态强持，在once/force/close前启动非daemon原keeper；准确intent原FileChannel归还后才能连server。每Op在allocate/connect/write/read前登记OWNERS，拥有唯一reader、原Socket、借用流、原archive writer和非daemon keeper。InputStream/OutputStream不自行close，唯一E4Owned<Socket> close只在原读取EOF/实际IO异常返回后执行；解析错误而shell可能仍运行时，同reader先drain至自然EOF/IO返回，无强关、二reader或重连。

reader与archive writer体内flag不自证线程结束。keeper join同一原reader，在原writer外确认其实际终止并join、每原文件close均返，才认物理资源归还；caller也join该keeper后才可资格成功/第二查询。Socket close失败或文件UNKNOWN，原keeper无限强持，不二close；资格10秒只能封依赖并返回PENDING，不能取消调用/线程。原writer尾通知未返时不能提前认资源归还。facts是提前快照，自身close/线程return不由该文件自证。

## 精确协议与固定白名单

仅固定127.0.0.1:5037，精确host:transport:HA1Q6WXR→同Socket shell,v2,raw:fixedScript。length为4个ASCII hex，status只OKAY/FAIL，FAIL限定256B且不fallback。shell帧5字节（ID+LE uint32，目标Android arm64 LE范围）；ID只接收1(stdout)、2(stderr)、3(EXIT)，EXIT必须长度1；无stdin需求仅发送一次4号零payload close-stdin。status/帧均逐字节读全，读碎片不当一帧；整数先校验再固定4096B块读，未审长度不申请大数组。单帧及两通道累计≤65536、帧数≤256；重复EXIT、EXIT后额外数据、未知ID、截断、EOF无EXIT均拒绝。

合法EXIT0与EOF仍分别必需，stderr非空不通过。EXIT无EOF资格失败保原Socket；EOF无EXIT虽物理归还但查询失败。第一query.run完成并实际join后才完整解析global instrumentation/ps，从准确旧scope/batch/class/method、app UID10221与am UID2000及父关系推导两个PID；无任意外部PID接口。第二读boot_id/stat/status/cmdline核准确UID/PPID/argv/start ticks，只是第二切片，不作旧owner ACK/终止许可；其他instrumentation/格式权限未知/全量超cap拒绝，fixture/codec未匹配仍UNKNOWN。

## 有界账及留存

Batch固定base116736B（host8192+exec65536+Java32768+observer8192+intent2048），每query预留72704B（双向wire70656+两metadata各1024），最多两query总262144B，不退款。wire记录发送意图（是否write返回另栏）及实际收到的handshake/status/FAIL/frame/payload；没有另写stdout/stderr副本，console只摘要。wire中的TX意图不是实际全部已发ACK；incomingWire/intendedTx/chargedWire及writesEntered/Returned分开。retainedWire是保留尝试的上界，queue offered/written及文件长度是不同事实；失败时不得冒完整持久化。

wire/帧/记录超限立即失败，不扩大留存：同原reader仍固定4096B buffer自然drain，截断/丢弃明确标记且保全部预留，不无限增长内存或补空raw；未留存实际流量可能超过cap，不能称实际全部接收预算成功。archive8×4096有界队列、原wire cap70656，queue满/落盘异常停依赖；尚在途保持原对象。所有资格都不是强制平台截止。once/current release/真实scope/sourceReview未签发，现审批pin ABSENT，无生产执行。

{common}
''')
text(R/'docs/coder/D1_E13I_SELF_CHECK_REPORT_V1.0.md',f'''# D1 E13I 有限离线自检 V1.0

2026-10-18。host-001一次生产javac exit0，编本批4生产源与最初ICheck/IFixtures，对准确F base JAR183 class；31个独立有限本地peer模式自然exit0，无生产源码修正或重编。supplement-002仅额外测试probe javac一次，对同host-001生产字节，不能把它隐写成所有javac只有一次。最终JAR{len(rows)}成员，全部新生产class保留实测原字节逐个核对；无检查/fixture类混入。

31模式：OK/SPLIT/INTERLEAVED/LIMIT/BAD_STATUS/FAIL/LONG_FAIL/SHELL_FAIL/TRUNC_HEADER/TRUNC_PAYLOAD/BAD_ID/LONG_FRAME/BAD_EXIT_LENGTH/FRAME_OVER/RAW_OVER/WIRE_OVER/EOF_NO_EXIT/EXIT_NO_EOF/DOUBLE_EXIT/AFTER_EXIT/STDERR/EXIT_NONZERO/CLOSE_PENDING/TAIL_PENDING/WRITE_PENDING/WRITE_FAIL/CONNECT_FAIL/CLOSE_UNKNOWN_CONTRACT/CHAIN_OK/CHAIN_BAD_SCOPE/CHAIN_PENDING。

实际生产解析器/Socket owner处理碎片、通道合上限、帧整数/长度/ID/过额、EXIT/EOF顺序/重复、非零/错误状态；pending在100ms资格先失败，原Socket/reader/writer keeper继续强持，释放同有限peer/hook后实际join/close一返；尾通知未返不得提前完成。实际写失败为Socket＋writer组合，record失败后不继续发shell，fixture原等待以自身1500ms读超时自然返回并close，原reader才获EOF；不能把此fixture错误写成真实设备行为。CONNECT_FAIL针对本地非法目标端口0产生实际connect失败；原fixture未接收client，100ms accept自然返回后stop/实际join/close，没有在join后才词法close的死等窗口。

CHAIN_OK两条同Socket握手分别完成，第一原reader/keeper实际结束后第二严格派生，原once FileChannel close/force返回，最终262144预留准确；CHAIN_BAD_SCOPE只一条、CHAIN_PENDING保同Batch及一条Op，最终自然归还仍不恢复资格，未自动第二。没有生产真实派单。

supplement-002额外测试同一生产字节的15身份/完整性/UID/父/组件/start ticks拒绝门、外部host/PID角色及未派执行拒绝；空stdout的真实Socket只有EXIT0+EOF+原物理返才通过协议层。非IO E4Owned open失败与永久close抛错UNKNOWN不能二分配/二close；这不是永久未知活Socket动态归还证明。实际Socket close未返/CLOSING已在链中扣住验证；永久异常分支静态保持非daemon原keeper，未造新永久未知网络对象后用kill/daemon退出冒通过。

父保管补充直接提取并执行实际check_host.py的run函数AST，仅把本地fixture wait适配为50ms：原pending文件记录同PID，父继续持有同Popen/输出句柄，再同原p.wait得到自然exit0及文件close；qualificationPreserved=false保持，函数断言失败由probe识别为预期，不改原资格。不是镜像父门、不是取消future，parentCustodyOutstanding=0。主套件20秒父等待未超资格，补充显式触发该分支，无20秒长跑。

PowerShell完整AST与准确角色未派/错产品角色拒绝实际回执，原observer owner主体与F实际字节比较相同。所有本地peer为非daemon、有限accept/read/释放路径且真实join，不靠daemon或kill结束。测试只连接自己临时端口，经工具明确本地网络权限，不访问真实5037。首H VERSION_OK缺ACK仍原样保留，本轮没有新未知地方probe。

官方协议源码固定commit完整下载，10份字节pin/NOTICE与片段可核；旧文档OVERVIEW.TXT在该commit HTTP NOT_FOUND留下0B，明确排除协议权威，没将下载失败说成成功。实际Android API31格式/权限/全局输出是否≤64KiB/服务实现均NOT_RUN；真实完整AM输出超限只拒绝不grep/追加。{common}
''')
text(R/'docs/coder/D1_E13I_E13G_SUPPLEMENT_PLAN_V1.0.md',f'''# D1 E13I E13G一次补充准确待派方案 V1.0

2026-10-18。协议实现已完成有限离线核验，仍需完整独立复审和负责人准确派单；目前APPROVED_REQUEST_SHA=ABSENT，实际scope/release/once/sourceReview null。不能编辑已冻结常量或绕过脚本直接执行；未来应另出绑定独立review/准确release SHA的来源策略版本并重审，不将本文当许可。

固定端点127.0.0.1:5037、serial HA1Q6WXR，无SDK/no server start/restart/host:kill。可选version请求本批省略（0）；两条设备query各一Socket，同一Socket串行请求transport再shell-v2，最多两Socket。服务白名单及wire格式见准确官方commit {commit}。

第一实际服务字符串在E13IIdentity.INVENTORY固定：shell,v2,raw:printf边界；dumpsys activity processes（完整global instrumentation/进程资料）；ps -A -w -o UID,PID,PPID,NAME,ARGS（完整global行）；分别准确成功结束标记。无外部script/serial参数。raw stdout与stderr分通道，只有exit0、EOF、原Socket/reader/archive/keeper实际归还、无不允许stderr/截断/落盘失败才解析，其他instrumentation/权限/格式未知或超过64KiB则停止。真实dump太大不能扩大cap或改grep。

第二实际服务必须据第一完整raw及其原归档字节绑定，严格核唯一原instrumentation组件、原runtime SHA {E13Scope if False else '116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef'}、batch D1-E13A-SOURCE-20261018/class/method，app UID10221与原am UID2000及父/argv。只由这两个当前匹配PID生成固定boot_id、/proc/PID/stat/status/cmdline读取；无示例PID外填，第一未返不第二。第二UID/PPID/argv/正start ticks变化即UNKNOWN，未匹配fixture/codec等仍未知，不凭两切片提供终止资格。

未来wrapper固定argv为：D:/Android/Android Studio/jbr/bin/java.exe、-cp、D:/CodexProjects/VideoKit/docs/coder/d1e13i/artifacts/e13i-host-tools.jar、com.videokit.spike.e4.E13IReadOnly、--g-readonly、准确release文件路径、该文件SHA。实际文件必须是经独立review绑定的typed e13iFixedReadOnlyRelease(kind/scope/serial/review/budget262144/requests2)，SHA固定进新来源策略；本文没有生成可执行release。固定root D:/CodexProjects/VideoKit/docs/tester/D1_E13I_G_SUPPLEMENT_EVIDENCE，only once e13i-g-readonly.once，wrapper id E13I-SUPPLEMENT-ONCE，cap32768；路径/角色/原scope/输入pins都必须一致，不能复用旧UUID或once。

总预算不扩大：已采host/父console8192＋原exec待收取65536＋外层Java摘要32768＋observer facts8192＋batch intent2048＋两query各(wire70656＋metadata2048)=262144B，余额0。wire含TX意图/实际RX握手/帧头/EXIT/FAIL/通道payload，只有一份wire文件，不重复channel文件/echo raw；两个metadata均≤1024、batch intent≤2048。stdout+stderr合65536、帧≤256、service≤2048、FAIL≤256，每query10秒资格。send失败全部意图额度未知不退款，重复摘要计相应预留。异常remote过量同reader固定buffer drain并丢弃标不完整，留存cap不是远端强制截止，过量不能通过/续第二。

原exec42537仍仅未来另派最多一次空输入收取、响应资格≤10秒、文本≤65536B，不循环/非空/Ctrl-C/重建session；本轮0次。若工具不能保证输出额度则不启动记BLOCKED，不用取消或丢返回。空输出/工具返回不是原owner ACK，晚证据另出补充，不回写旧切片。已采host切片19:31:58只作历史，不另偷偷新增CIM预算。

先独立审完整E13I，再由负责人签准确一次补充批次；读取结果仅用于最小收尾方案，所有行政终止仍另审，不能因服务连接成功放行产品/部署/T07。{common}
''')
latest='> 2026-10-18 E13I最新安排：固定同一原server Socket的serial transport＋两既定shell-v2只读角色已集中离线实现并有限验证，完整冻结交独立复审。当前审批pin ABSENT、生产执行未派，无真实5037/SDK/设备/旧handle动作；总256KiB含wire及所有元数据/重复输出，不扩大。E13H本地UNKNOWN只归档，旧主PENDING/旧诊断LOST与本地UNKNOWN三栏独立。E13F/H及所有历史冻结不改；用户持续授权已存在，T07未派，D1未过/M0未启。\n\n'
for rel in ['docs/MILESTONE_COORDINATION_V1.0.md','docs/milestones/D1_PHONE_TEST_EXECUTION_V1.0.md']:
 p=R/rel;t=p.read_text(encoding='utf-8');at=t.index('\n')+1;text(p,t[:at]+'\n'+latest+t[at:].lstrip('\n'));shutil.copyfile(p,B/'reference'/p.name)
print(json.dumps(dict(status='READY_FOR_INDEPENDENT_E13I_REVIEW',jar=pin(jar),classes=len(rows),newClasses=len(rows)-183,productionCompiles=1,testOnlyProbeCompiles=1,actual5037=0),ensure_ascii=False))
