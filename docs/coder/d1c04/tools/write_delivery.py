"""Generate C04 reports using audited artifact identities; never operates devices."""
from pathlib import Path
import json,re,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c04';e=base/'evidence';docs=root/'docs/coder'
rows=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks']
table='| 冻结文件 | 字节 | SHA-256 |\n| --- | ---: | --- |\n'+'\n'.join('| '+Path(r['path']).name+' | '+str(r['bytes'])+' | '+r['sha256']+' |' for r in rows)
methods={n:re.findall(r'@Test public void (\w+)\(', (base/'device/com/videokit/spike/c04'/n).read_text(encoding='utf-8')) for n in ['C04DeviceTests.java','C04IsolatedDeviceTests.java']}
delivery="""# D1-20261005-C04 开发交付

日期：2026-10-05；状态：BLOCKED / NOT_READY。所有 C04 Android 项目 NOT_RUN；本轮没有 ADB、安装、设备复制、清理或 M0 发布。依据 D1_C04_CODER_REQUIREMENTS_V1.0.md（含11:40平板补充）。没有缺陷被记作真机已关闭。

## 缺陷处理矩阵

| 需求 | 已完成代码与诊断 | 未完成证明及状态 |
| --- | --- | --- |
| PHONE-C02-01 | 新编写 Windows shell-v2 raw 流式二进制传输，默认PLAN_ONLY；固定C04私有别名、显式serial、空间与未知数据检查、源/目标长度及SHA；32KiB缓冲 | 桌面实际生成2147495993字节协议流及控制字节验证PASS；设备实际复制NOT_RUN |
| PHONE-C02-02 | AVI有/无SRT入口；prepare/mainLooper/Extractor/sniff/read/字幕阶段日志；5秒主线程等待、30秒准备预算；独立撤销Source并记录实际排空 | 旧180秒挂起根因未知；单次native/Extractor阻塞不能协作硬停；graphics未知不能称全释放，BLOCKED |
| PHONE-C02-03 | Android12 AMS拒绝含UUID连字符的isolated实例名，改为规范UUID派生合法名称；任务原UUID保持；source/bind/RPC/broker原cause及阶段保留；故障需实际进入hits=1 | 名称缺陷静态确认；旧NORMAL原因被旧代码丢弃，是否该缺陷导致旧失败须实测；NORMAL先PASS，BLOCKED |
| PHONE-C02-04 | 音轨支持/选择、renderer/session/sink/focus诊断；手动非静音MP4/MKV同机入口；AC3条件方案单列 | 手机MKV无声根因未确定；静音READY不算声音通过；未集成FFmpeg/GPL/未知权重，BLOCKED |
| TABLET-C03-01 | normal导出完整cause/stack及muxer阶段；对齐Media3 adapter的负时间戳声明、视频旋转与可选metadata过滤 | 1001是FAILED_RUNTIME_CHECK，旧日志缺内层cause；NO_INIT出现在release附近不足定根因；真实编码恢复BLOCKED |
| TABLET-C03-02 | ordinary实际codec API探针在身份/Hello/租约成功后运行，create失败与release未知分别记录 | 旧start失败不是codec权限证据，C04设备NOT_RUN；单App/Kit评估仍BLOCKED |
| TABLET-C03-03 | ordinary broker名称与原cause修复并保留正常前置；companion真实媒体、普通broker分别记录 | 下游fault/cancel/death/并行/跨owner不得由任意IOException冒充命中，BLOCKED |
| TABLET-C03-04 | AVI10秒scaled为空回退同10秒未缩放再有界缩放；MP4 2秒控制；元数据/空帧/超时/真实资源账本 | 不替换成0秒或空Bitmap；native挂起保留单槽隔离；实际frame PTS UNKNOWN、质量NOT_RUN，BLOCKED |

平板AVI与MKV人工正常不替代手机问题闭环。旧C02手机5项3PASS/1FAIL/1BLOCKED；旧C03平板22项7PASS/5FAIL/10BLOCKED，仅为先前候选证据。

## 本轮验证

最终离线strict构建PASS：App Debug、AndroidTest、worker Debug、unsigned Release、testDebugUnitTest，见c04-final-build.log。单元测试任务成功不代表新增Android覆盖。help配置探针按预期拒绝受限connected/UTP请求，未运行设备任务。

本轮47合同+7控制+6二进制协议断言全部PASS，共60。24恢复+12验证反例沿用冻结C03日志，未重复运行；四个规则/decoder/selfcheck源除命名空间外一致，见c03-evidence-reuse.json。T01独立视频/音频、时长、PTS及完整视频decode规则不变；T02指定stage、hits=1、错误链及编码后validate保留，gate-preservation.json仅静态确认。负PTS adapter声明对齐底层，但严格PTS门禁未放宽；设备不满足仍拒绝READY。

自有lease.c用NDK30重编译ARM64/API31，C04JNI运行NOT_RUN。App346/worker95个锁定坐标全来自既有审查图，无新坐标；OSV与47个advisory详情复用基线，不是新扫描或已修补。16个匹配组件工具限制继续有效，C03工具安全决策适用。NOTICE不等于法律准入，模型权利未关闭，无权重下载。包审计无INTERNET、命名样本/模型条目；release不含C04实验类；三份debug APK同签名。

"""+table+"""

冻结件目录：docs/coder/d1c04/artifacts/D1-20261005-C04。源码ZIP与完整文件/hash清单见evidence/source-manifest.json和freeze-summary.json；git_commit=null。报告不嵌入自身或ZIP hash，避免循环身份，以冻结清单为最终依据。verify_freeze.py只读核验产物、证据、ZIP及当前源。

C01/C02/C03候选快照、产物、证据及45个源媒体保持原hash，见integrity-check.json；可变根App/Gradle配置切到C04，不改旧快照。旧设备报告hash仅来源记录。

集中补测见D1_C04_DEVICE_APPENDIX_V1.0.md；23个入口准备完成，设备全部NOT_RUN。负责人选定C04并确认旧包/数据保留后由tester运行。隔离/AC3条件见D1_C04_ISOLATION_AND_AC3_OPTIONS_V1.0.md。额外UID companion仅D1实验，未批准产品分发。完整风险媒体流水线、P0隔离、标注质量/模型权利与平台能力仍未验收，不进入M0。
"""
appendix="""# D1 C04 设备追加批次 V1.0

candidateId：D1-20261005-C04；14+9=23项准备完成，手机/平板全部NOT_RUN。Coder未连接设备。旧C02手机、C03平板包/fixture/账本保留。负责人选定C04、tester核对设备/API/ABI/serial、现有包与数据用途、签名后才切换；未知数据不覆盖。禁止Gradle connected/UTP/managed路径。ARM64/API31+；unsigned release不安装；worker为不同普通UID的D1实验APK。

"""+table+"""

仅使用冻结复制件，不取可变build输出。签名见apk-audit.json与三份signing日志；按负责人批准方式安装，不擅自卸载或install-r，不混用旧测试结果。

## Fixture门禁

固定别名basic.mp4、subtitle.avi、subtitle.srt、large.mkv；精确源文件/hash在tools/transfer_fixtures.py的FIXTURES及media-inventory.json。SRT1445 cues、GB18030兼容GBK，源不重写，仅有界转UTF8。目的仅files/d1_c04_fixtures，不改旧候选目录。

transfer_fixtures.py默认PLAN_ONLY。未来实际复制需要--execute、--serial、--device-and-installed-c04-reviewed、--overwrite-c04-fixtures-reviewed、位于docs/tester的--result-file；这些参数必须对应tester已完成审查。--aliases仅固定别名。实际空间须至少请求文件总量+最大文件+256MiB；未知目录、空间不足、长度/SHA不符停止。32KiB shell-v2 raw帧传二进制，不用exec-in/tee；先.c04-part，源/stream/目标长度与SHA一致才提交，再验最终别名。工具不安装/卸载/管理ADB server/清理设备。实际2GiB+设备复制另留字节/hash证据，桌面6断言不替代。

## 顺序及通过条件

1. ordinary NORMAL先PASS，再pressure和故障。记录SOURCE_OPEN/BIND/CONNECTED/HELLO/RPC/BROKER、实际非宿主UID/PID、原cause；NORMAL/PRESSURE IOException均FAIL。fault模式必须实际进入且hits=1，并对应死亡/超时后实际排空；绑定失败不算命中。
2. normal host realEncoderOutput与companion isolatedActualEncodeAndReadyRecovery分别先PASS。失败保存完整ExportException cause/stack、muxer阶段、样本/字节；依赖项BLOCKED。T01 H264256×144/AAC，两轨独立非零样本、时长±150ms、严格PTS、全视频decoder/EOS/帧数/末PTS。规则反例不算真机恶意MP4 fuzz。
3. T02 write/flush指定stage、hits=1、ExportException精确D1_INJECTED_OUTPUT_WRITE/FLUSH；flush已有编码字节。validate须编码/fsync完成、非零字节且OUTPUT_VALIDATION_FAILED。错阶段、未命中、普通source/codec先失败均不PASS。READY响应丢失以同task QUERY收敛，abort不删READY。
4. 普通isolated负探针仅实际Hello/身份/租约后createEncoderByType失败、返回ISOLATED_CODEC_CAPABILITY_DENIED才通过；AVAILABLE、RELEASE_UNKNOWN或bind失败不算拒绝。保留cause。API探针不是GPU或产品隔离闭环；完整边界还需companion正常控制。
5. sample后cancel/crash/host death、另一task存活、dup-close、跨owner恢复保留C03门禁：真实样本后故障、确定死亡/Writer租约释放后才删未READY；未知lease隔离，不清除；另一task输出完整验真，不能假定同UID processgroup行为。
6. MP4对照AVI有/无SRT，prepare/post/enter/return、Extractor类sniff/read/offset、字幕decode/playerstate逐阶段记录。5秒主线程等待、30秒准备预算、五次seek及cue证据。WAV sniff不是根因。超时先独立撤销Source，再尝试main release；实际operations/consumers/failedClose和graphics未知分别记录，不能伪称全释放。
7. 自动播放静音，仅验结构/轨道/字幕。手动ProbeActivity volume=1，同机先MP4再MKV，人工记录听到/未听到；mime尤其AC3、supported/selected、decoder/session/sink/focus留证。不改系统音量，仅READY/音轨存在不算声音PASS；平板人工有声不替代手机。
8. 帧提取先MP4 2秒控制，再AVI10秒scaled；空帧回退同10秒原尺寸再有界缩放。metadata、耗时、异常与实际资源账本留证；两次空为FRAME_AT_REQUESTED_TIME_UNAVAILABLE。native超时不能硬中断就保留单槽与未释放事实。非空后才检测，不换0秒/空Bitmap；实际frame PTS UNKNOWN、质量NOT_RUN。

## 准备入口
"""
for name,items in methods.items():
 appendix+='\n### '+name+'\n\n| 方法 | C04执行 |\n| --- | --- |\n'+'\n'.join('| '+x+' | NOT_RUN |' for x in items)+'\n'
appendix+='\n每项记录候选hash、serial/API、fixture hash、阶段/cause、时间与PASS/FAIL/BLOCKED/NOT_RUN，写docs/tester自身目录。保留旧包/数据/输出，故障不自动清理；旧平板7/5/10不推导C04通过。\n'
for name,text in [('D1_DELIVERY_D1-20261005-C04.md',delivery),('D1_C04_DEVICE_APPENDIX_V1.0.md',appendix)]: (docs/name).write_text(text,encoding='utf-8')
print('written two reports', {n:len(v) for n,v in methods.items()})
