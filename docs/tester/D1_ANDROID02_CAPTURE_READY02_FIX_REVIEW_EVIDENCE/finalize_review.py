from pathlib import Path
import datetime,hashlib,json
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready02-fix';E=Path(__file__).resolve().parent;REPORT=R/'docs/tester/D1_ANDROID02_CAPTURE_READY02_FIX_PHASE_B_REVIEW_REPORT_V1.0.md';assert not REPORT.exists()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def anchor(path,text):
 p=B/path;hits=[k+1 for k,l in enumerate(p.read_text().splitlines()) if text in l];assert hits,(path,text);return {**pin(p),'line':hits[0],'match':text}
entry='tools/capture_android02.ps1';owner='tools/outer_owner.py';suite=read(E/'independent-suite-results.json');assert suite['seconds']<30 and len(suite['results'])==7 and sum(x['pass'] for x in suite['results'])==6 and not suite['results'][-1]['pass']
req=E/'fixtures/seven/request-identity.json';ad=E/'fixtures/seven/outputs/identity-owner-admission.json';co=suite['ownerFacts'][0]['records'][0]['console'];assert co['proofReadBytes']==ad.stat().st_size
save('request-admission-layer-accounting.json',{'firstRequestFile':pin(req),'firstAdmissionFile':pin(ad),'actualRequestWriterBytes':req.stat().st_size,'actualAdmissionWriterBytes':ad.stat().st_size,'consoleProofReadBytes':co['proofReadBytes'],'firstRoleHasNoPredecessorReads':True,'sourceCurrentReadCost':'Only admissionWriteBytes; request ReadJsonExact read exists before cost construction, not included','notClaimingAllHashPolicySourceReadsMustBeSdkTraffic':True,'actualSdkTraffic':0})
findings=[
 {'id':'CR2-B01','priority':'P2','title':'request/admission写成本已补，request正文读取仍未入控制账','type':'STATIC_CALLSITE_PLUS_ORIGINAL_LOCAL_COUNTER_EVIDENCE','facts':'PS确实ReadJsonExact读取本次request；ownerCurrentWriteCost计request+admission写入，ownerCurrentReadCost却仅admissionWriteBytes，第一次proofReadBytes也仅等admission文件长。下一次只补前驱proof/native/本次admission读，没有request正文读计量。正式要求明确核request/admission读写。','independentEvidence':'本审正常七步实际走通，首步request/admission原writer均关闭；first role没有前驱，console.proofReadBytes='+str(co['proofReadBytes'])+'恰等admission长度，request正文'+str(req.stat().st_size)+'B未在读取层入账。不是实际触发超限，也不主张把源码/policy/hash所有物理磁盘IO冒SDK入站。','fix':'在同原控制路径将明确要求的request正文读成本与admission/前驱proof/native读写分层计入control/总账，保console base+外delta来源及组界；先固定逻辑计量口径，不能用已有request写计数代读。','evidence':[anchor(entry,'$request=ReadJsonExact $RequestPath'),anchor(entry,'$ownerCurrentWriteCost=[long]$ad.requestWriteBytes+[long]$ad.admissionWriteBytes'),anchor(entry,'$ownerCurrentReadCost=[long]$ad.admissionWriteBytes'),anchor(entry,'$proofReadBytes+=$ownerCurrentReadCost')]},
 {'id':'CR2-B02','priority':'P2','title':'最后proof writer观察之后仍有受控哈希/交接尾段未纳入共享proof期限','type':'STATIC_CONTROL_FLOW_COUNTEREXAMPLE_DYNAMIC_ATTEMPT_INCONCLUSIVE','facts':'write_original内部wait_original在writer join后observe，run_one随后仍执行events.add、digest(pp)、next计数及records.append，成功返回前无最后observe。若writer及时但其后原proof SHA/交接尾段跨localProof界，self.failure可以保持None，下一run_one又新建proof_start，旧role迟返可漏过；末END也没有后续校核。同类后置metadata工作应纳入准确共享本地证明窗口。','independentEvidence':'原outer0.1s和proof0.03s+close0.12s正反验证确实在原线程pending时sticky并禁止后继。自有后置SHA有限return gate尝试未证明该反例：在到达预定验证点前，正常0.03s共享proof窗口已触发PROOF_WALL_TIMEOUT_STICKY，原writer随后归还，测试检查失败而不是候选超时门失效。故此项只据源码时序反例，不声称动态复现、系统磁盘迟返或实际设备问题。','fix':'共享proof时钟覆盖全部后置形成真实proof SHA、状态/记录与后继准入所必需的受控尾段；在准确最后受控点再次observe并保持原失败sticky，末END同样需外层真实返回判断。使用同一窗口，不退款/重领，不二写proof/kill或额外release框架。','evidence':[anchor(owner,'self.last_writer=self.write_original(pp,encode(proof),proof_start,delay)'),anchor(owner,'self.events.add(event);self.last_proof=digest(pp);self.next+=1'),anchor(owner,"self.records.append({'id':id"),anchor(owner,'return self.records[-1]'),anchor(owner,'proof_start=time.monotonic()')]}
]
save('concentrated-independent-findings.json',{'overall':'BLOCKED_TWO_SOURCE_P2_AND_INCOMPLETE_DYNAMIC_COVERAGE','findings':findings,'sdkAndroidReproductions':0,'tailAttemptMustNotBeReportedAsReproduced':True})
mapping=[{'prior':'CR-B01','current':'PARTIAL_FIXED_BASE_PLUS_REAL_NATIVE_PROOF_DELTA_AND_END_VERIFIED','remaining':'CR2-B01 current request read layer missing; reset/fake/double own dynamic guard group NOT_RUN after suite stopped'},{'prior':'CR-B02','current':'PARTIAL_FIXED_REAL_OUTER_AND_SHARED_PROOF_THREADS_TIME_STICKY_VERIFIED','remaining':'CR2-B02 final proof SHA/handoff tail static gap; dynamic attempt inconclusive, no new test after stop'},{'prior':'CR-B03','current':'SOURCE_FIX_VERIFIED_CODER13_POLICY_CASES_RETAINED','remaining':'Tester strict-schema/delta combined dynamic group NOT_RUN because earlier independent check failed; do not close independent runtime coverage or copy coder count as own'}]
save('old-three-finding-current-mapping.json',mapping)
coverage=read(R/'docs/tester/D1_ANDROID02_CAPTURE_READY01_REVIEW_EVIDENCE/independent-phase-a32-results.json')['cases'];assert len(coverage)==32
for c in coverage:
 c['priorReady01BStatus']=c.pop('independentStatus');c['independentStatus']='READY02_STATIC_REVIEW_WITH_LIMITED_LOCAL_RESULTS';c['actualProduction']='NOT_RUN'
 if c['id'] in ['AC12','AC16']:c['independentStatus']='PARTIAL_FIXED_NATIVE_PROOF_DELTA_PASS_REQUEST_READ_GAP_CR2_B01'
 if c['id']=='AC18':c['independentStatus']='PARTIAL_FIXED_REAL_OWNER_TIMEOUT_PASS_FINAL_TAIL_GAP_CR2_B02'
 if c['id']=='AC13':c['independentStatus']='STRICT_SCHEMA_SOURCE_FIX_CODER_CASES_RETAINED_TESTER_DYNAMIC_NOT_RUN'
 if c['id']=='AC21':c['independentStatus']='TESTER_SUITE_INCOMPLETE_6_GROUPS_PASS_ONE_INCONCLUSIVE_ONE_NOT_RUN_NO_RETRY'
