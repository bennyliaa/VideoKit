"""E12 documentation assembly only: reads pinned local sources, writes new audit files.
Never imports project code or starts devices, builds, media, or candidate checks.
"""
from pathlib import Path
import hashlib, json, re, zipfile
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/coder/d1e12'
def read(p): return (ROOT/p).read_text(encoding='utf-8-sig')
def digest(b): return hashlib.sha256(b).hexdigest()
def pin(p):
    b=(ROOT/p).read_bytes()
    return {'path':p,'bytes':len(b),'sha256':digest(b)}
def save(p,s):
    target=ROOT/p; target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(s,encoding='utf-8',newline='\n')
def js(p,v): save(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def link(p,line=None): return f'[{p}]({ROOT.as_posix()}/{p}'+(f':{line}' if line else '')+')'
U='docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md'
R='docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION_REPORT_V1.0.md'
assert pin(R)['sha256']=='60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635'
S='docs/coder/d1e11/'
sources={
 'U':U,'D':'docs/PROJECT_DECISIONS_AND_EXECUTION_V1.0.md',
 'D1':'docs/milestones/D1_CODER_REQUIREMENTS_V1.0.md',
 'G':'docs/coder/D1_R1_REQUIREMENT_GATE_MATRIX_V1.0.md',
 'J':'docs/coder/D1_R2_NATIVE_FAILURE_GATE_PLAN_V1.0.md',
 'C14':'docs/coder/D1_C14_REMAINING_GATE_REVIEW_V1.0.md',
 'C13':'docs/tester/D1_C13_TEST_REPORT_V1.0.md',
 'C14ENV':'docs/tester/D1_C14_ENVIRONMENT_STATUS_V1.0.md',
 'OBS':'docs/tester/D1_E6B_NORMAL_DEVICE_TEST_REPORT_V1.0.md',
 'E11':R,'STATIC':'docs/tester/D1_E11_ARCHITECTURE_REVIEW_REPORT_V1.0.md','A11':'docs/coder/D1_E11_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md',
 'E4G':'docs/coder/D1_E4_REMAINING_GATE_REVIEW_V1.0.md',
 'OSS':'docs/OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE_V1.0.md',
 'LIC':'docs/OPEN_SOURCE_AND_LICENSE_PLAN_V1.0.md',
 'FM':'docs/coder/D1_C14_FRAMEWORK_MAPPING_V1.0.md',
 'SET':S+'settings.gradle.kts','BUILD':S+'app/build.gradle.kts',
 'MAN':S+'app/src/debug/AndroidManifest.xml',
 'SERVICE':S+'android/com/videokit/spike/e4/E4CodecService.java',
 'SESSION':S+'android/com/videokit/spike/e4/E4Session.java',
 'CPU':S+'upstream-c14/android/com/videokit/spike/c14/CpuTaskClient.java',
 'TEST':S+'app/src/androidTest/java/com/videokit/spike/e4/E4DeviceTests.java',
 'LIFE':S+'android/com/videokit/spike/e4/E11ActivationLifetime.java',
 'RUNNER':S+'app/src/androidTest/java/com/videokit/spike/e4/E11ActivationInstrumentation.java',
 'SELECT':S+'src/com/videokit/spike/e4/E11Selection.java',
 'OBSERVE':S+'android/com/videokit/spike/e4/E9CurrentObservation.java',
 'ONCE':S+'revision-r1/tools/E11DeploymentOnce.java',
 'HOST':S+'revision-r1/tools/E9HostActivationSession.java',
 'SEAL0':S+'evidence/e11-freeze.json','SEAL1':S+'revision-r1/evidence/e11-final-freeze.json',
}
# Some R1 source roots intentionally retain their Java package directory.
for k in ['ONCE','HOST','RUNNER','OBSERVE','SELECT']:
    if not (ROOT/sources[k]).exists():
        base=ROOT/(S+'revision-r1' if k in ['ONCE','HOST'] else S)
        found=[p for p in base.rglob(Path(sources[k]).name) if 'build' not in p.parts and 'reference' not in p.parts]
        assert len(found)==1,(k,found)
        sources[k]=found[0].relative_to(ROOT).as_posix()
for k,p in sources.items(): assert (ROOT/p).is_file(),(k,p)
pins=[dict(id=k,**pin(p)) for k,p in sources.items()]
for row in pins:
    p=row['path']; save('docs/coder/d1e12/reference/'+p,read(p)) if False else None
    target=OUT/'reference'/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/p).read_bytes())
js('docs/coder/d1e12/input-pins.json',{'schema':1,'scope':'local read-only documentary audit; no online verification','inputs':pins})
index=['# E12 原始输入索引\n\n引用ID指向实际原文件；精确字节与SHA见 input-pins.json，原字节副本在reference中。冻结时点记录不被当作当前设备证明。\n']
for row in pins:index.append(f"- **{row['id']}** {link(row['path'])}；{row['bytes']}B；SHA256 `{row['sha256']}`")
save('docs/coder/d1e12/SOURCE_INDEX_V1.0.md','\n'.join(index)+'\n')

