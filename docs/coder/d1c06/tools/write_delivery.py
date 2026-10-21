"""Generate C06 reports from audited immutable-copy identities; no device actions."""
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c06';e=base/'evidence';docs=root/'docs/coder'
rows=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks']
table='| 冻结文件 | 字节 | SHA-256 |\n| --- | ---: | --- |\n'+'\n'.join('| '+Path(r['path']).name+' | '+str(r['bytes'])+' | '+r['sha256']+' |' for r in rows)
methods={n:re.findall(r'@Test public void (\w+)\(', (base/'device/com/videokit/spike/c06'/n).read_text(encoding='utf-8')) for n in ['C06DeviceTests.java','C06IsolatedDeviceTests.java']}
delivery="""# D1-20261005-C06 开发交付

日期：2026-10-05；状态：BLOCKED / NOT_READY。C06所有Android设备项目NOT_RUN。本轮仅本机分析、修复、自检、构建与冻结，没有ADB/设备操作、安装、媒体改写或M0发布。依据D1_C06_CODER_REQUIREMENTS_V1.0.md，完整读取C05报告、两项方法日志、对应协议日志及PID5588/UID99012原始tombstone。事实复核与来源hash见prior-failure-analysis.json。

## 两项缺陷与状态

| 需求 | 事实、方案与代码 | 当前状态 |
| --- | --- | --- |
| TABLET-C05-01 ordinary App trace缺失 | C05CREATE_BEGIN后匹配reason5/signal6、cause UNKNOWN/trace SHA空；外部PID5588/UID99012 tombstone显示codec2枚举中native abort。C06新增traceStatus区分App trace缺失、读取/解析失败、身份/信号不匹配与已匹配proto，不改TombstoneWitness allowlist、不把外部死因注入App。AOSP公开管理实现过滤非普通App UID及SELinux标签，提供机制解释；未确认本平板vendor实现 | 平台可观测性/自动原因分类仍BLOCKED；C06可能继续UNKNOWN/FAIL。不是新增日志即修复。C05实际death/source_released/lease_clear已有证明，C06完整复验保留 |
| TABLET-C05-02 AVI9～12秒无sample | 旧日志在0偏移大量1字节读，取消栈为Mp3Extractor探测读取，没有muxer建轨；支持格式探测/小异步读开销假设，不能凭WAV或取消定完整根因。C06采帧专用typed AVI/MP4 Extractor仍sniff实际源，阻止将AVI换成MP4控制；补seek/轨道格式/输入sample、实际video decoder创建、muxer/video sample/fsync阶段。仅采帧setRemoveAudio(true)，专用VideoFrameSink与VideoCaptureOutputValidator验1视频0音频、H264256×144、3秒时长、严格PTS、全视频decode/EOS/帧数，独立于正式双轨导出。watchdog仍默认10秒，不延长 | 方案已实现/编译，AVI修复效果设备NOT_RUN，未关闭。原AVI10秒请求映射9～12秒片段内1秒OPTION_CLOSEST保持；实际source frame PTS UNKNOWN、转码可有损、检测质量NOT_RUN |

ordinary具体外部abort只证明该匹配进程codec2服务发现失败事实，不证明全局服务停机、权限拒绝或产品隔离。App仍按证据返回UNKNOWN，原严格分类断言不改判通过。负探针退出准则建议、停止重复失败的评审条件与AVI方案决策点见D1_C06_DIAGNOSIS_AND_EXIT_REVIEW_V1.0.md，均待负责人决定；C06未自动实施退出或降低P0。

视频采帧不需要音频是显式独立契约，不是对正式编辑导出丢音轨放宽。专用sink不实现SinkCoordinator.Host，不产出产品READY/token；正式AuthorizedSink、AndroidOutputValidator、OutputValidationRules及companion完整双轨门禁保持原源。新片段只是host Debug采帧实验，不是已隔离的最终检测/遮罩流水线。

## 自检、构建与供应链

C06新增22条本机反例PASS，覆盖独立采帧轨集合、正式双轨不退化、视频编码/尺寸/时长/样本/PTS、typed路由、原10秒映射及unknown死亡不通过。继承119条本机证据（C05新增23+原96）未重跑，来源hash及15项源/门禁身份见c05-evidence-reuse.json。正式正常导出/T01/T02、普通SIGSEGV/HANG、真实sample取消/死亡/第二槽/跨owner及ordinary严格分类和最终释放测试除命名空间外一致；gate-preservation.json仅静态核对。

一次集中离线strict构建PASS：App Debug、AndroidTest、worker Debug、unsigned Release、testDebugUnitTest，见c06-final-build.log。单元测试任务完成不代表设备覆盖。help配置探针预期拒绝connected/UTP路径，无设备动作。自有JNI仅ARM64/API31本机重编译与ELF/符号核对，C06运行NOT_RUN。

App346/worker95个锁定坐标无新增；沿用审查过的Media3 1.9.3 extractor/decoder/transformer/muxer。既有OSV、47个advisory、16个匹配组件工具限制及NOTICE条件原样复用，不是新扫描或已修补。无新增依赖/GPL/FFmpeg/权重；闭源替代准入仍未批准。包审计确认三份debug同签名，无INTERNET、命名样本/模型条目，release无C06实验类；host采帧业务不进入worker APK。

"""+table+"""

冻结目录docs/coder/d1c06/artifacts/D1-20261005-C06；源码ZIP及完整source/产物/证据hash以source-manifest.json和freeze-summary.json为准，git_commit=null。报告不内嵌自身或ZIP hash避免循环身份；verify_freeze.py只读核验所有复制件、ZIP和当前源。

C01-C05候选冻结源、产物、证据和报告及45个源媒体保持原hash，根App/Gradle切到C06属于可变工作区。26入口集中补测见D1_C06_DEVICE_APPENDIX_V1.0.md。手机AVI/SRT、音频及Windows真实复制、单App/独立Kit隔离、模型权利、标注质量和完整P0仍未通过，不据C05的23限定PASS或本轮编译进入M0。
"""
appendix="""# D1 C06 集中设备追加说明 V1.0

candidateId：D1-20261005-C06；17+9=26入口准备完成，C06全部NOT_RUN。负责人选定整包后tester执行；本轮coder无ADB/设备操作。保留C04/C05包、fixture、账本/lease/owner、成功输出、失败采帧账本与电脑恢复备份；先核对设备/API/ABI/serial、实际安装APK hash、三包签名、现有数据用途与空间，未知数据不覆盖。禁止Gradle connected/UTP/managed路径。ARM64/API31+；unsigned release不安装，额外不同UID companion仅D1实验。

"""+table+"""

仅取冻结复制件，不取可变build输出。实际签名、manifest、ABI见apk-audit.json和各signing日志。更新/回退/清理按负责人授权和保留要求执行，不自动卸载或清数据。

## Fixture

C06读取files/d1_c06_fixtures的basic.mp4、subtitle.avi、subtitle.srt、large.mkv；精确源/hash见transfer_fixtures.py/FIXTURES与media-inventory.json。SRT1445 cues、GB18030兼容GBK，仅有界转UTF8不改源。可由tester在审查后重新验证已有C05副本，再复制到全新C06私有目录并核验长度/hash，不改C05目录；私有cp不证明Windows跨机传输工具通过。

若测Windows工具，默认PLAN_ONLY；实际需--execute、显式serial、--device-and-installed-c06-reviewed、--overwrite-c06-fixtures-reviewed、docs/tester内--result-file及固定aliases；空间至少请求总量+最大文件+256MiB，未知目录或身份不符即停止。32KiB shell-v2 raw流先.c06-part再校验提交，不用exec-in/tee，不管理ADB server/安装/卸载/清理。>2GiB电脑协议证据复用，不代替实际设备复制。

## 依赖、覆盖与判定

1. 正常宿主realEncoderOutput与companion isolatedActualEncodeAndReadyRecovery先PASS，再跑全部T01/T02和真实sample恢复。正式导出仍H264256×144/AAC，双轨各自非零样本、3秒±150ms、严格PTS、完整视频decode/EOS/帧数/末PTS。T02 write/flush指定stage/hits=1/精确cause，flush已有编码字节；validate编码/fsync后非零字节与OUTPUT_VALIDATION_FAILED。普通codec/source先失败不算注入命中。READY丢响应仍同task/token收敛，abort保留READY。
2. 普通NORMAL/PRESSURE/EXIT与独立SIGSEGV/HANG完整复验。指定模式同步ENTERED+ARMED/WAIT_BEGIN、hits=1；SIGSEGV必须没有正常RPC结果、实际Binder death及PID/isolated UID/启动时间匹配OS signal11，cleanup SIGKILL或单条mode不够。HANG精确WORKER_TIMEOUT、有界等待、实际死亡和Source计数排空。两个独立方法均执行，不能互相遮蔽。普通broker源账本不等于真实输出Writer lease。
3. ordinaryIsolatedCodecOutcomeDoesNotReady保持严格App分类与finally释放断言。记录task/epoch/UID/PID、LEASE_ACQUIRED/CREATE_BEGIN及traceStatus：APP_TRACE_ABSENT、READ_OR_PARSE_FAILED、IDENTITY_OR_SIGNAL_MISMATCH、MATCHED_PROTO等。App原因未知仍FAIL，不用SIGABRT或外部文字强造App通过；available/release未知/bind/ACK失败同样不算预期原因。即使分类失败，实际death/source_released/lease_clear/无token分别记录并复验。未知FD/lease quarantine，不删材料。
4. 另由tester有界保存对应本轮C06 PID/UID/时间/进程/阶段的原始native crash，分类为“外部死因事实”独立栏目。不能引入旧PID5588/C05 tombstone作为C06证据；不能把宿主UID-only日志当isolated栈。不把Hardware service manager错误文字推断为全局停机/权限拒绝。App trace可缺失，既定分类FAIL保留，负责人另审退出准则，不扩大allowlist或静默改判。
5. 新videoFrameCaptureMp4Control先跑：同一视频采帧管线对MP4原2秒请求（1～4秒片段内1秒），独立validator确认1视频0音频、H264256×144、3秒、有效样本/严格PTS、全视频decode/EOS/帧数/fsync和非空取帧。只有该控制PASS，再评估offlinePlatformFaceFeasibility的AVI回退；控制失败，依赖项另列BLOCKED，不把MP4结果当AVI成功。
6. face方法仍先直接MP4 2秒控制，再原AVI10秒scaled/unscaled。只有稳定FRAME_AT_REQUESTED_TIME_UNAVAILABLE触发原AVI视频-only回退，typed AviExtractor仍需实际sniff匹配，不fallback成原MP4。原AVI9～12秒转换片段内1秒OPTION_CLOSEST；源/clip请求映射留证，actual_source_frame_pts=UNKNOWN、quality=NOT_RUN。视频-only是采帧专用契约，不要求音频，也不能拿它满足正式双轨输出。decoder、轨道、muxer和sample实际阶段均保存，无有效片段/非空帧不得检测通过。
7. 保持默认10秒无sample watchdog，不延长掩盖无进展。按sniff/init/seek、track/endTracks/input sample、video decoder begin/created、muxer track/output sample/fsync/完整validate定位；SOURCE_READ_FAILED CANCELLED是取消现象，不直接作根因。90秒外层、5秒main等待、20秒retriever、10秒Source排空保持；单次native不可硬停如实保留quarantine。Transformer cancel返回不表示全部graphics资源释放。
8. C06保留d1_c06_capture_*.capture和对应片段，最多两条预算；MP4控制和AVI各占一条，不自动清理或反复重跑。达到预算FRAME_CLIP_CACHE_BUDGET_REVIEW_REQUIRED交负责人审查。output_descriptors_closed与source_released分别记录；不把capture_validated叫产品READY/token。AVI或控制失败材料保留，不修改旧C05 frame账本。
9. 真实companion sample后cancel/EXIT/SIGSEGV、第二槽存活、实际helper宿主死亡/跨owner恢复、native dup-close全部复验：真实sample后故障、确定死亡/Writer lease清除后才删未READY、第二输出完整验证/READY、同task/token恢复，未知lease保留。手机播放/声音和人工完整字幕/同步/旋转等未证据仍NOT_RUN，平板播放不移作手机通过。

## 26入口
"""
for name,items in methods.items():appendix+='\n### '+name+'\n\n| 方法 | C06执行 |\n| --- | --- |\n'+'\n'.join('| '+x+' | NOT_RUN |' for x in items)+'\n'
appendix+='\n逐项记录候选hash、serial/API、fixture hash、时间、实际stage/hits/cause、source/FD/lease最终状态和PASS/FAIL/BLOCKED/NOT_RUN，写docs/tester自身证据目录。原25入口全部保留并增加采帧MP4控制；依赖失败单列BLOCKED，其余独立方法继续。整批统一报告，不据部分PASS进入M0。退出准则提案尚待负责人评审，当前App内UNKNOWN仍FAIL。\n'
for name,text in [('D1_DELIVERY_D1-20261005-C06.md',delivery),('D1_C06_DEVICE_APPENDIX_V1.0.md',appendix)]: (docs/name).write_text(text,encoding='utf-8')
print('two C06 documents', {n:len(v) for n,v in methods.items()})
