from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,text):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(text)
a=load(B/'evidence/apk-audit.json');native=load(B/'evidence/cpu-native-build.json');app,test=a['apks'];cpu=native['output'];inputs=hashlib.sha256((B/'evidence/final-build-inputs.json').read_bytes()).hexdigest()
receipt='5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962';budget='730a73e1-50e1-4198-a515-047104f00e31';batch='D1-E4A-E6-NORMAL-TABLET-20261017';methods=['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']
common=dict(e4Batch=batch,e4BudgetIdentity=budget,e5aObservation='REVIEWED_ORIGINAL_N2_SETTLEMENT',e5aSettlementReceiptSha256=receipt)
steps=[]
for i,m in enumerate(methods):
 args=dict(common,**{'class':'com.videokit.spike.e4.E4DeviceTests#'+m,'e4Case':m});argv=['-s','HA1Q6WXR','shell','am','instrument','-w','-r']
 if i==3:args['e4NormalReceiptSha256']='<SHA256_OF_INDEPENDENTLY_REVIEWED_THIS_E6_TWO_NORMAL_RESULT_REPORT>'
 for k,v in args.items():argv+=['-e',k,v]
 argv+=['com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner'];steps.append(dict(order=i+1,method=m,arguments=args,reviewOnlyArgv=argv,gate='Both actual E6 normal PASS, independent normal receipt bound same tablet/batch/outputs and all original owners returned' if i==3 else 'All preceding stages independently admitted; each new host must actually observe original settled N2 before fixture/source/session'))