# Every individual bullet/numbered requirement in §§26–31 gets an explicit row.
section={
'26.1':('TEST/CPU/SESSION；E11四方法仅覆盖局部正常/取消/能力拒绝','缺正式API版本/快照/HostAction/Fake同契约与稳定错误组合；按原条目逐项验收','D1界定输入/释放语义；M0公共契约'),
'26.2':('CPU.readAt与TEST.positive；E11“MP4与AVI的严格normal门”仅六次取帧及输出验证','缺持续播放/音轨字幕/全部Seek/大视频NAS/断线矩阵；六帧输出不等播放','D1后端差异可行性；M1播放'),
'26.3':('C14/J09：旧平台Bitmap/FaceDetector对照；当前E11未含图片产品','缺本条真实图片格式、交互和生命周期证据','D1选型和危险解析路线；M2图片'),
'26.4':('SESSION许可/CPU2、codec独立owner；E11资源归还仅四方法','缺1/4/9/12混排、唯一音频、热/内存及故障他槽完整矩阵','D1预算与两任务边界；M3多实例'),
'26.5':('SERVICE/SESSION只写临时Sink；E11仅6帧video-only READY及0B取消','缺本条真实编辑或故障组合；无时间线/拼接/遮罩产品，未证资源继续OPEN','D1输入/Sink关键边界；M4/M6完整编辑导出'),
'26.6':('C14及G.P08：候选/设计与历史对照，E11无跟踪执行','缺权重和样本权利、标注、纠正/LOST/漏码/实际隐私及质量证据','D1合法路线与最小可行性；M5/M6完整质量'),
'26.7':('CPU/SERVICE显式broker身份与Sink、SET仅app；E11无Browser正式适配','缺本条宿主集成与产品级租约聚合；独立artifact/Fake/可移除回退未实现','D1接口不阻断可行性；M0/M7真实契约/集成'),
'26.8':('E11仅HA1Q6WXR/TB138FC/API31/ARM64；C14ENV手机阻断为历史','缺本条其他版本/设备/窗口/语言字体的实际证据','D1最低设备差异；M1/M3/M6/M8矩阵'),
'27':('E11仅指定源/临时Sink/有限资源四方法；SERVICE/SESSION/J记录边界','本条发布门未完成整产品证据，OPEN；不能由有限正常路径或文档替代','D1机制先处置；正式发布前全部硬门'),
'29':('D§3已有方向；C14“原文§29十二项”逐条设计与缺证仍有效','方向或内部命名不等最终接口/阈值/发行冻结；须负责人记录具体决定','D1解决有关可行性；M0设计冻结/相应阶段实证'),
'30':('D及既有十份V1.0设计文档/G差距分析；E11仅局部实现','设计说明存在不等产品可运行；本条跨宿主/源/业务/输出隔离仍需实证','D1报告可供决定；M0契约与M7集成'),
'31':('E11有限流水线；G.P01–P11分别追踪最终标准','本条最终成功未由当前候选证明，OPEN；保留为最终验收目标','D1给可行路线；M0–M8实现并整体验收'),
}
lines=read(U).splitlines(); rows=[]; current=''; n={}
for ln,text in enumerate(lines,1):
    m=re.match(r'#{2,3} (\d+(?:\.\d+)?)(?:\.)?\s',text)
    if m: current=m.group(1)
    if current.split('.')[0] not in {'26','27','28','29','30','31'}:continue
    if text.startswith('- ') or (current in {'29','31'} and re.match(r'\d+\. ',text)):
        n[current]=n.get(current,0)+1
        impl,gap,stage=section[current]
        rows.append({'id':f'U{current}-{n[current]:02d}','line':ln,'text':text.removeprefix('- '),'implementation':impl,'gap':gap,'stage':stage})
