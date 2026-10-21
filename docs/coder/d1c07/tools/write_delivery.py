"""Write complete C07 reports from current audited identities; no device actions."""
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c07';e=base/'evidence';docs=root/'docs/coder'
apks=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks']
table='| 文件 | 字节 | SHA-256 |\n| --- | ---: | --- |\n'+'\n'.join('| '+Path(r['path']).name+' | '+str(r['bytes'])+' | '+r['sha256']+' |' for r in apks)
methods={n:re.findall(r'@Test public void (\w+)\(',p.read_text(encoding='utf-8')) for n,p in [(name,next((base/'device').rglob(name))) for name in ['C07DeviceTests.java','C07IsolatedDeviceTests.java']]}
assert len(methods['C07DeviceTests.java'])==20 and len(methods['C07IsolatedDeviceTests.java'])==9
delivery='''# D1-20261005-C07 整批开发交付

日期：2026-10-05；状态 BLOCKED / NOT_READY，C07全部设备项目NOT_RUN。仅本机研究、源格式修复、自检与必要离线构建，无ADB/设备操作、付费、发布、权重或新CPU二进制引入，不进入M0。C01–C06及原媒体保持冻结；本文是新C07交付，不更正原C06冻结身份。

## 范围与状态

| 要求 | 本批结果 | 准入限制 |
| --- | --- | --- |
| 至多两条单App/AAR CPU高风险路线 | D1_SINGLE_APP_ISOLATION_OPTIONS_V1.0.md 已提交两种：FFmpeg n8.0 CPU解码+系统编码，或FFmpeg n8.0+OpenH264 v2.6.0全CPU导出；精确许可/配置/AVIO/API、危险链、数据校验、Manifest/多宿主、TOCTOU/预算/死亡与最小实验退出条件齐全 | 路线未选定、未准入、未实现CPU管线。没有把FFmpeg全部称GPL或LGPL一律排除，动态链接/源码/EULA/商店与专利条件需具体审核 |
| TABLET-C06-02实际sniff | 本机已审核Media3 1.9.3 AAR字节码确认单Extractor在BundledExtractorsAdapter.init直接选用，未进入sniff分支；原C06缺失不再只有假设。C07 FormatGuardExtractor在首次read前显式调用同一个真实AVI/MP4 extractor.sniff；不依靠多加假extractor诱导框架调用 | 修复已编译及本机边界测试通过；真实Media3 sniff/fixture与采帧设备NOT_RUN，不能提前关闭缺陷 |
| 有界探测及失败门禁 | 实际peek/advance累计32KiB、合作式5秒预算，逐短读前后检查、中断/零进展拒绝；不消费输入，finally reset peek；错格式/截断/解析失败稳定外层code，失败记忆不能换输入重试绕过。每次capture独立starts/matches/rejects，全部实际匹配才准输出验证 | 预算不能强制中断任意native/CPU调用；Routing read仍5秒，已开始的单次I/O可能超过合作式deadline，实际操作完成才SourceReleased，未知保留quarantine |
| 控制和反例 | 新增3设备方法：真实AVI/MP4控制、两种错路由/空/截断/损坏头、匹配RIFF但截断body由真实parser拒绝；无Sink/token，finally实际source释放断言 | 29编译入口；当前计划28项，ordinary原方法保留但不再同条件执行 |
| 原门禁 | 24项源码/片段身份核对：正式双轨、T01/T02、真实sample/第二槽/跨owner及ordinary严格源码保持；原10秒/9–12秒、专用video-only输出/full decode/取消/FD与源门禁保持 | C06平板25PASS/1FAIL仅历史局部证据；不当C07运行，不以研究或companion声明产品隔离 |

研究官方来源见cpu-route-source-review.json；Media3单候选字节码与既有cache AAR/classes hash见bundled-extractors-adapter-javap.txt及approved-jar-provenance.json。未获取完整FFmpeg/OpenH264源码包hash、未构建或扫描新CPU组件；它们不在本APK/SBOM。

## 自检、构建与供应链

本批26条新JVM边界断言PASS，使用可控Extractor/Input测试替身验证真实守卫代码；它不是实际Media3容器sniff成功证据。141条历史断言原ID/hash复用，未重跑或改名冒充新增。C07正式与采帧规则身份见gate-preservation.json，证据来源见c06-evidence-reuse.json。

一次集中离线strict构建PASS（42秒）：App Debug、AndroidTest、worker Debug、unsigned Release、testDebugUnitTest。本机ARM64/API31独立JNI重编译/ELF及入包来源核对，runtime NOT_RUN。help配置探针确认connected/UTP名称被拒绝，无设备动作。

App346/worker95坐标未增加；复用既有供应链审查和47个advisory，不是新扫描或漏洞已修补。APK静态审计三份debug同签名，无INTERNET、命名样本/模型及FFmpeg/OpenH264库；release无C07实验类；worker仅既有实验模块。根App/config切C07是可变工作区，不影响旧候选。

'''+table+'''

## 冻结及交接

产物目录docs/coder/d1c07/artifacts/D1-20261005-C07；4 APK与源码ZIP、完整source/evidence身份见source-manifest.json、freeze-summary.json，git_commit=null。报告不内嵌自身或ZIP hash，避免循环；verify_freeze.py只读核验ZIP/current source/复制产物及全部证据。完整追加计划见D1_C07_DEVICE_APPENDIX_V1.0.md，负责人选择/派发后tester才操作设备。

ordinary历史UNKNOWN=FAIL继续，C07源码不改变严格断言、没有外部cause注入，不为同条件重跑派测。模型权利/标签质量、单App产品隔离、手机AVI/SRT与AC3、真实NAS/资源/最终P0仍未闭合。CPU路线选择和许可审核是下一实际实现的前提，本文不自动批准或宣布D1通过。
'''
(docs/'D1_DELIVERY_D1-20261005-C07.md').write_text(delivery,encoding='utf-8')
rows=[]
for cls,names in methods.items():
 for name in names:rows.append('| '+cls.replace('.java','')+'.'+name+' | '+('NOT_SCHEDULED；历史UNKNOWN=FAIL保留' if name=='ordinaryIsolatedCodecOutcomeDoesNotReady' else 'NOT_RUN')+' |')
