from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,s):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(s)
a=load(B/'evidence/apk-audit.json');app,test=a['apks'];h=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()
def convert(v):
 if isinstance(v,str):return v.replace('D1-20261017-E6A','D1-20261017-E6B').replace('D1-E4A-E6A-NORMAL','D1-E4A-E6B-NORMAL').replace('/d1e6a/','/d1e6b/').replace('THIS_E6A_TWO','THIS_E6B_TWO').replace('E6A normal','E6B normal').replace('E6A two-normal','E6B two-normal')
 if isinstance(v,list):return [convert(x) for x in v]
 if isinstance(v,dict):return {k:convert(x) for k,x in v.items()}
 return v
plan=convert(load(R/'docs/coder/d1e6a/tools/device_plan.json'));plan['versionCode']=8;plan['versionName']='D1-E6B';plan['apks']=a['apks'];plan['state']='REVIEW_ONLY_NOT_DEVICE_PERMISSION';plan['deployment']['argv']=[['-s','HA1Q6WXR','install','-r',app['path']],['-s','HA1Q6WXR','install','-r',test['path']]]
plan['requiredEvidence'].append('Public precreation timeline failure preserves original PIPE_OUTPUT_TIMELINE cause/type and exact VALIDATOR/mode11/TIMELINE/NOT_CREATED/start NOT_STARTED; snapshot NOT_COLLECTED, no manufactured task. Do not confuse the legal JVM creation tripwire with real validation or Android success.')
put(B/'tools/device_plan.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
table='\n'.join('| '+x['role']+' | '+str(x['bytes'])+' | `'+x['sha256']+'` |' for x in a['apks'])
delivery=f'''# D1 E6B 完整交付 V1.0

2026-10-17。D1-20261017-E6B / versionCode8 / D1-E6B。仅修E6A-F01/P2公开入口创建前timeline异常归属，6个直接公开入口有限检查/59断言PASS，集中一次offline双APK构建PASS，无repair/native重建。Android/JNI/Binder系统及正常回归NOT_RUN，D1 NOT_PASSED/M0 NOT_STARTED、原P0/旧FAIL/许可保持。

唯一运行代码差异：公开E4CpuAdapter.validate(Context,...)的原PipelineRules.timeline调用外包catch(Exception|Error)，直接将捕获的原Throwable传给既有E6AFailure，标VALIDATOR/mode11/TIMELINE/NOT_CREATED/start NOT_STARTED，snapshot null。预检仍在TrackedProvider/CpuTaskClient创建之前，不为取得task而创建资源；offMain、合法输入后续及全部已拥有owner/后置验证/cleanup/原首份并发逻辑保持。未知实际在途仍原UNKNOWN。

tools/E6BPublicPreflightSelfCheck.java直接调用该公开Context重载，未用内部owner重载替代。5个坏timeline（null、长度、首值、非单调、超窗）均取得原生产PipelineRules.timeline抛出的IOException；primary与cause同一对象、原code/throw-site/type保持，无重建异常、cleanup为空、无task/snapshot，session实际路由由UNKNOWN改准确NOT_STARTED。五例均CPU创建tripwire/context/source open/digest为0。合法timeline另经同公开入口到达真实CpuTaskClient创建点，由测试Binder构造tripwire恰好一次终止，原sentinel身份保留；这是合法预检通过的校准，不是完整验证成功，也不作合法路径资源0或Android证明。

源码精确差异核实整个adapter仅上述catch不同，内部owned工作流后缀逐字节一致；其余所有运行源码、原JNI schema/sender/receiver、Source/validator作用域与原子首份、E6Muxer/E4CodecSink/PipelineRules、guard/recovery/每host观察/deadline/budget、app测试源码全部逐字节同E6A。原E6A20/112及E6原34只引用不重跑；本批仅6/59，日志evidence/public-run-001.log、输入/命令evidence/local-check-results.json。平台Context/Looper/Log/Binder为测试shim，实际Binder方法均禁止执行；无设备/媒体/导出件。

## 最终产物

| 角色 | 字节 | SHA-256 |
|---|---:|---|
{table}

仅用docs/coder/d1e6b/artifacts/D1-20261017-E6B/final，双证书 `{app['signerCertificateSha256']}` 与原相同，原AppID/两私有服务/权限保持。最终main-001绑定输入SHA `{h}`，一次offline成功。七native、native源码/header/config原字节不变，native重建0；35Maven/Media3 1.9.3/FFmpeg8.0.3/原白名单不变、下载0。原NOTICE及完整C14对应源容器保留；16KiB ZIP静态核验，不作Android16KiB或安全/许可放行。

开发与独立测试需求分别保存docs/milestones/D1_E6B_CODER_REQUIREMENTS_V1.0.md、D1_E6B_TESTER_REQUIREMENTS_V1.0.md，并随原审查报告纳入reference。完整四文档、精确diff、输入日志/SBOM/源码ZIP/外seal/包外只读verify整包交负责人复审。原E6A228不可变项只读核验PASS，未改旧冻结或原53651消费/失败产物。下一准确计划tools/device_plan.json：同签名保数据部署E6B→MP4→AVI→能力→仅本批两正常独立报告receipt条件cancel，每新host原实际观察，不新QUERY/ABORT。实际动作尚未启动。
'''
architecture='''# D1 E6B 架构及威胁边界 V1.0

2026-10-17。仅公开validate(Context,...)已知创建前timeline错误携带准确作用域；不扩验证/恢复或接口授权。

公开入口仍先offMain，再执行原PipelineRules.timeline。现在只在该调用外捕获原Exception/Error，直接以同一原对象构造既有E6AFailure：scope VALIDATOR、role mode11、phase TIMELINE、task NOT_CREATED、snapshot null、cleanup空。既有safe方法因此报告start NOT_STARTED与background NOT_COLLECTED；没有制造零native计数或task。session原路由能识别该异常，原在途UNKNOWN不被猜测为已启动或未启动。原首错/cause/throw-site和cleanup隔离规则保持。

捕获发生在TrackedProvider和CpuTaskClient构造前；失败立即返回，不会为拿到task而创建资源。合法timeline沿原TrackedProvider/真实CpuTaskClient/原平台适配器进入原owned validate，后半整段字节相同，公开offMain和其他参数/创建门未更改。生产接口没有test开关、fake输入源或额外Factory；只改一处catch。

本机五个坏timeline直接调用公开Context重载，使用真实生产PipelineRules而非替换timeline函数；观察f.primary与f.getCause()为同一对象、原IOException/type/code及首stack来自PipelineRules.timeline，源diff确认catch变量原样传入。session使用原E6ADiagnosticState先进入UNKNOWN再failure，准确转NOT_STARTED/TIMELINE/NOT_CREATED，源字段保持NOT_STARTED。CPU创建计数/context调用/provider open/digest均0；静态顺序同时证明连TrackedProvider也在预检之后。

合法timeline校准仍调用同公开入口，抵达真实CpuTaskClient构造站点，测试Binder构造tripwire一次抛预先持有的sentinel；既有CREATE包装保相同sentinel及NOT_CREATED。该正向校准证明合法预检继续原创建路径，不是全链成功，也不把该路径说成资源创建0。测试其他Binder方法均抛错，不模拟真实Binder执行。Context/Looper/Log/Binder shim及自检源码只在tools，未进入APK；旧E6A支持类只用于未改依赖类型，新adapter及纯规则从E6B重新编译。

只新增6个定点用例/59断言，无旧20/112或34/270/82模型重跑。无Android/JNI/媒体/导出件，本机tripwire不能当设备创建/FD/owner/death证据。整体原子首份、Java后置失败保native背景、source/validator task/mode/phase归属等E6A修复均字节保持。

原6帧/完整EOF/1000us/thumbnail/content/mapping、原2MiB输出/64MiB及8192readAt、60s/首cancel30s/协商12s/STARTED15s、真实owner/slot/资源归还、guard/recovery/每host实际观察/唯一R/S与稳定预算均保持；53651旧消费/失败产物、原N2结算/closeACKfalse及旧FAIL不改。七native与源码/header/config、JNI ABI及35Maven、原有限编解码/禁网络配置完全继承；无native构建或许可扩张。
'''
gates='''# D1 E6B 剩余门复审 V1.0

2026-10-17。

| 项 | 本批结论 | 仍需门 |
|---|---|---|
| E6A-F01/P2 | 公开预检原异常准确TIMELINE/NOT_CREATED/NOT_STARTED，五个直接负例零创建；合法公开入口创建校准支持 | 独立源码/完整证据复审，不能以内部owner测试替代 |
| E6A三项既有修复 | 除公开catch外所有运行类字节同E6A，原20/112不重跑 | 不把引用计作本批新通过或Android失败链实测 |
| E5C-REG-F01/P1及正常编码 | 继承E6封装修复与全部严格门 | E6B实际MP4完整READY及后续准确回归，旧FAIL不改 |
| JNI/native/16KiB/依赖 | 七库及原配置、35Maven不变，ZIP静态核验，无重建下载 | 实际Android16KiB/JNI/系统行为及既定许可/安全门 |
| 预算/原N2/当前host观察 | 原53651消费、失败产物、原结算和相关代码保持 | 每新host真实观察/原owner/资源/R/S门，不新ABORT或清账 |
| 正常MP4→AVI→能力→条件cancel | 本批设备NOT_RUN | 新冻结候选正式派发、本批两正常独立报告receipt |
| D1/M0/全P0/框架许可/旧signal | NOT_PASSED/NOT_STARTED及既定未完成保持 | 不当正式项目交付完成 |

任何FAIL/PENDING/UNKNOWN、原身份/EOF/画面/实际关闭/时限/预算不符均停止保留，不重试、弱化期望、延时、删产物、换UUID或清账；本机tripwire和模拟API不提供真实设备成功豁免。
'''
appendix='''# D1 E6B 设备执行附录 V1.0

2026-10-17。本次coder无设备/ADB/媒体源/导出件。tools/device_plan.json是精确待审计划，不是执行许可；负责人独立复审后另派。

仅原HA1Q6WXR/user0、AppUID10221/test10222，核最终外seal/同签名双APK/versionCode8/D1-E6B后app/test依次install-r保数据。不卸载/clear/降级/force-stop，不先部署旧候选，不重跑一次性G01根或更换原预算。53651累计消费/失败输出及原N2结算现场保持。

精确单方法/每次独立新host：com.videokit.spike.e4.E4DeviceTests#normalMp4SixRealFrames → #normalAviSixRealFrames → #capabilityDenialDoesNotOpenSource → 条件#cancelRejectsWrongEpochOversizeAndLateFrame。class#method/e4Case一致，不选fault全类。e4Batch=D1-E4A-E6B-NORMAL-TABLET-20261017，稳定e4BudgetIdentity=730a73e1-50e1-4198-a515-047104f00e31，e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT，结算SHA5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962。每个@Before实际执行原当前host观察，不复用旧live proof。原recoveryBatch=D1-E5B-N2-RECOVERY-20261017，无新QUERY/ABORT/独立OBSERVE。

正常须原真实六源/六输入/六samples、完整isolated6输出/EOF/PTS1000us/thumbnail/content/mapping/READY，准确source mode10与validator mode11各自task/phase及完整native字段，真实CPU/source/codec/FD/slot/CONTROL/owner和唯一R/S无pending。native OK仅背景，不替代Java或cleanup首错、全局READY。已知创建前timeline错误应TIMELINE/NOT_CREATED/start NOT_STARTED且无snapshot；实际在途仍UNKNOWN，缺日志不补零。

原方法60s/首次cancel30s/协商12s/STARTED15s、CPU8192readAt/64MiB、输出2MiB/三digest≤6MiB、方法日志4MiB和累计预算界保持，无Gradle/设备/媒体并发。MP4或AVI失败即停依赖；能力拒绝不得读源。cancel仅本批同设备两正常完整结果独立审证后，填该新报告准确e4NormalReceiptSha256，不能用旧报告/交付SHA或任意64字串。任何缺证/FAIL/PENDING/UNKNOWN停止保留原现场，不自动重试/新故障/正常后续/M0。

审阅四文档、原需求/复审、source-derivation精确唯一catch diff、local-check-results和public-run-001原日志、native-and-strict-logic-inheritance的整体/owned体字节比较、输入构建/签名/SBOM/ZIP/freeze与包外回执。tools/e6b_package.py verify只读，不执行自检/媒体；public runner默认INSPECT，冻结后拒绝运行。完整源ZIP无私钥/local.properties/cache/class/媒体，包含原native完整对应源、配置及来源；在独立副本自备既有SDK/缓存可按原离线配方构建，不重建或修改已冻结候选。
'''
for name,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gates),('DEVICE_EXECUTION_APPENDIX',appendix)]:put(R/f'docs/coder/D1_E6B_{name}_V1.0.md',text)
print('E6B four complete documents and precise review-only normal plan written')