details29=[
 ('D§3内部com.videokit/App命名已定；BUILD仍Debug v15','正式artifact/SemVer/兼容迁移未冻结；M0/M7'),
 ('D§3 api/core/playback等分包计划；SET仅app','实际播放/编辑依赖分离与发布产物未有；M0/M7'),
 ('BUILD只接Media3 muxer；FM/STATIC保留1.9.3与受限FFmpeg8.0.3','ExoPlayer/Transformer/图片与产品发行许可未闭合，不复刻媒体框架；D1/M1/M2/M6'),
 ('C14/G跟踪候选固定但非已准入权重','模型/训练/样本再分发权利、真实标注/最低设备未证；D1阻断及M5'),
 ('E11实测无音频6帧AVC/fMP4；旧host双轨为历史','不能代替首轮MP4/H264/AAC/SDR正式预设；M6参数/音频矩阵'),
 ('E11六帧是重编码，无无损拼接路径','remux需参数/关键帧/PTS/旋转/音轨兼容与fallback；D1设计/M4/M6'),
 ('E11有限64MiB/8192reads/6帧/2MiB门与耗时记录','非正式导出速度/质量/全进程RSS/热阈值；D1测法与M3/M5/M6审定'),
 ('D§3无UI原生Kit+可选View/Compose+Flutter已定','E11无Surface/Flutter生命周期实证；D1边界、M0接口/M1/M8'),
 ('SESSION本地临时Sink+有界顺序mux channel；E11写后关闭验证','不证明任意FD/非seekable宿主Sink能力；D1须决定必要能力与失败语义，M0/M6'),
 ('现有journal/epoch/终局迁移是实验任务记录','不是工程schema/undo/revision/跨进程恢复产品契约；M0/M4/M6'),
 ('U§20/D设计有方向，E11无正式控件/overlay接口','主题/宿主叠加/坐标/无障碍未定可用API；M0/M1/M2/M5/M8'),
 ('CPU进程内2槽/SESSION encoder1及账本，E11正常资源返回','不是宿主全局1–12公平/音频/硬解预算算法；D1权威与M0/M3'),
]
details27=[
 ('CPU只读授权输入；E11四方法的原样本与历史产物身份保持','未证全部编辑/取消/断线/进程终止产品组合；源不变仍发布硬门'),
 ('SESSION临时Sink/隔离验证/结算；两normal READY','宿主业务COMMIT没有由Kit替代；全Sink能力/宿主拒绝组合仍缺'),
 ('CPU broker只收opaque token/字节，SERVICE只接任务/FD','正式公共API/多宿主resolver未建立；不能据Debug不传凭据关闭全API门'),
 ('codec迁出host，压缩解析isolated；C13限定故障他槽历史','本候选故障/UNKNOWN/宿主lease JNI以及显示声音图片链未闭合'),
 ('CPU2/encoder1限制，E11无音频','唯一发声与资源不足反复创建/1–12降级无产品证据'),
 ('C14/G跟踪尚无完整合法质量链','LOST不能宣称完整保护；不得用手动回退删自动P0'),
 ('E11能力/取消两项0B ABORTED，无假READY','永久UNKNOWN、全部IO失败/损坏输出与工程编辑链未证'),
 ('E11四方法有界正常归还；SESSION保留未证资源','无长期/真实OOM/Surface/永久挂住取消完成保证；UNKNOWN不归零'),
 ('FM/STATIC仅受限Debug精确版本与7库/35依赖','闭源正式分发许可/模型权利未准入，不是本批新法律审查'),
 ('BUILD debug sourceSet含故障入口；非正式Release交付','最终Release移除压力/永久日志/凭据需独立发行审计，不能将Debug可交实验当可发行'),
 ('SET仅app，BUILD application','无独立AAR/无源码宿主构建/替换证明，M0/M7硬门'),
]
details31=[
 ('CPU/SERVICE无Browser数据库参数','正式API/Browser adapter仍未证；M0/M7'),
 ('E11仅MP4/AVI取帧，无持续播放/NAS','随机读取大视频与NAS正式稳定播放待M1'),
 ('当前候选没有统一图片产品会话','统一图片/视频会话及控件隐藏待M0/M2'),
 ('现有task/epoch/CPU2是实验机制','正式单媒体/多画面同架构和实例独立待M0/M3'),
 ('G/公共契约设计有MediaPlayHobby作用域要求','产品偏好往返全字段/作用域隔离待M0/M1/M7'),
 ('E11不实现HostAction/导航UI','通用宿主动作与邻近媒体同步待M0/M2/M7'),
 ('六帧新输出有限通过，无编辑器/跟踪产品','重排/拼接/手动及自动目标跟踪完整新视频待M4/M5/M6'),
 ('正常/指定取消源保持，UNKNOWN不伪称释放','全部失败/终止/断线源不变产品链待M6/M7'),
 ('SET/BUILD是Debug app，不是独立版本化AAR','独立构建/契约测试/替换待M0/M7'),
 ('E11候选无真实Browser缺失模块回退集成','宿主启动浏览和临时播放器回退待M0/M7'),
]
for key,details in [('29',details29),('27',details27),('31',details31)]:
    targets=[r for r in rows if r['id'].startswith('U'+key+'-')]
    assert len(targets)==len(details),(key,len(targets))
    for r,(impl,gap) in zip(targets,details):r['implementation']=impl;r['gap']=gap
assert all(any(r['id'].startswith('U'+s+'-') for r in rows) for s in section)
js('docs/coder/d1e12/requirement-rows.json',rows)
matrix=['# D1 E12 需求—实现—证据矩阵 V1.0\n',
'日期：2026-10-18。READ_ONLY_AUDIT。D1 **NOT_PASSED**；M0 **NOT_STARTED**。所有“OPEN”表示当前证据不足或未完成，不捏造新测试FAIL。原始需求为U，当前源码为E11 final R1；源码存在只证明实现位置。证据引用ID与原字节pins见 '+link('docs/coder/d1e12/SOURCE_INDEX_V1.0.md')+'。本批未联网核新版本/法律结论，沿用冻结项目记录，不作新的发行许可判定。\n',
'## 1. 已接受的有限增量与历史基线\n',
'E11报告“唯一部署”“四项实际结果”“最终账本”“限定关闭范围”接受一次14→15保数据部署、四个独立host的实时观察、MP4/AVI各6帧READY、能力源opens/bytes/reads=0、条件取消及全部原资源和五个PC会话自然归还。批次a129ad0a-9d93-49c6-8289-9087afd419ff，平板HA1Q6WXR/API31；非声音、字幕、长期或UNKNOWN实测。\n',
'最新接受账本214483B、7R/7S、reserved0，完整2271B SHA e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649；旧107218B/1011B前缀保持。这里只转述报告时点，不是本批在线重读。旧oldCloseACK=false、未知出生/信号均保持。\n',
'E6B-OBS-F01/P1（OBS，2026-10-17）原AVI Before失败保留；E11通过catalog来源与每新host实际观察解决该历史问题在本批独立host连续执行中的阻断，记 **CLOSED_LIMITED_E11_CROSS_HOST**。长期运行、系统重启、旧历史退出记录再缺失/新UNKNOWN均OPEN，不将旧报告FAIL改PASS。\n',
'C13报告（2026-10-16）self系统signal0严格FAIL、外部raw11与独立双槽系统11分别保留；C14ENV（2026-10-16 12:40）两项NOT_RUN_UNCHANGED_PLATFORM_LIMIT，不存在本批C14新signal PASS。E11正常退出不能覆盖这条历史失败或证明native死因可观测。\n',
'## 2. 原文§26–31逐条矩阵\n',
'每条原文均保留行号。第28节里程碑另见下表；第30节十个设计交付名称另列。以下OPEN均只限制其自己的最终要求，不表示把全部后续M阶段实现强塞D1。\n',
'| ID / 原文定位与逐条要求 | 当前实现和实际证据范围 | 缺证及能否关闭 | 阶段/出口 |\n|---|---|---|---|']
for r in rows:
    matrix.append(f"| {r['id']} / U:{r['line']} {r['text'].replace('|','/')} | {r['implementation']} | OPEN：{r['gap']} | {r['stage']} |")