plan=dict(schema=1,candidate='D1-20261017-E6',state='REVIEW_ONLY_NOT_DEVICE_EXECUTION_PERMISSION',serial='HA1Q6WXR',user=0,versionCode=6,versionName='D1-E6',apks=a['apks'],signer=app['signerCertificateSha256'],deployment=dict(order=['app','test'],argv=[['-s','HA1Q6WXR','install','-r',app['path']],['-s','HA1Q6WXR','install','-r',test['path']]],noUninstallClearDowngradeReset=True,appUid=10221,testUid=10222),normalBatch=batch,stableBudget=budget,priorConsumptionBytes=53651,activePendingExpected=False,steps=steps,perNewHost='Original unchanged E5AFinalObservation actually executes in @Before. Old receipts alone never grant admission.',preserveRecoveryBatch='D1-E5B-N2-RECOVERY-20261017',noNewQueryAbortOrStandaloneObserve=True,stop=['Any FAIL/BLOCKED/PENDING/UNKNOWN, missing actual return/close, bad fixture identity, schema/diagnostic gap, unexpected timebase/PTS/content/EOF or metadata bound: stop and retain all old/new artifacts and ledger.','No retry, deletion, budget UUID/account replacement, forced-close/reset, duration extension or next method to seek PASS.','No whole class selection, native fault/signals, G01 fixture rerun, original media transfer or decoder/network whitelist change.','Cancel receipt placeholder must be replaced by newly independently reviewed exact E6 two-normal report SHA; not an old normal report or this delivery SHA.','No ADB/Gradle/media concurrency. 60s method/first cancel30s and original @After actual terminal gates remain.'],limits=dict(methodSeconds=60,firstCancelSeconds=30,sourceReadCallsPerCpu=8192,compressedReadBytesPerCpu=67108864,outputBytes=2097152,outputHashReadsPerProduct=3,outputHashTotalBytesPerProduct=6291456,metadataLogPerMethodBytes=4194304,sourceFrames=6,encoderInputs=6,encodedSamples=6,outputDecodedAcceptedFrames=6,ptsToleranceUs=1000),requiredEvidence=['READY with original source/codec/isolated verifier identity separation and 6/6/6 plus complete 6 decoded, source timeline, unchanged thumb/content/visual checks and full EOF','validatorNativeDiagnostic complete dedicated HOST_DIAGNOSTICS field: code=E6_NATIVE_OK/site0, actual packet/decoded/accepted counts, lastPTS, demux_eof1/decoder_eof1/drain1 and actual read-at/compressed bytes. Missing is NOT_COLLECTED, never zero.','Original actual resource/slot/source death/FD returns and unique R/S settlement against stable original budget, preserve all prior53651 and N2 R/S0/archive','Separate first native code from cleanup/owner outcome; fail cannot erase actual return or old FAIL'],deviceCalls=0,originalSourceReads=0)
put(B/'tools/device_plan.json',json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
table='\n'.join('| '+x['role']+' | '+str(x['bytes'])+' | `'+x['sha256']+'` |' for x in a['apks'])
delivery=f'''# D1 E6 完整交付 V1.0

2026-10-17。D1-20261017-E6 / versionCode6 / D1-E6。已复现E5C-REG-F01的容器时间错误，完成生产封装修复和精确验证诊断链、本机关键证据、native及双APK离线构建。Android正常回归NOT_RUN；不宣称原设备失败已转PASS。D1 NOT_PASSED、M0 NOT_STARTED、全P0/正式Flutter/独立Kit/框架许可与历史FAIL保持。

## 有据定位与修复

唯一获准导出件failed-output-53651.mp4（SHA20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd）容器有两段5+1样本，90000Hz首段时长18750×5，尾段duration0，无tfdt/ctts。首段最后间隔被重复，使第六样本按FFmpeg8.0.3既有MOV track_end回退时间推为1041667µs；真实源及编码输入末PTS1000000µs，偏差41667µs，明确超过原native1000µs门。前五帧日志与此一致。原当时未记录具体拒绝谓词，不能把本机推导改写成旧实机branch trace，也不能排除后续其他条件。

使用实际缓存Media3 1.9.3封装库与原六样本有界回放，旧200ms策略复现5+1及41667µs偏差。新生产E6Muxer把合法<=2s六样本放同一fragment（3000ms是分段阈值，不是延长执行时限），并给空EOS元数据lastPTS+200000；新段durations=[18750,18750,18750,18750,15000,18000]，六PTS全部准确、最大偏差0。空EOS不是第七帧。实际源/编码PTS不重写，encoder/mux完整六样本/EOF/PTS/画面门均保持。最多6×262144B复制样本，2MiB输出上限未变。

新增numeric-only native诊断：命名谓词/原源码site/阶段/AVERROR原值、视频packet send次数/解码与接受帧、末PTS、demux/decoder EOF、drain、实际readAt调用/返回压缩字节。固定13数值经原鉴权Binder一次传输，校验1024B、取值、stage/帧数一致后保留；ERROR保留原精确安全码。E6FailureCodes有界解开future causes，首错不被cleanup覆盖。专用validatorNativeDiagnostic报告字段和仪器输出名单保留全结构，不依赖160字trace行。缺失诊断明确NOT_COLLECTED；pending Java原异常不会被cleanup后的JNI诊断覆盖。

## 验证与最终产物

| 角色 | 字节 | SHA-256 |
|---|---:|---|
{table}

最终双APK在docs/coder/d1e6/artifacts/D1-20261017-E6/final，证书均 `{app['signerCertificateSha256']}`；原两个私有服务/无新增权限与INTERNET/原AppID保持。签名与7native对应字节核验PASS。最终输入SHA `{inputs}`，最终repair-002成功绑定。

本机生产C同一e6_verify.h真实执行17项（合法6帧/末帧、原41667偏差、1000边界、真多/少帧、缺EOF等），生产Java诊断/异常与cleanup、原画面/映射/时间表17项，合计34 PASS；实际Media3回放另单列PASS。JVM回放只替代Android SparseArray与TextUtils基础容器/文本API，未替代Media3封装算法；不是Android解码通过。最初两个JVM harness因SDK Stub方法停止，补独立基础API shim后复现；未据此变更产品门。原历史270/82未重跑。

只重建独立项目libvideokit_cpu.so：18552B/ed02feb238b26ea2ac53b6ae2eafca3d3131d74ebfdfd52c39ff3a925648e9a7 → {cpu['bytes']}B/{cpu['sha256']}。另六库逐字节不变。原NDK30.0.16248370/API31/FFmpeg8.0.3及有限codec/demux/禁网络配置不变。七库ELF LOAD>=16KiB，最终APK zipalign -P16静态PASS；不是Android16KiB实测。精确源码diff、源码/header/config身份、构建命令/日志、native/Maven差异和NOTICE-E6随包；35Maven坐标锁不变，无下载。完整原C14对应源容器保留。

集中main-001及必要repair-001/002均编译成功。两次repair仅完整诊断报告及仪器输出白名单贯通（最终静态核查发现旧trace160字截断及显式字段名单遗漏）；前两轮APK、审核/输入/理由/日志及build-results-before-*全部保留，最终只取final。native包装库只编译一次，无第三方重建。

## 范围与交接

原E5C144项和E5B1561项不可变来源只读校验PASS。Guard/恢复/Observation/Admission/Lifecycle/Budget字节不改；原N2已结算、53651消费及失败产物不动。只读获准导出件两次共107302B，原test_media/设备/ADB/QUERY/ABORT/媒体传输/native fault/下载均0。私有回放派生媒体不放源码ZIP；其hash/时间表/工具和限额有记录。

四文档、tools/device_plan.json、source-manifest与完整源码ZIP/双APK/外seal一次交负责人复审。下一正式批次仅同签名保数据部署→正常MP4→AVI→能力拒绝→条件cancel，每新host原实际观察，稳定budget不变、无新ABORT；真实动作尚未启动。
'''
architecture='''# D1 E6 架构及威胁边界 V1.0

2026-10-17。本批修复输出时间封装，并提供精确诊断；隔离解析与真实画面验证不降级。

## 根因证据链

已授权导出件唯一固定53651B/SHA，经只读容器解析：首moof5样本duration均18750/90000s，次moof1样本duration0，无tfdt/ctts。对照原FFmpeg8.0.3 MOV代码的无tfdt/sidx→track_end回退、原JNI逐帧PTS谓词及旧实机前5日志。真实输入六PTS为0/208333/416667/625000/833333/1000000；旧容器末PTS1041667。原JNI输出验证在verified=5时仍按expected[5]比较；不把未写第六callback当仅解码五帧。

实际Media3旧配置复现相同两段错误；新生产E6Muxer与同版本真实库回放修正为一段六样本、末间隔15000和结束duration18000，所有PTS无偏移。封装3000ms阈值覆盖原2s合法输入窗和0.2s空EOS；仍2MiB最终文件、6samples、原压缩单sample256KiB。这里只改变分段策略和结束元数据，不改编码输入或时间、容差、解码计数、内容检查。旧native实际哪条branch当时未记录；目前证据证明容器缺陷可触发原拒绝，实际Android仍待复核。

## 生产native变化与精确诊断

原codec send/receive/drain循环没有为了PASS改写；AVERROR(EAGAIN)/EOF严格原规则保持。新e6_verify.h抽出等价严格维度/六帧/1000µs/完整demux+decoder EOF谓词，依旧在像素/PTS合格后才发frame callback、逐帧accept后才计数。源码原索引短路保持，第七帧不能读expected[6]。EOF不够6或decoder未EOF继续拒绝；无fake EOF或content pass。

在原cleanup真实释放FFmpeg对象后，若无原JNI pending Java异常，发一次onNativeDiagnostic（10个int+3个long）。site0表示本次成功；reason1…9表示DIMENSIONS/EXTRA_FRAME/PTS/MISSING_PTS/DEMUX/SEND/RECEIVE/DRAIN/INCOMPLETE_EOF；其余失败reason0/nonzero site精确映射到冻结cpu.c原行谓词。evidence/native-diagnostic-sites.json绑定源码SHA及每处条件。FFmpeg返回失败处保留原AVERROR，不把业务谓词0当系统错误；早期JNI返回或pending callback原异常若无snapshot，明确NOT_COLLECTED，不补零。

pkt计数为选中视频packet发送尝试数，decoded是receive实际帧数，accepted是完成原frame ACK后的数量；native readAt是JNI实际调用次数/返回字节，host另记录broker requests/returned bytes，不能以缺日志为0。诊断只含固定数值和本地映射的安全码，无native任意字符串、源路径、句柄或凭据。

CpuProtocol新增NATIVE_DIAGNOSTIC=17，保持单APK同版本host/isolated部署。原真实caller PID/UID/task/epoch/revoked检查及1024B metadata限额先于分发；一次snapshot、阶段/accept计数和字段边界校验，拒绝重复/错阶段/越界/尾数据。DONE仍需原6帧+orientation，另需本次native site0/accepted6/demuxEOF1/decoderEOF1。错误对象保留结构及代码，经原Future传播、E6FailureCodes最多8层first cause，cleanup suppressed单列。主报告validatorNativeDiagnostic完整字段与仪器HOST_DIAGNOSTICS显式名单贯通，trace只记短code；原160字行不会裁掉EOF/read计量。

## 保持的隔离、所有权及原现场

主进程不解析不可信原压缩媒体。真实六源解码和输出验证仍在无FD/path的isolated CPU，原broker只授予来源readAt；编码仍私有codec进程/真实MediaCodec，thumb/content/mapping完整校验仍生产PipelineRules，未用桌面回放代替。绝对60s、首次cancel30s、原session/CPU/slot/FD/Native call真实返回、callback ACK及原budget/R/S/无pending门不变。代码所有权/lease/current-host观察未新建替代路径。

原E5C/E5B冻结、实际G01范围、原N2结算R/S0/原closeACKfalse、旧N2 FAIL、53651消费/失败输出保持。新candidate不带一次性已消费的E5C夹具入口，不重跑旧根；Guard等相关生产源码字节不变。原本机/旧设备UNKNOWN不补证或清理。

## 本机证据边界

17项C测试直接编译并运行同生产header（Windows普通进程返回，无信号故障），17项Java执行生产诊断/cause/cleanup及未改PipelineRules正负例。真实Media3回放仅有独立SparseArray/TextUtils API shim，不替换封装算法；尚未桌面解码、Android JNI/Binder/MediaCodec/真源回归。静态传输/schema核验与编译不能代替远端实际调用。新的native诊断本身亦待Android实证。

原有限FFmpeg版本/配置/算法源码/六库不变，仅本项目cpu JNI wrapper重编；NOTICE-E6、完整原C14对应源容器、所需header/config及exact SHA/diff/build保留。静态16KiB ELF/ZIP检查不等于16KiB设备通过，SBOM/来源不是合规或安全放行。
'''
gates='''# D1 E6 剩余门复审 V1.0

2026-10-17。本机容器错误复现与修复有证据，实际Android产品验收仍待正式派发。

| 项 | 当前结果 | 仍需证据 |
|---|---|---|
| E5C-REG-F01/P1 | 旧容器5+1/末PTS偏41667µs复现，生产封装回放修复；旧实机原具体branch未补写 | E6实际MP4完整READY及精确新诊断，不能改旧FAIL |
| 严格六帧/末帧/多/少帧/EOF/PTS | 同生产C helper17项PASS | 实际JNI/FFmpeg解码与原输出全链 |
| 内容/映射、诊断/cause/cleanup | 原生产Java17项PASS | 实际真实源thumb/输出内容/完整诊断跨Binder报告 |
| Native/Maven | 仅CPU JNI包装库变、另六库及35坐标不变，原版本/白名单不扩；静态ELF/ZIP16KiB PASS | Android系统实际加载/验证，许可/安全既定审查 |
| 原N2/稳定budget | 结算和原R+S0/归档、53651消费/无pending保持 | 每新host真实最终观察，不靠旧报告放行；无新ABORT |
| G01 | E5C生产锁边界实证接受范围保持，相关核心不变 | 不将其扩称全恢复或产品通过，不重跑已消费根 |
| MP4→AVI→能力→条件cancel | 本批NOT_RUN | 新冻结候选独立复审、同签名保数据部署，准确顺序真实证据/本批两正常receipt |
| 全P0/正式Flutter/独立Kit/框架许可/旧signal | 原未完成/未通过保持 | 原既定产品链与全部验收 |
| D1/M0 | NOT_PASSED/NOT_STARTED | 不能把当前debug原型当正式交付完成 |

所有失败、诊断缺失、owner未实际返回或时限到均停止，不放宽frame/PTS/EOF/visual，不延时、不重跑、删产物、clear、清账、换UUID/账户或自动下一方法。新batch仍保留所有旧消费和失败输出；下一批任何真实损耗按原唯一R/S结算，不能为测试抹账。
'''
appendix=f'''# D1 E6 设备执行附录 V1.0

2026-10-17。精确待审计划docs/coder/d1e6/tools/device_plan.json；本次coder设备调用0。负责人/独立审查通过后再正式派发，不把此文件当执行许可。

仅原平板HA1Q6WXR/user0，AppUID10221、testUID10222，原同签名。核最终seal/双APK/hash/证书/版本6，再依次install -r app/test保数据更新，禁止卸载/clear/降级/force-stop/清预算/换UID。原N2已结算、原53651消费/无pending及原fixture元数据连续性需有限只读核对，不另读全源hash，不并发Gradle/设备/媒体。

四方法每次精确class#method/e4Case选择，独立新host：normalMp4SixRealFrames→normalAviSixRealFrames→capabilityDenialDoesNotOpenSource→条件cancelRejectsWrongEpochOversizeAndLateFrame。批次{batch}，e4BudgetIdentity={budget}，e5aObservation=REVIEWED_ORIGINAL_N2_SETTLEMENT，e5aSettlementReceiptSha256={receipt}。每个@Before均执行未改生产最终观察，不用旧proof替本host真实归还/死亡/force-close-sync；原recoveryBatch D1-E5B-N2-RECOVERY-20261017不改，不新QUERY/ABORT/独立OBSERVE。

每方法必须同时通过JUnit和业务/资源证据：正常真实六源、相对PTS与真实时间基、6inputs/6samples、isolated verifier完整6frames/EOF/原thumb-content-mapping/READY，实际source/CPU/codec/FD/slot/native/CONTROL/owner finish归还及合法R/S/无pending。新HOST_DIAGNOSTICS.validatorNativeDiagnostic必须完整输出code/site/stage/AVERROR/packets/decoded/accepted/lastPTS/EOF/drain/readAt/压缩字节；成功为E6_NATIVE_OK/site0/accepted6/EOF1+1/drain1。缺日志=NOT_COLLECTED，不能记0。失败要保留精确first native code和单列cleanup；原instrumentation/system退出不是close证明。

MP4失败即停AVI/后续，AVI失败即停后续；cancel仅本批同设备两正常完整报告独立审证后，e4NormalReceiptSha256填该新报告准确SHA（计划占位符必须替换，不能用旧报告或本交付SHA）。能力拒绝仍须不打开源并真实归还。两正常成功与receipt是外部独立准入，不由shape正则单独算通过。

原方法60s/首cancel30s、每CPU最多8192readAt/64MiB压缩读取、每输出2MiB/最多三次digest合计6MiB、每方法4MiB记录保持。私有预置fixture验证仍原逻辑，不重新导入/扫描/完整源hash；实际source readAt次数/字节从真实计量记录，不用日志行数推测。每新输出R/S消费沿原稳定budget累计，不删除53651失败产物。

任何FAIL/BLOCKED/PENDING/UNKNOWN、schema/身份/EOF/内容/资源/时限不符均整批停止保留原现场，集中报告，不临时改库、放宽验证、重试或下一方法求PASS。无新native故障/信号、G01根重跑、框架/依赖/权限变化。下一批结果仍需独立集中复核，不自动M0或正式项目交付。

本机只读重核可执行tools/e6_package.py verify；ZIP包含完整E6源码/config/native/build/diff/NOTICE及原完整C14对应源容器，配置自己local.properties后用既有缓存离线构建，无私钥/缓存/真实媒体。native build和local tests需显式运行且冻结后工具拒绝改候选；不要为复核重建已冻结产物。导出分析工具默认INSPECT不读文件，显式重现会新增一次53651B读取且本交付未执行；不在只读verify中自动运行。
'''
for suffix,text in [('DELIVERY',delivery),('ARCHITECTURE_AND_THREAT_BOUNDARY',architecture),('REMAINING_GATE_REVIEW',gates),('DEVICE_EXECUTION_APPENDIX',appendix)]:put(R/f'docs/coder/D1_E6_{suffix}_V1.0.md',text)
print('E6 four complete documents and exact review-only device plan written')