appendix='''# C07 集中设备追加说明 V1.0

日期：2026-10-05；候选D1-20261005-C07；计划，未执行。29入口编译保留（20 host+9 isolated），当前集中计划28项；ordinary历史严格FAIL不改，不再同条件派测。仅负责人明确授权后由tester独占指定设备/候选；coder本轮不ADB/设备，不改冻结包，不进入M0。CPU方案尚未选定，本批设备计划只验证已有Media3格式守卫及受影响回归，不测试未实现CPU方案。

## 身份、资料与保留边界

按freeze-summary/source-manifest/ZIP逐一核验源码与全部证据/4 APK hash，三debug同签名；只安装负责人所选Debug/Test/实验worker，unsigned Release只审计。先审目标旧包/签名/UID/私有副本/账本/成功输出和cache，保留C02–C06数据与备份，无自动卸载/清数据/恢复/删capture。C06两条capture已用满，其记录保留；C07只允许新前缀最多两条、每份2MiB输出上限，旧数据与总空间/预算须负责人审查，不按新前缀自动豁免存量。

fixtures仅basic.mp4、subtitle.avi、subtitle.srt、large.mkv，可信身份复用media-inventory及冻结原hash。新files/d1_c07_fixtures的复制/alias须长度/hash一致，不能以扩展名验证格式。私有cp复用不算Windows二进制传输工具通过，手机另行安排。新反例由测试内受控byte[]或只读provider映射生成，不改原媒体、不写共享目录、不上传。

'''+table+'''

## 顺序、真实断言与失败处理

1. sourceFormatValidControls：真实AVI/MP4各一次extractor.sniff、starts=matches=1/rejects=0，peek/read origin=0且重置；实际source归零。无Transformer/Sink/token。
2. sourceFormatWrongRouteAndInvalidHeaders：AVI路由给真实MP4、MP4路由给真实AVI，以及两种kind各空/4字节截断/64字节坏头。调用guard.read而非框架选型，必须在parser进入前得到SOURCE_FORMAT_*，attempts=1/matches=0，失败后第二read不得重新sniff绕过，源字节位置/peek reset和实际释放成立。
3. sourceFormatMatchedHeaderTruncatedBody：12字节RIFF/AVI头实际sniff匹配，但缺失body；真实AVI parser在最多8次read内因EOF/ParserException拒绝，不以sniff匹配宣称全容器有效，最终源释放，无Sink/token。
4. videoFrameCaptureMp4Control：通过相同MediaEngine显式guard，真实starts=matches>0/rejects=0的SOURCE_FORMAT_CAPTURE_GATE必须出现并断言；原2秒映射1–4秒片段内1秒，专用1视频0音频/full decode/fsync/非空帧/释放。
5. offlinePlatformFaceFeasibility：直接MP4控制，原AVI10秒retriever不足才用9–12秒片段内1秒回退；同guard实际匹配证据、专用验证/bitmap/取消和source/FD释放。MP4采帧控制失败则此依赖项BLOCKED；不得换0秒/空帧/仅MP4。actual source PTS UNKNOWN，候选数不是质量PASS。
6. 宿主realEncoderOutput与companion isolatedActualEncodeAndReadyRecovery正常前置后完整T01/T02和既有真实sample/跨owner/第二槽/租约回归；broker SIGSEGV/HANG各自独立NORMAL前置。播放MP4、AVI无SRT/有SRT、MKV/ASS受影响结构/Seek/释放也执行，自动静音不能判声音/字幕字形同步。

三个新format方法可独立执行；前置FAIL只阻断依赖项，不遮蔽其他安全恢复测试。格式反例只覆盖指定错误，不是全面恶意媒体fuzz。正式导出必须继续H264/AAC双轨各非零样本/3秒±150ms/严格PTS/full视频decode，video-only仅采帧、不发产品READY/token。

预算：sniff总32KiB/合作式5秒，每Routing read最多5秒，逐短读检查；不能因此声称native无条件可中断。format方法实际finally await source10秒、无输出FD；采帧done90秒、retriever20秒、主线程取消5秒、源释放10秒，默认无sample watchdog仍10秒。外部测试超时只收集当前task/PID/UID/阶段，不能代替实际source/FD/death/lease；未知quarantine，不主动清文件。日志须当前候选/源身份/设备/时间，不能复用C06运行PASS或旧PID8974作本轮事实。

## 入口清单

| 编译方法 | 本批状态 |
| --- | --- |
'''+ '\n'.join(rows)+'''

结束统一报告28计划项实际PASS/FAIL/BLOCKED/NOT_RUN，单列未派测ordinary历史FAIL和“当前未执行”；不能以29个编译方法作29个设备通过。保留所有旧任务/素材及新成功/失败capture账本；无自动手机切换、Gradle设备任务或CPU二进制集成。SOURCE_FORMAT_*匹配门禁成功也只关闭本候选/设备覆盖，CPU产品路线和全部P0仍待独立准入。
'''
(docs/'D1_C07_DEVICE_APPENDIX_V1.0.md').write_text(appendix,encoding='utf-8')
print('C07 delivery and appendix generated:29 compiled,28 scheduled,device NOT_RUN')
