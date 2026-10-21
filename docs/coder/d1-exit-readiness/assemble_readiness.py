"""Offline document/source audit only. Does not import or execute candidate code."""
from pathlib import Path
import json, hashlib, re, collections

R = Path('D:/CodexProjects/VideoKit').resolve()
B = (R / 'docs/coder/d1-exit-readiness').resolve()
def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(p): return (R / p).read_text(encoding='utf-8-sig')
def dump(name, value):
    (B / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

E = {}
def evidence(k, path, kind, anchor=None):
    raw=(R/path).read_bytes(); lines=raw.decode('utf-8-sig').splitlines()
    line=next((i for i,s in enumerate(lines,1) if anchor in s), None) if anchor else 1
    assert line is not None, (k,anchor)
    E[k]={'path':path,'sha256':sha(raw),'bytes':len(raw),'kind':kind,'line':line,'quote':lines[line-1][:450]}
    return k

def report(k, name, kind='INDEPENDENT_REVIEW', anchor=None):
    return evidence(k,'docs/tester/'+name+'.md',kind,anchor)
report('E11','D1_E11_FINAL_R1_TABLET_EXECUTION_REPORT_V1.0','REAL_DEVICE','结论')
report('E6B','D1_E6B_NORMAL_DEVICE_TEST_REPORT_V1.0','REAL_DEVICE','MP4 PASS')
report('E6EXPORT','D1_E6_OUTPUT_EXPORT_REPORT_V1.0','BINARY_COLLECTION_ONLY','结论')
report('E3','D1_E3_REAL_IO_TEST_REPORT_V1.0','REAL_WINDOWS_BYTE_IO','结论')
report('C12','D1_C12_TEST_REPORT_V1.0','REAL_DEVICE','平板52项')
report('C13','D1_C13_TEST_REPORT_V1.0','REAL_DEVICE','52 PASS、3 FAIL')
report('PHONE','D1_PHONE_TEST_REPORT_V1.0','REAL_DEVICE','PHONE_BATCH_BLOCKED')
report('TABLET','D1_TABLET_TEST_REPORT_V1.0','REAL_DEVICE','22 个方法')
report('C02','D1_C02_TEST_REPORT_D1-20261005-C02','STATIC_AND_HISTORICAL','样本覆盖')
report('E12','D1_E12_REQUIREMENT_GATE_REVIEW_REPORT_V1.0','INDEPENDENT_READ_ONLY','结论')
report('E13C','D1_E13C_TABLET_EXECUTION_REPORT_V1.0','REAL_DEVICE_INCOMPLETE','结论')
report('E13C1','D1_E13C_TABLET_EXECUTION_REPORT_V1.1','ADMINISTRATIVE_UNKNOWN','结论')
report('F','D1_E13F_LIFECYCLE_REVIEW_REPORT_V1.0','OFFLINE_STATIC_AND_LOCAL_FIXTURE','PASS_LIMITED_OFFLINE_REVIEW')
report('AK','D1_AK_CONSOLIDATED_CLOSEOUT_REPORT_V1.0','ADMINISTRATIVE_DISPOSITION','TERMINATED_WITHOUT_RETURN')
report('R01','D1_RESUME01_STATIC_REVIEW_REPORT_V1.0','OFFLINE_STATIC','PASS_STATIC_CANDIDATE_ONLY')
report('R02','D1_RESUME02_ACTIVATION_EXECUTION_REPORT_V1.0','ENVIRONMENT_ONLY','ENV_WAIT_OTHER_PROJECT_OCCUPIED')
report('ENV03','D1_ENV03_EXECUTION_REPORT_V1.0','ENVIRONMENT_ONLY','ENV_WAIT_OTHER_PROJECT_OCCUPIED')
report('R2','D1_R2_REVIEW_REPORT_V1.0','INDEPENDENT_DESIGN_REVIEW','J03–J06')
report('C06','D1_C06_TEST_REPORT_V1.0','REAL_DEVICE','结论')
report('E4N','D1_E4A_N_DEVICE_TEST_REPORT_V1.0','REAL_DEVICE','binderRefusesBeforeBeginAndOversizeParcel')
report('E5ABORT','D1_E5C_N2_ABORT_REPORT_V1.1','REAL_RECOVERY','结论')
report('E5REG','D1_E5C_OBSERVE_REGRESSION_REPORT_V1.0','REAL_DEVICE','结论')
report('E7A','D1_E7A_MANAGED_DIAGNOSTIC_REPORT_V1.0','REAL_DIAGNOSTIC_ONLY','QUALIFIED_DIAGNOSTIC')
report('E9B','D1_E9B_READ_ONLY_IDENTITY_DEVICE_REPORT_V1.0','REAL_IDENTITY_ONLY','结论')
report('E10FINAL','D1_E10A_FINAL_READONLY_REVIEW_REPORT_V1.0','INDEPENDENT_RAW_EVIDENCE_REVIEW','结论')
report('ABDEPLOY','D1_E13A_E13B_TABLET_EXECUTION_REPORT_V1.0','REAL_HOST_DEPLOY_FAILURE','E13AB-DEPLOY-F01')
evidence('ASSIGNMENT','docs/milestones/D1_EXIT_READINESS_CODER_REQUIREMENTS_V1.0.md','CURRENT_ASSIGNMENT')
evidence('D1C','docs/milestones/D1_CODER_REQUIREMENTS_V1.0.md','REQUIREMENT','## 目标')
evidence('D1T','docs/milestones/D1_TESTER_REQUIREMENTS_V1.0.md','REQUIREMENT','TC-D1-01')
U='docs/VideoKit_User_Requirements_and_LocalVideoBrowser_Interface_V1.0_2026-10-05.md'
evidence('U',U,'ORIGINAL_REQUIREMENT')
evidence('E12ROWS','docs/coder/d1e12/requirement-rows.json','FROZEN_99_ROW_MAPPING')
evidence('E12M','docs/coder/D1_E12_REQUIREMENT_EVIDENCE_MATRIX_V1.0.md','HISTORICAL_MATRIX')
evidence('C14LICENSE','docs/coder/D1_C14_LICENSE_BUILD_ADMISSION_V1.0.md','FROZEN_LICENSE_FACTS')
evidence('TRACK','docs/coder/D1_C13_TRACKING_EVIDENCE_V1.0.md','FROZEN_RIGHTS_AND_LABEL_FACTS')
evidence('DECISION','docs/coder/D1_E13_RENDER_AUDIO_SOURCE_AND_KIT_DECISION_V1.0.md','DESIGN_ONLY')
evidence('C01','docs/coder/D1_DELIVERY_D1-20261005-C01.md','HISTORICAL_DELIVERY','## 10.')
evidence('THEME','docs/FLUTTER_THEME_AND_SKINKIT_DEFERRAL_V1.0.md','CURRENT_OVERRIDE')
evidence('BATCH','docs/MILESTONES_SKINKIT_ADDENDUM_V1.0.md','CURRENT_OVERRIDE','1–3')
evidence('ROOT','app/src/main/java/com/videokit/app/MainActivity.kt','CURRENT_ROOT_SOURCE','Hello $name!')
P='docs/coder/d1e13f/'
S=P+'src/com/videokit/spike/e4/'
A=P+'android/com/videokit/spike/e4/'
C=P+'upstream-c14/src/com/videokit/spike/c14/'
evidence('BUILD',P+'app/build.gradle.kts','FROZEN_PRODUCT_SOURCE','android.application')
evidence('SERVICE',A+'E4CodecService.java','FROZEN_PRODUCT_SOURCE','callerUid!=Process.myUid()')
evidence('MANIFEST',P+'app/src/debug/AndroidManifest.xml','FROZEN_PRODUCT_SOURCE','exported="false"')
evidence('SOURCE',S+'E13SourceGroup.java','FROZEN_PRODUCT_SOURCE','class E13SourceGroup')
evidence('LEASE',C+'LeaseRegistry.java','FROZEN_PRODUCT_SOURCE','boolean released()')
evidence('BRIDGE',C+'AsyncReadBridge.java','FROZEN_PRODUCT_SOURCE','class AsyncReadBridge')
evidence('SINK',A+'E4CodecSink.java','FROZEN_PRODUCT_SOURCE','class E4CodecSink')
evidence('SESSION',A+'E4Session.java','FROZEN_PRODUCT_SOURCE','E4CpuAdapter.validate')
evidence('MUX',P+'android/com/videokit/spike/c14/E6Muxer.java','FROZEN_PRODUCT_SOURCE','FragmentedMp4Muxer.Builder')
evidence('PERMISSION',A+'E13PermissionProbe.java','FROZEN_PRODUCT_SOURCE','E13_FIXTURE_MUST_BE_DIFFERENT_SIGNATURE_UID')
evidence('METHODS',P+'app/src/androidTest/java/com/videokit/spike/e4/E13DeviceTests.java','FROZEN_DEVICE_TEST_SOURCE','ordinarySenderCannotBindCodec')
evidence('SOURCECASES',P+'checks/com/videokit/spike/e4/E13SourceCases.java','FINITE_FIXTURE_TEST_SOURCE','class E13SourceCases')
evidence('SBOM',P+'evidence/apk-delivery-final/sbom.json','FROZEN_SBOM')
evidence('FINISH',P+'binding/com/videokit/spike/e4/E13FinishOwner.java','FROZEN_PRODUCT_SOURCE','class E13FinishOwner')
evidence('PC',P+'tools/E9PcSupervisor.java','FROZEN_HOST_SOURCE','class E9PcSupervisor')
evidence('GUARD','docs/coder/d1resume01/tools/E13PendingGuard.java','CURRENT_FROZEN_HOST_SOURCE','class E13PendingGuard')

# Root reports only. Never descend into tester live/raw/claim trees.
inventory=[]
for p in sorted((R/'docs/tester').glob('D1*.md')):
    raw=p.read_bytes(); lines=raw.decode('utf-8-sig').splitlines()
    markers=[{'line':i,'text':s[:1000]} for i,s in enumerate(lines,1)
             if re.search(r'结论|NOT_PASSED|NOT_RUN|BLOCKED|FAIL|ENV_WAIT|UNKNOWN|PASS',s)]
    inventory.append({'id':p.stem,'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':sha(raw),
                      'title':next((s for s in lines if s.startswith('# ')),''),
                      'opening': [{'line':i,'text':s[:1200]} for i,s in enumerate(lines[:18],1) if s.strip()],
                      'outcome_excerpts':markers,
                      'interpretation':'原报告逐行摘录；并存/历史状态不得按PASS关键词聚合；非本次重测。'})
dump('report-inventory.json', {'scope':'docs/tester root D1*.md only; no recursive traversal', 'reports':inventory})

rows=[]
def row(i,title,req,framework,status,impl,validation,code,ev,gap,action,stage='D1',block='IMPLEMENTATION_OR_DESIGN',device=True):
    rows.append(dict(id=i,title=title,requirements=req,frameworks=framework,status=status,
                     implementation_state=impl,validation_state=validation,code_refs=code,evidence_refs=ev,
                     gap=gap,offline_next_action=action,stage=stage,blocker_class=block,device_validation_needed=device,
                     status_scope='本行命名的限定范围；不自动关闭父要求/P0或历史失败'))
row('G01','媒体身份与样本覆盖',['D1-C1','TC-D1-01'],'既有probe/Media3；无后缀推断','BLOCKED','PARTIAL','PARTIAL_REAL',['BRIDGE'],['C01','C02','TABLET'],
    '45文件/17媒体记录、AVI/SRT/ASS及大MKV已有身份；动态、双音轨、特殊图和真实跟踪标签不足。旧hash不是本次全片验真。','只按已有清单列缺口；负责人提供合法缺样本/标签后另批补齐，不读媒体或伪造格式。',block='SAMPLE_AND_RIGHTS')
row('G02','精确依赖与Debug供应链',['D1-C2','TC-D1-07'],'Media3 1.9.3；受限FFmpeg 8.0.3；7 native/35 Maven','PASS','IMPLEMENTED_LIMITED','INDEPENDENT_OFFLINE',['BUILD','MUX','SBOM'],['C14LICENSE','F'],
    '仅已冻结Debug闭包身份/锁/NOTICE/SBOM通过；不是所有候选准入或外发许可。','保留现有锁和受限白名单，下一批只核必要差异。',device=False,block='NONE_WITHIN_SCOPE')
row('G03','发行与模型权利',['D1-C2','D1-C5','TC-D1-05'],'LGPL obligations；YuNet/ViTTrack；OpenCV/ORT候选','BLOCKED','PARTIAL','NOT_GRANTED',['SBOM'],['C14LICENSE','TRACK','F'],
    '权重未取验、训练/人物/样本权利、对应源/替换再链接/EULA/商店/专利等未闭合。','负责人分别形成权重/样本/发行用途决定；不得以隔离或目录LICENSE放行。',block='RIGHTS_AND_RELEASE',device=False)
row('G04','真实大偏移有限字节IO',['D1-C3','TC-D1-02'],'Windows既有readAt/guard工具','PASS','IMPLEMENTED_LIMITED','REAL_WINDOWS_IO',[],['E3'],
    '61场景/160断言，仅L/C/Z窗口和有限字节输出；非NAS、播放、全片快照及产品持久性。','沿用结果；五产品namespace durability变体继续NOT_RUN，不重复IO工具实验。',block='NONE_WITHIN_SCOPE',device=False)
row('G05','Android读取/seek/代次和工作线程',['D1-C3','TC-D1-02','TC-D1-03'],'AsyncReadBridge/isolated FFmpeg；历史Media3 DataSource','BLOCKED','PARTIAL','PARTIAL_REAL',['BRIDGE','SOURCE','LEASE'],['C12','C13','TABLET','PHONE','E11'],
    'C12/13 CPU读取消代次限定通过、旧平板播放五seek通过；当前闭包为snapshot，持续播放/NAS断线/手机AVI和音频差异未闭合。','用成熟播放后端薄适配明确随机读/seek/线程和错误范围；与呈现簇一起补，不重写容器解析。',block='BACKEND_AND_DEVICE_GAP')
row('G06','有限MP4六帧输出',['D1-C4','TC-D1-04'],'平台MediaCodec + Media3 fMP4 + isolated validator','PASS','IMPLEMENTED_LIMITED','REAL_DEVICE',['SINK','SESSION','MUX'],['E6B','E11'],
    'E6B及E11平板有限6帧、无音轨，双EOF/drain/PTS1000us门；非完整MP4/AAC产品导出。','无需重复实现正常MP4；变更影响时才做受影响回归。',block='NONE_WITHIN_SCOPE')
row('G07','有限AVI六帧输出',['D1-C4','TC-D1-04'],'AVI/MPEG4取帧→平台AVC→Media3 fMP4','PASS','IMPLEMENTED_LIMITED','REAL_DEVICE',['SINK','SESSION','MUX'],['E6B','E11'],
    'E6B Before阻断保留；E11另批实际6帧READY，AVI末PTS偏差1000us。不是AVI全格式/音轨或手机通过。','沿用E11实际结果；不因旧阻断或准备PASS重复实现。',block='NONE_WITHIN_SCOPE')
row('G08','能力拒绝不打开生产源',['D1-C3','D1-C4','TC-D1-04'],'既有EncoderCapabilities/CountingProvider','PASS','IMPLEMENTED_LIMITED','REAL_DEVICE',['SERVICE','SESSION'],['E11','E6B'],
    'E11实际拒绝opens/bytes/reads=0、ABORTED0；fixture自检读与生产源计数分开。','保留指定能力负例，非所有codec能力矩阵。',block='NONE_WITHIN_SCOPE')
row('G09','指定取消/错代/超尺寸/迟到帧',['D1-C3','D1-C4','TC-D1-03','TC-D1-04'],'既有session/lifecycle/lease','PASS','IMPLEMENTED_LIMITED','REAL_DEVICE',['SESSION','LEASE'],['E11'],
    'E11带本批两normal真实回执实际执行；仅指定路径，非持续导出中任意时点、永久UNKNOWN或系统OOM。','继承原实际返回/取消截止语义；不因环境等待另造取消框架。',block='NONE_WITHIN_SCOPE')
row('G10','完整OutputSink/编辑可行性',['D1-C4','TC-D1-04'],'Media3 Transformer候选；当前只有muxer真实接续','BLOCKED','PARTIAL','PARTIAL_REAL',['SINK','SESSION','MUX'],['E11','C12','C13','E3','E12'],
    '授权FD顺序通道/flush/close/abort/验证有代码及局部实证；正式Transformer输入、随机写协商、空间权限/断线/长输出/持久性全矩阵未闭合。','先冻结顺序/随机/seek/reopen能力差距与稳定错误；使用已有成熟后端薄适配，不能绕Sink路径。',block='SINK_API_AND_BACKEND')
row('G11','普通发送者不能绑定codec',['D1-C6','TC-D1-06'],'Android exported=false/Binder UID；独立签名fixture','NOT_RUN','IMPLEMENTED_LIMITED','NO_ACCEPTED_DEVICE_RESULT',['SERVICE','MANIFEST','PERMISSION','METHODS'],['E4N','E13C','E13C1','F','AK','R01','R02','ENV03'],
    'E4A-N的Binder四拒绝在授权同UID入口，非独立普通发送者；旧v17首case未得绑定结果后外部终止；候选19/fixture3仅离线通过且未部署。不能称内核拒绝PASS或产品FAIL。','现码无新独立阻塞缺陷；无需为占用重编，环境可用后由负责人派现有精确T07，不重放旧scope。',block='ENVIRONMENT_AND_DEVICE_VALIDATION')
row('G12','源聚合五方法的Android验证',['D1-C3','TC-D1-03','TC-D1-06'],'生产E13SourceGroup/AsyncReadBridge/LeaseRegistry','NOT_RUN','IMPLEMENTED_LIMITED','OFFLINE_ONLY',['SOURCE','LEASE','SOURCECASES','METHODS'],['F','R01','E13C'],
    '授权正对照、旧代、双consumer、迟到open、迟到read/close失败已有接线和有限本机证据；五真实Android方法均未执行。','保留原owner/在途/失败close，合法整体测试范围由负责人另派；不把测试fixture等同媒体全消费者。',block='DEVICE_VALIDATION')
row('G13','生命周期三项P1修复及当前host收窄',['D1-C6','TC-D1-06','TC-D1-07'],'既有owner/PC/claim原返回门','PASS','IMPLEMENTED_LIMITED','INDEPENDENT_OFFLINE',['FINISH','PC','GUARD'],['F','R01'],
    'F01/F02/F03仅生产静态/本机交错限定关闭；RESUME01四处收窄静态通过。不是Android生命周期或旧任务正常归还。','不再复造诊断/authority/发布管理平台；出现新证据再集中修复。',block='NONE_WITHIN_SCOPE',device=False)
row('G14','旧任务行政终结与UNKNOWN',['D1-C6','TC-D1-06'],'原owner/行政处置记录','BLOCKED','NOT_A_PRODUCT_IMPLEMENTATION','ADMINISTRATIVE_ONLY',[],['AK','E13C1','R01'],
    'A/K TERMINATED_WITHOUT_RETURN且originalJavaReturn=false；B/H等行政隔离UNKNOWN及原预算不得退款；外层退出非内部ACK。','只继承受审行政事实，禁止重查旧handle或补造正常返回；不是当前新scope自动放行。',block='HISTORICAL_UNKNOWN',device=False)
row('G15','真实故障隔离与资源门',['D1-C6','TC-D1-06'],'ordinary isolated CPU + sameUID codec process','BLOCKED','PARTIAL','PARTIAL_REAL_WITH_HISTORICAL_FAIL',['SERVICE','MANIFEST','LEASE','SESSION'],['C12','C13','R2','F','E11'],
    'C13 self系统signal0严格FAIL，外部raw11/独立双槽OS11不覆盖；C14两项NOT_RUN；OOM、宿主JNI/显示音频/长期/热与最低设备未闭合。','保留精确失败，按J01–J11处理真实危险链；不重复已知ordinary isolated codec/GPU或同条件信号注入。',block='FAULT_BOUNDARY_AND_THRESHOLD')
row('G16','真实frame呈现与SourceReleased接续',['D1-C3','D1-C6','TC-D1-03','TC-D1-06'],'成熟平台Canvas/Bitmap/Surface薄适配候选','NOT_RUN','NOT_IMPLEMENTED','DESIGN_ONLY',['SOURCE','LEASE'],['DECISION','E12','E11'],
    '没有实际Surface/Texture/render consumer；六帧内容比较不是画面；持续decode→renderer、销毁/旧代/producer归还未证。','下一完整簇实现有限呈现owner/consumer，实际PTS/rotation、队列/背压、销毁代次与源聚合；优先复用平台，不自制GL引擎。',block='MISSING_IMPLEMENTATION')
row('G17','PCM声音输出与唯一audio owner',['D1-C3','D1-C6','TC-D1-06'],'平台AudioTrack/焦点薄适配候选','NOT_RUN','NOT_IMPLEMENTED','DESIGN_ONLY',['SOURCE','LEASE'],['DECISION','E12'],
    '无AudioTrack真实运行；生成PCM仅能证明输出链，不能证明压缩音轨产品支持。','与呈现完整簇实现有限合法PCM输出、焦点唯一权威、epoch/seek/pause/flush/release/在途归还。',block='MISSING_IMPLEMENTATION')
row('G18','压缩音频合法后端接续',['D1-C2','D1-C3','TC-D1-03'],'Media3/系统音频后端首选；禁止扩FFmpeg音频','BLOCKED','NOT_IMPLEMENTED','NO_ADMITTED_ROUTE',['BUILD'],['DECISION','C14LICENSE','PHONE','TABLET'],
    '当前FFmpeg白名单无音频；旧手机MKV无声与平板有声并存，根因未证；生成PCM不能关闭此门。','负责人确认既有Media3/平台后端的权限/故障/许可可行性；离线实现前先评审路线，未获准不加codec。',block='BACKEND_RIGHTS_AND_DESIGN')
row('G19','跟踪检测/纠正/LOST/AMBIGUOUS',['D1-C5','TC-D1-05'],'OpenCV/YuNet/ViTTrack；ORT备选','BLOCKED','NOT_IMPLEMENTED','NO_RIGHTS_OR_GROUND_TRUTH',[],['TRACK','C14LICENSE','E12'],
    '真实标签0帧、完整权利clip0；权重未验、质量阈值/最低设备/离线网络实测未完成。FaceDetector数量不是跟踪成功。','先权利与真实PTS标签/独立复核，再精确候选有限离线推理与纠正/丢失/遮挡评估；不自制替代跟踪器。',block='RIGHTS_LABELS_QUALITY')
row('G20','Apple/Windows兼容设计分析',['D1-C7','TC-D1-06'],'AVFoundation/MediaFoundation设计；固定宽C ABI方向','PASS','DESIGN_ONLY','PLATFORM_RUNTIME_NOT_RUN',[],['C01','DECISION'],
    '分析完成限定通过；无平台实现/构建/设备证据，缺其他平台设备不阻断当前Android。','保留异步range/URL Sink/进程差异；当前不开发这些平台。',block='NONE_WITHIN_SCOPE',device=False)
row('G21','构建输入与候选一致性',['D1-C1','TC-D1-07'],'冻结Gradle/来源映射/锁','PASS','IMPLEMENTED_LIMITED','INDEPENDENT_OFFLINE',['BUILD','SBOM'],['F','R01'],
    'app19/test精确pair/fixture3独立核；host后续收窄只影响hostJAR。构建成功不等功能通过或已安装。','下一批仅对新产品变化一次必要集中构建；本审查不运行构建/候选检查。',block='NONE_WITHIN_SCOPE',device=False)
row('G22','M0关键API/Sink/阈值冻结',['D1-C7','TC-D1-07'],'既有PUBLIC_API/编辑/架构设计','BLOCKED','DESIGN_PARTIAL','NOT_READY_TO_FREEZE',['SOURCE','LEASE','SINK'],['E12','DECISION','TRACK','R2'],
    'render/audio消费者、完整Sink/错误/UNKNOWN、多宿主打包、质量与资源阈值仍缺关键决定；不能把实验硬限额定为产品SLA。','D1补可行性/备选/风险和正式决定；最终公共schema/能力矩阵经M0契约测试冻结。',block='M0_CRITICAL_DESIGN',device=False)
row('G23','独立Kit/AAR与发行可行性',['D1-C7','TC-D1-07','原文§25/27/29'],'原生媒体Kit；Media3薄适配；C ABI方向','BLOCKED','DESIGN_PARTIAL','NO_AAR_OR_TWO_HOST_PROOF',['BUILD','SOURCE','SINK'],['DECISION','E12','C14LICENSE'],
    '当前application非AAR；实验包名/UID/设备pin与服务命名需移除耦合，版本/独立依赖/双宿主/可移除和升级回退未实证。','D1先明确接口/Manifest/依赖提取路线；M0模块与契约，M7独立构建/双宿主/回退，不提前做完整M7。','D1可行性/M0/M7','PACKAGING_AND_INTEGRATION')

# All original thirteen P0 items. Later milestone implementation is retained, not demanded in D1.
p0=[
('P01','稳定公共API/Fake/sample-host','M0',['G22','G12'],'NOT_IMPLEMENTED','NOT_RUN','无正式公共契约/真实与Fake同套测试；当前:app不是SDK。'),
('P02','单视频播放','M1',['G05','G16','G18'],'PARTIAL','BLOCKED','旧Media3播放器仅历史有限证据，当前闭包snapshot；格式/轨道/恢复/seek完整矩阵未验。'),
('P03','静态/动态图片','M2',['G01','G15'],'NOT_IMPLEMENTED','NOT_RUN','Coil3.3.0候选未接正式链；图片/动图/大图预算/危险解析未证。'),
('P04','HostAction扩展按钮','M0/M2',['G12','G22'],'DESIGN_ONLY','NOT_RUN','宿主业务和凭据隔离已设计，真实动作/超时与源全释放接线未实现。'),
('P05','播放状态捕获与恢复','M0/M1',['G22','G05'],'DESIGN_ONLY','NOT_RUN','稳定版本快照、可选字段、未知主版本、状态单一权威未完成契约回归。'),
('P06','多实例与资源报告','M3',['G15','G17'],'PARTIAL','BLOCKED','CPU2/encoder1不是手机4/平板9/最多12槽；唯一声音/公平降级/热与归零未验。'),
('P07','单视频片段重排','M4',['G10'],'NOT_IMPLEMENTED','NOT_RUN','六帧输出不含可编辑时间线/undo/revision/重排恢复。'),
('P08','多视频拼接','M4/M6',['G10'],'NOT_IMPLEMENTED','NOT_RUN','无异参数、多源音轨/remux fallback全链。'),
('P09','手动打码','M5/M6',['G16','G15'],'NOT_IMPLEMENTED','NOT_RUN','坐标变换/遮罩/预览导出一致性无产品实现。'),
('P10','人脸自动跟踪','M5',['G19'],'NOT_IMPLEMENTED','BLOCKED','权重/样本/质量/漏码阻断未闭合。'),
('P11','移动物体自动跟踪','M5',['G19'],'NOT_IMPLEMENTED','BLOCKED','纠正传播/遮挡LOST/AMBIGUOUS/ID切换无质量证据。'),
('P12','安全导出和取消','M6',['G06','G07','G08','G09','G10','G14'],'PARTIAL','BLOCKED','局部正常/取消实证保留；正式编辑/音轨/空间/进程死亡/UNKNOWN全矩阵未完。'),
('P13','LocalVideoBrowser适配器契约测试','M0/M7',['G12','G22','G23'],'NOT_IMPLEMENTED','NOT_RUN','BrowserMediaSource/MediaPlayHobby/HostAction/邻近条/唯一音频与资源/SourceReleased/安全Sink/移除和崩溃回退的真实适配器契约测试未完成。')]
for i,title,stage,gates,impl,status,gap in p0:
    referenced=[r for r in rows if r['id'] in gates]
    row(i,title,['P0:'+i],'; '.join(dict.fromkeys(r['frameworks'] for r in referenced)),status,impl,'PRODUCT_ACCEPTANCE_NOT_COMPLETE',
        list(dict.fromkeys(c for r in referenced for c in r['code_refs'])),
        list(dict.fromkeys(c for r in referenced for c in r['evidence_refs'])),gap,
        '按完整里程碑实现及整批验收；D1只须闭合其关键技术/接口可行性，不提前实现全部P0。',stage,'FUTURE_MILESTONE_WITH_D1_FEASIBILITY_GAPS')
    original_line=90+int(i[1:])
    original_text=read(U).splitlines()[original_line-1]
    assert '| P0 |' in original_text
    rows[-1]['original_requirement']={'path':U,'sha256':E['U']['sha256'],'line':original_line,'text':original_text}

danger=[
('J01','压缩输入探测/容器',['G05','G11'],'受限isolated FFmpeg范围仅MP4/H264与AVI/MPEG4；持续/全格式未证。'),
('J02','隔离CPU解码/原始帧',['G05','G15'],'有限正常/取消有实证；OOM/所有UNKNOWN/恶意输入全链未闭合。'),
('J03','codec能力查询',['G15'],'已迁:e4_codec同UID地址空间，不是权限/RCE沙箱。'),
('J04','configure/MediaCodec',['G06','G07','G15'],'正常6in/6out通过，不代表native crash/永久卡住。'),
('J05','Image/Plane/ByteBuffer',['G15'],'未证明所有色格式与Image分支，ByteBuffer正常不能覆盖。'),
('J06','Sink/lease/file/fsync JNI',['G10','G15'],'muxer在codec；宿主FD/lease/file/fsync JNI风险仍在，锁不撤销恶意FD。'),
('J07','输出重新解析验证',['G06','G07','G10'],'isolated mode11双EOF/6帧限定通过；旧双轨宿主验证与全音轨未闭合。'),
('J08','字幕/字体/显示',['G05','G16'],'旧平板SRT/ASS局部播放/人工结果保留；当前显示owner/危险链未接续。'),
('J09','静态图/动图',['G01','G15'],'旧Bitmap对照不等正式Coil/大图/动图隔离。'),
('J10','模型/跟踪/遮罩/GL',['G19','G16'],'未实现且权利/标签/质量缺口，不能声称已隔离。'),
('J11','Surface/AudioTrack/Flutter桥',['G16','G17','G18'],'真实显示与声音无运行，压缩音频路线未准入；Flutter媒体桥未实现。')]
for i,title,gates,gap in danger:
    linked=[r for r in rows if r['id'] in gates]
    row(i,title,['D1-C6','TC-D1-06','原文§27'], '; '.join(dict.fromkeys(r['frameworks'] for r in linked)),
        'BLOCKED','PARTIAL_OR_MISSING','FULL_CHAIN_NOT_PROVEN',
        list(dict.fromkeys(c for r in linked for c in r['code_refs'])),
        list(dict.fromkeys(c for r in linked for c in r['evidence_refs'])),gap,
        '沿既有成熟组件及owner补具体边界/真实证据；不得用分进程或正常路替代全链故障验收。',block='FULL_CHAIN_SAFETY')

# Preserve every E12-frozen original requirement row with updated explicit status and gate links.
old=json.loads(read('docs/coder/d1e12/requirement-rows.json'))
assert len(old)==99
submap={'1':['G22','P01','P04','P05'],'2':['G05','G16','G18','P02'],'3':['G01','P03'],
        '4':['G15','G17','P06'],'5':['G10','P07','P08','P09'],
        '6':['G19','P10','P11'],'7':['G12','G22','P04','P05','P06','P13'],'8':['G05','G15','P02','P03','P13']}
special={
 'U27-01':['G10','P12'],'U27-02':['G10','P12'],'U27-03':['G22','P01','P13'],
 'U27-04':['G15','P06'],'U27-05':['G15','G17','P06'],'U27-06':['G19','P10','P11'],
 'U27-07':['G10','P12'],'U27-08':['G14','G15','P06'],'U27-09':['G03','P13'],
 'U27-10':['G02','G21','P13'],'U27-11':['G22','P13'],
 'U29-01':['G22','P01','P13'],'U29-02':['G22','P01','P13'],'U29-03':['G02','G03','G05','G10','P03'],
 'U29-04':['G19'],'U29-05':['G06','G07','G10'],'U29-06':['G10','P08'],
 'U29-07':['G15','G19','G22'],'U29-08':['G16','P01','P13'],
 'U29-09':['G10','G22'],'U29-10':['G10','P07'],'U29-11':['G22','P04'],
 'U29-12':['G15','G17','P06'],
 'U30-01':['G05','P01'],'U30-02':['G12','P04'],'U30-03':['P05'],
 'U30-04':['G17','P06'],'U30-05':['P04'],'U30-06':['G10','P12'],
 'U30-07':['G19','P09','P10','P11'],'U30-08':['P01','P13'],
 'U31-01':['G22','P01','P04'],'U31-02':['G05','G16','G18','P02'],
 'U31-03':['P02','P03'],'U31-04':['P06'],'U31-05':['P05'],
 'U31-06':['P04'],'U31-07':['P07','P08','P09','P10','P11','P12'],
 'U31-08':['G10','P12'],'U31-09':['P13'],'U31-10':['P13']}
expanded=[]
for r in old:
    text=r['text']; num=re.match(r'U26\.(\d+)',r['id'])
    gates=submap[num.group(1)] if num else special[r['id']]
    linked=[x for x in rows if x['id'] in gates]
    state='NOT_RUN' if num and num.group(1) in {'1','3','7'} else 'BLOCKED'
    current_lines=read(U).splitlines()
    positions=[i for i,s in enumerate(current_lines,1) if r['text'] in s and i>=900]
    assert len(positions)==1,(r['id'],positions)
    current_line=positions[0]
    # Conservative per-original acceptance status; narrow experiment PASS never closes full requirement.
    expanded.append({**r,'frozen_prior_original_line':r['line'],'line':current_line,'original_path':U,'original_sha256':E['U']['sha256'],
        'status':state,'status_scope':'完整原条目尚无产品验收/正式决定闭合；不是新运行FAIL，也非均须D1提前实现；局部PASS另见具体门',
        'frameworks':list(dict.fromkeys(x['frameworks'] for x in linked)),
        'code_refs':list(dict.fromkeys(k for x in linked for k in x['code_refs'])),
        'evidence_refs':list(dict.fromkeys(k for x in linked for k in x['evidence_refs'])),
        'implementation_state':'参照关联门逐项区分PARTIAL/NOT_IMPLEMENTED/DESIGN_ONLY；不能由本行状态倒推没有代码',
        'current_gate_ids':gates,'update':'E13F/RESUME01静态增量、E13C无有效设备结果、ENV03仅环境；M0按最新Theme/UI决定覆盖旧E12阶段描述。',
        'frozen_prior_mapping_preserved':True})
    assert r['text'] in current_lines[current_line-1]

requirements={f'D1-C{i}':[] for i in range(1,8)}
requirements.update({f'TC-D1-0{i}':[] for i in range(1,8)})
for r in rows:
    for q in r['requirements']:
        if q in requirements: requirements[q].append(r['id'])
assert all(requirements.values())
for r in rows:
    assert r['status'] in {'PASS','FAIL','NOT_RUN','BLOCKED'}
    assert all(k in E for k in r['code_refs']+r['evidence_refs'])

matrix={'schema_version':1,'audit_date':'2026-10-20','mode':'OFFLINE_READINESS_ONLY','d1':'NOT_PASSED','m0':'NOT_STARTED',
        'product_or_frozen_files_modified':False,'builds':0,'device_or_sdk_operations':0,'old_handle_queries':0,
        'status_semantics':{'PASS':'仅本行限定能力与证据范围','FAIL':'仅真实运行未达预期；历史FAIL独立保留',
                            'NOT_RUN':'没有可接受的真实运行结果；可有实现及离线检查','BLOCKED':'命名完整门缺实施/路线/权利/阈值/证据；不虚构运行失败'},
        'evidence':E,'coverage':requirements,'rows':rows,'original_99_rows':expanded,
        'report_inventory':'report-inventory.json',
        'historical_failures':[{'id':'C13_SELF_SIGNAL','status':'FAIL','evidence':'C13','detail':'App系统signal0严格FAIL；raw11不回填；C14两项NOT_RUN'},
          {'id':'PHONE_C02_AVI_AND_MKV_AUDIO','status':'FAIL','evidence':'PHONE','detail':'AVI超时、MKV人工无声；平板结果不覆盖手机'},
          {'id':'E6B_OBS_F01','status':'FAIL','evidence':'E6B','later_disposition':'CLOSED_LIMITED_E11_CROSS_HOST','later_evidence':'E11'},
          {'id':'E5C_REG_F01','status':'FAIL','evidence':'E6EXPORT','later_disposition':'MP4限E6B/E11正常范围关闭，旧失败不改','later_evidence':'E11'}],
        'next_batch':{'name':'D1_RENDER_AUDIO_SOURCE_FEASIBILITY','state':'PROPOSAL_NOT_AUTHORIZATION',
          'scope':['既有source/原PTS→有限真实呈现及销毁/旧代/归还','合法有hash的PCM→AudioTrack/焦点/唯一声音/归还','render/audio消费者接既有源聚合','成熟压缩音频后端及Sink能力差距决定；不扩未准入codec','独立Kit可提取接口/Manifest/宿主耦合差距'],
          'offline_dependencies':['负责人审定有限呈现/PCM与成熟音频路线及预算','合法PCM与媒体来源/hash','原source与owner接口不绕过','精确单候选及真实测试前置/全部资源收尾方案'],
          'expected_build':'有新Android功能变化后一次集中app/test构建；fixture不变则复用；无native或host变更不重编。失败修复才必要重建并保留首次日志。',
          'does_not_close':['完整D1','压缩音频若仍未准入','跟踪权利与质量','正式Kit/Flutter与M阶段产品验收'],
          'existing_T07':'现有码与制品复用；负责人另派准确scope，环境可用并全部前置满足才执行，不为环境占用重建。'}}
dump('exit-matrix.json',matrix)
dump('evidence-index.json',E)

# Every report is attached to a scope without promoting any opening PASS to functional success.
for item in inventory:
    n=item['id']
    if re.match(r'D1_C\d',n) or 'PHONE' in n or n=='D1_TABLET_TEST_REPORT_V1.0': group=['G01','G02','G03','G05','G10','G15','G19','G21']
    elif re.match(r'D1_E[123](?:_|[A-F]_)',n): group=['G04','G22']
    elif n.startswith('D1_E4'): group=['G06','G07','G08','G09','G10','G11','G15']
    elif n.startswith('D1_E5'): group=['G10','G14','G15']
    elif n.startswith('D1_E6'): group=['G06','G07','G08','G09','G10']
    elif re.match(r'D1_E(?:7|8|9|10)',n): group=['G10','G14','G15','G22']
    elif n.startswith('D1_E11'): group=['G06','G07','G08','G09','G10','G15']
    elif n.startswith('D1_E12'): group=['G22']+[x[0] for x in p0]
    elif n.startswith('D1_E13'): group=['G11','G12','G13','G14','G21']
    elif any(x in n for x in ['RESUME','ENV03','AK_CONSOLIDATED','TABLET_CLOSEOUT']): group=['G11','G13','G14']
    else: group=['G04','G10','G15','G22']
    item['scope_gate_links']=group
    item['functional_promotion']='NONE_AUTOMATIC; 仅精确gate行引用的真实报告范围可支持该行PASS，其余按原历史摘录保留。'
    item['review_depth']='完整字节读取并定位开头/所有状态原行；关键运行报告另作门级语义核对；不宣称重审全部底层现场raw。'
dump('report-inventory.json', {'scope':'docs/tester root D1*.md only; no recursive traversal', 'reports':inventory})

def link(k):
    x=E[k]; return f'[{k}](D:/CodexProjects/VideoKit/{x["path"]}:{x["line"]})'

md='''# D1 退出就绪完整交付 V1.0

2026-10-20。OFFLINE_READINESS_ONLY；供负责人审查与制定下一完整派单。**D1 NOT_PASSED，M0 NOT_STARTED。** 本次只读取原需求、已交付报告和当前/冻结源码并生成本审查文件；没有实现产品、运行候选自检、构建、SDK/5037/设备操作、live registry/claim或旧会话/handle查询，未修改任何既有产品或冻结文件。

## 1. 退出结论与证据口径

D1原退出门是完整实验包与独立报告齐全，并且输入/Sink/API的M0关键设计无悬而未决阻断。当前真实呈现/音频合法接续、源全消费者释放、完整Sink/成熟编辑后端适配、模型/真实标签/质量与危险链仍有关键缺口。不能仅凭后来的采集、包完整性或生命周期离线PASS宣布退出。亦不把M0–M8全部产品工作提前要求在D1做完：D1须先交清关键可行性与决定，公共契约/Fake、完整UI和各功能继续按原里程碑完成。

PASS只覆盖行名所述有限范围；BLOCKED可表示实施、设计、权利、阈值或证据缺失，并非新运行FAIL；NOT_RUN表示没有可接受的真实结果，即使代码和离线审查已具备。真实历史FAIL逐条保存，后续有限关闭不改写原报告。设计完成与平台运行分栏。

机器矩阵包含全部7项原coder要求、7项TC-D1、13项原P0、J01–J11及E12已独立核验的99条原文映射。99条原映射保留历史行/文字/差距，并按当前原文精确文本重新定位（当前前置补充使这些行整体增加18；历史位置另存，冻结E12不改），另加当前门链接与状态。原P0第13项是LocalVideoBrowser适配器契约测试；独立Kit/合规另外列G23及许可门，不拿它替换第13项。不能把历史E12阶段文字覆盖最新Theme决定。报告清单逐份读取根目录D1*.md、保存精确hash与结论/状态原行；不是按PASS关键词投票，也不递归访问tester现场证据树。关键运行裁定以本报告下列精确报告为准。

## 2. 特别要求的四项实证与权限门

| 项目 | 当前可接受结论 | 不能扩大的范围 |
|---|---|---|
| MP4 | E6B已限本平板六帧READY；E11新批次实际再次6in/6out、双EOF/drain/PTS门通过 | 无音轨六帧，不是正式MP4/AAC导出、持续播放或全设备支持 |
| AVI | E6B在Before观察失败且未进主体；E11另批真实六帧READY，PTS偏差1000µs在原门内 | 保留E6B失败；不是AVI全部编码、音频或手机通过 |
| capabilityDenialDoesNotOpenSource | E11实际执行，生产源opens/bytes/reads均0，0B ABORTED、资源返还 | fixture自检读取另算；不是全部codec矩阵 |
| cancelRejectsWrongEpochOversizeAndLateFrame | E11带本批两normal真实回执后实际执行；指定错代/147457B/迟到帧拒绝及取消/归还通过 | 不是任意长时导出、永久UNKNOWN、进程死亡或OOM通过 |
| ordinarySenderCannotBindCodec | **NOT_RUN（无有效设备结果）**；E13C v17首case曾PENDING后行政终止；F/RESUME01只是源码/本机限定PASS，19/fixture3尚未部署 | 不得宣称内核拒绝PASS、已触达内部transact或把挂起原因唯一归为绑定；也不能因ENV_WAIT判产品FAIL |

E11关闭E6B-OBS-F01仅为CLOSED_LIMITED_E11_CROSS_HOST：本平板四个独立host与受审14→15保数据部署。其他设备、重启、长期、新UNKNOWN仍未证。E6失败输出53651B收取PASS只证明导出字节完整，不代表该旧媒体内容合格。

E4A-N的binderRefusesBeforeBeginAndOversizeParcel确有一次真实PASS，但四拒绝是BEGIN前FRAME/错epoch/旧instance/超Parcel，并非独立签名普通UID绑定负例；不能移植给ordinarySenderCannotBindCodec。

'''
md+='证据：'+', '.join(link(k) for k in ['E6B','E11','E6EXPORT','E4N','E13C','F','R01'])+'。\n\n'
md+='''较早真实结果按范围继续保留，不用最新准备材料冲掉：

| 历史序列 | 已证明/仍保留的事实 | 当前如何使用 |
|---|---|---|
| C03平板→C04/05→C06/07 | C03为7PASS/5FAIL/10BLOCKED；C04为20/3，C05为23/2，C06为25/1，C07为27/1；C06双轨正常导出/安全恢复门及AVI取帧已有实证 | 旧双轨宿主链不等当前isolated输出全音轨；普通isolated/严格信号历史失败不抹掉 |
| C09→C10→C11→C12→C13 | C09平板16/4/12，C10为38/2，C11为20/2/23；C12平板52PASS，C13为52/3/14；手机后续多批系统禁用 | C12注册/解码正常结果保留；C13新管线configure失败后由新路线有限normal补证，严格self signal FAIL独立保留 |
| E4A-N/N2→E5C | N2正常MP4 PENDING无帧且保留原预留；E5C隔离/只读QUERY限定通过，后原N2准确ABORTED_SETTLED0B | 原oldCloseACK=false及旧失败不补；真实恢复只归其事务，非新编码成功 |
| E5C回归→E6导出→E6B→E7A | E5C六帧输出验证FAIL；E6收取53651B成功；E6B仅MP4正常；E7A真实历史API返回0记录/死亡门仍BLOCKED | E6B-OBS根因不猜测；后E11四host有限解决，未知/长期不补 |
| E9B→E10A补审→E11 | E9B只读身份/ACK/归还；E10A单actor迁移原执行后补审完整DAG与终局PASS；E11新批四方法真运行 | 前两项是身份/迁移证据，不是媒体功能PASS；E11功能范围独立见上 |
| E13→E13A/B→E13C→D/E/F→RESUME01 | E13解绑虚报和A/B once文件名冲突均有独立历史缺陷；C完成部署但首case未返；D/E/F后续限定修复/复审 | 不要求再重修已关闭静态问题；最终Android结果仍缺，原任务行政false/UNKNOWN保留 |
| RESUME02→ENV03 | 分别2次环境读取，global均占用，后续部署/T07未执行 | 环境事实只限报告时点，无本轮设备复查，无新产品FAIL |

'''
md+='补充来源：'+', '.join(link(k) for k in ['C06','E5ABORT','E5REG','E7A','E9B','E10FINAL','ABDEPLOY'])+'；其余逐份原结论与SHA见118份报告索引。\n\n'
md+='''## 3. 原D1要求覆盖与逐门完整矩阵

以下代码栏给出实际源码锚点；空白表示没有对应产品实现或该门为权利/分析/行政事实。源码存在不代表真实执行。精确SHA、行号、证据类型、实施状态和验证状态均在JSON，表中不重复长hash。

| 原要求/用例 | 关联矩阵行 |
|---|---|
'''
for q,ids in requirements.items(): md+=f'| {q} | {", ".join(ids)} |\n'
md+='\n| ID/门 | 状态/实施/验证 | 代码；真实证据 | 剩余缺口与离线动作 |\n|---|---|---|---|\n'
for r in rows:
    md+=f'| {r["id"]} {r["title"]} | {r["status"]} / {r["implementation_state"]} / {r["validation_state"]} | '+', '.join(link(k) for k in r['code_refs'])+'；'+', '.join(link(k) for k in r['evidence_refs'])+f' | {r["gap"]} **下一步：**{r["offline_next_action"]}（{r["stage"]}） |\n'
md+='''
## 4. 当前真实工程与成熟框架复用

根MainActivity仍是Hello Android/Compose示例，不是已交付Flutter产品。E13F app的Gradle为android.application，Debug只引Media3 muxer；隔离CPU受限FFmpeg取帧/输出验证、平台MediaCodec、Media3 FragmentedMp4Muxer及项目自有输入/Sink/资源薄适配才是当前真实闭包。:e4_codec为同UID独立地址空间，ordinary isolated CPU是另一边界，两者不能混称权限/RCE全沙箱。实际SourceGroup聚合原LeaseRegistry，released条件为retired && consumers==0 && operations==0 && !closeFailed；这尚未覆盖产品播放、图片、字幕、跟踪、render、audio全部消费者。

| 原定框架 | 实际事实 | 后续复用决定/缺口 |
|---|---|---|
| Media3 1.9.3 ExoPlayer/Transformer/muxer（Apache-2.0冻结记录） | 旧播放器/Transformer实验有历史代码和有限设备结果；当前19闭包直接用muxer | 保持成熟播放/编辑后端薄适配首选；不把六帧自有胶水称完整Transformer/ExoPlayer接入，不另造容器/编辑框架 |
| Coil 3.3.0（Apache-2.0候选）/平台ImageDecoder | 图片候选及旧对照；非当前正式图片闭包 | 图像/动图/大图预算和危险解析尚需可行性；SDWebImage仅Apple设计候选 |
| OpenCV/YuNet/ViTTrack；ORT 1.22.1候选 | 固定Zoo commit/LFS身份及许可文字，不是实际权重已验或合法成品 | 模型、训练/人物/样本权利单审，0真实标签，不能以候选数/空模板关闭质量门 |
| FFmpeg 8.0.3有限Debug闭包 | 实际7native/35Maven冻结、原5个FFmpeg/allocator库来源保持；只运行受限MP4/H264、AVI/MPEG4 | 不扩音频/encoder/network，不以LGPL或FFI/隔离豁免发行义务；NOT_GRANTED发行状态保留 |
| Flutter/Theme/C ABI | 正式Flutter及共享内核未实现，原生状态单一权威/opaque handle方向已定 | M0自有ThemeData/ThemeExtension及整套UI；不把逐帧媒体经Dart往返，不引Browser凭据/路径/数据库类型 |
| media_kit控件、libmpv/libVLC/MDK等备选 | 不是当前集成事实 | Dart MIT不批准底层FFmpeg；GPL应用代码不得复制，LGPL构建/专有商业权利分别审核，无新依赖准入 |

以上版本与许可仅复核项目冻结材料，不是联网查询最新版本或新法律结论。当前不下载模型、媒体、依赖或替换后端。

## 5. 缺陷、实现缺口、设备验证与环境必须分开

**真实历史失败：**C13 self SIGSEGV的App系统signal0仍严格FAIL，外部raw11及另一任务OS11不回填；C14两项仍NOT_RUN_UNCHANGED_PLATFORM_LIMIT。手机C02 AVI超时与MKV实际无声不因平板有声/后续CPU通过自动关闭，根因不能臆断。E6B观察问题与E5C正常输出问题只在后续明确有限实证范围关闭。当前审查未产生新的运行失败或新增源码缺陷编号。

**可以离线推进的真实产品工作：**尚无render/Surface生命周期、AudioTrack/焦点唯一owner、压缩音频合法接续、正式成熟编辑输入/Sink适配、全部source consumer接续、图片/动图、时间线、遮罩/跟踪、独立Kit/Fake/Flutter等实现。后七类大部分属M阶段，本轮不提前开工；D1先补关键后端/输入/Sink/API/危险链可行性与权利/质量决定。E13F/RESUME01已有修复和源聚合接线不能因缺设备结果被说成“未写代码”。

**代码已具备但只缺真实验证：**普通发送者与源生命周期六方法；当前仅T07有已准备的下一scope材料，其他五法不能自行加入。继承F/RESUME01独立离线通过，无新源码证据时不重新实现或构建同功能。后续授权前置仍按原owner/真实返回/未知保管执行。

**环境：**RESUME02在identity PASS后global ENV_WAIT；原2/43 SDK读取388818B，未部署/测试。ENV03准确2/2读取371309B，LendManager前台，所有本轮原资源自然归还、无pending，也未部署/测试。它们不是产品FAIL、不是重新构建理由、不是当前在线状态，本审查没有再次查设备。scope已停，静态NOT_CONSUMED不授权重播，不挪旧预算。A/K行政TERMINATED_WITHOUT_RETURN/false与B/H未知保留，不用外层退出/进程缺席补内部ACK。

'''
md+='依据：'+', '.join(link(k) for k in ['C13','PHONE','F','R01','AK','R02','ENV03'])+'。\n\n'
md+='''## 6. 推荐下一整批：D1 呈现、合法PCM与源聚合可行性

这是供负责人审查的**完整功能簇提案，未实施、未构建、不是派单**。它处理现存render/audio/source关键缺口；不再新增发布、许可管理、诊断或控制平台。已具备的T07作为现有候选的独立受管验证计划保留，不为了等待设备创建另一轮同码候选，也不把其通过当本簇前提全部满足。

1. **完整开发范围：**复用既有受限raw frame来源与source/lease owner，接成熟平台Canvas/Bitmap/Surface最小呈现适配，携带原PTS、布局、rotation、task/epoch/sourceVersion及Surface generation。有限帧/时长、队列/在途/内存须负责人明确上限；处理暂停/seek旧代、Surface销毁重建、消费者失联、最后producer detach/原引用归还。没有真实持续解码时只能叫有限呈现，不能称完整播放器。
2. 同包接**权利明确、精确hash的本地生成或批准PCM16**到平台AudioTrack，单audio owner统一焦点、唯一发声/全静音、epoch、在途write、stop/flush/release及源聚合；采用既有48kHz双声道、≤20ms/3840B块候选，队列4/在途1仅作为待审有限预算，不擅定公共阈值。两消费者中的一个结束不提前SourceReleased；UI不持锁等IPC。
3. 同包必须交清**成熟Media3/平台压缩音频后端**、持续播放源、危险解析/同UID残余JNI、正式Sink的顺序/随机/reopen能力及独立Kit提取的具体接口差距和备选。压缩音频未经准入保持BLOCKED；PCM输出成功不关闭音轨支持。Kit服务命名/Manifest占位、移除实验包名/UID/inode耦合、无Browser业务依赖在D1给可行性决定，正式AAR仍M7。
4. **前置依赖：**负责人审定上述有限功能范围/合法来源和成熟后端路线；明确何项必须运行、实际测试证据及停止/归还方案；不扩受限FFmpeg音频、模型或新后端。若既有架构无法承接无权限/故障隔离条件，则先交具体BLOCKED决定，不以known-unsafe探针反复杀宿主。跟踪权利与标签由负责人并行组织，不假设本簇能解决。
5. **离线自检和一次构建：**先完成受影响owner/epoch/背压/销毁/焦点/source聚合有意义的有限测试及静态边界核查；统一源码后一次集中app/test构建并锁依赖/输入/候选hash。fixture未改复用、native未改不重编、host工具未改不重编。首次失败留证，修复后的必要集中重建不冒称“第一次即通过”；不为增加断言数扩大测试。代码/平台接口变化应在集中构建中实际检查。
6. **整批独立验收：**设备被释放且负责人正式派发后，同一候选一次完整簇验收：真实截图方向/帧与seek代次；真实听音或批准回环；焦点和唯一声音；Surface销毁/错误/迟到/取消；各consumer与原线程/FD/回调实际返回；现有正常输入/Sink受影响回归。记录观察窗与实际返回分离，UNKNOWN持续原owner保管，不强finish求绿。静态/JVM不替代设备效果，测试报告集中缺陷后统一修复回归。

这批即使限定通过，仍不自动关闭D1：压缩音频、模型/真实标签/质量、全危险链、必要手机差异、正式Sink/公共API关键决定需逐门审定。也不要求先做完全部后续M阶段UI/编辑/发行才能结束D1。退出由负责人根据完整矩阵决定。

## 7. M0保留范围、可冻结与禁止冻结

可继续保留为设计方向：opaque token/sourceVersion、原生播放状态单一权威、只读随机输入/授权临时Sink、真实原返回前不退租、未知保管、UI无线程阻塞、Kit不依赖Browser业务/Flutter、固定宽C ABI与retain/release/代次方向。**禁止据Spike直接冻结**最终API/schema/HostAction事务、完整Sink能力、全格式支持、唯一声音与资源算法、平台codec安全承诺、质量/热/时延/最低设备阈值、权重和发行权利、未知分支成功语义。

最新M0保留API/Fake/TestKit/sample-host，并优先实现按18页PPT的完整正式Flutter App UI、自有VideoKit ThemeData/ThemeExtension/集中Token、主题与偏好、中英/RTL/大字/无障碍/手机平板适配；明确标识的固定seed模拟数据仅供UI演示。SkinKit延后至正式Flutter支持后再评审，当前不接其Android二进制/桥接，不作为M0/M8硬门。M1–M6真实功能接回同一UI，M7独立宿主/AAR，M8全真实集成。负责人以后每批选择1–3个**完整**里程碑，整批开发自检冻结→tester整批验收→集中修复回归，不能逐小问题反复交接。当前M0仍NOT_STARTED。

'''
md+='现行覆盖决定：'+link('THEME')+'、'+link('BATCH')+'。\n\n'
md+='''## 8. 交付物与只读核验

- 本报告：`docs/coder/D1_EXIT_READINESS_DELIVERY_V1.0.md`。
- `docs/coder/d1-exit-readiness/exit-matrix.json`：逐门实施/验证/状态、代码/证据引用、7+7覆盖、13P0、J链、99原文和下一完整批提案。
- `evidence-index.json`：关键文件精确SHA256、长度、类型与行锚；`report-inventory.json`：全部根D1报告原结论/状态摘录与精确hash。
- `assemble_readiness.py`：仅本地文档解析/写本审查产物；不导入候选、不执行构建/SDK/设备。`verification.json`保存语法/引用/覆盖/输入未变核验与输出hash，核验数量不是功能测试数量。

本次没有新产品候选、APK/AAR或运行授权，没有推进M0，也没有通过文件存在或准备PASS抹除任何历史失败/未知。完整材料一次性交负责人审查后等待正式下一整批派单。
'''
(R/'docs/coder/D1_EXIT_READINESS_DELIVERY_V1.0.md').write_text(md,encoding='utf-8')

# Validate generated links and unchanged referenced bytes. No candidate execution.
checks=[]
checks.append({'id':'unique-gate-ids','pass':len({r['id'] for r in rows})==len(rows)})
checks.append({'id':'all-7-coder-and-7-tester-covered','pass':len(requirements)==14 and all(requirements.values())})
checks.append({'id':'all-13-original-P0','pass':len([r for r in rows if r['id'].startswith('P')])==13})
checks.append({'id':'all-11-danger-boundaries','pass':len([r for r in rows if r['id'].startswith('J')])==11})
for r in expanded:
    checks.append({'id':'original-text:'+r['id'],'pass':r['text'] in read(r['original_path']).splitlines()[r['line']-1] and all(x in {z['id'] for z in rows} for x in r['current_gate_ids']) and all(k in E for k in r['code_refs']+r['evidence_refs'])})
for r in rows:
    if 'original_requirement' in r:
        o=r['original_requirement'];checks.append({'id':'original-P0:'+r['id'],'pass':read(o['path']).splitlines()[o['line']-1]==o['text'] and '| P0 |' in o['text']})
for k,x in E.items():
    checks.append({'id':'input:'+k,'pass':sha((R/x['path']).read_bytes())==x['sha256']})
for x in inventory:
    checks.append({'id':'report:'+x['id'],'pass':sha((R/x['path']).read_bytes())==x['sha256']})
for path in re.findall(r'\]\(D:/CodexProjects/VideoKit/([^):]+)(?::(\d+))?\)',md):
    p=R/path[0]; checks.append({'id':'link:'+path[0]+':'+path[1], 'pass':p.exists() and (not path[1] or int(path[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()))})
assert all(c['pass'] for c in checks)
outpaths=[R/'docs/coder/D1_EXIT_READINESS_DELIVERY_V1.0.md']+[B/n for n in ['assemble_readiness.py','exit-matrix.json','evidence-index.json','report-inventory.json']]
outputs=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in outpaths]
verification={'result':'PASS_OFFLINE_DOCUMENT_REFERENCES_ONLY','counts':{'matrix_rows':len(rows),'original_rows':len(expanded),'reports':len(inventory),'key_inputs':len(E),'reference_checks':len(checks)},'coverage':requirements,'checks':checks,'outputs':outputs,'candidate_tests_run':0,'builds':0,'sdk_or_device_operations':0}
dump('verification.json',verification)
print(json.dumps({'result':verification['result'],'counts':verification['counts'],'statuses':dict(collections.Counter(r['status'] for r in rows)),'outputs':outputs},ensure_ascii=False,indent=2))
