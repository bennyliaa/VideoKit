import collections, json, pathlib
BASE=pathlib.Path(__file__).resolve().parent
results=json.loads((BASE/'tablet-batch-results.json').read_text(encoding='utf-8'))
counts=collections.Counter(r['result'] for r in results)
notes={
'realEncoderOutput':'正常导出 codec/source 失败，code=1001；未完成输出解码门禁。',
'outputValidationCounterexamples':'12 个规则层反例及拒绝未缩放/未剪辑原始 MP4；不是恶意容器 decoder fuzz。',
'realPipelineImmediateCancel':'实际 Transformer 立即取消、输入释放及无 READY；不是编码中途取消。',
'writingJournalRecovery':'WRITING 账本重开并 abort；不是实际宿主死亡。',
'ordinaryIsolatedCodecDenialDoesNotReady':'start 即 WORKER_START_FAILED，未进入预期 codec/GPU 拒绝与恢复断言。',
'nativeLeaseSurvivesDuplicateDescriptorClose':'设备原生锁竞争、重复 FD 关闭不释放原锁及 abort 检查通过。',
'isolatedActualEncodeAndReadyRecovery':'companion 返回 EXPORT_ERROR_1001，未完成有效输出、READY 响应丢失与恢复断言。',
'playbackMp4':'5 个 Seek 位置、短播放及输入排空通过；cue_events=0，PSS 69815 KiB。',
'playbackAviSrt':'约 26 秒内完成播放、5 个 Seek、字幕轨选择/开关和输入排空；cue_events=4，PSS 83754 KiB。',
'playbackMkvAss':'播放、5 个 Seek、字幕轨选择/开关和输入排空通过；cue_events=0，PSS 78124 KiB。',
'isolatedWorkerDeathAndTimeout':'NORMAL 首项 IOException 导致 injected termination only 失败，后续 PRESSURE/EXIT/SIGSEGV/HANG 未执行。',
'offlinePlatformFaceFeasibility':'authorized frame decode 断言失败，返回帧为空，未调用后续检测。'}
rows=[]
for r in results:
    note=notes.get(r['method'],'前置 '+str(r['dependency'])+' 未通过；未执行，不计为故障恢复通过。')
    rows.append('| '+r['method']+' | '+r['result']+' | '+note+' | [日志](D1_TABLET_C03_EVIDENCE/'+r['log']+') |')
