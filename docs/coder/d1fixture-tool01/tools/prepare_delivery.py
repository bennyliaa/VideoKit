from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'fixture-tool01-freeze.json').exists()
audit=json.loads((E/'jar-audit.json').read_text());build=json.loads((E/'build-result.json').read_text());assert build['status']=='COMPILED_AND_PACKAGED_ONLY_NOT_RUN'
driver=[x for x in json.loads((E/'source-input-pins.json').read_text()) if x['path'].startswith('driver/')]
for x in driver:assert sha(B/x['path'])==x['sha256']
bindings={1:['compiler-identity.json','build-recipe.json'],2:['source-input-pins.json','extracted-source-identity.json'],3:['build-result.json','build-001/javac-owner.json','build-001/jar-owner.json'],4:['jar-class-origin.json','jar-audit.json'],5:['sbom-and-licenses.json','source-license-inventory.json','licenses/SOURCE_NOTICES.txt'],6:['build-recipe.json','static-validation.json'],7:['SixFrameDriver.Job.prepareDirectory','FileOwner.open'],8:['Job.writer/reader/channel final holders','FileOwner state before open','phase=MUX_CREATE'],9:['AttemptBudgetChannel.write while remaining loop'],10:['attempted += count before writeOnce','per attempt<=65536'],11:['same source position advances by actual returned only','next partial suffix reserved again'],12:['setPosition does not refund','extent=max acknowledged ends','rewriteAttempted tracked'],13:['NATIVE_WRITE_FAILED_OR_UNKNOWN','physicalPositionUnknown=true','no further admission'],14:['returned<1/>count reject','empty buffer has no loop/native call'],15:['MAX_ATTEMPT-count subtract checks','seek0..16MiB'],16:['position()/size truthful native getters','read/truncate rejected'],17:['Job synthetic YUV loop','55296*6 reservation'],18:['encodeFrame actual nonempty/keyflag/IDR guard','frameEvidence raw AU size/hash/NAL list'],19:['Packet i/5 duration1','actual track duration units6','no E6 EOS written in JCodec path'],20:['frameEvidence before addFrame','original CodecMP4MuxerTrack single conversion','csdEvidence actual AvcCBox object','actual container per-AU AVCC observations deferred to separately reviewed qualification'],21:['raw SPS/PPS cumulative check before addFrame','CSD64KiB count guards','actual mux-track payload hex/hash and library converted AnnexB'],22:['muxFinishReturned','writer force/close returned','reader exact original close','main same worker joined'],23:['Job.deadline sticky','ORIGINAL strong reference','same worker indefinite join after60s','no interrupt/kill'],24:['never deletes any directory, partial output retained','fresh root only','old scopes untouched'],25:['jar-audit.json','source-input-pins.json','generation-plan.json'],26:['unmodified MP4Muxer.movieHeader new Date().getTime','generation-plan media hash null'],27:['prior-frozen-preservation.json','no old session poll/attach'],28:['completion-matrix.json','generation-plan separate new approval gate']}
phase=json.loads((B/'reference/phase-a-independent-driver-oracles.json').read_text());rows=[]
for old in phase['cases']:
 x=dict(old);n=int(x['id'][2:]);x['phaseAStatus']=x['status'];x['coderEvidence']=bindings[n];x['status']='STATIC_IMPLEMENTATION_TYPECHECKED_RUNTIME_NOT_RUN';x['independentNewToolVerdict']='PENDING_PHASE_B';x['runtimeExecuted']=False;x['executionAuthorized']=False
 if n<=6:x['status']='BUILD_OR_BYTE_AUDIT_COMPLETE_NO_RUNTIME_VERDICT'
 if n==20:x['representationBoundary']='Raw encoder AU and actual mux-track AVCC CSD fields implemented; actual per-AU container AVCC/hash and Media3 representation remain later independent qualification, no current golden'
 rows.append(x)