matrix+=['\n### §28里程碑与§30设计交付\n',
'| 原文范围 | 当前裁定 |\n|---|---|',
'| §28 VK-M0 | API/Fake/TestKit/示例宿主仍未正式实现/冻结；D1未过，不启动 |',
'| §28 VK-M1–M3 | 播放、图片、混排/唯一声音保留全部P0；D1仅验证关键后端与资源路线 |',
'| §28 VK-M4–M6 | 时间线、跟踪与安全导出需后续完整实现；六快照不等产品编辑器 |',
'| §28 VK-M7 | 正式AAR/兼容/可移除回退与真实Browser集成未过 |',
'| §28并行前提 | 公共API评审冻结是前提；当前不满足，不据建议并行擅自进入M0 |',
'| 后续App范围 | D已采纳Flutter，原文M0–M7建议表不取消后续执行文件中的App工作；当前无Flutter交付 |']
design=['PRODUCT_REQUIREMENTS','SYSTEM_ARCHITECTURE','PUBLIC_API_CONTRACT','LOCALVIDEOBROWSER_INTEGRATION','PLAYBACK_AND_IMAGE_DESIGN','EDIT_TIMELINE_AND_EXPORT_DESIGN','TRACKING_TECHNICAL_SPIKE','OPEN_SOURCE_AND_LICENSE_PLAN','TEST_AND_ACCEPTANCE_PLAN','MILESTONES']
for name in design:
    p='docs/'+name+'_V1.0.md'; assert (ROOT/p).exists()
    matrix.append(f'| §30 {name}.md | 已有版本化文件 {link(p)}；文档存在可确认，评审状态/实现与验收不得据存在推定 |')
