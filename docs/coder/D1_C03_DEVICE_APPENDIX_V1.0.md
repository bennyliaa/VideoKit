# D1 C03 集中设备追加批次

日期：2026-10-05；candidateId：D1-20261005-C03；手机/平板全部 NOT_RUN。本轮 coder 无 ADB、安装、fixture 复制或 device 执行。负责人正在让 tester 独占手机测 C02；本追加批次只能在负责人结束该批并明确选择 C03 后执行。不得混入 C02 结果。

## 固定产物与安装门禁

复制产物目录：`docs/coder/d1c03/artifacts/D1-20261005-C03`。只能使用冻结复制件，不使用可变 app/build 输出。

| 文件 | 字节 | SHA-256 |
| --- | ---: | --- |
| app-debug.apk | 40623215 | efe83f6b27df9d268374008af038c68d545508cec13cb35e118ae973fc0e66ac |
| app-debug-androidTest.apk | 2308763 | 8b0f3f2a316f22395505782090533f4fc0f84ddd89227282f31fa5aec505466d |
| app-release-unsigned.apk | 21607782 | 71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e |
| worker-debug.apk | 17077580 | 1bc6b4785884bf86d998e46f46856c3f55d787bfe1acf341d6b7e3ccf01e7503 |

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


### C03DeviceTests.java

- `playbackMp4`：手机 NOT_RUN；平板 NOT_RUN。
- `playbackAviSrt`：手机 NOT_RUN；平板 NOT_RUN。
- `playbackMkvAss`：手机 NOT_RUN；平板 NOT_RUN。
- `realEncoderOutput`：手机 NOT_RUN；平板 NOT_RUN。
- `outputValidationCounterexamples`：手机 NOT_RUN；平板 NOT_RUN。
- `exportReadyResponseLoss`：手机 NOT_RUN；平板 NOT_RUN。
- `exportWriteFault`：手机 NOT_RUN；平板 NOT_RUN。
- `exportFlushFault`：手机 NOT_RUN；平板 NOT_RUN。
- `exportValidationFault`：手机 NOT_RUN；平板 NOT_RUN。
- `realPipelineImmediateCancel`：手机 NOT_RUN；平板 NOT_RUN。
- `writingJournalRecovery`：手机 NOT_RUN；平板 NOT_RUN。
- `isolatedWorkerDeathAndTimeout`：手机 NOT_RUN；平板 NOT_RUN。
- `offlinePlatformFaceFeasibility`：手机 NOT_RUN；平板 NOT_RUN。

### C03IsolatedDeviceTests.java

- `ordinaryIsolatedCodecDenialDoesNotReady`：手机 NOT_RUN；平板 NOT_RUN。
- `nativeLeaseSurvivesDuplicateDescriptorClose`：手机 NOT_RUN；平板 NOT_RUN。
- `isolatedActualEncodeAndReadyRecovery`：手机 NOT_RUN；平板 NOT_RUN。
- `cancelAfterActualVideoSample`：手机 NOT_RUN；平板 NOT_RUN。
- `workerExitDuringActualEncoding`：手机 NOT_RUN；平板 NOT_RUN。
- `workerSigsegvDuringActualEncoding`：手机 NOT_RUN；平板 NOT_RUN。
- `secondCodecTaskSurvivesFirstNativeCrash`：手机 NOT_RUN；平板 NOT_RUN。
- `actualHostDeathDuringEncodingAndCrossOwnerAbort`：手机 NOT_RUN；平板 NOT_RUN。
- `actualHostDeathAfterReadyAndSameTaskQuery`：手机 NOT_RUN；平板 NOT_RUN。

每台设备保存 candidate/hash/证书/型号/API/ABI、方法结果、真实处理 proof、Binder death 与 generation Source query、输出 task 状态、源 hash、注入阶段/命中/错误链和人工现象。失败退出仍检查账本；未真正排空记 quarantine，不宣布释放。仅根据负责人保留决定清理本次明确登记的 C03 私有 fixture/临时 task，成功 READY 输出留待核查；不得删除 C02 恢复材料或用户数据。