dump(E/'completion-matrix.json',{'phaseAReportSha256':'1c823c521003c3384cc60a4396c559e5bb98eb5398a60a2d7979508f9c41a330','cases':rows,'attemptExamples':'reference/phase-a-attempt-accounting-examples.json; six DECLARATIVE expectations only, actual Java adapter IO scenarios NOT_RUN','lanes':{'actualBuild':'One javac and one jar each natural exit0','static':'Source/byte/hash/license/class-origin audit, not execution of driver','runtime':'Main, encoder init, native wrapper IO, media generation, Media3 qualification all NOT_RUN'},'D1':'NOT_PASSED','M0':'NOT_STARTED'})
java=next(x for x in json.loads((E/'compiler-identity.json').read_text())['files'] if x['path'].endswith('java.exe'))
command=[java['path'],'-Xmx256m','-XX:-UsePerfData','-jar',str(B/'artifacts/videokit-fixture-tool01.jar'),'--generate-six','--scope=D1GEN01-CANDIDATE-001']
plan={'status':'BUILT_TOOL_PROPOSAL_NOT_GENERATION_AUTHORIZATION','toolJar':audit['artifact'],'toolJarBytes':audit['bytes'],'toolJarSha256':audit['sha256'],'driverInputs':driver,'javaExeSha256':java['sha256'],'futureExactCommandArgumentsProposed':command,'currentCommandExecutions':0,'scopeLabelIsPermissionToken':False,'approvedGenerationScope':None,'approvedGenerationToolIdentity':None,'freshResourceGate':None,'generationAuthorized':False,'output':'D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4','outputOpen':'CREATE_NEW + fresh root/directory + canonical real-path/NOFOLLOW guard; no hostile filesystem TOCTOU/RCE isolation claim','input':'Project-authored YUV420J synthetic pattern only, no licensed source media input','limits':{'heapBytes':268435456,'originalWorkers':1,'nativeFileOwnersMax':2,'perSourceInFlight':1,'queue':0,'inputAttemptedCumulative':8388608,'outputAttemptedCumulative':16777216,'nativeWriteChunkMax':65536,'nativeWriteEventsMax':512,'receiptUtf8Max':1048576,'sampleEachBytes':262144,'sixPayloadBytesMax':1572864,'csdBytesMax':65536,'samples':6,'width':256,'height':144,'rawPixelBytesPerFrame':55296,'rawPixelTotal':331776,'deadlineMs':60000,'ptsUs':[0,200000,400000,600000,800000,1000000],'packetTimescale':5,'packetDurationUnits':1,'expectedEndUs':1200000},'returnPolicy':'Same original external worker join, actual mux finish/optional force/original close separately. Deadline closes admission and emits UNKNOWN then same original join without timeout force. Unknown allocation/close/deadline retains static original; never interrupt/kill/second native close/refund/delete. All candidate directories retained, even known failed output, for later review. No cleanup permission inferred.','evidencePolicy':'At future generation raw encoder AnnexB before mux mutation, six actual PTS/size/hash/keyflag/IDR/NAL observations; actual mux-track AvcCBox SPS/PPS payloads and library-converted AnnexB hex/hash. Raw full output read-only reopen/EOF/hash after same writer close. Actual container AU AVCC hashes / Media3 normalized AU representation / duration/qualification require separate independent review; no unlike representation hash equality asserted. Exit0 alone not PASS; JSON status and original return evidence mandatory. Missing/overflow receipt blocks, no implicit rerun.','currentMediaSha256':None,'currentCsdHashes':None,'currentAuGolden':None,'wholeMediaHashRepeatableClaim':False,'timebaseAndPixelsDeterministicButMovieTimestamp':'Original MP4Muxer.movieHeader uses current Date, so output hash must be frozen from actual one future generated file, no repeated hash guarantee','e6Boundary':'Current JCodec consumes6 Packets+finish, no seventh payload or E6 empty EOS. Later Media3 E6 must receive empty flags4 EOS1200000/fragment3000ms under its own approved qualified scope.','requiredNextGates':['Coordinator and tester B review exact immutable built tool/driver and byte/code evidence','Resolve any concentrated review defects via a new separately authorized batch, never rebuild this frozen candidate','New exact generation approval and budgets/owner/resource scope, not old once/scope/host idle balance','Actual generated immutable file/metadata/CSD/NAL/AU manifest and independent real Media3 fixture qualification','Only then a new Android mux candidate with fixed registry admission; no App/APK dependency change in this batch'],'legacyLocalOwners':'Original48945/17257 remain UNKNOWN; no collection/attach/diagnosis/intervention in this batch; isolated tool build is not host-idle proof'}
dump(E/'generation-plan.json',plan)
dump(E/'controller-return-receipt.json',{'toolSession':73877,'observedProcessResult':'exitCode0 from existing exec session final tool output','originalControllerReturned':True,'compilerInvocations':1,'jarInvocations':1,'newBuildToolRetry':False,'runtimeMainCalls':0,'oldOwnerSessionCollections':0,'evidenceSource':'Current coder tool-call history; actual JDK original process owners independently recorded in build-001'})
foot=[p for p in B.rglob('*') if p.is_file()];total=sum(p.stat().st_size for p in foot)
assert total<67108864
dump(E/'candidate-pre-freeze-footprint.json',{'allCandidateFilesBytesBeforeThisReceipt':total,'fileCount':len(foot),'deduplicationApplied':False,'buildMeasuredAtReturnBytes':build['actualBuildOutputBytesAtNaturalReturn'],'allCandidatePlusArchiveMustAlsoStayUnder64MiB':True,'scopeExplanation':'Source/main input budget4465907 includes711 actual Java source files. Exact existing installed JDK compiler/runtime pinned separately; JDK installation not a copied build input or package output. Build-output/classes, JAR, package-resource copies, raw logs and all later evidence/package copies counted by actual bytes, not final JAR alone.'})
report=f'''# D1_FIXTURE_TOOL01_BUILD 完整交付报告 V1.0

2026-10-21。一次获准离线javac/jar构建已完成，准确工具身份已取得；提交完整新冻结候选供负责人及tester阶段B独立整包审。**本批没有运行Main、初始化/加载运行JCodec编码器、生成媒体、执行wrapper运行测试或Media3资格化。** 编译/打包不是encoder运行准入、fixture PASS或产品完成；D1未过、M0未启。旧本机48945/17257 UNKNOWN保持，未收取、查询、诊断或干预，不能宣称host空闲或收尾完成。

## 一、范围、固定来源与差异

独立目录D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool01。正式CODER要求及集中阶段A补充、原Android01 B报告845cd5920251c44beed2497d66d6843e5e6531e209d503cc93eb598f45fe2829、阶段A报告1c823c521003c3384cc60a4396c559e5bb98eb5398a60a2d7979508f9c41a330与FT01–FT28/6组示例/证据合同均保全到reference。它们的准备状态没有回写成新实现通过。

仅原批准官方org.jcodec:jcodec:0.2.5 sources.jar1246282B、SHA256 9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db，807条目。708 Java原字节全保留=635 org.jcodec+73 bundled JAAD，4435752B。新增项目driver3文件：SixFrameDriver、AttemptBudgetChannel、ReceiptJson；其hash随source-input-pins.json与generation-plan.json冻结。没有修改任何成熟库源码、MovieHeader时间或容器/codec，没有同名伪接口/补依赖/JUnit/annotation processor/插件。初始化时org-only路径假设遇到bundled JAAD后在文件展开阶段修正，修复前脚本保留；这是编译之前的材料处理，未浪费或重试compiler调用。

完整711 Java输入{build['sourceInputBytes']}B，≤16MiB；固定现有JetBrains JDK21.0.10，java/javac/jar/release/lib/modules准确hash列compiler-identity.json。JDK安装是已有编译工具本体，未复制或下载到包，不把50MB runtime偷偷混入source输入口径。构建脚本及实际读入固定材料也有prebuild-all-candidate-input-pins全hash；显式source argfile、全部原argv/cwd/env去注入选项保全。没有Maven/Gradle、网络、PATH fallback、共享缓存、native/新binary下载；新二进制仅本次按授权从原源码编译的工具JAR，不进App/APK/产品依赖。

## 二、一次实际构建与准确产物

构建一次，JDK工具并发峰1，先javac再jar各一进程；控制器持有原Popen句柄，超时只记UNKNOWN并等待同原返回，未知不准下一工具、无kill/interrupt/盲重试。本次两者均自然exit0，未触发60秒未知路径。javac PID3284原记录UTC00:08:09.652283至00:08:16.778591；jar PID29872 UTC00:08:17.155389至00:08:33.566592。仅记录当次原句柄/argv/起止，不冒未来PID身份；原输出文件也由控制器在原进程返回后关一次。javac有1条上游dep-ann警告及废弃/unchecked提示，原源码不为消警改动，raw stderr保全。

固定javac参数-J-Xmx512m、-J-XX:-UsePerfData、--release11、UTF-8、-proc:none、-implicit:none，classpath/sourcepath/processorpath为空专属目录，711 source全部显式列入；无source自动补全或执行processor。打包固定jar.exe、-J-Xmx512m、Main-Class及entry date2026-10-21T00:00:00Z，只读原classes+准确license resources，不执行任何产出类。编译器/打包器各自60秒观察窗不与未来生成worker期限混同。

产物artifacts/videokit-fixture-tool01.jar：**{audit['bytes']}B，SHA256 {audit['sha256']}**。Main-Class com.videokit.fixturetool.SixFrameDriver；manifest Created-By21.0.10 JetBrains。982个class全部与本次真实javac输出逐字一致；逐class SourceFile/类名/Java11 major55及所属原输入hash均在jar-class-origin.json，classes原文件一同封存，不用自报文件名代来源证据。JAR只有这些class、manifest与明确license resources，无额外class/resource/native。全main树内其他codec/decoder/CLI只是被编译，不能据此获准调用它们。

构建自然返回时实际输出{build['actualBuildOutputBytesAtNaturalReturn']}B，包含classes、JAR、license资源副本、argfile/log/原owner回执；无dedup冒实际占用。最终封存另核所有候选文件+完整源码ZIP仍≤64MiB，不能只用1.95MB JAR作全部输出。当前是实际尺寸/停止后续准入检查，并未建立OS磁盘配额或沙箱，未声称能靠超时强杀来约束compiler；本次实际输入/输出/时间均在界内。

## 三、真实driver与累计attempt通道

未来唯一提案命令/准确tool+java hash见generation-plan.json；--scope标签只是证据标签，不是许可。固定新路径D:/CodexProjects/VideoKit/docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4；新root及new-output均独占createDirectory，输出CREATE_NEW/WRITE/NOFOLLOW。每个既有父逐层属性与真实canonical路径核对，拒绝symlink/isOther/reparse重定向或已有输出，不接受任意path/URL/媒体输入，不覆盖旧路径；这是可信私有workspace的防误用边界，不冒抵御恶意并发文件系统TOCTOU或RCE隔离。

原writer、reader、channel holder在Job与原线程创建前登记，FileChannel.open之前标OPEN_CALL_ENTERED；也早于会立即写header的MP4Muxer构造器。原allocation/close抛错结果未知时保留原holder/Job，不造替身handle。每个native操作在同一原worker，单源inflight1/queue0；原write FileChannel只从预算adapter进入。

adapter.write必须完全消耗来访buffer或失败，解决库constructor/chunk/NIOUtils.writeLong可能单次write的语义。每次至多64KiB，**native调用前按本次requested预留**，positive partial只按actual returned前移同buffer，下次剩余请求再次全量计attempt，不退款。非空0/负值/>request拒绝，不spin；异常后停止并标物理amount/position UNKNOWN，不重发/rewind。写次数/每次requested/return/原buffer位置/累计attempt/已知lower bound/extent等有最多512项有界证据；满界先拒绝再native，不静默丢日志。header回写同通道照计；seek不等写、不退款，offset采用减法边界防overflow，read/truncate拒绝。

FT示例10→3再7→7为attempt17、known returned10、extent10、pos10；seek0回写8后attempt25、returned18、extent10、pos8。六例是继承声明式oracle与静态代码对照，**本批没有运行受控partial/zero/异常/预算边界IO测试**；不能将算术说明写作实际adapter PASS。物理状态未知与最后已知下界分栏，不用file size/最终position代累计attempt。

## 四、六帧、CSD/NAL、时间与证据

仅程序原创YUV420J 256x144六帧，单帧55296B/共331776B。Y unsigned16+16*((x/16+y/16+i)%14)，存signed值减128，U/V signed0；不读BBB/音频/原媒体或解码输入。实际H264Encoder.createH264Encoder、keyInterval1、motionSearch0，原DumbRateControl初QP20，未声称constant-QP或改变成熟实现。

未来encodeFrame每AU实际非空≤262144B，六AU≤1572864B、实际isKeyFrame和IDR NAL都检查，raw encoder AnnexB在track.addFrame变更前留size/hash/NAL类型hash；SPS/PPS累计先守64KiB。实际CodecMP4MuxerTrack自己strip PS并AnnexB→AVCC一次，driver不额外先转换/自写mux。finish后从实际mux track AvcCBox采SPS/PPS原payload hex/hash及库转换AnnexB hex/hash，区分表示。**实际container每AU AVCC数据/hash与Media3归一化观察尚须后续独立资格化，driver当前raw-AU/CSD内部对象证据不冒container重开或跨表示hash等同。** 当前运行0，所有AU/CSD/media golden均null。

六Packet pts0..5/timescale5/duration1，输入PTS us0..1000000步200000，结束6/5=1200000us；实际mux track durationUnits必须6。当前JCodec是六Packet+finish，不额外写第七sample或Media3 E6空EOS，E6 flags4 EOS1200000/fragment3000ms留未来独立Media3范围。该输入时基/像素确定不能推出整片hash每次一致：原MP4Muxer.movieHeader仍用new Date().getTime，未补假golden或改原库时间；未来实际生成一次后再冻实际文件hash、容器PTS/duration/CSD/NAL等。

## 五、原返回、期限和未来生成预算

writer实际mux.finish、同原FileChannel.force(true)、同原close返回、reader只读重开全EOF/hash/原close、同原worker外部join分别留证。只在writer已原close后设只读、开固定reader；复制/原创像素/输出digest/EOF预留全部纳入input8MiB，64KiB块，native owners全局≤2，输出attempt16MiB包含partial/header重写、不退款。输出readback完整文件hash不等格式合格或Media3验证。

未来生成worker60秒观察、non-daemon同原线程，期限关准入，首错/UNKNOWN sticky，原静态Job/encoder/mux/channel引用强保管；外部同原caller继续join同worker，不interrupt/kill/二close、不给迟到成功升级。close UNKNOWN不再native close；allocation UNKNOWN不换holder；未归还目录绝不删，当前实现所有新输出包括已知失败也保留待审，不含自动cleanup/delete。receipt上限1MiB、native写事件512项、heap提案256MiB；pending receipt不遍历原worker正写的列表。没有完整receipt/原进程自然返回，不依exit0补成功或重跑。

这些原FD/fsync/worker/异常/期限代码本批仅编译和静态核对，实际运行全NOT_RUN；不是已经验证native返回行为。原旧UNKNOWN、P0/J11/C13、FFmpeg/发行/专利缺口均不关闭。

## 六、许可、SBOM及28项映射

保全原官方Maven POM/source身份与当前官方仓库FreeBSD copyright2008–2019 JCodec Project/免责声明；不冒不存在的release标签原LICENSE。708文件原头及SOURCE_NOTICES全留，73 bundled JAAD头声明Public Domain及JCodec变更FreeBSD，org/jcodec/common/Preconditions.java为2007 Guava Authors Apache2.0，附完整Apache2文本。POM FreeBSD不一概覆盖全树；evidence/source-license-inventory.json逐file保留原头，sbom-and-licenses.json列来源/适用例外/未运行范围。自有driver只作内部开发审查，本批不作发布许可或专利/商业清权。

FT01–28完整映射在evidence/completion-matrix.json：build/字节审计项有实际证据，runtime项只有静态实现+类型检查、未运行；FT20明确raw-AU/track-CSD与未来container AU表示的证据边界。6组attempt例仍DECLARATIVE_NOT_EXECUTED。源码/编译/未来三栏清楚，不将coder自核冒tester独立通过。阶段A原manifest/source证据保持，完整冻结后由负责人另派B。

## 七、冻结与后续门

新seal evidence/fixture-tool01-freeze.json、源码ZIP D:/CodexProjects/VideoKit/docs/coder/D1-20261021-FIXTURE-TOOL01-BUILD-source.zip列全hash。包含708原source、3driver、完整build recipe/source pins/compiler身份、982实际classes/JAR、许可/SBOM/原调用stdout/stderr/原返回及28项映射。无JDK/缓存/密钥/媒体。纯静态只读入口tools/review_materials.py只核文件/JAR及新旧seal，不编译/不运行任何JVM或挂起场景。

旧Android01 seal740项及更早6232共6972文件逐hash不变，原Android01 B与本工具阶段A独立manifest保持；未触碰原活动目录/session/once/余额。工具来源UNBUILT缺口仅由本批实际产物身份解决，**运行准入仍未批准**。下一步准确built tool/driver负责人+tester B整包审，若有缺陷另批集中修复；之后才可另签精确生成范围/预算/原owner和资源门，实际生成新immutable媒体manifest，再独立真实Media3资格化、另一个Android mux候选嵌入。当前不提前操作任何一步，不启M0。
'''
main=R/'docs/coder/D1_FIXTURE_TOOL01_BUILD_DELIVERY_V1.0.md';main.write_text(report,encoding='utf-8')
dump(E/'main-report-identity.json',{'path':main.relative_to(R).as_posix(),'bytes':main.stat().st_size,'sha256':sha(main)})
print(json.dumps({'report':main.relative_to(R).as_posix(),'bytes':main.stat().st_size,'sha256':sha(main),'matrixRows':len(rows),'toolJarSha256':audit['sha256']},ensure_ascii=False,indent=2))