matrix+=['\n## 3. 原文§4全部13项P0（无减项）\n',
'| P0原文行/内容 | 现有实现/证据 | 缺口与D1责任；最终阶段 |\n|---|---|---|']
p0details=[
('SET仅:app，BUILD是application；G.P10','正式api/Fake/示例不存在；D1确定可独立封装与释放语义，M0基础契约'),
('CPU六次snapshot/E11有限正常','非连续播放器；D1后端/源可行性，M1'),
('J09旧Bitmap对照，不在E11功能闭包','图片/动图危险解析与候选需D1处置；M2完整UI'),
('G.P07、§30宿主业务隔离设计','无真实HostAction产品；D1只需定边界，M0/M2'),
('G.P07与公共契约设计','无产品完整状态往返；D1列快照兼容风险，M0/M1'),
('CPU2/encoder1、SESSION账本；E11正常归还','未知未实测/唯一音频无证；D1许可/故障隔离可行性，M3'),
('六帧流水线不含时间线','D1确认输入/Sink接续，M4片段重排'),
('六帧无音频fMP4，不是多源拼接','D1记录remux与格式限制，M4/M6'),
('J10设计，无正式遮罩GL链','D1原生危险边界路线，M5/M6'),
('C14跟踪候选，无合法真实标签集完整证据','D1模型/样本权利与最小质量路线阻断，M5'),
('C14物体候选与模板对照','D1合法模型/LOST/纠正可行性，M5'),
('E11两READY+两0B ABORTED/SESSION门','真实UNKNOWN/断线/空间权限及全产品未证；D1关键释放/Sink语义，M6'),
('G.P10及设计，E11没有Browser产品适配','D1可移除/无业务API依赖路线，M0/M7'),
]
p0=[(i,l) for i,l in enumerate(lines,1) if re.match(r'\|.*\| P0 \|',l)]
assert len(p0)==13
for (ln,text),(impl,gap) in zip(p0,p0details):matrix.append(f"| U:{ln} {text.split('|')[1].strip()} | {impl} | OPEN：{gap} |")
matrix+=['\n## 4. J01–J11 当前实现差分（历史R2位置不可原样当现状）\n',
'| 门 | 当前源码位置/owner/权限与证据 | 缺证、状态及出口 |\n|---|---|---|']
jrows=[
('J01','CPU在isolated处理压缩源；旧MediaEngine宿主Media3路径属历史，不在最小E11产品闭包；E11两限定格式取帧','PARTIAL：仅MP4/H264、AVI/MPEG4；其他容器/持续播放/真实provider及普通发送者拒绝未证'),
('J02','CPU task/epoch+Binder实际UID/PID；FFmpeg在isolated；E11实际6源任务/normal','PARTIAL：正常读取/释放成立；C13故障限定证据保留，真实OOM/所有UNKNOWN不由正常路覆盖'),
('J03','SERVICE独立:e4_codec承担编码能力查询；同UID，非isolated，E11实际启动','PARTIAL：已迁出UI host地址空间；不具权限/RCE隔离，未证当前服务故障与他槽全链'),
('J04','SERVICE编码owner；SESSION保留在途与原代；E11 AVC6in/6out','PARTIAL：正常和指定取消通过；非native crash/卡住/实际UNKNOWN结束证明'),
('J05','SERVICE持Image/Plane或ByteBuffer；E11报告未独立声明Image分支已进入','OPEN：不得用正常编码推定所有色格式/Image路径；按实际分支再定有限验证'),
('J06','muxer在codec owner；SESSION宿主Sink/lease/file/fsync与AndroidLease JNI仍在','PARTIAL：实际正常close/输出结算成立，host残留JNI及FD未知未消除，flock不撤销恶意FD'),
('J07','输出CPU isolated validator mode11；E11两normal双EOF/drain/6decoded；旧双轨host验证历史保留','PARTIAL：当前6帧视频输出有限通过，不外推多音轨/validator death与全容器'),
('J08','旧SRT/Media3字幕路径；E11无字幕显示实现','OPEN：读取/解析/字体/Surface owner和销毁代次未证；D1设计路线，M1完整字幕'),
('J09','旧Bitmap/FaceDetector对照，不在当前E11能力闭包','OPEN：图像解析/动图/正式模型和资源边界未证；D1合法候选与危险解析决定'),
('J10','跟踪/遮罩/GL正式链未实现；C14/G记录候选','BLOCKED：模型/标签/质量及执行owner无证，不能把未实现写成已隔离；D1最小路线，M5完整'),
('J11','E11无实际Surface/Texture/AudioTrack/Flutter bridge；C14只有有限显示/PCM设计','BLOCKED：无准入PCM解码输入，禁止扩FFmpeg音频；先决定raw显示/source权威和音频合法路线再派功能实现'),
]
for j,impl,gap in jrows:matrix.append(f'| {j} | {impl} | {gap} |')
matrix+=['\n## 5. 开源选型与实际集成\n',
'OSS是2026-10-05初步估算，写明只有Flutter确定，不能把候选清单当依赖已冻结。BUILD实际只debugImplementation Media3 muxer及既有运行时约束；SET只含app。FM记录自有胶水是授权输入、队列、owner、Sink和资源门；不是自制codec。\n',
'| 原计划 | 当前事实（冻结记录/源码） | 差距与下一步 |\n|---|---|---|',
'| Flutter/本地化 | 已确定App路线，E11为原生Debug应用 | 未实现；M0桥接契约/M8完整App，禁止用Java测试APK冒充产品 |',
'| ExoPlayer | 旧C14 MediaEngine实验，当前最小E11只muxer依赖 | 持续播放/字幕/音轨后端仍缺；保留薄适配首选，先解决宿主读取与危险边界 |',
'| Transformer/Composition | 原首选，当前六帧编码采用公开MediaCodec+Media3 fMP4 | 没有Transformer输入/Sink正式集成；后续以精确Sink能力/故障边界再决定是否适用，不继续扩自有编辑框架 |',
'| Coil/SDWebImage | 图片候选，未在E11实际接入 | Android图片选型待验证；Apple仅分析，不启动构建 |',
'| OpenCV/YuNet/ViTTrack/ONNX | 历史固定候选/对照，正式模型/权重与标签权利未闭合 | 负责人组织权利与标注；不得自制跟踪器代替未达成P0 |',
'| media_kit控件 | 选择性MIT控件候选，E11无Flutter控件 | 不默认引入底层libmpv/FFmpeg；后续UI按已审组件适配 |',
'| FFmpeg8.0.3 | 当前受限Debug CPU库真实参与，原初估算未计入 | 后续受限技术准入不等闭源外发；7native/35Maven不扩；替换/再链接/NOTICE/专利等发行门OPEN |',
'| 自有协议工具 | broker、资源owner、source/Sink事务承担本项目边界 | 下一批复用既有监督/观察/生命周期；禁止新authority服务/诊断平台/另套取消框架 |',
'\n结论：D1关键剩余项是权限负例、UNKNOWN真实生命周期、产品源聚合及显示/音频危险边界、合法跟踪与封装可行性；全图片UI/1–12混排/完整编辑器和最终AAR发行仍按原阶段实施。下一批提案只选择其中一个可完整核验的功能簇，其余逐项OPEN，不宣布D1通过。\n']
save('docs/coder/D1_E12_REQUIREMENT_EVIDENCE_MATRIX_V1.0.md','\n'.join(matrix)+'\n')

