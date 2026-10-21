from pathlib import Path
import datetime,hashlib,json
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-android02-recovery01';E=Path(__file__).resolve().parent;REPORT=R/'docs/tester/D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_PHASE_B_REVIEW_REPORT_V1.0.md'
assert not REPORT.exists()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def anchor(path,text):
 p=B/path;lines=p.read_text().splitlines();found=[i+1 for i,l in enumerate(lines) if text in l];assert found,(path,text)
 return {**pin(p),'line':found[0],'match':text}
j='instrumentation/com/videokit/d1media3/android02/test/ExperimentJob.java';i='instrumentation/com/videokit/d1media3/android02/test/Media3Instrumentation.java';o='instrumentation/com/videokit/d1media3/android02/test/OwnedFiles.java';mx='src/com/videokit/d1input/MatureContainerRemux.java';mb='src/com/videokit/d1input/MatureMuxerBinding.java';ow='upstream/com/videokit/spike/e4/E4Owned.java'
findings=[
 {'id':'R01-B01','priority':'P2','prior':'REC-OBS01','title':'部分失败或pending时此前case历史未导出','type':'DETERMINISTIC_SOURCE_REPORTING_GAP','trigger':'scopeAll已完成前k项，后一case抛异常/原返回pending，或whole deadline在子case执行时到达','facts':'run循环每次method=next；仅十项全部成功后method=requestedMethod；receipt只在current method==scopeAll加入caseReceipts/completedCaseCount。因此失败/pending时已存的历史仍在原Job，外部receipt却没有。不是此前未执行，也不是原Job完全丢失。','impact':'无法按实际部分执行结算全scope；不能交设备求测后才补历史。','fix':'按requestedMethod输出有界已有历史/完成数/当前case与同scope累计账；失败当前case另标partial；保持原Job/firstError/UNKNOWN，不重放完成case，不突破262144B。','evidence':[anchor(j,'method=next;resetCase()'),anchor(j,'method=requestedMethod;status='),anchor(j,'if(method==ExperimentContract.Method.scopeAll)result.put'),anchor(i,'pending.putString("receipt",bounded(j.receipt(false)))')]},
 {'id':'R01-B02','priority':'P2','prior':'REC-OBS02 + A02-S04 remaining layer gap','title':'原生attempt全scope累计已修，SDK requested及完整phase分层仍缺失','type':'SOURCE_OBSERVABILITY_CONTRACT_GAP','trigger':'inspectShort3时桥接SDK count可大于3，native实际read n=min(count,chunk,size-at)=3；或copy/hash/sniff/seek/reopen任一phase','facts':'reserveInput(n)在native读取前累计，inputActual只加正返回；sdk count无独立累计/预扣且phase无分层记录；receipt无SDK requested与native attempted/returned完整分层，readCalls不能推算。8MiB当前是native attempt+copy/control/EOF reserve，不是SDK requested总量。','impact':'M2A10/35/37的全口径观测与预算合同未闭合；绝不声称本批已实际超限。','fix':'同原路径在调用前记录/准入SDK requested、native attempted、returned/EOF及phase累计，无退款无新factory额度；明确copy/control非native传输计数；原native FD/asset/writer分层峰值也需在设备合同前补齐，不能从sourcePeak冒FD峰值。','evidence':[anchor(o,'int n=(int)Math.min(Math.min(count,chunk),size-at)'),anchor(o,'job.reserveInput(n);owner.original().seek'),anchor(j,'void reserveInput(int bytes)'),anchor(j,'inputAttemptedReserved'),anchor(j,'physicalBytes",provider.physicalBytes')]},
 {'id':'R01-B03','priority':'P2','prior':'A02-S02 STILL_APPLIES','title':'wholebody完成标记仍早于最后受控返回信号','type':'SOURCE_ORDER_COUNTEREXAMPLE_NOT_RUNTIME_REPRO','trigger':'cleanup后marker及时，但之后同步E13ReturnEvents.returned回调/调度尾段跨60秒，等待者晚恢复时worker已结束','facts':'completedNano/workerBodyReturned均在returned()之前；returned同步遍历listener.changed。onStart只看isAlive/早marker差值。59.9s写marker，60.1s回调后worker结束，可被早时间认作及时。','impact':'源码不满足M2A42 last-controlled-point，实际join不能替较早body点；不伪称已实机触发。','fix':'把最后受控body标记置于全部cleanup/可延迟信号之后，保同worker join、等界迟及UNKNOWN sticky；若信号需提前，明确最终不可提前补绿的原完成点。','evidence':[anchor(j,'completedNano=System.nanoTime();workerBodyReturned=true;E13ReturnEvents.returned()'),anchor('upstream/com/videokit/spike/e4/E13ReturnEvents.java','for(Listener l:listeners)l.changed()'),anchor(i,'j.completedNano-j.startedNano>=60000000000L')]},
 {'id':'R01-B04','priority':'P2','prior':'A02-S03 STILL_APPLIES','title':'Os.open成功至流包装返回间raw FD仍未进入原owner','type':'SOURCE_EXCEPTION_RETENTION_GAP','trigger':'Os.open成功返回原FD，随后new FileOutputStream(fd)构造异常','facts':'createNew仍内嵌Os.open；外E4Owned仅在action.run整体返回后写resource，故此窗口原FD无登记字段/closer。包中正常Android wrapper关闭所有权依据仍API_UNPROVEN，不能用JDK helper替平台。','impact':'已注册外holder并不证明原FD被强保管；异常路径原FD归还证据缺口。未OOM/坏资源/权限注入，不断言正常Android一定泄漏。','fix':'先登记原native descriptor owner并在open返回后立即采用，包装/关闭单一权责，异常UNKNOWN强保管；提供准确Android关闭依据，防二close；不重放/强制清空。','evidence':[anchor(o,'new FileOutputStream(android.system.Os.open'),anchor(ow,'resource=action.run();'),anchor(j,'dest.allocate(()->OwnedFiles.createNew(sourceFile))'),anchor(o,'job.outputHost=this;original.allocate')]},
 {'id':'R01-B05','priority':'P2','prior':'NEW_INDEPENDENT_FINDING_INHERITED_SOURCE','title':'原Media3 muxer在addTrack/write/EOS异常后无Job级保管及关闭门','type':'SOURCE_EXCEPTION_OWNERSHIP_GAP_NOT_ANDROID_REPRO','trigger':'MatureMuxerBinding构造及E6Muxer.create成功，后续addTrack、sample或E6 EOS/close抛异常','facts':'binding仅writeAndInspect栈局部；private original只在binding内，未登记到Job原owner。正路finishWriter才走E6Muxer.finish/close；异常没有finally或保管转移。Job cleanup只abort TemporaryOutput/关hostFD，resourcesReturned无binding/muxer状态。即使sink/native均返回，仍不能据此证原Media3 muxer已close/归还。','impact':'失败路径原muxer引用/原close返回缺口；可能在外资源已返回时允许finisher通过，不代表该muxer事实已证。源码继承不等此合同已验收。','fix':'原muxer/binding在创建前有Job级keeper、成功后采用；错误保管同原对象，按真实API明确一次关闭/close未知状态门，不重建muxer、不二close、不把sink abort当原mux close。','evidence':[anchor(mx,'MatureMuxerBinding binding=new MatureMuxerBinding(output)'),anchor(mb,'original=com.videokit.spike.c14.E6Muxer.create'),anchor(mb,'E6Muxer.finish(original,track,samples,last)'),anchor('upstream/com/videokit/spike/c14/E6Muxer.java','muxer.close();'),anchor(j,'if(output!=null)try{if(!output.abort())'),anchor(j,'if(outputHost!=null&&!outputHost.original.returned())')]}
]
save('concentrated-independent-findings.json',{'actualAndroidReproductions':0,'findings':findings,'scope':'ALL_728_COMPLETE_REVIEW_NOT_PIECEMEAL_REPAIR_DISPATCH'})
mapping=[{'old':'A02-S01','current':'SOURCE_POLICY_FIXED_AND_17_LIMITED_HOST_POLICIES_PASS_ACTUAL_EXTRACTOR_NOT_RUN','evidence':'QualifiedObservation.supportedFlags permits KEY and optional LAST only index5; raw preserved, mux passes key domain after full require; q.flags old list remains reference but no longer raw comparator. Unknown bits still rejected.'},{'old':'A02-S02','current':'STILL_APPLIES','currentFinding':'R01-B03'},{'old':'A02-S03','current':'STILL_APPLIES','currentFinding':'R01-B04'},{'old':'A02-S04','current':'PARTIAL_FIXED_ONE_JOB_ONE_SCOPE_NATIVE_AND_OUTPUT_CUMULATIVE','remaining':'R01-B02 SDK/phase layers absent. Future six-op binary/text proposal improved, exact device/capture/transport/whole-wall/cleanup binding still before execution; no actual device overrun claimed.'}]
save('old-static-findings-current-mapping.json',mapping)
orig=read(R/'docs/tester/D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_EVIDENCE/independent-m2a01-m2a48-oracles.json')['cases'];assert len(orig)==48
notes={
 'M2A01':'正式新B范围；设备未派。', 'M2A02':'新728/旧seal及所有baseline身份保持；旧UNKNOWN未触碰。', 'M2A03':'APK实际asset8849/hash与QUAL03一致。', 'M2A04':'APK字节已核；copy/EOF/sync/read-only只源码，FD保管R01-B04。', 'M2A05':'真实AXML/签名身份/零权限组件native已核；同UID不宣称隔离。', 'M2A06':'唯一scopeAll三参数准入纯政策通过；十directcase拒；BBB不mux。', 'M2A07':'准确source/license资产/继承metadata与SBOM；无新权利清场。', 'M2A08':'strict真实300/17与Media31.9.3，DEX无JCodec/fork/host helper。', 'M2A09':'源preopen guards/政策拒，native open实际NOT_RUN。', 'M2A10':'short3 native限定存在，分层requested不足R01-B02；无Android样本。', 'M2A11':'真实Extractor/DefaultInput的DEX实现及源链存在，运行未证。', 'M2A12':'真实format源getter/资格比较存在；actual值未运行。', 'M2A13':'实际sampleData/Metadata代码与capture门存在；实际six未运行。', 'M2A14':'实际initData逐buffer长度/hash及concat规范化，不写host三数组；真实数组未运行。', 'M2A15':'A02-S01源码政策已修/17host政策通过，真实flags未运行。', 'M2A16':'比较实际timeUs与0..1e6；Android callback未发生。', 'M2A17':'实际SeekMap.first/epoch/replay代码；真实seek支持未证。', 'M2A18':'NO_INDEPENDENT_DTS_API显式保留，actualDTS不填PTS。', 'M2A19':'完整capture/release/immutable copy源门；原mux keeper新增R01-B05。', 'M2A20':'manifest只作参考；源码真实getters比较，未以golden填actual。', 'M2A21':'实际mux类DEX/调用存在，原mux异常保管R01-B05，调用NOT_RUN。', 'M2A22':'原E6 six+emptyEOS4/1200000未改；真实EOS/close未运行。', 'M2A23':'原3000ms/copying配置未改；实际fragment未运行。', 'M2A24':'真实SeekMap/TrackOutput duration==1200000，TIME_UNSET拒；实际能力UNPROVEN。', 'M2A25':'真实CSD concat相等门；实际fMP4 arrays未运行。', 'M2A26':'同框架key/PTS/size/hash + declaredraw政策源门，实测无。', 'M2A27':'输出extent/hash/实际class与sniff门；没有输出文件/实际parser结果。', 'M2A28':'sequentialdigest/extent-readback匹配及writeAttempt门继承；真实output未写。', 'M2A29':'原rawFD异常R01-B04，原mux异常R01-B05；不冒原owner已闭。', 'M2A30':'实际Os/FDsync方法编译入DEX不代真实关闭API依据/返回。', 'M2A31':'Future/计数与E13返回分门；平台/原mux全返回未证。', 'M2A32':'MC-B01源完全同旧已修，不重跑旧未知套件；原同grant/REOPEN1保留。', 'M2A33':'controlled cancellation源与旧有限非媒体事实继承，wholedeadline marker R01-B03。', 'M2A34':'rawEOF/parserEOF/release/dsclose/FDclose分项源；本机17政策不验证。', 'M2A35':'source2/oneinflight源门；真实FD峰值/完整phase/SDK分层需R01-B02补齐。', 'M2A36':'sameworker join及E13 canFinish门；receipt finalizer owner1与外finishreturn分列，原mux缺R01-B05。', 'M2A37':'同Job native/copy预算累计不reset，SDK/phase缺R01-B02。', 'M2A38':'同Job outputAttempt累计含controlled4/真实muxattempt，无退款；native实际未跑。', 'M2A39':'新6logicalops/双APK7590909/出入文本上界计划已核，ADB framing/tool/wholewall/cleanup仍待准确设备合同。', 'M2A40':'cancelLateRead/writerPending仅controlledHOST源；其余阶段实际未跑且当前非全面故障覆盖。', 'M2A41':'17policy含scopeonly/10directreject；wrongfixture源guard存在，无媒体fuzz。', 'M2A42':'R01-B03源码标记次序不符，等界迟/unknownsticky虽存在不能代。', 'M2A43':'pending不sticky/真firstfailure源门保留，partial导出R01-B01。', 'M2A44':'同scope停止源；partial外账缺R01-B01及muxkeeperR01-B05；无自动kill/删除旧。', 'M2A45':'728/86/真实DEX方法/双APK/v2/300strict已核。', 'M2A46':'实际wholeAPK/DEX无JCodec/JAAD/fork/check；平台定义与旧继承集精确同。', 'M2A47':'scope/serial/freshidle/capture null，当前不是执行计划；持续设备许可不重复询问。', 'M2A48':'本结论有限静态/政策，不签容器实测或D1/M0/READY/播放。'}