save('independent-phase-a32-results.json',{'cases':coverage,'phaseAStatusUnchanged':True,'no32RuntimePassClaim':True,'actualSdkDeviceCalls':0})
baseline=[]
for p,expected in [(R/'docs/coder/d1android02-capture-ready01/evidence/capture-ready01-freeze.json','3ff8b42d7bd5c31f578bcfdec8bba7286dd32ba90289fcc6556dc338368fa51d'),(R/'docs/coder/d1media3-android02-fix02/evidence/fix02-freeze.json','39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad'),(R/'docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json','65e8413b3e90dd571c22fea7049778b29c0d94221cd490560cdcd5c3cc00ae5a')]:
 assert sha(p)==expected;d=read(p)
 for x in d['files']:
  q=R/x['path'];assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
 baseline.append({'seal':pin(p),'rows':len(d['files'])})
seal=B/'evidence/ready02-fix-freeze.json'
for x in read(seal)['files']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
save('baseline-and-post-review-preservation.json',{'baselines':baseline,'new364UnchangedAfter':True,'oldUnknownActions':0,'sdkToolsNotRehashed':True})
ownerrecords=[o for o in suite['ownerFacts']];count=sum(len(o['records']) for o in ownerrecords);assert count==13
save('test-boundary-and-read-ledger.json',{'actualSuiteSeconds':suite['seconds'],'actualOriginalCaptureControllers':13,'completedGroups':6,'inconclusiveFailedCheck':suite['results'][-1],'notRunGroup':'strict-policy-and-three-delta-guards','originalWaitReadCloseProofWritersAllReturned':all(r['proofWriter']['closeReturned'] for o in ownerrecords for r in o['records']),'noPermanentUnknownInjectionOrPendingNewPopen':True,'afterFailureNewDynamicCalls':0,'controlledDigestGate':'One finite local digest return shim preserving actual hash and source files; no reflection/state edit, real disk fault, SDK or media. Inconclusive due pre-existing normal proof timeout.','textObservedAndWritten':suite['textObservedAndWritten'],'producerStdinBytes':6144,'fixedFixtureLimit':65536,'textLimit':4194304,'candidateNotClaimedPassed':True,'identityReads':'Opaque frozen364/ZIP365 and baseline756/874/818 rows include APK/media bytes as finite hashes, not media parsers/physical IO/old or future device ledger','newSdkDevice5037OccupancyGradleJvmMediaCalls':0,'unknownRetryKillInterrupt':0})
ftext='\n\n'.join('### '+f['id']+' / '+f['priority']+' — '+f['title']+'\n\n类型：'+f['type']+'；SDK/Android复现0。\n\n源码事实：'+f['facts']+'\n\n独立证据：'+f['independentEvidence']+'\n\n集中修复：'+f['fix']+'\n\n准确来源：'+'；'.join(x['path']+':'+str(x['line'])+'（SHA '+x['sha256']+'）' for x in f['evidence'])+'。' for f in findings)
text='''# D1 ANDROID02_CAPTURE_READY02_FIX 独立完整离线阶段B复审 V1.0

2026-10-21；tester；完整冻结工具审查，无设备activation。

## 结论

**BLOCKED_TWO_SOURCE_P2_AND_INCOMPLETE_DYNAMIC_COVERAGE**。364原清单/ZIP365逐内容及准确七角色/产品pins/默认准备态/原owner源码核完；旧三项核心修复明显推进，但仍集中交回**2项P2源码口径/时序缺口**：CR2-B01本次request正文读取未计control；CR2-B02末proof writer观察后还有未受同一proof deadline校核的SHA/状态交接尾段。

独立动态套件18.36秒<30秒后在第七检查处失败并停止：**6组完成通过，1组尾段反例尝试不确定，最后严格schema/三delta拒绝组NOT_RUN**。不能称完整自检通过、不能以coder最终7组结果代自己覆盖。尾段测试先遇正常proof超时门，未达到预定反例点，**CR2-B02仅按源码时序反例报告，动态复现未成立**。没有延长或重新领取本地测试窗、重跑旧套件、修改冻结源、自动后继测试或设备操作。

本审是完整静态整包/全部已得动态证据与未覆盖的集中报告，不签capture就绪/完整独立B通过。真实SDK/Android/FD/Media3/平台finish/DTS/播放均NOT_RUN或UNPROVEN；不重开已接受的产品五项有限关闭，D1未过/M0未启。后续由负责人统一安排源码修复与必要未覆盖验证，不能自动activation。

## 准确冻结与来源差异

coder报告11076B/SHAabea5b1b9dc635743b3274bcbe13c03a8ca40ecb4527f2fc1aa1c6bce87da99a；seal c5ec7bafa461bc6e99ed2790248c67edce92cf11cd4a3e33c72fed54f5b82b1e，**364项**全部大小/hash吻合；ZIP SHA929ae193f2cf385c911b0cb4e82e4b99aeacf6e76f819fe2107ef0303e1adb9e，**365唯一成员=364清单+seal**，独立逐集合/解压CRC/大小/hash核。只读材料入口bad=[]，结束再核364字节未变；没有在冻结目录运行写入型自检/生成/冻结脚本。

入口105118bf3d027ce0cb220e9a07ec50dbdedbf316edb15c72b7a93f660a6f3096；实际生产outer_owner.py 3aab1fee40b2989e41e3ca4a2750a5a481b0caa5c8691bf287b26900ad192fa3；producer4b0aea7b372f737ae6d0970374d18d491c2f537c741df3fa7166c5ef654e8d5a。新owner从已有原Popen/reader/wait/stream+handle/proofwriter模式准确适配，固定生产CLI/七角色顺序，无任意命令接口或新native helper/平台release层。旧入口→新入口与producer全文差异已独立保存；producer只补firstFailure:null等当前严格政策所需有限fixture事实，非真实Android回执。

七角色计划与READY01字节同SHAf0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199；默认PS与Python owner均PREPARATION_ONLY/SDK前拒，activation approved=false且scope/runId/root/B/freshroute/initialproof/实际wall值仍空。生产新绑定owner/Python/source/entry/plan/产品与准确前驱，不把模板或候选proof自身approved字段当执行票。

产品原seal39acf773...fbe0ad/app7151481B f67edf0184f2d1cb6c87fe2350f2113e0c56d0452b185b02b24c879d61ac04ad/test478124B b034ceb0e19e37ff2e10fc3db3a89c88b3d9a50d02851bbcb9e360b551dc37d9/准确FIX02版本/签名/runner/scopeAll+fixture19e815...778a9c+新runId保持。旧READY01756/FIX02874/RENDER818原seal全行结束独立核不变；无SDK文件重新hash、当前server/claim/5037/占用或旧35512/48945/17257查询，所有旧报告/消费/FAIL/UNKNOWN不回写。

## 旧三P2修复迁移

| 旧项 | 本包准确裁定 |
| --- | --- |
| CR-B01 console只能等账 | **核心delta接续及END已实际验证，部分修复**。新PS保原console基账，校真实native/proof大小/sourceOwner/PID/request/receipt/raw/eventId/准确next，不直接放松相等。正常首base14146+真实delta2789成功接续，末END也加2852；request读层仍CR2-B01。自有reset/fake/double负例最后未运行，不照抄coder三例为自身结果。 |
| CR-B02 outer/proof仅字段 | **真实原线程观察/共享窗口与sticky已验证，部分修复**。starter/wait/readers/close worker/每writer持有原引用，outer0.1与proof0.03+close延迟0.12时观察原pending线程并保持失败、禁止新run_one；但末SHA/交接尾段仍CR2-B02源码缺口。 |
| CR-B03负账/首错假成功 | **准确源码已修，独立动态覆盖未完成**。StrictReceipt存在/类型/int-long非bool、非负上界、firstFailure存在且null、十history/身份/时间/原owner等源门明确。coder13纯语义样本准确保留；本审policy组NOT_RUN，不能签自身runtime关闭或冒全部严格schema回归完成。 |

原native/proof增量是实际文件长而非自签哈希循环，eventId与源相连；request/admission writer在首Popen前真实flush/close/join，proof candidate显式candidateOnlyWriterCloseNotProven=true，下一admission必须由原owner在前writer归还且及时后产生。proof迟返前落盘可能仍有approved=true，源码原owner已sticky不生成下一admission/不新Popen，候选本身不能证明close/及时；不把此声明误作新增成功权力或恶意本地主机认证。

## 自有有限本地验证与真实边界

仅在D1_ANDROID02_CAPTURE_READY02_FIX_REVIEW_EVIDENCE/fixtures构造新快照；直接加载冻结准确Owner源码（-B，不写pycache）、复制冻结entry/plan/route文本并用新OFFLINE_FIXTURE policy，固定Python producer，生产模式未激活。原7SDK计划没有被消费；本地capture原控制器共**13个**、各自然wait/两reader join/stream/Windows handle/proofwriter归还；不把owner.failure等于仍有物理调用未知。全部有限writer均closeReturned，无永久unknown注入，无kill/interrupt/二close/未知重试或后继动态补跑。

实际18.36秒；观察/写入文本**160044B**<4MiB，producer stdin**6144B**<64KiB，另少量固定参数/状态元数据，不冒真实APK/wire传输。自有受控尾段尝试只给同原digest返回加0.08秒有限门、真实hash不变、源文件不改/无反射改状态；它不是系统磁盘/Android故障注入，失败结果不伪装复现。

| 自有检查 | 真实结果 |
| --- | --- |
| PREPARE owner | Popen前拒绝，通过。 |
| 完整七角色原owner链 | 七角色fixture capture均完成，4096+2048同原stdin/pin返回，pending/final保留；所有proofwriter真实关闭后接续，首增量2789，末END增量2852；末control138086/total139583/payload6144。 |
| busy原capture | identity后global_busy真实producer→capture ENV_WAIT，下一app_absence未进入。非纯重放、非设备fresh事实。 |
| 超额部分保存 | read192B/save64B，明确失败sticky，未称完整raw保存成功。 |
| 原outer观察窗 | 0.1秒时同原3线程pending被记录OUTER_WALL_TIMEOUT_STICKY；全部原返后仍拒后继。 |
| 共享proof关闭窗 | 0.03秒时同原1writer pending，延迟0.12秒后自然close/join；PROOF_WALL_TIMEOUT_STICKY保持，后继拒绝。 |
| 后置SHA尾段反例尝试 | 在预定验证点前正常共享proof0.03秒已触发timeout（有1原writer pending记录）；最后原writer正常返，检查预期不成立。**INCONCLUSIVE，不是产品门运行失败或动态复现**。 |
| 严格政策/三delta拒绝 | 脚本排序在前一失败之后，**NOT_RUN**；保留待跑源码，不追加时间/重领窗口，不引用开发13+3替代自身执行。 |

所以动态summary原样为INCOMPLETE_OR_FAILED，6组pass/1组检查失败，计划8组缺最后1组，不改成allPassed。不把scope timeout本身归因为产品缺陷；本次检查未通过是测试预期没有到达目标分支，后续只在准确新范围安排必要针对覆盖。

## 两项集中源码问题

'''+ftext+'''

## 预算、时间和全32oracle

精确七角色/HA1Q6WXR固定argv/独立global门/自身两包absence/无-r安装/scopeAll一次保持；无retry/并发1/额外push/pull/截图/logcat/清理。四preflight1048576、两install131072、instrument所有pending-final1048576、controllerproof1048576，总logical inbound3276800；binary7629605+command全28672=out7658277。源read-locked文件pin、源hash读/SDK内部再读/ADBframing未知分列，不拿6144fixture模拟冒7629605真实安装。

四15+两45+90=240仍是分项观察和，App60；owner outer/localproof/whole生产值上限600/30/600且实际尚未绑定。共享前后proof段已使用local_used扣除outer等待，窗口不整份重领；本次问题是最后观察后仍有必要受控工作而无末点校核，不否定已正确实现的原pending观察。未知保同原对象并停新准入，后来自然返回不退款/补绿，不强停。

independent-phase-a32-results.json保原32oracle并逐条标本包迁移、静态/有限动态/部分/未跑。未改A的PREPARED_NOT_RUN，未把开发7组/本审6组冒32runtime PASS。StrictReceipt源码与coder13是各自证据；原外层/末proof候选/成功App内部worker/mux自报仍不是平台finisher Binder尾段返回，最高有限分类INTERNAL_FINISH_UNPROVEN不变。

开发最终19.125秒整套与较早19.062秒中间源码记录保留分层，只有最终源码/owner快照可绑定当前交付；中间未完整保全owner源，不当全最终动态证据。本审真实设备/SDK/ADB/5037/占用/Gradle/JVM/Media3/原FD/平台finish均0/NOT_RUN，无host全空闲或发行许可声明。

## 保全与交接

完整源/diff/364-ZIP365/原baseline、全部已执行owner records/原raw与候选proof/writer/超时记录、失败检查及未执行政策源码、两项source anchors与32覆盖一起冻结后一次回交负责人。没有修改已发旧报告/产品五项有限关闭；所有旧UNKNOWN保持。有限hash包含opaque媒体/APK字节，不声称载荷读取0/物理IO精确或倒灌旧资格/未来设备8MiB账。

当前两项源码阻断及独立覆盖缺口集中处理，建议负责人同一新准确范围修复并补有限目标验证后整包再审；不逐项派修、不自动activation或设备测试。持续平板授权保持，无需重复索通用许可。
'''
REPORT.write_text(text,encoding='utf-8');manifest={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'BLOCKED_TWO_SOURCE_P2_AND_INCOMPLETE_DYNAMIC_COVERAGE','report':REPORT.relative_to(R).as_posix(),'reportBytes':REPORT.stat().st_size,'reportSha256':sha(REPORT),'evidenceFiles':[pin(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json'],'findings':[f['id'] for f in findings],'independentDynamic':'6 groups pass, one inconclusive failed check, one not run; no whole-suite pass','suiteSeconds':suite['seconds'],'actualSdkDeviceJvmMediaCalls':0,'oldUnknownActions':0};save('review-evidence-manifest.json',manifest);print(json.dumps({'reportBytes':manifest['reportBytes'],'reportSha256':manifest['reportSha256'],'manifestSha256':sha(E/'review-evidence-manifest.json'),'evidenceFiles':len(manifest['evidenceFiles']),'overall':manifest['overall']}))