decision='''# D1 E12 剩余门裁定 V1.0

日期：2026-10-18。提交负责人/独立tester审定；本文只做证据与范围裁定，不是未来实现/设备派单。

## 有限关闭

E6B-OBS-F01/P1仅在E11 final R1本平板、四个独立instrumentation host的真实当前观察范围记CLOSED_LIMITED_E11_CROSS_HOST。E11独立报告已接受准确14→15保数据部署、两个6帧READY、能力源零打开、条件取消、全部原资源和五PC自然归还。保持严格6帧/双EOF/drain/PTS1000µs；不重复MP4/AVI/迁移实现。未触发的UNKNOWN、重启、长期、其他设备仍OPEN。E11较旧交付中“尚未部署/回执不存在”是当时事实，由新报告补充，原冻结文件不改。

## 剩余门、优先级及责任

| 门 | 本批判定 | D1必须处置的有限内容与后续阶段 |
|---|---|---|
| 普通发送者权限 | OPEN，源码有exported=false及内核UID/实例校验，E11无实际普通发送者负例 | 下一完整批次先补最小真实负例和同授权host正对照；不同UID/旧代拒绝不等同UID RCE沙箱 |
| 隔离资源UNKNOWN | OPEN，SESSION/CPU/LIFE已有保留门，旧close-unproven是quarantine用例，E11 runner不选它 | 下一批先沿既有owner证明可返回的源/调用异常；真实永久UNKNOWN必须有原持有者持续保管及可观察停止方案后另派，不能为了JUnit结束释放/杀进程 |
| 源/取消/SourceReleased | PARTIAL，正常和条件取消通过 | 补双消费者/迟到返回/源聚合可行性；一个CPU结束不能宣布全源释放；NAS真实产品M1/M7 |
| renderer/audio/source边界 | BLOCKED，六帧输出没有Surface和声音；PCM合法路线未准入 | D1要明确压缩输入、raw渲染owner、音频源/焦点唯一权威、销毁代次和归还机制；先做具体接口差距决定，不扩音频codec/FFmpeg。实际显示/听音另完整批次，不以设计标PASS |
| 独立Kit | OPEN，SET只有app/BUILD application，并非AAR | D1先定无Browser类型/无硬编码宿主、服务命名和独立依赖的可行性；M0模块/API/Fake，M7独立构建、双宿主/可移除/升级实证，不要求本批提前完成M7 |
| J01–J11全危险链 | PARTIAL/OPEN，各行见矩阵 | J03–J05迁到独立codec进程是实际改进，同UID不提供权限隔离；host lease/file JNI、图片字幕GL/显示声音仍有边界缺口 |
| 跟踪与模型/样本权利 | BLOCKED | D1由负责人组织合法候选/标签/质量最小路线，不能以FaceDetector数量或模板完成度替代自动跟踪P0；完整M5/M6质量后验 |
| 许可/发行/供应链 | OPEN，当前受限Debug记录不能外推外发准入 | 冻结原7库/35Maven，FFmpeg8.0.3/Media3 1.9.3不扩；权利决定由负责人处理，M6/M7发行材料继续硬门 |
| 手机及设备差异 | OPEN/历史环境阻断 | 平板四方法不覆盖手机AVI/MKV音频旧差异；按可用资源后续整批验证，其他项目占设备时等待 |
| C13/C14 signal历史 | FAIL/UNKNOWN/NOT_RUN原样保留 | 2026-10-16 C13 self系统0严格FAIL，外部raw11及另方法OS11不互相覆盖；C14两项未跑。新的有限功能证据不修改历史测试结果 |
| 长期准入/重启 | OPEN | 新host短时通过不是长期可靠性；不再为本门扩展迁移/许可管理工具平台 |

## 下一批建议

建议只派“普通发送者与源资源生命周期完整簇”（暂称E13提案），详见两份NEXT_BATCH提案：补真实权限负例、授权source正对照、迟到源/多消费者释放以及既有UNKNOWN门的有限可核验检查，同一新候选一次集中构建。其核心是补现有输入/资源边界缺证，不重复编码normal实现，不再新增authority、安全或诊断模型。

真实永久UNKNOWN的Android quarantine执行不并入可正常收尾的四方法，也不得直接把旧closeUnproven方法加进E11 runner。先复用原owner/监督器做静态及受控可返回的有限检查；如果缺少既有机制可持有并观察未知，交BLOCKED及具体证据，由负责人再定专门批次，禁止拿模拟检查关闭Android UNKNOWN门。renderer/audio、Kit封装可行性以具体接口差距与决定同时提交；不提前实现M0或扩依赖。

这是优先次序建议，不是把其余D1项删除或延期到最终发布才发现：源聚合/渲染声音/封装关键接口仍不满足D1退出条件，完整D1不能在本提案完成后自动通过。全部13项P0、原文§27发布阻断及§29设计决定逐项保留。负责人审查后正式派发才开始下一批；当前D1 NOT_PASSED / M0 NOT_STARTED。
'''
save('docs/coder/D1_E12_REMAINING_GATE_DECISION_V1.0.md',decision)