cases=[]
for c in orig:
 cases.append({'id':c['id'],'area':c['area'],'originalOracle':c['oracle'],'phaseAStatusUnchanged':'PREPARED_NOT_RUN','independentBResult':'COMPLETE_OFFLINE_REVIEW_WITH_SOURCE_BLOCKERS_AND_PLATFORM_NOT_RUN','notes':notes[c['id']],'actualAndroidStatus':'NOT_RUN','runtimePass':False})
save('independent-m2a01-m2a48-results.json',{'cases':cases,'globalAndroidRuns':0,'policyHelperCasesOnly':17,'doesNotReclassifyA':True})
# Independently preserve every explicitly listed baseline; never inspect live cache/old process state.
baseline=[]
for x in read(B/'evidence/all-baseline-preservation.json'):
 target=x.get('seal',x.get('manifest'));p=R/target['path'];assert p.stat().st_size==target['bytes'] and sha(p)==target['sha256'];d=read(p);rows=d.get('files',d.get('evidenceFiles'))
 for y in rows:
  q=R/y['path'];assert q.stat().st_size==y['bytes'] and sha(q)==y['sha256']
 if 'report' in x:
  y=x['report'];q=R/y['path'];assert q.stat().st_size==y['bytes'] and sha(q)==y['sha256']
 baseline.append({'manifest':target,'rowsVerified':len(rows)})