report='''# D1 平板 C03 测试报告 V1.0

日期：2026-10-05。测试员：本会话 tester。候选：D1-20261005-C03。

结论：TABLET_BATCH_BLOCKED，自动批次已结束；D1 未通过。22 个方法中 7 PASS、5 FAIL、10 BLOCKED。正常导出与 companion 编码前置失败，T02 精确注入、真实 sample 后取消/死亡、第二槽存活及跨 owner 恢复均未验证。人工声音/字幕观察未收到确认的项目保留 NOT_RUN。手机 C02 仍 WAITING_FOR_FIX_CANDIDATE。

## 设备与冻结门禁

仅操作平板 HA1Q6WXR，TB138FC / olivine，Android 12 API31，arm64-v8a，1536×2560，density320，sw768dp/xlarge。安装前 /data 可用 110127460 KiB；三个 com.videokit 包均不存在，无覆盖既有数据。手机 U4999DLBNRR89DOR 及模拟器未操作。

只用冻结目录 docs/coder/d1c03/artifacts/D1-20261005-C03 内产物；5 个 artifact、95 个 evidence 共 100 项 hash 匹配，ZIP 93 个源码文件匹配。三份 debug/test/worker 包同证书 SHA256 5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f，顺序安装均 Success，未使用 install-r。没有安装 unsigned release、运行 Gradle、修改产品源码或切换 C04。

| 包 | 安装后 UID | APK SHA256 |
| --- | ---: | --- |
| com.videokit.app | 10221 | efe83f6b27df9d268374008af038c68d545508cec13cb35e118ae973fc0e66ac |
| com.videokit.app.test | 10222 | 8b0f3f2a316f22395505782090533f4fc0f84ddd89227282f31fa5aec505466d |
| com.videokit.worker.spike | 10220 | 1bc6b4785884bf86d998e46f46856c3f55d787bfe1acf341d6b7e3ccf01e7503 |

[设备记录](D1_TABLET_C03_EVIDENCE/preflight.json)、[冻结核对](D1_TABLET_C03_EVIDENCE/freeze-hash-check.json)、三份 signing 日志见同证据目录。

## 素材与执行范围

只读电脑源，使用本次手机阶段验证的本机 ADB shell-v2 二进制传输工具，直接写授权 App 私有 files/d1_c03_fixtures。没有共享存储中转或上传。四份总计 3949857219 字节，源与设备 SHA256 均一致；不删除手机素材。

| 别名 | 字节 | SHA256 |
| --- | ---: | --- |
| basic.mp4 | 349102 | 720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9 |
| subtitle.avi | 736454656 | 3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f |
| subtitle.srt | 93550 | d3a44be0636d9ec4d5a2782d1a5d6ceb7141d7bf4f8df2f693d9850f867144bd |
| large.mkv | 3212959911 | 28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26 |

[传输和 hash](D1_TABLET_C03_EVIDENCE/fixture-hash-check.json)。逐方法单独 instrumentation，180～360 秒外部上限；本轮没有方法触发外部超时。FAIL 判定来自冻结方法断言，BLOCKED 方法未运行。自动批次电脑时间 11:26:58～11:28:14；设备日志时间与电脑有偏差，不将跨时钟差值解释为执行性能。

## 逐方法结果

| 方法 | 状态 | 范围及证据解释 | 日志 |
| --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

[完整结果和命令](D1_TABLET_C03_EVIDENCE/tablet-batch-results.json)、[控制台](D1_TABLET_C03_EVIDENCE/tablet-batch-console.log)。播放用例显式 setVolume(0)，没有实际音轨可听性或音画同步断言。三项播放 thermal=3，仅为快照，无持续性能或温控通过结论。

## 输出门禁与隔离释放

T01 的规则层反例通过；实际正常导出先发生 code1001 错误，因此 H264/AAC、256×144、3 秒输出、两轨非零样本、PTS、视频 decoder drain/帧数/EOS 及成功 READY 未通过真机验证。不能关闭完整 T01。

T02 的 write/flush/validate 未运行，没有 stage/hits=1 或正确 cause chain 的设备证据；READY 响应丢失也未运行。正常路径未命中故障不能计为注入 PASS。

companion 安装和绑定后有自身 UID10220 日志及 EXPORT_ERROR_1001，但没有有效样本/成功输出证明。普通 isolated start 失败；预期 codec 拒绝、SourceReleased、实际死亡和恢复断言未到达。两条失败路径最终释放未逐项证明，按未证实排空/quarantine 保留，不能因测试进程结束宣布释放。立即取消及三种播放的输入排空断言通过。原生 FD 锁检查通过，仅覆盖该方法实际执行的锁语义。

测试后私有 cache 中只有任务账本/lease/owner 文件，目录列表未见 MP4 输出；文件不存在不能替代锁或账本排空证据。保留全部任务材料，不清理。[cache 列表](D1_TABLET_C03_EVIDENCE/private-cache-after-batch.txt)、[私有素材列表](D1_TABLET_C03_EVIDENCE/private-state-after-batch.txt)。日志按本次 App/companion UID 采集，没有清空全局日志。

## 平板效果与手机缺陷复核

| 项目 | 平板结果 | 对手机结论的影响 |
| --- | --- | --- |
| MKV 测试页画面 | PASS，仅截图可见 READY 和片头图像 | 不证明声音、ASS 字形或同步 |
| MKV 声音、中文 ASS、字形和对白同步 | NOT_RUN，已在明确前台 MKV 页请求用户观察，待反馈 | 手机 MKV 无声仍未关闭；手机 MP4 有声音的用户对照不移作平板结果 |
| MP4 实际声音 | NOT_RUN | 自动静音播放不能替代人工 |
| AVI 中文 SRT 效果 | NOT_RUN；自动 cue_events=4 及轨道开关通过 | 平板没有复现手机 180 秒挂起，但不同设备/候选不能关闭手机缺陷 |
| 旋转、前后台、RTL、完整 UI | NOT_RUN | 未改变设备全局设置，技术验证 UI 不是产品验收 |
| 人脸检测/标注质量 | NOT_RUN，取帧前置 FAIL | 未生成可供质量判断的帧 |

[MKV 截图](D1_TABLET_C03_EVIDENCE/probe-mkv.png)、[前台 Activity](D1_TABLET_C03_EVIDENCE/probe-mkv-resumed.txt)、[只读音量信息](D1_TABLET_C03_EVIDENCE/music-volume-readonly.txt)。片头中文标识不是 ASS 字幕证据。

## 集中缺陷与后续回归

| ID / 严重度 | 复现与影响 | 修复后需验证 |
| --- | --- | --- |
| TABLET-C03-01 / 高 | realEncoderOutput 约4秒结束，codec/source code1001；companion 同为 EXPORT_ERROR_1001。对应日志有 ACodec dequeueBuffer NO_INIT(-19)，仅现象关联，根因尚不确定 | 分层记录 source/decoder/encoder/muxer 和完整错误链；先两条正常导出及完整输出 decoder 门禁，再所有 T02/恢复项 |
| TABLET-C03-02 / 高 | ordinaryIsolatedCodecDenialDoesNotReady 在 start 抛 WORKER_START_FAILED，没有进入预期拒绝路径 | 服务启动/绑定/协议原因及失败退出 drain；不得以任意 IOException 代替正确拒绝与释放 |
| TABLET-C03-03 / 高 | 旧 broker NORMAL 失败，injected termination only 断言；与手机缺陷同类现象 | 先 NORMAL 的真实 broker 读取，再 PRESSURE/EXIT/SIGSEGV/HANG、UID/PID、死亡与排空 |
| TABLET-C03-04 / 中 | offlinePlatformFaceFeasibility 取10秒 scaled frame 返回 null，authorized frame decode 失败 | 帧提取能力及稳定失败解释；再运行检测，使用标注数据验证质量 |

手机 PHONE-C02-01 的传输截断本轮经任务工具绕过，不代表原工具修复。PHONE-C02-02 的 AVI 挂起在平板本轮未复现，仍需手机修复候选补测。PHONE-C02-03 的 NORMAL 失败仍出现。PHONE-C02-04 的 MKV 无声待平板人工及手机修复回归。C02-T01/T02 均未完整关闭。

## 批次保留与未覆盖项

自动批次已结束，核心门禁阻断。三个授权包、四份私有素材与所有任务账本保留供审查；人工页仅在等待本次观察期间播放，结束停止本次 App，不卸载、不清数据、不更改用户全局设置。未触碰手机。C04 尚未整体交接，本轮不替换候选。

native OOM、满盘/权限、NAS不协作、12路并发、标注质量、模型权利与供应链未决项保持 NOT_RUN/BLOCKED。D1 未全量通过，不据限定 PASS 进入 M0。待完整修复候选集中回归，手机补测另安排。
'''
(BASE.parent/'D1_TABLET_TEST_REPORT_V1.0.md').write_text(report,encoding='utf-8')
print(dict(counts))