coder='''# D1 下一完整批次 coder需求提案 V1.0

来源：E12审计建议；暂称E13，PROPOSAL_ONLY，未正式派发。不能凭本文启动实现、构建或设备测试。

目标：一次可审候选补齐普通发送者与授权输入实际生命周期的紧邻缺口，复用E11真实catalog/当前观察、原监督器与资源owner机制，不再建设许可/迁移诊断框架。

1. 在新目录/新候选保留E11完整冻结，新增精确白名单方法；权限负例覆盖无权第三方普通UID绑定exported=false服务的实际系统拒绝，同已授权host进行零媒体或最小授权source正对照。跨UID拒绝与同UID旧task/epoch/instance拒绝分栏；不同签名负例fixture仅Debug实验，不是产品必须另装companion。普通外部无法取得Binder时如实报告绑定边界，禁止冒称已执行内部onTransact。对直接Binder身份校验的单元/受控替身检查独立标注，不能伪作跨UID真机调用。
2. 以现有Provider/ReadHandle接口实现最小双消费者、迟到open/read/cancel/close可返回路径；证明源聚合释放的必要条件及引用归还，不提前造全部公共API/TestKit。未完成聚合不得发SourceReleased；凭据/完整路径与Browser业务类型不得进入接口，输入只读，输出只宿主临时Sink。
3. 沿SESSION/CPU/LIFE既有门做受控、可返回的错误与资源保留验证，精确记录原owner、调用进入/返回、引用、callback和permit。源码/本机检查与Android实际分栏。永久卡住/close-unproven仍UNKNOWN，不能用恢复替身的成功覆盖原资源。没有已有可审持续保管/观察/停止方案时，永久UNKNOWN实机项BLOCKED，不启动、不通过、不force-stop、不补close；将缺口作为完整交付的一部分交负责人裁定。
4. 同一交付给出source→raw frame→renderer/PCM→audio owner的具体接口差距图及Kit可提取依赖清单：真实Surface/AudioTrack未执行标NOT_RUN，合法PCM解码缺口标BLOCKED；列宿主残余JNI/权限、source消费者聚合、服务命名/host包依赖和Manifest。禁止扩FFmpeg音频/新模型/新后端，禁止声称同UID沙箱或独立AAR已完成。决定具体可复用的Media3/平台薄适配后，显示/声音功能另交完整批次建议。
5. 只集中一次Android构建，确因失败修正才记录必要补构建；不重建native、不下载依赖。新runner只选正式批准方法，旧E11编码normal作为已接受来源，若改动其共有实现才提出精确必要回归，不整类重跑。候选只交一次源码/pins/依赖锁/APK/ZIP/外置seal及完整结果/缺陷矩阵。

资源/真机：正式派单前给方法数、来源/字节、process/log/时间/输出上限及UNKNOWN保管出口；此提案不伪造已批准数值。原budget730a73e1-50e1-4198-a515-047104f00e31保持214483B/7R7S/0reserved接受基线，旧前缀/产物/fence/oldCloseACKfalse不动；默认权限/源实验不新建媒体输出，不重做迁移或清账。确需新输出的具体预算由正式派单列出，现有总4MiB/单2MiB/128任务不扩大。用户已有项目常规真机授权，其他项目占用时等待，不抢占。

完成标准：完整新增功能与本机/设备证据按正式派单交付，明确所有NOT_RUN/BLOCKED；源拒绝/取消/归还无虚报，历史FAIL不覆盖，E11封印逐字节保持。提案完成不自动关闭Android永久UNKNOWN、renderer/audio、独立Kit或全部D1门；tester独立审查后由负责人决定下一步。
'''
tester='''# D1 下一完整批次 tester需求提案 V1.0

来源：E12；暂称E13，PROPOSAL_ONLY，须负责人另行正式派发后才能执行。

先审核新候选唯一身份、源码/依赖/服务Manifest/方法白名单和E11不可变封印；独立复核方法数/字节/process/log/时间预算及UNKNOWN保管出口，未定则不启动。只验证完整“普通发送者与授权source资源生命周期”簇，不做MP4/AVI/迁移整类重跑。

| 项 | 真正独立成功条件 | 不得推定 |
|---|---|---|
| 普通第三方UID拒绝 | 实际系统身份/绑定返回、目标服务未开启任务或源；同授权host正对照 | exported=false静态事实不冒充实际拒绝；无Binder endpoint不能声称内部onTransact被调用 |
| 同UID旧代/错task/instance | 精确原实现拒绝、无源读取/输出/错误permit释放 | 不当作抵御同UID恶意RCE或授权凭证来源认证 |
| 授权source双消费者 | 同源两个真实consumer身份/代次；一个结束另一个仍可用；最终都返才SourceReleased | 一个CPU死亡/取消响应不能等全源释放；不得误释放他槽 |
| 迟到open/read与取消 | UI/取消响应与原操作真实返回分别记；迟到结果不被采用，资源各自归还 | 超时不等close或允许重试；可返回错误不充native故障 |
| UNKNOWN有限门 | 按实际源码/可返回检查证明保留与不READY/不复用；原owner审证 | 本机替身不等Android未知实测；永久UNKNOWN无合法保管出口则BLOCKED，禁止启动旧quarantine再强杀收尾 |
| renderer/audio/source及Kit差距材料 | 按实际源码核每一owner/UID/JNI/依赖/Manifest、source聚合/合法PCM/回退方案 | 材料审SUPPORTED不等显示声音PASS或AAR可分发 |

只有正式派单批准的可正常收尾方法可进行设备测试。常规项目真机授权已给，无需重复索取；先确认占用，其他项目在用则稍后。源码不由tester改动；若发现功能缺陷集中反馈新修复批次。任何PENDING/UNKNOWN保持原资源/证据，不重复派发、换UUID、清账、kill/force-stop或把新对象归还当旧对象关闭。

预算与原档：默认不产生新媒体输出；保持接受的214483B/7R7S/0reserved和旧107218B前缀，fence及oldCloseACK=false不改。无实际在线重读则只说“接受报告时点”。四方法以外回归必须有共有代码变化与正式范围理由。独立报告一次整包提交，保留历史C13系统signal0 FAIL、C14 NOT_RUN和ordinary UNKNOWN。D1 NOT_PASSED / M0 NOT_STARTED，不自行启动后续阶段。
'''
save('docs/coder/D1_E12_NEXT_BATCH_CODER_REQUIREMENTS_PROPOSAL_V1.0.md',coder)
save('docs/coder/D1_E12_NEXT_BATCH_TESTER_REQUIREMENTS_PROPOSAL_V1.0.md',tester)
planned='''

## 建议正式派单的六个精确入口与预算

以下为待负责人采纳的具体上限，不是已批准执行许可；方法名是新候选提案，不声称当前已有。

| 提议方法 | 最小完整行为 | 数据与结果 |
|---|---|---|
| ordinarySenderCannotBindCodec | 单个独立普通UID Debug负例fixture发起一次服务绑定，并核实际系统拒绝；授权host HELLO正对照 | 不取得源/FD、不触发编码；实际绑定返回与目标无任务分栏 |
| authorizedHostSourceReadAndClose | 原Provider接口授权本地实验source，正常open/read/close | 4096B独立生成非媒体字节；不读test_media或旧device媒体；不是NAS/解码证据 |
| oldGenerationNeverOpensSource | 同授权host旧task/epoch/instance由生产校验拒绝 | 原provider opens/reads/bytes均0，不以规则替身当真实跨UID证据 |
| twoConsumersHoldSourceUntilLastReturn | 同一只读实验source两个实际consumer，先返一个后另一个 | 两份原句柄与consumer身份；第一个关闭后另一个仍可读；最终才释放聚合源 |
| cancelLateOpenRetainsOriginalOwner | 受控Provider的原open迟到，取消先响应，原open确返后关闭其原句柄 | 进入/返回/原句柄close分别记；全程不把取消响应当SourceReleased |
| lateReadAndCloseFailureDoNotReleaseEarly | 原read在取消后返回被拒采纳；一次明确可返回close失败按既有允许规则处理 | 只验证可返回错误的实际账本/保留，原资源未返则保留UNKNOWN；不作永久native挂起 |

建议一次集中Gradle调用生成app/test及负例fixture；新候选精确版本/身份由正式派单锁定，不在本提案伪造已签发版本。必要安装只允许正式审过的pair升级各一次和独立fixture一次，未成功或身份不符停止；不重装/降级/clear。实验source总大小≤4096B，总读取≤64KiB，open≤8、close尝试≤16且不得超过原实现允许次数，无编码/validator任务、新输出/READY/R/S均0。每入口总观察窗≤30秒，其中取消响应/回收分别计时，不把30秒当强制终止保证；所有原资源未知即停止后继，不自动续下一项。

全批六入口各一次，宿主/负例fixture均由既有受管PC监督，不新增控制协议。process操作建议总≤48，日志/文本累计≤2MiB；只能采证明这些方法必需的metadata与原输出，不扫设备/媒体或全量重hash。达到预算或实际UNKNOWN停止并保留，不补次数/延时/换UUID。永久UNKNOWN/quarantine、native故障、真实OOM、重启与长期观察方法数量0。若实现发现此预算或原机制不足，集中交具体差距给负责人修订派单，不能自行扩范围。
'''
for p in ['docs/coder/D1_E12_NEXT_BATCH_CODER_REQUIREMENTS_PROPOSAL_V1.0.md','docs/coder/D1_E12_NEXT_BATCH_TESTER_REQUIREMENTS_PROPOSAL_V1.0.md']:
    save(p,read(p)+planned)