sbom=read(B/'media3-android02-recovery01-sbom.cdx.json');coords={':'.join(c[k] for k in ['group','name','version']) for c in sbom['components']};locks={l.split('=')[0] for l in (B/'app/gradle.lockfile').read_text().splitlines() if l and not l.startswith(('#','empty='))};assert coords==locks and len(coords)==17
for c in sbom['components']:
 hashes={h['content'] for h in c['hashes'] if h['alg']=='SHA-256'};coord=':'.join(c[k] for k in ['group','name','version']);selected=[x for x in read(B/'evidence/actual-consumption/artifacts.json') if x['coordinate']==coord];binaries={x['sha256'] for x in selected if x['kind']=='binary'};assert selected and c.get('licenses')
 if binaries:assert hashes&binaries
 else:assert not hashes and coord in ['androidx.annotation:annotation:1.6.0','org.jetbrains.kotlin:kotlin-bom:1.8.0']
save('baseline-license-and-post-seal-review.json',{'baselines':baseline,'sbomCoordinates':sorted(coords),'licenseScope':'Inherited admitted metadata/provenance preserved, not patent/commercial/global release clearance','oldUnknownQueries':0})
seal=read(B/'evidence/recovery01-freeze.json')
for x in seal['files']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
save('review-process-and-read-ledger.json',{'testerPolicyCompileAndJvmCalls':2,'optionalNewPolicyHelperCalls':0,'newGradleAndroidDeviceMediaParserCalls':0,'originalPythonAuditFirstExit':1,'auditCorrection':'Tester assertion assumed versionName occupies an indented standalone line; actual Gradle puts version fields on same line. Changed to exact whole-file old-version->new-version equality. Finalizer first assumed every SBOM coordinate has binary SHA; annotation aggregator and kotlin-bom are metadata-only and correctly have empty binary hashes. Narrowed to applicable binary components plus exact two metadata-only identities. No product change, no JVM/test rerun.','policyJvmRerunForAuditCorrection':False,'identityReadScope':'finite raw file hashes, ZIP member decompression/CRC, binaryAXML/DEX/classfile and APK signature reads. These DO read media bytes as opaque assets/containing files; no MP4/AVC/Media3 parser/decode.','logicalAssetPasses':'materials verifier inherited baselines; independent728hash/ZIP728; raw APK asset comparison; post728hash; explicit old-baseline preservation. Not physical disk I/O, not original QUAL03 or future Android8MiB ledger.','apksigInternalFileReadBytes':'NOT_INSTRUMENTED_DO_NOT_INVENT_ZERO_OR_EXACT_TOTAL','actualAndroidMediaMethods':'NOT_RUN','oldUnknownActions':0,'sameFrozen728After':True})
audit=read(E/'independent-audit-summary.json');policy=read(E/'policy-signatures-001/result.json');assert policy['policyCases']==17
findingtext='\n\n'.join('### '+f['id']+' / '+f['priority']+' — '+f['title']+'\n\n原映射：'+f['prior']+'；证据类型：'+f['type']+'；Android动态复现0。\n\n触发：'+f['trigger']+'。\n\n证据：'+f['facts']+'\n\n影响：'+f['impact']+'\n\n集中修复：'+f['fix']+'\n\n准确冻结来源：'+'；'.join(a['path']+':'+str(a['line'])+'（SHA '+a['sha256']+'）' for a in f['evidence'])+'。' for f in findings)
text='''# D1 Media3 Android02 BUILD_RECOVERY01 独立完整阶段B复审 V1.0

2026-10-21；tester；新冻结728完整恢复包，原372静态审已先完成发送。

## 结论

**OFFLINE_ARTIFACTS_VERIFIED_WITH_5_SOURCE_BLOCKERS_ANDROID_NOT_RUN**。新APK/源-class-JAR-DEX/签名/准确资产/实际strict双闭包及两次原构建返回已独立核实；17项有限公共政策与四份真实APK验签通过。集中交回**5项P2源码/观测阻断**：R01-B01部分case历史导出、R01-B02 SDK/native/actual及phase分层、R01-B03最后受控时间点、R01-B04 rawFD包装异常保管、R01-B05原Media3 muxer异常后未被Job保管/关闭门覆盖。最后一项为独立新增，不只转发coder两项自报。

这不是5次Android实机复现。实际Android/Media3容器解析、mux、nativeFD/平台finish均**NOT_RUN**；当前不能签设备执行就绪、完整容器链PASS、HOST_ISOLATED_FORMAT/READY/COMMIT/播放/RCE/J11/P0或D1通过。M0未启动。全部问题在整包报告集中回交，由负责人统一派下一批，未逐项发修。

## 准确封存与独立材料审

coder完整报告11433B/SHA a0dbc309e9f7df2c1e07dd0cb0e74330f43b033a7940eb137e66f50079901481；seal f58ff8acfea8d05a75af6dc46f80307afac3d5d9d12ed175dc838fc976786937。纯Python新材料入口0c3c114254ab72059301517f917e5b1da5d3ac8c71d0becde3aabdd655bd5649通过；另独立核**728原文件/728唯一ZIP成员**全集、大小/hash/成员CRC解压及结束再hash。外ZIP12879742B/SHA bd9fd8d83c39cc12de616cddcd01cfff01118652f68ac16582484b1aff1c2ced。候选保持不变，无cache/registry旧进程查询、无新Gradle或设备动作。

逐src/android/upstream/instrumentation/app/src全集比旧372，准确**7处声明差异（6Java+1testManifest）**无增删漏项；app Gradle另仅versionName改RECOVERY01，原锁/verification逐字不变。阶段A补充在首构建期间到达，首构建原源/产物保存在build001/before-stage-a；第二构建完整采用最终源pin。旧九份相对Android01差异不能误报成本恢复新增九处。

## 实际双APK与来源链

| 最终产物 | 大小 | SHA256 |
| --- | ---: | --- |
| app-debug.apk | 7124541 | 0998beeaa129ef3858fbe1122b80394383f96ad75196c8e4f22b4b856237f6c8 |
| test-debug.apk | 466368 | f8323a1c0d82d23382baf4f776e56b26174fd5354de5e86d897cb979a467f5de |

真实app class JAR130790B/hash95a6068c5719cc4400d2e10d8dd4262a40d7fe4463166b7889975c4b02f62e6b；test class JAR32695B/hash5742a92cb8910689db7e464a7992093848162e00a47147924c6a79e3de9d6940。独立JVM classfile SourceFile/major55/sourcehash/classhash/JAR entry逐项86类（78生产+8instrumentation），APK实际DEX全类存在；原Extractor/FragmentedMuxer以及run/receipt/预算/原返回等核心方法有真实codeOffset/指令体。此为源pin与产物链交叉证据，不声称JVM字节与DEX逐指令等价，更不等实际方法已运行。

真实二进制AXML包com.videokit.d1media3.android02/.test、versionCode1、RECOVERY01、process:media3、准确built-in runner/targetProcesses已核；零权限/活动服务provider receiver/native，无sharedUID，无JCodec/JAAD/fork/fixture-tool/host checks混入。继承android构建定义集合与Android01准确同，不一概误判平台类。test不混入Media3本体，实际通过app闭包。准确qualified8849/hash19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c、BBB349102及来源/资格manifest/许可资产逐字对应；无替代旧APK。

固定apksig9.3.3先对verification元数据SHA准入，tester自己一次有界控制器编译已读固定公共政策/验签helper，再一次JVM执行；**17政策项/4个实际APK（最终2+首构建保全2）签名v2=true/同单证书5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f通过**。class path最终生产JAR在前，来源打印准确；未运行ExperimentJob、Android方法、媒体parser或旧host大套件。javac PID36740 UTC03:53:59.597177–03:54:00.465068，JVM PID6736 UTC03:54:00.465068–03:54:00.816889，原exit0/两流关闭；总1.25秒、两进程各heap256MiB、全窗口<30秒。stdout0/1511B、stderr均0。可选新增tester纯Java helper未使用，没有为审计脚本修正重跑JVM。

## 两次构建、实际strict消费及原返回

仅读准确冻结原receipt/controller/全stdout-stderr/daemon快照，不新查询进程。001 client28184/daemon22948 UIDcf8fac88-ff0c-4260-a786-800c078335f6 UTC03:31:18.427016–03:32:59.039903；002 client36588/daemon39576 UID15d77138-57c5-43dc-845f-6203324b6da2 UTC03:35:33.027334–03:36:10.047127。各client原exit0/两流关闭、daemon准确新创建时间/镜像及同已持有Win32 handle waitResult0/exit0，UID/PID与各自当次日志及client stdout对应，真实BUILD SUCCESSFUL及shutdown末句相符。保留single-use daemon事实，不把--no-daemon请求误报为没有JVM。两次各<600秒/每流<16MiB，无第三构建/kill/stop。

每次实际consumption原事件独立提取**300唯一artifact=123binary+37module+140POM**，每项实际镜像/metadata副本SHA吻合verification并与原Android01实际300身份完全相同；不是只请求strict或读取SBOM。app/test四个实际configuration分别compile12/runtime17/testcompile12/testruntime0，逐独立事件集合吻合锁，不从app17推测试闭包；各两条实际javac classpath事件。metadata verify true、锁与元数据原字节，Media31.9.3及原17坐标不变。

新SBOM17坐标/适用binaryhash/许可项与闭包核实；annotation聚合坐标和kotlin-bom仅metadata消费，空binaryhash不冒二进制。继承source-admission及官方metadata来源封存，BBB与合成资产来源保持；不将静态依赖准入扩大成专利/商业/FFmpeg/模型/发布清权。原Android02 372/Android01 740/Container02 676/fork2738与QUAL03/A证据各原manifest及全部列项再次核保持，不改报告和旧失败。新4个构建进程返回不解决旧daemon35512或48945/17257的UNKNOWN，也不证明host全局空闲。

## 全scope源码、旧问题迁移与未运行边界

唯一外准入scopeAll，内部preopenAdmission/rejectFixture/cancelLateRead/writerPending/inspectKnown/inspectShort3/inspectUnknown/inspectSeek1s/bbbObserve/muxQualified十项，同一Job/同一原worker/同一60秒；newJob计量不再每case重置。原assetOwners/providers/factories保留跨case，inputReserved/outputAttemptReserved累计；controlled读1/写4预扣属于保守controlled口，不冒真实native传输。每case成功资源返回后才进入后继；异常和UNKNOWN停止，不为补历史重试。

| 旧372静态项 | 新728裁定 |
| --- | --- |
| A02-S01 raw flags全1冲突 | **源码政策已修，17有限host政策通过**；actual raw flags保留，仅KEY+末index5的LAST可准入，mux只传已准入key语义；真实extractor/fMP4 flags仍NOT_RUN。旧q.flags列表仍存在但不再作raw全等。 |
| A02-S02 早body marker | **仍适用，R01-B03**；清理后还有同步returned回调。 |
| A02-S03 原FD包装保管 | **仍适用，R01-B04**；Os.open表达式/外owner赋值窗口未变。 |
| A02-S04 同scope全case预算 | **部分修复**：同Job native/copy/EOF与output attempt累计已修，六操作/双APK文本上界计划已补；SDK requested/phase分层归R01-B02，准确外设备/捕获/全wall/cleanup仍待派发前绑定。不能搬称全项未修或已全闭。 |

实际CSD由真实Format.initData逐buffer记录长度/hash、AnnexB4 concat20比固定规范化hash，不照抄host SPS7/PPS3/20成三数组；sample比较真实normalizedAnnexB1340/hash/PTS0..1e6，旧rawAU1360不混。真实raw flags在receipt保留，未知bit拒，不现场mask求绿；实际库可能字段/附加位返回仍未运行。独立DTS API明确NO_INDEPENDENT_DTS_API，不用PTS代DTS。真实input/fMP4 duration须SeekMap或TrackOutput1200000，否则UNPROVEN/拒；空EOS4/1200000只是原E6意图，非第七payload或实际duration证明。原fragment3000/copying不变。

MatureExtractor/capture→原MatureMuxerBinding/FragmentedMuxer→原Sink→同writer/task/只读grant→实际fMP4 parser的源码与DEX链存在，但实际执行0。MC-B01同grant一次REOPEN、未返回pending不sticky/不耗检查保留原已修源码，不重复原旧20父组/含8子项。controlled BoundaryScenarios不冒nativeFD错误注入，也不等全取消阶段覆盖。finalizer owner-at-receipt1、super.finish外部原返回/两流完成分列，source0/Future.done/SDKclose不替原返回。

## 集中问题（一次交回）

'''+findingtext+'''

## 全48项与后续准确范围

independent-m2a01-m2a48-results.json对M2A01–48逐条原oracle给离线证据/源码缺陷/平台NOT_RUN边界；未改A的48个PREPARED_NOT_RUN，未把17公共政策项冒48个Android PASS。实际FD/格式/PTS/DTS/duration/flush-sync/原mux/finish、真实sourceepoch/FD峰值/取消各阶段均未运行。

计划准确双APK合计7590909B，六逻辑调用（fingerprint1、本APP/TEST存在性各1、准确各install1、不-r，scopeAll instrumentation1）；命令每op4096总24576，上行逻辑payload7615485B；preflight786432/install131072/instrumentation pending+final1048576/controllerproof1048576，总下行文本3014656B；每receipt262144B。独立算术核这些上界准确，ADB协议framing明确未观测，不造精确wire字节。scope/serial/freshIdle/captureTool尚null，完整外wholewall/cleanup处置与捕获工具/协议预算需在缺陷处理后的准确新设备合同绑定，不能以当前六逻辑计划自动执行。

用户持续平板使用授权保持，无需再重复向用户索取通用平板授权；当前范围仅离线B，未发起设备/ADB/5037/占用/安装/生成播放或网络/旧进程动作。当前五项问题先由负责人统一组织新集中修复，再整包独立复审及另派准确设备范围；本tester不自行改候选、开第三构建或转设备。

## 过程与冻结

一次独立Python材料核和独立自写审计完整完成；初审tester对Gradle versionName行缩进的错误断言（实际同一行含多个version字段），改为整文件旧version→新version精确等值；最终器首次误假设所有SBOM坐标都有binaryhash，明确annotation聚合与kotlin-bom仅metadata消费后按层核实。两次均为tester静态断言修正，不属于产品错误，未改候选或重放JVM。读取过有限文件/ZIP/AXML/DEX/class/签名及包含媒体的opaque字节，不能声称媒体载荷读取0；没有MP4/AVC/Media3解析，也不倒灌旧QUAL03或未来设备8MiB账。本机apksig内部读量未单独观测，不伪填0或精确总量。

本报告/完整问题/48矩阵/独立源与binary审/两build消费/原返回/17政策与签名原流及owner/旧seal保全一并冻结于D1_MEDIA3_ANDROID02_BUILD_RECOVERY01_REVIEW_EVIDENCE，manifest在全部写完后生成；发送收据另存证据目录外。冻结后不改报告及已发送证据，停止后继等负责人整包处理。没有自动审批拒绝或待用户重复授权动作。
'''
assert 7124541+466368==7590909 and 6*4096+7590909==7615485 and 786432+131072+1048576*2==3014656
REPORT.write_text(text,encoding='utf-8')
manifest={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'overall':'OFFLINE_ARTIFACTS_VERIFIED_WITH_5_SOURCE_BLOCKERS_ANDROID_NOT_RUN','report':REPORT.relative_to(R).as_posix(),'reportBytes':REPORT.stat().st_size,'reportSha256':sha(REPORT),'evidenceFiles':[pin(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json'],'independentFindings':[f['id'] for f in findings],'oldUnknownActions':0,'deviceActions':0,'actualAndroidMediaRuntime':0}
save('review-evidence-manifest.json',manifest);print(json.dumps({'reportBytes':manifest['reportBytes'],'reportSha256':manifest['reportSha256'],'manifestSha256':sha(E/'review-evidence-manifest.json'),'evidenceFiles':len(manifest['evidenceFiles']),'findings':len(findings),'overall':manifest['overall']}))
