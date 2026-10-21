"""Write C03 reports from actual audited APK identities and exact prepared test method names."""
from pathlib import Path
import json,sys,re
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c03';docs=root/'docs/coder';e=base/'evidence'
audit=json.loads((e/'apk-audit.json').read_text());rows=audit['apks'];table='| 文件 | 字节 | SHA-256 |\n| --- | ---: | --- |\n'+'\n'.join('| '+Path(r['path']).name+' | '+str(r['bytes'])+' | '+r['sha256']+' |' for r in rows)
methods={name:re.findall(r'@Test public void (\w+)\(', (base/'device/com/videokit/spike/c03'/name).read_text()) for name in ['C03DeviceTests.java','C03IsolatedDeviceTests.java']}
appendix='''# D1 C03 集中设备追加批次

日期：2026-10-05；candidateId：D1-20261005-C03；手机/平板全部 NOT_RUN。本轮 coder 无 ADB、安装、fixture 复制或 device 执行。负责人正在让 tester 独占手机测 C02；本追加批次只能在负责人结束该批并明确选择 C03 后执行。不得混入 C02 结果。

## 固定产物与安装门禁

复制产物目录：`docs/coder/d1c03/artifacts/D1-20261005-C03`。只能使用冻结复制件，不使用可变 app/build 输出。

'''+table+'''

实际证书 hash 见 `evidence/apk-audit.json` 与三份 signing 日志。App Debug、Test、worker-debug 已静态验证同一证书；Release unsigned 仅构建证据，不安装。worker 是额外普通应用 UID 的 APK，不是 isolatedProcess APK。先检查已授权设备的型号/API/ABI/空间及三个包的已存在状态和数据用途；确认 C02 数据、产物与恢复点的保留要求，未知数据不得覆盖。只有负责人明确批准切换测试候选后 tester 才安装三份同签名 debug APK，不擅自 install-r 或卸载旧包。ARM64/API31+；本 JNI 只有 arm64-v8a，不以 x86 模拟器代替。不得同时运行 Gradle UTP/managed/emulator-control；此工具链仍限制使用。

## Fixture 与源保护

新增 worker/recovery 批次只需 basic.mp4：349102 字节，SHA-256 `720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9`；取电脑原文件 `test_media/imgs_and_videos/videos/sample.mp4` 的只读副本，授权设备 App 私有目录 `files/d1_c03_fixtures/basic.mp4`。不要把 C02 fixture 目录改名、删除或当作 C03 未验证副本。复制前后核对字节/hash。

字幕/多源回归另需 subtitle.avi、subtitle.srt、large.mkv，原媒体 hash 见冻结 `media-inventory.json` 与 C02 请求，不修改 C02 请求。基础集合至少 1.5GB、大集合至少 5GB 是准备建议，先检查实际可用空间；不足即不复制并记相应 NOT_RUN。SRT 为 GB18030 兼容 GBK、1445 cues；源不重写，仅有界转 UTF8。

`tools/device_setup.py` 现在只打印已验 hash 的计划，不执行 ADB、安装或清理。实际命令、序列号、包数据授权和空间门禁由 tester 记录，不能只凭一个 --authorized 开关覆盖未知数据。

## 成组回归顺序与通过条件

1. 正常 `realEncoderOutput` 先建立真实 codec/source 前置能力，再执行 T01 反例与 T02 三阶段注入、READY 响应丢失。正常路径强制 H264/AAC、256×144、3 秒剪辑、两轨独立非零有效样本、各轨时长/PTS 和全视频 decoder drain。解码帧计数必须等于视频样本数，EOS 与末 PTS 验证；不是字形/遮罩或画面正确性目测。`outputValidationCounterexamples` 执行 12 个纯规则反例并拒绝原始未缩放/未剪辑 MP4。空视频＋有效音频等 12 个反例是规则层测试，未制造并真机运行所有恶意 MP4；不得写成 decoder fuzz 覆盖。
2. T02 write/flush 只有指定 hitStage、hits=1 和 ExportException 的 `D1_INJECTED_OUTPUT_WRITE/FLUSH` cause chain 才能 PASS；flush 必须已有编码字节。validate 必须编码完成、fsync/字节非零，再 hits=1，返回 OUTPUT_VALIDATION_FAILED。任何故障前 codec/source 失败、错阶段、缺错误链、未命中或错误 READY 均 FAIL；前置设备能力不足另记录 BLOCKED，不能把无关失败作为注入 PASS。保留阶段、次数、错误链的脱敏记录。
3. ordinary isolated Service 拒绝路径探针：预期实际失败、无 READY、实际 Source drain/abort；若平台意外成功，不把它静默认作架构通过，保留 codec/GPU 与 SELinux 现象由负责人复查。
4. companion 实际编码：确认异 UID/异 PID、broker 有读取字节及实际 H264 视频 sample progress；验证完成、worker Binder death、SourceReleased、lease 恢复、同 task READY_UNKNOWN 查询及 token 一致。七秒输出同样有实际 decoder 门禁。
5. 在实际视频 sample 已写出的 gate 后依次取消、自己的 worker EXIT、自己的 worker SIGSEGV；实际死亡、账本排空后同 task abort，不完整输出无 READY。不发送外部 PID，不 kill 设备或其他 App。
6. 两任务分别在固定 slot 编码并报告真实 sample，再让第一个自身 SIGSEGV；第二任务必须仍活着，RESUME 后通过输出验证/READY。共享 companion UID 的 Android 进程组行为尚未实测，若另一任务被带走则 FAIL，不以之后重建新任务代替并行存活。
7. 用本 App 私有 RecoveryHostService（本 App UID、独立 PID）在实际 sample 后杀其自身；instrumentation 宿主继续，新 owner 等实际 lease 释放后同 task abort。再测试 helper 完成 durable READY 后、返回 token 前自杀；新 owner 查询原 task 得同 READY/token。Windows 实验不可替代此批。
8. 保留 C02 多源/字幕、Seek、界面观察回归，按手机和平板分别记录。实际中文显示/字幕同步/ASS、音画、旋转/后台和输出内容需真实观察，不由 cue/sample 计数推断。剩余 native OOM、NAS 不协作、权限/满盘等未新增完整入口，保持 NOT_RUN/BLOCKED。

## 精确测试入口

'''
for name,names in methods.items():appendix+='\n### '+name+'\n\n'+'\n'.join('- `'+n+'`：手机 NOT_RUN；平板 NOT_RUN。' for n in names)+'\n'
appendix+='''
每台设备保存 candidate/hash/证书/型号/API/ABI、方法结果、真实处理 proof、Binder death 与 generation Source query、输出 task 状态、源 hash、注入阶段/命中/错误链和人工现象。失败退出仍检查账本；未真正排空记 quarantine，不宣布释放。仅根据负责人保留决定清理本次明确登记的 C03 私有 fixture/临时 task，成功 READY 输出留待核查；不得删除 C02 恢复材料或用户数据。
'''
(docs/'D1_C03_DEVICE_APPENDIX_V1.0.md').write_text(appendix,encoding='utf-8')
delivery='''# D1 C03 交付报告

日期：2026-10-05；candidateId：D1-20261005-C03；状态：**BLOCKED / NOT_READY_FOR_FORMAL_ACCEPTANCE**。已完成本轮可做的实现、集中本机验证与打包；不是 D1、M0 或全部 P0 通过。手机由 tester 独占 C02，coder 本轮不操作设备、不覆盖冻结 C01/C02。

## 完成矩阵

| 要求 | 本轮结果 | 验证与剩余 |
| --- | --- | --- |
| 实际媒体 worker/broker | 实现/编译完成；可行性 BLOCKED | 实际 Media3 读取、解析、缩放重编码及输出重开/解码已接入异 UID companion；普通 isolated Service 权限限制另备拒绝探针。extra APK 产品决定与实际 codec/GPU/FD 运行 NOT_RUN；宿主播放/平台人脸对照入口仍在宿主，未声称全管线迁移 |
| 实际编码中取消、死亡、跨 owner | 入口成组完成 | gate 只在实际 H264 sample 成功写入后报告；自身 worker EXIT/SIGSEGV、私有 host helper 自杀、同 task READY 响应丢失/查询及并行第二槽存活测试已编译；Android 全部 NOT_RUN |
| close 重试/查询、有界非协作 | 局部 PASS | 新 24 条桌面实验含双 handle 独立恢复、每 handle 初次加最多两次显式 retry、永久失败不释放、2 IO+16 queue 耗尽、迟到实际排空、真实 test-owned JVM host/worker kill 与跨 owner 恢复。不是 NAS 硬终止或 Android FD/Binder durability 证明 |
| 16 工具漏洞处置 | 明确限制使用；未修补 | 复用 346 匹配、展开 47 advisory；禁止 UTP/远程 emulator-control，限定本地 offline 可信输入；lint 实际运行披露。保护探针预期拒绝 PASS，不盲覆盖 AGP 内部版本。风险残留与支持升级待审核 |
| 合法人脸/跟踪及标注 | 研究/规范完成，质量 BLOCKED | 平台与自有模板仅对照，ML Kit 因条款/指标/离线准入待审核，Zoo 权重权利未闭合，未集成新权重。10 clip/1000 连续事件帧最少标注申请与格式完成，真实样本/标注未取得 |
| M0 边界 | 清单完成；未冻结 M0 | 区分已证语义、设备/平台未测和关键隔离替代产品决定；保留全部正式 P0 门禁 |
| C02-T01 高风险验证缺陷 | 源码修复＋12 规则断言 PASS | 两轨单独非空、准确 H264/AAC/256×144/预设时长/严格 PTS、实际 CPU decoder 全样本计数/EOS/末 PTS 才 ready；Android 实际验证与特殊 MP4 对抗运行 NOT_RUN |
| C02-T02 故障假 PASS | 源码修复/入口编译 | write/flush 检查 stage/hits=1/指定 cause chain；validate 需完整编码/fsync 后命中、准确 OUTPUT_VALIDATION_FAILED。任意无关 codec/source 错误不再 PASS；真机执行 NOT_RUN |

## 构建与复制产物

AGP 9.3.3、Kotlin 2.2.10、Media3 1.9.3、compileSdk36.1/min31/target36；本地已安装 NDK30.0.16248370，own JNI 仅 ARM64/API31、16KiB page alignment。`c03-prevalidation-build.log` 为集中 Debug/Test/worker/Release/unit-test 严格 offline 构建成功（53s）；最终两项验证补强的 `c03-final-build.log` 为 Debug/Test/worker 严格 offline 集中成功。此前源码目录 API/OsConstants 失败日志保留，不掩盖失败记录。Gradle unit-test 任务成功不代表有产品 Android 单元覆盖；本轮有效局部证明为 Java probes。

复制产物：`docs/coder/d1c03/artifacts/D1-20261005-C03`。

'''+table+'''

四 APK 无 INTERNET 权限、无按已知名字命中的媒体、无 .onnx/.tflite/.pth 条目；静态命名扫描不能排除改名内容或代替动态隐私证明。Release 仍示例 unsigned、优化关闭、无 C03 技术代码，不是 Kit AAR/产品发布。三份 debug/test/worker 的实际证书 SHA-256：`'''+next(r['certificate_sha256'] for r in rows if 'certificate_sha256' in r)+'''`。worker DEX 不含宿主 fixture/broker/UI/helper 类；包含实际 Transformer 及 FD 输出验证。宿主和 worker APK 内 own JNI hash 见 apk-audit.json，AGP stripped binary 与未 strip 的 native-build.json hash不同，不能混用。

源码 ZIP `D1-20261005-C03-source.zip`、逐文件 source-manifest 与递归证据/artifact 的字节/hash由 [freeze-summary](d1c03/evidence/freeze-summary.json)统一记录；没有 Git commit。ZIP 排除全部媒体、C01/C02 冻结材料、tester 可变报告、本机缓存与 build 输出；包含 C03 代码/配置/工具/报告与自己的 JNI 源/ARM64 库。最终一致性检查与 ZIP 内容 hash 需一并核对，不使用 app/build 浮动产物。

## 实际隔离、所有权与回收

ordinary isolated UID 无已证硬件 codec/GPU 权限；依据与风险见 [M0 边界](D1_C03_M0_FREEZE_SCOPE_V1.0.md)。本轮具体替代不是仅方案文稿：独立 `:d1worker` APK 已编译，正常应用 UID 与宿主不同，无网络/存储/相机/麦克风权限；signature permission、精确 host package UID、broker 与 callback 的 UID/PID/task/epoch 全部校验，不提供同 UID downgrade。

host 只授 opaque source token 的有界 READ IPC，不传源 path/输入 FD/凭据。每任务 max4 RPC、8 active handles、64 retained handles、64KiB read；2 个 worker 槽、每宿主最多2个 active/quarantined owners，不无限创建新线程池。provider 永久不协作或 close 永久失败仍占有账本和 quarantine，明确资源耗尽，不以 timeout 清零。

output/readonly lease FD 经 Binder 逐任务授予；host/worker 都使用自有 JNI **flock open-file-description**，不是 Android FileChannel 的 POSIX lock。worker 在打开输出 writer、fsync dup、validation dup 全部关闭之前保留共享 lease；close 不确定保留到真实进程死亡。host exclusive fencing/owner lease、task UUID/epoch、journal+文件/目录 fsync控制同 task grant/abort/ready。worker 只内部管理 Media3 的 codec/GPU Surface，未跨进程传宿主预览 Surface；验证 decoder 用 buffer 输出、无 Surface。actual FD/Surface 生命周期与设备 persistence尚未运行。

取消以 task/epoch 限定，未发送 grant 的竞态由原子 grantPhase 阻止；已授 FD 无法靠撤销 broker强行撤销，等待自己的 worker 实际 death与exclusive lease后清理。flock是协作恢复，不宣称恶意 worker FD强撤销/RCE封闭。两个槽共享 companion UID，native crash可能受平台进程组策略影响，专门并行 test NOT_RUN。helper 与实际主 App同UID不同PID用于杀自己的测试宿主，主 instrumentation保持；不是任意外部PID kill。

READY 之前要求 worker 验证成功、真实 death与exclusive lease；响应丢失只同task查询，READY不可改abort、不当 COMMITTED。SourceReleased 是 retired/消费者/actual operation/failed closes 的独立事实，不代表 output FD/Surface/全局 NAS 生命周期已结束；API31+锁/死亡/权限具体证据由追加批次取得。

## 本机证据与交接

`contract-probe.log`：47 assertions / 0 failures；`recovery-probe.log`：24 / 0（自己创建的实际 Windows/JVM processes及锁；目录 fsync mocked）；`validation-probe.log`：12 / 0。新增反例包括空视频＋有效音频、错误音轨、尺寸、时长、负/逆序 PTS、空样本/截断视频；规则 PASS不等于已在 Android 构造、解码所有畸形 MP4。传统五合成结果只复制 C02 冻结日志并记录 provenance。

`native-build.json` / readelf/symbols：自己的 JNI 编译/ELF PASS，Android syscall NOT_RUN。`tool-guard-probe.log`：expected configuration rejection，不是 build FAIL被当功能PASS。`apk-audit.json`：静态包/证书审计。`baseline-reuse.json`：worker95、host346、新 Maven坐标0；许可证和 NOTICE复用精确版本，最终商用/分发review仍未闭合。`integrity-check.json`：120条C01/C02 immutable检查、45媒体只读hash均PASS。

新增设备批次见 [C03 appendix](D1_C03_DEVICE_APPENDIX_V1.0.md)，13个旧路径/T01/T02回归方法与9个新隔离/恢复方法逐项手机/平板NOT_RUN。先正常编码，再三个故障；缺命中不得PASS。仅负责人选择新candidate后一次性交tester；本轮未自行发消息派测、安装、覆盖C02或执行设备命令。

工具风险决定：[security decision](D1_C03_TOOL_SECURITY_DECISION_V1.0.md)；模型/样本：[tracking labels](D1_C03_TRACKING_SAMPLES_AND_LABELS_V1.0.md)。Apple/Windows产品能力、NAS/满盘/权限/真实OOM、生产槽调度、完整人脸/媒体迁移、正式权重和最终保护质量仍按范围NOT_RUN/BLOCKED，不以本机通过清除P0。

负责人需结合tester C02手机报告、C03补测与companion分发决定判断D1退出。本交付完成授权的本机工作与准确候选冻结，不进入M0、不发布产品。
'''
(docs/'D1_DELIVERY_D1-20261005-C03.md').write_text(delivery,encoding='utf-8');print('Wrote C03 delivery and device appendix; prepared', {k:len(v) for k,v in methods.items()})