# Exact source line anchors supplement method/section names in the matrix.
patterns={
 'SERVICE':['getCallingUid','E4_CALLER_UID','admissionUnknown','private void verify','private Session exact'],
 'SESSION':['remoteClosed','boolean released','retainedSessions','directoryCloseUnknown','Source'],
 'CPU':['CPU_BROKER_IDENTITY','CPU_READ_BOUNDS','AbandonedSource','private void revoke'],
 'RUNNER':['onCreate','canFinish','PENDING_ORIGINAL_OWNERS'],
 'LIFE':['canFinish'], 'SELECT':['Set.of(MP4','receipt('],
 'OBSERVE':['beginCurrentObservation','ACTIVE','retained()'],
 'TEST':['@Before','normalMp4','normalAvi','capabilityDenial','cancelRejects','closeUnproven'],
 'BUILD':['application','sourceSets','debugImplementation'], 'SET':['include('],
 'MAN':['exported=','isolatedProcess='],
 'E11':['## ','### '], 'C13':['C13-T02','signal0','PID12673'], 'C14ENV':['NOT_RUN_UNCHANGED','2026-10-16'],
}
anchors=['# E12 精确源码与证据定位\n\n仅原文件行号/摘录，不执行所引用代码。完整字节见reference与pins。\n']
for key,needles in patterns.items():
    anchors.append('\n## '+key+'\n')
    for ln,t in enumerate(read(sources[key]).splitlines(),1):
        if any(n in t for n in needles):anchors.append(f'- {link(sources[key],ln)}：`'+t.strip().replace('`',"'")+'`')
save('docs/coder/d1e12/SOURCE_LOCATIONS_V1.0.md','\n'.join(anchors)+'\n')
print(json.dumps({'inputs':len(pins),'explicitRequirements':len(rows),'P0':len(p0),'J':len(jrows),'status':'DOCUMENTS_WRITTEN_NOT_FROZEN'},ensure_ascii=False))
