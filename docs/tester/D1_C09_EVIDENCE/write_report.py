import collections,datetime,json,pathlib,re
B=pathlib.Path(__file__).resolve().parent;R=B.parents[2]
phone=json.loads((B/'phone/results.json').read_text());tablet=json.loads((B/'tablet/results.json').read_text())
assert len(phone)==len(tablet)==32
assert len({r['method'] for r in phone})==len({r['method'] for r in tablet})==32
def counts(rs,group=None):return dict(collections.Counter(r['result'] for r in rs if group is None or r['group']==group))
summary={d:{g:counts(rs,g) for g in ['cpu','host','legacy']} for d,rs in [('phone',phone),('tablet',tablet)]}
(B/'result-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
cpu=[r['method'] for r in phone if r['group']=='cpu'];host=[r['method'] for r in phone if r['group']=='host'];legacy=[r['method'] for r in phone if r['group']=='legacy']
def table(methods):
 rows=['| 方法 | 手机 | 平板 |','| --- | --- | --- |']
 for method in methods:
  cells=[]
  for device,rs in [('phone',phone),('tablet',tablet)]:
   r=next(r for r in rs if r['method']==method);label=r['result']
   if device=='phone' and r['group']=='cpu' and label=='FAIL':label+='（环境）'
   cells.append('['+label+'](D1_C09_EVIDENCE/'+device+'/'+r['log']+')')
  rows.append('| '+method+' | '+' | '.join(cells)+' |')
 return '\n'.join(rows)
frameproof={}
for device,uid in [('phone','10262'),('tablet','10221')]:
 for method in cpu:
  f=B/device/(method+'-uid'+uid+'.log')
  if f.exists():
   lines=[line for line in f.read_text(encoding='utf-8',errors='replace').splitlines() if 'stage=CPU_FRAME ' in line or 'stage=CPU_LEDGER ' in line]
   if lines:frameproof[device+'/'+method]=lines
(B/'cpu-frame-and-ledger-proof.json').write_text(json.dumps(frameproof,ensure_ascii=False,indent=2),encoding='utf-8')
report='''# D1 C09 手机和平板集中测试报告 V1.0

日期：2026-10-16。冻结候选D1-20261016-C09。依据D1_C09_TESTER_REQUIREMENTS正式整包交接及C09_DEVICE_APPENDIX，17CPU＋7host＋8legacy，每设备32计划项。

**当前结论：C09_NOT_PASSED。平板批次已完成，16 PASS／4 FAIL／12 BLOCKED。手机host七项通过，但测试App被系统禁用、ADB启用被Android拒绝，保持WAITING_FOR_USER_ENABLE：当前8 PASS／4环境FAIL／20 BLOCKED，手机CPU/legacy尚未完成可用环境下的整批复验。本报告不宣布两设备全部通过或手机批次完全结束。**

平板已获得真实FFmpeg CPU帧，但正常/伪协议方法的停止阶段触发CPU_OWNER，death和slot回收门禁失败；相关依赖不能计通过。手机四项环境失败不归作CPU解码器故障。历史ordinary UNKNOWN与C07 signal差异不重写，D1仍未通过，不进入M0。

## 1. 冻结与Debug准入复核

最终freeze-summary SHA256 `cdc48afed4f10e38fca5ad5efaf3fb4602947acc2166caa1f08d255bb89ce4fa`；源码ZIP `7551a6bb0fc94cf0d66a65b4b027925ec85c17e19d03a796b072eaaa31e3af28`。5产物、112证据、10051源码/ZIP条目匹配，归档模式核验，不把浮动根工作树作候选。纯规则215项来自冻结本机回执，本轮未执行Gradle或重复运行这些规则，不计入设备PASS。

| 产物 | SHA256 | 本轮用途 |
| --- | --- | --- |
| app-debug.apk | 55e5bea436b2195517af72c991c9f36ede75e6da390c450bb65ae9ad2106a9f0 | 两设备主包，实际已安装主APK另拉回核验一致 |
| app-debug-androidTest.apk | 2701b39a780174c76235db86262583204f0f9ac27b7ffd513ba32574a4a0c673 | 两设备测试包 |
| worker-debug.apk | e27a4d77d51e4fdc59eb56234b383c9b845e33f5d40ac45b4e9b0113627fc0bd | 仅平板legacy组；手机legacy等待，未安装 |
| app-release-unsigned.apk | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e | 仅静态对照，无安装 |

三debug包独立签名检查同证书SHA256 `5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f`。C09 Debug实验准入检查通过，不是产品/商店/专利或SDK发行准入。

FFmpeg8.0.3：266对象、608源/生成依赖逐项hash核对；588 LGPL、10生成、4上游默认薄文件、3 IJG、ISC/Zlib/宽松显式头各1项。H263为必要传递依赖且保留注册，静态原生输入门禁仅AVI/MPEG4、MOV-family/H264；动态H263拒绝测试因正常方法最终释放FAIL而BLOCKED，不能据静态审查宣称设备拒绝通过。object-map的scope文字有一处沿用267，实际数组/最终准入均266，按实际计数记录。

8份官方补丁材料与身份核对，6项反向check成功回执保留；IAMF两项反向check因上下文变化失败，独立检查同一scalable_channel_layout_config内两项新增拒绝条件确实存在，不把反向check失败写成成功。五CVE累计覆盖不等于穷尽漏洞或fuzz通过。APK16个native条目（含继承库）内容/ZIP_STORED/16384偏移与ELF LOAD对齐复核；12份license/特别NOTICE逐字节匹配。独立检查工具初版未区分继承ELF32，修正后重新通过；不是候选ELF缺陷。GPG采用冻结签名回执，未重新运行GPG。

[冻结核验](D1_C09_EVIDENCE/freeze-check.json)、[独立G01核验](D1_C09_EVIDENCE/admission-check.json)。本机ADB在受限执行环境启动/枚举失败，所需权限执行环境下固定SDK路径成功识别两台；未盲kill全局ADB或其他项目服务，没有把连接问题说成设备未授权。

## 2. 本次设备与更新、素材、预算

| 项目 | 手机 | 平板 |
| --- | --- | --- |
| 本次serial/型号 | U4999DLBNRR89DOR / PDYM20 | HA1Q6WXR / TB138FC |
| Android/API/ABI | Android12 / 31 / arm64-v8a | Android12 / 31 / arm64-v8a |
| 实际页面大小 | 4096 | 4096 |
| 宿主/测试UID | 10262 / 10263 | 10221 / 10222 |
| 初始已装候选 | C02主/测试包hash匹配；无companion | C07主/测试包hash匹配，旧worker另核验后更新 |
| 本轮更新 | 主/测试同签名install-r成功 | 主/测试成功；CPU组后才更新legacy worker，UID10220 |
| App启用状态 | enabled=2，lastDisabledCaller=com.oplus.athena，等待人工启用；不推断具体系统冻结策略 | enabled=0，可用，未更改 |
| 旧包与恢复材料 | APK＋cache-before-c09.tar＋包路径/dumpsys均保留 | 同左；旧C06/C07八个capture文件/账本SHA均未变 |
| 新CPU fixture | 两文件736803758字节 | 两文件736803758字节 |
| 终态C09输出/账本预算 | 961246字节、6任务记录 | 2735217字节、15任务记录 |
| 本轮日志预算检查 | 504254字节 | 522426字节 |

实际源/目的私有文件均核对长度/SHA后复制到全新files/d1_c09_fixtures；只含basic.mp4和subtitle.avi。原源/旧目录不改，结束hash仍匹配。每设备新fixture、32MiB日志、32项/8MiB旧回归输出预算均未超限，没有CPU持久帧、增加capture或自动清理。4KiB页面成功不能当16KiB页设备实测。

先手机CPU及host；手机环境等待后，根据负责人安排串行转平板CPU/host/legacy，没有设备并发或与Gradle争用。CPU组只用主/测试包，直接同APK CpuIsolatedService；平板旧companion保留但CPU未启动它，legacy另列，不能以legacy的不同UID进程代替CPU证据。

[手机前置](D1_C09_EVIDENCE/phone/preflight.json)、[平板前置](D1_C09_EVIDENCE/tablet/preflight.json)、[手机素材](D1_C09_EVIDENCE/phone/fixtures.json)、[平板素材](D1_C09_EVIDENCE/tablet/fixtures.json)、[手机预算及保留](D1_C09_EVIDENCE/phone/output-budget-final.json)、[平板预算及旧capture](D1_C09_EVIDENCE/tablet/output-budget-final.json)。

## 3. 分设备、分组结果

| 组 | 手机 | 平板 |
| --- | --- | --- |
| CPU 17方法 | 1 PASS、4环境FAIL、12 BLOCKED | 1 PASS、4 FAIL、12 BLOCKED |
| host 7方法 | 7 PASS | 7 PASS |
| legacy 8方法 | 8 BLOCKED（App环境） | 8 PASS |

CPU方法整体正常控制须含最后死亡/源/slot门禁才PASS；平板虽然已经加载native并得到帧，正常方法最终FAIL仍阻断依赖。独立未知/空长度构造及协议反例照常安排；不让负例因为任意绑定/解码异常就计PASS。各方法一次有界执行；手机环境修正未成功的误调度单独披露，不作为有效重试。所有本轮有效方法没有触发外部180～360秒超时。

### CPU 17方法

'''+table(cpu)+'''

伪epoch与claimedIdentity在同一方法内循环；平板首分支finally已FAIL，后续claimedIdentity分支不能声称实际完成。配额、尺寸预分配拒绝、H263动态拒绝、seek、新epoch、实际sample后取消/HANG/自身SIGSEGV/第二CPU槽等因正常最终门禁FAIL而未执行，保持BLOCKED。唯一CPU PASS是未知/空长度的构造拒绝及实际close/账本核对，不代表nativeCPU管线通过。

### host安全回归

'''+table(host)+'''

正式H264/AAC双轨非零样本、3秒预设、PTS/full视频decode及T02精确stage/hits/cause在当前方法范围通过。规则反例不等于真机恶意容器fuzz。手机App禁用时instrumentation内这些独立host方法仍能运行，不能据其PASS推断Service可绑定。

### legacy（额外worker实验组）

'''+table(legacy)+'''

legacy PASS仅指冻结方法断言，包括真实sample、death/source/Writer lease/第二槽/跨owner等；不是CPU单APK路径，也不是所有原始signal已经独立证明。ordinary UNKNOWN及C07旧broker signal差异方法本轮NOT_SCHEDULED，历史FAIL不改。其他未派测编译方法、播放/声音人工效果也不能计入32项通过数。

## 4. 平板实际帧与资源事实

| 实际控制 | MP4/H264 | AVI/MPEG4 |
| --- | --- | --- |
| worker PID/isolated UID | 20145 / 99028 | 20217 / 99029 |
| 目标时间 | 2000000us | 10000000us |
| 返回换算PTS | 2000000us | 10010040us |
| raw/time_base | 24576 / (1/12288) | 300 / (83417/2500000) |
| best_effort | 0，原生frame pts分支 | 1，明确为FFmpeg best_effort分支，不能冒充原始精确PTS |
| payload | RGBA256×144，147456字节 | 同左 |
| allocator peak/current | 2662598 / 2662598字节 | 15179327 / 11707363字节 |
| sampled peak RSS | 129024 KiB | 172260 KiB |
| 最后native阶段 | 5（真实帧归一化） | 5 |
| 最后源/死亡/slot | source=true，death=false，slot=false | 同左 |

同APK绑定、实际不同UID/PID、FFmpeg8.0.3预算回调、native阶段1～5和CPU_FRAME均有证据。源码调用真实avcodec_send_packet/receive_frame及sws_scale；PTS来自frame->pts或显式best_effort_timestamp，不是直接返回请求时间。宿主有界副本/换算路径存在，但本轮没有独立可信解码器逐帧像素/时间对照、全面B帧/EOS/精确PTS质量验收，不能扩展结论。

两正常方法仍FAIL：stopAndAwait等待后actual_death=false、slot_released=false，源operations/consumers/failed_closes均0、source_released=true。后续instrumentation进程结束时系统记录isolated not needed而回收进程，不是该API已可靠取消或按时释放的证明，也不将末尾ps为空改成PASS。CPU没有READY或输出token，无文件不是释放证明。

[当前帧与账本汇总](D1_C09_EVIDENCE/cpu-frame-and-ledger-proof.json)、[MP4宿主证据](D1_C09_EVIDENCE/tablet/cpuMp4H264ActualPtsFrame-uid10221.log)、[MP4 worker证据](D1_C09_EVIDENCE/tablet/cpuMp4H264ActualPtsFrame-isolated-uid99028.log)、[AVI宿主证据](D1_C09_EVIDENCE/tablet/cpuAviMpeg4ActualPtsFrame-uid10221.log)、[AVI worker证据](D1_C09_EVIDENCE/tablet/cpuAviMpeg4ActualPtsFrame-isolated-uid99029.log)。

## 5. 集中缺陷、环境阻断与测试过程偏差

| ID / 严重度 | 复现、证据和影响 | 修复后需一次整包验证 |
| --- | --- | --- |
| C09-T01 / 阻断 | 平板正常MP4/AVI已有真实帧，STOP时worker日志SecurityException CPU_OWNER；最终death=false/slot=false。客户端sendStop用FLAG_ONEWAY，service owner按同步HELLO保存的UID/PID严格比较，异步调用不提供PID，高置信协议不兼容候选 | 保持UID/task/epoch/Binder认证强度，采用能正确认证的有界停止协议；不能仅删除PID校验。先正常解码和真实释放，再配额/反例/取消/HANG/CPU SIGSEGV/第二槽整组 |
| C09-T02 / 高 | 多方法finally的released断言覆盖原始start/功能异常；onServiceConnected又将原cause变成CPU_BIND_IDENTITY_FAILED。手机仅看最终断言无法看到Service not found，需系统诊断才定位 | 同时保留脱敏原始阶段/原因、最终death/source/slot及suppressed清理错误；不放宽资源断言，也不把诊断增加当功能修复 |
| C09-ENV01 / 手机环境 | 实际包hash正确但enabled=2；系统Unable to start service … not found，pid/uid=-1/native_stage0，无CPU_FRAME。pm enable返回Android SecurityException Shell cannot change component state；状态未变 | 用户在手机解除该App禁用/冻结后有界确认状态，再继续原手机批次。不是重新请求测试授权；不卸载/清数据、不绕过系统安全限制、不把此当CPU解码失败 |

C09-T01证据分级：运行日志已确认CPU_OWNER与失败最终账本；冻结源码已确认单向STOP和严格caller PID比较。[Android12 Binder源码](https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/android-12.0.0_r1/core/java/android/os/Binder.java)说明oneway不提供caller PID。尚未记录拒绝瞬间的实际caller PID/UID，故不把候选写成唯一根因定论。未修改包/源码/断言、未重跑平板求偶然PASS。[调用端](D1_C09_EVIDENCE/CpuTaskClient.java)、[服务端](D1_C09_EVIDENCE/CpuIsolatedService.java)、[当前系统事件](D1_C09_EVIDENCE/tablet/cpu-system-bind-diagnostic.log)。

手机过程披露：首次设备前置没有及时将App enabled=2识别为服务测试阻断，执行了四个会失败的CPU方法；完整原始结果/log保存在environment-disabled-attempt。随后尝试可逆启用该App，Android拒绝；串行调度未正确在失败退出后停止，额外触发一个MP4控制及AVI开始，已中止本机调度并归档于environment-enable-refused-attempt，后者没有完整收回结果，不猜测通过。没有将它们作为“环境已修正”的重跑或覆盖原失败；用户已获告知，测试辅助调度新增包状态前置与失败退出门槛。本项目源码/冻结包未改。这是tester过程偏差，与C09产品缺陷分开。

当前手机仍WAITING_FOR_USER_ENABLE；未成功修改启用状态，无恢复命令可执行，也没有为了取得结果绕过限制。host七项原PASS保留，legacy未启动/未安装worker。手机独立证据不因平板能解码而升级。原始App信号与外部匹配crash继续分栏；本次CPU故障依赖BLOCKED，没有CPU SIGSEGV原始crash可声称闭合。

## 6. 设计与开源框架追踪

| 设计/计划 | 当前真实版本与调用/证据 | 必要自有胶水 | 偏差及负责人决定/未证边界 |
| --- | --- | --- | --- |
| SYSTEM_ARCHITECTURE / Flutter正式App | C09仍Android Debug测试harness，release对照未变 | 测试入口 | 有限D1实验授权，不以Compose测试骨架替代Flutter正式App；正式UI未验收 |
| 独立Kit/AAR、多宿主 | 当前同APK CpuIsolatedService真实进程/manifest静态证据；非独立Kit产物 | task/epoch、source/budget/错误及资源账本 | 单APK CPU实验不等于AAR/多宿主准入，产品分发未交付 |
| Media3薄适配及正式输出 | 锁定1.9.3继承，host7项两设备PASS，legacy8项平板PASS | Source/Sink、验证和READY事务 | 默认正式后端未被CPU实验替换；T01/T02不降低 |
| OPEN_SOURCE许可计划 / 已批准CPU方案A | 官方FFmpeg8.0.3、真实decoder阶段和avcodec_receive_frame/sws_scale，实际库/许可已核对 | opaque AVIO/JNI、帧协议、malloc-prefix配额、isolated Service | 经明确D1 Debug实验决定引入；没有自造解码器替代开源框架，产品商店/专利仍未批准，系统显示编码等未由本批证明 |
| OpenCV/ONNX及模型、跟踪/遮罩 | 本批没有新模型/权重或推理实现 | 无假模型/伪检测结果 | 人脸/物体质量、图片/字幕完整危险链等未实现能力不因视频帧实验关闭 |

设计依据SYSTEM_ARCHITECTURE、OPEN_SOURCE_AND_LICENSE_PLAN、OPEN_SOURCE_FRAMEWORKS_AND_DEVELOPMENT_EFFORT_ESTIMATE与C09明确实验决定；其冻结输入身份及设计映射已有交付证据。本轮独立核查实际CPU和Media3代码/库/运行路径，不仅复述coder方案；没有将研究提案当设备PASS。

## 7. 结束、保留与待续

平板当前32计划项已结束，存在阻断缺陷；手机只完成当前可执行项，人工环境前置仍待解除。两设备旧APK、cache前/后原字节备份、全部源fixture/旧capture/账本/成功输出均保留，源hash不变，预算未超限。没有主动kill测试worker或force-stop制造释放，没有卸载/清数据；末尾进程快照不替代方法finally资源证明。

CPU单APK、host、legacy、冻结215纯规则、App历史退出/外部raw、人工效果严格分栏。未派测的声音/字幕/旋转、Windows传输工具、精确PTS/效果质量、模型权利、完整Kit/Flutter/跨平台/NAS/全P0与发行仍未闭合。旧C07 ordinary UNKNOWN和signal FAIL保留。当前汇总见result-summary.json，手机环境解除后的原批次续测应更新本报告且保留全部尝试记录，不自动换候选或开启新开发批次。D1仍未通过。
'''
(B.parent/'D1_C09_TEST_REPORT_V1.0.md').write_text(report,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
