from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
oraclePath=E/'independent-m2a01-m2a48-oracles.json';v=load(oraclePath)
clarified={'M2A09':'Unsupported capability/container/invalid seek or unqualified fixture rejects before DataSource creation/open, actual provider/native open and parser/mux allocation; distinguish any factory identity registration/quota from physical opens, never falsely claim all source counters0','M2A35':'Within scope HostInput sources2/per-source1/queue0; copy/writer/readback native FD owners and peaks separately recorded with phase ordering and shared input/output ledger; no newfactory quota reset or treating FD count as identical to source slots'}
for x in v['cases']:
 if x['id'] in clarified:x['oracle']=clarified[x['id']]
save(oraclePath,v);cases=v['cases'];a=load(E/'authority-and-baseline.json');assert len(cases)==48 and all(x['status']=='PREPARED_NOT_RUN' and not x['actualNewCandidateRead'] and not x['actualDeviceRun'] for x in cases)
assert a['actualFixtureReadReturned']==8849 and a['actualFixtureReadRequested']==8850 and a['parserJvmGradleAdbDeviceCalls']==a['newCandidateQueriesOrReads']==a['bbbPayloadReads']==a['activeUnknownSessionQueries']==0
f=load(E/'stage-a-fixture-read-ledger.json');assert f['owner']['fileOpenCalls']==1 and f['owner']['actualEof'] and f['owner']['sameOriginalCloseReturned']
table='\n'.join('| '+x['id']+' '+x['area']+' | '+x['oracle']+' | PREPARED_NOT_RUN |' for x in cases)
report=R/'docs/tester/D1_MEDIA3_ANDROID02_CONTAINER_PHASE_A_REPORT_V1.0.md'
text=f'''# D1 Media3 Android02 Container 阶段A独立测试准备报告 V1.0

2026-10-21；tester；只读冻结基线与已资格fixture，阶段A。

## 结论

**PHASE_A_MEDIA3_CONTAINER_CHAIN_ORACLES_PREPARED**。M2A01–M2A48全链验收矩阵、原作用/来源/表示/PTS-EOS/预算与设备准入合同已完成，全部 **PREPARED_NOT_RUN**。没有读取、列目录或查询coder新Android02浮动候选；Gradle/缓存/SDK现场/ADB/设备、Media3/parser/JVM/encoder/decoder/生成0，未重跑D1QUAL03或历史主机套件。

本A只有限核准确fixture一次：**8849B/SHA25619e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c**与实际EOF、readonly/无reparse，原流关闭；read requested8850B含EOF1、returned8849B。这是独立外部身份读，不是再次容器资格化，BBB及其他媒体载荷读取0，不倒灌原D1QUAL03或未来Android账本。

此文件已经准确D1QUAL03取得有限HOST_CONTAINER资格，可作本批良性fixture准入事实；**实际Media3 capture→mux→Sink→fMP4重开仍NOT_RUN**。同UID实验不冒RCE/J11/P0；不签HOST_ISOLATED_FORMAT_V1/validated/产品READY COMMIT/播放。旧48945/17257 UNKNOWN不查询/attach/强停，D1未过M0未启。

## 依据、冻结身份及本A实际核验范围

依据 docs/milestones/D1_MEDIA3_ANDROID02_CONTAINER_TESTER_REQUIREMENTS_V1.0.md，原字节快照保全；本阶段并行只审旧冻Android01/Container02与D1QUAL03实际报告，完整新候选冻结后负责人另派B离线整包审，再另准确设备scope。既有用户持续平板授权保留，未来不要求重复人工授权，但本A无设备执行令、准确产物/case/tool/device绑定也未形成，因此不操作设备。

| 冻结依据 | 本A准确anchor |
| --- | --- |
| Android01 coder报告 | 660f33d468ad9f6b905795345edc8970aef641462efaa02fd39aa05759cc194e |
| Android01 seal | fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a，声明740项 |
| Android01独立B报告 | 845cd5920251c44beed2497d66d6843e5e6531e209d503cc93eb598f45fe2829，静态完成但本地UNKNOWN/功能缺口保留 |
| Container02 coder报告 | cfe817dd8d966f4cebdc8710a243d47b217f1ff16139f6099de91b29029efbc6 |
| Container02 seal | 0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d，声明676项 |
| Container02独立复审 | e857e11a919475562587ff300223472076e8c190388f838e61a8417fecd46649，MC-B01仅指定准入/原归还修复通过 |
| D1QUAL03实际报告 | a814ac8e2b2dc5c38189a1a582ee161646cefe1a4a1f43bae863a50aad9e0926 |
| D1QUAL03 manifest | 7408ad04c4534fbf8aa656898736e6a4fad3f5b8297e2eda4cfc1d2aeb827251，18证据全hash核不变 |

本A核旧报告/seal本身anchor、**26个选定冻结源码/计划/锁/SBOM**对相应seal逐项hash，及D1QUAL03完整18证据/实际收据和上述一次文件身份。未声称重新审完整旧740/676所有载荷或重验签/重跑1306旧自检，未读取活动suites-001、历史挂起owner或原BBB载荷。新candidate/newAPK/runner/method/class/签名/设备身份一律UNBOUND，不能拿旧Android01身份装作新包。

## 冻结基线告诉我们的门与差距

原Android01有真实1.9.3 HostDataSource/readAt→DefaultExtractorInput→Mp4Extractor/FragmentedMp4Extractor观察代码、固定asset/private owner、有限seek/replay与E13 finish；旧六帧registry=null，muxQualified在源/输出/mux分配前FIXTURE_BLOCKED。其MatureContainerRemux/MatureMuxerBinding正路与实际duration/真实平台FD均未在设备跑，静态方法体或主机有限绿不代它们。

Container02的MC-B01修复将原REOPEN/observer待归还留为检查前准入wait，不写首错/不消耗未开始检查资格，同Provider REOPEN仍1。真超时/取消/错误/UNKNOWN仍sticky；新Android02必须继承，不把同Provider暂待重开为新任务或先释放资源。原成功缓存路径亦需真实运行后才能签，旧顺序模拟不替真实fMP4成功链。

**FT-B02时限不能自动继承成Android已修证据**：冻结Android01 onStart是worker.join(60000)后看isAlive，job只有bodyReturned flag，没有同原单调最后完成时间；新批要防join超窗后恰逢线程结束造成晚成功。必须同原cleanup/最后受控信号完成点、等界为迟、先前UNKNOWN sticky与实际join分列。这里只定位旧基线/新验收要求，**没有读取新候选所以不登记新候选缺陷**。

原private FileOutputStream(false)虽在fresh独占根内，不能单凭该构造声明新要求的CREATE_NEW机制已经证明；新候选需明确固定路径/原分配/不覆盖条件和真实只读授予。源asset哈希与私有副本实际读回hash分列；计算同一读入buffer的hash不再算一次OS读，但真实私有再读/parse/seek/重开都必须记账。

## 实际fixture truth与Media3表示边界

D1QUAL03证明：实际单avc1视频、无音轨、256×144、identity/rotation0，6个AVCC sample各1340B，actual IDR NAL各1336B；PTS/DTS0..1000000步200000、原timebase5/durationUnits6=1200000us。真实source SHA/大小/来源report作为**fixture eligibility与跨框架reference**，不能复制这些值填实际Media3 Format/TrackOutput收据。

host CSD有三种记录：SPS payload7B（不含NAL header）、PPS payload3B、成熟规范化拼接AnnexB20B；它们不是“Media3 initializationData有三项”的观察。原raw encoder AU1360B含PS也不等文件AVCC1340B。Media3实际CSD数组数量/边界、原sample bytes/flags、是否规范化AnnexB要由真实1.9.3 API输出记录，并在候选冻结前声明有来源的对照规则，不能先抄3hash或keybool→rawflags1。

同Media3 capture→fMP4 reopen优先比较**同一已声明表示**的实际CSD数组、sample size/hash/PTS/key/encryption/EOS语义；若需要跨框架规范化，只能用既有成熟API/已声明structured metadata规则，禁止手写NAL parser或跑后补前缀/换mask/容差求PASS。wholefile hash前后因容器写法/metadata不同通常无相等要求；输出hash本身及顺序writer digest/extent对真实重开EOF另核。

真实seek1s必须使用实际SeekMap.first的byte/time、source epoch、extractor.seek和重放callback，不能将requested1s或JCodec原offset直接当Media3 seek结果。不支持/无SeekMap准确UNSUPPORTED，不改fixture/库参数硬达门。

## PTS、DTS、EOS与真实duration的能力边界

冻结HostMp4Inspection.Sample仅timeUs/flags/size/hash，TrackOutput.sampleMetadata只一个time参数；**没有独立DTS暴露**。host stts-derived DTS可作为reference，但Media3实际DTS保持null/UNPROVEN，不能以all-IDR、PTS单调或getMediaPts别名冒独立DTS。如果新验收必须该项而成熟API不可得，集中报能力缺口，不改门或临时塞JCodec进APK。

原E6Muxer真实配置fragmentDuration3000ms/sampleCopying，写6个非空payload后一个**空EOS flags4/time last+200000=1200000us**，关闭原muxer。空EOS不是第7帧、不是新的压缩payload；不得改变fragment时间或编码参数求通过。

EOS意图/最后PTS+步长/host1.2秒都不是输出文件实际duration。必须真实FragmentedMp4Extractor的SeekMap或TrackOutput reportedDuration等原成熟来源证明1200000，源API和单位分列；若TIME_UNSET/无callback/unsupported准确NOT_PROVEN。actualMedia3Dts、actualMedia3Duration、CSD及sample fields当前均null，等待真实运行，不能仅凭B源码/构建填绿。

## 全链阶段与原返回合同

1. **asset→private**：新空数据包与固定asset；原InputStream/目标FD holder先登记，明确CREATE_NEW/路径/runId；输入实际EOF/hash，原输出flush/sync与同原close返回，再授readonly。私有副本实际再次完整hash若与copy同buffer哈希不是一读，分别计账。
2. **Media3 capture**：固定已准入只读Provider/readAt→真实Mp4Extractor；wholeEOF/hash、sniff/peekreset/endTracks/实际6sample/Format/CSD与parserEOF。真实encoded capture有界不可变，原DataSource/extractor/provider/FD/caller/observer均归还后才允许mux。
3. **mux→Sink**：真实返回addTrack token，逐真实sample送原FragmentedMp4Muxer，六payload+空EOS；原mux.close、channel.producerClosed只是各自事实，不能代同原native writer flush/FD.sync/close。实际attempt/ack lower bound/extent/partial UNKNOWN分开，禁止生成器/其他mux backend。
4. **read-only reopen→fMP4**：原writer与原observer真实返回、readonly capability后同原REOPEN一次，待归还不提前标inspection开始；真实FragmentedMp4Extractor wholeEOF/hash/轨道/CSD/样本/时长与原释放，输出digest对source bytes并不等输入wholefilehash。
5. **runner finish**：同原caseworker最后完成点及实际join、source/output/native observer返回、E13 finalizer和平台super.finish原返回分别证。receipt创建时finalizerOwnerAtReceipt=1仅代表仍在，外部原采集需要自然返回与真实platform返回事实；拿不到就UNPROVEN，不凭counter0/Future.done/PID消失补齐。
6. **cleanup**：全部原返回正证后仅清新自有包/目录。UNKNOWN/过量/身份不符/首错停所有后继，保留原Job/FD/流/目录，不interrupt/kill/强卸载/第二close/退款/重试，不用迟返升级成功。

详细逐phase actor/证据/停点见pipeline-original-owner-evidence-contract.json。本A没有发起任何这些Android阶段。

## 全scope预算与取消：不能按phase换新factory清账

继承scope内HostInput source≤2/每源inflight1/queue0；copy/writer/readback native FD及线程峰值另记，不能把FD数与source槽当同一计数。输入**8MiB累计**贯穿copy/hash实际再读/sniff/parse/seek/重开/EOF；输出**16MiB attempt**含partial、未知保留、回写，块64KiB、sample≤262144、CSD64KiB、六AVC/原时序不扩。若一个device scope含多case/phase，不自动给每case或newfactory重置8MiB；任何拟单case独立scope分配须完整计划事前明确，不能静默乘N。

readAt caller请求、短读政策后的原native requested、reserved与actualReturned分列：short3不把每次SDK大buffer请求冒物理全长read，也不只以returned掩盖异常保留。所有真实重读累加，内存摘要同一bytes不算新磁盘读，外部APK/fixture保全hash和设备SDK账另类，不称physical disk IO。

取消只在良性有限控制门覆盖before-open/during-read/原write返回但ACK或observer未归还/REOPEN前后等，保留实际同一调用线程/资源、首错、迟返与最终join。不能用坏atom/资源攻击/强阻塞FD测“隔离”；取消资源归还可以合格，但不标媒体链成功。deadline60秒只关准入，等界迟、先前UNKNOWN不清、不因线程随后结束补绿。

旧Android01计划14操作/6case/receipt262144B/外层text4MiB等仅历史提案，**不能直接算新Android02还有14操作可用**。新完整候选必须列所有准确method/runId/runner/操作数，绑定两APK真实输入字节、framing、每case及allpending+final的stdout/stderr、proof/log/binary出站、总wall、停止与最终cleanup额度。当前这些数值/工具/设备绑定未提供即null，不新增临时诊断命令补证或复用旧scope余量。

## M2A01–M2A48独立验收矩阵

矩阵中的方法是能力/语义意图，不是已经核过的新入口；真实case名称、参数、DEX代码和产物须完整B绑定。全部设备/Media3运行状态保持NOT_RUN。

| 项目 | 独立oracle | 状态 |
| --- | --- | --- |
{table}

## 后续B与实机准入：完整包再集中交接

新包冻结后独立B需核：主/test APK source→实际Android javac/JAR→DEX方法与类集合/二进制manifest/version/签名/assets，固定1.9.3实际各配置编译/runtime消费与strict locks/metadata、许可证/修改与fixturequalification来源。原280个android构建类历史集合不是JVM替身的同义词，不能 blanket拒绝所有android名称；但Uri/ErrnoException/OsConstants JVM替身、checks、JCodec/审计fork必须不进新APK/产品。

stageA不评新candidate缺陷（**NOT_EVALUATED_FLOATING_CANDIDATE_NOT_READ**），也不运行新的离线自检/平台probe。旧BBB仍只保留原已授权提取角色，不改320×180+AAC参数或借其权属送入AVC6 mux，当前不再读其载荷。合成fixture已有限host资格，但Media3实际数据与最终duration/DTS能力仍独立待证。

精确future app/test/runner/process/version/cert/APKhash/case/runId/scope、设备serial/build/capturetool/freshidle及全操作预算均UNBOUND。用户已有平板持续授权无需重复索取，本A/B边界也不能据此自行查其他项目/设备占用、Gradle/缓存或执行新方法。旧UNKNOWN/原FAIL/关闭顺序/FFmpeg发布/许可/P0/J11/C13等门均不因本矩阵关闭。

完整A报告/48矩阵/fixturetruth/一次有限hash账/原source证据/wholebudget与设备合同冻结立即交负责人，然后停止；等待完整新Android候选核定另派B，不自动设备或升级有限HOST_CONTAINER到Media3、隔离/validated/READY COMMIT/播放。
'''
assert not report.exists();report.write_text(text,encoding='utf8')
files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='phase-a-evidence-manifest.json']
save(E/'phase-a-evidence-manifest.json',dict(frozenUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=report.relative_to(R).as_posix(),reportBytes=report.stat().st_size,reportSha256=sha(report),overall='PHASE_A_MEDIA3_CONTAINER_CHAIN_ORACLES_PREPARED',evidenceFiles=files,preparedOracles=48,allOracleStatuses='PREPARED_NOT_RUN',newCandidateRead=False,actualMediaParserJvmGradleDeviceCalls=0,finiteFixtureIdentityHashReadBytes=8849,oldSessionsTouched=False))
print(json.dumps(dict(report=str(report),reportBytes=report.stat().st_size,reportSha256=sha(report),evidenceFiles=len(files),manifestSha256=sha(E/'phase-a-evidence-manifest.json')),ensure_ascii=False))
